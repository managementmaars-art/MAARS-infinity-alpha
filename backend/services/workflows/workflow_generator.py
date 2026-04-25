"""LLM → workflow DAG generator.

Two public entrypoints:
  • from_description(prompt, user_id) — "build me a flow that ..."
  • from_chat(chat_id, user_id)       — take a chat's user message + assistant
                                        delegation plan and emit a workflow

Both produce a workflow *draft* — a dict matching the shape `workflows`
route accepts, with a generated `workflow_id` and `active: False` so the
operator reviews before turning it on.

Generation grounds the LLM in the actual tool registry so it can't invent
nodes that the executor doesn't know about. We pass a slim tool catalog
(name + one-line description + required params) in the system prompt.

Parsed output is validated: unknown tools are dropped, missing params
are flagged in `validation_warnings` on the draft.
"""
from __future__ import annotations
import json
import logging
import re
import uuid
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


def _tool_catalog() -> list[dict[str, Any]]:
    """Short, LLM-friendly catalog of every workflow tool.

    Keep entries tight — the generator sees all of them in one prompt.
    Every tool in services.workflow_executor.TOOL_REGISTRY belongs here so
    the AI can suggest the same tools the executor can actually run; the
    /workflow/tools endpoint in routes/workflows.py is the runtime check
    that keeps this list in sync."""
    return [
        # Control flow
        {"tool": "if_condition",   "category": "flow",  "one_line": "Binary branch on a JSON-path value comparison.",
         "params": "left (path), op (==|!=|in|exists|>|<), right"},
        {"tool": "switch",         "category": "flow",  "one_line": "N-way branch by matching cases to a value.",
         "params": "value (path), cases [{when, branch, op}], default_branch"},
        {"tool": "ai_branch",      "category": "flow",  "one_line": "AI picks the branch label that fits the input.",
         "params": "branches [{label, when_description}], input_field"},
        {"tool": "wait",           "category": "flow",  "one_line": "Sleep N seconds.",
         "params": "seconds"},
        {"tool": "sub_workflow",   "category": "flow",  "one_line": "Invoke another workflow by id.",
         "params": "workflow_id, overrides"},
        {"tool": "merge",          "category": "flow",  "one_line": "Combine parent outputs.",
         "params": "mode (combine|concat|first_ok)"},
        {"tool": "loop",           "category": "flow",  "one_line": "For each item run a child tool.",
         "params": "items (path), tool, params, max_parallel"},
        {"tool": "filter",         "category": "data",  "one_line": "Drop items failing predicate.",
         "params": "items (path), predicate"},
        {"tool": "set",            "category": "data",  "one_line": "Reshape/merge/replace output.",
         "params": "mode (merge|replace), fields"},
        {"tool": "sort",           "category": "data",  "one_line": "Sort a list.",
         "params": "items (path), by, order"},
        {"tool": "dedupe",         "category": "data",  "one_line": "Drop duplicates.",
         "params": "items (path), by"},
        {"tool": "aggregate",      "category": "data",  "one_line": "Sum/count/avg over a list.",
         "params": "items (path), op, field"},
        # Data + code
        {"tool": "code_js",        "category": "code",  "one_line": "Run sandboxed Node.js (5-30s).",
         "params": "code"},
        {"tool": "code_python",    "category": "code",  "one_line": "Run sandboxed Python (5-30s).",
         "params": "code"},
        {"tool": "sql_query",      "category": "db",    "one_line": "Postgres/MySQL query.",
         "params": "engine (pg|mysql), connection_string, sql, params"},
        {"tool": "mongo_query",    "category": "db",    "one_line": "MongoDB operation.",
         "params": "uri, db, collection, op, query"},
        {"tool": "rag_query",      "category": "ai",    "one_line": "Vector search over indexed docs.",
         "params": "query, top_k"},
        {"tool": "classify",       "category": "ai",    "one_line": "LLM classifier.",
         "params": "input, labels, model"},
        # HTTP / webhooks
        {"tool": "http_request",   "category": "http",  "one_line": "Arbitrary HTTP call.",
         "params": "method, url, headers, json, auth"},
        {"tool": "webhook_out",    "category": "http",  "one_line": "POST/PUT/DELETE to a URL.",
         "params": "method, url, headers, json"},
        {"tool": "respond_webhook","category": "http",  "one_line": "Reply to the triggering webhook.",
         "params": "status, body"},
        {"tool": "wait_for_webhook","category": "http", "one_line": "Pause until an external token hits /resume.",
         "params": "timeout_s, description"},
        {"tool": "approval",       "category": "flow",  "one_line": "Human-in-the-loop approve/reject gate.",
         "params": "title, description, timeout_s"},
        # MAARS-native
        {"tool": "search_leads",   "category": "maars", "one_line": "Lead search via MAARS BrowserAgent.",
         "params": "query, filters, limit"},
        {"tool": "enrich_contact", "category": "maars", "one_line": "Single-person lookup.",
         "params": "email|linkedin_url|name_company"},
        {"tool": "send_email",     "category": "maars", "one_line": "1-off transactional email.",
         "params": "to, subject, body, html"},
        {"tool": "run_campaign",   "category": "maars", "one_line": "Full cold-outreach campaign.",
         "params": "name, leads, template, schedule"},
        {"tool": "post_social",    "category": "maars", "one_line": "Post to LinkedIn/X/etc.",
         "params": "platform, content, media"},
        {"tool": "generate_image", "category": "maars", "one_line": "Image via smart router.",
         "params": "prompt, size, quality"},
        {"tool": "generate_video", "category": "maars", "one_line": "Video via smart router.",
         "params": "prompt, duration, resolution"},
        {"tool": "enhance_prompt", "category": "maars", "one_line": "LLM prompt enhancer.",
         "params": "prompt, purpose"},
        # Integrations
        {"tool": "slack_send",     "category": "comms", "one_line": "Post to Slack channel.",
         "params": "webhook_url|token+channel, text, blocks"},
        {"tool": "discord_send",   "category": "comms", "one_line": "Post to Discord webhook.",
         "params": "webhook_url, content, embeds"},
        {"tool": "telegram_send",  "category": "comms", "one_line": "Telegram bot message.",
         "params": "bot_token, chat_id, text"},
        {"tool": "twilio_sms",     "category": "comms", "one_line": "Send SMS via Twilio.",
         "params": "account_sid, auth_token, from, to, body"},
        {"tool": "google_sheets_append","category": "data", "one_line": "Append a row to Google Sheets.",
         "params": "spreadsheet_id, range, values"},
        {"tool": "notion_create",  "category": "data",  "one_line": "Create a Notion database item.",
         "params": "database_id, properties"},
        {"tool": "airtable_append","category": "data",  "one_line": "Append an Airtable row.",
         "params": "base_id, table, fields"},
        {"tool": "github",         "category": "dev",   "one_line": "GitHub op (issues/PRs/files).",
         "params": "op, owner, repo, ..."},
        {"tool": "jira",           "category": "dev",   "one_line": "Jira op.",
         "params": "op, project_key, ..."},
        {"tool": "hubspot_op",     "category": "crm",   "one_line": "HubSpot CRM op.",
         "params": "op, object, data"},
        {"tool": "stripe_op",      "category": "pay",   "one_line": "Stripe op.",
         "params": "op, data"},
        {"tool": "shopify_op",     "category": "ecom",  "one_line": "Shopify op.",
         "params": "op, data"},
        {"tool": "salesforce_op",  "category": "crm",   "one_line": "Salesforce op (create/update/get/delete/upsert/soql_query).",
         "params": "op, object, fields, soql"},
        {"tool": "gmail_op",       "category": "email", "one_line": "Gmail full CRUD (send/list/search/draft/label/trash).",
         "params": "op, to, subject, body, message_id, label_ids"},
        {"tool": "notion_op",      "category": "data",  "one_line": "Notion full CRUD (page + database + blocks).",
         "params": "op, database_id, page_id, properties, children"},
        {"tool": "draft_email",    "category": "maars", "one_line": "Compose an outreach email draft.",
         "params": "recipient, context, tone"},
        {"tool": "post_linkedin",  "category": "social","one_line": "Post to LinkedIn (alias for post_social).",
         "params": "content, media"},
        {"tool": "schedule_post",  "category": "social","one_line": "Queue a social post for a future time.",
         "params": "platform, content, scheduled_at"},
        # Dev + PM integrations
        {"tool": "gitlab",         "category": "dev",   "one_line": "GitLab op.",
         "params": "op, project_id, ..."},
        {"tool": "linear",         "category": "dev",   "one_line": "Linear (create_issue).",
         "params": "team_id, title, description"},
        {"tool": "asana",          "category": "pm",    "one_line": "Asana (create_task).",
         "params": "workspace, project, name, notes"},
        {"tool": "trello",         "category": "pm",    "one_line": "Trello (create_card).",
         "params": "list_id, name, desc"},
        {"tool": "clickup",        "category": "pm",    "one_line": "ClickUp (create_task).",
         "params": "list_id, name, description"},
        {"tool": "monday",         "category": "pm",    "one_line": "Monday.com (create_item).",
         "params": "board_id, group_id, item_name, column_values"},
        # Support / customer comms
        {"tool": "intercom_send",  "category": "support","one_line": "Send admin-initiated Intercom message.",
         "params": "user_id|email, body"},
        {"tool": "zendesk_ticket", "category": "support","one_line": "Zendesk — create ticket.",
         "params": "subject, body, priority, requester"},
        {"tool": "freshdesk_ticket","category": "support","one_line": "Freshdesk — create ticket.",
         "params": "subject, description, priority, email"},
        # Marketing
        {"tool": "mailchimp_subscribe","category": "mktg","one_line": "Add email to a Mailchimp list.",
         "params": "list_id, email, merge_fields"},
        {"tool": "typeform_list",  "category": "mktg",  "one_line": "List responses from a Typeform.",
         "params": "form_id, since, until"},
        {"tool": "sendgrid_send",  "category": "email", "one_line": "Send a transactional email via SendGrid.",
         "params": "to, from, subject, html"},
        # Enrichment
        {"tool": "clearbit_enrich","category": "enrich","one_line": "Clearbit person/company enrichment.",
         "params": "email|domain"},
        {"tool": "dropcontact_enrich","category": "enrich","one_line": "Dropcontact email validation + enrichment.",
         "params": "first, last, company"},
        {"tool": "openweather_get","category": "enrich","one_line": "OpenWeather lookup.",
         "params": "city|lat+lon"},
        # Storage
        {"tool": "google_drive_upload","category": "storage","one_line": "Upload a file to Google Drive.",
         "params": "name, content, folder_id, mime_type"},
        {"tool": "dropbox_upload", "category": "storage","one_line": "Upload a file to Dropbox.",
         "params": "path, content"},
        {"tool": "box_upload",     "category": "storage","one_line": "Upload a file to Box.",
         "params": "parent_id, name, content"},
        {"tool": "file_read",      "category": "storage","one_line": "Read a local file (sandboxed path).",
         "params": "path"},
        {"tool": "file_write",     "category": "storage","one_line": "Write a local file (sandboxed path).",
         "params": "path, content, mode"},
        {"tool": "s3_put",         "category": "storage","one_line": "Upload to S3.",
         "params": "bucket, key, body, content_type"},
        {"tool": "s3_get",         "category": "storage","one_line": "Download from S3.",
         "params": "bucket, key"},
        # Calendar / meetings
        {"tool": "calendly_list",  "category": "cal",   "one_line": "List Calendly availability or events.",
         "params": "user_uri, min_start_time, max_start_time"},
        {"tool": "zoom_create_meeting","category": "cal","one_line": "Schedule a Zoom meeting.",
         "params": "topic, start_time, duration, timezone"},
        # Search
        {"tool": "algolia_op",     "category": "search","one_line": "Algolia index or search.",
         "params": "op (index|search), index_name, object|query"},
        {"tool": "typesense_op",   "category": "search","one_line": "Typesense index (upsert) or search.",
         "params": "op, collection, doc|query"},
        # Data transforms
        {"tool": "group_by",       "category": "data",  "one_line": "Group a list of objects by a key.",
         "params": "items (path), key"},
        {"tool": "summarize",      "category": "data",  "one_line": "LLM-summarize a blob of text.",
         "params": "text, max_words, focus"},
        {"tool": "transform",      "category": "data",  "one_line": "Reshape data with a jq-style map.",
         "params": "items (path), map"},
        # Agent invocation — use this when the task fits a specific MAARS agent's role
        {"tool": "agent_chat",     "category": "maars", "one_line": "Invoke a specific MAARS agent by agent_id; routes through gateway with budget + skill-cache + training applied.",
         "params": "agent_id, prompt, model, max_tokens, temperature"},
        # Unified integration driver — one tool, all connected apps, API or browser
        {"tool": "integration_action", "category": "maars",
         "one_line": "Act on any connected integration (linkedin/x/instagram/tiktok/youtube/facebook/whatsapp/slack/discord/telegram) via API or live-browser driver. Use when you need to post, send, or read data in a real app the operator has connected.",
         "params": "provider, action, prefer_mode ('api'|'browser'), content, to, platform, etc."},
    ]


