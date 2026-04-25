"""
Migration: bring up the wallet + ledger + hashed-api-key foundation.

Idempotent. Safe to run multiple times. Performs, in order:

    1. Create MongoDB indexes for wallets, ledger_entries, api_keys.
    2. Open a wallet for every existing user (balance seeded from subscriptions.credits).
    3. Post an opening CREDIT ledger entry for each seeded wallet (idempotent).
    4. Migrate `client_gateway_keys` rows whose `key` is still plaintext into the
       new hashed `api_keys` collection, then redact the legacy plaintext column.

Run with:
    cd backend && python -m scripts.migrate_wallets
"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone

from db import db
from services import api_key_service
from services.billing import ledger_service, wallet_service
from services.billing.ledger_service import LedgerEntryType, append_entry

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)s  %(message)s")
log = logging.getLogger("migrate_wallets")


async def step_indexes() -> None:
    log.info("creating indexes…")
    await wallet_service.ensure_indexes()
    await ledger_service.ensure_indexes()
    await api_key_service.ensure_indexes()
    log.info("  → wallets, ledger_entries, api_keys indexes OK")


async def step_open_wallets() -> tuple[int, int]:
    """Open a wallet for every user, seeded from subscriptions.credits."""
    opened = 0
    seeded = 0
    cursor = db.users.find({}, {"_id": 0, "user_id": 1})
    async for user in cursor:
        user_id = user["user_id"]
        existing = await db.wallets.find_one({"user_id": user_id}, {"_id": 0})
        if existing:
            continue

        sub = await db.subscriptions.find_one({"user_id": user_id}, {"_id": 0})
        initial = int((sub or {}).get("credits", 0))
        if initial < 0:
            initial = 0

        # Ensure wallet (no grant yet — we'll post it manually so the reference_id is stable).
        wallet = await wallet_service.ensure_wallet(user_id, initial_credits=0)
        opened += 1

        if initial > 0:
            await append_entry(
                wallet_id=wallet["wallet_id"],
                user_id=user_id,
                entry_type=LedgerEntryType.CREDIT,
                amount_credits=initial,
                reference_type="migration_backfill",
                reference_id=f"backfill_{user_id}",
                description="Initial balance backfilled from subscriptions.credits",
                metadata={"source": "migrate_wallets"},
            )
            await db.wallets.update_one(
                {"user_id": user_id},
                {
                    "$inc": {"balance_credits": initial},
                    "$set": {"updated_at": datetime.now(timezone.utc).isoformat()},
                },
            )
            seeded += 1
    log.info("  → opened %d wallets (%d seeded with balance)", opened, seeded)
    return opened, seeded


async def step_hash_legacy_api_keys() -> int:
    """
    Migrate `client_gateway_keys` plaintext → hashed `api_keys` rows.
    Redacts the plaintext `key` field after copying (replaced with last4-only).
    """
    migrated = 0
    cursor = db.client_gateway_keys.find(
        {"key": {"$regex": r"^maars-sk-"}},
        {"_id": 0},
    )
    async for legacy in cursor:
        raw = legacy.get("key")
        if not raw:
            continue
        # Skip if we already have a matching api_keys row for this user with the same last4.
        last4 = raw[-4:]
        already = await db.api_keys.find_one(
            {"user_id": legacy["user_id"], "last4": last4},
            {"_id": 0, "api_key_id": 1},
        )
        if already:
            # Scrub the plaintext value if not already scrubbed.
            if raw.startswith("maars-sk-"):
                await db.client_gateway_keys.update_one(
                    {"user_id": legacy["user_id"], "key": raw},
                    {"$set": {"key": f"…{last4}", "migrated": True}},
                )
            continue

        # Create a new hashed key row, but copy the plaintext's hash so the raw value still works.
        from services.api_key_service import _hash  # type: ignore
        now = datetime.now(timezone.utc).isoformat()
        import uuid
        doc = {
            "api_key_id": f"ak_{uuid.uuid4().hex[:16]}",
            "user_id": legacy["user_id"],
            "name": "legacy-gateway",
            "key_hash": _hash(raw),
            "last4": last4,
            "plan_id": legacy.get("plan_id", "free"),
            "monthly_budget_usd": float(legacy.get("monthly_budget_usd", 0.0)),
            "used_usd": float(legacy.get("used_usd", 0.0)),
            "cycle_start": legacy.get("cycle_start", now),
            "status": legacy.get("status", "active"),
            "created_at": legacy.get("created_at", now),
            "last_used_at": None,
            "revoked_at": None,
        }
        try:
            await db.api_keys.insert_one(doc)
            migrated += 1
        except Exception as exc:  # duplicate hash — already migrated
            log.debug("skip duplicate hash for user %s: %s", legacy["user_id"], exc)

        # Scrub plaintext.
        await db.client_gateway_keys.update_one(
            {"user_id": legacy["user_id"], "key": raw},
            {"$set": {"key": f"…{last4}", "migrated": True}},
        )
    log.info("  → migrated %d plaintext keys into hashed api_keys", migrated)
    return migrated


async def main() -> None:
    log.info("===  MAARS wallet + ledger + api-key migration  ===")
    await step_indexes()
    opened, seeded = await step_open_wallets()
    migrated = await step_hash_legacy_api_keys()
    log.info("done.  wallets_opened=%d  seeded=%d  keys_migrated=%d", opened, seeded, migrated)


if __name__ == "__main__":
    asyncio.run(main())
