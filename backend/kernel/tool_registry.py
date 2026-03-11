"""MAARS — Kernel: Tool Registry with Health Monitoring & Schema Validation."""

from datetime import datetime, timezone
from db import db
from governance.audit import log_action

TOOL_COLLECTION = "tool_registry"
TOOL_HEALTH = "tool_health"


async def register_tool(tool_id: str, name: str, description: str, schema: dict, permissions: list = None, category: str = "general"):
    """Register a tool in the registry."""
    tool = {
        "tool_id": tool_id,
        "name": name,
        "description": description,
        "schema": schema,
        "permissions": permissions or ["all"],
        "category": category,
        "status": "active",
        "version": "1.0",
        "call_count": 0,
        "failure_count": 0,
        "avg_latency_ms": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db[TOOL_COLLECTION].update_one({"tool_id": tool_id}, {"$set": tool}, upsert=True)
    await log_action("tool_registered", "system", "tool_registry", "tool", tool_id)
    return tool


async def get_tools(category: str = None, status: str = "active"):
    """List registered tools."""
    query = {}
    if category:
        query["category"] = category
    if status:
        query["status"] = status
    cursor = db[TOOL_COLLECTION].find(query, {"_id": 0})
    return await cursor.to_list(length=200)


async def validate_schema(tool_id: str, input_data: dict):
    """Validate input against a tool's schema."""
    tool = await db[TOOL_COLLECTION].find_one({"tool_id": tool_id}, {"_id": 0})
    if not tool:
        return {"valid": False, "error": "tool_not_found"}
    schema = tool.get("schema", {})
    required = schema.get("required", [])
    missing = [f for f in required if f not in input_data]
    if missing:
        return {"valid": False, "error": f"missing_fields: {missing}"}
    return {"valid": True, "tool_id": tool_id}


async def record_tool_call(tool_id: str, success: bool, latency_ms: int):
    """Record a tool call for health tracking."""
    inc = {"call_count": 1}
    if not success:
        inc["failure_count"] = 1
    await db[TOOL_COLLECTION].update_one({"tool_id": tool_id}, {"$inc": inc})

    health = {
        "tool_id": tool_id,
        "success": success,
        "latency_ms": latency_ms,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    await db[TOOL_HEALTH].insert_one(health)


async def get_tool_health(tool_id: str = None):
    """Get tool health metrics."""
    match = {}
    if tool_id:
        match["tool_id"] = tool_id
    pipeline = [
        {"$match": match},
        {"$group": {
            "_id": "$tool_id",
            "total_calls": {"$sum": 1},
            "successes": {"$sum": {"$cond": ["$success", 1, 0]}},
            "avg_latency": {"$avg": "$latency_ms"},
        }},
        {"$project": {
            "_id": 0, "tool_id": "$_id", "total_calls": 1, "successes": 1,
            "avg_latency": {"$round": ["$avg_latency", 0]},
            "uptime": {"$round": [{"$multiply": [{"$divide": ["$successes", {"$max": ["$total_calls", 1]}]}, 100]}, 1]},
        }},
    ]
    return await db[TOOL_HEALTH].aggregate(pipeline).to_list(length=100)
