"""Single source of truth for the "blended cost per credit" figure.

Before this module, three different surfaces each computed their own blended
cost independently:
  - /admin/avg-cost (used by Profit Margin Calculator)     → threshold 50 calls
  - /admin/intelligence/recommendations (Package Advisor)  → threshold 10 calls
  - /admin/gateway/stats (Universal Gateway Overview)      → yet another path

That meant the same plan could show three different margins on three different
pages, which is a credibility killer on a dashboard about pricing.

This module centralises the calculation. Every caller that needs a blended
cost per credit imports `get_blended_cost_per_credit()` from here.

Returned shape:
    {
      "value":              <float USD/credit>,
      "source":             "real_usage" | "estimated_from_model_pricing" | "fallback_default",
      "total_calls":        <int>,
      "total_cost_usd":     <float>,
      "free_routing_pct":   <float 0-100>,
      "free_calls":         <int>,
      "paid_calls":         <int>,
      "threshold_calls":    <int>  # how many calls until we switch to real_usage
    }
"""
from __future__ import annotations
import logging
from typing import Any

from db import db

logger = logging.getLogger(__name__)

# Providers that never cost anything — used to classify calls in the blend.
# Single source of truth: shared/free_providers.py. Import as `FREE_PROVIDERS`
# for backward compat with existing callers in this module.
from shared.free_providers import FREE_PROVIDERS as _FREE
FREE_PROVIDERS: set[str] = set(_FREE)

# Cache across one request cycle so three callers don't hit the DB three times.
_cache: dict[str, Any] = {"value": None, "ts": 0.0}
_CACHE_TTL = 30.0  # seconds — fresh enough for a dashboard

MIN_CALLS_FOR_REAL_DATA = 10  # unified threshold (was 50 on /admin/avg-cost, 10 on intel)


