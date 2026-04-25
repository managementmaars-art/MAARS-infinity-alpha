"""Agent-powered failure diagnosis — when a workflow node errors, hand
the error + upstream context to an LLM and ask it to propose a concrete
fix (either a new node config or an inserted repair step).

Not in the hot path — called by the admin endpoint when operator clicks
"Diagnose" on a failed run. Never auto-applies suggestions; operator
reviews and decides.

Output shape the UI expects:
  {
    summary:   "one-line diagnosis",
    root_cause: "why it failed",
    proposed_fix: {
      kind:    "param_patch" | "insert_repair" | "swap_tool" | "retry_with_backoff",
      target_node_id: "...",
      patch:   { ... }        # kind-specific
    },
    confidence: 0..1,
  }
"""
from __future__ import annotations
import json
import logging
import re
from typing import Any

logger = logging.getLogger(__name__)


async def diagnose_run(run_id: str, user_id: str) -> dict[str, Any]:
    from db import db
    run = await db.workflow_runs.find_one({"run_id": run_id}, {"_id": 0})
    if not run:
        raise ValueError("run_not_found")
    if run.get("status") != "failed":
        return {"summary": "run did not fail — nothing to diagnose",
                "root_cause": None, "proposed_fix": None, "confidence": 0.0}
    workflow = await db.workflows.find_one({"workflow_id": run["workflow_id"]}, {"_id": 0})
    if not workflow:
        raise ValueError("workflow_not_found")

    failed_node_id = run.get("failed_node")
    error = run.get("error") or ""
    state = run.get("state") or {}
    nodes = workflow.get("nodes") or []
    failed_node = next((n for n in nodes if n.get("id") == failed_node_id), None)

    # Collect context on the failed node's immediate parents
    parents = []
    for n in nodes:
        downstream = set()
        for t in (n.get("next") or []):
            downstream.add(t)
        for t in (n.get("branch_yes") or []):
            downstream.add(t)
        for t in (n.get("branch_no") or []):
            downstream.add(t)
        for tlist in (n.get("branches") or {}).values():
            for t in (tlist or []):
                downstream.add(t)
        if failed_node_id in downstream:
            parents.append(n)

    parent_outputs = {p["id"]: state.get(p["id"]) for p in parents}

    prompt = (
        f"A workflow node failed. Propose ONE concrete fix.\n\n"
        f"WORKFLOW: {workflow.get('name','')} — {workflow.get('description','')[:300]}\n"
        f"FAILED NODE: {json.dumps(failed_node, default=str)[:2000] if failed_node else failed_node_id}\n"
        f"ERROR: {error[:800]}\n"
        f"PARENT OUTPUTS: {json.dumps(parent_outputs, default=str)[:2000]}\n\n"
        "Reply ONLY with compact JSON in this schema:\n"
        '{"summary": "<one sentence>", "root_cause": "<why it failed>", '
        '"proposed_fix": {"kind": "param_patch"|"insert_repair"|"swap_tool"|"retry_with_backoff", '
        '"target_node_id": "<id>", "patch": <object>}, "confidence": 0.0-1.0}\n\n'
        "Kinds:\n"
        "  param_patch: patch is a dict merged into node.params\n"
        "  insert_repair: patch is a NEW node dict to insert before the failed one\n"
        "  swap_tool: patch is {new_tool: \"...\", params: {...}}\n"
        "  retry_with_backoff: patch is {retries: N, backoff_s: N}\n"
    )

    from services.llm_gateway import complete_text
    raw = await complete_text(
        user_id,
        system_prompt=(
            "You are Commander Orion ∞, diagnosing a failed MAARS workflow run. "
            "Terse, accurate, evidence-based. Never guess; if uncertain, lower confidence."
        ),
        user_prompt=prompt,
        model="maars/auto",
        max_tokens=800, temperature=0.1,
        source="workflow_diagnose",
        agent_id="agent_commander",
    )
    m = re.search(r"\{[\s\S]*\}", raw or "")
    try:
        out = json.loads(m.group(0)) if m else {}
    except Exception:
        out = {}
    return {
        "summary":      out.get("summary") or "diagnosis_unavailable",
        "root_cause":   out.get("root_cause"),
        "proposed_fix": out.get("proposed_fix"),
        "confidence":   float(out.get("confidence") or 0.5),
        "run_id":       run_id,
        "failed_node":  failed_node_id,
    }
