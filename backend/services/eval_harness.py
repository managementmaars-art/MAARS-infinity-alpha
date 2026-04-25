"""LLM-judge regression harness.

Problem this solves: when a provider's model ID changes (Gemini flash →
flash-2.0, Anthropic claude-opus → opus-4.1, Groq swaps a slug), the
router silently routes to the new version. Nothing measures whether
the new version is as good as the old one — until a client complains.

This module replays a curated **golden dataset** of (query, expected
shape) through each candidate provider/model on a schedule. An LLM
judge scores each completion on named dimensions, and the result feeds
back into `provider_scorecard` so the bandit router benches providers
that drop below threshold.

Dataset shape (in Mongo `eval_golden_set`):
    {
      item_id:   "ge_001",
      prompt:    "Summarize the key points of this text: ...",
      task:      "summarization" | "reasoning" | "code" | "extraction",
      reference: "expected ideal answer" (optional — used when available),
      rubric:    ["correctness", "coherence", "completeness"] (dimensions),
      created_at, updated_by
    }

Run shape (in Mongo `eval_runs`):
    {
      run_id:   "evr_...",
      started_at, finished_at,
      models:   ["openai/gpt-4.1", "gemini/gemini-2.5-flash", ...],
      judge_model: "openai/gpt-4o-mini",
      scores: {
        "<model>": {
          "<item_id>": {"per_dim": {"correctness": 0.9, ...}, "mean": 0.85, "passed": True},
        }
      },
      summary: {
        "<model>": {"mean": 0.82, "pass_rate": 0.91, "sample_size": 40}
      }
    }

Public API:
    add_golden(item)
    list_golden(task=None)
    run_eval(models, judge_model=None, pass_threshold=0.7)
    summary(run_id)
    latest_per_model()
"""
from __future__ import annotations
import asyncio
import json
import logging
import re
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

logger = logging.getLogger(__name__)

DEFAULT_JUDGE_MODEL = "maars/auto"  # router picks a cheap capable model
DEFAULT_PASS_THRESHOLD = 0.7       # Opik's standard
RUBRIC_DEFAULT = ["correctness", "coherence", "completeness"]


async def add_golden(
    *, prompt: str, task: str = "general",
    reference: str | None = None, rubric: list[str] | None = None,
    updated_by: str = "system",
) -> dict[str, Any]:
    """Append a golden-set item. Idempotent on (prompt, task) pair."""
    from db import db
    now = datetime.now(timezone.utc).isoformat()
    item = {
        "item_id":    f"ge_{uuid.uuid4().hex[:10]}",
        "prompt":     prompt.strip(),
        "task":       task,
        "reference":  (reference or "").strip() or None,
        "rubric":     rubric or RUBRIC_DEFAULT,
        "updated_by": updated_by,
        "created_at": now,
    }
    await db.eval_golden_set.update_one(
        {"prompt": item["prompt"], "task": task},
        {"$setOnInsert": item},
        upsert=True,
    )
    return item


async def list_golden(task: str | None = None, limit: int = 500) -> list[dict]:
    from db import db
    q: dict[str, Any] = {}
    if task:
        q["task"] = task
    cursor = db.eval_golden_set.find(q, {"_id": 0}).sort("created_at", -1).limit(limit)
    return await cursor.to_list(length=limit)


async def _score_completion(
    user_id: str, judge_model: str, prompt: str, completion: str,
    rubric: list[str], reference: str | None,
) -> dict[str, Any]:
    """LLM-judge a single completion against a rubric. Returns
    {per_dim: {dim: 0-1}, mean, reasoning}."""
    from services.llm_gateway import complete_text
    ref_block = f"\n\nREFERENCE ANSWER (for comparison):\n{reference}" if reference else ""
    instr = (
        "You are a strict evaluator. Score the completion on each dimension "
        "from 0.0 (terrible) to 1.0 (perfect). Reply ONLY with JSON:\n"
        '{"scores": {"<dim>": <float>}, "reasoning": "<1 sentence>"}'
        f"\n\nDIMENSIONS TO SCORE: {', '.join(rubric)}\n\n"
        f"PROMPT:\n{prompt}\n\n"
        f"COMPLETION:\n{completion}{ref_block}"
    )
    raw = await complete_text(
        user_id,
        system_prompt="You produce strict JSON only.",
        user_prompt=instr,
        model=judge_model,
        max_tokens=400, temperature=0.0,
        source="eval_harness.judge",
        enable_cache=False,
    )
    m = re.search(r"\{[\s\S]*\}", raw or "")
    if not m:
        return {"per_dim": {d: 0.0 for d in rubric}, "mean": 0.0,
                "reasoning": "judge_parse_failed", "raw": raw[:200] if raw else ""}
    try:
        parsed = json.loads(m.group(0))
    except Exception as exc:
        return {"per_dim": {d: 0.0 for d in rubric}, "mean": 0.0,
                "reasoning": f"json_error: {exc}"}
    dim_scores = parsed.get("scores") or {}
    per_dim = {}
    for d in rubric:
        v = dim_scores.get(d)
        try:
            per_dim[d] = max(0.0, min(1.0, float(v)))
        except (TypeError, ValueError):
            per_dim[d] = 0.0
    mean = sum(per_dim.values()) / len(per_dim) if per_dim else 0.0
    return {"per_dim": per_dim, "mean": round(mean, 3),
            "reasoning": (parsed.get("reasoning") or "")[:200]}


