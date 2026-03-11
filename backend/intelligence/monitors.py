"""MAARS — Intelligence: Monitors (News, Competitor, Regulatory, Trend, Sentiment, Risk)."""

import logging
from datetime import datetime, timezone
from db import db

logger = logging.getLogger(__name__)
MONITOR_COLLECTION = "intelligence_monitors"
ALERT_COLLECTION = "intelligence_alerts"


async def create_monitor(monitor_type: str, target: str, config: dict = None):
    """Create a new intelligence monitor."""
    monitor = {
        "monitor_type": monitor_type,
        "target": target,
        "config": config or {},
        "status": "active",
        "last_check": None,
        "check_count": 0,
        "findings": [],
        "alert_level": "none",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db[MONITOR_COLLECTION].insert_one(monitor)
    monitor.pop("_id", None)
    return monitor


async def run_monitor(monitor_type: str, target: str):
    """Execute a monitor check using real web search and store findings."""
    from intelligence.search_engine import search_and_rank

    query_map = {
        "news": f"{target} latest news",
        "competitor": f"{target} competitor analysis market",
        "regulatory": f"{target} regulation compliance update",
        "trend": f"{target} trend analysis",
        "sentiment": f"{target} reviews opinions sentiment",
        "risk": f"{target} risk assessment threats",
    }
    query = query_map.get(monitor_type, f"{target} {monitor_type}")
    search_results = await search_and_rank(query, "fresh")

    alert = False
    alert_level = "none"
    details = []

    for r in search_results.get("results", [])[:3]:
        details.append({
            "title": r.get("title", ""),
            "url": r.get("url", ""),
            "snippet": r.get("snippet", "")[:200],
            "credibility": r.get("credibility_score", 0),
            "is_fresh": r.get("freshness", {}).get("fresh", False),
        })

    if details:
        avg_cred = sum(d["credibility"] for d in details) / len(details)
        fresh_count = sum(1 for d in details if d["is_fresh"])
        if monitor_type in ["risk", "regulatory"] and fresh_count > 0:
            alert = True
            alert_level = "high" if fresh_count >= 2 else "medium"
        elif fresh_count > 0:
            alert_level = "low"

    finding = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "status": "findings_available" if details else "no_results",
        "details": details,
        "alert": alert,
        "alert_level": alert_level,
        "result_count": search_results.get("total", 0),
    }

    await db[MONITOR_COLLECTION].update_one(
        {"monitor_type": monitor_type, "target": target},
        {
            "$set": {"last_check": finding["checked_at"], "alert_level": alert_level},
            "$inc": {"check_count": 1},
            "$push": {"findings": {"$each": [finding], "$slice": -50}},
        },
    )

    if alert:
        alert_doc = {
            "monitor_type": monitor_type,
            "target": target,
            "alert_level": alert_level,
            "finding": finding,
            "acknowledged": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        await db[ALERT_COLLECTION].insert_one(alert_doc)

    return finding


async def get_monitors(monitor_type: str = None, status: str = "active"):
    """List all monitors, optionally filtered."""
    query = {}
    if monitor_type:
        query["monitor_type"] = monitor_type
    if status:
        query["status"] = status
    cursor = db[MONITOR_COLLECTION].find(query, {"_id": 0})
    return await cursor.to_list(length=100)


async def get_alerts(min_level: str = "low"):
    """Get alerts across all monitors."""
    levels = {"none": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}
    threshold = levels.get(min_level, 1)
    cursor = db[ALERT_COLLECTION].find({"acknowledged": False}, {"_id": 0}).sort("created_at", -1)
    results = await cursor.to_list(length=100)
    return [r for r in results if levels.get(r.get("alert_level", "none"), 0) >= threshold]
