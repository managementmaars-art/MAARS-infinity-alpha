"""
Seed a deterministic test user, mint a fresh API key, and top the wallet up
to at least 50 credits. Prints the raw key on the last line so setup.sh can
grep it out.

Idempotent — re-running revokes old keys for this user and issues a fresh one,
leaving the wallet at ≥ 50 credits.

Usage:
    cd backend && python -m scripts.seed_test_user [--email test@maars.local]
"""
from __future__ import annotations

import argparse
import asyncio
import logging
import uuid
from datetime import datetime, timezone

from db import db
from services import api_key_service
from services.billing import ledger_service, wallet_service

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)s  %(message)s")
log = logging.getLogger("seed_test_user")

TARGET_CREDITS = 50


async def ensure_user(email: str, name: str) -> str:
    existing = await db.users.find_one({"email": email}, {"_id": 0, "user_id": 1})
    if existing:
        return existing["user_id"]
    user_id = f"user_{uuid.uuid4().hex[:12]}"
    await db.users.insert_one({
        "user_id": user_id,
        "email": email,
        "name": name,
        "password_hash": "",
        "picture": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    log.info("created user %s (%s)", user_id, email)
    return user_id


async def revoke_existing_keys(user_id: str) -> int:
    res = await db.api_keys.update_many(
        {"user_id": user_id, "status": "active"},
        {"$set": {"status": "revoked", "revoked_at": datetime.now(timezone.utc).isoformat()}},
    )
    return res.modified_count


async def ensure_min_credits(user_id: str, minimum: int) -> dict:
    summary = await wallet_service.get_summary(user_id)
    if summary["balance_credits"] >= minimum:
        return summary
    delta = minimum - summary["balance_credits"]
    return await wallet_service.grant(
        user_id,
        delta,
        reference_type="seed_test_user",
        reference_id=f"seed_{user_id}_{int(datetime.now(timezone.utc).timestamp())}",
        description=f"Seed top-up to {minimum} credits",
    )


async def main(email: str, name: str) -> None:
    await wallet_service.ensure_indexes()
    await ledger_service.ensure_indexes()
    await api_key_service.ensure_indexes()

    user_id = await ensure_user(email, name)
    revoked = await revoke_existing_keys(user_id)
    if revoked:
        log.info("revoked %d prior active key(s) for %s", revoked, user_id)

    await wallet_service.ensure_wallet(user_id, initial_credits=0)
    summary = await ensure_min_credits(user_id, TARGET_CREDITS)

    key = await api_key_service.create_key(user_id, name="setup.sh", plan_id="free")

    log.info("user_id=%s balance=%s credits", user_id, summary["balance_credits"])
    print(f"MAARS_USER_ID={user_id}")
    print(f"MAARS_USER_EMAIL={email}")
    print(f"MAARS_BALANCE={summary['balance_credits']}")
    print(f"MAARS_API_KEY={key['raw_key']}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--email", default="test@maars.local")
    ap.add_argument("--name", default="MAARS Test User")
    args = ap.parse_args()
    asyncio.run(main(args.email, args.name))
