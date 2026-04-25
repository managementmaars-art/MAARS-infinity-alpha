"""Treasury — the operator's money pipeline, automated.

Problem: when a user pays $50 for a plan that costs MAARS ~$1-5 in
provider COGS, the operator was previously having to manually reconcile
which provider got paid what. They asked for this to be automated —
they don't care which API provider receives the cash, they just want:

  Revenue in → COGS reserved automatically → Profit extracted automatically
  Provider payments happen via each provider's OWN native auto-recharge,
  pointing at the operator's payment card. MAARS never moves money to
  providers — it tracks spend, books the reserve, and leaves the rest
  as profit.

Three ledgers, all operator-side (no Stripe Connect, no multi-party
splits, just accounting on top of a single Stripe account):

  revenue_ledger        — every dollar in (from Stripe subscription /
                          top-up / custom package)
  cogs_reserve_ledger   — at charge time we book the expected COGS here
                          (either a plan-level default % or a configured
                          fixed amount). As API calls fire, real COGS
                          debits this pool. Monthly reconcile zeroes out
                          any surplus → profit.
  operator_profit_ledger — revenue minus cogs_reserve; what the operator
                          actually keeps.

Flow:
  Stripe webhook (subscription paid):
     revenue += $50
     cogs_reserve += $5          (10% default for Creator tier)
     operator_profit += $45

  Each API call:
     cogs_reserve -= actual_cost_usd   (per gateway_usage_logs)

  End of month (or on demand):
     if cogs_reserve > 0:           any surplus rolls to operator_profit
     if cogs_reserve < 0:           alert — actual COGS exceeded reserved;
                                    operator must top up from profit or
                                    adjust the reserve rate upward.

Provider-level payments: outside this module. Providers are paid via
each provider's own native auto-recharge (OpenAI/Anthropic/Fal/etc.);
operator configures that ONCE per provider pointing at their card.
Treasury just tracks; it never pushes funds to providers.

Mongo collections:
  operator_treasury       — running tally (one row, singleton)
  operator_treasury_log   — append-only history of every revenue/cogs/profit entry
"""
from __future__ import annotations
import datetime as _dt
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

TREASURY_COLLECTION = "operator_treasury"
TREASURY_LOG        = "operator_treasury_log"
SINGLETON_ID        = "operator_treasury_singleton"

# ── Plan → default COGS reserve rate ─────────────────────────────────
# How much of each dollar we book as "expected COGS" at charge time.
# Real measured COGS (from cost_simulation_report.json) is ~1-3% of
# revenue at current provider mix. Default 10% leaves generous
# headroom; reconcile returns surplus to profit monthly.

DEFAULT_COGS_RATE_BY_PLAN = {
    "free":     0.00,   # $0 revenue; $0 reserve
    "creator":  0.05,   # 5% of $29 = $1.45
    "studio":   0.05,   # 5% of $99 = $4.95
    "scale":    0.08,   # 8% of $299 = $23.92 (heavier video usage possible)
    "infinity": 0.10,   # 10% of $999 = $99.90 (fair-use, higher variance)
    # Legacy plans → best-effort default
    "starter":      0.10,
    "essential":    0.10,
    "basic":        0.08,
    "standard":     0.08,
    "professional": 0.08,
    "advanced":     0.08,
    "growth":       0.08,
    "business":     0.08,
    "enterprise":   0.10,
    "elite":        0.10,
    "lifetime":     0.05,
}

# Flat fallback if an unrecognized plan_id shows up
FALLBACK_COGS_RATE = 0.08


async def _ensure_singleton() -> dict:
    """Lazy-init the singleton treasury doc with zeros on both ledgers."""
    from db import db
    existing = await db[TREASURY_COLLECTION].find_one({"_id": SINGLETON_ID}, {})
    if existing:
        return existing
    doc = {
        "_id":                 SINGLETON_ID,
        "revenue_usd":         0.0,
        "cogs_reserve_usd":    0.0,
        "cogs_actual_usd":     0.0,
        "operator_profit_usd": 0.0,
        "surplus_rolled_usd":  0.0,
        "deficit_alerts":      0,
        "created_at":          _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "updated_at":          _dt.datetime.now(_dt.timezone.utc).isoformat(),
    }
    try:
        await db[TREASURY_COLLECTION].insert_one(doc)
    except Exception:
        pass
    return doc


async def _log(kind: str, amount_usd: float, metadata: dict | None = None) -> None:
    """Append-only audit trail."""
    from db import db
    try:
        await db[TREASURY_LOG].insert_one({
            "kind":       kind,
            "amount_usd": float(amount_usd),
            "metadata":   metadata or {},
            "ts":         _dt.datetime.now(_dt.timezone.utc).isoformat(),
        })
    except Exception as exc:
        logger.info("treasury log insert failed (kind=%s): %s", kind, exc)


# ── Public API: called from Stripe webhook + every billed API call ──

