"""MAARS Infinity — WebSocket streaming for real-time execution progress.
Provides live step-by-step updates during agent runtime and orchestrator execution."""

import asyncio
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

logger = logging.getLogger(__name__)
router = APIRouter()

# Track connected clients by channel
_infinity_connections: dict[str, list[WebSocket]] = {}


async def broadcast_execution_event(channel: str, event: dict):
    """Broadcast an execution event to all subscribers on a channel."""
    if channel not in _infinity_connections:
        return
    dead = []
    for ws in _infinity_connections[channel]:
        try:
            await ws.send_json(event)
        except Exception:
            dead.append(ws)
    for ws in dead:
        try:
            _infinity_connections[channel].remove(ws)
        except ValueError:
            pass
    if channel in _infinity_connections and not _infinity_connections[channel]:
        del _infinity_connections[channel]


async def broadcast_step(execution_id: str, step_name: str, status: str, detail: str = "", step_num: int = 0, total_steps: int = 13):
    """Broadcast a single runtime step update."""
    event = {
        "type": "step_update",
        "execution_id": execution_id,
        "step": step_name,
        "status": status,
        "detail": detail,
        "step_num": step_num,
        "total_steps": total_steps,
        "progress": round((step_num / max(total_steps, 1)) * 100),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    await broadcast_execution_event(f"exec:{execution_id}", event)
    await broadcast_execution_event("global", event)


async def broadcast_metrics_update(metrics: dict):
    """Broadcast live metrics to all observability subscribers."""
    event = {
        "type": "metrics_update",
        "metrics": metrics,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    await broadcast_execution_event("metrics", event)


async def broadcast_alert(alert: dict):
    """Broadcast a triggered alert."""
    event = {
        "type": "alert_triggered",
        "alert": alert,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    await broadcast_execution_event("metrics", event)
    await broadcast_execution_event("global", event)


async def broadcast_job_update(job_id: str, status: str, progress: int, detail: str = ""):
    """Broadcast worker job progress."""
    event = {
        "type": "job_update",
        "job_id": job_id,
        "status": status,
        "progress": progress,
        "detail": detail,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    await broadcast_execution_event(f"job:{job_id}", event)
    await broadcast_execution_event("global", event)


@router.websocket("/ws/infinity")
async def ws_infinity(websocket: WebSocket, token: str = Query(""), channel: str = Query("global")):
    """WebSocket endpoint for MAARS Infinity real-time streaming.
    
    Channels:
    - global: All events (executions, metrics, alerts, jobs)
    - metrics: Live metrics + alerts only
    - exec:{execution_id}: Specific execution progress
    - job:{job_id}: Specific job progress
    """
    if not token:
        await websocket.close(code=4001, reason="Missing token")
        return

    from auth import verify_token
    user = await verify_token(token)
    if not user:
        await websocket.close(code=4001, reason="Invalid token")
        return

    await websocket.accept()

    # Register on channel
    if channel not in _infinity_connections:
        _infinity_connections[channel] = []
    _infinity_connections[channel].append(websocket)

    try:
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connected",
            "channel": channel,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        while True:
            try:
                msg = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                if msg == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "channel": channel,
                        "active_channels": len(_infinity_connections),
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    })
                elif msg.startswith("subscribe:"):
                    new_channel = msg.split(":", 1)[1]
                    if new_channel not in _infinity_connections:
                        _infinity_connections[new_channel] = []
                    _infinity_connections[new_channel].append(websocket)
                    await websocket.send_json({"type": "subscribed", "channel": new_channel})
            except asyncio.TimeoutError:
                # Send heartbeat
                await websocket.send_json({
                    "type": "heartbeat",
                    "channel": channel,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"Infinity WS error: {e}")
    finally:
        # Remove from all channels
        for ch in list(_infinity_connections.keys()):
            if websocket in _infinity_connections.get(ch, []):
                try:
                    _infinity_connections[ch].remove(websocket)
                except ValueError:
                    pass
                if not _infinity_connections[ch]:
                    del _infinity_connections[ch]


def get_connection_stats():
    """Get WebSocket connection statistics."""
    return {
        "total_channels": len(_infinity_connections),
        "channels": {ch: len(conns) for ch, conns in _infinity_connections.items()},
        "total_connections": sum(len(c) for c in _infinity_connections.values()),
    }
