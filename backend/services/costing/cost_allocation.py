"""Cost allocation — per-user + per-plan profit/loss from live traffic.

The Pricing Command Center previously had NO answer to "which clients
are costing us more than they pay" or "which plan tier is underwater."
This module produces those numbers on demand.

Three headline views:

  users_this_month()    — every active user: cost, revenue share,
                          plan, margin. Sorted worst-margin first so
                          the loss-makers bubble to the top.

  plans_this_month()    — by plan tier: active users, total real cost,
                          total revenue (price × users), avg cost per
                          user, margin.

  anomalies_this_month()— users exceeding their plan's monthly_cap_usd;
                          candidates for downgrade conversation or
                          auto-upgrade.

Everything reads the live ledger (`gateway_usage_logs`). No
pre-materialization required.
"""
from __future__ import annotations
import logging
import time
from datetime import datetime, timezone, timedelta
from typing import Any

logger = logging.getLogger(__name__)

_CACHE_TTL = 180
_cache: dict[str, tuple[Any, float]] = {}


def _cached(key: str):
    hit = _cache.get(key)
    if hit and time.time() - hit[1] < _CACHE_TTL:
        return hit[0]
    return None


def _put(key: str, value):
    _cache[key] = (value, time.time())
    return value


def invalidate():
    _cache.clear()


def _month_start_iso(offset_months: int = 0) -> str:
    now = datetime.now(timezone.utc)
    if offset_months == 0:
        return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
    y = now.year + ((now.month - 1 + offset_months) // 12)
    m = ((now.month - 1 + offset_months) % 12) + 1
    return datetime(y, m, 1, tzinfo=timezone.utc).isoformat()


async def users_this_month(*, limit: int = 200) -> list[dict[str, Any]]:
    """Per-user spend + plan + margin rollup for the current month."""
    key = f"users:{_month_start_iso()}"
    c = _cached(key)
    if c: return c

    from db import db
    from shared.constants import SUBSCRIPTION_PLANS

    since = _month_start_iso()
    spend_pipeline = [
        {"$match": {"timestamp": {"$gte": since}}},
        {"$group": {
            "_id": "$user_id",
            "total_cost_usd":  {"$sum": "$cost_usd"},
            "total_credits":   {"$sum": "$credits_charged"},
            "calls":           {"$sum": 1},
        }},
        {"$sort": {"total_cost_usd": -1}},
    ]
    try:
        spend_rows = await db.gateway_usage_logs.aggregate(spend_pipeline).to_list(limit)
    except Exception as exc:
        logger.info("cost_allocation.users aggregate failed: %s", exc)
        spend_rows = []

    user_ids = [r["_id"] for r in spend_rows if r.get("_id")]
    subs = await db.subscriptions.find(
        {"user_id": {"$in": user_ids}},
        {"user_id": 1, "plan_id": 1, "_id": 0},
    ).to_list(len(user_ids))
    sub_map = {s["user_id"]: s.get("plan_id") for s in subs}

    out: list[dict[str, Any]] = []
    for r in spend_rows:
        uid = r["_id"]
        plan_id = sub_map.get(uid)
        plan = SUBSCRIPTION_PLANS.get(plan_id or "") or {}
        price = float(plan.get("price_usd", 0))
        cost  = round(float(r.get("total_cost_usd") or 0), 4)
        margin = price - cost
        out.append({
            "user_id":        uid,
            "plan_id":        plan_id,
            "plan_name":      plan.get("name"),
            "plan_price_usd": price,
            "cost_usd":       cost,
            "credits":        int(r.get("total_credits") or 0),
            "calls":          int(r.get("calls") or 0),
            "margin_usd":     round(margin, 2),
            "margin_pct":     round((margin / price) * 100, 2) if price > 0 else None,
            "over_cap":       bool(plan.get("monthly_cap_usd") and cost > float(plan["monthly_cap_usd"])),
        })
    return _put(key, out)


async def plans_this_month() -> list[dict[str, Any]]:
    """Per-plan roll-up — the one view that answers 'is this tier
    profitable on average.'"""
    key = f"plans:{_month_start_iso()}"
    c = _cached(key)
    if c: return c

    from db import db
    from shared.constants import SUBSCRIPTION_PLANS

    since = _month_start_iso()
    subs = await db.subscriptions.find(
        {"status": {"$in": ["active", "trialing", None]}},
        {"user_id": 1, "plan_id": 1, "_id": 0},
    ).to_list(100000)
    plan_users: dict[str, list[str]] = {}
    for s in subs:
        plan_users.setdefault(s.get("plan_id") or "free", []).append(s["user_id"])

    results: list[dict[str, Any]] = []
    for plan_id, plan in SUBSCRIPTION_PLANS.items():
        uids = plan_users.get(plan_id, [])
        if not uids:
            results.append({
                "plan_id":      plan_id,
                "plan_name":    plan.get("name"),
                "price_usd":    plan.get("price_usd", 0),
                "active_users": 0,
                "revenue_usd":  0,
                "cost_usd":     0,
                "margin_usd":   0,
                "margin_pct":   None,
                "avg_cost_per_user_usd": 0,
            })
            continue
        pipeline = [
            {"$match": {"user_id": {"$in": uids}, "timestamp": {"$gte": since}}},
            {"$group": {"_id": None, "cost": {"$sum": "$cost_usd"},
                        "calls": {"$sum": 1}, "credits": {"$sum": "$credits_charged"}}},
        ]
        try:
            rows = await db.gateway_usage_logs.aggregate(pipeline).to_list(1)
        except Exception:
            rows = []
        total_cost = round(float((rows[0]["cost"] if rows else 0.0) or 0.0), 4)
        price = float(plan.get("price_usd", 0))
        revenue = price * len(uids)
        results.append({
            "plan_id":      plan_id,
            "plan_name":    plan.get("name"),
            "price_usd":    price,
            "active_users": len(uids),
            "revenue_usd":  round(revenue, 2),
            "cost_usd":     total_cost,
            "margin_usd":   round(revenue - total_cost, 2),
            "margin_pct":   round(((revenue - total_cost) / revenue) * 100, 2) if revenue > 0 else None,
            "avg_cost_per_user_usd": round(total_cost / max(len(uids), 1), 4),
            "calls":        int((rows[0]["calls"] if rows else 0) or 0) if rows else 0,
        })
    # Sort lowest-margin first so cash-leaking tiers surface.
    results.sort(key=lambda r: (r["margin_pct"] if r["margin_pct"] is not None else 100))
    return _put(key, results)


async def anomalies_this_month(*, overage_threshold_mult: float = 1.0) -> list[dict[str, Any]]:
    """Users whose actual spend this month exceeded their plan's
    monthly_cap_usd by >= threshold_mult × the cap. Candidates for
    auto-upgrade conversation or rate-limiting."""
    users = await users_this_month(limit=1000)
    flagged: list[dict[str, Any]] = []
    for u in users:
        price = u.get("plan_price_usd") or 0
        cost  = u.get("cost_usd") or 0
        from shared.constants import SUBSCRIPTION_PLANS
        plan = SUBSCRIPTION_PLANS.get(u.get("plan_id") or "") or {}
        cap = float(plan.get("monthly_cap_usd") or 0)
        if cap <= 0: continue
        if cost >= cap * overage_threshold_mult:
            flagged.append({
                **u,
                "monthly_cap_usd": cap,
                "overage_usd":     round(cost - cap, 4),
                "overage_pct":     round(((cost - cap) / cap) * 100, 2) if cap > 0 else None,
            })
    flagged.sort(key=lambda r: r.get("overage_usd", 0), reverse=True)
    return flagged
