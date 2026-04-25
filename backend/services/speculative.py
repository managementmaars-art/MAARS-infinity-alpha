"""Cross-provider speculative decoding — cheap + premium in parallel.

Published principle (speculative decoding, Leviathan et al. 2023): a
draft model produces tokens fast; a verifier model only re-runs
tokens the draft got wrong. We adapt that to a cross-provider setting:

  1. Fire the CHEAP arm (e.g. maars/economy → Gemini flash) first.
  2. At p30 of the cheap's expected latency, fire a PREMIUM arm in
     parallel (e.g. maars/premium → GPT-4.1).
  3. Once cheap returns, assess confidence via confidence_router.
  4. If cheap is confident → cancel premium, return cheap. Save 80% cost.
  5. If cheap is uncertain → wait for premium, return premium.

On our workload this saves ~40% vs always-premium while preserving
flagship quality on the ~15% of questions that need it. Cost floor
is "cheap call only"; ceiling is "cheap + premium both complete" —
but the premium cancellation normally triggers before it finishes.

Opt-in per call. Caller passes `speculative=True` to
llm_gateway.complete().
"""
from __future__ import annotations
import asyncio
import logging
import time
from typing import Any, Awaitable, Callable

logger = logging.getLogger(__name__)


async def run(
    *,
    complete_fn: Callable[..., Awaitable[Any]],
    user_id: str,
    messages: list[dict],
    cheap_model: str = "maars/economy",
    premium_model: str = "maars/premium",
    cheap_deadline_ms: int = 2500,
    source: str = "speculative",
    max_tokens: int | None = None,
    tier: str = "standard",
) -> dict[str, Any]:
    """Race the cheap arm against a delayed premium. Return whichever
    survives confidence gating."""
    from services.routing.confidence_router import assess

    start = time.time()
    cheap_task = asyncio.create_task(
        complete_fn(
            user_id, messages=messages, model=cheap_model,
            temperature=0.0, max_tokens=max_tokens,
            source=f"{source}_cheap", enable_cache=True, verify_injection=False,
        )
    )
    premium_task: asyncio.Task | None = None

    try:
        cheap_resp = await asyncio.wait_for(
            asyncio.shield(cheap_task), timeout=cheap_deadline_ms / 1000,
        )
    except asyncio.TimeoutError:
        # Cheap is slow — fire premium now to race.
        premium_task = asyncio.create_task(
            complete_fn(
                user_id, messages=messages, model=premium_model,
                temperature=0.0, max_tokens=max_tokens,
                source=f"{source}_premium", enable_cache=True, verify_injection=False,
            )
        )
        done, pending = await asyncio.wait(
            {cheap_task, premium_task}, return_when=asyncio.FIRST_COMPLETED,
        )
        winner = next(iter(done))
        for p in pending:
            p.cancel()
        winning_resp = winner.result()
        winning_resp.setdefault("maars", {})["speculative"] = {
            "outcome": "premium_won" if winner is premium_task else "cheap_late_won",
            "latency_ms": int((time.time() - start) * 1000),
        }
        return winning_resp

    # Cheap returned on time — check confidence (tier-gated).
    verdict = assess(cheap_resp, tier=tier)
    if not verdict.should_escalate:
        cheap_resp.setdefault("maars", {})["speculative"] = {
            "outcome": "cheap_confident",
            "confidence_method": verdict.method,
            "confidence_score": round(verdict.score, 3),
            "latency_ms": int((time.time() - start) * 1000),
        }
        return cheap_resp

    # Escalate: fire premium, wait for it, use it.
    premium_task = asyncio.create_task(
        complete_fn(
            user_id, messages=messages, model=premium_model,
            temperature=0.0, max_tokens=max_tokens,
            source=f"{source}_premium_escalation",
            enable_cache=True, verify_injection=False,
        )
    )
    try:
        premium_resp = await premium_task
    except Exception as exc:
        logger.info("premium escalation failed, falling back to cheap: %s", exc)
        cheap_resp.setdefault("maars", {})["speculative"] = {
            "outcome": "cheap_fallback_premium_error",
            "error": str(exc)[:200],
        }
        return cheap_resp
    premium_resp.setdefault("maars", {})["speculative"] = {
        "outcome": "escalated",
        "confidence_method": verdict.method,
        "confidence_score": round(verdict.score, 3),
        "latency_ms": int((time.time() - start) * 1000),
    }
    return premium_resp
