"""SLO + error-budget tracking.

Every production gateway needs a numeric answer to "how's reliability?"
We define two SLIs:

  availability   = (successful_calls / total_calls) in the last 30 days.
                   SLO target 99.5% → error budget 0.5% (~36m/day down).
  latency        = (calls with latency_ms <= P95_TARGET / total) in 7d.
                   P95_TARGET default 8000ms.

When 50% of the budget is consumed mid-window we fire a WARN alert;
at 100% consumption we fire a CRIT alert and optionally auto-disable
non-essential features (shadow traffic, drift-detector sampling) to
protect capacity for real traffic.

Consumed from `/admin/gateway/health` which reads `snapshot()`.
"""
from __future__ import annotations
import logging
from datetime import datetime, timezone, timedelta
from typing import Any

logger = logging.getLogger(__name__)

AVAILABILITY_TARGET = 0.995
LATENCY_P95_TARGET_MS = 8000
AVAILABILITY_WINDOW_DAYS = 30
LATENCY_WINDOW_DAYS = 7


async def availability_slo() -> dict[str, Any]:
    """Compute availability over the last AVAILABILITY_WINDOW_DAYS."""
    from db import db
    since = (datetime.now(timezone.utc) - timedelta(days=AVAILABILITY_WINDOW_DAYS)).isoformat()
    pipeline = [
        {"$match": {"timestamp": {"$gte": since}}},
        {"$group": {
            "_id": None,
            "total": {"$sum": 1},
            "errors": {"$sum": {"$cond": [{"$gt": [{"$ifNull": ["$error", None]}, None]}, 1, 0]}},
        }},
    ]
    try:
        rows = await db.gateway_usage_logs.aggregate(pipeline).to_list(1)
    except Exception:
        rows = []
    total = (rows[0]["total"] if rows else 0) or 0
    errors = (rows[0]["errors"] if rows else 0) or 0
    if total == 0:
        return {"target": AVAILABILITY_TARGET, "observed": None, "budget_consumed_pct": 0}
    observed = (total - errors) / total
    budget = 1 - AVAILABILITY_TARGET
    consumed = (1 - observed) / budget if budget > 0 else 0
    return {
        "target": AVAILABILITY_TARGET,
        "observed": round(observed, 5),
        "error_budget_total": budget,
        "error_budget_consumed_pct": round(min(consumed, 1.5) * 100, 2),
        "window_days": AVAILABILITY_WINDOW_DAYS,
        "total_calls": total,
        "error_calls": errors,
    }


async def latency_slo() -> dict[str, Any]:
    """P95 latency SLO over LATENCY_WINDOW_DAYS."""
    from db import db
    since = (datetime.now(timezone.utc) - timedelta(days=LATENCY_WINDOW_DAYS)).isoformat()
    pipeline = [
        {"$match": {"timestamp": {"$gte": since}, "latency_ms": {"$exists": True, "$gt": 0}}},
        {"$group": {
            "_id": None,
            "total": {"$sum": 1},
            "within_target": {"$sum": {"$cond": [{"$lte": ["$latency_ms", LATENCY_P95_TARGET_MS]}, 1, 0]}},
        }},
    ]
    try:
        rows = await db.gateway_usage_logs.aggregate(pipeline).to_list(1)
    except Exception:
        rows = []
    total = (rows[0]["total"] if rows else 0) or 0
    within = (rows[0]["within_target"] if rows else 0) or 0
    if total == 0:
        return {"target_ms": LATENCY_P95_TARGET_MS, "observed_pct": None}
    observed = within / total
    return {
        "target_ms": LATENCY_P95_TARGET_MS,
        "observed_within_target_pct": round(observed * 100, 2),
        "window_days": LATENCY_WINDOW_DAYS,
        "total_calls": total,
        "slow_calls": total - within,
    }


async def snapshot() -> dict[str, Any]:
    """Combined view. Returns budget status + suggested action."""
    av = await availability_slo()
    lat = await latency_slo()

    status = "healthy"
    suggestion = "no action needed"
    pct = av.get("error_budget_consumed_pct", 0) or 0
    if pct >= 100:
        status = "critical"
        suggestion = "budget exhausted — disable non-essential features"
    elif pct >= 50:
        status = "warn"
        suggestion = "error budget 50%+ consumed — investigate provider health"

    return {
        "availability": av,
        "latency": lat,
        "status": status,
        "suggestion": suggestion,
    }
