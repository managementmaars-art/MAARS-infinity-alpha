"""MAARS — Embedded Browser Runtime routes.

REST endpoints for agents and admin UIs to drive a session. A WebSocket at
`/browser/sessions/{id}/ws` streams screenshots to the frontend and accepts
real-time mouse/keyboard input from the human user — so the same browser
session is simultaneously usable by agents, the system, and the user.

Also exposes the autonomous BrowserAgent via Server-Sent Events at
`/browser/agent/run`, and a one-shot vision-and-act primitive at
`/browser/sessions/{id}/see-and-act`.
"""
from __future__ import annotations

import asyncio
import base64
import contextlib
import json
import logging

from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from auth import get_current_user, User
from services.browser_service import (
    BrowserUnavailable,
    get_browser_pool,
    tool_browser_see_and_act,
)
from services.browser_agent import run_goal as agent_run_goal
from governance.browser_policy import (
    BudgetExhausted, PolicyDenied,
    get_domain_policy, set_domain_policy,
    get_browser_budget, set_browser_budget,
    get_usage_summary,
)
from auth import require_admin

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/browser", tags=["browser"])


# ── Request/response bodies ─────────────────────────────────────────────────
class OpenSessionBody(BaseModel):
    start_url:  str | None = None
    agent_id:   str | None = None


class NavigateBody(BaseModel):
    url:        str
    wait_until: str = "domcontentloaded"


class SelectorBody(BaseModel):
    selector:   str


class FillBody(BaseModel):
    selector:   str
    value:      str


class TypeBody(BaseModel):
    text:       str


class KeyBody(BaseModel):
    key:        str


class ScrollBody(BaseModel):
    dy:         int


class CoordBody(BaseModel):
    x:          int
    y:          int


class EvalBody(BaseModel):
    expression: str


class HandoffBody(BaseModel):
    driver:     str = Field(pattern="^(agent|system|user|shared)$")


class SeeAndActBody(BaseModel):
    goal:       str
    execute:    bool = True


class AgentRunBody(BaseModel):
    goal:              str
    start_url:         str | None = None
    max_steps:         int = 20
    session_id:        str | None = None
    handoff_on_2fa:    bool = True


class OpenTabBody(BaseModel):
    url:            str | None = None
    integration_id: str | None = None
    label:          str | None = None
    activate:       bool = True


class IntegrationConnectBody(BaseModel):
    session_id:     str | None = None      # reuse an open session, else a new one is made
    run_agent:      bool = False           # fire the BrowserAgent to drive the flow
    agent_goal:     str | None = None      # override the default agent goal


# ── Health / availability ───────────────────────────────────────────────────
@router.get("/health")
async def browser_health():
    pool = get_browser_pool()
    available = pool.available()
    return {
        "available":     available,
        "active_sessions": len([s for s in pool._sessions.values()]),  # noqa: SLF001
        "install_hint":  pool.install_hint() if not available else "",
    }


# ── Session lifecycle ──────────────────────────────────────────────────────
@router.post("/sessions")
async def open_session(body: OpenSessionBody, user: User = Depends(get_current_user)):
    try:
        session = await get_browser_pool().open(
            user_id=user.user_id, agent_id=body.agent_id, start_url=body.start_url
        )
    except BrowserUnavailable as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    except BudgetExhausted as e:
        raise HTTPException(status_code=429, detail=str(e)) from e
    except PolicyDenied as e:
        raise HTTPException(status_code=451, detail=str(e)) from e
    except Exception as e:
        # Surface the real traceback — otherwise uvicorn swallows it to a
        # generic 500 "Internal Server Error" and the operator can't diagnose.
        import traceback
        tb = traceback.format_exc()
        logger.error(f"open_session crashed:\n{tb}")
        raise HTTPException(
            status_code=500,
            detail=f"{type(e).__name__}: {e}\n\n{tb}",
        ) from e
    return await session.state()


@router.get("/sessions")
async def list_sessions(user: User = Depends(get_current_user)):
    return await get_browser_pool().list_for_user(user.user_id)


@router.delete("/sessions/{session_id}")
async def close_session(session_id: str, user: User = Depends(get_current_user)):
    s = get_browser_pool().get(session_id)
    if s is None or s.user_id != user.user_id:
        raise HTTPException(status_code=404, detail="session not found")
    ok = await get_browser_pool().close_session(session_id)
    return {"closed": ok}


