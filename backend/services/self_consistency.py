"""Self-consistency — sample N times, vote on the answer.

Wang et al. 2022 (Google Research): for reasoning tasks, taking the
majority answer across N temperature-sampled generations beats a single
greedy decode by 5-20 points on GSM8K / ARC / CommonsenseQA.

Cost: N× the tokens. Use sparingly — only when the caller flags the task
as reasoning-heavy. We expose it as an opt-in in llm_gateway.complete()
via `consistency_samples=5`.

Voting rule:
  - Numeric / boolean answer → exact-match vote.
  - Free-text answer → cluster by semantic similarity (embedding cosine
    >= 0.85) and take the largest cluster's centroid.

For our gateway the realistic use is: client calls
`complete(..., consistency_samples=3)` on a math or code-gen task; we
fire 3 parallel completions at temp=0.7, vote, return the winner.
"""
from __future__ import annotations
import asyncio
import logging
import re
from collections import Counter
from typing import Any, Awaitable, Callable

logger = logging.getLogger(__name__)

_NUMERIC_RE = re.compile(r"-?\d+(?:\.\d+)?")


def _extract_numeric(text: str) -> str | None:
    """Grab the final numeric answer if one exists. For math problems we
    use this instead of semantic clustering — cheaper and exact."""
    if not text:
        return None
    # Look for the LAST number (common answer position).
    matches = _NUMERIC_RE.findall(text)
    if not matches:
        return None
    return matches[-1]


def _vote_numeric(answers: list[str]) -> str | None:
    nums = [_extract_numeric(a) for a in answers]
    nums = [n for n in nums if n is not None]
    if not nums:
        return None
    c = Counter(nums)
    winner, _ = c.most_common(1)[0]
    # Find the original answer that had this number (for traceability).
    for a in answers:
        if _extract_numeric(a) == winner:
            return a
    return winner


def _vote_text(answers: list[str]) -> str:
    """Cluster by char-shingle Jaccard — fast, no embeddings needed.
    For high-fidelity we'd use embeddings, but this is the hot path."""
    if not answers:
        return ""
    if len(answers) == 1:
        return answers[0]

    def shingles(s: str) -> set[str]:
        s = " ".join(s.lower().split())
        return {s[i:i+4] for i in range(max(0, len(s) - 3))}

    shs = [shingles(a) for a in answers]
    # Greedy clustering
    clusters: list[list[int]] = []
    for i, sh in enumerate(shs):
        placed = False
        for cl in clusters:
            sample = shs[cl[0]]
            if sample and sh:
                jacc = len(sample & sh) / max(1, len(sample | sh))
                if jacc >= 0.55:
                    cl.append(i)
                    placed = True
                    break
        if not placed:
            clusters.append([i])
    clusters.sort(key=len, reverse=True)
    # Return the answer in the largest cluster that is closest to the
    # cluster centroid (shortest sum of set-differences).
    winners = clusters[0]
    if len(winners) == 1:
        return answers[winners[0]]
    best_i = min(
        winners,
        key=lambda i: sum(len(shs[i] ^ shs[j]) for j in winners if j != i)
    )
    return answers[best_i]


async def run(
    *,
    complete_fn: Callable[..., Awaitable[Any]],
    user_id: str,
    messages: list[dict],
    model: str = "maars/auto",
    samples: int = 3,
    temperature: float = 0.7,
    source: str = "self_consistency",
    max_tokens: int | None = None,
) -> dict[str, Any]:
    """Fire N samples in parallel, vote, return the winning response.

    Returns the FULL winning response dict (so the caller still has
    `usage`, `maars.credits_used` etc. — summed across the N calls).
    """
    samples = max(2, min(5, samples))
    tasks = [
        complete_fn(
            user_id,
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            source=f"{source}_n{i+1}",
        )
        for i in range(samples)
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    responses = [r for r in results if not isinstance(r, Exception) and isinstance(r, dict)]
    if not responses:
        # All samples failed — bubble up the first error.
        for r in results:
            if isinstance(r, Exception):
                raise r
        raise RuntimeError("self_consistency: no samples succeeded")

    answers = [r["choices"][0]["message"]["content"] for r in responses if r.get("choices")]
    numeric_winner = _vote_numeric(answers)
    if numeric_winner is not None:
        winning_answer = numeric_winner
    else:
        winning_answer = _vote_text(answers)

    # Pick the response dict whose content matches the winning answer.
    winner = next(
        (r for r in responses if r["choices"][0]["message"]["content"] == winning_answer),
        responses[0],
    )
    # Sum credits across all N calls.
    total_credits = sum(r.get("maars", {}).get("credits_used", 0) for r in responses)
    winner.setdefault("maars", {})["credits_used"] = total_credits
    winner["maars"]["self_consistency_samples"] = len(responses)
    return winner
