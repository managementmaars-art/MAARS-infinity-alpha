"""Idempotency keys — don't double-charge a client for a retried request.

Clients retry on timeout. Without an idempotency key, a slow first call
that they retry can hit us twice, burn 2× credits, and produce 2 rows
in their analytics. The Stripe / industry-standard fix is:

  client sends: Idempotency-Key: <uuid>
  we store the response keyed by that UUID for 24 hours.
  second request with the same key returns the cached response.

This module exposes:
  - get_cached(key, user_id) -> response or None
  - store_cached(key, user_id, response, credits_charged)

Keyed by (user_id, idempotency_key) so a leaked key from one tenant
can't retrieve another tenant's response. 24-hour TTL via Mongo's
expireAfterSeconds index on `created_at_epoch`.
"""
from __future__ import annotations
import logging
import time
from typing import Any

logger = logging.getLogger(__name__)

TTL_SECONDS = 24 * 3600
_INDEX_READY = False


async def _ensure_index() -> None:
    global _INDEX_READY
    if _INDEX_READY:
        return
    try:
        from db import db
        await db.idempotency_cache.create_index(
            [("user_id", 1), ("key", 1)], unique=True
        )
        await db.idempotency_cache.create_index(
            "created_at_epoch", expireAfterSeconds=TTL_SECONDS
        )
        _INDEX_READY = True
    except Exception as exc:
        logger.info("idempotency index setup deferred: %s", exc)


async def get_cached(key: str | None, user_id: str) -> dict[str, Any] | None:
    if not key:
        return None
    await _ensure_index()
    from db import db
    try:
        doc = await db.idempotency_cache.find_one({"user_id": user_id, "key": key})
    except Exception:
        return None
    if not doc:
        return None
    if time.time() - doc.get("created_at_epoch", 0) > TTL_SECONDS:
        try:
            await db.idempotency_cache.delete_one({"_id": doc["_id"]})
        except Exception:
            pass
        return None
    resp = doc.get("response")
    if isinstance(resp, dict):
        resp.setdefault("maars", {})["idempotent_replay"] = True
    return resp


async def store_cached(
    key: str | None,
    user_id: str,
    response: dict[str, Any],
    *,
    credits_charged: int = 0,
) -> None:
    if not key:
        return
    await _ensure_index()
    from db import db
    try:
        await db.idempotency_cache.replace_one(
            {"user_id": user_id, "key": key},
            {
                "user_id": user_id,
                "key": key,
                "response": response,
                "credits_charged": credits_charged,
                "created_at_epoch": time.time(),
            },
            upsert=True,
        )
    except Exception as exc:
        logger.info("idempotency store failed: %s", exc)
