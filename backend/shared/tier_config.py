"""Single source of truth for per-tier routing, caching, and cascade knobs.

Before this module existed, every tier-aware service hard-coded its own
tier thresholds:

  confidence_router.py  —  escalation logprob per tier
  semantic_cache.py     —  similarity threshold per tier
  routing/router.py     —  Pareto weights per tier (mode)
  llm_gateway.py        —  plan-keyword → tier mapping

Each was tuned independently. This meant the routing decision for
"premium" could use weights intended for premium, but the cache would
classify that same request as "standard" because the two services saw
different tier strings, or plan keywords didn't match across files.

Now every tier-aware decision reads from `TIERS` here. One file, one
verdict, one tuning surface.

Tiers align with the plan-pricing ladder:
  * **premium**   — $1k+/mo plans; quality first, strict cache
  * **standard**  — default; balanced
  * **economy**   — $50-$500/mo; cost-first, looser cache
  * **free**      — $0/mo; cheapest only, loosest cache

Routing modes that AREN'T plan tiers also live here (`chat`, `batch`,
`auto`) because they share the Pareto-weight shape. They just don't
have cache/escalation knobs.
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass(frozen=True)
class TierConfig:
    """All knobs for one tier OR routing mode."""
    # Pareto weights for provider ranking (router.py). Sums to 1.0.
    pareto_weights: dict
    # Semantic-cache cosine threshold. Higher = stricter match.
    cache_similarity: float = 0.88
    # Cascade escalation threshold on avg-token logprob. Lower (more
    # negative) = more permissive (cheap answers are kept more often).
    escalation_logprob: float = -1.0
    # Plan-name substrings that resolve to this tier. Checked case-
    # insensitively; first match wins (iteration order in TIERS).
    plan_keywords: tuple[str, ...] = field(default_factory=tuple)
    # Minimum model-quality score required for this tier. Candidates
    # scoring below this are FILTERED OUT of the Pareto pool before
    # ranking. This is the "never embarrass a paying customer" knob:
    # premium customers never see a response from a model that scored
    # below 0.92, even if it would be cheaper. Free users get anything
    # above 0.70.
    min_quality_score: float = 0.60
    # Maximum response tokens for trivial prompts on this tier. Prevents
    # a 2-word "hi" from burning a 500-token response. Hard tasks override
    # via explicit max_tokens in the call.
    default_max_tokens_trivial: int = 50


# ── Tier / mode catalogue ────────────────────────────────────────────
# Order matters for resolve_tier_from_plan(): premium keywords win over
# standard, standard over economy, etc. List premium first.

TIERS: dict[str, TierConfig] = {
    "premium": TierConfig(
        pareto_weights={"quality": 0.85, "cost": 0.05, "latency": 0.10},
        cache_similarity=0.93,
        escalation_logprob=-0.3,
        plan_keywords=(
            "premium", "enterprise", "unlimited", "infinity",
            "titan", "vanguard", "apex", "elite", "corporate",
        ),
        min_quality_score=0.92,              # Opus / GPT-5.2 / Claude Sonnet floor
        default_max_tokens_trivial=150,      # let Opus be expressive even on short prompts
    ),
    "standard": TierConfig(
        pareto_weights={"quality": 0.45, "cost": 0.35, "latency": 0.20},
        cache_similarity=0.88,
        escalation_logprob=-1.0,
        plan_keywords=(
            "standard", "professional", "advanced", "business", "agency", "studio",
        ),
        min_quality_score=0.82,              # GPT-4o / Sonnet / Llama-70B class
        default_max_tokens_trivial=100,
    ),
    "economy": TierConfig(
        pareto_weights={"quality": 0.20, "cost": 0.70, "latency": 0.10},
        cache_similarity=0.84,
        escalation_logprob=-1.8,
        plan_keywords=("economy", "basic", "essential"),
        min_quality_score=0.72,              # Llama-8B / Mistral-7B / Gemini-Flash floor
        default_max_tokens_trivial=80,
    ),
    "free": TierConfig(
        pareto_weights={"quality": 0.20, "cost": 0.70, "latency": 0.10},
        cache_similarity=0.82,
        escalation_logprob=-2.2,
        plan_keywords=("free", "starter", "trial"),
        min_quality_score=0.65,              # anything coherent is fine
        default_max_tokens_trivial=50,
    ),
    # Routing-only modes — share pareto shape but no caching / cascade knobs
    "chat":  TierConfig(pareto_weights={"quality": 0.40, "cost": 0.20, "latency": 0.40}),
    "batch": TierConfig(pareto_weights={"quality": 0.50, "cost": 0.50, "latency": 0.00}),
    "auto":  TierConfig(pareto_weights={"quality": 0.45, "cost": 0.35, "latency": 0.20}),
}


DEFAULT_TIER = "standard"


# ── Accessors ────────────────────────────────────────────────────────

def get_tier(name: str | None) -> TierConfig:
    """Look up a tier config; unknown names fall through to 'standard'."""
    return TIERS.get((name or "").lower(), TIERS[DEFAULT_TIER])


def resolve_tier_from_plan(plan_name: str | None) -> str:
    """Map a plan label (eg 'MAARS Business Plus', 'Free tier') to one of
    the four pricing tiers. Case-insensitive substring match; order of
    TIERS decides precedence when a plan happens to match multiple sets."""
    if not plan_name:
        return DEFAULT_TIER
    plan = plan_name.lower()
    for tier, cfg in TIERS.items():
        # Skip mode-only entries (they have no plan_keywords)
        if not cfg.plan_keywords:
            continue
        if any(kw in plan for kw in cfg.plan_keywords):
            return tier
    return DEFAULT_TIER


def cache_similarity(tier: str | None) -> float:
    return get_tier(tier).cache_similarity


def escalation_logprob(tier: str | None) -> float:
    return get_tier(tier).escalation_logprob


def pareto_weights(mode_or_tier: str | None) -> dict:
    return dict(get_tier(mode_or_tier).pareto_weights)


def min_quality(tier: str | None) -> float:
    """Minimum model-quality score this tier will accept. Used by the
    router to filter candidates before Pareto ranking — a premium
    customer never sees a response from a model below 0.92."""
    return get_tier(tier).min_quality_score


def max_tokens_trivial(tier: str | None) -> int:
    """Cap for trivial prompts on this tier — prevents 'hi' → 500-token
    response burning credits for nothing."""
    return get_tier(tier).default_max_tokens_trivial
