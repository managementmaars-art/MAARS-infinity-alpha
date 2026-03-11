"""MAARS — Portfolio: Venture Portfolio State Machine + Opportunity Scoring."""

from datetime import datetime, timezone
from db import db
from governance.audit import log_action

VENTURE_COLLECTION = "ventures"

STAGES = ["idea", "validation", "mvp", "growth", "scale", "mature", "sunset"]
ACTIONS = ["scale", "optimize", "pivot", "pause", "sunset", "kill"]


async def create_venture(name: str, description: str, stage: str = "idea", initial_investment: float = 0):
    """Create a new venture in the portfolio."""
    venture = {
        "name": name, "description": description, "status": "active", "stage": stage,
        "revenue": 0, "costs": initial_investment, "cac": 0, "ltv": 0,
        "burn_rate": 0, "runway_months": 0, "opportunity_score": 0,
        "next_action": "validate", "metrics_history": [],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    await db[VENTURE_COLLECTION].insert_one(venture)
    await log_action("venture_created", "system", "portfolio", "venture", name)
    venture.pop("_id", None)
    return venture


async def update_venture_metrics(name: str, metrics: dict):
    """Update venture financial metrics and compute opportunity score."""
    now = datetime.now(timezone.utc).isoformat()
    revenue = metrics.get("revenue", 0)
    costs = metrics.get("costs", 0)
    cac = metrics.get("cac", 0)
    ltv = metrics.get("ltv", 0)
    burn = costs - revenue if costs > revenue else 0
    runway = round(metrics.get("cash_on_hand", 0) / max(burn, 1)) if burn > 0 else 99
    margin = round((revenue - costs) / max(revenue, 1) * 100, 1)

    # Opportunity score (0-100)
    score = 50
    if ltv > 0 and cac > 0:
        ltv_cac = ltv / cac
        score += min(25, ltv_cac * 5)
    if margin > 20:
        score += 10
    if revenue > 0:
        score += 10
    score = round(min(100, max(0, score)), 1)

    # Determine recommended action
    action = "optimize"
    if score >= 75:
        action = "scale"
    elif score >= 50:
        action = "optimize"
    elif score >= 30:
        action = "pivot"
    elif score >= 15:
        action = "pause"
    else:
        action = "kill"

    update = {
        "revenue": revenue, "costs": costs, "cac": cac, "ltv": ltv,
        "burn_rate": burn, "runway_months": runway,
        "opportunity_score": score, "next_action": action,
        "updated_at": now,
    }
    await db[VENTURE_COLLECTION].update_one(
        {"name": name},
        {"$set": update, "$push": {"metrics_history": {"$each": [{**metrics, "score": score, "timestamp": now}], "$slice": -100}}},
    )
    return {**update, "name": name, "margin": margin}


async def get_ventures(status: str = None):
    """List all ventures."""
    query = {}
    if status:
        query["status"] = status
    cursor = db[VENTURE_COLLECTION].find(query, {"_id": 0}).sort("opportunity_score", -1)
    return await cursor.to_list(length=100)


async def transition_venture(name: str, new_stage: str):
    """Transition a venture to a new stage."""
    if new_stage not in STAGES:
        return {"error": f"Invalid stage. Must be one of: {STAGES}"}
    await db[VENTURE_COLLECTION].update_one(
        {"name": name},
        {"$set": {"stage": new_stage, "updated_at": datetime.now(timezone.utc).isoformat()}},
    )
    await log_action("venture_transition", "system", "portfolio", "venture", name, {"new_stage": new_stage})
    return {"name": name, "stage": new_stage}


async def get_portfolio_summary():
    """Get aggregate portfolio metrics."""
    pipeline = [
        {"$match": {"status": "active"}},
        {"$group": {
            "_id": None,
            "total_ventures": {"$sum": 1},
            "total_revenue": {"$sum": "$revenue"},
            "total_costs": {"$sum": "$costs"},
            "avg_opportunity_score": {"$avg": "$opportunity_score"},
            "avg_runway": {"$avg": "$runway_months"},
        }},
        {"$project": {"_id": 0}},
    ]
    results = await db[VENTURE_COLLECTION].aggregate(pipeline).to_list(length=1)
    return results[0] if results else {"total_ventures": 0, "total_revenue": 0, "total_costs": 0}
