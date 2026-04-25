"""Workflow versioning — immutable snapshots + rollback + env variables.

Versioning model:
  - Every `PUT /workflows/{id}` or explicit "publish" creates a snapshot
    into `workflow_versions` (append-only). Version number increments
    per workflow.
  - The workflow doc itself always holds the CURRENT draft. Runs use
    the draft by default OR a pinned version via `runs_from_version`.
  - `rollback(id, version)` copies a snapshot back into the draft.

Environment variables:
  - `workflow_env` collection stores per-user and per-org key-value
    pairs.  `{{$env.KEY}}` already resolves against os.environ for
    allow-listed names; we extend it via a lookup in workflow_env at
    resolve time.
  - UI writes to `workflow_env` via /env endpoints below.
"""
from __future__ import annotations
import logging
import os
import time
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


# ── Versioning ───────────────────────────────────────────────────────

async def snapshot_version(workflow_id: str, user_id: str, note: str = "") -> dict[str, Any]:
    """Take a point-in-time snapshot of the current workflow draft and
    write it as an immutable version. Returns {version, created_at}."""
    from db import db
    wf = await db.workflows.find_one({"workflow_id": workflow_id, "user_id": user_id})
    if not wf:
        raise KeyError(f"workflow {workflow_id} not found")
    # next version number
    last = await db.workflow_versions.find_one(
        {"workflow_id": workflow_id},
        sort=[("version", -1)],
        projection={"version": 1, "_id": 0},
    )
    next_v = (last or {}).get("version", 0) + 1
    doc = {
        "workflow_id": workflow_id,
        "user_id":     user_id,
        "version":     next_v,
        "created_at":  datetime.now(timezone.utc).isoformat(),
        "note":        note,
        "snapshot":    {
            "name":         wf.get("name"),
            "description":  wf.get("description"),
            "trigger":      wf.get("trigger"),
            "nodes":        wf.get("nodes"),
            "on_error_workflow_id": wf.get("on_error_workflow_id"),
            "max_parallel": wf.get("max_parallel"),
        },
    }
    await db.workflow_versions.insert_one(doc)
    await db.workflows.update_one(
        {"workflow_id": workflow_id},
        {"$set": {"current_version": next_v, "last_versioned_at": doc["created_at"]}},
    )
    return {"version": next_v, "created_at": doc["created_at"], "note": note}


async def list_versions(workflow_id: str, user_id: str, limit: int = 50) -> list[dict]:
    from db import db
    rows = await db.workflow_versions.find(
        {"workflow_id": workflow_id, "user_id": user_id},
        {"_id": 0, "snapshot.nodes": 0},    # exclude big nodes blob
    ).sort("version", -1).limit(limit).to_list(limit)
    return rows


async def get_version(workflow_id: str, version: int, user_id: str) -> dict | None:
    from db import db
    return await db.workflow_versions.find_one(
        {"workflow_id": workflow_id, "version": version, "user_id": user_id},
        {"_id": 0},
    )


async def rollback_to(workflow_id: str, version: int, user_id: str) -> dict:
    """Copy a snapshot back into the workflow draft. Also takes a new
    snapshot of the about-to-be-overwritten state so rollbacks are
    themselves reversible."""
    from db import db
    # snapshot current state first
    try:
        await snapshot_version(workflow_id, user_id, note=f"auto-before-rollback-to-v{version}")
    except Exception:
        pass

    v = await get_version(workflow_id, version, user_id)
    if not v:
        raise KeyError(f"version {version} not found")
    snap = v.get("snapshot") or {}
    await db.workflows.update_one(
        {"workflow_id": workflow_id, "user_id": user_id},
        {"$set": {
            "name":        snap.get("name"),
            "description": snap.get("description"),
            "trigger":     snap.get("trigger"),
            "nodes":       snap.get("nodes"),
            "on_error_workflow_id": snap.get("on_error_workflow_id"),
            "max_parallel": snap.get("max_parallel"),
            "rolled_back_from_version": version,
            "updated_at":  datetime.now(timezone.utc).isoformat(),
        }},
    )
    return {"ok": True, "workflow_id": workflow_id, "rolled_back_to": version}


# ── Env variables ────────────────────────────────────────────────────

async def env_put(scope: str, scope_id: str, key: str, value: Any,
                  *, secret: bool = False, updated_by: str = "") -> dict:
    """scope = 'user' | 'org' | 'system'."""
    from db import db
    doc = {
        "scope": scope, "scope_id": scope_id, "key": key,
        "value": value, "secret": bool(secret),
        "updated_at": time.time(),
        "updated_by": updated_by,
    }
    await db.workflow_env.update_one(
        {"scope": scope, "scope_id": scope_id, "key": key},
        {"$set": doc}, upsert=True,
    )
    return {"ok": True, **{k: v for k, v in doc.items() if k != "value" or not secret}}


async def env_get(key: str, *, user_id: str | None = None, org_id: str | None = None) -> Any:
    """Resolution order: user → org → system. Returns the raw value.
    Expressions.{{$env.KEY}} can either use os.environ (already
    working) or this function via a helper."""
    from db import db
    for (scope, sid) in [("user", user_id), ("org", org_id), ("system", "global")]:
        if not sid: continue
        doc = await db.workflow_env.find_one({"scope": scope, "scope_id": sid, "key": key})
        if doc: return doc.get("value")
    return None


async def env_list(*, user_id: str | None = None, org_id: str | None = None) -> list[dict]:
    from db import db
    scopes = [("system", "global")]
    if org_id:  scopes.append(("org", org_id))
    if user_id: scopes.append(("user", user_id))
    out: list[dict] = []
    for scope, sid in scopes:
        async for doc in db.workflow_env.find({"scope": scope, "scope_id": sid}):
            out.append({
                "scope": scope, "scope_id": sid,
                "key":   doc["key"],
                "value": "***" if doc.get("secret") else doc.get("value"),
                "secret": bool(doc.get("secret")),
                "updated_at": doc.get("updated_at"),
            })
    return out


async def env_delete(scope: str, scope_id: str, key: str) -> bool:
    from db import db
    r = await db.workflow_env.delete_one({"scope": scope, "scope_id": scope_id, "key": key})
    return bool(r.deleted_count)