_TOOL_NAMES = {t["tool"] for t in _tool_catalog()}


# Tool synonym map — catches hallucinated tool names and remaps them to
# real TOOL_REGISTRY entries instead of dropping the node. Keyed by the
# fake name the LLM keeps inventing; value is the canonical MAARS tool.
# When the LLM says "upload_video", the node becomes generate_video; the
# node's existing params carry through.
_TOOL_SYNONYMS: dict[str, str] = {
    # Video
    "upload_video":       "generate_video",
    "render_video":       "generate_video",
    "compile_video":      "generate_video",
    "create_video":       "generate_video",
    "make_video":         "generate_video",
    "video_render":       "generate_video",
    "video_create":       "generate_video",
    "produce_video":      "generate_video",
    "assemble_video":     "generate_video",
    "edit_video":         "generate_video",
    # Image
    "create_image":       "generate_image",
    "make_image":         "generate_image",
    "render_image":       "generate_image",
    "design_graphic":     "generate_image",
    "design_graphics":    "generate_image",
    "create_graphic":     "generate_image",
    "generate_graphic":   "generate_image",
    # Social posting
    "publish_post":       "post_social",
    "share_post":         "post_social",
    "share_social":       "post_social",
    "post":               "post_social",
    "publish":            "post_social",
    "broadcast":          "post_social",
    "distribute":         "post_social",
    "social_post":        "post_social",
    "upload_social":      "post_social",
    "upload_post":        "post_social",
    "cross_post":         "post_social",
    "promote_video":      "post_social",
    "promote_post":       "post_social",
    "schedule_social":    "schedule_post",
    # Email
    "send_message":       "send_email",
    "send_mail":          "send_email",
    "email":              "send_email",
    "email_send":         "send_email",
    "email_reply":        "send_email",
    "notify_email":       "send_email",
    # LLM
    "llm_call":           "agent_chat",
    "llm":                "agent_chat",
    "chat":               "agent_chat",
    "ask_agent":          "agent_chat",
    "run_agent":          "agent_chat",
    "agent_invoke":       "agent_chat",
    "invoke_agent":       "agent_chat",
    # Flow
    "condition":          "if_condition",
    "if":                 "if_condition",
    "branch":             "if_condition",
    "choice":             "switch",
    "case":               "switch",
    "decide":             "ai_branch",
    "ai_decision":        "ai_branch",
    "iterate":            "loop",
    "foreach":            "loop",
    "for_each":           "loop",
    "sleep":              "wait",
    "pause":              "wait",
    "delay":              "wait",
    # Data
    "map":                "transform",
    "reshape":            "transform",
    "extract":            "set",
    "search":             "search_leads",
    "find_leads":         "search_leads",
    "enrich":             "enrich_contact",
    # HTTP
    "request":            "http_request",
    "fetch":              "http_request",
    "api_call":           "http_request",
    "webhook":            "webhook_out",
    "send_webhook":       "webhook_out",
}


