"""Admin + client endpoints for the unified integration driver.

Surfaces the per-provider driver catalog, per-user status, connect flow
(for browser mode = open a live session for the operator to sign in),
and a direct `act()` playground so an agent or the operator can run a
provider action without writing a workflow.
"""
from __future__ import annotations
import logging
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from auth import get_current_user
from models.schemas import User

logger = logging.getLogger(__name__)
router = APIRouter()


# ── Catalog: what drivers exist + each provider's action surfaces ───

@router.get("/integrations/drivers")
async def integration_drivers_catalog(_: User = Depends(get_current_user)):
    from services import integration_driver
    return {"object": "integration_drivers", "drivers": integration_driver.list_drivers()}


# ── Per-user status for a single provider ──────────────────────────

@router.get("/integrations/{provider}/status")
async def integration_status(provider: str, current_user: User = Depends(get_current_user)):
    from services import integration_driver
    return await integration_driver.status(provider, current_user.user_id)


# ── Status batch: every driver + per-user readiness in one call ────

@router.get("/integrations/status-all")
async def integration_status_all(current_user: User = Depends(get_current_user)):
    from services import integration_driver
    drivers = integration_driver.list_drivers()
    out = []
    for d in drivers:
        s = await integration_driver.status(d["provider"], current_user.user_id)
        out.append(s)
    ready_modes_total = sum(1 for o in out if o.get("ready_modes"))
    return {
        "object": "integration_status_all",
        "total_drivers": len(out),
        "ready_providers": ready_modes_total,
        "providers": out,
    }


# ── Generic act playground — run any provider/action directly ──────

class _ActBody(BaseModel):
    provider: str
    action: str
    params: dict = {}
    prefer_mode: Optional[str] = None


@router.post("/integrations/act")
async def integration_act(body: _ActBody, current_user: User = Depends(get_current_user)):
    from services import integration_driver
    return await integration_driver.act(
        provider=body.provider, action=body.action,
        params=body.params, user_id=current_user.user_id,
        prefer_mode=body.prefer_mode,
    )


# ── Browser-mode connect: open a live session at the provider's login URL ──

class _ConnectBody(BaseModel):
    provider: str


@router.post("/integrations/{provider}/connect-browser")
async def integration_connect_browser(
    provider: str, current_user: User = Depends(get_current_user),
):
    """Open the user's browser session at the provider's login page.
    They sign in once; Playwright persists the cookies to the session
    file. Subsequent `act()` calls in browser mode reuse the login."""
    from services import integration_driver
    d = integration_driver._DRIVERS.get(provider)
    if not d:
        raise HTTPException(404, f"unknown_provider: {provider}")
    if not d.login_url:
        raise HTTPException(400, f"{provider} has no login_url registered")
    from services.browser_service import get_browser_pool
    pool = get_browser_pool()
    session = await pool.open(
        user_id=current_user.user_id,
        agent_id="integration_connect",
        start_url=d.login_url,
    )
    # Hand control to the user so they can type credentials + 2FA
    session.take_control("user")
    return {
        "ok": True,
        "provider": provider,
        "session_id": session.session_id,
        "login_url": d.login_url,
        "note": "Browser session opened at login URL. Sign in; cookies persist for future acts.",
    }


# ── Disconnect: drop API credential + (optionally) browser session ─

class _DisconnectBody(BaseModel):
    wipe_browser_session: bool = False


@router.post("/integrations/{provider}/disconnect")
async def integration_disconnect(
    provider: str, body: _DisconnectBody = None,
    current_user: User = Depends(get_current_user),
):
    from services import credential_vault
    body = body or _DisconnectBody()
    removed = []
    try:
        if await credential_vault.delete(provider, user_id=current_user.user_id):
            removed.append("api_credential")
    except Exception as exc:
        logger.info("disconnect credential delete failed: %s", exc)
    if body.wipe_browser_session:
        # Clear persisted cookies by truncating storage_state file
        from pathlib import Path
        storage = Path("browser_data/storage_states") / f"{current_user.user_id}.json"
        if storage.exists():
            try:
                storage.write_text("{}", encoding="utf-8")
                removed.append("browser_session")
            except Exception:
                pass
    return {"ok": True, "provider": provider, "removed": removed}


# ── Per-provider dashboard / feed / grants ─────────────────────────

