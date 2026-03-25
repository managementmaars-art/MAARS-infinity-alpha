"""MAARS Agent Catalog Manager.
Manages the full agent registry with maturity states, activation, search/filter, and admin controls."""

from datetime import datetime, timezone
from db import db

AGENT_COLLECTION = "agents"


async def get_catalog(
    network: str = None,
    maturity: str = None,
    search: str = None,
    capability: str = None,
    tier: int = None,
    limit: int = 50,
    skip: int = 0,
):
    """Query the agent catalog with filters."""
    query = {}
    if network:
        query["network"] = network
    if maturity:
        query["maturity"] = maturity
    if tier is not None:
        query["autonomy_tier"] = tier
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"role": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}},
            {"agent_id": {"$regex": search, "$options": "i"}},
        ]
    if capability:
        query["capabilities"] = {"$regex": capability, "$options": "i"}

    cursor = db[AGENT_COLLECTION].find(query, {"_id": 0}).sort("name", 1).skip(skip).limit(limit)
    agents = await cursor.to_list(length=limit)
    total = await db[AGENT_COLLECTION].count_documents(query)
    return {"agents": agents, "total": total, "skip": skip, "limit": limit}


async def get_agent_detail(agent_id: str):
    """Get full agent detail."""
    agent = await db[AGENT_COLLECTION].find_one({"agent_id": agent_id}, {"_id": 0})
    if not agent:
        return None
    # Get recent executions
    execs = await db["runtime_executions"].find(
        {"agent_id": agent_id}, {"_id": 0}
    ).sort("timestamp", -1).limit(5).to_list(length=5)
    # Get trust score
    trust = await db["trust_scores"].find_one(
        {"entity_id": agent_id}, {"_id": 0}
    )
    agent["recent_executions"] = execs
    agent["trust_detail"] = trust
    return agent


async def update_agent_maturity(agent_id: str, maturity: str):
    """Update agent maturity state."""
    valid = {"catalog-only", "experimental", "partial", "production-ready"}
    if maturity not in valid:
        return {"error": f"Invalid maturity. Must be one of: {valid}"}
    await db[AGENT_COLLECTION].update_one(
        {"agent_id": agent_id},
        {"$set": {"maturity": maturity, "maturity_updated_at": datetime.now(timezone.utc).isoformat()}},
    )
    return {"agent_id": agent_id, "maturity": maturity}


async def get_catalog_stats():
    """Get statistics about the agent catalog."""
    pipeline = [
        {"$facet": {
            "by_network": [{"$group": {"_id": "$network", "count": {"$sum": 1}}}, {"$sort": {"count": -1}}],
            "by_maturity": [{"$group": {"_id": "$maturity", "count": {"$sum": 1}}}],
            "by_tier": [{"$group": {"_id": "$autonomy_tier", "count": {"$sum": 1}}}, {"$sort": {"_id": 1}}],
            "total": [{"$count": "count"}],
        }}
    ]
    result = await db[AGENT_COLLECTION].aggregate(pipeline).to_list(length=1)
    if not result:
        return {}
    r = result[0]
    return {
        "total_agents": r["total"][0]["count"] if r["total"] else 0,
        "by_network": [{"network": d["_id"], "count": d["count"]} for d in r["by_network"]],
        "by_maturity": [{"maturity": d["_id"] or "production-ready", "count": d["count"]} for d in r["by_maturity"]],
        "by_tier": [{"tier": d["_id"], "count": d["count"]} for d in r["by_tier"]],
    }


async def get_networks():
    """Get all network definitions with agent counts."""
    from infinity_catalog import NETWORK_DEFINITIONS
    pipeline = [
        {"$group": {"_id": "$network", "count": {"$sum": 1}, "avg_trust": {"$avg": "$trust_score"}}},
    ]
    counts = await db[AGENT_COLLECTION].aggregate(pipeline).to_list(length=50)
    count_map = {d["_id"]: d for d in counts}
    networks = []
    for net_id, net_def in NETWORK_DEFINITIONS.items():
        c = count_map.get(net_id, {"count": 0, "avg_trust": 0})
        networks.append({
            "network_id": net_id,
            **net_def,
            "agent_count": c["count"],
            "avg_trust": round(c.get("avg_trust") or 0, 1),
        })
    return sorted(networks, key=lambda x: x["agent_count"], reverse=True)
