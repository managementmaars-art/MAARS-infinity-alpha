"""
Stripe billing — checkout session creation + webhook handling.

This service complements the existing `routes/subscriptions.py` (built on
`emergentintegrations`). It exposes a cleaner `/billing/*` surface using the
standard `stripe` Python SDK with proper webhook signature verification.

Credit allocation goes through `wallet_service.grant`, whose idempotency is
enforced by the ledger's unique index on (reference_type, reference_id, type).
A retried Stripe delivery of the same event is a no-op.
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any, Optional

import stripe

from services import customer_pricing_service, revenue_service
from services.billing import wallet_service

logger = logging.getLogger(__name__)


STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")

if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY


# ----------------------------------------------------------------- packages

@dataclass(frozen=True)
class Package:
    id: str
    name: str
    price_usd: float
    credits: int
    # Subscription split: fraction of price_usd that's booked as operator
    # revenue / profit pool. The remainder backs the user's credits (covers
    # the provider call costs we'll incur on their behalf). Tunable per-package.
    operator_share_pct: float = 0.30

    @property
    def operator_share_usd(self) -> float:
        return round(self.price_usd * self.operator_share_pct, 6)

    @property
    def user_backing_usd(self) -> float:
        return round(self.price_usd * (1.0 - self.operator_share_pct), 6)


# PACKAGES is now a *derived view* of shared.constants.SUBSCRIPTION_PLANS.
# One source of truth: the existing pricing manager already loads
# SUBSCRIPTION_PLANS overrides from `platform_config` at startup
# (server.py: "Loaded pricing from database"), so apply_overrides() / the
# admin pricing endpoints stay in sync automatically.
#
# `_DEFAULT_PACKAGES` is kept for code paths that need the original code-time
# defaults (e.g., delete_package guard against deleting a default tier).

_DEFAULT_PACKAGES: dict[str, Package] = {}  # populated lazily by _seed_defaults()
PACKAGES: dict[str, Package] = {}


_PLATFORM_CONFIG_KEY = "pricing"   # unified — was "stripe_packages"


def _plan_to_package(pid: str, plan: dict[str, Any]) -> Optional[Package]:
    """Build a Package from a SUBSCRIPTION_PLANS row. Skips free tier."""
    price = float(plan.get("price_usd") or 0.0)
    if price <= 0:
        return None
    return Package(
        id=pid,
        name=str(plan.get("name") or pid.title()),
        price_usd=price,
        credits=int(plan.get("credits") or 0),
        operator_share_pct=max(0.0, min(1.0, float(plan.get("operator_share_pct", 0.30)))),
    )


def _rebuild_packages_from_plans() -> None:
    """Refresh PACKAGES from the current SUBSCRIPTION_PLANS dict."""
    from shared import constants
    PACKAGES.clear()
    for pid, plan in constants.SUBSCRIPTION_PLANS.items():
        pkg = _plan_to_package(pid, plan)
        if pkg is not None:
            PACKAGES[pid] = pkg


def _seed_defaults() -> None:
    """One-time snapshot of the original code-time defaults."""
    if _DEFAULT_PACKAGES:
        return
    from shared import constants
    for pid, plan in constants.SUBSCRIPTION_PLANS.items():
        pkg = _plan_to_package(pid, plan)
        if pkg is not None:
            _DEFAULT_PACKAGES[pid] = pkg


async def load_overrides_from_db() -> None:
    """
    Sync PACKAGES from SUBSCRIPTION_PLANS.

    The `platform_config.config_type="pricing"` doc is read by server.py at
    startup into `constants.SUBSCRIPTION_PLANS` directly — this function just
    derives the Package view. Calling it after apply_overrides() keeps PACKAGES
    aligned with whatever's currently in SUBSCRIPTION_PLANS.
    """
    _seed_defaults()                     # capture code-time defaults on first call
    _rebuild_packages_from_plans()
    logger.info("PACKAGES synced from SUBSCRIPTION_PLANS: %d entries", len(PACKAGES))


async def apply_overrides(
    updates: dict[str, dict[str, Any]],
    *,
    actor_id: str = "system",
) -> dict[str, Any]:
    """
    Persist + apply per-plan edits. Writes to the unified `platform_config`
    `config_type="pricing"` doc — same store the existing pricing manager uses
    — so the owner's edits show up in BOTH the legacy pricing-manager UI and
    the Stripe checkout flow.

    `updates` shape:
        { "pro":         {"operator_share_pct": 0.40, "price_usd": 59.0},
          "enterprise":  {"name": "Enterprise", "price_usd": 999, "credits": 200_000,
                          "operator_share_pct": 0.40} }

    Custom (non-default) plan ids ARE allowed — that's how the owner adds new
    tiers without a code edit. Custom plans require name + price_usd + credits.
    """
    from db import db
    from governance.audit import log_action
    from shared import constants

    _seed_defaults()

    doc = await db.platform_config.find_one(
        {"config_type": _PLATFORM_CONFIG_KEY}, {"_id": 0},
    ) or {"config_type": _PLATFORM_CONFIG_KEY, "plans": {}}
    persisted_plans = doc.get("plans") or {}

    applied: list[str] = []
    for pid, fields in (updates or {}).items():
        existing = persisted_plans.get(pid) or dict(constants.SUBSCRIPTION_PLANS.get(pid) or {})
        is_new_custom = (
            pid not in _DEFAULT_PACKAGES and pid not in persisted_plans and pid not in constants.SUBSCRIPTION_PLANS
        )

        if is_new_custom:
            for required in ("name", "price_usd", "credits"):
                if required not in fields:
                    raise ValueError(f"new plan '{pid}' requires '{required}'")
            # Backfill default plan shape so the public /pricing page can render it.
            existing.setdefault("price_bdt", float(fields.get("price_usd", 0)) * 107)
            existing.setdefault("max_agents", 0)
            existing.setdefault("max_custom_agents", 0)
            existing.setdefault("includes_commander", False)
            existing.setdefault("max_team_members", 1)
            existing.setdefault("monthly_cap_usd", 0.0)
            existing.setdefault("features", [])

        before = dict(existing)
        for k in ("name", "price_usd", "credits", "operator_share_pct"):
            if k in fields:
                existing[k] = fields[k]
        persisted_plans[pid] = existing
        applied.append(pid)

        # Mirror into in-memory constants so subsequent reads see the change.
        if pid in constants.SUBSCRIPTION_PLANS:
            constants.SUBSCRIPTION_PLANS[pid].update(existing)
        else:
            constants.SUBSCRIPTION_PLANS[pid] = dict(existing)

        try:
            await log_action(
                action="plan_override_apply",
                actor_type="admin",
                actor_id=actor_id,
                target_type="subscription_plan",
                target_id=pid,
                details={"before": before, "after": existing, "is_new": is_new_custom},
            )
        except Exception as exc:
            logger.warning("audit log failed for plan override %s: %s", pid, exc)

    await db.platform_config.update_one(
        {"config_type": _PLATFORM_CONFIG_KEY},
        {"$set": {"plans": persisted_plans}},
        upsert=True,
    )
    _rebuild_packages_from_plans()
    return list_packages()


async def delete_package(pkg_id: str, *, actor_id: str = "system") -> bool:
    """
    Remove a custom plan. Code-default plans cannot be deleted — they revert
    to code defaults via reset_overrides() instead.
    """
    _seed_defaults()
    if pkg_id in _DEFAULT_PACKAGES:
        raise ValueError(f"cannot delete default plan '{pkg_id}' — use reset_overrides() to revert")

    from db import db
    from governance.audit import log_action
    from shared import constants

    before = PACKAGES.get(pkg_id)
    res = await db.platform_config.update_one(
        {"config_type": _PLATFORM_CONFIG_KEY},
        {"$unset": {f"plans.{pkg_id}": ""}},
    )
    constants.SUBSCRIPTION_PLANS.pop(pkg_id, None)
    PACKAGES.pop(pkg_id, None)
    deleted = res.modified_count > 0
    if deleted:
        try:
            await log_action(
                action="plan_override_delete",
                actor_type="admin",
                actor_id=actor_id,
                target_type="subscription_plan",
                target_id=pkg_id,
                details={"before": before.__dict__ if before else None},
            )
        except Exception as exc:
            logger.warning("audit log failed for delete %s: %s", pkg_id, exc)
    return deleted


async def reset_overrides(*, actor_id: str = "system") -> dict[str, Any]:
    """Drop every override; revert SUBSCRIPTION_PLANS + PACKAGES to code defaults."""
    from db import db
    from governance.audit import log_action

    # Reload constants from source: re-import shared.constants is the cleanest
    # way to pick up the original module-level dict literal.
    import importlib
    from shared import constants
    importlib.reload(constants)

    await db.platform_config.delete_one({"config_type": _PLATFORM_CONFIG_KEY})
    _DEFAULT_PACKAGES.clear()
    _seed_defaults()
    _rebuild_packages_from_plans()

    try:
        await log_action(
            action="plan_override_reset",
            actor_type="admin",
            actor_id=actor_id,
            target_type="subscription_plan_catalog",
            target_id="all",
            details={},
        )
    except Exception as exc:
        logger.warning("audit log failed for reset: %s", exc)
    return list_packages()


def list_packages() -> list[dict[str, Any]]:
    return [
        {
            "id": p.id, "name": p.name, "price_usd": p.price_usd, "credits": p.credits,
            "operator_share_pct": p.operator_share_pct,
            "operator_share_usd": p.operator_share_usd,
            "user_backing_usd":   p.user_backing_usd,
        }
        for p in PACKAGES.values()
    ]


# ----------------------------------------------------------------- checkout

async def create_checkout_session(
    *,
    user_id: str,
    package_id: str,
    success_url: str,
    cancel_url: str,
    customer_email: Optional[str] = None,
) -> dict[str, Any]:
    """Create a Stripe Checkout Session for a one-time credit top-up."""
    if not STRIPE_SECRET_KEY:
        raise RuntimeError("STRIPE_SECRET_KEY not configured")
    pkg = PACKAGES.get(package_id)
    if pkg is None:
        raise ValueError(f"Unknown package_id: {package_id}")

    session = stripe.checkout.Session.create(
        mode="payment",
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "usd",
                "unit_amount": int(pkg.price_usd * 100),
                "product_data": {
                    "name": f"MAARS {pkg.name} — {pkg.credits:,} credits",
                    "description": f"{pkg.credits:,} MAARS Command credits",
                },
            },
            "quantity": 1,
        }],
        success_url=success_url,
        cancel_url=cancel_url,
        customer_email=customer_email,
        metadata={
            "user_id": user_id,
            "package_id": pkg.id,
            "credits": str(pkg.credits),
            "maars_billing": "v1",
        },
    )
    return {
        "session_id": session.id,
        "url": session.url,
        "package": {"id": pkg.id, "name": pkg.name, "credits": pkg.credits, "price_usd": pkg.price_usd},
    }


# ----------------------------------------------------------------- webhook

def verify_webhook(payload: bytes, signature: str) -> dict[str, Any]:
    """Verify and parse a Stripe webhook event. Raises on invalid signature."""
    if not STRIPE_WEBHOOK_SECRET:
        # Dev / local mode — skip verification but log loudly.
        logger.warning("STRIPE_WEBHOOK_SECRET not set; parsing webhook without signature check")
        import json
        return json.loads(payload.decode("utf-8"))
    return stripe.Webhook.construct_event(payload, signature, STRIPE_WEBHOOK_SECRET)


async def handle_event(event: dict[str, Any]) -> dict[str, Any]:
    """
    Process a verified Stripe event. Currently handles `checkout.session.completed`.

    Idempotency: credit grant is keyed on `stripe:session:{session_id}` via the
    ledger unique index. Replays are no-ops.
    """
    event_type = event.get("type")
    session = (event.get("data") or {}).get("object") or {}

    if event_type != "checkout.session.completed":
        return {"status": "ignored", "event_type": event_type}

    meta = session.get("metadata") or {}
    if meta.get("maars_billing") != "v1":
        # Event for a non-MAARS-billing checkout (e.g. legacy subscriptions path).
        return {"status": "skipped", "reason": "not maars_billing v1"}

    user_id = meta.get("user_id")
    credits = int(meta.get("credits") or 0)
    package_id = meta.get("package_id", "")
    session_id = session.get("id") or "unknown"

    if not user_id or credits <= 0:
        return {"status": "error", "reason": "missing user_id or credits in metadata"}

    pkg = PACKAGES.get(package_id)
    operator_share_pct = float(pkg.operator_share_pct) if pkg else 0.30
    amount_total_cents = int(session.get("amount_total") or (pkg.price_usd * 100 if pkg else 0))
    amount_total_usd   = amount_total_cents / 100.0

    # Per-customer pricing override — beats the package default if active.
    override = await customer_pricing_service.get(user_id=user_id, package_id=package_id)
    override_applied: dict[str, Any] = {}
    if override:
        if "operator_share_pct" in override:
            operator_share_pct = float(override["operator_share_pct"])
            override_applied["operator_share_pct"] = operator_share_pct
        if "price_usd" in override:
            amount_total_usd = float(override["price_usd"])
            override_applied["price_usd"] = amount_total_usd
        # credits_bonus is added AFTER the derivation below.

    operator_usd     = round(amount_total_usd * operator_share_pct, 6)
    user_backing_usd = round(amount_total_usd - operator_usd, 6)

    # ── Credit grant derives from the user-backing dollars, not the plan's
    # ── fixed `credits` field. This is what makes the system real PAYG behind
    # ── the subscription mask: the user spends down dollars-as-credits, and
    # ── their balance drains in actual provider cost, not flat per-model units.
    from shared.constants import CREDITS_PER_USD
    derived_credits = max(0, round(user_backing_usd * CREDITS_PER_USD))
    if override and "credits_bonus" in override:
        derived_credits += int(override["credits_bonus"])
        override_applied["credits_bonus"] = override["credits_bonus"]
    credits = derived_credits

    # ── 1. Grant the user's credit allocation (idempotent via ledger) ────────
    # Split across bucket pools per the plan's allowance ratios. A one-off
    # top-up (`package_id` not a plan) still grants — lands on `general`
    # so users can spend it however they want. Plan renewals get split.
    from services.billing.plan_buckets import split_credits, plan_allows_general_fallback
    from shared.constants import SUBSCRIPTION_PLANS
    is_plan = package_id in SUBSCRIPTION_PLANS
    if is_plan and credits > 0:
        bucket_splits = split_credits(credits, package_id)
        summary = await wallet_service.grant_buckets(
            user_id,
            bucket_splits,
            reference_type="stripe_checkout",
            reference_id=session_id,
            description=f"Plan renewal: {package_id} ({credits} credits split by modality)",
            metadata={
                "stripe_session_id": session_id,
                "package_id": package_id,
                "amount_total_usd": amount_total_usd,
                "currency": session.get("currency"),
                "operator_share_pct": operator_share_pct,
                "operator_share_usd": operator_usd,
                "user_backing_usd": user_backing_usd,
                "bucket_splits": bucket_splits,
            },
        )
        # Propagate plan's fallback policy to the wallet flag.
        from db import db as _db
        await _db["wallets"].update_one(
            {"user_id": user_id},
            {"$set": {"allow_general_fallback": plan_allows_general_fallback(package_id)}},
        )
    else:
        summary = await wallet_service.grant(
            user_id,
            credits,
            reference_type="stripe_checkout",
            reference_id=session_id,
            description=f"Credit top-up: {package_id} ({credits} credits)",
            metadata={
                "stripe_session_id": session_id,
                "package_id": package_id,
                "amount_total_usd": amount_total_usd,
                "currency": session.get("currency"),
                "operator_share_pct": operator_share_pct,
                "operator_share_usd": operator_usd,
                "user_backing_usd": user_backing_usd,
            },
            bucket="general",  # ad-hoc top-ups land on general (flexible)
        )

    # ── 2. Book the operator-revenue side of the split (idempotent) ─────────
    revenue_entry = await revenue_service.record_revenue(
        amount_usd=operator_usd,
        source_type="stripe_checkout",
        source_ref=session_id,
        user_id=user_id,
        package_id=package_id,
        metadata={
            "amount_total_usd": amount_total_usd,
            "user_backing_usd": user_backing_usd,
            "operator_share_pct": operator_share_pct,
            "credits_granted": credits,
            "currency": session.get("currency"),
        },
    )

    return {
        "status": "credited",
        "user_id": user_id,
        "credits_granted": credits,
        "wallet": summary,
        "session_id": session_id,
        "split": {
            "amount_total_usd": amount_total_usd,
            "operator_share_pct": operator_share_pct,
            "operator_share_usd": operator_usd,
            "user_backing_usd": user_backing_usd,
            "revenue_booked": revenue_entry is not None,
            "customer_override_applied": override_applied or None,
        },
    }