async def _gather_user_resources(user_id: str) -> dict[str, Any]:
    """Snapshot the caller's actual wired resources so the generator
    produces workflows that reference REAL agents + connected services
    instead of emitting skeleton nodes."""
    from db import db
    out: dict[str, Any] = {"agents": [], "social_platforms": [],
                           "integrations": [], "role_map": {}}

    # Agents — prefer core-team (is_commander/is_custom false, lifecycle_state=active)
    # Listing ~60 keeps the prompt under budget.
    try:
        cursor = db.agents.find(
            {"lifecycle_state": {"$ne": "retired"}},
            {"_id": 0, "agent_id": 1, "name": 1, "role": 1, "network": 1,
             "capabilities": 1, "is_commander": 1},
        ).sort([("is_commander", -1), ("is_infinity", 1)]).limit(60)
        async for a in cursor:
            caps = (a.get("capabilities") or [])[:4]
            out["agents"].append({
                "agent_id":   a["agent_id"],
                "name":       a.get("name"),
                "role":       a.get("role"),
                "network":    a.get("network"),
                "capabilities": caps,
            })
    except Exception:
        pass

    # Role → agent_id map (static + DB overrides) so the LLM can pick a role
    # and we resolve post-hoc
    try:
        from services.agents import agent_router_map
        static = await agent_router_map._static_map()
        overrides = await agent_router_map._overrides()
        # Merge with overrides winning
        merged = dict(static)
        for k, v in overrides.items():
            if v: merged[k] = v[0]
        out["role_map"] = merged
    except Exception:
        pass

    # Connected social platforms — what the credential vault reports as
    # wired per platform. Gives the LLM a concrete list for post_social.
    try:
        cursor = db.credentials.find(
            {"user_id": user_id},
            {"_id": 0, "provider": 1, "platform": 1, "status": 1},
        ).limit(40)
        social_platforms_set: set[str] = set()
        integrations_set: set[str] = set()
        _social = {"linkedin", "twitter", "x", "instagram", "tiktok",
                   "facebook", "youtube", "threads", "pinterest"}
        async for c in cursor:
            label = (c.get("platform") or c.get("provider") or "").lower()
            if label in _social:
                social_platforms_set.add("x" if label == "twitter" else label)
            elif label:
                integrations_set.add(label)
        out["social_platforms"] = sorted(social_platforms_set)
        out["integrations"]     = sorted(integrations_set)
    except Exception:
        pass

    # Fallback: check env for platform tokens (TWITTER_API_KEY etc.) so
    # prod deployments that keep creds in env rather than vault still
    # surface available platforms.
    try:
        import os
        env_hints = {
            "linkedin":  bool(os.environ.get("LINKEDIN_ACCESS_TOKEN") or os.environ.get("LINKEDIN_API_KEY")),
            "x":         bool(os.environ.get("TWITTER_BEARER_TOKEN") or os.environ.get("X_API_KEY")),
            "instagram": bool(os.environ.get("INSTAGRAM_ACCESS_TOKEN") or os.environ.get("META_APP_ID")),
            "tiktok":    bool(os.environ.get("TIKTOK_ACCESS_TOKEN") or os.environ.get("TIKTOK_CLIENT_KEY")),
            "youtube":   bool(os.environ.get("YOUTUBE_API_KEY") or os.environ.get("GOOGLE_API_KEY")),
            "facebook":  bool(os.environ.get("FACEBOOK_ACCESS_TOKEN") or os.environ.get("META_APP_ID")),
        }
        for plat, present in env_hints.items():
            if present and plat not in out["social_platforms"]:
                out["social_platforms"].append(plat)
    except Exception:
        pass
    out["social_platforms"] = sorted(set(out["social_platforms"]))
    return out