async def get_blended_cost_per_credit() -> dict[str, Any]:
    """Return the blended $/credit figure + provenance metadata. Cached 30s."""
    import time
    now = time.time()
    if _cache["value"] is not None and (now - _cache["ts"]) < _CACHE_TTL:
        return _cache["value"]

    # ── Stage 1: try real usage from gateway_usage_logs (primary — new path) ──
    # Field name differs by collection:
    #   gateway_usage_logs:  cost_usd + credits_charged
    #   usage_logs (legacy): estimated_cost_usd + (no credits field)
    # `value` MUST be cost-per-credit (not cost-per-call) since every caller
    # multiplies it by `credits` to derive plan economics. A call can consume
    # 1 credit (chat) or 400 credits (Sora video); dividing by calls falsely
    # blends them into one meaningless average.
    for collection_name in ("gateway_usage_logs", "usage_logs"):
        try:
            coll = db[collection_name]
            pipeline = [
                {"$group": {
                    "_id": "$provider",
                    "calls":   {"$sum": 1},
                    "cost":    {"$sum": {"$ifNull": ["$cost_usd", "$estimated_cost_usd"]}},
                    "credits": {"$sum": {"$ifNull": ["$credits_charged", 1]}},   # assume 1cr/call for legacy
                }},
            ]
            stats = await coll.aggregate(pipeline).to_list(100)
            total_calls   = sum(s.get("calls", 0) for s in stats)
            total_cost    = sum(s.get("cost", 0) or 0 for s in stats)
            total_credits = sum(s.get("credits", 0) or 0 for s in stats)
            # Prefer real usage data whenever we have enough calls. If older
            # rows are missing credits_charged (pre-schema-fix), fall back to
            # cost/calls. The free_routing_pct is always call-based so it
            # reports what actually happened, not a provider-count heuristic.
            if total_calls >= MIN_CALLS_FOR_REAL_DATA:
                free_calls = sum(s["calls"] for s in stats if s.get("_id") in FREE_PROVIDERS)
                paid_calls = total_calls - free_calls
                # Cost-per-credit: use credits if populated, else fall back to
                # cost-per-call (rows missing credits_charged indicate legacy
                # schema; one credit per call is a reasonable approximation).
                denom = total_credits if total_credits > 0 else total_calls
                result = {
                    "value": round(total_cost / denom, 8) if denom else 0.0,
                    "source": "real_usage" if total_credits > 0 else "real_usage_calls_proxy",
                    "total_calls":   total_calls,
                    "total_credits": int(total_credits),
                    "total_cost_usd": round(total_cost, 6),
                    "free_calls": free_calls,
                    "paid_calls": paid_calls,
                    "free_routing_pct": round((free_calls / total_calls) * 100, 1) if total_calls else 0,
                    "threshold_calls": MIN_CALLS_FOR_REAL_DATA,
                    "collection": collection_name,
                }
                _cache.update({"value": result, "ts": now})
                return result
        except Exception as exc:
            logger.warning("blended_cost: %s aggregate failed: %s", collection_name, exc)

    # ── Stage 2: estimated from per-model pricing + configured providers ──
    try:
        from services.llm_service import MODEL_COSTS_MAP
        from shared.constants import DIRECT_API_KEYS
        TOKENS_PER_CREDIT = 500
        provider_cheapest = {}
        for _model_id, info in MODEL_COSTS_MAP.items():
            if info.get("per_unit"):
                continue
            cost = ((info.get("input", 0) * 0.5) + (info.get("output", 0) * 0.5)) * TOKENS_PER_CREDIT / 1_000_000
            p = info.get("provider", "unknown")
            if p not in provider_cheapest or cost < provider_cheapest[p]:
                provider_cheapest[p] = cost
        configured = {slug for slug, key in DIRECT_API_KEYS.items() if key}
        free_configured = configured & FREE_PROVIDERS
        paid_configured = configured - FREE_PROVIDERS
        free_pct = max(len(free_configured) / max(len(configured), 1), 0.5)
        paid_costs = sorted([provider_cheapest.get(p, 0.001) for p in paid_configured if p in provider_cheapest])
        avg_paid = sum(paid_costs[:5]) / max(len(paid_costs[:5]), 1) if paid_costs else 0.0005
        blended = (1 - free_pct) * avg_paid
        # No real traffic yet — report the PROVIDER-COUNT ratio under a
        # distinct field name so the UI can distinguish measured-from-
        # traffic (`free_routing_pct`) from a pre-launch estimate.
        result = {
            "value": round(blended, 8),
            "source": "estimated_from_model_pricing",
            "total_calls": 0,
            "total_cost_usd": 0,
            "free_calls": 0,
            "paid_calls": 0,
            # Zero traffic measured → 0% measured free routing. UI shows
            # `free_routing_pct_estimated` separately so nothing fakes a
            # high free-routing percentage before any calls are made.
            "free_routing_pct": 0.0,
            "free_routing_pct_estimated": round(free_pct * 100, 1),
            "threshold_calls": MIN_CALLS_FOR_REAL_DATA,
            "configured_providers": len(configured),
            "free_tier_providers": len(free_configured),
        }
        _cache.update({"value": result, "ts": now})
        return result
    except Exception as exc:
        logger.warning("blended_cost estimate failed: %s", exc)

    # ── Stage 3: hard-coded fallback so the UI never breaks ──
    fallback = {
        "value": 0.000031,
        "source": "fallback_default",
        "total_calls": 0, "total_cost_usd": 0,
        "free_calls": 0, "paid_calls": 0,
        "free_routing_pct": 70.0,
        "threshold_calls": MIN_CALLS_FOR_REAL_DATA,
    }
    _cache.update({"value": fallback, "ts": now})
    return fallback


def invalidate_cache() -> None:
    """Force next call to recompute — call after every wallet settle if you want
    the dashboard to feel instant. Otherwise the 30s TTL handles refresh."""
    _cache["value"] = None
    _cache["ts"] = 0.0
