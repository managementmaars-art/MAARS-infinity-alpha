"""MAARS MCP server implementation.

Dual transport:
  • stdio      — for Claude Desktop (local command)
  • HTTP + SSE — for Cursor / web clients (runs on MCP_PORT)

Auth: incoming clients send `MAARS_MCP_TOKEN=<key>` which maps to a MAARS
user_id. The server stores (token → user_id) in db.mcp_tokens so every
tool call executes under the right wallet/agent context.

Usage:
    python -m mcp_server          # stdio
    MCP_PORT=8900 python -m mcp_server --sse   # HTTP/SSE
"""
from __future__ import annotations
import asyncio
import json
import logging
import os
import sys
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

logger = logging.getLogger(__name__)

# Globals resolved at handler time (lazy so the module imports cheap)
_server = Server("maars-command")


# ── Token → user_id resolution ──────────────────────────────────────

async def _resolve_user(token: str | None) -> str | None:
    if not token:
        return os.environ.get("MAARS_MCP_DEFAULT_USER_ID")  # optional dev fallback
    from db import db
    doc = await db.mcp_tokens.find_one({"token": token}, {"user_id": 1})
    return (doc or {}).get("user_id") if doc else None


# ── Tool registrations ──────────────────────────────────────────────

@_server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="maars.chat",
            description=(
                "Send a chat completion through MAARS Universal Gateway. Routes to "
                "the cheapest capable provider across 22 LLMs; applies wallet + "
                "skill cache + budget + audit log."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "messages": {"type": "array", "items": {"type": "object"}},
                    "model":    {"type": "string", "default": "maars/auto"},
                    "temperature": {"type": "number"},
                    "max_tokens":  {"type": "integer"},
                    "agent_id":    {"type": "string", "description": "optional: route through a specific MAARS agent"},
                },
                "required": ["messages"],
            },
        ),
        Tool(
            name="maars.agent_chat",
            description="Invoke a specific MAARS agent by agent_id with a prompt.",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_id": {"type": "string"},
                    "prompt":   {"type": "string"},
                },
                "required": ["agent_id", "prompt"],
            },
        ),
        Tool(
            name="maars.list_agents",
            description="List available MAARS agents with role + network + capabilities.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "default": 50},
                    "role_contains": {"type": "string"},
                },
            },
        ),
        Tool(
            name="maars.image",
            description="Generate an image via MAARS media router (SDXL / DALL-E / Replicate).",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {"type": "string"},
                    "size":   {"type": "string", "default": "1024x1024"},
                    "quality":{"type": "string", "default": "standard"},
                },
                "required": ["prompt"],
            },
        ),
        Tool(
            name="maars.video",
            description="Generate a video via MAARS media router (Sora / Runway / Pika).",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt":     {"type": "string"},
                    "duration_s": {"type": "integer", "default": 4},
                },
                "required": ["prompt"],
            },
        ),
        Tool(
            name="maars.tts",
            description="Text-to-speech via ElevenLabs / OpenAI TTS.",
            inputSchema={
                "type": "object",
                "properties": {
                    "text":  {"type": "string"},
                    "voice": {"type": "string", "default": "alloy"},
                },
                "required": ["text"],
            },
        ),
        Tool(
            name="maars.web_search",
            description="Live web search (used for corrective-RAG fallback).",
            inputSchema={
                "type": "object",
                "properties": {
                    "query":   {"type": "string"},
                    "top_k":   {"type": "integer", "default": 5},
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="maars.list_integrations",
            description=(
                "Per-integration readiness for the authenticated user. Shows API "
                "and browser mode availability for LinkedIn/X/Instagram/TikTok/"
                "YouTube/Facebook/WhatsApp/Slack/Discord/Telegram."
            ),
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="maars.integration_act",
            description=(
                "Execute an action on any connected integration. Example: "
                "{provider:'linkedin', action:'post', content:'Launch day!'}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "provider":    {"type": "string"},
                    "action":      {"type": "string"},
                    "params":      {"type": "object"},
                    "prefer_mode": {"type": "string", "enum": ["api", "browser"]},
                },
                "required": ["provider", "action"],
            },
        ),
        Tool(
            name="maars.run_workflow",
            description="Kick a saved MAARS workflow by workflow_id.",
            inputSchema={
                "type": "object",
                "properties": {
                    "workflow_id": {"type": "string"},
                    "overrides":   {"type": "object"},
                },
                "required": ["workflow_id"],
            },
        ),
        Tool(
            name="maars.commander_orchestrate",
            description=(
                "Commander Orion takes a goal in natural language and "
                "plans + saves + runs a workflow end-to-end. Returns the run_id "
                "so the caller can follow execution."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "goal":      {"type": "string"},
                    "auto_run":  {"type": "boolean", "default": True},
                },
                "required": ["goal"],
            },
        ),
    ]


