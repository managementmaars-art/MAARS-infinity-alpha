"""MAARS — Governance: Circuit Breaker System.
Monitors system health metrics and automatically trips breakers
when thresholds are exceeded to prevent cascade failures."""

from datetime import datetime, timezone
from db import db
from governance.audit import log_action

CB_COLLECTION = "circuit_breakers"

# Default circuit breaker definitions
DEFAULT_BREAKERS = [
    {
        "breaker_id": "daily_spend",
        "name": "Daily Spend Limit",
        "target_type": "system",
        "target_id": "global",
        "status": "closed",  # closed=normal, open=tripped, half_open=testing
        "trigger_condition": "daily_spend_exceeds",
        "trigger_threshold": 100.0,
        "current_value": 0.0,
        "action_on_trip": "pause_all_workflows",
        "cooldown_seconds": 3600,
    },
    {
        "breaker_id": "error_rate",
        "name": "Error Rate Spike",
        "target_type": "system",
        "target_id": "global",
        "status": "closed",
        "trigger_condition": "error_rate_exceeds",
        "trigger_threshold": 0.3,
        "current_value": 0.0,
        "action_on_trip": "throttle_agents",
        "cooldown_seconds": 1800,
    },
    {
        "breaker_id": "verification_failure_rate",
        "name": "Verification Failure Spike",
        "target_type": "verification",
        "target_id": "global",
        "status": "closed",
        "trigger_condition": "verification_failure_rate_exceeds",
        "trigger_threshold": 0.4,
        "current_value": 0.0,
        "action_on_trip": "require_human_approval",
        "cooldown_seconds": 3600,
    },
    {
        "breaker_id": "retry_storm",
        "name": "Retry Storm Detection",
        "target_type": "execution",
        "target_id": "global",
        "status": "closed",
        "trigger_condition": "retry_count_exceeds",
        "trigger_threshold": 50,
        "current_value": 0,
        "action_on_trip": "pause_affected_workflows",
        "cooldown_seconds": 1800,
    },
    {
        "breaker_id": "provider_failure",
        "name": "Provider Failure",
        "target_type": "provider",
        "target_id": "any",
        "status": "closed",
        "trigger_condition": "consecutive_failures_exceed",
        "trigger_threshold": 5,
        "current_value": 0,
        "action_on_trip": "disable_provider_routing",
        "cooldown_seconds": 600,
    },
]


async def seed_default_breakers():
    """Seed default circuit breakers if not present."""
    for breaker in DEFAULT_BREAKERS:
        existing = await db[CB_COLLECTION].find_one({"breaker_id": breaker["breaker_id"]})
        if not existing:
            breaker["created_at"] = datetime.now(timezone.utc).isoformat()
            breaker["tripped_at"] = None
            breaker["recovered_at"] = None
            breaker["trip_count"] = 0
            await db[CB_COLLECTION].insert_one(breaker)


async def get_all_breakers():
    """Get all circuit breaker states."""
    cursor = db[CB_COLLECTION].find({}, {"_id": 0})
    return await cursor.to_list(length=50)


async def update_breaker_value(breaker_id: str, new_value: float):
    """Update the current value of a circuit breaker and check if it should trip."""
    breaker = await db[CB_COLLECTION].find_one({"breaker_id": breaker_id}, {"_id": 0})
    if not breaker:
        return None

    should_trip = new_value >= breaker["trigger_threshold"]
    updates = {"current_value": new_value}

    if should_trip and breaker["status"] == "closed":
        updates["status"] = "open"
        updates["tripped_at"] = datetime.now(timezone.utc).isoformat()
        await db[CB_COLLECTION].update_one(
            {"breaker_id": breaker_id},
            {"$set": updates, "$inc": {"trip_count": 1}},
        )
        await log_action(
            "circuit_breaker_tripped", "system", "circuit_breaker",
            "breaker", breaker_id,
            {"value": new_value, "threshold": breaker["trigger_threshold"], "action": breaker["action_on_trip"]},
            result="tripped",
        )
        return {"breaker_id": breaker_id, "status": "open", "action": breaker["action_on_trip"], "tripped": True}
    else:
        await db[CB_COLLECTION].update_one(
            {"breaker_id": breaker_id}, {"$set": updates}
        )
        return {"breaker_id": breaker_id, "status": breaker["status"], "tripped": False}


async def reset_breaker(breaker_id: str):
    """Manually reset a tripped circuit breaker."""
    await db[CB_COLLECTION].update_one(
        {"breaker_id": breaker_id},
        {"$set": {"status": "closed", "current_value": 0, "recovered_at": datetime.now(timezone.utc).isoformat()}},
    )
    await log_action("circuit_breaker_reset", "operator", "manual", "breaker", breaker_id)
    return {"breaker_id": breaker_id, "status": "closed"}


async def get_tripped_breakers():
    """Get all currently tripped circuit breakers."""
    cursor = db[CB_COLLECTION].find({"status": "open"}, {"_id": 0})
    return await cursor.to_list(length=50)
