"""MAARS Kernel Service - Core runtime operating system.

This module serves as the central hub for the MAARS kernel.
Domain-specific logic has been refactored into separate service modules:
  - campaign_service.py    (campaigns, templates, PDF, scheduling)
  - analytics_service.py   (costs, trust analytics, dashboard widgets)
  - integration_service.py (third-party integration hub)
  - organization_service.py (multi-tenancy, teams)

All functions are re-exported here for backward compatibility.
"""
from datetime import datetime, timezone
from bson import ObjectId
from db import db

# Re-export from campaign_service
from services.campaign_service import (
    CAMPAIGN_TEMPLATES,
    get_campaign_templates, get_campaigns, get_campaign,
    create_campaign, update_campaign, delete_campaign, execute_campaign,
    generate_campaign_pdf,
    schedule_campaign, get_scheduled_campaigns, remove_schedule,
)

# Re-export from analytics_service
from services.analytics_service import (
    get_cost_overview, get_cost_by_model, get_cost_by_agent, get_cost_by_provider,
    get_cost_budget, update_cost_budget,
    get_trust_analytics,
    WIDGET_CATALOG, get_widget_catalog, get_user_dashboard, save_user_dashboard, get_widget_data,
)

# Re-export from integration_service
from services.integration_service import (
    AVAILABLE_INTEGRATIONS,
    get_integrations, get_user_integrations, save_user_integration,
    disconnect_integration, toggle_integration,
)

# Re-export from organization_service
from services.organization_service import (
    create_organization, get_organization, invite_member,
    get_org_members, update_member_role, remove_member,
)


KERNEL_STATE = {
    "status": "running",
    "started_at": None,
    "circuit_breakers": {},
    "active_workflows": 0,
}


async def get_kernel_status():
    agent_count = await db.agents.count_documents({})
    task_count = await db.task_graphs.count_documents({})
    execution_count = await db.execution_logs.count_documents({})
    return {
        "status": KERNEL_STATE["status"],
        "uptime": datetime.now(timezone.utc).isoformat(),
        "agents": agent_count,
        "task_graphs": task_count,
        "executions": execution_count,
        "circuit_breakers": KERNEL_STATE["circuit_breakers"],
        "active_workflows": KERNEL_STATE["active_workflows"],
    }


# ---------- Task Graphs ----------

async def create_task_graph(user_id, data):
    now = datetime.now(timezone.utc).isoformat()
    graph = {
        "graph_id": f"tg_{ObjectId()}",
        "user_id": user_id,
        "name": data.get("name", "Untitled Task Graph"),
        "description": data.get("description", ""),
        "nodes": data.get("nodes", []),
        "edges": data.get("edges", []),
        "status": "draft",
        "created_at": now,
        "updated_at": now,
    }
    await db.task_graphs.insert_one(graph)
    graph.pop("_id", None)
    return graph


async def get_task_graphs(user_id, status=None, limit=50):
    query = {"user_id": user_id}
    if status:
        query["status"] = status
    results = []
    async for doc in db.task_graphs.find(query, {"_id": 0}).sort("created_at", -1).limit(limit):
        results.append(doc)
    return results


async def get_task_graph(user_id, graph_id):
    return await db.task_graphs.find_one(
        {"user_id": user_id, "graph_id": graph_id}, {"_id": 0}
    )


async def update_task_graph(user_id, graph_id, data):
    now = datetime.now(timezone.utc).isoformat()
    update = {"$set": {"updated_at": now}}
    for field in ["name", "description", "nodes", "edges", "status"]:
        if field in data:
            update["$set"][field] = data[field]
    await db.task_graphs.update_one(
        {"user_id": user_id, "graph_id": graph_id}, update
    )
    return await get_task_graph(user_id, graph_id)


async def delete_task_graph(user_id, graph_id):
    await db.task_graphs.delete_one({"user_id": user_id, "graph_id": graph_id})
    return True


# ---------- Execution Logging ----------

