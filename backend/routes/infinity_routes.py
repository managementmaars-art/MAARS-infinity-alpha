"""MAARS Infinity — Phase 1 API Routes.
Exposes kernel, router, verification, governance endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from kernel.task_graph import (
    create_goal, create_task_graph, get_task_graph,
    get_ready_nodes, update_node_status, check_graph_completion, list_task_graphs,
)
from kernel.budget_controller import (
    get_budget, record_spend, set_budget_limit, get_spend_summary,
)
from kernel.policy_engine import check_all_policies, get_policies, seed_default_policies
from kernel.scheduler import (
    find_best_agent, assign_agent_to_task, release_agent,
    update_agent_performance, get_agent_workload,
)
from router.engine import route_task, get_model_performance, log_model_result, classify_task, PROVIDER_CATALOG
from verification.engine import (
    verify_output, crosscheck, get_verification_results,
    get_verification_stats,
)
from governance.audit import query_audit_log
from governance.circuit_breaker import (
    get_all_breakers, update_breaker_value, reset_breaker,
    get_tripped_breakers, seed_default_breakers,
)
from governance.trust_scoring import (
    get_trust_score, update_trust_score, get_trust_leaderboard,
    get_low_trust_entities,
)

router = APIRouter(prefix="/infinity", tags=["MAARS Infinity"])


# ─── Pydantic Models ───

class GoalRequest(BaseModel):
    description: str
    classification: Optional[dict] = None
    requester_id: Optional[str] = "system"

class TaskGraphRequest(BaseModel):
    goal_id: str
    objective: str
    nodes: list
    edges: Optional[list] = None
    collaboration_mode: Optional[str] = "sequential"
    budget_allocated: Optional[float] = 10.0
    priority: Optional[str] = "normal"
    environment: Optional[str] = "simulation"

class NodeUpdateRequest(BaseModel):
    updates: dict

class SpendRequest(BaseModel):
    entity_type: str
    entity_id: str
    amount: float
    model: Optional[str] = ""
    task_id: Optional[str] = ""

class BudgetLimitRequest(BaseModel):
    entity_type: str
    entity_id: str
    period: str
    limit: float

class RouteRequest(BaseModel):
    task_description: str
    metadata: Optional[dict] = None

class VerifyRequest(BaseModel):
    task_id: str
    output: str
    verification_type: Optional[str] = "fact"
    verifier_agent_id: Optional[str] = "system_verifier"
    context: Optional[dict] = None

class CrosscheckRequest(BaseModel):
    task_id: str
    output: str
    verifier_ids: Optional[list] = None
    context: Optional[dict] = None

class TrustUpdateRequest(BaseModel):
    entity_type: str
    entity_id: str
    event: dict


# ─── KERNEL: Goals & Task Graphs ───

@router.post("/kernel/goals")
async def api_create_goal(req: GoalRequest):
    return await create_goal(req.description, req.classification, req.requester_id)

@router.get("/kernel/goals")
async def api_list_goals():
    from db import db
    cursor = db["goals"].find({}, {"_id": 0}).sort("created_at", -1).limit(50)
    return await cursor.to_list(length=50)

@router.post("/kernel/task-graphs")
async def api_create_task_graph(req: TaskGraphRequest):
    return await create_task_graph(
        req.goal_id, req.objective, req.nodes, req.edges,
        req.collaboration_mode, req.budget_allocated, req.priority,
        environment=req.environment,
    )

@router.get("/kernel/task-graphs")
async def api_list_task_graphs(status: Optional[str] = None):
    return await list_task_graphs(status)

@router.get("/kernel/task-graphs/{graph_id}")
async def api_get_task_graph(graph_id: str):
    graph = await get_task_graph(graph_id)
    if not graph:
        raise HTTPException(404, "Task graph not found")
    return graph

@router.get("/kernel/task-graphs/{graph_id}/ready-nodes")
async def api_get_ready_nodes(graph_id: str):
    return await get_ready_nodes(graph_id)

@router.patch("/kernel/task-graphs/{graph_id}/nodes/{node_id}")
async def api_update_node(graph_id: str, node_id: str, req: NodeUpdateRequest):
    return await update_node_status(graph_id, node_id, req.updates)

@router.post("/kernel/task-graphs/{graph_id}/check-completion")
async def api_check_completion(graph_id: str):
    result = await check_graph_completion(graph_id)
    return {"graph_id": graph_id, "status": result}


# ─── KERNEL: Scheduler ───

@router.get("/kernel/scheduler/workload")
async def api_workload():
    return await get_agent_workload()

@router.post("/kernel/scheduler/find-agent")
async def api_find_agent(capabilities: Optional[list] = None, network: Optional[str] = None, min_trust: Optional[float] = 0):
    agent = await find_best_agent(capabilities, network, min_trust)
    if not agent:
        raise HTTPException(404, "No matching agent found")
    return agent


# ─── KERNEL: Budget ───

@router.get("/kernel/budget/{entity_type}/{entity_id}")
async def api_get_budget(entity_type: str, entity_id: str, period: str = "daily"):
    return await get_budget(entity_type, entity_id, period)

@router.post("/kernel/budget/spend")
async def api_record_spend(req: SpendRequest):
    return await record_spend(req.entity_type, req.entity_id, req.amount, req.model, req.task_id)

@router.post("/kernel/budget/set-limit")
async def api_set_budget_limit(req: BudgetLimitRequest):
    return await set_budget_limit(req.entity_type, req.entity_id, req.period, req.limit)

@router.get("/kernel/budget/summary")
async def api_spend_summary(entity_type: Optional[str] = None, period: str = "daily"):
    return await get_spend_summary(entity_type, period)


# ─── KERNEL: Policies ───

@router.get("/kernel/policies")
async def api_get_policies(category: Optional[str] = None):
    return await get_policies(category)

@router.post("/kernel/policies/check")
async def api_check_policies(context: dict):
    return await check_all_policies(context)


# ─── MODEL ROUTER ───

@router.post("/router/route")
async def api_route_task(req: RouteRequest):
    return await route_task(req.task_description, req.metadata)

@router.post("/router/classify")
async def api_classify_task(req: RouteRequest):
    return classify_task(req.task_description, req.metadata)

@router.get("/router/performance")
async def api_model_performance(provider: Optional[str] = None):
    return await get_model_performance(provider)

@router.get("/router/providers")
async def api_get_providers():
    return PROVIDER_CATALOG


# ─── VERIFICATION ───

@router.post("/verify/check")
async def api_verify(req: VerifyRequest):
    return await verify_output(req.task_id, req.output, req.verification_type, req.verifier_agent_id, req.context)

@router.post("/verify/crosscheck")
async def api_crosscheck(req: CrosscheckRequest):
    return await crosscheck(req.task_id, req.verifier_ids, req.output, req.context)

@router.get("/verify/results")
async def api_verification_results(task_id: Optional[str] = None, limit: int = 50):
    return await get_verification_results(task_id, limit=limit)

@router.get("/verify/stats")
async def api_verification_stats():
    return await get_verification_stats()


# ─── GOVERNANCE: Audit ───

@router.get("/governance/audit")
async def api_audit_log(action: Optional[str] = None, actor_id: Optional[str] = None, skip: int = 0, limit: int = 50):
    filters = {}
    if action:
        filters["action"] = action
    if actor_id:
        filters["actor_id"] = actor_id
    return await query_audit_log(filters, skip, limit)


# ─── GOVERNANCE: Circuit Breakers ───

@router.get("/governance/circuit-breakers")
async def api_get_breakers():
    return await get_all_breakers()

@router.get("/governance/circuit-breakers/tripped")
async def api_tripped_breakers():
    return await get_tripped_breakers()

@router.post("/governance/circuit-breakers/{breaker_id}/update")
async def api_update_breaker(breaker_id: str, value: float):
    result = await update_breaker_value(breaker_id, value)
    if not result:
        raise HTTPException(404, "Breaker not found")
    return result

@router.post("/governance/circuit-breakers/{breaker_id}/reset")
async def api_reset_breaker(breaker_id: str):
    return await reset_breaker(breaker_id)


# ─── GOVERNANCE: Trust Scores ───

@router.get("/governance/trust/{entity_type}/{entity_id}")
async def api_get_trust(entity_type: str, entity_id: str):
    return await get_trust_score(entity_type, entity_id)

@router.post("/governance/trust/update")
async def api_update_trust(req: TrustUpdateRequest):
    return await update_trust_score(req.entity_type, req.entity_id, req.event)

@router.get("/governance/trust/leaderboard")
async def api_trust_leaderboard(entity_type: str = "agent", limit: int = 20):
    return await get_trust_leaderboard(entity_type, limit)

@router.get("/governance/trust/low")
async def api_low_trust(entity_type: Optional[str] = None, threshold: float = 30.0):
    return await get_low_trust_entities(entity_type, threshold)


# ─── SYSTEM STATUS ───

@router.get("/system/status")
async def api_system_status():
    """Get overall system health status."""
    tripped = await get_tripped_breakers()
    workload = await get_agent_workload()
    graphs = await list_task_graphs(status="in_progress")
    verify_stats = await get_verification_stats()

    return {
        "status": "degraded" if tripped else "operational",
        "circuit_breakers_tripped": len(tripped),
        "tripped_breakers": [b["name"] for b in tripped],
        "active_workflows": len(graphs),
        "agent_networks": len(workload),
        "total_agents": sum(w["total"] for w in workload),
        "busy_agents": sum(w["busy"] for w in workload),
        "verification_stats": verify_stats,
    }
