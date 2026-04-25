"""Workflow builder — "Zapier for AI" scaffold.

Data model: a workflow = a DAG of nodes. Each node is typed:
  - trigger: manual | scheduled | webhook | email_reply
  - action:  search_leads | enrich | draft_email | send_email |
             wait | generate_image | post_linkedin | webhook_out |
             if_condition

Edges connect one node's output to another's input. The scheduler
owns execution — it reads the DAG, walks it, and fires each node
through the same services agents already use.

This module exposes CRUD + a `run()` endpoint. Execution engine is
scaffolded — full DAG walker coming next iteration.

Shape of a saved workflow:
    {
      "workflow_id": "wf_abc",
      "name": "SaaS outbound + follow-up",
      "trigger": {"type": "manual"},
      "nodes": [
        {"id": "n1", "type": "action", "tool": "search_leads",
         "params": {...}, "next": ["n2"]},
        {"id": "n2", "type": "action", "tool": "draft_email",
         "params": {...}, "next": ["n3"]},
        {"id": "n3", "type": "action", "tool": "send_email",
         "params": {...}, "next": []}
      ]
    }
"""
from __future__ import annotations
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from auth import get_current_user
from models.schemas import User

router = APIRouter()


VALID_TOOLS = {
    "search_leads", "enrich_contact",
    "draft_email", "send_email", "send_cold_email", "run_campaign",
    "post_linkedin", "post_social", "schedule_post",
    "generate_image", "generate_video",
    "enhance_prompt",
    "webhook_out",
    "wait",          # wait N seconds/minutes/hours before next node
    "if_condition",  # binary branch
    "switch",        # N-way branch
    "ai_branch",     # agent-picked branch
    "agent_chat",    # invoke a specific MAARS agent by agent_id
    "integration_action",  # unified API/browser driver for any connected integration
    "evaluator",           # relevance-filter retrieved chunks before synthesis
    # Data + code (from workflow_tools.py)
    "http_request", "set", "filter", "loop", "merge", "sub_workflow",
    "code_js", "code_python", "sql_query", "mongo_query",
    "sort", "dedupe", "aggregate", "group_by", "summarize",
    "classify", "rag_query",
    "slack_send", "discord_send", "telegram_send",
    "google_sheets_append", "notion_create", "airtable_append",
    "file_read", "file_write", "s3_put", "s3_get",
    # Control + service integrations (from workflow_services.py)
    "respond_webhook", "wait_for_webhook", "approval",
    "github", "gitlab", "jira", "linear", "asana", "trello", "clickup", "monday",
    "stripe_op", "hubspot_op", "salesforce_op", "intercom_send",
    "zendesk_ticket", "freshdesk_ticket",
    "gmail_op", "notion_op",
    "mailchimp_subscribe", "typeform_list", "sendgrid_send",
    "clearbit_enrich", "dropcontact_enrich", "openweather_get",
    "google_drive_upload", "dropbox_upload", "box_upload",
    "calendly_list", "zoom_create_meeting",
    "shopify_op", "algolia_op", "typesense_op", "twilio_sms",
}

VALID_TRIGGER_TYPES = {"manual", "scheduled", "webhook", "email_reply"}


class Node(BaseModel):
    id: str
    type: str                  # trigger | action | condition
    tool: str | None = None
    params: dict = {}
    next: list[str] = []
    branch_yes: list[str] | None = None  # for if_condition
    branch_no: list[str] | None = None
    branches: dict[str, list[str]] | None = None   # for switch / ai_branch (label → target ids)
    on_failure: list[str] | None = None  # n8n "Error output" — route failure here


class WorkflowBody(BaseModel):
    name: str
    description: str | None = None
    trigger: dict
    nodes: list[Node]
    active: bool = False


@router.get("/workflows")
async def list_workflows(current_user: User = Depends(get_current_user)):
    from db import db
    docs = await db.workflows.find(
        {"user_id": current_user.user_id},
        {"_id": 0},
    ).sort("updated_at", -1).to_list(200)
    return {"object": "list", "data": docs}


