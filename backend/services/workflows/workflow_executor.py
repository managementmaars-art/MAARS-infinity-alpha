"""Workflow DAG executor — the engine routes/workflows.py has been waiting for.

routes/workflows.py stores DAGs and queues runs with status="queued".
This module actually walks them. Lives in its own service so the
scheduler, the `/workflows/{id}/run` route, and any future trigger
sources (webhook, email_reply, scheduled) all share one executor.

Execution model:
  1. Fetch workflow + run row from Mongo.
  2. Topological walk from any node with zero predecessors, honoring
     next / branch_yes / branch_no.
  3. Each node fires its tool via TOOL_REGISTRY below.
  4. Each node's output becomes the next node's `input` (plus any named
     `params` the DAG author set at design time).
  5. Retries: 3 attempts with exp-backoff per node. Hard-fail on 4th.
  6. Timeout: per-node 5m default, overridable via node.params.timeout_ms.
  7. Progress: each node transition writes a `workflow_run_events` row
     AND emits an asyncio broadcast so SSE subscribers see live progress.

The public surface:
    await run(run_id, workflow_doc, overrides) -> final state dict
    subscribe(run_id) -> async generator of event dicts (for SSE)

Tools map to existing MAARS services — no new business logic lives
here. That keeps the executor a thin walker and the tools
independently testable.
"""
from __future__ import annotations
import asyncio
import inspect
import json
import logging
import time
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT_MS = 5 * 60_000
DEFAULT_RETRIES = 3
INITIAL_BACKOFF = 0.5


# ── Event bus ────────────────────────────────────────────────────────
# One queue per active run. SSE consumers subscribe; the executor pushes.
_subscribers: dict[str, list[asyncio.Queue]] = {}


def subscribe(run_id: str) -> asyncio.Queue:
    q: asyncio.Queue = asyncio.Queue(maxsize=500)
    _subscribers.setdefault(run_id, []).append(q)
    return q


def unsubscribe(run_id: str, q: asyncio.Queue) -> None:
    subs = _subscribers.get(run_id)
    if subs and q in subs:
        subs.remove(q)
        if not subs:
            _subscribers.pop(run_id, None)


async def _publish(run_id: str, event: dict[str, Any]) -> None:
    """Non-blocking fanout. Drop events for slow consumers rather than
    stall the executor."""
    for q in list(_subscribers.get(run_id, [])):
        try:
            q.put_nowait(event)
        except asyncio.QueueFull:
            pass


# ── Tool registry ────────────────────────────────────────────────────
# Each tool is an async callable:
#   async def tool(user_id, params, input_from_prev_node) -> dict
# Registering here keeps workflows.py's VALID_TOOLS set consistent
# with what the executor can actually run.

async def _t_search_leads(user_id: str, params: dict, _inp: dict) -> dict:
    from routes.lead_research import _get_adapter
    adapter, _ = _get_adapter()
    if adapter is None:
        return {"ok": False, "error": "lead research adapter not configured"}
    q = params.get("query") or {}
    rows = await adapter.search_people(q)
    return {"ok": True, "leads": rows}


async def _t_enrich_contact(user_id: str, params: dict, inp: dict) -> dict:
    from routes.lead_research import _get_adapter
    adapter, _ = _get_adapter()
    if adapter is None or not hasattr(adapter, "enrich"):
        return {"ok": False, "error": "enrich not supported by active adapter"}
    email = params.get("email") or (inp.get("leads", [{}])[0].get("email") if inp.get("leads") else None)
    if not email:
        return {"ok": False, "error": "no email to enrich"}
    r = await adapter.enrich(email)
    return {"ok": True, "contact": r}


async def _t_agent_chat(user_id: str, params: dict, inp: dict) -> dict:
    """Invoke a specific MAARS agent with a prompt. Routes through the
    same `llm_gateway.complete_text()` everything else does, so the
    agent's system_prompt + golden examples + per-agent budget + skill
    cache all apply.

    params:
      agent_id:   Required. One of the 499 agents in db.agents.
      prompt:     What the agent should do (may use {{upstream.foo}} etc).
      system:     Optional system prompt override (defaults to the
                  agent's stored system_prompt via the gateway).
      model:      Optional model override (default: agent's own or
                  maars/auto).
      max_tokens, temperature: Optional sampling overrides.
    Returns:
      {ok, output, agent_id, agent_name}
    """
    from db import db
    from services.llm_gateway import complete_text
    agent_id = (params.get("agent_id") or "").strip()
    if not agent_id:
        return {"ok": False, "error": "agent_chat: params.agent_id required"}
    agent = await db.agents.find_one({"agent_id": agent_id}, {"_id": 0})
    if not agent:
        return {"ok": False, "error": f"agent_chat: unknown agent_id '{agent_id}'"}
    # Use the agent's own system_prompt unless caller overrides
    system = params.get("system") or agent.get("system_prompt") or ""
    prompt = params.get("prompt") or params.get("user_prompt") or ""
    if not prompt:
        # Fall back to using prev-node's output as the prompt so agents
        # can chain without explicit wiring
        try:
            prompt = json.dumps(inp, default=str)[:4000]
        except Exception:
            prompt = str(inp)[:4000]
    model = (params.get("model")
             or agent.get("model_name")
             or "maars/auto")
    # Provider-prefix if the agent stored provider/model split
    if model and "/" not in model and agent.get("model_provider"):
        model = f"{agent['model_provider']}/{model}"
    output = await complete_text(
        user_id,
        system_prompt=system,
        user_prompt=prompt,
        model=model,
        max_tokens=params.get("max_tokens", 1200),
        temperature=params.get("temperature", 0.5),
        source=f"workflow.agent_chat:{agent_id}",
        agent_id=agent_id,
    )
    return {
        "ok": True,
        "output":     output,
        "agent_id":   agent_id,
        "agent_name": agent.get("name"),
    }


async def _t_delegate_to_agent(user_id: str, params: dict, inp: dict) -> dict:
    """Full cross-agent delegation — hand the request to another agent
    and run THEIR full Office SOP. Unlike `agent_chat` (one-shot LLM call),
    this runs the target agent through their entire research → plan →
    produce → verify → deliver pipeline.

    params:
      agent_id:     Required. Target agent's id.
      user_request: Required. The brief the target agent receives.
      context:      Optional dict passed as accumulated context.
      timeout_s:    Optional hard cap on delegation (default: 300s).
    Returns:
      {ok, output, trace, agent_id, studio_name, quality_checks}

    This is the mechanism Commander Orion uses for multi-agent
    orchestration. Commander's SOP step `delegate` emits tool_calls
    pointing at this handler; runner executes; result threads back
    into Commander's `supervise` + `verify` steps.
    """
    import asyncio
    agent_id = (params.get("agent_id") or "").strip()
    request  = (params.get("user_request") or params.get("prompt") or "").strip()
    if not agent_id:
        return {"ok": False, "error": "delegate_to_agent: params.agent_id required"}
    if not request:
        # Fall through to upstream-node output like agent_chat does
        try: request = json.dumps(inp, default=str)[:4000]
        except Exception: request = str(inp)[:4000]
    from services.agents.agent_office import get as office_get, run_sop
    target = await office_get(agent_id)
    if not target:
        return {"ok": False, "error": f"delegate_to_agent: no office for '{agent_id}'"}
    try:
        result = await asyncio.wait_for(
            run_sop(target, request, user_id=user_id, context=params.get("context")),
            timeout=float(params.get("timeout_s") or 300.0),
        )
    except asyncio.TimeoutError:
        return {"ok": False, "error": "delegate_to_agent: timeout",
                "agent_id": agent_id}
    return {
        "ok":              bool(result.get("ok")),
        "agent_id":        agent_id,
        "studio_name":     target.studio_name,
        "output":          result.get("output"),
        "trace":           result.get("trace"),
        "quality_checks":  result.get("quality_checks"),
        "matched_skill":   result.get("matched_skill"),
    }


