"""MAARS — Governance: Trust Scoring Engine.
Dynamic trust scores for agents, tools, and models based on performance."""

from datetime import datetime, timezone
from db import db

TRUST_COLLECTION = "trust_scores"


async def get_trust_score(entity_type: str, entity_id: str):
    """Get trust score for an entity."""
    doc = await db[TRUST_COLLECTION].find_one(
        {"entity_type": entity_type, "entity_id": entity_id}, {"_id": 0}
    )
    if not doc:
        doc = {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "score": 50.0,
            "factors": {
                "verification_pass_rate": 0.0,
                "compliance": 1.0,
                "usefulness": 0.5,
                "cost_efficiency": 0.5,
                "incident_rate": 0.0,
            },
            "history": [],
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }
        await db[TRUST_COLLECTION].insert_one({**doc})
    return doc


async def update_trust_score(entity_type: str, entity_id: str, event: dict):
    """Update trust score based on a new event.
    event: {type, verification_passed, had_incident, cost_efficient, useful}"""
    current = await get_trust_score(entity_type, entity_id)
    factors = current["factors"]

    # Weighted update based on event type
    if event.get("verification_passed") is not None:
        old = factors.get("verification_pass_rate", 0.5)
        factors["verification_pass_rate"] = round(old * 0.9 + (1.0 if event["verification_passed"] else 0.0) * 0.1, 3)

    if event.get("had_incident"):
        old = factors.get("incident_rate", 0.0)
        factors["incident_rate"] = round(min(1.0, old * 0.9 + 0.1), 3)
    else:
        factors["incident_rate"] = round(factors.get("incident_rate", 0.0) * 0.95, 3)

    if event.get("cost_efficient") is not None:
        old = factors.get("cost_efficiency", 0.5)
        factors["cost_efficiency"] = round(old * 0.9 + (1.0 if event["cost_efficient"] else 0.0) * 0.1, 3)

    if event.get("useful") is not None:
        old = factors.get("usefulness", 0.5)
        factors["usefulness"] = round(old * 0.9 + (1.0 if event["useful"] else 0.0) * 0.1, 3)

    # Compute composite score (0-100)
    weights = {
        "verification_pass_rate": 30,
        "compliance": 20,
        "usefulness": 20,
        "cost_efficiency": 15,
        "incident_rate": 15,
    }
    raw = sum(factors.get(k, 0.5) * w for k, w in weights.items())
    # Incident rate is inverse (lower is better)
    raw -= factors.get("incident_rate", 0) * weights["incident_rate"] * 2
    score = round(max(0, min(100, raw)), 1)

    history_entry = {"score": score, "timestamp": datetime.now(timezone.utc).isoformat()}

    await db[TRUST_COLLECTION].update_one(
        {"entity_type": entity_type, "entity_id": entity_id},
        {
            "$set": {"score": score, "factors": factors, "last_updated": history_entry["timestamp"]},
            "$push": {"history": {"$each": [history_entry], "$slice": -100}},
        },
        upsert=True,
    )
    return {"entity_type": entity_type, "entity_id": entity_id, "score": score, "factors": factors}


async def get_trust_leaderboard(entity_type: str = "agent", limit: int = 20):
    """Get top-scoring entities."""
    cursor = (
        db[TRUST_COLLECTION]
        .find({"entity_type": entity_type}, {"_id": 0, "history": 0})
        .sort("score", -1)
        .limit(limit)
    )
    return await cursor.to_list(length=limit)


async def get_low_trust_entities(entity_type: str = None, threshold: float = 30.0):
    """Get entities below trust threshold for review."""
    query = {"score": {"$lt": threshold}}
    if entity_type:
        query["entity_type"] = entity_type
    cursor = db[TRUST_COLLECTION].find(query, {"_id": 0, "history": 0})
    return await cursor.to_list(length=50)
