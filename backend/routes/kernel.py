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
    get_campaign_templates, get_campaigns, get_campaign,
    create_campaign, update_campaign, delete_campaign, execute_campaign,
    get_integrations, get_user_integrations, save_user_integration,
    disconnect_integration, toggle_integration,
    generate_campaign_pdf,
    get_trust_analytics,
    schedule_campaign, get_scheduled_campaigns, remove_schedule,
    create_organization, get_organization, invite_member, get_org_members,
    update_member_role, remove_member,
    get_widget_catalog, get_user_dashboard, save_user_dashboard, get_widget_data,
    analyze_agent_gaps, auto_create_agent,
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


# ---------- Campaign Builder ----------

class CampaignCreate(BaseModel):
    template_id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    context: Optional[str] = None
    steps: Optional[list] = None

class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    steps: Optional[list] = None
    context: Optional[str] = None
    status: Optional[str] = None


@router.get("/campaign-templates")
async def list_templates(user=Depends(get_current_user)):
    return await get_campaign_templates()


@router.get("/campaigns")
async def list_campaigns(user=Depends(get_current_user)):
    return await get_campaigns(user.user_id)


@router.post("/campaigns")
async def new_campaign(data: CampaignCreate, user=Depends(get_current_user)):
    return await create_campaign(user.user_id, data.dict())


@router.get("/campaigns/{campaign_id}")
async def get_camp(campaign_id: str, user=Depends(get_current_user)):
    c = await get_campaign(user.user_id, campaign_id)
    if not c:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return c


@router.put("/campaigns/{campaign_id}")
async def update_camp(campaign_id: str, data: CampaignUpdate, user=Depends(get_current_user)):
    result = await update_campaign(user.user_id, campaign_id, data.dict(exclude_none=True))
    if not result:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return result


@router.delete("/campaigns/{campaign_id}")
async def delete_camp(campaign_id: str, user=Depends(get_current_user)):
    await delete_campaign(user.user_id, campaign_id)
    return {"status": "deleted"}


