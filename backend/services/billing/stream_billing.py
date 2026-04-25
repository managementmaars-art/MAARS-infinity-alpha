"""Streaming billing + stream-to-cache normalization.

Server-Sent-Events (SSE) chat completions are the default UX for any
serious chat product. Two things the naive streaming path gets wrong:

  1. BILLING — we reserve credits up front, then what? Naive impls
     either (a) settle at stream-close with ZERO idea how many tokens
     actually came out (the `usage` field is often missing on stream
     responses, or arrives only in the final `[DONE]` chunk), or
     (b) burn the full reserved amount regardless of actual output.
     Both are wrong. We want the TRUE output-token count and settle
     at the actual cost.

  2. CACHE — since we didn't see the full response until the stream
     ended, we skip semantic_cache.store(). That means no warm hits
     ever on streaming responses — which is most of them. We fix
     this by accumulating the stream into a buffer and calling
     semantic_cache.store() on stream-close with the assembled text.

This module wraps a provider SSE generator and returns an enhanced
generator that:
  - Passes chunks through unchanged to the client.
  - Extracts token counts from `usage` chunks when providers send them
    (OpenAI, Groq, Cerebras, Fireworks all emit a final usage chunk).
  - Falls back to tiktoken on assembled text if no usage chunk.
  - Fires settle/cache/observability in a `finally` block so we record
    even on client disconnect.

Usage in /v1/chat/completions streaming path:

    async def stream():
        gen = _stream_provider(...)
        async for chunk in stream_billing.wrap(
            gen, user_id=user_id, model=maars_model, provider=provider,
            credits_reserved=credits_estimate, assembled_messages=messages,
        ):
            yield chunk
"""
from __future__ import annotations
import json
import logging
import time
from typing import Any, AsyncIterator

logger = logging.getLogger(__name__)


def _extract_text_chunk(raw: str) -> tuple[str, dict | None]:
    """Return (content_delta, usage_dict_or_None) from a single SSE line."""
    if not raw.startswith("data:"):
        return "", None
    payload = raw[5:].strip()
    if payload == "[DONE]":
        return "", None
    try:
        obj = json.loads(payload)
    except json.JSONDecodeError:
        return "", None
    try:
        delta = obj["choices"][0].get("delta", {}).get("content", "") or ""
    except (KeyError, IndexError, TypeError):
        delta = ""
    usage = obj.get("usage")
    if isinstance(usage, dict) and usage.get("completion_tokens") is not None:
        return delta, usage
    return delta, None


async def wrap(
    source: AsyncIterator[str],
    *,
    user_id: str,
    model: str,
    provider: str,
    native_model: str,
    credits_reserved: int,
    messages: list[dict],
    pricing: dict,
    req_id: str,
    source_tag: str = "stream",
) -> AsyncIterator[str]:
    """Wrap a provider SSE generator with MAARS billing + cache + metrics."""
    assembled: list[str] = []
    reported_usage: dict | None = None
    start = time.time()
    try:
        async for chunk in source:
            try:
                # chunk is already an SSE line like "data: {...}\n\n"
                for line in chunk.split("\n"):
                    if not line:
                        continue
                    delta, usage = _extract_text_chunk(line)
                    if delta:
                        assembled.append(delta)
                    if usage:
                        reported_usage = usage
            except Exception:
                pass
            yield chunk
    finally:
        latency_ms = int((time.time() - start) * 1000)
        full_text = "".join(assembled)
        # Determine completion tokens.
        try:
            from services.token_counter import count_tokens, count_messages
            if reported_usage and reported_usage.get("completion_tokens"):
                ct = int(reported_usage["completion_tokens"])
                pt = int(reported_usage.get("prompt_tokens", 0) or count_messages(messages, provider=provider, model=native_model))
            else:
                ct = count_tokens(full_text, provider=provider, model=native_model) if full_text else 0
                pt = count_messages(messages, provider=provider, model=native_model)
        except Exception:
            ct = max(1, len(full_text) // 4)
            pt = sum(len((m.get("content") or "")) // 4 for m in messages)

        # Wallet settle at actual cost.
        try:
            import math
            from services.billing import wallet_service
            from shared.constants import CREDITS_PER_USD
            from services.pricing_math import token_cost_usd
            act_cost = token_cost_usd(
                prompt_tokens=pt, completion_tokens=ct,
                input_price_per_m=pricing.get("input", 0.003),
                output_price_per_m=pricing.get("output", 0.003),
            )
            credits_actual = min(credits_reserved, max(1, math.ceil(act_cost * CREDITS_PER_USD)))
            await wallet_service.settle(
                user_id, reserved_amount=credits_reserved, actual_amount=credits_actual,
                reference_id=req_id,
                description=f"Stream inference {provider}/{native_model} ({source_tag})",
                metadata={
                    "provider": provider, "native_model": native_model,
                    "latency_ms": latency_ms, "streamed": True,
                    "completion_tokens": ct, "prompt_tokens": pt, "source": source_tag,
                },
            )
        except Exception as exc:
            logger.warning("stream settle failed for %s: %s", req_id, exc)
            credits_actual = credits_reserved

        # Cache the assembled response for future hits. Build an
        # OpenAI-compat response so downstream lookup finds it.
        if full_text:
            try:
                from services import semantic_cache
                fake_resp = {
                    "id": req_id,
                    "choices": [{"index": 0, "message": {"role": "assistant", "content": full_text},
                                 "finish_reason": "stop"}],
                    "usage": {"prompt_tokens": pt, "completion_tokens": ct, "total_tokens": pt + ct},
                    "model": model,
                    "maars": {"source": source_tag, "streamed": True},
                }
                await semantic_cache.store(
                    model=model, messages=messages, response=fake_resp,
                    temperature=None, has_tools=False, stream=False,
                )
            except Exception as exc:
                logger.info("stream cache store failed: %s", exc)

        # Observability.
        try:
            from services import prometheus_metrics as pm
            from services.routing import router as bandit_router
            pm.inc_requests(provider, native_model, source_tag, "ok")
            pm.inc_credits(provider, native_model, source_tag, credits_actual)
            pm.observe_latency(provider, native_model, latency_ms)
            bandit_router.record(
                f"{provider}/{native_model}", success=True,
                latency_ms=latency_ms, credits=credits_actual,
            )
        except Exception:
            pass

        # Usage log row.
        try:
            from db import db
            from datetime import datetime, timezone
            from services.pricing_math import token_cost_usd
            cost_usd = token_cost_usd(
                prompt_tokens=pt, completion_tokens=ct,
                input_price_per_m=pricing.get("input", 0.003),
                output_price_per_m=pricing.get("output", 0.003),
            )
            await db.gateway_usage_logs.insert_one({
                "log_id":       f"gw_stream_{str(user_id)[:8]}_{int(time.time()*1000)}",
                "user_id":      user_id,
                "provider":     provider,
                "native_model": native_model,
                "maars_model":  model,
                "cost_usd":     cost_usd,
                "billed_usd":   cost_usd,
                "latency_ms":   latency_ms,
                "streamed":     True,
                "prompt_tokens":     pt,
                "completion_tokens": ct,
                "credits_charged":   credits_actual,
                "source":       source_tag,
                "timestamp":    datetime.now(timezone.utc).isoformat(),
            })
        except Exception as log_exc:
            logger.info("stream usage log failed: %s", log_exc)
