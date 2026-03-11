"""MAARS Kernel — Audit Logger.
Immutable append-only audit log for every action in the system."""

from datetime import datetime, timezone
from db import db

AUDIT_COLLECTION = "audit_log"


async def log_action(
    action: str,
    actor_type: str,
    actor_id: str,
    target_type: str = "",
    target_id: str = "",
    details: dict = None,
    result: str = "success",
):
    """Append an immutable audit entry. Returns the inserted id string."""
    entry = {
        "action": action,
        "actor_type": actor_type,
        "actor_id": actor_id,
        "target_type": target_type,
        "target_id": target_id,
        "details": details or {},
        "result": result,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "immutable": True,
    }
    res = await db[AUDIT_COLLECTION].insert_one(entry)
    return str(res.inserted_id)


async def query_audit_log(
    filters: dict = None,
    skip: int = 0,
    limit: int = 50,
    sort_desc: bool = True,
):
    """Query audit log with pagination. Filters can include action, actor_id, target_type, etc."""
    query = {}
    if filters:
        if filters.get("action"):
            query["action"] = filters["action"]
        if filters.get("actor_id"):
            query["actor_id"] = filters["actor_id"]
        if filters.get("target_type"):
            query["target_type"] = filters["target_type"]
        if filters.get("target_id"):
            query["target_id"] = filters["target_id"]
        if filters.get("from_date"):
            query.setdefault("timestamp", {})["$gte"] = filters["from_date"]
        if filters.get("to_date"):
            query.setdefault("timestamp", {})["$lte"] = filters["to_date"]

    sort_dir = -1 if sort_desc else 1
    cursor = (
        db[AUDIT_COLLECTION]
        .find(query, {"_id": 0})
        .sort("timestamp", sort_dir)
        .skip(skip)
        .limit(limit)
    )
    entries = await cursor.to_list(length=limit)
    total = await db[AUDIT_COLLECTION].count_documents(query)
    return {"entries": entries, "total": total, "skip": skip, "limit": limit}
