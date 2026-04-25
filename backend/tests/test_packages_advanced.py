"""Phase-9 tests — custom package CRUD, audit trail, per-customer pricing overrides."""
from __future__ import annotations

import os
import time

import pytest

from tests.conftest import MAARS_TEST_LOOP


def _run(coro):
    return MAARS_TEST_LOOP.run_until_complete(coro)


pytestmark_db = pytest.mark.skipif(
    not os.environ.get("MONGO_URL"),
    reason="MONGO_URL not configured",
)


# ──────────────────────────────────────── custom package CRUD

@pytestmark_db
def test_can_add_custom_package_via_apply_overrides():
    from db import db
    from services.billing import stripe_service

    pkg_id = f"enterprise_test_{os.getpid()}"

    async def scenario():
        await stripe_service.reset_overrides()
        await stripe_service.apply_overrides({
            pkg_id: {
                "name": "Enterprise Test", "price_usd": 999.0,
                "credits": 100_000, "operator_share_pct": 0.40,
            },
        })
        return stripe_service.PACKAGES.get(pkg_id)

    custom = _run(scenario())
    assert custom is not None
    assert custom.name == "Enterprise Test"
    assert custom.price_usd == 999.0
    assert custom.credits == 100_000
    assert custom.operator_share_pct == 0.40
    assert custom.operator_share_usd == pytest.approx(399.60, abs=1e-2)


@pytestmark_db
def test_new_custom_package_requires_name_price_credits():
    from services.billing import stripe_service

    async def scenario():
        await stripe_service.reset_overrides()
        try:
            await stripe_service.apply_overrides({
                "missing_required": {"operator_share_pct": 0.50},
            })
            return None
        except ValueError as exc:
            return str(exc)

    err = _run(scenario())
    assert err is not None
    assert "requires" in err


@pytestmark_db
def test_default_packages_cannot_be_deleted():
    from services.billing import stripe_service

    async def scenario():
        try:
            await stripe_service.delete_package("starter")
            return None
        except ValueError as exc:
            return str(exc)

    err = _run(scenario())
    assert err is not None
    assert "default" in err


@pytestmark_db
def test_custom_package_can_be_deleted():
    from services.billing import stripe_service
    pkg_id = f"team_test_{os.getpid()}_{int(time.time()*1000)}"

    async def scenario():
        await stripe_service.apply_overrides({
            pkg_id: {"name": "Team", "price_usd": 99.0, "credits": 12_000, "operator_share_pct": 0.30},
        })
        present = pkg_id in stripe_service.PACKAGES
        ok = await stripe_service.delete_package(pkg_id)
        absent = pkg_id not in stripe_service.PACKAGES
        return present, ok, absent

    present, ok, absent = _run(scenario())
    assert present and ok and absent


# ──────────────────────────────────────── audit trail

@pytestmark_db
def test_apply_overrides_writes_audit_entry():
    from db import db
    from services.billing import stripe_service

    pkg_id = "starter"

    async def scenario():
        # Snapshot current count of audit entries for this target.
        target_type = "subscription_plan"
        before = await db.audit_log.count_documents({"target_type": target_type, "target_id": pkg_id})
        await stripe_service.apply_overrides(
            {pkg_id: {"operator_share_pct": 0.42}},
            actor_id="test_admin",
        )
        after = await db.audit_log.count_documents({"target_type": target_type, "target_id": pkg_id})
        latest = await db.audit_log.find_one(
            {"target_type": target_type, "target_id": pkg_id},
            sort=[("timestamp", -1)],
        )
        return before, after, latest

    before, after, latest = _run(scenario())
    assert after == before + 1
    assert latest is not None
    assert latest["actor_id"] == "test_admin"
    assert latest["action"] == "plan_override_apply"
    assert "after" in latest["details"]


# ──────────────────────────────────────── per-customer pricing