def _format_resources(res: dict[str, Any]) -> str:
    """Compact resource block: role → first matching agent_id, plus
    connected platforms. Dense enough that the LLM can't drift into
    'do lead research' when the goal is about video production."""
    lines: list[str] = []
    agents = res.get("agents") or []
    # Bucket by role string; keep one representative per role so the
    # LLM sees compact choices. Prefer non-Commander, non-Infinity
    # (core team) since those are the polished user-facing roles.
    by_role: dict[str, str] = {}
    for a in agents:
        role = (a.get("role") or "").strip()
        if not role:
            continue
        if role not in by_role and not a.get("is_commander"):
            by_role[role] = f"{a['agent_id']} ({a.get('name','')})"
    if by_role:
        lines.append("AVAILABLE AGENTS — one per role. Use tool=agent_chat and set params.agent_id to the id (before the parentheses):")
        for role in sorted(by_role.keys()):
            lines.append(f"  {role:34} → {by_role[role]}")
    if res.get("role_map"):
        rm = res["role_map"]
        # Collapse role_map into a short keyword-to-agent_id list so the
        # LLM can resolve colloquial role names too.
        keywords = sorted({k for k in rm.keys() if " " not in k})[:30]
        if keywords:
            lines.append("KEYWORDS you can use as agent_id (resolved at save time): " + ", ".join(keywords))
    if res.get("social_platforms"):
        lines.append(f"CONNECTED SOCIAL PLATFORMS: {', '.join(res['social_platforms'])}")
        lines.append("  → When the goal says 'all social media', emit one post_social node per platform above (params.platform must be one of these).")
    else:
        lines.append("CONNECTED SOCIAL PLATFORMS: none wired yet — operator will connect at deploy; still emit post_social nodes with descriptive platform params (linkedin, x, tiktok, instagram, youtube).")
    if res.get("integrations"):
        lines.append(f"CONNECTED INTEGRATIONS: {', '.join(res['integrations'])}")
    return "\n".join(lines)


def _build_generation_prompt(user_goal: str, extra_context: str = "", resources_block: str = "") -> str:
    catalog_lines = []
    for t in _tool_catalog():
        catalog_lines.append(f"- {t['tool']}: {t['one_line']} params: {t['params']}")
    resources_hint = (
        "\n\nUSER RESOURCES (prefer these over generic tool nodes):\n" + resources_block
        if resources_block else ""
    )
    return (
        f"USER GOAL:\n{user_goal}\n\n"
        "You are Commander Orion ∞ assembling a workflow for MAARS-Command — a team of AI specialists, not a grab-bag of raw tools. "
        "Produce a workflow DAG as strict JSON.\n\n"
        "━━━ PRIMARY RULE ━━━\n"
        "**AGENTS ARE THE WORKFLOW.** Every creative, research, analytical, strategic, communication, or writing step MUST be an "
        "`agent_chat` node referencing one of the user's real AGENTS below (use the agent_id shown before the parenthesis). "
        "You are delegating work to Zara, Kai, Luna, Scarlett, and the rest — not calling raw APIs. Raw tools are their HANDS, "
        "not the workflow's nodes.\n\n"
        "REFERENCE PIPELINES (use these shapes for matching goals):\n"
        "  • Video / reel production:\n"
        "      agent_chat(agent_researcher, 'find catchy story on <topic>') →\n"
        "      agent_chat(agent_graphics, 'design visuals/thumbnails for the story: {{researcher.output}}') →\n"
        "      agent_chat(agent_video, 'assemble reel from story + visuals') →\n"
        "      agent_chat(agent_copywriter, 'write caption + hashtags for {{video.output}}') →\n"
        "      agent_chat(agent_socialmedia, 'schedule post on <platform>') → post_social\n"
        "  • Cold outreach / sales:\n"
        "      agent_chat(agent_researcher, 'find N prospects matching <ICP>') →\n"
        "      agent_chat(agent_copywriter, 'draft personalized email for each lead') →\n"
        "      agent_chat(agent_sales, 'review + sequence the outreach') → run_campaign\n"
        "  • Content series:\n"
        "      agent_chat(agent_contentwriter, 'outline a <N>-part series on <topic>') →\n"
        "      loop over parts: agent_chat(agent_contentwriter, 'write part {{i}}') →\n"
        "      agent_chat(agent_marketing, 'plan distribution') → post_social per platform\n"
        "\n"
        "━━━ DAG SHAPE ━━━\n"
        "1. Every node: id (snake_case), type ('trigger'|'action'), tool, params, next (list of ids).\n"
        "2. Branching: if_condition (branch_yes/branch_no), switch (branches map), ai_branch (branches map; branches={label:[ids]}).\n"
        "3. Never invent tool names — only use the catalog below. agent_chat is always valid.\n"
        "4. First node is type='trigger'; workflow-level trigger config goes on the top-level 'trigger' field.\n"
        "5. Parameterize with {{previous_node_id.output}} or {{previous.field}}. $now / $today / $run.id available.\n"
        "\n"
        "━━━ NODE PARAMS (never leave empty) ━━━\n"
        "  • agent_chat → MUST have params.agent_id (from AVAILABLE AGENTS) + params.prompt (concrete, 1-3 sentences, "
        "    references upstream outputs with {{prev.output}}).\n"
        "  • generate_image / generate_video → params.prompt (descriptive); these typically FOLLOW an agent_chat that produced the prompt.\n"
        "  • post_social → params.platform (linkedin | x | tiktok | instagram | youtube | facebook) + params.content "
        "    (usually {{socialmedia.output}} or a template).\n"
        "  • loop → params.items (array like [1,2,...,N]) + params.tool (typically 'agent_chat') + params.params (the inner node's params).\n"
        "\n"
        "━━━ TOPIC MATCHING ━━━\n"
        "Match the USER GOAL exactly. Video/reels → agent_video + agent_graphics + agent_researcher. Email outreach → agent_copywriter + agent_sales. Data ETL → http_request + transform (no agents). Stay on topic — never default to lead research unless the goal is about leads.\n\n"
        "━━━ SERIES & FAN-OUT ━━━\n"
        "Series (e.g. '10 reels'): use a single loop node with items=[1..N]. Don't emit 10 separate nodes.\n"
        "'All social media': if CONNECTED SOCIAL PLATFORMS are listed, emit one post_social per platform. Otherwise emit for the major ones (linkedin, x, tiktok, instagram, youtube) so operator can wire creds.\n\n"
        "Output ONE JSON object: {\"name\", \"description\", \"trigger\": {\"type\": \"manual|scheduled|webhook\", ...}, \"nodes\": [...]}. No commentary, no markdown fences.\n\n"
        "TOOL CATALOG (prefer agent_chat; raw tools are secondary):\n" + "\n".join(catalog_lines) +
        resources_hint +
        (f"\n\nADDITIONAL CONTEXT:\n{extra_context}" if extra_context else "")
    )


