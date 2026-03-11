"""MAARS — Memory: Working Memory.
Active task context that agents use during execution. Scoped to task_id."""

from datetime import datetime, timezone
from db import db

WM_COLLECTION = "memory_working"


async def store_working(task_id: str, agent_id: str, context: dict, intermediate_results: list = None):
    """Store or update working memory for a task."""
    await db[WM_COLLECTION].update_one(
        {"task_id": task_id, "agent_id": agent_id},
        {"$set": {
            "context": context,
            "intermediate_results": intermediate_results or [],
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }, "$setOnInsert": {"created_at": datetime.now(timezone.utc).isoformat()}},
        upsert=True,
    )
    return {"task_id": task_id, "agent_id": agent_id, "status": "stored"}


async def get_working(task_id: str, agent_id: str = None):
    """Retrieve working memory for a task."""
    query = {"task_id": task_id}
    if agent_id:
        query["agent_id"] = agent_id
    cursor = db[WM_COLLECTION].find(query, {"_id": 0})
    return await cursor.to_list(length=20)


async def append_result(task_id: str, agent_id: str, result: dict):
    """Append an intermediate result to working memory."""
    result["timestamp"] = datetime.now(timezone.utc).isoformat()
    await db[WM_COLLECTION].update_one(
        {"task_id": task_id, "agent_id": agent_id},
        {"$push": {"intermediate_results": {"$each": [result], "$slice": -50}},
         "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}},
        upsert=True,
    )
    return {"task_id": task_id, "appended": True}


async def clear_working(task_id: str):
    """Clear working memory for a completed task."""
    result = await db[WM_COLLECTION].delete_many({"task_id": task_id})
    return {"task_id": task_id, "cleared": result.deleted_count}