def _resolve_session(session_id: str, user: User):
    s = get_browser_pool().get(session_id)
    if s is None or s.user_id != user.user_id:
        raise HTTPException(status_code=404, detail="session not found")
    return s


# ── Control handoff ─────────────────────────────────────────────────────────
@router.post("/sessions/{session_id}/take-control")
async def take_control(session_id: str, body: HandoffBody,
                       user: User = Depends(get_current_user)):
    s = _resolve_session(session_id, user)
    await s.take_control(body.driver)
    return await s.state()


@router.post("/sessions/{session_id}/release-control")
async def release_control(session_id: str, body: HandoffBody,
                          user: User = Depends(get_current_user)):
    s = _resolve_session(session_id, user)
    await s.release_control(body.driver)
    return await s.state()


# ── Navigation + interaction ────────────────────────────────────────────────
@router.post("/sessions/{session_id}/navigate")
async def session_navigate(session_id: str, body: NavigateBody,
                           user: User = Depends(get_current_user)):
    s = _resolve_session(session_id, user)
    try:
        return await s.navigate(body.url, caller="user", wait_until=body.wait_until)
    except PolicyDenied as e:
        raise HTTPException(status_code=451, detail=str(e)) from e


@router.post("/sessions/{session_id}/click")
async def session_click(session_id: str, body: SelectorBody,
                        user: User = Depends(get_current_user)):
    s = _resolve_session(session_id, user)
    return await s.click(body.selector, caller="user")


@router.post("/sessions/{session_id}/click-at")
async def session_click_at(session_id: str, body: CoordBody,
                           user: User = Depends(get_current_user)):
    s = _resolve_session(session_id, user)
    return await s.click_at(body.x, body.y, caller="user")


@router.post("/sessions/{session_id}/fill")
async def session_fill(session_id: str, body: FillBody,
                       user: User = Depends(get_current_user)):
    s = _resolve_session(session_id, user)
    return await s.fill(body.selector, body.value, caller="user")


@router.post("/sessions/{session_id}/type")
async def session_type(session_id: str, body: TypeBody,
                       user: User = Depends(get_current_user)):
    s = _resolve_session(session_id, user)
    return await s.type_text(body.text, caller="user")


@router.post("/sessions/{session_id}/key")
async def session_key(session_id: str, body: KeyBody,
                      user: User = Depends(get_current_user)):
    s = _resolve_session(session_id, user)
    return await s.press_key(body.key, caller="user")


@router.post("/sessions/{session_id}/scroll")
async def session_scroll(session_id: str, body: ScrollBody,
                         user: User = Depends(get_current_user)):
    s = _resolve_session(session_id, user)
    return await s.scroll(body.dy, caller="user")


@router.post("/sessions/{session_id}/evaluate")
async def session_evaluate(session_id: str, body: EvalBody,
                           user: User = Depends(get_current_user)):
    s = _resolve_session(session_id, user)
    try:
        return {"result": await s.evaluate(body.expression, caller="user")}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


# ── Read-only extraction ────────────────────────────────────────────────────
@router.get("/sessions/{session_id}/state")
async def session_state(session_id: str, user: User = Depends(get_current_user)):
    return await _resolve_session(session_id, user).state()


@router.get("/sessions/{session_id}/screenshot")
async def session_screenshot(session_id: str,
                             user: User = Depends(get_current_user),
                             full_page: bool = False):
    png = await _resolve_session(session_id, user).screenshot(full_page=full_page)
    return {"image_base64": base64.b64encode(png).decode()}


@router.get("/sessions/{session_id}/text")
async def session_text(session_id: str, selector: str = "body",
                       user: User = Depends(get_current_user)):
    return {"text": await _resolve_session(session_id, user).extract_text(selector)}


@router.get("/sessions/{session_id}/html")
async def session_html(session_id: str, user: User = Depends(get_current_user)):
    return {"html": await _resolve_session(session_id, user).extract_html()}


# ── Tabs ────────────────────────────────────────────────────────────────────
@router.get("/sessions/{session_id}/tabs")
async def list_tabs(session_id: str, user: User = Depends(get_current_user)):
    return await _resolve_session(session_id, user).list_tabs()


