"""MAARS — Worker Queue Manager.
Async job queue for long-running LLM tasks and background processing.
Uses asyncio for non-blocking execution with MongoDB-backed persistence."""

import asyncio
import uuid
import time
import logging
from datetime import datetime, timezone
from db import db

logger = logging.getLogger(__name__)

JOBS_COLLECTION = "worker_jobs"
QUEUE_STATS_COLLECTION = "queue_stats"

# In-memory tracking for active workers
_active_jobs = {}
_job_callbacks = {}


def _now():
    return datetime.now(timezone.utc).isoformat()


def _uid():
    return str(uuid.uuid4())[:12]


async def enqueue_job(
    job_type: str,
    payload: dict,
    priority: int = 5,
    callback_url: str = None,
    max_retries: int = 2,
    timeout_seconds: int = 120,
):
    """Enqueue a new background job."""
    job_id = f"job-{_uid()}"
    job = {
        "job_id": job_id,
        "job_type": job_type,
        "payload": payload,
        "priority": priority,
        "status": "queued",
        "progress": 0,
        "result": None,
        "error": None,
        "retries": 0,
        "max_retries": max_retries,
        "timeout_seconds": timeout_seconds,
        "callback_url": callback_url,
        "created_at": _now(),
        "started_at": None,
        "completed_at": None,
    }
    await db[JOBS_COLLECTION].insert_one({**job})
    job.pop("_id", None)

    # Start processing in background
    asyncio.create_task(_process_job(job_id))

    return {"job_id": job_id, "status": "queued", "message": "Job enqueued for processing"}


async def _process_job(job_id: str):
    """Background worker that processes a queued job."""
    job = await db[JOBS_COLLECTION].find_one({"job_id": job_id}, {"_id": 0})
    if not job:
        return

    _active_jobs[job_id] = True
    await db[JOBS_COLLECTION].update_one(
        {"job_id": job_id},
        {"$set": {"status": "running", "started_at": _now()}},
    )

    try:
        job_type = job["job_type"]
        payload = job["payload"]

        if job_type == "llm_execution":
            result = await _execute_llm_job(job_id, payload)
        elif job_type == "agent_runtime":
            result = await _execute_agent_job(job_id, payload)
        elif job_type == "batch_analysis":
            result = await _execute_batch_job(job_id, payload)
        elif job_type == "search_and_report":
            result = await _execute_search_job(job_id, payload)
        else:
            result = {"output": f"Unknown job type: {job_type}", "status": "completed"}

        await db[JOBS_COLLECTION].update_one(
            {"job_id": job_id},
            {"$set": {
                "status": "completed",
                "progress": 100,
                "result": result,
                "completed_at": _now(),
            }},
        )

    except asyncio.TimeoutError:
        await _handle_job_failure(job_id, "Job timed out", job)
    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}")
        await _handle_job_failure(job_id, str(e), job)
    finally:
        _active_jobs.pop(job_id, None)


async def _handle_job_failure(job_id: str, error: str, job: dict):
    """Handle job failure with retry logic."""
    retries = job.get("retries", 0)
    max_retries = job.get("max_retries", 2)

    if retries < max_retries:
        await db[JOBS_COLLECTION].update_one(
            {"job_id": job_id},
            {"$set": {"status": "queued", "progress": 0}, "$inc": {"retries": 1}},
        )
        await asyncio.sleep(2 ** retries)  # exponential backoff
        asyncio.create_task(_process_job(job_id))
    else:
        await db[JOBS_COLLECTION].update_one(
            {"job_id": job_id},
            {"$set": {
                "status": "failed",
                "error": error,
                "completed_at": _now(),
            }},
        )


async def _update_progress(job_id: str, progress: int, detail: str = ""):
    """Update job progress (0-100)."""
    update = {"progress": progress}
    if detail:
        update["progress_detail"] = detail
    await db[JOBS_COLLECTION].update_one({"job_id": job_id}, {"$set": update})


async def _execute_llm_job(job_id: str, payload: dict):
    """Execute an LLM task in the background."""
    from router.engine import execute_routed_task

    await _update_progress(job_id, 10, "Routing to model")
    task = payload.get("task_description", "")
    context = payload.get("context", "")

    await _update_progress(job_id, 30, "Executing LLM call")
    result = await execute_routed_task(task, context)

    await _update_progress(job_id, 90, "Finalizing")
    return {
        "output": result.get("output", ""),
        "model": result.get("execution", {}).get("model", ""),
        "provider": result.get("execution", {}).get("provider", ""),
        "latency_ms": result.get("execution", {}).get("latency_ms", 0),
    }


