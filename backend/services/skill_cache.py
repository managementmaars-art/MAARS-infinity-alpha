"""Per-agent skill-reuse cache — replay successful responses for repetitive tasks.

Problem this solves: MAARS's 499 client agents run many repetitive flows
(the same cold-email template against different leads, the same summariser
against new docs). Each run re-hits a provider even though the system prompt
+ task shape are identical. OpenSpace measured 46% fewer tokens in phase 2
via exactly this pattern.

Scope (deliberately narrow to avoid stale-cache incidents):
  - Only caches when `agent_id` is set AND temperature ≤ 0.3 (deterministic).
  - Only caches "successful" responses (no provider errors / tool-call stubs).
  - Fingerprint = sha256 of (agent_id, model, canonical(messages)).
  - 7-day TTL via Mongo TTL index on `expires_at`.
  - Miss is cheap (single indexed lookup); hit returns a normalized response
    the gateway emits without hitting any provider.

Invalidation: when the admin edits an agent's `system_prompt`, the
fingerprint naturally changes (system prompt is part of the hash input),
so stale entries age out without explicit busting.

Public surface:
    async lookup(agent_id, model, messages, temperature) -> dict | None
    async store(agent_id, model, messages, temperature, response) -> None
    async invalidate_agent(agent_id) -> int
"""
from __future__ import annotations
import hashlib
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

logger = logging.getLogger(__name__)

COLLECTION = "agent_skill_cache"
TTL_DAYS = 7
TEMP_CEILING = 0.3


def _fingerprint(agent_id: str, model: str, messages: list[dict]) -> str:
    """Deterministic key. Messages are canonicalised (role+content only;
    drop ephemeral fields like 'name', 'tool_call_id') so trivial metadata
    drift doesn't miss the cache."""
    canon = [{"role": m.get("role"), "content": m.get("content") or ""} for m in messages]
    blob = json.dumps([agent_id, model, canon], separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


async def _ensure_indexes() -> None:
    """Idempotent. Creates (fingerprint) unique index + TTL on expires_at."""
    from db import db
    try:
        await db[COLLECTION].create_index("fingerprint", unique=True)
        await db[COLLECTION].create_index("agent_id")
        await db[COLLECTION].create_index("expires_at", expireAfterSeconds=0)
    except Exception as exc:
        logger.info("skill_cache index init skipped: %s", exc)


async def lookup(
    *, agent_id: Optional[str], model: str, messages: list[dict],
    temperature: Optional[float],
) -> Optional[dict[str, Any]]:
    if not agent_id:
        return None
    if temperature is not None and float(temperature) > TEMP_CEILING:
        return None
    from db import db
    fp = _fingerprint(agent_id, model, messages)
    doc = await db[COLLECTION].find_one({"fingerprint": fp}, {"response": 1, "_id": 0})
    if not doc:
        return None
    resp = doc.get("response")
    if not resp:
        return None
    maars = dict(resp.get("maars") or {})
    maars["from_cache"] = "skill"
    maars["credits_used"] = 0
    resp = dict(resp)
    resp["maars"] = maars
    return resp


async def store(
    *, agent_id: Optional[str], model: str, messages: list[dict],
    temperature: Optional[float], response: dict[str, Any],
) -> None:
    if not agent_id:
        return
    if temperature is not None and float(temperature) > TEMP_CEILING:
        return
    if not response or not (response.get("choices") or []):
        return
    # Skip tool-call responses — they depend on live function outputs.
    first_msg = (response["choices"][0] or {}).get("message") or {}
    if first_msg.get("tool_calls"):
        return
    try:
        await _ensure_indexes()
        from db import db
        now = datetime.now(timezone.utc)
        fp = _fingerprint(agent_id, model, messages)
        await db[COLLECTION].update_one(
            {"fingerprint": fp},
            {"$set": {
                "fingerprint":  fp,
                "agent_id":     agent_id,
                "model":        model,
                "response":     response,
                "stored_at":    now,
                "expires_at":   now + timedelta(days=TTL_DAYS),
            }},
            upsert=True,
        )
    except Exception as exc:
        logger.info("skill_cache store soft-fail for %s: %s", agent_id, exc)


async def invalidate_agent(agent_id: str) -> int:
    """Drop every cached response for one agent. Called when admin edits
    the system prompt or wipes the cache from the UI."""
    from db import db
    res = await db[COLLECTION].delete_many({"agent_id": agent_id})
    return int(getattr(res, "deleted_count", 0) or 0)
