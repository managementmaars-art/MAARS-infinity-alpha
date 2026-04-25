"""
Per-customer pricing overrides — promotes MAARS to a B2B-capable platform.

Use case: an enterprise customer negotiates a custom rev-share, a discounted
price, or a credit bonus. Instead of forking the global package config, you
attach an override to that user_id. The Stripe webhook checks for it and
falls back to the package default if absent.

Override fields (all optional — only provided ones are applied):
    operator_share_pct   override the global package's split %
    price_usd            override the price (use when the customer is on a
                         negotiated invoice, not standard Stripe checkout)
    credits_bonus        +N additional credits granted on top of the package
    notes                free text — shows in the admin UI
    expires_at           ISO timestamp; the override stops applying after this

Collection: customer_pricing_overrides
Index:      (user_id, package_id)  UNIQUE   — one override per (user, package)
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Optional

from db import db

logger = logging.getLogger(__name__)

OVERRIDE_COLLECTION = "customer_pricing_overrides"


# --------------------------------------------------------- write

async def upsert(
    *,
    user_id: str,
    package_id: str,
    operator_share_pct: Optional[float] = None,
    price_usd: Optional[float] = None,
    credits_bonus: Optional[int] = None,
    notes: str = "",
    expires_at: Optional[str] = None,
    actor_id: str = "",
) -> dict[str, Any]:
    """Create or update a per-customer override. Idempotent on (user_id, package_id)."""
    if not user_id or not package_id:
        raise ValueError("user_id and package_id are required")
    if operator_share_pct is not None:
        operator_share_pct = max(0.0, min(1.0, float(operator_share_pct)))
    if price_usd is not None and price_usd < 0:
        raise ValueError("price_usd must be non-negative")
    if credits_bonus is not None and credits_bonus < 0:
        raise ValueError("credits_bonus must be non-negative")

    now = datetime.now(timezone.utc).isoformat()
    fields: dict[str, Any] = {
        "user_id": user_id,
        "package_id": package_id,
        "notes": notes or "",
        "updated_at": now,
        "updated_by": actor_id or "system",
    }
    if operator_share_pct is not None:
        fields["operator_share_pct"] = operator_share_pct
    if price_usd is not None:
        fields["price_usd"] = float(price_usd)
    if credits_bonus is not None:
        fields["credits_bonus"] = int(credits_bonus)
    if expires_at:
        fields["expires_at"] = expires_at

    await db[OVERRIDE_COLLECTION].update_one(
        {"user_id": user_id, "package_id": package_id},
        {"$set": fields, "$setOnInsert": {"created_at": now}},
        upsert=True,
    )
    return await get(user_id=user_id, package_id=package_id) or fields


async def get(*, user_id: str, package_id: str) -> Optional[dict[str, Any]]:
    """Return an override if active (not expired). None otherwise."""
    doc = await db[OVERRIDE_COLLECTION].find_one(
        {"user_id": user_id, "package_id": package_id}, {"_id": 0},
    )
    if not doc:
        return None
    expires_at = doc.get("expires_at")
    if expires_at:
        try:
            if datetime.fromisoformat(expires_at).timestamp() < datetime.now(timezone.utc).timestamp():
                return None
        except Exception:
            pass
    return doc


async def list_for_user(user_id: str) -> list[dict[str, Any]]:
    cursor = db[OVERRIDE_COLLECTION].find({"user_id": user_id}, {"_id": 0}).sort("updated_at", -1)
    return [d async for d in cursor]


async def list_all(limit: int = 200) -> list[dict[str, Any]]:
    cursor = db[OVERRIDE_COLLECTION].find({}, {"_id": 0}).sort("updated_at", -1).limit(int(limit))
    return [d async for d in cursor]


async def delete(*, user_id: str, package_id: str) -> bool:
    res = await db[OVERRIDE_COLLECTION].delete_one(
        {"user_id": user_id, "package_id": package_id},
    )
    return res.deleted_count > 0


# --------------------------------------------------------- bootstrap

async def ensure_indexes() -> None:
    await db[OVERRIDE_COLLECTION].create_index(
        [("user_id", 1), ("package_id", 1)],
        unique=True,
        name="customer_override_unique",
    )
    await db[OVERRIDE_COLLECTION].create_index(
        [("user_id", 1), ("updated_at", -1)],
        name="customer_override_by_user_time",
    )
