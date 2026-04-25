"""
Wallet service — per-user credit balance with reserve-then-settle semantics.

Wallet state lives in the `wallets` collection, one document per user:
    balance_credits   — credits spendable right now
    reserved_credits  — credits held against in-flight inference requests
    status            — "active" | "frozen" | "closed"

The reserve / settle / refund operations are all single atomic `find_one_and_update`
calls, so concurrent requests cannot over-spend even without a MongoDB transaction.
Every mutation is mirrored as an immutable ledger entry (see ledger_service).

Collection: `wallets`
Index: user_id UNIQUE
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Optional

from pymongo import ReturnDocument

from db import db
from services.billing.ledger_service import LedgerEntryType, append_entry
from services.billing.credit_buckets import BUCKETS, empty_buckets, classify_source

logger = logging.getLogger(__name__)

WALLET_COLLECTION = "wallets"
DEFAULT_FREE_GRANT = 50  # credits granted when a wallet is first opened


# ---------------------------------------------------------------------------
# Open / read
# ---------------------------------------------------------------------------

async def ensure_wallet(user_id: str, *, initial_credits: int = DEFAULT_FREE_GRANT) -> dict[str, Any]:
    """
    Return the wallet for `user_id`, creating it with an initial grant if absent.
    Safe to call on every authenticated request. Also back-fills the per-bucket
    `buckets` sub-document on wallets created before multi-bucket support.
    """
    now = datetime.now(timezone.utc).isoformat()
    existing = await db[WALLET_COLLECTION].find_one({"user_id": user_id}, {"_id": 0})
    if existing:
        # Back-fill buckets on pre-multi-bucket wallets so every reserve
        # path can atomically $inc the nested paths without KeyError.
        if not existing.get("buckets"):
            legacy_bal = int(existing.get("balance_credits", 0))
            legacy_res = int(existing.get("reserved_credits", 0))
            pools = empty_buckets()
            # Move all legacy credit to the general pool so existing users
            # aren't locked out of any modality.
            pools["general"] = {"balance": legacy_bal, "reserved": legacy_res}
            await db[WALLET_COLLECTION].update_one(
                {"user_id": user_id},
                {"$set": {"buckets": pools, "allow_general_fallback": True,
                          "updated_at": now}},
            )
            existing["buckets"] = pools
            existing["allow_general_fallback"] = True
        return existing

    pools = empty_buckets()
    # Seed the general bucket with the initial grant.
    pools["general"] = {"balance": int(initial_credits), "reserved": 0}
    wallet = {
        "wallet_id": f"wal_{user_id}",
        "user_id": user_id,
        "unit": "credits",
        "balance_credits": int(initial_credits),
        "reserved_credits": 0,
        "buckets": pools,
        "allow_general_fallback": True,
        "status": "active",
        "created_at": now,
        "updated_at": now,
    }
    try:
        await db[WALLET_COLLECTION].insert_one(wallet)
    except Exception:
        # Lost a race — another request opened the wallet first. Read it.
        wallet = await db[WALLET_COLLECTION].find_one({"user_id": user_id}, {"_id": 0}) or wallet

    if initial_credits > 0:
        await append_entry(
            wallet_id=wallet["wallet_id"],
            user_id=user_id,
            entry_type=LedgerEntryType.CREDIT,
            amount_credits=int(initial_credits),
            reference_type="wallet_open_grant",
            reference_id=wallet["wallet_id"],
            description="Initial credit grant on wallet open",
            metadata={"bucket": "general"},
        )
    return wallet


async def get_summary(user_id: str) -> dict[str, Any]:
    """Wallet summary suitable for user-facing /v1/credits.

    Returns aggregate balance + per-bucket balances so the client can
    show both the grand total and the per-modality pool. Keys:
      balance_credits    — SUM across all buckets (legacy field)
      reserved_credits   — SUM of reserves across all buckets
      buckets            — {chat: {balance, reserved}, image: {...}, ...}
      allow_general_fallback — plan flag
    """
    wallet = await ensure_wallet(user_id, initial_credits=0)
    pools = wallet.get("buckets") or empty_buckets()
    # Compute aggregates defensively — the stored `balance_credits` may
    # be stale if a caller only updated a bucket. Recompute from pools.
    total_balance = sum(int((pools.get(b) or {}).get("balance", 0)) for b in BUCKETS)
    total_reserved = sum(int((pools.get(b) or {}).get("reserved", 0)) for b in BUCKETS)
    return {
        "user_id": user_id,
        "wallet_id": wallet["wallet_id"],
        "unit": wallet.get("unit", "credits"),
        "balance_credits": total_balance,
        "reserved_credits": total_reserved,
        "status": wallet.get("status", "active"),
        "buckets": {b: dict(pools.get(b) or {"balance": 0, "reserved": 0}) for b in BUCKETS},
        "allow_general_fallback": bool(wallet.get("allow_general_fallback", True)),
    }


async def bucket_balance(user_id: str, bucket: str) -> dict[str, int]:
    """Return {balance, reserved} for one specific bucket."""
    await ensure_wallet(user_id, initial_credits=0)
    row = await db[WALLET_COLLECTION].find_one(
        {"user_id": user_id}, {"_id": 0, f"buckets.{bucket}": 1}
    )
    p = ((row or {}).get("buckets") or {}).get(bucket) or {"balance": 0, "reserved": 0}
    return {"balance": int(p.get("balance", 0)), "reserved": int(p.get("reserved", 0))}


# ---------------------------------------------------------------------------
# Mutating flows — all atomic via find_one_and_update
# ---------------------------------------------------------------------------

async def grant(
    user_id: str,
    amount: int,
    *,
    reference_type: str,
    reference_id: str,
    description: str = "",
    metadata: Optional[dict[str, Any]] = None,
    bucket: Optional[str] = None,
) -> dict[str, Any]:
    """
    Add credits to a wallet. `bucket` selects the pool (chat/vibe/image/…).
    Defaults to `general` — back-compat for every existing call site that
    doesn't yet specify a bucket.

    Idempotent on (reference_type, reference_id) via the ledger unique
    index — a duplicate call is a no-op.
    """
    if amount <= 0:
        raise ValueError("grant amount must be positive")

    await ensure_wallet(user_id, initial_credits=0)
    target_bucket = bucket if bucket in BUCKETS else "general"

    # Ledger first — if the entry already exists, short-circuit before touching balance.
    entry = await append_entry(
        wallet_id=f"wal_{user_id}",
        user_id=user_id,
        entry_type=LedgerEntryType.CREDIT,
        amount_credits=int(amount),
        reference_type=reference_type,
        reference_id=reference_id,
        description=description,
        metadata={**(metadata or {}), "bucket": target_bucket},
    )
    if entry is None:
        return await get_summary(user_id)

    now = datetime.now(timezone.utc).isoformat()
    await db[WALLET_COLLECTION].update_one(
        {"user_id": user_id},
        {
            "$inc": {
                "balance_credits": int(amount),                          # legacy sum
                f"buckets.{target_bucket}.balance": int(amount),        # per-pool
            },
            "$set": {"updated_at": now},
        },
    )
    return await get_summary(user_id)


async def grant_buckets(
    user_id: str,
    pools: dict[str, int],
    *,
    reference_type: str,
    reference_id: str,
    description: str = "",
    metadata: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Grant multiple buckets in one atomic update. Used when a plan
    renewal tops up chat + vibe + image + video + voice + stt + agent_sop
    allowances together so the ledger shows one CREDIT per bucket and the
    wallet update is a single $inc.
    """
    clean: dict[str, int] = {}
    for b, amt in (pools or {}).items():
        if b in BUCKETS and int(amt) > 0:
            clean[b] = int(amt)
    if not clean:
        return await get_summary(user_id)

    await ensure_wallet(user_id, initial_credits=0)

    # One ledger entry per bucket — keeps attribution clean + preserves
    # idempotency per bucket (reference_id composed with bucket name).
    for b, amt in clean.items():
        await append_entry(
            wallet_id=f"wal_{user_id}",
            user_id=user_id,
            entry_type=LedgerEntryType.CREDIT,
            amount_credits=amt,
            reference_type=reference_type,
            reference_id=f"{reference_id}:{b}",
            description=description or f"Bucket grant: {b}",
            metadata={**(metadata or {}), "bucket": b},
        )

    total = sum(clean.values())
    now = datetime.now(timezone.utc).isoformat()
    inc: dict[str, int] = {"balance_credits": total}
    for b, amt in clean.items():
        inc[f"buckets.{b}.balance"] = amt
    await db[WALLET_COLLECTION].update_one(
        {"user_id": user_id},
        {"$inc": inc, "$set": {"updated_at": now}},
    )
    return await get_summary(user_id)