@router.post("/workflows")
async def create_workflow(body: WorkflowBody, current_user: User = Depends(get_current_user)):
    _validate(body)
    from db import db
    now = datetime.now(timezone.utc).isoformat()
    doc = {
        "workflow_id": f"wf_{uuid.uuid4().hex[:12]}",
        "user_id": current_user.user_id,
        "name": body.name,
        "description": body.description,
        "trigger": body.trigger,
        "nodes": [n.model_dump() for n in body.nodes],
        "active": body.active,
        "created_at": now,
        "updated_at": now,
        "run_count": 0,
    }
    await db.workflows.insert_one({**doc, "_id": None})
    return doc


@router.put("/workflows/{workflow_id}")
async def update_workflow(
    workflow_id: str,
    body: WorkflowBody,
    snapshot_before: bool = True,
    current_user: User = Depends(get_current_user),
):
    _validate(body)
    from db import db
    from services.workflows import workflow_versioning as _vx
    # Auto-snapshot the about-to-be-overwritten state so we can roll back.
    if snapshot_before:
        try:
            await _vx.snapshot_version(workflow_id, current_user.user_id, note="auto-before-update")
        except Exception:
            pass
    res = await db.workflows.update_one(
        {"workflow_id": workflow_id, "user_id": current_user.user_id},
        {"$set": {
            "name": body.name,
            "description": body.description,
            "trigger": body.trigger,
            "nodes": [n.model_dump() for n in body.nodes],
            "active": body.active,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }},
    )
    if not res.matched_count:
        raise HTTPException(404, "workflow not found")
    return {"ok": True}


# ── Versioning endpoints ─────────────────────────────────────────────

@router.post("/workflows/{workflow_id}/versions")
async def publish_version(
    workflow_id: str,
    note: str = "",
    current_user: User = Depends(get_current_user),
):
    """Explicit 'publish' — snapshot the current draft as a version."""
    from services.workflows import workflow_versioning as _vx
    try:
        r = await _vx.snapshot_version(workflow_id, current_user.user_id, note=note)
    except KeyError:
        raise HTTPException(404, "workflow not found")
    return r


@router.get("/workflows/{workflow_id}/versions")
async def list_workflow_versions(
    workflow_id: str,
    current_user: User = Depends(get_current_user),
):
    from services.workflows import workflow_versioning as _vx
    rows = await _vx.list_versions(workflow_id, current_user.user_id)
    return {"object": "list", "data": rows, "count": len(rows)}


@router.get("/workflows/{workflow_id}/versions/{version}")
async def get_workflow_version(
    workflow_id: str,
    version: int,
    current_user: User = Depends(get_current_user),
):
    from services.workflows import workflow_versioning as _vx
    v = await _vx.get_version(workflow_id, version, current_user.user_id)
    if not v:
        raise HTTPException(404, "version not found")
    return v


@router.post("/workflows/{workflow_id}/versions/{version}/rollback")
async def rollback_workflow(
    workflow_id: str,
    version: int,
    current_user: User = Depends(get_current_user),
):
    from services.workflows import workflow_versioning as _vx
    try:
        return await _vx.rollback_to(workflow_id, version, current_user.user_id)
    except KeyError as exc:
        raise HTTPException(404, str(exc))


# ── Env variables ───────────────────────────────────────────────────

class _EnvBody(BaseModel):
    key: str
    value: Any
    secret: bool = False
    scope: str = "user"       # user | org | system
    scope_id: str | None = None


@router.get("/workflows/env")
async def list_env(
    org_id: str | None = None,
    current_user: User = Depends(get_current_user),
):
    from services.workflows import workflow_versioning as _vx
    return {"object": "list",
            "data": await _vx.env_list(user_id=current_user.user_id, org_id=org_id)}


@router.put("/workflows/env")
async def put_env(
    body: _EnvBody,
    current_user: User = Depends(get_current_user),
):
    from services.workflows import workflow_versioning as _vx
    scope = body.scope
    if scope == "user":
        scope_id = current_user.user_id
    elif scope == "org":
        scope_id = body.scope_id or ""
        if not scope_id:
            raise HTTPException(400, "scope_id required for org scope")
    else:  # system — admin gate
        scope_id = "global"
    return await _vx.env_put(scope, scope_id, body.key, body.value,
                             secret=body.secret, updated_by=current_user.user_id)