@pytestmark_db
def test_customer_override_upsert_get_delete():
    from services import customer_pricing_service

    user_id = f"t_cust_{os.getpid()}_{int(time.time()*1000)}"

    async def scenario():
        await customer_pricing_service.ensure_indexes()
        rec = await customer_pricing_service.upsert(
            user_id=user_id, package_id="starter",
            operator_share_pct=0.20,
            credits_bonus=500,
            notes="enterprise discount",
            actor_id="test_admin",
        )
        fetched = await customer_pricing_service.get(user_id=user_id, package_id="starter")
        # Update one field — the others must be preserved.
        await customer_pricing_service.upsert(
            user_id=user_id, package_id="starter", operator_share_pct=0.15,
        )
        merged = await customer_pricing_service.get(user_id=user_id, package_id="starter")
        deleted = await customer_pricing_service.delete(user_id=user_id, package_id="starter")
        absent = await customer_pricing_service.get(user_id=user_id, package_id="starter")
        return rec, fetched, merged, deleted, absent

    rec, fetched, merged, deleted, absent = _run(scenario())
    assert rec["operator_share_pct"] == 0.20
    assert fetched["credits_bonus"] == 500
    assert merged["operator_share_pct"] == 0.15        # updated
    assert merged["credits_bonus"] == 500              # preserved
    assert deleted is True
    assert absent is None


@pytestmark_db
def test_expired_override_returns_none():
    from datetime import datetime, timedelta, timezone
    from services import customer_pricing_service

    user_id = f"t_exp_{os.getpid()}"

    async def scenario():
        await customer_pricing_service.ensure_indexes()
        past = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        await customer_pricing_service.upsert(
            user_id=user_id, package_id="starter",
            operator_share_pct=0.10,
            expires_at=past,
        )
        return await customer_pricing_service.get(user_id=user_id, package_id="starter")

    assert _run(scenario()) is None


@pytestmark_db
def test_stripe_webhook_applies_customer_override():
    """An active per-customer override must beat the package default in handle_event()."""
    from db import db
    from services import customer_pricing_service, stripe_service, wallet_service

    user_id = f"t_overflow_{os.getpid()}_{int(time.time()*1000)}"
    session_id = f"cs_overflow_{user_id}"

    async def scenario():
        # Clean state.
        await db.wallets.delete_many({"user_id": user_id})
        await db.ledger_entries.delete_many({"user_id": user_id})
        await db.operator_revenue_entries.delete_many({"user_id": user_id})
        await customer_pricing_service.ensure_indexes()
        await wallet_service.ensure_wallet(user_id, initial_credits=0)

        # Customer gets 10% operator share + 1000 bonus credits.
        await customer_pricing_service.upsert(
            user_id=user_id, package_id="starter",
            operator_share_pct=0.10,
            credits_bonus=1000,
        )
        result = await stripe_service.handle_event({
            "type": "checkout.session.completed",
            "data": {"object": {
                "id": session_id, "amount_total": 4900, "currency": "usd",
                "metadata": {
                    "maars_billing": "v1", "user_id": user_id,
                    "package_id": "starter", "credits": "6000",
                },
            }},
        })
        wallet = await wallet_service.get_summary(user_id)
        return result, wallet

    result, wallet = _run(scenario())
    # Operator share is 10% of $49 = $4.90 (NOT the 30% default = $14.70)
    assert result["split"]["operator_share_pct"] == pytest.approx(0.10, abs=1e-6)
    assert result["split"]["operator_share_usd"] == pytest.approx(4.90, abs=1e-4)
    # Credits derived from user_backing_usd × CREDITS_PER_USD, then the
    # customer override's credits_bonus is added on top.
    # backing = $49 × 0.90 = $44.10 → 44100 credits  + 1000 bonus = 45100
    from shared.constants import CREDITS_PER_USD
    expected = round(49.0 * 0.90 * CREDITS_PER_USD) + 1000
    assert wallet["balance_credits"] == expected
    # The split block reports the override that was applied.
    co = result["split"]["customer_override_applied"]
    assert co is not None
    assert co["operator_share_pct"] == 0.10
    assert co["credits_bonus"] == 1000
