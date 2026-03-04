"""Memory Governance — versioning, relevance scoring, pruning for agent memory."""
import uuid
import math
import logging
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from db import db
from auth import get_current_user, User

logger = logging.getLogger(__name__)
router = APIRouter()

RELEVANCE_HALF_LIFE_DAYS = 30
MAX_MEMORY_PER_USER = 500


def _relevance_score(created_at: str, access_count: int, importance: float) -> float:
    """Calculate relevance using time-decay + access frequency + importance."""
    try:
        created = datetime.fromisoformat(created_at)
    except (ValueError, TypeError):
        created = datetime.now(timezone.utc) - timedelta(days=30)
    age_days = max((datetime.now(timezone.utc) - created.replace(tzinfo=timezone.utc if created.tzinfo is None else created.tzinfo)).days, 0)
    decay = math.pow(0.5, age_days / RELEVANCE_HALF_LIFE_DAYS)
    freq_bonus = min(access_count * 0.05, 0.5)
    return round(min(decay * importance + freq_bonus, 1.0), 4)


@router.get("/memory/entries")
async def list_memory_entries(
    page: int = 1,
    limit: int = 30,
    sort_by: str = "relevance",
    agent_id: str = "",
    current_user: User = Depends(get_current_user),
):
    """List all memory entries for current user with relevance scores."""
    user_id = current_user.user_id
    query = {"user_id": user_id}
    if agent_id:
        query["agent_id"] = agent_id

    skip = (page - 1) * limit
    entries = await db.memory_entries.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).to_list(limit)
    total = await db.memory_entries.count_documents(query)

    for e in entries:
        e["relevance_score"] = _relevance_score(
            e.get("created_at", ""),
            e.get("access_count", 0),
            e.get("importance", 0.5),
        )

    if sort_by == "relevance":
        entries.sort(key=lambda x: x["relevance_score"], reverse=True)

    stats = await _memory_stats(user_id)

    return {
        "entries": entries,
        "total": total,
        "page": page,
        "pages": max(1, -(-total // limit)),
        "stats": stats,
    }


@router.post("/memory/entries")
async def create_memory_entry(request: Request, current_user: User = Depends(get_current_user)):
    """Create a new memory entry."""
    data = await request.json()
    user_id = current_user.user_id

    count = await db.memory_entries.count_documents({"user_id": user_id})
    if count >= MAX_MEMORY_PER_USER:
        raise HTTPException(400, f"Memory limit reached ({MAX_MEMORY_PER_USER}). Prune old entries first.")

    now = datetime.now(timezone.utc).isoformat()
    entry = {
        "memory_id": f"mem_{uuid.uuid4().hex[:12]}",
        "user_id": user_id,
        "agent_id": data.get("agent_id", ""),
        "agent_name": data.get("agent_name", ""),
        "category": data.get("category", "general"),
        "content": data.get("content", ""),
        "summary": data.get("summary", ""),
        "importance": min(max(float(data.get("importance", 0.5)), 0), 1),
        "access_count": 0,
        "version": 1,
        "versions": [{
            "version": 1,
            "content": data.get("content", ""),
            "updated_at": now,
            "reason": "Initial creation",
        }],
        "tags": data.get("tags", []),
        "source": data.get("source", "manual"),
        "created_at": now,
        "updated_at": now,
    }

    await db.memory_entries.insert_one(entry)
    entry.pop("_id", None)
    entry["relevance_score"] = _relevance_score(now, 0, entry["importance"])
    return entry


@router.put("/memory/entries/{memory_id}")
async def update_memory_entry(memory_id: str, request: Request, current_user: User = Depends(get_current_user)):
    """Update a memory entry, creating a new version."""
    data = await request.json()
    existing = await db.memory_entries.find_one({"memory_id": memory_id, "user_id": current_user.user_id}, {"_id": 0})
    if not existing:
        raise HTTPException(404, "Memory entry not found")

    now = datetime.now(timezone.utc).isoformat()
    new_version = existing.get("version", 1) + 1
    new_content = data.get("content", existing["content"])

    version_entry = {
        "version": new_version,
        "content": new_content,
        "updated_at": now,
        "reason": data.get("reason", "Manual update"),
    }

    update = {
        "$set": {
            "content": new_content,
            "summary": data.get("summary", existing.get("summary", "")),
            "importance": min(max(float(data.get("importance", existing.get("importance", 0.5))), 0), 1),
            "category": data.get("category", existing.get("category", "general")),
            "tags": data.get("tags", existing.get("tags", [])),
            "version": new_version,
            "updated_at": now,
        },
        "$push": {"versions": version_entry},
    }

    await db.memory_entries.update_one({"memory_id": memory_id, "user_id": current_user.user_id}, update)
    updated = await db.memory_entries.find_one({"memory_id": memory_id}, {"_id": 0})
    updated["relevance_score"] = _relevance_score(updated.get("created_at", ""), updated.get("access_count", 0), updated.get("importance", 0.5))
    return updated


@router.delete("/memory/entries/{memory_id}")
async def delete_memory_entry(memory_id: str, current_user: User = Depends(get_current_user)):
    """Delete a memory entry."""
    result = await db.memory_entries.delete_one({"memory_id": memory_id, "user_id": current_user.user_id})
    if result.deleted_count == 0:
        raise HTTPException(404, "Memory entry not found")
    return {"message": "Memory entry deleted", "memory_id": memory_id}


@router.get("/memory/entries/{memory_id}/versions")
async def get_memory_versions(memory_id: str, current_user: User = Depends(get_current_user)):
    """Get version history for a memory entry."""
    entry = await db.memory_entries.find_one({"memory_id": memory_id, "user_id": current_user.user_id}, {"_id": 0})
    if not entry:
        raise HTTPException(404, "Memory entry not found")

    # Increment access count
    await db.memory_entries.update_one(
        {"memory_id": memory_id},
        {"$inc": {"access_count": 1}},
    )

    return {
        "memory_id": memory_id,
        "current_version": entry.get("version", 1),
        "versions": entry.get("versions", []),
    }


@router.post("/memory/prune")
async def prune_memories(request: Request, current_user: User = Depends(get_current_user)):
    """Prune low-relevance memory entries."""
    data = await request.json()
    threshold = float(data.get("threshold", 0.15))
    dry_run = data.get("dry_run", True)

    user_id = current_user.user_id
    entries = await db.memory_entries.find({"user_id": user_id}, {"_id": 0}).to_list(MAX_MEMORY_PER_USER)

    to_prune = []
    for e in entries:
        score = _relevance_score(e.get("created_at", ""), e.get("access_count", 0), e.get("importance", 0.5))
        if score < threshold:
            to_prune.append({"memory_id": e["memory_id"], "content_preview": e.get("content", "")[:60], "relevance_score": score})

    if not dry_run and to_prune:
        ids = [p["memory_id"] for p in to_prune]
        result = await db.memory_entries.delete_many({"memory_id": {"$in": ids}, "user_id": user_id})
        return {"pruned": result.deleted_count, "entries": to_prune, "dry_run": False}

    return {"candidates": len(to_prune), "entries": to_prune, "dry_run": True, "threshold": threshold}


@router.get("/memory/stats")
async def get_memory_stats(current_user: User = Depends(get_current_user)):
    """Get memory usage stats."""
    return await _memory_stats(current_user.user_id)


async def _memory_stats(user_id: str) -> dict:
    """Compute memory stats for a user."""
    total = await db.memory_entries.count_documents({"user_id": user_id})
    entries = await db.memory_entries.find({"user_id": user_id}, {"_id": 0, "created_at": 1, "access_count": 1, "importance": 1, "category": 1, "agent_id": 1}).to_list(MAX_MEMORY_PER_USER)

    scores = [_relevance_score(e.get("created_at", ""), e.get("access_count", 0), e.get("importance", 0.5)) for e in entries]
    avg_relevance = round(sum(scores) / max(len(scores), 1), 4)
    low_relevance = sum(1 for s in scores if s < 0.15)

    # Category breakdown
    categories = {}
    for e in entries:
        cat = e.get("category", "general")
        categories[cat] = categories.get(cat, 0) + 1

    # Agent breakdown
    agents = {}
    for e in entries:
        aid = e.get("agent_id", "system")
        agents[aid] = agents.get(aid, 0) + 1

    return {
        "total_entries": total,
        "max_entries": MAX_MEMORY_PER_USER,
        "usage_pct": round(total / MAX_MEMORY_PER_USER * 100, 1),
        "avg_relevance": avg_relevance,
        "low_relevance_count": low_relevance,
        "categories": categories,
        "agents": agents,
    }
