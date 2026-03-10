"""MAARS Kernel API Routes - Core runtime, task graphs, execution gateway, tool registry."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from auth import get_current_user
from services.kernel_service import (
    get_kernel_status, create_task_graph, get_task_graphs,
    get_task_graph, update_task_graph, delete_task_graph,
    log_execution, get_execution_logs, get_trust_scores,
    register_tool, get_tool_registry, get_circuit_breakers,
    create_kg_node, create_kg_edge, get_knowledge_graph,
    delete_kg_node, seed_knowledge_graph,
    get_rbac_config, get_user_roles, set_user_role,
    get_circuit_breakers_full, update_circuit_breaker, reset_circuit_breaker,
    get_cost_overview, get_cost_by_model, get_cost_by_agent,
    get_cost_budget, update_cost_budget,
    create_workflow, get_workflows, get_workflow, update_workflow, delete_workflow,
    execute_workflow, get_workflow_runs, get_workflow_run,
    advance_workflow_step, simulate_workflow_execution,
    get_environments, get_user_environment, set_user_environment, get_env_stats,
    get_memory_layers, get_memory_stats,
)
from infinity_catalog import (
    NETWORK_DEFINITIONS, AUTONOMY_TIERS, AGENT_LIFECYCLE_STATES,
    INFINITY_AGENTS, get_agents_by_network, get_network_for_agent,
)

router = APIRouter(prefix="/kernel", tags=["kernel"])


# ---------- Kernel Status ----------
@router.get("/status")
async def kernel_status(user=Depends(get_current_user)):
    return await get_kernel_status()


# ---------- System Architecture ----------
@router.get("/architecture")
async def get_architecture(user=Depends(get_current_user)):
    """Return the full MAARS Infinity system architecture."""
    return {
        "system": "MAARS Infinity",
        "version": "1.0",
        "layers": [
            {"name": "Human Governance Layer", "level": 0, "description": "Humans retain final authority over all high-impact decisions"},
            {"name": "Infinity Strategic Council", "level": 1, "description": "Top AI strategic board with 17 council members"},
            {"name": "Global Coordination Core", "level": 2, "description": "Macro-level coordination engine"},
            {"name": "MAARS Kernel", "level": 3, "description": "Core runtime operating system with 15 subsystems"},
            {"name": "Planning & Task Graph Layer", "level": 4, "description": "Structured task decomposition and tracking"},
            {"name": "Executive Agent Layer", "level": 5, "description": "12 executive agents translating strategy to execution"},
            {"name": "Department & Industry Networks", "level": 6, "description": "27 specialized agent networks"},
            {"name": "Live Web Search & Intelligence", "level": 7, "description": "Real-time external awareness"},
            {"name": "Tool Registry & Capability Marketplace", "level": 8, "description": "Central tool management"},
            {"name": "Execution Gateway", "level": 9, "description": "All actions flow through governed execution"},
            {"name": "Memory & Knowledge Layer", "level": 10, "description": "7-layer memory hierarchy"},
            {"name": "Economic Feedback & Portfolio", "level": 11, "description": "Outcome-driven resource allocation"},
            {"name": "Verification & Experimentation", "level": 12, "description": "Output validation and learning loops"},
            {"name": "Risk, Safety & Compliance", "level": 13, "description": "Governance, legal, and security controls"},
            {"name": "Observability & Audit", "level": 14, "description": "Full system visibility and traceability"},
            {"name": "Infrastructure Layer", "level": 15, "description": "Runtime infrastructure and recovery"},
        ],
        "networks": NETWORK_DEFINITIONS,
        "autonomy_tiers": AUTONOMY_TIERS,
        "lifecycle_states": AGENT_LIFECYCLE_STATES,
        "total_agents": len(INFINITY_AGENTS),
        "total_networks": len(NETWORK_DEFINITIONS),
    }


# ---------- Networks & Agents ----------
@router.get("/networks")
async def list_networks(user=Depends(get_current_user)):
    """List all agent networks with agent counts."""
    result = []
    for key, net in NETWORK_DEFINITIONS.items():
        agents = get_agents_by_network(key)
        result.append({
            "key": key,
            **net,
            "agent_count": len(agents),
        })
    return result


@router.get("/networks/{network_key}/agents")
async def list_network_agents(network_key: str, user=Depends(get_current_user)):
    """List all agents in a specific network."""
    if network_key not in NETWORK_DEFINITIONS:
        raise HTTPException(status_code=404, detail="Network not found")
    agents = get_agents_by_network(network_key)
    return {
        "network": NETWORK_DEFINITIONS[network_key],
        "agents": agents,
    }


# ---------- Task Graphs ----------
class TaskGraphCreate(BaseModel):
    title: str
    objective: str = ""
    scope: str = ""
    nodes: list = []
    edges: list = []
    success_criteria: list = []
    required_agents: list = []
    required_tools: list = []
    cost_estimate: float = 0
    risk_score: float = 0
    timeline: str = ""


class TaskGraphUpdate(BaseModel):
    title: Optional[str] = None
    objective: Optional[str] = None
    status: Optional[str] = None
    nodes: Optional[list] = None
    edges: Optional[list] = None


@router.post("/task-graphs")
async def create_graph(data: TaskGraphCreate, user=Depends(get_current_user)):
    graph = await create_task_graph(user.user_id, data.dict())
    return graph


@router.get("/task-graphs")
async def list_graphs(status: Optional[str] = None, user=Depends(get_current_user)):
    return await get_task_graphs(user.user_id, status=status)


@router.get("/task-graphs/{graph_id}")
async def get_graph(graph_id: str, user=Depends(get_current_user)):
    graph = await get_task_graph(user.user_id, graph_id)
    if not graph:
        raise HTTPException(status_code=404, detail="Task graph not found")
    return graph


@router.put("/task-graphs/{graph_id}")
async def update_graph(graph_id: str, data: TaskGraphUpdate, user=Depends(get_current_user)):
    update_data = {k: v for k, v in data.dict().items() if v is not None}
    success = await update_task_graph(user.user_id, graph_id, update_data)
    if not success:
        raise HTTPException(status_code=404, detail="Task graph not found")
    return {"status": "updated"}


@router.delete("/task-graphs/{graph_id}")
async def remove_graph(graph_id: str, user=Depends(get_current_user)):
    success = await delete_task_graph(user.user_id, graph_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task graph not found")
    return {"status": "deleted"}


# ---------- Execution Gateway ----------
class ExecutionLog(BaseModel):
    action: str
    agent_id: str = ""
    tool_id: str = ""
    input_summary: str = ""
    output_summary: str = ""
    status: str = "completed"
    cost: float = 0
    latency_ms: float = 0
    environment: str = "production"


@router.post("/execute")
async def log_exec(data: ExecutionLog, user=Depends(get_current_user)):
    return await log_execution(user.user_id, data.dict())


@router.get("/execution-logs")
async def list_exec_logs(limit: int = 100, user=Depends(get_current_user)):
    return await get_execution_logs(user.user_id, limit=limit)


# ---------- Trust Scores ----------
@router.get("/trust-scores")
async def list_trust_scores(user=Depends(get_current_user)):
    return await get_trust_scores(user.user_id)


# ---------- Tool Registry ----------
class ToolRegister(BaseModel):
    tool_id: str
    name: str
    category: str = "general"
    description: str = ""
    endpoint: str = ""
    reliability_score: float = 1.0
    cost_score: float = 0
    risk_score: float = 0


@router.post("/tools")
async def register_new_tool(data: ToolRegister, user=Depends(get_current_user)):
    if getattr(user, 'role', '') != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    return await register_tool(data.dict())


@router.get("/tools")
async def list_tools(user=Depends(get_current_user)):
    return await get_tool_registry()


# ---------- Circuit Breakers ----------
@router.get("/circuit-breakers")
async def list_circuit_breakers(user=Depends(get_current_user)):
    return await get_circuit_breakers()


# ---------- Knowledge Graph ----------
class KGNodeCreate(BaseModel):
    node_id: str
    label: str
    type: str = "entity"
    properties: dict = {}


class KGEdgeCreate(BaseModel):
    edge_id: str
    source: str
    target: str
    relationship: str = "related_to"
    weight: float = 1.0
    properties: dict = {}


@router.get("/knowledge-graph")
async def get_kg(user=Depends(get_current_user)):
    """Get the full knowledge graph."""
    await seed_knowledge_graph(user.user_id)
    return await get_knowledge_graph(user.user_id)


@router.post("/knowledge-graph/nodes")
async def add_kg_node(data: KGNodeCreate, user=Depends(get_current_user)):
    return await create_kg_node(user.user_id, data.dict())


@router.post("/knowledge-graph/edges")
async def add_kg_edge(data: KGEdgeCreate, user=Depends(get_current_user)):
    return await create_kg_edge(user.user_id, data.dict())


@router.delete("/knowledge-graph/nodes/{node_id}")
async def remove_kg_node(node_id: str, user=Depends(get_current_user)):
    await delete_kg_node(user.user_id, node_id)
    return {"status": "deleted"}


# ---------- RBAC ----------

class UserRoleUpdate(BaseModel):
    role: str


@router.get("/rbac/config")
async def rbac_config(user=Depends(get_current_user)):
    return await get_rbac_config()


@router.get("/rbac/users")
async def rbac_users(user=Depends(get_current_user)):
    return await get_user_roles()


@router.put("/rbac/users/{user_id}/role")
async def rbac_set_role(user_id: str, data: UserRoleUpdate, user=Depends(get_current_user)):
    result = await set_user_role(user_id, data.role)
    if not result:
        raise HTTPException(status_code=400, detail="Invalid role")
    return result


# ---------- Circuit Breakers (Full CRUD) ----------

class CBUpdate(BaseModel):
    state: str = None
    failure_threshold: int = None
    reset_timeout_s: int = None
    failures: int = None
    name: str = None
    description: str = None


@router.get("/circuit-breakers/full")
async def list_circuit_breakers_full(user=Depends(get_current_user)):
    return await get_circuit_breakers_full()


@router.put("/circuit-breakers/{breaker_id}")
async def update_cb(breaker_id: str, data: CBUpdate, user=Depends(get_current_user)):
    result = await update_circuit_breaker(breaker_id, data.dict(exclude_none=True))
    if not result:
        raise HTTPException(status_code=404, detail="Circuit breaker not found")
    return result


@router.post("/circuit-breakers/{breaker_id}/reset")
async def reset_cb(breaker_id: str, user=Depends(get_current_user)):
    result = await reset_circuit_breaker(breaker_id)
    if not result:
        raise HTTPException(status_code=404, detail="Circuit breaker not found")
    return result


# ---------- Cost Governance ----------

class BudgetUpdate(BaseModel):
    monthly_limit: float = None
    daily_limit: float = None
    alert_threshold: float = None
    auto_pause: bool = None


@router.get("/cost/overview")
async def cost_overview(user=Depends(get_current_user)):
    return await get_cost_overview()


@router.get("/cost/by-model")
async def cost_by_model(user=Depends(get_current_user)):
    return await get_cost_by_model()


@router.get("/cost/by-agent")
async def cost_by_agent(user=Depends(get_current_user)):
    return await get_cost_by_agent()


@router.get("/cost/budget")
async def cost_budget(user=Depends(get_current_user)):
    return await get_cost_budget()


@router.put("/cost/budget")
async def update_budget(data: BudgetUpdate, user=Depends(get_current_user)):
    return await update_cost_budget(data.dict(exclude_none=True))


# ---------- Workflows ----------

class WorkflowCreate(BaseModel):
    name: str = "Untitled Workflow"
    description: str = ""
    nodes: list = []
    edges: list = []


class WorkflowUpdate(BaseModel):
    name: str = None
    description: str = None
    nodes: list = None
    edges: list = None
    status: str = None


@router.get("/workflows")
async def list_workflows(user=Depends(get_current_user)):
    return await get_workflows(user.user_id)


@router.post("/workflows")
async def create_wf(data: WorkflowCreate, user=Depends(get_current_user)):
    return await create_workflow(user.user_id, data.dict())


@router.get("/workflows/{workflow_id}")
async def get_wf(workflow_id: str, user=Depends(get_current_user)):
    wf = await get_workflow(user.user_id, workflow_id)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return wf


@router.put("/workflows/{workflow_id}")
async def update_wf(workflow_id: str, data: WorkflowUpdate, user=Depends(get_current_user)):
    result = await update_workflow(user.user_id, workflow_id, data.dict(exclude_none=True))
    if not result:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return result


@router.delete("/workflows/{workflow_id}")
async def delete_wf(workflow_id: str, user=Depends(get_current_user)):
    await delete_workflow(user.user_id, workflow_id)
    return {"status": "deleted"}


# ---------- Workflow Execution ----------

@router.post("/workflows/{workflow_id}/run")
async def run_workflow(workflow_id: str, user=Depends(get_current_user)):
    """Start a workflow run."""
    run = await execute_workflow(user.user_id, workflow_id)
    if not run:
        raise HTTPException(status_code=404, detail="Workflow not found")
    # Simulate execution in background
    import asyncio
    asyncio.create_task(simulate_workflow_execution(user.user_id, run["run_id"]))
    return run


@router.get("/workflows/{workflow_id}/runs")
async def list_workflow_runs(workflow_id: str, user=Depends(get_current_user)):
    return await get_workflow_runs(user.user_id, workflow_id)


@router.get("/workflow-runs/{run_id}")
async def get_run(run_id: str, user=Depends(get_current_user)):
    run = await get_workflow_run(user.user_id, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


# ---------- Environments ----------

class EnvSwitch(BaseModel):
    environment: str


@router.get("/environments")
async def list_envs(user=Depends(get_current_user)):
    envs = await get_environments()
    user_env = await get_user_environment(user.user_id)
    stats = await get_env_stats()
    return {"environments": envs, "active": user_env.get("active_env", "sandbox"), "stats": stats}


@router.put("/environments/active")
async def switch_env(data: EnvSwitch, user=Depends(get_current_user)):
    result = await set_user_environment(user.user_id, data.environment)
    if not result:
        raise HTTPException(status_code=400, detail="Invalid environment")
    return result


# ---------- Memory Hierarchy ----------

@router.get("/memory/layers")
async def memory_layers(user=Depends(get_current_user)):
    return await get_memory_layers()


@router.get("/memory/stats")
async def memory_stats(user=Depends(get_current_user)):
    return await get_memory_stats(user.user_id)