async def on_subscription_paid(
    *,
    amount_usd: float,
    plan_id: str,
    user_id: str,
    reference_id: str,
    description: str = "",
) -> dict[str, Any]:
    """Book the 3-way split for a subscription / top-up payment.

    Idempotent on `reference_id` (Stripe session_id) — a duplicate
    webhook is a no-op. Returns the updated treasury snapshot.
    """
    from db import db
    if amount_usd <= 0:
        return {"ok": False, "skipped": "zero amount"}

    # Idempotency check
    already = await db[TREASURY_LOG].find_one(
        {"kind": "revenue", "metadata.reference_id": reference_id}, {"_id": 1},
    )
    if already:
        logger.info("treasury.on_subscription_paid: duplicate %s ignored", reference_id)
        snapshot = await get_snapshot()
        return {"ok": True, "duplicate": True, **snapshot}

    rate = DEFAULT_COGS_RATE_BY_PLAN.get(plan_id, FALLBACK_COGS_RATE)
    reserve = round(amount_usd * rate, 6)
    profit  = round(amount_usd - reserve, 6)

    await _ensure_singleton()
    await db[TREASURY_COLLECTION].update_one(
        {"_id": SINGLETON_ID},
        {
            "$inc": {
                "revenue_usd":         amount_usd,
                "cogs_reserve_usd":    reserve,
                "operator_profit_usd": profit,
            },
            "$set": {"updated_at": _dt.datetime.now(_dt.timezone.utc).isoformat()},
        },
    )
    meta_common = {"reference_id": reference_id, "plan_id": plan_id,
                   "user_id": user_id, "cogs_rate": rate, "description": description}
    await _log("revenue",   amount_usd, meta_common)
    await _log("reserve",   reserve,    meta_common)
    await _log("profit",    profit,     meta_common)
    return {
        "ok":           True,
        "revenue_usd":  amount_usd,
        "reserve_usd":  reserve,
        "profit_usd":   profit,
        "cogs_rate":    rate,
    }


async def on_api_call_billed(
    *,
    actual_cost_usd: float,
    provider: str,
    user_id: Optional[str] = None,
    model: Optional[str] = None,
    reference_id: Optional[str] = None,
) -> None:
    """Debit the COGS reserve by the actual provider cost of one API call.

    Called once per settle() in llm_gateway and media_billing. Small
    dollar amounts — a single $0.0002 chat call should not trip any
    alerting. When the reserve goes negative, we emit a log warning
    and the monthly reconcile will flag it for operator attention.
    """
    from db import db
    if actual_cost_usd <= 0:
        return
    await _ensure_singleton()
    await db[TREASURY_COLLECTION].update_one(
        {"_id": SINGLETON_ID},
        {
            "$inc": {
                "cogs_reserve_usd": -float(actual_cost_usd),
                "cogs_actual_usd":   float(actual_cost_usd),
            },
            "$set": {"updated_at": _dt.datetime.now(_dt.timezone.utc).isoformat()},
        },
    )
    await _log("cogs_actual", actual_cost_usd, {
        "provider": provider, "model": model,
        "user_id": user_id, "reference_id": reference_id,
    })


async def get_snapshot() -> dict[str, Any]:
    """Current treasury state — the data that feeds the operator dashboard."""
    await _ensure_singleton()
    from db import db
    doc = await db[TREASURY_COLLECTION].find_one({"_id": SINGLETON_ID}, {"_id": 0}) or {}
    rev  = float(doc.get("revenue_usd") or 0)
    res  = float(doc.get("cogs_reserve_usd") or 0)
    act  = float(doc.get("cogs_actual_usd") or 0)
    prof = float(doc.get("operator_profit_usd") or 0)
    net  = rev - act
    gross_margin_pct = (net / rev * 100) if rev > 0 else 0.0
    return {
        "revenue_usd":          round(rev, 4),
        "cogs_reserve_usd":     round(res, 4),
        "cogs_actual_usd":      round(act, 4),
        "operator_profit_usd":  round(prof, 4),
        "net_profit_usd":       round(net, 4),
        "gross_margin_pct":     round(gross_margin_pct, 2),
        "surplus_rolled_usd":   round(float(doc.get("surplus_rolled_usd") or 0), 4),
        "deficit_alerts":       int(doc.get("deficit_alerts") or 0),
        "updated_at":           doc.get("updated_at"),
    }


async def monthly_reconcile() -> dict[str, Any]:
    """Close the month — move any COGS reserve surplus to profit,
    or emit a deficit alert if actual exceeded reserved.

    Safe to run anytime (idempotent on the current snapshot); typical
    cadence is end-of-month via scheduler. Returns the action taken.
    """
    from db import db
    await _ensure_singleton()
    snap = await get_snapshot()
    reserve = snap["cogs_reserve_usd"]
    if reserve > 0:
        # Surplus → profit
        await db[TREASURY_COLLECTION].update_one(
            {"_id": SINGLETON_ID},
            {
                "$inc": {
                    "cogs_reserve_usd":    -reserve,
                    "operator_profit_usd": reserve,
                    "surplus_rolled_usd":  reserve,
                },
                "$set": {"last_reconcile_at": _dt.datetime.now(_dt.timezone.utc).isoformat()},
            },
        )
        await _log("reconcile_surplus", reserve, {"rolled_to_profit": True})
        return {"ok": True, "action": "surplus_rolled_to_profit", "amount_usd": reserve}
    if reserve < 0:
        deficit = abs(reserve)
        await db[TREASURY_COLLECTION].update_one(
            {"_id": SINGLETON_ID},
            {
                "$inc": {"deficit_alerts": 1},
                "$set": {"last_reconcile_at": _dt.datetime.now(_dt.timezone.utc).isoformat()},
            },
        )
        await _log("reconcile_deficit", deficit, {"needs_operator_attention": True})
        logger.warning("treasury: COGS deficit $%.2f — reserve went negative", deficit)
        return {"ok": True, "action": "deficit_alert", "amount_usd": deficit}
    return {"ok": True, "action": "noop", "amount_usd": 0}


async def recent_log(limit: int = 100) -> list[dict]:
    """Operator-facing feed of recent treasury entries."""
    from db import db
    cur = db[TREASURY_LOG].find({}, {"_id": 0}).sort("ts", -1).limit(limit)
    return await cur.to_list(limit)
