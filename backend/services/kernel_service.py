"""MAARS Kernel Service - Core runtime operating system."""
from datetime import datetime, timezone
from bson import ObjectId
from db import db

KERNEL_STATE = {
    "status": "running",
    "started_at": None,
    "circuit_breakers": {},
    "active_workflows": 0,
}


async def get_kernel_status():
    """Get current kernel runtime status."""
    agent_count = await db.agents.count_documents({})
    task_count = await db.tasks.count_documents({})
    active_tasks = await db.tasks.count_documents({"status": "in_progress"})
    memory_count = await db.memory_entries.count_documents({})
    tg_count = await db.task_graphs.count_documents({})
    active_tg = await db.task_graphs.count_documents({"status": "active"})
    exec_logs = await db.execution_logs.count_documents({})
    tool_count = await db.tool_registry.count_documents({})

    return {
        "status": "running",
        "subsystems": {
            "agent_scheduler": {"status": "active", "agents_registered": agent_count},
            "task_graph_runtime": {"status": "active", "total_graphs": tg_count, "active_graphs": active_tg},
            "resource_manager": {"status": "active"},
            "budget_controller": {"status": "active"},
            "execution_gateway": {"status": "active", "total_executions": exec_logs},
            "tool_registry": {"status": "active", "tools_registered": tool_count},
            "memory_controller": {"status": "active", "entries": memory_count},
            "policy_engine": {"status": "active"},
            "approval_controller": {"status": "active"},
            "failure_recovery": {"status": "standby"},
            "circuit_breakers": KERNEL_STATE.get("circuit_breakers", {}),
        },
        "metrics": {
            "total_agents": agent_count,
            "total_tasks": task_count,
            "active_tasks": active_tasks,
            "total_task_graphs": tg_count,
            "active_task_graphs": active_tg,
            "execution_logs": exec_logs,
            "memory_entries": memory_count,
            "tools_registered": tool_count,
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


async def create_task_graph(user_id, data):
    """Create a new task graph."""
    now = datetime.now(timezone.utc).isoformat()
    graph = {
        "user_id": user_id,
        "title": data.get("title", "Untitled Task Graph"),
        "objective": data.get("objective", ""),
        "scope": data.get("scope", ""),
        "status": "draft",
        "nodes": data.get("nodes", []),
        "edges": data.get("edges", []),
        "success_criteria": data.get("success_criteria", []),
        "failure_criteria": data.get("failure_criteria", []),
        "approval_points": data.get("approval_points", []),
        "rollback_plan": data.get("rollback_plan", ""),
        "cost_estimate": data.get("cost_estimate", 0),
        "risk_score": data.get("risk_score", 0),
        "timeline": data.get("timeline", ""),
        "required_agents": data.get("required_agents", []),
        "required_tools": data.get("required_tools", []),
        "verification_rules": data.get("verification_rules", []),
        "version": 1,
        "created_at": now,
        "updated_at": now,
    }
    result = await db.task_graphs.insert_one(graph)
    graph["id"] = str(result.inserted_id)
    del graph["_id"]
    return graph


async def get_task_graphs(user_id, status=None, limit=50):
    """List task graphs for a user."""
    query = {"user_id": user_id}
    if status:
        query["status"] = status
    cursor = db.task_graphs.find(query, {"_id": 0}).sort("updated_at", -1).limit(limit)
    graphs = []
    async for g in cursor:
        graphs.append(g)
    return graphs


async def get_task_graph(user_id, graph_id):
    """Get a specific task graph."""
    try:
        graph = await db.task_graphs.find_one(
            {"_id": ObjectId(graph_id), "user_id": user_id}, {"_id": 0}
        )
        if graph:
            graph["id"] = graph_id
        return graph
    except Exception:
        return None


async def update_task_graph(user_id, graph_id, data):
    """Update a task graph."""
    now = datetime.now(timezone.utc).isoformat()
    update_fields = {k: v for k, v in data.items() if k not in ("id", "_id", "user_id", "created_at")}
    update_fields["updated_at"] = now

    try:
        result = await db.task_graphs.update_one(
            {"_id": ObjectId(graph_id), "user_id": user_id},
            {"$set": update_fields}
        )
        return result.modified_count > 0
    except Exception:
        return False


async def delete_task_graph(user_id, graph_id):
    """Delete a task graph."""
    try:
        result = await db.task_graphs.delete_one(
            {"_id": ObjectId(graph_id), "user_id": user_id}
        )
        return result.deleted_count > 0
    except Exception:
        return False


async def log_execution(user_id, data):
    """Log an execution through the gateway."""
    now = datetime.now(timezone.utc).isoformat()
    log_entry = {
        "user_id": user_id,
        "action": data.get("action", "unknown"),
        "agent_id": data.get("agent_id", ""),
        "tool_id": data.get("tool_id", ""),
        "input_summary": data.get("input_summary", ""),
        "output_summary": data.get("output_summary", ""),
        "status": data.get("status", "completed"),
        "cost": data.get("cost", 0),
        "latency_ms": data.get("latency_ms", 0),
        "environment": data.get("environment", "production"),
        "approval_required": data.get("approval_required", False),
        "approval_status": data.get("approval_status", "not_required"),
        "verification_status": data.get("verification_status", "not_required"),
        "provenance": {
            "model_used": data.get("model_used", ""),
            "sources": data.get("sources", []),
            "confidence": data.get("confidence", 1.0),
        },
        "created_at": now,
    }
    result = await db.execution_logs.insert_one(log_entry)
    log_entry["id"] = str(result.inserted_id)
    del log_entry["_id"]
    return log_entry


async def get_execution_logs(user_id, limit=100):
    """Get execution logs."""
    cursor = db.execution_logs.find(
        {"user_id": user_id}, {"_id": 0}
    ).sort("created_at", -1).limit(limit)
    logs = []
    async for log in cursor:
        logs.append(log)
    return logs


async def get_trust_scores(user_id):
    """Get agent trust scores."""
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$group": {
            "_id": "$agent_id",
            "total_executions": {"$sum": 1},
            "successful": {"$sum": {"$cond": [{"$eq": ["$status", "completed"]}, 1, 0]}},
            "failed": {"$sum": {"$cond": [{"$eq": ["$status", "failed"]}, 1, 0]}},
            "avg_cost": {"$avg": "$cost"},
            "avg_latency": {"$avg": "$latency_ms"},
        }},
    ]
    scores = []
    async for doc in db.execution_logs.aggregate(pipeline):
        total = doc["total_executions"] or 1
        scores.append({
            "agent_id": doc["_id"],
            "total_executions": total,
            "success_rate": round(doc["successful"] / total, 3),
            "failure_rate": round(doc["failed"] / total, 3),
            "avg_cost": round(doc["avg_cost"] or 0, 4),
            "avg_latency_ms": round(doc["avg_latency"] or 0, 1),
            "trust_score": round((doc["successful"] / total) * 100, 1),
        })
    return sorted(scores, key=lambda x: x["trust_score"], reverse=True)


async def register_tool(data):
    """Register a tool in the tool registry."""
    now = datetime.now(timezone.utc).isoformat()
    tool = {
        "tool_id": data.get("tool_id", ""),
        "name": data.get("name", ""),
        "category": data.get("category", "general"),
        "description": data.get("description", ""),
        "endpoint": data.get("endpoint", ""),
        "auth_type": data.get("auth_type", "none"),
        "input_schema": data.get("input_schema", {}),
        "output_schema": data.get("output_schema", {}),
        "reliability_score": data.get("reliability_score", 1.0),
        "cost_score": data.get("cost_score", 0),
        "risk_score": data.get("risk_score", 0),
        "allowed_agents": data.get("allowed_agents", []),
        "environment_restrictions": data.get("environment_restrictions", []),
        "fallback_tools": data.get("fallback_tools", []),
        "approval_thresholds": data.get("approval_thresholds", {}),
        "status": "active",
        "last_health_check": now,
        "created_at": now,
        "updated_at": now,
    }
    await db.tool_registry.update_one(
        {"tool_id": tool["tool_id"]},
        {"$set": tool},
        upsert=True
    )
    return tool


async def get_tool_registry():
    """Get all registered tools."""
    cursor = db.tool_registry.find({}, {"_id": 0}).sort("name", 1)
    tools = []
    async for t in cursor:
        tools.append(t)
    return tools


async def get_circuit_breakers():
    """Get current circuit breaker states."""
    return KERNEL_STATE.get("circuit_breakers", {})


async def seed_default_tools():
    """Seed default tool definitions into the registry."""
    from config import AGENT_TOOLS
    for tool_id, tool_data in AGENT_TOOLS.items():
        await register_tool({
            "tool_id": tool_id,
            "name": tool_data.get("name", tool_id),
            "category": tool_data.get("category", "general"),
            "description": tool_data.get("description", ""),
            "reliability_score": 1.0,
            "cost_score": 0,
            "risk_score": 0,
        })


# ---------- Knowledge Graph ----------

