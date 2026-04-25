"""Single source of truth for which providers are 'free tier'.

Before this module existed, at least 6 places in the codebase defined
their own FREE_PROVIDERS set — admin.py had two, admin_metrics.py had
one, blended_cost.py had one, llm_gateway.py had one, provider_balance.py
had one. Each list subtly disagreed, which is why the Cost Health
dashboard said 83.32% free absorption while the Pricing Manager tab
said 99%: same traffic, different classification.

Use `FREE_PROVIDERS` from this module everywhere. Add a provider here
when you wire a free-tier adapter (not when you wire the signup page).

Criteria for inclusion: the provider has a publicly-advertised free
quota that's usable at production volumes (>= 100 req/day) without a
credit card.
"""
from __future__ import annotations

FREE_PROVIDERS: frozenset[str] = frozenset({
    "groq",              # 14,400 req/day free
    "gemini",            # 1,500 req/day free (alias for google)
    "google",            # same underlying quota as gemini
    "cerebras",          # 30M tokens/month free
    "sambanova",         # 500 req/day free
    "nvidia",            # 1,000 req/day free (alias for nvidia_nim)
    "nvidia_nim",        # same
    "huggingface",       # free inference API (rate-limited)
    "together",          # $1 free signup credit — limited free tier
    "fireworks",         # 500 req/day free
    "openrouter_free",   # 200 req/day on :free-suffix models
    "novita",            # generous free credits on signup
    "mistral",           # free tier (experimental)
})


def is_free(provider: str) -> bool:
    """Case-insensitive membership check."""
    return (provider or "").lower() in FREE_PROVIDERS
