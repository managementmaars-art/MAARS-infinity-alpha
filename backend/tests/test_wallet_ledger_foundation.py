"""
Smoke tests for the wallet + ledger + api-key foundation.

Hits MongoDB directly; skipped if MONGO_URL is unset. Uses asyncio.run() so
this file doesn't depend on pytest-asyncio.
"""
from __future__ import annotations

import asyncio
import os

import pytest

from services.billing import ledger_service, wallet_service
from services.api_key_service import create_key, find_by_raw_key, revoke
from services.billing.ledger_service import LedgerEntryType

pytestmark = pytest.mark.skipif(
    not os.environ.get("MONGO_URL"),
    reason="MONGO_URL not configured — skipping DB-backed smoke tests",
)


from tests.conftest import MAARS_TEST_LOOP  # shared across the whole test session


def _run(coro):
    return MAARS_TEST_LOOP.run_until_complete(coro)


async def _reset(user_id: str) -> None:
    """Fresh-state the user before a test and ensure unique indexes exist."""
    from db import db
    await ledger_service.ensure_indexes()
    await wallet_service.ensure_indexes()
    await db.wallets.delete_one({"user_id": user_id})
    await db.ledger_entries.delete_many({"user_id": user_id})


def test_reserve_settle_happy_path():
    user_id = f"test_user_reserve_{os.getpid()}"

    async def scenario():
        await _reset(user_id)
        await wallet_service.ensure_wallet(user_id, initial_credits=1000)

        reserved = await wallet_service.reserve(user_id, 100, reference_id=f"{user_id}_req1")
        assert reserved is not None
        assert reserved["balance_credits"] == 900
        assert reserved["reserved_credits"] == 100

        settled = await wallet_service.settle(
            user_id, reserved_amount=100, actual_amount=40, reference_id=f"{user_id}_req1",
        )
        assert settled["balance_credits"] == 960
        assert settled["reserved_credits"] == 0

        entries = await ledger_service.list_entries(user_id=user_id, limit=10)
        return [e["type"] for e in entries]

    types = _run(scenario())
    assert "DEBIT" in types and "RELEASE" in types and "RESERVE" in types


def test_reserve_rejected_on_insufficient_balance():
    user_id = f"test_user_reject_{os.getpid()}"

    async def scenario():
        await _reset(user_id)
        await wallet_service.ensure_wallet(user_id, initial_credits=10)
        return await wallet_service.reserve(user_id, 999, reference_id=f"{user_id}_req")

    assert _run(scenario()) is None


def test_refund_returns_reserve():
    user_id = f"test_user_refund_{os.getpid()}"

    async def scenario():
        await _reset(user_id)
        await wallet_service.ensure_wallet(user_id, initial_credits=500)
        await wallet_service.reserve(user_id, 200, reference_id=f"{user_id}_r")
        return await wallet_service.refund(user_id, reserved_amount=200, reference_id=f"{user_id}_r")

    refunded = _run(scenario())
    assert refunded["balance_credits"] == 500
    assert refunded["reserved_credits"] == 0


def test_ledger_idempotency():
    user_id = f"test_user_idem_{os.getpid()}"

    async def scenario():
        await _reset(user_id)
        await wallet_service.ensure_wallet(user_id, initial_credits=0)
        first = await ledger_service.append_entry(
            wallet_id=f"wal_{user_id}", user_id=user_id,
            entry_type=LedgerEntryType.CREDIT, amount_credits=50,
            reference_type="test", reference_id=f"idem_{user_id}",
            description="first",
        )
        second = await ledger_service.append_entry(
            wallet_id=f"wal_{user_id}", user_id=user_id,
            entry_type=LedgerEntryType.CREDIT, amount_credits=50,
            reference_type="test", reference_id=f"idem_{user_id}",
            description="replay — should be no-op",
        )
        return first, second

    first, second = _run(scenario())
    assert first is not None
    assert second is None


def test_api_key_roundtrip_and_revoke():
    user_id = f"test_user_key_{os.getpid()}"

    async def scenario():
        from db import db
        await db.api_keys.delete_many({"user_id": user_id})
        result = await create_key(user_id, name="smoke-test")
        raw = result["raw_key"]
        key_id = result["api_key_id"]
        looked_up = await find_by_raw_key(raw)
        revoked_ok = await revoke(key_id, user_id)
        after = await find_by_raw_key(raw)
        return raw, looked_up, revoked_ok, after

    raw, looked_up, revoked_ok, after = _run(scenario())
    assert looked_up is not None
    assert looked_up["user_id"] == user_id
    assert looked_up["last4"] == raw[-4:]
    assert revoked_ok is True
    assert after is None