async def _t_draft_email(user_id: str, params: dict, inp: dict) -> dict:
    from services.llm_gateway import complete_text
    system = params.get("system", "You write short, personal cold emails.")
    prompt = params.get("user_prompt") or params.get("prompt") or ""
    ctx_leads = inp.get("leads") or []
    if ctx_leads and "{lead}" in prompt:
        prompt = prompt.replace("{lead}", json.dumps(ctx_leads[0], default=str))
    body = await complete_text(
        user_id, system, prompt, model=params.get("model", "maars/auto"),
        max_tokens=params.get("max_tokens", 800),
        temperature=params.get("temperature", 0.4),
        source="workflow.draft_email",
    )
    return {"ok": True, "body": body, "subject": params.get("subject", "Quick question")}


async def _t_send_email(user_id: str, params: dict, inp: dict) -> dict:
    from services.email_sender import send_email
    to = params.get("to") or (inp.get("leads", [{}])[0].get("email") if inp.get("leads") else None)
    if not to:
        return {"ok": False, "error": "no recipient"}
    body = params.get("body") or inp.get("body") or ""
    subject = params.get("subject") or inp.get("subject") or "Hello"
    r = await send_email(user_id=user_id, to=to, subject=subject, body=body)
    return {"ok": True, **(r or {})}


async def _t_run_campaign(user_id: str, params: dict, inp: dict) -> dict:
    from services.campaign_orchestrator import run_campaign
    r = await run_campaign(
        user_id=user_id,
        name=params.get("name", "Workflow campaign"),
        persona=params.get("persona", {}),
        subject_template=params.get("subject_template", ""),
        email_template=params.get("email_template", ""),
        lead_count=int(params.get("lead_count", 20)),
        send_window_days=int(params.get("send_window_days", 5)),
        daily_send_cap=int(params.get("daily_send_cap", 40)),
    )
    return {"ok": True, **(r or {})}


async def _t_post_social(user_id: str, params: dict, inp: dict) -> dict:
    """Unified social post. params.platform = x | linkedin | instagram |
    facebook | tiktok | youtube. Uses the new platforms registry."""
    from services.platforms import get_adapter
    platform = params.get("platform", "x").lower()
    adapter = get_adapter(platform)
    if adapter is None:
        return {"ok": False, "error": f"no adapter for platform '{platform}'"}
    text = params.get("text") or inp.get("body") or inp.get("text", "")
    media = params.get("media_urls") or inp.get("media_urls") or []
    r = await adapter.publish(user_id=user_id, text=text, media_urls=media, params=params)
    return r


async def _t_generate_image(user_id: str, params: dict, inp: dict) -> dict:
    from services.media_router import route_image
    prompt = params.get("prompt") or inp.get("prompt") or ""
    r = await route_image(
        user_id=user_id, prompt=prompt,
        size=params.get("size", "1024x1024"),
        quality=params.get("quality", "standard"),
    )
    return {"ok": True, **(r or {})}


async def _t_generate_video(user_id: str, params: dict, inp: dict) -> dict:
    from services.media_router import route_video
    prompt = params.get("prompt") or inp.get("prompt") or ""
    r = await route_video(
        user_id=user_id, prompt=prompt,
        duration=int(params.get("duration", 4)),
    )
    return {"ok": True, **(r or {})}


async def _t_enhance_prompt(user_id: str, params: dict, inp: dict) -> dict:
    from services.agents.agent_prompt_enhancer import enhance
    r = await enhance(user_id, params.get("prompt") or inp.get("prompt") or "")
    return {"ok": True, "prompt": r}


# ── Research tools (web_search + browser_*) ──────────────────────────
# Every role SOP's research step references these. Until now they
# returned `unknown_tool` because they weren't registered. Backed by:
#   web_search   → services.search_providers.search_web (Brave → DDG)
#   browser_*    → services.browser_tools (httpx + bs4 text extraction)

async def _t_web_search(user_id: str, params: dict, inp: dict) -> dict:
    """Search the web via Brave (if keyed) or DuckDuckGo fallback.

    params:
      query:     required search string
      count:     result count (default 10, max 20)
      freshness: Brave freshness filter — 'pd' (24h) | 'pw' | 'pm' | 'py'
    Returns:
      {ok, results: [{title, url, snippet, age}], query}
    """
    from services.search_providers import search_web
    query = (params.get("query") or inp.get("query") or "").strip()
    if not query:
        return {"ok": False, "error": "web_search: params.query required"}
    try:
        count = int(params.get("count", 10))
    except Exception:
        count = 10
    return await search_web(query, count=count, freshness=params.get("freshness"))


async def _t_browser_open(user_id: str, params: dict, inp: dict) -> dict:
    from services.browser_tools import browser_open
    url = (params.get("url") or inp.get("url") or "").strip()
    if not url:
        return {"ok": False, "error": "browser_open: params.url required"}
    try:
        mc = int(params.get("max_chars", 12000))
    except Exception:
        mc = 12000
    return await browser_open(url, max_chars=mc)


async def _t_browser_navigate(user_id: str, params: dict, inp: dict) -> dict:
    from services.browser_tools import browser_navigate
    url = (params.get("url") or inp.get("url") or "").strip()
    if not url:
        return {"ok": False, "error": "browser_navigate: params.url required"}
    return await browser_navigate(url, max_chars=int(params.get("max_chars", 12000)))


async def _t_browser_extract(user_id: str, params: dict, inp: dict) -> dict:
    """Fetch a URL + optionally extract text matching a CSS selector.

    params:
      url:       required
      selector:  optional CSS selector (e.g. 'h1', 'article p', '.price')
      max_chars: default 12000
    """
    from services.browser_tools import browser_extract
    url = (params.get("url") or inp.get("url") or "").strip()
    if not url:
        return {"ok": False, "error": "browser_extract: params.url required"}
    return await browser_extract(
        url,
        selector=params.get("selector"),
        max_chars=int(params.get("max_chars", 12000)),
    )


async def _t_browser_screenshot(user_id: str, params: dict, inp: dict) -> dict:
    """Text-snapshot fallback. Real pixel screenshots require the MCP
    Playwright bridge which registers richer tools that supersede this."""
    from services.browser_tools import browser_screenshot
    url = (params.get("url") or inp.get("url") or "").strip()
    if not url:
        return {"ok": False, "error": "browser_screenshot: params.url required"}
    return await browser_screenshot(url)