async def _try_reserve_from_bucket(
    user_id: str, bucket: str, amount: int, now: str,
) -> Optional[dict[str, Any]]:
    """Atomic CAS reserve from one specific bucket. Returns the wallet
    post-reserve, or None if the bucket can't cover `amount`.
    """
    return await db[WALLET_COLLECTION].find_one_and_update(
        {
            "user_id": user_id,
            "status": "active",
            f"buckets.{bucket}.balance": {"$gte": int(amount)},
        },
        {
            "$inc": {
                f"buckets.{bucket}.balance":  -int(amount),
                f"buckets.{bucket}.reserved": int(amount),
                "balance_credits":            -int(amount),     # aggregate mirror
                "reserved_credits":           int(amount),
            },
            "$set": {"updated_at": now},
        },
        projection={"_id": 0},
        return_document=ReturnDocument.AFTER,
    )


async def reserve(
    user_id: str,
    amount: int,
    *,
    reference_id: str,
    description: str = "",
    metadata: Optional[dict[str, Any]] = None,
    bucket: Optional[str] = None,
    source: Optional[str] = None,
) -> Optional[dict[str, Any]]:
    """
    Hold `amount` credits against an in-flight inference request.

    Bucket resolution order:
      1. explicit `bucket` kwarg (if in BUCKETS)
      2. `classify_source(source)` — inspects the source tag (e.g.
         "vibe.create" → vibe bucket, "office_sop:*" → agent_sop)
      3. "general" — catch-all

    If the resolved bucket can't cover `amount` AND the wallet has
    `allow_general_fallback=True`, falls through to the general pool.
    Finally, tries auto-topup before giving up.

    Returns updated summary or None if still uncovered.
    """
    if amount <= 0:
        raise ValueError("reserve amount must be positive")

    wallet = await ensure_wallet(user_id, initial_credits=0)
    now = datetime.now(timezone.utc).isoformat()

    resolved = classify_source(source, bucket)
    charged_bucket = resolved
    updated = await _try_reserve_from_bucket(user_id, resolved, amount, now)

    # Fall through to general if the specific pool is dry + plan allows.
    if updated is None and resolved != "general" and wallet.get("allow_general_fallback", True):
        updated = await _try_reserve_from_bucket(user_id, "general", amount, now)
        if updated is not None:
            charged_bucket = "general"

    # Auto-topup as the last resort — any bucket; re-route through resolution.
    if updated is None:
        try:
            from services.billing import auto_topup
            topup = await auto_topup.maybe_topup(user_id)
            if topup.get("ok"):
                updated = await _try_reserve_from_bucket(user_id, resolved, amount, now)
                charged_bucket = resolved
                if updated is None and resolved != "general":
                    updated = await _try_reserve_from_bucket(user_id, "general", amount, now)
                    if updated is not None:
                        charged_bucket = "general"
        except Exception:
            pass

    if updated is None:
        return None

    await append_entry(
        wallet_id=updated["wallet_id"],
        user_id=user_id,
        entry_type=LedgerEntryType.RESERVE,
        amount_credits=int(amount),
        reference_type="inference_request",
        reference_id=reference_id,
        description=description or "Credits reserved for inference",
        metadata={**(metadata or {}), "bucket": charged_bucket,
                  "requested_bucket": resolved},
    )
    # Stash the bucket actually charged on the wallet for the settle() path
    # so we settle the same pool we reserved.
    await db[WALLET_COLLECTION].update_one(
        {"user_id": user_id},
        {"$set": {f"bucket_pending.{reference_id}": charged_bucket}},
    )
    return await get_summary(user_id)


