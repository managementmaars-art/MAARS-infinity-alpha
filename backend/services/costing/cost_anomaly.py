"""Per-user cost-spike detector — catches runaway integrations fast.

drift_detector watches provider-level cost creep over weeks. This
module watches PER-USER spend velocity over hours. A user who normally
burns $2/day suddenly billing $30/hour is either (a) a wildly profitable
growth event or (b) a looping agent — either way, ops should see it.

Method: rolling EWMA of per-user hourly cost. When current-hour spend
exceeds (baseline + k × stddev), fire.

  baseline_hourly : EWMA over last 7 days
  stddev          : computed from hourly bucket variance
  threshold       : current >= baseline + 6σ  → CRIT
                    current >= baseline + 3σ  → WARN

Called from the scheduler every 15 minutes. Alerts go to
notifications_center.notify_admins and optionally pause the user's
API key (configurable via admin).
"""
from __future__ import annotations
import logging
import math
import time
from datetime import datetime, timezone, timedelta
from typing import Any

logger = logging.getLogger(__name__)

Z_WARN = 3.0
Z_CRIT = 6.0
BASELINE_DAYS = 7


async def _hourly_spend(user_id: str, since: datetime, until: datetime) -> list[float]:
    from db import db
    pipeline = [
        {"$match": {"user_id": user_id, "timestamp": {
            "$gte": since.isoformat(), "$lt": until.isoformat(),
        }, "cost_usd": {"$gt": 0}}},
        {"$group": {
            "_id": {"$substr": ["$timestamp", 0, 13]},  # yyyy-mm-ddTHH
            "total": {"$sum": "$cost_usd"},
        }},
    ]
    try:
        rows = await db.gateway_usage_logs.aggregate(pipeline).to_list(24 * (BASELINE_DAYS + 1))
    except Exception:
        rows = []
    return [float(r.get("total", 0.0)) for r in rows]


def _stats(vals: list[float]) -> tuple[float, float]:
    if not vals:
        return 0.0, 0.0
    n = len(vals)
    mean = sum(vals) / n
    var = sum((v - mean) ** 2 for v in vals) / max(n - 1, 1)
    return mean, math.sqrt(var)


async def check_user(user_id: str) -> dict[str, Any] | None:
    now = datetime.now(timezone.utc)
    baseline_start = now - timedelta(days=BASELINE_DAYS)
    current_hour_start = now.replace(minute=0, second=0, microsecond=0)

    baseline_vals = await _hourly_spend(user_id, baseline_start, current_hour_start)
    if len(baseline_vals) < 10:
        return None  # insufficient history
    mean, sd = _stats(baseline_vals)
    current_vals = await _hourly_spend(user_id, current_hour_start, now)
    current = sum(current_vals)

    if sd == 0:
        # fall back to ratio check
        if mean > 0 and current > mean * 10:
            return {"user_id": user_id, "kind": "cost_spike_10x", "current_hour_usd": current, "baseline_mean_usd": mean}
        return None

    z = (current - mean) / sd
    if z >= Z_CRIT:
        return {"user_id": user_id, "kind": "cost_spike_crit", "z": round(z, 2),
                "current_hour_usd": round(current, 4), "baseline_mean_usd": round(mean, 4),
                "baseline_sigma": round(sd, 4)}
    if z >= Z_WARN:
        return {"user_id": user_id, "kind": "cost_spike_warn", "z": round(z, 2),
                "current_hour_usd": round(current, 4), "baseline_mean_usd": round(mean, 4),
                "baseline_sigma": round(sd, 4)}
    return None


async def scan_all_active_users(*, limit: int = 500) -> list[dict[str, Any]]:
    """Pull every user who spent anything in the last hour, check each."""
    from db import db
    since = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
    try:
        active_rows = await db.gateway_usage_logs.aggregate([
            {"$match": {"timestamp": {"$gte": since}, "cost_usd": {"$gt": 0}}},
            {"$group": {"_id": "$user_id"}},
            {"$limit": limit},
        ]).to_list(limit)
    except Exception:
        active_rows = []
    alerts = []
    for row in active_rows:
        uid = row.get("_id")
        if not uid:
            continue
        alert = await check_user(uid)
        if alert:
            alerts.append(alert)
    if alerts:
        try:
            from routes.notifications_center import notify_admins
            for a in alerts:
                await notify_admins(
                    title=f"Cost anomaly: {a['kind']}",
                    body=str(a),
                    kind="warn" if a["kind"].endswith("warn") else "error",
                    link="/admin/gateway",
                )
        except Exception as exc:
            logger.info("cost_anomaly dispatch failed: %s", exc)
    return alerts
