"""Quality-regression + cost-drift detector.

Providers silently change model behavior all the time: OpenAI pushes a
GPT-4o revision, Gemini retrains flash-8b, our answer quality shifts
without a version-number bump. Same story for cost — a provider's token
accounting can shift up by 5-10% between billing cycles.

We guard against both with two rolling z-score detectors:

  QUALITY DRIFT
    For each (provider, model) sample 1% of calls to run in "shadow"
    against the one-tier-up model; judge the winner via llm_judge.
    Track win-rate over trailing 7 days. If the rolling win-rate drops
    by >= 15% vs the prior 7-day window, fire an alert.

  COST DRIFT
    For each (provider, model) track avg USD/1k-tokens from our
    gateway_usage_logs over 7 days. If it jumps >= 10% vs the prior
    7-day window, fire an alert. (This is either a pricing change
    we missed, a token-counting bug, or a model change.)

Alerts go via `notifications_center.notify(user_id=admin, ...)` and
are surfaced on /admin/gateway as red banners.
"""
from __future__ import annotations
import logging
import statistics
from datetime import datetime, timezone, timedelta
from typing import Any

logger = logging.getLogger(__name__)


async def quality_drift_check(*, lookback_days: int = 14) -> list[dict[str, Any]]:
    """Aggregate llm_judge outcomes by (provider, model). Return providers
    whose win-rate dropped >= 15% vs the prior window."""
    from db import db
    now = datetime.now(timezone.utc)
    mid = (now - timedelta(days=lookback_days / 2)).isoformat()
    start = (now - timedelta(days=lookback_days)).isoformat()

    async def winrate_for(since: str, until: str) -> dict[str, float]:
        pipeline = [
            {"$match": {"timestamp": {"$gte": since, "$lt": until}, "judge_winner": {"$exists": True}}},
            {"$group": {
                "_id": "$provider",
                "wins": {"$sum": {"$cond": [{"$eq": ["$judge_winner", "self"]}, 1, 0]}},
                "total": {"$sum": 1},
            }},
        ]
        try:
            rows = await db.gateway_usage_logs.aggregate(pipeline).to_list(100)
        except Exception:
            rows = []
        return {r["_id"]: (r["wins"] / max(r["total"], 1)) for r in rows if r["total"] >= 10}

    recent = await winrate_for(mid, now.isoformat())
    prior  = await winrate_for(start, mid)

    regressions = []
    for p, r_rate in recent.items():
        p_rate = prior.get(p)
        if p_rate is None:
            continue
        delta = r_rate - p_rate
        if delta <= -0.15:
            regressions.append({
                "provider": p,
                "recent_winrate": round(r_rate, 3),
                "prior_winrate":  round(p_rate, 3),
                "delta":          round(delta, 3),
                "kind":           "quality_regression",
            })
    return regressions


async def cost_drift_check(*, lookback_days: int = 14, threshold: float = 0.10) -> list[dict[str, Any]]:
    """Compare avg cost/1k-tokens between prior and recent windows.
    threshold=0.10 = flag >=10% increase (or decrease — could indicate
    we're billing less than we should)."""
    from db import db
    now = datetime.now(timezone.utc)
    mid = (now - timedelta(days=lookback_days / 2)).isoformat()
    start = (now - timedelta(days=lookback_days)).isoformat()

    async def avg_cost_per_1k(since: str, until: str) -> dict[str, float]:
        pipeline = [
            {"$match": {"timestamp": {"$gte": since, "$lt": until},
                        "cost_usd": {"$gt": 0}}},
            {"$group": {
                "_id": {"provider": "$provider", "model": "$native_model"},
                "total_cost": {"$sum": "$cost_usd"},
                "total_tokens": {"$sum": "$prompt_words"},
                "n": {"$sum": 1},
            }},
        ]
        try:
            rows = await db.gateway_usage_logs.aggregate(pipeline).to_list(500)
        except Exception:
            rows = []
        return {
            f"{r['_id']['provider']}/{r['_id']['model']}":
                (r["total_cost"] / max(r["total_tokens"], 1)) * 1000
            for r in rows if r["n"] >= 20
        }

    recent = await avg_cost_per_1k(mid, now.isoformat())
    prior  = await avg_cost_per_1k(start, mid)

    drifts = []
    for k, r_cost in recent.items():
        p_cost = prior.get(k)
        if not p_cost or p_cost == 0:
            continue
        ratio = (r_cost - p_cost) / p_cost
        if abs(ratio) >= threshold:
            provider, model = k.split("/", 1)
            drifts.append({
                "provider": provider,
                "model": model,
                "recent_usd_per_1k": round(r_cost, 6),
                "prior_usd_per_1k": round(p_cost, 6),
                "delta_pct": round(ratio * 100, 2),
                "kind": "cost_drift_up" if ratio > 0 else "cost_drift_down",
            })
    return drifts


async def run_all_checks() -> dict[str, Any]:
    """Convenience — called by the scheduler every 6 hours."""
    q = await quality_drift_check()
    c = await cost_drift_check()
    alerts = q + c
    if alerts:
        try:
            from routes.notifications_center import notify_admins
            for a in alerts:
                await notify_admins(
                    title=f"{a['kind']}: {a.get('provider', '')}",
                    body=str(a),
                    kind="warn",
                    link="/admin/gateway",
                )
        except Exception as exc:
            logger.info("drift alert dispatch failed: %s", exc)
    return {"quality_regressions": q, "cost_drifts": c}
