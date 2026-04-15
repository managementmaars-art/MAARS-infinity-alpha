"""MAARS — Browser Vision.

Given a screenshot of the current page and a goal, ask a vision-capable model
what to do next. Returns a structured `Action` that the BrowserAgent executes.

Supported vision providers (in fallback order):
    OpenAI GPT-4o / gpt-4o-mini
    Anthropic Claude 3.5 Sonnet

Both take images as base64. The prompt asks for a STRICT JSON response so we
can parse reliably; if the model returns commentary around it we extract the
first JSON block.
"""
from __future__ import annotations

import base64
import json
import logging
import os
import re
from dataclasses import asdict, dataclass
from typing import Literal

import httpx

logger = logging.getLogger(__name__)

ActionKind = Literal[
    "click",          # click coordinates (x, y are viewport pixels)
    "type",           # type text into currently focused element
    "key",            # press a keyboard key (Enter, Tab, Escape, ...)
    "navigate",       # open a URL
    "scroll",         # positive = scroll down, negative = up
    "wait",           # wait N ms (useful after network actions)
    "handoff",        # ask the human to take over (2FA, CAPTCHA, payment …)
    "done",           # goal achieved — stop the loop
    "error",          # can't proceed, give up with reason
]


@dataclass
class Action:
    kind:        ActionKind
    x:           int | None = None
    y:           int | None = None
    text:        str | None = None
    key:         str | None = None
    url:         str | None = None
    dy:          int | None = None
    ms:          int | None = None
    reason:      str = ""
    confidence:  float = 0.0


SYSTEM_PROMPT = """You are the vision module inside an autonomous web agent.

Input: a screenshot of the current browser viewport, the user's goal, and the
history of actions already taken. Decide the single next action.

Always reply with ONE JSON object matching this schema exactly:

{
  "kind": "click|type|key|navigate|scroll|wait|handoff|done|error",
  "x": <int or null>,            // viewport pixels, only for click
  "y": <int or null>,            // viewport pixels, only for click
  "text": <string or null>,      // for type
  "key": <string or null>,       // for key ("Enter", "Tab", "Escape", ...)
  "url": <string or null>,       // for navigate
  "dy": <int or null>,           // for scroll (positive = down)
  "ms": <int or null>,           // for wait
  "reason": "<one short sentence on why this is the right next step>",
  "confidence": <float 0.0..1.0>
}

Rules:
- If the page is asking for a one-time code, 2FA, CAPTCHA, or payment info
  that a human must provide, return kind="handoff" with a clear reason.
- If the goal appears achieved (target content visible, success message, etc.),
  return kind="done".
- If there's no way forward (blocked, error page, wrong site), return kind="error".
- NEVER include any explanation outside the JSON object.
- For click, pick coordinates near the CENTER of the target element.
- Viewport size is 1280x800 unless otherwise stated.
"""


def _extract_json(text: str) -> dict | None:
    """Tolerant JSON extraction — handles fenced blocks and surrounding prose."""
    text = text.strip()
    # Strip common fences.
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    # Try straight parse.
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Find the first JSON object in the text.
    m = re.search(r"\{[\s\S]*\}", text)
    if m:
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            return None
    return None


def _coerce_action(payload: dict) -> Action:
    kind = payload.get("kind", "error")
    if kind not in {"click","type","key","navigate","scroll","wait","handoff","done","error"}:
        kind = "error"
    def _as_int(v):
        try: return int(v) if v is not None else None
        except Exception: return None
    return Action(
        kind       = kind,                                             # type: ignore[arg-type]
        x          = _as_int(payload.get("x")),
        y          = _as_int(payload.get("y")),
        text       = payload.get("text"),
        key        = payload.get("key"),
        url        = payload.get("url"),
        dy         = _as_int(payload.get("dy")),
        ms         = _as_int(payload.get("ms")),
        reason     = str(payload.get("reason", ""))[:500],
        confidence = float(payload.get("confidence") or 0.0),
    )


def _user_message(goal: str, history: list[dict], current_url: str) -> str:
    hist = "\n".join(
        f"  {i+1}. {h.get('kind','?')} — {h.get('reason','')}" for i, h in enumerate(history[-10:])
    ) or "  (none yet)"
    return (
        f"GOAL: {goal}\n\n"
        f"CURRENT URL: {current_url or '(blank tab)'}\n\n"
        f"RECENT ACTIONS:\n{hist}\n\n"
        "Look at the screenshot and decide the single next action."
    )


# ── Provider adapters ───────────────────────────────────────────────────────
async def _decide_via_openai(goal, history, current_url, screenshot_png) -> Action | None:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None
    img_b64 = base64.b64encode(screenshot_png).decode()
    body = {
        "model": os.environ.get("MAARS_VISION_MODEL", "gpt-4o-mini"),
        "max_tokens": 400,
        "temperature": 0.0,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": [
                {"type": "text", "text": _user_message(goal, history, current_url)},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}},
            ]},
        ],
    }
    try:
        async with httpx.AsyncClient(timeout=60) as http:
            r = await http.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json=body,
            )
            r.raise_for_status()
            text = r.json()["choices"][0]["message"]["content"]
        parsed = _extract_json(text)
        return _coerce_action(parsed) if parsed else None
    except Exception as e:
        logger.warning(f"browser vision openai failed: {e}")
        return None


async def _decide_via_anthropic(goal, history, current_url, screenshot_png) -> Action | None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    img_b64 = base64.b64encode(screenshot_png).decode()
    body = {
        "model": os.environ.get("MAARS_VISION_ANTHROPIC_MODEL", "claude-sonnet-4-6"),
        "max_tokens": 400,
        "system": SYSTEM_PROMPT,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": img_b64}},
                {"type": "text",  "text": _user_message(goal, history, current_url)},
            ],
        }],
    }
    try:
        async with httpx.AsyncClient(timeout=60) as http:
            r = await http.post(
                "https://api.anthropic.com/v1/messages",
                headers={"x-api-key": api_key, "anthropic-version": "2023-06-01", "Content-Type": "application/json"},
                json=body,
            )
            r.raise_for_status()
            text = r.json()["content"][0]["text"]
        parsed = _extract_json(text)
        return _coerce_action(parsed) if parsed else None
    except Exception as e:
        logger.warning(f"browser vision anthropic failed: {e}")
        return None


# ── Public API ──────────────────────────────────────────────────────────────
async def decide_next_action(
    *, goal: str, history: list[dict], current_url: str, screenshot_png: bytes,
) -> Action:
    """Get the next action from a vision model. Returns Action(kind='error')
    with a useful reason when no provider is available."""
    action = await _decide_via_openai(goal, history, current_url, screenshot_png)
    if action is not None:
        return action
    action = await _decide_via_anthropic(goal, history, current_url, screenshot_png)
    if action is not None:
        return action
    return Action(
        kind="error",
        reason="No vision-capable LLM is configured. Set OPENAI_API_KEY or ANTHROPIC_API_KEY.",
    )


def action_to_dict(a: Action) -> dict:
    return asdict(a)