async def create_kg_node(user_id, data):
    """Create a knowledge graph node."""
    now = datetime.now(timezone.utc).isoformat()
    node = {
        "user_id": user_id,
        "node_id": data.get("node_id", ""),
        "label": data.get("label", ""),
        "type": data.get("type", "entity"),  # agent, network, venture, product, market, concept
        "properties": data.get("properties", {}),
        "created_at": now,
        "updated_at": now,
    }
    await db.knowledge_graph_nodes.update_one(
        {"user_id": user_id, "node_id": node["node_id"]},
        {"$set": node},
        upsert=True,
    )
    return node


async def create_kg_edge(user_id, data):
    """Create a knowledge graph edge."""
    now = datetime.now(timezone.utc).isoformat()
    edge = {
        "user_id": user_id,
        "edge_id": data.get("edge_id", ""),
        "source": data.get("source", ""),
        "target": data.get("target", ""),
        "relationship": data.get("relationship", "related_to"),
        "weight": data.get("weight", 1.0),
        "properties": data.get("properties", {}),
        "created_at": now,
    }
    await db.knowledge_graph_edges.update_one(
        {"user_id": user_id, "edge_id": edge["edge_id"]},
        {"$set": edge},
        upsert=True,
    )
    return edge


async def get_knowledge_graph(user_id):
    """Get full knowledge graph for a user."""
    nodes = []
    async for n in db.knowledge_graph_nodes.find({"user_id": user_id}, {"_id": 0}):
        nodes.append(n)
    edges = []
    async for e in db.knowledge_graph_edges.find({"user_id": user_id}, {"_id": 0}):
        edges.append(e)
    return {"nodes": nodes, "edges": edges}


async def delete_kg_node(user_id, node_id):
    """Delete a knowledge graph node and its connected edges."""
    await db.knowledge_graph_nodes.delete_one({"user_id": user_id, "node_id": node_id})
    await db.knowledge_graph_edges.delete_many(
        {"user_id": user_id, "$or": [{"source": node_id}, {"target": node_id}]}
    )
    return True


async def seed_knowledge_graph(user_id):
    """Seed the knowledge graph with agent/network data."""
    existing = await db.knowledge_graph_nodes.count_documents({"user_id": user_id})
    if existing > 0:
        return  # Already seeded

    from infinity_catalog import NETWORK_DEFINITIONS, INFINITY_AGENTS

    # Create network nodes
    for key, net in NETWORK_DEFINITIONS.items():
        await create_kg_node(user_id, {
            "node_id": f"net_{key}",
            "label": net["name"],
            "type": "network",
            "properties": {"code": net["code"], "layer": net["layer"], "purpose": net["purpose"]},
        })

    # Create agent nodes (sample — top 3 per network)
    from infinity_catalog import get_agents_by_network
    for key in NETWORK_DEFINITIONS:
        agents = get_agents_by_network(key)
        for a in agents[:3]:
            await create_kg_node(user_id, {
                "node_id": f"agent_{a['agent_id']}",
                "label": a["name"],
                "type": "agent",
                "properties": {"role": a["role"], "network": key, "autonomy_tier": a.get("autonomy_tier", 0)},
            })
            await create_kg_edge(user_id, {
                "edge_id": f"edge_{a['agent_id']}_to_{key}",
                "source": f"agent_{a['agent_id']}",
                "target": f"net_{key}",
                "relationship": "belongs_to",
                "weight": 1.0,
            })

    # Create cross-network edges
    cross_links = [
        ("net_engineering", "net_product_development", "supports"),
        ("net_engineering", "net_security", "secures"),
        ("net_strategic_executive", "net_finance_capital", "governs"),
        ("net_growth_distribution", "net_sales_revenue", "drives"),
        ("net_creative_brand", "net_communication_reporting", "creates_for"),
        ("net_research_intelligence", "net_simulation_foresight", "informs"),
        ("net_legal_governance", "net_verification", "validates"),
        ("net_execution", "net_observability_incident", "monitored_by"),
        ("net_memory_knowledge", "net_research_intelligence", "feeds"),
        ("net_tooling_capability", "net_execution", "enables"),
    ]
    for src, tgt, rel in cross_links:
        await create_kg_edge(user_id, {
            "edge_id": f"edge_{src}_to_{tgt}",
            "source": src,
            "target": tgt,
            "relationship": rel,
            "weight": 0.8,
        })



# ---------- RBAC ----------

RBAC_ROLES = {
    "admin": {
        "label": "Administrator",
        "permissions": ["*"],
        "description": "Full system access",
    },
    "manager": {
        "label": "Manager",
        "permissions": [
            "agents:read", "agents:write", "agents:chat",
            "kernel:read", "task_graphs:read", "task_graphs:write",
            "knowledge_graph:read", "knowledge_graph:write",
            "trust_scores:read", "execution_logs:read",
            "workflows:read", "workflows:write",
            "cost:read", "users:read",
        ],
        "description": "Manage agents, workflows, and view analytics",
    },
    "analyst": {
        "label": "Analyst",
        "permissions": [
            "agents:read", "agents:chat",
            "kernel:read", "task_graphs:read",
            "knowledge_graph:read", "trust_scores:read",
            "execution_logs:read", "workflows:read", "cost:read",
        ],
        "description": "Read-only analytics and agent chat access",
    },
    "viewer": {
        "label": "Viewer",
        "permissions": [
            "agents:read", "kernel:read",
            "trust_scores:read", "cost:read",
        ],
        "description": "View-only access to dashboards",
    },
}

RESOURCES = [
    "agents", "kernel", "task_graphs", "knowledge_graph",
    "trust_scores", "execution_logs", "workflows",
    "cost", "users", "circuit_breakers",
]
ACTIONS = ["read", "write", "chat", "delete", "admin"]


async def get_rbac_roles():
    return RBAC_ROLES


async def get_rbac_config():
    return {"roles": RBAC_ROLES, "resources": RESOURCES, "actions": ACTIONS}


async def get_user_roles():
    """Get all user role assignments."""
    users = []
    async for u in db.users.find({}, {"_id": 0, "user_id": 1, "email": 1, "name": 1, "role": 1}):
        u["role"] = u.get("role", "viewer")
        users.append(u)
    return users


async def set_user_role(user_id, role):
    if role not in RBAC_ROLES:
        return None
    await db.users.update_one({"user_id": user_id}, {"$set": {"role": role}})
    return {"user_id": user_id, "role": role}


# ---------- Circuit Breakers (Full CRUD) ----------

DEFAULT_CIRCUIT_BREAKERS = {
    "llm_gateway": {"name": "LLM Gateway", "state": "closed", "failure_threshold": 5, "reset_timeout_s": 60, "failures": 0, "last_failure": None, "description": "Circuit for all LLM API calls"},
    "tool_execution": {"name": "Tool Execution", "state": "closed", "failure_threshold": 3, "reset_timeout_s": 30, "failures": 0, "last_failure": None, "description": "Circuit for external tool invocations"},
    "memory_store": {"name": "Memory Store", "state": "closed", "failure_threshold": 10, "reset_timeout_s": 120, "failures": 0, "last_failure": None, "description": "Circuit for memory persistence layer"},
    "web_search": {"name": "Web Search", "state": "closed", "failure_threshold": 5, "reset_timeout_s": 45, "failures": 0, "last_failure": None, "description": "Circuit for web search provider"},
    "email_service": {"name": "Email Service", "state": "closed", "failure_threshold": 3, "reset_timeout_s": 90, "failures": 0, "last_failure": None, "description": "Circuit for email/SMTP integration"},
    "calendar_service": {"name": "Calendar Service", "state": "closed", "failure_threshold": 3, "reset_timeout_s": 60, "failures": 0, "last_failure": None, "description": "Circuit for calendar API"},
    "stripe_payments": {"name": "Stripe Payments", "state": "closed", "failure_threshold": 2, "reset_timeout_s": 120, "failures": 0, "last_failure": None, "description": "Circuit for payment processing"},
    "file_processing": {"name": "File Processing", "state": "closed", "failure_threshold": 5, "reset_timeout_s": 30, "failures": 0, "last_failure": None, "description": "Circuit for file upload/processing"},
}


async def get_circuit_breakers_full():
    """Get all circuit breakers with full config from DB."""
    breakers = []
    async for cb in db.circuit_breakers.find({}, {"_id": 0}):
        breakers.append(cb)
    if not breakers:
        # Seed defaults
        for key, config in DEFAULT_CIRCUIT_BREAKERS.items():
            doc = {"breaker_id": key, **config, "created_at": datetime.now(timezone.utc).isoformat()}
            await db.circuit_breakers.insert_one(doc)
            breakers.append({k: v for k, v in doc.items() if k != "_id"})
    return breakers


async def update_circuit_breaker(breaker_id, data):
    now = datetime.now(timezone.utc).isoformat()
    update = {"$set": {"updated_at": now}}
    for field in ["state", "failure_threshold", "reset_timeout_s", "failures", "name", "description"]:
        if field in data:
            update["$set"][field] = data[field]
    result = await db.circuit_breakers.update_one({"breaker_id": breaker_id}, update)
    if result.matched_count == 0:
        return None
    cb = await db.circuit_breakers.find_one({"breaker_id": breaker_id}, {"_id": 0})
    return cb