@router.get("/integrations/{provider}/dashboard")
async def integration_dashboard(
    provider: str, current_user: User = Depends(get_current_user),
):
    """Single-call data for the /apps/{provider} command-center page."""
    from services import integration_dashboard as dash
    out = await dash.dashboard(provider, current_user.user_id)
    if not out.get("ok") and out.get("error", "").startswith("unknown_provider"):
        raise HTTPException(404, out["error"])
    return out


@router.get("/integrations/{provider}/feed")
async def integration_feed(
    provider: str, limit: int = 50, unseen_only: bool = False,
    current_user: User = Depends(get_current_user),
):
    from services import integration_activity
    items = await integration_activity.get_feed(
        provider, current_user.user_id, limit=limit, unseen_only=unseen_only,
    )
    return {"object": "integration_feed", "provider": provider,
            "count": len(items), "items": items}


@router.post("/integrations/{provider}/poll")
async def integration_poll_now(
    provider: str, current_user: User = Depends(get_current_user),
):
    """On-demand poll for this provider (the UI refresh button)."""
    from services import integration_activity
    return await integration_activity.poll_provider(provider, current_user.user_id)


class _MarkSeenBody(BaseModel):
    external_ids: list[str]


@router.post("/integrations/{provider}/mark-seen")
async def integration_mark_seen(
    provider: str, body: _MarkSeenBody,
    current_user: User = Depends(get_current_user),
):
    from services import integration_activity
    modified = await integration_activity.mark_seen(
        provider, current_user.user_id, body.external_ids,
    )
    return {"ok": True, "modified": modified}


@router.get("/integrations/{provider}/agent-grants")
async def integration_agent_grants(
    provider: str, current_user: User = Depends(get_current_user),
):
    """List every agent with authority on this provider."""
    from db import db
    grants = await db.integration_authority.find(
        {"user_id": current_user.user_id, "providers": provider},
        {"_id": 0},
    ).to_list(length=100)
    enriched: list[dict[str, Any]] = []
    for g in grants:
        agent = await db.agents.find_one(
            {"agent_id": g.get("agent_id")},
            {"_id": 0, "agent_id": 1, "name": 1, "role": 1, "avatar": 1},
        )
        enriched.append({**g, "agent": agent})
    return {"object": "integration_agent_grants", "provider": provider,
            "count": len(enriched), "grants": enriched}


# ── Recent action audit log ────────────────────────────────────────

