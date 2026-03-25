"""MAARS Recovery System — Rollback, quarantine, retry, and incident management."""

from datetime import datetime, timezone
from db import db

RECOVERY_LOG = "recovery_actions"
QUARANTINE = "quarantined_agents"


def _now():
    return datetime.now(timezone.utc).isoformat()


async def quarantine_agent(agent_id: str, reason: str, quarantined_by: str = "system"):
    """Quarantine an agent, preventing it from executing tasks."""
    await db["agents"].update_one(
        {"agent_id": agent_id},
        {"$set": {"status": "quarantined", "quarantine_reason": reason, "quarantined_at": _now()}},
    )
    doc = {
        "agent_id": agent_id, "reason": reason, "quarantined_by": quarantined_by,
        "quarantined_at": _now(), "released": False,
    }
    await db[QUARANTINE].insert_one(doc)
    doc.pop("_id", None)
    return doc


async def release_from_quarantine(agent_id: str, released_by: str = "operator"):
    """Release an agent from quarantine."""
    await db["agents"].update_one(
        {"agent_id": agent_id},
        {"$set": {"status": "active", "quarantine_reason": None, "quarantined_at": None}},
    )
    await db[QUARANTINE].update_one(
        {"agent_id": agent_id, "released": False},
        {"$set": {"released": True, "released_by": released_by, "released_at": _now()}},
    )
    return {"agent_id": agent_id, "status": "released"}


async def get_quarantined_agents():
    cursor = db[QUARANTINE].find({"released": False}, {"_id": 0})
    return await cursor.to_list(length=100)


async def rollback_graph(graph_id: str, reason: str):
    """Mark a graph execution as rolled back."""
    await db["task_graphs"].update_one(
        {"graph_id": graph_id},
        {"$set": {"status": "rolled_back", "rollback_reason": reason, "rolled_back_at": _now()}},
    )
    await db["execution_runs"].update_one(
        {"graph_id": graph_id},
        {"$set": {"status": "rolled_back", "rollback_reason": reason}},
    )
    action = {
        "type": "rollback", "graph_id": graph_id, "reason": reason, "timestamp": _now(),
    }
    await db[RECOVERY_LOG].insert_one(action)
    action.pop("_id", None)
    return action


async def retry_failed_node(graph_id: str, node_id: str):
    """Retry a failed node in a task graph."""
    from kernel.task_graph import update_node_status
    await update_node_status(graph_id, node_id, {
        "status": "pending", "error_log": [], "retry_count_inc": True, "retried_at": _now(),
    })
    action = {"type": "retry", "graph_id": graph_id, "node_id": node_id, "timestamp": _now()}
    await db[RECOVERY_LOG].insert_one(action)
    action.pop("_id", None)
    return action


async def get_recovery_log(limit: int = 30):
    cursor = db[RECOVERY_LOG].find({}, {"_id": 0}).sort("timestamp", -1).limit(limit)
    return await cursor.to_list(length=limit)