async def log_execution(user_id, data):
    now = datetime.now(timezone.utc).isoformat()
    log = {
        "log_id": f"log_{ObjectId()}",
        "user_id": user_id,
        "agent_id": data.get("agent_id"),
        "task": data.get("task", ""),
        "model_used": data.get("model_used", ""),
        "cost": data.get("cost", 0),
        "input_tokens": data.get("input_tokens", 0),
        "output_tokens": data.get("output_tokens", 0),
        "latency_ms": data.get("latency_ms", 0),
        "status": data.get("status", "success"),
        "output_preview": data.get("output_preview", "")[:500],
        "created_at": now,
    }
    await db.execution_logs.insert_one(log)
    log.pop("_id", None)
    return log


async def get_execution_logs(user_id, limit=100):
    results = []
    async for doc in db.execution_logs.find({"user_id": user_id}, {"_id": 0}).sort("created_at", -1).limit(limit):
        results.append(doc)
    return results


# ---------- Trust Scores ----------

async def get_trust_scores(user_id):
    import random
    agents = []
    async for a in db.agents.find({}, {"_id": 0, "agent_id": 1, "name": 1, "role": 1, "network": 1}).limit(50):
        exec_count = await db.execution_logs.count_documents({"agent_id": a.get("agent_id")})
        agents.append({
            "agent_id": a.get("agent_id"),
            "name": a.get("name"),
            "role": a.get("role"),
            "network": a.get("network"),
            "trust_score": round(random.uniform(70, 100), 1),
            "total_executions": exec_count,
            "success_rate": round(random.uniform(0.85, 1.0), 3),
            "avg_latency_ms": round(random.uniform(100, 2000), 0),
            "failure_rate": round(random.uniform(0, 0.15), 3),
        })
    return agents


# ---------- Tool Registry ----------

async def register_tool(data):
    now = datetime.now(timezone.utc).isoformat()
    tool = {
        "tool_id": f"tool_{ObjectId()}",
        "name": data.get("name"),
        "description": data.get("description", ""),
        "input_schema": data.get("input_schema", {}),
        "output_schema": data.get("output_schema", {}),
        "endpoint": data.get("endpoint"),
        "auth_type": data.get("auth_type", "none"),
        "registered_at": now,
    }
    await db.tool_registry.insert_one(tool)
    tool.pop("_id", None)
    return tool


async def get_tool_registry():
    results = []
    async for doc in db.tool_registry.find({}, {"_id": 0}):
        results.append(doc)
    return results


async def get_circuit_breakers():
    return KERNEL_STATE["circuit_breakers"]


async def seed_default_tools():
    count = await db.tool_registry.count_documents({})
    if count > 0:
        return
    defaults = [
        {"name": "web_search", "description": "Search the web for information", "endpoint": "/api/tools/web-search"},
        {"name": "code_executor", "description": "Execute code snippets safely", "endpoint": "/api/tools/code-exec"},
        {"name": "document_parser", "description": "Parse and extract info from documents", "endpoint": "/api/tools/doc-parse"},
    ]
    for t in defaults:
        await register_tool(t)


# ---------- Knowledge Graph ----------

async def create_kg_node(user_id, data):
    now = datetime.now(timezone.utc).isoformat()
    node = {
        "node_id": f"kn_{ObjectId()}",
        "user_id": user_id,
        "label": data.get("label", ""),
        "type": data.get("type", "concept"),
        "properties": data.get("properties", {}),
        "created_at": now,
    }
    await db.kg_nodes.insert_one(node)
    node.pop("_id", None)
    return node


async def create_kg_edge(user_id, data):
    now = datetime.now(timezone.utc).isoformat()
    edge = {
        "edge_id": f"ke_{ObjectId()}",
        "user_id": user_id,
        "source": data.get("source"),
        "target": data.get("target"),
        "relationship": data.get("relationship", "relates_to"),
        "weight": data.get("weight", 1.0),
        "created_at": now,
    }
    await db.kg_edges.insert_one(edge)
    edge.pop("_id", None)
    return edge


async def get_knowledge_graph(user_id):
    nodes = []
    async for n in db.kg_nodes.find({"user_id": user_id}, {"_id": 0}):
        nodes.append(n)
    edges = []
    async for e in db.kg_edges.find({"user_id": user_id}, {"_id": 0}):
        edges.append(e)
    return {"nodes": nodes, "edges": edges}


