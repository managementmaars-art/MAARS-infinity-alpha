"""Integration sync — BrowserAgent logs into an integration, extracts
data, writes it back to MAARS.

The chain:
  1. Caller: POST /integrations/{id}/sync → we kick off a job.
  2. BrowserAgent opens the integration's URL + user's stored session
     cookie (from the vault's "browser_session" kind).
  3. Agent navigates to the extraction target (e.g. Salesforce "Leads"
     list, HubSpot "Contacts", a bank account's transactions).
  4. Agent vision+DOM extracts structured rows via a prompt template.
  5. We upsert the rows into the right MAARS collection
     (`external_leads`, `external_contacts`, `external_transactions`,
     etc.) tagged with source=integration_id.
  6. Job status written to `integration_sync_jobs` — UI polls.

We don't own the agent's decision-making — that lives in
services.browser_agent. This module composes: agent goal + extraction
template + storage target.

Three preset extractors (easy to add more):
  "leads"       → list rows with (name, email, company, title)
  "contacts"    → (name, email, phone, last_contact_at)
  "transactions"→ (date, amount, description)
"""
from __future__ import annotations
import json
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


_EXTRACTORS: dict[str, dict[str, Any]] = {
    "leads": {
        "collection": "external_leads",
        "goal_template": (
            "Navigate to the leads list on the current page. For each visible "
            "lead row, capture: full name, email, company name, job title. "
            "Scroll until at least {limit} rows or until no new rows appear. "
            "Return as JSON: [{\"name\":..,\"email\":..,\"company\":..,\"title\":..}]"
        ),
        "schema": ["name", "email", "company", "title"],
    },
    "contacts": {
        "collection": "external_contacts",
        "goal_template": (
            "Navigate to the contacts list. For each contact: name, email, "
            "phone, last_contact_at. Scroll until {limit} rows. Return JSON."
        ),
        "schema": ["name", "email", "phone", "last_contact_at"],
    },
    "transactions": {
        "collection": "external_transactions",
        "goal_template": (
            "Navigate to the transactions list. Capture each row's date, "
            "amount (with sign), description. Scroll until {limit} rows. "
            "Return JSON."
        ),
        "schema": ["date", "amount", "description"],
    },
}


async def start_sync(
    *,
    user_id: str,
    integration_id: str,
    extractor: str,
    start_url: str,
    limit: int = 200,
    session_id: str | None = None,
) -> dict[str, Any]:
    """Kick off a sync job. Returns a job_id; result lands in
    `integration_sync_jobs` asynchronously."""
    if extractor not in _EXTRACTORS:
        return {"ok": False, "error": f"unknown extractor '{extractor}'"}

    from db import db
    job_id = f"sync_{uuid.uuid4().hex[:12]}"
    cfg = _EXTRACTORS[extractor]
    goal = cfg["goal_template"].format(limit=limit)

    await db.integration_sync_jobs.insert_one({
        "job_id": job_id,
        "user_id": user_id,
        "integration_id": integration_id,
        "extractor": extractor,
        "start_url": start_url,
        "limit": limit,
        "status": "queued",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "_id": None,
    })

    # Fire the agent as a background task.
    import asyncio
    async def _go():
        try:
            await _run_sync(job_id, user_id, integration_id, extractor, start_url, goal, session_id, limit)
        except Exception as exc:
            logger.warning("integration_sync %s crashed: %s", job_id, exc)
            try:
                from db import db as _d
                await _d.integration_sync_jobs.update_one(
                    {"job_id": job_id}, {"$set": {"status": "failed", "error": str(exc)[:500]}},
                )
            except Exception:
                pass
    asyncio.create_task(_go())
    return {"ok": True, "job_id": job_id, "status": "running"}


async def _run_sync(
    job_id: str, user_id: str, integration_id: str, extractor: str,
    start_url: str, goal: str, session_id: str | None, limit: int,
) -> None:
    from db import db
    cfg = _EXTRACTORS[extractor]
    collection_name = cfg["collection"]

    try:
        from services.browser_agent import agent_run_goal  # type: ignore
    except Exception as exc:
        await db.integration_sync_jobs.update_one(
            {"job_id": job_id},
            {"$set": {"status": "failed", "error": f"browser_agent unavailable: {exc}"}},
        )
        return

    # Navigate + extract via the autonomous browser agent.
    events: list[dict[str, Any]] = []
    extracted_text: str = ""
    try:
        # browser_agent.agent_run_goal is an async generator of events.
        async for event in agent_run_goal(
            user_id=user_id,
            goal=f"Open {start_url}. Then: {goal}",
            max_steps=int(12 + limit / 50),
            session_id=session_id,
        ):
            events.append(event)
            if event.get("kind") == "final" and event.get("message"):
                extracted_text = event["message"]
    except Exception as exc:
        await db.integration_sync_jobs.update_one(
            {"job_id": job_id},
            {"$set": {"status": "failed", "error": f"agent: {exc}", "events": events[-20:]}},
        )
        return

    # Parse the agent's final output into structured rows.
    rows = _parse_rows(extracted_text, cfg["schema"])
    if not rows:
        await db.integration_sync_jobs.update_one(
            {"job_id": job_id},
            {"$set": {"status": "empty", "rows_found": 0, "events": events[-20:]}},
        )
        return

    # Upsert tagged rows.
    stamp = datetime.now(timezone.utc).isoformat()
    inserted, updated = 0, 0
    for r in rows:
        row = {
            **{k: r.get(k) for k in cfg["schema"]},
            "user_id": user_id,
            "integration_id": integration_id,
            "source": "integration_sync",
            "synced_at": stamp,
        }
        # Natural key: (user_id, integration_id, email) for leads/contacts,
        # fall through to (row signature) otherwise.
        key = {"user_id": user_id, "integration_id": integration_id}
        if r.get("email"):
            key["email"] = r["email"]
        else:
            key["_natural"] = json.dumps(r, sort_keys=True, default=str)[:240]
        res = await db[collection_name].update_one(key, {"$set": row}, upsert=True)
        if getattr(res, "upserted_id", None):
            inserted += 1
        else:
            updated += 1

    await db.integration_sync_jobs.update_one(
        {"job_id": job_id},
        {"$set": {
            "status": "completed",
            "rows_found": len(rows),
            "rows_inserted": inserted,
            "rows_updated": updated,
            "finished_at": datetime.now(timezone.utc).isoformat(),
        }},
    )


def _parse_rows(text: str, schema: list[str]) -> list[dict[str, Any]]:
    """Extract a JSON array from the agent's freeform response.
    Tolerates markdown code fences + trailing commentary."""
    if not text:
        return []
    import re
    # Strip code fences.
    m = re.search(r"```(?:json)?\s*(\[.*?\])\s*```", text, re.DOTALL)
    if m:
        payload = m.group(1)
    else:
        # Find the first top-level [...] array.
        start = text.find("[")
        end = text.rfind("]")
        if start < 0 or end <= start:
            return []
        payload = text[start:end + 1]
    try:
        raw = json.loads(payload)
    except json.JSONDecodeError:
        return []
    if not isinstance(raw, list):
        return []
    out = []
    for r in raw:
        if isinstance(r, dict):
            out.append({k: r.get(k) for k in schema})
    return out


async def job_status(job_id: str) -> dict[str, Any] | None:
    from db import db
    return await db.integration_sync_jobs.find_one({"job_id": job_id}, {"_id": 0})
