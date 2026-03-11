"""MAARS — Verification Civilization.
Core verification pipeline: fact check, confidence scoring, crosscheck consensus."""

import uuid
from datetime import datetime, timezone
from db import db
from governance.audit import log_action

VERIFICATION_COLLECTION = "verification_results"
CROSSCHECK_COLLECTION = "crosscheck_results"


def _now():
    return datetime.now(timezone.utc).isoformat()


def _uid():
    return str(uuid.uuid4())[:12]


async def verify_output(
    task_id: str,
    output: str,
    verification_type: str = "fact",
    verifier_agent_id: str = "system_verifier",
    context: dict = None,
    task_graph_id: str = None,
):
    """Run a single verification check on an output.
    verification_type: fact | source | hallucination | code | quantitative | compliance | financial | launch_readiness
    Returns the verification result dict."""
    context = context or {}

    # Scoring rubric — each dimension 0-10
    scores = {
        "completeness": _score_completeness(output, context),
        "correctness": _score_correctness(output, context),
        "source_grounding": _score_source_grounding(output, context),
        "actionability": _score_actionability(output, context),
        "compliance": _score_compliance(output, context),
        "professionalism": _score_professionalism(output, context),
    }

    confidence_score = round(sum(scores.values()) / len(scores), 2)
    verification_pass = confidence_score >= 6.0

    retry_rec = None
    escalation_rec = None
    if not verification_pass:
        if confidence_score >= 4.0:
            retry_rec = "retry_with_better_model"
        elif confidence_score >= 2.0:
            retry_rec = "retry_with_alternate_agent"
        else:
            retry_rec = "retry_with_more_sources"
            escalation_rec = "escalate_to_human"

    result = {
        "verification_id": _uid(),
        "task_id": task_id,
        "task_graph_id": task_graph_id,
        "verification_type": verification_type,
        "verifier_agent_id": verifier_agent_id,
        "verification_pass": verification_pass,
        "confidence_score": confidence_score,
        **scores,
        "verification_notes": _generate_notes(scores, verification_type),
        "retry_recommendation": retry_rec,
        "escalation_recommendation": escalation_rec,
        "output_preview": output[:500] if output else "",
        "created_at": _now(),
    }

    await db[VERIFICATION_COLLECTION].insert_one(result)
    await log_action(
        "verification_completed", "agent", verifier_agent_id,
        "task", task_id,
        {"type": verification_type, "pass": verification_pass, "score": confidence_score},
    )
    result.pop("_id", None)
    return result


async def crosscheck(
    task_id: str,
    verifier_ids: list = None,
    output: str = "",
    context: dict = None,
):
    """Run crosscheck verification with multiple verifier agents.
    Returns consensus result."""
    verifier_ids = verifier_ids or ["fact_verifier", "source_verifier", "hallucination_detector"]
    individual_results = []

    for vid in verifier_ids:
        vtype = vid.replace("_verifier", "").replace("_detector", "")
        r = await verify_output(task_id, output, vtype, vid, context)
        individual_results.append(r)

    scores = [r["confidence_score"] for r in individual_results]
    consensus_score = round(sum(scores) / len(scores), 2) if scores else 0
    consensus_reached = all(r["verification_pass"] == individual_results[0]["verification_pass"] for r in individual_results)
    passes = sum(1 for r in individual_results if r["verification_pass"])
    final_verdict = passes > len(individual_results) / 2

    dissenting = [
        {"verifier": r["verifier_agent_id"], "score": r["confidence_score"], "notes": r["verification_notes"]}
        for r in individual_results
        if r["verification_pass"] != final_verdict
    ]

    crosscheck_result = {
        "crosscheck_id": _uid(),
        "task_id": task_id,
        "verifier_ids": verifier_ids,
        "individual_scores": [{"verifier": r["verifier_agent_id"], "score": r["confidence_score"], "pass": r["verification_pass"]} for r in individual_results],
        "consensus_score": consensus_score,
        "consensus_reached": consensus_reached,
        "final_verdict": final_verdict,
        "dissenting_notes": dissenting,
        "created_at": _now(),
    }

    await db[CROSSCHECK_COLLECTION].insert_one(crosscheck_result)
    await log_action(
        "crosscheck_completed", "system", "crosscheck_coordinator",
        "task", task_id,
        {"verdict": final_verdict, "consensus": consensus_score, "verifiers": len(verifier_ids)},
    )
    crosscheck_result.pop("_id", None)
    return crosscheck_result


async def get_verification_results(task_id: str = None, task_graph_id: str = None, limit: int = 50):
    """Fetch verification results."""
    query = {}
    if task_id:
        query["task_id"] = task_id
    if task_graph_id:
        query["task_graph_id"] = task_graph_id
    cursor = db[VERIFICATION_COLLECTION].find(query, {"_id": 0}).sort("created_at", -1).limit(limit)
    return await cursor.to_list(length=limit)


async def get_verification_stats():
    """Aggregate verification statistics."""
    pipeline = [
        {"$group": {
            "_id": "$verification_type",
            "total": {"$sum": 1},
            "passed": {"$sum": {"$cond": ["$verification_pass", 1, 0]}},
            "avg_confidence": {"$avg": "$confidence_score"},
        }},
        {"$project": {
            "_id": 0,
            "type": "$_id",
            "total": 1,
            "passed": 1,
            "pass_rate": {"$round": [{"$divide": ["$passed", {"$max": ["$total", 1]}]}, 3]},
            "avg_confidence": {"$round": ["$avg_confidence", 2]},
        }},
    ]
    return await db[VERIFICATION_COLLECTION].aggregate(pipeline).to_list(length=20)


# --- Scoring functions (deterministic heuristics, will be LLM-enhanced in Phase 2) ---

def _score_completeness(output: str, context: dict) -> float:
    if not output:
        return 0.0
    length = len(output)
    if length < 50:
        return 3.0
    if length < 200:
        return 5.0
    if length < 1000:
        return 7.0
    return 8.5


def _score_correctness(output: str, context: dict) -> float:
    # Base score — will be LLM-verified in Phase 2
    if not output:
        return 0.0
    return 7.0  # Default baseline


def _score_source_grounding(output: str, context: dict) -> float:
    sources = context.get("sources", [])
    if not sources:
        return 4.0  # No sources provided
    return min(9.0, 5.0 + len(sources) * 0.5)


def _score_actionability(output: str, context: dict) -> float:
    action_words = ["should", "must", "recommend", "implement", "next step", "action"]
    count = sum(1 for w in action_words if w in output.lower())
    return min(9.0, 4.0 + count * 1.0)


def _score_compliance(output: str, context: dict) -> float:
    # Check for compliance red flags
    red_flags = ["confidential", "not for distribution", "internal only"]
    flags = sum(1 for f in red_flags if f in output.lower())
    return max(3.0, 8.0 - flags * 2.0)


def _score_professionalism(output: str, context: dict) -> float:
    if not output:
        return 0.0
    # Simple heuristic
    if len(output) > 100 and output[0].isupper():
        return 7.5
    return 5.0


def _generate_notes(scores: dict, vtype: str) -> str:
    weak = [k for k, v in scores.items() if v < 5.0]
    strong = [k for k, v in scores.items() if v >= 7.0]
    notes = f"Verification type: {vtype}. "
    if strong:
        notes += f"Strong: {', '.join(strong)}. "
    if weak:
        notes += f"Needs improvement: {', '.join(weak)}. "
    return notes
