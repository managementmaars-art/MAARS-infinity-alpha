"""
Platform API — the cohesive /v2/platform/* surface that ties the MAARS
subsystems (orchestrator, tools, memory, verification, governance, workers)
together for external consumers.

Every write endpoint debits the wallet via services.wallet_service and the
ledger's unique index guarantees idempotency on retries.
"""
from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from auth import get_current_user, require_admin
from models.schemas import User
from services import (
    governance_service,
    memory_facade,
    profit_engine,
    verification_service,
)
from services.agents import agent_orchestrator
from services.billing import wallet_service
from services.tools import get_tool, list_tools
from workers import task_runner

router = APIRouter()


# ---------------------------------------------------------------- orchestrator

class OrchestratorRequest(BaseModel):
    goal: str = Field(..., min_length=1, max_length=4000)
    verify: bool = True
    verify_threshold: int = Field(60, ge=0, le=100)
    max_steps: int = Field(5, ge=1, le=5)
    background: bool = False


@router.post("/v2/platform/orchestrator/run")
async def orchestrator_run(req: OrchestratorRequest, current_user: User = Depends(get_current_user)):
    if req.background:
        task = await task_runner.submit(
            kind="orchestrator.run",
            payload={
                "user_id": current_user.user_id,
                "goal": req.goal,
                "verify": req.verify,
                "verify_threshold": req.verify_threshold,
                "max_steps": req.max_steps,
            },
            user_id=current_user.user_id,
            timeout_seconds=600.0,
        )
        return {"object": "orchestrator.run", "status": "queued", "task": task}

    try:
        run = await agent_orchestrator.run(
            user_id=current_user.user_id,
            goal=req.goal,
            verify=req.verify,
            verify_threshold=req.verify_threshold,
            max_steps=req.max_steps,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    return {"object": "orchestrator.run", "run": run.to_dict()}


# ---------------------------------------------------------------- tools

@router.get("/v2/platform/tools")
async def platform_list_tools():
    return {"object": "list", "data": [t.spec() for t in list_tools()]}


class ToolCallRequest(BaseModel):
    tool: str
    args: dict[str, Any] = Field(default_factory=dict)


@router.post("/v2/platform/tools/call")
async def platform_call_tool(req: ToolCallRequest, current_user: User = Depends(get_current_user)):
    tool = get_tool(req.tool)
    if tool is None:
        raise HTTPException(status_code=404, detail=f"Unknown tool: {req.tool}")

    # Debit a small credit cost for the tool call — symmetric with inference.
    reserved = await wallet_service.reserve(
        current_user.user_id,
        tool.credit_cost,
        reference_id=f"tool:{req.tool}:{id(req)}",
        description=f"Tool call: {tool.name}",
    )
    if reserved is None:
        raise HTTPException(
            status_code=402,
            detail={"error": {"type": "insufficient_credits", "message": f"{tool.credit_cost} credit(s) required"}},
        )

    result = await tool.run(req.args)
    await wallet_service.settle(
        current_user.user_id,
        reserved_amount=tool.credit_cost,
        actual_amount=tool.credit_cost if result.ok else 0,
        reference_id=f"tool:{req.tool}:{id(req)}",
        description=f"Tool {tool.name} {'ok' if result.ok else 'failed'}",
    )
    return {
        "object": "tool.result",
        "tool": tool.name,
        "ok": result.ok,
        "data": result.data,
        "error": result.error,
        "latency_ms": result.latency_ms,
        "credits_used": tool.credit_cost if result.ok else 0,
    }


# ---------------------------------------------------------------- memory

class MemoryWriteRequest(BaseModel):
    key: str
    value: Any
    tier: str = "episodic"
    session_id: Optional[str] = None
    tags: list[str] = Field(default_factory=list)


@router.post("/v2/platform/memory")
async def memory_write(req: MemoryWriteRequest, current_user: User = Depends(get_current_user)):
    try:
        rec = await memory_facade.remember(
            user_id=current_user.user_id,
            key=req.key, value=req.value, tier=req.tier,
            session_id=req.session_id, tags=req.tags,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"object": "memory.record", **rec}


@router.get("/v2/platform/memory")
async def memory_read(
    query: str = Query(""),
    session_id: Optional[str] = None,
    tier: Optional[str] = None,
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
):
    records = await memory_facade.recall(
        user_id=current_user.user_id, query=query,
        session_id=session_id, tier=tier, limit=limit,
    )
    return {"object": "list", "data": records}


# ---------------------------------------------------------------- verification

class VerifyRequest(BaseModel):
    prompt: str
    response: str
    context: str = ""
    confidence_threshold: int = Field(60, ge=0, le=100)
    correct: bool = False


@router.post("/v2/platform/verify")
async def platform_verify(req: VerifyRequest, current_user: User = Depends(get_current_user)):
    reserved = await wallet_service.reserve(
        current_user.user_id, 1,
        reference_id=f"verify:{id(req)}",
        description="Verification call",
    )
    if reserved is None:
        raise HTTPException(status_code=402, detail="Insufficient credits for verification (1 required)")

    result = await verification_service.verify(
        prompt=req.prompt, response=req.response, context=req.context,
        confidence_threshold=req.confidence_threshold, correct=req.correct,
    )
    await wallet_service.settle(
        current_user.user_id, reserved_amount=1, actual_amount=1,
        reference_id=f"verify:{id(req)}",
        description="Verification settled",
    )
    return {"object": "verification.result", **result.to_dict()}


# ---------------------------------------------------------------- governance

class PolicyCheckRequest(BaseModel):
    messages: list[dict[str, Any]]
    max_tokens: Optional[int] = None
    estimated_credits: int = 0


@router.post("/v2/platform/governance/check")
async def platform_governance_check(req: PolicyCheckRequest, current_user: User = Depends(get_current_user)):
    decision = governance_service.check_request(
        user_id=current_user.user_id,
        messages=req.messages,
        requested_max_tokens=req.max_tokens,
        estimated_credits=req.estimated_credits,
    )
    return {"object": "governance.decision", **decision.to_dict()}


# ---------------------------------------------------------------- profit

class ProfitDecideRequest(BaseModel):
    credits_remaining: int
    estimated_credits: int
    estimated_cost_usd: float
    requested_tier: str = "standard"


@router.post("/v2/platform/profit/decide")
async def platform_profit_decide(req: ProfitDecideRequest, current_user: User = Depends(get_current_user)):
    decision = profit_engine.decide(
        credits_remaining=req.credits_remaining,
        estimated_credits=req.estimated_credits,
        estimated_cost_usd=req.estimated_cost_usd,
        requested_tier=req.requested_tier,
    )
    return {"object": "profit.decision", **decision.to_dict()}


# ---------------------------------------------------------------- workers

@router.get("/v2/platform/tasks/{task_id}")
async def get_task(task_id: str, current_user: User = Depends(get_current_user)):
    task = await task_runner.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    # Let admins inspect any task; users only their own.
    if not getattr(current_user, "is_admin", False) and task.get("user_id") != current_user.user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return task


@router.get("/v2/platform/tasks")
async def list_user_tasks(
    status: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500),
    current_user: User = Depends(get_current_user),
):
    tasks = await task_runner.list_tasks(user_id=current_user.user_id, status=status, limit=limit)
    return {"object": "list", "data": tasks}


@router.get("/v2/platform/admin/tasks")
async def admin_list_tasks(
    status: Optional[str] = None,
    limit: int = Query(200, ge=1, le=1000),
    _: User = Depends(require_admin),
):
    tasks = await task_runner.list_tasks(status=status, limit=limit)
    return {"object": "list", "data": tasks}
