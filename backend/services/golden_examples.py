"""Golden examples — per-agent / per-network few-shot library.

A "golden example" is one ideal (user input → ideal agent output) pair
for a specific agent or the network the agent belongs to. At inference
time we inject the top-N matching examples as few-shot context so the
agent's responses converge on the curated style.

Two levels of scope:
  • agent_id   — this exact agent only
  • network    — every agent in the network (28 networks on MAARS);
                 lets you curate once and have it apply to all 14-40
                 agents inside a network. Infinity agents inherit
                 network-level training automatically.

Selection order at lookup time:
  1. Agent-specific examples (highest priority; override network).
  2. Network-level examples.
  3. Role-level fallback (same role string across agents).

Shape of a stored doc (collection `agent_golden_examples`):
    {
      example_id:      "ge_<uuid>",
      scope:           "agent" | "network" | "role",
      scope_value:     "agent_marketing" | "10G" | "Sales Representative",
      user_input:      "...",        # what the client asks
      ideal_output:    "...",        # what a best-in-class agent replies
      notes:           "...",        # optional context for reviewers
      created_by:      "admin@...",
      created_at:      ISO,
      updated_at:      ISO,
      source:          "manual" | "promoted_from_feedback" | "imported",
      weight:          float,         # 0..1; higher = shown first
      tags:            [str],
    }

No TTL — these are curated training data, not ephemeral cache.
"""
from __future__ import annotations
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

logger = logging.getLogger(__name__)

COLLECTION = "agent_golden_examples"
DEFAULT_TOP_N = 3
MAX_TOP_N = 10


async def _ensure_indexes() -> None:
    from db import db
    try:
        await db[COLLECTION].create_index([("scope", 1), ("scope_value", 1)])
        await db[COLLECTION].create_index("example_id", unique=True)
        await db[COLLECTION].create_index([("scope_value", 1), ("weight", -1)])
    except Exception as exc:
        logger.info("golden_examples index init skipped: %s", exc)


async def list_examples(
    *, scope: Optional[str] = None, scope_value: Optional[str] = None,
    limit: int = 100,
) -> list[dict[str, Any]]:
    from db import db
    q: dict[str, Any] = {}
    if scope:
        q["scope"] = scope
    if scope_value:
        q["scope_value"] = scope_value
    cursor = db[COLLECTION].find(q, {"_id": 0}).sort([("weight", -1), ("created_at", -1)]).limit(limit)
    return await cursor.to_list(length=limit)


async def create(
    *, scope: str, scope_value: str, user_input: str, ideal_output: str,
    notes: str = "", created_by: str = "system",
    source: str = "manual", weight: float = 1.0, tags: Optional[list[str]] = None,
) -> dict[str, Any]:
    if scope not in ("agent", "network", "role"):
        raise ValueError(f"invalid scope '{scope}' (expected agent|network|role)")
    if not (scope_value and user_input.strip() and ideal_output.strip()):
        raise ValueError("scope_value, user_input, ideal_output are required")
    await _ensure_indexes()
    from db import db
    now = datetime.now(timezone.utc).isoformat()
    doc = {
        "example_id":   f"ge_{uuid.uuid4().hex[:16]}",
        "scope":        scope,
        "scope_value":  scope_value,
        "user_input":   user_input.strip(),
        "ideal_output": ideal_output.strip(),
        "notes":        (notes or "").strip(),
        "created_by":   created_by,
        "created_at":   now,
        "updated_at":   now,
        "source":       source,
        "weight":       max(0.0, min(1.0, float(weight))),
        "tags":         list(tags or []),
    }
    await db[COLLECTION].insert_one(dict(doc))
    doc.pop("_id", None)
    return doc


async def update(example_id: str, patch: dict[str, Any]) -> dict[str, Any]:
    from db import db
    allowed = {"user_input", "ideal_output", "notes", "weight", "tags"}
    update = {k: v for k, v in patch.items() if k in allowed}
    if "weight" in update:
        try:
            update["weight"] = max(0.0, min(1.0, float(update["weight"])))
        except (TypeError, ValueError):
            raise ValueError("weight must be a number in [0, 1]")
    update["updated_at"] = datetime.now(timezone.utc).isoformat()
    await db[COLLECTION].update_one({"example_id": example_id}, {"$set": update})
    doc = await db[COLLECTION].find_one({"example_id": example_id}, {"_id": 0})
    return doc or {}


async def delete(example_id: str) -> bool:
    from db import db
    res = await db[COLLECTION].delete_one({"example_id": example_id})
    return bool(getattr(res, "deleted_count", 0))


async def resolve_for_agent(agent: dict[str, Any], *, top_n: int = DEFAULT_TOP_N) -> list[dict[str, Any]]:
    """Return the examples to inject for this agent, ranked by:
      1. scope == 'agent'  and scope_value == agent.agent_id
      2. scope == 'network' and scope_value == agent.network
      3. scope == 'role'    and scope_value == agent.role
    Higher weight wins within each bucket; bucket-1 fills before bucket-2.
    """
    n = max(1, min(int(top_n or DEFAULT_TOP_N), MAX_TOP_N))
    out: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    from db import db

    async def _take(scope: str, value: Optional[str]) -> None:
        if not value or len(out) >= n:
            return
        cursor = db[COLLECTION].find(
            {"scope": scope, "scope_value": value},
            {"_id": 0},
        ).sort([("weight", -1), ("created_at", -1)]).limit(n - len(out) + 2)
        async for doc in cursor:
            if doc["example_id"] in seen_ids:
                continue
            out.append(doc)
            seen_ids.add(doc["example_id"])
            if len(out) >= n:
                return

    await _take("agent",   agent.get("agent_id"))
    await _take("network", agent.get("network"))
    await _take("role",    agent.get("role"))
    return out


def format_as_fewshot(examples: list[dict[str, Any]]) -> str:
    """Render examples as a system-prompt suffix the model can pattern-match on.
    Intentionally terse — more examples is better than long ones."""
    if not examples:
        return ""
    lines = [
        "",
        "── TRAINED EXAMPLES ───────────────────────────",
        "Match the style and depth of these golden outputs. They represent",
        "the quality bar for this role.",
    ]
    for i, ex in enumerate(examples, 1):
        lines.append(f"\nEXAMPLE {i}")
        lines.append(f"User: {ex.get('user_input','').strip()}")
        lines.append(f"Ideal reply: {ex.get('ideal_output','').strip()}")
    lines.append("── END TRAINED EXAMPLES ───────────────────────\n")
    return "\n".join(lines)
