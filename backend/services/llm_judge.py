"""LLM-as-judge — pairwise comparison to benchmark our routing.

MT-Bench / Chatbot-Arena use GPT-4 as an impartial judge: shown two
answers to the same prompt, it picks a winner. Correlation with human
preference is ~85%. We use the same pattern to:

  1. Benchmark candidate models internally before promoting to alias tiers.
  2. Spot-check production traffic (sample 1% of calls, run them on the
     next-tier-up model, judge, log the delta). Over time this tells us
     whether the economy tier is drifting away from flagship quality.
  3. Build ground truth for the RouteLLM matrix.

Opinionated judge prompt (borrowed verbatim-style from MT-Bench):
  'You are a fair and impartial judge...' + the two answers + rubric.

Output schema: {"winner": "A"|"B"|"tie", "score_a": 0-10, "score_b": 0-10,
                "reason": "..."}
"""
from __future__ import annotations
import json
import logging
import re
from dataclasses import dataclass
from typing import Any, Awaitable, Callable

logger = logging.getLogger(__name__)


_JUDGE_SYSTEM = (
    "You are an impartial judge. You will compare two assistant answers "
    "to the same user question. Evaluate on: (1) correctness of factual "
    "claims, (2) direct responsiveness to the question, (3) clarity, "
    "(4) absence of hallucination. Do not be biased by length or by the "
    "order the answers are shown.\n\n"
    "Return ONLY JSON: "
    '{"winner":"A"|"B"|"tie","score_a":<0-10>,"score_b":<0-10>,'
    '"reason":"one-sentence rationale"}'
)


@dataclass
class JudgeResult:
    winner: str
    score_a: float
    score_b: float
    reason: str


def _parse(raw: str) -> JudgeResult:
    match = re.search(r"\{.*\}", raw or "", re.DOTALL)
    if not match:
        return JudgeResult(winner="tie", score_a=0.0, score_b=0.0, reason="unparsable")
    try:
        obj = json.loads(match.group(0))
    except json.JSONDecodeError:
        return JudgeResult(winner="tie", score_a=0.0, score_b=0.0, reason="bad_json")
    w = obj.get("winner", "tie")
    if w not in ("A", "B", "tie"):
        w = "tie"
    return JudgeResult(
        winner=w,
        score_a=float(obj.get("score_a", 0.0)),
        score_b=float(obj.get("score_b", 0.0)),
        reason=str(obj.get("reason", ""))[:300],
    )


async def judge(
    *,
    complete_fn: Callable[..., Awaitable[Any]],
    user_id: str,
    question: str,
    answer_a: str,
    answer_b: str,
    judge_model: str = "maars/premium",
) -> JudgeResult:
    """Run a pairwise judgment. Position bias is mitigated by calling
    twice (A/B then B/A) and reconciling — see `judge_bidirectional`."""
    user_msg = (
        f"## User question\n{question}\n\n"
        f"## Answer A\n{answer_a}\n\n"
        f"## Answer B\n{answer_b}"
    )
    r = await complete_fn(
        user_id,
        messages=[
            {"role": "system", "content": _JUDGE_SYSTEM},
            {"role": "user",   "content": user_msg},
        ],
        model=judge_model,
        temperature=0.0,
        max_tokens=400,
        source="llm_judge",
        enable_cache=False,
        verify_injection=False,
    )
    return _parse(r["choices"][0]["message"]["content"])


async def judge_bidirectional(
    *,
    complete_fn: Callable[..., Awaitable[Any]],
    user_id: str,
    question: str,
    answer_a: str,
    answer_b: str,
    judge_model: str = "maars/premium",
) -> JudgeResult:
    """Run both (A,B) and (B,A) orderings; reconcile. Removes position bias.

    Reconciliation: if both runs pick the same side, that's the answer.
    If they disagree, it's a tie and we keep the score diff small.
    """
    r1 = await judge(
        complete_fn=complete_fn, user_id=user_id, question=question,
        answer_a=answer_a, answer_b=answer_b, judge_model=judge_model,
    )
    r2 = await judge(
        complete_fn=complete_fn, user_id=user_id, question=question,
        answer_a=answer_b, answer_b=answer_a, judge_model=judge_model,
    )
    # r2 has answer_b on side A and vice-versa — invert.
    flipped = {"A": "B", "B": "A", "tie": "tie"}[r2.winner]
    if r1.winner == flipped:
        return JudgeResult(
            winner=r1.winner,
            score_a=(r1.score_a + r2.score_b) / 2,
            score_b=(r1.score_b + r2.score_a) / 2,
            reason=r1.reason,
        )
    return JudgeResult(
        winner="tie",
        score_a=(r1.score_a + r2.score_b) / 2,
        score_b=(r1.score_b + r2.score_a) / 2,
        reason=f"disagreement (fwd={r1.winner}, rev={r2.winner})",
    )