def _parse_workflow_json(raw: str) -> dict:
    """Pull the first balanced {...} block out of the LLM reply.

    The greedy `\\{[\\s\\S]*\\}` regex breaks when the model tacks on a
    second object or stray text after the workflow JSON. Walk the string
    tracking brace depth (respecting quoted strings + escapes) so we
    extract exactly the first top-level object."""
    if not raw:
        raise ValueError("no_json_object_in_response")
    start = raw.find("{")
    if start < 0:
        raise ValueError("no_json_object_in_response")
    depth = 0
    in_str = False
    escape = False
    end = -1
    for i in range(start, len(raw)):
        ch = raw[i]
        if in_str:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i
                break
    if end < 0:
        raise ValueError("json_parse_failed: unbalanced braces")
    candidate = raw[start:end + 1]
    try:
        return json.loads(candidate)
    except Exception as exc:
        raise ValueError(f"json_parse_failed: {exc}")


# Synonym map — catches hallucinated agent_ids that look like roles but
# aren't in the canonical map (e.g. LLM emits "story_agent" instead of
# "researcher", or "caption_agent" instead of "copywriter"). Values are
# lowercased role-map keys; the resolver looks them up in AGENT_ROLE_MAP
# which returns the actual agent_id. Extend as the LLM invents new names.
_AGENT_ID_SYNONYMS: dict[str, str] = {
    # Content + narrative
    "story":            "research",
    "story_agent":      "research",
    "narrative":        "research",
    "narrative_agent":  "research",
    "research_agent":   "research",
    "story_researcher": "research",
    "storyteller":      "copywriting",
    "script":           "copywriting",
    "script_agent":     "copywriting",
    "scriptwriter":     "copywriting",
    "caption":          "copywriting",
    "caption_agent":    "copywriting",
    "copy_agent":       "copywriting",
    "copywriter_agent": "copywriting",
    "writer":           "copywriting",
    "writer_agent":     "copywriting",
    "content_agent":    "content",
    # Visual + media
    "graphics_agent":   "graphic design",
    "graphic":          "graphic design",
    "graphic_agent":    "graphic design",
    "designer":         "graphic design",
    "designer_agent":   "graphic design",
    "visuals":          "graphic design",
    "visuals_agent":    "graphic design",
    "image_agent":      "graphic design",
    "image":            "graphic design",
    "video_agent":      "video",
    "reel":             "video",
    "reel_agent":       "video",
    "reels":            "video",
    "reels_agent":      "video",
    "editor":           "video",
    "editor_agent":     "video",
    "video_editor":     "video",
    "youtube_agent":    "video",
    # Social
    "social":           "social media",
    "social_agent":     "social media",
    "socialmedia":      "social media",
    "socialmedia_agent":"social media",
    "poster":           "social media",
    "publisher":        "social media",
    "publisher_agent":  "social media",
    # Marketing + growth
    "marketer":         "marketing",
    "marketer_agent":   "marketing",
    "brand_agent":      "brand",
    "branding":         "brand",
    "growth_agent":     "growth",
    "seo_agent":        "seo",
    "email_agent":      "email",
    "newsletter_agent": "newsletter",
    # Sales + CRM
    "sales_agent":      "sales",
    "rep":              "sales",
    "sdr":              "sales",
    "bdr":              "sales",
    "crm_agent":        "hubspot_op",  # direct tool pointer
    # Strategy + ops
    "strategist":       "strategy",
    "strategy_agent":   "strategy",
    "business_agent":   "business",
    "pm":               "product management",
    "product_agent":    "product management",
    "project_agent":    "project management",
    "ops":              "operations",
    "ops_agent":        "operations",
    # Research + data
    "researcher":       "research",
    "researcher_agent": "research",
    "analyst":          "analytics",
    "analyst_agent":    "analytics",
    "data_agent":       "data",
    # Support + legal + compliance
    "support_agent":    "support",
    "customer_agent":   "customer service",
    "legal_agent":      "legal",
    "compliance_agent": "compliance",
    # Finance
    "finance_agent":    "finance",
    "cfo_agent":        "finance",
    # Generic
    "ai_agent":         "ai",
    "assistant":        "secretary",
    "assistant_agent":  "secretary",
    "secretary_agent":  "secretary",
}


# Per-tool required param surfaces. A node missing these is treated as
# incomplete and either auto-filled (from upstream state) or flagged for
# the LLM repair pass. Keeps "empty looking" nodes out of the canvas.
_REQUIRED_PARAMS: dict[str, list[str]] = {
    "agent_chat":       ["agent_id", "prompt"],
    "generate_image":   ["prompt"],
    "generate_video":   ["prompt"],
    "post_social":      ["platform", "content"],
    "schedule_post":    ["platform", "content"],
    "send_email":       ["to", "subject", "body"],
    "send_cold_email":  ["to", "subject", "body"],
    "run_campaign":     ["name"],
    "http_request":     ["method", "url"],
    "webhook_out":      ["url"],
    "wait":             ["seconds"],
    "if_condition":     ["left", "op"],
    "switch":           ["value", "cases"],
    "ai_branch":        ["branches"],
    "loop":             ["items"],
    "filter":           ["items"],
    "set":              ["fields"],
    "sub_workflow":     ["workflow_id"],
    "slack_send":       ["text"],
    "discord_send":     ["content"],
    "twilio_sms":       ["to", "body"],
    "google_sheets_append": ["spreadsheet_id", "values"],
    "notion_op":        ["op"],
    "stripe_op":        ["op"],
    "hubspot_op":       ["op"],
    "salesforce_op":    ["op"],
    "gmail_op":         ["op"],
    "shopify_op":       ["op"],
    "sql_query":        ["sql"],
    "code_js":          ["code"],
    "code_python":      ["code"],
}


def _thin_nodes_for_repair(nodes: list[dict]) -> list[dict]:
    """Return only nodes missing required params — keeps the repair
    prompt tight."""
    out: list[dict] = []
    for n in nodes:
        if not isinstance(n, dict): continue
        tool = n.get("tool") or ""
        req = _REQUIRED_PARAMS.get(tool)
        if not req: continue
        params = n.get("params") or {}
        missing = [k for k in req if not params.get(k)]
        if missing:
            out.append({"id": n.get("id"), "tool": tool,
                        "missing": missing, "current_params": params})
    return out


