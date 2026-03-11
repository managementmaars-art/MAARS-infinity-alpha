"""MAARS — Orchestrator: Commander Orion.
Full goal-to-execution pipeline: classify → decompose → assign → execute → verify → report."""

from datetime import datetime, timezone
from db import db
from kernel.task_graph import create_goal, create_task_graph, get_task_graph, get_ready_nodes, update_node_status, check_graph_completion
from kernel.scheduler import find_best_agent, assign_agent_to_task, update_agent_performance
from router.engine import route_task, classify_task
from verification.engine import verify_output, crosscheck
from kernel.budget_controller import record_spend
from governance.audit import log_action
from memory_system.episodic import record_episode


COMMANDER_LOG = "commander_log"


def _now():
    return datetime.now(timezone.utc).isoformat()


def classify_goal(description: str):
    """Classify a goal into type, risk, complexity, freshness requirement."""
    desc = description.lower()
    goal_type = "general"
    risk = "medium"
    complexity = "medium"
    freshness = "standard"

    if any(w in desc for w in ["research", "analyze", "investigate", "market"]):
        goal_type = "research"
        freshness = "fresh"
    elif any(w in desc for w in ["build", "implement", "create", "develop", "code"]):
        goal_type = "engineering"
        complexity = "high"
    elif any(w in desc for w in ["legal", "compliance", "contract", "regulation"]):
        goal_type = "legal"
        risk = "high"
    elif any(w in desc for w in ["financial", "revenue", "forecast", "budget"]):
        goal_type = "financial"
        risk = "high"
    elif any(w in desc for w in ["campaign", "marketing", "launch", "brand"]):
        goal_type = "marketing"
    elif any(w in desc for w in ["crisis", "emergency", "incident", "breach"]):
        goal_type = "crisis"
        risk = "critical"
        freshness = "real_time"

    return {"goal_type": goal_type, "risk_level": risk, "complexity": complexity, "freshness": freshness}


def decompose_goal(description: str, classification: dict):
    """Decompose a goal into a task graph with nodes and dependencies."""
    goal_type = classification.get("goal_type", "general")

    # Template task graphs per goal type
    templates = {
        "research": [
            {"task_description": "Define research scope and questions", "capabilities": ["research", "planning"]},
            {"task_description": "Gather data from primary sources", "capabilities": ["web_search", "data_collection"], "deps": [0]},
            {"task_description": "Gather data from secondary sources", "capabilities": ["web_search", "analysis"], "deps": [0]},
            {"task_description": "Analyze and synthesize findings", "capabilities": ["analysis", "synthesis"], "deps": [1, 2]},
            {"task_description": "Verify facts and sources", "capabilities": ["verification"], "deps": [3]},
            {"task_description": "Write final report with recommendations", "capabilities": ["writing", "strategy"], "deps": [4]},
        ],
        "engineering": [
            {"task_description": "Define technical requirements and architecture", "capabilities": ["architecture", "planning"]},
            {"task_description": "Implement core functionality", "capabilities": ["coding", "engineering"], "deps": [0]},
            {"task_description": "Write tests and validate", "capabilities": ["testing", "quality"], "deps": [1]},
            {"task_description": "Code review and verification", "capabilities": ["code_review", "verification"], "deps": [2]},
            {"task_description": "Deploy and document", "capabilities": ["devops", "documentation"], "deps": [3]},
        ],
        "marketing": [
            {"task_description": "Research target audience and competitors", "capabilities": ["research", "market_analysis"]},
            {"task_description": "Develop campaign strategy", "capabilities": ["strategy", "marketing"], "deps": [0]},
            {"task_description": "Create campaign content and assets", "capabilities": ["creative", "content"], "deps": [1]},
            {"task_description": "Verify compliance and brand alignment", "capabilities": ["compliance", "brand"], "deps": [2]},
            {"task_description": "Launch plan and distribution", "capabilities": ["distribution", "growth"], "deps": [3]},
        ],
        "financial": [
            {"task_description": "Gather financial data and inputs", "capabilities": ["finance", "data_collection"]},
            {"task_description": "Build financial model", "capabilities": ["financial_modeling", "analysis"], "deps": [0]},
            {"task_description": "Run scenarios and sensitivity analysis", "capabilities": ["forecasting", "simulation"], "deps": [1]},
            {"task_description": "Verify quantitative accuracy", "capabilities": ["quantitative_verification"], "deps": [2]},
            {"task_description": "Produce financial summary and recommendations", "capabilities": ["writing", "finance"], "deps": [3]},
        ],
        "legal": [
            {"task_description": "Review relevant documents and context", "capabilities": ["legal", "research"]},
            {"task_description": "Analyze legal implications", "capabilities": ["legal_analysis", "compliance"], "deps": [0]},
            {"task_description": "Verify compliance status", "capabilities": ["compliance_verification"], "deps": [1]},
            {"task_description": "Produce legal assessment and recommendations", "capabilities": ["legal", "writing"], "deps": [2]},
        ],
        "crisis": [
            {"task_description": "Assess situation and gather facts", "capabilities": ["research", "monitoring"]},
            {"task_description": "Identify impact and affected parties", "capabilities": ["analysis", "risk"], "deps": [0]},
            {"task_description": "Develop response plan", "capabilities": ["strategy", "crisis_management"], "deps": [1]},
            {"task_description": "Execute communications", "capabilities": ["communication", "pr"], "deps": [2]},
        ],
    }

    tasks = templates.get(goal_type, [
        {"task_description": "Analyze the goal and gather context", "capabilities": ["analysis"]},
        {"task_description": "Execute primary work", "capabilities": ["general"], "deps": [0]},
        {"task_description": "Verify and review output", "capabilities": ["verification"], "deps": [1]},
        {"task_description": "Produce final deliverable", "capabilities": ["writing"], "deps": [2]},
    ])

    nodes = []
    for i, t in enumerate(tasks):
        node = {
            "node_id": f"node_{i}",
            "task_description": f"{t['task_description']} — for: {description[:80]}",
            "required_capabilities": t.get("capabilities", []),
            "dependencies": [f"node_{d}" for d in t.get("deps", [])],
        }
        nodes.append(node)

    return nodes