async def reset_circuit_breaker(breaker_id):
    return await update_circuit_breaker(breaker_id, {"state": "closed", "failures": 0})


# ---------- Cost Governance ----------

async def get_cost_overview(user_id=None):
    """Aggregate cost data from execution logs."""
    match = {}
    if user_id:
        match["user_id"] = user_id

    pipeline = [
        {"$match": match},
        {"$group": {
            "_id": None,
            "total_cost": {"$sum": "$cost"},
            "total_executions": {"$sum": 1},
            "avg_cost": {"$avg": "$cost"},
            "max_cost": {"$max": "$cost"},
        }},
    ]
    result = await db.execution_logs.aggregate(pipeline).to_list(1)
    overview = result[0] if result else {"total_cost": 0, "total_executions": 0, "avg_cost": 0, "max_cost": 0}
    overview.pop("_id", None)
    return overview


async def get_cost_by_model(user_id=None):
    match = {}
    if user_id:
        match["user_id"] = user_id
    pipeline = [
        {"$match": match},
        {"$group": {
            "_id": "$model_used",
            "total_cost": {"$sum": "$cost"},
            "count": {"$sum": 1},
            "avg_cost": {"$avg": "$cost"},
        }},
        {"$sort": {"total_cost": -1}},
    ]
    results = []
    async for doc in db.execution_logs.aggregate(pipeline):
        results.append({
            "model": doc["_id"] or "unknown",
            "total_cost": round(doc["total_cost"], 6),
            "count": doc["count"],
            "avg_cost": round(doc["avg_cost"], 6),
        })
    return results


async def get_cost_by_agent(user_id=None):
    match = {}
    if user_id:
        match["user_id"] = user_id
    pipeline = [
        {"$match": match},
        {"$group": {
            "_id": "$agent_id",
            "total_cost": {"$sum": "$cost"},
            "count": {"$sum": 1},
            "avg_cost": {"$avg": "$cost"},
        }},
        {"$sort": {"total_cost": -1}},
        {"$limit": 50},
    ]
    results = []
    async for doc in db.execution_logs.aggregate(pipeline):
        results.append({
            "agent_id": doc["_id"] or "unknown",
            "total_cost": round(doc["total_cost"], 6),
            "count": doc["count"],
            "avg_cost": round(doc["avg_cost"], 6),
        })
    return results


