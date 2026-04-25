"""MAARS Infinity — Full System API Routes (Phases 1-5).
Exposes kernel, router, verification, governance, orchestrator, memory, intelligence, portfolio endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime, timezone
from db import db

ALERT_RULES_COLLECTION = "alert_rules"
ALERTS_COLLECTION = "system_alerts"
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
from kernel.tool_registry import register_tool, get_tools, validate_schema, record_tool_call, get_tool_health
from kernel.approval_controller import request_approval, decide_approval, get_pending_approvals, get_approval_history
# `router.engine` helpers were only used by the deleted /router/* endpoints.
# log_model_result is no longer imported here — if any other module needs it,
# import directly from router.engine there.
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
from governance.incidents import create_incident, resolve_incident, get_incidents, escalate, get_escalations, resolve_escalation
from governance.autonomy import get_tier_info, check_action_allowed, get_agent_autonomy, set_agent_autonomy, get_all_tiers
from orchestrator.commander import execute_goal, get_commander_log, classify_goal_ai, classify_goal_rules, execute_graph, get_execution_runs
from memory_system.working import store_working, get_working, append_result, clear_working
from memory_system.episodic import record_episode, recall_episodes, recall_similar, get_lessons
from memory_system.knowledge_graph import add_entity, add_relationship, get_entity, query_graph, get_graph_stats, traverse_graph, search_entities, find_paths
from intelligence.search_engine import plan_query, search_and_rank, verify_across_sources
from intelligence.monitors import create_monitor, run_monitor, get_monitors, get_alerts
from intelligence.citation import create_citation, get_citations
from portfolio.ventures import create_venture, update_venture_metrics, get_ventures, transition_venture, get_portfolio_summary

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


# ─── MODEL ROUTER (removed) ───
# /router/route, /router/classify, /router/performance, /router/providers,
# /router/execute were deleted — they exposed provider picks to clients
# (breaking the Universal Gateway's client-opacity design) and duplicated
# the execution path handled by /v1/chat/completions + llm_gateway.complete().
# Internal callers use services.llm_gateway.complete() directly.


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


# ════════════════════════════════════════════════════════════════════
# PHASE 2: Intelligence + Memory
# ════════════════════════════════════════════════════════════════════

# ─── Memory: Working ───

class WorkingMemoryRequest(BaseModel):
    task_id: str
    agent_id: str
    context: dict
    intermediate_results: Optional[list] = None

class AppendResultRequest(BaseModel):
    task_id: str
    agent_id: str
    result: dict

@router.post("/memory/working/store")
async def api_store_working(req: WorkingMemoryRequest):
    return await store_working(req.task_id, req.agent_id, req.context, req.intermediate_results)

@router.get("/memory/working/{task_id}")
async def api_get_working(task_id: str, agent_id: Optional[str] = None):
    return await get_working(task_id, agent_id)

@router.post("/memory/working/append")
async def api_append_result(req: AppendResultRequest):
    return await append_result(req.task_id, req.agent_id, req.result)

@router.delete("/memory/working/{task_id}")
async def api_clear_working(task_id: str):
    return await clear_working(task_id)


# ─── Memory: Episodic ───

class EpisodeRequest(BaseModel):
    agent_id: str
    event_type: str
    event_data: dict
    outcome: Optional[str] = ""
    lessons_learned: Optional[str] = ""

@router.post("/memory/episodic/record")
async def api_record_episode(req: EpisodeRequest):
    return await record_episode(req.agent_id, req.event_type, req.event_data, req.outcome, req.lessons_learned)

@router.get("/memory/episodic/{agent_id}")
async def api_recall_episodes(agent_id: str, event_type: Optional[str] = None, limit: int = 20):
    return await recall_episodes(agent_id, event_type, limit)

@router.get("/memory/episodic/collective/{event_type}")
async def api_recall_similar(event_type: str, limit: int = 10):
    return await recall_similar(event_type, limit)

@router.get("/memory/lessons")
async def api_get_lessons(agent_id: Optional[str] = None, limit: int = 20):
    return await get_lessons(agent_id, limit)


# ─── Memory: Knowledge Graph ───

class EntityRequest(BaseModel):
    entity: str
    entity_type: str
    attributes: Optional[dict] = None
    source: Optional[str] = "system"

class RelationshipRequest(BaseModel):
    entity: str
    target: str
    relationship_type: str
    weight: Optional[float] = 1.0
    source: Optional[str] = "system"

@router.post("/memory/knowledge-graph/entity")
async def api_add_entity(req: EntityRequest):
    return await add_entity(req.entity, req.entity_type, req.attributes, req.source)

@router.post("/memory/knowledge-graph/relationship")
async def api_add_relationship(req: RelationshipRequest):
    return await add_relationship(req.entity, req.target, req.relationship_type, req.weight, req.source)

@router.get("/memory/knowledge-graph/entity/{entity}")
async def api_get_entity(entity: str):
    doc = await get_entity(entity)
    if not doc:
        raise HTTPException(404, "Entity not found")
    return doc

@router.get("/memory/knowledge-graph/query")
async def api_query_graph(entity_type: Optional[str] = None, limit: int = 50):
    return await query_graph(entity_type, limit=limit)

@router.get("/memory/knowledge-graph/stats")
async def api_graph_stats():
    return await get_graph_stats()


@router.get("/memory/knowledge-graph/traverse/{entity}")
async def api_traverse_graph(entity: str, max_depth: int = 3, relationship: Optional[str] = None):
    return await traverse_graph(entity, max_depth, relationship)


@router.get("/memory/knowledge-graph/search")
async def api_search_entities(q: str, limit: int = 20):
    return await search_entities(q, limit)


@router.get("/memory/knowledge-graph/paths")
async def api_find_paths(source: str, target: str, max_depth: int = 4):
    return await find_paths(source, target, max_depth)


# ─── Intelligence: Search ───

class SearchRequest(BaseModel):
    query: str
    freshness: Optional[str] = "standard"

class VerifyClaimRequest(BaseModel):
    claim: str
    results: list

@router.post("/intelligence/search/plan")
async def api_plan_query(goal: str):
    return await plan_query(goal)

@router.post("/intelligence/search")
async def api_search(req: SearchRequest):
    return await search_and_rank(req.query, req.freshness)

@router.post("/intelligence/verify-sources")
async def api_verify_sources(req: VerifyClaimRequest):
    return await verify_across_sources(req.claim, req.results)


# ─── Intelligence: Monitors ───

class MonitorRequest(BaseModel):
    monitor_type: str
    target: str
    config: Optional[dict] = None

@router.post("/intelligence/monitors")
async def api_create_monitor(req: MonitorRequest):
    return await create_monitor(req.monitor_type, req.target, req.config)

@router.get("/intelligence/monitors")
async def api_get_monitors(monitor_type: Optional[str] = None):
    return await get_monitors(monitor_type)

@router.post("/intelligence/monitors/run")
async def api_run_monitor(monitor_type: str, target: str):
    return await run_monitor(monitor_type, target)

@router.get("/intelligence/alerts")
async def api_get_alerts(min_level: str = "low"):
    return await get_alerts(min_level)


# ─── Intelligence: Citations ───

class CitationRequest(BaseModel):
    claim: str
    sources: list
    confidence: float
    verified: Optional[bool] = False

@router.post("/intelligence/citations")
async def api_create_citation(req: CitationRequest):
    return await create_citation(req.claim, req.sources, req.confidence, req.verified)

@router.get("/intelligence/citations")
async def api_get_citations(verified_only: bool = False, limit: int = 50):
    return await get_citations(verified_only, limit)


# ─── Tool Registry ───

class ToolRegisterRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    tool_id: str
    name: str
    description: str
    tool_schema: dict = Field(default_factory=dict, alias="schema")
    permissions: Optional[list] = None
    category: Optional[str] = "general"
    contract: Optional[dict] = None
    version: Optional[str] = "1.0"
    tags: Optional[list] = None

class ToolCallRequest(BaseModel):
    tool_id: str
    success: bool
    latency_ms: int

@router.post("/tools/register")
async def api_register_tool(req: ToolRegisterRequest):
    return await register_tool(
        req.tool_id,
        req.name,
        req.description,
        req.tool_schema,
        req.permissions,
        req.category,
        contract=req.contract,
        version=req.version or "1.0",
        tags=req.tags,
    )

@router.get("/tools")
async def api_get_tools(category: Optional[str] = None):
    return await get_tools(category)

@router.post("/tools/validate")
async def api_validate_schema(tool_id: str, input_data: dict):
    return await validate_schema(tool_id, input_data)

@router.post("/tools/record-call")
async def api_record_tool_call(req: ToolCallRequest):
    await record_tool_call(req.tool_id, req.success, req.latency_ms)
    return {"recorded": True}

@router.get("/tools/health")
async def api_tool_health(tool_id: Optional[str] = None):
    return await get_tool_health(tool_id)


# ════════════════════════════════════════════════════════════════════
# PHASE 3: Commander Orion + Governance
# ════════════════════════════════════════════════════════════════════

class ExecuteGoalRequest(BaseModel):
    description: str
    requester_id: Optional[str] = "system"
    environment: Optional[str] = "simulation"

@router.post("/orchestrator/execute")
async def api_execute_goal(req: ExecuteGoalRequest):
    return await execute_goal(req.description, req.requester_id, req.environment)

@router.get("/orchestrator/log")
async def api_commander_log(limit: int = 20):
    return await get_commander_log(limit)

@router.post("/orchestrator/classify")
async def api_classify_goal(description: str):
    return await classify_goal_ai(description)


# ─── Approvals ───

class ApprovalRequest(BaseModel):
    task_id: str
    graph_id: str
    action: str
    reason: str
    urgency: Optional[str] = "normal"

class ApprovalDecision(BaseModel):
    task_id: str
    approved: bool
    approver: str
    notes: Optional[str] = ""

@router.post("/governance/approvals/request")
async def api_request_approval(req: ApprovalRequest):
    return await request_approval(req.task_id, req.graph_id, req.action, req.reason, urgency=req.urgency)

@router.post("/governance/approvals/decide")
async def api_decide_approval(req: ApprovalDecision):
    return await decide_approval(req.task_id, req.approved, req.approver, req.notes)

@router.get("/governance/approvals/pending")
async def api_pending_approvals():
    return await get_pending_approvals()

@router.get("/governance/approvals/history")
async def api_approval_history(limit: int = 50):
    return await get_approval_history(limit)


# ─── Incidents & Escalations ───

class IncidentRequest(BaseModel):
    incident_type: str
    severity: str
    description: str
    affected: Optional[list] = None

class EscalateRequest(BaseModel):
    source_task_id: str
    reason: str
    severity: Optional[str] = "high"

@router.post("/governance/incidents")
async def api_create_incident(req: IncidentRequest):
    return await create_incident(req.incident_type, req.severity, req.description, req.affected)

@router.get("/governance/incidents")
async def api_get_incidents(status: Optional[str] = None, severity: Optional[str] = None):
    return await get_incidents(status, severity)

@router.post("/governance/escalations")
async def api_escalate(req: EscalateRequest):
    return await escalate(req.source_task_id, req.reason, req.severity)

@router.get("/governance/escalations")
async def api_get_escalations(status: str = "open"):
    return await get_escalations(status)


# ─── Autonomy Tiers ───

@router.get("/governance/autonomy/tiers")
async def api_all_tiers():
    return get_all_tiers()

@router.get("/governance/autonomy/agent/{agent_id}")
async def api_agent_autonomy(agent_id: str):
    return await get_agent_autonomy(agent_id)

@router.post("/governance/autonomy/agent/{agent_id}/set")
async def api_set_autonomy(agent_id: str, tier: int):
    return await set_agent_autonomy(agent_id, tier)

@router.post("/governance/autonomy/check")
async def api_check_action(tier: int, action: str):
    return check_action_allowed(tier, action)


# ════════════════════════════════════════════════════════════════════
# PHASE 4: Portfolio & Economics
# ════════════════════════════════════════════════════════════════════

class VentureRequest(BaseModel):
    name: str
    description: str
    stage: Optional[str] = "idea"
    initial_investment: Optional[float] = 0

class VentureMetricsRequest(BaseModel):
    name: str
    metrics: dict

@router.post("/portfolio/ventures")
async def api_create_venture(req: VentureRequest):
    return await create_venture(req.name, req.description, req.stage, req.initial_investment)

@router.get("/portfolio/ventures")
async def api_get_ventures(status: Optional[str] = None):
    return await get_ventures(status)

@router.post("/portfolio/ventures/metrics")
async def api_update_metrics(req: VentureMetricsRequest):
    return await update_venture_metrics(req.name, req.metrics)

@router.post("/portfolio/ventures/{name}/transition")
async def api_transition_venture(name: str, stage: str):
    return await transition_venture(name, stage)

@router.get("/portfolio/summary")
async def api_portfolio_summary():
    return await get_portfolio_summary()


# ════════════════════════════════════════════════════════════════════
# PHASE 5: Operator Control & Test Harness
# ════════════════════════════════════════════════════════════════════

from testing_harness.scenarios import run_scenario, run_all_scenarios, get_test_runs, SCENARIOS


@router.get("/test-harness/scenarios")
async def api_list_scenarios():
    return {k: {"name": v["name"], "description": v["description"]} for k, v in SCENARIOS.items()}


@router.post("/test-harness/run/{scenario_id}")
async def api_run_scenario(scenario_id: str):
    result = await run_scenario(scenario_id)
    if "error" in result:
        raise HTTPException(400, result["error"])
    return result


@router.post("/test-harness/run-all")
async def api_run_all():
    return await run_all_scenarios()


@router.get("/test-harness/history")
async def api_test_history(scenario_id: Optional[str] = None, limit: int = 20):
    return await get_test_runs(scenario_id, limit)


@router.get("/operator/dashboard")
async def api_operator_dashboard():
    """Get unified operator dashboard data."""
    from kernel.scheduler import get_agent_workload
    from governance.circuit_breaker import get_all_breakers, get_tripped_breakers
    from kernel.budget_controller import get_spend_summary
    from governance.trust_scoring import get_low_trust_entities

    tripped = await get_tripped_breakers()
    workload = await get_agent_workload()
    pending = await get_pending_approvals()
    active_incidents = await get_incidents(status="open")
    open_escalations = await get_escalations(status="open")
    breakers = await get_all_breakers()
    budget = await get_spend_summary(period="daily")
    low_trust = await get_low_trust_entities(threshold=30)

    return {
        "system_health": "degraded" if tripped else "operational",
        "pending_approvals": len(pending),
        "approvals": pending[:10],
        "open_incidents": len(active_incidents),
        "incidents": active_incidents[:10],
        "open_escalations": len(open_escalations),
        "escalations": open_escalations[:10],
        "circuit_breakers": {"total": len(breakers), "tripped": len(tripped), "breakers": breakers},
        "budget_summary": budget,
        "low_trust_entities": low_trust,
        "agent_workload": workload,
        "tiers": get_all_tiers(),
    }


# ════════════════════════════════════════════════════════════════════
# EXECUTION LOOP ENDPOINTS
# ════════════════════════════════════════════════════════════════════

@router.post("/orchestrator/execute-graph/{graph_id}")
async def api_execute_graph(graph_id: str):
    result = await execute_graph(graph_id)
    if "error" in result:
        raise HTTPException(404, result["error"])
    return result


class FullExecuteRequest(BaseModel):
    description: str
    requester_id: Optional[str] = "operator"
    environment: Optional[str] = "production"


@router.post("/orchestrator/full-execute")
async def api_full_execute(req: FullExecuteRequest):
    """Full pipeline: classify → decompose → create graph → execute all nodes → verify → report."""
    goal_result = await execute_goal(req.description, req.requester_id, req.environment)
    exec_result = await execute_graph(goal_result["graph_id"])
    return {**goal_result, "execution": exec_result}


@router.get("/orchestrator/runs")
async def api_get_runs(graph_id: Optional[str] = None, limit: int = 20):
    return await get_execution_runs(graph_id, limit)


# ════════════════════════════════════════════════════════════════════
# METRICS & ALERTING ENDPOINTS
# ════════════════════════════════════════════════════════════════════

from governance.metrics import collect_metrics, evaluate_alerts, get_active_alerts, acknowledge_alert, get_alert_rules, update_alert_rule, get_metrics_history


@router.get("/metrics/live")
async def api_live_metrics():
    metrics = await collect_metrics()
    alerts = await evaluate_alerts(metrics)
    return {"metrics": metrics, "triggered_alerts": alerts}


@router.get("/metrics/history")
async def api_metrics_history(limit: int = 30):
    return await get_metrics_history(limit)


@router.get("/alerts/active")
async def api_get_active_alerts():
    return await get_active_alerts()


@router.post("/alerts/{rule_id}/acknowledge")
async def api_ack_alert(rule_id: str):
    return await acknowledge_alert(rule_id)


@router.get("/alerts/rules")
async def api_get_rules():
    return await get_alert_rules()


class UpdateRuleRequest(BaseModel):
    threshold: Optional[float] = None
    enabled: Optional[bool] = None
    severity: Optional[str] = None


@router.put("/alerts/rules/{rule_id}")
async def api_update_rule(rule_id: str, req: UpdateRuleRequest):
    return await update_alert_rule(rule_id, req.dict(exclude_none=True))


# ════════════════════════════════════════════════════════════════════
# AGENT RUNTIME
# ════════════════════════════════════════════════════════════════════

from runtime.agent_runtime import execute_agent_loop, get_runtime_executions


class AgentExecRequest(BaseModel):
    agent_id: str
    task_description: str
    context: Optional[dict] = None
    environment: Optional[str] = "sandbox"
    graph_id: Optional[str] = None
    node_id: Optional[str] = None


@router.post("/runtime/execute")
async def api_runtime_execute(req: AgentExecRequest):
    return await execute_agent_loop(
        req.agent_id, req.task_description, req.context,
        req.environment, req.graph_id, req.node_id,
    )


@router.get("/runtime/history")
async def api_runtime_history(agent_id: Optional[str] = None, status: Optional[str] = None, limit: int = 20):
    return await get_runtime_executions(agent_id, status, limit)


# ════════════════════════════════════════════════════════════════════
# AGENT CATALOG
# ════════════════════════════════════════════════════════════════════

from services.catalog_manager import get_catalog, get_agent_detail, update_agent_maturity, get_catalog_stats, get_networks


@router.get("/catalog/agents")
async def api_catalog(network: Optional[str] = None, maturity: Optional[str] = None, search: Optional[str] = None, capability: Optional[str] = None, tier: Optional[int] = None, limit: int = 50, skip: int = 0):
    return await get_catalog(network, maturity, search, capability, tier, limit, skip)


@router.get("/catalog/agents/{agent_id}")
async def api_agent_detail(agent_id: str):
    agent = await get_agent_detail(agent_id)
    if not agent:
        raise HTTPException(404, "Agent not found")
    return agent


@router.put("/catalog/agents/{agent_id}/maturity")
async def api_update_maturity(agent_id: str, maturity: str):
    return await update_agent_maturity(agent_id, maturity)


@router.get("/catalog/stats")
async def api_catalog_stats():
    return await get_catalog_stats()


@router.get("/catalog/networks")
async def api_catalog_networks():
    return await get_networks()


# ════════════════════════════════════════════════════════════════════
# RECOVERY SYSTEM
# ════════════════════════════════════════════════════════════════════

from governance.recovery import quarantine_agent, release_from_quarantine, get_quarantined_agents, rollback_graph, retry_failed_node, get_recovery_log


class QuarantineRequest(BaseModel):
    agent_id: str
    reason: str


@router.post("/recovery/quarantine")
async def api_quarantine(req: QuarantineRequest):
    return await quarantine_agent(req.agent_id, req.reason)


@router.post("/recovery/release/{agent_id}")
async def api_release(agent_id: str):
    return await release_from_quarantine(agent_id)


@router.get("/recovery/quarantined")
async def api_quarantined():
    return await get_quarantined_agents()


@router.post("/recovery/rollback/{graph_id}")
async def api_rollback(graph_id: str, reason: str = "operator_rollback"):
    return await rollback_graph(graph_id, reason)


@router.post("/recovery/retry/{graph_id}/{node_id}")
async def api_retry(graph_id: str, node_id: str):
    return await retry_failed_node(graph_id, node_id)


@router.get("/recovery/log")
async def api_recovery_log(limit: int = 30):
    return await get_recovery_log(limit)


# ════════════════════════════════════════════════════════════════════
# SEMANTIC MEMORY
# ════════════════════════════════════════════════════════════════════

from memory_system.semantic import (
    store_concept, query_semantic, build_agent_context,
    extract_concepts_from_execution, get_concept, get_semantic_stats,
)


class StoreConceptRequest(BaseModel):
    concept: str
    concept_type: str
    description: str
    source_agent: Optional[str] = "system"
    related_entities: Optional[List[str]] = None
    confidence: Optional[float] = 1.0
    tags: Optional[List[str]] = None


class SemanticQueryRequest(BaseModel):
    query: str
    agent_id: Optional[str] = None
    concept_type: Optional[str] = None
    limit: Optional[int] = 10


class AgentContextRequest(BaseModel):
    agent_id: str
    task_description: str
    limit: Optional[int] = 5


@router.post("/memory/semantic/store")
async def api_store_concept(req: StoreConceptRequest):
    return await store_concept(
        req.concept, req.concept_type, req.description,
        req.source_agent, req.related_entities, req.confidence, req.tags,
    )


@router.post("/memory/semantic/query")
async def api_query_semantic(req: SemanticQueryRequest):
    return await query_semantic(req.query, req.agent_id, req.concept_type, req.limit)


@router.post("/memory/semantic/agent-context")
async def api_agent_context(req: AgentContextRequest):
    return await build_agent_context(req.agent_id, req.task_description, req.limit)


@router.get("/memory/semantic/concept/{concept}")
async def api_get_concept(concept: str):
    doc = await get_concept(concept)
    if not doc:
        raise HTTPException(404, "Concept not found")
    return doc


@router.get("/memory/semantic/stats")
async def api_semantic_stats():
    return await get_semantic_stats()


# ════════════════════════════════════════════════════════════════════
# WORKER QUEUES
# ════════════════════════════════════════════════════════════════════

from workers.queue_manager import (
    enqueue_job, get_job, list_jobs, cancel_job, get_queue_stats,
)


class EnqueueJobRequest(BaseModel):
    job_type: str
    payload: dict
    priority: Optional[int] = 5
    callback_url: Optional[str] = None
    max_retries: Optional[int] = 2
    timeout_seconds: Optional[int] = 120


@router.post("/workers/enqueue")
async def api_enqueue_job(req: EnqueueJobRequest):
    return await enqueue_job(
        req.job_type, req.payload, req.priority,
        req.callback_url, req.max_retries, req.timeout_seconds,
    )


@router.get("/workers/jobs")
async def api_list_jobs(status: Optional[str] = None, job_type: Optional[str] = None, limit: int = 20):
    return await list_jobs(status, job_type, limit)


@router.get("/workers/jobs/{job_id}")
async def api_get_job(job_id: str):
    job = await get_job(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    return job


@router.post("/workers/jobs/{job_id}/cancel")
async def api_cancel_job(job_id: str):
    return await cancel_job(job_id)


@router.get("/workers/stats")
async def api_queue_stats():
    return await get_queue_stats()


# ════════════════════════════════════════════════════════════════════
# MULTI-ENVIRONMENT
# ════════════════════════════════════════════════════════════════════

from governance.environments import (
    get_active_environment, set_active_environment,
    get_environment_config, get_all_environments,
    validate_execution_environment, get_environment_stats,
    store_environment_config,
)


class SetEnvironmentRequest(BaseModel):
    environment: str


class EnvironmentOverrideRequest(BaseModel):
    environment: str
    overrides: dict


@router.get("/environments/active")
async def api_active_env():
    env = get_active_environment()
    config = get_environment_config(env)
    return {"active": env, "config": config}


@router.post("/environments/set")
async def api_set_env(req: SetEnvironmentRequest):
    result = set_active_environment(req.environment)
    if "error" in result:
        raise HTTPException(400, result["error"])
    return result


@router.get("/environments")
async def api_all_envs():
    return get_all_environments()


@router.get("/environments/stats")
async def api_env_stats():
    return await get_environment_stats()


@router.post("/environments/validate")
async def api_validate_env(environment: str, autonomy_tier: int = 1, model: Optional[str] = None):
    return validate_execution_environment(environment, autonomy_tier, model)


@router.post("/environments/configure")
async def api_configure_env(req: EnvironmentOverrideRequest):
    return await store_environment_config(req.environment, req.overrides)


# ════════════════════════════════════════════════════════════════════
# CUSTOM ALERT RULES (CRUD)
# ════════════════════════════════════════════════════════════════════

from governance.metrics import get_alert_rules


class CreateAlertRuleRequest(BaseModel):
    rule_id: str
    name: str
    metric: str
    operator: str
    threshold: float
    severity: Optional[str] = "medium"
    enabled: Optional[bool] = True


@router.post("/alerts/rules")
async def api_create_alert_rule(req: CreateAlertRuleRequest):
    """Create a new custom alert rule."""
    existing = await db[ALERT_RULES_COLLECTION].find_one({"rule_id": req.rule_id})
    if existing:
        raise HTTPException(400, f"Rule '{req.rule_id}' already exists")
    rule = {
        "rule_id": req.rule_id,
        "name": req.name,
        "metric": req.metric,
        "operator": req.operator,
        "threshold": req.threshold,
        "severity": req.severity,
        "enabled": req.enabled,
        "custom": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db[ALERT_RULES_COLLECTION].insert_one({**rule})
    rule.pop("_id", None)
    return rule


@router.delete("/alerts/rules/{rule_id}")
async def api_delete_alert_rule(rule_id: str):
    """Delete a custom alert rule."""
    result = await db[ALERT_RULES_COLLECTION].delete_one({"rule_id": rule_id})
    if result.deleted_count == 0:
        raise HTTPException(404, "Rule not found")
    # Also remove any active alerts for this rule
    await db[ALERTS_COLLECTION].delete_many({"rule_id": rule_id})
    return {"rule_id": rule_id, "deleted": True}


# ════════════════════════════════════════════════════════════════════
# WEBSOCKET CONNECTION STATS
# ════════════════════════════════════════════════════════════════════

from routes.infinity_ws import get_connection_stats


@router.get("/ws/stats")
async def api_ws_stats():
    return get_connection_stats()