@router.post("/sessions/{session_id}/tabs")
async def open_tab(session_id: str, body: OpenTabBody,
                   user: User = Depends(get_current_user)):
    s = _resolve_session(session_id, user)
    try:
        return await s.open_tab(
            url=body.url, integration_id=body.integration_id,
            label=body.label, activate=body.activate,
        )
    except PolicyDenied as e:
        raise HTTPException(status_code=451, detail=str(e)) from e


@router.post("/sessions/{session_id}/tabs/{tab_id}/activate")
async def activate_tab(session_id: str, tab_id: str,
                       user: User = Depends(get_current_user)):
    s = _resolve_session(session_id, user)
    try:
        return await s.switch_tab(tab_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.delete("/sessions/{session_id}/tabs/{tab_id}")
async def close_tab(session_id: str, tab_id: str,
                    user: User = Depends(get_current_user)):
    s = _resolve_session(session_id, user)
    closed = await s.close_tab(tab_id)
    return {"closed": closed}


# ── Integration connect ─────────────────────────────────────────────────────
# Well-known OAuth / connect URLs for each integration. Values come from the
# `oauth_url` field in INTEGRATION_SERVICES where present; we enrich a few
# common ones the catalog leaves blank so "click to connect" works out of the
# box. Extend here when adding a new integration.
_INTEGRATION_CONNECT_URL = {
    "google_suite": "https://accounts.google.com/signin",
    "github":       "https://github.com/login",
    "slack":        "https://slack.com/signin",
    "hubspot":      "https://app.hubspot.com/login",
    "salesforce":   "https://login.salesforce.com/",
    "shopify":      "https://accounts.shopify.com/store-login",
    "stripe":       "https://dashboard.stripe.com/login",
    "notion":       "https://www.notion.so/login",
    "jira":         "https://id.atlassian.com/login",
    "confluence":   "https://id.atlassian.com/login",
    "linkedin":     "https://www.linkedin.com/login",
    "twitter":      "https://twitter.com/i/flow/login",
    "facebook":     "https://www.facebook.com/login",
    "instagram":    "https://www.instagram.com/accounts/login/",
    "tiktok":       "https://www.tiktok.com/login",
    "youtube":      "https://accounts.google.com/signin",
    "airtable":     "https://airtable.com/login",
    "calendly":     "https://calendly.com/login",
    "telegram":     "https://web.telegram.org/",
    "whatsapp":     "https://web.whatsapp.com/",
    "sendgrid":     "https://app.sendgrid.com/login",
    "resend":       "https://resend.com/login",
    "twilio":       "https://login.twilio.com/",
    "viber":        "https://www.viber.com/en/",
    "line":         "https://account.line.biz/login",
    "giphy":        "https://giphy.com/login",
    "webhooks":     "about:blank",   # no UI — just a config hub
    "browser":      "about:blank",
}


@router.post("/integrations/{integration_id}/connect")
async def integration_connect(integration_id: str, body: IntegrationConnectBody,
                              user: User = Depends(get_current_user)):
    """Open a browser tab at the integration's login/OAuth URL and optionally
    hand it to the autonomous BrowserAgent to drive the flow."""
    from shared.constants import INTEGRATION_SERVICES
    if integration_id not in INTEGRATION_SERVICES:
        raise HTTPException(status_code=404, detail=f"unknown integration: {integration_id}")

    spec = INTEGRATION_SERVICES[integration_id]
    url = spec.get("oauth_url") or _INTEGRATION_CONNECT_URL.get(integration_id) or "about:blank"

    pool = get_browser_pool()
    try:
        if body.session_id:
            s = pool.get(body.session_id)
            if s is None or s.user_id != user.user_id:
                raise HTTPException(status_code=404, detail="session not found")
        else:
            s = await pool.open(user_id=user.user_id, agent_id="integration_connect")
    except BrowserUnavailable as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    except BudgetExhausted as e:
        raise HTTPException(status_code=429, detail=str(e)) from e

    tab = await s.open_tab(url=url, integration_id=integration_id,
                           label=spec.get("name", integration_id), activate=True)

    agent_kickoff = None
    if body.run_agent:
        from services.browser_agent import run_goal as agent_run_goal
        goal = body.agent_goal or (
            f"Sign in to {spec.get('name', integration_id)}. Hand off to the "
            f"human user for any one-time code, 2FA, CAPTCHA, or password entry."
        )
        events: list[dict] = []
        async for evt in agent_run_goal(
            user_id=user.user_id, goal=goal, max_steps=12,
            existing_session_id=s.session_id, handoff_on_2fa=True,
        ):
            events.append(evt.to_dict())
            if evt.kind in {"done", "error", "handoff", "waiting_for_user"}:
                break     # stop streaming here; client can re-start via /agent/run
        agent_kickoff = events

    return {
        "session_id":     s.session_id,
        "tab":            tab,
        "integration_id": integration_id,
        "url":            url,
        "agent_kickoff":  agent_kickoff,
    }


# ── Vision: one-shot see-and-act ────────────────────────────────────────────
@router.post("/sessions/{session_id}/see-and-act")
async def see_and_act(session_id: str, body: SeeAndActBody,
                      user: User = Depends(get_current_user)):
    """Take a screenshot, ask the vision model what to do next toward `goal`,
    optionally execute it. Use when one perception + action step is enough."""
    _resolve_session(session_id, user)   # authz + existence check
    try:
        return await tool_browser_see_and_act(session_id, body.goal, execute=body.execute, caller="user")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


# ── Autonomous BrowserAgent (streaming) ─────────────────────────────────────
@router.post("/agent/run")
async def agent_run(body: AgentRunBody, user: User = Depends(get_current_user)):
    """Run the autonomous BrowserAgent against a goal. Streams Server-Sent
    Events; each line is `data: <json>\\n\\n`. Events have `kind` ∈
    {step, action, handoff, waiting_for_user, done, error}."""

    async def event_stream():
        # SSE framing: each event JSON on its own `data:` line.
        try:
            async for evt in agent_run_goal(
                user_id=user.user_id,
                goal=body.goal,
                start_url=body.start_url,
                max_steps=max(1, min(body.max_steps, 50)),
                existing_session_id=body.session_id,
                handoff_on_2fa=body.handoff_on_2fa,
            ):
                yield f"data: {json.dumps(evt.to_dict())}\n\n"
                if evt.kind in {"done", "error"}:
                    break
        except BrowserUnavailable as e:
            yield f"data: {json.dumps({'kind': 'error', 'step': 0, 'message': str(e)})}\n\n"
        except Exception as e:
            logger.exception("agent_run failed")
            yield f"data: {json.dumps({'kind': 'error', 'step': 0, 'message': str(e)})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ── Governance: domain policy + budget + usage ──────────────────────────────
class DomainPolicyBody(BaseModel):
    allow: list[str] = []
    deny:  list[str] = []


class BudgetBody(BaseModel):
    minutes_per_day: int


@router.get("/policy/domains")
async def policy_get_domains(environment: str = "production",
                             _: User = Depends(require_admin)):
    return {
        "environment": environment,
        "policy":      await get_domain_policy(environment),
    }


@router.put("/policy/domains")
async def policy_put_domains(body: DomainPolicyBody,
                             environment: str = "production",
                             _: User = Depends(require_admin)):
    await set_domain_policy(environment, {"allow": body.allow, "deny": body.deny})
    return {"environment": environment, "policy": await get_domain_policy(environment)}


@router.get("/policy/budget")
async def policy_get_budget(user: User = Depends(get_current_user)):
    return {
        "user_id":         user.user_id,
        "minutes_per_day": await get_browser_budget(user.user_id),
    }


@router.put("/policy/budget/{user_id}")
async def policy_put_budget(user_id: str, body: BudgetBody,
                            _: User = Depends(require_admin)):
    await set_browser_budget(user_id, body.minutes_per_day)
    return {
        "user_id":         user_id,
        "minutes_per_day": await get_browser_budget(user_id),
    }


@router.get("/usage")
async def my_browser_usage(user: User = Depends(get_current_user)):
    return await get_usage_summary(user.user_id)


@router.get("/usage/{user_id}")
async def any_user_browser_usage(user_id: str, _: User = Depends(require_admin)):
    return await get_usage_summary(user_id)


# ── WebSocket: live view + user input ───────────────────────────────────────
# Protocol — JSON messages both directions:
#   server → client:  {"type": "frame", "image_base64": "...", "state": {...}}
#                     {"type": "error", "message": "..."}
#   client → server:  {"type": "click", "x": 120, "y": 340}
#                     {"type": "type", "text": "hello"}
#                     {"type": "key", "key": "Enter"}
#                     {"type": "scroll", "dy": 400}
#                     {"type": "navigate", "url": "https://..."}
#                     {"type": "take_control"}   / {"type": "release_control"}
#
# The initial query arg `token` authenticates the websocket — REST auth middleware
# does not apply to WebSockets so we validate here.

@router.websocket("/sessions/{session_id}/ws")
async def session_ws(websocket: WebSocket, session_id: str):
    """Live browser WS.

    Query params:
      token  (required) — JWT for auth
      stream (optional) — 'event' (default) or 'continuous'
      fps    (optional) — frames per second when stream=continuous; default 10
      fmt    (optional) — 'png' (default) or 'jpeg'; jpeg for smooth streaming
    """
    from auth import verify_token  # local import — avoids circular at module load

    await websocket.accept()
    token = websocket.query_params.get("token", "")
    authed_user = await verify_token(token) if token else None
    if authed_user is None:
        await websocket.send_json({"type": "error", "message": "invalid token"})
        await websocket.close()
        return

    session = get_browser_pool().get(session_id)
    if session is None or session.user_id != authed_user.user_id:
        await websocket.send_json({"type": "error", "message": "session not found"})
        await websocket.close()
        return

    # Stream mode config
    stream_mode = websocket.query_params.get("stream", "event")
    img_fmt     = websocket.query_params.get("fmt", "png").lower()
    try:
        fps = max(1, min(int(websocket.query_params.get("fps", "10")), 24))
    except ValueError:
        fps = 10
    mime = "image/jpeg" if img_fmt == "jpeg" else "image/png"

    queue = session.attach_watcher()

    async def send_frame(png_or_jpeg: bytes) -> None:
        with contextlib.suppress(Exception):
            await websocket.send_json({
                "type":         "frame",
                "mime":         mime,
                "image_base64": base64.b64encode(png_or_jpeg).decode(),
                "state":        await session.state(),
            })

    async def push_event_driven():
        # Send an initial snapshot so the UI has something immediately.
        try:
            img = await session.screenshot(kind=img_fmt)
            await send_frame(img)
        except Exception as e:
            logger.warning(f"initial frame failed: {e}")
        while True:
            try:
                # The pool broadcasts pngs; re-encode as jpeg if asked.
                png = await queue.get()
            except asyncio.CancelledError:
                break
            if img_fmt == "jpeg":
                # Re-encode using Playwright to guarantee same viewport dimensions.
                try:
                    png = await session.screenshot(kind="jpeg")
                except Exception:
                    pass
            await send_frame(png)

    async def push_continuous():
        period = 1.0 / fps
        while True:
            try:
                img = await session.screenshot(kind=img_fmt)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.debug(f"continuous frame failed: {e}")
                await asyncio.sleep(period)
                continue
            await send_frame(img)
            await asyncio.sleep(period)

    push_frames = push_continuous if stream_mode == "continuous" else push_event_driven

    async def pull_input():
        while True:
            try:
                raw = await websocket.receive_text()
            except WebSocketDisconnect:
                return
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                continue
            kind = msg.get("type")
            try:
                if kind == "click":
                    await session.click_at(int(msg["x"]), int(msg["y"]), caller="user")
                elif kind == "type":
                    await session.type_text(str(msg.get("text", "")), caller="user")
                elif kind == "key":
                    await session.press_key(str(msg.get("key", "")), caller="user")
                elif kind == "scroll":
                    await session.scroll(int(msg.get("dy", 0)), caller="user")
                elif kind == "navigate":
                    await session.navigate(str(msg.get("url", "")), caller="user")
                elif kind == "take_control":
                    await session.take_control("user")
                elif kind == "release_control":
                    await session.release_control("user")
                else:
                    await websocket.send_json({"type": "error", "message": f"unknown msg: {kind}"})
            except PermissionError as e:
                await websocket.send_json({"type": "error", "message": str(e)})
            except Exception as e:
                logger.warning(f"browser WS input error: {e}")
                await websocket.send_json({"type": "error", "message": str(e)})

    push = asyncio.create_task(push_frames())
    pull = asyncio.create_task(pull_input())
    try:
        await pull
    finally:
        push.cancel()
        with contextlib.suppress(Exception):
            await push
        session.detach_watcher(queue)