async def run_eval(
    *, models: list[str], user_id: str,
    judge_model: str = DEFAULT_JUDGE_MODEL,
    pass_threshold: float = DEFAULT_PASS_THRESHOLD,
    task: str | None = None, limit: int = 40,
) -> dict[str, Any]:
    """Replay the golden set through each candidate model and judge."""
    from db import db
    from services.llm_gateway import complete_text
    run_id = f"evr_{uuid.uuid4().hex[:10]}"
    started = datetime.now(timezone.utc).isoformat()
    goldens = await list_golden(task=task, limit=limit)
    if not goldens:
        return {"ok": False, "error": "no_golden_set_items"}

    scores_by_model: dict[str, dict[str, Any]] = {m: {} for m in models}
    # One parallel task per (model, golden) tuple keeps wall-clock low
    sem = asyncio.Semaphore(6)  # avoid blowing rate limits

    async def _one(model: str, item: dict):
        async with sem:
            try:
                completion = await complete_text(
                    user_id, system_prompt="", user_prompt=item["prompt"],
                    model=model, max_tokens=800, temperature=0.2,
                    source=f"eval_harness.replay:{model}",
                    enable_cache=False,
                )
            except Exception as exc:
                scores_by_model[model][item["item_id"]] = {
                    "per_dim": {d: 0.0 for d in (item.get("rubric") or RUBRIC_DEFAULT)},
                    "mean": 0.0, "error": f"{type(exc).__name__}: {exc}",
                    "passed": False,
                }
                return
            judged = await _score_completion(
                user_id, judge_model,
                prompt=item["prompt"], completion=completion,
                rubric=item.get("rubric") or RUBRIC_DEFAULT,
                reference=item.get("reference"),
            )
            judged["completion"] = completion[:1500]
            judged["passed"] = judged["mean"] >= pass_threshold
            scores_by_model[model][item["item_id"]] = judged

    tasks = [_one(m, g) for m in models for g in goldens]
    await asyncio.gather(*tasks)

    # Summarize per model
    summary: dict[str, Any] = {}
    for m in models:
        results = list(scores_by_model[m].values())
        n = len(results)
        mean = sum(r["mean"] for r in results) / n if n else 0.0
        passed = sum(1 for r in results if r.get("passed")) / n if n else 0.0
        summary[m] = {
            "mean":       round(mean, 3),
            "pass_rate":  round(passed, 3),
            "sample_size": n,
            "benched":    mean < pass_threshold,
        }

    finished = datetime.now(timezone.utc).isoformat()
    doc = {
        "run_id":        run_id,
        "started_at":    started,
        "finished_at":   finished,
        "models":        models,
        "judge_model":   judge_model,
        "pass_threshold": pass_threshold,
        "task":          task,
        "sample_size":   len(goldens),
        "scores":        scores_by_model,
        "summary":       summary,
    }
    await db.eval_runs.insert_one(doc)
    # Feed benched decisions back into the scorecard so the bandit router
    # stops picking a regressed model on next call.
    try:
        from services import provider_scorecard
        for m, s in summary.items():
            await provider_scorecard.record_eval_score(
                model=m, mean_score=s["mean"], pass_rate=s["pass_rate"],
                sample_size=s["sample_size"],
            )
    except Exception as exc:
        logger.info("scorecard feedback skipped: %s", exc)
    doc.pop("_id", None)
    return doc


async def summary(run_id: str) -> dict[str, Any] | None:
    from db import db
    return await db.eval_runs.find_one({"run_id": run_id}, {"_id": 0})


async def latest_per_model() -> dict[str, Any]:
    """Most-recent eval summary for each model. Feeds the admin UI."""
    from db import db
    latest = await db.eval_runs.find_one({}, {"_id": 0}, sort=[("finished_at", -1)])
    return (latest or {}).get("summary") or {}