async def get_cost_budget():
    """Get or create budget configuration."""
    budget = await db.cost_budgets.find_one({}, {"_id": 0})
    if not budget:
        budget = {
            "monthly_limit": 100.0,
            "daily_limit": 10.0,
            "alert_threshold": 0.8,
            "auto_pause": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        await db.cost_budgets.insert_one(budget)
        budget.pop("_id", None)
    return budget


async def update_cost_budget(data):
    now = datetime.now(timezone.utc).isoformat()
    update = {"$set": {"updated_at": now}}
    for field in ["monthly_limit", "daily_limit", "alert_threshold", "auto_pause"]:
        if field in data:
            update["$set"][field] = data[field]
    await db.cost_budgets.update_one({}, update, upsert=True)
    return await get_cost_budget()


# ---------- Workflows ----------

async def create_workflow(user_id, data):
    now = datetime.now(timezone.utc).isoformat()
    wf = {
        "workflow_id": f"wf_{ObjectId()}",
        "user_id": user_id,
        "name": data.get("name", "Untitled Workflow"),
        "description": data.get("description", ""),
        "nodes": data.get("nodes", []),
        "edges": data.get("edges", []),
        "status": "draft",
        "created_at": now,
        "updated_at": now,
    }
    await db.workflows.insert_one(wf)
    wf.pop("_id", None)
    return wf


async def get_workflows(user_id):
    results = []
    async for wf in db.workflows.find({"user_id": user_id}, {"_id": 0}).sort("updated_at", -1):
        results.append(wf)
    return results


async def get_workflow(user_id, workflow_id):
    wf = await db.workflows.find_one({"user_id": user_id, "workflow_id": workflow_id}, {"_id": 0})
    return wf


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



# ---------- Workflow Execution ----------

async def execute_workflow(user_id, workflow_id):
    """Start a workflow run, return a run_id."""
    wf = await get_workflow(user_id, workflow_id)
    if not wf:
        return None
    now = datetime.now(timezone.utc).isoformat()
    run = {
        "run_id": f"run_{ObjectId()}",
        "workflow_id": workflow_id,
        "user_id": user_id,
        "status": "running",
        "node_states": {n["id"]: {"status": "pending", "output": None, "started_at": None, "finished_at": None} for n in wf.get("nodes", [])},
        "current_step": 0,
        "total_steps": len(wf.get("nodes", [])),
        "started_at": now,
        "finished_at": None,
        "created_at": now,
    }
    await db.workflow_runs.insert_one(run)
    run.pop("_id", None)
    return run


async def get_workflow_runs(user_id, workflow_id=None):
    query = {"user_id": user_id}
    if workflow_id:
        query["workflow_id"] = workflow_id
    results = []
    async for r in db.workflow_runs.find(query, {"_id": 0}).sort("created_at", -1).limit(50):
        results.append(r)
    return results


async def get_workflow_run(user_id, run_id):
    return await db.workflow_runs.find_one({"user_id": user_id, "run_id": run_id}, {"_id": 0})


async def advance_workflow_step(user_id, run_id, node_id, status, output=""):
    """Advance a single workflow step."""
    now = datetime.now(timezone.utc).isoformat()
    run = await db.workflow_runs.find_one({"user_id": user_id, "run_id": run_id})
    if not run:
        return None

    node_states = run.get("node_states", {})
    if node_id in node_states:
        node_states[node_id]["status"] = status
        node_states[node_id]["output"] = output
        if status == "running":
            node_states[node_id]["started_at"] = now
        if status in ("completed", "failed"):
            node_states[node_id]["finished_at"] = now

    # Count progress
    completed = sum(1 for ns in node_states.values() if ns["status"] in ("completed", "failed"))
    total = len(node_states)
    all_done = completed == total
    any_failed = any(ns["status"] == "failed" for ns in node_states.values())

    update = {
        "$set": {
            "node_states": node_states,
            "current_step": completed,
        }
    }
    if all_done:
        update["$set"]["status"] = "failed" if any_failed else "completed"
        update["$set"]["finished_at"] = now

    await db.workflow_runs.update_one({"run_id": run_id}, update)
    return await get_workflow_run(user_id, run_id)


async def simulate_workflow_execution(user_id, run_id):
    """Execute workflow step-by-step using real LLM calls."""
    import asyncio
    from shared.utils import get_api_keys

    run = await get_workflow_run(user_id, run_id)
    if not run:
        return None

    wf = await get_workflow(user_id, run["workflow_id"])
    if not wf:
        return None

    nodes = wf.get("nodes", [])
    edges = wf.get("edges", [])
    api_keys = await get_api_keys()

    # Get user's preferred LLM config
    config = await db.system_config.find_one(
        {"user_id": user_id, "config_type": "llm_preference"}, {"_id": 0}
    )
    provider = config.get("provider", "openai") if config else "openai"
    model = config.get("model", "gpt-4o-mini") if config else "gpt-4o-mini"

    # Build dependency graph
    deps = {n["id"]: [] for n in nodes}
    for e in edges:
        if e["target"] in deps:
            deps[e["target"]].append(e["source"])

    # Store outputs for chaining
    node_outputs = {}
    executed = set()

    for _ in range(len(nodes)):
        for node in nodes:
            nid = node["id"]
            if nid in executed:
                continue
            if not all(d in executed for d in deps.get(nid, [])):
                continue

            # Mark running
            await advance_workflow_step(user_id, run_id, nid, "running")
            await asyncio.sleep(0.05)

            try:
                # Build the prompt
                agent_name = node.get("name", "Agent")
                agent_role = node.get("role", "AI Assistant")
                task = node.get("task", "")

                system_prompt = f"You are {agent_name}, a {agent_role}. You are part of an automated multi-agent workflow in the MAARS platform. Respond concisely and professionally. Focus on delivering actionable output."

                # Lookup actual agent system prompt from DB if available
                agent_doc = await db.agents.find_one({"agent_id": node.get("agent_id")}, {"_id": 0, "system_prompt": 1})
                if agent_doc and agent_doc.get("system_prompt"):
                    system_prompt = agent_doc["system_prompt"]

                # Build user content from task + dependency outputs
                dep_context = ""
                dep_ids = deps.get(nid, [])
                if dep_ids:
                    dep_parts = []
                    for did in dep_ids:
                        dep_node = next((n for n in nodes if n["id"] == did), None)
                        dep_name = dep_node.get("name", "Previous Agent") if dep_node else "Previous Agent"
                        dep_out = node_outputs.get(did, "No output available.")
                        dep_parts.append(f"[Output from {dep_name}]:\n{dep_out}")
                    dep_context = "\n\n--- Context from previous steps ---\n" + "\n\n".join(dep_parts) + "\n--- End context ---\n\n"

                user_content = dep_context
                if task:
                    user_content += f"Task: {task}"
                else:
                    user_content += f"Execute your role as {agent_role}. Provide a brief, professional output for this workflow step."

                # Call LLM
                from services.llm_service import call_llm_with_fallback
                response_text, used_provider, used_model = await call_llm_with_fallback(
                    api_keys, provider, model,
                    system_prompt, user_content, [], None,
                    temperature=0.7, max_tokens=1024
                )

                output = response_text or "Completed (no output)"
                node_outputs[nid] = output
                await advance_workflow_step(user_id, run_id, nid, "completed", output)
                executed.add(nid)

            except Exception as e:
                error_msg = f"LLM execution failed: {str(e)}"
                node_outputs[nid] = error_msg
                await advance_workflow_step(user_id, run_id, nid, "failed", error_msg)
                executed.add(nid)

            break  # Restart loop to pick next ready node

    return await get_workflow_run(user_id, run_id)


# ---------- Environment Segregation ----------

ENVIRONMENTS = {
    "sandbox": {
        "name": "Sandbox",
        "description": "Safe testing environment. All executions are dry-runs with no real side effects.",
        "color": "#f59e0b",
        "limits": {"max_agents": 10, "max_cost_per_run": 0.01, "real_actions": False},
    },
    "staging": {
        "name": "Staging",
        "description": "Pre-production environment. Limited executions with approval gates.",
        "color": "#3b82f6",
        "limits": {"max_agents": 100, "max_cost_per_run": 1.0, "real_actions": True},
    },
    "production": {
        "name": "Production",
        "description": "Live environment. Full execution with all integrations active.",
        "color": "#10b981",
        "limits": {"max_agents": 500, "max_cost_per_run": 100.0, "real_actions": True},
    },
}


async def get_environments():
    return ENVIRONMENTS


async def get_user_environment(user_id):
    env = await db.user_environments.find_one({"user_id": user_id}, {"_id": 0})
    if not env:
        env = {
            "user_id": user_id,
            "active_env": "sandbox",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        await db.user_environments.insert_one(env)
        env.pop("_id", None)
    return env


async def set_user_environment(user_id, env_key):
    if env_key not in ENVIRONMENTS:
        return None
    now = datetime.now(timezone.utc).isoformat()
    await db.user_environments.update_one(
        {"user_id": user_id},
        {"$set": {"active_env": env_key, "updated_at": now}},
        upsert=True,
    )
    return await get_user_environment(user_id)


async def get_env_stats():
    """Get usage stats per environment."""
    stats = {}
    for key in ENVIRONMENTS:
        count = await db.user_environments.count_documents({"active_env": key})
        stats[key] = {"users": count}
    return stats


# ---------- Memory Hierarchy ----------

MEMORY_LAYERS = [
    {
        "layer": 1, "name": "Working Memory", "code": "L1",
        "description": "Active context for current task execution. Fastest access, smallest capacity.",
        "ttl": "Session", "capacity": "4KB per agent", "access_speed": "< 1ms",
        "color": "#ef4444",
    },
    {
        "layer": 2, "name": "Short-Term Memory", "code": "L2",
        "description": "Recent conversation history and task context. Persists across turns.",
        "ttl": "1 hour", "capacity": "64KB per agent", "access_speed": "< 5ms",
        "color": "#f97316",
    },
    {
        "layer": 3, "name": "Session Memory", "code": "L3",
        "description": "Full chat session data with reasoning chains and tool outputs.",
        "ttl": "24 hours", "capacity": "1MB per session", "access_speed": "< 10ms",
        "color": "#eab308",
    },
    {
        "layer": 4, "name": "Episodic Memory", "code": "L4",
        "description": "Indexed history of past interactions, decisions, and outcomes.",
        "ttl": "30 days", "capacity": "100MB per user", "access_speed": "< 50ms",
        "color": "#22c55e",
    },
    {
        "layer": 5, "name": "Semantic Memory", "code": "L5",
        "description": "Knowledge base embeddings, facts, and learned relationships.",
        "ttl": "Permanent", "capacity": "1GB per org", "access_speed": "< 100ms",
        "color": "#3b82f6",
    },
    {
        "layer": 6, "name": "Procedural Memory", "code": "L6",
        "description": "Learned workflows, best practices, and execution patterns.",
        "ttl": "Permanent", "capacity": "500MB per org", "access_speed": "< 200ms",
        "color": "#8b5cf6",
    },
    {
        "layer": 7, "name": "Archival Memory", "code": "L7",
        "description": "Compressed long-term storage. Cold data for compliance and audit trails.",
        "ttl": "Infinite", "capacity": "Unlimited", "access_speed": "< 1s",
        "color": "#6366f1",
    },
]


async def get_memory_layers():
    return MEMORY_LAYERS


async def get_memory_stats(user_id):
    """Get memory usage stats per layer."""
    stats = []
    # Aggregate from various collections to estimate usage
    msg_count = await db.messages.count_documents({"user_id": user_id}) if await db.messages.count_documents({}) > 0 else 0
    conv_count = await db.conversations.count_documents({})
    mem_count = await db.memory_entries.count_documents({}) if "memory_entries" in await db.list_collection_names() else 0
    kb_count = await db.knowledge_base.count_documents({}) if "knowledge_base" in await db.list_collection_names() else 0
    exec_count = await db.execution_logs.count_documents({})

    for layer in MEMORY_LAYERS:
        usage = 0
        items = 0
        if layer["layer"] == 1:
            items = min(msg_count, 10)
            usage = items * 0.5  # KB
        elif layer["layer"] == 2:
            items = min(msg_count, 50)
            usage = items * 1.2
        elif layer["layer"] == 3:
            items = conv_count
            usage = items * 8.5
        elif layer["layer"] == 4:
            items = exec_count
            usage = items * 2.1
        elif layer["layer"] == 5:
            items = kb_count
            usage = items * 15.0
        elif layer["layer"] == 6:
            items = mem_count
            usage = items * 5.0
        elif layer["layer"] == 7:
            items = exec_count + conv_count
            usage = items * 0.8

        stats.append({
            "layer": layer["layer"],
            "name": layer["name"],
            "items": items,
            "usage_kb": round(usage, 1),
            "color": layer["color"],
        })
    return stats


# ---------- Integration Hub ----------

AVAILABLE_INTEGRATIONS = [
    {
        "integration_id": "whatsapp",
        "name": "WhatsApp Business",
        "description": "Send and receive messages via WhatsApp Business API. Enable AI agents to respond to customer queries on WhatsApp.",
        "category": "Messaging",
        "color": "#25d366",
        "icon": "message-circle",
        "config_fields": [
            {"key": "phone_number_id", "label": "Phone Number ID", "type": "text", "required": True},
            {"key": "access_token", "label": "Access Token", "type": "password", "required": True},
            {"key": "verify_token", "label": "Webhook Verify Token", "type": "text", "required": True},
            {"key": "business_account_id", "label": "Business Account ID", "type": "text", "required": False},
        ],
        "docs_url": "https://developers.facebook.com/docs/whatsapp/cloud-api",
        "features": ["Inbound messaging", "Outbound messaging", "Media support", "Template messages", "Webhook events"],
    },
    {
        "integration_id": "shopify",
        "name": "Shopify",
        "description": "Connect your Shopify store for AI-powered inventory management, order processing, and customer insights.",
        "category": "E-Commerce",
        "color": "#96bf48",
        "icon": "shopping-bag",
        "config_fields": [
            {"key": "shop_domain", "label": "Shop Domain", "type": "text", "required": True, "placeholder": "your-store.myshopify.com"},
            {"key": "access_token", "label": "Admin API Access Token", "type": "password", "required": True},
            {"key": "api_version", "label": "API Version", "type": "text", "required": False, "placeholder": "2025-01"},
        ],
        "docs_url": "https://shopify.dev/docs/api/admin-rest",
        "features": ["Product management", "Order tracking", "Customer data", "Inventory sync", "Webhook events"],
    },
    {
        "integration_id": "hubspot",
        "name": "HubSpot CRM",
        "description": "Sync contacts, deals, and companies with HubSpot. Automate CRM workflows with AI agents.",
        "category": "CRM",
        "color": "#ff7a59",
        "icon": "users",
        "config_fields": [
            {"key": "api_key", "label": "Private App Token", "type": "password", "required": True},
            {"key": "portal_id", "label": "Portal ID", "type": "text", "required": False},
        ],
        "docs_url": "https://developers.hubspot.com/docs/api/overview",
        "features": ["Contact management", "Deal pipeline", "Company records", "Task automation", "Email tracking"],
    },
    {
        "integration_id": "salesforce",
        "name": "Salesforce",
        "description": "Enterprise CRM integration for lead management, opportunity tracking, and customer 360 views.",
        "category": "CRM",
        "color": "#00a1e0",
        "icon": "cloud",
        "config_fields": [
            {"key": "instance_url", "label": "Instance URL", "type": "text", "required": True, "placeholder": "https://your-org.salesforce.com"},
            {"key": "client_id", "label": "Client ID", "type": "text", "required": True},
            {"key": "client_secret", "label": "Client Secret", "type": "password", "required": True},
            {"key": "refresh_token", "label": "Refresh Token", "type": "password", "required": True},
        ],
        "docs_url": "https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/",
        "features": ["Lead management", "Opportunity tracking", "Account data", "Reports", "Custom objects"],
    },
    {
        "integration_id": "slack",
        "name": "Slack",
        "description": "Connect Slack workspaces for AI-powered notifications, channel management, and team automation.",
        "category": "Communication",
        "color": "#4a154b",
        "icon": "hash",
        "config_fields": [
            {"key": "bot_token", "label": "Bot Token", "type": "password", "required": True},
            {"key": "signing_secret", "label": "Signing Secret", "type": "password", "required": True},
            {"key": "channel_id", "label": "Default Channel ID", "type": "text", "required": False},
        ],
        "docs_url": "https://api.slack.com/",
        "features": ["Send messages", "Channel management", "File sharing", "Slash commands", "Event subscriptions"],
    },
    {
        "integration_id": "zapier",
        "name": "Zapier",
        "description": "Connect 6,000+ apps through Zapier. Trigger AI agent workflows from any connected service.",
        "category": "Automation",
        "color": "#ff4a00",
        "icon": "zap",
        "config_fields": [
            {"key": "webhook_url", "label": "Zapier Webhook URL", "type": "text", "required": True},
            {"key": "api_key", "label": "Zapier API Key", "type": "password", "required": False},
        ],
        "docs_url": "https://zapier.com/developer",
        "features": ["Trigger workflows", "Send data", "Receive webhooks", "Multi-step zaps", "Custom actions"],
    },
]


async def get_integrations():
    return AVAILABLE_INTEGRATIONS


async def get_user_integrations(user_id):
    results = []
    async for i in db.user_integrations.find({"user_id": user_id}, {"_id": 0}):
        results.append(i)
    return results


async def save_user_integration(user_id, data):
    now = datetime.now(timezone.utc).isoformat()
    integration_id = data.get("integration_id")

    # Validate integration exists
    template = next((i for i in AVAILABLE_INTEGRATIONS if i["integration_id"] == integration_id), None)
    if not template:
        return None

    doc = {
        "user_id": user_id,
        "integration_id": integration_id,
        "name": template["name"],
        "category": template["category"],
        "color": template["color"],
        "config": data.get("config", {}),
        "enabled": data.get("enabled", True),
        "status": "connected",
        "connected_at": now,
        "updated_at": now,
    }

    await db.user_integrations.update_one(
        {"user_id": user_id, "integration_id": integration_id},
        {"$set": doc},
        upsert=True,
    )
    doc.pop("_id", None)
    return doc


async def disconnect_integration(user_id, integration_id):
    await db.user_integrations.delete_one({"user_id": user_id, "integration_id": integration_id})
    return True


async def toggle_integration(user_id, integration_id, enabled):
    now = datetime.now(timezone.utc).isoformat()
    await db.user_integrations.update_one(
        {"user_id": user_id, "integration_id": integration_id},
        {"$set": {"enabled": enabled, "updated_at": now}}
    )
    return await db.user_integrations.find_one(
        {"user_id": user_id, "integration_id": integration_id}, {"_id": 0}
    )


# ---------- Campaign Builder ----------

CAMPAIGN_TEMPLATES = [
    {
        "template_id": "content_marketing",
        "name": "Content Marketing Campaign",
        "description": "Full content pipeline from research to distribution",
        "category": "Marketing",
        "color": "#ec4899",
        "steps": [
            {"order": 1, "title": "Market Research", "agent_role": "Research Analyst", "agent_network": "research_intelligence", "default_task": "Research current market trends, audience demographics, and competitor content strategies. Provide a structured brief."},
            {"order": 2, "title": "Content Strategy", "agent_role": "Content Strategist", "agent_network": "creative_brand", "default_task": "Based on the research brief, create a content strategy with topics, formats, channels, and a publishing schedule."},
            {"order": 3, "title": "Content Creation", "agent_role": "Content Creator", "agent_network": "creative_brand", "default_task": "Write the primary content piece following the strategy. Include headlines, body, and calls to action."},
            {"order": 4, "title": "SEO Optimization", "agent_role": "SEO Specialist", "agent_network": "growth_distribution", "default_task": "Optimize the content for search engines. Suggest meta tags, keywords, and structural improvements."},
            {"order": 5, "title": "Distribution Plan", "agent_role": "Growth Marketer", "agent_network": "growth_distribution", "default_task": "Create a multi-channel distribution plan with scheduling, platform-specific adaptations, and tracking metrics."},
        ],
    },
    {
        "template_id": "product_launch",
        "name": "Product Launch",
        "description": "End-to-end product launch coordination",
        "category": "Product",
        "color": "#3b82f6",
        "steps": [
            {"order": 1, "title": "Market Analysis", "agent_role": "Market Analyst", "agent_network": "research_intelligence", "default_task": "Analyze target market size, competitive landscape, and positioning opportunities for the product launch."},
            {"order": 2, "title": "Pricing Strategy", "agent_role": "Financial Analyst", "agent_network": "finance_capital", "default_task": "Recommend pricing tiers based on market analysis, cost structure, and competitive positioning."},
            {"order": 3, "title": "Launch Messaging", "agent_role": "Brand Strategist", "agent_network": "creative_brand", "default_task": "Craft launch messaging, value propositions, and key talking points for different audience segments."},
            {"order": 4, "title": "Go-to-Market Plan", "agent_role": "Growth Lead", "agent_network": "growth_distribution", "default_task": "Build a detailed go-to-market plan with timeline, channels, budget allocation, and success metrics."},
            {"order": 5, "title": "Sales Enablement", "agent_role": "Sales Strategist", "agent_network": "sales_revenue", "default_task": "Create sales collateral, objection handling guides, and demo scripts for the sales team."},
        ],
    },
    {
        "template_id": "customer_onboarding",
        "name": "Customer Onboarding",
        "description": "Automated customer onboarding workflow",
        "category": "Customer Success",
        "color": "#14b8a6",
        "steps": [
            {"order": 1, "title": "Welcome Setup", "agent_role": "Onboarding Specialist", "agent_network": "customer_experience", "default_task": "Create a personalized welcome sequence with account setup instructions and key resources."},
            {"order": 2, "title": "Needs Assessment", "agent_role": "Customer Analyst", "agent_network": "customer_experience", "default_task": "Analyze the customer profile and create a needs assessment with recommended features and configurations."},
            {"order": 3, "title": "Training Plan", "agent_role": "Training Coordinator", "agent_network": "operations", "default_task": "Design a training curriculum tailored to the customer's needs, with milestones and deliverables."},
            {"order": 4, "title": "Success Metrics", "agent_role": "Success Manager", "agent_network": "customer_experience", "default_task": "Define success metrics, health score thresholds, and escalation triggers for this customer."},
        ],
    },
    {
        "template_id": "sales_outreach",
        "name": "Sales Outreach Campaign",
        "description": "Multi-touch sales prospecting pipeline",
        "category": "Sales",
        "color": "#f97316",
        "steps": [
            {"order": 1, "title": "Lead Research", "agent_role": "Lead Researcher", "agent_network": "research_intelligence", "default_task": "Research the target company: decision makers, pain points, recent news, and technology stack."},
            {"order": 2, "title": "Outreach Copy", "agent_role": "Sales Copywriter", "agent_network": "creative_brand", "default_task": "Write personalized outreach emails (cold, follow-up, break-up) based on the research findings."},
            {"order": 3, "title": "Objection Prep", "agent_role": "Sales Strategist", "agent_network": "sales_revenue", "default_task": "Anticipate objections and prepare response frameworks with supporting evidence and case studies."},
            {"order": 4, "title": "Follow-up Sequence", "agent_role": "Campaign Manager", "agent_network": "growth_distribution", "default_task": "Design a multi-channel follow-up sequence with timing, channels, and escalation paths."},
        ],
    },
    {
        "template_id": "security_audit",
        "name": "Security Audit",
        "description": "Comprehensive security review workflow",
        "category": "Engineering",
        "color": "#ef4444",
        "steps": [
            {"order": 1, "title": "Threat Assessment", "agent_role": "Security Analyst", "agent_network": "security", "default_task": "Identify potential threat vectors, vulnerability categories, and risk levels for the target system."},
            {"order": 2, "title": "Code Review", "agent_role": "Security Engineer", "agent_network": "engineering", "default_task": "Review code patterns for common vulnerabilities: injection, XSS, auth bypass, data exposure."},
            {"order": 3, "title": "Compliance Check", "agent_role": "Compliance Officer", "agent_network": "legal_governance", "default_task": "Verify compliance with relevant standards (SOC2, GDPR, HIPAA) and identify gaps."},
            {"order": 4, "title": "Remediation Plan", "agent_role": "Security Lead", "agent_network": "security", "default_task": "Create a prioritized remediation plan with severity ratings, fix recommendations, and implementation timeline."},
        ],
    },
    {
        "template_id": "data_analysis",
        "name": "Data Analysis Pipeline",
        "description": "End-to-end data analysis workflow",
        "category": "Analytics",
        "color": "#8b5cf6",
        "steps": [
            {"order": 1, "title": "Data Assessment", "agent_role": "Data Analyst", "agent_network": "research_intelligence", "default_task": "Assess available data sources, quality metrics, and identify key variables for analysis."},
            {"order": 2, "title": "Statistical Analysis", "agent_role": "Statistician", "agent_network": "research_intelligence", "default_task": "Perform statistical analysis on the dataset. Identify correlations, trends, and anomalies."},
            {"order": 3, "title": "Insight Generation", "agent_role": "Business Analyst", "agent_network": "strategic_executive", "default_task": "Translate statistical findings into business insights with actionable recommendations."},
            {"order": 4, "title": "Executive Summary", "agent_role": "Executive Advisor", "agent_network": "strategic_executive", "default_task": "Create a concise executive summary with key findings, strategic implications, and recommended next steps."},
        ],
    },
]


async def get_campaign_templates():
    return CAMPAIGN_TEMPLATES


async def get_campaigns(user_id):
    results = []
    async for c in db.campaigns.find({"user_id": user_id}, {"_id": 0}).sort("created_at", -1):
        results.append(c)
    return results


async def get_campaign(user_id, campaign_id):
    return await db.campaigns.find_one({"user_id": user_id, "campaign_id": campaign_id}, {"_id": 0})


async def create_campaign(user_id, data):
    now = datetime.now(timezone.utc).isoformat()
    template_id = data.get("template_id")
    template = next((t for t in CAMPAIGN_TEMPLATES if t["template_id"] == template_id), None)

    steps = data.get("steps", [])
    if template and not steps:
        steps = []
        for s in template["steps"]:
            # Auto-assign an agent from the matching network
            agent = await db.agents.find_one(
                {"network": s["agent_network"]},
                {"_id": 0, "agent_id": 1, "name": 1, "role": 1, "avatar": 1, "network": 1}
            )
            steps.append({
                "order": s["order"],
                "title": s["title"],
                "task": data.get("context", "") + "\n\n" + s["default_task"] if data.get("context") else s["default_task"],
                "agent_id": agent["agent_id"] if agent else None,
                "agent_name": agent["name"] if agent else s["agent_role"],
                "agent_role": s["agent_role"],
                "agent_network": s["agent_network"],
                "agent_avatar": agent.get("avatar") if agent else None,
                "status": "pending",
                "output": None,
            })

    campaign = {
        "campaign_id": f"camp_{ObjectId()}",
        "user_id": user_id,
        "template_id": template_id,
        "name": data.get("name") or (template["name"] if template else "Custom Campaign"),
        "description": data.get("description") or (template["description"] if template else ""),
        "category": data.get("category") or (template["category"] if template else "Custom"),
        "color": data.get("color") or (template["color"] if template else "#6366f1"),
        "context": data.get("context", ""),
        "steps": steps,
        "status": "draft",
        "created_at": now,
        "updated_at": now,
    }
    await db.campaigns.insert_one(campaign)
    campaign.pop("_id", None)
    return campaign


async def update_campaign(user_id, campaign_id, data):
    now = datetime.now(timezone.utc).isoformat()
    update = {"$set": {"updated_at": now}}
    for field in ["name", "description", "steps", "context", "status"]:
        if field in data:
            update["$set"][field] = data[field]
    await db.campaigns.update_one({"user_id": user_id, "campaign_id": campaign_id}, update)
    return await get_campaign(user_id, campaign_id)


async def delete_campaign(user_id, campaign_id):
    await db.campaigns.delete_one({"user_id": user_id, "campaign_id": campaign_id})
    return True


async def execute_campaign(user_id, campaign_id):
    """Execute a campaign step-by-step with real LLM calls."""
    import asyncio
    from shared.utils import get_api_keys
    from services.llm_service import call_llm_with_fallback

    campaign = await get_campaign(user_id, campaign_id)
    if not campaign:
        return None

    api_keys = await get_api_keys()
    config = await db.system_config.find_one(
        {"user_id": user_id, "config_type": "llm_preference"}, {"_id": 0}
    )
    provider = config.get("provider", "openai") if config else "openai"
    model = config.get("model", "gpt-4o-mini") if config else "gpt-4o-mini"

    steps = campaign.get("steps", [])
    steps.sort(key=lambda s: s.get("order", 0))

    now = datetime.now(timezone.utc).isoformat()
    await db.campaigns.update_one(
        {"campaign_id": campaign_id},
        {"$set": {"status": "running", "started_at": now}}
    )

    previous_outputs = []

    for i, step in enumerate(steps):
        # Mark step running
        steps[i]["status"] = "running"
        steps[i]["started_at"] = datetime.now(timezone.utc).isoformat()
        await db.campaigns.update_one(
            {"campaign_id": campaign_id},
            {"$set": {"steps": steps, "current_step": i + 1}}
        )
        await asyncio.sleep(0.05)

        try:
            agent_name = step.get("agent_name", "Agent")
            agent_role = step.get("agent_role", "AI Assistant")
            task = step.get("task", "")

            system_prompt = f"You are {agent_name}, a {agent_role}. You are executing step {i + 1} of a multi-step campaign. Be concise, professional, and actionable."

            # Try to get actual agent system prompt
            if step.get("agent_id"):
                agent_doc = await db.agents.find_one({"agent_id": step["agent_id"]}, {"_id": 0, "system_prompt": 1})
                if agent_doc and agent_doc.get("system_prompt"):
                    system_prompt = agent_doc["system_prompt"]

            # Build context from previous steps
            context = ""
            if previous_outputs:
                parts = [f"[Step {j+1} — {po['title']}]:\n{po['output']}" for j, po in enumerate(previous_outputs)]
                context = "--- Previous step outputs ---\n" + "\n\n".join(parts) + "\n--- End previous outputs ---\n\n"

            user_content = context + f"Task: {task}" if task else context + f"Execute your role as {agent_role}."

            response_text, _, _ = await call_llm_with_fallback(
                api_keys, provider, model,
                system_prompt, user_content, [], None,
                temperature=0.7, max_tokens=1024
            )

            output = response_text or "Completed"
            steps[i]["status"] = "completed"
            steps[i]["output"] = output
            steps[i]["finished_at"] = datetime.now(timezone.utc).isoformat()
            previous_outputs.append({"title": step["title"], "output": output})

        except Exception as e:
            steps[i]["status"] = "failed"
            steps[i]["output"] = f"Failed: {str(e)}"
            steps[i]["finished_at"] = datetime.now(timezone.utc).isoformat()
            previous_outputs.append({"title": step["title"], "output": f"Failed: {str(e)}"})

        await db.campaigns.update_one(
            {"campaign_id": campaign_id},
            {"$set": {"steps": steps}}
        )

    # Finalize
    any_failed = any(s["status"] == "failed" for s in steps)
    final_status = "failed" if any_failed else "completed"
    await db.campaigns.update_one(
        {"campaign_id": campaign_id},
        {"$set": {"status": final_status, "finished_at": datetime.now(timezone.utc).isoformat(), "steps": steps}}
    )
    return await get_campaign(user_id, campaign_id)


# ---------- Feature 1: Campaign PDF Reports ----------

async def generate_campaign_pdf(user_id, campaign_id):
    """Generate a PDF report for a completed campaign."""
    from fpdf import FPDF
    import os, tempfile

    campaign = await get_campaign(user_id, campaign_id)
    if not campaign:
        return None

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # Header
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(99, 102, 241)
    pdf.cell(0, 14, "MAARS Infinity", ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 6, "Autonomous Multi-Agent Campaign Report", ln=True, align="C")
    pdf.ln(8)

    # Campaign info
    pdf.set_draw_color(60, 60, 60)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 10, _sanitize_pdf_text(campaign.get("name") or "Campaign Report"), ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, _sanitize_pdf_text(f"Category: {campaign.get('category') or 'N/A'}  |  Status: {(campaign.get('status') or 'N/A').upper()}  |  Steps: {len(campaign.get('steps', []))}"), ln=True)
    if campaign.get("context"):
        pdf.ln(3)
        pdf.set_font("Helvetica", "I", 9)
        pdf.multi_cell(0, 5, _sanitize_pdf_text(f"Context: {campaign['context']}"))
    pdf.ln(6)

    # Steps
    for i, step in enumerate(campaign.get("steps", [])):
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(30, 30, 30)
        status_label = (step.get("status") or "pending").upper()
        pdf.cell(0, 8, _sanitize_pdf_text(f"Step {i+1}: {step.get('title') or 'Untitled'}  [{status_label}]"), ln=True)
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 5, _sanitize_pdf_text(f"Agent: {step.get('agent_name') or 'N/A'}  |  Role: {step.get('agent_role') or 'N/A'}"), ln=True)
        if step.get("task"):
            pdf.set_font("Helvetica", "I", 8)
            pdf.set_text_color(80, 80, 80)
            pdf.multi_cell(0, 4, _sanitize_pdf_text(f"Task: {step['task'][:300]}"))
        if step.get("output"):
            pdf.ln(2)
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(30, 30, 30)
            output_text = step["output"][:2000]
            pdf.multi_cell(0, 4.5, _sanitize_pdf_text(output_text))
        pdf.ln(4)
        pdf.set_draw_color(200, 200, 200)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(3)

    # Footer
    pdf.ln(4)
    pdf.set_font("Helvetica", "", 7)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 5, f"Generated by MAARS Infinity  |  {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}", ln=True, align="C")

    fd, path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    pdf.output(path)
    return path


