"""
MAARS API key service — hashed storage, last4 display, revoke.

Replaces the plaintext `client_gateway_keys.key` field flagged by audit 010.
Keys are generated once, handed to the user in the response, and stored
as `sha256(pepper + raw_key)`. Lookups hit the hash index.

Key shape:  maars_sk_live_<40 hex>   (display: maars_sk_live_…<last4>)
"""
from __future__ import annotations

import hashlib
import hmac
import os
import secrets
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from db import db

API_KEY_COLLECTION = "api_keys"
KEY_PREFIX = "maars_sk_live_"
_PEPPER = os.environ.get("MAARS_API_KEY_PEPPER") or os.environ.get("JWT_SECRET", "maars-default-pepper")


def _hash(raw_key: str) -> str:
    """HMAC-SHA256 of the raw key with a server-side pepper."""
    return hmac.new(_PEPPER.encode("utf-8"), raw_key.encode("utf-8"), hashlib.sha256).hexdigest()


def _last4(raw_key: str) -> str:
    return raw_key[-4:] if len(raw_key) >= 4 else raw_key


async def create_key(
    user_id: str,
    *,
    name: str = "default",
    plan_id: str = "free",
    monthly_budget_usd: float = 0.0,
) -> dict[str, Any]:
    """
    Generate a fresh key for `user_id`. Returns the raw key exactly ONCE —
    subsequent reads only expose the hash + last4.
    """
    raw_key = f"{KEY_PREFIX}{secrets.token_hex(20)}"
    now = datetime.now(timezone.utc).isoformat()
    doc = {
        "api_key_id": f"ak_{uuid.uuid4().hex[:16]}",
        "user_id": user_id,
        "name": name,
        "key_hash": _hash(raw_key),
        "last4": _last4(raw_key),
        "plan_id": plan_id,
        "monthly_budget_usd": float(monthly_budget_usd),
        "used_usd": 0.0,
        "cycle_start": now,
        "status": "active",
        "created_at": now,
        "last_used_at": None,
        "revoked_at": None,
    }
    await db[API_KEY_COLLECTION].insert_one(doc)
    return {"raw_key": raw_key, **{k: v for k, v in doc.items() if k != "_id"}}


async def find_by_raw_key(raw_key: str) -> Optional[dict[str, Any]]:
    """Lookup an active key by the value the client just sent. None if invalid/revoked."""
    if not raw_key:
        return None
    key_hash = _hash(raw_key)
    doc = await db[API_KEY_COLLECTION].find_one({"key_hash": key_hash, "status": "active"}, {"_id": 0})
    if doc:
        await db[API_KEY_COLLECTION].update_one(
            {"api_key_id": doc["api_key_id"]},
            {"$set": {"last_used_at": datetime.now(timezone.utc).isoformat()}},
        )
    return doc


async def list_keys(user_id: str) -> list[dict[str, Any]]:
    """Return the user's keys without exposing the hash."""
    cursor = db[API_KEY_COLLECTION].find(
        {"user_id": user_id},
        {"_id": 0, "key_hash": 0},
    ).sort("created_at", -1)
    return [doc async for doc in cursor]


async def revoke(api_key_id: str, user_id: str) -> bool:
    """Revoke a key. Returns True if a row was changed."""
    result = await db[API_KEY_COLLECTION].update_one(
        {"api_key_id": api_key_id, "user_id": user_id, "status": "active"},
        {
            "$set": {
                "status": "revoked",
                "revoked_at": datetime.now(timezone.utc).isoformat(),
            }
        },
    )
    return result.modified_count > 0


async def ensure_indexes() -> None:
    await db[API_KEY_COLLECTION].create_index("key_hash", unique=True, name="api_key_hash_unique")
    await db[API_KEY_COLLECTION].create_index(
        [("user_id", 1), ("status", 1)], name="api_key_by_user_status"
    )
