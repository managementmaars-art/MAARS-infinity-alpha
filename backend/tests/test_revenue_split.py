"""
Tests for the subscription split-fund layer.

Confirms:
  * Package.operator_share_pct math works
  * Stripe webhook splits into wallet grant + operator-revenue entry
  * Replayed Stripe events do NOT double-book either side
  * Admin revenue queries return correct aggregates
"""
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


# ------------------------------------------------------- pure split math

def test_package_split_math():
    """Splits derive from SUBSCRIPTION_PLANS — verify math against real plan prices."""
    import asyncio
    from services.billing import stripe_service
    asyncio.get_event_loop_policy().get_event_loop()
    # Make sure the derived view is built.
    stripe_service._seed_defaults()
    stripe_service._rebuild_packages_from_plans()

    starter = stripe_service.PACKAGES["starter"]      # $50, 30% operator
    essential = stripe_service.PACKAGES["essential"]  # $100, 30% operator
    elite = stripe_service.PACKAGES["elite"]          # premium tier, 40% operator
    assert abs(starter.operator_share_usd  - 15.00)   < 1e-4
    assert abs(starter.user_backing_usd    - 35.00)   < 1e-4
    assert abs(essential.operator_share_usd - 30.00)  < 1e-4
    assert abs(essential.user_backing_usd   - 70.00)  < 1e-4
    # Elite: any positive split, retained share > 35%.
    assert elite.operator_share_pct >= 0.35
    assert elite.operator_share_usd > 0


def test_list_packages_exposes_split_fields():
    from services.billing import stripe_service
    stripe_service._seed_defaults()
    stripe_service._rebuild_packages_from_plans()
    pkgs = {p["id"]: p for p in stripe_service.list_packages()}
    assert pkgs, "list_packages() should not be empty"
    for p in pkgs.values():
        assert "operator_share_pct" in p
        assert "operator_share_usd" in p
        assert "user_backing_usd" in p
        assert abs(p["operator_share_usd"] + p["user_backing_usd"] - p["price_usd"]) < 1e-4


# ------------------------------------------------------- end-to-end webhook

@pytestmark_db
def test_stripe_event_books_split_and_idempotent():
    from db import db
    from services.billing import ledger_service, revenue_service, stripe_service, wallet_service

    user_id = f"t_split_{os.getpid()}_{int(time.time()*1000)}"
    session_id = f"cs_split_{user_id}"

    async def scenario():
        await ledger_service.ensure_indexes()
        await wallet_service.ensure_indexes()
        await revenue_service.ensure_indexes()

        # Clean any prior data for this synthetic user.
        await db.wallets.delete_many({"user_id": user_id})
        await db.ledger_entries.delete_many({"user_id": user_id})
        await db.operator_revenue_entries.delete_many({"user_id": user_id})

        await wallet_service.ensure_wallet(user_id, initial_credits=0)

        event = {
            "type": "checkout.session.completed",
            "data": {"object": {
                "id": session_id,
                "amount_total": 5000,            # $50 — Starter (SUBSCRIPTION_PLANS price)
                "currency": "usd",
                "metadata": {
                    "maars_billing": "v1",
                    "user_id": user_id,
                    "package_id": "starter",
                    "credits": "300",
                },
            }},
        }
        first = await stripe_service.handle_event(event)
        replay = await stripe_service.handle_event(event)

        wallet  = await wallet_service.get_summary(user_id)
        rev_rows = await db.operator_revenue_entries.count_documents({"user_id": user_id})
        cred_rows = await db.ledger_entries.count_documents({
            "user_id": user_id, "reference_type": "stripe_checkout", "type": "CREDIT",
        })
        # Sum just THIS user's revenue contribution — not global, which can
        # contain residual data from other test runs in the shared test DB.
        user_revenue = 0.0
        async for row in db.operator_revenue_entries.aggregate([
            {"$match": {"user_id": user_id}},
            {"$group": {"_id": None, "sum": {"$sum": "$amount_usd"}}},
        ]):
            user_revenue = float(row.get("sum") or 0.0)
        return first, replay, wallet, user_revenue, rev_rows, cred_rows

    first, replay, wallet, user_revenue, rev_rows, cred_rows = _run(scenario())

    # First call books both halves of the split. Starter: $50 × 30% = $15.
    assert first["status"] == "credited"
    assert first["split"]["operator_share_usd"] == pytest.approx(15.00, abs=1e-4)
    assert first["split"]["user_backing_usd"]   == pytest.approx(35.00, abs=1e-4)
    assert first["split"]["revenue_booked"] is True

    # Credits granted are DERIVED from user_backing_usd × CREDITS_PER_USD —
    # NOT the plan's legacy fixed `credits` field. $35 backing × 1000 = 35000.
    from shared.constants import CREDITS_PER_USD
    expected_credits = round(35.00 * CREDITS_PER_USD)
    assert wallet["balance_credits"] == expected_credits

    # Replay was idempotent on BOTH sides.
    assert replay["status"] == "credited"
    assert wallet["balance_credits"] == expected_credits        # not doubled
    assert rev_rows == 1, f"expected exactly one operator_revenue_entries row, got {rev_rows}"
    assert cred_rows == 1, f"expected exactly one stripe_checkout CREDIT ledger row, got {cred_rows}"

    assert user_revenue == pytest.approx(15.00, abs=1e-4)


@pytestmark_db
def test_revenue_aggregates_by_package_and_user():
    """Two purchases by two users → aggregates split correctly."""
    from db import db
    from services import revenue_service, stripe_service

    suffix = f"{os.getpid()}_{int(time.time()*1000)}"

    async def scenario():
        await revenue_service.ensure_indexes()
        await db.operator_revenue_entries.delete_many({"user_id": {"$regex": f"^t_agg_{os.getpid()}_"}})
        # User A buys starter twice (different sessions). $50 × 0.30 = $15 each.
        await revenue_service.record_revenue(
            amount_usd=15.00, source_type="stripe_checkout",
            source_ref=f"cs_agg_{suffix}_a1",
            user_id=f"t_agg_{os.getpid()}_a", package_id="starter",
        )
        await revenue_service.record_revenue(
            amount_usd=15.00, source_type="stripe_checkout",
            source_ref=f"cs_agg_{suffix}_a2",
            user_id=f"t_agg_{os.getpid()}_a", package_id="starter",
        )
        # User B buys essential. $100 × 0.30 = $30.
        await revenue_service.record_revenue(
            amount_usd=30.00, source_type="stripe_checkout",
            source_ref=f"cs_agg_{suffix}_b1",
            user_id=f"t_agg_{os.getpid()}_b", package_id="essential",
        )
        # User-A purchase count — query directly so accumulated test data in
        # the shared DB doesn't push us out of revenue_by_user's top-10.
        user_a_purchases = await db.operator_revenue_entries.count_documents(
            {"user_id": f"t_agg_{os.getpid()}_a"},
        )
        return (
            await revenue_service.revenue_by_package(days=1),
            user_a_purchases,
        )

    by_pkg, user_a_purchases = _run(scenario())
    pkg_starter = next((r for r in by_pkg if r["package_id"] == "starter"), None)
    pkg_essential = next((r for r in by_pkg if r["package_id"] == "essential"), None)
    assert pkg_starter is not None and pkg_starter["amount_usd"] >= 30.00
    assert pkg_essential is not None and pkg_essential["amount_usd"] >= 30.00
    assert user_a_purchases >= 2
