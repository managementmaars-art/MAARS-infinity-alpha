"""Unified provider router — online bandit + multi-objective pareto in one module.

Two complementary strategies live here because both answer "which provider?":

  • Bandit (Thompson sampling) — adaptive, learns from call-level feedback.
    The record() side is wired on every completion so the posteriors shift
    toward arms that actually perform; the pick() side is available when the
    caller only has arm IDs (no pre-known quality/cost/latency scores).

  • Pareto — mode-aware multi-objective ranking. Caller provides Candidate
    objects carrying quality / cost / latency; pareto filters the dominated
    ones, then picks from the frontier using weights implied by the mode
    (premium=quality-first, economy=cost-first, batch=latency-ignored, etc.)

Why one file: they share no state but share a purpose. Splitting them into
two files implied they were interchangeable strategies for the same pick —
they're not. Bandit is online learning; pareto is offline ranking. Keeping
them colocated makes it obvious to future readers that they're a choose-one
pair depending on whether the caller has scores or just IDs.

Reward definition for the bandit (per call):
    reward = w_success * was_success
           - w_latency * min(1.0, latency_ms / 10000)
           - w_cost    * min(1.0, credits_used / 10)

Pareto mode weights are tuned for the product tiers:
    "chat"    → balanced (0.40q 0.20c 0.40l)
    "premium" → quality-first (0.70q 0.10c 0.20l)   — premium plans
    "economy" → cost-first   (0.20q 0.70c 0.10l)    — free/starter tiers
    "batch"   → cost-first, latency-ignored (0.50q 0.50c 0.00l)
    "auto"    → mild balance (0.45q 0.35c 0.20l)

State is in-process for both — same tradeoff as circuit_breaker. Upgrade
path if we ever scale beyond one backend host is Redis for the bandit arms.
"""
from __future__ import annotations
import logging
import math
import random
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


# ═══ Bandit (Thompson sampling) ══════════════════════════════════════

REWARD_WEIGHTS = {"success": 1.0, "latency": 0.3, "cost": 0.2}
EMA_ALPHA = 0.1


@dataclass
class _Arm:
    alpha: float = 1.0         # Beta posterior on success-probability
    beta: float = 1.0
    ema_reward: float = 0.0    # EWMA of normalized reward
    pulls: int = 0


_arms: dict[str, _Arm] = {}


def _key(arm_id: str) -> _Arm:
    a = _arms.get(arm_id)
    if a is None:
        a = _Arm()
        _arms[arm_id] = a
    return a


def record(
    arm_id: str,
    *,
    success: bool,
    latency_ms: float = 0.0,
    credits: float = 0.0,
    weights: dict[str, float] | None = None,
) -> None:
    """Feed one call's outcome into the arm's posterior."""
    w = {**REWARD_WEIGHTS, **(weights or {})}
    a = _key(arm_id)
    a.pulls += 1
    if success:
        a.alpha += 1
    else:
        a.beta += 1
    reward = (
        w["success"] * (1.0 if success else 0.0)
        - w["latency"] * min(1.0, latency_ms / 10000)
        - w["cost"] * min(1.0, credits / 10)
    )
    a.ema_reward = a.ema_reward * (1 - EMA_ALPHA) + reward * EMA_ALPHA


def _sample_beta(alpha: float, beta: float) -> float:
    return random.betavariate(max(alpha, 1e-3), max(beta, 1e-3))


def pick(arm_ids: list[str], *, explore_bias: float = 0.0) -> str | None:
    """Pick the arm with the highest Thompson-sampled score.

    explore_bias > 0 bumps unseen arms (< 10 pulls) to encourage exploration.
    """
    if not arm_ids:
        return None
    best = arm_ids[0]
    best_score = -math.inf
    for aid in arm_ids:
        a = _key(aid)
        p_success = _sample_beta(a.alpha, a.beta)
        score = p_success + a.ema_reward * 0.3
        if explore_bias and a.pulls < 10:
            score += random.uniform(0, explore_bias)
        if score > best_score:
            best_score = score
            best = aid
    return best


def snapshot() -> dict[str, dict]:
    out = {}
    for aid, a in _arms.items():
        p = a.alpha / max(a.alpha + a.beta, 1e-3)
        out[aid] = {
            "pulls": a.pulls,
            "success_rate": round(p, 4),
            "ema_reward": round(a.ema_reward, 4),
            "alpha": round(a.alpha, 2),
            "beta": round(a.beta, 2),
        }
    return out


def reset(arm_id: str) -> None:
    if arm_id in _arms:
        _arms[arm_id] = _Arm()


# ═══ Pareto (multi-objective mode-aware ranking) ═════════════════════

@dataclass
class Candidate:
    provider: str
    model: str
    quality: float            # 0.0 (bad) → 1.0 (great) — arena / benchmark
    cost: float               # USD per representative request
    latency_ms: float
    free_tier: bool = False


# Pareto weights now live in shared/tier_config.py so every tier-aware
# service draws from the same config. Keeping this module-level dict as
# a backward-compat alias for anyone importing it directly.
from shared.tier_config import TIERS as _TIERS
WEIGHTS_BY_MODE = {t: dict(cfg.pareto_weights) for t, cfg in _TIERS.items()}


