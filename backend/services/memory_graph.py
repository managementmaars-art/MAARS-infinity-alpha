"""Temporal knowledge-graph memory — Mongo-backed.

Same shape as Graphiti/Zep's temporal KG: every fact is an edge
`(user) -[STATED {valid_from, valid_to}]-> fact` so you can query
"what did the user believe on date X" and supersede prior beliefs
without deleting history.

Backing store: `db.memory_graph` (collection). Each document is one
fact/edge. Upsert-by-hash keeps storage flat; temporal validity is
managed by expiring the previous doc's `valid_to`.

Why Mongo not Neo4j (for now):
- No new infra to operate at launch
- MAARS already indexes by (user_id, updated_at)
- Queries are "recent N beliefs about topic X" — flat + filtered works
- Swap to Graphiti later by reading the same shape out of Mongo and
  pushing to Neo4j with identical predicates

Public API:
    record_fact(user_id, subject, predicate, object, agent_id)
    recall(user_id, topic, limit=10, as_of=None)
    supersede(user_id, subject, predicate, new_object)
    forget(user_id, fact_id)
"""
from __future__ import annotations
import hashlib
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

logger = logging.getLogger(__name__)

COLLECTION = "memory_graph"


def _fact_hash(user_id: str, subject: str, predicate: str) -> str:
    key = f"{user_id}|{subject.lower()}|{predicate.lower()}"
    return hashlib.sha1(key.encode("utf-8")).hexdigest()[:16]


async def _ensure_indexes() -> None:
    from db import db
    try:
        await db[COLLECTION].create_index([("user_id", 1), ("subject", 1), ("predicate", 1)])
        await db[COLLECTION].create_index([("user_id", 1), ("valid_from", -1)])
        await db[COLLECTION].create_index([("user_id", 1), ("topic", 1)])
        await db[COLLECTION].create_index("fact_id", unique=True)
    except Exception as exc:
        logger.info("memory_graph index init skipped: %s", exc)


async def record_fact(
    *, user_id: str, subject: str, predicate: str, obj: Any,
    topic: str | None = None, agent_id: str | None = None,
    source_ref: str | None = None,
) -> dict[str, Any]:
    """Append a fact. If a prior fact with the same (subject, predicate)
    exists, close its validity window and write a new one."""
    from db import db
    await _ensure_indexes()
    now = datetime.now(timezone.utc).isoformat()
    # Close the most recent open fact on this (subject, predicate)
    await db[COLLECTION].update_many(
        {"user_id": user_id, "subject": subject, "predicate": predicate,
         "valid_to": None},
        {"$set": {"valid_to": now}},
    )
    fact_id = f"mf_{uuid.uuid4().hex[:12]}"
    doc = {
        "fact_id":    fact_id,
        "user_id":    user_id,
        "subject":    subject,
        "predicate":  predicate,
        "object":     obj,
        "topic":      topic or predicate,
        "agent_id":   agent_id,
        "source_ref": source_ref,
        "valid_from": now,
        "valid_to":   None,
        "created_at": now,
        "hash_key":   _fact_hash(user_id, subject, predicate),
    }
    await db[COLLECTION].insert_one(doc)
    doc.pop("_id", None)
    return doc


async def recall(
    *, user_id: str, topic: str | None = None,
    subject: str | None = None, predicate: str | None = None,
    limit: int = 10, as_of: str | None = None,
    include_superseded: bool = False,
) -> list[dict[str, Any]]:
    """Retrieve active facts. By default returns only currently-valid
    ones (valid_to is None OR > as_of). Pass `include_superseded=True`
    to see history too."""
    from db import db
    q: dict[str, Any] = {"user_id": user_id}
    if topic:    q["topic"] = topic
    if subject:  q["subject"] = subject
    if predicate: q["predicate"] = predicate
    if not include_superseded:
        if as_of:
            q["$or"] = [{"valid_to": None}, {"valid_to": {"$gt": as_of}}]
            q["valid_from"] = {"$lte": as_of}
        else:
            q["valid_to"] = None
    cursor = db[COLLECTION].find(q, {"_id": 0}).sort("valid_from", -1).limit(
        max(1, min(int(limit), 200))
    )
    return await cursor.to_list(length=limit)


async def forget(user_id: str, fact_id: str) -> bool:
    from db import db
    res = await db[COLLECTION].delete_one({"user_id": user_id, "fact_id": fact_id})
    return bool(getattr(res, "deleted_count", 0))


async def topic_summary(user_id: str, topic: str) -> dict[str, Any]:
    """Human-readable one-shot summary of the active facts on a topic."""
    facts = await recall(user_id=user_id, topic=topic, limit=50)
    return {
        "topic": topic,
        "active_facts": len(facts),
        "facts": [
            {
                "subject":   f["subject"],
                "predicate": f["predicate"],
                "object":    f["object"],
                "since":     f["valid_from"],
            }
            for f in facts
        ],
    }


async def extract_and_record(
    *, user_id: str, text: str, agent_id: str | None = None,
) -> list[dict[str, Any]]:
    """LLM-powered fact extractor. Pulls declarative statements out of
    free-form user input and records them. Keeps the cost tiny via the
    cheap-model default."""
    import json, re
    from services.llm_gateway import complete_text
    prompt = (
        "Extract concrete facts the user is STATING about themselves or "
        "their situation. Skip questions, requests, hypotheticals. "
        'Reply ONLY with a JSON array: [{"subject": "user|company", '
        '"predicate": "short_key", "object": "value", "topic": "short"}]. '
        f"TEXT:\n{text[:3000]}"
    )
    try:
        raw = await complete_text(
            user_id,
            system_prompt="You are a terse fact extractor. Output strict JSON only.",
            user_prompt=prompt,
            model="maars/auto",
            max_tokens=500, temperature=0.0,
            source="memory_graph.extract",
            enable_cache=True,
        )
    except Exception as exc:
        logger.info("extract_and_record LLM failed: %s", exc)
        return []
    m = re.search(r"\[[\s\S]*\]", raw or "")
    try:
        items = json.loads(m.group(0)) if m else []
    except Exception:
        items = []
    out: list[dict] = []
    for item in items if isinstance(items, list) else []:
        if not isinstance(item, dict):
            continue
        subject = str(item.get("subject") or "user").strip()
        predicate = str(item.get("predicate") or "").strip()
        obj = item.get("object")
        if not predicate or obj is None:
            continue
        rec = await record_fact(
            user_id=user_id, subject=subject,
            predicate=predicate, obj=obj,
            topic=str(item.get("topic") or predicate),
            agent_id=agent_id,
        )
        out.append(rec)
    return out