@router.get("/integrations/audit")
async def integration_audit(
    limit: int = 50,
    provider: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    from db import db
    q: dict[str, Any] = {"user_id": current_user.user_id}
    if provider:
        q["provider"] = provider
    cursor = db.integration_action_log.find(q, {"_id": 0}).sort("at", -1).limit(
        max(1, min(int(limit), 500))
    )
    return {"object": "integration_audit", "items": await cursor.to_list(length=limit)}


# ── Authority grant: which integrations Commander (or any agent) can act on ──

class _GrantBody(BaseModel):
    agent_id: str = "agent_commander"
    providers: list[str]                       # e.g. ["linkedin","x","instagram"]
    actions: Optional[list[str]] = None        # None = all actions; else subset
    expires_at: Optional[float] = None         # epoch; None = no expiry


@router.get("/integrations/authority/{agent_id}")
async def integration_authority_list(
    agent_id: str, current_user: User = Depends(get_current_user),
):
    from db import db
    doc = await db.integration_authority.find_one(
        {"user_id": current_user.user_id, "agent_id": agent_id}, {"_id": 0},
    )
    return doc or {
        "user_id":   current_user.user_id, "agent_id": agent_id,
        "providers": [], "actions": None, "expires_at": None,
    }


@router.put("/integrations/authority")
async def integration_authority_grant(
    body: _GrantBody, current_user: User = Depends(get_current_user),
):
    """Operator grants Commander (default) authority to act on a set of
    integrations. When the workflow executor runs an integration_action
    node, it checks this grant. No grant → workflow fails with an
    authority_denied error the operator can resolve from the UI."""
    from db import db
    from datetime import datetime, timezone
    doc = {
        "user_id":    current_user.user_id,
        "agent_id":   body.agent_id,
        "providers":  sorted(set(body.providers or [])),
        "actions":    body.actions,
        "expires_at": body.expires_at,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.integration_authority.update_one(
        {"user_id": current_user.user_id, "agent_id": body.agent_id},
        {"$set": doc},
        upsert=True,
    )
    return {"ok": True, **doc}


@router.delete("/integrations/authority/{agent_id}")
async def integration_authority_revoke(
    agent_id: str, current_user: User = Depends(get_current_user),
):
    from db import db
    res = await db.integration_authority.delete_one(
        {"user_id": current_user.user_id, "agent_id": agent_id},
    )
    return {"ok": True, "deleted": int(getattr(res, "deleted_count", 0) or 0)}


# ── MCP token management ────────────────────────────────────────────
# Issue/revoke tokens that map a Cursor/Claude Desktop session to a
# MAARS user_id. The MCP server at backend/mcp_server reads these to
# pick the right wallet + agent + budget context per incoming call.

class _MCPIssue(BaseModel):
    label: str = "default"


@router.post("/mcp/tokens/issue")
async def mcp_token_issue(body: _MCPIssue, current_user: User = Depends(get_current_user)):
    import secrets
    from db import db
    from datetime import datetime, timezone
    token = f"maars_mcp_{secrets.token_urlsafe(24)}"
    await db.mcp_tokens.insert_one({
        "token":    token,
        "user_id":  current_user.user_id,
        "label":    body.label,
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    return {"ok": True, "token": token,
            "hint": "Add as MAARS_MCP_TOKEN env var in Claude Desktop / Cursor MCP config."}


@router.get("/mcp/tokens")
async def mcp_token_list(current_user: User = Depends(get_current_user)):
    from db import db
    cursor = db.mcp_tokens.find(
        {"user_id": current_user.user_id},
        {"_id": 0, "token": 1, "label": 1, "created_at": 1},
    )
    tokens = await cursor.to_list(length=50)
    # Mask the middle of each token so they're identifiable but not copied
    for t in tokens:
        raw = t.get("token") or ""
        t["token_preview"] = raw[:14] + "…" + raw[-4:] if len(raw) > 20 else raw
        t.pop("token", None)
    return {"object": "mcp_tokens", "tokens": tokens}


@router.delete("/mcp/tokens/{token_prefix}")
async def mcp_token_revoke(token_prefix: str, current_user: User = Depends(get_current_user)):
    """Revoke by the first ~14 characters shown in the UI."""
    from db import db
    res = await db.mcp_tokens.delete_one({
        "user_id": current_user.user_id,
        "token": {"$regex": f"^{token_prefix}"},
    })
    return {"ok": True, "deleted": int(getattr(res, "deleted_count", 0) or 0)}


# ── Commander drives the browser ────────────────────────────────────

class _CommanderDriveBody(BaseModel):
    session_id: str
    goal: str
    max_steps: int = 8


@router.post("/commander/drive-browser")
async def commander_drive_browser(
    body: _CommanderDriveBody, current_user: User = Depends(get_current_user),
):
    """Commander Orion takes control of a live browser session and
    executes `goal` autonomously. Uses the existing BrowserAgent loop
    (screenshot → vision LLM → action) with Commander as the caller so
    his training/system_prompt/agent_id appear in gateway_usage_logs.
    Returns the final state + action trace so the UI can display what
    he did.
    """
    from services.browser_service import get_browser_pool
    try:
        from services import browser_agent
    except Exception as exc:
        raise HTTPException(503, f"browser_agent_unavailable: {exc}")
    pool = get_browser_pool()
    session = pool.get(body.session_id)
    if not session:
        raise HTTPException(404, "session_not_found")
    # Claim control for Commander so user input is paused while he works
    session.take_control("agent")
    trace: list[dict] = []
    try:
        # Most browser_agent modules expose a `run()` or `run_goal()`
        # coroutine that loops internally. Fall back to a simple screenshot
        # → LLM → action cycle if the run function isn't exported.
        run_fn = (getattr(browser_agent, "run_goal", None)
                  or getattr(browser_agent, "run", None))
        if run_fn:
            async for event in run_fn(
                session=session,
                goal=body.goal,
                user_id=current_user.user_id,
                agent_id="agent_commander",
                max_steps=max(1, min(int(body.max_steps), 20)),
            ):
                # Events are yielded by browser_agent; collect a compact trace
                if isinstance(event, dict):
                    trace.append({
                        "kind":    event.get("kind"),
                        "step":    event.get("step"),
                        "action":  event.get("action"),
                        "summary": str(event.get("summary") or "")[:200],
                    })
                    if len(trace) >= body.max_steps + 4:
                        break
        else:
            trace.append({"kind": "error",
                          "summary": "browser_agent has no run/run_goal export"})
    finally:
        session.release_control("agent")
    return {
        "ok": True, "session_id": body.session_id,
        "goal": body.goal, "steps": len(trace), "trace": trace,
    }