@_server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Central dispatch. Every tool resolves user_id from the token
    attached to this session (set by the stdio/SSE wrappers)."""
    token = os.environ.get("MAARS_MCP_TOKEN") or arguments.get("_token")
    user_id = await _resolve_user(token)
    if not user_id:
        return [TextContent(type="text", text=json.dumps({
            "ok": False, "error": "auth_required: set MAARS_MCP_TOKEN"}))]

    try:
        result = await _dispatch(name, arguments, user_id)
    except Exception as exc:
        logger.exception("mcp tool %s failed", name)
        result = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
    return [TextContent(type="text", text=json.dumps(result, default=str))]


# ── Per-tool implementations ────────────────────────────────────────

async def _dispatch(name: str, args: dict, user_id: str) -> dict:
    if name == "maars.chat":
        from services.llm_gateway import complete
        return await complete(
            user_id,
            messages=args.get("messages") or [],
            model=args.get("model") or "maars/auto",
            temperature=args.get("temperature"),
            max_tokens=args.get("max_tokens"),
            agent_id=args.get("agent_id"),
            source="mcp.chat",
        )

    if name == "maars.agent_chat":
        from services.llm_gateway import complete_text
        from db import db
        agent_id = args["agent_id"]
        agent = await db.agents.find_one({"agent_id": agent_id}, {"_id": 0, "system_prompt": 1, "name": 1})
        if not agent:
            return {"ok": False, "error": f"unknown_agent: {agent_id}"}
        reply = await complete_text(
            user_id,
            system_prompt=agent.get("system_prompt") or "",
            user_prompt=args["prompt"],
            source=f"mcp.agent_chat:{agent_id}",
            agent_id=agent_id,
        )
        return {"ok": True, "agent_id": agent_id, "agent_name": agent.get("name"), "output": reply}

    if name == "maars.list_agents":
        from db import db
        q: dict[str, Any] = {"lifecycle_state": {"$ne": "retired"}}
        if args.get("role_contains"):
            q["role"] = {"$regex": args["role_contains"], "$options": "i"}
        cursor = db.agents.find(q, {
            "_id": 0, "agent_id": 1, "name": 1, "role": 1,
            "network": 1, "capabilities": 1,
        }).limit(max(1, min(int(args.get("limit", 50)), 500)))
        agents = await cursor.to_list(length=None)
        return {"ok": True, "count": len(agents), "agents": agents}

    if name == "maars.image":
        from services.media_router import generate_image
        return await generate_image(
            user_id=user_id,
            prompt=args["prompt"],
            size=args.get("size", "1024x1024"),
            quality=args.get("quality", "standard"),
        )

    if name == "maars.video":
        from services.media_router import generate_video
        return await generate_video(
            user_id=user_id,
            prompt=args["prompt"],
            duration_s=int(args.get("duration_s", 4)),
        )

    if name == "maars.tts":
        try:
            from services.media_router import synthesize_speech
        except ImportError:
            return {"ok": False, "error": "tts_adapter_not_available"}
        return await synthesize_speech(
            user_id=user_id, text=args["text"], voice=args.get("voice", "alloy"),
        )

    if name == "maars.web_search":
        try:
            from services.web_search import search as _search
        except ImportError:
            return {"ok": False, "error": "web_search_not_available"}
        return await _search(args["query"], top_k=int(args.get("top_k", 5)))

    if name == "maars.list_integrations":
        from services import integration_driver
        drivers = integration_driver.list_drivers()
        out = []
        for d in drivers:
            s = await integration_driver.status(d["provider"], user_id)
            out.append(s)
        return {"ok": True, "count": len(out), "providers": out}

    if name == "maars.integration_act":
        from services import integration_driver
        return await integration_driver.act(
            provider=args["provider"], action=args["action"],
            params=args.get("params") or {},
            user_id=user_id, prefer_mode=args.get("prefer_mode"),
        )

    if name == "maars.run_workflow":
        from services.workflows import workflow_executor as wx
        from db import db
        wf = await db.workflows.find_one({"workflow_id": args["workflow_id"]}, {"_id": 0})
        if not wf:
            return {"ok": False, "error": "workflow_not_found"}
        if wf.get("user_id") != user_id:
            return {"ok": False, "error": "forbidden"}
        run_id = await wx._enqueue_run(
            wf, trigger_meta={"source": "mcp.run_workflow"},
            overrides=args.get("overrides") or {},
        )
        return {"ok": True, "run_id": run_id, "workflow_id": args["workflow_id"]}

    if name == "maars.commander_orchestrate":
        from services.workflows import workflow_generator, workflow_executor as wx
        from db import db
        from datetime import datetime, timezone
        draft = await workflow_generator.from_description(
            args["goal"], user_id, agent_id="agent_commander",
        )
        draft["active"] = bool(args.get("auto_run", True))
        draft["updated_at"] = datetime.now(timezone.utc).isoformat()
        draft["run_count"] = 0
        draft["orchestrated_by"] = "agent_commander"
        await db.workflows.insert_one({**draft, "_id": None})
        run_id = None
        if draft["active"]:
            run_id = await wx._enqueue_run(draft, trigger_meta={"source": "mcp.orchestrate"})
        return {"ok": True,
                "workflow_id": draft["workflow_id"],
                "nodes": len(draft.get("nodes") or []),
                "run_id": run_id,
                "validation_warnings": draft.get("validation_warnings") or []}

    return {"ok": False, "error": f"unknown_tool: {name}"}


# ── Entry points ────────────────────────────────────────────────────

async def _run_stdio() -> None:
    async with stdio_server() as (read, write):
        await _server.run(read, write, _server.create_initialization_options())


def main() -> None:
    # Default to stdio unless --sse is passed
    if "--sse" in sys.argv:
        _run_sse()
    else:
        asyncio.run(_run_stdio())


def _run_sse() -> None:
    """HTTP + SSE variant — bind to MCP_PORT (default 8900).

    Imports deferred so stdio mode doesn't pay the cost. The SSE transport
    uses starlette >=0.49 which conflicts with our FastAPI 0.110 (0.37.x
    starlette), so this mode is only safe to run in a separate process
    OR after bumping the main FastAPI stack. Keep stdio as the primary
    transport for now.
    """
    raise RuntimeError(
        "SSE transport requires starlette>=0.49 which conflicts with "
        "MAARS's FastAPI 0.110. Run stdio transport (default) or upgrade "
        "the FastAPI stack first. Use --stdio explicitly to silence this."
    )


if __name__ == "__main__":
    main()
