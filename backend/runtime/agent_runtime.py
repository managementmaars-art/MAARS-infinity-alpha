"""MAARS Agent Runtime — The shared execution loop for ALL agents.
Every agent executes through this 13-step loop:
1. load role pack → 2. load context → 3. retrieve memory → 4. analyze task →
5. plan → 6. choose action → 7. create ActionRequest → 8. run policy →
9. request approval → 10. execute via gateway → 11. verify result →
12. update memory → 13. continue / escalate / stop"""

import uuid
import time
import logging
from datetime import datetime, timezone
from db import db

logger = logging.getLogger(__name__)

RUNTIME_LOG = "runtime_executions"
ACTION_REQUESTS = "action_requests"


def _now():
    return datetime.now(timezone.utc).isoformat()


def _uid():
    return str(uuid.uuid4())[:12]


# ── Action Classifications ──
ACTION_TYPES = {
    "READ": {"risk": "low", "requires_approval_tier": 99},
    "WRITE": {"risk": "medium", "requires_approval_tier": 3},
    "EXTERNAL": {"risk": "high", "requires_approval_tier": 2},
    "CODE": {"risk": "medium", "requires_approval_tier": 3},
    "DEPLOY": {"risk": "critical", "requires_approval_tier": 1},
    "BILLING": {"risk": "high", "requires_approval_tier": 1},
    "LEGAL": {"risk": "critical", "requires_approval_tier": 0},
    "SENSITIVE": {"risk": "high", "requires_approval_tier": 1},
    "EXPORT": {"risk": "medium", "requires_approval_tier": 2},
    "PROD": {"risk": "critical", "requires_approval_tier": 1},
}


def classify_action(task_description: str, environment: str = "sandbox") -> str:
    """Classify an action type from task description."""
    desc = task_description.lower()
    if any(w in desc for w in ["deploy", "release", "publish", "production"]):
        return "DEPLOY" if environment == "production" else "CODE"
    if any(w in desc for w in ["payment", "billing", "charge", "invoice", "subscription"]):
        return "BILLING"
    if any(w in desc for w in ["legal", "contract", "compliance", "regulation", "lawsuit"]):
        return "LEGAL"
    if any(w in desc for w in ["api call", "external", "webhook", "third-party", "send email"]):
        return "EXTERNAL"
    if any(w in desc for w in ["write", "update", "create", "delete", "modify", "edit"]):
        return "WRITE"
    if any(w in desc for w in ["code", "implement", "build", "develop", "program"]):
        return "CODE"
    if any(w in desc for w in ["export", "download", "extract"]):
        return "EXPORT"
    if any(w in desc for w in ["sensitive", "personal", "private", "confidential"]):
        return "SENSITIVE"
    return "READ"


