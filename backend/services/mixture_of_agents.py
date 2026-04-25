"""Mixture-of-Agents (MoA) — ensemble that beats single-model flagship.

Wang et al. 2024: layered ensemble where multiple cheap "proposer" models
draft candidate answers in parallel, then a final "aggregator" synthesizes
a better answer conditioned on all drafts. Achieved 65.1% on AlpacaEval
2.0 vs GPT-4o's 57.5% — using open-source Llama-3-70b and Qwen-72b under
the hood.

Our variant:
  Layer 1 (proposers, parallel) :  3 cheap models via maars/economy
  Layer 2 (aggregator)          :  1 call via maars/premium

Cost: ~4× a single premium call, for published quality above flagship.
Use for high-stakes outputs: legal drafts, formal reports, final campaign
copy. Opt-in via `moa=True` in complete() — never on by default.

Proposer prompt:
    "Draft an answer to the user's question. Be thorough."

Aggregator prompt:
    "You have received {n} draft answers. Synthesize the best final
    answer, correcting any errors, preserving factual claims made in
    multiple drafts (consensus is a signal), and hedging anything
    only a single draft claimed."
"""
from __future__ import annotations
import asyncio
import logging
from typing import Any, Awaitable, Callable

logger = logging.getLogger(__name__)


_AGGREGATOR_SYSTEM = (
    "You are an expert synthesizer. You will be shown {n} independently-"
    "generated draft answers to a user's question. Produce the BEST final "
    "answer by:\n"
    "1. Preserving facts that appear in multiple drafts (consensus = signal).\n"
    "2. Correcting contradictions in favor of the most internally consistent draft.\n"
    "3. Dropping hallucinations (claims that only appear in one draft with no support).\n"
    "4. Combining complementary details.\n"
    "Do NOT mention the drafts. Output the final answer only."
)


async def run(
    *,
    complete_fn: Callable[..., Awaitable[Any]],
    user_id: str,
    messages: list[dict],
    proposer_model: str = "maars/economy",
    aggregator_model: str = "maars/premium",
    n_proposers: int = 3,
    source: str = "mixture_of_agents",
    max_tokens: int | None = None,
) -> dict[str, Any]:
    """Execute one MoA round. Returns the aggregator's response dict with
    `maars.moa = {proposers, aggregator, total_credits}` injected."""
    n_proposers = max(2, min(5, n_proposers))

    # Layer 1: proposers in parallel, mild temperature for diversity.
    proposer_tasks = [
        complete_fn(
            user_id, messages=messages, model=proposer_model,
            temperature=0.7, max_tokens=max_tokens,
            source=f"{source}_proposer_{i+1}",
            enable_cache=False, verify_injection=False,
        )
        for i in range(n_proposers)
    ]
    proposer_results = await asyncio.gather(*proposer_tasks, return_exceptions=True)

    drafts: list[str] = []
    credits_layer1 = 0
    for r in proposer_results:
        if isinstance(r, Exception):
            continue
        try:
            drafts.append(r["choices"][0]["message"]["content"])
            credits_layer1 += r.get("maars", {}).get("credits_used", 0)
        except (KeyError, IndexError):
            continue

    if not drafts:
        raise RuntimeError("moa: all proposers failed")

    # Layer 2: aggregator receives the drafts + the original question.
    orig_user = next(
        (m.get("content") for m in reversed(messages) if m.get("role") == "user"),
        "",
    )
    drafts_block = "\n\n".join(f"### Draft {i+1}\n{d}" for i, d in enumerate(drafts))
    aggregator_messages = [
        {"role": "system", "content": _AGGREGATOR_SYSTEM.format(n=len(drafts))},
        {"role": "user",   "content": f"User question:\n{orig_user}\n\n{drafts_block}"},
    ]
    final = await complete_fn(
        user_id, messages=aggregator_messages, model=aggregator_model,
        temperature=0.2, max_tokens=max_tokens,
        source=f"{source}_aggregator",
        enable_cache=False, verify_injection=False,
    )

    final.setdefault("maars", {})["moa"] = {
        "proposers": len(drafts),
        "proposer_model": proposer_model,
        "aggregator_model": aggregator_model,
        "credits_layer1": credits_layer1,
    }
    final["maars"]["credits_used"] = credits_layer1 + final["maars"].get("credits_used", 0)
    return final