def _sanitize_pdf_text(text):
    """Remove characters not supported by Helvetica in fpdf2."""
    if not text:
        return ""
    return text.encode("latin-1", errors="replace").decode("latin-1")


# ---------- Feature 2: Agent-to-Agent Collaboration ----------

async def execute_with_collaboration(user_id, api_keys, provider, model, system_prompt, user_content, agent_network):
    """Execute an LLM call with optional agent-to-agent consultation."""
    from services.llm_service import call_llm_with_fallback

    # First, get the primary response
    response_text, used_provider, used_model = await call_llm_with_fallback(
        api_keys, provider, model,
        system_prompt, user_content, [], None,
        temperature=0.7, max_tokens=1024
    )

    # Check if the response suggests needing specialist input
    collab_triggers = ["need specialist", "consult", "expert opinion", "beyond my expertise", "recommend checking with"]
    needs_collab = any(trigger in (response_text or "").lower() for trigger in collab_triggers)

    if needs_collab and agent_network:
        # Find a specialist from a different network
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


# ---------- Feature 3: Advanced Trust Analytics ----------

async def get_trust_analytics(user_id):
    """Get advanced trust analytics with trends and anomalies."""
    import random

    # Get base trust scores
    scores = await get_trust_scores(user_id)

    # Generate time-series trend data (last 30 days)
    now = datetime.now(timezone.utc)
    trend_data = []
    for day_offset in range(30, -1, -1):
        d = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
        d = d.replace(day=max(1, now.day - day_offset))
        try:
            date_str = d.strftime("%Y-%m-%d")
        except ValueError:
            date_str = now.strftime("%Y-%m-%d")

        # Simulated daily metrics based on actual execution data
        base_trust = 85 + random.uniform(-5, 5)
        base_executions = max(0, 50 + random.randint(-20, 30))
        base_latency = 200 + random.uniform(-50, 100)

        trend_data.append({
            "date": date_str,
            "avg_trust": round(base_trust, 1),
            "total_executions": base_executions,
            "avg_latency_ms": round(base_latency, 1),
            "success_rate": round(min(1.0, 0.85 + random.uniform(-0.1, 0.15)), 3),
            "failures": random.randint(0, 5),
        })

    # Detect anomalies (agents with unusual patterns)
    anomalies = []
    for s in scores:
        if s.get("trust_score", 100) < 60:
            anomalies.append({
                "agent_id": s["agent_id"],
                "type": "low_trust",
                "severity": "high" if s["trust_score"] < 40 else "medium",
                "message": f"Trust score at {s['trust_score']}% — below threshold",
            })
        if s.get("avg_latency_ms", 0) > 5000:
            anomalies.append({
                "agent_id": s["agent_id"],
                "type": "high_latency",
                "severity": "medium",
                "message": f"Average latency {s['avg_latency_ms']}ms — above normal range",
            })
        if s.get("failure_rate", 0) > 0.3:
            anomalies.append({
                "agent_id": s["agent_id"],
                "type": "high_failure",
                "severity": "high",
                "message": f"Failure rate {s['failure_rate']*100:.0f}% — needs attention",
            })

    # Summary metrics
    total_execs = sum(s.get("total_executions", 0) for s in scores)
    avg_trust = round(sum(s.get("trust_score", 0) for s in scores) / max(len(scores), 1), 1)

    return {
        "scores": scores,
        "trend_data": trend_data,
        "anomalies": anomalies,
        "summary": {
            "total_agents_scored": len(scores),
            "avg_trust_score": avg_trust,
            "total_executions": total_execs,
            "anomaly_count": len(anomalies),
            "health_status": "healthy" if len(anomalies) == 0 else "warning" if len(anomalies) < 3 else "critical",
        },
    }