@router.post("/campaigns/{campaign_id}/run")
async def run_campaign(campaign_id: str, user=Depends(get_current_user)):
    """Execute a campaign with real LLM calls."""
    campaign = await get_campaign(user.user_id, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if campaign.get("status") == "running":
        raise HTTPException(status_code=409, detail="Campaign already running")
    import asyncio
    asyncio.create_task(execute_campaign(user.user_id, campaign_id))
    return {"status": "started", "campaign_id": campaign_id}


# ---------- Integration Hub ----------

class IntegrationConnect(BaseModel):
    integration_id: str
    config: dict = {}
    enabled: bool = True

class IntegrationToggle(BaseModel):
    enabled: bool


@router.get("/integrations/available")
async def list_available_integrations(user=Depends(get_current_user)):
    available = await get_integrations()
    user_integrations = await get_user_integrations(user.user_id)
    connected_ids = {i["integration_id"] for i in user_integrations}
    return {
        "available": available,
        "connected": user_integrations,
        "connected_ids": list(connected_ids),
    }


@router.post("/integrations/connect")
async def connect_integration(data: IntegrationConnect, user=Depends(get_current_user)):
    result = await save_user_integration(user.user_id, data.dict())
    if not result:
        raise HTTPException(status_code=400, detail="Invalid integration")
    return result


@router.delete("/integrations/{integration_id}")
async def remove_integration(integration_id: str, user=Depends(get_current_user)):
    await disconnect_integration(user.user_id, integration_id)
    return {"status": "disconnected"}


@router.put("/integrations/{integration_id}/toggle")
async def toggle_int(integration_id: str, data: IntegrationToggle, user=Depends(get_current_user)):
    result = await toggle_integration(user.user_id, integration_id, data.enabled)
    if not result:
        raise HTTPException(status_code=404, detail="Integration not found")
    return result


# ---------- Campaign PDF Report ----------

@router.get("/campaigns/{campaign_id}/report")
async def campaign_report(campaign_id: str, token: Optional[str] = None, user=Depends(get_current_user)):
    """Generate and download a PDF report for a campaign."""
    from fastapi.responses import FileResponse
    path = await generate_campaign_pdf(user.user_id, campaign_id)
    if not path:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return FileResponse(path, media_type="application/pdf", filename=f"campaign_{campaign_id}.pdf")


# ---------- Trust Analytics ----------

@router.get("/trust-analytics")
async def trust_analytics(user=Depends(get_current_user)):
    return await get_trust_analytics(user.user_id)


# ---------- Campaign Scheduling ----------

class ScheduleData(BaseModel):
    frequency: str = "weekly"
    day_of_week: Optional[int] = None
    day_of_month: Optional[int] = None
    hour: int = 9
    minute: int = 0
    enabled: bool = True


@router.post("/campaigns/{campaign_id}/schedule")
async def set_schedule(campaign_id: str, data: ScheduleData, user=Depends(get_current_user)):
    result = await schedule_campaign(user.user_id, campaign_id, data.dict())
    if not result:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return result


@router.delete("/campaigns/{campaign_id}/schedule")
async def unset_schedule(campaign_id: str, user=Depends(get_current_user)):
    return await remove_schedule(user.user_id, campaign_id)


@router.get("/scheduled-campaigns")
async def list_scheduled(user=Depends(get_current_user)):
    return await get_scheduled_campaigns(user.user_id)


# ---------- Multi-Tenancy / Organizations ----------

class OrgCreate(BaseModel):
    name: str
    slug: Optional[str] = None

class InviteData(BaseModel):
    email: str
    role: str = "member"

class MemberRoleUpdate(BaseModel):
    role: str


@router.post("/organizations")
async def create_org(data: OrgCreate, user=Depends(get_current_user)):
    return await create_organization(user.user_id, data.dict())


@router.get("/organizations/me")
async def my_org(user=Depends(get_current_user)):
    org = await get_organization(user.user_id)
    if not org:
        return {"org": None, "members": []}
    members = org.get("members", [])
    # Enrich members with user info
    enriched = []
    for m in members:
        from db import db as _db
        u = await _db.users.find_one({"user_id": m["user_id"]}, {"_id": 0, "name": 1, "email": 1})
        enriched.append({**m, "name": u.get("name", "Unknown") if u else "Unknown", "email": u.get("email", "") if u else ""})
    return {"org": org, "members": enriched}


@router.post("/organizations/{org_id}/invite")
async def invite(org_id: str, data: InviteData, user=Depends(get_current_user)):
    result = await invite_member(user.user_id, org_id, data.dict())
    if not result:
        raise HTTPException(status_code=403, detail="Not authorized or org not found")
    return result


@router.put("/organizations/{org_id}/members/{target_user_id}/role")
async def set_member_role(org_id: str, target_user_id: str, data: MemberRoleUpdate, user=Depends(get_current_user)):
    return await update_member_role(user.user_id, org_id, target_user_id, data.role)


@router.delete("/organizations/{org_id}/members/{target_user_id}")
async def kick_member(org_id: str, target_user_id: str, user=Depends(get_current_user)):
    await remove_member(user.user_id, org_id, target_user_id)
    return {"status": "removed"}


# ---------- Custom Analytics Widgets ----------

class DashboardSave(BaseModel):
    widgets: list

class AutoCreateAgent(BaseModel):
    name: str
    role: str
    network: str = "operations"
    description: str = ""


@router.get("/widgets/catalog")
async def widget_cat(user=Depends(get_current_user)):
    return await get_widget_catalog()


@router.get("/dashboard/custom")
async def get_dash(user=Depends(get_current_user)):
    return await get_user_dashboard(user.user_id)


@router.put("/dashboard/custom")
async def save_dash(data: DashboardSave, user=Depends(get_current_user)):
    return await save_user_dashboard(user.user_id, data.dict())


@router.get("/widgets/{widget_id}/data")
async def widget_data(widget_id: str, user=Depends(get_current_user)):
    return await get_widget_data(user.user_id, widget_id)


# ---------- Self-Expanding Agent Creation ----------

@router.get("/agent-suggestions")
async def agent_gaps(user=Depends(get_current_user)):
    return await analyze_agent_gaps(user.user_id)


@router.post("/agent-suggestions/create")
async def create_suggested(data: AutoCreateAgent, user=Depends(get_current_user)):
    return await auto_create_agent(user.user_id, data.dict())
