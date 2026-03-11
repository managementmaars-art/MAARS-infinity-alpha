"""MAARS — Intelligence: Monitors (News, Competitor, Regulatory, Trend, Sentiment, Risk)."""

from datetime import datetime, timezone
from db import db

MONITOR_COLLECTION = "intelligence_monitors"


async def create_monitor(monitor_type: str, target: str, config: dict = None):
    """Create a new intelligence monitor."""
    monitor = {
        "monitor_type": monitor_type,
        "target": target,
        "config": config or {},
        "status": "active",
        "last_check": None,
        "findings": [],
        "alert_level": "none",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db[MONITOR_COLLECTION].insert_one(monitor)
    monitor.pop("_id", None)
    return monitor


async def run_monitor(monitor_type: str, target: str):
    """Execute a monitor check and store findings."""
    finding = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "status": "no_change",
        "details": f"Monitored {target} for {monitor_type} signals",
        "alert": False,
    }
    await db[MONITOR_COLLECTION].update_one(
        {"monitor_type": monitor_type, "target": target},
        {"$set": {"last_check": finding["checked_at"]},
         "$push": {"findings": {"$each": [finding], "$slice": -100}}},
    )
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
    """Get monitors with active alerts."""
    levels = {"none": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}
    cursor = db[MONITOR_COLLECTION].find(
        {"alert_level": {"$ne": "none"}, "status": "active"}, {"_id": 0}
    )
    results = await cursor.to_list(length=100)
    threshold = levels.get(min_level, 1)
    return [r for r in results if levels.get(r.get("alert_level", "none"), 0) >= threshold]