async def _repair_empty_params(
    draft: dict, user_goal: str, resources: dict[str, Any],
    user_id: str,
) -> list[str]:
    """Second-pass LLM fill for nodes with empty required params.
    Prevents the 'empty nodes on canvas' problem — every node gets
    concrete instructions the executor can run."""
    warnings: list[str] = []
    thin = _thin_nodes_for_repair(draft.get("nodes") or [])
    if not thin:
        return warnings
    # Compact context: what the LLM needs to fill the gaps
    import json as _json
    from services.llm_gateway import complete_text
    prompt = (
        f"USER GOAL: {user_goal}\n\n"
        "The following workflow nodes are missing required params. Fill in concrete values "
        "that match the USER GOAL. For agent_chat, keep the agent_id already set (pre-resolved "
        "to a real MAARS agent); just fill the prompt. For post_social, fill platform with one of "
        f"{', '.join(resources.get('social_platforms') or ['linkedin','x','tiktok','instagram','youtube'])} "
        "and content with a caption appropriate to the goal. For generate_image/generate_video, "
        "write a descriptive prompt tied to the goal.\n\n"
        "Reply ONLY with a JSON array of objects shaped like "
        '{"id": "<node_id>", "params": {<filled key/values>}}. '
        "Return ONLY the keys that were missing. No prose, no fences.\n\n"
        "NODES TO REPAIR:\n" + _json.dumps(thin, default=str)[:3500]
    )
    try:
        raw = await complete_text(
            user_id,
            system_prompt=(
                "You are Commander Orion ∞, fixing incomplete workflow nodes for MAARS-Command. "
                "Output strict JSON only — no prose."
            ),
            user_prompt=prompt,
            model="maars/auto",
            max_tokens=1500, temperature=0.2,
            source="workflow_generator.repair",
            agent_id="agent_commander",
            enable_cache=False,
        )
    except Exception as exc:
        warnings.append(f"param-repair skipped: {exc}")
        return warnings
    # Extract the first balanced [...] block
    import re as _re
    m = _re.search(r"\[[\s\S]*\]", raw or "")
    if not m:
        warnings.append("param-repair: no array in LLM reply")
        return warnings
    try:
        patches = _json.loads(m.group(0))
    except Exception as exc:
        warnings.append(f"param-repair parse failed: {exc}")
        return warnings
    # Apply patches by id
    by_id = {n.get("id"): n for n in (draft.get("nodes") or []) if isinstance(n, dict)}
    applied = 0
    for p in patches if isinstance(patches, list) else []:
        if not isinstance(p, dict): continue
        nid = p.get("id")
        node = by_id.get(nid)
        if not node: continue
        new_params = p.get("params") or {}
        if not isinstance(new_params, dict): continue
        node_params = node.setdefault("params", {})
        for k, v in new_params.items():
            if v and not node_params.get(k):
                node_params[k] = v
                applied += 1
    if applied:
        warnings.append(f"param-repair: filled {applied} missing field(s)")
    return warnings


# Which raw creative tools imply "an agent should drive this" when they
# appear without a preceding agent_chat in the pipeline. Value is the
# canonical role to upgrade the pipeline with.
_ORPHAN_TOOL_TO_ROLE: dict[str, str] = {
    "generate_image":  "graphic design",
    "generate_video":  "video",
    "enhance_prompt":  "ai optimization",
    "post_social":     "social media",
    "schedule_post":   "social media",
    "post_linkedin":   "social media",
    "draft_email":     "copywriting",
    "send_email":      "copywriting",
    "send_cold_email": "copywriting",
    "run_campaign":    "sales",
    "search_leads":    "research",
    "enrich_contact":  "research",
}


async def _upgrade_orphan_tools_to_agent_driven(
    draft: dict, resources: dict[str, Any],
) -> list[str]:
    """If a creative/communication tool (generate_video, post_social,
    etc.) has no preceding agent_chat in its DAG path, inject an
    agent_chat driver node before it. That way every real action is
    owned by a named MAARS agent, not a bare tool invocation."""
    warnings: list[str] = []
    role_map = resources.get("role_map") or {}
    agents = resources.get("agents") or []
    # Map role → agent_id (prefer exact role_map entries, then first roster
    # agent with a matching role string).
    role_to_aid: dict[str, str] = dict(role_map)
    for a in agents:
        r = (a.get("role") or "").lower()
        if r and r not in role_to_aid:
            role_to_aid[r] = a["agent_id"]
        # Also index singular words
        for w in r.replace("/", " ").replace("-", " ").split():
            role_to_aid.setdefault(w, a["agent_id"])

    nodes = draft.get("nodes") or []
    by_id = {n.get("id"): n for n in nodes if isinstance(n, dict)}

    # Build reverse-edge index: for each node, who are its parents?
    parents: dict[str, list[str]] = {nid: [] for nid in by_id.keys()}
    for n in nodes:
        if not isinstance(n, dict): continue
        nid = n.get("id")
        for t in (n.get("next") or []):
            if t in parents: parents[t].append(nid)
        for t in (n.get("branch_yes") or []):
            if t in parents: parents[t].append(nid)
        for t in (n.get("branch_no") or []):
            if t in parents: parents[t].append(nid)
        for tl in (n.get("branches") or {}).values():
            for t in (tl or []):
                if t in parents: parents[t].append(nid)

    # For each orphan creative tool, check: does ANY ancestor use agent_chat?
    # If not, insert an agent_chat driver before it.
    import uuid as _uuid
    inserted = 0
    for n in list(nodes):
        if not isinstance(n, dict): continue
        tool = n.get("tool")
        role = _ORPHAN_TOOL_TO_ROLE.get(tool)
        if not role: continue
        # Walk ancestors up to depth 4 looking for an agent_chat
        seen: set[str] = set()
        queue = list(parents.get(n.get("id"), []))
        has_driver = False
        while queue and len(seen) < 20:
            pid = queue.pop(0)
            if pid in seen: continue
            seen.add(pid)
            parent = by_id.get(pid) or {}
            if parent.get("tool") == "agent_chat":
                has_driver = True
                break
            queue.extend(parents.get(pid, []))
        if has_driver:
            continue
        # Resolve role to real agent_id
        agent_id = role_to_aid.get(role.lower())
        if not agent_id:
            # Try each word of the role as fallback
            for w in role.split():
                if w.lower() in role_to_aid:
                    agent_id = role_to_aid[w.lower()]
                    break
        if not agent_id:
            continue  # No agent matches; leave as-is
        # Build the driver agent_chat node and rewire edges
        driver_id = f"driver_{n.get('id')}_{_uuid.uuid4().hex[:4]}"
        inner_prompt_stub = {
            "generate_image":  "Produce a detailed visual brief for the image generator.",
            "generate_video":  "Produce a detailed storyboard + prompt for the video generator.",
            "post_social":     f"Write a platform-appropriate caption (platform={n.get('params',{}).get('platform','linkedin')}).",
            "schedule_post":   f"Plan the scheduled post (platform={n.get('params',{}).get('platform','linkedin')}).",
            "draft_email":     "Draft a personalized email body.",
            "send_email":      "Compose the email subject + body before sending.",
            "send_cold_email": "Compose the personalized cold-email body.",
            "run_campaign":    "Plan the outreach campaign strategy + message templates.",
            "search_leads":    "Build the lead search criteria (titles, industries, geos, signals).",
            "enrich_contact":  "Research this contact deeply before enrichment.",
        }.get(tool, "Prepare inputs for the next step.")
        driver = {
            "id":     driver_id,
            "type":   "action",
            "tool":   "agent_chat",
            "params": {
                "agent_id": agent_id,
                "prompt":   inner_prompt_stub,
            },
            "next":   [n["id"]],
        }
        nodes.insert(nodes.index(n), driver)
        # Rewire: anyone who pointed to n should now point to driver
        for other in nodes:
            if not isinstance(other, dict) or other is driver: continue
            for field in ("next", "branch_yes", "branch_no"):
                lst = other.get(field)
                if not lst: continue
                other[field] = [driver_id if x == n["id"] else x for x in lst]
            for label, tlist in list((other.get("branches") or {}).items()):
                other["branches"][label] = [driver_id if x == n["id"] else x for x in (tlist or [])]
        inserted += 1
        warnings.append(f"wrapped orphan {tool} with agent_chat driver ({agent_id})")

    draft["nodes"] = nodes
    if inserted:
        warnings.insert(0, f"Commander Orion added {inserted} agent driver(s) so your real agents run the pipeline")
    return warnings