async def _pending_bucket(user_id: str, reference_id: str) -> str:
    """Read which bucket the matching reserve() used so we settle to the
    same pool. Defaults to `general` if we can't find the stash (legacy
    reserves made before multi-bucket)."""
    row = await db[WALLET_COLLECTION].find_one(
        {"user_id": user_id}, {"_id": 0, f"bucket_pending.{reference_id}": 1}
    )
    bp = ((row or {}).get("bucket_pending") or {})
    return bp.get(reference_id) or "general"


async def settle(
    user_id: str,
    *,
    reserved_amount: int,
    actual_amount: int,
    reference_id: str,
    description: str = "",
    metadata: Optional[dict[str, Any]] = None,
    bucket: Optional[str] = None,
) -> dict[str, Any]:
    """
    Close out a previously-reserved hold. Bucket defaults to the one used
    at reserve() time (stashed in `bucket_pending.<ref_id>`). Every
    bucket's balance/reserved is updated atomically alongside the
    aggregate `balance_credits` / `reserved_credits` legacy fields.
    """
    if reserved_amount < 0 or actual_amount < 0:
        raise ValueError("amounts must be non-negative")

    await ensure_wallet(user_id, initial_credits=0)
    now = datetime.now(timezone.utc).isoformat()
    shortfall = 0
    # Prefer the bucket we actually reserved against (stash wins over
    # caller override) — otherwise fallback-routed reserves produce
    # negative `reserved` in the caller's intended bucket. The stash
    # records what `_try_reserve_from_bucket` actually debited.
    stash_bucket = await _pending_bucket(user_id, reference_id)
    if stash_bucket in BUCKETS:
        target = stash_bucket
    elif bucket in BUCKETS:
        target = bucket
    else:
        target = "general"
    bal_path = f"buckets.{target}.balance"
    res_path = f"buckets.{target}.reserved"

    if actual_amount <= reserved_amount:
        release_amount = reserved_amount - actual_amount
        await db[WALLET_COLLECTION].update_one(
            {"user_id": user_id},
            {
                "$inc": {
                    res_path:            -int(reserved_amount),
                    bal_path:            int(release_amount),
                    "reserved_credits":  -int(reserved_amount),
                    "balance_credits":   int(release_amount),
                },
                "$set": {"updated_at": now},
                "$unset": {f"bucket_pending.{reference_id}": ""},
            },
        )
    else:
        overage = actual_amount - reserved_amount
        # Try to cover overage from the same bucket first.
        updated = await db[WALLET_COLLECTION].find_one_and_update(
            {
                "user_id": user_id,
                bal_path:   {"$gte": int(overage)},
            },
            {
                "$inc": {
                    res_path:           -int(reserved_amount),
                    bal_path:           -int(overage),
                    "reserved_credits": -int(reserved_amount),
                    "balance_credits":  -int(overage),
                },
                "$set": {"updated_at": now},
                "$unset": {f"bucket_pending.{reference_id}": ""},
            },
            projection={"_id": 0},
            return_document=ReturnDocument.AFTER,
        )
        if updated is None and target != "general":
            # Fall through to general pool for the overage.
            updated = await db[WALLET_COLLECTION].find_one_and_update(
                {
                    "user_id": user_id,
                    "buckets.general.balance": {"$gte": int(overage)},
                },
                {
                    "$inc": {
                        res_path:                      -int(reserved_amount),
                        "buckets.general.balance":     -int(overage),
                        "reserved_credits":            -int(reserved_amount),
                        "balance_credits":             -int(overage),
                    },
                    "$set": {"updated_at": now},
                    "$unset": {f"bucket_pending.{reference_id}": ""},
                },
                projection={"_id": 0},
                return_document=ReturnDocument.AFTER,
            )
        if updated is None:
            # No pool covered overage — record shortfall + drop the reserve.
            await db[WALLET_COLLECTION].update_one(
                {"user_id": user_id},
                {
                    "$inc": {
                        res_path:           -int(reserved_amount),
                        "reserved_credits": -int(reserved_amount),
                    },
                    "$set": {"updated_at": now},
                    "$unset": {f"bucket_pending.{reference_id}": ""},
                },
            )
            shortfall = overage
            actual_amount = reserved_amount
        release_amount = 0

    wallet_id = f"wal_{user_id}"
    if actual_amount > 0:
        await append_entry(
            wallet_id=wallet_id,
            user_id=user_id,
            entry_type=LedgerEntryType.DEBIT,
            amount_credits=int(actual_amount),
            reference_type="inference_request",
            reference_id=reference_id,
            description=description or "Credits debited for inference",
            metadata={**(metadata or {}), "bucket": target,
                      **({"shortfall_credits": shortfall} if shortfall else {})},
        )
    if release_amount > 0:
        await append_entry(
            wallet_id=wallet_id,
            user_id=user_id,
            entry_type=LedgerEntryType.RELEASE,
            amount_credits=int(release_amount),
            reference_type="inference_request",
            reference_id=reference_id,
            description="Unused reserve returned to balance",
            metadata={**(metadata or {}), "bucket": target},
        )
    return await get_summary(user_id)


