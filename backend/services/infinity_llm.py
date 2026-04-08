"""MAARS Infinity — LLM Interface.
Lightweight wrapper for Infinity subsystems to call LLMs via the existing service.
Supports all 33 providers with smart routing, auto-selection and fallback chain."""

import uuid
import time
import logging
from shared.constants import EMERGENT_LLM_KEY

logger = logging.getLogger(__name__)

# Map router model names → (provider, model_id) for convenience lookups
ROUTER_MODEL_MAP = {
    # OpenAI
    "gpt-5.2":              ("openai",     "gpt-5.2"),
    "gpt-4.1":              ("openai",     "gpt-4.1"),
    "gpt-4.1-mini":         ("openai",     "gpt-4.1-mini"),
    "gpt-4.1-nano":         ("openai",     "gpt-4.1-nano"),
    "gpt-4o":               ("openai",     "gpt-4o"),
    "gpt-4o-mini":          ("openai",     "gpt-4o-mini"),
    "o4":                   ("openai",     "o4"),
    "o4-mini":              ("openai",     "o4-mini"),
    "o3":                   ("openai",     "o3"),
    "o3-mini":              ("openai",     "o3-mini"),
    # Anthropic
    "claude-opus-4-6":      ("anthropic",  "claude-opus-4-6-20260101"),
    "claude-sonnet-4-6":    ("anthropic",  "claude-sonnet-4-6-20260101"),
    "claude-sonnet-4.5":    ("anthropic",  "claude-sonnet-4-5-20250929"),
    "claude-opus-4.5":      ("anthropic",  "claude-opus-4-5-20251101"),
    "claude-haiku-4.5":     ("anthropic",  "claude-haiku-4-5-20251001"),
    # Google Gemini
    "gemini-2.5-pro":       ("gemini",     "gemini-2.5-pro-preview"),
    "gemini-2.5-flash":     ("gemini",     "gemini-2.5-flash-preview"),
    "gemini-2.5-flash-lite":("gemini",     "gemini-2.5-flash-lite-preview"),
    "gemini-3-flash":       ("gemini",     "gemini-3-flash-preview"),
    "gemini-3-pro":         ("gemini",     "gemini-3-pro-preview"),
    # xAI
    "grok-3":               ("xai",        "grok-3"),
    "grok-3-mini":          ("xai",        "grok-3-mini"),
    "grok-2":               ("xai",        "grok-2"),
    # DeepSeek
    "deepseek-v3":          ("deepseek",   "deepseek-chat"),
    "deepseek-r1":          ("deepseek",   "deepseek-reasoner"),
    "deepseek-chat":        ("deepseek",   "deepseek-chat"),
    "deepseek-reasoner":    ("deepseek",   "deepseek-reasoner"),
    # Mistral
    "mistral-large":        ("mistral",    "mistral-large-latest"),
    "mistral-medium":       ("mistral",    "mistral-medium-latest"),
    "mistral-small":        ("mistral",    "mistral-small-latest"),
    "codestral":            ("mistral",    "codestral-latest"),
    "mistral-nemo":         ("mistral",    "open-mistral-nemo"),
    # Perplexity
    "sonar-pro":            ("perplexity", "sonar-pro"),
    "sonar":                ("perplexity", "sonar"),
    "sonar-reasoning-pro":  ("perplexity", "sonar-reasoning-pro"),
    "sonar-deep-research":  ("perplexity", "sonar-deep-research"),
    # Cohere
    "command-a":            ("cohere",     "command-a-03-2025"),
    "command-r-plus":       ("cohere",     "command-r-plus"),
    "command-r":            ("cohere",     "command-r"),
    # Groq
    "llama-4-scout":        ("groq",       "llama-4-scout-17b-16e-instruct"),
    "llama-4-maverick":     ("groq",       "llama-4-maverick-17b-128e-instruct"),
    "llama-3.3-70b":        ("groq",       "llama-3.3-70b-versatile"),
    # Cerebras
    "cerebras-llama-3.3":   ("cerebras",   "llama-3.3-70b"),
    "cerebras-llama-3.1":   ("cerebras",   "llama-3.1-70b"),
    # Together AI
    "together-llama-4":     ("together",   "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8"),
    "together-deepseek-r1": ("together",   "deepseek-ai/DeepSeek-R1"),
    # Fireworks AI
    "fw-llama-4":           ("fireworks",  "accounts/fireworks/models/llama-v3p1-405b-instruct"),
    "fw-deepseek-v3":       ("fireworks",  "accounts/fireworks/models/deepseek-v3"),
    # AI21
    "jamba-1.6-large":      ("ai21",       "jamba-1.6-large"),
    "jamba-1.6-mini":       ("ai21",       "jamba-1.6-mini"),
    # SambaNova
    "samba-llama-4":        ("sambanova",  "Meta-Llama-4-Maverick-17B-128E-Instruct"),
    "samba-deepseek-r1":    ("sambanova",  "DeepSeek-R1-0528"),
    # Minimax AI
    "minimax-text-01":      ("minimax",    "minimax-text-01"),
    # Nvidia NIM
    "nemotron-ultra":       ("nvidia",     "nvidia/llama-3.1-nemotron-ultra-253b-v1"),
    "nemotron-super":       ("nvidia",     "nvidia/llama-3.3-nemotron-super-49b-v1"),
    # Moonshot (Kimi)
    "kimi-latest":          ("moonshot",   "moonshot-v1-auto"),
    "kimi-128k":            ("moonshot",   "moonshot-v1-128k"),
    # Qwen / Alibaba
    "qwen-max":             ("qwen",       "qwen-max"),
    "qwen-plus":            ("qwen",       "qwen-plus"),
    "qwq-32b":              ("qwen",       "qwq-32b"),
}

# Ordered fallback chain — best quality first, economical providers at the end
FALLBACK_CHAIN = [
    ("openai",     "gpt-4.1"),
    ("anthropic",  "claude-sonnet-4-6-20260101"),
    ("gemini",     "gemini-2.5-flash-preview"),
    ("deepseek",   "deepseek-chat"),
    ("groq",       "llama-4-scout-17b-16e-instruct"),
    ("cerebras",   "llama-3.3-70b"),
    ("mistral",    "mistral-small-latest"),
    ("cohere",     "command-r"),
    ("together",   "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8"),
    ("xai",        "grok-3-mini"),
    ("qwen",       "qwen-plus"),
]


async def call(
    prompt: str,
    system_message: str = "You are a helpful AI assistant.",
    model_name: str = None,
    provider: str = None,
    max_retries: int = 3,
):
    """Call an LLM with auto-selection and fallback chain across all 33 providers.
    Returns dict: {response, provider, model, latency_ms}"""
    from services.llm_service import call_direct_llm
    from shared.utils import get_api_keys

    api_keys = await get_api_keys()

    # Build candidate chain
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
    attempts = 0
    for prov, model_id in chain:
        if attempts >= max_retries + 1:
            break

        key = api_keys.get(prov, "")
        if not key:
            # Try EMERGENT_LLM_KEY as last resort for openai/anthropic/gemini
            if prov in ("openai", "anthropic", "gemini") and EMERGENT_LLM_KEY:
                key = EMERGENT_LLM_KEY
            else:
                continue

        attempts += 1
        try:
            start = time.time()
            response = await call_direct_llm(
                provider=prov,
                model_name=model_id,
                system_prompt=system_message,
                content=prompt,
                attachments=[],
                api_key=key,
            )
            latency_ms = int((time.time() - start) * 1000)

            return {
                "response": response,
                "provider": prov,
                "model": model_id,
                "latency_ms": latency_ms,
                "attempt": attempts,
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
