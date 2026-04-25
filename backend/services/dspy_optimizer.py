"""DSPy-style reflection prompt optimizer.

Stanford DSPy (Khattab et al. 2023) treats prompts as parameters to
optimize. Given (input, expected output) pairs, it automatically
rewrites the prompt using gradient-free search: sample candidate
prompts, score each via the LLM-judge, keep the winner.

We implement the simpler "reflect and rewrite" variant:
  1. Start with caller's seed prompt + a few input/output examples.
  2. Ask a critic model "what does this prompt fail at?"
  3. Ask a writer model "rewrite the prompt to fix those failures."
  4. Evaluate candidate on held-out examples with llm_judge.
  5. Keep if it beats baseline by >= threshold.

Typical use: admin ingests a new system prompt via
/admin/prompts/optimize; we run 3 rounds and save the final revision
in `optimized_prompts` collection, keyed by the original hash. Future
calls to `get_optimized(original)` return the improved version.

Output lives in Mongo so it survives restarts and is auditable.
"""
from __future__ import annotations
import hashlib
import logging
from dataclasses import dataclass
from typing import Any, Awaitable, Callable

logger = logging.getLogger(__name__)


_REFLECT_SYSTEM = (
    "You analyze a system prompt and a handful of example (input, expected_output) "
    "pairs the prompt should handle. Identify what the prompt is likely to fail at: "
    "ambiguity, missing constraints, tone drift, format slippage, hallucination risk. "
    "Reply with a bulleted list of 3-5 specific failure modes. Be concise."
)

_REWRITE_SYSTEM = (
    "You rewrite system prompts to fix known failure modes. Preserve the original "
    "intent; tighten ambiguity; add missing constraints; be explicit about format. "
    "Do NOT make it longer than 1.5x the original. Reply ONLY with the revised prompt, "
    "no preamble."
)


@dataclass
class OptimizationResult:
    original: str
    revised: str
    rounds: int
    score_delta: float
    improved: bool


def _hash(p: str) -> str:
    return hashlib.sha256((p or "").encode()).hexdigest()[:24]


async def optimize(
    *,
    complete_fn: Callable[..., Awaitable[Any]],
    user_id: str,
    original_prompt: str,
    examples: list[dict],
    rounds: int = 3,
    critic_model: str = "maars/economy",
    writer_model: str = "maars/premium",
    judge_model: str = "maars/premium",
    min_improvement: float = 0.6,
) -> OptimizationResult:
    """Run N reflect→rewrite rounds, keep best by judge score.

    examples : [{"input": "...", "expected": "..."}, ...] — at least 3
    min_improvement : score_delta required to prefer revision over original
    """
    from services.llm_judge import judge_bidirectional
    if len(examples) < 3:
        raise ValueError("dspy_optimizer: need >= 3 examples")

    current = original_prompt
    best_delta = 0.0

    for r in range(max(1, rounds)):
        # 1) Reflect
        examples_text = "\n\n".join(
            f"[ex {i+1}] INPUT: {e['input']}\nEXPECTED: {e['expected']}"
            for i, e in enumerate(examples)
        )
        critique = await complete_fn(
            user_id,
            messages=[
                {"role": "system", "content": _REFLECT_SYSTEM},
                {"role": "user", "content": f"PROMPT:\n{current}\n\nEXAMPLES:\n{examples_text}"},
            ],
            model=critic_model,
            temperature=0.2,
            max_tokens=500,
            source="dspy_reflect",
            enable_cache=False,
            verify_injection=False,
        )
        failures = critique["choices"][0]["message"]["content"]

        # 2) Rewrite
        revised = await complete_fn(
            user_id,
            messages=[
                {"role": "system", "content": _REWRITE_SYSTEM},
                {"role": "user", "content": f"ORIGINAL:\n{current}\n\nFAILURES:\n{failures}"},
            ],
            model=writer_model,
            temperature=0.5,
            max_tokens=min(2048, len(current) * 2),
            source="dspy_rewrite",
            enable_cache=False,
            verify_injection=False,
        )
        candidate = revised["choices"][0]["message"]["content"].strip()
        if not candidate or candidate == current:
            break

        # 3) Evaluate on held-out example (last one)
        held = examples[-1]
        a_baseline = await complete_fn(
            user_id,
            messages=[
                {"role": "system", "content": current},
                {"role": "user",   "content": held["input"]},
            ],
            model="maars/economy", temperature=0.0, max_tokens=800,
            source="dspy_eval_baseline", enable_cache=False, verify_injection=False,
        )
        a_candidate = await complete_fn(
            user_id,
            messages=[
                {"role": "system", "content": candidate},
                {"role": "user",   "content": held["input"]},
            ],
            model="maars/economy", temperature=0.0, max_tokens=800,
            source="dspy_eval_candidate", enable_cache=False, verify_injection=False,
        )
        verdict = await judge_bidirectional(
            complete_fn=complete_fn, user_id=user_id,
            question=held["input"],
            answer_a=a_baseline["choices"][0]["message"]["content"],
            answer_b=a_candidate["choices"][0]["message"]["content"],
            judge_model=judge_model,
        )
        delta = verdict.score_b - verdict.score_a
        if delta >= min_improvement:
            current = candidate
            best_delta = max(best_delta, delta)
        else:
            break  # no further gain; stop early

    improved = current != original_prompt
    try:
        from db import db
        if improved:
            await db.optimized_prompts.replace_one(
                {"_id": _hash(original_prompt)},
                {
                    "_id": _hash(original_prompt),
                    "original": original_prompt,
                    "revised": current,
                    "score_delta": best_delta,
                    "rounds": rounds,
                },
                upsert=True,
            )
    except Exception as exc:
        logger.info("optimized_prompts persist failed: %s", exc)

    return OptimizationResult(
        original=original_prompt,
        revised=current,
        rounds=rounds,
        score_delta=best_delta,
        improved=improved,
    )


async def get_optimized(original: str) -> str | None:
    """Fetch a previously-optimized revision (if any) for this prompt."""
    try:
        from db import db
        doc = await db.optimized_prompts.find_one({"_id": _hash(original)})
        if doc and doc.get("revised"):
            return doc["revised"]
    except Exception:
        return None
    return None
