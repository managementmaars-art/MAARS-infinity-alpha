"""MAARS Kernel — Task Graph Runtime.
Manages DAG-based task execution with dependency resolution,
parallel/sequential execution, checkpoints, and approval gates."""

import uuid
from datetime import datetime, timezone
from db import db
from governance.audit import log_action

TASK_GRAPH_COLLECTION = "task_graphs"
GOAL_COLLECTION = "goals"


def _now():
    return datetime.now(timezone.utc).isoformat()


def _uid():
    return str(uuid.uuid4())[:12]


async def create_goal(description: str, classification: dict = None, requester_id: str = "system"):
    """Create a new goal that will be decomposed into a task graph."""
    goal = {
        "goal_id": _uid(),
        "description": description,
        "classification": classification or {},
        "risk_level": classification.get("risk_level", "medium") if classification else "medium",
        "freshness_requirement": classification.get("freshness", "standard") if classification else "standard",
        "complexity": classification.get("complexity", "medium") if classification else "medium",
        "priority": classification.get("priority", "normal") if classification else "normal",
        "requester_id": requester_id,
        "status": "pending",
        "task_graph_id": None,
        "created_at": _now(),
        "completed_at": None,
        "outcome_metrics": {},
    }
    await db[GOAL_COLLECTION].insert_one(goal)
    await log_action("goal_created", "user", requester_id, "goal", goal["goal_id"], {"description": description})
    goal.pop("_id", None)
    return goal


async def create_task_graph(
    goal_id: str,
    objective: str,
    nodes: list,
    edges: list = None,
    collaboration_mode: str = "sequential",
    budget_allocated: float = 10.0,
    priority: str = "normal",
    deadline: str = None,
    approval_checkpoints: list = None,
    environment: str = "simulation",
):
    """Create a task graph (DAG) for a goal.
    nodes: [{node_id, task_description, assigned_agent_id, model_class, dependencies, ...}]
    edges: [{from, to, type}]"""
    graph_id = _uid()

    # Normalize nodes
    for node in nodes:
        node.setdefault("node_id", _uid())
        node.setdefault("status", "pending")
        node.setdefault("assigned_agent_id", None)
        node.setdefault("backup_agent_id", None)
        node.setdefault("model_class", "auto")
        node.setdefault("model_used", None)
        node.setdefault("tool_requirements", [])
        node.setdefault("dependencies", [])
        node.setdefault("outputs", None)
        node.setdefault("verification_status", None)
        node.setdefault("verification_score", None)
        node.setdefault("started_at", None)
        node.setdefault("completed_at", None)
        node.setdefault("retry_count", 0)
        node.setdefault("cost", 0.0)
        node.setdefault("error_log", [])
        node.setdefault("rollback_plan", None)

    graph = {
        "graph_id": graph_id,
        "goal_id": goal_id,
        "objective": objective,
        "status": "pending",
        "environment": environment,
        "priority": priority,
        "deadline": deadline,
        "collaboration_mode": collaboration_mode,
        "budget_allocated": budget_allocated,
        "budget_used": 0.0,
        "nodes": nodes,
        "edges": edges or [],
        "approval_checkpoints": approval_checkpoints or [],
        "final_output": None,
        "verification_result": None,
        "created_at": _now(),
        "updated_at": _now(),
    }
    await db[TASK_GRAPH_COLLECTION].insert_one(graph)

    # Link goal to graph
    await db[GOAL_COLLECTION].update_one(
        {"goal_id": goal_id}, {"$set": {"task_graph_id": graph_id, "status": "in_progress"}}
    )
    await log_action("task_graph_created", "system", "task_graph_runtime", "task_graph", graph_id, {"goal_id": goal_id, "node_count": len(nodes)})
    graph.pop("_id", None)
    return graph


async def get_task_graph(graph_id: str):
    """Fetch a task graph by ID."""
    doc = await db[TASK_GRAPH_COLLECTION].find_one({"graph_id": graph_id}, {"_id": 0})
    return doc


async def get_ready_nodes(graph_id: str):
    """Find nodes whose dependencies are all completed — ready to execute."""
    graph = await get_task_graph(graph_id)
    if not graph:
        return []

    completed_ids = {n["node_id"] for n in graph["nodes"] if n["status"] == "completed"}
    ready = []
    for node in graph["nodes"]:
        if node["status"] != "pending":
            continue
        deps_met = all(d in completed_ids for d in node["dependencies"])
        if deps_met:
            ready.append(node)
    return ready


async def update_node_status(graph_id: str, node_id: str, updates: dict):
    """Update a specific node within a task graph."""
    set_fields = {f"nodes.$.{k}": v for k, v in updates.items()}
    set_fields["updated_at"] = _now()
    await db[TASK_GRAPH_COLLECTION].update_one(
        {"graph_id": graph_id, "nodes.node_id": node_id},
        {"$set": set_fields},
    )
    if updates.get("status") == "completed":
        await log_action("task_node_completed", "system", "task_graph_runtime", "node", node_id, {"graph_id": graph_id})
    return await get_task_graph(graph_id)


async def check_graph_completion(graph_id: str):
    """Check if all nodes in a graph are completed or failed."""
    graph = await get_task_graph(graph_id)
    if not graph:
        return None

    statuses = [n["status"] for n in graph["nodes"]]
    if all(s == "completed" for s in statuses):
        await db[TASK_GRAPH_COLLECTION].update_one(
            {"graph_id": graph_id}, {"$set": {"status": "completed", "updated_at": _now()}}
        )
        await db[GOAL_COLLECTION].update_one(
            {"goal_id": graph["goal_id"]}, {"$set": {"status": "completed", "completed_at": _now()}}
        )
        return "completed"
    elif any(s == "failed" for s in statuses):
        failed_nodes = [n["node_id"] for n in graph["nodes"] if n["status"] == "failed"]
        can_proceed = True
        for node in graph["nodes"]:
            if node["status"] == "pending":
                if any(d in failed_nodes for d in node["dependencies"]):
                    can_proceed = False
        if not can_proceed:
            await db[TASK_GRAPH_COLLECTION].update_one(
                {"graph_id": graph_id}, {"$set": {"status": "blocked", "updated_at": _now()}}
            )
            return "blocked"
    return "in_progress"


async def list_task_graphs(status: str = None, limit: int = 50):
    """List task graphs with optional status filter."""
    query = {}
    if status:
        query["status"] = status
    cursor = db[TASK_GRAPH_COLLECTION].find(query, {"_id": 0}).sort("created_at", -1).limit(limit)
    return await cursor.to_list(length=limit)