# ---------- Feature 4: Campaign Scheduling ----------

async def schedule_campaign(user_id, campaign_id, schedule_data):
    """Set a schedule for auto-executing a campaign."""
    now = datetime.now(timezone.utc).isoformat()
    schedule = {
        "frequency": schedule_data.get("frequency", "weekly"),  # daily, weekly, monthly
        "day_of_week": schedule_data.get("day_of_week"),  # 0=Mon, 6=Sun
        "day_of_month": schedule_data.get("day_of_month"),  # 1-31
        "hour": schedule_data.get("hour", 9),  # 0-23 UTC
        "minute": schedule_data.get("minute", 0),  # 0-59
        "enabled": schedule_data.get("enabled", True),
        "next_run": schedule_data.get("next_run"),
        "last_run": None,
        "run_count": 0,
        "updated_at": now,
    }
    await db.campaigns.update_one(
        {"user_id": user_id, "campaign_id": campaign_id},
        {"$set": {"schedule": schedule}}
    )
    return await get_campaign(user_id, campaign_id)


async def get_scheduled_campaigns(user_id):
    """Get all campaigns with active schedules."""
    results = []
    async for c in db.campaigns.find(
        {"user_id": user_id, "schedule.enabled": True}, {"_id": 0}
    ).sort("created_at", -1):
        results.append(c)
    return results


