"""
Immutable append-only ledger for MAARS Command wallets.

Every credit movement — grant, reserve, release, debit, refund, operator adjustment —
is recorded as a separate entry. Entries are keyed by (reference_type, reference_id, type)
so that a retried webhook or a replayed settlement cannot double-post.

Collection: `ledger_entries`
Index: (reference_type, reference_id, type) UNIQUE — idempotency primitive

Entries are never mutated or deleted. Corrections are posted as new ADJUSTMENT rows.
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from pymongo.errors import DuplicateKeyError

from db import db

logger = logging.getLogger(__name__)


class LedgerEntryType(str, Enum):
    CREDIT = "CREDIT"           # user acquired credits (plan grant, top-up, promo)
    RESERVE = "RESERVE"         # credits held pending settlement (inference in flight)
    RELEASE = "RELEASE"         # unused portion of a reserve returned to balance
    DEBIT = "DEBIT"             # credits consumed by a settled request
    REFUND = "REFUND"           # credits returned for a failed/refunded settlement
    ADJUSTMENT = "ADJUSTMENT"   # operator-initiated manual correction


LEDGER_COLLECTION = "ledger_entries"


async def append_entry(
    *,
    wallet_id: str,
    user_id: str,
    entry_type: LedgerEntryType,
    amount_credits: int,
    reference_type: str,
    reference_id: str,
    description: str = "",
    metadata: Optional[dict[str, Any]] = None,
) -> Optional[dict[str, Any]]:
    """
    Append a single ledger entry. Idempotent on (reference_type, reference_id, type).

    Returns the inserted document, or None if a matching entry already existed
    (duplicate-key — treat as no-op, caller already succeeded previously).
    """
    if amount_credits < 0:
        raise ValueError("amount_credits must be non-negative; use entry_type to signal direction")

    doc = {
        "entry_id": f"ldg_{uuid.uuid4().hex[:16]}",
        "wallet_id": wallet_id,
        "user_id": user_id,
        "type": entry_type.value,
        "amount_credits": int(amount_credits),
        "reference_type": reference_type,
        "reference_id": reference_id,
        "description": description,
        "metadata": metadata or {},
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        await db[LEDGER_COLLECTION].insert_one(doc)
        return doc
    except DuplicateKeyError:
        logger.info(
            "ledger idempotent no-op: %s/%s/%s already posted",
            entry_type.value, reference_type, reference_id,
        )
        return None


async def list_entries(
    *,
    user_id: str,
    limit: int = 100,
    skip: int = 0,
    entry_type: Optional[LedgerEntryType] = None,
) -> list[dict[str, Any]]:
    """Return ledger entries for a user, newest first."""
    query: dict[str, Any] = {"user_id": user_id}
    if entry_type is not None:
        query["type"] = entry_type.value

    cursor = (
        db[LEDGER_COLLECTION]
        .find(query, {"_id": 0})
        .sort("created_at", -1)
        .skip(int(skip))
        .limit(int(limit))
    )
    return [doc async for doc in cursor]


async def count_entries(*, user_id: str, entry_type: Optional[LedgerEntryType] = None) -> int:
    query: dict[str, Any] = {"user_id": user_id}
    if entry_type is not None:
        query["type"] = entry_type.value
    return await db[LEDGER_COLLECTION].count_documents(query)


async def ensure_indexes() -> None:
    """Create the idempotency + query indexes. Safe to call repeatedly."""
    await db[LEDGER_COLLECTION].create_index(
        [("reference_type", 1), ("reference_id", 1), ("type", 1)],
        unique=True,
        name="ledger_idempotency_unique",
    )
    await db[LEDGER_COLLECTION].create_index(
        [("user_id", 1), ("created_at", -1)],
        name="ledger_by_user_time",
    )
    await db[LEDGER_COLLECTION].create_index(
        [("wallet_id", 1), ("created_at", -1)],
        name="ledger_by_wallet_time",
    )