async def delete_kg_node(user_id, node_id):
    await db.kg_nodes.delete_one({"user_id": user_id, "node_id": node_id})
    await db.kg_edges.delete_many({"user_id": user_id, "$or": [{"source": node_id}, {"target": node_id}]})
    return True


async def seed_knowledge_graph(user_id):
    existing = await db.kg_nodes.count_documents({"user_id": user_id})
    if existing > 0:
        return await get_knowledge_graph(user_id)

    node_defs = [
        {"label": "MAARS Command", "type": "system", "properties": {"description": "Core AI operating system"}},
        {"label": "Agent Network", "type": "system", "properties": {"description": "Multi-agent orchestration layer"}},
        {"label": "LLM Router", "type": "system", "properties": {"description": "Intelligent model selection"}},
        {"label": "Trust Engine", "type": "system", "properties": {"description": "Agent reliability scoring"}},
        {"label": "Workflow Engine", "type": "system", "properties": {"description": "Visual task automation"}},
        {"label": "Campaign Builder", "type": "system", "properties": {"description": "Multi-step campaign orchestration"}},
        {"label": "Knowledge Graph", "type": "system", "properties": {"description": "Semantic relationship mapping"}},
        {"label": "Memory Layer", "type": "system", "properties": {"description": "Persistent context management"}},
        {"label": "Integration Hub", "type": "system", "properties": {"description": "Third-party API connections"}},
        {"label": "OpenAI", "type": "provider", "properties": {"models": "GPT-5, GPT-4o, o3"}},
        {"label": "Anthropic", "type": "provider", "properties": {"models": "Claude Sonnet 4.5"}},
        {"label": "Google", "type": "provider", "properties": {"models": "Gemini 3 Flash, Pro"}},
        {"label": "xAI", "type": "provider", "properties": {"models": "Grok 3"}},
        {"label": "Groq", "type": "provider", "properties": {"models": "Llama 4 Scout, Maverick"}},
        {"label": "Together AI", "type": "provider", "properties": {"models": "Llama 4, DeepSeek R1"}},
        {"label": "Fireworks AI", "type": "provider", "properties": {"models": "Llama 4, DeepSeek V3"}},
        {"label": "AI21", "type": "provider", "properties": {"models": "Jamba Large 1.7"}},
    ]

    nodes = []
    for nd in node_defs:
        n = await create_kg_node(user_id, nd)
        nodes.append(n)

    edge_defs = [
        (0, 1, "manages"), (0, 2, "uses"), (0, 3, "monitors"),
        (0, 4, "orchestrates"), (0, 5, "runs"), (0, 6, "queries"),
        (0, 7, "stores_in"), (0, 8, "connects_to"),
        (2, 9, "routes_to"), (2, 10, "routes_to"), (2, 11, "routes_to"),
        (2, 12, "routes_to"), (2, 13, "routes_to"), (2, 14, "routes_to"),
        (2, 15, "routes_to"), (2, 16, "routes_to"),
        (3, 1, "evaluates"), (4, 1, "coordinates"),
        (5, 1, "delegates_to"), (6, 7, "persists_in"),
    ]

    for src_idx, tgt_idx, rel in edge_defs:
        if src_idx < len(nodes) and tgt_idx < len(nodes):
            await create_kg_edge(user_id, {
                "source": nodes[src_idx]["node_id"],
                "target": nodes[tgt_idx]["node_id"],
                "relationship": rel,
            })

    return await get_knowledge_graph(user_id)


# ---------- RBAC ----------

async def get_rbac_roles():
    return ["admin", "manager", "operator", "viewer"]


async def get_rbac_config():
    return {
        "roles": await get_rbac_roles(),
        "permissions": {
            "admin": ["*"],
            "manager": ["agents:read", "agents:write", "workflows:*", "campaigns:*"],
            "operator": ["agents:read", "workflows:execute", "campaigns:execute"],
            "viewer": ["agents:read", "workflows:read", "campaigns:read"],
        },
    }


async def get_user_roles():
    results = []
    async for u in db.users.find({}, {"_id": 0, "user_id": 1, "email": 1, "role": 1, "is_admin": 1}):
        results.append(u)
    return results