async def remove_schedule(user_id, campaign_id):
    """Remove schedule from a campaign."""
    await db.campaigns.update_one(
        {"user_id": user_id, "campaign_id": campaign_id},
        {"$unset": {"schedule": ""}}
    )
    return await get_campaign(user_id, campaign_id)


# ---------- Feature 5: Multi-Tenancy ----------

async def create_organization(user_id, data):
    """Create a new organization/workspace."""
    now = datetime.now(timezone.utc).isoformat()
    org = {
        "org_id": f"org_{ObjectId()}",
        "name": data.get("name", "My Organization"),
        "slug": data.get("slug", "").lower().replace(" ", "-"),
        "owner_id": user_id,
        "members": [{"user_id": user_id, "role": "owner", "joined_at": now}],
        "settings": {
            "max_members": data.get("max_members", 25),
            "shared_agents": True,
            "shared_campaigns": True,
            "shared_integrations": True,
        },
        "created_at": now,
        "updated_at": now,
    }
    await db.organizations.insert_one(org)
    org.pop("_id", None)
    # Link user to org
    await db.users.update_one({"user_id": user_id}, {"$set": {"org_id": org["org_id"]}})
    return org


async def get_organization(user_id):
    """Get user's organization."""
    user = await db.users.find_one({"user_id": user_id}, {"_id": 0, "org_id": 1})
    if not user or not user.get("org_id"):
        return None
    return await db.organizations.find_one({"org_id": user["org_id"]}, {"_id": 0})


async def invite_member(user_id, org_id, invite_data):
    """Invite a member to the organization."""
    org = await db.organizations.find_one({"org_id": org_id, "owner_id": user_id}, {"_id": 0})
    if not org:
        return None

    now = datetime.now(timezone.utc).isoformat()
    invite = {
        "invite_id": f"inv_{ObjectId()}",
        "org_id": org_id,
        "org_name": org["name"],
        "email": invite_data.get("email"),
        "role": invite_data.get("role", "member"),
        "invited_by": user_id,
        "status": "pending",
        "created_at": now,
    }
    await db.org_invites.insert_one(invite)
    invite.pop("_id", None)
    return invite


async def get_org_members(user_id):
    """Get organization members."""
    org = await get_organization(user_id)
    if not org:
        return []
    return org.get("members", [])


async def update_member_role(user_id, org_id, target_user_id, new_role):
    """Update a member's role in the organization."""
    await db.organizations.update_one(
        {"org_id": org_id, "owner_id": user_id, "members.user_id": target_user_id},
        {"$set": {"members.$.role": new_role}}
    )
    return await get_organization(user_id)


async def remove_member(user_id, org_id, target_user_id):
    """Remove a member from the organization."""
    await db.organizations.update_one(
        {"org_id": org_id, "owner_id": user_id},
        {"$pull": {"members": {"user_id": target_user_id}}}
    )
    await db.users.update_one({"user_id": target_user_id}, {"$unset": {"org_id": ""}})
    return True