async def refund(
    user_id: str,
    *,
    reserved_amount: int,
    reference_id: str,
    description: str = "",
    metadata: Optional[dict[str, Any]] = None,
    bucket: Optional[str] = None,
) -> dict[str, Any]:
    """
    Fully return a reserved hold to the same bucket it came from.
    Caller may override the bucket explicitly; otherwise we look up
    the bucket we stashed at reserve() time.
    """
    if reserved_amount <= 0:
        raise ValueError("reserved_amount must be positive")

    now = datetime.now(timezone.utc).isoformat()
    # Same "stash wins" rule as settle() so fallback-routed reserves
    # refund against the pool they were actually debited from.
    stash_bucket = await _pending_bucket(user_id, reference_id)
    if stash_bucket in BUCKETS:
        target = stash_bucket
    elif bucket in BUCKETS:
        target = bucket
    else:
        target = "general"
    await db[WALLET_COLLECTION].update_one(
        {"user_id": user_id},
        {
            "$inc": {
                f"buckets.{target}.reserved": -int(reserved_amount),
                f"buckets.{target}.balance":  int(reserved_amount),
                "reserved_credits":            -int(reserved_amount),
                "balance_credits":             int(reserved_amount),
            },
            "$set": {"updated_at": now},
            "$unset": {f"bucket_pending.{reference_id}": ""},
        },
    )
    await append_entry(
        wallet_id=f"wal_{user_id}",
        user_id=user_id,
        entry_type=LedgerEntryType.REFUND,
        amount_credits=int(reserved_amount),
        reference_type="inference_request",
        reference_id=reference_id,
        description=description or "Full reserve refunded — provider call failed",
        metadata={**(metadata or {}), "bucket": target},
    )
    return await get_summary(user_id)