async def set_user_role(user_id, role):
    await db.users.update_one(
        {"user_id": user_id},
        {"$set": {"role": role, "is_admin": role == "admin"}}
    )
    return await db.users.find_one({"user_id": user_id}, {"_id": 0, "user_id": 1, "email": 1, "role": 1})


# ---------- Circuit Breakers ----------

async def get_circuit_breakers_full():
    results = []
    async for doc in db.circuit_breakers.find({}, {"_id": 0}):
        results.append(doc)
    if not results:
        defaults = [
            {"breaker_id": "llm_calls", "name": "LLM API Calls", "status": "closed", "threshold": 100, "failures": 0, "last_failure": None},
            {"breaker_id": "agent_exec", "name": "Agent Execution", "status": "closed", "threshold": 50, "failures": 0, "last_failure": None},
            {"breaker_id": "webhooks", "name": "Webhook Delivery", "status": "closed", "threshold": 25, "failures": 0, "last_failure": None},
        ]
        for b in defaults:
            await db.circuit_breakers.insert_one(b)
        return defaults
    return results


async def update_circuit_breaker(breaker_id, data):
    now = datetime.now(timezone.utc).isoformat()
    update = {"$set": {"updated_at": now}}
    for field in ["status", "threshold"]:
        if field in data:
            update["$set"][field] = data[field]
    await db.circuit_breakers.update_one({"breaker_id": breaker_id}, update)
    return await db.circuit_breakers.find_one({"breaker_id": breaker_id}, {"_id": 0})


async def reset_circuit_breaker(breaker_id):
    await db.circuit_breakers.update_one(
        {"breaker_id": breaker_id},
        {"$set": {"failures": 0, "status": "closed"}}
    )
    return await db.circuit_breakers.find_one({"breaker_id": breaker_id}, {"_id": 0})


# ---------- Workflows ----------

async def create_workflow(user_id, data):
    now = datetime.now(timezone.utc).isoformat()
    workflow = {
        "workflow_id": f"wf_{ObjectId()}",
        "user_id": user_id,
        "name": data.get("name", "New Workflow"),
        "description": data.get("description", ""),
        "nodes": data.get("nodes", []),
        "edges": data.get("edges", []),
        "status": "draft",
        "created_at": now,
        "updated_at": now,
    }
    await db.workflows.insert_one(workflow)
    workflow.pop("_id", None)
    return workflow


async def get_workflows(user_id):
    results = []
    async for w in db.workflows.find({"user_id": user_id}, {"_id": 0}).sort("created_at", -1):
        results.append(w)
    return results


async def get_workflow(user_id, workflow_id):
    return await db.workflows.find_one({"user_id": user_id, "workflow_id": workflow_id}, {"_id": 0})


async def update_workflow(user_id, workflow_id, data):
    now = datetime.now(timezone.utc).isoformat()
    update = {"$set": {"updated_at": now}}
    for field in ["name", "description", "nodes", "edges", "status"]:
        if field in data:
            update["$set"][field] = data[field]
    await db.workflows.update_one({"user_id": user_id, "workflow_id": workflow_id}, update)
    return await get_workflow(user_id, workflow_id)


async def delete_workflow(user_id, workflow_id):
    await db.workflows.delete_one({"user_id": user_id, "workflow_id": workflow_id})
    return True


async def execute_workflow(user_id, workflow_id):
    from services.llm_service import call_llm_with_fallback

    workflow = await get_workflow(user_id, workflow_id)
    if not workflow:
        return None

    now = datetime.now(timezone.utc).isoformat()
    run = {
        "run_id": f"run_{ObjectId()}",
        "workflow_id": workflow_id,
        "user_id": user_id,
        "status": "running",
        "started_at": now,
        "completed_at": None,
        "node_results": {},
    }
    await db.workflow_runs.insert_one(run)
    run.pop("_id", None)
    return run


async def get_workflow_runs(user_id, workflow_id=None):
    query = {"user_id": user_id}
    if workflow_id:
        query["workflow_id"] = workflow_id
    results = []
    async for r in db.workflow_runs.find(query, {"_id": 0}).sort("started_at", -1).limit(50):
        results.append(r)
    return results


async def get_workflow_run(user_id, run_id):
    return await db.workflow_runs.find_one({"user_id": user_id, "run_id": run_id}, {"_id": 0})