async def _t_generate_voiceover(user_id: str, params: dict, inp: dict) -> dict:
    """Generate premium voice-over in any supported language. Prefers
    ElevenLabs multilingual v2 (29 languages natively) when language is
    non-English; falls through to Edge TTS (free, 400+ voices) / OpenAI
    tts-1-hd per the premium chain. Audio is uploaded to storage and the
    signed URL returned.

    params:
      text:      Required. Narration content.
      language:  ISO-639 code (en, es, fr, ja, zh, ar, hi, pt, ...). Drives
                 multilingual_v2 auto-selection.
      voice:     friendly name or provider voice_id (default 'rachel').
      tier:      'premium' (default for voice-over) | 'standard'.
      filename:  Optional stored object name.
    """
    from services.media_router import route_tts
    text = (params.get("text")
            or inp.get("text")
            or inp.get("voiceover_text")
            or inp.get("script") or "")
    if not text:
        return {"ok": False, "error": "generate_voiceover: params.text required"}
    try:
        audio, meta = await route_tts(
            text=text,
            voice=params.get("voice", "rachel"),
            tier=params.get("tier", "premium"),
            language=params.get("language"),
        )
    except Exception as exc:
        return {"ok": False, "error": f"tts_failed: {exc}"}
    # Persist to storage so downstream compositor / delivery steps have a URL.
    try:
        from services.storage import upload_bytes
        fn = params.get("filename") or f"voiceover_{int(time.time())}.mp3"
        url = await upload_bytes(audio, fn, content_type="audio/mpeg",
                                 user_id=user_id)
    except Exception:
        url = None
    return {
        "ok":        True,
        "audio_url": url,
        "bytes":     len(audio),
        "provider":  meta.get("provider"),
        "model":     meta.get("model"),
        "cost_usd":  meta.get("cost_usd"),
        "credits":   meta.get("cost_credits"),
        "language":  params.get("language") or "en",
    }


async def _t_generate_tts(user_id: str, params: dict, inp: dict) -> dict:
    """Alias of generate_voiceover but defaults to standard tier (cheaper,
    Edge TTS first). Used for UI prompts, notifications, etc."""
    merged = {**(params or {}), "tier": params.get("tier", "standard")}
    return await _t_generate_voiceover(user_id, merged, inp)


async def _t_composite_video(user_id: str, params: dict, inp: dict) -> dict:
    """Stitch video clips, overlay a voice-over audio track, and optionally
    burn subtitles to a single final MP4. Backed by ffmpeg via
    services.media_compositor. Returns signed URL + duration.

    params:
      clip_urls:    list[str] in scene order. If omitted, read from
                    inp.scene_urls or inp.clips.
      audio_url:    voice-over mp3 url (from generate_voiceover step).
      subtitles:    optional list[{start_s, end_s, text}] OR .srt URL.
      aspect:       '16:9' | '9:16' | '1:1' (default 16:9).
      resolution:   '1080p' | '720p' | '4k' (default 720p).
      filename:     output object name.
    """
    from services.media_compositor import composite_video
    clip_urls = (params.get("clip_urls")
                 or inp.get("scene_urls")
                 or inp.get("clips")
                 or [])
    if not clip_urls:
        return {"ok": False, "error": "composite_video: clip_urls required"}
    try:
        result = await composite_video(
            clip_urls=clip_urls,
            audio_url=params.get("audio_url") or inp.get("audio_url"),
            subtitles=params.get("subtitles"),
            aspect=params.get("aspect", "16:9"),
            resolution=params.get("resolution", "720p"),
            filename=params.get("filename"),
            user_id=user_id,
        )
    except Exception as exc:
        return {"ok": False, "error": f"composite_failed: {exc}"}
    return {"ok": True, **result}


async def _t_wait(user_id: str, params: dict, inp: dict) -> dict:
    seconds = float(params.get("seconds", params.get("minutes", 0) * 60 + params.get("hours", 0) * 3600))
    seconds = max(0.0, min(seconds, 3600))  # hard-cap 1h per wait node
    await asyncio.sleep(seconds)
    return {"ok": True, "waited_seconds": seconds}


async def _t_webhook_out(user_id: str, params: dict, inp: dict) -> dict:
    import httpx
    url = params.get("url")
    if not url:
        return {"ok": False, "error": "url required"}
    method = (params.get("method") or "POST").upper()
    headers = params.get("headers") or {}
    payload = params.get("body") or inp
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.request(method, url, json=payload, headers=headers)
    return {"ok": 200 <= r.status_code < 300, "status": r.status_code, "response": r.text[:2000]}


async def _t_if_condition(user_id: str, params: dict, inp: dict) -> dict:
    """Evaluate a simple condition string against the previous node's
    output. Only JSON-path equality + in + exists are supported — no
    arbitrary eval."""
    left = params.get("left")
    op = params.get("op", "==")
    right = params.get("right")

    def _dig(obj, path):
        cur = obj
        for seg in (path or "").split("."):
            if isinstance(cur, dict):
                cur = cur.get(seg)
            elif isinstance(cur, list):
                try:
                    cur = cur[int(seg)]
                except (ValueError, IndexError):
                    return None
            else:
                return None
        return cur

    lv = _dig(inp, left) if isinstance(left, str) else left
    result = False
    if op == "==":
        result = lv == right
    elif op == "!=":
        result = lv != right
    elif op == "in":
        result = lv in (right or [])
    elif op == "exists":
        result = lv is not None
    elif op == ">":
        try: result = float(lv) > float(right)
        except (TypeError, ValueError): result = False
    elif op == "<":
        try: result = float(lv) < float(right)
        except (TypeError, ValueError): result = False
    return {"ok": True, "branch": "yes" if result else "no", "evaluated": result}


async def _t_switch(user_id: str, params: dict, inp: dict) -> dict:
    """Multi-way branching. Evaluate the input against an ordered list
    of cases; the first match wins, otherwise fall through to default.

    params:
      value:   "user.plan"              # JSON path (same dig() semantics as if_condition)
      cases:   [
        {"when": "enterprise", "branch": "a"},  # equals match
        {"when": "pro", "branch": "b"},
        {"op": "in", "values": ["free","starter"], "branch": "c"},
        {"op": ">", "right": 5000, "branch": "d"},
      ]
      default_branch: "z"               # when nothing matches; optional

    On the node:
      branches: {"a": [...ids], "b": [...ids], "c": [...ids], ...}

    Returns:
      {"ok": True, "branch": "a"|..., "matched_case": index_or_-1}
    """
    value_path = params.get("value")
    cases = params.get("cases") or []
    default_branch = params.get("default_branch")

    def _dig(obj, path):
        cur = obj
        for seg in (path or "").split("."):
            if isinstance(cur, dict):
                cur = cur.get(seg)
            elif isinstance(cur, list):
                try:
                    cur = cur[int(seg)]
                except (ValueError, IndexError):
                    return None
            else:
                return None
        return cur

    lv = _dig(inp, value_path) if isinstance(value_path, str) else value_path
    for i, case in enumerate(cases):
        op = case.get("op", "==")
        matched = False
        if op == "==":
            matched = lv == case.get("when")
        elif op == "!=":
            matched = lv != case.get("when")
        elif op == "in":
            matched = lv in (case.get("values") or [])
        elif op == "contains":
            matched = isinstance(lv, str) and isinstance(case.get("when"), str) and case["when"] in lv
        elif op == ">":
            try: matched = float(lv) > float(case.get("right"))
            except (TypeError, ValueError): matched = False
        elif op == "<":
            try: matched = float(lv) < float(case.get("right"))
            except (TypeError, ValueError): matched = False
        elif op == "regex":
            import re as _re
            try:
                matched = isinstance(lv, str) and bool(_re.search(case.get("pattern", ""), lv))
            except Exception:
                matched = False
        if matched:
            return {"ok": True, "branch": str(case.get("branch", f"case_{i}")), "matched_case": i, "value": lv}
    return {"ok": True, "branch": str(default_branch) if default_branch else "default",
            "matched_case": -1, "value": lv}