async def _execute_agent_job(job_id: str, payload: dict):
    """Execute a full agent runtime loop in the background."""
    from runtime.agent_runtime import execute_agent_loop

    await _update_progress(job_id, 10, "Loading agent")
    agent_id = payload.get("agent_id", "")
    task = payload.get("task_description", "")
    env = payload.get("environment", "sandbox")

    await _update_progress(job_id, 20, "Running 13-step loop")
    result = await execute_agent_loop(agent_id, task, environment=env)

    await _update_progress(job_id, 90, "Completing")
    return {
        "execution_id": result.get("execution_id"),
        "status": result.get("status"),
        "output": result.get("output", "")[:500],
        "steps_completed": result.get("summary", {}).get("passed", 0),
    }


async def _execute_batch_job(job_id: str, payload: dict):
    """Execute a batch of tasks sequentially."""
    from router.engine import execute_routed_task

    tasks = payload.get("tasks", [])
    results = []
    total = len(tasks)

    for i, task in enumerate(tasks):
        pct = int(((i + 1) / max(total, 1)) * 90)
        await _update_progress(job_id, pct, f"Processing {i+1}/{total}")
        r = await execute_routed_task(task.get("description", ""), task.get("context", ""))
        results.append({
            "task": task.get("description", "")[:100],
            "output": r.get("output", "")[:300],
            "model": r.get("execution", {}).get("model", ""),
        })

    return {"batch_size": total, "completed": len(results), "results": results}


async def _execute_search_job(job_id: str, payload: dict):
    """Execute a search-and-report job."""
    from intelligence.search_engine import search_and_rank

    await _update_progress(job_id, 20, "Searching")
    query = payload.get("query", "")
    results = await search_and_rank(query)

    await _update_progress(job_id, 80, "Compiling report")
    return {
        "query": query,
        "results_count": len(results.get("results", [])),
        "results": results,
    }


async def get_job(job_id: str):
    """Get a job by ID."""
    doc = await db[JOBS_COLLECTION].find_one({"job_id": job_id}, {"_id": 0})
    return doc


async def list_jobs(status: str = None, job_type: str = None, limit: int = 20):
    """List jobs with optional filters."""
    query = {}
    if status:
        query["status"] = status
    if job_type:
        query["job_type"] = job_type
    cursor = db[JOBS_COLLECTION].find(query, {"_id": 0}).sort("created_at", -1).limit(limit)
    return await cursor.to_list(length=limit)


async def cancel_job(job_id: str):
    """Cancel a queued or running job."""
    job = await db[JOBS_COLLECTION].find_one({"job_id": job_id}, {"_id": 0})
    if not job:
        return {"error": "Job not found"}
    if job["status"] in ("completed", "failed", "cancelled"):
        return {"error": f"Job already {job['status']}"}

    _active_jobs.pop(job_id, None)
    await db[JOBS_COLLECTION].update_one(
        {"job_id": job_id},
        {"$set": {"status": "cancelled", "completed_at": _now()}},
    )
    return {"job_id": job_id, "status": "cancelled"}


async def get_queue_stats():
    """Get queue statistics."""
    pipeline = [
        {"$group": {"_id": "$status", "count": {"$sum": 1}}},
        {"$project": {"_id": 0, "status": "$_id", "count": 1}},
    ]
    status_counts = await db[JOBS_COLLECTION].aggregate(pipeline).to_list(length=10)

    type_pipeline = [
        {"$group": {"_id": "$job_type", "count": {"$sum": 1}}},
        {"$project": {"_id": 0, "job_type": "$_id", "count": 1}},
    ]
    type_counts = await db[JOBS_COLLECTION].aggregate(type_pipeline).to_list(length=20)

    active = len(_active_jobs)
    total = await db[JOBS_COLLECTION].count_documents({})

    return {
        "total_jobs": total,
        "active_workers": active,
        "by_status": {s["status"]: s["count"] for s in status_counts},
        "by_type": {t["job_type"]: t["count"] for t in type_counts},
    }
