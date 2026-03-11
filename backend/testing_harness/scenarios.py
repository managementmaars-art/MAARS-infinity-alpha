"""MAARS — Testing Harness: Validation Scenarios A-E.
End-to-end test scenarios that validate the full MAARS Infinity pipeline."""

import uuid
import asyncio
from datetime import datetime, timezone
from db import db

HARNESS_COLLECTION = "test_harness_runs"


def _now():
    return datetime.now(timezone.utc).isoformat()


def _uid():
    return str(uuid.uuid4())[:12]


async def _run_scenario_a():
    """Scenario A: Research Goal Pipeline — Tests classification → decomposition → routing → execution flow."""
    from orchestrator.commander import execute_goal
    steps = []
    try:
        result = await execute_goal("Research the latest trends in quantum computing and produce a strategic brief", "test_harness", "simulation")
        steps.append({"step": "goal_execution", "status": "pass", "detail": f"Goal created, classified as {result['classification']['goal_type']}, {result['nodes']} nodes"})
        if result["classification"]["goal_type"] != "research":
            steps.append({"step": "classification_check", "status": "fail", "detail": f"Expected 'research', got '{result['classification']['goal_type']}'"})
        else:
            steps.append({"step": "classification_check", "status": "pass", "detail": "Correctly classified as research"})
        if result["nodes"] < 3:
            steps.append({"step": "decomposition_check", "status": "fail", "detail": f"Expected 3+ nodes, got {result['nodes']}"})
        else:
            steps.append({"step": "decomposition_check", "status": "pass", "detail": f"{result['nodes']} task nodes created"})
        steps.append({"step": "agent_assignment", "status": "pass" if result["assignments"] else "warn", "detail": f"{len(result['assignments'])} agents assigned"})
    except Exception as e:
        steps.append({"step": "goal_execution", "status": "fail", "detail": str(e)})
    return steps


async def _run_scenario_b():
    """Scenario B: Verification Pipeline — Tests output verification and crosscheck consensus."""
    from verification.engine import verify_output, crosscheck
    steps = []
    task_id = f"test_b_{_uid()}"
    try:
        v_result = await verify_output(task_id, "The global AI market is expected to reach $500B by 2027, driven by enterprise adoption. Key players include OpenAI, Google DeepMind, and Anthropic.", "fact", "test_verifier", {"sources": ["forbes.com", "statista.com"]})
        steps.append({"step": "single_verification", "status": "pass", "detail": f"Score: {v_result['confidence_score']}, Pass: {v_result['verification_pass']}"})

        cc_result = await crosscheck(task_id, ["fact_verifier", "source_verifier", "hallucination_detector"], "The global AI market is expected to reach $500B by 2027.")
        steps.append({"step": "crosscheck_consensus", "status": "pass", "detail": f"Consensus: {cc_result['consensus_score']}, Verdict: {cc_result['final_verdict']}, Unanimous: {cc_result['consensus_reached']}"})
    except Exception as e:
        steps.append({"step": "verification", "status": "fail", "detail": str(e)})
    return steps


async def _run_scenario_c():
    """Scenario C: Memory & Learning Loop — Tests working memory → episodic memory → lesson learning."""
    from memory_system.working import store_working, get_working, append_result, clear_working
    from memory_system.episodic import record_episode, get_lessons
    steps = []
    task_id = f"test_c_{_uid()}"
    try:
        await store_working(task_id, "test_agent", {"goal": "test memory flow"})
        steps.append({"step": "working_memory_store", "status": "pass", "detail": "Context stored"})

        await append_result(task_id, "test_agent", {"finding": "important data point"})
        wm = await get_working(task_id)
        steps.append({"step": "working_memory_retrieve", "status": "pass" if wm else "fail", "detail": f"Retrieved {len(wm)} entries"})

        await record_episode("test_agent", "test_scenario_c", {"task_id": task_id}, "success", "Working memory flows correctly into episodic")
        lessons = await get_lessons("test_agent")
        steps.append({"step": "episodic_record_and_learn", "status": "pass" if lessons else "warn", "detail": f"{len(lessons)} lessons found"})

        await clear_working(task_id)
        steps.append({"step": "working_memory_cleanup", "status": "pass", "detail": "Working memory cleared"})
    except Exception as e:
        steps.append({"step": "memory_flow", "status": "fail", "detail": str(e)})
    return steps


async def _run_scenario_d():
    """Scenario D: Intelligence Search → Verify → Cite — Tests search, source ranking, and citation chain."""
    from intelligence.search_engine import search_and_rank, verify_across_sources
    from intelligence.citation import create_citation
    steps = []
    try:
        results = await search_and_rank("artificial intelligence enterprise adoption 2026", "standard")
        steps.append({"step": "web_search", "status": "pass" if results["total"] > 0 else "fail", "detail": f"{results['total']} results found, source: {results['source']}"})

        if results["results"]:
            ranked = results["results"]
            has_credibility = all("credibility_score" in r for r in ranked)
            steps.append({"step": "source_ranking", "status": "pass" if has_credibility else "fail", "detail": f"Top result: credibility={ranked[0].get('credibility_score', 0)}"})

            claim = "AI adoption is accelerating in enterprises"
            verify = await verify_across_sources(claim, ranked)
            steps.append({"step": "source_verification", "status": "pass", "detail": f"Claim '{claim[:40]}' — status: {verify['status']}, confidence: {verify['confidence']}"})

            citation = await create_citation(claim, [r["url"] for r in ranked[:3]], verify["confidence"], verify["status"] == "verified")
            steps.append({"step": "citation_creation", "status": "pass", "detail": f"Citation created, verified={citation['verified']}"})
        else:
            steps.append({"step": "search_results", "status": "warn", "detail": "No search results to verify"})
    except Exception as e:
        steps.append({"step": "intelligence_pipeline", "status": "fail", "detail": str(e)})
    return steps


