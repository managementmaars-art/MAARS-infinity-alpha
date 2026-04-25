"""
Scoring router — replaces rule-based alias resolution with a weighted scorer.

    score = (
        w_cap  × capability_match +
        w_cost × (1 / normalized_cost) +
        w_lat  × (1 / normalized_latency) +
        w_hlth × provider_health +
        w_tier × tier_match
    )

This module is **pure** — no DB, no HTTP, no side effects. Callers pass in the
candidate set and optional context (task type, tier preference, health map).
That keeps ranking unit-testable and auditable, and lets v1_gateway log the
full breakdown alongside each request for operator diagnosis.

Rule-based fallback: when the scorer produces no positive-scored candidate
(e.g. every provider unhealthy), caller should fall back to the existing
`_resolve_maars_alias` path.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

# --------------------------------------------------------------------------- weights

DEFAULT_WEIGHTS: dict[str, float] = {
    "capability":  3.0,   # matches intent / task to model's known strengths
    "cost":        2.0,   # cheaper wins — reciprocal
    "latency":     1.0,   # faster wins — reciprocal
    "health":      2.5,   # unhealthy → hard penalty
    "tier":        1.5,   # tier preference match
}

# Task → preferred capability flags. Aligned with the existing task classifier
# (backend/services/llm_router.py). A model scores full capability points iff
# it lists the flag in its `capabilities`.
TASK_CAPABILITY_MAP: dict[str, list[str]] = {
    "code":        ["code"],
    "math":        ["reasoning", "math"],
    "reasoning":   ["reasoning"],
    "creative":    ["creative", "long_context"],
    "data":        ["reasoning", "code"],
    "legal":       ["reasoning", "long_context"],
    "research":    ["search", "long_context"],
    "translation": ["multilingual"],
    "summary":     ["long_context"],
    "vision":      ["vision"],
    "quick":       ["fast"],
    "chat":        [],
}

TIERS = ("economy", "standard", "premium")


# --------------------------------------------------------------------------- data shapes

@dataclass
class Candidate:
    """A single provider/model option the router may pick."""
    provider: str
    model: str
    tier: str                             # economy | standard | premium
    cost_per_mtok: float                  # blended input+output cost per M tokens
    avg_latency_ms: int = 1500            # rolling avg, populated from metrics when available
    capabilities: list[str] = field(default_factory=list)
    context_window: int = 16_000


@dataclass
class ScoredCandidate:
    candidate: Candidate
    score: float
    breakdown: dict[str, float]

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider": self.candidate.provider,
            "model": self.candidate.model,
            "tier": self.candidate.tier,
            "score": round(self.score, 4),
            "breakdown": {k: round(v, 4) for k, v in self.breakdown.items()},
        }


# --------------------------------------------------------------------------- scoring

def _capability_match(candidate: Candidate, desired: list[str]) -> float:
    if not desired:
        return 0.5  # neutral for generic chat
    have = set(c.lower() for c in candidate.capabilities)
    want = set(c.lower() for c in desired)
    if not want:
        return 0.5
    return len(have & want) / len(want)


def _normalize_reciprocal(value: float, floor: float = 0.05) -> float:
    """Reciprocal score in (0, 1] — clamped so zero-cost / zero-latency doesn't explode."""
    return 1.0 / max(value, floor)


def _tier_match(candidate_tier: str, preferred: Optional[str]) -> float:
    if not preferred or preferred not in TIERS:
        return 0.5
    if candidate_tier == preferred:
        return 1.0
    # Adjacent tier → half points (economy ↔ standard, standard ↔ premium).
    try:
        return 0.5 if abs(TIERS.index(candidate_tier) - TIERS.index(preferred)) == 1 else 0.0
    except ValueError:
        return 0.0


def score_candidate(
    candidate: Candidate,
    *,
    task_type: str = "chat",
    tier_preference: Optional[str] = None,
    provider_health: float = 1.0,
    weights: Optional[dict[str, float]] = None,
) -> ScoredCandidate:
    w = {**DEFAULT_WEIGHTS, **(weights or {})}
    desired_caps = TASK_CAPABILITY_MAP.get(task_type.lower(), [])

    cap = _capability_match(candidate, desired_caps)
    cost = _normalize_reciprocal(candidate.cost_per_mtok, floor=0.05)
    lat = _normalize_reciprocal(candidate.avg_latency_ms / 1000.0, floor=0.1)
    hlth = max(0.0, min(1.0, provider_health))
    tier = _tier_match(candidate.tier, tier_preference)

    breakdown = {
        "capability_raw": cap,
        "cost_raw": cost,
        "latency_raw": lat,
        "health_raw": hlth,
        "tier_raw": tier,
        "capability_wt": cap * w["capability"],
        "cost_wt": cost * w["cost"],
        "latency_wt": lat * w["latency"],
        "health_wt": hlth * w["health"],
        "tier_wt": tier * w["tier"],
    }
    total = sum(v for k, v in breakdown.items() if k.endswith("_wt"))

    # Hard penalty: if the task explicitly requires capabilities and this
    # candidate has ZERO of them, scale the total down heavily so it only
    # wins when no capable alternative exists.
    if desired_caps and cap == 0.0:
        total *= 0.2
        breakdown["capability_penalty"] = 0.2

    return ScoredCandidate(candidate=candidate, score=total, breakdown=breakdown)


def rank_candidates(
    candidates: list[Candidate],
    *,
    task_type: str = "chat",
    tier_preference: Optional[str] = None,
    health_map: Optional[dict[str, float]] = None,
    weights: Optional[dict[str, float]] = None,
) -> list[ScoredCandidate]:
    """
    Score every candidate and return them sorted descending.

    `health_map`: provider_slug → 0.0 (down) .. 1.0 (perfect). Default 1.0.
    """
    health = health_map or {}
    scored = [
        score_candidate(
            c,
            task_type=task_type,
            tier_preference=tier_preference,
            provider_health=health.get(c.provider, 1.0),
            weights=weights,
        )
        for c in candidates
    ]
    scored.sort(key=lambda s: s.score, reverse=True)
    return scored


def pick_best(
    candidates: list[Candidate],
    *,
    task_type: str = "chat",
    tier_preference: Optional[str] = None,
    health_map: Optional[dict[str, float]] = None,
    weights: Optional[dict[str, float]] = None,
) -> Optional[ScoredCandidate]:
    ranked = rank_candidates(
        candidates,
        task_type=task_type,
        tier_preference=tier_preference,
        health_map=health_map,
        weights=weights,
    )
    # Hard-filter: reject zero-health (down) candidates before returning.
    viable = [s for s in ranked if s.breakdown["health_raw"] > 0.0]
    return viable[0] if viable else None
