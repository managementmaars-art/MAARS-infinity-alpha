"""Response-level trust / confidence scoring.

Cleanlab TLM-style signal on every answer. Two cheap methods:

  1. **Self-consistency**  — re-sample the same prompt at a low
     temperature and compute semantic similarity; agreement → high
     confidence.
  2. **Logprob average**   — when the provider exposes logprobs
     (OpenAI, Groq), mean token logprob → mapped to 0-1.

Neither method requires the Cleanlab API. Self-consistency costs one
extra cheap-model call (Gemini-flash / Groq); logprob is free.

Returns a small dict:
    {"score": 0.0-1.0, "method": "self_consistency"|"logprob",
     "reasoning": "<short>", "agreement": 0-1 (if method=self_consistency)}

Writes nothing itself — the caller attaches the score to the response
envelope AND persists it as `gateway_usage_logs.trust_score` for
rollup analytics.
"""
from __future__ import annotations
import logging
import math
import re
from typing import Any, Optional

logger = logging.getLogger(__name__)


# ── Logprob-based (free when provider reports them) ────────────────

def score_from_logprobs(usage_or_choices: dict | list) -> dict[str, Any] | None:
    """If the provider returned logprobs in the completion, compute a
    summary score. Returns None if logprobs aren't present so the caller
    can fall through to self-consistency."""
    if not usage_or_choices:
        return None
    choices = usage_or_choices if isinstance(usage_or_choices, list) else (usage_or_choices.get("choices") or [])
    if not choices:
        return None
    lp = ((choices[0] or {}).get("logprobs") or {}).get("content") or []
    if not lp:
        return None
    values: list[float] = []
    for tok in lp:
        v = tok.get("logprob") if isinstance(tok, dict) else None
        if isinstance(v, (int, float)):
            values.append(float(v))
    if not values:
        return None
    # Average logprob is negative; normalize to 0-1 via exp.
    # -0.1 → ~0.9 (very confident), -2 → ~0.14 (uncertain), -0.01 → ~0.99
    mean_lp = sum(values) / len(values)
    score = max(0.0, min(1.0, math.exp(mean_lp)))
    return {
        "score":    round(score, 3),
        "method":   "logprob",
        "token_count": len(values),
        "mean_logprob": round(mean_lp, 4),
        "reasoning": f"mean logprob {mean_lp:.2f} over {len(values)} tokens",
    }


# ── Self-consistency ───────────────────────────────────────────────

def _jaccard_similarity(a: str, b: str) -> float:
    """Cheap word-level Jaccard for two strings. Good enough as a
    cheap-model agreement check; no embeddings needed."""
    tokens = lambda s: set(re.findall(r"[A-Za-z0-9]{3,}", (s or "").lower()))
    sa, sb = tokens(a), tokens(b)
    if not sa or not sb:
        return 0.0
    inter = len(sa & sb)
    union = len(sa | sb)
    return inter / union if union else 0.0


async def score_by_self_consistency(
    user_id: str, *, system_prompt: str, user_prompt: str,
    first_completion: str,
    model: str = "maars/auto",
) -> dict[str, Any]:
    """Re-sample the same prompt with the cheapest model available,
    compute similarity with the first completion."""
    from services.llm_gateway import complete_text
    try:
        second = await complete_text(
            user_id,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model=model,
            max_tokens=500, temperature=0.3,
            source="trust_scorer.self_consistency",
            enable_cache=False,
        )
    except Exception as exc:
        return {"score": 0.5, "method": "self_consistency",
                "reasoning": f"fallback_call_failed: {exc}"}
    agreement = _jaccard_similarity(first_completion, second)
    # Map Jaccard (typically 0.0-0.5 for real text) to 0-1 trust.
    # Similar answers at low-temperature → high confidence.
    # We stretch: 0.1 → 0.5, 0.3 → 0.85, 0.5 → 1.0.
    score = min(1.0, agreement * 2.0)
    return {
        "score":     round(score, 3),
        "method":    "self_consistency",
        "agreement": round(agreement, 3),
        "reasoning": f"jaccard={agreement:.2f} between primary + sampled completion",
    }


# ── Public facade ──────────────────────────────────────────────────

async def score(
    *, user_id: str, response: dict,
    system_prompt: str = "", user_prompt: str = "",
    mode: str = "auto",       # "auto" | "logprob" | "self_consistency" | "none"
) -> dict[str, Any]:
    """Compute a trust score for an LLM response.

    mode="auto": try logprob first (free); fall back to self_consistency.
    Return a dict safe to inline into `response.maars.trust`.
    """
    if mode == "none":
        return {"score": None, "method": "disabled"}
    if mode in ("auto", "logprob"):
        lp_score = score_from_logprobs(response)
        if lp_score:
            return lp_score
        if mode == "logprob":
            return {"score": None, "method": "logprob_unavailable"}
    # Self-consistency path needs the original prompts
    completion = ""
    try:
        completion = ((response.get("choices") or [{}])[0]
                      .get("message", {}).get("content", ""))
    except Exception:
        completion = ""
    if not completion:
        return {"score": None, "method": "no_completion"}
    return await score_by_self_consistency(
        user_id,
        system_prompt=system_prompt, user_prompt=user_prompt,
        first_completion=completion,
    )
