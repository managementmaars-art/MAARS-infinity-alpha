"""MAARS Kernel — Budget Controller.
Tracks real-time spend per entity (agent, workflow, user, system).
Enforces hard limits and fires alerts at configurable thresholds."""

from datetime import datetime, timezone
from db import db
from governance.audit import log_action

BUDGET_COLLECTION = "budget_tracking"
DEFAULTS = {"daily_limit": 100.0, "monthly_limit": 2000.0, "alert_threshold": 0.8}


async def get_budget(entity_type: str, entity_id: str, period: str = "daily"):
    """Get current budget state for an entity."""
    doc = await db[BUDGET_COLLECTION].find_one(
        {"entity_type": entity_type, "entity_id": entity_id, "period": period},
        {"_id": 0},
    )
    if not doc:
        doc = {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "period": period,
            "allocated": DEFAULTS.get(f"{period}_limit", 100.0),
            "spent": 0.0,
            "remaining": DEFAULTS.get(f"{period}_limit", 100.0),
            "alerts": [],
            "transactions": [],
        }
        await db[BUDGET_COLLECTION].insert_one({**doc})
    return doc


async def record_spend(
    entity_type: str,
    entity_id: str,
    amount: float,
    model: str = "",
    task_id: str = "",
    period: str = "daily",
):
    """Record a spend transaction. Returns (allowed, budget_state, alert)."""
    budget = await get_budget(entity_type, entity_id, period)
    new_spent = budget["spent"] + amount
    remaining = budget["allocated"] - new_spent

    alert = None
    allowed = True

    if remaining <= 0:
        allowed = False
        alert = "budget_exceeded"
        await log_action(
            "budget_exceeded", entity_type, entity_id,
            details={"amount": amount, "spent": new_spent, "limit": budget["allocated"]},
            result="blocked",
        )
    elif new_spent >= budget["allocated"] * DEFAULTS["alert_threshold"]:
        alert = "budget_warning"

    if allowed:
        tx = {
            "amount": amount,
            "model": model,
            "task_id": task_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        await db[BUDGET_COLLECTION].update_one(
            {"entity_type": entity_type, "entity_id": entity_id, "period": period},
            {
                "$set": {"spent": new_spent, "remaining": remaining},
                "$push": {
                    "transactions": {"$each": [tx], "$slice": -500},
                    **({"alerts": alert} if alert else {}),
                },
            },
            upsert=True,
        )

    return {
        "allowed": allowed,
        "spent": new_spent if allowed else budget["spent"],
        "remaining": remaining if allowed else budget["remaining"],
        "allocated": budget["allocated"],
        "alert": alert,
    }


async def set_budget_limit(entity_type: str, entity_id: str, period: str, limit: float):
    """Set or update a budget limit."""
    await db[BUDGET_COLLECTION].update_one(
        {"entity_type": entity_type, "entity_id": entity_id, "period": period},
        {"$set": {"allocated": limit, "remaining": limit}},
        upsert=True,
    )
    await log_action(
        "budget_limit_set", "system", "budget_controller",
        target_type=entity_type, target_id=entity_id,
        details={"period": period, "limit": limit},
    )
    return {"entity_type": entity_type, "entity_id": entity_id, "period": period, "allocated": limit}


async def get_spend_summary(entity_type: str = None, period: str = "daily"):
    """Get spend summary across all entities or filtered."""
    query = {"period": period}
    if entity_type:
        query["entity_type"] = entity_type
    cursor = db[BUDGET_COLLECTION].find(query, {"_id": 0, "transactions": 0})
    return await cursor.to_list(length=200)