async def execute_agent_loop(
    agent_id: str,
    task_description: str,
    context: dict = None,
    environment: str = "sandbox",
    graph_id: str = None,
    node_id: str = None,
):
    """The shared 13-step agent runtime loop.
    Every agent in MAARS executes through this same pipeline."""

    execution_id = _uid()
    context = context or {}
    steps = []
    started_at = time.time()

    def _step(name, status, detail=""):
        elapsed = int((time.time() - started_at) * 1000)
        steps.append({"step": name, "status": status, "detail": detail, "elapsed_ms": elapsed})

    try:
        # ── Step 1: Load Role Pack ──
        agent = await db["agents"].find_one({"agent_id": agent_id}, {"_id": 0})
        if not agent:
            _step("load_role_pack", "fail", f"Agent {agent_id} not found")
            return _build_result(execution_id, agent_id, task_description, steps, "failed", environment)

        role_pack = {
            "name": agent["name"],
            "role": agent.get("role", ""),
            "network": agent.get("network", ""),
            "capabilities": agent.get("capabilities", []),
            "autonomy_tier": agent.get("autonomy_tier", 1),
            "tools": agent.get("tools", []),
            "maturity": agent.get("maturity", "production-ready"),
        }
        _step("load_role_pack", "pass", f"{role_pack['name']} (tier {role_pack['autonomy_tier']}, {role_pack['maturity']})")

        # ── Step 2: Load Context ──
        exec_context = {
            "task": task_description,
            "environment": environment,
            "graph_id": graph_id,
            "node_id": node_id,
            "agent_capabilities": role_pack["capabilities"],
            **context,
        }
        _step("load_context", "pass", f"env={environment}, graph={graph_id or 'standalone'}")

        # ── Step 3: Retrieve Memory ──
        from memory_system.working import get_working
        from memory_system.episodic import recall_episodes
        working_mem = await get_working(graph_id or execution_id)
        episodes = await recall_episodes(agent_id, limit=3)
        memory_context = ""
        if working_mem:
            memory_context += f"Working memory: {len(working_mem)} entries. "
        if episodes:
            lessons = [e.get("lessons_learned", "") for e in episodes if e.get("lessons_learned")]
            if lessons:
                memory_context += f"Past lessons: {'; '.join(lessons[:2])}"
        _step("retrieve_memory", "pass", memory_context or "No prior memory")

        # ── Step 4: Analyze Task ──
        action_type = classify_action(task_description, environment)
        action_risk = ACTION_TYPES.get(action_type, {}).get("risk", "low")
        _step("analyze_task", "pass", f"type={action_type}, risk={action_risk}")

        # ── Step 5: Plan ──
        from router.engine import route_task
        routing = await route_task(task_description)
        selected_model = routing["selection"]["model"]
        selected_provider = routing["selection"]["provider"]
        _step("plan", "pass", f"model={selected_provider}/{selected_model}, task_type={routing['classification']['task_type']}")

        # ── Step 6: Choose Action ──
        action_request = {
            "request_id": _uid(),
            "agent_id": agent_id,
            "action_type": action_type,
            "task_description": task_description,
            "model": selected_model,
            "provider": selected_provider,
            "environment": environment,
            "risk": action_risk,
            "created_at": _now(),
        }
        _step("create_action_request", "pass", f"req={action_request['request_id']}, type={action_type}")

        # ── Step 7: Run Policy ──
        from kernel.policy_engine import check_all_policies
        policy_context = {
            "action": action_type.lower(),
            "autonomy_tier": role_pack["autonomy_tier"],
            "environment": environment,
            "daily_spend": 0,
        }
        policy_result = await check_all_policies(policy_context)
        if not policy_result.get("all_passed", True):
            violations = policy_result.get("violations", [])
            _step("policy_check", "fail", f"Violations: {violations}")
            return _build_result(execution_id, agent_id, task_description, steps, "policy_denied", environment)
        _step("policy_check", "pass", "All policies passed")

        # ── Step 8: Request Approval (if needed) ──
        approval_tier = ACTION_TYPES.get(action_type, {}).get("requires_approval_tier", 99)
        needs_approval = role_pack["autonomy_tier"] < approval_tier and action_risk in ("high", "critical")
        if needs_approval and environment == "production":
            from kernel.approval_controller import request_approval
            await request_approval(graph_id or execution_id, action_request["request_id"], action_type, f"Agent {agent_id}: {task_description[:100]}", "medium")
            _step("approval", "pending", f"Approval requested (tier {role_pack['autonomy_tier']} < required {approval_tier})")
            return _build_result(execution_id, agent_id, task_description, steps, "awaiting_approval", environment)
        _step("approval", "pass", "Auto-approved" if not needs_approval else "Sandbox mode — no approval needed")

        # ── Step 9: Execute via Gateway ──
        from router.engine import execute_routed_task
        dep_context = memory_context
        if context.get("dependency_outputs"):
            dep_context += f"\nPrevious outputs:\n{context['dependency_outputs'][:1000]}"

        exec_result = await execute_routed_task(task_description, context=dep_context)
        output = exec_result["output"]
        exec_provider = exec_result["execution"]["provider"]
        exec_model = exec_result["execution"]["model"]
        exec_latency = exec_result["execution"]["latency_ms"]
        exec_cost = exec_result["execution"].get("estimated_cost", 0)
        _step("execute", "pass", f"{exec_provider}/{exec_model} ({exec_latency}ms, ${exec_cost:.4f})")

        # ── Step 10: Verify Result ──
        from verification.engine import verify_output
        v_result = await verify_output(
            node_id or execution_id, output, "fact", "runtime_verifier",
            {"task": task_description, "agent": agent_id}, graph_id,
        )
        v_score = v_result["confidence_score"]
        v_pass = v_result["verification_pass"]
        _step("verify", "pass" if v_pass else "warn", f"confidence={v_score:.1f}, pass={v_pass}")

        # ── Step 11: Update Memory ──
        from memory_system.working import store_working, append_result
        from memory_system.episodic import record_episode
        if graph_id:
            await append_result(graph_id, agent_id, {"output_preview": output[:500], "model": exec_model})
        await record_episode(
            agent_id, "task_execution",
            {"task": task_description[:200], "model": exec_model, "cost": exec_cost},
            outcome="completed" if v_pass else "flagged",
            lessons_learned=f"Used {exec_model} for {routing['classification']['task_type']} task",
        )
        _step("update_memory", "pass", "Working + episodic memory updated")

        # ── Step 12: Log ──
        from governance.audit import log_action
        await log_action("agent_execution", "agent", agent_id, "task", node_id or execution_id, {
            "action_type": action_type, "model": exec_model, "cost": exec_cost,
            "verification_pass": v_pass, "environment": environment,
        })
        _step("audit_log", "pass", "Execution logged to audit trail")

        # ── Step 13: Return Result ──
        _step("complete", "pass", "Execution complete")

        result = _build_result(execution_id, agent_id, task_description, steps, "completed", environment)
        result["output"] = output
        result["execution"] = {
            "provider": exec_provider, "model": exec_model,
            "latency_ms": exec_latency, "cost": exec_cost,
        }
        result["verification"] = {"score": v_score, "pass": v_pass}
        result["routing"] = {"task_type": routing["classification"]["task_type"], "model": selected_model}

        await db[RUNTIME_LOG].insert_one({**result})
        result.pop("_id", None)
        return result

    except Exception as e:
        logger.error(f"Runtime loop failed for {agent_id}: {e}")
        _step("error", "fail", str(e))
        result = _build_result(execution_id, agent_id, task_description, steps, "failed", environment)
        result["error"] = str(e)
        await db[RUNTIME_LOG].insert_one({**result})
        result.pop("_id", None)
        return result


def _build_result(exec_id, agent_id, task, steps, status, env):
    passed = sum(1 for s in steps if s["status"] == "pass")
    failed = sum(1 for s in steps if s["status"] == "fail")
    total_ms = steps[-1]["elapsed_ms"] if steps else 0
    return {
        "execution_id": exec_id,
        "agent_id": agent_id,
        "task": task[:200],
        "status": status,
        "environment": env,
        "steps": steps,
        "summary": {"passed": passed, "failed": failed, "total": len(steps), "latency_ms": total_ms},
        "timestamp": _now(),
    }


async def get_runtime_executions(agent_id: str = None, status: str = None, limit: int = 20):
    """Get runtime execution history."""
    query = {}
    if agent_id:
        query["agent_id"] = agent_id
    if status:
        query["status"] = status
    cursor = db[RUNTIME_LOG].find(query, {"_id": 0}).sort("timestamp", -1).limit(limit)
    return await cursor.to_list(length=limit)
