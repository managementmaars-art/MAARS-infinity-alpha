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
    """Simulate step-by-step execution of a workflow. Returns the final state."""
    import asyncio
    run = await get_workflow_run(user_id, run_id)
    if not run:
        return None

    wf = await get_workflow(user_id, run["workflow_id"])
    if not wf:
        return None

    nodes = wf.get("nodes", [])
    edges = wf.get("edges", [])

    # Build dependency graph
    deps = {n["id"]: [] for n in nodes}
    for e in edges:
        if e["target"] in deps:
            deps[e["target"]].append(e["source"])

    # Topological execution
    executed = set()
    for _ in range(len(nodes)):
        for node in nodes:
            nid = node["id"]
            if nid in executed:
                continue
            # Check if all dependencies are met
            if all(d in executed for d in deps.get(nid, [])):
                # Mark running
                await advance_workflow_step(user_id, run_id, nid, "running")
                # Simulate execution
                await asyncio.sleep(0.1)
                # Mark completed
                output = f"Executed task by {node.get('name', 'Agent')}: {node.get('role', 'processed')}"
                await advance_workflow_step(user_id, run_id, nid, "completed", output)
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