async def adjust(
    user_id: str,
    delta: int,
    *,
    actor_id: str,
    reason: str,
    reference_id: Optional[str] = None,
    metadata: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """
    Operator-initiated manual adjustment. `delta` may be positive (grant) or
    negative (claw-back). All adjustments are recorded with the actor_id for
    audit.
    """
    if delta == 0:
        return await get_summary(user_id)

    await ensure_wallet(user_id, initial_credits=0)
    now = datetime.now(timezone.utc).isoformat()
    reference_id = reference_id or f"adj_{int(datetime.now(timezone.utc).timestamp() * 1000)}"

    if delta > 0:
        await db[WALLET_COLLECTION].update_one(
            {"user_id": user_id},
            {"$inc": {"balance_credits": int(delta)}, "$set": {"updated_at": now}},
        )
    else:
        # Don't let a claw-back drive the wallet negative.
        updated = await db[WALLET_COLLECTION].find_one_and_update(
            {"user_id": user_id, "balance_credits": {"$gte": -int(delta)}},
            {"$inc": {"balance_credits": int(delta)}, "$set": {"updated_at": now}},
            projection={"_id": 0},
            return_document=ReturnDocument.AFTER,
        )
        if updated is None:
            # Clamp to zero to preserve non-negative invariant; record clamped amount.
            wallet = await db[WALLET_COLLECTION].find_one({"user_id": user_id}, {"_id": 0})
            clamped = min(-int(delta), int(wallet.get("balance_credits", 0)))
            await db[WALLET_COLLECTION].update_one(
                {"user_id": user_id},
                {"$inc": {"balance_credits": -clamped}, "$set": {"updated_at": now}},
            )
            delta = -clamped
            metadata = {**(metadata or {}), "clamped_to_zero": True}

    await append_entry(
        wallet_id=f"wal_{user_id}",
        user_id=user_id,
        entry_type=LedgerEntryType.ADJUSTMENT,
        amount_credits=abs(int(delta)),
        reference_type="operator_adjustment",
        reference_id=reference_id,
        description=reason,
        metadata={
            **(metadata or {}),
            "actor_id": actor_id,
            "direction": "credit" if delta > 0 else "debit",
        },
    )
    return await get_summary(user_id)


async def set_status(user_id: str, status: str) -> dict[str, Any]:
    """Freeze / unfreeze / close a wallet."""
    allowed = {"active", "frozen", "closed"}
    if status not in allowed:
        raise ValueError(f"status must be one of {allowed}")
    await db[WALLET_COLLECTION].update_one(
        {"user_id": user_id},
        {"$set": {"status": status, "updated_at": datetime.now(timezone.utc).isoformat()}},
    )
    return await get_summary(user_id)


# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------

async def ensure_indexes() -> None:
    await db[WALLET_COLLECTION].create_index(
        "user_id", unique=True, name="wallet_user_id_unique",
    )
