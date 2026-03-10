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
