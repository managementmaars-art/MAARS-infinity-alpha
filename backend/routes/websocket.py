"""WebSocket endpoint for real-time activity streaming."""
import json
import asyncio
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from db import db

logger = logging.getLogger(__name__)
router = APIRouter()

# Track connected clients per user
_connections: dict[str, list[WebSocket]] = {}


async def broadcast_activity(user_id: str, event: dict):
    """Broadcast an activity event to all connected clients for a user."""
    if user_id not in _connections:
        return
    dead = []
    for ws in _connections[user_id]:
        try:
            await ws.send_json(event)
        except Exception:
            dead.append(ws)
    for ws in dead:
        _connections[user_id].remove(ws)


async def _get_activity_snapshot(user_id: str) -> dict:
    """Get a full activity snapshot for a user (same data as /activity/live)."""
    active_projects = await db.projects.find(
        {"user_id": user_id, "status": "in_progress"}, {"_id": 0, "project_id": 1, "title": 1, "goal": 1, "status": 1}
    ).to_list(10)

    recent_tasks = await db.tasks.find(
        {"user_id": user_id}, {"_id": 0, "task_id": 1, "title": 1, "status": 1, "agent_name": 1, "agent_role": 1, "project_id": 1, "created_at": 1, "updated_at": 1}
    ).sort("updated_at", -1).limit(50).to_list(50)

    recent_collabs = await db.collaborations.find(
        {"user_id": user_id}, {"_id": 0}
    ).sort("created_at", -1).limit(30).to_list(30)

    recent_tools = await db.tool_calls.find(
        {"user_id": user_id}, {"_id": 0, "tool_name": 1, "agent_name": 1, "status": 1, "timestamp": 1}
    ).sort("timestamp", -1).limit(30).to_list(30)

    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$group": {"_id": "$agent_name", "task_count": {"$sum": 1}, "completed": {"$sum": {"$cond": [{"$eq": ["$status", "completed"]}, 1, 0]}}, "latest": {"$max": "$updated_at"}}},
        {"$sort": {"task_count": -1}}
    ]
    agent_activity = await db.tasks.aggregate(pipeline).to_list(50)

    comm_flows = []
    seen = set()
    for c in recent_collabs:
        sender = c.get("sender", "")
        for r in c.get("receivers", []):
            key = f"{sender}->{r}"
            if key not in seen:
                seen.add(key)
                comm_flows.append({"from": sender, "to": r, "objective": c.get("objective", "")[:80], "status": c.get("status", "pending")})

    dependencies = []
    for t in recent_tasks:
        if t.get("project_id"):
            dependencies.append({"task_id": t.get("task_id", ""), "title": t.get("title", "")[:60], "agent": t.get("agent_name", ""), "status": t.get("status", ""), "project_id": t.get("project_id", "")})

    return {
        "type": "snapshot",
        "active_projects": active_projects,
        "agent_activity": [{"agent": a["_id"] or "Unknown", "task_count": a["task_count"], "completed": a["completed"], "latest": a.get("latest", "")} for a in agent_activity],
        "communication_flows": comm_flows,
        "task_graph": dependencies[:30],
        "recent_tool_calls": recent_tools[:15],
        "recent_collabs": recent_collabs[:10],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.websocket("/ws/activity")
async def ws_activity(websocket: WebSocket, token: str = Query("")):
    """WebSocket endpoint for real-time activity updates."""
    if not token:
        await websocket.close(code=4001, reason="Missing token")
        return

    from auth import verify_token
    user = await verify_token(token)
    if not user:
        await websocket.close(code=4001, reason="Invalid token")
        return

    user_id = user.user_id
    await websocket.accept()

    # Register connection
    if user_id not in _connections:
        _connections[user_id] = []
    _connections[user_id].append(websocket)

    try:
        # Send initial snapshot
        snapshot = await _get_activity_snapshot(user_id)
        await websocket.send_json(snapshot)

        # Keep connection alive and send periodic updates
        while True:
            try:
                # Wait for client messages (ping/pong) or timeout
                msg = await asyncio.wait_for(websocket.receive_text(), timeout=8.0)
                if msg == "ping":
                    await websocket.send_json({"type": "pong", "timestamp": datetime.now(timezone.utc).isoformat()})
                elif msg == "refresh":
                    snapshot = await _get_activity_snapshot(user_id)
                    await websocket.send_json(snapshot)
            except asyncio.TimeoutError:
                # Send periodic update every 8 seconds
                snapshot = await _get_activity_snapshot(user_id)
                await websocket.send_json(snapshot)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        if user_id in _connections:
            try:
                _connections[user_id].remove(websocket)
            except ValueError:
                pass
            if not _connections[user_id]:
                del _connections[user_id]