@router.delete("/workflows/env/{scope}/{key}")
async def delete_env(
    scope: str,
    key: str,
    scope_id: str | None = None,
    current_user: User = Depends(get_current_user),
):
    from services.workflows import workflow_versioning as _vx
    sid = current_user.user_id if scope == "user" else (scope_id or "global")
    ok = await _vx.env_delete(scope, sid, key)
    return {"ok": ok}


@router.delete("/workflows/{workflow_id}")
async def delete_workflow(workflow_id: str, current_user: User = Depends(get_current_user)):
    from db import db
    res = await db.workflows.delete_one({
        "workflow_id": workflow_id, "user_id": current_user.user_id,
    })
    return {"ok": bool(res.deleted_count)}


@router.post("/workflows/{workflow_id}/run")
async def run_workflow(
    workflow_id: str,
    overrides: dict = {},
    background: bool = True,
    current_user: User = Depends(get_current_user),
):
    """Kick off a workflow execution.

    background=True (default): insert a queued run, return immediately;
    scheduler picks it up within 30s and runs it. Use SSE
    `/workflows/runs/{run_id}/events` to watch progress.

    background=False: execute synchronously and return the final state.
    """
    import asyncio
    from db import db
    from services.workflows.workflow_executor import run as wf_run
    wf = await db.workflows.find_one(
        {"workflow_id": workflow_id, "user_id": current_user.user_id},
    )
    if not wf:
        raise HTTPException(404, "workflow not found")
    run_id = f"wfrun_{uuid.uuid4().hex[:12]}"
    await db.workflow_runs.insert_one({
        "run_id": run_id,
        "workflow_id": workflow_id,
        "user_id": current_user.user_id,
        "status": "queued",
        "overrides": overrides,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "_id": None,
    })
    await db.workflows.update_one(
        {"workflow_id": workflow_id},
        {"$inc": {"run_count": 1},
         "$set": {"last_run_at": datetime.now(timezone.utc).isoformat()}},
    )
    if not background:
        final = await wf_run(run_id, wf, overrides=overrides)
        return {"ok": True, "run_id": run_id, "status": final.get("status"), "final": final}
    # Background path: fire-and-forget — scheduler's next tick will also
    # pick it up, but starting now reduces first-event latency from ~30s
    # to immediate.
    async def _go():
        try:
            await wf_run(run_id, wf, overrides=overrides)
        except Exception as exc:
            import logging
            logging.getLogger(__name__).warning("wf run crashed: %s", exc)
    asyncio.create_task(_go())
    return {"ok": True, "run_id": run_id, "status": "running"}


@router.get("/workflows/{workflow_id}/runs")
async def list_runs(
    workflow_id: str,
    limit: int = 50,
    status: str | None = None,
    current_user: User = Depends(get_current_user),
):
    """Execution history for a workflow — paginated, filterable by status."""
    from db import db
    q: dict = {"workflow_id": workflow_id, "user_id": current_user.user_id}
    if status:
        q["status"] = status
    rows = await db.workflow_runs.find(q, {"_id": 0, "state": 0}).sort("started_at", -1).limit(min(limit, 200)).to_list(min(limit, 200))
    return {"object": "list", "data": rows, "count": len(rows)}


@router.get("/workflows/runs/{run_id}")
async def get_run(run_id: str, current_user: User = Depends(get_current_user)):
    from db import db
    row = await db.workflow_runs.find_one(
        {"run_id": run_id, "user_id": current_user.user_id},
        {"_id": 0},
    )
    if not row:
        raise HTTPException(404, "run not found")
    events = await db.workflow_run_events.find(
        {"run_id": run_id}, {"_id": 0},
    ).sort("ts", 1).to_list(500)
    return {"run": row, "events": events}


class _TestNodeBody(BaseModel):
    """Shape for POST /workflows/{id}/nodes/{node_id}/test."""
    input: dict = {}
    overrides_params: dict | None = None


