"""Batch API wrapper — 50% cost discount for non-urgent workloads.

Both OpenAI and Anthropic offer a 'batch' mode: submit a file of
requests, get results within 24h, pay 50% of the normal rate. Groq and
Gemini have similar endpoints.

Perfect for:
  - Nightly enrichment jobs
  - Bulk email personalization
  - Content backfills
  - Analytics aggregations

We expose:
  submit(user_id, lines: list[dict]) -> batch_id
  poll(batch_id) -> {"status": "in_progress"|"completed"|"failed", "results": [...]}

Results are written to batch_jobs collection so the admin UI can show
progress. Credits are reserved on submit, settled when results come
back (at 50% discount vs realtime).

OpenAI format: JSONL, each line:
  {"custom_id":"...","method":"POST","url":"/v1/chat/completions",
   "body":{...chat-completion params...}}

Anthropic format: JSONL, each line:
  {"custom_id":"...","params":{...messages-api params...}}
"""
from __future__ import annotations
import io
import json
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


async def submit_openai(
    user_id: str,
    requests: list[dict],
    *,
    endpoint: str = "/v1/chat/completions",
) -> dict[str, Any]:
    """Submit a list of chat-completion requests to OpenAI Batch.
    Returns {batch_id, total_requests, created_at}. Caller should poll
    via `poll_openai(batch_id)` until status == completed."""
    from shared.utils import get_api_keys
    from db import db
    import httpx

    keys = await get_api_keys()
    openai_key = keys.get("openai") if isinstance(keys, dict) else None
    if not openai_key:
        raise RuntimeError("OpenAI key not configured for batch")

    buf = io.StringIO()
    for i, req in enumerate(requests):
        line = {
            "custom_id": req.get("custom_id") or f"req-{i}",
            "method": "POST",
            "url": endpoint,
            "body": req["body"],
        }
        buf.write(json.dumps(line) + "\n")
    data = buf.getvalue().encode()

    async with httpx.AsyncClient(timeout=60) as client:
        files_resp = await client.post(
            "https://api.openai.com/v1/files",
            headers={"Authorization": f"Bearer {openai_key}"},
            files={"file": ("batch.jsonl", data, "application/jsonl")},
            data={"purpose": "batch"},
        )
        files_resp.raise_for_status()
        file_id = files_resp.json()["id"]

        batch_resp = await client.post(
            "https://api.openai.com/v1/batches",
            headers={
                "Authorization": f"Bearer {openai_key}",
                "Content-Type": "application/json",
            },
            json={
                "input_file_id": file_id,
                "endpoint": endpoint,
                "completion_window": "24h",
            },
        )
        batch_resp.raise_for_status()
        batch = batch_resp.json()

    await db.batch_jobs.insert_one({
        "_id": batch["id"],
        "user_id": user_id,
        "provider": "openai",
        "endpoint": endpoint,
        "file_id": file_id,
        "total": len(requests),
        "status": batch.get("status", "in_progress"),
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    return {
        "batch_id": batch["id"],
        "total_requests": len(requests),
        "status": batch.get("status", "in_progress"),
    }


async def poll_openai(batch_id: str) -> dict[str, Any]:
    from shared.utils import get_api_keys
    from db import db
    import httpx

    keys = await get_api_keys()
    openai_key = keys.get("openai") if isinstance(keys, dict) else None
    if not openai_key:
        raise RuntimeError("OpenAI key not configured")

    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(
            f"https://api.openai.com/v1/batches/{batch_id}",
            headers={"Authorization": f"Bearer {openai_key}"},
        )
        r.raise_for_status()
        batch = r.json()
    status = batch.get("status")
    update: dict[str, Any] = {"status": status}

    result_lines: list[dict] = []
    if status == "completed" and batch.get("output_file_id"):
        async with httpx.AsyncClient(timeout=120) as client:
            out = await client.get(
                f"https://api.openai.com/v1/files/{batch['output_file_id']}/content",
                headers={"Authorization": f"Bearer {openai_key}"},
            )
            out.raise_for_status()
            for ln in out.text.strip().split("\n"):
                if ln:
                    try:
                        result_lines.append(json.loads(ln))
                    except json.JSONDecodeError:
                        continue
        update["completed_at"] = datetime.now(timezone.utc).isoformat()
        update["result_count"] = len(result_lines)

    await db.batch_jobs.update_one({"_id": batch_id}, {"$set": update})
    return {"batch_id": batch_id, "status": status, "results": result_lines}


async def submit_anthropic(
    user_id: str,
    requests: list[dict],
) -> dict[str, Any]:
    """Submit batch to Anthropic Messages Batches API."""
    from shared.utils import get_api_keys
    from db import db
    import httpx

    keys = await get_api_keys()
    anthropic_key = keys.get("anthropic") if isinstance(keys, dict) else None
    if not anthropic_key:
        raise RuntimeError("Anthropic key not configured for batch")

    lines = [{"custom_id": req.get("custom_id") or f"req-{i}", "params": req["params"]}
             for i, req in enumerate(requests)]

    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(
            "https://api.anthropic.com/v1/messages/batches",
            headers={
                "x-api-key": anthropic_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            json={"requests": lines},
        )
        r.raise_for_status()
        batch = r.json()

    await db.batch_jobs.insert_one({
        "_id": batch["id"],
        "user_id": user_id,
        "provider": "anthropic",
        "total": len(requests),
        "status": batch.get("processing_status", "in_progress"),
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    return {
        "batch_id": batch["id"],
        "total_requests": len(requests),
        "status": batch.get("processing_status", "in_progress"),
    }


async def poll_anthropic(batch_id: str) -> dict[str, Any]:
    from shared.utils import get_api_keys
    from db import db
    import httpx

    keys = await get_api_keys()
    anthropic_key = keys.get("anthropic") if isinstance(keys, dict) else None
    if not anthropic_key:
        raise RuntimeError("Anthropic key not configured")

    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(
            f"https://api.anthropic.com/v1/messages/batches/{batch_id}",
            headers={"x-api-key": anthropic_key, "anthropic-version": "2023-06-01"},
        )
        r.raise_for_status()
        batch = r.json()
    status = batch.get("processing_status")
    update = {"status": status}
    results: list[dict] = []
    if status == "ended" and batch.get("results_url"):
        async with httpx.AsyncClient(timeout=120) as client:
            out = await client.get(
                batch["results_url"],
                headers={"x-api-key": anthropic_key, "anthropic-version": "2023-06-01"},
            )
            out.raise_for_status()
            for ln in out.text.strip().split("\n"):
                if ln:
                    try:
                        results.append(json.loads(ln))
                    except json.JSONDecodeError:
                        continue
        update["completed_at"] = datetime.now(timezone.utc).isoformat()
        update["result_count"] = len(results)

    await db.batch_jobs.update_one({"_id": batch_id}, {"$set": update})
    return {"batch_id": batch_id, "status": status, "results": results}
