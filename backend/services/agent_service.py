"""Agent execution service - tools, workspace context, commander delegation."""
import re
import uuid
import json
import asyncio
import logging
import httpx
from datetime import datetime, timezone

from db import db
from config import DEFAULT_AGENTS, AGENT_TOOLS, AGENT_TOOL_MAP, DEFAULT_BRAIN_PROFILES
from shared.constants import (
    UPLOAD_DIR, INTEGRATION_SERVICES
)
from services.integration_service import get_effective_integration_config
from services.llm_service import call_llm_with_fallback
from services.artifact_service import create_artifact

logger = logging.getLogger(__name__)

CLARIFICATION_INSTRUCTION = """

IMPORTANT RESPONSE GUIDELINES:
- If the user's request is clear and specific, respond directly with your best professional output. Do NOT ask questions.
- Only ask a clarifying question if the request is genuinely ambiguous (e.g., "help me with marketing" with no details).
- When you DO need clarification, ask ONE focused question, not multiple.
- Default to action over clarification. When in doubt, give a comprehensive answer that covers likely interpretations.
- For technical/creative tasks, just do the work. Don't ask "what style" or "what tone" — use your professional judgment.
"""

AGENT_ROLE_MAP = {
    "marketing": "agent_marketing",
    "strategy": "agent_strategist",
    "business": "agent_strategist",
    "web design": "agent_webdesigner",
    "ui/ux": "agent_webdesigner",
    "development": "agent_appdev",
    "coding": "agent_appdev",
    "copywriting": "agent_copywriter",
    "copy": "agent_copywriter",
    "seo": "agent_seo",
    "sales": "agent_sales",
    "social media": "agent_socialmedia",
    "data": "agent_analyst",
    "analytics": "agent_analyst",
    "content": "agent_contentwriter",
    "blog": "agent_contentwriter",
    "customer service": "agent_customerservice",
    "support": "agent_customerservice",
    "project management": "agent_projectmanager",
    "planning": "agent_projectmanager",
    "research": "agent_researcher",
    "finance": "agent_finance",
    "budget": "agent_finance",
    "hr": "agent_hr",
    "hiring": "agent_hr",
    "graphic design": "agent_graphics",
    "design": "agent_graphics",
    "legal": "agent_legal",
    "contract": "agent_legal",
    "email": "agent_email",
    "newsletter": "agent_email",
    "video": "agent_video",
    "youtube": "agent_video",
    "secretary": "agent_secretary",
    "schedule": "agent_secretary",
    # New agent role mappings
    "cybersecurity": "agent_cybersecurity",
    "security": "agent_cybersecurity",
    "infosec": "agent_cybersecurity",
    "automation": "agent_automation",
    "workflow": "agent_automation",
    "integration": "agent_automation",
    "growth": "agent_growthhacker",
    "growth hacking": "agent_growthhacker",
    "acquisition": "agent_growthhacker",
    "compliance": "agent_compliance",
    "regulatory": "agent_compliance",
    "audit": "agent_compliance",
    "ai optimization": "agent_aioptimizer",
    "ai": "agent_aioptimizer",
    "prompt engineering": "agent_aioptimizer",
    "operations": "agent_operations",
    "supply chain": "agent_operations",
    "logistics": "agent_operations",
    "revenue": "agent_revenue",
    "pricing": "agent_revenue",
    "monetization": "agent_revenue",
    # Phase 2 agent role mappings
    "chief strategy": "agent_cso",
    "corporate strategy": "agent_cso",
    "strategic planning": "agent_cso",
    "investor relations": "agent_investor",
    "fundraising": "agent_investor",
    "pitch deck": "agent_investor",
    "product management": "agent_productmgr",
    "product": "agent_productmgr",
    "roadmap": "agent_productmgr",
    "user stories": "agent_productmgr",
    "data engineering": "agent_dataengineer",
    "pipeline": "agent_dataengineer",
    "etl": "agent_dataengineer",
    "brand": "agent_brand",
    "brand identity": "agent_brand",
    "brand guidelines": "agent_brand",
    "ux research": "agent_uxresearch",
    "user research": "agent_uxresearch",
    "usability": "agent_uxresearch",
    "3d": "agent_3d",
    "3d visualization": "agent_3d",
    "rendering": "agent_3d",
    "pr": "agent_pr",
    "public relations": "agent_pr",
    "crisis management": "agent_pr",
    "media relations": "agent_pr",
    "procurement": "agent_procurement",
    "vendor": "agent_procurement",
    "purchasing": "agent_procurement",
    "customer experience": "agent_cx",
    "cx": "agent_cx",
    "loyalty": "agent_cx",
    "ethics": "agent_ethics",
    "governance": "agent_ethics",
    "risk": "agent_ethics",
    "knowledge": "agent_knowledge",
    "documentation": "agent_knowledge",
    "wiki": "agent_knowledge",
    "localization": "agent_localization",
    "translation": "agent_localization",
    "internationalization": "agent_localization",
    "global expansion": "agent_localization",
}


async def seed_default_agents():
    # Seed original 41 agents
    for agent_data in DEFAULT_AGENTS:
        existing = await db.agents.find_one({"agent_id": agent_data["agent_id"]})
        if not existing:
            agent_data["created_at"] = datetime.now(timezone.utc).isoformat()
            await db.agents.insert_one(agent_data)
        else:
            update_fields = {}
            # Always sync name from config (fixes renames like Arjun→Adrian, Priya→Elena)
            if existing.get("name") != agent_data["name"]:
                update_fields["name"] = agent_data["name"]
            # Only update avatar if existing one is SVG or missing (preserve CDN/photo avatars)
            existing_avatar = existing.get("avatar", "")
            if existing_avatar != agent_data["avatar"] and (not existing_avatar or existing_avatar.startswith("data:image/svg")):
                update_fields["avatar"] = agent_data["avatar"]
            if "tools" in agent_data and existing.get("tools") != agent_data.get("tools"):
                update_fields["tools"] = agent_data["tools"]
            if update_fields:
                await db.agents.update_one(
                    {"agent_id": agent_data["agent_id"]},
                    {"$set": update_fields}
                )
    logger.info("Default agents seeded")

    # Seed MAARS Infinity agents (370+ agents across 27 networks)
    from infinity_catalog import get_all_infinity_agents, get_tools_for_agent, NETWORK_TOOL_MAP
    infinity_agents = get_all_infinity_agents()
    seeded_count = 0
    for agent_data in infinity_agents:
        existing = await db.agents.find_one({"agent_id": agent_data["agent_id"]})
        if not existing:
            agent_data["created_at"] = datetime.now(timezone.utc).isoformat()
            await db.agents.insert_one(agent_data)
            seeded_count += 1
        else:
            # Update existing infinity agents with any new fields, but preserve AI-generated photo avatars
            update_fields = {}
            for field in ["network", "autonomy_tier", "authority_tier", "is_infinity", "lifecycle_state"]:
                if field in agent_data and existing.get(field) != agent_data[field]:
                    update_fields[field] = agent_data[field]
            # Refresh SVG avatars with latest generated version; preserve /api/static/ photo avatars
            existing_avatar = existing.get("avatar", "")
            if not existing_avatar or existing_avatar.startswith("data:image/svg"):
                update_fields["avatar"] = agent_data["avatar"]
            if update_fields:
                await db.agents.update_one(
                    {"agent_id": agent_data["agent_id"]},
                    {"$set": update_fields}
                )
    if seeded_count > 0:
        logger.info(f"Seeded {seeded_count} new MAARS Infinity agents")

    capability_defaults = {
        "agent_graphics": {"can_generate_image": True, "can_generate_video": False, "can_generate_pdf": True, "can_generate_files": True},
        "agent_video": {"can_generate_image": False, "can_generate_video": True, "can_generate_pdf": True, "can_generate_files": True},
        "agent_socialmedia": {"can_generate_image": True, "can_generate_video": False, "can_generate_pdf": True, "can_generate_files": True},
        "agent_contentwriter": {"can_generate_image": True, "can_generate_video": False, "can_generate_pdf": True, "can_generate_files": True},
        "agent_webdesigner": {"can_generate_image": True, "can_generate_video": False, "can_generate_pdf": True, "can_generate_files": True},
    }
    for agent_id, caps in capability_defaults.items():
        existing = await db.agents.find_one({"agent_id": agent_id})
        if existing:
            update = {}
            for field, default_val in caps.items():
                if field not in existing:
                    update[field] = default_val
            if update:
                await db.agents.update_one({"agent_id": agent_id}, {"$set": update})

    all_agents = await db.agents.find({}).to_list(50)
    for agent in all_agents:
        update = {}
        for field in ["can_generate_image", "can_generate_video", "can_generate_pdf", "can_generate_files"]:
            if field not in agent:
                update[field] = field in ("can_generate_pdf", "can_generate_files")
        if update:
            await db.agents.update_one({"agent_id": agent["agent_id"]}, {"$set": update})


