"""
Multi-agent orchestrator — planner → executor → verifier.

Given a user goal, runs three phases:
    PLAN     — a planner model decomposes the goal into 2-5 concrete steps.
    EXECUTE  — an executor model works each step, optionally invoking tools
               from services/tools/. Step outputs are accumulated in working
               context for subsequent steps.
    VERIFY   — services/verification_service.verify reviews the final output.

Wallet / ledger integration: each phase emits a wallet reserve+settle via
services.wallet_service using the run_id as the reference. This means the
run appears in the user's usage ledger with exact cost attribution.

This orchestrator is intentionally simple — no DAGs, no parallel branches,
no resumption. It targets the common case of "take a goal, work it,
verify it, return the answer." Complex flows still belong in the existing
backend/kernel + backend/orchestrator/commander.
"""
from __future__ import annotations

import json
import logging
import re
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Optional

from services.billing import wallet_service
from services.providers import get_provider
from services.tools import get_tool, list_tools
from services.verification_service import verify as verify_response

logger = logging.getLogger(__name__)

DEFAULT_PLANNER = ("groq", "llama-3.3-70b-versatile")
DEFAULT_EXECUTOR = ("groq", "llama-3.3-70b-versatile")

PLANNER_COST_CREDITS = 2
STEP_COST_CREDITS = 2
VERIFIER_COST_CREDITS = 1

_PLAN_SYSTEM = """You are a planning agent. Given a user goal, produce a JSON plan of 2-5 steps. \
Each step has: title, action (reason|tool_call), optional tool (one of: web_search, http_fetch, \
code_executor, db_query), and a brief description. Return ONLY JSON matching:
{
  "steps": [
    {"title": "...", "action": "reason"|"tool_call", "tool": "...", "description": "..."}
  ]
}
"""

_EXEC_SYSTEM = """You are an execution agent. You receive a plan step, the user's goal, and \
accumulated prior results. Produce the most useful concise output for this step. \
If the step calls for a tool, you can reference its data; otherwise reason directly."""


# --------------------------------------------------------------------------- data shapes

@dataclass
class StepResult:
    title: str
    action: str
    tool: Optional[str]
    tool_result: Optional[dict[str, Any]]
    output: str
    latency_ms: int
    credits_used: int


@dataclass
class OrchestratorRun:
    run_id: str
    user_id: str
    goal: str
    plan: list[dict[str, Any]]
    steps: list[StepResult]
    final_answer: str
    verification: Optional[dict[str, Any]]
    total_credits: int
    total_latency_ms: int
    started_at: float
    ended_at: float
    status: str
    error: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "user_id": self.user_id,
            "goal": self.goal,
            "plan": self.plan,
            "steps": [s.__dict__ for s in self.steps],
            "final_answer": self.final_answer,
            "verification": self.verification,
            "total_credits": self.total_credits,
            "total_latency_ms": self.total_latency_ms,
            "status": self.status,
            "error": self.error,
        }


# --------------------------------------------------------------------------- helpers

def _first_json(text: str) -> Optional[dict[str, Any]]:
    if not text:
        return None
    m = re.search(r"\{[\s\S]*\}", text)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except Exception:
        return None


async def _llm_call(provider: str, model: str, messages: list[dict[str, Any]]) -> str:
    p = get_provider(provider)
    if p is None or not p.available:
        raise RuntimeError(f"provider {provider} unavailable for orchestrator")
    resp = await p.execute_chat_completion(model=model, messages=messages)
    return (resp.get("choices") or [{}])[0].get("message", {}).get("content", "")


async def _charge(user_id: str, amount: int, *, run_id: str, phase: str) -> None:
    """Reserve + immediately settle a per-phase cost. No refund path — phase already ran."""
    reserved = await wallet_service.reserve(
        user_id, amount, reference_id=f"{run_id}:{phase}",
        description=f"Agent {phase} step for run {run_id}",
    )
    if reserved is None:
        raise RuntimeError(f"insufficient credits for orchestrator phase '{phase}'")
    await wallet_service.settle(
        user_id, reserved_amount=amount, actual_amount=amount,
        reference_id=f"{run_id}:{phase}",
        description=f"Agent {phase} settled",
    )


# --------------------------------------------------------------------------- public API

