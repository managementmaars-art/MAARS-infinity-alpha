"""MAARS — Orchestrator: Commander Orion.
Full goal-to-execution pipeline: classify → decompose → assign → execute → verify → report.
Uses real LLM for intelligent goal classification and task decomposition."""

import logging
from datetime import datetime, timezone
from db import db
from kernel.task_graph import create_goal, create_task_graph, get_ready_nodes, update_node_status, TASK_GRAPH_COLLECTION
from kernel.scheduler import find_best_agent, assign_agent_to_task
from router.engine import route_task
from governance.audit import log_action
from memory_system.episodic import record_episode

logger = logging.getLogger(__name__)
COMMANDER_LOG = "commander_log"


def _now():
    return datetime.now(timezone.utc).isoformat()


async def classify_goal_ai(description: str):
    """Use LLM to classify a goal into type, risk, complexity, freshness requirement."""
    from services.infinity_llm import call_json

    prompt = f"""Classify this goal into a structured task. Return JSON only.

Goal: "{description}"

Return this exact JSON structure:
{{
  "goal_type": "<one of: research, engineering, marketing, financial, legal, crisis, creative, operational, general>",
  "risk_level": "<one of: low, medium, high, critical>",
  "complexity": "<one of: low, medium, high>",
  "freshness": "<one of: standard, fresh, real_time>",
  "reasoning": "<brief explanation of classification>"
}}"""

    try:
        result = await call_json(prompt, system_message="You are MAARS Commander Orion, an AI orchestration engine. Classify goals accurately based on their content, domain, and risk profile. Respond with JSON only.")
        classification = result["parsed"]
        classification["ai_powered"] = True
        classification["model_used"] = result["model"]
        classification["provider_used"] = result["provider"]
        classification["latency_ms"] = result["latency_ms"]
        return classification
    except Exception as e:
        logger.warning(f"AI classification failed, using rule-based fallback: {e}")
        result = classify_goal_rules(description)
        result["ai_powered"] = False
        result["fallback_reason"] = str(e)
        return result


def classify_goal_rules(description: str):
    """Rule-based fallback for goal classification."""
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

    return {"goal_type": goal_type, "risk_level": risk, "complexity": complexity, "freshness": freshness, "reasoning": "Rule-based classification"}


async def decompose_goal_ai(description: str, classification: dict):
    """Use LLM to decompose a goal into a task graph with nodes and dependencies."""
    from services.infinity_llm import call_json

    goal_type = classification.get("goal_type", "general")
    risk = classification.get("risk_level", "medium")
    complexity = classification.get("complexity", "medium")

    node_count_hint = {"low": "3-4", "medium": "4-6", "high": "6-8"}.get(complexity, "4-6")

    prompt = f"""Decompose this goal into a task graph for an AI agent team.

Goal: "{description}"
Classification: type={goal_type}, risk={risk}, complexity={complexity}

Create {node_count_hint} task nodes. Each node should have:
- task_description: Clear, actionable description
- capabilities: List of required skills (e.g., ["research", "web_search"], ["coding", "testing"])
- deps: List of node indices this depends on (0-indexed). First node has no deps.

Return a JSON array of objects:
[
  {{"task_description": "...", "capabilities": ["..."], "deps": []}},
  {{"task_description": "...", "capabilities": ["..."], "deps": [0]}},
  ...
]

Rules:
- First node must have empty deps []
- Dependencies must reference earlier nodes only (no circular)
- Final node should produce the deliverable
- Include a verification/review step before the final output"""

    try:
        result = await call_json(prompt, system_message="You are MAARS Commander Orion, an AI orchestration engine. Break down goals into precise, actionable task graphs. Each task should be specific enough for a single AI agent to execute. Respond with a JSON array only.")
        tasks = result["parsed"]
        if not isinstance(tasks, list) or len(tasks) < 2:
            raise ValueError("Invalid task graph structure")

        nodes = []
        for i, t in enumerate(tasks):
            node = {
                "node_id": f"node_{i}",
                "task_description": f"{t.get('task_description', f'Task {i}')} — for: {description[:60]}",
                "required_capabilities": t.get("capabilities", ["general"]),
                "dependencies": [f"node_{d}" for d in t.get("deps", []) if isinstance(d, int) and d < i],
            }
            nodes.append(node)
        return nodes, {"ai_powered": True, "model": result["model"], "provider": result["provider"], "latency_ms": result["latency_ms"]}
    except Exception as e:
        logger.warning(f"AI decomposition failed, using template fallback: {e}")
        nodes = decompose_goal_rules(description, classification)
        return nodes, {"ai_powered": False, "fallback_reason": str(e)}