async def _resolve_role_references(draft: dict, resources: dict[str, Any]) -> list[str]:
    """Resolve any agent_chat nodes whose agent_id is a role string,
    keyword, compound, or hallucinated synonym (e.g. 'story_agent',
    'caption_agent', 'video/graphics/content_agent') into a real
    agent_id. Resolution order:
      1. Exact match in roster
      2. AGENT_ROLE_MAP (static + DB overrides)
      3. Agent_id suffix (agent_X)
      4. Live roster role → first agent with that role
      5. Fuzzy word match across role tokens
      6. `_AGENT_ID_SYNONYMS` map (hallucination catcher)
    """
    warnings: list[str] = []
    role_map = resources.get("role_map") or {}
    agents = resources.get("agents") or []
    known_agent_ids = {a["agent_id"] for a in agents}
    # Build a role → agent_id index from the live roster
    roster_by_role: dict[str, str] = {}
    for a in agents:
        r = (a.get("role") or "").strip().lower()
        if r and r not in roster_by_role:
            roster_by_role[r] = a["agent_id"]
        for word in r.replace("/", " ").replace("-", " ").split():
            w = word.lower()
            if len(w) >= 4 and w not in roster_by_role:
                roster_by_role[w] = a["agent_id"]
    for a in agents:
        aid = a["agent_id"]
        if aid.startswith("agent_"):
            key = aid[6:]
            roster_by_role.setdefault(key, aid)

    def _try_resolve(raw: str) -> str | None:
        s = (raw or "").strip().lower()
        if not s: return None
        # 1. Already a real agent_id
        if s in known_agent_ids: return s
        # 2. Static role map
        if s in role_map: return role_map[s]
        # 3. Agent_id suffix (video → agent_video)
        if s in roster_by_role: return roster_by_role[s]
        # 4. Synonym hop — map to canonical role, then look up
        if s in _AGENT_ID_SYNONYMS:
            canonical = _AGENT_ID_SYNONYMS[s]
            if canonical in role_map:      return role_map[canonical]
            if canonical in roster_by_role: return roster_by_role[canonical]
            if canonical in known_agent_ids: return canonical
        # 5. Compound like "video/graphics/content_agent" — try each part
        parts = s.replace("/", " ").replace(",", " ").replace("_agent", "").split()
        for part in parts:
            p = part.strip().lower()
            if p in role_map:           return role_map[p]
            if p in roster_by_role:     return roster_by_role[p]
            if p in _AGENT_ID_SYNONYMS:
                canonical = _AGENT_ID_SYNONYMS[p]
                if canonical in role_map:       return role_map[canonical]
                if canonical in roster_by_role: return roster_by_role[canonical]
        return None

    connected_platforms = resources.get("social_platforms") or []
    for n in draft.get("nodes") or []:
        if not isinstance(n, dict):
            continue
        tool = n.get("tool")
        params = n.setdefault("params", {})
        if tool == "agent_chat":
            aid = (params.get("agent_id") or "").strip()
            if aid and aid not in known_agent_ids:
                resolved = _try_resolve(aid)
                if resolved:
                    params["agent_id"] = resolved
                    warnings.append(f"node {n.get('id')}: agent '{aid}' → {resolved}")
                else:
                    warnings.append(f"node {n.get('id')}: agent_id '{aid}' not in your roster — review before running")
        if tool == "post_social":
            plat = (params.get("platform") or "").lower()
            if not plat and connected_platforms:
                params["platform"] = connected_platforms[0]
                warnings.append(f"node {n.get('id')}: no platform set — defaulted to '{connected_platforms[0]}'")
            elif plat and connected_platforms and plat not in connected_platforms:
                warnings.append(
                    f"node {n.get('id')}: platform '{plat}' not connected yet "
                    f"(you have: {', '.join(connected_platforms)}) — connect or change before running"
                )
    return warnings


def _validate_draft(draft: dict) -> tuple[dict, list[str]]:
    """Strip unknown tools, normalize shape, collect warnings.

    Before dropping a node for an unknown tool, try the synonym map —
    'upload_video' → 'generate_video', 'publish_post' → 'post_social',
    etc. Keeps workflows intact when the LLM invents near-miss names."""
    warnings: list[str] = []
    nodes = draft.get("nodes") or []
    cleaned: list[dict] = []
    seen_ids: set[str] = set()
    for i, n in enumerate(nodes):
        if not isinstance(n, dict):
            warnings.append(f"node[{i}] is not an object; dropped")
            continue
        nid = str(n.get("id") or f"n_{i}")
        while nid in seen_ids:
            nid = f"{nid}_dup"
        seen_ids.add(nid)
        n["id"] = nid
        tool = n.get("tool")
        ntype = n.get("type")
        if ntype != "trigger" and tool and tool not in _TOOL_NAMES:
            # Try synonym map before dropping
            canonical = _TOOL_SYNONYMS.get(str(tool).lower())
            if canonical and canonical in _TOOL_NAMES:
                n["tool"] = canonical
                warnings.append(f"node {nid}: tool '{tool}' → {canonical}")
            else:
                warnings.append(f"node {nid}: unknown tool '{tool}' — dropped")
                continue
        cleaned.append(n)
    draft["nodes"] = cleaned
    # Backfill basics
    draft.setdefault("name", "Generated workflow")
    draft.setdefault("description", "")
    draft.setdefault("trigger", {"type": "manual"})
    return draft, warnings