def _normalize_cost(candidates: list[Candidate]) -> list[float]:
    costs = [c.cost for c in candidates]
    cmin = min(costs) if costs else 0.0
    cmax = max(costs) if costs else 1.0
    if cmax == cmin:
        return [1.0 for _ in candidates]
    return [1.0 - (c.cost - cmin) / (cmax - cmin) for c in candidates]  # invert: lower cost → higher score


def _normalize_latency(candidates: list[Candidate]) -> list[float]:
    lats = [c.latency_ms for c in candidates if c.latency_ms > 0]
    if not lats:
        return [0.5 for _ in candidates]
    lmin = min(lats)
    lmax = max(lats)
    if lmax == lmin:
        return [1.0 for _ in candidates]
    out = []
    for c in candidates:
        lat = c.latency_ms if c.latency_ms > 0 else (lmin + lmax) / 2
        out.append(1.0 - (lat - lmin) / (lmax - lmin))
    return out


def _pareto_front(candidates: list[Candidate]) -> list[int]:
    """Indices of candidates not dominated by any other. Domination:
    another candidate is >= on all axes and strictly > on at least one."""
    n = len(candidates)
    front = []
    for i in range(n):
        a = candidates[i]
        dominated = False
        for j in range(n):
            if i == j:
                continue
            b = candidates[j]
            ge = (b.quality >= a.quality and b.cost <= a.cost and b.latency_ms <= a.latency_ms)
            gt = (b.quality > a.quality or b.cost < a.cost or b.latency_ms < a.latency_ms)
            if ge and gt:
                dominated = True
                break
        if not dominated:
            front.append(i)
    return front


def choose(
    candidates: list[Candidate],
    *,
    mode: str = "auto",
    free_first: bool = True,
) -> Candidate | None:
    """Pareto-filter the candidates then pick the one closest to the
    caller's weight vector. If `free_first` is set and any Pareto-front
    candidate is on the free tier, a free candidate wins — preserves the
    zero-marginal-cost arbitrage behind MAARS margin.

    `premium` mode short-circuits to highest raw quality regardless of
    cost — paying customers are buying quality, not router optimization.
    """
    if not candidates:
        return None
    weights = WEIGHTS_BY_MODE.get(mode, WEIGHTS_BY_MODE["auto"])

    front_idx = _pareto_front(candidates)
    front = [candidates[i] for i in front_idx]

    # Premium: pure quality. Operator's intent is "$1k+/mo customers get
    # the best model on the bench" — normalized cost/latency penalties
    # would let a flashy free model win on numerical score, defeating
    # the product promise.
    if mode == "premium":
        return max(front, key=lambda c: c.quality)

    if free_first:
        free = [c for c in front if c.free_tier]
        if free:
            cost_norm = _normalize_cost(free)
            lat_norm = _normalize_latency(free)
            best_i, best_score = 0, -math.inf
            for i, c in enumerate(free):
                score = (weights["quality"] * c.quality
                         + weights["cost"] * cost_norm[i]
                         + weights["latency"] * lat_norm[i])
                if score > best_score:
                    best_score, best_i = score, i
            return free[best_i]

    cost_norm = _normalize_cost(front)
    lat_norm = _normalize_latency(front)
    best_i, best_score = 0, -math.inf
    for i, c in enumerate(front):
        score = (weights["quality"] * c.quality
                 + weights["cost"] * cost_norm[i]
                 + weights["latency"] * lat_norm[i])
        if score > best_score:
            best_score, best_i = score, i
    return front[best_i]


# ═══ Convenience rerank for the hot path ═════════════════════════════

def rerank_for_mode(
    ranked_pairs: list[tuple[str, str]],
    *,
    mode: str,
    quality_map: dict[tuple[str, str], float] | None = None,
    cost_map: dict[tuple[str, str], float] | None = None,
    latency_map: dict[tuple[str, str], float] | None = None,
    free_set: set[tuple[str, str]] | None = None,
) -> list[tuple[str, str]]:
    """Re-order a (provider, model) candidate list using Pareto + mode
    weights. Designed to plug into the gateway hot path: smart_router
    produces the initial candidate ranking, this function re-orders it
    for premium/batch tiers without replacing the original logic.

    If score maps are missing, the original order is returned — safe
    fallback so a missing benchmark doesn't break routing.
    """
    if not ranked_pairs or mode in (None, "", "auto"):
        return ranked_pairs
    quality_map = quality_map or {}
    cost_map    = cost_map    or {}
    latency_map = latency_map or {}
    free_set    = free_set    or set()
    cands: list[Candidate] = []
    for pair in ranked_pairs:
        # Default: middle-of-the-road if we don't have a score yet.
        cands.append(Candidate(
            provider=pair[0], model=pair[1],
            quality=float(quality_map.get(pair, 0.5)),
            cost=float(cost_map.get(pair, 1.0)),
            latency_ms=float(latency_map.get(pair, 500.0)),
            free_tier=(pair in free_set),
        ))
    chosen = choose(cands, mode=mode, free_first=(mode != "premium"))
    if chosen is None:
        return ranked_pairs
    # Move the chosen candidate to the front, keep the rest in original order.
    head = (chosen.provider, chosen.model)
    return [head] + [p for p in ranked_pairs if p != head]