@router.post("/workflows/{workflow_id}/nodes/{node_id}/test")
async def test_single_node(
    workflow_id: str,
    node_id: str,
    body: _TestNodeBody,
    current_user: User = Depends(get_current_user),
):
    """Execute ONE node with the supplied input — no wallet reserve via
    the workflow path, no writes to workflow_runs. Useful for design-time
    debugging: pick a node in the canvas, paste a sample input, see the
    output. Expressions are still resolved against a minimal ctx."""
    from db import db
    from services.workflows import workflow_executor as wx, expressions as _ex
    wf = await db.workflows.find_one(
        {"workflow_id": workflow_id, "user_id": current_user.user_id},
    )
    if not wf:
        raise HTTPException(404, "workflow not found")
    node = next((n for n in (wf.get("nodes") or []) if n.get("id") == node_id), None)
    if not node:
        raise HTTPException(404, "node not found")

    # Build a throwaway ctx: state is just {node_id: {input}} so
    # `{{prev.foo}}` or `{{<node_id>.foo}}` references resolve.
    raw_params = dict(node.get("params") or {})
    if body.overrides_params:
        raw_params.update(body.overrides_params)
    test_node = {**node, "params": raw_params}

    ctx = _ex.build_context(
        workflow=wf, run_id="test-" + node_id,
        state={"prev": body.input or {}}, prev_output=body.input or {},
    )
    ok, output = await wx._fire_one_node(
        "test-" + node_id, current_user.user_id, test_node, body.input or {}, ctx,
    )
    return {"ok": ok, "output": output, "node_id": node_id, "tool": node.get("tool")}


class _PinBody(BaseModel):
    output: dict


@router.put("/workflows/{workflow_id}/nodes/{node_id}/pin")
async def pin_node_output(
    workflow_id: str,
    node_id: str,
    body: _PinBody,
    current_user: User = Depends(get_current_user),
):
    """Pin a node's output for design-time testing. When the workflow
    runs in 'design' mode, pinned outputs are used instead of firing the
    tool. Useful for iterating on downstream nodes without re-running
    expensive upstream ones."""
    from db import db
    res = await db.workflows.update_one(
        {"workflow_id": workflow_id, "user_id": current_user.user_id},
        {"$set": {f"pinned_outputs.{node_id}": body.output}},
    )
    if not res.matched_count:
        raise HTTPException(404, "workflow not found")
    return {"ok": True, "node_id": node_id}


@router.delete("/workflows/{workflow_id}/nodes/{node_id}/pin")
async def unpin_node_output(
    workflow_id: str,
    node_id: str,
    current_user: User = Depends(get_current_user),
):
    from db import db
    await db.workflows.update_one(
        {"workflow_id": workflow_id, "user_id": current_user.user_id},
        {"$unset": {f"pinned_outputs.{node_id}": ""}},
    )
    return {"ok": True, "node_id": node_id}


@router.get("/workflows/tools/catalog")
async def tools_catalog(_: User = Depends(get_current_user)):
    """List every tool the executor can fire — used by the canvas node
    palette so it stays in sync with the backend."""
    from services.workflows.workflow_executor import TOOL_REGISTRY
    return {
        "object": "list",
        "count": len(TOOL_REGISTRY),
        "tools": sorted(TOOL_REGISTRY.keys()),
    }


@router.get("/workflows/runs/{run_id}/events")
async def stream_run_events(
    run_id: str,
    current_user: User = Depends(get_current_user),
):
    """SSE stream of executor events for live progress in the UI."""
    import asyncio
    import json as _json
    from fastapi.responses import StreamingResponse
    from services.workflows import workflow_executor as wx
    from db import db
    row = await db.workflow_runs.find_one(
        {"run_id": run_id, "user_id": current_user.user_id},
        {"_id": 0, "status": 1},
    )
    if not row:
        raise HTTPException(404, "run not found")

    q = wx.subscribe(run_id)

    async def _gen():
        try:
            while True:
                try:
                    ev = await asyncio.wait_for(q.get(), timeout=30)
                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"
                    continue
                yield f"data: {_json.dumps(ev)}\n\n"
                if ev.get("event") == "run_end":
                    break
        finally:
            wx.unsubscribe(run_id, q)

    return StreamingResponse(_gen(), media_type="text/event-stream", headers={
        "Cache-Control": "no-cache", "X-Accel-Buffering": "no",
    })


