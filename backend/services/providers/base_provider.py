"""Abstract provider interface — every concrete adapter must implement this."""
from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import Any, Optional


@dataclass(frozen=True)
class UsageEstimate:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost_usd: float


@dataclass(frozen=True)
class HealthStatus:
    provider: str
    healthy: bool
    latency_ms: Optional[int] = None
    detail: str = ""


class BaseProvider(abc.ABC):
    """
    Thin, typed contract over an LLM provider.

    Implementations are expected to be:
      - async, I/O-bound
      - stateless (configuration via constructor)
      - safe to call concurrently
      - defensive: never raise on expected provider errors, convert to a
        structured HealthStatus(healthy=False, detail=...) instead.
    """

    slug: str = ""
    display_name: str = ""

    def __init__(self, *, api_key: str = "", base_url: Optional[str] = None, timeout: float = 30.0):
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout

    @property
    def available(self) -> bool:
        """True when the provider can be called (api_key configured)."""
        return bool(self.api_key)

    # ---------------------------------------------------------------- contract

    @abc.abstractmethod
    async def execute_chat_completion(
        self,
        *,
        model: str,
        messages: list[dict[str, Any]],
        params: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Fire a chat completion. Return the provider's raw OpenAI-compatible
        response dict. MUST raise on failure so callers (v1_gateway's
        `_call_with_fallback`) can select an alternate route and refund the
        wallet reserve.
        """

    @abc.abstractmethod
    async def estimate_usage(
        self,
        *,
        model: str,
        messages: list[dict[str, Any]],
        max_output_tokens: int = 512,
    ) -> UsageEstimate:
        """
        Cheap local estimate (no API call) used before reserving credits.
        Conservative: over-estimate rather than under.
        """

    @abc.abstractmethod
    async def health_check(self) -> HealthStatus:
        """
        Lightweight reachability + auth check. Prefer a no-cost endpoint such
        as GET /v1/models. MUST NOT raise — return HealthStatus(healthy=False, ...).
        """
