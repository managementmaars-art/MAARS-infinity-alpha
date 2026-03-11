"""MAARS Kernel — Agent Scheduler.
Assigns tasks to agents based on capabilities, trust, availability, and autonomy tier."""

from datetime import datetime, timezone
from db import db
from governance.audit import log_action

AGENT_COLLECTION = "agents"


async def find_best_agent(
    required_capabilities: list = None,
    required_network: str = None,
    min_trust_score: float = 0.0,
    max_autonomy_tier: int = 5,
    exclude_agents: list = None,
):
    """Find the best available agent matching requirements.
    Ranks by trust_score descending, then verification_pass_rate."""
    query = {"status": {"$ne": "disabled"}}
    if required_network:
        query["network"] = required_network
    if max_autonomy_tier < 5:
        query["autonomy_tier"] = {"$lte": max_autonomy_tier}
    if min_trust_score > 0:
        query["trust_score"] = {"$gte": min_trust_score}
    if exclude_agents:
        query["agent_id"] = {"$nin": exclude_agents}

    cursor = db[AGENT_COLLECTION].find(query, {"_id": 0}).sort("trust_score", -1).limit(20)
    candidates = await cursor.to_list(length=20)

    if required_capabilities:
        req_set = set(c.lower() for c in required_capabilities)
        scored = []
        for agent in candidates:
            agent_caps = set(c.lower() for c in agent.get("capabilities", []))
            overlap = len(req_set & agent_caps)
            if overlap > 0:
                scored.append((overlap, agent.get("trust_score", 50), agent))
        scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
        candidates = [s[2] for s in scored]

    return candidates[0] if candidates else None


async def assign_agent_to_task(agent_id: str, task_id: str, graph_id: str):
    """Record that an agent has been assigned to a task."""
    await db[AGENT_COLLECTION].update_one(
        {"agent_id": agent_id},
        {"$set": {"current_task_id": task_id, "current_graph_id": graph_id}},
    )
    await log_action(
        "agent_assigned", "system", "scheduler",
        "agent", agent_id,
        {"task_id": task_id, "graph_id": graph_id},
    )
    return {"agent_id": agent_id, "task_id": task_id, "status": "assigned"}


async def release_agent(agent_id: str):
    """Release an agent from its current task."""
    await db[AGENT_COLLECTION].update_one(
        {"agent_id": agent_id},
        {"$set": {"current_task_id": None, "current_graph_id": None}},
    )


async def update_agent_performance(agent_id: str, task_result: dict):
    """Update agent performance metrics after task completion."""
    inc_fields = {"performance.tasks_started": 0}
    if task_result.get("completed"):
        inc_fields["performance.tasks_completed"] = 1
    if task_result.get("retry_count", 0) > 0:
        inc_fields["performance.retry_count"] = task_result["retry_count"]
    if task_result.get("verification_passed"):
        inc_fields["performance.verification_passes"] = 1
    if task_result.get("incident"):
        inc_fields["performance.incident_count"] = 1

    await db[AGENT_COLLECTION].update_one(
        {"agent_id": agent_id},
        {"$inc": inc_fields},
    )


async def get_agent_workload():
    """Get current workload across all agents."""
    pipeline = [
        {"$match": {"status": {"$ne": "disabled"}}},
        {"$group": {
            "_id": "$network",
            "total": {"$sum": 1},
            "busy": {"$sum": {"$cond": [{"$ne": ["$current_task_id", None]}, 1, 0]}},
            "avg_trust": {"$avg": "$trust_score"},
        }},
        {"$project": {"_id": 0, "network": "$_id", "total": 1, "busy": 1, "avg_trust": 1}},
    ]
    return await db[AGENT_COLLECTION].aggregate(pipeline).to_list(length=50)
