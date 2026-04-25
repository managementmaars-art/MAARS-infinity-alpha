"""
Operator revenue ledger — the "profit pool" side of the subscription split.

When a user pays for a credit package, the cash splits two ways:
    operator portion  → recorded here, in `operator_revenue_entries`
    user portion      → grants credits via wallet_service (already wired in stripe_service)

This file owns the operator side. It is append-only, idempotent on
(source_type, source_ref), and exposes admin aggregates that complement the
existing `/admin/metrics/profitability` endpoint (which reasons about credit
debits vs internal provider cost — a different lens).

Collection:  operator_revenue_entries
Index:       (source_type, source_ref) UNIQUE
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from pymongo.errors import DuplicateKeyError

from db import db

logger = logging.getLogger(__name__)

REVENUE_COLLECTION = "operator_revenue_entries"


# ---------------------------------------------------------------- write

async def record_revenue(
    *,
    amount_usd: float,
    source_type: str,
    source_ref: str,
    user_id: Optional[str] = None,
    package_id: Optional[str] = None,
    metadata: Optional[dict[str, Any]] = None,
) -> Optional[dict[str, Any]]:
    """
    Append an operator-revenue entry. Idempotent: a duplicate `source_ref` for
    the same `source_type` is a no-op (caller already booked it).

    Returns the inserted document, or None if a matching entry already existed.
    """
    if amount_usd < 0:
        raise ValueError("amount_usd must be non-negative")
    if not source_type or not source_ref:
        raise ValueError("source_type and source_ref are required")

    doc = {
        "entry_id": f"rev_{uuid.uuid4().hex[:16]}",
        "source_type": source_type,
        "source_ref": source_ref,
        "amount_usd": round(float(amount_usd), 6),
        "user_id": user_id,
        "package_id": package_id,
        "metadata": metadata or {},
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        await db[REVENUE_COLLECTION].insert_one(doc)
        return doc
    except DuplicateKeyError:
        logger.info("revenue idempotent no-op: %s/%s already booked", source_type, source_ref)
        return None


async def record_refund(
    *,
    amount_usd: float,
    source_type: str,
    source_ref: str,
    refund_ref: str,
    user_id: Optional[str] = None,
    metadata: Optional[dict[str, Any]] = None,
) -> Optional[dict[str, Any]]:
    """
    Reverse a prior revenue booking (negative entry). Keyed on (source_type,
    refund_ref) so multiple partial refunds against the same checkout are OK.
    """
    if amount_usd <= 0:
        raise ValueError("refund amount_usd must be positive")

    doc = {
        "entry_id": f"rev_refund_{uuid.uuid4().hex[:16]}",
        "source_type": f"{source_type}_refund",
        "source_ref": refund_ref,
        "amount_usd": -round(float(amount_usd), 6),
        "user_id": user_id,
        "package_id": None,
        "metadata": {**(metadata or {}), "original_source_ref": source_ref},
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        await db[REVENUE_COLLECTION].insert_one(doc)
        return doc
    except DuplicateKeyError:
        return None


# ---------------------------------------------------------------- read

def _window_start(days: int) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()


async def total_revenue(*, days: int = 30) -> float:
    pipeline = [
        {"$match": {"created_at": {"$gte": _window_start(days)}}},
        {"$group": {"_id": None, "total": {"$sum": "$amount_usd"}}},
    ]
    async for row in db[REVENUE_COLLECTION].aggregate(pipeline):
        return float(row.get("total") or 0.0)
    return 0.0


async def revenue_by_package(*, days: int = 30) -> list[dict[str, Any]]:
    pipeline = [
        {"$match": {"created_at": {"$gte": _window_start(days)}}},
        {"$group": {
            "_id": "$package_id",
            "amount_usd": {"$sum": "$amount_usd"},
            "purchases": {"$sum": 1},
        }},
        {"$sort": {"amount_usd": -1}},
    ]
    out: list[dict[str, Any]] = []
    async for row in db[REVENUE_COLLECTION].aggregate(pipeline):
        out.append({
            "package_id": row.get("_id") or "unknown",
            "amount_usd": round(float(row.get("amount_usd") or 0.0), 4),
            "purchases": int(row.get("purchases") or 0),
        })
    return out


async def revenue_by_user(*, days: int = 30, limit: int = 10) -> list[dict[str, Any]]:
    pipeline = [
        {"$match": {"created_at": {"$gte": _window_start(days)}, "user_id": {"$ne": None}}},
        {"$group": {
            "_id": "$user_id",
            "amount_usd": {"$sum": "$amount_usd"},
            "purchases": {"$sum": 1},
        }},
        {"$sort": {"amount_usd": -1}},
        {"$limit": int(limit)},
    ]
    out: list[dict[str, Any]] = []
    async for row in db[REVENUE_COLLECTION].aggregate(pipeline):
        out.append({
            "user_id": row.get("_id"),
            "amount_usd": round(float(row.get("amount_usd") or 0.0), 4),
            "purchases": int(row.get("purchases") or 0),
        })
    return out


async def recent_entries(*, limit: int = 50) -> list[dict[str, Any]]:
    cursor = (
        db[REVENUE_COLLECTION]
        .find({}, {"_id": 0})
        .sort("created_at", -1)
        .limit(int(limit))
    )
    return [doc async for doc in cursor]


async def ensure_indexes() -> None:
    await db[REVENUE_COLLECTION].create_index(
        [("source_type", 1), ("source_ref", 1)],
        unique=True,
        name="revenue_idempotency_unique",
    )
    await db[REVENUE_COLLECTION].create_index(
        [("created_at", -1)],
        name="revenue_by_time",
    )
    await db[REVENUE_COLLECTION].create_index(
        [("user_id", 1), ("created_at", -1)],
        name="revenue_by_user_time",
    )
    await db[REVENUE_COLLECTION].create_index(
        [("package_id", 1), ("created_at", -1)],
        name="revenue_by_package_time",
    )
