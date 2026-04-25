"""Parlant bridge — deterministic state-machine agents for regulated flows.

Pattern from patchy631/ai-engineering-hub/parlant-conversational-agent:
for KYC / loan / insurance / medical / compliance intake, monolithic
prompts can't pass audit. Parlant provides if-then guidelines attached
to an agent + explicit state-machine journeys (N0 → N1 → N2 …).

Deployment model: Parlant runs as a sidecar on port 8800. MAARS calls
it via HTTP for regulated conversations. Non-regulated chat continues
through the normal `llm_gateway.complete()` path.

Public API:
  is_available() — does the env point to a live Parlant server?
  chat(user_id, journey_id, message) — route one turn through Parlant
  list_journeys() — journeys registered on the server

Required env:
  PARLANT_URL            — http://localhost:8800 by default
  PARLANT_API_KEY        — optional, set per-deployment

Install + run sidecar:
  pip install parlant
  parlant-server --port 8800
  # then register journeys via their CLI or API
"""
from __future__ import annotations
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


def _base_url() -> str:
    return os.environ.get("PARLANT_URL", "http://localhost:8800").rstrip("/")


def _headers() -> dict[str, str]:
    h = {"Content-Type": "application/json"}
    k = os.environ.get("PARLANT_API_KEY")
    if k:
        h["Authorization"] = f"Bearer {k}"
    return h


async def is_available() -> bool:
    """Ping the sidecar; True only when running."""
    import httpx
    try:
        async with httpx.AsyncClient(timeout=3) as c:
            r = await c.get(f"{_base_url()}/health", headers=_headers())
            return r.status_code < 400
    except Exception:
        return False


async def list_journeys() -> list[dict[str, Any]]:
    if not await is_available():
        return []
    import httpx
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.get(f"{_base_url()}/agents", headers=_headers())
    return r.json() if r.status_code < 400 else []


async def chat(
    *, user_id: str, journey_id: str, message: str,
    session_id: str | None = None,
) -> dict[str, Any]:
    """Route one turn through the Parlant sidecar. Returns
    {reply, next_state, citations?}."""
    if not await is_available():
        return {"ok": False, "error": "parlant_sidecar_not_running",
                "hint": "Start with: parlant-server --port 8800"}
    import httpx
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.post(
            f"{_base_url()}/sessions/{session_id or 'default'}/message",
            headers=_headers(),
            json={
                "journey_id": journey_id,
                "user_id":    user_id,
                "message":    message,
            },
        )
    if r.status_code >= 400:
        return {"ok": False, "error": f"parlant_error: {r.status_code} {r.text[:200]}"}
    data = r.json() or {}
    return {
        "ok":          True,
        "reply":       data.get("reply") or data.get("content"),
        "state":       data.get("state") or data.get("node"),
        "next_state":  data.get("next_state"),
        "compliance":  data.get("compliance_flags") or [],
    }


# ── Executor hook: state_machine_node for workflow_executor ──────

async def _t_state_machine(user_id: str, params: dict, inp: dict) -> dict:
    """New workflow tool: route a turn through a Parlant journey.

    params:
      journey_id:  string, registered on the sidecar
      message:     string (usually {{prev.output}})
      session_id:  string; stable per end-user conversation
    """
    journey = (params.get("journey_id") or "").strip()
    msg = (params.get("message") or "").strip()
    sid = params.get("session_id")
    if not (journey and msg):
        return {"ok": False, "error": "journey_id + message required"}
    return await chat(user_id=user_id, journey_id=journey,
                       message=msg, session_id=sid)


# Self-register on import so the executor picks up the new tool
try:
    from services.workflows.workflow_executor import TOOL_REGISTRY as _TR
    _TR.setdefault("state_machine", _t_state_machine)
except Exception:
    pass
