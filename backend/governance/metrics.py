"""MAARS — Metrics aggregation and alerting rules engine."""

from datetime import datetime, timezone
from db import db

ALERTS_COLLECTION = "system_alerts"
ALERT_RULES_COLLECTION = "alert_rules"
METRICS_SNAPSHOTS = "metrics_snapshots"

DEFAULT_RULES = [
    {"rule_id": "circuit_breaker_tripped", "name": "Circuit Breaker Tripped", "metric": "circuit_breakers_tripped", "operator": ">", "threshold": 0, "severity": "high", "enabled": True},
    {"rule_id": "high_budget_usage", "name": "High Budget Usage", "metric": "budget_used_pct", "operator": ">", "threshold": 80, "severity": "medium", "enabled": True},
    {"rule_id": "low_success_rate", "name": "Low Model Success Rate", "metric": "model_success_rate_min", "operator": "<", "threshold": 70, "severity": "high", "enabled": True},
    {"rule_id": "open_incidents", "name": "Multiple Open Incidents", "metric": "open_incidents", "operator": ">", "threshold": 3, "severity": "medium", "enabled": True},
    {"rule_id": "low_trust_agents", "name": "Agents Below Trust Threshold", "metric": "low_trust_count", "operator": ">", "threshold": 5, "severity": "low", "enabled": True},
    {"rule_id": "execution_failures", "name": "Execution Failure Spike", "metric": "recent_failures", "operator": ">", "threshold": 2, "severity": "high", "enabled": True},
]


async def _ensure_default_rules():
    count = await db[ALERT_RULES_COLLECTION].count_documents({})
    if count == 0:
        await db[ALERT_RULES_COLLECTION].insert_many([{**r} for r in DEFAULT_RULES])


async def collect_metrics():
    """Aggregate real-time metrics from all subsystems."""
    from governance.circuit_breaker import get_tripped_breakers, get_all_breakers
    from governance.trust_scoring import get_low_trust_entities
    from governance.incidents import get_incidents
    from kernel.scheduler import get_agent_workload
    from router.engine import get_model_performance

    tripped = await get_tripped_breakers()
    all_breakers = await get_all_breakers()
    incidents_open = await get_incidents(status="open")
    low_trust = await get_low_trust_entities(threshold=30)
    workload = await get_agent_workload()
    perf = await get_model_performance()

    total_agents = sum(w.get("total", 0) for w in workload)
    busy_agents = sum(w.get("busy", 0) for w in workload)

    min_success = 100
    for p in perf:
        sr = p.get("success_rate", 1) * 100
        if p.get("total_calls", 0) > 0 and sr < min_success:
            min_success = sr

    recent_runs = await db["execution_runs"].find({"status": {"$ne": "completed"}}, {"_id": 0}).sort("started_at", -1).limit(10).to_list(length=10)
    recent_failures = sum(1 for r in recent_runs if r.get("summary", {}).get("failed", 0) > 0)

    metrics = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "circuit_breakers_tripped": len(tripped),
        "circuit_breakers_total": len(all_breakers),
        "open_incidents": len(incidents_open),
        "low_trust_count": len(low_trust),
        "total_agents": total_agents,
        "busy_agents": busy_agents,
        "agent_utilization": round(busy_agents / max(total_agents, 1) * 100, 1),
        "model_success_rate_min": round(min_success, 1),
        "model_count": len(perf),
        "recent_failures": recent_failures,
        "networks": len(workload),
    }

    # Store snapshot
    await db[METRICS_SNAPSHOTS].insert_one({**metrics})
    # Keep last 500 snapshots
    count = await db[METRICS_SNAPSHOTS].count_documents({})
    if count > 500:
        oldest = await db[METRICS_SNAPSHOTS].find({}, {"_id": 1}).sort("timestamp", 1).limit(count - 500).to_list(length=count - 500)
        ids = [d["_id"] for d in oldest]
        await db[METRICS_SNAPSHOTS].delete_many({"_id": {"$in": ids}})

    return metrics


async def evaluate_alerts(metrics: dict):
    """Evaluate alert rules against current metrics."""
    await _ensure_default_rules()
    rules = await db[ALERT_RULES_COLLECTION].find({"enabled": True}, {"_id": 0}).to_list(length=50)
    triggered = []
    for rule in rules:
        metric_value = metrics.get(rule["metric"])
        if metric_value is None:
            continue
        threshold = rule["threshold"]
        op = rule["operator"]
        fired = False
        if op == ">" and metric_value > threshold:
            fired = True
        elif op == "<" and metric_value < threshold:
            fired = True
        elif op == ">=" and metric_value >= threshold:
            fired = True
        elif op == "==" and metric_value == threshold:
            fired = True

        if fired:
            alert = {
                "rule_id": rule["rule_id"],
                "rule_name": rule["name"],
                "severity": rule["severity"],
                "metric": rule["metric"],
                "value": metric_value,
                "threshold": threshold,
                "operator": op,
                "triggered_at": metrics["timestamp"],
                "acknowledged": False,
            }
            triggered.append(alert)
            await db[ALERTS_COLLECTION].update_one(
                {"rule_id": rule["rule_id"], "acknowledged": False},
                {"$set": alert},
                upsert=True,
            )
    return triggered


async def get_active_alerts():
    cursor = db[ALERTS_COLLECTION].find({"acknowledged": False}, {"_id": 0}).sort("triggered_at", -1)
    return await cursor.to_list(length=50)


async def acknowledge_alert(rule_id: str):
    await db[ALERTS_COLLECTION].update_one({"rule_id": rule_id}, {"$set": {"acknowledged": True}})
    return {"rule_id": rule_id, "acknowledged": True}


async def get_alert_rules():
    await _ensure_default_rules()
    cursor = db[ALERT_RULES_COLLECTION].find({}, {"_id": 0})
    return await cursor.to_list(length=50)


async def update_alert_rule(rule_id: str, updates: dict):
    allowed = {"threshold", "enabled", "severity"}
    filtered = {k: v for k, v in updates.items() if k in allowed}
    await db[ALERT_RULES_COLLECTION].update_one({"rule_id": rule_id}, {"$set": filtered})
    return await db[ALERT_RULES_COLLECTION].find_one({"rule_id": rule_id}, {"_id": 0})


async def get_metrics_history(limit: int = 30):
    cursor = db[METRICS_SNAPSHOTS].find({}, {"_id": 0}).sort("timestamp", -1).limit(limit)
    results = await cursor.to_list(length=limit)
    results.reverse()
    return results
