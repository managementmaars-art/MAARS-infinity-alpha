"""MAARS — Autonomous BrowserAgent.

Hand it a goal, it drives the embedded browser until the goal is achieved or
it needs a human to take over (2FA, CAPTCHA, payment, anything ambiguous).

The agent's loop is deliberately small and auditable:

    for step in range(max_steps):
        screenshot = session.screenshot()
        action     = await browser_vision.decide_next_action(goal, history, url, png)
        emit(progress_event)
        execute(action)                    # may also handoff → wait for user
        if action.kind in {"done","error"}: break

Execution is cooperative: the agent takes a lock on the browser session via
`session.take_control("agent")` and releases it when handing off or finishing.
If the user grabs control mid-run (take_control("user")), the agent yields
until the user releases it.

The agent is exposed both as:
    * a service class used by other backend code, and
    * a streaming HTTP endpoint (Server-Sent Events) in routes/browser.py.
"""
from __future__ import annotations

import asyncio
import contextlib
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import AsyncIterator

from services.browser_service import BrowserSession, get_browser_pool
from services.browser_vision import Action, action_to_dict, decide_next_action

logger = logging.getLogger(__name__)


@dataclass
class AgentEvent:
    kind:      str                        # step | action | handoff | waiting_for_user | done | error
    step:      int
    action:    dict | None = None
    state:     dict | None = None
    message:   str = ""
    timestamp: str = ""

    def to_dict(self) -> dict:
        return {
            "kind":      self.kind,
            "step":      self.step,
            "action":    self.action,
            "state":     self.state,
            "message":   self.message,
            "timestamp": self.timestamp or datetime.now(timezone.utc).isoformat(),
        }


HANDOFF_KEYWORDS = (
    # 2FA / one-time codes
    "verification code", "two-factor", "two factor", "2fa", "authentication code",
    "one-time code", "one-time password", "otp", "authenticator app",
    # CAPTCHA
    "captcha", "i'm not a robot", "are you human", "prove you're human",
    # Payment / cardholder action
    "enter card number", "cvv", "3-d secure", "3d secure", "verify payment",
)


def _looks_like_handoff(text: str) -> bool:
    t = (text or "").lower()
    return any(k in t for k in HANDOFF_KEYWORDS)


async def _wait_for_user_release(session: BrowserSession, timeout_s: int = 300) -> bool:
    """Block until the user releases control (driver goes back to shared/agent)
    or the timeout elapses. Returns True if released, False on timeout."""
    deadline = asyncio.get_event_loop().time() + timeout_s
    while asyncio.get_event_loop().time() < deadline:
        if session.driver in ("shared", "agent"):
            return True
        await asyncio.sleep(0.5)
    return False


async def _execute_action(session: BrowserSession, action: Action) -> str:
    """Apply an action to the session. Returns a human-readable status line."""
    try:
        if action.kind == "click":
            if action.x is None or action.y is None:
                return "click without coordinates"
            await session.click_at(action.x, action.y, caller="agent")
            return f"clicked ({action.x}, {action.y})"
        if action.kind == "type":
            await session.type_text(action.text or "", caller="agent")
            return f"typed {len(action.text or '')} chars"
        if action.kind == "key":
            await session.press_key(action.key or "Enter", caller="agent")
            return f"pressed {action.key or 'Enter'}"
        if action.kind == "navigate":
            await session.navigate(action.url or "about:blank", caller="agent")
            return f"navigated to {action.url}"
        if action.kind == "scroll":
            await session.scroll(int(action.dy or 400), caller="agent")
            return f"scrolled by {action.dy}"
        if action.kind == "wait":
            await asyncio.sleep((action.ms or 500) / 1000)
            return f"waited {action.ms}ms"
    except PermissionError as e:
        # User grabbed control — surface it so the loop waits.
        return f"blocked: {e}"
    except Exception as e:
        logger.warning(f"browser agent action {action.kind} failed: {e}")
        return f"failed: {e}"
    return f"no-op ({action.kind})"


async def run_goal(
    *, user_id: str, goal: str, start_url: str | None = None,
    max_steps: int = 20, existing_session_id: str | None = None,
    handoff_on_2fa: bool = True,
) -> AsyncIterator[AgentEvent]:
    """Drive the browser toward `goal`. Yields AgentEvents as a stream.

    If `existing_session_id` is given, the agent joins that session (shares
    cookies and state with whatever the user was already doing). Otherwise it
    opens a fresh session bound to the user.
    """
    pool = get_browser_pool()

    # ── Acquire or open a session ───────────────────────────────────────────
    if existing_session_id:
        session = pool.get(existing_session_id)
        if session is None or session.user_id != user_id:
            yield AgentEvent(kind="error", step=0,
                             message=f"session {existing_session_id} not found for user")
            return
    else:
        try:
            session = await pool.open(user_id=user_id, agent_id="browser_agent",
                                      start_url=start_url)
        except Exception as e:
            yield AgentEvent(kind="error", step=0,
                             message=f"could not open session: {e}")
            return

    await session.take_control("agent")
    history: list[dict] = []

    try:
        for step in range(1, max_steps + 1):
            # If the user has taken over, wait for them before thinking.
            if session.driver == "user":
                yield AgentEvent(kind="waiting_for_user", step=step,
                                 message="User has control; agent paused.",
                                 state=await session.state())
                released = await _wait_for_user_release(session)
                if not released:
                    yield AgentEvent(kind="error", step=step,
                                     message="Timed out waiting for user to release control.",
                                     state=await session.state())
                    return
                await session.take_control("agent")

            # Perceive.
            try:
                screenshot = await session.screenshot()
            except Exception as e:
                yield AgentEvent(kind="error", step=step,
                                 message=f"screenshot failed: {e}")
                return
            state = await session.state()

            # Decide.
            action = await decide_next_action(
                goal=goal, history=history, current_url=state.get("url", ""),
                screenshot_png=screenshot,
            )
            history.append({"kind": action.kind, "reason": action.reason})
            yield AgentEvent(kind="action", step=step,
                             action=action_to_dict(action), state=state)

            # 2FA / CAPTCHA / payment handoff.
            if handoff_on_2fa and (
                action.kind == "handoff"
                or _looks_like_handoff(action.reason)
            ):
                await session.release_control("agent")  # let the user in
                await session.take_control("user")
                yield AgentEvent(kind="handoff", step=step,
                                 message=action.reason or "Handoff requested (2FA / CAPTCHA / payment).",
                                 state=await session.state())
                released = await _wait_for_user_release(session)
                if not released:
                    yield AgentEvent(kind="error", step=step,
                                     message="Timed out waiting for user to complete the handoff.",
                                     state=await session.state())
                    return
                await session.take_control("agent")
                continue  # re-perceive the page the user just finished

            if action.kind == "done":
                yield AgentEvent(kind="done", step=step,
                                 message=action.reason or "Goal achieved.",
                                 state=await session.state())
                return
            if action.kind == "error":
                yield AgentEvent(kind="error", step=step,
                                 message=action.reason or "Agent gave up.",
                                 state=await session.state())
                return

            # Execute.
            status = await _execute_action(session, action)
            yield AgentEvent(kind="step", step=step, message=status,
                             state=await session.state())

        # Fell off the end without a done/error — cap with a clean stop.
        yield AgentEvent(kind="error", step=max_steps,
                         message=f"Reached max_steps={max_steps} without finishing.",
                         state=await session.state())
    finally:
        with contextlib.suppress(Exception):
            await session.release_control("agent")