async def from_description(user_prompt: str, user_id: str, agent_id: str | None = None) -> dict:
    """Generate a workflow draft from a natural-language description.
    Resource-aware: reads the user's agents + connected platforms first
    and grounds the LLM in those so generated nodes reference REAL
    agent_ids and real platforms instead of skeleton placeholders."""
    from services.llm_gateway import complete_text
    resources = await _gather_user_resources(user_id)
    resources_block = _format_resources(resources)
    # enable_cache=False so every build fresh-rolls. Otherwise the
    # semantic cache replays an earlier (possibly empty) response.
    # When agent_id='agent_commander' the system prompt carries his
    # orchestrator identity — he signs the workflow description and
    # picks agents from the roster.
    system_prompt = (
        "You are Commander Orion ∞, MAARS Infinity's supreme orchestrator. "
        "Convert the user's goal into an executable workflow DAG using the "
        "agents and tools below. Output STRICT JSON only — no prose, no "
        "markdown fences, no commentary. Decompose. Delegate. Verify."
        if agent_id == "agent_commander"
        else "You produce strict JSON workflow specs. Never output prose."
    )
    # Pin the generator to a reasoning-capable model. Workflows are
    # generated once and run many times — output quality compounds, cost
    # doesn't. "maars/reasoning" is the alias for the best-available
    # reasoning tier; falls through to maars/auto if unmapped.
    raw = await complete_text(
        user_id,
        system_prompt=system_prompt,
        user_prompt=_build_generation_prompt(user_prompt, resources_block=resources_block),
        model="maars/reasoning",
        max_tokens=4000, temperature=0.2,
        source="workflow_generator.from_description",
        agent_id=agent_id,
        enable_cache=False,
    )
    draft = _parse_workflow_json(raw)
    draft, warnings = _validate_draft(draft)
    resolve_warnings = await _resolve_role_references(draft, resources)
    warnings.extend(resolve_warnings)
    # Wrap orphan creative/comms tools with agent_chat drivers so your
    # real MAARS agents (not raw API calls) own every pipeline step.
    orphan_warnings = await _upgrade_orphan_tools_to_agent_driven(draft, resources)
    warnings.extend(orphan_warnings)
    # Second pass: fill any node that's still missing required params
    # so the canvas never shows "empty nodes".
    repair_warnings = await _repair_empty_params(draft, user_prompt, resources, user_id)
    warnings.extend(repair_warnings)
    draft["workflow_id"] = f"wf_{uuid.uuid4().hex[:12]}"
    draft["user_id"] = user_id
    draft["active"] = False
    draft["created_at"] = datetime.now(timezone.utc).isoformat()
    draft["validation_warnings"] = warnings
    draft["generated_from"] = "description"
    draft["resources_used"] = {
        "agents_available":     len(resources.get("agents") or []),
        "social_platforms":     resources.get("social_platforms") or [],
        "integrations":         resources.get("integrations") or [],
    }
    return draft


async def from_chat(chat_id: str, user_id: str) -> dict:
    """Pull recent messages from a chat and condense into a workflow.
    Uses the most recent user→assistant pair: the user's goal as the
    workflow description, the assistant's action plan (if any) as extra
    context to ground the DAG structure."""
    from db import db
    msgs = await db.messages.find(
        {"chat_id": chat_id},
        {"_id": 0, "role": 1, "content": 1, "created_at": 1, "execution_steps": 1},
    ).sort("created_at", -1).limit(10).to_list(length=10)
    msgs.reverse()
    if not msgs:
        raise ValueError("chat_has_no_messages")
    # Most recent user prompt — the "goal"
    user_msgs = [m for m in msgs if m.get("role") == "user"]
    if not user_msgs:
        raise ValueError("chat_has_no_user_messages")
    goal = (user_msgs[-1].get("content") or "").strip()
    # Nearest assistant reply + any execution_steps to feed the LLM context
    extra_lines: list[str] = []
    last_assistant = next(
        (m for m in reversed(msgs) if m.get("role") == "assistant"), None
    )
    if last_assistant:
        content = (last_assistant.get("content") or "").strip()
        if content:
            extra_lines.append("PRIOR ASSISTANT PLAN:\n" + content[:3000])
        steps = last_assistant.get("execution_steps") or []
        if steps:
            extra_lines.append(
                "PRIOR EXECUTION STEPS:\n"
                + json.dumps(steps, default=str)[:2000]
            )
    from services.llm_gateway import complete_text
    resources = await _gather_user_resources(user_id)
    resources_block = _format_resources(resources)
    raw = await complete_text(
        user_id,
        system_prompt=(
            "You are Commander Orion ∞, MAARS Infinity's supreme orchestrator. "
            "Convert the user's goal into an executable workflow DAG using the "
            "agents and tools below. Output STRICT JSON only — no prose, no "
            "markdown fences, no commentary. Decompose. Delegate. Verify."
        ),
        user_prompt=_build_generation_prompt(
            goal, extra_context="\n\n".join(extra_lines),
            resources_block=resources_block,
        ),
        model="maars/auto",
        max_tokens=4000, temperature=0.15,
        source="workflow_generator.from_chat",
        agent_id="agent_commander",
        enable_cache=False,
    )
    draft = _parse_workflow_json(raw)
    draft, warnings = _validate_draft(draft)
    resolve_warnings = await _resolve_role_references(draft, resources)
    warnings.extend(resolve_warnings)
    orphan_warnings = await _upgrade_orphan_tools_to_agent_driven(draft, resources)
    warnings.extend(orphan_warnings)
    repair_warnings = await _repair_empty_params(draft, goal, resources, user_id)
    warnings.extend(repair_warnings)
    draft["workflow_id"] = f"wf_{uuid.uuid4().hex[:12]}"
    draft["user_id"] = user_id
    draft["active"] = False
    draft["created_at"] = datetime.now(timezone.utc).isoformat()
    draft["validation_warnings"] = warnings
    draft["generated_from"] = f"chat:{chat_id}"
    draft["resources_used"] = {
        "agents_available":     len(resources.get("agents") or []),
        "social_platforms":     resources.get("social_platforms") or [],
        "integrations":         resources.get("integrations") or [],
    }
    return draft