async def build_workspace_context(user_id: str, current_agent_id: str) -> str:
    context_parts = []
    tasks_cursor = db.tasks.find(
        {"user_id": user_id}, {"_id": 0, "task_id": 1, "title": 1, "description": 1, "status": 1, "priority": 1, "assigned_agents": 1, "created_at": 1, "result": 1}
    ).sort("created_at", -1).limit(15)
    tasks = await tasks_cursor.to_list(15)
    if tasks:
        task_lines = []
        for t in tasks:
            assigned = ", ".join(t.get("assigned_agents", [])) or "unassigned"
            result_snippet = ""
            if t.get("result"):
                result_snippet = f" | Result: {str(t['result'])[:150]}..."
            task_lines.append(f"- [{t.get('status','pending').upper()}] {t.get('title','')} (Priority: {t.get('priority','medium')}, Assigned: {assigned}, ID: {t.get('task_id','')}){result_snippet}")
        context_parts.append("## WORKSPACE TASKS\n" + "\n".join(task_lines))

    other_chats = db.chats.find(
        {"user_id": user_id, "agent_id": {"$ne": current_agent_id, "$exists": True}},
        {"_id": 0, "agent_id": 1, "messages": {"$slice": -2}}
    ).sort("updated_at", -1).limit(8)
    summaries = []
    async for chat in other_chats:
        agent_id = chat.get("agent_id", "")
        agent_doc = await db.agents.find_one({"agent_id": agent_id}, {"_id": 0, "name": 1, "role": 1})
        agent_name = agent_doc.get("name", agent_id) if agent_doc else agent_id
        agent_role = agent_doc.get("role", "") if agent_doc else ""
        msgs = chat.get("messages", [])
        if msgs:
            last = msgs[-1]
            content_preview = str(last.get("content", ""))[:300]
            role = "User" if last.get("role") == "user" else agent_name
            summaries.append(f"- {agent_name} ({agent_role}): {role} said: \"{content_preview}\"")
    if summaries:
        context_parts.append("## RECENT TEAM ACTIVITY (Other Agents)\n" + "\n".join(summaries))

    if not context_parts:
        return ""

    return "\n\n--- SHARED WORKSPACE CONTEXT ---\n" + "\n\n".join(context_parts) + "\n--- END WORKSPACE CONTEXT ---\n\nUse this context to understand what other team members are working on and what tasks exist. Reference tasks by their ID when relevant. Collaborate with the user's goals across agents.\n"


