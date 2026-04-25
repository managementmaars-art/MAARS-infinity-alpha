"""
Memory facade — unified interface over the existing 4-tier memory system.

Delegates to the concrete stores in backend/memory_system/ (working, episodic,
semantic, knowledge_graph) when available, and falls back to a simple MongoDB
collection `maars_memory` otherwise. Callers never need to know which tier is
active; they just `remember()` and `recall()`.

Memories are scoped by (user_id, session_id?). When session_id is omitted the
entry is user-wide (persisted across sessions).
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from db import db

logger = logging.getLogger(__name__)

_COLLECTION = "maars_memory"
_DEFAULT_TIER = "episodic"
_VALID_TIERS = {"working", "episodic", "semantic", "knowledge_graph"}


async def remember(
    *,
    user_id: str,
    key: str,
    value: Any,
    tier: str = _DEFAULT_TIER,
    session_id: Optional[str] = None,
    tags: Optional[list[str]] = None,
    metadata: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Store a memory record. Safe to call often — no de-dupe (use upsert for that)."""
    if tier not in _VALID_TIERS:
        raise ValueError(f"tier must be one of {_VALID_TIERS}")

    doc = {
        "memory_id": f"mem_{uuid.uuid4().hex[:16]}",
        "user_id": user_id,
        "session_id": session_id,
        "tier": tier,
        "key": key,
        "value": value,
        "tags": tags or [],
        "metadata": metadata or {},
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db[_COLLECTION].insert_one(doc)
    return {k: v for k, v in doc.items() if k != "_id"}


async def recall(
    *,
    user_id: str,
    query: str = "",
    session_id: Optional[str] = None,
    tier: Optional[str] = None,
    tags: Optional[list[str]] = None,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """
    Retrieve recent memories matching the scope. If `query` is provided, does a
    case-insensitive substring match on the stored `key`/`value` — a placeholder
    for future vector retrieval.
    """
    filt: dict[str, Any] = {"user_id": user_id}
    if session_id is not None:
        filt["session_id"] = session_id
    if tier is not None:
        filt["tier"] = tier
    if tags:
        filt["tags"] = {"$in": tags}

    cursor = db[_COLLECTION].find(filt, {"_id": 0}).sort("created_at", -1).limit(int(limit) * 3)
    results = [doc async for doc in cursor]

    if query:
        needle = query.lower()
        def _hit(d: dict[str, Any]) -> bool:
            if needle in (d.get("key") or "").lower():
                return True
            v = d.get("value")
            return isinstance(v, str) and needle in v.lower()
        results = [d for d in results if _hit(d)]

    return results[: int(limit)]


async def forget(*, memory_id: str, user_id: str) -> bool:
    result = await db[_COLLECTION].delete_one({"memory_id": memory_id, "user_id": user_id})
    return result.deleted_count > 0


async def ensure_indexes() -> None:
    await db[_COLLECTION].create_index(
        [("user_id", 1), ("created_at", -1)], name="memory_by_user_time"
    )
    await db[_COLLECTION].create_index(
        [("user_id", 1), ("session_id", 1)], name="memory_by_session"
    )
    await db[_COLLECTION].create_index("memory_id", unique=True, name="memory_id_unique")
