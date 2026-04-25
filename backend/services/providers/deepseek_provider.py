"""DeepSeek provider adapter — OpenAI-compatible, cheap reasoning models."""
from __future__ import annotations

import time
from typing import Any, Optional

import httpx

from .base_provider import BaseProvider, HealthStatus, UsageEstimate


class DeepSeekProvider(BaseProvider):
    slug = "deepseek"
    display_name = "DeepSeek (Economy Reasoning)"

    def __init__(self, *, api_key: str = "", base_url: Optional[str] = None, timeout: float = 30.0):
        super().__init__(api_key=api_key, base_url=base_url or "https://api.deepseek.com", timeout=timeout)

    async def execute_chat_completion(self, *, model, messages, params=None) -> dict[str, Any]:
        from services.llm_service import call_direct_llm
        sys_prompt = ""
        user_content = ""
        tool_msgs: list = []
        for m in messages:
            if m.get("role") == "system":
                sys_prompt += (m.get("content") or "") + "\n"
            elif m.get("role") == "user":
                user_content = m.get("content") or ""
            else:
                tool_msgs.append(m)
        text = await call_direct_llm("deepseek", model, sys_prompt.strip(), user_content, tool_msgs, self.api_key)
        return {
            "id": f"chatcmpl-{int(time.time()*1000)}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": [{"index": 0, "message": {"role": "assistant", "content": text}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        }

    async def estimate_usage(self, *, model, messages, max_output_tokens=512) -> UsageEstimate:
        from services.llm_service import MODEL_COSTS_MAP
        pricing = MODEL_COSTS_MAP.get(model, {"input": 0.14, "output": 0.28})
        joined = " ".join((m.get("content") or "") for m in messages if isinstance(m.get("content"), str))
        pt = max(int(len(joined.split()) * 1.3), 10)
        ct = int(max_output_tokens)
        cost = round((pricing["input"] * pt + pricing["output"] * ct) / 1_000_000, 8)
        return UsageEstimate(prompt_tokens=pt, completion_tokens=ct, total_tokens=pt + ct, estimated_cost_usd=cost)

    async def health_check(self) -> HealthStatus:
        if not self.available:
            return HealthStatus(provider=self.slug, healthy=False, detail="no api_key configured")
        t0 = time.time()
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as c:
                r = await c.get(f"{self.base_url}/v1/models", headers={"Authorization": f"Bearer {self.api_key}"})
            return HealthStatus(
                provider=self.slug,
                healthy=(200 <= r.status_code < 300),
                latency_ms=int((time.time() - t0) * 1000),
                detail=f"HTTP {r.status_code}",
            )
        except Exception as exc:
            return HealthStatus(provider=self.slug, healthy=False, detail=f"{type(exc).__name__}: {exc}")