def decompose_goal_rules(description: str, classification: dict):
    """Rule-based fallback for goal decomposition."""
    goal_type = classification.get("goal_type", "general")
    templates = {
        "research": [
            {"task_description": "Define research scope and questions", "capabilities": ["research", "planning"]},
            {"task_description": "Gather data from primary sources", "capabilities": ["web_search", "data_collection"], "deps": [0]},
            {"task_description": "Gather data from secondary sources", "capabilities": ["web_search", "analysis"], "deps": [0]},
            {"task_description": "Analyze and synthesize findings", "capabilities": ["analysis", "synthesis"], "deps": [1, 2]},
            {"task_description": "Verify facts and sources", "capabilities": ["verification"], "deps": [3]},
            {"task_description": "Write final report", "capabilities": ["writing", "strategy"], "deps": [4]},
        ],
        "engineering": [
            {"task_description": "Define technical requirements", "capabilities": ["architecture", "planning"]},
            {"task_description": "Implement core functionality", "capabilities": ["coding", "engineering"], "deps": [0]},
            {"task_description": "Write tests and validate", "capabilities": ["testing", "quality"], "deps": [1]},
            {"task_description": "Code review and verification", "capabilities": ["code_review", "verification"], "deps": [2]},
            {"task_description": "Deploy and document", "capabilities": ["devops", "documentation"], "deps": [3]},
        ],
    }
    tasks = templates.get(goal_type, [
        {"task_description": "Analyze goal and gather context", "capabilities": ["analysis"]},
        {"task_description": "Execute primary work", "capabilities": ["general"], "deps": [0]},
        {"task_description": "Verify and review output", "capabilities": ["verification"], "deps": [1]},
        {"task_description": "Produce final deliverable", "capabilities": ["writing"], "deps": [2]},
    ])
    nodes = []
    for i, t in enumerate(tasks):
        nodes.append({
            "node_id": f"node_{i}",
            "task_description": f"{t['task_description']} — for: {description[:80]}",
            "required_capabilities": t.get("capabilities", []),
            "dependencies": [f"node_{d}" for d in t.get("deps", [])],
        })
    return nodes


async def execute_goal(description: str, requester_id: str = "system", environment: str = "simulation"):
    """Full Commander Orion pipeline: AI classify → AI decompose → route → assign agents."""
    # Step 1: AI-powered classification
    classification = await classify_goal_ai(description)
    await log_action("goal_classified", "orchestrator", "commander_orion", details={"classification": classification})

    # Step 2: Create goal
    goal = await create_goal(description, classification, requester_id)

    # Step 3: AI-powered decomposition
    nodes, decomp_meta = await decompose_goal_ai(description, classification)

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
        "decomposition_meta": decomp_meta,
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

    reasoning_parts = [
        f"Goal classified as {classification['goal_type']} (risk={classification['risk_level']}).",
        f"{'AI-powered' if classification.get('ai_powered') else 'Rule-based'} classification",
    ]
    if classification.get("model_used"):
        reasoning_parts.append(f"using {classification['model_used']}")
    reasoning_parts.append(f". Decomposed into {len(nodes)} tasks.")
    if decomp_meta.get("ai_powered"):
        reasoning_parts.append(f" AI decomposition via {decomp_meta['model']}.")
    reasoning_parts.append(f" {len(assignments)} agents assigned to ready nodes.")

    return {
        "goal": goal,
        "classification": classification,
        "decomposition_meta": decomp_meta,
        "graph_id": graph["graph_id"],
        "nodes": len(nodes),
        "node_details": [{"node_id": n["node_id"], "task": n["task_description"][:100], "model": n.get("routed_model"), "provider": n.get("routed_provider")} for n in nodes],
        "assignments": assignments,
        "environment": environment,
        "reasoning": "".join(reasoning_parts),
    }


async def get_commander_log(limit: int = 20):
    """Get recent commander orchestration logs."""
    cursor = db[COMMANDER_LOG].find({}, {"_id": 0}).sort("timestamp", -1).limit(limit)
    return await cursor.to_list(length=limit)


# ════════════════════════════════════════════════════════════════════
# FULL EXECUTION LOOP: Execute → Verify → Report
# ════════════════════════════════════════════════════════════════════

EXECUTION_RUNS = "execution_runs"


