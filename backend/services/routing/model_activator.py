"""Deep model activation — every registered model reachable via routing.

MODEL_REGISTRY has 612 entries across 33 providers; the curated tier
pools in universal.py include only 85. This leaves 527 models dormant:
reachable only via explicit `provider/model` ids, never via maars/auto.

This module closes that gap:

  1. At startup it groups every MODEL_REGISTRY entry by provider.
  2. `deep_candidates_for_tier(tier)` returns every registered model
     whose estimated cost fits the tier, sorted by cost ascending.
  3. `deep_candidates_for_alias(alias)` returns every model that fits
     a maars/* specialist alias (maars/code, maars/vision, etc.) by
     keyword matching on the model id + description.
  4. `activation_report()` tells the admin dashboard how many models
     are live (configured + routable) vs dormant.

The deep pool is used as a LATE FALLBACK by the gateway router so the
curated pools still win when they have a fresh open slot. Only when the
curated pool is saturated do we tap into the deep pool — this preserves
the "best model first" behavior while making every registered model
technically reachable.

HuggingFace passthrough is handled separately in _parse_model_id; any
`huggingface/{org}/{name}` routes to the HF inference API directly, so
all 175,000+ HF models are callable without needing registry entries.
"""
from __future__ import annotations
import logging
import re
from typing import Any

logger = logging.getLogger(__name__)


# Cost heuristics for bucketing models into tiers when we don't have
# explicit cost data. Uses model-id substrings; same prefixes that the
# curated pools use.
_PREMIUM_KEYWORDS = re.compile(
    r"\b(opus|o3|o4|o5|gpt-5|claude-(opus|sonnet-4|sonnet-5)|grok-3|sonar-pro|"
    r"deep-research|reasoning-pro|gpt-5\.[2-9])\b", re.I,
)
_ECONOMY_KEYWORDS = re.compile(
    r"\b(nano|mini|flash|small|tiny|8b|9b|haiku|-lite|nemo|turbo|"
    r"instant|gemma|phi-4|qwen-turbo|command-r\b(?!-plus)|moonshot-v1-8k)\b", re.I,
)
_CODE_KEYWORDS = re.compile(
    r"\b(codestral|code|coder|programmer|devstral)\b", re.I,
)
_VISION_KEYWORDS = re.compile(
    r"\b(vision|multimodal|4o|pixtral|gpt-4-turbo|vl|gemini-(2|3)\.)\b", re.I,
)
_REASONING_KEYWORDS = re.compile(
    r"\b(o[1-9]\b|opus|reasoning|r1|thinking|think|sonar-reasoning|nemotron-ultra)\b", re.I,
)
_SEARCH_KEYWORDS = re.compile(
    r"\b(sonar|perplexity|search|grounded|web)\b", re.I,
)
_FAST_KEYWORDS = re.compile(
    r"\b(flash|instant|turbo|fast|nano|mini|haiku|small|8b|9b)\b", re.I,
)


def _classify_tier_from_id(model_id: str, desc: str = "") -> str:
    """Assign a tier to an unknown model by model-id keyword matching.
    Conservative: if ambiguous, default to 'standard' so we don't
    accidentally send premium customers a cheap model."""
    blob = f"{model_id} {desc}".lower()
    if _PREMIUM_KEYWORDS.search(blob):
        return "premium"
    if _ECONOMY_KEYWORDS.search(blob):
        return "economy"
    return "standard"


def _classify_alias_fit(model_id: str, desc: str = "") -> list[str]:
    """Return the maars/* specialist aliases this model is a good fit for."""
    blob = f"{model_id} {desc}"
    fits = []
    if _CODE_KEYWORDS.search(blob):      fits.append("maars/code")
    if _VISION_KEYWORDS.search(blob):    fits.append("maars/vision")
    if _REASONING_KEYWORDS.search(blob): fits.append("maars/reasoning")
    if _SEARCH_KEYWORDS.search(blob):    fits.append("maars/search")
    if _FAST_KEYWORDS.search(blob):      fits.append("maars/fast")
    return fits


def _load_registry() -> list[tuple]:
    """Pull the registry once at module-load; re-read if hot-reloading."""
    from routes.v1_gateway import MODEL_REGISTRY
    return MODEL_REGISTRY


def deep_candidates_for_tier(tier: str, *, configured_providers: set[str] | None = None) -> list[tuple[str, str]]:
    """Return every registered model classified as this tier, as
    (provider, model_id) pairs. Filters to configured providers when
    given. Sorted by a rough cost heuristic (economy-keyword models first
    inside each tier)."""
    tier = (tier or "").lower()
    registry = _load_registry()
    out: list[tuple[str, str, float]] = []  # (provider, model, score)
    for entry in registry:
        if len(entry) < 3:
            continue
        _, provider, model_id = entry[0], entry[1], entry[2]
        desc = entry[4] if len(entry) >= 5 else ""
        if configured_providers is not None and provider not in configured_providers:
            continue
        my_tier = _classify_tier_from_id(model_id, desc)
        if my_tier != tier:
            continue
        # Very rough sort score: models with -nano / -mini / flash etc. first.
        score = 1 if _ECONOMY_KEYWORDS.search(model_id + desc) else 2
        out.append((provider, model_id, score))
    out.sort(key=lambda t: t[2])
    return [(p, m) for p, m, _ in out]


