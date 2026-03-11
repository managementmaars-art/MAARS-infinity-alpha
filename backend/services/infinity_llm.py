"""MAARS Infinity — LLM Interface.
Lightweight wrapper for Infinity subsystems to call LLMs via the existing service.
Supports auto-selection and the router's model selection."""

import uuid
import time
import logging
from datetime import datetime, timezone
from shared.constants import EMERGENT_LLM_KEY

logger = logging.getLogger(__name__)

# Map router model names → emergentintegrations (provider, model_id)
ROUTER_MODEL_MAP = {
    "gpt-5.2": ("openai", "gpt-5.2"),
    "gpt-4o": ("openai", "gpt-4o"),
    "gpt-4o-mini": ("openai", "gpt-4o-mini"),
    "o3": ("openai", "o3"),
    "claude-sonnet-4.5": ("anthropic", "claude-sonnet-4-5-20250929"),
    "claude-opus-4.5": ("anthropic", "claude-opus-4-5-20251101"),
    "claude-haiku-4.5": ("anthropic", "claude-haiku-4-5-20251001"),
    "gemini-3-flash": ("gemini", "gemini-3-flash-preview"),
    "gemini-3-pro": ("gemini", "gemini-3-pro-preview"),
}

FALLBACK_CHAIN = [
    ("openai", "gpt-5.2"),
    ("anthropic", "claude-sonnet-4-5-20250929"),
    ("gemini", "gemini-3-flash-preview"),
]


async def call(
    prompt: str,
    system_message: str = "You are a helpful AI assistant.",
    model_name: str = None,
    provider: str = None,
    max_retries: int = 2,
):
    """Call an LLM with auto-selection and fallback chain.
    Returns dict: {response, provider, model, latency_ms}"""
    from emergentintegrations.llm.chat import LlmChat, UserMessage

    api_key = EMERGENT_LLM_KEY
    if not api_key:
        raise RuntimeError("EMERGENT_LLM_KEY not set")

    chain = []
    if model_name:
        mapped = ROUTER_MODEL_MAP.get(model_name)
        if mapped:
            chain.append(mapped)
        elif provider:
            chain.append((provider, model_name))

    for fb in FALLBACK_CHAIN:
        if fb not in chain:
            chain.append(fb)

    last_error = None
    for attempt, (prov, model_id) in enumerate(chain[:max_retries + 1]):
        session_id = f"infinity_{uuid.uuid4().hex[:10]}"
        try:
            chat = LlmChat(
                api_key=api_key,
                session_id=session_id,
                system_message=system_message,
            ).with_model(prov, model_id)

            start = time.time()
            response = await chat.send_message(UserMessage(text=prompt))
            latency_ms = int((time.time() - start) * 1000)

            return {
                "response": response,
                "provider": prov,
                "model": model_id,
                "latency_ms": latency_ms,
                "attempt": attempt + 1,
            }
        except Exception as e:
            last_error = str(e)
            logger.warning(f"Infinity LLM failed ({prov}/{model_id}): {e}")
            continue

    raise RuntimeError(f"All providers failed: {last_error}")


async def call_json(
    prompt: str,
    system_message: str = "You are a helpful AI assistant. Always respond with valid JSON only, no markdown.",
    model_name: str = None,
):
    """Call LLM and parse response as JSON."""
    import json
    result = await call(prompt, system_message, model_name)
    text = result["response"].strip()

    if text.startswith("```"):
        lines = text.split("\n")
        lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            parsed = json.loads(text[start:end])
        else:
            start = text.find("[")
            end = text.rfind("]") + 1
            if start >= 0 and end > start:
                parsed = json.loads(text[start:end])
            else:
                raise ValueError(f"Could not parse JSON: {text[:200]}")

    result["parsed"] = parsed
    return result
