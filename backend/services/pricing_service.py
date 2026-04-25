"""Pricing — single source of truth.

Before this module, plan data was assembled in two places:
  - `routes/subscriptions.py` GET /plans (legacy dict shape)
  - `routes/public_pricing.py` GET /plans/v2 (new list shape with annual)

Two handlers, two shapes, two places to drift. This service collapses
them into one loader + one formatter, called by exactly one endpoint.

One call — `load_plans_payload()` — returns everything a pricing page,
landing section, or checkout flow could need:
  - plans (legacy dict, for backward compat with existing PricingPage)
  - plans_v2 (list with monthly + annual, for LandingPricingSection)
  - credit_packages
  - custom_package
  - bdt_rate, annual_discount_pct

No more duplication. Changing pricing math = one file.
"""
from __future__ import annotations
from typing import Any

from services.billing.annual_billing import resolve_plan_pricing, ANNUAL_DISCOUNT


async def _load_raw_plans() -> tuple[dict, float]:
    """Plans dict + BDT rate. Prefers platform_config (operator-published)
    and falls back to the in-memory SUBSCRIPTION_PLANS so a fresh install
    has data before the operator hits Publish."""
    from db import db
    config = await db.platform_config.find_one({"config_type": "pricing"}, {"_id": 0}) or {}
    plans = config.get("plans") or {}
    bdt_rate = float(config.get("bdt_exchange_rate", 107.0))
    if not plans:
        try:
            from shared.constants import SUBSCRIPTION_PLANS
            plans = dict(SUBSCRIPTION_PLANS)
        except Exception:
            plans = {}
    return plans, bdt_rate


def _to_v2_row(plan_id: str, plan: dict, bdt_rate: float,
               engine_config: dict | None = None) -> dict:
    """Canonical shape each plan renders as for LandingPricingSection
    and any future consumer. Monthly + annual are both present so the
    UI can toggle without a second fetch.

    `capacity_features` is a buyer-language feature list derived from
    the plan's credit grant + engine_config — this is what the client
    sees, not the credit number. The legacy `features` list is kept
    alongside for backward compat + admin editing.

    `bucket_allowances` + `allow_general_fallback` surface the per-
    modality credit split so the pricing UI can show buyers exactly
    what they get per pool (chat / vibe / image / video / voice / stt)
    rather than one vague credit number.
    """
    from services.plan_capacity import derive_capacity, capacity_features
    from services.billing.plan_buckets import plan_bucket_summary
    from services.billing.plan_deliverables import plan_deliverables
    ec = engine_config or {}
    credits_raw = int(plan.get("credits") or 0)
    credits_float = float(credits_raw)
    capacity = derive_capacity(credits_float, ec) if ec else None
    cap_features = capacity_features(credits_float, ec) if ec else None
    bucket_summary = plan_bucket_summary(plan_id, credits_raw)
    return {
        "plan_id": plan_id,
        "name": plan.get("name", plan_id.title()),
        "features": plan.get("features", []),
        "capacity_features": cap_features,
        "capacity": capacity,
        "max_agents": plan.get("max_agents"),
        "max_custom_agents": plan.get("max_custom_agents"),
        "max_team_members": plan.get("max_team_members", 1),
        "includes_commander": plan.get("includes_commander", False),
        "credits": credits_raw,
        "bucket_allowances": bucket_summary["bucket_allowances"],
        "allow_general_fallback": bucket_summary["allow_general_fallback"],
        # Deliverables: the UNIFIED buyer-facing language. Resolves legacy
        # plan_ids through LEGACY_TO_UNIFIED (e.g. 'starter' → 'creator').
        "deliverables": plan_deliverables(plan_id),
        "monthly": resolve_plan_pricing(plan, "monthly", bdt_rate),
        "annual":  resolve_plan_pricing(plan, "annual",  bdt_rate),
    }


def _unified_rows(bdt_rate: float) -> list[dict]:
    """Build v2 rows directly from the unified 5-tier PLAN_CATALOG.
    This is the catalog buyers see on the pricing page going forward —
    legacy plans stay around for existing subscribers only.
    """
    from services.billing.plan_deliverables import (
        PLAN_CATALOG, plan_deliverables, total_credits_for,
    )
    from services.billing.plan_buckets import plan_bucket_summary
    out: list[dict] = []
    for plan in PLAN_CATALOG:
        pid = plan["plan_id"]
        price_usd = float(plan.get("price_usd", 0))
        credits = total_credits_for(pid)
        bucket_summary = plan_bucket_summary(pid, credits)
        row = {
            "plan_id": pid,
            "name":    plan["name"],
            "tagline": plan.get("tagline"),
            "price_usd": price_usd,
            "price_bdt": round(price_usd * bdt_rate, 2),
            "max_agents":        plan.get("max_agents"),
            "max_custom_agents": plan.get("max_custom_agents"),
            "max_team_members":  plan.get("max_team_members", 1),
            "includes_commander": plan.get("includes_commander", False),
            "popular":           bool(plan.get("popular", False)),
            # Both forms so UI can toggle between headline credits + deliverables.
            "credits": credits,
            "bucket_allowances": bucket_summary["bucket_allowances"],
            "allow_general_fallback": bucket_summary["allow_general_fallback"],
            "deliverables": plan_deliverables(pid),
            "expected_mix": plan.get("expected_mix") or {},
            "highlights":  plan.get("highlights", []),
            "features":    plan.get("highlights", []),  # back-compat alias
            "monthly": {
                "price_usd": price_usd,
                "price_bdt": round(price_usd * bdt_rate, 2),
            },
            "annual": {
                "price_usd": round(price_usd * 12 * 0.83, 2),   # ~17% discount
                "price_bdt": round(price_usd * 12 * 0.83 * bdt_rate, 2),
            },
        }
        out.append(row)
    return out