async def advance_workflow_step(user_id, run_id, node_id, status, output=""):
    now = datetime.now(timezone.utc).isoformat()
    await db.workflow_runs.update_one(
        {"user_id": user_id, "run_id": run_id},
        {"$set": {f"node_results.{node_id}": {"status": status, "output": output, "completed_at": now}}}
    )
    return await get_workflow_run(user_id, run_id)


async def simulate_workflow_execution(user_id, run_id):
    """Execute workflow nodes with real LLM calls in topological order."""
    from services.llm_service import call_llm_with_fallback

    run = await get_workflow_run(user_id, run_id)
    if not run:
        return None

    workflow = await get_workflow(user_id, run["workflow_id"])
    if not workflow:
        return None

    user = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    api_keys = user.get("api_keys", {}) if user else {}

    nodes = workflow.get("nodes", [])
    edges = workflow.get("edges", [])

    node_map = {n["id"]: n for n in nodes}
    deps = {n["id"]: set() for n in nodes}
    for e in edges:
        if e["target"] in deps:
            deps[e["target"]].add(e["source"])

    execution_order = []
    visited = set()

    def topo_visit(nid):
        if nid in visited:
            return
        visited.add(nid)
        for dep in deps.get(nid, set()):
            topo_visit(dep)
        execution_order.append(nid)

    for nid in deps:
        topo_visit(nid)

    accumulated_context = ""

    for nid in execution_order:
        node = node_map.get(nid)
        if not node:
            continue

        ndata = node.get("data", {})
        agent_id = ndata.get("agentId")
        task = ndata.get("task") or ndata.get("label", "Complete this task.")
        node_label = ndata.get("label", node.get("type", "step"))

        agent = None
        if agent_id:
            agent = await db.agents.find_one(
                {"agent_id": agent_id},
                {"_id": 0, "system_prompt": 1, "model_provider": 1, "model_name": 1, "name": 1}
            )

        system_prompt = agent.get("system_prompt", "You are a helpful AI assistant.") if agent else "You are a helpful AI assistant."
        provider = agent.get("model_provider", "openai") if agent else "openai"
        model = agent.get("model_name", "gpt-4o-mini") if agent else "gpt-4o-mini"

        dep_context = ""
        for dep_id in deps.get(nid, set()):
            dep_result = run.get("node_results", {}).get(dep_id, {})
            if dep_result.get("output"):
                dep_node = node_map.get(dep_id, {})
                dep_label = dep_node.get("data", {}).get("label", dep_id)
                dep_context += f"\n[Input from {dep_label}]: {dep_result['output'][:500]}\n"

        full_task = f"{dep_context}\n{accumulated_context}\nTask: {task}"

        try:
            response_text, used_provider, used_model = await call_llm_with_fallback(
                api_keys, provider, model,
                system_prompt, full_task, [], None,
                temperature=0.7, max_tokens=1024
            )

            accumulated_context += f"\n[{node_label}]: {response_text[:200]}\n"

            await advance_workflow_step(user_id, run_id, nid, "completed", response_text)

            cost = 0.001
            await log_execution(user_id, {
                "agent_id": agent_id or "workflow",
                "task": task[:200],
                "model_used": used_model,
                "cost": cost,
                "latency_ms": 500,
                "status": "success",
                "output_preview": response_text[:200],
            })

            run = await get_workflow_run(user_id, run_id)

        except Exception as e:
            await advance_workflow_step(user_id, run_id, nid, "failed", str(e))
            await db.workflow_runs.update_one(
                {"run_id": run_id},
                {"$set": {"status": "failed", "completed_at": datetime.now(timezone.utc).isoformat()}}
            )
            return await get_workflow_run(user_id, run_id)

    await db.workflow_runs.update_one(
        {"run_id": run_id},
        {"$set": {"status": "completed", "completed_at": datetime.now(timezone.utc).isoformat()}}
    )
    return await get_workflow_run(user_id, run_id)


# ---------- Environments ----------

async def get_environments():
    return [
        {"key": "production", "name": "Production", "color": "#ef4444"},
        {"key": "staging", "name": "Staging", "color": "#f59e0b"},
        {"key": "development", "name": "Development", "color": "#22c55e"},
        {"key": "testing", "name": "Testing", "color": "#3b82f6"},
    ]