def _validate(body: WorkflowBody) -> None:
    if body.trigger.get("type") not in VALID_TRIGGER_TYPES:
        raise HTTPException(400, f"trigger.type must be one of {VALID_TRIGGER_TYPES}")
    ids = [n.id for n in body.nodes]
    if len(ids) != len(set(ids)):
        raise HTTPException(400, "duplicate node ids")
    for n in body.nodes:
        if n.type == "action" and n.tool not in VALID_TOOLS:
            raise HTTPException(400, f"unknown tool: {n.tool}")
        branch_targets: list[str] = list(n.next) + list(n.branch_yes or []) + list(n.branch_no or [])
        for _label, targets in (n.branches or {}).items():
            branch_targets.extend(targets or [])
        for target in branch_targets:
            if target and target not in ids:
                raise HTTPException(400, f"node {n.id} references unknown node {target}")


# ── AI-native additions (NL→workflow, chat→workflow, diagnose, autocomplete, replay) ──

class _GenerateBody(BaseModel):
    prompt: str
    save: bool = False           # if True, persist the draft as active=False immediately


@router.post("/workflows/generate")
async def workflow_generate(body: _GenerateBody, current_user: User = Depends(get_current_user)):
    """Build a draft workflow from a natural-language description."""
    from services.workflows import workflow_generator
    try:
        # Pin the generator to Commander Orion so his system_prompt,
        # golden examples, and per-agent training apply — the button
        # on the canvas is literally "Commander Orion", so attribution
        # should match.
        draft = await workflow_generator.from_description(
            body.prompt, current_user.user_id,
            agent_id="agent_commander",
        )
    except ValueError as exc:
        raise HTTPException(400, f"generation_failed: {exc}")
    if body.save:
        from db import db
        await db.workflows.insert_one({**draft, "updated_at": draft.get("created_at"),
                                       "run_count": 0, "_id": None})
    return draft


class _FromChatBody(BaseModel):
    chat_id: str
    save: bool = False


@router.post("/workflows/from-chat")
async def workflow_from_chat(body: _FromChatBody, current_user: User = Depends(get_current_user)):
    """Generate a workflow draft from a recent chat session."""
    from services.workflows import workflow_generator
    try:
        draft = await workflow_generator.from_chat(body.chat_id, current_user.user_id)
    except ValueError as exc:
        raise HTTPException(400, f"generation_failed: {exc}")
    if body.save:
        from db import db
        await db.workflows.insert_one({**draft, "updated_at": draft.get("created_at"),
                                       "run_count": 0, "_id": None})
    return draft


@router.get("/workflows/{workflow_id}/runs/{run_id}/diagnose")
async def workflow_diagnose(
    workflow_id: str, run_id: str,
    current_user: User = Depends(get_current_user),
):
    from services.workflows import workflow_diagnose as _wd
    try:
        return await _wd.diagnose_run(run_id, current_user.user_id)
    except ValueError as exc:
        raise HTTPException(404, str(exc))


class _ReplayBody(BaseModel):
    resume_from_node_id: str | None = None
    override_outputs: dict | None = None


@router.post("/workflows/runs/{run_id}/replay")
async def workflow_replay(
    run_id: str, body: _ReplayBody,
    current_user: User = Depends(get_current_user),
):
    """Re-run from the original run's state. Optional resume point +
    overrides let operator apply a diagnose-suggested fix and see the
    workflow proceed past the failure without editing the saved spec."""
    from services.workflows import workflow_executor as wx
    try:
        new_run_id = await wx.replay_run(
            run_id,
            resume_from_node_id=body.resume_from_node_id,
            override_outputs=body.override_outputs,
        )
    except ValueError as exc:
        raise HTTPException(404, str(exc))
    return {"ok": True, "run_id": new_run_id,
            "replaying": run_id, "resume_from": body.resume_from_node_id}