async def log_tool_call(user_id: str, tool_name: str, tool_input: dict, result: str, duration_ms: int, status: str):
    """Log a tool invocation for observability."""
    try:
        await db.tool_logs.insert_one({
            "user_id": user_id,
            "tool_name": tool_name,
            "input_summary": {k: str(v)[:200] for k, v in tool_input.items()} if tool_input else {},
            "result_preview": str(result)[:500] if result else "",
            "duration_ms": duration_ms,
            "status": status,
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
    except Exception:
        pass


async def _get_connector_config(user_id: str, integration_id: str) -> dict:
    config_info = await get_effective_integration_config(user_id, integration_id)
    return config_info.get("config", {}) or {}


async def _store_tool_artifact(
    user_id: str,
    artifact_type: str,
    title: str,
    payload,
    source_tool: str,
    source_integration: str,
    content_type: str = "application/json",
    metadata: dict = None,
):
    try:
        await create_artifact(
            user_id=user_id,
            artifact_type=artifact_type,
            title=title,
            payload=payload,
            source_tool=source_tool,
            source_integration=source_integration,
            content_type=content_type,
            metadata=metadata or {},
        )
    except Exception as artifact_err:
        logger.warning(f"Artifact creation failed for {source_tool}: {artifact_err}")


async def _salesforce_access_token(user_id: str):
    config = await _get_connector_config(user_id, "salesforce")
    instance_url = (config.get("instance_url") or "").rstrip("/")
    client_id = config.get("client_id", "")
    client_secret = config.get("client_secret", "")
    refresh_token = config.get("refresh_token", "")
    if not all([instance_url, client_id, client_secret, refresh_token]):
        return None, None, "Salesforce is not configured. Add instance_url, client_id, client_secret, and refresh_token."

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(
            "https://login.salesforce.com/services/oauth2/token",
            data={
                "grant_type": "refresh_token",
                "client_id": client_id,
                "client_secret": client_secret,
                "refresh_token": refresh_token,
            },
        )
        if resp.status_code != 200:
            return None, None, f"Salesforce auth error: {resp.text[:200]}"
        data = resp.json()
        return data.get("access_token", ""), data.get("instance_url", instance_url), ""


async def execute_tool(tool_name: str, tool_input: dict, user_id: str) -> str:
    """Execute a tool and return the result as a string. Logs the call for observability."""
    import time

    # Check system mode - simulation mode blocks real-world actions
    REAL_WORLD_TOOLS = {
        "send_email", "send_gmail", "send_sms", "send_slack", "schedule_meeting",
        "google_calendar", "github_action", "hubspot_action", "shopify_action",
        "salesforce_action", "webhook_action",
    }
    if tool_name in REAL_WORLD_TOOLS:
        mode_config = await db.system_config.find_one({"user_id": user_id, "mode": {"$exists": True}}, {"_id": 0})
        if not mode_config or mode_config.get("mode") != "execution":
            return f"[SIMULATION MODE] Would execute '{tool_name}' with parameters: {str(tool_input)[:300]}. Switch to Execution Mode in KPI Dashboard to enable real API calls."

    start = time.time()
    status = "success"
    result = ""
    try:
        result = await _execute_tool_inner(tool_name, tool_input, user_id)
        return result
    except Exception as e:
        status = "error"
        result = str(e)[:500]
        raise
    finally:
        duration_ms = int((time.time() - start) * 1000)
        await log_tool_call(user_id, tool_name, tool_input, result, duration_ms, status)


async def _execute_tool_inner(tool_name: str, tool_input: dict, user_id: str) -> str:
    """Internal tool execution logic."""
    try:
        if tool_name == "web_search":
            query = tool_input.get("query", "")
            if not query:
                return "Error: No search query provided."
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(
                    "https://api.duckduckgo.com/",
                    params={"q": query, "format": "json", "no_html": 1, "skip_disambig": 1}
                )
                data = resp.json()
                results = []
                if data.get("AbstractText"):
                    results.append(f"Summary: {data['AbstractText']}")
                    if data.get("AbstractSource"):
                        results.append(f"Source: {data['AbstractSource']}")
                for topic in (data.get("RelatedTopics", []))[:5]:
                    if isinstance(topic, dict) and topic.get("Text"):
                        results.append(f"- {topic['Text']}")
                if not results:
                    results.append(f"Web search for '{query}' returned no instant results. Based on general knowledge, I'll provide what I know.")
                return "\n".join(results)

        elif tool_name == "calculate":
            expression = tool_input.get("expression", "")
            if not expression:
                return "Error: No expression provided."
            import ast
            import operator
            allowed_ops = {
                ast.Add: operator.add, ast.Sub: operator.sub,
                ast.Mult: operator.mul, ast.Div: operator.truediv,
                ast.Pow: operator.pow, ast.Mod: operator.mod,
                ast.USub: operator.neg, ast.UAdd: operator.pos,
            }
            def safe_eval(node):
                if isinstance(node, ast.Expression):
                    return safe_eval(node.body)
                elif isinstance(node, ast.Constant):
                    if isinstance(node.value, (int, float)):
                        return node.value
                    raise ValueError("Only numbers allowed")
                elif isinstance(node, ast.BinOp):
                    op = allowed_ops.get(type(node.op))
                    if not op:
                        raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
                    return op(safe_eval(node.left), safe_eval(node.right))
                elif isinstance(node, ast.UnaryOp):
                    op = allowed_ops.get(type(node.op))
                    if not op:
                        raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
                    return op(safe_eval(node.operand))
                raise ValueError(f"Unsupported expression: {ast.dump(node)}")
            try:
                tree = ast.parse(expression, mode='eval')
                result = safe_eval(tree)
                return f"Result: {result}"
            except Exception as e:
                return f"Calculation error: {e}. Expression: {expression}"

        elif tool_name == "create_task":
            title = tool_input.get("title", "Untitled Task")
            description = tool_input.get("description", "")
            priority = tool_input.get("priority", "medium")
            if priority not in ("low", "medium", "high"):
                priority = "medium"
            task_doc = {
                "task_id": f"task_{uuid.uuid4().hex[:12]}",
                "user_id": user_id,
                "title": title,
                "description": description,
                "status": "pending",
                "priority": priority,
                "assigned_agents": [],
                "result": None,
                "source": "agent_tool",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            await db.tasks.insert_one(task_doc)
            return f"Task created successfully: '{title}' (Priority: {priority}, ID: {task_doc['task_id']})"

        elif tool_name == "query_tasks":
            status_filter = tool_input.get("status", "")
            query = {"user_id": user_id}
            if status_filter and status_filter in ("pending", "in_progress", "completed", "cancelled"):
                query["status"] = status_filter
            cursor = db.tasks.find(query, {"_id": 0}).sort("created_at", -1).limit(20)
            tasks = await cursor.to_list(20)
            if not tasks:
                return "No tasks found."
            lines = []
            for t in tasks:
                assigned = ", ".join(t.get("assigned_agents", [])) or "unassigned"
                lines.append(f"[{t['status'].upper()}] {t['title']} | Priority: {t.get('priority','medium')} | Assigned: {assigned} | ID: {t['task_id']}\n  Description: {t.get('description','')[:200]}")
                if t.get("result"):
                    lines.append(f"  Result: {str(t['result'])[:300]}")
            return f"Found {len(tasks)} tasks:\n" + "\n".join(lines)

        elif tool_name == "update_task":
            task_id = tool_input.get("task_id", "")
            if not task_id:
                return "Error: task_id is required"
            task = await db.tasks.find_one({"task_id": task_id, "user_id": user_id}, {"_id": 0})
            if not task:
                return f"Task '{task_id}' not found."
            update = {}
            if tool_input.get("status") in ("pending", "in_progress", "completed", "cancelled"):
                update["status"] = tool_input["status"]
            if tool_input.get("result"):
                update["result"] = tool_input["result"]
            if tool_input.get("description"):
                update["description"] = tool_input["description"]
            if not update:
                return f"Task '{task_id}' found but no valid updates provided. Current: [{task['status']}] {task['title']}"
            update["updated_at"] = datetime.now(timezone.utc).isoformat()
            await db.tasks.update_one({"task_id": task_id}, {"$set": update})
            return f"Task '{task['title']}' updated: {', '.join(f'{k}={v}' for k, v in update.items() if k != 'updated_at')}"

        elif tool_name == "query_agent_history":
            target_agent = tool_input.get("agent_id", "")
            if not target_agent:
                return "Error: agent_id is required (e.g. 'agent_marketing', 'agent_projectmanager')"
            chat = await db.chats.find_one(
                {"user_id": user_id, "agent_id": target_agent},
                {"_id": 0, "messages": {"$slice": -10}}
            )
            if not chat or not chat.get("messages"):
                return f"No conversation history found with {target_agent}."
            agent_doc = await db.agents.find_one({"agent_id": target_agent}, {"_id": 0, "name": 1, "role": 1})
            agent_name = agent_doc.get("name", target_agent) if agent_doc else target_agent
            lines = [f"Recent conversation with {agent_name}:"]
            for msg in chat["messages"]:
                role = "User" if msg.get("role") == "user" else agent_name
                lines.append(f"  {role}: {str(msg.get('content',''))[:400]}")
            return "\n".join(lines)

        elif tool_name == "analyze_data":
            data_str = tool_input.get("data", "")
            question = tool_input.get("question", "Summarize the data")
            if not data_str:
                return "Error: No data provided to analyze."
            lines = data_str.strip().split("\n")
            numbers = []
            for line in lines:
                for part in line.replace(",", " ").split():
                    try:
                        numbers.append(float(part))
                    except ValueError:
                        pass
            analysis = [f"Data has {len(lines)} lines."]
            if numbers:
                analysis.append(f"Found {len(numbers)} numbers: min={min(numbers)}, max={max(numbers)}, avg={sum(numbers)/len(numbers):.2f}, sum={sum(numbers):.2f}")
            analysis.append(f"Analysis question: {question}")
            return "\n".join(analysis)

        elif tool_name == "send_slack":
            slack_config = await _get_connector_config(user_id, "slack")
            token = slack_config.get("bot_token", "")
            if not token:
                return "Slack is not configured. Ask your admin to add a Slack Bot Token in the Integrations panel."
            channel = tool_input.get("channel", "#general").lstrip("#")
            message = tool_input.get("message", "")
            if not message:
                return "Error: No message provided."
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(
                    "https://slack.com/api/chat.postMessage",
                    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                    json={"channel": channel, "text": message}
                )
                data = resp.json()
                if data.get("ok"):
                    await _store_tool_artifact(
                        user_id,
                        "message",
                        f"Slack message to #{channel}",
                        {"channel": channel, "message": message, "response": data},
                        "send_slack",
                        "slack",
                    )
                    return f"Message sent to #{channel} successfully."
                return f"Slack error: {data.get('error', 'Unknown error')}"

        elif tool_name == "send_email":
            sendgrid_config = await _get_connector_config(user_id, "sendgrid")
            resend_config = await _get_connector_config(user_id, "resend")
            sg_key = sendgrid_config.get("api_key", "")
            resend_key = resend_config.get("api_key", "")
            to_email = tool_input.get("to", "")
            subject = tool_input.get("subject", "No Subject")
            body = tool_input.get("body", "")
            if not to_email:
                return "Error: No recipient email provided."
            if sg_key:
                async with httpx.AsyncClient(timeout=10) as client:
                    resp = await client.post(
                        "https://api.sendgrid.com/v3/mail/send",
                        headers={"Authorization": f"Bearer {sg_key}", "Content-Type": "application/json"},
                        json={"personalizations": [{"to": [{"email": to_email}]}], "from": {"email": "noreply@maarsglobal.com"}, "subject": subject, "content": [{"type": "text/html", "value": body}]}
                    )
                    if resp.status_code in (200, 201, 202):
                        await _store_tool_artifact(
                            user_id,
                            "email",
                            f"Email to {to_email}",
                            {"to": to_email, "subject": subject, "provider": "sendgrid"},
                            "send_email",
                            "sendgrid",
                        )
                        return f"Email sent to {to_email} via SendGrid successfully."
                    return f"SendGrid error: {resp.status_code} - {resp.text[:200]}"
            elif resend_key:
                async with httpx.AsyncClient(timeout=10) as client:
                    resp = await client.post(
                        "https://api.resend.com/emails",
                        headers={"Authorization": f"Bearer {resend_key}", "Content-Type": "application/json"},
                        json={"from": "noreply@maarsglobal.com", "to": [to_email], "subject": subject, "html": body}
                    )
                    if resp.status_code in (200, 201):
                        await _store_tool_artifact(
                            user_id,
                            "email",
                            f"Email to {to_email}",
                            {"to": to_email, "subject": subject, "provider": "resend"},
                            "send_email",
                            "resend",
                        )
                        return f"Email sent to {to_email} via Resend successfully."
                    return f"Resend error: {resp.status_code} - {resp.text[:200]}"
            return "Email service not configured. Ask your admin to add SendGrid or Resend API key in Integrations."

        elif tool_name == "send_sms":
            twilio_config = await _get_connector_config(user_id, "twilio")
            sid = twilio_config.get("account_sid", "")
            auth = twilio_config.get("auth_token", "")
            from_phone = twilio_config.get("phone_number", "")
            if not sid or not auth:
                return "Twilio is not configured. Ask your admin to add Twilio credentials in the Integrations panel."
            to_phone = tool_input.get("to", "")
            sms_body = tool_input.get("message", "")
            if not to_phone or not sms_body:
                return "Error: Phone number and message are required."
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(
                    f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json",
                    auth=(sid, auth),
                    data={"To": to_phone, "From": from_phone, "Body": sms_body[:160]}
                )
                data = resp.json()
                if resp.status_code in (200, 201):
                    await _store_tool_artifact(
                        user_id,
                        "sms",
                        f"SMS to {to_phone}",
                        {"to": to_phone, "message": sms_body[:160], "sid": data.get("sid", "")},
                        "send_sms",
                        "twilio",
                    )
                    return f"SMS sent to {to_phone} successfully. SID: {data.get('sid', 'N/A')}"
                return f"Twilio error: {data.get('message', resp.text[:200])}"

        elif tool_name == "github_action":
            github_config = await _get_connector_config(user_id, "github")
            token = github_config.get("personal_access_token", "")
            if not token:
                return "GitHub is not configured. Ask your admin to add a GitHub Personal Access Token in Integrations."
            action = tool_input.get("action", "list_repos")
            repo = tool_input.get("repo", "")
            headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
            async with httpx.AsyncClient(timeout=10) as client:
                if action == "create_issue":
                    if not repo:
                        return "Error: repo (owner/repo) is required."
                    resp = await client.post(f"https://api.github.com/repos/{repo}/issues", headers=headers, json={"title": tool_input.get("title", "New Issue"), "body": tool_input.get("body", "")})
                    if resp.status_code == 201:
                        data = resp.json()
                        await _store_tool_artifact(
                            user_id,
                            "github_issue",
                            f"{repo} issue #{data['number']}",
                            data,
                            "github_action",
                            "github",
                        )
                        return f"Issue created: #{data['number']} - {data['title']} ({data['html_url']})"
                    return f"GitHub error: {resp.status_code} - {resp.text[:200]}"
                elif action == "list_issues":
                    if not repo:
                        return "Error: repo (owner/repo) is required."
                    resp = await client.get(f"https://api.github.com/repos/{repo}/issues?per_page=10", headers=headers)
                    issues = resp.json()
                    if isinstance(issues, list):
                        return "\n".join([f"#{i['number']} [{i['state']}] {i['title']}" for i in issues[:10]])
                    return f"GitHub error: {resp.text[:200]}"
                elif action == "list_repos":
                    resp = await client.get("https://api.github.com/user/repos?per_page=10&sort=updated", headers=headers)
                    repos = resp.json()
                    if isinstance(repos, list):
                        return "\n".join([f"{r['full_name']} - {r.get('description', 'No description')}" for r in repos[:10]])
                    return f"GitHub error: {resp.text[:200]}"
                elif action == "search_code":
                    q = tool_input.get("body", tool_input.get("title", ""))
                    resp = await client.get(f"https://api.github.com/search/code?q={q}&per_page=5", headers=headers)
                    data = resp.json()
                    items = data.get("items", [])
                    return "\n".join([f"{it['repository']['full_name']}/{it['path']}" for it in items[:5]]) or "No results found."
            return "Unknown GitHub action."

        elif tool_name == "airtable_action":
            airtable_config = await _get_connector_config(user_id, "airtable")
            token = airtable_config.get("api_key", "")
            if not token:
                return "Airtable is not configured. Ask your admin to add an Airtable API key in Integrations."
            action = tool_input.get("action", "list_records")
            base_id = tool_input.get("base_id", "")
            table_name = tool_input.get("table_name", "")
            if not base_id or not table_name:
                return "Error: base_id and table_name are required."
            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
            async with httpx.AsyncClient(timeout=10) as client:
                if action == "list_records":
                    resp = await client.get(f"https://api.airtable.com/v0/{base_id}/{table_name}?maxRecords=10", headers=headers)
                    data = resp.json()
                    records = data.get("records", [])
                    return "\n".join([str(r.get("fields", {})) for r in records[:10]]) or "No records found."
                elif action == "create_record":
                    fields = tool_input.get("fields", {})
                    resp = await client.post(f"https://api.airtable.com/v0/{base_id}/{table_name}", headers=headers, json={"records": [{"fields": fields}]})
                    if resp.status_code == 200:
                        await _store_tool_artifact(
                            user_id,
                            "record",
                            f"Airtable record in {table_name}",
                            resp.json(),
                            "airtable_action",
                            "airtable",
                        )
                        return "Record created successfully."
                    return f"Airtable error: {resp.text[:200]}"
            return "Unknown Airtable action."

        elif tool_name == "search_gif":
            giphy_config = await _get_connector_config(user_id, "giphy")
            token = giphy_config.get("api_key", "")
            if not token:
                return "Giphy is not configured. Ask your admin to add a Giphy API key in Integrations."
            query = tool_input.get("query", "")
            if not query:
                return "Error: No search query provided."
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get("https://api.giphy.com/v1/gifs/search", params={"api_key": token, "q": query, "limit": 3, "rating": "g"})
                data = resp.json()
                gifs = data.get("data", [])
                if gifs:
                    return "\n".join([f"![{g['title']}]({g['images']['fixed_height']['url']})" for g in gifs[:3]])
                return "No GIFs found."

        elif tool_name == "schedule_meeting":
            calendly_config = await _get_connector_config(user_id, "calendly")
            token = calendly_config.get("api_key", "")
            if not token:
                return "Calendly is not configured. Ask your admin to add a Calendly API key in Integrations."
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get("https://api.calendly.com/users/me", headers={"Authorization": f"Bearer {token}"})
                if resp.status_code == 200:
                    user_data = resp.json()
                    scheduling_url = user_data.get("resource", {}).get("scheduling_url", "")
                    await _store_tool_artifact(
                        user_id,
                        "scheduling_link",
                        "Calendly scheduling link",
                        {"scheduling_url": scheduling_url},
                        "schedule_meeting",
                        "calendly",
                    )
                    return f"Calendly scheduling link: {scheduling_url}\nShare this with participants to schedule a meeting."
                return f"Calendly error: {resp.text[:200]}"

        elif tool_name == "google_calendar":
            google_config = await _get_connector_config(user_id, "google_suite")
            svc_json = google_config.get("service_account_json", "")
            if not svc_json:
                return "Google Suite is not configured. Ask your admin to add Google Suite credentials in Integrations."
            delegate_email = google_config.get("delegate_email", "")
            action = tool_input.get("action", "list_events")
            try:
                import json as _json
                from google.oauth2 import service_account as _sa
                from googleapiclient.discovery import build as _build
                scopes = ["https://www.googleapis.com/auth/calendar"]
                info = _json.loads(svc_json) if isinstance(svc_json, str) else svc_json
                creds = _sa.Credentials.from_service_account_info(info, scopes=scopes)
                if delegate_email:
                    creds = creds.with_subject(delegate_email)
                service = _build("calendar", "v3", credentials=creds)
                if action == "create_event":
                    summary = tool_input.get("title", tool_input.get("summary", "New Event"))
                    start = tool_input.get("start", "")
                    end = tool_input.get("end", "")
                    description = tool_input.get("description", "")
                    attendees = tool_input.get("attendees", "")
                    event_body = {"summary": summary, "description": description}
                    if start:
                        event_body["start"] = {"dateTime": start, "timeZone": "UTC"}
                    if end:
                        event_body["end"] = {"dateTime": end, "timeZone": "UTC"}
                    elif start:
                        event_body["end"] = event_body["start"]
                    if attendees:
                        emails = [e.strip() for e in attendees.split(",") if e.strip()]
                        event_body["attendees"] = [{"email": e} for e in emails]
                    result = service.events().insert(calendarId="primary", body=event_body).execute()
                    await _store_tool_artifact(
                        user_id,
                        "calendar_event",
                        result.get("summary", "Calendar event"),
                        result,
                        "google_calendar",
                        "google_suite",
                    )
                    return f"Event created: {result.get('summary')} on {result.get('start', {}).get('dateTime', 'N/A')}\nLink: {result.get('htmlLink', '')}"
                else:
                    from datetime import datetime as _dt, timezone as _tz
                    now = _dt.now(_tz.utc).isoformat()
                    max_results = int(tool_input.get("max_results", 10))
                    results = service.events().list(
                        calendarId="primary", timeMin=now,
                        maxResults=max_results, singleEvents=True, orderBy="startTime"
                    ).execute()
                    events = results.get("items", [])
                    if not events:
                        return "No upcoming events found."
                    lines = [f"Upcoming {len(events)} events:"]
                    for ev in events:
                        start_dt = ev["start"].get("dateTime", ev["start"].get("date", ""))
                        lines.append(f"- {ev.get('summary', 'No title')} | {start_dt}")
                    return "\n".join(lines)
            except Exception as cal_err:
                logger.error(f"Google Calendar error: {cal_err}")
                return f"Google Calendar error: {str(cal_err)[:200]}"

        elif tool_name == "send_gmail":
            google_config = await _get_connector_config(user_id, "google_suite")
            svc_json = google_config.get("service_account_json", "")
            if not svc_json:
                return "Google Suite is not configured. Ask your admin to add Google Suite credentials in Integrations."
            delegate_email = google_config.get("delegate_email", "")
            if not delegate_email:
                return "Gmail requires a Delegate Email in Google Suite settings. Ask your admin to add the sender email in Admin > Integrations."
            to_email = tool_input.get("to", "")
            subject = tool_input.get("subject", "No Subject")
            body = tool_input.get("body", "")
            if not to_email:
                return "Error: No recipient email provided."
            try:
                import json as _json
                import base64 as _b64
                from email.mime.text import MIMEText as _MIMEText
                from google.oauth2 import service_account as _sa
                from googleapiclient.discovery import build as _build
                scopes = ["https://www.googleapis.com/auth/gmail.send"]
                info = _json.loads(svc_json) if isinstance(svc_json, str) else svc_json
                creds = _sa.Credentials.from_service_account_info(info, scopes=scopes)
                creds = creds.with_subject(delegate_email)
                service = _build("gmail", "v1", credentials=creds)
                message = _MIMEText(body, "html")
                message["to"] = to_email
                message["from"] = delegate_email
                message["subject"] = subject
                raw = _b64.urlsafe_b64encode(message.as_bytes()).decode()
                result = service.users().messages().send(userId="me", body={"raw": raw}).execute()
                await _store_tool_artifact(
                    user_id,
                    "email",
                    f"Gmail to {to_email}",
                    {"to": to_email, "subject": subject, "message_id": result.get("id", "")},
                    "send_gmail",
                    "google_suite",
                )
                return f"Email sent to {to_email} via Gmail. Message ID: {result.get('id', 'N/A')}"
            except Exception as gmail_err:
                logger.error(f"Gmail error: {gmail_err}")
                return f"Gmail error: {str(gmail_err)[:200]}"

        elif tool_name == "webhook_action":
            webhook_config = await _get_connector_config(user_id, "webhooks")
            webhook_url = tool_input.get("webhook_url") or webhook_config.get("webhook_url")
            signing_secret = webhook_config.get("signing_secret", "")
            if not webhook_url:
                return "Webhook automation is not configured. Add a webhook_url in Webhooks."
            method = str(tool_input.get("method", "POST")).upper()
            payload = tool_input.get("payload", tool_input.get("body", {}))
            headers = dict(tool_input.get("headers", {}) or {})
            if signing_secret:
                headers.setdefault("X-MAARS-Signature", signing_secret)
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.request(
                    method,
                    webhook_url,
                    json=payload if isinstance(payload, (dict, list)) else None,
                    content=payload if isinstance(payload, str) else None,
                    headers=headers,
                )
                response_preview = resp.text[:300]
                await _store_tool_artifact(
                    user_id,
                    "webhook_delivery",
                    f"Webhook {method} delivery",
                    {
                        "url": webhook_url,
                        "method": method,
                        "status_code": resp.status_code,
                        "response_preview": response_preview,
                    },
                    "webhook_action",
                    "webhooks",
                )
                return f"Webhook {method} sent to {webhook_url}. Status: {resp.status_code}. Response: {response_preview}"

        elif tool_name == "hubspot_action":
            hubspot_config = await _get_connector_config(user_id, "hubspot")
            token = hubspot_config.get("access_token", "")
            if not token:
                return "HubSpot is not configured. Add an access_token in the Integration Hub."
            action = tool_input.get("action", "list_contacts")
            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
            async with httpx.AsyncClient(timeout=15) as client:
                if action == "list_contacts":
                    resp = await client.get(
                        "https://api.hubapi.com/crm/v3/objects/contacts",
                        headers=headers,
                        params={"limit": int(tool_input.get("limit", 10)), "properties": "firstname,lastname,email,company"},
                    )
                    data = resp.json()
                    results = data.get("results", [])
                    if resp.status_code != 200:
                        return f"HubSpot error: {resp.text[:200]}"
                    await _store_tool_artifact(
                        user_id,
                        "crm_export",
                        "HubSpot contacts",
                        data,
                        "hubspot_action",
                        "hubspot",
                    )
                    lines = []
                    for item in results[:10]:
                        props = item.get("properties", {})
                        lines.append(f"- {props.get('firstname', '')} {props.get('lastname', '')}".strip() + f" <{props.get('email', 'no-email')}>")
                    return "\n".join(lines) or "No HubSpot contacts found."
                elif action == "create_contact":
                    properties = tool_input.get("properties", {})
                    if not properties.get("email"):
                        return "HubSpot create_contact requires properties.email."
                    resp = await client.post(
                        "https://api.hubapi.com/crm/v3/objects/contacts",
                        headers=headers,
                        json={"properties": properties},
                    )
                    if resp.status_code not in (200, 201):
                        return f"HubSpot error: {resp.text[:200]}"
                    data = resp.json()
                    await _store_tool_artifact(
                        user_id,
                        "crm_record",
                        f"HubSpot contact {properties.get('email')}",
                        data,
                        "hubspot_action",
                        "hubspot",
                    )
                    return f"HubSpot contact created: {properties.get('email')} (id: {data.get('id', 'N/A')})"
            return "Unknown HubSpot action."

        elif tool_name == "shopify_action":
            shopify_config = await _get_connector_config(user_id, "shopify")
            store_url = (shopify_config.get("store_url") or "").rstrip("/")
            access_token = shopify_config.get("access_token", "")
            api_version = tool_input.get("api_version", "2025-01")
            if not store_url or not access_token:
                return "Shopify is not configured. Add store_url and access_token in the Integration Hub."
            headers = {"X-Shopify-Access-Token": access_token, "Content-Type": "application/json"}
            action = tool_input.get("action", "list_products")
            async with httpx.AsyncClient(timeout=15) as client:
                if action == "list_products":
                    resp = await client.get(
                        f"{store_url}/admin/api/{api_version}/products.json",
                        headers=headers,
                        params={"limit": int(tool_input.get("limit", 10))},
                    )
                    if resp.status_code != 200:
                        return f"Shopify error: {resp.text[:200]}"
                    data = resp.json()
                    await _store_tool_artifact(
                        user_id,
                        "catalog_export",
                        "Shopify products",
                        data,
                        "shopify_action",
                        "shopify",
                    )
                    products = data.get("products", [])
                    return "\n".join([f"- {p.get('title', 'Untitled')} (id: {p.get('id')})" for p in products]) or "No products found."
                elif action == "create_product":
                    product = tool_input.get("product", {})
                    if not product.get("title"):
                        return "Shopify create_product requires product.title."
                    resp = await client.post(
                        f"{store_url}/admin/api/{api_version}/products.json",
                        headers=headers,
                        json={"product": product},
                    )
                    if resp.status_code not in (200, 201):
                        return f"Shopify error: {resp.text[:200]}"
                    data = resp.json()
                    await _store_tool_artifact(
                        user_id,
                        "catalog_item",
                        product.get("title", "Shopify product"),
                        data,
                        "shopify_action",
                        "shopify",
                    )
                    created = data.get("product", {})
                    return f"Shopify product created: {created.get('title', product.get('title'))} (id: {created.get('id', 'N/A')})"
            return "Unknown Shopify action."

        elif tool_name == "salesforce_action":
            access_token, instance_url, auth_error = await _salesforce_access_token(user_id)
            if auth_error:
                return auth_error
            action = tool_input.get("action", "query_accounts")
            headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
            async with httpx.AsyncClient(timeout=15) as client:
                if action == "query_accounts":
                    soql = tool_input.get("soql", "SELECT Id, Name, Industry FROM Account ORDER BY LastModifiedDate DESC LIMIT 10")
                    resp = await client.get(
                        f"{instance_url}/services/data/v60.0/query",
                        headers=headers,
                        params={"q": soql},
                    )
                    if resp.status_code != 200:
                        return f"Salesforce error: {resp.text[:200]}"
                    data = resp.json()
                    await _store_tool_artifact(
                        user_id,
                        "crm_export",
                        "Salesforce query result",
                        data,
                        "salesforce_action",
                        "salesforce",
                    )
                    records = data.get("records", [])
                    return "\n".join([f"- {r.get('Name', 'Untitled')} ({r.get('Id', '')})" for r in records]) or "No Salesforce records found."
                elif action == "create_lead":
                    lead = tool_input.get("lead", {})
                    if not lead.get("LastName") or not lead.get("Company"):
                        return "Salesforce create_lead requires lead.LastName and lead.Company."
                    resp = await client.post(
                        f"{instance_url}/services/data/v60.0/sobjects/Lead",
                        headers=headers,
                        json=lead,
                    )
                    if resp.status_code not in (200, 201):
                        return f"Salesforce error: {resp.text[:200]}"
                    data = resp.json()
                    await _store_tool_artifact(
                        user_id,
                        "crm_record",
                        f"Salesforce lead {lead.get('Company')}",
                        data,
                        "salesforce_action",
                        "salesforce",
                    )
                    return f"Salesforce lead created. ID: {data.get('id', 'N/A')}"
            return "Unknown Salesforce action."

        elif tool_name == "product_scan":
            product_query = tool_input.get("product_query", "")
            if not product_query:
                return "Error: No product query provided. Specify the product name/brand/model to scan."
            try:
                from services.product_scanner import scan_product
                result = await scan_product(product_query, UPLOAD_DIR)
                await _store_tool_artifact(
                    user_id,
                    "research_brief",
                    f"Product scan: {product_query}",
                    result,
                    "product_scan",
                    "web_search",
                )
                context = result.get("context", "")
                ref_path = result.get("reference_image_path")
                images = result.get("images", [])
                output_parts = [context]
                if ref_path:
                    output_parts.append(f"\n[Downloaded high-res reference image: {ref_path}]")
                if images:
                    output_parts.append(f"\nFound {len(images)} professional product images for reference.")
                    for i, img in enumerate(images[:4], 1):
                        output_parts.append(f"  Image {i}: {img['url']}")
                return "\n".join(output_parts)
            except Exception as scan_err:
                logger.error(f"Product scan error: {scan_err}")
                return f"Product scan failed: {str(scan_err)[:200]}. Try a web_search instead."

        return f"Unknown tool: {tool_name}"
    except Exception as e:
        return f"Tool execution error ({tool_name}): {str(e)[:200]}"


async def build_tool_prompt_async(tools: list, user_id: str) -> str:
    if not tools:
        return ""
    alternative_requirements = {
        "send_email": ["sendgrid", "resend"],
        "webhook_action": ["webhooks"],
    }
    tool_descriptions = []
    available_tools = []
    for tool_name in tools:
        tool = AGENT_TOOLS.get(tool_name)
        if not tool:
            continue
        requires = tool.get("requires")
        if requires:
            requirement_ids = alternative_requirements.get(tool_name, [requires])
            has_key = False
            for requirement_id in requirement_ids:
                service_config = (await get_effective_integration_config(user_id, requirement_id)).get("config", {})
                service_def = INTEGRATION_SERVICES.get(requirement_id, {})
                if any(service_config.get(f) for f in service_def.get("key_fields", [])):
                    has_key = True
                    break
            if not has_key:
                continue
        tool_descriptions.append(f"  - {tool['name']}: {tool['description']} | Parameters: {tool['parameters']}")
        available_tools.append(tool_name)
    if not tool_descriptions:
        return ""
    return f"""

You are an autonomous AI agent with access to tools. When a task requires real-time data, calculations, or actions, you MUST use your tools.

AVAILABLE TOOLS:
{chr(10).join(tool_descriptions)}

HOW TO USE A TOOL — output this exact format on a single line:
[TOOL_CALL] tool_name | {{"param1": "value1"}}

RULES:
1. When the user asks to search, look up, or find current info -> use web_search
2. When the user needs math, percentages, or number crunching -> use calculate
3. When the user asks to create, add, or track a task -> use create_task
4. When data analysis is needed -> use analyze_data
5. When the user asks to send a message to Slack -> use send_slack
6. When the user asks to send an email -> use send_email
7. When the user asks to send a text/SMS -> use send_sms
8. When the user asks about GitHub repos/issues -> use github_action
9. When the user asks for CRM work like contacts, leads, or accounts -> use hubspot_action or salesforce_action
10. When the user asks for ecommerce catalog or store operations -> use shopify_action
11. When the user asks to trigger an automation or webhook -> use webhook_action
12. When the user references tasks, to-dos, or shared work -> use query_tasks first
13. When the user asks about what another team member/agent discussed -> use query_agent_history
14. When the user asks to update, complete, or change a task -> use update_task
15. For questions you can fully answer from memory, respond directly
16. After receiving a tool result, weave it naturally into your final answer"""


async def build_brain_context(user_id: str, agent_id: str) -> str:
    """Build context from the agent's Custom Brain Profile."""
    # Check user-specific brain first
    brain = await db.agent_brains.find_one(
        {"user_id": user_id, "agent_id": agent_id}, {"_id": 0}
    )
    if not brain:
        brain = DEFAULT_BRAIN_PROFILES.get(agent_id, {})
    if not brain:
        return ""

    parts = []
    if brain.get("communication_style"):
        parts.append(f"Communication Style: {brain['communication_style']}")
    if brain.get("kpis"):
        parts.append(f"Your KPIs: {', '.join(brain['kpis'])}")
    if brain.get("escalation_rules"):
        parts.append(f"Escalation Rules: {'; '.join(brain['escalation_rules'])}")
    if brain.get("risk_boundaries"):
        rb = brain["risk_boundaries"]
        if rb.get("max_budget_authority"):
            parts.append(f"Budget Authority: Up to ${rb['max_budget_authority']:,}")
        if rb.get("can_approve_external_comms"):
            parts.append("You CAN approve and send external communications")
        else:
            parts.append("External communications require user approval")
    if brain.get("output_templates"):
        parts.append(f"Preferred Output Formats: {', '.join(brain['output_templates'])}")
    autonomy = brain.get("autonomy_level", 3)
    autonomy_desc = {0: "No autonomy - ask before every action", 1: "Minimal - ask before most actions",
                     2: "Low - ask before important actions", 3: "Medium - act on routine, ask on important",
                     4: "High - act independently, report results", 5: "Full autonomy - execute without asking"}
    parts.append(f"Autonomy Level: {autonomy}/5 ({autonomy_desc.get(autonomy, 'Medium')})")

    if not parts:
        return ""
    return "\n\n--- CUSTOM BRAIN PROFILE ---\n" + "\n".join(parts) + "\n--- END BRAIN PROFILE ---\n"


async def agent_execute_with_tools(
    agent: dict, user_content: str, chat_id: str, api_keys: dict,
    model_provider: str, model_name: str, user_id: str, attachments: list = None
) -> dict:
    agent_tools = AGENT_TOOL_MAP.get(agent.get("agent_id", ""), [])
    if not agent_tools:
        return None

    tool_prompt = await build_tool_prompt_async(agent_tools, user_id)
    enhanced_system_prompt = agent["system_prompt"] + CLARIFICATION_INSTRUCTION + tool_prompt

    workspace_ctx = await build_workspace_context(user_id, agent.get("agent_id", ""))
    if workspace_ctx:
        enhanced_system_prompt += workspace_ctx

    brain_ctx = await build_brain_context(user_id, agent.get("agent_id", ""))
    if brain_ctx:
        enhanced_system_prompt += brain_ctx

    user_override = await db.user_agent_overrides.find_one(
        {"user_id": user_id, "agent_id": agent.get("agent_id")}, {"_id": 0}
    )
    if user_override:
        override_parts = []
        if user_override.get("personality_tone"):
            override_parts.append(f"User-requested personality adjustment: {user_override['personality_tone']}")
        if user_override.get("custom_instructions"):
            override_parts.append(f"User-specific instructions: {user_override['custom_instructions']}")
        if override_parts:
            enhanced_system_prompt += "\n\n--- USER CUSTOMIZATION ---\n" + "\n".join(override_parts)

    execution_steps = []
    max_iterations = 4
    accumulated_context = f"User: {user_content}"
    if attachments:
        accumulated_context += f"\n[User attached {len(attachments)} file(s)]"

    final_response = ""

    for iteration in range(max_iterations):
        try:
            # Route every tool-loop iteration through the Universal Gateway.
            from services.llm_gateway import complete
            gw_model = "maars/auto" if model_provider in ("auto", None) else f"{model_provider}/{model_name}"
            gw_resp = await complete(
                user_id=user_id,
                messages=[
                    {"role": "system", "content": enhanced_system_prompt},
                    {"role": "user",   "content": accumulated_context},
                ],
                model=gw_model,
                source=f"agent.tool_loop:{agent.get('agent_id','?')}:iter_{iteration}",
            )
            llm_response = gw_resp["choices"][0]["message"]["content"]
            maars_meta = gw_resp.get("maars", {})
            model_provider = maars_meta.get("provider", model_provider)
            actual_m = maars_meta.get("model", gw_model)
            if "/" in actual_m:
                _, model_name = actual_m.split("/", 1)
        except Exception as e:
            logger.error(f"Agent tool loop LLM error (iter {iteration}): {e}")
            if not final_response:
                final_response = f"I apologize, but I encountered an error: {str(e)}"
            break

        tool_match = re.search(r'\[TOOL_CALL\]\s*(\w+)\s*\|\s*(\{.*?\})', llm_response, re.DOTALL)
        if not tool_match:
            tool_match = re.search(r'TOOL_CALL:\s*(\w+)\s*\|\s*(\{.*?\})', llm_response, re.DOTALL)
        if not tool_match:
            tool_match = re.search(r'\[TOOL\]\s*(\w+)\s*\|\s*(\{.*?\})', llm_response, re.DOTALL)

        if tool_match:
            tool_name = tool_match.group(1).strip()
            tool_input_str = tool_match.group(2).strip()
            thinking_text = llm_response[:tool_match.start()].strip()
            if thinking_text:
                execution_steps.append({"step_type": "thinking", "content": thinking_text})
            try:
                tool_input = json.loads(tool_input_str)
            except json.JSONDecodeError:
                tool_input = {"query": tool_input_str}
            if tool_name not in agent_tools:
                execution_steps.append({"step_type": "tool_error", "tool_name": tool_name, "content": f"Tool '{tool_name}' is not available."})
                accumulated_context += f"\n\nSystem: Tool '{tool_name}' is not available. Please use one of: {', '.join(agent_tools)}. Or respond directly."
                continue
            execution_steps.append({"step_type": "tool_call", "tool_name": tool_name, "tool_input": tool_input})
            tool_result = await execute_tool(tool_name, tool_input, user_id)
            execution_steps.append({"step_type": "tool_result", "tool_name": tool_name, "content": tool_result})
            accumulated_context += f"\n\nAssistant: {thinking_text}\n[Used tool: {tool_name}]\n\nTool Result ({tool_name}):\n{tool_result}\n\nNow incorporate this tool result into your response to the user. Do NOT use another tool call unless absolutely necessary. Provide your final answer."
        else:
            final_response = llm_response
            break

    if not final_response and execution_steps:
        final_response = "Based on my analysis, here's what I found:\n\n"
        for step in execution_steps:
            if step["step_type"] == "tool_result":
                final_response += f"{step['content']}\n\n"

    if not final_response:
        final_response = "I encountered an issue while processing your request. Please try again."

    return {"content": final_response, "execution_steps": execution_steps if execution_steps else None}


async def background_commander_delegate(goal: str, chat_id: str, msg_id: str, api_keys: dict, user_id: str):
    try:
        result = await commander_delegate(goal, chat_id, api_keys, user_id, msg_id)
        await db.chats.update_one(
            {"chat_id": chat_id, "messages.message_id": msg_id},
            {"$set": {
                "messages.$.content": result["content"],
                "messages.$.delegation_data": result.get("delegation_data"),
                "messages.$.commander_status": "complete"
            }}
        )
        logger.info(f"Commander delegation complete for chat {chat_id}")
    except Exception as e:
        logger.error(f"Background commander delegation failed: {e}")
        await db.chats.update_one(
            {"chat_id": chat_id, "messages.message_id": msg_id},
            {"$set": {
                "messages.$.content": f"I encountered an issue while coordinating the specialists. Please try again.\n\nError: {str(e)[:200]}",
                "messages.$.commander_status": "error"
            }}
        )


async def commander_delegate(goal: str, chat_id: str, api_keys: dict, user_id: str, msg_id: str = None) -> dict:
    async def update_progress(phase, agents_progress=None, current_agent=None):
        if not msg_id:
            return
        progress = {"phase": phase, "agents": agents_progress or [], "current_agent": current_agent}
        await db.chats.update_one(
            {"chat_id": chat_id, "messages.message_id": msg_id},
            {"$set": {"messages.$.delegation_progress": progress}}
        )

    await update_progress("planning")

    plan_prompt = f"""You are Commander Orion. A user has given you this goal:

"{goal}"

Analyze this goal and create a delegation plan. Return ONLY a JSON array of sub-tasks in this exact format:
[
  {{"task": "Brief task description", "agent_role": "one of: marketing, strategy, web design, development, copywriting, seo, sales, social media, data, content, customer service, project management, research, finance, hr, graphic design, legal, email, video, secretary", "priority": "high or medium or low", "title": "Short task title for tracking"}},
  ...
]

Choose 2-4 most relevant specialists. Be specific about what each should do. Assign priority based on urgency and importance. Return ONLY the JSON array, no other text."""

    try:
        from services.llm_gateway import complete_text
        plan_text = await complete_text(
            user_id=user_id,
            system_prompt="You are a task planning AI. Output only valid JSON arrays.",
            user_prompt=plan_prompt,
            model="maars/auto",
            source="agent.commander_plan",
        )
        plan_text_clean = plan_text.strip()
        if plan_text_clean.startswith("```"):
            plan_text_clean = plan_text_clean.split("\n", 1)[1] if "\n" in plan_text_clean else plan_text_clean[3:]
        if plan_text_clean.endswith("```"):
            plan_text_clean = plan_text_clean[:-3]
        plan_text_clean = plan_text_clean.strip()
        tasks = json.loads(plan_text_clean)
    except Exception as e:
        logger.error(f"Commander planning error: {e}")
        fallback = f"I analyzed your goal: \"{goal}\"\n\nI encountered an issue breaking this down automatically. Let me provide my strategic assessment instead:\n\nThis goal would benefit from a multi-disciplinary approach. I recommend starting with research and strategy, then moving to execution. Would you like me to try again, or shall I connect you with a specific specialist?"
        return {"content": fallback, "delegation_data": None}

    created_tasks = []
    now = datetime.now(timezone.utc).isoformat()
    agents_progress = []

    from services.agents import agent_router_map
    for i, task_item in enumerate(tasks):
        task_desc = task_item.get("task", "")
        agent_role = task_item.get("agent_role", "").lower()
        try:
            agent_id = await agent_router_map.resolve(agent_role)
        except Exception:
            agent_id = AGENT_ROLE_MAP.get(agent_role, "agent_strategist")
        priority = task_item.get("priority", "medium").lower()
        if priority not in ("high", "medium", "low"):
            priority = "medium"
        title = task_item.get("title", task_desc[:60])

        task_doc = {
            "task_id": f"task_{uuid.uuid4().hex[:12]}",
            "user_id": user_id,
            "title": title,
            "description": task_desc,
            "status": "pending",
            "priority": priority,
            "assigned_agents": [agent_id],
            "result": None,
            "source": "commander",
            "source_goal": goal[:200],
            "created_at": now,
            "updated_at": now,
        }
        await db.tasks.insert_one(task_doc)

        agent_doc = await db.agents.find_one({"agent_id": agent_id}, {"_id": 0, "agent_id": 1, "name": 1, "avatar": 1, "role": 1})
        agents_progress.append({
            "agent_id": agent_id,
            "agent_name": agent_doc.get("name", "Agent") if agent_doc else "Agent",
            "agent_avatar": agent_doc.get("avatar", "") if agent_doc else "",
            "agent_role": agent_doc.get("role", "Specialist") if agent_doc else "Specialist",
            "task_title": title,
            "priority": priority,
            "status": "pending"
        })
        created_tasks.append({"task_id": task_doc["task_id"], "title": title, "agent_id": agent_id, "priority": priority, "desc": task_desc})

    await update_progress("delegating", agents_progress)
    delegation_agents = []

    for i, ct in enumerate(created_tasks):
        agent = await db.agents.find_one({"agent_id": ct["agent_id"]}, {"_id": 0})
        if not agent:
            continue
        if i < len(agents_progress):
            agents_progress[i]["status"] = "working"
            await update_progress("delegating", agents_progress, agents_progress[i]["agent_name"])

        agent_entry = {
            "agent_id": ct["agent_id"],
            "agent_name": agent.get("name", "Agent"),
            "agent_role": agent.get("role", "Specialist"),
            "agent_avatar": agent.get("avatar", ""),
            "task": ct["desc"],
            "task_title": ct["title"],
            "priority": ct["priority"],
            "response": "",
            "status": "completed"
        }

        try:
            from services.llm_gateway import complete_text
            specialist_provider = agent.get("model_provider", "auto")
            specialist_model = agent.get("model_name", "auto")
            gw_model = "maars/auto" if specialist_provider in ("auto", None) else f"{specialist_provider}/{specialist_model}"
            specialist_prompt = f"The Commander has assigned you this task as part of a larger project. Do NOT ask clarifying questions — just execute the task directly with your best professional output.\n\nWrite in clean, conversational paragraphs. Avoid excessive markdown headers (## ###). Use bold sparingly. Be concise and professional.\n\nOverall Goal: {goal}\n\nYour specific task: {ct['desc']}\n\nProvide a concise but actionable response. Focus on deliverables and next steps."
            response = await complete_text(
                user_id=user_id,
                system_prompt=agent["system_prompt"],
                user_prompt=specialist_prompt,
                model=gw_model,
                source=f"agent.commander_specialist:{ct['agent_id']}",
            )
            agent_entry["response"] = response
            await db.tasks.update_one(
                {"task_id": ct["task_id"]},
                {"$set": {"status": "completed", "result": response[:2000], "updated_at": datetime.now(timezone.utc).isoformat()}}
            )
            # Memory Auto-Learning from commander delegation
            try:
                from services.memory_learning_service import extract_learnings_from_task
                asyncio.create_task(extract_learnings_from_task(
                    task_result=response[:2000],
                    task_description=ct["desc"],
                    task_title=ct["title"],
                    agent_name=agent.get("name", "Agent"),
                    agent_id=ct["agent_id"],
                    user_id=user_id,
                    api_keys=api_keys,
                ))
            except Exception as learn_err:
                logger.error(f"Auto-learn error (commander): {learn_err}")
        except Exception as e:
            logger.error(f"Commander delegation error for {ct['agent_id']}: {e}")
            agent_entry["response"] = "Unable to complete - task saved for manual execution."
            agent_entry["status"] = "failed"

        delegation_agents.append(agent_entry)
        if i < len(agents_progress):
            agents_progress[i]["status"] = agent_entry["status"]
            await update_progress("delegating", agents_progress)

    await update_progress("complete", agents_progress)

    summary = f"Mission Report: {len(created_tasks)} specialists deployed for your goal. {len(created_tasks)} tasks auto-created. Check the Tasks page for tracking."
    delegation_data = {
        "type": "commander_delegation",
        "goal": goal,
        "task_count": len(created_tasks),
        "agents": delegation_agents,
        "summary": summary
    }

    text_parts = [f"Commander Orion's Mission Report\n\nGoal: {goal}\n\nDelegation Plan: {len(tasks)} specialists deployed | {len(created_tasks)} tasks created\n\n---\n"]
    for i, a in enumerate(delegation_agents):
        priority_label = {"high": "HIGH", "medium": "MED", "low": "LOW"}.get(a["priority"], "MED")
        text_parts.append(f"{i+1}. {a['agent_name']} ({a['agent_role']}) [{priority_label}]\nTask: {a['task']}\n\n{a['response']}\n\n---\n")
    text_parts.append(f"\nAll specialists have reported. {len(created_tasks)} tasks have been auto-created and can be found on your Tasks page. Let me know if you'd like any section expanded or revised.")

    return {"content": "\n".join(text_parts), "delegation_data": delegation_data}


async def backfill_usage_logs():
    from services.llm_service import MODEL_COSTS_MAP
    already_done = await db.platform_config.find_one({"config_type": "usage_backfill_done"})
    if already_done:
        return
    logger.info("Backfilling usage logs from historical chats...")
    count = 0
    chats = await db.chats.find({}, {"_id": 0}).to_list(5000)
    for chat in chats:
        agent_id = chat.get("agent_id", "")
        user_id = chat.get("user_id", "")
        agent = await db.agents.find_one({"agent_id": agent_id}, {"_id": 0})
        default_model = agent.get("model_name", "gpt-5.2") if agent else "gpt-5.2"
        default_provider = agent.get("model_provider", "openai") if agent else "openai"
        messages = chat.get("messages", [])
        for i, msg in enumerate(messages):
            if msg.get("role") != "assistant":
                continue
            content = msg.get("content", "")
            model_used = msg.get("model_used", default_model)
            user_content = ""
            if i > 0 and messages[i-1].get("role") == "user":
                user_content = messages[i-1].get("content", "")
            system_prompt = agent.get("system_prompt", "") if agent else ""
            input_text = user_content + system_prompt
            est_input_tokens = max(len(input_text) // 4, 50)
            est_output_tokens = max(len(content) // 4, 50)
            model_clean = model_used.split("/")[-1] if "/" in model_used else model_used
            costs = MODEL_COSTS_MAP.get(model_clean, {"input": 2.50, "output": 10.00, "provider": default_provider})
            est_cost = (est_input_tokens * costs["input"] / 1_000_000) + (est_output_tokens * costs["output"] / 1_000_000)
            created_at = msg.get("timestamp") or chat.get("created_at") or datetime.now(timezone.utc).isoformat()
            usage_log = {
                "log_id": f"backfill_{uuid.uuid4().hex[:10]}",
                "user_id": user_id,
                "chat_id": chat.get("chat_id", ""),
                "agent_id": agent_id,
                "model": model_used,
                "provider": costs.get("provider", default_provider),
                "input_tokens": est_input_tokens,
                "output_tokens": est_output_tokens,
                "estimated_cost_usd": round(est_cost, 6),
                "key_source": "emergent",
                "created_at": created_at,
                "backfilled": True
            }
            await db.usage_logs.insert_one(usage_log)
            count += 1
    await db.platform_config.insert_one({"config_type": "usage_backfill_done", "count": count, "done_at": datetime.now(timezone.utc).isoformat()})
    logger.info(f"Backfilled {count} usage log entries from historical chats")