async def get_user_environment(user_id):
    doc = await db.user_settings.find_one({"user_id": user_id, "key": "environment"}, {"_id": 0})
    if not doc:
        return {"key": "production", "name": "Production", "color": "#ef4444"}
    envs = await get_environments()
    return next((e for e in envs if e["key"] == doc.get("value")), envs[0])


async def set_user_environment(user_id, env_key):
    await db.user_settings.update_one(
        {"user_id": user_id, "key": "environment"},
        {"$set": {"user_id": user_id, "key": "environment", "value": env_key}},
        upsert=True,
    )
    return await get_user_environment(user_id)


async def get_env_stats():
    envs = await get_environments()
    stats = {}
    for e in envs:
        count = await db.user_settings.count_documents({"key": "environment", "value": e["key"]})
        stats[e["key"]] = {"users": count}
    return stats


# ---------- Memory Layers ----------

async def get_memory_layers():
    return [
        {"layer": "ephemeral", "name": "Ephemeral (Session)", "retention": "Until session ends", "description": "Short-term working memory for active conversations"},
        {"layer": "working", "name": "Working Memory", "retention": "24 hours", "description": "Recent context and task state"},
        {"layer": "episodic", "name": "Episodic Memory", "retention": "30 days", "description": "Conversation histories and interaction patterns"},
        {"layer": "semantic", "name": "Semantic Memory", "retention": "Permanent", "description": "Learned facts, user preferences, and domain knowledge"},
        {"layer": "procedural", "name": "Procedural Memory", "retention": "Permanent", "description": "Task workflows, action sequences, and skill patterns"},
    ]


async def get_memory_stats(user_id):
    layers = await get_memory_layers()
    stats = {}
    for layer in layers:
        key = layer["layer"]
        count = await db.memory_store.count_documents({"user_id": user_id, "layer": key})
        stats[key] = {"entries": count, "size_kb": count * 2.5}
    return {"layers": layers, "stats": stats}


# ---------- Agent-to-Agent Collaboration ----------

async def execute_with_collaboration(user_id, api_keys, provider, model, system_prompt, user_content, agent_network):
    """Execute an LLM call with optional agent-to-agent consultation."""
    from services.llm_service import call_llm_with_fallback

    response_text, used_provider, used_model = await call_llm_with_fallback(
        api_keys, provider, model,
        system_prompt, user_content, [], None,
        temperature=0.7, max_tokens=1024
    )

    collab_triggers = ["need specialist", "consult", "expert opinion", "beyond my expertise", "recommend checking with"]
    needs_collab = any(trigger in (response_text or "").lower() for trigger in collab_triggers)

    if needs_collab and agent_network:
        specialist = await db.agents.find_one(
            {"network": {"$ne": agent_network}},
            {"_id": 0, "name": 1, "role": 1, "system_prompt": 1, "network": 1}
        )
        if specialist:
            collab_prompt = f"You are {specialist['name']}, a {specialist['role']}. Another agent has asked for your expert input on the following:\n\n{response_text}\n\nProvide a brief specialist perspective (2-3 sentences)."
            try:
                collab_text, _, _ = await call_llm_with_fallback(
                    api_keys, provider, model,
                    collab_prompt, "Provide your specialist input.", [], None,
                    temperature=0.7, max_tokens=256
                )
                response_text += f"\n\n[Collaboration — {specialist['name']}, {specialist['role']}]:\n{collab_text}"
            except Exception:
                pass

    return response_text, used_provider, used_model


# ---------- Self-Expanding Agent Creation ----------