# ── Commander Orion — orchestrator entry point ──────────────────────
# One endpoint that gives Commander Orion full authority to plan, save,
# activate, and trigger a workflow run from a single natural-language
# goal. UI surfaces this as an "Orchestrate" button alongside the
# "Commander Orion" Build modal — Build drafts on canvas for review,
# Orchestrate ships the whole thing end-to-end.

class _OrchestrateBody(BaseModel):
    goal: str
    auto_run: bool = True           # save + activate + run; False = draft only
    name_override: str | None = None  # optional human-set name


@router.post("/commander/orchestrate")
async def commander_orchestrate(
    body: _OrchestrateBody,
    current_user: User = Depends(get_current_user),
):
    """Commander Orion takes the goal, plans the DAG, and (by default)
    runs it. Returns the workflow_id + run_id so the caller can follow
    execution via the existing SSE stream."""
    from services.workflows import workflow_generator, workflow_executor as wx
    from db import db
    if not body.goal.strip():
        raise HTTPException(400, "goal_required")
    try:
        draft = await workflow_generator.from_description(
            body.goal, current_user.user_id,
            agent_id="agent_commander",
        )
    except ValueError as exc:
        raise HTTPException(400, f"orchestrate_generation_failed: {exc}")
    if body.name_override:
        draft["name"] = body.name_override
    if not (draft.get("nodes") or []):
        raise HTTPException(
            502,
            "Commander Orion returned an empty plan — retry or rephrase the goal.",
        )
    # Persist the draft so the run has a real workflow_id to reference
    now = datetime.now(timezone.utc).isoformat()
    draft["active"] = bool(body.auto_run)
    draft["updated_at"] = now
    draft["run_count"] = 0
    draft["orchestrated_by"] = "agent_commander"
    await db.workflows.insert_one({**draft, "_id": None})
    response = {
        "ok": True,
        "workflow_id": draft["workflow_id"],
        "name": draft["name"],
        "nodes": len(draft.get("nodes") or []),
        "validation_warnings": draft.get("validation_warnings") or [],
        "run_id": None,
    }
    if body.auto_run:
        # Kick a run immediately — scheduler picks it up on the next tick.
        run_id = await wx._enqueue_run(
            draft, trigger_meta={"source": "commander_orchestrate"}
        )
        response["run_id"] = run_id
        response["status_stream"] = f"/api/workflows/{draft['workflow_id']}/runs/{run_id}/stream"
    return response


@router.get("/workflow/tools")
async def workflow_tools_catalog(current_user: User = Depends(get_current_user)):
    """Live catalog of every tool the workflow executor knows about.

    Pulls from the runtime TOOL_REGISTRY (executor + workflow_tools +
    workflow_services) so the frontend can render the palette dynamically
    without hardcoding node lists. Metadata (category + one-liner + params)
    comes from workflow_generator._tool_catalog() — the same catalog the
    AI Build generator uses, so what the user sees in the palette and
    what the generator can suggest are the same set."""
    from services.workflows import workflow_executor as wx, workflow_generator
    registry_names = sorted(wx.TOOL_REGISTRY.keys())
    meta_by_name = {t["tool"]: t for t in workflow_generator._tool_catalog()}
    out = []
    for name in registry_names:
        m = meta_by_name.get(name, {})
        out.append({
            "tool":     name,
            "category": m.get("category", "other"),
            "one_line": m.get("one_line", ""),
            "params":   m.get("params", ""),
            "documented_in_generator": name in meta_by_name,
        })
    categories = sorted({t["category"] for t in out})
    return {
        "object":     "workflow_tools",
        "count":      len(out),
        "categories": categories,
        "tools":      out,
    }


@router.get("/workflows/{workflow_id}/autocomplete")
async def workflow_autocomplete(
    workflow_id: str, node_id: str, prefix: str = "",
    current_user: User = Depends(get_current_user),
):
    from services.workflows import workflow_autocomplete as _ac
    return {
        "object": "autocomplete_suggestions",
        "suggestions": await _ac.suggest(
            workflow_id, node_id, prefix, user_id=current_user.user_id,
        ),
    }
