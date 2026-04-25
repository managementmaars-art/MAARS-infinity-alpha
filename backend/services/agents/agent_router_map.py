"""Role → agent routing, with quality-aware fallback.

Commander delegation historically used the static `AGENT_ROLE_MAP`
dict in `services.agent_service` — one role key → one agent_id, no
fallback. If that agent underperformed or got throttled, every
Commander invocation of that role degraded.

This module wraps the static map with:
  1. Operator overrides stored in Mongo (`agent_role_map` collection).
  2. Per-call scoring from recent performance (agent_performance.rollup).
  3. Ranked fallback: try primary, then 2nd, then 3rd.

Shape of a stored override (singleton per role_key):
    {
      role_key:  "marketing",
      agents:    ["agent_marketing_v2", "agent_marketing", "agent_copywriter"],
      updated_at: ISO,
      updated_by: "admin-user-id",
    }

Public surface:
    async resolve(role_key) -> str            # best agent_id for this role
    async ranked_for(role_key) -> list[str]   # full ordered fallback list
    async get_map() -> dict[str, list[str]]   # for the admin UI
    async set_override(role_key, agents) -> dict
    async clear_override(role_key) -> bool
"""
from __future__ import annotations
import logging
from datetime import datetime, timezone
from typing import Any, Optional

logger = logging.getLogger(__name__)

COLLECTION = "agent_role_map"
_DEFAULT_FALLBACK = "agent_strategist"


async def _static_map() -> dict[str, str]:
    """The hardcoded map imported from agent_service."""
    from services.agent_service import AGENT_ROLE_MAP
    return dict(AGENT_ROLE_MAP)


async def _overrides() -> dict[str, list[str]]:
    from db import db
    cursor = db[COLLECTION].find({}, {"_id": 0, "role_key": 1, "agents": 1})
    out: dict[str, list[str]] = {}
    async for doc in cursor:
        key = doc.get("role_key")
        if key:
            out[key] = list(doc.get("agents") or [])
    return out


async def ranked_for(role_key: str) -> list[str]:
    """Return the ordered fallback list for a role. Priority:
       override > static > [_DEFAULT_FALLBACK]."""
    key = (role_key or "").strip().lower()
    if not key:
        return [_DEFAULT_FALLBACK]
    overrides = await _overrides()
    if key in overrides and overrides[key]:
        return list(overrides[key])
    static = await _static_map()
    if key in static:
        return [static[key], _DEFAULT_FALLBACK] if static[key] != _DEFAULT_FALLBACK else [_DEFAULT_FALLBACK]
    return [_DEFAULT_FALLBACK]


async def resolve(role_key: str) -> str:
    """Return the best-performing agent_id from the ranked list. If
    performance data is thin, falls through to static map order."""
    candidates = await ranked_for(role_key)
    if len(candidates) <= 1:
        return candidates[0] if candidates else _DEFAULT_FALLBACK
    # Rank by recent performance score
    try:
        from services.agents import agent_performance
        rollup = await agent_performance.rollup(window_days=7)
        scored = {r["agent_id"]: r for r in rollup if r.get("score") is not None}
        best = None
        best_score = -1.0
        for cand in candidates:
            s = scored.get(cand, {}).get("score")
            if s is None:
                continue
            if s > best_score:
                best_score = s
                best = cand
        if best:
            return best
    except Exception as exc:
        logger.info("resolve scoring soft-fail: %s", exc)
    return candidates[0]


async def get_map() -> dict[str, list[str]]:
    """Full role → ranked-agents map with overrides applied. For the UI."""
    static = await _static_map()
    overrides = await _overrides()
    keys = set(static) | set(overrides)
    return {
        k: (overrides.get(k) or [static.get(k)] if static.get(k) else overrides.get(k) or [])
        for k in sorted(keys)
    }


async def set_override(role_key: str, agents: list[str], updated_by: str = "") -> dict[str, Any]:
    key = (role_key or "").strip().lower()
    if not key:
        raise ValueError("role_key required")
    cleaned = [a.strip() for a in (agents or []) if a and a.strip()]
    if not cleaned:
        raise ValueError("agents list cannot be empty")
    from db import db
    now = datetime.now(timezone.utc).isoformat()
    await db[COLLECTION].update_one(
        {"role_key": key},
        {"$set": {
            "role_key":   key,
            "agents":     cleaned,
            "updated_at": now,
            "updated_by": updated_by,
        }},
        upsert=True,
    )
    return {"role_key": key, "agents": cleaned, "updated_at": now}


async def clear_override(role_key: str) -> bool:
    from db import db
    res = await db[COLLECTION].delete_one({"role_key": (role_key or "").strip().lower()})
    return bool(getattr(res, "deleted_count", 0))
