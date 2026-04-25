"""Confidence-aware routing — escalate uncertain answers to a stronger model.

Cheap model runs first. If its answer comes back low-confidence (by
logprobs or a self-report), silently retry on the flagship tier. The
expensive model only gets called on the ~15% of queries where the cheap
one wasn't sure — published savings of ~40% vs always-flagship.

Two confidence signals we use:
  1. logprobs — OpenAI/Groq/Cerebras return `logprobs` when asked.
     Compute avg token log-prob; if below threshold → low confidence.
  2. Self-report — append "On a scale of 0-10, how confident are you?"
     as a follow-up. Bottom ~20% gets escalated. Slower but works for
     providers that don't expose logprobs (Anthropic, Gemini).

This module doesn't call providers itself. It takes a response dict and
returns a `ConfidenceAssessment` that `llm_gateway.complete()` uses to
decide whether to re-dispatch to a stronger model.
"""
from __future__ import annotations
import logging
import math
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)

LOGPROB_CONFIDENT_THRESHOLD = -0.45   # avg token logprob above this = confident
LOGPROB_UNCERTAIN_THRESHOLD = -1.2    # below this = definitely escalate

# Per-tier escalation thresholds now live in shared/tier_config.py so
# every tier-aware service agrees on the same knobs. Import for backward
# compatibility — dict shape preserved so any external caller keeps working.
from shared.tier_config import TIERS as _TIERS
TIER_ESCALATION_THRESHOLDS = {
    t: cfg.escalation_logprob for t, cfg in _TIERS.items()
    if cfg.plan_keywords  # skip mode-only entries (chat/batch/auto)
}


@dataclass
class ConfidenceAssessment:
    score: float              # 0.0 (certain wrong) to 1.0 (certain right)
    method: str               # "logprobs" | "self_report" | "heuristic"
    should_escalate: bool
    reason: str = ""


def _avg_logprob(choice: dict) -> float | None:
    """OpenAI-compat: logprobs.content is a list of {token, logprob, ...}."""
    lp = choice.get("logprobs")
    if not lp or not isinstance(lp, dict):
        return None
    tokens = lp.get("content") or []
    if not tokens:
        return None
    total = 0.0
    n = 0
    for t in tokens:
        v = t.get("logprob")
        if isinstance(v, (int, float)) and not math.isnan(v):
            total += v
            n += 1
    if n == 0:
        return None
    return total / n


def assess(response: dict[str, Any], *, tier: str = "standard") -> ConfidenceAssessment:
    """Extract whatever confidence signal we can from this response.

    `tier` picks the escalation threshold: premium escalates aggressively
    (delivers quality), economy stays cheap (preserves margin)."""
    threshold = TIER_ESCALATION_THRESHOLDS.get(tier, LOGPROB_UNCERTAIN_THRESHOLD)
    if not response or "choices" not in response:
        return ConfidenceAssessment(
            score=0.5, method="heuristic", should_escalate=False, reason="no_choices"
        )
    choice = response["choices"][0]
    avg_lp = _avg_logprob(choice)
    if avg_lp is not None:
        # Map [-3, 0] → [0, 1]; clamp.
        score = max(0.0, min(1.0, (avg_lp + 3.0) / 3.0))
        escalate = avg_lp < threshold
        return ConfidenceAssessment(
            score=score,
            method="logprobs",
            should_escalate=escalate,
            reason=f"avg_logprob={avg_lp:.3f} tier={tier} threshold={threshold}",
        )

    # Heuristic fallback: look for hedging language.
    content = choice.get("message", {}).get("content", "") or ""
    low = content.lower()
    hedges = (
        "i'm not sure", "i don't know", "not certain", "unclear",
        "it depends", "may or may not", "cannot determine",
    )
    hedge_hits = sum(1 for h in hedges if h in low)
    if hedge_hits >= 2:
        return ConfidenceAssessment(
            score=0.3, method="heuristic", should_escalate=True,
            reason=f"hedge_phrases={hedge_hits}",
        )
    return ConfidenceAssessment(
        score=0.7, method="heuristic", should_escalate=False, reason="no_hedges",
    )


def enable_logprobs_for_params(params: dict[str, Any], *, provider: str) -> dict[str, Any]:
    """Amend request params so the provider returns logprobs we can read.
    No-op for providers that don't support it."""
    p = dict(params or {})
    provider = (provider or "").lower()
    if provider in ("openai", "groq", "cerebras", "fireworks", "together"):
        p.setdefault("logprobs", True)
        # top_logprobs is required by some providers to actually populate
        # the field; 1 is enough for avg-confidence.
        p.setdefault("top_logprobs", 1)
    return p
