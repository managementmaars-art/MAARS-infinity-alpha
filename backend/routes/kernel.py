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
