"""SME (subject-matter expert) correction queue.

Pattern from Cleanlab Codex (`rag-sql-router`): low-quality responses
get queued for human review → SME edits the response → the corrected
answer is keyed by a semantic fingerprint so future similar queries
hit the validated answer at ZERO LLM cost.

Flow:
  1. `llm_gateway.complete()` emits trust_score OR quality_review < threshold
  2. Entry auto-queues into `db.sme_corrections` with status="pending"
  3. Admin UI shows queue; SME approves original or writes a correction
  4. On approval: entry status="validated" + answer keyed by
     fingerprint(prompt)
  5. Future calls with a similar prompt (Jaccard > 0.7 on fingerprint
     tokens) short-circuit to the validated answer

Public API:
    queue_for_review(user_id, query, response, agent_id, reason)
    approve(correction_id, corrected_answer)
    reject(correction_id)
    lookup_validated(query) → corrected answer or None
"""
from __future__ import annotations
import hashlib
import logging
import re
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

logger = logging.getLogger(__name__)

COLLECTION = "sme_corrections"


def _fingerprint(text: str) -> set[str]:
    """Word-level fingerprint — set of meaningful tokens."""
    return set(re.findall(r"[A-Za-z0-9]{3,}", (text or "").lower()))


def _jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


async def _ensure_indexes() -> None:
    from db import db
    try:
        await db[COLLECTION].create_index([("status", 1), ("queued_at", -1)])
        await db[COLLECTION].create_index([("user_id", 1), ("status", 1)])
        await db[COLLECTION].create_index("correction_id", unique=True)
    except Exception as exc:
        logger.info("sme_corrections index init skipped: %s", exc)


async def queue_for_review(
    *, user_id: str, query: str, response: str,
    agent_id: str | None = None, reason: str = "low_quality",
    extra: dict | None = None,
) -> dict[str, Any]:
    from db import db
    await _ensure_indexes()
    now = datetime.now(timezone.utc).isoformat()
    cid = f"smc_{uuid.uuid4().hex[:12]}"
    doc = {
        "correction_id":     cid,
        "user_id":           user_id,
        "agent_id":          agent_id,
        "query":             query.strip()[:4000],
        "original_response": (response or "")[:8000],
        "corrected_response": None,
        "reason":            reason,
        "status":            "pending",
        "queued_at":         now,
        "query_hash":        hashlib.sha1(query.strip().encode("utf-8")).hexdigest()[:16],
        "extra":             extra or {},
    }
    await db[COLLECTION].insert_one(dict(doc))
    doc.pop("_id", None)
    return doc


async def approve(
    correction_id: str, *,
    corrected_answer: str | None = None,
    reviewer: str = "admin",
) -> dict[str, Any] | None:
    """Mark approved with the canonical answer. If `corrected_answer`
    is None the original response is treated as good-enough."""
    from db import db
    now = datetime.now(timezone.utc).isoformat()
    patch: dict[str, Any] = {
        "status":      "validated",
        "decided_at":  now,
        "reviewer":    reviewer,
    }
    if corrected_answer is not None:
        patch["corrected_response"] = corrected_answer[:8000]
    await db[COLLECTION].update_one({"correction_id": correction_id}, {"$set": patch})
    return await db[COLLECTION].find_one({"correction_id": correction_id}, {"_id": 0})


async def reject(correction_id: str, *, reviewer: str = "admin") -> bool:
    from db import db
    now = datetime.now(timezone.utc).isoformat()
    res = await db[COLLECTION].update_one(
        {"correction_id": correction_id},
        {"$set": {"status": "rejected", "decided_at": now, "reviewer": reviewer}},
    )
    return bool(getattr(res, "modified_count", 0))


async def list_queue(
    status: str = "pending", limit: int = 50,
    user_id: str | None = None,
) -> list[dict]:
    from db import db
    q: dict[str, Any] = {"status": status}
    if user_id:
        q["user_id"] = user_id
    cursor = db[COLLECTION].find(q, {"_id": 0}).sort("queued_at", -1).limit(limit)
    return await cursor.to_list(length=limit)


async def lookup_validated(
    query: str, *, user_id: str | None = None,
    min_similarity: float = 0.7,
) -> dict[str, Any] | None:
    """Return a validated correction whose query fingerprint is >= `min_similarity`
    to the incoming query. O(n) over validated set — fine at the scale
    (< 10k validated items); add embedding-based lookup when it matters."""
    from db import db
    q_fp = _fingerprint(query)
    if not q_fp:
        return None
    mongo_q: dict[str, Any] = {"status": "validated"}
    if user_id:
        mongo_q["user_id"] = user_id
    cursor = db[COLLECTION].find(
        mongo_q,
        {"_id": 0, "correction_id": 1, "query": 1,
         "corrected_response": 1, "original_response": 1},
    ).sort("decided_at", -1).limit(500)
    best: dict | None = None
    best_score = 0.0
    async for c in cursor:
        sim = _jaccard(q_fp, _fingerprint(c.get("query", "")))
        if sim > best_score:
            best_score = sim
            best = c
    if best and best_score >= min_similarity:
        best["similarity"] = round(best_score, 3)
        best["answer"] = best.get("corrected_response") or best.get("original_response")
        return best
    return None