async def execute_goal(description: str, requester_id: str = "system", environment: str = "simulation"):
    """Full Commander Orion pipeline: classify → decompose → create graph → assign agents."""
    # Step 1: Classify
    classification = classify_goal(description)
    await log_action("goal_classified", "orchestrator", "commander_orion", details={"classification": classification})

    # Step 2: Create goal
    goal = await create_goal(description, classification, requester_id)

    # Step 3: Decompose into task graph
    nodes = decompose_goal(description, classification)

    # Step 4: Route each node to optimal model
    for node in nodes:
        routing = await route_task(node["task_description"])
        node["model_class"] = routing["classification"]["task_type"]
        node["routed_model"] = routing["selection"]["model"]
        node["routed_provider"] = routing["selection"]["provider"]

    # Step 5: Create task graph
    graph = await create_task_graph(
        goal["goal_id"], description, nodes,
        environment=environment,
        budget_allocated=len(nodes) * 2.0,
        priority=classification.get("priority", "normal"),
    )

    # Step 6: Assign agents to ready nodes
    ready = await get_ready_nodes(graph["graph_id"])
    assignments = []
    for node in ready:
        caps = node.get("required_capabilities", [])
        agent = await find_best_agent(required_capabilities=caps)
        if agent:
            await assign_agent_to_task(agent["agent_id"], node["node_id"], graph["graph_id"])
            await update_node_status(graph["graph_id"], node["node_id"], {
                "status": "assigned",
                "assigned_agent_id": agent["agent_id"],
                "started_at": _now(),
            })
            assignments.append({"node_id": node["node_id"], "agent": agent["name"], "model": node.get("routed_model")})

    # Log commander execution
    log_entry = {
        "goal_id": goal["goal_id"],
        "graph_id": graph["graph_id"],
        "classification": classification,
        "node_count": len(nodes),
        "assignments": assignments,
        "environment": environment,
        "timestamp": _now(),
    }
    await db[COMMANDER_LOG].insert_one(log_entry)

    await record_episode(
        "commander_orion", "goal_execution",
        {"goal": description, "classification": classification, "nodes": len(nodes)},
        outcome="graph_created",
    )

    return {
        "goal": goal,
        "classification": classification,
        "graph_id": graph["graph_id"],
        "nodes": len(nodes),
        "assignments": assignments,
        "environment": environment,
        "reasoning": f"Goal classified as {classification['goal_type']} (risk={classification['risk_level']}). "
                     f"Decomposed into {len(nodes)} tasks. {len(assignments)} agents assigned to ready nodes.",
    }


async def get_commander_log(limit: int = 20):
    """Get recent commander orchestration logs."""
    cursor = db[COMMANDER_LOG].find({}, {"_id": 0}).sort("timestamp", -1).limit(limit)
    return await cursor.to_list(length=limit)