def deep_candidates_for_alias(alias: str, *, configured_providers: set[str] | None = None) -> list[tuple[str, str]]:
    """Return every registered model matching a maars/* specialist alias."""
    registry = _load_registry()
    out: list[tuple[str, str]] = []
    for entry in registry:
        if len(entry) < 3:
            continue
        _, provider, model_id = entry[0], entry[1], entry[2]
        desc = entry[4] if len(entry) >= 5 else ""
        if configured_providers is not None and provider not in configured_providers:
            continue
        if alias in _classify_alias_fit(model_id, desc):
            out.append((provider, model_id))
    return out


async def _configured_providers() -> set[str]:
    """Return the set of providers with an API key present."""
    try:
        from shared.utils import get_api_keys
        keys = await get_api_keys()
        return {k.lower() for k, v in keys.items() if v}
    except Exception:
        return set()


async def activation_report() -> dict[str, Any]:
    """Report for the admin dashboard: how many models are live vs dormant,
    per provider + per tier."""
    registry = _load_registry()
    configured = await _configured_providers()

    by_provider: dict[str, dict] = {}
    for entry in registry:
        if len(entry) < 3: continue
        provider = entry[1] or ""
        model_id = entry[2] or ""
        if not provider or not model_id:
            continue
        desc = entry[4] if len(entry) >= 5 else ""
        tier = _classify_tier_from_id(model_id, desc)
        aliases = _classify_alias_fit(model_id, desc)
        row = by_provider.setdefault(provider, {
            "provider": provider,
            "configured": provider.lower() in configured,
            "total_models": 0,
            "by_tier": {"economy": 0, "standard": 0, "premium": 0},
            "alias_fit": {"maars/code": 0, "maars/vision": 0, "maars/reasoning": 0,
                          "maars/search": 0, "maars/fast": 0},
            "sample_models": [],
        })
        row["total_models"] += 1
        row["by_tier"][tier] = row["by_tier"].get(tier, 0) + 1
        for a in aliases:
            row["alias_fit"][a] = row["alias_fit"].get(a, 0) + 1
        if len(row["sample_models"]) < 5:
            row["sample_models"].append(model_id)

    total_models = sum(r["total_models"] for r in by_provider.values())
    live_models = sum(r["total_models"] for r in by_provider.values() if r["configured"])
    dormant_by_key = total_models - live_models

    return {
        "total_models":      total_models,
        "configured_providers": len([r for r in by_provider.values() if r["configured"]]),
        "unconfigured_providers": len([r for r in by_provider.values() if not r["configured"]]),
        "live_models":        live_models,
        "dormant_by_missing_key": dormant_by_key,
        "huggingface_passthrough": {
            "enabled": "huggingface" in configured,
            "universe_size": "175,000+ via huggingface/{org}/{model} passthrough",
        },
        "providers": sorted(
            by_provider.values(),
            key=lambda r: (not r["configured"], -r["total_models"]),
        ),
    }


# ── Quality score heuristic ─────────────────────────────────────────
# Estimate a 0..1 quality score for an arbitrary (provider, model)
# pair based on its name. Used by the router's tier-quality filter so
# premium customers never route to budget models. Crude but effective
# at the extremes (Opus vs Llama-8B); fuzzy in the middle-tier.

_QUALITY_BY_KEYWORD = [
    # (regex, score)
    (re.compile(r"opus|gpt-5(\.[2-9])?|o[3-5]\b|claude-sonnet-(4|5)|grok-(4|5)",    re.I), 0.95),
    (re.compile(r"gpt-4\.1\b|gpt-4o\b|sonnet-4|deepseek-r1|qwen3-max|grok-3\b",     re.I), 0.88),
    (re.compile(r"llama-3\.[3-9]-70b|llama-4-maverick|qwen-max|command-(r-)?plus|"
                r"mistral-large|gemini-(2\.5|3)\.pro",                                re.I), 0.85),
    (re.compile(r"gpt-4o-mini|4\.1-mini|claude-haiku|sonar-reasoning|"
                r"gemini-(2|3)\.flash|pixtral-large",                                 re.I), 0.78),
    (re.compile(r"llama-3\.[1-2]-70b|llama-3\.3-70b|nemotron-70b|phi-4|"
                r"mistral-medium|command-r\b|moonshot-v1-32k|gpt-4\.1-nano",          re.I), 0.75),
    (re.compile(r"llama-[34]-scout|qwen3-32b|qwen3-235b|"
                r"mistral-small|codestral|deepseek-v3",                               re.I), 0.70),
    (re.compile(r"llama-3\.[12]-8b|llama-3\.1-8b-instant|gemma2-9b|qwen-turbo|"
                r"mistral-nemo|gemini-(2|3)\.flash-lite|phi-3|gpt-3\.5",              re.I), 0.65),
    (re.compile(r"0\.5b|1b|3b|-tiny|llama-guard|moderation",                          re.I), 0.55),
]


def quality_estimate_for(provider: str, model_id: str) -> float:
    """Estimate 0..1 quality score for a (provider, model) pair.
    Defaults to 0.70 for unknown models (safe middle-of-road)."""
    if not model_id:
        return 0.70
    text = f"{provider} {model_id}"
    for pat, score in _QUALITY_BY_KEYWORD:
        if pat.search(text):
            return score
    return 0.70


def all_configured_candidates(configured_providers: set[str]) -> list[tuple[str, str]]:
    """Flat list of every (provider, model) pair from the registry whose
    provider has a key configured. Used as the absolute-last-resort
    fallback in the router — guarantees we never say 'no candidates'
    just because the curated pools were saturated."""
    registry = _load_registry()
    out = []
    for entry in registry:
        if len(entry) < 3: continue
        if entry[1].lower() in configured_providers:
            out.append((entry[1], entry[2]))
    return out