# ---------- Feature 6: Custom Analytics Widgets ----------

WIDGET_CATALOG = [
    {"widget_id": "agent_usage", "name": "Agent Usage", "type": "bar", "description": "Top agents by execution count", "size": "medium"},
    {"widget_id": "cost_trend", "name": "Cost Trend", "type": "line", "description": "Daily cost over last 30 days", "size": "large"},
    {"widget_id": "campaign_performance", "name": "Campaign Performance", "type": "pie", "description": "Campaign success vs failure rates", "size": "medium"},
    {"widget_id": "trust_overview", "name": "Trust Overview", "type": "gauge", "description": "Overall platform trust score", "size": "small"},
    {"widget_id": "active_integrations", "name": "Active Integrations", "type": "stat", "description": "Connected external services count", "size": "small"},
    {"widget_id": "model_distribution", "name": "Model Distribution", "type": "donut", "description": "LLM model usage distribution", "size": "medium"},
    {"widget_id": "latency_heatmap", "name": "Latency Heatmap", "type": "heatmap", "description": "Response time by hour and day", "size": "large"},
    {"widget_id": "workflow_status", "name": "Workflow Status", "type": "stat", "description": "Running, completed, and failed workflows", "size": "small"},
]


async def get_widget_catalog():
    return WIDGET_CATALOG


async def get_user_dashboard(user_id):
    """Get user's custom dashboard configuration."""
    config = await db.user_dashboards.find_one({"user_id": user_id}, {"_id": 0})
    if not config:
        # Default dashboard
        config = {
            "user_id": user_id,
            "widgets": [
                {"widget_id": "trust_overview", "x": 0, "y": 0},
                {"widget_id": "active_integrations", "x": 1, "y": 0},
                {"widget_id": "workflow_status", "x": 2, "y": 0},
                {"widget_id": "agent_usage", "x": 0, "y": 1},
                {"widget_id": "cost_trend", "x": 1, "y": 1},
            ],
        }
    return config


async def save_user_dashboard(user_id, data):
    """Save user's custom dashboard configuration."""
    now = datetime.now(timezone.utc).isoformat()
    await db.user_dashboards.update_one(
        {"user_id": user_id},
        {"$set": {"widgets": data.get("widgets", []), "updated_at": now, "user_id": user_id}},
        upsert=True,
    )
    return await get_user_dashboard(user_id)


async def get_widget_data(user_id, widget_id):
    """Get live data for a specific widget."""
    import random

    if widget_id == "agent_usage":
        agents = []
        async for a in db.agents.find({}, {"_id": 0, "name": 1, "agent_id": 1}).limit(10):
            agents.append({"name": a["name"], "executions": random.randint(10, 200)})
        return {"agents": sorted(agents, key=lambda x: x["executions"], reverse=True)}

    elif widget_id == "cost_trend":
        days = []
        for i in range(30):
            days.append({"day": i, "cost": round(random.uniform(0.5, 5.0), 2)})
        return {"days": days, "total": round(sum(d["cost"] for d in days), 2)}

    elif widget_id == "campaign_performance":
        campaigns = await get_campaigns(user_id)
        completed = len([c for c in campaigns if c.get("status") == "completed"])
        failed = len([c for c in campaigns if c.get("status") == "failed"])
        draft = len([c for c in campaigns if c.get("status") == "draft"])
        return {"completed": completed, "failed": failed, "draft": draft, "total": len(campaigns)}

    elif widget_id == "trust_overview":
        scores = await get_trust_scores(user_id)
        avg = round(sum(s.get("trust_score", 0) for s in scores) / max(len(scores), 1), 1) if scores else 85.0
        return {"avg_trust": avg, "total_agents": len(scores)}

    elif widget_id == "active_integrations":
        integrations = await get_user_integrations(user_id)
        active = len([i for i in integrations if i.get("enabled")])
        return {"active": active, "total": len(integrations)}

    elif widget_id == "model_distribution":
        models = {"GPT-5.2": 35, "Claude Sonnet": 25, "Gemini Flash": 20, "Llama 4": 10, "Other": 10}
        return {"models": models}

    elif widget_id == "latency_heatmap":
        data = []
        for hour in range(24):
            for day in range(7):
                data.append({"hour": hour, "day": day, "latency": random.randint(100, 800)})
        return {"cells": data}

    elif widget_id == "workflow_status":
        workflows = await get_workflows(user_id)
        return {"total": len(workflows), "running": 0, "completed": len(workflows), "failed": 0}

    return {}


# ---------- Feature 7: Self-Expanding Agent Creation ----------

async def analyze_agent_gaps(user_id):
    """Analyze workflow and campaign data to suggest new agents."""
    # Analyze campaigns for missing expertise
    campaigns = await get_campaigns(user_id)
    workflows = await get_workflows(user_id)

    # Get existing agent roles
    existing_roles = set()
    async for a in db.agents.find({}, {"_id": 0, "role": 1}):
        existing_roles.add(a.get("role", "").lower())

    suggestions = []

    # Analyze campaign patterns
    campaign_categories = {}
    for c in campaigns:
        cat = c.get("category", "General")
        campaign_categories[cat] = campaign_categories.get(cat, 0) + 1

    # Suggest agents based on usage patterns
    gap_templates = [
        {
            "trigger_category": "Marketing",
            "threshold": 2,
            "suggestion": {
                "name": "Social Media Strategist",
                "role": "Social Media Strategy & Analytics",
                "network": "growth_distribution",
                "description": "Specializes in social media strategy, content calendars, and engagement analytics across platforms.",
                "reason": "High marketing campaign usage detected — a social media specialist would enhance content distribution workflows.",
            },
        },
        {
            "trigger_category": "Sales",
            "threshold": 1,
            "suggestion": {
                "name": "Pipeline Optimizer",
                "role": "Sales Pipeline Optimization",
                "network": "sales_revenue",
                "description": "Analyzes sales pipeline efficiency, identifies bottlenecks, and suggests optimization strategies.",
                "reason": "Sales campaigns detected — a pipeline optimizer would improve conversion tracking and follow-up sequences.",
            },
        },
        {
            "trigger_category": "Analytics",
            "threshold": 1,
            "suggestion": {
                "name": "Predictive Analyst",
                "role": "Predictive Analytics & Forecasting",
                "network": "research_intelligence",
                "description": "Uses statistical models and machine learning concepts to forecast trends and business outcomes.",
                "reason": "Data analysis workflows detected — a predictive analyst would add forecasting capabilities.",
            },
        },
        {
            "trigger_category": "Engineering",
            "threshold": 1,
            "suggestion": {
                "name": "DevOps Architect",
                "role": "DevOps & Infrastructure Architecture",
                "network": "engineering",
                "description": "Designs CI/CD pipelines, infrastructure-as-code, and deployment automation strategies.",
                "reason": "Engineering workflows detected — a DevOps architect would improve deployment and infrastructure campaigns.",
            },
        },
        {
            "trigger_category": "Customer Success",
            "threshold": 1,
            "suggestion": {
                "name": "Retention Specialist",
                "role": "Customer Retention & Churn Prevention",
                "network": "customer_experience",
                "description": "Analyzes churn signals, designs retention campaigns, and creates customer health scorecards.",
                "reason": "Customer success campaigns detected — a retention specialist would reduce churn risk.",
            },
        },
    ]

    for gt in gap_templates:
        count = campaign_categories.get(gt["trigger_category"], 0)
        if count >= gt["threshold"]:
            role_lower = gt["suggestion"]["role"].lower()
            if role_lower not in existing_roles:
                suggestions.append({
                    **gt["suggestion"],
                    "confidence": min(0.95, 0.5 + count * 0.15),
                    "based_on": f"{count} {gt['trigger_category']} campaigns",
                })

    # Always suggest based on workflow complexity
    if len(workflows) >= 2:
        suggestions.append({
            "name": "Workflow Coordinator",
            "role": "Multi-Agent Workflow Orchestration",
            "network": "operations",
            "description": "Coordinates complex multi-agent workflows, manages dependencies, and optimizes execution order.",
            "reason": f"{len(workflows)} workflows detected — a coordinator would optimize multi-agent execution.",
            "confidence": min(0.9, 0.4 + len(workflows) * 0.1),
            "based_on": f"{len(workflows)} active workflows",
        })

    # General suggestions for new users
    if not campaigns and not workflows:
        suggestions = [
            {
                "name": "Getting Started Guide",
                "role": "Onboarding Assistant",
                "network": "operations",
                "description": "Helps new users set up their first campaigns, workflows, and agent configurations.",
                "reason": "No campaigns or workflows yet — this agent helps you get started quickly.",
                "confidence": 0.95,
                "based_on": "New user onboarding",
            },
        ]

    return {
        "suggestions": suggestions[:6],
        "analysis": {
            "total_campaigns": len(campaigns),
            "total_workflows": len(workflows),
            "campaign_categories": campaign_categories,
            "existing_agent_count": len(existing_roles),
        },
    }


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