async def run(
    *,
    user_id: str,
    goal: str,
    verify: bool = True,
    verify_threshold: int = 60,
    max_steps: int = 5,
    planner: tuple[str, str] = DEFAULT_PLANNER,
    executor: tuple[str, str] = DEFAULT_EXECUTOR,
) -> OrchestratorRun:
    """Execute a planner→executor→verifier cycle for `goal`. Blocks until complete."""
    run_id = f"orc_{uuid.uuid4().hex[:16]}"
    started = time.time()
    run_obj = OrchestratorRun(
        run_id=run_id, user_id=user_id, goal=goal,
        plan=[], steps=[], final_answer="", verification=None,
        total_credits=0, total_latency_ms=0,
        started_at=started, ended_at=started, status="running",
    )

    try:
        # ── PLAN ──────────────────────────────────────────────────────
        await _charge(user_id, PLANNER_COST_CREDITS, run_id=run_id, phase="plan")
        run_obj.total_credits += PLANNER_COST_CREDITS

        t0 = time.time()
        plan_text = await _llm_call(planner[0], planner[1], [
            {"role": "system", "content": _PLAN_SYSTEM},
            {"role": "user", "content": f"Goal: {goal}\n\nAvailable tools: " +
                                        ", ".join(t.name for t in list_tools())},
        ])
        plan_json = _first_json(plan_text) or {}
        steps = plan_json.get("steps") or []
        if not isinstance(steps, list) or not steps:
            # Fallback: single reason step using the raw goal.
            steps = [{"title": "Answer the goal directly", "action": "reason",
                      "description": goal}]
        steps = steps[: int(max_steps)]
        run_obj.plan = steps
        plan_latency = int((time.time() - t0) * 1000)

        # ── EXECUTE ───────────────────────────────────────────────────
        accumulated: list[str] = []
        for i, step in enumerate(steps):
            await _charge(user_id, STEP_COST_CREDITS, run_id=run_id, phase=f"step_{i}")
            run_obj.total_credits += STEP_COST_CREDITS

            t_step = time.time()
            tool_name = step.get("tool") if step.get("action") == "tool_call" else None
            tool_result: Optional[dict[str, Any]] = None
            if tool_name:
                tool = get_tool(tool_name)
                if tool is not None:
                    # Ask the executor to produce the tool arguments given the step.
                    arg_text = await _llm_call(executor[0], executor[1], [
                        {"role": "system", "content":
                            f"Output ONLY a JSON object for the arguments to the `{tool_name}` tool. "
                            f"Schema: {json.dumps(tool.argument_schema)}"},
                        {"role": "user", "content":
                            f"Step: {step.get('title')} — {step.get('description')}\n"
                            f"Goal: {goal}"},
                    ])
                    args = _first_json(arg_text) or {}
                    raw = await tool.run(args)
                    tool_result = {
                        "ok": raw.ok, "data": raw.data, "error": raw.error,
                        "latency_ms": raw.latency_ms, "metadata": raw.metadata,
                    }

            exec_messages = [
                {"role": "system", "content": _EXEC_SYSTEM},
                {"role": "user", "content":
                    f"Goal:\n{goal}\n\n"
                    f"Step {i+1}: {step.get('title')}\n{step.get('description')}\n\n"
                    + (f"Tool `{tool_name}` result:\n{json.dumps(tool_result)[:4000]}\n\n"
                       if tool_result else "")
                    + (f"Prior step outputs:\n" + "\n\n".join(accumulated) + "\n\n"
                       if accumulated else "")
                    + "Produce your output for this step:"},
            ]
            output = await _llm_call(executor[0], executor[1], exec_messages)
            accumulated.append(f"[{step.get('title')}]\n{output}")
            run_obj.steps.append(StepResult(
                title=step.get("title", f"step-{i+1}"),
                action=step.get("action", "reason"),
                tool=tool_name,
                tool_result=tool_result,
                output=output,
                latency_ms=int((time.time() - t_step) * 1000),
                credits_used=STEP_COST_CREDITS,
            ))

        # ── FINAL ASSEMBLY + VERIFY ──────────────────────────────────
        run_obj.final_answer = accumulated[-1] if accumulated else ""
        if verify and run_obj.final_answer:
            await _charge(user_id, VERIFIER_COST_CREDITS, run_id=run_id, phase="verify")
            run_obj.total_credits += VERIFIER_COST_CREDITS
            vres = await verify_response(
                prompt=goal,
                response=run_obj.final_answer,
                context="\n\n".join(accumulated[:-1]) if len(accumulated) > 1 else "",
                confidence_threshold=verify_threshold,
                correct=False,
            )
            run_obj.verification = vres.to_dict()

        run_obj.status = "complete"
        run_obj.total_latency_ms = plan_latency + sum(s.latency_ms for s in run_obj.steps)
    except Exception as exc:
        run_obj.status = "error"
        run_obj.error = f"{type(exc).__name__}: {exc}"
        logger.exception("orchestrator run %s failed", run_id)

    run_obj.ended_at = time.time()
    run_obj.total_latency_ms = int((run_obj.ended_at - run_obj.started_at) * 1000)

    # Persist the run for admin visibility / audit.
    try:
        from db import db
        await db.orchestrator_runs.insert_one(run_obj.to_dict())
    except Exception as exc:
        logger.warning("failed to persist orchestrator run %s: %s", run_id, exc)

    return run_obj