async def _t_ai_branch(user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    """AI-decides-the-branch. Ask a MAARS agent to pick the next branch
    based on upstream state. This is the 'better than n8n' version of
    switch — the caller supplies branch labels + a description for each,
    and the agent returns the best fit.

    params:
      branches: [
        {"label": "refund", "when_description": "Customer asks for money back"},
        {"label": "upgrade", "when_description": "Customer wants to buy more"},
        {"label": "support", "when_description": "Customer has a problem we should fix"},
      ]
      input_field: "email.body"    # JSON path into input; falls back to stringified inp
      model:       "maars/economy" # optional override; defaults to auto
      agent_id:    "agent_..."     # optional — scopes to agent's training
    Returns:
      {"ok": True, "branch": "<chosen_label>", "confidence": 0..1, "rationale": "..."}
    """
    branches = params.get("branches") or []
    if not branches or not isinstance(branches, list):
        return {"ok": False, "error": "ai_branch: params.branches is required (list of {label,when_description})"}

    def _dig(obj, path):
        cur = obj
        for seg in (path or "").split("."):
            if isinstance(cur, dict): cur = cur.get(seg)
            elif isinstance(cur, list):
                try: cur = cur[int(seg)]
                except (ValueError, IndexError): return None
            else: return None
        return cur

    field = params.get("input_field")
    text = _dig(inp, field) if isinstance(field, str) else None
    if text is None:
        import json as _json
        try: text = _json.dumps(inp)[:4000]
        except Exception: text = str(inp)[:4000]

    menu_lines = [f"- {b.get('label')}: {b.get('when_description','')}" for b in branches]
    import json as _json
    prompt = (
        "Pick exactly one label from the list below that best fits the input. "
        "Reply ONLY with a compact JSON object like "
        "{\"branch\": \"<label>\", \"confidence\": 0.0-1.0, \"rationale\": \"<one sentence>\"}.\n\n"
        f"LABELS:\n" + "\n".join(menu_lines) + f"\n\nINPUT:\n{text}\n"
    )
    from services.llm_gateway import complete_text
    # Default ai_branch routing decisions to Commander Orion — he's the
    # orchestrator, so branch picks are his authority by default. Callers
    # can override via params.agent_id when a domain specialist is better.
    from db import db as _db
    chosen_agent = params.get("agent_id")
    if not chosen_agent:
        commander = await _db.agents.find_one(
            {"agent_id": "agent_commander"}, {"agent_id": 1}
        )
        chosen_agent = commander["agent_id"] if commander else None
    raw = await complete_text(
        user_id,
        system_prompt=(
            "You are Commander Orion ∞, picking the next branch in a MAARS "
            "workflow. Reply with exactly one label that best fits the input."
            if chosen_agent == "agent_commander"
            else "You are a precise router. Pick exactly one label."
        ),
        user_prompt=prompt,
        model=params.get("model") or "maars/auto",
        max_tokens=200, temperature=0.0,
        source="workflow_ai_branch",
        agent_id=chosen_agent,
    )
    import re as _re
    m = _re.search(r"\{[\s\S]*\}", raw or "")
    try:
        decided = _json.loads(m.group(0)) if m else {}
    except Exception:
        decided = {}
    label = str(decided.get("branch") or "").strip()
    labels = [b.get("label") for b in branches]
    if label not in labels:
        # Fallback: first label, flag low confidence
        label = labels[0] if labels else "default"
        decided["confidence"] = 0.0
    return {
        "ok": True,
        "branch": label,
        "confidence": float(decided.get("confidence") or 0.5),
        "rationale": str(decided.get("rationale") or "")[:500],
        "raw": (raw or "")[:500],
    }


TOOL_REGISTRY: dict[str, Callable[..., Awaitable[dict]]] = {
    "search_leads":     _t_search_leads,
    "enrich_contact":   _t_enrich_contact,
    "draft_email":      _t_draft_email,
    "send_email":       _t_send_email,
    "send_cold_email":  _t_send_email,
    "run_campaign":     _t_run_campaign,
    "post_linkedin":    _t_post_social,    # legacy alias — routes to x/linkedin via params.platform
    "post_social":      _t_post_social,
    "schedule_post":    _t_post_social,    # scheduling handled by platform adapter if supported
    "generate_image":   _t_generate_image,
    "generate_video":   _t_generate_video,
    "generate_voiceover": _t_generate_voiceover,
    "generate_tts":     _t_generate_tts,
    "composite_video":  _t_composite_video,
    "enhance_prompt":   _t_enhance_prompt,
    # Research tools — every role SOP references these. Without them the
    # research step returned `unknown_tool` and the agent pretended to
    # research. With them wired, every SOP can actually hit the web.
    "web_search":       _t_web_search,
    "browser_open":     _t_browser_open,
    "browser_navigate": _t_browser_navigate,
    "browser_extract":  _t_browser_extract,
    "browser_screenshot": _t_browser_screenshot,
    "wait":             _t_wait,
    "webhook_out":      _t_webhook_out,
    "if_condition":     _t_if_condition,
    "switch":           _t_switch,
    "ai_branch":        _t_ai_branch,
    "agent_chat":       _t_agent_chat,
    "delegate_to_agent": _t_delegate_to_agent,
}


async def _t_integration_action(user_id: str, params: dict, inp: dict) -> dict:
    """Dispatch any connected integration action through the unified
    driver. Picks API vs browser mode based on what's wired for this
    user; caller can pin with params.prefer_mode.

    Authority gate: if params.agent_id is set, check that this agent has
    been granted authority over the provider for this user. Missing
    grant → authority_denied (operator resolves from the UI).

    params:
      provider:    "linkedin" | "x" | "instagram" | ...
      action:      provider-specific
      agent_id:    (optional) the agent claiming to act — enforces grant
      prefer_mode: "api" | "browser" | None (auto)
      ...          provider-specific kwargs (content, to, etc.)
    """
    provider = (params.get("provider") or "").strip()
    action = (params.get("action") or "").strip()
    if not (provider and action):
        return {"ok": False, "error": "provider + action required"}

    # Authority check — only enforced when agent_id is supplied. Direct
    # operator calls (no agent_id) bypass; they're already authenticated.
    agent_id = (params.get("agent_id") or "").strip()
    if agent_id:
        from db import db
        grant = await db.integration_authority.find_one(
            {"user_id": user_id, "agent_id": agent_id},
            {"_id": 0, "providers": 1, "actions": 1, "expires_at": 1},
        )
        if not grant:
            return {"ok": False, "error": "authority_denied",
                    "hint": f"agent '{agent_id}' has no grant. Open Integration Hub → Authority and add '{provider}'."}
        if provider not in (grant.get("providers") or []):
            return {"ok": False, "error": "authority_denied",
                    "hint": f"agent '{agent_id}' not granted access to '{provider}'. "
                            f"Granted: {grant.get('providers')}"}
        allowed_actions = grant.get("actions")
        if allowed_actions and action not in allowed_actions:
            return {"ok": False, "error": "authority_denied",
                    "hint": f"action '{action}' not in grant's allowed actions: {allowed_actions}"}
        import time as _t
        if grant.get("expires_at") and _t.time() > float(grant["expires_at"]):
            return {"ok": False, "error": "authority_expired",
                    "hint": "Regrant authority from the Integration Hub."}

    from services import integration_driver
    forward = {k: v for k, v in (params or {}).items()
               if k not in ("provider", "action", "prefer_mode", "agent_id")}
    return await integration_driver.act(
        provider=provider, action=action, params=forward,
        user_id=user_id, prefer_mode=params.get("prefer_mode"),
    )


TOOL_REGISTRY["integration_action"] = _t_integration_action


async def _t_evaluator(user_id: str, params: dict, inp: dict) -> dict:
    """Relevance filter for retrieved chunks. Cheap-model pass that drops
    noise before the expensive synthesis step — pattern from
    context-engineering-workflow + paralegal-agent-crew.

    params:
      items:     JSON path into inp to a list of {text|content, ...} dicts
                 OR a direct list
      query:     What the downstream step is trying to answer
      min_score: 0-1; chunks below are dropped (default 0.5)
      keep_top:  Optional hard cap on kept items
      model:     Override (default: cheap tier)
    Returns:
      {ok, kept: [...items with relevance_score], dropped_count, query}
    """
    # Resolve items (accept either a JSON-path string or a literal list)
    items_param = params.get("items")
    if isinstance(items_param, str):
        # Dig into inp using dot notation
        cur: Any = inp
        for seg in items_param.split("."):
            if isinstance(cur, dict):
                cur = cur.get(seg)
            else:
                cur = None
                break
        items = cur if isinstance(cur, list) else []
    elif isinstance(items_param, list):
        items = items_param
    else:
        items = inp.get("items") if isinstance(inp, dict) else []
    if not isinstance(items, list):
        return {"ok": False, "error": "items must resolve to a list"}

    query = (params.get("query") or "").strip()
    if not query:
        return {"ok": False, "error": "query required"}
    min_score = float(params.get("min_score", 0.5))
    keep_top = params.get("keep_top")
    model = params.get("model") or "maars/auto"

    # One cheap classifier call per chunk. Batch across chunks in a single
    # prompt to cut token cost.
    import json as _json, re as _re
    stub_items = []
    for i, it in enumerate(items[:40]):  # hard cap to protect context
        text = ""
        if isinstance(it, dict):
            text = str(it.get("text") or it.get("content") or it.get("body") or "")[:600]
        else:
            text = str(it)[:600]
        stub_items.append({"i": i, "text": text})
    if not stub_items:
        return {"ok": True, "kept": [], "dropped_count": 0, "query": query}

    from services.llm_gateway import complete_text
    prompt = (
        f"For each chunk, score its relevance to the query from 0.0 to 1.0.\n"
        f"QUERY: {query}\n\n"
        f"CHUNKS:\n{_json.dumps(stub_items)[:6000]}\n\n"
        'Reply ONLY with JSON: {"scores": {"<i>": 0.0-1.0, ...}}. '
        "No prose."
    )
    try:
        raw = await complete_text(
            user_id,
            system_prompt="You are a terse relevance classifier. Output strict JSON only.",
            user_prompt=prompt,
            model=model,
            max_tokens=400, temperature=0.0,
            source="workflow.evaluator",
            enable_cache=True,
        )
    except Exception as exc:
        return {"ok": False, "error": f"classifier_failed: {exc}"}

    m = _re.search(r"\{[\s\S]*\}", raw or "")
    try:
        parsed = _json.loads(m.group(0)) if m else {}
    except Exception:
        parsed = {}
    scores = parsed.get("scores") or {}
    kept: list = []
    for i, it in enumerate(items):
        if i >= 40:
            # Preserve overflow without a score (assume relevant)
            kept.append({"item": it, "relevance_score": None, "reason": "beyond_eval_window"})
            continue
        try:
            sc = max(0.0, min(1.0, float(scores.get(str(i), 0.0))))
        except (TypeError, ValueError):
            sc = 0.0
        if sc >= min_score:
            if isinstance(it, dict):
                kept.append({**it, "relevance_score": round(sc, 3)})
            else:
                kept.append({"item": it, "relevance_score": round(sc, 3)})
    # Sort by score desc so synthesis sees best context first
    kept.sort(key=lambda x: x.get("relevance_score") or 0.0, reverse=True)
    if keep_top:
        try:
            kept = kept[: max(1, int(keep_top))]
        except Exception:
            pass
    return {
        "ok":             True,
        "kept":           kept,
        "dropped_count":  max(0, len(items) - len(kept)),
        "total_evaluated": min(40, len(items)),
        "query":          query,
    }


TOOL_REGISTRY["evaluator"] = _t_evaluator


# Pull in the expanded n8n-parity toolset from workflow_tools.py.
# Imported lazily so any issue there doesn't break the executor core.
try:
    from services.workflows.workflow_tools import PHASE1_TOOLS, PHASE2_TOOLS
    TOOL_REGISTRY.update(PHASE1_TOOLS)
    TOOL_REGISTRY.update(PHASE2_TOOLS)
except Exception as _tools_exc:
    logger.warning("workflow_tools import failed: %s", _tools_exc)

try:
    from services.workflows.workflow_services import CONTROL_TOOLS, SERVICE_TOOLS
    TOOL_REGISTRY.update(CONTROL_TOOLS)
    TOOL_REGISTRY.update(SERVICE_TOOLS)
except Exception as _svc_exc:
    logger.warning("workflow_services import failed: %s", _svc_exc)


# ── Walker ───────────────────────────────────────────────────────────

async def _invoke_with_ctx(fn, user_id: str, params: dict, inp: dict, ctx: dict):
    """Call a tool regardless of whether its signature is the old
    (user_id, params, inp) or new (user_id, params, inp, ctx)."""
    import inspect
    sig = inspect.signature(fn)
    if len(sig.parameters) >= 4:
        return await fn(user_id, params, inp, ctx)
    return await fn(user_id, params, inp)


async def _fire_one_node(
    run_id: str, user_id: str, node: dict, prev_output: dict, ctx: dict,
) -> tuple[bool, dict]:
    """Run a single node with retry + timeout. Returns (ok, output).

    Expression resolution: node.params is walked before each attempt so
    `{{n1.field}}` templates resolve against the latest state.
    """
    from services import expressions as _ex
    tool = node.get("tool")
    node_id = node.get("id", "?")
    raw_params = node.get("params") or {}

    if node.get("type") == "trigger":
        return True, {"ok": True, "trigger": node.get("trigger", {})}

    fn = TOOL_REGISTRY.get(tool)
    if fn is None:
        return False, {"ok": False, "error": f"unknown tool '{tool}'"}

    timeout = float(raw_params.get("timeout_ms", DEFAULT_TIMEOUT_MS)) / 1000
    retries = int(raw_params.get("retries", DEFAULT_RETRIES))
    backoff = INITIAL_BACKOFF
    last_err: str = ""

    for attempt in range(1, retries + 1):
        # Resolve templated params against current ctx (state may have
        # changed since last attempt — e.g. a sibling branch finished).
        params = _ex.resolve(raw_params, ctx)
        await _publish(run_id, {
            "event": "node_start", "node_id": node_id, "tool": tool, "attempt": attempt,
        })
        start = time.time()
        try:
            output = await asyncio.wait_for(
                _invoke_with_ctx(fn, user_id, params, prev_output, ctx),
                timeout=timeout,
            )
            latency_ms = int((time.time() - start) * 1000)
            if not isinstance(output, dict):
                output = {"ok": True, "value": output}
            output.setdefault("ok", True)
            await _publish(run_id, {
                "event": "node_done", "node_id": node_id, "tool": tool,
                "attempt": attempt, "latency_ms": latency_ms, "ok": output.get("ok"),
            })
            return output.get("ok", True), output
        except asyncio.TimeoutError:
            last_err = f"timeout after {timeout}s"
        except Exception as exc:
            last_err = f"{type(exc).__name__}: {exc}"

        await _publish(run_id, {
            "event": "node_retry", "node_id": node_id, "tool": tool,
            "attempt": attempt, "error": last_err, "backoff_s": backoff,
        })
        await asyncio.sleep(backoff)
        backoff = min(backoff * 2, 30)

    await _publish(run_id, {
        "event": "node_failed", "node_id": node_id, "tool": tool, "error": last_err,
    })
    return False, {"ok": False, "error": last_err}


def _all_branch_targets(n: dict) -> list[str]:
    """Every downstream id reachable from any branch label on this node.
    Used by root + in-degree calculations to include switch / ai_branch
    alongside the legacy branch_yes / branch_no."""
    out: list[str] = []
    for t in (n.get("next") or []):
        out.append(t)
    for t in (n.get("branch_yes") or []):
        out.append(t)
    for t in (n.get("branch_no") or []):
        out.append(t)
    for _label, targets in (n.get("branches") or {}).items():
        for t in (targets or []):
            out.append(t)
    return out


def _roots(nodes: list[dict]) -> list[dict]:
    """A node is a root if no other node lists it as downstream."""
    incoming: set[str] = set()
    for n in nodes:
        for t in _all_branch_targets(n):
            incoming.add(t)
    return [n for n in nodes if n["id"] not in incoming]


def _by_id(nodes: list[dict]) -> dict[str, dict]:
    return {n["id"]: n for n in nodes}


def _incoming_counts(nodes: list[dict]) -> dict[str, int]:
    """Count in-degrees per node. A merge node waits for all parents."""
    counts: dict[str, int] = {n["id"]: 0 for n in nodes}
    for n in nodes:
        for t in _all_branch_targets(n):
            if t in counts: counts[t] += 1
    return counts


async def run(
    run_id: str,
    workflow: dict,
    overrides: dict | None = None,
    *,
    max_nodes: int = 500,
    trigger_meta: dict | None = None,
    _in_error_handler: bool = False,
) -> dict:
    """Walk the DAG with PARALLEL independent-branch execution.

    Two-queue scheduler: a ready-set of node ids whose deps have
    satisfied, an in-flight set of asyncio tasks. Dispatch all ready
    nodes concurrently, await on FIRST_COMPLETED, process their outputs
    to unlock downstream deps, loop. This runs sibling branches in
    parallel the way n8n does.

    Error workflow: if workflow.on_error_workflow_id is set AND this
    isn't already an error handler run, a failure triggers that
    workflow with `failed_run`, `failed_node`, and `error` passed as
    overrides.
    """
    from db import db
    from services import expressions as _ex

    user_id = workflow.get("user_id")
    nodes = workflow.get("nodes") or []
    by_id = _by_id(nodes)
    roots = _roots(nodes)
    if not roots:
        roots = nodes[:1]

    in_degree = _incoming_counts(nodes)
    # For branching nodes (if_condition) parents only decrement one side —
    # we lazily fix in-degree when the branch resolves.

    await db.workflow_runs.update_one(
        {"run_id": run_id},
        {"$set": {"status": "running", "started_at": datetime.now(timezone.utc).isoformat()}},
    )
    await _publish(run_id, {"event": "run_start", "workflow_id": workflow.get("workflow_id")})

    # Pre-load workflow env vars once per run so {{$env.X}} resolves
    # without a DB roundtrip per node.
    env_map: dict[str, Any] = {}
    try:
        from db import db
        async for doc in db.workflow_env.find({
            "$or": [
                {"scope": "user", "scope_id": user_id},
                {"scope": "system", "scope_id": "global"},
            ]
        }):
            env_map.setdefault(doc["key"], doc.get("value"))
    except Exception:
        pass

    state: dict[str, dict] = {}
    prev_output_for: dict[str, dict] = {r["id"]: dict(overrides or {}) for r in roots}
    remaining_in: dict[str, int] = {**in_degree}
    ready: set[str] = {r["id"] for r in roots}
    fired = 0
    hard_fail = False
    first_fail: tuple[str, str] | None = None   # (node_id, error)
    inflight: dict[asyncio.Task, str] = {}
    max_parallel = int(workflow.get("max_parallel", 8))

    def _ctx_for(prev: dict) -> dict:
        return _ex.build_context(
            workflow=workflow, run_id=run_id, state=state,
            trigger_meta=trigger_meta, prev_output=prev, env=env_map,
        )

    while (ready or inflight) and fired < max_nodes:
        # Dispatch up to max_parallel from ready.
        while ready and len(inflight) < max_parallel and fired < max_nodes:
            node_id = ready.pop()
            node = by_id.get(node_id)
            if node is None:
                continue
            fired += 1
            prev = prev_output_for.pop(node_id, {})
            ctx = _ctx_for(prev)

            # Design-time: if this node has a pinned output and the run
            # was kicked in "design" mode, short-circuit to the pin.
            # Replay runs pass pins via overrides.__replay_pins so one
            # failed production run can be resumed without editing the
            # saved workflow spec.
            _replay_pins = (overrides or {}).get("__replay_pins") or {}
            _wf_pins = workflow.get("pinned_outputs") or {}
            pinned = None
            if _replay_pins.get(node_id) is not None:
                pinned = _replay_pins[node_id]
            elif (overrides or {}).get("__design_mode") and _wf_pins.get(node_id) is not None:
                pinned = _wf_pins[node_id]
            if pinned is not None:
                async def _pinned_echo(_a=pinned):
                    return True, dict(_a)
                task = asyncio.create_task(_pinned_echo())
            else:
                task = asyncio.create_task(_fire_one_node(run_id, user_id, node, prev, ctx))
            inflight[task] = node_id

        if not inflight:
            break
        done, _ = await asyncio.wait(inflight.keys(), return_when=asyncio.FIRST_COMPLETED)
        for task in done:
            node_id = inflight.pop(task)
            node = by_id.get(node_id, {})
            try:
                ok, output = task.result()
            except Exception as exc:
                ok, output = False, {"ok": False, "error": str(exc)[:400]}
            state[node_id] = output
            try:
                await db.workflow_run_events.insert_one({
                    "run_id": run_id, "node_id": node_id, "tool": node.get("tool"),
                    "ok": ok, "output": output,
                    "ts": datetime.now(timezone.utc).isoformat(),
                })
            except Exception:
                pass

            if not ok:
                # Per-node `on_failure` branch routes failure to an
                # alternate node instead of halting — n8n's "Error"
                # output on a node.
                on_fail = node.get("on_failure") or []
                if on_fail:
                    for nid in on_fail:
                        if nid in remaining_in:
                            # Route there regardless of in-degree since
                            # it's the error path.
                            remaining_in[nid] = 0
                            prev_output_for[nid] = output
                            ready.add(nid)
                    # don't halt — treat failure as handled
                    continue
                # Respect per-node continue_on_error so one failure doesn't halt the world
                if not (node.get("params") or {}).get("continue_on_error"):
                    if not hard_fail:
                        hard_fail = True
                        first_fail = (node_id, str(output.get("error", "")))
                    # cancel still-running siblings
                    for t in list(inflight.keys()):
                        t.cancel()
                    inflight.clear()
                    ready.clear()
                    break

            # Unlock downstream deps.
            tool = node.get("tool")
            if tool == "if_condition":
                branch = output.get("branch", "no")
                taken = (node.get("branch_yes") or []) if branch == "yes" else (node.get("branch_no") or [])
                # Decrement in-degree for the NOT-taken branch too so
                # downstream nodes don't wait forever.
                not_taken = (node.get("branch_no") or []) if branch == "yes" else (node.get("branch_yes") or [])
                for nid in not_taken:
                    if nid in remaining_in and remaining_in[nid] > 0:
                        remaining_in[nid] = max(0, remaining_in[nid] - 1)
                next_ids = taken
            elif tool in ("switch", "ai_branch"):
                # N-way: take exactly one branch label from node.branches,
                # drop the in-degree on every other label's targets.
                chosen_label = str(output.get("branch") or "")
                branches_map = node.get("branches") or {}
                taken = list(branches_map.get(chosen_label) or [])
                for label, targets in branches_map.items():
                    if label == chosen_label:
                        continue
                    for nid in (targets or []):
                        if nid in remaining_in and remaining_in[nid] > 0:
                            remaining_in[nid] = max(0, remaining_in[nid] - 1)
                # Also support a plain `next` alongside branches — always fires.
                next_ids = taken + list(node.get("next") or [])
            else:
                next_ids = node.get("next") or []
            for nid in next_ids:
                if nid not in remaining_in:
                    continue
                remaining_in[nid] = max(0, remaining_in[nid] - 1)
                # For nodes whose node.type=="merge" we WAIT for all parents.
                target = by_id.get(nid, {})
                need_all = target.get("type") == "merge" or (target.get("tool") == "merge")
                prev_output_for[nid] = output  # latest parent output becomes prev by default
                if need_all:
                    if remaining_in[nid] == 0:
                        ready.add(nid)
                else:
                    ready.add(nid)

    status = "failed" if hard_fail else ("completed" if fired <= max_nodes else "cutoff")
    final = {
        "run_id": run_id, "status": status, "nodes_fired": fired,
        "state": state,
    }
    if first_fail:
        final["failed_node"] = first_fail[0]
        final["error"] = first_fail[1]

    await db.workflow_runs.update_one(
        {"run_id": run_id},
        {"$set": {
            "status": status,
            "finished_at": datetime.now(timezone.utc).isoformat(),
            "nodes_fired": fired,
            "state": state,
            **({"failed_node": first_fail[0], "error": first_fail[1]} if first_fail else {}),
        }},
    )
    await _publish(run_id, {"event": "run_end", **final})

    # Error workflow binding — fires if the main flow failed.
    if hard_fail and not _in_error_handler:
        eid = workflow.get("on_error_workflow_id")
        if eid:
            try:
                err_wf = await db.workflows.find_one({"workflow_id": eid})
                if err_wf:
                    err_run_id = await _enqueue_run(
                        err_wf,
                        trigger_meta={"source": "on_error", "parent_run": run_id,
                                      "failed_workflow": workflow.get("workflow_id")},
                        overrides={
                            "failed_run": run_id,
                            "failed_workflow": workflow.get("workflow_id"),
                            "failed_node": first_fail[0] if first_fail else None,
                            "error": first_fail[1] if first_fail else None,
                            "state": state,
                        },
                    )
                    asyncio.create_task(run(
                        err_run_id, err_wf, overrides={"failed_run": run_id},
                        trigger_meta={"source": "on_error"},
                        _in_error_handler=True,
                    ))
                    final["on_error_run_id"] = err_run_id
            except Exception as exc:
                logger.warning("on_error workflow dispatch failed: %s", exc)

    return final


# ── Trigger dispatch ─────────────────────────────────────────────────
# The workflow schema declares four trigger types:
#   manual        — POST /workflows/{id}/run (already wired)
#   scheduled     — periodic, based on workflow.trigger.{cron | interval_minutes | interval_hours}
#   webhook       — external POST to /api/webhooks/workflow/{id} (see routes/webhooks_in.py)
#   email_reply   — fires from email_events webhook when an inbound reply matches a filter
# This section adds the first-class enqueue + scheduled-polling pieces.


async def _enqueue_run(
    workflow: dict,
    *,
    trigger_meta: dict | None = None,
    overrides: dict | None = None,
) -> str:
    """Create a queued run row. Scheduler's `_workflow_tick` picks it up."""
    from db import db
    import uuid as _uuid
    run_id = f"wfrun_{_uuid.uuid4().hex[:12]}"
    await db.workflow_runs.insert_one({
        "run_id":      run_id,
        "workflow_id": workflow.get("workflow_id"),
        "user_id":     workflow.get("user_id"),
        "status":      "queued",
        "trigger":     trigger_meta or {},
        "overrides":   overrides or {},
        "started_at":  datetime.now(timezone.utc).isoformat(),
    })
    await db.workflows.update_one(
        {"workflow_id": workflow.get("workflow_id")},
        {"$inc": {"run_count": 1},
         "$set": {"last_run_at": datetime.now(timezone.utc).isoformat()}},
    )
    return run_id


async def replay_run(
    original_run_id: str,
    *,
    resume_from_node_id: str | None = None,
    override_outputs: dict | None = None,
) -> str:
    """Kick a new run seeded with the original run's state.

    If `resume_from_node_id` is provided, the new run pins every
    upstream node's output (so the executor short-circuits them) and
    re-executes from that node forward. If omitted, the whole workflow
    re-runs with the same trigger payload — useful for transient
    failures (network glitches, rate-limit).

    `override_outputs` is an optional dict {node_id: new_output}
    layered on top of the original state so operators can fix a bad
    upstream output and see the flow proceed. Pairs with the AI-
    diagnose output — operator approves the proposed fix, we patch it
    here, replay from the fix point.
    """
    from db import db
    original = await db.workflow_runs.find_one({"run_id": original_run_id}, {"_id": 0})
    if not original:
        raise ValueError("original_run_not_found")
    workflow = await db.workflows.find_one({"workflow_id": original["workflow_id"]}, {"_id": 0})
    if not workflow:
        raise ValueError("workflow_not_found")
    state = dict(original.get("state") or {})
    if override_outputs:
        state.update(override_outputs)

    # Build pinned_outputs for every node BEFORE the resume point.
    pinned: dict[str, dict] = {}
    if resume_from_node_id:
        # Walk upstream of the target — pin every ancestor so it short-circuits.
        nodes = workflow.get("nodes") or []
        by_id = {n["id"]: n for n in nodes}
        parents: dict[str, set[str]] = {n["id"]: set() for n in nodes}
        for n in nodes:
            for t in _all_branch_targets(n):
                if t in parents: parents[t].add(n["id"])
        seen: set[str] = set()
        stack = list(parents.get(resume_from_node_id, set()))
        while stack:
            nid = stack.pop()
            if nid in seen: continue
            seen.add(nid)
            stack.extend(parents.get(nid, set()))
        for nid in seen:
            if nid in state:
                pinned[nid] = state[nid]

    trigger_meta = {
        "source": "replay",
        "original_run_id": original_run_id,
        "resume_from": resume_from_node_id,
    }
    overrides = dict(original.get("overrides") or {})
    overrides["__design_mode"] = True if pinned else overrides.get("__design_mode", False)
    # Stash pinned outputs on a transient copy of the workflow so the
    # executor's pin-lookup path fires without mutating the saved spec.
    if pinned:
        wf_copy = dict(workflow)
        wf_copy["pinned_outputs"] = {**(workflow.get("pinned_outputs") or {}), **pinned}
        # Save a short-lived replay snapshot; scheduler loads by workflow_id,
        # so we attach the pins to overrides and merge at run time.
        overrides["__replay_pins"] = pinned
    run_id = await _enqueue_run(workflow, trigger_meta=trigger_meta, overrides=overrides)
    return run_id


def _next_due_from_trigger(trig: dict, last_run_at: str | None) -> float | None:
    """Compute the next-due epoch for a scheduled trigger. Returns None if
    the trigger has no valid schedule."""
    import time as _t
    now = _t.time()

    interval_s: float | None = None
    if isinstance(trig.get("interval_minutes"), (int, float)) and trig["interval_minutes"] > 0:
        interval_s = float(trig["interval_minutes"]) * 60
    elif isinstance(trig.get("interval_hours"), (int, float)) and trig["interval_hours"] > 0:
        interval_s = float(trig["interval_hours"]) * 3600
    elif isinstance(trig.get("interval_seconds"), (int, float)) and trig["interval_seconds"] > 0:
        interval_s = max(30.0, float(trig["interval_seconds"]))   # min 30s

    if interval_s is None:
        # cron support — parse if `croniter` is installed; otherwise skip.
        cron_expr = trig.get("cron")
        if cron_expr:
            try:
                from croniter import croniter
                from datetime import datetime as _dt
                base = _dt.fromtimestamp(now)
                return croniter(cron_expr, base).get_next(float)
            except ImportError:
                logger.info(
                    "scheduled workflow uses cron but `croniter` isn't installed — skipping"
                )
                return None
            except Exception as exc:
                logger.info("bad cron expr '%s': %s", cron_expr, exc)
                return None
        return None

    if not last_run_at:
        return now + interval_s   # first-run after one interval to avoid instant-fire on creation
    try:
        from datetime import datetime as _dt
        last_ts = _dt.fromisoformat(last_run_at.replace("Z", "+00:00")).timestamp()
    except Exception:
        return now + interval_s
    return last_ts + interval_s


async def trigger_scheduled_workflows() -> int:
    """Scheduler tick: fire any active `scheduled` workflow whose next-due
    time has passed. Returns count of workflows enqueued.

    Wired into services.scheduler:start_scheduler as `_trigger_scheduled`.
    """
    import time as _t
    from db import db

    now = _t.time()
    fired = 0
    cursor = db.workflows.find(
        {"active": True, "trigger.type": "scheduled"},
    )
    async for wf in cursor:
        trig = wf.get("trigger") or {}
        due_at = _next_due_from_trigger(trig, wf.get("last_run_at"))
        if due_at is None:
            continue
        if due_at <= now:
            try:
                await _enqueue_run(wf, trigger_meta={"source": "scheduled", "due_at": due_at})
                fired += 1
            except Exception as exc:
                logger.warning("scheduled enqueue failed for %s: %s", wf.get("workflow_id"), exc)
    return fired


async def trigger_webhook(
    workflow_id: str,
    *,
    payload: dict | None = None,
    signing_ok: bool = True,
) -> dict:
    """External webhook → workflow. Called from routes/webhooks_in.py.

    Returns {ok, run_id | error}. Signing verification is done in the route
    layer (HMAC of the payload against workflow.trigger.signing_secret).
    """
    from db import db
    wf = await db.workflows.find_one({"workflow_id": workflow_id, "active": True})
    if not wf:
        return {"ok": False, "error": "workflow not found or inactive"}
    if (wf.get("trigger") or {}).get("type") != "webhook":
        return {"ok": False, "error": "workflow trigger type is not 'webhook'"}
    if not signing_ok:
        return {"ok": False, "error": "signature mismatch"}
    run_id = await _enqueue_run(
        wf,
        trigger_meta={"source": "webhook"},
        overrides={"webhook_payload": payload or {}},
    )
    return {"ok": True, "run_id": run_id}


async def trigger_email_reply(
    *,
    user_id: str,
    from_email: str,
    subject: str,
    body: str,
    message_id: str | None = None,
) -> list[str]:
    """Email events pipeline calls this on every inbound reply. Any active
    `email_reply` workflow whose filters match is enqueued.

    Filter schema on `trigger`:
      {"type":"email_reply", "from_contains":"...", "subject_contains":"...",
       "body_contains":"..."}
    An empty filter = match every reply for this user.

    Returns list of run_ids that were enqueued.
    """
    from db import db
    run_ids: list[str] = []
    cursor = db.workflows.find({
        "active": True, "user_id": user_id, "trigger.type": "email_reply",
    })
    fe = (from_email or "").lower()
    subj = (subject or "").lower()
    body_l = (body or "").lower()
    async for wf in cursor:
        trig = wf.get("trigger") or {}
        if (s := trig.get("from_contains")) and s.lower() not in fe:
            continue
        if (s := trig.get("subject_contains")) and s.lower() not in subj:
            continue
        if (s := trig.get("body_contains")) and s.lower() not in body_l:
            continue
        try:
            rid = await _enqueue_run(wf, trigger_meta={
                "source": "email_reply", "from": from_email,
                "subject": subject, "message_id": message_id,
            }, overrides={
                "email_from": from_email, "email_subject": subject,
                "email_body": body, "email_message_id": message_id,
            })
            run_ids.append(rid)
        except Exception as exc:
            logger.warning("email_reply enqueue failed for %s: %s", wf.get("workflow_id"), exc)
    return run_ids


# ── Scheduler integration ────────────────────────────────────────────
_inflight: set[str] = set()


async def pick_and_run_queued(*, max_concurrent: int = 4) -> int:
    """Scheduler tick: pick up to max_concurrent queued runs, execute
    them in the background, return how many we started."""
    from db import db
    if len(_inflight) >= max_concurrent:
        return 0
    to_start = max_concurrent - len(_inflight)
    queued = await db.workflow_runs.find(
        {"status": "queued"},
    ).sort("started_at", 1).limit(to_start).to_list(to_start)

    started = 0
    for row in queued:
        run_id = row["run_id"]
        workflow_id = row["workflow_id"]
        overrides = row.get("overrides") or {}
        wf = await db.workflows.find_one({"workflow_id": workflow_id})
        if not wf:
            await db.workflow_runs.update_one(
                {"run_id": run_id},
                {"$set": {"status": "failed", "error": "workflow_not_found"}},
            )
            continue
        _inflight.add(run_id)

        async def _go(rid=run_id, wfdoc=wf, ov=overrides):
            try:
                await run(rid, wfdoc, overrides=ov)
            except Exception as exc:
                logger.warning("workflow %s crashed: %s", rid, exc)
                try:
                    await db.workflow_runs.update_one(
                        {"run_id": rid},
                        {"$set": {"status": "failed", "error": str(exc)[:500]}},
                    )
                except Exception:
                    pass
            finally:
                _inflight.discard(rid)

        asyncio.create_task(_go())
        started += 1
    return started
