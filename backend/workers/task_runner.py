"""
Simple async task runner — in-process background queue for long-running
orchestrator runs, Stripe reconciliation, etc. No external broker needed;
suitable for single-process deployments. When you need distribution, swap
this for RQ / Celery / Arq without changing callers.

Submitted tasks are stored in MongoDB (`background_tasks` collection) so an
admin can see status / results across a crash/restart. The in-process loop
only dispatches — persistence is the system of record.
"""
from __future__ import annotations

import asyncio
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable, Optional

from db import db

logger = logging.getLogger(__name__)

TASKS_COLLECTION = "background_tasks"

# Registry of known task handlers.
_HANDLERS: dict[str, Callable[..., Awaitable[Any]]] = {}


def register_handler(name: str, fn: Callable[..., Awaitable[Any]]) -> None:
    _HANDLERS[name] = fn


def list_handlers() -> list[str]:
    return sorted(_HANDLERS.keys())


# --------------------------------------------------------------------------- submit + run

async def submit(
    *,
    kind: str,
    payload: dict[str, Any],
    user_id: Optional[str] = None,
    max_retries: int = 2,
    timeout_seconds: float = 600.0,
) -> dict[str, Any]:
    """Enqueue a task. Returns immediately with task_id; worker runs async."""
    if kind not in _HANDLERS:
        raise ValueError(f"unknown task kind: {kind}")
    task_id = f"task_{uuid.uuid4().hex[:16]}"
    doc = {
        "task_id": task_id,
        "kind": kind,
        "payload": payload,
        "user_id": user_id,
        "status": "queued",
        "attempts": 0,
        "max_retries": int(max_retries),
        "timeout_seconds": float(timeout_seconds),
        "result": None,
        "error": "",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "started_at": None,
        "ended_at": None,
    }
    await db[TASKS_COLLECTION].insert_one(doc)
    asyncio.create_task(_run(task_id))
    return {k: v for k, v in doc.items() if k != "_id"}


async def _run(task_id: str) -> None:
    task = await db[TASKS_COLLECTION].find_one({"task_id": task_id}, {"_id": 0})
    if not task:
        return
    kind = task["kind"]
    handler = _HANDLERS.get(kind)
    if handler is None:
        await _mark(task_id, status="error", error=f"no handler for kind: {kind}")
        return

    for attempt in range(task["max_retries"] + 1):
        await db[TASKS_COLLECTION].update_one(
            {"task_id": task_id},
            {"$set": {
                "status": "running",
                "attempts": attempt + 1,
                "started_at": datetime.now(timezone.utc).isoformat(),
            }},
        )
        t0 = time.time()
        try:
            result = await asyncio.wait_for(
                handler(**task["payload"]),
                timeout=task["timeout_seconds"],
            )
            await _mark(
                task_id, status="complete", result=result,
                latency_ms=int((time.time() - t0) * 1000),
            )
            return
        except asyncio.TimeoutError:
            err = f"timeout after {task['timeout_seconds']}s"
        except Exception as exc:
            err = f"{type(exc).__name__}: {exc}"
            logger.warning("task %s attempt %d failed: %s", task_id, attempt + 1, err)

        if attempt >= task["max_retries"]:
            await _mark(task_id, status="error", error=err,
                        latency_ms=int((time.time() - t0) * 1000))
            return
        # Exponential backoff between retries.
        await asyncio.sleep(2 ** attempt)


async def _mark(task_id: str, *, status: str, result: Any = None,
                error: str = "", latency_ms: int = 0) -> None:
    update: dict[str, Any] = {
        "status": status,
        "ended_at": datetime.now(timezone.utc).isoformat(),
        "latency_ms": latency_ms,
    }
    if result is not None:
        update["result"] = result
    if error:
        update["error"] = error
    await db[TASKS_COLLECTION].update_one({"task_id": task_id}, {"$set": update})


# --------------------------------------------------------------------------- reads

async def get(task_id: str) -> Optional[dict[str, Any]]:
    return await db[TASKS_COLLECTION].find_one({"task_id": task_id}, {"_id": 0})


async def list_tasks(
    *, user_id: Optional[str] = None, limit: int = 50, status: Optional[str] = None,
) -> list[dict[str, Any]]:
    q: dict[str, Any] = {}
    if user_id:
        q["user_id"] = user_id
    if status:
        q["status"] = status
    cursor = db[TASKS_COLLECTION].find(q, {"_id": 0}).sort("created_at", -1).limit(int(limit))
    return [d async for d in cursor]


async def ensure_indexes() -> None:
    await db[TASKS_COLLECTION].create_index("task_id", unique=True, name="task_id_unique")
    await db[TASKS_COLLECTION].create_index(
        [("user_id", 1), ("created_at", -1)], name="task_by_user_time"
    )
    await db[TASKS_COLLECTION].create_index("status", name="task_by_status")


# --------------------------------------------------------------------------- default handlers

async def _handler_orchestrator_run(**kwargs: Any) -> Any:
    """Default handler: run the agent orchestrator in the background."""
    from services.agents import agent_orchestrator
    run = await agent_orchestrator.run(**kwargs)
    return run.to_dict()


register_handler("orchestrator.run", _handler_orchestrator_run)
