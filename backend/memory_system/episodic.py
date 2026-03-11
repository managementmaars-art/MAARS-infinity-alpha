"""MAARS — Memory: Episodic Memory.
Records event sequences and outcomes so agents learn from experience."""

from datetime import datetime, timezone
from db import db

EP_COLLECTION = "memory_episodic"


async def record_episode(agent_id: str, event_type: str, event_data: dict, outcome: str = "", lessons_learned: str = ""):
    """Record an episodic memory entry."""
    episode = {
        "agent_id": agent_id,
        "event_type": event_type,
        "event_data": event_data,
        "outcome": outcome,
        "lessons_learned": lessons_learned,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    await db[EP_COLLECTION].insert_one(episode)
    episode.pop("_id", None)
    return episode


async def recall_episodes(agent_id: str, event_type: str = None, limit: int = 20):
    """Recall episodic memories for an agent, optionally filtered by event type."""
    query = {"agent_id": agent_id}
    if event_type:
        query["event_type"] = event_type
    cursor = db[EP_COLLECTION].find(query, {"_id": 0}).sort("timestamp", -1).limit(limit)
    return await cursor.to_list(length=limit)


async def recall_similar(event_type: str, limit: int = 10):
    """Recall episodes across all agents for a given event type (collective learning)."""
    cursor = db[EP_COLLECTION].find({"event_type": event_type}, {"_id": 0}).sort("timestamp", -1).limit(limit)
    return await cursor.to_list(length=limit)


async def get_lessons(agent_id: str = None, limit: int = 20):
    """Get episodes that have lessons learned (for learning loops)."""
    query = {"lessons_learned": {"$ne": ""}}
    if agent_id:
        query["agent_id"] = agent_id
    cursor = db[EP_COLLECTION].find(query, {"_id": 0}).sort("timestamp", -1).limit(limit)
    return await cursor.to_list(length=limit)