def _sort_key(p: dict):
    """Free first, then ascending monthly price. Stable so the landing
    grid + the full pricing ladder stay in the same order."""
    monthly_usd = (p.get("monthly") or {}).get("price_usd", 0)
    return (0 if p["plan_id"] == "free" else 1, monthly_usd)


async def load_plans_payload() -> dict[str, Any]:
    """One function, every shape.

    Returns:
        plans:          legacy dict keyed by plan_id — {free: {...}, starter: {...}}
                        (preserves backward compat with the existing PricingPage)
        plans_v2:       list of canonical rows with monthly + annual keys
                        (feeds LandingPricingSection + any new UI)
        credit_packages + custom_package: untouched from the legacy shape
        bdt_rate, annual_discount_pct: top-level so UI doesn't guess
    """
    from shared.utils import get_custom_package_config, get_credit_packages

    plans, bdt_rate = await _load_raw_plans()

    # Inject capacity_features + capacity dict into each plan_v2 row.
    try:
        from services.pricing_math import load_pricing_config
        cfg = await load_pricing_config()
        engine_config = cfg.get("engine_config") or {}
    except Exception:
        engine_config = {}

    # plans_v2 = whatever catalog is ACTIVE in the DB. Operator picks via
    # the "Load UNIFIED 5-Tier Preset" / "Legacy 13-Tier" buttons in the
    # PricingManager, or via direct edits — whatever's persisted in
    # platform_config.pricing.plans is what the pricing page serves.
    # The PLAN_CATALOG unified-5 preset is still exposed as an alternate
    # rendering for reference, but it's no longer forced.
    legacy_v2 = [_to_v2_row(pid, p, bdt_rate, engine_config) for pid, p in plans.items()]
    legacy_v2.sort(key=_sort_key)
    unified_v2 = _unified_rows(bdt_rate)
    unified_v2.sort(key=lambda r: r.get("price_usd", 0))

    # Auto-detect which catalog is active. Legacy 13-tier has these
    # canonical IDs (starter, essential, etc.); unified 5-tier has
    # creator/studio/scale/infinity. If DB matches unified → use unified;
    # otherwise (13-tier, custom, or mixed) use legacy rendering so the
    # operator's active plans surface exactly as saved.
    UNIFIED_IDS = {"free", "creator", "studio", "scale", "infinity"}
    db_ids = set(plans.keys())
    is_unified = bool(db_ids) and db_ids.issubset(UNIFIED_IDS)
    plans_v2 = unified_v2 if is_unified else legacy_v2

    # Enrich the legacy dict shape with bucket_allowances so the existing
    # PricingPage.jsx (which consumes `plans[plan_id]`) gets per-modality
    # data without needing a frontend refactor to the v2 shape.
    from services.billing.plan_buckets import plan_bucket_summary
    enriched_plans: dict[str, Any] = {}
    for pid, p in plans.items():
        credits_raw = int(p.get("credits") or 0)
        summary = plan_bucket_summary(pid, credits_raw)
        enriched_plans[pid] = {
            **p,
            "bucket_allowances": summary["bucket_allowances"],
            "allow_general_fallback": summary["allow_general_fallback"],
        }

    custom_config = await get_custom_package_config()
    if isinstance(custom_config, dict):
        custom_config.pop("config_type", None)
    credit_pkgs = await get_credit_packages()

    return {
        "plans": enriched_plans,              # legacy dict shape + bucket_allowances
        "plans_v2": plans_v2,                 # whichever catalog is ACTIVE in DB
        "active_catalog": "unified" if is_unified else "legacy",
        "unified_plans_v2": unified_v2,       # always-available reference
        "legacy_plans_v2": legacy_v2,         # always-available reference
        "credit_packages": credit_pkgs,
        "custom_package": custom_config,
        "bdt_rate": bdt_rate,
        "annual_discount_pct": int(ANNUAL_DISCOUNT * 100),
    }
