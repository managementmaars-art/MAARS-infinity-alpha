"""Owner-editable subscription splits — tests for stripe_service.apply_overrides()."""
from __future__ import annotations

import os

import pytest

from tests.conftest import MAARS_TEST_LOOP


def _run(coro):
    return MAARS_TEST_LOOP.run_until_complete(coro)


pytestmark_db = pytest.mark.skipif(
    not os.environ.get("MONGO_URL"),
    reason="MONGO_URL not configured",
)


@pytestmark_db
def test_apply_overrides_persists_and_applies():
    from db import db
    from services.billing import stripe_service

    async def scenario():
        await db.platform_config.delete_one({"config_type": "stripe_packages"})
        # Make sure we start at defaults.
        await stripe_service.reset_overrides()
        original_pro = stripe_service.PACKAGES["starter"].operator_share_pct

        # Bump pro to 50%.
        result = await stripe_service.apply_overrides({
            "starter": {"operator_share_pct": 0.50},
        })
        new_pro = stripe_service.PACKAGES["starter"]
        return original_pro, new_pro, result

    original_pro, new_pro, result = _run(scenario())
    assert original_pro == 0.30
    assert new_pro.operator_share_pct == 0.50
    assert new_pro.operator_share_usd == pytest.approx(25.00, abs=1e-4)   # $50 × 0.50
    pro_row = next(r for r in result if r["id"] == "starter")
    assert pro_row["operator_share_pct"] == 0.50


@pytestmark_db
def test_apply_overrides_clamps_pct_into_valid_range():
    """Out-of-range share % gets clamped server-side (Pydantic also rejects, but model layer is defensive)."""
    from services.billing import stripe_service

    async def scenario():
        await stripe_service.reset_overrides()
        await stripe_service.apply_overrides({"starter": {"operator_share_pct": 1.7}})
        too_high = stripe_service.PACKAGES["starter"].operator_share_pct
        await stripe_service.apply_overrides({"starter": {"operator_share_pct": -0.1}})
        too_low = stripe_service.PACKAGES["starter"].operator_share_pct
        return too_high, too_low

    too_high, too_low = _run(scenario())
    assert too_high == 1.0
    assert too_low == 0.0


@pytestmark_db
def test_load_overrides_from_db_at_startup():
    """A fresh process must pick up persisted overrides via apply_overrides() →
    SUBSCRIPTION_PLANS → derived PACKAGES."""
    from db import db
    from services.billing import stripe_service
    from shared import constants

    async def scenario():
        # Wipe whatever's in the unified pricing config.
        await db.platform_config.delete_one({"config_type": "pricing"})
        # Persist an override directly via the unified path.
        await stripe_service.apply_overrides(
            {"starter": {"operator_share_pct": 0.45, "price_usd": 12.0}},
        )
        # Simulate fresh process: reload the constants module to drop the in-memory
        # mutation, then re-apply by reading the DB doc back through server-side
        # logic equivalent.
        import importlib
        importlib.reload(constants)
        # Re-merge the persisted doc into the freshly-reloaded SUBSCRIPTION_PLANS
        # (this is what server.py does at startup).
        doc = await db.platform_config.find_one({"config_type": "pricing"}, {"_id": 0})
        if doc and doc.get("plans"):
            for pid, fields in doc["plans"].items():
                if pid in constants.SUBSCRIPTION_PLANS:
                    constants.SUBSCRIPTION_PLANS[pid].update(fields)
                else:
                    constants.SUBSCRIPTION_PLANS[pid] = dict(fields)
        await stripe_service.load_overrides_from_db()
        return stripe_service.PACKAGES["starter"]

    starter = _run(scenario())
    assert starter.operator_share_pct == 0.45
    assert starter.price_usd == 12.0


@pytestmark_db
def test_reset_overrides_returns_to_defaults():
    from services.billing import stripe_service

    async def scenario():
        await stripe_service.apply_overrides({"elite": {"operator_share_pct": 0.80}})
        before_reset = stripe_service.PACKAGES["elite"].operator_share_pct
        await stripe_service.reset_overrides()
        after_reset = stripe_service.PACKAGES["elite"].operator_share_pct
        return before_reset, after_reset

    before, after = _run(scenario())
    assert before == 0.80
    assert after == 0.40   # original elite (premium-tier) default