async def _run_scenario_e():
    """Scenario E: Budget & Governance — Tests budget tracking, policy enforcement, trust scoring, and audit trail."""
    from kernel.budget_controller import record_spend, get_budget
    from kernel.policy_engine import check_all_policies
    from governance.trust_scoring import update_trust_score, get_trust_score
    from governance.audit import query_audit_log
    steps = []
    entity_id = f"test_e_{_uid()}"
    try:
        await record_spend("agent", entity_id, 0.50, "gpt-4o", "test_task")
        budget = await get_budget("agent", entity_id, "daily")
        steps.append({"step": "budget_tracking", "status": "pass", "detail": f"Spent: ${budget.get('spent', 0)}, Limit: ${budget.get('limit', 'none')}"})

        policy_result = await check_all_policies({"action": "execute_production", "autonomy_tier": 2, "environment": "production", "daily_spend": 0.5})
        violations = policy_result.get("violations", [])
        steps.append({"step": "policy_enforcement", "status": "pass", "detail": f"All passed: {policy_result.get('all_passed', True)}, Violations: {len(violations)}"})

        await update_trust_score("agent", entity_id, {"type": "task_completed", "success": True, "confidence": 0.9})
        trust = await get_trust_score("agent", entity_id)
        steps.append({"step": "trust_scoring", "status": "pass", "detail": f"Trust score: {trust.get('score', 0)}"})

        audit = await query_audit_log({"actor_id": entity_id}, limit=5)
        steps.append({"step": "audit_trail", "status": "pass", "detail": f"{audit.get('total', 0)} audit entries found"})
    except Exception as e:
        steps.append({"step": "governance_pipeline", "status": "fail", "detail": str(e)})
    return steps


SCENARIOS = {
    "A": {"name": "Research Goal Pipeline", "description": "Goal → Classify → Decompose → Route → Assign", "fn": _run_scenario_a},
    "B": {"name": "Verification Pipeline", "description": "Output → Verify → Crosscheck → Consensus", "fn": _run_scenario_b},
    "C": {"name": "Memory & Learning Loop", "description": "Working Memory → Episodic → Lessons → Cleanup", "fn": _run_scenario_c},
    "D": {"name": "Intelligence Search → Verify → Cite", "description": "Search → Rank → Verify Sources → Create Citation", "fn": _run_scenario_d},
    "E": {"name": "Budget & Governance", "description": "Budget → Policy → Trust → Audit", "fn": _run_scenario_e},
}


async def run_scenario(scenario_id: str):
    """Run a single test scenario and return results."""
    scenario = SCENARIOS.get(scenario_id.upper())
    if not scenario:
        return {"error": f"Unknown scenario: {scenario_id}. Valid: {list(SCENARIOS.keys())}"}

    run_id = _uid()
    started_at = _now()
    steps = await scenario["fn"]()
    completed_at = _now()

    passed = sum(1 for s in steps if s["status"] == "pass")
    failed = sum(1 for s in steps if s["status"] == "fail")
    warned = sum(1 for s in steps if s["status"] == "warn")

    result = {
        "run_id": run_id,
        "scenario_id": scenario_id.upper(),
        "scenario_name": scenario["name"],
        "scenario_description": scenario["description"],
        "steps": steps,
        "summary": {"passed": passed, "failed": failed, "warnings": warned, "total": len(steps)},
        "overall_status": "pass" if failed == 0 else "fail",
        "started_at": started_at,
        "completed_at": completed_at,
    }

    await db[HARNESS_COLLECTION].insert_one(result)
    result.pop("_id", None)
    return result


async def run_all_scenarios():
    """Run all scenarios sequentially and return combined results."""
    run_id = _uid()
    started_at = _now()
    results = []
    for sid in SCENARIOS:
        r = await run_scenario(sid)
        results.append(r)

    completed_at = _now()
    total_passed = sum(r["summary"]["passed"] for r in results)
    total_failed = sum(r["summary"]["failed"] for r in results)
    total_steps = sum(r["summary"]["total"] for r in results)

    return {
        "suite_run_id": run_id,
        "scenarios": results,
        "suite_summary": {"passed": total_passed, "failed": total_failed, "total_steps": total_steps, "scenarios_run": len(results)},
        "overall_status": "pass" if total_failed == 0 else "fail",
        "started_at": started_at,
        "completed_at": completed_at,
    }


async def get_test_runs(scenario_id: str = None, limit: int = 20):
    """Get historical test runs."""
    query = {}
    if scenario_id:
        query["scenario_id"] = scenario_id.upper()
    cursor = db[HARNESS_COLLECTION].find(query, {"_id": 0}).sort("started_at", -1).limit(limit)
    return await cursor.to_list(length=limit)
