"""Lifetime Deal (LTD) tier — one-time payment for permanent access.

Bootstrapped-SaaS classic. Draws early-adopter cash the week you
launch, locks them in as a reference customer, seeds reviews/tweets.

Pricing math:
  - LTD price = Starter annual × 3  (≈3 years of value, front-loaded)
  - Credits: Starter annual × 3 initially, then Starter monthly forever
  - Refund policy: 60 days no-questions, then final
  - Features: all current Starter-tier features; NOT automatically
    upgraded when new tiers ship (no "free upgrades forever")

Setup:
  1. Enable by setting MAARS_LTD_ENABLED=1
  2. Tune price: MAARS_LTD_PRICE_USD (default 497)
  3. Monthly credits granted after initial batch:
     MAARS_LTD_MONTHLY_CREDITS (default same as Starter)
  4. Cap total sold: MAARS_LTD_INVENTORY (default 100 — scarcity)

The orchestration (Stripe price, wallet grant, flag in user record)
is handled here so the frontend just shows a Buy LTD button when
is_available() returns True.
"""
from __future__ import annotations
import os
from datetime import datetime, timezone


def is_enabled() -> bool:
    return os.environ.get("MAARS_LTD_ENABLED", "0") == "1"


def ltd_config() -> dict:
    return {
        "enabled": is_enabled(),
        "price_usd": float(os.environ.get("MAARS_LTD_PRICE_USD", "497")),
        "initial_credits": int(os.environ.get("MAARS_LTD_INITIAL_CREDITS", "18000")),
        "monthly_credits": int(os.environ.get("MAARS_LTD_MONTHLY_CREDITS", "500")),
        "inventory_cap": int(os.environ.get("MAARS_LTD_INVENTORY", "100")),
        "refund_days": int(os.environ.get("MAARS_LTD_REFUND_DAYS", "60")),
        "tagline": os.environ.get("MAARS_LTD_TAGLINE", "Pay once. Keep forever."),
    }


async def remaining_inventory() -> int:
    """How many LTD slots left. Returns -1 if unlimited."""
    from db import db
    cap = ltd_config()["inventory_cap"]
    if cap <= 0:
        return -1
    sold = await db.subscriptions.count_documents({"plan_id": "lifetime"})
    return max(0, cap - sold)


async def is_available() -> bool:
    """Enabled AND has inventory."""
    if not is_enabled():
        return False
    remaining = await remaining_inventory()
    return remaining != 0  # -1 (unlimited) or positive


async def activate_ltd_for_user(user_id: str, stripe_charge_id: str) -> dict:
    """Grant LTD. Called from the Stripe webhook on LTD product purchase."""
    from db import db
    from services.billing import wallet_service
    cfg = ltd_config()
    now = datetime.now(timezone.utc).isoformat()

    # Flag subscription as lifetime
    await db.subscriptions.update_one(
        {"user_id": user_id},
        {"$set": {
            "user_id": user_id,
            "plan_id": "lifetime",
            "status": "active",
            "activated_at": now,
            "stripe_charge_id": stripe_charge_id,
            "monthly_credit_grant": cfg["monthly_credits"],
        }},
        upsert=True,
    )
    # Grant initial credits
    try:
        await wallet_service.grant(
            user_id=user_id,
            amount=cfg["initial_credits"],
            reason="ltd_initial",
        )
    except Exception:
        pass
    return {"ok": True, "plan": "lifetime", "initial_credits": cfg["initial_credits"]}
