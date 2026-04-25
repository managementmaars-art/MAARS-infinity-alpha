"""
MAARS provider registry — pluggable adapters over the Universal Gateway.

Each adapter implements `BaseProvider.execute_chat_completion`, `estimate_usage`,
and `health_check`. v1_gateway and router_scoring both resolve providers through
the registry so the call path is uniform.

Registry entries are created lazily so missing API keys don't crash startup —
a provider is simply marked `available=False` until its env key is set.
"""
from __future__ import annotations

import os
from typing import Optional

from .base_provider import BaseProvider, HealthStatus, UsageEstimate
from .anthropic_provider import AnthropicProvider
from .deepseek_provider import DeepSeekProvider
from .groq_provider import GroqProvider
from .openai_provider import OpenAIProvider

_PROVIDERS: dict[str, BaseProvider] = {}


def _register_defaults() -> None:
    _PROVIDERS["openai"] = OpenAIProvider(api_key=os.environ.get("OPENAI_API_KEY", ""))
    _PROVIDERS["anthropic"] = AnthropicProvider(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))
    _PROVIDERS["groq"] = GroqProvider(api_key=os.environ.get("GROQ_API_KEY", ""))
    _PROVIDERS["deepseek"] = DeepSeekProvider(api_key=os.environ.get("DEEPSEEK_API_KEY", ""))


_register_defaults()


def get_provider(slug: str) -> Optional[BaseProvider]:
    """Return the provider adapter for `slug` ('openai', 'anthropic', …) or None."""
    return _PROVIDERS.get(slug.lower())


def list_providers() -> list[BaseProvider]:
    return list(_PROVIDERS.values())


__all__ = [
    "BaseProvider",
    "HealthStatus",
    "UsageEstimate",
    "get_provider",
    "list_providers",
]
