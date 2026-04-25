"""Prompt-cache helpers — 90% discount on cached prefix tokens.

Anthropic and Gemini both charge 10% (Anthropic) / ~10% (Gemini) of the
usual input-token price for tokens that were already part of a recent
prompt. On long system prompts + tool schemas that a user hits repeatedly,
this is the single biggest margin lever we have.

Anthropic: attach `cache_control: {"type":"ephemeral"}` to the LAST block
of any content segment you want to cache. Min 1024 tokens for Sonnet/Opus
(2048 for Haiku) or it's silently ignored. The cache TTL is 5 minutes,
refreshed on every hit.

Gemini: use the explicit Context Caching API — create a cache resource,
then reference it by name in subsequent calls. Minimum 32768 tokens; TTL
is configurable (default 1h). Too heavy for one-shot chats; use for
long system prompts or knowledge docs only.

OpenAI: prompt caching is automatic since Oct 2024 for prompts >1024
tokens — no markers needed, just structure repeated content at the TOP.
So the optimization there is "don't shuffle the system prompt".

This module:
  - Annotates Anthropic message arrays with cache_control markers.
  - Detects cacheable prefixes (system, tool schemas, stable context).
  - Exposes a heuristic `should_cache(text)` that checks the 1024/2048
    minimum so we don't waste markers on short prompts.
"""
from __future__ import annotations
import logging
from typing import Any

logger = logging.getLogger(__name__)

_ANTHROPIC_MIN_CACHE_TOKENS = 1024      # Sonnet/Opus
_ANTHROPIC_MIN_CACHE_TOKENS_HAIKU = 2048
_GEMINI_MIN_CACHE_TOKENS = 32768


def _rough_tokens(text: str) -> int:
    """Cheap ~token count for the gatekeeping check. We use the accurate
    tiktoken counter only when the rough count says we're close to the
    threshold — avoids loading 100MB encoders for obviously-small prompts."""
    return max(1, len(text) // 4)


def should_cache(text: str, *, provider: str = "anthropic", model: str = "") -> bool:
    """Is this prefix long enough that cache markers are worth attaching?"""
    if not text:
        return False
    rough = _rough_tokens(text)
    if provider == "anthropic":
        threshold = _ANTHROPIC_MIN_CACHE_TOKENS_HAIKU if "haiku" in model.lower() else _ANTHROPIC_MIN_CACHE_TOKENS
        if rough < threshold * 0.7:  # obviously too small
            return False
        if rough > threshold * 1.3:  # obviously big enough
            return True
        try:
            from services.token_counter import count_tokens
            actual = count_tokens(text, provider="anthropic", model=model or "claude-sonnet")
            return actual >= threshold
        except Exception:
            return rough >= threshold
    if provider == "gemini":
        return rough >= _GEMINI_MIN_CACHE_TOKENS
    return False  # OpenAI auto-caches; no marker needed


def annotate_anthropic(messages: list[dict], *, model: str = "claude-sonnet") -> list[dict]:
    """Return a copy of messages with cache_control on the system prompt
    and any stable prefix blocks.

    Rules:
      - System message (if long enough) → always marked.
      - The first user-role block is NOT marked (changes every request).
      - If a single message's content is already a list of blocks, we
        mark the last block that passes the length check.
    """
    if not messages:
        return messages
    out: list[dict] = []
    for msg in messages:
        role = msg.get("role")
        content = msg.get("content")
        if role == "system" and isinstance(content, str) and should_cache(content, provider="anthropic", model=model):
            out.append({
                "role": "system",
                "content": [{
                    "type": "text",
                    "text": content,
                    "cache_control": {"type": "ephemeral"},
                }],
            })
            continue
        if isinstance(content, list) and content:
            # Mark the last text block if it meets the threshold
            blocks = [dict(b) for b in content]
            for b in reversed(blocks):
                if b.get("type") == "text" and should_cache(
                    b.get("text", ""), provider="anthropic", model=model
                ):
                    b["cache_control"] = {"type": "ephemeral"}
                    break
            out.append({**msg, "content": blocks})
            continue
        out.append(msg)
    return out


def annotate(messages: list[dict], *, provider: str, model: str = "") -> list[dict]:
    """Dispatch: annotate messages for the target provider.

    For OpenAI we just return as-is (caching is automatic). For Gemini the
    caching is out-of-band (create cache resource, reference by name) and
    doesn't touch the messages array — the caller handles that via
    `gemini_create_cache()` below. For Anthropic we rewrite content blocks.
    """
    provider = (provider or "").lower()
    if provider == "anthropic":
        return annotate_anthropic(messages, model=model)
    return messages


async def gemini_create_cache(
    *,
    model: str,
    contents: list[dict],
    api_key: str,
    system_instruction: str | None = None,
    ttl_seconds: int = 3600,
    display_name: str = "maars-cache",
) -> str | None:
    """Create a Gemini explicit cache. Returns the cache resource name
    (`cachedContents/...`) which you then pass as `cachedContent` on the
    generateContent call. Returns None on failure — caller falls through
    to a normal uncached call.
    """
    import httpx
    url = f"https://generativelanguage.googleapis.com/v1beta/cachedContents?key={api_key}"
    body: dict[str, Any] = {
        "model": f"models/{model}",
        "contents": contents,
        "ttl": f"{ttl_seconds}s",
        "displayName": display_name,
    }
    if system_instruction:
        body["systemInstruction"] = {"parts": [{"text": system_instruction}]}
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(url, json=body)
            r.raise_for_status()
            return r.json().get("name")
    except Exception as exc:
        logger.info("gemini cache create failed: %s", exc)
        return None


def extract_cache_savings(usage: dict) -> dict[str, int]:
    """Pull cached-token fields out of a provider response's usage block.

    Anthropic reports cache_creation_input_tokens + cache_read_input_tokens;
    OpenAI reports prompt_tokens_details.cached_tokens; Gemini reports
    cachedContentTokenCount. Normalize into one shape for our usage logs."""
    if not usage:
        return {"cache_read": 0, "cache_write": 0}
    cache_read = (
        usage.get("cache_read_input_tokens")
        or (usage.get("prompt_tokens_details") or {}).get("cached_tokens")
        or usage.get("cachedContentTokenCount")
        or 0
    )
    cache_write = usage.get("cache_creation_input_tokens") or 0
    return {"cache_read": int(cache_read or 0), "cache_write": int(cache_write or 0)}