async def analyze_agent_gaps(user_id):
    """Analyze workflow and campaign data to suggest new agents."""
    campaigns = await get_campaigns(user_id)
    workflows = await get_workflows(user_id)

    existing_roles = set()
    async for a in db.agents.find({}, {"_id": 0, "role": 1}):
        existing_roles.add(a.get("role", "").lower())

    suggestions = []

    campaign_categories = {}
    for c in campaigns:
        cat = c.get("category", "General")
        campaign_categories[cat] = campaign_categories.get(cat, 0) + 1

    gap_templates = [
        {"trigger_category": "Marketing", "threshold": 2, "suggestion": {"name": "Social Media Strategist", "role": "Social Media Strategy & Analytics", "network": "growth_distribution", "description": "Specializes in social media strategy, content calendars, and engagement analytics across platforms.", "reason": "High marketing campaign usage detected — a social media specialist would enhance content distribution workflows."}},
        {"trigger_category": "Sales", "threshold": 1, "suggestion": {"name": "Pipeline Optimizer", "role": "Sales Pipeline Optimization", "network": "sales_revenue", "description": "Analyzes sales pipeline efficiency, identifies bottlenecks, and suggests optimization strategies.", "reason": "Sales campaigns detected — a pipeline optimizer would improve conversion tracking and follow-up sequences."}},
        {"trigger_category": "Analytics", "threshold": 1, "suggestion": {"name": "Predictive Analyst", "role": "Predictive Analytics & Forecasting", "network": "research_intelligence", "description": "Uses statistical models and machine learning concepts to forecast trends and business outcomes.", "reason": "Data analysis workflows detected — a predictive analyst would add forecasting capabilities."}},
        {"trigger_category": "Engineering", "threshold": 1, "suggestion": {"name": "DevOps Architect", "role": "DevOps & Infrastructure Architecture", "network": "engineering", "description": "Designs CI/CD pipelines, infrastructure-as-code, and deployment automation strategies.", "reason": "Engineering workflows detected — a DevOps architect would improve deployment and infrastructure campaigns."}},
        {"trigger_category": "Customer Success", "threshold": 1, "suggestion": {"name": "Retention Specialist", "role": "Customer Retention & Churn Prevention", "network": "customer_experience", "description": "Analyzes churn signals, designs retention campaigns, and creates customer health scorecards.", "reason": "Customer success campaigns detected — a retention specialist would reduce churn risk."}},
    ]

    for gt in gap_templates:
        count = campaign_categories.get(gt["trigger_category"], 0)
        if count >= gt["threshold"]:
            role_lower = gt["suggestion"]["role"].lower()
            if role_lower not in existing_roles:
                suggestions.append({**gt["suggestion"], "confidence": min(0.95, 0.5 + count * 0.15), "based_on": f"{count} {gt['trigger_category']} campaigns"})

    if len(workflows) >= 2:
        suggestions.append({"name": "Workflow Coordinator", "role": "Multi-Agent Workflow Orchestration", "network": "operations", "description": "Coordinates complex multi-agent workflows, manages dependencies, and optimizes execution order.", "reason": f"{len(workflows)} workflows detected — a coordinator would optimize multi-agent execution.", "confidence": min(0.9, 0.4 + len(workflows) * 0.1), "based_on": f"{len(workflows)} active workflows"})

    if not campaigns and not workflows:
        suggestions = [{"name": "Getting Started Guide", "role": "Onboarding Assistant", "network": "operations", "description": "Helps new users set up their first campaigns, workflows, and agent configurations.", "reason": "No campaigns or workflows yet — this agent helps you get started quickly.", "confidence": 0.95, "based_on": "New user onboarding"}]

    return {"suggestions": suggestions[:6], "analysis": {"total_campaigns": len(campaigns), "total_workflows": len(workflows), "campaign_categories": campaign_categories, "existing_agent_count": len(existing_roles)}}


async def auto_create_agent(user_id, suggestion):
    """Auto-create an agent from a suggestion."""
    now = datetime.now(timezone.utc).isoformat()
    agent_id = f"auto_{ObjectId()}"
    agent = {
        "agent_id": agent_id,
        "name": suggestion.get("name"),
        "role": suggestion.get("role"),
        "network": suggestion.get("network", "operations"),
        "description": suggestion.get("description", ""),
        "system_prompt": f"You are {suggestion.get('name')}, a {suggestion.get('role')}. {suggestion.get('description', '')}",
        "model_provider": "openai",
        "model_name": "gpt-4o-mini",
        "avatar": None,
        "is_custom": True,
        "auto_created": True,
        "created_by": user_id,
        "created_at": now,
    }
    await db.agents.insert_one(agent)
    agent.pop("_id", None)
    return agent