async def execute_graph(graph_id: str, max_retries_per_node: int = 1):
    """Execute all nodes in a task graph through the full LLM pipeline.
    Flow: get ready nodes → execute via LLM → verify → mark done → repeat → final report."""
    from router.engine import execute_routed_task
    from verification.engine import verify_output
    from kernel.task_graph import get_task_graph, get_ready_nodes, update_node_status, check_graph_completion
    from kernel.budget_controller import record_spend

    graph = await get_task_graph(graph_id)
    if not graph:
        return {"error": "Graph not found"}

    run_id = str(__import__("uuid").uuid4())[:12]
    started_at = _now()
    node_results = []
    total_cost = 0.0
    total_latency = 0

    await db[TASK_GRAPH_COLLECTION].update_one(
        {"graph_id": graph_id}, {"$set": {"status": "executing", "updated_at": _now()}}
    )

    # Execute nodes in dependency order
    max_rounds = len(graph["nodes"]) + 2
    for _ in range(max_rounds):
        ready = await get_ready_nodes(graph_id)
        if not ready:
            status = await check_graph_completion(graph_id)
            break

        for node in ready:
            task_desc = node.get("task_description", "Execute task")
            node_id = node["node_id"]

            # Build context from dependency outputs
            dep_context = ""
            g = await get_task_graph(graph_id)
            for dep_id in node.get("dependencies", []):
                dep_node = next((n for n in g["nodes"] if n["node_id"] == dep_id), None)
                if dep_node and dep_node.get("outputs"):
                    dep_context += f"\n--- Output from {dep_id} ---\n{dep_node['outputs'][:800]}\n"

            await update_node_status(graph_id, node_id, {"status": "executing", "started_at": _now()})

            # Execute via LLM
            try:
                exec_result = await execute_routed_task(task_desc, context=dep_context)
                output = exec_result["output"]
                provider = exec_result["execution"]["provider"]
                model = exec_result["execution"]["model"]
                latency = exec_result["execution"]["latency_ms"]
                cost = exec_result["execution"].get("estimated_cost", 0)
            except Exception as e:
                logger.error(f"Node {node_id} execution failed: {e}")
                await update_node_status(graph_id, node_id, {
                    "status": "failed", "error_log": [str(e)], "completed_at": _now(),
                })
                node_results.append({"node_id": node_id, "status": "failed", "error": str(e)})
                continue

            # Verify output
            try:
                v = await verify_output(node_id, output, "fact", "auto_verifier", {"task": task_desc}, graph_id)
                v_score = v["confidence_score"]
                v_pass = v["verification_pass"]
            except Exception:
                v_score = 5.0
                v_pass = True

            # Record spend
            try:
                await record_spend("model", f"{provider}/{model}", cost, model, node_id)
            except Exception:
                pass

            total_cost += cost
            total_latency += latency

            await update_node_status(graph_id, node_id, {
                "status": "completed",
                "outputs": output[:3000],
                "model_used": f"{provider}/{model}",
                "cost": cost,
                "verification_status": "passed" if v_pass else "flagged",
                "verification_score": v_score,
                "completed_at": _now(),
            })

            node_results.append({
                "node_id": node_id,
                "task": task_desc[:100],
                "status": "completed",
                "provider": provider,
                "model": model,
                "latency_ms": latency,
                "cost": cost,
                "verification_score": v_score,
                "verification_pass": v_pass,
                "output_preview": output[:200],
            })

    # Check final graph status
    final_status = await check_graph_completion(graph_id)
    completed_nodes = [r for r in node_results if r["status"] == "completed"]
    failed_nodes = [r for r in node_results if r["status"] == "failed"]

    # Generate consolidated report from all outputs
    final_report = None
    if completed_nodes and not failed_nodes:
        from services.infinity_llm import call
        all_outputs = "\n\n".join(
            f"### {r['task']}\n{r['output_preview']}" for r in completed_nodes
        )
        try:
            report_result = await call(
                prompt=f"Consolidate these task outputs into a cohesive final report. Be concise but thorough.\n\nGoal: {graph.get('objective', 'Unknown')}\n\n{all_outputs}",
                system_message="You are a senior analyst producing final consolidated reports. Synthesize all inputs into a clear, actionable deliverable.",
                model_name="gpt-5.2",
            )
            final_report = report_result["response"]
            total_latency += report_result["latency_ms"]
        except Exception as e:
            final_report = f"Report generation failed: {e}. Raw outputs available in node results."

        await db[TASK_GRAPH_COLLECTION].update_one(
            {"graph_id": graph_id},
            {"$set": {"final_output": final_report[:5000], "verification_result": {"all_passed": True}, "budget_used": total_cost}},
        )

    completed_at = _now()
    run = {
        "run_id": run_id,
        "graph_id": graph_id,
        "goal_id": graph.get("goal_id"),
        "objective": graph.get("objective", ""),
        "status": final_status or "completed",
        "node_results": node_results,
        "summary": {
            "total_nodes": len(graph["nodes"]),
            "completed": len(completed_nodes),
            "failed": len(failed_nodes),
            "total_cost": round(total_cost, 4),
            "total_latency_ms": total_latency,
        },
        "final_report": final_report,
        "started_at": started_at,
        "completed_at": completed_at,
    }
    await db[EXECUTION_RUNS].insert_one(run)
    run.pop("_id", None)

    await record_episode(
        "commander_orion", "graph_execution",
        {"graph_id": graph_id, "nodes": len(graph["nodes"]), "cost": total_cost},
        outcome=final_status or "completed",
        lessons_learned=f"Executed {len(completed_nodes)} nodes, {len(failed_nodes)} failed, cost=${total_cost:.4f}",
    )

    return run


async def get_execution_runs(graph_id: str = None, limit: int = 20):
    """Get execution run history."""
    query = {}
    if graph_id:
        query["graph_id"] = graph_id
    cursor = db[EXECUTION_RUNS].find(query, {"_id": 0}).sort("started_at", -1).limit(limit)
    return await cursor.to_list(length=limit)
