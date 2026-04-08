"""MAARS Universal API — OpenRouter-style developer gateway.

Mounted at /v1/ — fully OpenAI SDK-compatible.
Auth: Authorization: Bearer maars-sk-<hex>   (no JWT required)

Total models accessible: 175,609+
  • 609 curated models across 33 direct providers
  • 175,000+ open-source models via HuggingFace pass-through

Model addressing (OpenRouter style):
  openai/gpt-4.1                          → OpenAI GPT-4.1
  anthropic/claude-sonnet-4-6             → Anthropic Claude Sonnet 4.6
  google/gemini-2.5-flash                 → Google Gemini 2.5 Flash
  huggingface/meta-llama/Llama-3.1-70B-Instruct → Any of 175,000+ HF models
  maars/auto                              → Smart router picks best model
  maars/smart                             → Task-classified routing
  maars/economy                           → Economy tier best option
  maars/standard                          → Standard tier best option
  maars/premium                           → Premium tier best option

Endpoints:
  POST /v1/chat/completions   — Chat (streaming + non-streaming)
  GET  /v1/models             — Full model registry (+ HF pass-through note)
  GET  /v1/models/{model_id}  — Single model card
  GET  /v1/usage              — Key spend & budget
  GET  /v1/rate-limits        — Key rate limit status
"""

import time
import json
import logging
import asyncio
from datetime import datetime, timezone
from typing import Optional, List, AsyncIterator

import httpx
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel

from db import db
from services.llm_service import call_direct_llm, MODEL_COSTS_MAP, MODEL_CREDIT_COSTS
from shared.utils import get_api_keys

logger = logging.getLogger(__name__)
router = APIRouter()


# ─────────────────────────────────────────────────────────────────────────────
# KEY AUTHENTICATION
# ─────────────────────────────────────────────────────────────────────────────

async def _get_key_doc(request: Request) -> dict:
    """Extract and validate MAARS API key from Authorization header."""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail={
            "error": {"message": "Missing Authorization header. Use: Authorization: Bearer maars-sk-...", "type": "auth_error", "code": 401}
        })
    key = auth[7:].strip()
    if not key.startswith("maars-sk-"):
        raise HTTPException(status_code=401, detail={
            "error": {"message": "Invalid key format. MAARS keys begin with 'maars-sk-'", "type": "auth_error", "code": 401}
        })

    doc = await db.client_gateway_keys.find_one({"key": key}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=401, detail={
            "error": {"message": "Invalid API key", "type": "auth_error", "code": 401}
        })
    if doc.get("status") != "active":
        raise HTTPException(status_code=403, detail={
            "error": {"message": f"API key is {doc.get('status', 'inactive')}. Contact your administrator.", "type": "auth_error", "code": 403}
        })
    return doc


async def _check_budget(key_doc: dict) -> tuple:
    """Returns (budget_ok, used_usd, remaining_usd).

    Supports three billing modes:
      subscription (default) — monthly_budget_usd hard cap, reset each cycle
      payg                   — prepaid balance_usd, deducted per call with markup
      hybrid                 — subscription cap first, then PAYG balance for overages
    """
    billing_mode = key_doc.get("billing_mode", "subscription")

    if billing_mode == "payg":
        balance = key_doc.get("balance_usd", 0.0)
        return balance > 0.0, 0.0, round(balance, 6)

    if billing_mode == "hybrid":
        budget  = key_doc.get("monthly_budget_usd", 0.0)
        used    = key_doc.get("used_usd", 0.0)
        balance = key_doc.get("balance_usd", 0.0)
        if budget <= 0:
            return True, used, float("inf")
        remaining_sub = budget - used
        if remaining_sub > 0:
            return True, used, round(remaining_sub, 6)
        # subscription exhausted — fall over to PAYG balance
        return balance > 0.0, used, round(balance, 6)

    # Default: subscription mode
    budget = key_doc.get("monthly_budget_usd", 0.0)
    used   = key_doc.get("used_usd", 0.0)
    if budget <= 0:
        return True, used, float("inf")
    remaining = budget - used
    return remaining > 0, used, round(remaining, 6)


# ─────────────────────────────────────────────────────────────────────────────
# RATE LIMITING  (simple in-memory per key, resets per minute)
# ─────────────────────────────────────────────────────────────────────────────

_RL: dict = {}          # key → (count, window_start)
_RL_WINDOW = 60         # seconds
_RL_DEFAULT_RPM = 60    # requests per minute (admin can override on key doc)


def _check_rate_limit(key: str, rpm_limit: int = _RL_DEFAULT_RPM) -> tuple:
    """Returns (allowed, count, reset_in_seconds)."""
    now = time.time()
    entry = _RL.get(key)
    if not entry or (now - entry[1]) >= _RL_WINDOW:
        _RL[key] = (1, now)
        return True, 1, _RL_WINDOW
    count, start = entry
    if count >= rpm_limit:
        reset_in = int(_RL_WINDOW - (now - start))
        return False, count, reset_in
    _RL[key] = (count + 1, start)
    return True, count + 1, int(_RL_WINDOW - (now - start))


# ─────────────────────────────────────────────────────────────────────────────
# OPENAI-COMPATIBLE STREAMING URLS
# All these providers support the standard SSE streaming format.
# ─────────────────────────────────────────────────────────────────────────────

_OPENAI_COMPAT_STREAM_URLS = {
    "openai":      "https://api.openai.com/v1/chat/completions",
    "xai":         "https://api.x.ai/v1/chat/completions",
    "deepseek":    "https://api.deepseek.com/chat/completions",
    "mistral":     "https://api.mistral.ai/v1/chat/completions",
    "perplexity":  "https://api.perplexity.ai/chat/completions",
    "groq":        "https://api.groq.com/openai/v1/chat/completions",
    "together":    "https://api.together.xyz/v1/chat/completions",
    "fireworks":   "https://api.fireworks.ai/inference/v1/chat/completions",
    "ai21":        "https://api.ai21.com/studio/v1/chat/completions",
    "cerebras":    "https://api.cerebras.ai/v1/chat/completions",
    "sambanova":   "https://api.sambanova.ai/v1/chat/completions",
    "nvidia":      "https://integrate.api.nvidia.com/v1/chat/completions",
    "moonshot":    "https://api.moonshot.cn/v1/chat/completions",
    "qwen":        "https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions",
    "yi":          "https://api.lingyiwanwu.com/v1/chat/completions",
    "zhipu":       "https://open.bigmodel.cn/api/paas/v4/chat/completions",
    "doubao":      "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
    "huggingface": "https://api-inference.huggingface.co/v1/chat/completions",
    "hyperbolic":  "https://api.hyperbolic.xyz/v1/chat/completions",
    "upstage":     "https://api.upstage.ai/v1/chat/completions",
    "llama":       "https://api.llama.com/v1/chat/completions",
    "writer":      "https://api.writer.com/v1/chat",
    "novita":      "https://api.novita.ai/v3/openai/chat/completions",
    "lepton":      "https://llm.lepton.run/api/v1/chat/completions",
    "lambda":      "https://api.lambdalabs.com/v1/chat/completions",
    # ── New direct providers (replacing OpenRouter) ───────────────────────────
    "amazon":    "https://bedrock-runtime.us-east-1.amazonaws.com/v1/chat/completions",
    "minimax":   "https://api.minimaxi.chat/v1/chat/completions",
    "inception": "https://api.inception.ai/v1/chat/completions",
    "arcee":     "https://api.arcee.ai/v1/chat/completions",
}


# ─────────────────────────────────────────────────────────────────────────────
# MODEL REGISTRY  (OpenRouter-style id: "provider/model")
# 609 curated models across 33 providers + 10 MAARS smart routing aliases
# + 175,000+ HuggingFace open-source models via pass-through (huggingface/{org/model})
# Total accessible: 175,609+ models via one MAARS Universal Key
# ─────────────────────────────────────────────────────────────────────────────

# Each entry: (maars_id, provider, model_id, context_length, description)
MODEL_REGISTRY = [

    # ══════════════════════════════════════════════════════════════════════════
    # FRONTIER CLOSED-SOURCE MODELS
    # ══════════════════════════════════════════════════════════════════════════

    # ── OpenAI ───────────────────────────────────────────────────────────────
    ("openai/gpt-4.1",        "openai", "gpt-4.1",        1_000_000, "GPT-4.1 flagship — 1M context, code + analysis"),
    ("openai/gpt-4.1-mini",   "openai", "gpt-4.1-mini",   1_000_000, "GPT-4.1 Mini — fast balanced, 1M context"),
    ("openai/gpt-4.1-nano",   "openai", "gpt-4.1-nano",   1_000_000, "GPT-4.1 Nano — ultra-fast, lowest cost"),
    ("openai/gpt-4o",         "openai", "gpt-4o",           128_000, "GPT-4o — multimodal vision + text"),
    ("openai/gpt-4o-mini",    "openai", "gpt-4o-mini",      128_000, "GPT-4o Mini — economy multimodal"),
    ("openai/o4",             "openai", "o4",               200_000, "o4 — frontier reasoning: math, code, science"),
    ("openai/o4-mini",        "openai", "o4-mini",          200_000, "o4-mini — fast reasoning at reduced cost"),
    ("openai/o3",             "openai", "o3",               200_000, "o3 — advanced reasoning + programming"),
    ("openai/o3-mini",        "openai", "o3-mini",          200_000, "o3-mini — efficient reasoning model"),
    ("openai/o1",             "openai", "o1",               200_000, "o1 — original frontier reasoning model"),
    ("openai/o1-mini",        "openai", "o1-mini",          128_000, "o1-mini — cost-effective reasoning"),
    ("openai/o1-pro",         "openai", "o1-pro",           200_000, "o1-pro — highest capability reasoning"),
    ("openai/gpt-4-turbo",    "openai", "gpt-4-turbo",      128_000, "GPT-4 Turbo — 128K ctx, vision"),
    ("openai/gpt-3.5-turbo",  "openai", "gpt-3.5-turbo",    16_385,  "GPT-3.5 Turbo — cheapest GPT, widely supported"),
    ("openai/gpt-5",            "openai", "gpt-5",            1_000_000, "GPT-5 — OpenAI's frontier multimodal model"),
    ("openai/gpt-5.4",          "openai", "gpt-5.4",          1_000_000, "GPT-5.4 — latest GPT flagship (Feb 2026)"),
    ("openai/gpt-5.4-mini",     "openai", "gpt-5.4-mini",     1_000_000, "GPT-5.4 Mini — fast balanced GPT-5 variant"),
    ("openai/gpt-5.4-nano",     "openai", "gpt-5.4-nano",     1_000_000, "GPT-5.4 Nano — lowest-cost GPT-5 variant"),
    ("openai/o3-pro",           "openai", "o3-pro",             200_000, "o3-pro — maximum compute reasoning, hardest problems"),
    ("openai/o3-deep-research", "openai", "o3-deep-research",   200_000, "o3 Deep Research — multi-step web + doc research"),
    ("openai/o4-mini-deep-research","openai","o4-mini-deep-research",200_000,"o4-mini Deep Research — fast multi-step research"),
    ("openai/gpt-oss-120b",     "openai", "gpt-oss-120b",       200_000, "GPT OSS 120B — OpenAI open-weight 120B model"),
    ("openai/gpt-oss-20b",      "openai", "gpt-oss-20b",        200_000, "GPT OSS 20B — OpenAI open-weight 20B model"),
    ("openai/gpt-4.5-preview",         "openai", "gpt-4.5-preview",           128_000, "GPT-4.5 Preview — incremental update with improved reasoning"),
    ("openai/gpt-4o-2024-11-20",       "openai", "gpt-4o-2024-11-20",         128_000, "GPT-4o Nov 2024 — pinned stable version"),
    ("openai/gpt-4o-2024-08-06",       "openai", "gpt-4o-2024-08-06",         128_000, "GPT-4o Aug 2024 — structured outputs + JSON schema"),
    ("openai/o1-preview",              "openai", "o1-preview",                 128_000, "o1 Preview — original chain-of-thought reasoning"),
    ("openai/chatgpt-4o-latest",       "openai", "chatgpt-4o-latest",          128_000, "ChatGPT-4o Latest — auto-updates to newest GPT-4o"),
    ("openai/gpt-4-0125-preview",      "openai", "gpt-4-0125-preview",         128_000, "GPT-4 Turbo Jan 2025 — pinned preview version"),
    ("openai/gpt-4-32k",               "openai", "gpt-4-32k",                   32_768, "GPT-4 32K — legacy extended context window"),

    # ── Anthropic ────────────────────────────────────────────────────────────
    ("anthropic/claude-opus-4-6",   "anthropic", "claude-opus-4-6",            200_000, "Claude Opus 4.6 — most powerful Claude, research-grade"),
    ("anthropic/claude-sonnet-4-6", "anthropic", "claude-sonnet-4-6",          200_000, "Claude Sonnet 4.6 — best for code, creative, analysis"),
    ("anthropic/claude-haiku-4-5",  "anthropic", "claude-haiku-4-5-20251001",  200_000, "Claude Haiku 4.5 — fastest Claude, very cheap"),
    ("anthropic/claude-3-5-sonnet", "anthropic", "claude-3-5-sonnet-20241022", 200_000, "Claude 3.5 Sonnet — proven code + analysis workhorse"),
    ("anthropic/claude-3-5-haiku",  "anthropic", "claude-3-5-haiku-20241022",  200_000, "Claude 3.5 Haiku — fast budget Claude"),
    ("anthropic/claude-3-opus",     "anthropic", "claude-3-opus-20240229",      200_000, "Claude 3 Opus — legacy flagship, long-form writing"),
    ("anthropic/claude-3-sonnet",      "anthropic", "claude-3-sonnet-20240229",  200_000, "Claude 3 Sonnet — balanced performance, legacy"),
    ("anthropic/claude-3-haiku",       "anthropic", "claude-3-haiku-20240307",   200_000, "Claude 3 Haiku — fastest legacy Claude, very cheap"),
    ("anthropic/claude-opus-4-5",    "anthropic", "claude-opus-4-5-20251101",   200_000, "Claude Opus 4.5 — Nov 2025 flagship, best for agentic coding"),
    ("anthropic/claude-3-7-sonnet",  "anthropic", "claude-3-7-sonnet-20250219", 200_000, "Claude 3.7 Sonnet — released Feb 2025, extended thinking"),

    # ── Google Gemini ─────────────────────────────────────────────────────────
    ("google/gemini-2.5-pro",        "gemini", "gemini-2.5-pro",           2_000_000, "Gemini 2.5 Pro — research + 2M context, multimodal"),
    ("google/gemini-2.5-flash",      "gemini", "gemini-2.5-flash",         1_000_000, "Gemini 2.5 Flash — speed + quality balance"),
    ("google/gemini-2.5-flash-lite", "gemini", "gemini-2.5-flash-lite",    1_000_000, "Gemini 2.5 Flash-Lite — economy Gemini"),
    ("google/gemini-2.0-flash",      "gemini", "gemini-2.0-flash",         1_000_000, "Gemini 2.0 Flash — stable GA, fast multimodal"),
    ("google/gemini-2.0-flash-lite", "gemini", "gemini-2.0-flash-lite",    1_000_000, "Gemini 2.0 Flash-Lite — cheapest Gemini"),
    ("google/gemini-1.5-pro",        "gemini", "gemini-1.5-pro",           2_000_000, "Gemini 1.5 Pro — 2M context long-form analysis"),
    ("google/gemini-1.5-flash",      "gemini", "gemini-1.5-flash",         1_000_000, "Gemini 1.5 Flash — fast 1M context model"),
    ("google/gemini-3-flash",        "gemini", "gemini-3-flash",            1_000_000, "Gemini 3 Flash — Google's next-gen fast model"),
    ("google/gemini-3-pro",          "gemini", "gemini-3-pro",              1_000_000, "Gemini 3 Pro — Google's next-gen flagship"),
    ("google/gemini-3.1-pro",        "gemini", "gemini-3.1-pro",            1_000_000, "Gemini 3.1 Pro — released Feb 2026, latest Google flagship"),
    ("google/gemini-2.5-flash-thinking","gemini", "gemini-2.5-flash-preview-04-17", 1_000_000, "Gemini 2.5 Flash Thinking — reasoning with budget tokens"),
    ("google/gemma-3-27b",             "gemini", "gemma-3-27b-it",              131_072, "Gemma 3 27B — Google open-weight flagship"),
    ("google/gemma-3-12b",             "gemini", "gemma-3-12b-it",              131_072, "Gemma 3 12B — compact Google open model"),
    ("google/gemma-3-4b",              "gemini", "gemma-3-4b-it",               131_072, "Gemma 3 4B — tiny efficient Gemma"),
    ("google/gemma-2-27b",             "gemini", "gemma-2-27b-it",                8_192, "Gemma 2 27B — Google balanced open model"),
    ("google/gemma-3-1b",            "gemini", "gemma-3-1b-it",                 32_768, "Gemma 3 1B — Google's smallest open model"),
    ("google/gemma-3n-e4b",          "gemini", "gemma-3n-e4b-it",               32_768, "Gemma 3n E4B — Gemma nano optimized for edge devices"),
    ("google/gemma-3n-e2b",          "gemini", "gemma-3n-e2b-it",               32_768, "Gemma 3n E2B — ultra-tiny Gemma for mobile/edge"),

    # ── xAI Grok ─────────────────────────────────────────────────────────────
    ("xai/grok-4",                 "xai", "grok-4-0709",               256_000, "Grok-4 — xAI's frontier reasoning model, tool calling + vision"),
    ("xai/grok-4-fast",            "xai", "grok-4-fast-non-reasoning",  256_000, "Grok-4 Fast — high-speed non-reasoning Grok-4"),
    ("xai/grok-4-fast-reasoning",  "xai", "grok-4-fast-reasoning",      256_000, "Grok-4 Fast Reasoning — high-speed chain-of-thought"),
    ("xai/grok-4.1-fast",          "xai", "grok-4.1-fast-non-reasoning",256_000, "Grok-4.1 Fast — latest fast xAI model (2026)"),
    ("xai/grok-4.1-fast-reasoning","xai", "grok-4.1-fast-reasoning",    256_000, "Grok-4.1 Fast Reasoning — latest xAI reasoning (2026)"),
    ("xai/grok-3",                 "xai", "grok-3-beta",                131_072, "Grok-3 — creative long-form reasoning"),
    ("xai/grok-3-mini",            "xai", "grok-3-mini-beta",           131_072, "Grok-3 Mini — affordable Grok"),
    ("xai/grok-2",                 "xai", "grok-2-1212",                131_072, "Grok-2 — stable general-purpose Grok"),
    ("xai/grok-2-vision",          "xai", "grok-2-vision-1212",         131_072, "Grok-2 Vision — multimodal Grok with image understanding"),
    ("xai/grok-4.20",              "xai", "grok-4.20-beta",              256_000, "Grok-4.20 Beta — xAI's latest experimental frontier model"),
    ("xai/grok-code-fast",         "xai", "grok-code-fast-1",            256_000, "Grok Code Fast — xAI's specialized code generation model"),

    # ── DeepSeek ─────────────────────────────────────────────────────────────
    ("deepseek/deepseek-v3",       "deepseek", "deepseek-v3-0324",  128_000, "DeepSeek V3 — best value, code, data, multilingual"),
    ("deepseek/deepseek-r1",       "deepseek", "deepseek-r1-0528",  128_000, "DeepSeek R1 — open-source reasoning champion"),
    ("deepseek/deepseek-chat",     "deepseek", "deepseek-chat",      128_000, "DeepSeek Chat — ultra-cheap general chat"),
    ("deepseek/deepseek-reasoner", "deepseek", "deepseek-reasoner",  128_000, "DeepSeek Reasoner — math + logic specialist"),
    ("deepseek/deepseek-v2.5",         "deepseek", "deepseek-v2.5-0905",       128_000, "DeepSeek V2.5 — previous generation value model"),
    ("deepseek/deepseek-coder-v2",     "deepseek", "deepseek-coder-v2-instruct",128_000, "DeepSeek Coder V2 — enterprise code specialist"),
    ("deepseek/deepseek-r1-zero",      "deepseek", "deepseek-r1-zero",          128_000, "DeepSeek R1 Zero — pure RL reasoning, no SFT"),
    ("deepseek/deepseek-v3.1",           "deepseek", "deepseek-chat",                       128_000, "DeepSeek V3.1 — hybrid V3+R1 thinking/non-thinking (Aug 2025)"),
    ("deepseek/deepseek-v3.2",           "deepseek", "deepseek-v3.2",                       128_000, "DeepSeek V3.2 — latest flagship, improved code + reasoning"),
    ("deepseek/deepseek-r1-0528",        "deepseek", "deepseek-r1-0528",                    128_000, "DeepSeek R1 0528 — May 2025 reasoning snapshot"),
    ("deepseek/deepseek-r1-distill-llama","deepseek","deepseek-r1-distill-llama-70b",        64_000, "DeepSeek R1 Distill Llama 70B — reasoning in Llama body"),
    ("deepseek/deepseek-r1-distill-qwen", "deepseek","deepseek-r1-distill-qwen-32b",         64_000, "DeepSeek R1 Distill Qwen 32B — reasoning in Qwen body"),

    # ── Mistral ───────────────────────────────────────────────────────────────
    ("mistral/mistral-large",  "mistral", "mistral-large-latest",  131_072, "Mistral Large — enterprise reasoning + multilingual"),
    ("mistral/mistral-medium", "mistral", "mistral-medium-latest", 131_072, "Mistral Medium — balanced performance"),
    ("mistral/mistral-small",  "mistral", "mistral-small-latest",  131_072, "Mistral Small — fast and cheap"),
    ("mistral/codestral",      "mistral", "codestral-latest",      256_000, "Codestral — code generation specialist, 256K ctx"),
    ("mistral/pixtral-large",  "mistral", "pixtral-large-latest",  131_072, "Pixtral Large — vision + text multimodal"),
    ("mistral/pixtral-12b",    "mistral", "pixtral-12b-2409",       32_768, "Pixtral 12B — lightweight vision model"),
    ("mistral/mistral-nemo",   "mistral", "mistral-nemo",           128_000, "Mistral Nemo — translation, efficient chat"),
    ("mistral/ministral-8b",   "mistral", "ministral-8b-latest",   131_072, "Ministral 8B — efficient edge model"),
    ("mistral/ministral-3b",   "mistral", "ministral-3b-latest",   131_072, "Ministral 3B — ultra-fast compact model"),
    ("mistral/open-mistral-7b",        "mistral", "open-mistral-7b",             32_768, "Open Mistral 7B — Mistral's foundational open model"),
    ("mistral/open-mixtral-8x7b",      "mistral", "open-mixtral-8x7b",           32_768, "Open Mixtral 8x7B — classic open MoE"),
    ("mistral/open-mixtral-8x22b",     "mistral", "open-mixtral-8x22b",          65_536, "Open Mixtral 8x22B — large open MoE"),
    ("mistral/magistral-medium",       "mistral", "magistral-medium-2506",       131_072, "Magistral Medium — Mistral's reasoning model"),
    ("mistral/mistral-embed",          "mistral", "mistral-embed",                 8_192, "Mistral Embed — sentence embeddings model"),
    ("mistral/mistral-medium-3",     "mistral", "mistral-medium-3-2505",        128_000, "Mistral Medium 3 — May 2025, strong balance of performance"),
    ("mistral/magistral-small",      "mistral", "magistral-small-2506",         128_000, "Magistral Small — open-source 24B reasoning model (Apache 2.0)"),
    ("mistral/devstral",             "mistral", "devstral-latest",              128_000, "Devstral — Mistral's state-of-the-art coding agent model"),
    ("mistral/devstral-small",       "mistral", "devstral-small-2505",          128_000, "Devstral Small — compact 24B coding agent model"),
    ("mistral/mistral-3-small",      "mistral", "mistral-small-3b-latest",      128_000, "Mistral 3 Small (3B) — ultra-compact dense model (Dec 2025)"),
    ("mistral/mistral-large-2512",   "mistral", "mistral-large-2512",           131_072, "Mistral Large 2512 — December 2025 release"),
    ("mistral/mistral-small-3.2",    "mistral", "mistral-small-3.2-24b-instruct",131_072, "Mistral Small 3.2 — 24B improved instruction following"),
    ("mistral/codestral-2508",       "mistral", "codestral-2508",               256_000, "Codestral 2508 — latest code specialist, August 2025"),
    ("mistral/voxtral-small",        "mistral", "voxtral-small-24b-2507",       131_072, "Voxtral Small 24B — Mistral's speech-aware model"),
    ("mistral/ministral-14b",        "mistral", "ministral-14b-2512",           131_072, "Ministral 14B — new edge model, December 2025"),
    ("mistral/devstral-medium",      "mistral", "devstral-medium",              128_000, "Devstral Medium — mid-size coding agent model"),
    ("mistral/mistral-medium-3.1",   "mistral", "mistral-medium-3.1",           131_072, "Mistral Medium 3.1 — improved multimodal medium model"),

    # ── Perplexity (Web-Search Augmented) ─────────────────────────────────────
    ("perplexity/sonar-deep-research", "perplexity", "sonar-deep-research", 127_000, "Sonar Deep Research — multi-step web research + citations"),
    ("perplexity/sonar-pro",           "perplexity", "sonar-pro",           127_000, "Sonar Pro — web search + analysis, grounded answers"),
    ("perplexity/sonar-reasoning-pro", "perplexity", "sonar-reasoning-pro", 127_000, "Sonar Reasoning Pro — reasoning over live web data"),
    ("perplexity/sonar",               "perplexity", "sonar",               127_000, "Sonar — fast web-grounded answers with citations"),

    # ── Cohere ───────────────────────────────────────────────────────────────
    ("cohere/command-a",      "cohere", "command-a-03-2025", 256_000, "Command A — enterprise RAG + tool use, 256K ctx"),
    ("cohere/command-r-plus", "cohere", "command-r-plus",    128_000, "Command R+ — business document analysis"),
    ("cohere/command-r",      "cohere", "command-r",         128_000, "Command R — cost-efficient RAG and document tasks"),
    ("cohere/command-r7b",             "cohere", "command-r7b-12-2024",         128_000, "Command R7B — small fast enterprise Cohere"),
    ("cohere/command-light",           "cohere", "command-light",                  4_096, "Command Light — fastest cheapest Cohere"),
    ("cohere/command",                 "cohere", "command",                        4_096, "Command — original Cohere enterprise model"),

    # ── AI21 Jamba ────────────────────────────────────────────────────────────
    ("ai21/jamba-large", "ai21", "jamba-large-1.7", 256_000, "Jamba Large 1.7 — 256K hybrid SSM-Transformer"),
    ("ai21/jamba-mini",  "ai21", "jamba-mini-1.7",  256_000, "Jamba Mini 1.7 — fast hybrid for everyday tasks"),
    ("ai21/jamba-1.5-large",           "ai21", "jamba-1.5-large",               256_000, "Jamba 1.5 Large — high-quality 256K SSM-Transformer"),
    ("ai21/jamba-1.5-mini",            "ai21", "jamba-1.5-mini",                 256_000, "Jamba 1.5 Mini — faster 256K hybrid model"),

    # ══════════════════════════════════════════════════════════════════════════
    # HIGH-SPEED INFERENCE PLATFORMS
    # ══════════════════════════════════════════════════════════════════════════

    # ── Groq (ultra-fast LPU inference) ───────────────────────────────────────
    ("groq/llama-4-scout",         "groq", "llama-4-scout-17b-16e-instruct",         131_072, "Llama 4 Scout on Groq — ultra-fast 16-expert MoE"),
    ("groq/llama-4-maverick",      "groq", "llama-4-maverick-17b-128e-instruct",     131_072, "Llama 4 Maverick on Groq — 128-expert creative reasoning"),
    ("groq/llama-3.3-70b",        "groq", "llama-3.3-70b-versatile",               128_000, "Llama 3.3 70B on Groq — fast open-source flagship"),
    ("groq/llama-3.2-90b-vision", "groq", "llama-3.2-90b-vision-preview",          128_000, "Llama 3.2 90B Vision on Groq — multimodal"),
    ("groq/llama-3.2-11b-vision", "groq", "llama-3.2-11b-vision-preview",          128_000, "Llama 3.2 11B Vision on Groq — compact vision"),
    ("groq/llama-3.2-3b",         "groq", "llama-3.2-3b-preview",                  128_000, "Llama 3.2 3B on Groq — ultra-fast compact"),
    ("groq/llama-3.1-70b",        "groq", "llama-3.1-70b-versatile",               128_000, "Llama 3.1 70B on Groq — reliable versatile"),
    ("groq/llama-3.1-8b",         "groq", "llama-3.1-8b-instant",                  128_000, "Llama 3.1 8B on Groq — instant sub-second response"),
    ("groq/deepseek-r1-70b",      "groq", "deepseek-r1-distill-llama-70b",         131_072, "DeepSeek-R1 70B on Groq — fast reasoning distillation"),
    ("groq/deepseek-r1-qwen-32b", "groq", "deepseek-r1-distill-qwen-32b",          131_072, "DeepSeek-R1 Qwen-32B on Groq — compact reasoning"),
    ("groq/qwen-qwq-32b",         "groq", "qwen-qwq-32b",                           131_072, "QwQ-32B on Groq — fast reasoning"),
    ("groq/qwen-3-32b",           "groq", "qwen-3-32b",                             131_072, "Qwen3-32B on Groq — fast multilingual reasoning"),
    ("groq/gemma2-9b",            "groq", "gemma2-9b-it",                             8_192, "Gemma 2 9B on Groq — Google compact instruct"),
    ("groq/mistral-saba",         "groq", "mistral-saba-24b",                       131_072, "Mistral Saba 24B on Groq — Arabic + multilingual"),
    ("groq/llama-3.2-1b",              "groq", "llama-3.2-1b-preview",            8_192, "Llama 3.2 1B on Groq — smallest fastest model"),
    ("groq/llama3-70b",                "groq", "llama3-70b-8192",                  8_192, "Llama 3 70B on Groq — classic fast inference"),
    ("groq/llama3-8b",                 "groq", "llama3-8b-8192",                   8_192, "Llama 3 8B on Groq — instant sub-second"),
    ("groq/deepseek-r1-8b",            "groq", "deepseek-r1-distill-llama-8b",   32_768, "DeepSeek-R1 8B on Groq — tiny fast reasoning"),
    ("groq/phi-4-mini",                "groq", "phi-4-mini",                       16_384, "Phi-4 Mini on Groq — Microsoft compact reasoning"),
    ("groq/llama-guard-3-8b",          "groq", "llama-guard-3-8b",                 8_192, "Llama Guard 3 on Groq — content moderation"),
    ("groq/llama-3.2-11b-text",        "groq", "llama-3.2-11b-text-preview",      128_000, "Llama 3.2 11B Text on Groq — mid-size fast model"),
    ("groq/qwen-2.5-7b",               "groq", "qwen-2.5-7b",                      32_768, "Qwen2.5-7B on Groq — compact multilingual"),
    ("groq/gpt-oss-120b",            "groq", "gpt-oss-120b",                    131_072, "GPT OSS 120B on Groq — OpenAI open-weight via Groq LPU"),
    ("groq/gpt-oss-20b",             "groq", "gpt-oss-20b",                     131_072, "GPT OSS 20B on Groq — OpenAI compact open-weight"),

    # ── Cerebras (fastest AI inference on earth) ──────────────────────────────
    ("cerebras/llama-3.3-70b", "cerebras", "llama-3.3-70b",  131_072, "Llama 3.3 70B on Cerebras — sub-second 70B"),
    ("cerebras/llama-3.1-70b", "cerebras", "llama-3.1-70b",  131_072, "Llama 3.1 70B on Cerebras — blazing fast"),
    ("cerebras/llama-3.1-8b",  "cerebras", "llama-3.1-8b",   131_072, "Llama 3.1 8B on Cerebras — fastest 8B globally"),
    ("cerebras/qwen-3-32b",    "cerebras", "qwen-3-32b",      131_072, "Qwen3-32B on Cerebras — fast multilingual reasoning"),
    ("cerebras/qwen-3-8b",     "cerebras", "qwen-3-8b",       131_072, "Qwen3-8B on Cerebras — compact fast multilingual"),
    ("cerebras/llama-3.2-3b",          "cerebras", "llama-3.2-3b",               8_192, "Llama 3.2 3B on Cerebras — tiny ultra-fast"),
    ("cerebras/deepseek-r1-70b",       "cerebras", "deepseek-r1-distill-llama-70b", 32_768, "DeepSeek-R1 70B on Cerebras — fast reasoning"),
    ("cerebras/llama-3.1-405b",        "cerebras", "llama-3.1-405b",               131_072, "Llama 3.1 405B on Cerebras — ultra-fast 405B"),
    ("cerebras/deepseek-r1-8b",        "cerebras", "deepseek-r1-distill-llama-8b",  32_768, "DeepSeek-R1 8B on Cerebras — tiny fast reasoning"),
    ("cerebras/qwen-2.5-coder-32b",    "cerebras", "qwen-2.5-coder-32b",            32_768, "Qwen2.5-Coder-32B on Cerebras — fast code model"),
    ("cerebras/gpt-oss-120b",        "cerebras", "gpt-oss-120b",                131_072, "GPT OSS 120B on Cerebras — OpenAI open-weight at wafer speed"),
    ("cerebras/qwen3-235b-thinking", "cerebras", "qwen3-235b-thinking",          40_960, "Qwen3-235B Thinking on Cerebras — massive fast reasoning"),
    ("cerebras/glm-4.7",             "cerebras", "glm-4.7",                     128_000, "GLM-4.7 on Cerebras — Zhipu frontier model at high speed"),

    # ── Hyperbolic (fast open-source GPU hosting) ──────────────────────────────
    ("hyperbolic/llama-3.3-70b",  "hyperbolic", "meta-llama/Llama-3.3-70B-Instruct",          128_000, "Llama 3.3 70B on Hyperbolic — fast open-source"),
    ("hyperbolic/llama-3.1-405b", "hyperbolic", "meta-llama/Meta-Llama-3.1-405B-Instruct",    128_000, "Llama 3.1 405B on Hyperbolic — massive open model"),
    ("hyperbolic/deepseek-r1",    "hyperbolic", "deepseek-ai/DeepSeek-R1-hyperbolic",         128_000, "DeepSeek-R1 on Hyperbolic — fast reasoning"),
    ("hyperbolic/qwen-2.5-72b",   "hyperbolic", "Qwen/Qwen2.5-72B-Instruct-hyperbolic",       128_000, "Qwen2.5-72B on Hyperbolic — fast multilingual"),
    ("hyperbolic/deepseek-v3",         "hyperbolic", "deepseek-ai/DeepSeek-V3-0324",               128_000, "DeepSeek-V3 on Hyperbolic — value model"),
    ("hyperbolic/llama-3.1-70b",       "hyperbolic", "meta-llama/Meta-Llama-3.1-70B-Instruct",     128_000, "Llama 3.1 70B on Hyperbolic — fast"),
    ("hyperbolic/qwen3-72b",           "hyperbolic", "Qwen/Qwen3-72B",                              128_000, "Qwen3-72B on Hyperbolic — reasoning"),
    ("hyperbolic/hermes-3-405b",       "hyperbolic", "NousResearch/Hermes-3-Llama-3.1-405B",       128_000, "Hermes 3 405B on Hyperbolic — RLHF tuned"),

    # ══════════════════════════════════════════════════════════════════════════
    # MULTI-MODEL OPEN-SOURCE PLATFORMS
    # ══════════════════════════════════════════════════════════════════════════

    # ── Together AI ───────────────────────────────────────────────────────────
    ("together/llama-4-maverick",     "together", "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8", 131_072, "Llama 4 Maverick FP8 on Together — 128E reasoning"),
    ("together/llama-4-scout",        "together", "meta-llama/Llama-4-Scout-17B-16E-Instruct-FP8",    131_072, "Llama 4 Scout FP8 on Together — fast 16E"),
    ("together/llama-3.3-70b",       "together", "meta-llama/Llama-3.3-70B-Instruct-Turbo",          128_000, "Llama 3.3 70B Turbo on Together"),
    ("together/llama-3.2-90b-vision", "together", "meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo",  128_000, "Llama 3.2 90B Vision on Together — multimodal"),
    ("together/llama-3.2-11b-vision", "together", "meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo",  128_000, "Llama 3.2 11B Vision on Together — compact vision"),
    ("together/llama-3.1-405b",      "together", "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",   128_000, "Llama 3.1 405B Turbo on Together — largest open"),
    ("together/llama-3.1-70b",       "together", "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",    128_000, "Llama 3.1 70B Turbo on Together"),
    ("together/deepseek-r1",         "together", "deepseek-ai/DeepSeek-R1",                          163_840, "DeepSeek-R1 on Together — open-source reasoning"),
    ("together/deepseek-v3",         "together", "deepseek-ai/DeepSeek-V3",                          128_000, "DeepSeek-V3 on Together — excellent value"),
    ("together/qwen3-235b",          "together", "Qwen/Qwen3-235B-A22B-Instruct-FP8",                40_960,  "Qwen3 235B FP8 on Together — largest Qwen"),
    ("together/qwen-2.5-72b",        "together", "Qwen/Qwen2.5-72B-Instruct-Turbo",                 128_000, "Qwen2.5-72B on Together — multilingual"),
    ("together/qwq-32b",             "together", "Qwen/QwQ-32B",                                     40_960,  "QwQ-32B on Together — reasoning specialist"),
    ("together/mixtral-8x7b",        "together", "mistralai/Mixtral-8x7B-Instruct-v0.1",             32_768,  "Mixtral 8x7B on Together — classic MoE"),
    ("together/mixtral-8x22b",       "together", "mistralai/Mixtral-8x22B-Instruct-v0.1",            65_536,  "Mixtral 8x22B on Together — large MoE"),
    ("together/wizardlm-2-8x22b",    "together", "microsoft/WizardLM-2-8x22B",                       65_536,  "WizardLM-2 8x22B on Together — instruction following"),
    ("together/hermes-3-70b",        "together", "NousResearch/Hermes-3-Llama-3.1-70B",             128_000, "Hermes 3 70B — Nous Research fine-tune"),
    ("together/hermes-3-405b",       "together", "NousResearch/Hermes-3-Llama-3.1-405B",            128_000, "Hermes 3 405B — Nous Research flagship"),
    ("together/hermes-4-70b",        "together", "NousResearch/Hermes-4-Llama-3.1-70B",             128_000, "Hermes 4 70B — NousResearch's latest tool-use specialist"),
    ("together/hermes-4-405b",       "together", "NousResearch/Hermes-4-Llama-3.1-405B",            128_000, "Hermes 4 405B — NousResearch's latest function-calling flagship"),
    ("together/gemma-2-27b",         "together", "google/gemma-2-27b-it",                            40_960,  "Gemma 2 27B on Together — Google open model"),
    ("together/gemma-2-9b",          "together", "google/gemma-2-9b-it",                              8_192,  "Gemma 2 9B on Together — compact Google model"),

    # ── Together AI — Additional Models ───────────────────────────────────────
    ("together/gemma-3-27b",        "together", "google/gemma-3-27b-it-FP8",                          131_072, "Gemma 3 27B on Together — fast open model"),
    ("together/gemma-3-12b",        "together", "google/gemma-3-12b-it",                              131_072, "Gemma 3 12B on Together — compact open model"),
    ("together/gemma-3-4b",         "together", "google/gemma-3-4b-it",                               131_072, "Gemma 3 4B on Together — tiny Gemma"),
    ("together/phi-4",              "together", "microsoft/phi-4",                                     16_384, "Phi-4 on Together — Microsoft reasoning compact"),
    ("together/codellama-70b",      "together", "codellama/CodeLlama-70b-Instruct-hf",                 4_096, "CodeLlama 70B on Together — code specialist"),
    ("together/starcoder2-15b",     "together", "bigcode/starcoder2-15b-instruct-v0.1",               16_384, "StarCoder2 15B on Together — code generation"),
    ("together/deepseek-r1-70b",    "together", "deepseek-ai/DeepSeek-R1-Distill-Llama-70B",         131_072, "DeepSeek-R1 70B on Together — reasoning distillation"),
    ("together/deepseek-r1-qwen-32b","together","deepseek-ai/DeepSeek-R1-Distill-Qwen-32B",           131_072, "DeepSeek-R1 Qwen-32B on Together — compact reasoning"),
    ("together/qwen2.5-coder-32b",  "together", "Qwen/Qwen2.5-Coder-32B-Instruct",                    32_768, "Qwen2.5 Coder 32B on Together — code specialist"),
    ("together/qwen2.5-7b",         "together", "Qwen/Qwen2.5-7B-Instruct-Turbo",                     32_768, "Qwen2.5 7B on Together — compact multilingual"),
    ("together/mistral-7b",         "together", "mistralai/Mistral-7B-Instruct-v0.3",                 32_768, "Mistral 7B on Together — efficient open model"),
    ("together/openchat-3.5",       "together", "openchat/openchat-3.5-1210",                          8_192, "OpenChat 3.5 on Together — RLHF fine-tuned"),
    ("together/nous-hermes-2-34b",  "together", "NousResearch/Nous-Hermes-2-Yi-34B",                  4_096, "Nous Hermes 2 34B on Together — instruction tuned"),
    ("together/falcon-180b",        "together", "tiiuae/falcon-180B-chat",                              2_048, "Falcon 180B on Together — TII's largest model"),
    ("together/solar-10.7b",        "together", "upstage/SOLAR-10.7B-Instruct-v1.0",                   4_096, "SOLAR 10.7B on Together — Upstage instruction model"),
    ("together/vicuna-13b",         "together", "lmsys/vicuna-13b-v1.5-16k",                           16_384, "Vicuna 13B on Together — LMSYS fine-tune"),
    ("together/llama-3.2-3b",       "together", "meta-llama/Llama-3.2-3B-Instruct-Turbo",             131_072, "Llama 3.2 3B Turbo on Together — fast compact"),
    ("together/llama-3.2-1b",       "together", "meta-llama/Llama-3.2-1B-Instruct-Turbo",             131_072, "Llama 3.2 1B Turbo on Together — smallest fast"),
    ("together/deepseek-r1-14b",    "together", "deepseek-ai/DeepSeek-R1-Distill-Qwen-14B",           131_072, "DeepSeek-R1 14B on Together — compact reasoning"),
    ("together/qwen3-8b",           "together", "Qwen/Qwen3-8B-Instruct",                             131_072, "Qwen3-8B on Together — compact multilingual"),

    # ── Fireworks AI ──────────────────────────────────────────────────────────
    ("fireworks/llama-4-scout",    "fireworks", "accounts/fireworks/models/llama4-scout-instruct-basic",     131_072, "Llama 4 Scout on Fireworks — fast multi-expert"),
    ("fireworks/llama-4-maverick", "fireworks", "accounts/fireworks/models/llama4-maverick-instruct-basic",  131_072, "Llama 4 Maverick on Fireworks — 128E instruct"),
    ("fireworks/deepseek-v3",      "fireworks", "accounts/fireworks/models/deepseek-v3",                     163_840, "DeepSeek-V3 on Fireworks — fast value model"),
    ("fireworks/phi-4",            "fireworks", "accounts/fireworks/models/phi-4",                            16_384,  "Phi-4 on Fireworks — Microsoft reasoning compact"),
    ("fireworks/qwen3-235b",       "fireworks", "accounts/fireworks/models/qwen3-235b-a22b",                  40_960,  "Qwen3-235B on Fireworks — top multilingual"),
    ("fireworks/qwen3-30b",        "fireworks", "accounts/fireworks/models/qwen3-30b-a3b-instruct",           32_768,  "Qwen3-30B on Fireworks — efficient reasoning"),
    ("fireworks/mixtral-8x7b",     "fireworks", "accounts/fireworks/models/mixtral-8x7b-instruct-hf",        32_768,  "Mixtral 8x7B on Fireworks"),

    # ── Fireworks AI — Additional Models ──────────────────────────────────────
    ("fireworks/llama-3.1-405b",    "fireworks", "accounts/fireworks/models/llama-v3p1-405b-instruct",  131_072, "Llama 3.1 405B on Fireworks — massive open model"),
    ("fireworks/llama-3.1-70b",     "fireworks", "accounts/fireworks/models/llama-v3p1-70b-instruct",   131_072, "Llama 3.1 70B on Fireworks — fast instruct"),
    ("fireworks/llama-3.3-70b",     "fireworks", "accounts/fireworks/models/llama-v3p3-70b-instruct",   131_072, "Llama 3.3 70B on Fireworks — versatile open model"),
    ("fireworks/gemma-3-27b",       "fireworks", "accounts/fireworks/models/gemma3p-27b-it",            131_072, "Gemma 3 27B on Fireworks — fast open model"),
    ("fireworks/deepseek-r1-70b",   "fireworks", "accounts/fireworks/models/deepseek-r1-distill-llama-70b", 131_072, "DeepSeek-R1 70B on Fireworks — fast reasoning"),
    ("fireworks/qwen2.5-72b",       "fireworks", "accounts/fireworks/models/qwen2p5-72b-instruct",      131_072, "Qwen2.5-72B on Fireworks — multilingual"),
    ("fireworks/qwen2.5-coder-32b", "fireworks", "accounts/fireworks/models/qwen2p5-coder-32b-instruct", 32_768, "Qwen2.5 Coder 32B on Fireworks — code specialist"),
    ("fireworks/gemma-2-27b",       "fireworks", "accounts/fireworks/models/gemma2-27b-it",              8_192, "Gemma 2 27B on Fireworks — Google open model"),
    ("fireworks/mistral-7b",        "fireworks", "accounts/fireworks/models/mistral-7b-instruct-v0p3",  32_768, "Mistral 7B on Fireworks — efficient open model"),
    ("fireworks/phi-4-mini",        "fireworks", "accounts/fireworks/models/phi-4-mini",                16_384, "Phi-4 Mini on Fireworks — Microsoft compact"),
    ("fireworks/llama-3.2-3b",      "fireworks", "accounts/fireworks/models/llama-v3p2-3b-instruct",   131_072, "Llama 3.2 3B on Fireworks — fast compact"),
    ("fireworks/starcoder2-15b",    "fireworks", "accounts/fireworks/models/starcoder2-15b-instruct-v0p1", 16_384, "StarCoder2 15B on Fireworks — code generation"),
    ("fireworks/deepseek-r1-14b",   "fireworks", "accounts/fireworks/models/deepseek-r1-distill-qwen-14b", 131_072, "DeepSeek-R1 14B on Fireworks — compact reasoning"),

    # ── SambaNova ─────────────────────────────────────────────────────────────
    ("sambanova/llama-4-scout",    "sambanova", "Meta-Llama-4-Scout-17B-16E-Instruct",     131_072, "Llama 4 Scout on SambaNova — enterprise speed"),
    ("sambanova/llama-4-maverick", "sambanova", "Meta-Llama-4-Maverick-17B-128E-Instruct", 131_072, "Llama 4 Maverick on SambaNova — enterprise inference"),
    ("sambanova/deepseek-r1",      "sambanova", "DeepSeek-R1-0528",                         163_840, "DeepSeek-R1 on SambaNova — enterprise reasoning"),
    ("sambanova/deepseek-v3",      "sambanova", "DeepSeek-V3-0324",                         128_000, "DeepSeek-V3 on SambaNova — fast value"),
    ("sambanova/llama-3.3-70b",   "sambanova", "Meta-Llama-3.3-70B-Instruct",              128_000, "Llama 3.3 70B on SambaNova"),
    ("sambanova/qwen-2.5-72b",    "sambanova", "Qwen2.5-72B-Instruct",                     128_000, "Qwen2.5-72B on SambaNova — multilingual 72B"),
    ("sambanova/qwen-2.5-32b",    "sambanova", "Qwen2.5-32B-Instruct",                      32_768,  "Qwen2.5-32B on SambaNova — compact multilingual"),
    ("sambanova/llama-3.1-405b",       "sambanova", "Meta-Llama-3.1-405B-Instruct",         128_000, "Llama 3.1 405B on SambaNova — massive enterprise"),
    ("sambanova/llama-3.2-3b",         "sambanova", "Meta-Llama-3.2-3B-Instruct",             32_768, "Llama 3.2 3B on SambaNova — compact fast"),
    ("sambanova/qwen3-32b",            "sambanova", "Qwen3-32B",                               32_768, "Qwen3-32B on SambaNova — fast reasoning"),
    ("sambanova/qwen3-72b",            "sambanova", "Qwen3-72B",                              131_072, "Qwen3-72B on SambaNova — large multilingual"),
    ("sambanova/deepseek-r1-distill-llama-70b", "sambanova", "DeepSeek-R1-Distill-Llama-70B",  131_072, "DeepSeek-R1 70B Distill on SambaNova — fast reasoning"),
    ("sambanova/llama-3.1-8b",         "sambanova", "Meta-Llama-3.1-8B-Instruct",              131_072, "Llama 3.1 8B on SambaNova — fast compact"),
    ("sambanova/qwen2.5-coder-32b",    "sambanova", "Qwen2.5-Coder-32B-Instruct",               32_768, "Qwen2.5-Coder-32B on SambaNova — code specialist"),

    # ── Amazon Bedrock (Nova family) ──────────────────────────────────────────
    ("amazon/nova-premier", "amazon", "us.amazon.nova-premier-v1:0", 300_000, "Amazon Nova Premier — AWS's most capable multimodal model"),
    ("amazon/nova-pro",     "amazon", "us.amazon.nova-pro-v1:0",     300_000, "Amazon Nova Pro — AWS enterprise vision + reasoning"),
    ("amazon/nova-lite",    "amazon", "us.amazon.nova-lite-v1:0",    300_000, "Amazon Nova Lite — fast AWS multimodal"),
    ("amazon/nova-micro",   "amazon", "us.amazon.nova-micro-v1:0",   128_000, "Amazon Nova Micro — ultra-fast AWS text model"),

    # ── Minimax AI ────────────────────────────────────────────────────────────
    ("minimax/minimax-m2",   "minimax", "MiniMax-M2",    1_000_000, "Minimax M2 — powerful MoE with 1M context"),
    ("minimax/minimax-m2.5", "minimax", "MiniMax-M2.5",  1_000_000, "Minimax M2.5 — improved MoE reasoning"),
    ("minimax/minimax-m1",   "minimax", "MiniMax-M1",    1_000_000, "Minimax M1 — reasoning-focused model"),
    ("minimax/minimax-01",   "minimax", "MiniMax-01",    1_000_000, "Minimax-01 — flagship baseline model"),

    # ── Inception AI (diffusion-based LLMs) ──────────────────────────────────
    ("inception/mercury-2",     "inception", "mercury-2",     131_072, "Inception Mercury 2 — ultra-fast diffusion LLM"),
    ("inception/mercury-coder", "inception", "mercury-coder", 131_072, "Inception Mercury Coder — fast diffusion-based code model"),

    # ── Arcee AI ──────────────────────────────────────────────────────────────
    ("arcee/maestro-reasoning", "arcee", "maestro-reasoning", 131_072, "Arcee Maestro — enterprise reasoning model"),
    ("arcee/virtuoso-large",    "arcee", "virtuoso-large",    131_072, "Arcee Virtuoso Large — enterprise instruction following"),
    ("arcee/spotlight",         "arcee", "spotlight",         131_072, "Arcee Spotlight — efficient domain-specific model"),

    # ── Meta Llama API (official Meta platform) ───────────────────────────────
    ("llama/llama-4-scout",    "llama", "Llama-4-Scout-17B-16E-Instruct",          131_072, "Llama 4 Scout — Meta's official API"),
    ("llama/llama-4-maverick", "llama", "Llama-4-Maverick-17B-128E-Instruct-FP8", 131_072, "Llama 4 Maverick — Meta's official API"),
    ("llama/llama-3.3-70b",   "llama", "Llama-3.3-70B-Instruct",                  128_000, "Llama 3.3 70B — Meta's official API"),
    ("llama/llama-3.2-90b-vision",     "llama", "Llama-3.2-90B-Vision-Instruct",  128_000, "Llama 3.2 90B Vision — Meta's official vision API"),
    ("llama/llama-3.1-405b",           "llama", "Meta-Llama-3.1-405B-Instruct",   128_000, "Llama 3.1 405B — Meta's massive open model API"),
    ("llama/llama-3.2-11b-vision",     "llama", "Llama-3.2-11B-Vision-Instruct",  128_000, "Llama 3.2 11B Vision — Meta's compact vision API"),

    # ── HuggingFace Inference API ─────────────────────────────────────────────
    ("huggingface/phi-4",        "huggingface", "microsoft/phi-4",                    16_384,  "Phi-4 on HuggingFace — Microsoft reasoning compact"),
    ("huggingface/gemma-2-9b",   "huggingface", "google/gemma-2-9b-it",               8_192,  "Gemma 2 9B on HuggingFace — Google open model"),
    ("huggingface/llama-3.1-8b", "huggingface", "meta-llama/Llama-3.1-8B-Instruct",  128_000, "Llama 3.1 8B on HuggingFace — free open-source"),
    ("huggingface/mistral-7b",   "huggingface", "mistralai/Mistral-7B-Instruct-v0.3", 32_768,  "Mistral 7B on HuggingFace — efficient multilingual"),
    ("huggingface/llama-3.1-70b",      "huggingface", "meta-llama/Llama-3.1-70B-Instruct",       128_000, "Llama 3.1 70B on HuggingFace — open model"),
    ("huggingface/qwen2.5-72b",        "huggingface", "Qwen/Qwen2.5-72B-Instruct",               128_000, "Qwen2.5-72B on HuggingFace — multilingual"),
    ("huggingface/deepseek-r1-7b",     "huggingface", "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",  32_768, "DeepSeek-R1 7B on HuggingFace — compact reasoning"),
    ("huggingface/zephyr-7b",          "huggingface", "HuggingFaceH4/zephyr-7b-beta",             32_768, "Zephyr 7B Beta — RLHF-tuned Mistral"),
    ("huggingface/starcoder2-15b",     "huggingface", "bigcode/starcoder2-15b-instruct-v0.1",     16_384, "StarCoder2 15B on HuggingFace — code generation"),
    ("huggingface/codellama-34b",      "huggingface", "codellama/CodeLlama-34b-Instruct-hf",      16_384, "CodeLlama 34B on HuggingFace — code specialist"),
    ("huggingface/falcon-7b",          "huggingface", "tiiuae/falcon-7b-instruct",                 8_192, "Falcon 7B on HuggingFace — TII open model"),
    ("huggingface/openchat-3.5",       "huggingface", "openchat/openchat-3.5-0106",                8_192, "OpenChat 3.5 on HuggingFace — RLHF tuned"),

    # ══════════════════════════════════════════════════════════════════════════
    # SPECIALIZED & REGIONAL PROVIDERS
    # ══════════════════════════════════════════════════════════════════════════

    # ── Nvidia NIM (GPU-accelerated inference) ────────────────────────────────
    ("nvidia/nemotron-ultra",      "nvidia", "nvidia/llama-3.1-nemotron-ultra-253b-v1",    128_000, "Nemotron Ultra 253B — NVIDIA's largest model"),
    ("nvidia/nemotron-70b",        "nvidia", "nvidia/llama-3.1-nemotron-70b-instruct",     128_000, "Nemotron 70B — NVIDIA-tuned reasoning"),
    ("nvidia/llama-3.3-70b",       "nvidia", "meta/llama-3.3-70b-instruct",                128_000, "Llama 3.3 70B on NVIDIA NIM — GPU-accelerated"),
    ("nvidia/llama-3.2-90b-vision","nvidia", "meta/llama-3.2-90b-vision-instruct",         128_000, "Llama 3.2 90B Vision on NVIDIA NIM — multimodal"),
    ("nvidia/llama-3.1-8b",        "nvidia", "meta/llama-3.1-8b-instruct",                 128_000, "Llama 3.1 8B on NVIDIA NIM — fast inference"),
    ("nvidia/phi-4-multimodal",    "nvidia", "microsoft/phi-4-multimodal-instruct",          16_384, "Phi-4 Multimodal on NVIDIA NIM — vision + text"),
    ("nvidia/mistral-nemo",        "nvidia", "mistralai/mistral-nemo-instruct-2407",        128_000, "Mistral Nemo on NVIDIA NIM — multilingual"),
    ("nvidia/deepseek-r1-671b",        "nvidia", "deepseek-ai/deepseek-r1",                  131_072, "DeepSeek-R1 671B on NVIDIA NIM — full model"),
    ("nvidia/qwen-2.5-72b",            "nvidia", "qwen/qwen2.5-72b-instruct",                128_000, "Qwen2.5-72B on NVIDIA NIM — multilingual"),
    ("nvidia/llama-3.2-3b",            "nvidia", "meta/llama-3.2-3b-instruct",               128_000, "Llama 3.2 3B on NVIDIA NIM — fast compact"),
    ("nvidia/gemma-3-27b",             "nvidia", "google/gemma-3-27b-it",                    131_072, "Gemma 3 27B on NVIDIA NIM — open model"),
    ("nvidia/mistral-large",           "nvidia", "mistralai/mistral-large-2-instruct",       128_000, "Mistral Large on NVIDIA NIM — enterprise"),

    # ── Moonshot AI / Kimi ────────────────────────────────────────────────────
    ("moonshot/kimi-k2",          "moonshot", "kimi-k2-instruct",        128_000, "Kimi K2 — agentic coding + reasoning, latest"),
    ("moonshot/kimi-k2-thinking", "moonshot", "kimi-k2-thinking",        131_072, "Kimi K2 Thinking — extended chain-of-thought Kimi"),
    ("moonshot/kimi-k2.5",        "moonshot", "kimi-k2.5",               131_072, "Kimi K2.5 — latest Kimi agentic model"),
    ("moonshot/kimi-128k",  "moonshot", "moonshot-v1-128k",   128_000, "Kimi 128K — long-context specialist"),
    ("moonshot/kimi-32k",   "moonshot", "moonshot-v1-32k",     32_000, "Kimi 32K — balanced general purpose"),
    ("moonshot/kimi-8k",    "moonshot", "moonshot-v1-8k",       8_000, "Kimi 8K — fast short-context"),
    ("moonshot/kimi-vl-a3b",           "moonshot", "kimi-vl-a3b-thinking",  131_072, "Kimi VL A3B — vision-language reasoning"),
    ("moonshot/moonshot-v1-auto",      "moonshot", "moonshot-v1-auto",       200_000, "Moonshot v1 Auto — auto-selects context window"),

    # ── Qwen / Alibaba DashScope ──────────────────────────────────────────────
    ("qwen/qwen-max",     "qwen", "qwen-max",              32_768,  "Qwen-Max — most powerful Qwen, enterprise tasks"),
    ("qwen/qwen-plus",    "qwen", "qwen-plus",            131_072,  "Qwen-Plus — balanced cost and quality"),
    ("qwen/qwen-turbo",   "qwen", "qwen-turbo",            32_768,  "Qwen-Turbo — fast cheap Qwen"),
    ("qwen/qwen3-235b",   "qwen", "qwen3-235b-a22b",      131_072,  "Qwen3-235B — Alibaba's largest reasoning model"),
    ("qwen/qwen-2.5-72b", "qwen", "qwen2.5-72b-instruct", 131_072,  "Qwen2.5-72B — open-source multilingual 72B"),
    ("qwen/qwq-32b",      "qwen", "qwq-32b",               32_768,  "QwQ-32B — Qwen's reasoning specialist"),
    ("qwen/qwen3-72b",                 "qwen", "qwen3-72b",                  131_072, "Qwen3-72B — flagship reasoning from Alibaba"),
    ("qwen/qwen3-30b",                 "qwen", "qwen3-30b-a3b",               32_768, "Qwen3-30B — efficient MoE reasoning"),
    ("qwen/qwen3-14b",                 "qwen", "qwen3-14b",                   131_072, "Qwen3-14B — mid-range multilingual"),
    ("qwen/qwen3-8b",                  "qwen", "qwen3-8b",                    131_072, "Qwen3-8B — compact reasoning model"),
    ("qwen/qwen2.5-coder-32b",         "qwen", "qwen2.5-coder-32b-instruct",  128_000, "Qwen2.5-Coder-32B — code specialist"),
    ("qwen/qwen2.5-math-72b",          "qwen", "qwen2.5-math-72b-instruct",     4_096, "Qwen2.5-Math-72B — mathematics specialist"),
    ("qwen/qwen3-max",               "qwen", "qwen3-max",                       131_072, "Qwen3-Max — Alibaba's largest reasoning model (Sep 2025)"),
    ("qwen/qwen3-max-thinking",      "qwen", "qwen3-max-thinking",              131_072, "Qwen3-Max Thinking — extended chain-of-thought (Jan 2026)"),
    ("qwen/qwen3-omni",              "qwen", "qwen3-omni",                       32_768, "Qwen3-Omni — multimodal audio+vision+text (Sep 2025)"),
    ("qwen/qwen3.5",                 "qwen", "qwen3.5-plus",                    131_072, "Qwen3.5 — Alibaba's 397B MoE model (Feb 2026)"),
    ("qwen/qwen3.5-397b",            "qwen", "qwen3.5-397b-a17b",               131_072, "Qwen3.5 397B — Alibaba's largest open MoE model"),
    ("qwen/qwen3.5-122b",            "qwen", "qwen3.5-122b-a10b",               131_072, "Qwen3.5 122B — large multilingual MoE"),
    ("qwen/qwen3.5-35b",             "qwen", "qwen3.5-35b-a3b",                  32_768, "Qwen3.5 35B — efficient mid-size MoE"),
    ("qwen/qwen3.5-27b",             "qwen", "qwen3.5-27b",                     131_072, "Qwen3.5 27B — dense general-purpose model"),
    ("qwen/qwen3.5-9b",              "qwen", "qwen3.5-9b",                      131_072, "Qwen3.5 9B — compact multilingual model"),
    ("qwen/qwen3-vl-235b",           "qwen", "qwen3-vl-235b-a22b-instruct",     131_072, "Qwen3-VL 235B — flagship vision-language reasoning"),
    ("qwen/qwen3-vl-72b",            "qwen", "qwen3-vl-72b-instruct",           131_072, "Qwen3-VL 72B — powerful vision + text multimodal"),
    ("qwen/qwen3-vl-32b",            "qwen", "qwen3-vl-32b-instruct",           131_072, "Qwen3-VL 32B — efficient multimodal model"),
    ("qwen/qwen3-vl-8b",             "qwen", "qwen3-vl-8b-instruct",             32_768, "Qwen3-VL 8B — lightweight vision model"),
    ("qwen/qwen3-coder",             "qwen", "qwen3-coder",                     131_072, "Qwen3-Coder — Alibaba's frontier code generation model"),
    ("qwen/qwen3-coder-30b",         "qwen", "qwen3-coder-30b-a3b-instruct",     32_768, "Qwen3-Coder 30B — efficient MoE code model"),
    ("qwen/qwen-vl-max",             "qwen", "qwen-vl-max",                      32_768, "Qwen-VL Max — visual understanding + complex reasoning"),
    ("qwen/qwen-vl-plus",            "qwen", "qwen-vl-plus",                     32_768, "Qwen-VL Plus — efficient vision-language model"),
    ("qwen/qwen2.5-vl-72b",          "qwen", "qwen2.5-vl-72b-instruct",         131_072, "Qwen2.5-VL 72B — strong multimodal model"),
    ("qwen/qwen2.5-vl-32b",          "qwen", "qwen2.5-vl-32b-instruct",         131_072, "Qwen2.5-VL 32B — efficient vision model"),
    ("qwen/qwen2.5-7b",              "qwen", "qwen2.5-7b-instruct",             131_072, "Qwen2.5 7B — compact multilingual model"),

    # ── 01.AI / Yi ───────────────────────────────────────────────────────────
    ("yi/yi-lightning",   "yi", "yi-lightning",    16_000,  "Yi Lightning — fastest Yi, very cheap"),
    ("yi/yi-large-fc",    "yi", "yi-large-fc",     32_000,  "Yi Large FC — function calling specialist"),
    ("yi/yi-medium-200k", "yi", "yi-medium-200k", 200_000,  "Yi Medium 200K — ultra-long context"),
    ("yi/yi-large",                    "yi", "yi-large",    32_000, "Yi Large — 01.AI's strongest model"),
    ("yi/yi-spark",                    "yi", "yi-spark",    16_000, "Yi Spark — compact 01.AI efficient model"),

    # ── Zhipu AI / GLM ───────────────────────────────────────────────────────
    ("zhipu/glm-4-plus",  "zhipu", "glm-4-plus",  128_000, "GLM-4-Plus — top Zhipu model for complex tasks"),
    ("zhipu/glm-4-0520",  "zhipu", "glm-4-0520",  128_000, "GLM-4-0520 — balanced Zhipu model"),
    ("zhipu/glm-4-air",   "zhipu", "glm-4-air",   128_000, "GLM-4-Air — fast efficient GLM"),
    ("zhipu/glm-z1-air",  "zhipu", "glm-z1-air",  128_000, "GLM-Z1-Air — Zhipu reasoning model"),
    ("zhipu/codegeex-4",               "zhipu", "codegeex-4",     128_000, "CodeGeeX-4 — Zhipu code specialist"),
    ("zhipu/glm-4v",                   "zhipu", "glm-4v",           8_192, "GLM-4V — Zhipu vision-language model"),
    ("zhipu/glm-4-flash",              "zhipu", "glm-4-flash",     128_000, "GLM-4-Flash — ultra-fast free Zhipu model"),
    ("zhipu/glm-z1-plus",              "zhipu", "glm-z1-plus",     128_000, "GLM-Z1-Plus — Zhipu reasoning plus model"),
    ("zhipu/glm-4.5",                  "zhipu", "glm-4.5",         131_072, "GLM-4.5 — Zhipu's latest reasoning model"),
    ("zhipu/glm-5",                    "zhipu", "glm-5",           131_072, "GLM-5 — Zhipu's frontier flagship model"),
    ("zhipu/glm-4.7",                  "zhipu", "glm-4.7",         131_072, "GLM-4.7 — Zhipu vision + text model"),

    # ── ByteDance Doubao ──────────────────────────────────────────────────────
    ("doubao/doubao-pro-128k",  "doubao", "doubao-pro-128k",  128_000, "Doubao Pro 128K — ByteDance flagship"),
    ("doubao/doubao-pro-32k",   "doubao", "doubao-pro-32k",    32_000, "Doubao Pro 32K — balanced ByteDance model"),
    ("doubao/doubao-lite-128k", "doubao", "doubao-lite-128k", 128_000, "Doubao Lite 128K — fast cheap 128K"),
    ("doubao/doubao-lite-32k",  "doubao", "doubao-lite-32k",   32_000, "Doubao Lite 32K — economy ByteDance"),
    ("doubao/doubao-vision-pro-32k",   "doubao", "doubao-vision-pro-32k",      32_000, "Doubao Vision Pro — ByteDance multimodal"),
    ("doubao/doubao-character-pro-32k","doubao", "doubao-character-pro-32k",   32_000, "Doubao Character Pro — role-playing specialist"),
    ("doubao/seed-1.5-pro",            "doubao", "Seed-1.5-Pro",               256_000, "Seed 1.5 Pro — ByteDance latest flagship"),
    ("doubao/seed-1.5-flash",          "doubao", "Seed-1.5-Flash",             256_000, "Seed 1.5 Flash — fast ByteDance model"),
    ("doubao/seed-1.6",                "doubao", "Seed-1.6",                   131_072, "Seed 1.6 — ByteDance's new flagship Seed model"),
    ("doubao/seed-2.0-mini",           "doubao", "Seed-2.0-Mini",              131_072, "Seed 2.0 Mini — efficient next-gen ByteDance model"),

    # ── Upstage Solar ─────────────────────────────────────────────────────────
    ("upstage/solar-pro",  "upstage", "solar-pro",   4_096, "Solar Pro — Upstage top-tier reasoning"),
    ("upstage/solar-mini", "upstage", "solar-mini",  4_096, "Solar Mini — efficient Upstage model"),
    ("upstage/solar-pro-preview",      "upstage", "solar-pro-preview",  4_096, "Solar Pro Preview — latest Upstage reasoning"),

    # ── Writer Palmyra ────────────────────────────────────────────────────────
    ("writer/palmyra-x-004", "writer", "palmyra-x-004", 128_000, "Palmyra X 004 — Writer's enterprise LLM"),
    ("writer/palmyra-med",   "writer", "palmyra-med",    32_000, "Palmyra Med — medical domain specialist"),
    ("writer/palmyra-fin",   "writer", "palmyra-fin",    32_000, "Palmyra Fin — financial domain specialist"),
    ("writer/palmyra-x-002-instruct",  "writer", "palmyra-x-002-instruct", 32_000, "Palmyra X 002 — previous generation Writer model"),
    ("writer/palmyra-creative",        "writer", "palmyra-creative",       32_000, "Palmyra Creative — Writer's storytelling specialist"),

    # ── Groq — Additional Models ──────────────────────────────────────────────
    ("groq/llama-3.3-70b-specdec",        "groq", "llama-3.3-70b-specdec",                        8_192, "Llama 3.3 70B SpecDec on Groq — speculative decoding, 2× faster"),
    ("groq/llama-3.1-70b-specdec",        "groq", "llama-3.1-70b-specdec",                        8_192, "Llama 3.1 70B SpecDec on Groq — speculative decoding"),
    ("groq/llama-3.1-405b",               "groq", "llama-3.1-405b-reasoning",                   131_072, "Llama 3.1 405B Reasoning on Groq — largest open reasoning"),
    ("groq/compound-beta",                "groq", "compound-beta",                               131_072, "Compound Beta on Groq — autonomous tool-calling agent"),
    ("groq/compound-beta-mini",           "groq", "compound-beta-mini",                          131_072, "Compound Beta Mini on Groq — fast agentic model"),
    ("groq/qwen-2.5-coder-32b",           "groq", "qwen-2.5-coder-32b-instruct",                  32_768, "Qwen2.5-Coder-32B on Groq — fast code specialist"),
    ("groq/llama-guard-4-12b",            "groq", "llama-guard-4-12b",                           128_000, "Llama Guard 4 12B on Groq — content safety filter"),
    ("groq/llama-3-70b",                  "groq", "llama3-70b-8192",                               8_192, "Llama 3 70B on Groq — classic inference"),
    ("groq/llama-3-8b",                   "groq", "llama3-8b-8192",                                8_192, "Llama 3 8B on Groq — compact classic"),
    ("groq/mixtral-8x7b",                 "groq", "mixtral-8x7b-32768",                           32_768, "Mixtral 8x7B on Groq — MoE fast"),
    ("groq/gemma-7b",                     "groq", "gemma-7b-it",                                   8_192, "Gemma 7B on Groq — Google compact instruct"),

    # ── Cerebras — Additional Models ─────────────────────────────────────────
    ("cerebras/llama-3.2-1b",             "cerebras", "llama-3.2-1b",                              8_192, "Llama 3.2 1B on Cerebras — world's fastest 1B"),
    ("cerebras/phi-4",                    "cerebras", "phi-4",                                    16_384, "Phi-4 on Cerebras — Microsoft reasoning at wafer speed"),
    ("cerebras/mistral-7b",               "cerebras", "mistral-7b-instruct",                      32_768, "Mistral 7B on Cerebras — blazing fast open model"),
    ("cerebras/llama-3-70b",              "cerebras", "llama3-70b",                                8_192, "Llama 3 70B on Cerebras — legacy ultra-fast"),
    ("cerebras/llama-3-8b",               "cerebras", "llama3-8b",                                 8_192, "Llama 3 8B on Cerebras — legacy instant"),

    # ── SambaNova — Additional Models ────────────────────────────────────────
    ("sambanova/llama-3.2-1b",            "sambanova", "Meta-Llama-3.2-1B-Instruct",               32_768, "Llama 3.2 1B on SambaNova — smallest enterprise"),
    ("sambanova/llama-3.1-405b-reasoning","sambanova", "Meta-Llama-3.1-405B-Instruct",            131_072, "Llama 3.1 405B on SambaNova — massive enterprise"),
    ("sambanova/deepseek-r1-qwen-32b",    "sambanova", "DeepSeek-R1-Distill-Qwen-32B",             32_768, "DeepSeek-R1 Qwen-32B Distill on SambaNova"),
    ("sambanova/deepseek-r1-qwen-14b",    "sambanova", "DeepSeek-R1-Distill-Qwen-14B",             32_768, "DeepSeek-R1 Qwen-14B Distill on SambaNova"),
    ("sambanova/llama-3.2-90b-vision",    "sambanova", "Llama-3.2-90B-Vision-Instruct",           128_000, "Llama 3.2 90B Vision on SambaNova — enterprise vision"),
    ("sambanova/llama-3.2-11b-vision",    "sambanova", "Llama-3.2-11B-Vision-Instruct",           128_000, "Llama 3.2 11B Vision on SambaNova — compact vision"),

    # ── Together AI — Phase 2 ─────────────────────────────────────────────────
    ("together/phi-4-multimodal",         "together", "microsoft/phi-4-multimodal-instruct",        16_384, "Phi-4 Multimodal on Together — vision + text"),
    ("together/qwen2.5-vl-72b",           "together", "Qwen/Qwen2.5-VL-72B-Instruct",             128_000, "Qwen2.5-VL-72B on Together — vision-language 72B"),
    ("together/qwen2.5-vl-7b",            "together", "Qwen/Qwen2.5-VL-7B-Instruct",               32_768, "Qwen2.5-VL-7B on Together — compact vision-language"),
    ("together/llama-3.1-8b",             "together", "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo", 128_000, "Llama 3.1 8B Turbo on Together — fast compact"),
    ("together/llama-3-70b",              "together", "meta-llama/Llama-3-70b-chat-hf",              8_192, "Llama 3 70B on Together — classic open-source"),
    ("together/llama-3-8b",               "together", "meta-llama/Llama-3-8b-chat-hf",               8_192, "Llama 3 8B on Together — classic compact"),
    ("together/llama-2-70b",              "together", "meta-llama/Llama-2-70b-chat-hf",              4_096, "Llama 2 70B on Together — legacy flagship"),
    ("together/llama-2-13b",              "together", "meta-llama/Llama-2-13b-chat-hf",              4_096, "Llama 2 13B on Together — legacy balanced"),
    ("together/llama-2-7b",               "together", "meta-llama/Llama-2-7b-chat-hf",               4_096, "Llama 2 7B on Together — legacy compact"),
    ("together/deepseek-coder-v2",        "together", "deepseek-ai/DeepSeek-Coder-V2-Instruct",   163_840, "DeepSeek Coder V2 on Together — 236B MoE code"),
    ("together/deepseek-r1-7b",           "together", "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",   32_768, "DeepSeek-R1 7B on Together — tiny reasoning"),
    ("together/deepseek-r1-1.5b",         "together", "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B", 32_768, "DeepSeek-R1 1.5B on Together — smallest reasoning"),
    ("together/internlm2-20b",            "together", "internlm/internlm2_5-20b-chat",              32_768, "InternLM2.5 20B on Together — bilingual CN/EN"),
    ("together/nous-hermes-2-mixtral",    "together", "NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO", 32_768, "Nous Hermes 2 Mixtral on Together — DPO fine-tune"),
    ("together/dolphin-2.5-mixtral",      "together", "cognitivecomputations/dolphin-2.5-mixtral-8x7b", 32_768, "Dolphin 2.5 Mixtral on Together"),
    ("together/qwen2-72b",                "together", "Qwen/Qwen2-72B-Instruct",                  128_000, "Qwen2-72B on Together — previous generation"),
    ("together/qwen2-7b",                 "together", "Qwen/Qwen2-7B-Instruct",                   128_000, "Qwen2-7B on Together — compact multilingual"),
    ("together/qwen-2.5-coder-7b",        "together", "Qwen/Qwen2.5-Coder-7B-Instruct",            32_768, "Qwen2.5-Coder-7B on Together — compact code"),
    ("together/gemma-2-2b",               "together", "google/gemma-2-2b-it",                       8_192, "Gemma 2 2B on Together — Google tiny model"),
    ("together/phi-3-medium",             "together", "microsoft/Phi-3-medium-4k-instruct",          4_096, "Phi-3 Medium on Together — Microsoft 14B balanced"),
    ("together/phi-3-mini",               "together", "microsoft/Phi-3-mini-4k-instruct",            4_096, "Phi-3 Mini on Together — Microsoft 3.8B efficient"),
    ("together/phi-3.5-mini",             "together", "microsoft/Phi-3.5-mini-instruct",             32_768, "Phi-3.5 Mini on Together — improved compact Microsoft"),
    ("together/orca-2-13b",               "together", "microsoft/Orca-2-13b",                        4_096, "Orca-2 13B on Together — Microsoft reasoning fine-tune"),
    ("together/llama-3-70b-instruct",     "together", "meta-llama/Meta-Llama-3-70B-Instruct",        8_192, "Llama 3 70B Instruct on Together"),
    ("together/llama-3-8b-instruct",      "together", "meta-llama/Meta-Llama-3-8B-Instruct",         8_192, "Llama 3 8B Instruct on Together"),
    ("together/nous-capybara-34b",        "together", "NousResearch/Nous-Capybara-34B",            200_000, "Nous Capybara 34B on Together — long context"),
    ("together/llama-3.1-nemotron-70b",   "together", "nvidia/Llama-3.1-Nemotron-70B-Instruct-HF", 128_000, "Nemotron 70B on Together — NVIDIA RLHF tuned"),
    ("together/qwen3-14b",                "together", "Qwen/Qwen3-14B",                            131_072, "Qwen3-14B on Together — mid-range reasoning"),
    ("together/qwen3-4b",                 "together", "Qwen/Qwen3-4B",                             131_072, "Qwen3-4B on Together — compact reasoning"),
    ("together/qwen3-1.7b",               "together", "Qwen/Qwen3-1.7B",                            32_768, "Qwen3-1.7B on Together — tiny reasoning"),
    ("together/striped-hyena-nous-7b",    "together", "togethercomputer/StripedHyena-Nous-7B",      32_768, "StripedHyena-Nous 7B on Together — SSM architecture"),
    ("together/chronos-13b",              "together", "Austism/chronos-hermes-13b-v2",               4_096, "Chronos-Hermes 13B on Together — creative fiction"),
    ("together/xwin-lm-70b",              "together", "Xwin-LM/Xwin-LM-70B-V0.1",                   4_096, "Xwin-LM 70B on Together — RLHF Llama 2 fine-tune"),
    ("together/yi-34b",                   "together", "zero-one-ai/Yi-34B-Chat",                   200_000, "Yi-34B on Together — long context 01.AI model"),
    ("together/nous-hermes-2-34b",        "together", "NousResearch/Nous-Hermes-2-Yi-34B",           4_096, "Nous Hermes 2 34B on Together — Yi fine-tune"),
    ("together/llama-3.2-90b-vision",     "together", "meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo", 128_000, "Llama 3.2 90B Vision Turbo on Together — multimodal"),

    # ── Fireworks AI — Phase 2 ────────────────────────────────────────────────
    ("fireworks/llama-3.2-90b-vision",    "fireworks", "accounts/fireworks/models/llama-v3p2-90b-vision-instruct", 128_000, "Llama 3.2 90B Vision on Fireworks — multimodal"),
    ("fireworks/llama-3.2-11b-vision",    "fireworks", "accounts/fireworks/models/llama-v3p2-11b-vision-instruct", 128_000, "Llama 3.2 11B Vision on Fireworks — compact vision"),
    ("fireworks/llama-3.1-8b",            "fireworks", "accounts/fireworks/models/llama-v3p1-8b-instruct",        128_000, "Llama 3.1 8B on Fireworks — fast compact"),
    ("fireworks/deepseek-r1-7b",          "fireworks", "accounts/fireworks/models/deepseek-r1-distill-qwen-7b",    32_768, "DeepSeek-R1 7B on Fireworks — tiny reasoning"),
    ("fireworks/qwen3-72b",               "fireworks", "accounts/fireworks/models/qwen3-72b",                     131_072, "Qwen3-72B on Fireworks — multilingual reasoning"),
    ("fireworks/llama-3-70b",             "fireworks", "accounts/fireworks/models/llama-v3-70b-instruct",           8_192, "Llama 3 70B on Fireworks — reliable open model"),
    ("fireworks/llama-3-8b",              "fireworks", "accounts/fireworks/models/llama-v3-8b-instruct",            8_192, "Llama 3 8B on Fireworks — compact fast"),
    ("fireworks/mixtral-8x22b",           "fireworks", "accounts/fireworks/models/mixtral-8x22b-instruct-hf",      65_536, "Mixtral 8x22B on Fireworks — large MoE"),
    ("fireworks/qwen2-72b",               "fireworks", "accounts/fireworks/models/qwen2-72b-instruct",            128_000, "Qwen2-72B on Fireworks — multilingual"),
    ("fireworks/gemma-2-9b",              "fireworks", "accounts/fireworks/models/gemma2-9b-it",                    8_192, "Gemma 2 9B on Fireworks — Google compact"),
    ("fireworks/hermes-3-405b",           "fireworks", "accounts/fireworks/models/hermes-3-llama-3p1-405b",       131_072, "Hermes 3 405B on Fireworks — RLHF flagship"),
    ("fireworks/deepseek-coder-v2-lite",  "fireworks", "accounts/fireworks/models/deepseek-coder-v2-lite-instruct", 163_840, "DeepSeek Coder V2 Lite on Fireworks — efficient code"),
    ("fireworks/nous-hermes-2-mixtral",   "fireworks", "accounts/fireworks/models/nous-hermes-2-mixtral-8x7b-dpo", 32_768, "Nous Hermes 2 Mixtral on Fireworks"),
    ("fireworks/llama-3.3-70b-fp8",       "fireworks", "accounts/fireworks/models/llama-v3p3-70b-fp8",            131_072, "Llama 3.3 70B FP8 on Fireworks — quantized fast"),
    ("fireworks/gemma-3-12b",             "fireworks", "accounts/fireworks/models/gemma3p-12b-it",                131_072, "Gemma 3 12B on Fireworks — compact Google open"),
    ("fireworks/qwen2.5-coder-7b",        "fireworks", "accounts/fireworks/models/qwen2p5-coder-7b-instruct",      32_768, "Qwen2.5-Coder-7B on Fireworks — compact code"),
    ("fireworks/llama-2-70b",             "fireworks", "accounts/fireworks/models/llama-v2-70b-chat",               4_096, "Llama 2 70B on Fireworks — legacy flagship"),
    ("fireworks/mixtral-8x7b-instruct",   "fireworks", "accounts/fireworks/models/mixtral-8x7b-instruct-hf-v0.1",  32_768, "Mixtral 8x7B Instruct on Fireworks — classic MoE"),
    ("fireworks/llama3-groq-70b-tool",    "fireworks", "accounts/fireworks/models/llama3-groq-70b-8192-tool-use-preview", 8_192, "Llama3 Groq 70B Tool Use on Fireworks — function calling"),
    ("fireworks/qwen3-14b",               "fireworks", "accounts/fireworks/models/qwen3-14b",                     131_072, "Qwen3-14B on Fireworks — mid-range reasoning"),
    ("fireworks/phi-4-multimodal",        "fireworks", "accounts/fireworks/models/phi-4-multimodal-instruct",       16_384, "Phi-4 Multimodal on Fireworks — vision + text"),
    ("fireworks/deepseek-v2.5",           "fireworks", "accounts/fireworks/models/deepseek-v2p5-0905",            128_000, "DeepSeek V2.5 on Fireworks — previous gen value"),
    ("fireworks/qwen3-30b-moe",           "fireworks", "accounts/fireworks/models/qwen3-30b-a3b",                  32_768, "Qwen3-30B MoE on Fireworks — efficient reasoning"),
    ("fireworks/llama-guard-3-8b",        "fireworks", "accounts/fireworks/models/llama-guard-3-8b",               8_192, "Llama Guard 3 8B on Fireworks — content safety"),

    # ── HuggingFace — Additional Models ──────────────────────────────────────
    ("huggingface/llama-3.2-3b",          "huggingface", "meta-llama/Llama-3.2-3B-Instruct",         128_000, "Llama 3.2 3B on HuggingFace — compact open-source"),
    ("huggingface/llama-3.3-70b",         "huggingface", "meta-llama/Llama-3.3-70B-Instruct",        128_000, "Llama 3.3 70B on HuggingFace — latest open flagship"),
    ("huggingface/llama-3.2-1b",          "huggingface", "meta-llama/Llama-3.2-1B-Instruct",         128_000, "Llama 3.2 1B on HuggingFace — ultra-compact open-source"),
    ("huggingface/qwen3-8b",              "huggingface", "Qwen/Qwen3-8B",                            131_072, "Qwen3-8B on HuggingFace — compact reasoning"),
    ("huggingface/qwen3-32b",             "huggingface", "Qwen/Qwen3-32B",                            32_768, "Qwen3-32B on HuggingFace — balanced reasoning"),
    ("huggingface/phi-4",                 "huggingface", "microsoft/phi-4",                            16_384, "Phi-4 on HuggingFace — Microsoft reasoning"),
    ("huggingface/phi-3-mini-128k",       "huggingface", "microsoft/Phi-3-mini-128k-instruct",        128_000, "Phi-3 Mini 128K on HuggingFace — tiny long context"),
    ("huggingface/phi-3.5-mini",          "huggingface", "microsoft/Phi-3.5-mini-instruct",            32_768, "Phi-3.5 Mini on HuggingFace — efficient"),
    ("huggingface/phi-3-medium",          "huggingface", "microsoft/Phi-3-medium-128k-instruct",      128_000, "Phi-3 Medium 128K on HuggingFace — large context"),
    ("huggingface/gemma-3-27b",           "huggingface", "google/gemma-3-27b-it",                    131_072, "Gemma 3 27B on HuggingFace — Google open"),
    ("huggingface/gemma-3-12b",           "huggingface", "google/gemma-3-12b-it",                    131_072, "Gemma 3 12B on HuggingFace — compact Google"),
    ("huggingface/gemma-3-4b",            "huggingface", "google/gemma-3-4b-it",                     131_072, "Gemma 3 4B on HuggingFace — tiny Google"),
    ("huggingface/gemma-2-2b",            "huggingface", "google/gemma-2-2b-it",                       8_192, "Gemma 2 2B on HuggingFace — Google smallest open"),
    ("huggingface/llama-2-70b",           "huggingface", "meta-llama/Llama-2-70b-chat-hf",             4_096, "Llama 2 70B on HuggingFace — legacy flagship"),
    ("huggingface/llama-2-13b",           "huggingface", "meta-llama/Llama-2-13b-chat-hf",             4_096, "Llama 2 13B on HuggingFace — legacy balanced"),
    ("huggingface/nous-hermes-2-70b",     "huggingface", "NousResearch/Hermes-3-Llama-3.1-70B",      128_000, "Hermes 3 70B on HuggingFace — fine-tuned"),
    ("huggingface/mistral-nemo-12b",      "huggingface", "mistralai/Mistral-Nemo-Instruct-2407",     128_000, "Mistral Nemo 12B on HuggingFace — multilingual"),
    ("huggingface/qwen2.5-7b",            "huggingface", "Qwen/Qwen2.5-7B-Instruct",                  32_768, "Qwen2.5-7B on HuggingFace — compact multilingual"),
    ("huggingface/qwen2.5-72b",           "huggingface", "Qwen/Qwen2.5-72B-Instruct",                128_000, "Qwen2.5-72B on HuggingFace — large multilingual"),
    ("huggingface/deepseek-r1-14b",       "huggingface", "deepseek-ai/DeepSeek-R1-Distill-Qwen-14B",  32_768, "DeepSeek-R1 14B on HuggingFace — compact reasoning"),
    ("huggingface/deepseek-v3",           "huggingface", "deepseek-ai/DeepSeek-V3",                  128_000, "DeepSeek-V3 on HuggingFace — value model"),
    ("huggingface/llava-1.5-7b",          "huggingface", "llava-hf/llava-1.5-7b-hf",                   4_096, "LLaVA 1.5 7B on HuggingFace — vision-language"),
    ("huggingface/idefics-80b",           "huggingface", "HuggingFaceM4/idefics2-8b",                  8_192, "IDEFICS2 8B on HuggingFace — multimodal open"),
    ("huggingface/nllb-200",              "huggingface", "facebook/nllb-200-distilled-600M",            1_024, "NLLB-200 on HuggingFace — 200-language translation"),
    ("huggingface/mpt-30b",               "huggingface", "mosaicml/mpt-30b-chat",                      8_192, "MPT-30B on HuggingFace — MosaicML open model"),
    ("huggingface/falcon-40b",            "huggingface", "tiiuae/falcon-40b-instruct",                  2_048, "Falcon 40B on HuggingFace — TII large model"),

    # ── Nvidia NIM — Additional Models ───────────────────────────────────────
    ("nvidia/llama-3.1-405b",             "nvidia", "meta/llama-3.1-405b-instruct",            128_000, "Llama 3.1 405B on NVIDIA NIM — GPU accelerated"),
    ("nvidia/llama-3.1-70b",              "nvidia", "meta/llama-3.1-70b-instruct",             128_000, "Llama 3.1 70B on NVIDIA NIM"),
    ("nvidia/llama-3.2-3b",               "nvidia", "meta/llama-3.2-3b-instruct",              128_000, "Llama 3.2 3B on NVIDIA NIM — fast compact"),
    ("nvidia/phi-4-mini",                 "nvidia", "microsoft/phi-4-mini-instruct",             16_384, "Phi-4 Mini on NVIDIA NIM — efficient reasoning"),
    ("nvidia/mixtral-8x22b",              "nvidia", "mistralai/mixtral-8x22b-instruct-v0.1",    65_536, "Mixtral 8x22B on NVIDIA NIM — large MoE"),
    ("nvidia/gemma-3-12b",                "nvidia", "google/gemma-3-12b-it",                   131_072, "Gemma 3 12B on NVIDIA NIM — compact Google"),
    ("nvidia/qwen3-235b",                 "nvidia", "qwen/qwen3-235b-a22b-instruct",             40_960, "Qwen3-235B on NVIDIA NIM — large reasoning"),
    ("nvidia/nemotron-4-340b",            "nvidia", "nvidia/nemotron-4-340b-instruct",          128_000, "Nemotron-4 340B on NVIDIA NIM — massive model"),
    ("nvidia/codellama-70b",              "nvidia", "meta/codellama-70b-instruct-hf",            16_384, "CodeLlama 70B on NVIDIA NIM — code specialist"),
    ("nvidia/starcoder2-15b",             "nvidia", "bigcode/starcoder2-15b",                    16_384, "StarCoder2 15B on NVIDIA NIM — code generation"),
    ("nvidia/nemotron-3-super-120b",      "nvidia", "nvidia/nemotron-3-super-120b-a12b",          131_072, "Nemotron 3 Super 120B — Nvidia's new efficient MoE"),
    ("nvidia/nemotron-3-nano-30b",        "nvidia", "nvidia/nemotron-3-nano-30b-a3b",             131_072, "Nemotron 3 Nano 30B — Nvidia ultra-efficient MoE"),
    ("nvidia/llama-3.2-11b-vision",       "nvidia", "meta/llama-3.2-11b-vision-instruct",      128_000, "Llama 3.2 11B Vision on NVIDIA NIM — compact vision"),
    ("nvidia/deepseek-r1-70b",            "nvidia", "deepseek-ai/deepseek-r1-distill-llama-70b", 131_072, "DeepSeek-R1 70B Distill on NVIDIA NIM"),
    ("nvidia/qwen2.5-72b",                "nvidia", "qwen/qwen2.5-72b-instruct",               128_000, "Qwen2.5-72B on NVIDIA NIM — multilingual"),

    # ── Mistral — Additional Models ───────────────────────────────────────────
    ("mistral/mistral-large-2411",        "mistral", "mistral-large-2411",             131_072, "Mistral Large Nov 2024 — pinned stable version"),
    ("mistral/mistral-large-2407",        "mistral", "mistral-large-2407",             131_072, "Mistral Large Jul 2024 — reliable pinned version"),
    ("mistral/codestral-2501",            "mistral", "codestral-2501",                 256_000, "Codestral Jan 2025 — pinned code specialist"),
    ("mistral/codestral-mamba",           "mistral", "codestral-mamba-latest",         256_000, "Codestral Mamba — SSM-based efficient code model"),
    ("mistral/mistral-7b-instruct",       "mistral", "open-mistral-7b",                 32_768, "Mistral 7B Instruct — foundational open Mistral"),

    # ── Perplexity — Additional Models ────────────────────────────────────────
    ("perplexity/sonar-reasoning",        "perplexity", "sonar-reasoning",            127_000, "Sonar Reasoning — web-grounded chain-of-thought"),
    ("perplexity/sonar-small-online",     "perplexity", "sonar-small-online",          127_000, "Sonar Small Online — fast grounded answers"),

    # ── Cohere — Additional Models ────────────────────────────────────────────
    ("cohere/command-r-plus-08-2024",     "cohere", "command-r-plus-08-2024",         128_000, "Command R+ Aug 2024 — pinned enterprise model"),
    ("cohere/command-r-08-2024",          "cohere", "command-r-08-2024",              128_000, "Command R Aug 2024 — pinned RAG model"),
    ("cohere/command-nightly",            "cohere", "command-nightly",                  4_096, "Command Nightly — latest Cohere preview"),

    # ── OpenAI — Additional Pinned Versions ───────────────────────────────────
    ("openai/gpt-4o-mini-2024-07-18",     "openai", "gpt-4o-mini-2024-07-18",         128_000, "GPT-4o Mini Jul 2024 — pinned stable version"),
    ("openai/gpt-4-1106-preview",         "openai", "gpt-4-1106-preview",             128_000, "GPT-4 Turbo Nov 2023 — first Turbo preview"),
    ("openai/gpt-3.5-turbo-0125",         "openai", "gpt-3.5-turbo-0125",              16_385, "GPT-3.5 Turbo Jan 2024 — latest pinned 3.5"),
    ("openai/gpt-3.5-turbo-1106",         "openai", "gpt-3.5-turbo-1106",              16_385, "GPT-3.5 Turbo Nov 2023 — stable version"),
    ("openai/gpt-3.5-turbo-16k",          "openai", "gpt-3.5-turbo-16k",               16_385, "GPT-3.5 Turbo 16K — extended context"),

    # ── Anthropic — Additional Pinned Versions ────────────────────────────────
    ("anthropic/claude-2.1",              "anthropic", "claude-2.1",                  200_000, "Claude 2.1 — 200K context, legacy Claude"),
    ("anthropic/claude-2.0",              "anthropic", "claude-2.0",                  100_000, "Claude 2.0 — legacy balanced Claude"),
    ("anthropic/claude-instant-1.2",      "anthropic", "claude-instant-1.2",          100_000, "Claude Instant 1.2 — ultra-cheap legacy"),

    # ── Hyperbolic — Additional Models ────────────────────────────────────────
    ("hyperbolic/llama-3.2-3b",           "hyperbolic", "meta-llama/Llama-3.2-3B-Instruct",          128_000, "Llama 3.2 3B on Hyperbolic — fast compact"),
    ("hyperbolic/phi-4",                  "hyperbolic", "microsoft/phi-4",                             16_384, "Phi-4 on Hyperbolic — Microsoft reasoning"),
    ("hyperbolic/qwen3-72b",              "hyperbolic", "Qwen/Qwen3-72B",                             131_072, "Qwen3-72B on Hyperbolic — multilingual reasoning"),
    ("hyperbolic/deepseek-r1-70b",        "hyperbolic", "deepseek-ai/DeepSeek-R1-Distill-Llama-70B",  131_072, "DeepSeek-R1 70B Distill on Hyperbolic"),
    ("hyperbolic/llama-3.3-70b-fp8",      "hyperbolic", "meta-llama/Llama-3.3-70B-Instruct-FP8",     128_000, "Llama 3.3 70B FP8 on Hyperbolic — quantized fast"),
    ("hyperbolic/gemma-2-9b",             "hyperbolic", "google/gemma-2-9b-it",                         8_192, "Gemma 2 9B on Hyperbolic — Google compact"),

    # ══════════════════════════════════════════════════════════════════════════
    # NEW PROVIDERS
    # ══════════════════════════════════════════════════════════════════════════

    # ── Novita AI (100+ open-source models, HuggingFace model IDs) ────────────
    ("novita/llama-4-scout",              "novita", "meta-llama/llama-4-scout-17b-16e-instruct",       131_072, "Llama 4 Scout on Novita — fast multi-expert"),
    ("novita/llama-4-maverick",           "novita", "meta-llama/llama-4-maverick-17b-128e-instruct",   131_072, "Llama 4 Maverick on Novita — 128E reasoning"),
    ("novita/llama-3.3-70b",              "novita", "meta-llama/llama-3.3-70b-instruct",               128_000, "Llama 3.3 70B on Novita — fast open-source"),
    ("novita/llama-3.1-405b",             "novita", "meta-llama/llama-3.1-405b-instruct",              128_000, "Llama 3.1 405B on Novita — largest open model"),
    ("novita/llama-3.1-70b",              "novita", "meta-llama/llama-3.1-70b-instruct",               128_000, "Llama 3.1 70B on Novita"),
    ("novita/llama-3.1-8b",               "novita", "meta-llama/llama-3.1-8b-instruct",                128_000, "Llama 3.1 8B on Novita — compact fast"),
    ("novita/llama-3.2-90b-vision",       "novita", "meta-llama/llama-3.2-90b-vision-instruct",        128_000, "Llama 3.2 90B Vision on Novita — multimodal"),
    ("novita/llama-3.2-11b-vision",       "novita", "meta-llama/llama-3.2-11b-vision-instruct",        128_000, "Llama 3.2 11B Vision on Novita — compact vision"),
    ("novita/llama-3.2-3b",               "novita", "meta-llama/llama-3.2-3b-instruct",                128_000, "Llama 3.2 3B on Novita — tiny compact"),
    ("novita/llama-3.2-1b",               "novita", "meta-llama/llama-3.2-1b-instruct",                128_000, "Llama 3.2 1B on Novita — ultra-compact"),
    ("novita/deepseek-r1",                "novita", "deepseek-ai/deepseek-r1",                         128_000, "DeepSeek-R1 on Novita — open reasoning"),
    ("novita/deepseek-v3",                "novita", "deepseek-ai/deepseek-v3",                         128_000, "DeepSeek-V3 on Novita — value model"),
    ("novita/deepseek-r1-70b",            "novita", "deepseek-ai/deepseek-r1-distill-llama-70b",       131_072, "DeepSeek-R1 70B Distill on Novita"),
    ("novita/deepseek-r1-32b",            "novita", "deepseek-ai/deepseek-r1-distill-qwen-32b",         32_768, "DeepSeek-R1 32B Distill on Novita"),
    ("novita/deepseek-r1-14b",            "novita", "deepseek-ai/deepseek-r1-distill-qwen-14b",         32_768, "DeepSeek-R1 14B Distill on Novita — compact"),
    ("novita/deepseek-r1-7b",             "novita", "deepseek-ai/deepseek-r1-distill-qwen-7b",          32_768, "DeepSeek-R1 7B Distill on Novita — tiny"),
    ("novita/deepseek-r1-1.5b",           "novita", "deepseek-ai/deepseek-r1-distill-qwen-1.5b",        32_768, "DeepSeek-R1 1.5B Distill on Novita — smallest"),
    ("novita/deepseek-v2.5",              "novita", "deepseek-ai/deepseek-v2.5",                        128_000, "DeepSeek-V2.5 on Novita — previous gen value"),
    ("novita/qwen3-235b",                 "novita", "qwen/qwen3-235b-a22b-instruct",                    40_960, "Qwen3-235B on Novita — largest reasoning"),
    ("novita/qwen3-72b",                  "novita", "qwen/qwen3-72b-instruct",                         131_072, "Qwen3-72B on Novita — strong multilingual"),
    ("novita/qwen3-32b",                  "novita", "qwen/qwen3-32b-instruct",                          32_768, "Qwen3-32B on Novita — balanced reasoning"),
    ("novita/qwen3-14b",                  "novita", "qwen/qwen3-14b-instruct",                         131_072, "Qwen3-14B on Novita — mid multilingual"),
    ("novita/qwen3-8b",                   "novita", "qwen/qwen3-8b-instruct",                          131_072, "Qwen3-8B on Novita — compact reasoning"),
    ("novita/qwen3-4b",                   "novita", "qwen/qwen3-4b-instruct",                          131_072, "Qwen3-4B on Novita — tiny reasoning"),
    ("novita/qwen2.5-72b",                "novita", "qwen/qwen2.5-72b-instruct",                       128_000, "Qwen2.5-72B on Novita"),
    ("novita/qwen2.5-32b",                "novita", "qwen/qwen2.5-32b-instruct",                        32_768, "Qwen2.5-32B on Novita"),
    ("novita/qwen2.5-coder-32b",          "novita", "qwen/qwen2.5-coder-32b-instruct",                  32_768, "Qwen2.5-Coder-32B on Novita — code"),
    ("novita/qwen2.5-coder-7b",           "novita", "qwen/qwen2.5-coder-7b-instruct",                   32_768, "Qwen2.5-Coder-7B on Novita — compact code"),
    ("novita/qwq-32b",                    "novita", "qwen/qwq-32b",                                     32_768, "QwQ-32B on Novita — reasoning"),
    ("novita/phi-4",                      "novita", "microsoft/phi-4",                                   16_384, "Phi-4 on Novita — Microsoft reasoning"),
    ("novita/phi-4-mini",                 "novita", "microsoft/phi-4-mini-instruct",                     16_384, "Phi-4 Mini on Novita — compact Microsoft"),
    ("novita/phi-3.5-mini",               "novita", "microsoft/phi-3.5-mini-instruct",                    4_096, "Phi-3.5 Mini on Novita — efficient 3.8B"),
    ("novita/phi-3-medium-128k",          "novita", "microsoft/phi-3-medium-128k-instruct",             128_000, "Phi-3 Medium 128K on Novita — large context"),
    ("novita/gemma-3-27b",                "novita", "google/gemma-3-27b-it",                           131_072, "Gemma 3 27B on Novita — Google open"),
    ("novita/gemma-3-12b",                "novita", "google/gemma-3-12b-it",                           131_072, "Gemma 3 12B on Novita — compact Google"),
    ("novita/gemma-3-4b",                 "novita", "google/gemma-3-4b-it",                            131_072, "Gemma 3 4B on Novita — tiny Google"),
    ("novita/gemma-2-27b",                "novita", "google/gemma-2-27b-it",                             8_192, "Gemma 2 27B on Novita — Google flagship open"),
    ("novita/gemma-2-9b",                 "novita", "google/gemma-2-9b-it",                              8_192, "Gemma 2 9B on Novita — Google compact open"),
    ("novita/mistral-nemo",               "novita", "mistralai/mistral-nemo-instruct-2407",             128_000, "Mistral Nemo on Novita — multilingual efficient"),
    ("novita/mistral-7b",                 "novita", "mistralai/mistral-7b-instruct-v0.3",                32_768, "Mistral 7B on Novita — efficient open model"),
    ("novita/mixtral-8x7b",               "novita", "mistralai/mixtral-8x7b-instruct-v0.1",             32_768, "Mixtral 8x7B on Novita — MoE model"),
    ("novita/mixtral-8x22b",              "novita", "mistralai/mixtral-8x22b-instruct-v0.1",            65_536, "Mixtral 8x22B on Novita — large MoE"),
    ("novita/hermes-3-70b",               "novita", "nousresearch/hermes-3-llama-3.1-70b",             128_000, "Hermes 3 70B on Novita — RLHF fine-tune"),
    ("novita/hermes-3-405b",              "novita", "nousresearch/hermes-3-llama-3.1-405b",            128_000, "Hermes 3 405B on Novita — RLHF flagship"),
    ("novita/codellama-34b",              "novita", "codellama/codellama-34b-instruct-hf",               16_384, "CodeLlama 34B on Novita — code specialist"),
    ("novita/codellama-70b",              "novita", "codellama/codellama-70b-instruct-hf",               16_384, "CodeLlama 70B on Novita — large code model"),
    ("novita/starcoder2-15b",             "novita", "bigcode/starcoder2-15b-instruct-v0.1",              16_384, "StarCoder2 15B on Novita — code generation"),
    ("novita/nemotron-70b",               "novita", "nvidia/llama-3.1-nemotron-70b-instruct-hf",       128_000, "Nemotron 70B on Novita — NVIDIA RLHF"),
    ("novita/dolphin-llama3-70b",         "novita", "cognitivecomputations/dolphin-2.9-llama3-70b",      8_192, "Dolphin Llama3 70B on Novita — uncensored"),
    ("novita/llama-3.1-nemotron-70b",     "novita", "nvidia/llama-3.1-nemotron-70b-instruct-hf",       128_000, "Llama 3.1 Nemotron 70B on Novita — NVIDIA aligned"),
    ("novita/internlm2-20b",              "novita", "internlm/internlm2_5-20b-chat",                     32_768, "InternLM2.5 20B on Novita — Chinese/English"),
    ("novita/yi-34b",                     "novita", "01-ai/yi-34b-chat",                               200_000, "Yi-34B on Novita — long context 01.AI"),
    ("novita/nous-hermes-2-mixtral",      "novita", "nousresearch/nous-hermes-2-mixtral-8x7b-dpo",      32_768, "Nous Hermes 2 Mixtral on Novita"),
    ("novita/wizard-coder-34b",           "novita", "wizardlm/wizardcoder-34b-v1.0",                    16_384, "WizardCoder 34B on Novita — code specialist"),
    ("novita/openchat-3.5",               "novita", "openchat/openchat-3.5-0106",                         8_192, "OpenChat 3.5 on Novita — RLHF tuned"),
    ("novita/mistral-large",              "novita", "mistralai/mistral-large-2411",                     131_072, "Mistral Large on Novita — enterprise reasoning"),

    # ── Lepton AI (OpenAI-compatible inference platform) ──────────────────────
    ("lepton/llama-4-scout",              "lepton", "llama4-scout",                                    131_072, "Llama 4 Scout on Lepton — fast multi-expert"),
    ("lepton/llama-4-maverick",           "lepton", "llama4-maverick",                                 131_072, "Llama 4 Maverick on Lepton — 128E instruct"),
    ("lepton/llama-3.3-70b",              "lepton", "llama3.3-70b",                                    131_072, "Llama 3.3 70B on Lepton — fast inference"),
    ("lepton/llama-3.1-405b",             "lepton", "llama3.1-405b",                                   131_072, "Llama 3.1 405B on Lepton — largest open model"),
    ("lepton/llama-3.1-70b",              "lepton", "llama3.1-70b",                                    131_072, "Llama 3.1 70B on Lepton"),
    ("lepton/llama-3.1-8b",               "lepton", "llama3.1-8b",                                     131_072, "Llama 3.1 8B on Lepton — fast compact"),
    ("lepton/deepseek-r1",                "lepton", "deepseek-r1",                                     163_840, "DeepSeek-R1 on Lepton — open reasoning"),
    ("lepton/deepseek-v3",                "lepton", "deepseek-v3",                                     163_840, "DeepSeek-V3 on Lepton — value model"),
    ("lepton/deepseek-r1-70b",            "lepton", "deepseek-r1-distill-llama-70b",                   131_072, "DeepSeek-R1 70B Distill on Lepton"),
    ("lepton/deepseek-r1-32b",            "lepton", "deepseek-r1-distill-qwen-32b",                     32_768, "DeepSeek-R1 32B Distill on Lepton"),
    ("lepton/qwq-32b",                    "lepton", "qwq-32b",                                          32_768, "QwQ-32B on Lepton — reasoning"),
    ("lepton/qwen3-235b",                 "lepton", "qwen3-235b-a22b",                                  40_960, "Qwen3-235B on Lepton — largest reasoning"),
    ("lepton/qwen3-72b",                  "lepton", "qwen3-72b",                                       131_072, "Qwen3-72B on Lepton — multilingual reasoning"),
    ("lepton/qwen3-32b",                  "lepton", "qwen3-32b",                                        32_768, "Qwen3-32B on Lepton — balanced"),
    ("lepton/qwen-2.5-72b",               "lepton", "qwen2.5-72b",                                     131_072, "Qwen2.5-72B on Lepton — multilingual"),
    ("lepton/qwen-2.5-coder-32b",         "lepton", "qwen2.5-coder-32b",                                32_768, "Qwen2.5-Coder-32B on Lepton — code specialist"),
    ("lepton/mixtral-8x7b",               "lepton", "mixtral-8x7b",                                     32_768, "Mixtral 8x7B on Lepton"),
    ("lepton/mistral-7b",                 "lepton", "mistral-7b",                                        32_768, "Mistral 7B on Lepton — efficient open"),
    ("lepton/gemma-2-9b",                 "lepton", "gemma2-9b",                                          8_192, "Gemma 2 9B on Lepton — Google compact"),
    ("lepton/llama-3-70b",                "lepton", "llama3-70b",                                        8_192, "Llama 3 70B on Lepton — classic flagship"),
    ("lepton/llama-3-8b",                 "lepton", "llama3-8b",                                         8_192, "Llama 3 8B on Lepton — compact"),
    ("lepton/wizardlm-2-8x22b",           "lepton", "wizardlm-2-8x22b",                                 65_536, "WizardLM-2 8x22B on Lepton — instruction following"),
    ("lepton/nous-hermes-3-70b",          "lepton", "hermes3-70b",                                     128_000, "Hermes 3 70B on Lepton — RLHF fine-tune"),
    ("lepton/phi-4",                      "lepton", "phi-4",                                             16_384, "Phi-4 on Lepton — Microsoft reasoning"),
    ("lepton/gemma-3-27b",                "lepton", "gemma3-27b",                                      131_072, "Gemma 3 27B on Lepton — Google open"),
    ("lepton/deepseek-r1-7b",             "lepton", "deepseek-r1-distill-qwen-7b",                      32_768, "DeepSeek-R1 7B Distill on Lepton — tiny"),
    ("lepton/llama-3.2-3b",               "lepton", "llama3.2-3b",                                     131_072, "Llama 3.2 3B on Lepton — compact fast"),
    ("lepton/internlm2-20b",              "lepton", "internlm2-20b",                                     32_768, "InternLM2.5 20B on Lepton — bilingual"),

    # ── Lambda Labs (GPU Cloud, OpenAI-compatible) ────────────────────────────
    ("lambda/llama-4-scout",              "lambda", "llama4-scout-instruct",                           131_072, "Llama 4 Scout on Lambda — multi-expert fast"),
    ("lambda/llama-4-maverick",           "lambda", "llama4-maverick-instruct",                        131_072, "Llama 4 Maverick on Lambda — 128E instruct"),
    ("lambda/llama-3.3-70b",              "lambda", "llama3.3-70b-instruct-fp8",                       131_072, "Llama 3.3 70B on Lambda — GPU cloud inference"),
    ("lambda/llama-3.1-405b",             "lambda", "llama3.1-405b-instruct-fp8",                      131_072, "Llama 3.1 405B on Lambda — massive open model"),
    ("lambda/llama-3.1-70b",              "lambda", "llama3.1-70b-instruct-fp8",                       131_072, "Llama 3.1 70B on Lambda — reliable open model"),
    ("lambda/llama-3.1-8b",               "lambda", "llama3.1-8b-instruct",                            131_072, "Llama 3.1 8B on Lambda — fast compact"),
    ("lambda/llama-3.2-3b",               "lambda", "llama3.2-3b-instruct",                            131_072, "Llama 3.2 3B on Lambda — compact GPU cloud"),
    ("lambda/deepseek-r1",                "lambda", "deepseek-r1-0528",                                163_840, "DeepSeek-R1 on Lambda — GPU cloud reasoning"),
    ("lambda/deepseek-v3",                "lambda", "deepseek-v3-0324",                                163_840, "DeepSeek-V3 on Lambda — value model"),
    ("lambda/deepseek-r1-70b",            "lambda", "deepseek-r1-distill-llama-70b",                   131_072, "DeepSeek-R1 70B Distill on Lambda"),
    ("lambda/qwen3-235b",                 "lambda", "qwen3-235b-a22b",                                  40_960, "Qwen3-235B on Lambda — large reasoning"),
    ("lambda/qwen3-72b",                  "lambda", "qwen3-72b",                                       131_072, "Qwen3-72B on Lambda"),
    ("lambda/qwen3-30b",                  "lambda", "qwen3-30b-a3b",                                    32_768, "Qwen3-30B on Lambda — efficient MoE"),
    ("lambda/qwen2.5-72b",                "lambda", "qwen25-72b-instruct",                             128_000, "Qwen2.5-72B on Lambda — multilingual"),
    ("lambda/hermes-3-405b",              "lambda", "hermes3-405b",                                    128_000, "Hermes 3 405B on Lambda — RLHF flagship"),
    ("lambda/lfm-40b",                    "lambda", "lfm-40b",                                         131_072, "LFM-40B on Lambda — Lambda Foundation Model 40B"),
    ("lambda/lfm-3b",                     "lambda", "lfm-3b",                                           32_768, "LFM-3B on Lambda — Lambda Foundation Model compact"),
    ("lambda/llama-3-70b",                "lambda", "llama3-70b-instruct-fp8",                           8_192, "Llama 3 70B on Lambda — classic open model"),
    ("lambda/gemma-3-27b",                "lambda", "gemma3-27b-it",                                   131_072, "Gemma 3 27B on Lambda — Google open"),
    ("lambda/mistral-nemo",               "lambda", "mistral-nemo-instruct-2407",                      128_000, "Mistral Nemo 12B on Lambda — multilingual"),

    # ══════════════════════════════════════════════════════════════════════════
    # MAARS SMART ROUTING ALIASES (10 routing strategies)
    # ══════════════════════════════════════════════════════════════════════════
    ("maars/auto",      None, None, 200_000, "MAARS Auto — smart router picks the best model for your prompt"),
    ("maars/smart",     None, None, 200_000, "MAARS Smart — task-classifier routes to the right specialist"),
    ("maars/economy",   None, None, 200_000, "MAARS Economy — fastest & cheapest capable model"),
    ("maars/standard",  None, None, 200_000, "MAARS Standard — balanced quality and cost"),
    ("maars/premium",   None, None, 200_000, "MAARS Premium — highest quality regardless of cost"),
    ("maars/code",      None, None, 200_000, "MAARS Code — routes to best coding model (Codestral, GPT-4.1, Claude)"),
    ("maars/vision",    None, None, 200_000, "MAARS Vision — routes to best multimodal vision model"),
    ("maars/reasoning", None, None, 200_000, "MAARS Reasoning — routes to best math/logic reasoning model"),
    ("maars/search",    None, None, 200_000, "MAARS Search — routes to web-search augmented model (Perplexity)"),
    ("maars/fast",      None, None, 200_000, "MAARS Fast — fastest possible response via Cerebras or Groq"),
]

# Build lookups
_ID_TO_ENTRY  = {m[0]: m for m in MODEL_REGISTRY}
_MAARS_ALIASES = {
    "maars/auto", "maars/smart", "maars/economy", "maars/standard", "maars/premium",
    "maars/code", "maars/vision", "maars/reasoning", "maars/search", "maars/fast",
}

# Pricing lookup by native model_id
def _get_pricing(model_id: str) -> dict:
    return MODEL_COSTS_MAP.get(model_id, {"input": 0.003, "output": 0.003})


def _estimate_cost(model_id: str, prompt: str, response: str) -> float:
    cost = _get_pricing(model_id)
    in_tokens  = max(len(prompt.split()) * 1.3, 10)
    out_tokens = max(len(response.split()) * 1.3, 10)
    return round(
        (cost["input"] * in_tokens + cost["output"] * out_tokens) / 1_000_000, 8
    )


# ─────────────────────────────────────────────────────────────────────────────
# MAARS ALIAS RESOLUTION
# ─────────────────────────────────────────────────────────────────────────────

async def _resolve_maars_alias(alias: str, prompt: str, credits: int, api_keys: dict) -> tuple:
    """
    Resolve maars/* aliases via the smart router.
    Returns (provider, native_model_id).
    """
    from routes.universal import _smart_candidates

    # ── Specialist routing aliases ──────────────────────────────────────────
    specialist_candidates = {
        "maars/code": [
            ("mistral",   "codestral-latest"),
            ("openai",    "gpt-4.1"),
            ("anthropic", "claude-sonnet-4-6"),
            ("deepseek",  "deepseek-v3-0324"),
            ("openai",    "gpt-4o"),
        ],
        "maars/vision": [
            ("openai",    "gpt-4o"),
            ("anthropic", "claude-sonnet-4-6"),
            ("gemini",    "gemini-2.5-flash"),
            ("xai",       "grok-2-vision-1212"),
            ("groq",      "llama-3.2-90b-vision-preview"),
        ],
        "maars/reasoning": [
            ("openai",    "o4"),
            ("anthropic", "claude-opus-4-6"),
            ("deepseek",  "deepseek-r1-0528"),
            ("groq",      "deepseek-r1-distill-llama-70b"),
            ("openai",    "o3"),
        ],
        "maars/search": [
            ("perplexity", "sonar-pro"),
            ("perplexity", "sonar-reasoning-pro"),
            ("perplexity", "sonar-deep-research"),
            ("perplexity", "sonar"),
        ],
        "maars/fast": [
            ("cerebras", "llama-3.3-70b"),
            ("cerebras", "llama-3.1-8b"),
            ("groq",     "llama-3.1-8b-instant"),
            ("groq",     "llama-3.2-3b-preview"),
            ("deepseek", "deepseek-chat"),
            ("openai",   "gpt-4.1-nano"),
        ],
    }

    if alias in specialist_candidates:
        for provider, model_id in specialist_candidates[alias]:
            if api_keys.get(provider):
                return provider, model_id

    # ── Quality-tier aliases ────────────────────────────────────────────────
    quality_map = {
        "maars/economy":  "economy",
        "maars/standard": "standard",
        "maars/premium":  "premium",
        "maars/auto":     None,
        "maars/smart":    None,
    }
    quality_override = quality_map.get(alias)

    candidates, _ = _smart_candidates(prompt, credits, quality_override)
    for provider, model_id in candidates:
        if api_keys.get(provider):
            return provider, model_id

    raise HTTPException(status_code=503, detail={
        "error": {"message": "No configured provider available for routing", "type": "routing_error"}
    })


def _parse_model_id(raw: str) -> tuple:
    """
    Parse 'provider/model' → (maars_id, provider, native_model_id).
    Accepts OpenRouter-style IDs like 'anthropic/claude-sonnet-4-6'.
    Falls back to treating entire string as a native model_id with provider lookup.

    HuggingFace pass-through: any 'huggingface/{org/model}' not in the registry is
    routed directly to the HuggingFace Inference API, giving access to 175,000+ models.
    Example: huggingface/meta-llama/Llama-3.1-70B-Instruct
             huggingface/mistralai/Mistral-7B-v0.1
             huggingface/HuggingFaceH4/zephyr-7b-beta
    """
    entry = _ID_TO_ENTRY.get(raw)
    if entry:
        return entry  # (maars_id, provider, native_model_id, ctx, desc)

    # Try matching by native model_id anywhere in registry
    for m in MODEL_REGISTRY:
        if m[2] == raw:
            return m

    # Try stripping provider prefix and matching
    if "/" in raw:
        _, model_part = raw.split("/", 1)
        for m in MODEL_REGISTRY:
            if m[2] and (m[2].endswith(model_part) or m[2] == model_part):
                return m

    # ── HuggingFace universal pass-through ───────────────────────────────────
    # Allows any of the 175,000+ open-source models on HuggingFace to be called
    # via the MAARS Universal Key using the format: huggingface/{org}/{model}
    # The native HF model ID is passed directly to api-inference.huggingface.co
    if raw.startswith("huggingface/"):
        hf_model_id = raw[len("huggingface/"):]  # e.g. "meta-llama/Llama-3.1-8B-Instruct"
        if hf_model_id:
            return (raw, "huggingface", hf_model_id, 131_072, f"HuggingFace open-source — {hf_model_id}")

    return None


# ─────────────────────────────────────────────────────────────────────────────
# LIVE MODEL VALIDATION
# Checks native model IDs against provider's /models endpoint (cached 1 hr).
# Supports: openai, xai, deepseek, mistral, groq, together, fireworks,
#           cerebras, sambanova, nvidia, novita, lepton, lambda, minimax,
#           inception, arcee, amazon, perplexity, moonshot,
#           qwen, yi, huggingface, hyperbolic, upstage, llama, cohere, gemini
# ─────────────────────────────────────────────────────────────────────────────

_MV_CACHE: dict = {}          # provider → {"ids": set[str], "fetched_at": float}
_MV_TTL   = 3600              # seconds — refresh every hour

_MV_URLS = {
    "openai":      ("GET", "https://api.openai.com/v1/models",                      "bearer"),
    "xai":         ("GET", "https://api.x.ai/v1/models",                            "bearer"),
    "deepseek":    ("GET", "https://api.deepseek.com/models",                        "bearer"),
    "mistral":     ("GET", "https://api.mistral.ai/v1/models",                       "bearer"),
    "groq":        ("GET", "https://api.groq.com/openai/v1/models",                  "bearer"),
    "together":    ("GET", "https://api.together.xyz/v1/models",                     "bearer"),
    "fireworks":   ("GET", "https://api.fireworks.ai/inference/v1/models",           "bearer"),
    "cerebras":    ("GET", "https://api.cerebras.ai/v1/models",                      "bearer"),
    "sambanova":   ("GET", "https://api.sambanova.ai/v1/models",                     "bearer"),
    "nvidia":      ("GET", "https://integrate.api.nvidia.com/v1/models",             "bearer"),
    "minimax":     ("GET", "https://api.minimaxi.chat/v1/models",                    "bearer"),
    "inception":   ("GET", "https://api.inception.ai/v1/models",                     "bearer"),
    "arcee":       ("GET", "https://api.arcee.ai/v1/models",                         "bearer"),
    "perplexity":  ("GET", "https://api.perplexity.ai/models",                       "bearer"),
    "moonshot":    ("GET", "https://api.moonshot.cn/v1/models",                      "bearer"),
    "hyperbolic":  ("GET", "https://api.hyperbolic.xyz/v1/models",                   "bearer"),
    "upstage":     ("GET", "https://api.upstage.ai/v1/models",                       "bearer"),
    "llama":       ("GET", "https://api.llama.com/v1/models",                        "bearer"),
    "huggingface": ("GET", "https://api-inference.huggingface.co/v1/models",         "bearer"),
}


async def _fetch_provider_models(provider: str, api_key: str) -> set:
    """Fetch live model list from provider. Returns set of model IDs."""
    spec = _MV_URLS.get(provider)
    if not spec:
        return set()
    _, url, auth_scheme = spec
    headers = {}
    if auth_scheme == "bearer":
        headers["Authorization"] = f"Bearer {api_key}"

    # Special case: Gemini uses query param, not bearer
    if provider == "gemini":
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        headers = {}

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code != 200:
                return set()
            data = resp.json()
            # Most providers: {"data": [{"id": "..."}, ...]}
            # Gemini:         {"models": [{"name": "models/gemini-2.5-pro"}, ...]}
            # Together:       [{"id": "..."}] or {"data": [...]}
            ids = set()
            if isinstance(data, list):
                for m in data:
                    mid = m.get("id") or m.get("name", "")
                    if mid:
                        ids.add(mid)
            elif "data" in data:
                for m in data["data"]:
                    mid = m.get("id") or m.get("name", "")
                    if mid:
                        ids.add(mid)
            elif "models" in data:
                for m in data["models"]:
                    mid = m.get("id") or m.get("name", "")
                    if mid:
                        # Gemini returns "models/gemini-2.5-pro" — strip prefix
                        if mid.startswith("models/"):
                            ids.add(mid[7:])
                        ids.add(mid)
            return ids
    except Exception as exc:
        logger.debug(f"Model list fetch failed for {provider}: {exc}")
        return set()


async def _validate_model(provider: str, native_model_id: str, api_key: str) -> tuple:
    """
    Check if `native_model_id` is live on provider's API.
    Returns (valid: bool, provider_model_ids: set).
    Uses a 1-hour in-memory cache per provider.
    Skips validation for providers without a /models endpoint.

    HuggingFace pass-through: skip registry validation for dynamically addressed
    HF models (175,000+ open-source). The HF Inference API will reject bad IDs itself.
    """
    if provider not in _MV_URLS and provider != "gemini":
        return True, set()   # Unknown — assume valid, let the call decide

    # HuggingFace pass-through — HF's /models list only returns 20 curated models,
    # but the Inference API supports any of 175k+ models. Skip registry check.
    if provider == "huggingface":
        return True, set()

    now = time.time()
    cached = _MV_CACHE.get(provider)
    if cached and (now - cached["fetched_at"]) < _MV_TTL:
        ids = cached["ids"]
    else:
        ids = await _fetch_provider_models(provider, api_key)
        if ids:   # Only cache non-empty results
            _MV_CACHE[provider] = {"ids": ids, "fetched_at": now}

    if not ids:
        return True, set()   # Couldn't fetch — assume valid

    return native_model_id in ids, ids


# ─────────────────────────────────────────────────────────────────────────────
# FORMAT CONVERSION HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _extract_prompt_text(messages: list) -> str:
    """Extract text from messages for routing/cost estimation."""
    parts = []
    for m in messages:
        content = m.get("content", "")
        if isinstance(content, str):
            parts.append(content)
        elif isinstance(content, list):
            for part in content:
                if part.get("type") == "text":
                    parts.append(part.get("text", ""))
    return " ".join(parts)


def _tools_openai_to_anthropic(tools: list) -> list:
    """Convert OpenAI tools → Anthropic tool format."""
    result = []
    for t in tools:
        if t.get("type") == "function":
            fn = t["function"]
            result.append({
                "name": fn["name"],
                "description": fn.get("description", ""),
                "input_schema": fn.get("parameters", {"type": "object", "properties": {}}),
            })
    return result


def _tool_choice_openai_to_anthropic(tc) -> dict:
    """Convert OpenAI tool_choice → Anthropic format."""
    if tc == "auto":   return {"type": "auto"}
    if tc == "none":   return {"type": "none"}
    if tc == "required": return {"type": "any"}
    if isinstance(tc, dict) and tc.get("type") == "function":
        return {"type": "tool", "name": tc["function"]["name"]}
    return {"type": "auto"}


def _messages_to_gemini(messages: list) -> list:
    """Convert OpenAI messages → Gemini contents format."""
    gemini = []
    for m in messages:
        role    = "model" if m.get("role") == "assistant" else "user"
        content = m.get("content", "")
        if isinstance(content, str):
            parts = [{"text": content}]
        elif isinstance(content, list):
            parts = []
            for part in content:
                if part.get("type") == "text":
                    parts.append({"text": part["text"]})
                elif part.get("type") == "image_url":
                    url = part.get("image_url", {}).get("url", "")
                    if url.startswith("data:"):
                        header, data_b64 = url.split(",", 1)
                        mime = header.split(":")[1].split(";")[0]
                        parts.append({"inlineData": {"mimeType": mime, "data": data_b64}})
                    else:
                        parts.append({"text": f"[Image: {url}]"})
        else:
            parts = [{"text": str(content)}]
        gemini.append({"role": role, "parts": parts})
    return gemini


def _anthropic_to_openai(data: dict, model_id: str) -> dict:
    """Normalize Anthropic response → OpenAI format."""
    content_blocks = data.get("content", [])
    text = None
    tool_calls = []
    for block in content_blocks:
        if block.get("type") == "text":
            text = block.get("text", "")
        elif block.get("type") == "tool_use":
            tool_calls.append({
                "id":   block.get("id", f"call_{int(time.time())}"),
                "type": "function",
                "function": {
                    "name":      block.get("name", ""),
                    "arguments": json.dumps(block.get("input", {})),
                },
            })
    usage  = data.get("usage", {})
    msg    = {"role": "assistant", "content": text}
    finish = "tool_calls" if data.get("stop_reason") == "tool_use" else "stop"
    if tool_calls:
        msg["tool_calls"] = tool_calls
    return {
        "id":      data.get("id", f"chatcmpl-maars-{int(time.time())}"),
        "object":  "chat.completion",
        "created": int(time.time()),
        "model":   model_id,
        "choices": [{"index": 0, "message": msg, "finish_reason": finish}],
        "usage": {
            "prompt_tokens":     usage.get("input_tokens", 0),
            "completion_tokens": usage.get("output_tokens", 0),
            "total_tokens":      usage.get("input_tokens", 0) + usage.get("output_tokens", 0),
        },
    }


def _gemini_to_openai(data: dict, model_id: str) -> dict:
    """Normalize Gemini response → OpenAI format."""
    candidates = data.get("candidates", [])
    text, finish = "", "stop"
    if candidates:
        candidate = candidates[0]
        parts     = candidate.get("content", {}).get("parts", [])
        text      = "".join(p.get("text", "") for p in parts if p.get("text"))
        fr_map    = {"STOP": "stop", "MAX_TOKENS": "length", "SAFETY": "content_filter"}
        finish    = fr_map.get(candidate.get("finishReason", "STOP"), "stop")
    meta = data.get("usageMetadata", {})
    pt   = meta.get("promptTokenCount", 0)
    ct   = meta.get("candidatesTokenCount", 0)
    return {
        "id":      f"chatcmpl-maars-{int(time.time())}",
        "object":  "chat.completion",
        "created": int(time.time()),
        "model":   model_id,
        "choices": [{"index": 0, "message": {"role": "assistant", "content": text}, "finish_reason": finish}],
        "usage":   {"prompt_tokens": pt, "completion_tokens": ct, "total_tokens": pt + ct},
    }


def _cohere_to_openai(data: dict, model_id: str) -> dict:
    """Normalize Cohere v2 response → OpenAI format."""
    message = data.get("message", {})
    blocks  = message.get("content", [])
    text    = blocks[0].get("text", "") if blocks else ""
    usage   = data.get("usage", {}).get("tokens", {})
    pt      = usage.get("input_tokens", 0)
    ct      = usage.get("output_tokens", 0)
    return {
        "id":      data.get("id", f"chatcmpl-maars-{int(time.time())}"),
        "object":  "chat.completion",
        "created": int(time.time()),
        "model":   model_id,
        "choices": [{"index": 0, "message": {"role": "assistant", "content": text}, "finish_reason": "stop"}],
        "usage":   {"prompt_tokens": pt, "completion_tokens": ct, "total_tokens": pt + ct},
    }


# ─────────────────────────────────────────────────────────────────────────────
# FULL-PARAMETER PROVIDER CALLER
# ─────────────────────────────────────────────────────────────────────────────

# Vision-capable providers (support image_url content in messages)
_VISION_PROVIDERS = {"openai", "anthropic", "gemini", "xai", "groq", "together",
                     "fireworks", "nvidia", "minimax"}

def _strip_vision(messages: list) -> list:
    """Strip image parts from messages for providers that don't support vision."""
    cleaned = []
    for m in messages:
        content = m.get("content", "")
        if isinstance(content, list):
            text_parts = [p.get("text", "") for p in content if p.get("type") == "text"]
            content = " ".join(text_parts)
        cleaned.append({**m, "content": content})
    return cleaned


async def _call_provider_full(
    provider: str, model_id: str, messages: list, api_key: str, params: dict
) -> dict:
    """
    Call any provider with full OpenAI-parameter support.
    Returns a normalized OpenAI-format response dict with real token counts.
    """
    max_tokens = params.get("max_tokens", 4096)
    tools      = params.get("tools")

    # Strip vision content for providers that don't support it
    if provider not in _VISION_PROVIDERS:
        messages = _strip_vision(messages)

    if provider == "anthropic":
        sys_msg   = next((m["content"] for m in messages if m["role"] == "system"), None)
        user_msgs = [m for m in messages if m["role"] != "system"]
        payload: dict = {"model": model_id, "max_tokens": max_tokens, "messages": user_msgs}
        if sys_msg:
            payload["system"] = sys_msg
        if params.get("temperature") is not None:
            payload["temperature"] = min(float(params["temperature"]), 1.0)
        if params.get("top_p") is not None:
            payload["top_p"] = params["top_p"]
        stop = params.get("stop")
        if stop:
            payload["stop_sequences"] = stop if isinstance(stop, list) else [stop]
        if tools:
            payload["tools"] = _tools_openai_to_anthropic(tools)
            if params.get("tool_choice"):
                payload["tool_choice"] = _tool_choice_openai_to_anthropic(params["tool_choice"])

        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={"x-api-key": api_key, "anthropic-version": "2023-06-01", "Content-Type": "application/json"},
                json=payload
            )
            resp.raise_for_status()
            return _anthropic_to_openai(resp.json(), model_id)

    elif provider == "gemini":
        sys_msg   = next((m["content"] for m in messages if m["role"] == "system"), None)
        user_msgs = [m for m in messages if m["role"] != "system"]
        gen_cfg: dict = {"maxOutputTokens": max_tokens}
        if params.get("temperature") is not None:
            gen_cfg["temperature"] = params["temperature"]
        if params.get("top_p") is not None:
            gen_cfg["topP"] = params["top_p"]
        stop = params.get("stop")
        if stop:
            gen_cfg["stopSequences"] = stop if isinstance(stop, list) else [stop]
        payload = {"contents": _messages_to_gemini(user_msgs), "generationConfig": gen_cfg}
        if sys_msg:
            payload["systemInstruction"] = {"parts": [{"text": sys_msg}]}

        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent?key={api_key}",
                headers={"Content-Type": "application/json"},
                json=payload
            )
            resp.raise_for_status()
            return _gemini_to_openai(resp.json(), model_id)

    elif provider == "cohere":
        payload = {"model": model_id, "messages": messages, "max_tokens": max_tokens}
        if params.get("temperature") is not None:
            payload["temperature"] = params["temperature"]
        if params.get("top_p") is not None:
            payload["p"] = params["top_p"]
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                "https://api.cohere.com/v2/chat",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json=payload
            )
            resp.raise_for_status()
            return _cohere_to_openai(resp.json(), model_id)

    else:
        # All OpenAI-compatible providers — full parameter passthrough
        url = _OPENAI_COMPAT_STREAM_URLS.get(provider, "")
        if not url:
            raise ValueError(f"No API URL configured for provider '{provider}'")

        payload = {"model": model_id, "messages": messages, "max_tokens": max_tokens}
        for p in ["temperature", "top_p", "stop", "frequency_penalty", "presence_penalty",
                  "seed", "tools", "tool_choice", "response_format", "n",
                  "logprobs", "top_logprobs", "user", "stream_options"]:
            if params.get(p) is not None:
                payload[p] = params[p]

        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            return resp.json()


# ─────────────────────────────────────────────────────────────────────────────
# AUTO-FALLBACK ROUTING
# ─────────────────────────────────────────────────────────────────────────────

_FALLBACK_CHAIN = [
    ("openai",    "gpt-4.1"),
    ("anthropic", "claude-sonnet-4-6"),
    ("gemini",    "gemini-2.5-flash"),
    ("deepseek",  "deepseek-v3-0324"),
    ("groq",      "llama-3.3-70b-versatile"),
    ("openai",    "gpt-4o-mini"),
]


async def _call_with_fallback(
    provider: str, model_id: str, messages: list, api_key: str,
    params: dict, api_keys: dict
) -> tuple:
    """
    Try primary provider/model. On failure auto-retry with fallback chain.
    Validates model against provider's live /models endpoint first.
    Returns (response_dict, actual_provider, actual_model_id, model_warning).
    """
    model_warning = None

    # ── Live model validation ────────────────────────────────────────────────
    valid, provider_ids = await _validate_model(provider, model_id, api_key)
    if not valid:
        closest = next(
            (m for m in sorted(provider_ids) if model_id.split("-")[0] in m),
            None
        )
        hint = f" Closest available: '{closest}'" if closest else ""
        model_warning = (
            f"Model '{model_id}' was not found in {provider}'s live model list "
            f"(checked {len(provider_ids)} models).{hint} Routing to fallback."
        )
        logger.warning(model_warning)
        # Skip primary — go straight to fallback chain
        candidates = []
    else:
        candidates = [(provider, model_id, api_key)]

    for fb_p, fb_m in _FALLBACK_CHAIN:
        if (fb_p, fb_m) == (provider, model_id):
            continue
        fb_key = api_keys.get(fb_p, "")
        if fb_key:
            candidates.append((fb_p, fb_m, fb_key))

    last_err: Exception | None = None
    for try_p, try_m, try_key in candidates[:4]:  # max 4 attempts
        try:
            result = await _call_provider_full(try_p, try_m, messages, try_key, params)
            if try_p != provider:
                logger.info(f"Fallback: served {try_p}/{try_m} (primary {provider}/{model_id} failed)")
            return result, try_p, try_m, model_warning
        except Exception as exc:
            last_err = exc
            logger.warning(f"Provider {try_p}/{try_m} error: {exc}")

    raise last_err or Exception("All providers failed")


# ─────────────────────────────────────────────────────────────────────────────
# STREAMING  SSE HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _sse_chunk(content: str, model: str, finish: bool = False) -> str:
    chunk = {
        "id": f"chatcmpl-maars-{int(time.time())}",
        "object": "chat.completion.chunk",
        "created": int(time.time()),
        "model": model,
        "choices": [{
            "index": 0,
            "delta": {} if finish else {"content": content},
            "finish_reason": "stop" if finish else None,
        }]
    }
    return f"data: {json.dumps(chunk)}\n\n"


async def _stream_openai_compat(url: str, headers: dict, model_id: str, messages: list, maars_model: str, params: dict | None = None) -> AsyncIterator[str]:
    """Native SSE streaming for any OpenAI-compatible endpoint."""
    payload = {"model": model_id, "messages": messages, "stream": True,
               "max_tokens": (params or {}).get("max_tokens", 4096)}
    if params:
        for p in ["temperature", "top_p", "stop", "frequency_penalty", "presence_penalty",
                  "seed", "tools", "tool_choice", "response_format", "n", "user"]:
            if params.get(p) is not None:
                payload[p] = params[p]
    async with httpx.AsyncClient(timeout=120) as client:
        async with client.stream(
            "POST", url,
            headers=headers,
            json=payload
        ) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if line.startswith("data: "):
                    payload = line[6:]
                    if payload.strip() == "[DONE]":
                        yield _sse_chunk("", maars_model, finish=True)
                        yield "data: [DONE]\n\n"
                        return
                    try:
                        d = json.loads(payload)
                        delta = d["choices"][0]["delta"].get("content", "")
                        if delta:
                            yield _sse_chunk(delta, maars_model)
                    except Exception:
                        pass


async def _stream_simulated(provider: str, model_id: str, messages: list, api_key: str, maars_model: str) -> AsyncIterator[str]:
    """Simulated streaming: fetch full response, emit in 5-word chunks."""
    sys_prompt   = next((m["content"] for m in messages if m["role"] == "system"), "You are a helpful AI assistant.")
    user_content = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
    full = await call_direct_llm(provider, model_id, sys_prompt, user_content, [], api_key)
    words = full.split(" ")
    for i in range(0, len(words), 5):
        chunk = " ".join(words[i:i+5])
        if i + 5 < len(words):
            chunk += " "
        yield _sse_chunk(chunk, maars_model)
        await asyncio.sleep(0.02)


async def _stream_response(
    provider: str, model_id: str, system_prompt: str,
    messages: list, api_key: str, maars_model: str,
    params: dict | None = None
) -> AsyncIterator[str]:
    """
    Stream response as SSE.
    - OpenAI-compatible providers: native SSE (22 providers)
    - Anthropic: native Anthropic SSE format
    - Gemini + Cohere: simulated streaming (full response chunked)
    """
    try:
        if provider == "anthropic":
            # Anthropic uses its own SSE event format
            sys_msg   = next((m["content"] for m in messages if m["role"] == "system"), "You are a helpful AI assistant.")
            user_msgs = [m for m in messages if m["role"] != "system"]
            async with httpx.AsyncClient(timeout=120) as client:
                async with client.stream(
                    "POST", "https://api.anthropic.com/v1/messages",
                    headers={"x-api-key": api_key, "anthropic-version": "2023-06-01", "Content-Type": "application/json"},
                    json={"model": model_id, "max_tokens": (params or {}).get("max_tokens", 4096),
                          "system": sys_msg, "messages": user_msgs, "stream": True,
                          **({"temperature": params["temperature"]} if params and params.get("temperature") is not None else {})}
                ) as resp:
                    resp.raise_for_status()
                    async for line in resp.aiter_lines():
                        if line.startswith("data: "):
                            try:
                                d = json.loads(line[6:])
                                if d.get("type") == "content_block_delta":
                                    delta = d.get("delta", {}).get("text", "")
                                    if delta:
                                        yield _sse_chunk(delta, maars_model)
                                elif d.get("type") == "message_stop":
                                    yield _sse_chunk("", maars_model, finish=True)
                                    yield "data: [DONE]\n\n"
                                    return
                            except Exception:
                                pass

        elif provider in _OPENAI_COMPAT_STREAM_URLS:
            # Native SSE streaming — 22 providers all use same format
            url     = _OPENAI_COMPAT_STREAM_URLS[provider]
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            async for chunk in _stream_openai_compat(url, headers, model_id, messages, maars_model, params):
                yield chunk
            return

        else:
            # Gemini, Cohere, or unknown — simulate streaming
            async for chunk in _stream_simulated(provider, model_id, messages, api_key, maars_model):
                yield chunk

        yield _sse_chunk("", maars_model, finish=True)
        yield "data: [DONE]\n\n"

    except Exception as e:
        err = json.dumps({"error": {"message": str(e), "type": "provider_error"}})
        yield f"data: {err}\n\n"
        yield "data: [DONE]\n\n"


# ─────────────────────────────────────────────────────────────────────────────
# POST /v1/chat/completions
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/v1/chat/completions")
async def v1_chat_completions(request: Request):
    """
    OpenAI-compatible chat completions.
    Supports: tools, vision, streaming, all OpenAI parameters.
    Model addressing: provider/model  OR  maars/auto  OR  native model ID.

    Works with any OpenAI SDK:
        client = OpenAI(base_url="https://your-domain.com/api", api_key="maars-sk-...")
        client.chat.completions.create(model="anthropic/claude-sonnet-4-6", ...)
    """
    import uuid as _uuid
    req_id = f"chatcmpl-maars-{_uuid.uuid4().hex[:16]}"

    key_doc = await _get_key_doc(request)
    key     = key_doc["key"]
    user_id = key_doc["user_id"]

    # Rate limit
    rpm_limit = key_doc.get("rpm_limit", _RL_DEFAULT_RPM)
    allowed, count, reset_in = _check_rate_limit(key, rpm_limit)
    if not allowed:
        raise HTTPException(
            status_code=429,
            headers={"X-RateLimit-Limit": str(rpm_limit), "X-RateLimit-Reset": str(reset_in),
                     "Retry-After": str(reset_in)},
            detail={"error": {"message": f"Rate limit exceeded ({rpm_limit} rpm). Retry in {reset_in}s.",
                               "type": "rate_limit_error", "code": 429}}
        )

    # Budget / balance check
    _billing_mode = key_doc.get("billing_mode", "subscription")
    ok, used_usd, remaining = await _check_budget(key_doc)
    if not ok:
        if _billing_mode == "payg":
            _msg = f"Prepaid balance depleted (${key_doc.get('balance_usd', 0):.4f}). Top up your balance to continue."
        elif _billing_mode == "hybrid":
            _msg = f"Monthly budget and prepaid balance both exhausted. Top up to continue."
        else:
            _msg = f"Monthly AI budget exhausted (${key_doc.get('monthly_budget_usd', 0):.2f}). Contact your administrator."
        raise HTTPException(status_code=402, detail={
            "error": {"message": _msg, "type": "budget_error", "code": 402}
        })

    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail={"error": {"message": "Invalid JSON", "type": "invalid_request_error"}})

    model_raw  = body.get("model", "maars/auto")
    messages   = body.get("messages", [])
    stream     = body.get("stream", False)

    if not messages:
        raise HTTPException(status_code=400, detail={"error": {"message": "'messages' is required", "type": "invalid_request_error"}})

    # Collect all passthrough parameters
    params: dict = {}
    for p in ["temperature", "top_p", "max_tokens", "stop", "frequency_penalty",
              "presence_penalty", "seed", "tools", "tool_choice", "response_format",
              "n", "logprobs", "top_logprobs", "user", "stream_options"]:
        val = body.get(p)
        if val is not None:
            params[p] = val
    if "max_tokens" not in params:
        params["max_tokens"] = 4096

    prompt_text  = _extract_prompt_text(messages)
    api_keys     = await get_api_keys()
    user_doc     = await db.users.find_one({"user_id": user_id}, {"_id": 0, "credits": 1})
    credits      = (user_doc or {}).get("credits", 50)
    start        = time.time()

    # Resolve model → (provider, native_model_id)
    if model_raw in _MAARS_ALIASES:
        provider, native_model_id = await _resolve_maars_alias(model_raw, prompt_text, credits, api_keys)
        maars_model = model_raw
    else:
        entry = _parse_model_id(model_raw)
        if not entry:
            raise HTTPException(status_code=400, detail={
                "error": {"message": f"Unknown model '{model_raw}'. Call GET /v1/models for the full list.",
                          "type": "invalid_request_error", "param": "model"}
            })
        _, provider, native_model_id, _, _ = entry
        maars_model = entry[0]
        if not api_keys.get(provider):
            raise HTTPException(status_code=503, detail={
                "error": {"message": f"Provider '{provider}' is not configured on this gateway.",
                          "type": "provider_not_configured"}
            })

    api_key = api_keys.get(provider, "")

    # ── Streaming path ────────────────────────────────────────────────────────
    if stream:
        actual_provider = [provider]
        actual_model    = [native_model_id]

        async def stream_and_track():
            text_acc = []
            try:
                async for chunk in _stream_response(
                    provider, native_model_id, "", messages, api_key, maars_model, params
                ):
                    if chunk.startswith("data: ") and chunk.strip() != "data: [DONE]":
                        try:
                            d = json.loads(chunk[6:])
                            delta = d["choices"][0]["delta"].get("content", "")
                            if delta:
                                text_acc.append(delta)
                        except Exception:
                            pass
                    yield chunk
            finally:
                latency_ms   = int((time.time() - start) * 1000)
                approx       = " ".join(text_acc)
                cost         = _estimate_cost(actual_model[0], prompt_text, approx)
                _mkp         = key_doc.get("markup_pct", 0.0)
                _billed      = round(cost * (1 + _mkp / 100.0), 8) if _mkp > 0 else cost
                _bmode       = key_doc.get("billing_mode", "subscription")
                await _record_usage(user_id, key, maars_model, actual_provider[0],
                                    actual_model[0], cost, _billed, latency_ms, prompt_text, True,
                                    _bmode, _mkp)

        return StreamingResponse(
            stream_and_track(),
            media_type="text/event-stream",
            headers={
                "Cache-Control":      "no-cache",
                "X-Accel-Buffering":  "no",
                "X-Request-ID":       req_id,
                "X-MAARS-Model":      maars_model,
                "X-MAARS-Provider":   provider,
                "X-RateLimit-Limit":  str(rpm_limit),
                "X-RateLimit-Remaining": str(max(rpm_limit - count, 0)),
            }
        )

    # ── Non-streaming path — with auto-fallback ───────────────────────────────
    try:
        data, actual_provider, actual_model, model_warning = await _call_with_fallback(
            provider, native_model_id, messages, api_key, params, api_keys
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail={
            "error": {"message": str(exc), "type": "provider_error",
                      "provider": provider, "model": native_model_id}
        })

    latency_ms = int((time.time() - start) * 1000)

    # Use real token counts if provider returned them
    usage     = data.get("usage", {})
    pt        = usage.get("prompt_tokens")     or int(len(prompt_text.split()) * 1.3)
    ct        = usage.get("completion_tokens") or 0
    cost_usd  = _estimate_cost(actual_model, prompt_text, "")

    # More accurate cost from actual token counts if available
    if usage.get("prompt_tokens"):
        cost_info = _get_pricing(actual_model)
        cost_usd  = round(
            (cost_info.get("input", 0.003) * pt + cost_info.get("output", 0.003) * ct) / 1_000_000, 8
        )

    # Apply markup for PAYG/hybrid billing — billed_usd is what the client is actually charged
    markup_pct  = key_doc.get("markup_pct", 0.0)
    billed_usd  = round(cost_usd * (1 + markup_pct / 100.0), 8) if markup_pct > 0 else cost_usd

    await _record_usage(user_id, key, maars_model, actual_provider, actual_model,
                        cost_usd, billed_usd, latency_ms, prompt_text, False,
                        _billing_mode, markup_pct)

    # Compute remaining balance for response
    if _billing_mode == "payg":
        _remaining_display = round(max(key_doc.get("balance_usd", 0) - billed_usd, 0), 6)
    elif _billing_mode == "hybrid":
        _sub_left = key_doc.get("monthly_budget_usd", 0) - key_doc.get("used_usd", 0)
        _remaining_display = round(max(_sub_left if _sub_left > 0 else key_doc.get("balance_usd", 0) - billed_usd, 0), 6)
    else:
        _remaining_display = round(max(key_doc.get("monthly_budget_usd", 0) - key_doc.get("used_usd", 0) - cost_usd, 0), 6)

    # Normalize + inject MAARS metadata
    data["id"]       = req_id
    data["model"]    = maars_model
    data["provider"] = actual_provider
    data["x_maars"]  = {
        "native_model":         actual_model,
        "actual_provider":      actual_provider,
        "cost_usd":             cost_usd,
        "billed_usd":           billed_usd,
        "markup_pct":           markup_pct,
        "billing_mode":         _billing_mode,
        "latency_ms":           latency_ms,
        "remaining_usd":        _remaining_display,
        "fallback_used":        actual_provider != provider,
        "model_warning":        model_warning,
    }
    return data


async def _record_usage(
    user_id: str, key: str, maars_model: str, provider: str, native_model_id: str,
    cost_usd: float, billed_usd: float, latency_ms: int, prompt_text: str, streamed: bool,
    billing_mode: str = "subscription", markup_pct: float = 0.0
):
    """Write usage log + update key spend.

    cost_usd   — raw provider cost (what MAARS pays the AI provider)
    billed_usd — cost_usd × markup (what the client is charged)
    billing_mode:
      subscription — deduct cost_usd from used_usd (monthly cap)
      payg         — deduct billed_usd from balance_usd
      hybrid       — deduct from used_usd first; once budget exhausted, deduct from balance_usd
    """
    try:
        await db.gateway_usage_logs.insert_one({
            "log_id":        f"gw_{user_id[:8]}_{int(time.time()*1000)}",
            "user_id":       user_id,
            "key_prefix":    key[:16],
            "maars_model":   maars_model,
            "provider":      provider,
            "native_model":  native_model_id,
            "cost_usd":      cost_usd,
            "billed_usd":    billed_usd,
            "markup_pct":    markup_pct,
            "billing_mode":  billing_mode,
            "latency_ms":    latency_ms,
            "streamed":      streamed,
            "prompt_words":  len(prompt_text.split()),
            "source":        "v1_gateway",
            "timestamp":     datetime.now(timezone.utc).isoformat(),
        })

        if billing_mode == "payg":
            # Deduct billed amount from prepaid balance
            update_op = {"$inc": {"balance_usd": -billed_usd, "total_calls": 1}}
        elif billing_mode == "hybrid":
            # Deduct from used_usd (subscription) — once capped, balance deduction handled separately
            update_op = {"$inc": {"used_usd": cost_usd, "total_calls": 1}}
        else:
            # subscription: track provider cost against monthly budget
            update_op = {"$inc": {"used_usd": cost_usd, "total_calls": 1}}

        result = await db.client_gateway_keys.find_one_and_update(
            {"user_id": user_id},
            update_op,
            return_document=True,
        )

        # For hybrid mode: if subscription budget exceeded, also drain from balance
        if billing_mode == "hybrid" and result:
            budget = result.get("monthly_budget_usd", 0.0)
            used   = result.get("used_usd", 0.0)
            if budget > 0 and used > budget:
                overage = used - budget
                await db.client_gateway_keys.update_one(
                    {"user_id": user_id},
                    {"$inc": {"balance_usd": -overage}}
                )

        # Fire budget threshold webhooks asynchronously
        if result:
            budget = result.get("monthly_budget_usd", 0.0)
            used   = result.get("used_usd", 0.0)
            asyncio.create_task(_check_and_fire_budget_webhooks(user_id, key[:16], budget, used))
    except Exception as e:
        logger.warning(f"Usage recording failed: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# GET /v1/models
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/v1/models")
async def v1_list_models(request: Request):
    """List all available models in OpenAI format.
    Public — no auth required (returns availability based on gateway config).
    Auth header optional — if provided, shows budget info.
    """
    try:
        api_keys = await get_api_keys()
    except Exception:
        api_keys = {}

    now = int(time.time())
    data = []
    for maars_id, provider, native_id, ctx, desc in MODEL_REGISTRY:
        is_maars_alias = provider is None
        available = is_maars_alias or bool(api_keys.get(provider))
        cost_info  = _get_pricing(native_id or "") if native_id else {}
        credit_cost = MODEL_CREDIT_COSTS.get((native_id or "").split("/")[-1], 1)
        data.append({
            "id":               maars_id,
            "object":           "model",
            "created":          now,
            "owned_by":         "maars" if is_maars_alias else provider,
            "description":      desc,
            "context_length":   ctx,
            "native_model_id":  native_id,
            "provider":         provider or "maars",
            "available":        available,
            "pricing": {
                "prompt":     cost_info.get("input", 0),
                "completion": cost_info.get("output", 0),
                "unit":       "USD per 1M tokens",
            },
            "credits_per_call": credit_cost,
            "is_maars_router":  is_maars_alias,
        })

    # ── HuggingFace universal pass-through entry ─────────────────────────────
    # Signals to clients that ANY of the 175,000+ HuggingFace open-source models
    # can be called using the format: huggingface/{org}/{model-id}
    hf_available = bool(api_keys.get("huggingface"))
    data.append({
        "id":               "huggingface/*",
        "object":           "model",
        "created":          now,
        "owned_by":         "huggingface",
        "description":      "HuggingFace Universal Pass-through — call any of 175,000+ open-source models using huggingface/{org}/{model-id}. Example: huggingface/meta-llama/Llama-3.1-70B-Instruct",
        "context_length":   131_072,
        "native_model_id":  "{any HuggingFace model ID}",
        "provider":         "huggingface",
        "available":        hf_available,
        "pricing": {"prompt": 0.0005, "completion": 0.0005, "unit": "USD per 1M tokens (varies by model)"},
        "credits_per_call": 1,
        "is_maars_router":  False,
        "is_passthrough":   True,
        "passthrough_count": "175,000+",
    })

    return {"object": "list", "data": data, "total": len(data), "huggingface_passthrough": "175,000+ additional open-source models available via huggingface/{org}/{model-id}"}


@router.get("/v1/models/{model_id:path}")
async def v1_get_model(model_id: str, request: Request):
    """Get a single model card."""
    entry = _ID_TO_ENTRY.get(model_id) or _parse_model_id(model_id)
    if not entry:
        raise HTTPException(status_code=404, detail={
            "error": {"message": f"Model '{model_id}' not found", "type": "invalid_request_error"}
        })

    maars_id, provider, native_id, ctx, desc = entry
    cost_info  = _get_pricing(native_id or "") if native_id else {}
    credit_cost = MODEL_CREDIT_COSTS.get((native_id or "").split("/")[-1], 1)

    return {
        "id":               maars_id,
        "object":           "model",
        "created":          int(time.time()),
        "owned_by":         "maars" if provider is None else provider,
        "description":      desc,
        "context_length":   ctx,
        "native_model_id":  native_id,
        "provider":         provider or "maars",
        "pricing": {
            "prompt":     cost_info.get("input", 0),
            "completion": cost_info.get("output", 0),
            "unit":       "USD per 1M tokens",
        },
        "credits_per_call": credit_cost,
        "is_maars_router":  provider is None,
    }


# ─────────────────────────────────────────────────────────────────────────────
# GET /v1/models/validate  — live model availability check
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/v1/models/validate")
async def v1_validate_model(model: str, request: Request):
    """
    Check if a model ID is currently available on its provider's live API.
    Query param: model=openai/gpt-5.4  or  model=anthropic/claude-sonnet-4-6
    Returns: {valid, model, provider, native_model_id, provider_model_count,
              cached, warning, available_from_provider: [...]}
    Auth: maars-sk key OR no auth (public endpoint for discovery).
    """
    # Try to resolve key for api_key — fall back to env keys if no auth
    api_keys = await get_api_keys()
    try:
        key_doc  = await _get_key_doc(request)
        _        = key_doc  # authenticated — api_keys already fetched
    except HTTPException:
        pass  # Public — use platform api_keys only

    entry = _parse_model_id(model)
    if not entry:
        raise HTTPException(status_code=404, detail={
            "error": {"message": f"Model '{model}' not in MAARS registry. Call GET /v1/models for the full list.",
                      "type": "invalid_request_error"}
        })

    maars_id, provider, native_id, ctx, desc = entry
    if provider is None:
        # MAARS routing alias — always valid
        return {
            "model":             maars_id,
            "valid":             True,
            "provider":          "maars",
            "native_model_id":   None,
            "is_maars_router":   True,
            "message":           "MAARS routing alias — resolves dynamically at call time.",
        }

    api_key = api_keys.get(provider, "")
    now     = time.time()
    cached  = provider in _MV_CACHE and (now - _MV_CACHE[provider]["fetched_at"]) < _MV_TTL

    valid, provider_ids = await _validate_model(provider, native_id, api_key)

    # Find alternatives from same provider if invalid
    suggestions = []
    if not valid and provider_ids:
        prefix = native_id.split("-")[0] if native_id else ""
        suggestions = sorted(m for m in provider_ids if prefix and prefix in m)[:10]

    return {
        "model":                 maars_id,
        "native_model_id":       native_id,
        "provider":              provider,
        "valid":                 valid,
        "provider_model_count":  len(provider_ids),
        "cached":                cached,
        "cache_ttl_seconds":     _MV_TTL,
        "context_length":        ctx,
        "description":           desc,
        "warning":               None if valid else f"'{native_id}' not found in {provider}'s live model list.",
        "suggestions":           suggestions if not valid else [],
    }


# ─────────────────────────────────────────────────────────────────────────────
# GET /v1/usage
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/v1/usage")
async def v1_usage(request: Request):
    """Return key spend, budget, and per-model breakdown for this billing cycle."""
    key_doc = await _get_key_doc(request)
    user_id = key_doc["user_id"]

    cycle_start = key_doc.get("cycle_start", "")
    logs = await db.gateway_usage_logs.find(
        {"user_id": user_id, "source": "v1_gateway", "timestamp": {"$gte": cycle_start}},
        {"_id": 0}
    ).sort("timestamp", -1).limit(500).to_list(500)

    total_cost  = round(sum(l.get("cost_usd", 0) for l in logs), 8)
    total_calls = len(logs)
    by_model    = {}
    by_provider = {}

    for l in logs:
        m = l.get("maars_model", "unknown")
        p = l.get("provider", "unknown")
        by_model[m]    = {"calls": by_model.get(m, {}).get("calls", 0) + 1, "cost_usd": round(by_model.get(m, {}).get("cost_usd", 0) + l.get("cost_usd", 0), 8)}
        by_provider[p] = {"calls": by_provider.get(p, {}).get("calls", 0) + 1, "cost_usd": round(by_provider.get(p, {}).get("cost_usd", 0) + l.get("cost_usd", 0), 8)}

    billing_mode = key_doc.get("billing_mode", "subscription")
    budget    = key_doc.get("monthly_budget_usd", 0)
    used      = key_doc.get("used_usd", 0)
    balance   = key_doc.get("balance_usd", 0.0)
    markup_pct = key_doc.get("markup_pct", 0.0)

    total_billed = round(sum(l.get("billed_usd", l.get("cost_usd", 0)) for l in logs), 8)

    if billing_mode == "payg":
        remaining = round(balance, 6)
    elif billing_mode == "hybrid":
        sub_left = budget - used
        remaining = round(max(sub_left, 0) + max(balance, 0), 6)
    else:
        remaining = round(max(budget - used, 0), 6)

    return {
        "object":            "usage",
        "billing_mode":      billing_mode,
        "cycle_start":       cycle_start,
        "budget_usd":        budget,
        "used_usd":          round(used, 8),
        "balance_usd":       round(balance, 6),
        "markup_pct":        markup_pct,
        "remaining_usd":     remaining,
        "budget_used_pct":   round(used / budget * 100, 1) if budget > 0 else 0,
        "total_calls":       total_calls,
        "total_cost_usd":    total_cost,
        "total_billed_usd":  total_billed,
        "avg_cost_per_call": round(total_cost / max(total_calls, 1), 8),
        "by_model":          by_model,
        "by_provider":       by_provider,
    }


# ─────────────────────────────────────────────────────────────────────────────
# GET /v1/balance   (PAYG clients — prepaid credit balance)
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/v1/balance")
async def v1_balance(request: Request):
    """Return prepaid balance and billing mode for this API key."""
    key_doc      = await _get_key_doc(request)
    billing_mode = key_doc.get("billing_mode", "subscription")
    balance      = key_doc.get("balance_usd", 0.0)
    markup_pct   = key_doc.get("markup_pct", 0.0)
    budget       = key_doc.get("monthly_budget_usd", 0.0)
    used         = key_doc.get("used_usd", 0.0)

    # Estimate how many calls remain based on last 10 average cost
    recent = await db.gateway_usage_logs.find(
        {"user_id": key_doc["user_id"], "source": "v1_gateway"},
        {"cost_usd": 1, "_id": 0}
    ).sort("timestamp", -1).limit(10).to_list(10)
    avg_call_cost = round(sum(r.get("cost_usd", 0) for r in recent) / max(len(recent), 1), 8)
    est_calls_remaining = int(balance / avg_call_cost) if avg_call_cost > 0 and balance > 0 else None

    return {
        "object":                "balance",
        "billing_mode":          billing_mode,
        "balance_usd":           round(balance, 6),
        "markup_pct":            markup_pct,
        "monthly_budget_usd":    budget,
        "used_usd":              round(used, 8),
        "est_calls_remaining":   est_calls_remaining,
        "avg_call_cost_usd":     avg_call_cost,
        "auto_topup_enabled":    key_doc.get("auto_topup_enabled", False),
        "low_balance_threshold": key_doc.get("low_balance_threshold_usd", 5.0),
    }


# ─────────────────────────────────────────────────────────────────────────────
# GET /v1/pricing   (PAYG client-visible per-model pricing with markup)
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/v1/pricing")
async def v1_pricing(request: Request):
    """Return per-model pricing including any markup applied to this key.
    Clients can use this to understand what each model costs before calling.
    """
    key_doc    = await _get_key_doc(request)
    markup_pct = key_doc.get("markup_pct", 0.0)
    multiplier = 1 + markup_pct / 100.0

    try:
        api_keys = await get_api_keys()
    except Exception:
        api_keys = {}

    pricing = []
    for maars_id, provider, native_id, ctx, desc in MODEL_REGISTRY:
        is_alias = provider is None
        if is_alias:
            continue
        cost_info = _get_pricing(native_id or "")
        input_raw  = cost_info.get("input", 0)
        output_raw = cost_info.get("output", 0)
        available  = bool(api_keys.get(provider))
        pricing.append({
            "model":                    maars_id,
            "provider":                 provider,
            "context_length":           ctx,
            "available":                available,
            "provider_cost": {
                "input_per_1m_tokens":  input_raw,
                "output_per_1m_tokens": output_raw,
            },
            "your_price": {
                "input_per_1m_tokens":  round(input_raw * multiplier, 6),
                "output_per_1m_tokens": round(output_raw * multiplier, 6),
                "markup_pct":           markup_pct,
            },
            "est_cost_1k_tokens": round((input_raw * 0.75 + output_raw * 0.25) * multiplier / 1000, 8),
        })

    pricing.sort(key=lambda x: x["est_cost_1k_tokens"])
    return {
        "object":      "pricing_list",
        "markup_pct":  markup_pct,
        "billing_mode": key_doc.get("billing_mode", "subscription"),
        "currency":    "USD",
        "unit":        "per 1M tokens",
        "data":        pricing,
        "total":       len(pricing),
    }


# ─────────────────────────────────────────────────────────────────────────────
# GET /v1/rate-limits
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/v1/rate-limits")
async def v1_rate_limits(request: Request):
    """Return rate limit status for this key."""
    key_doc = await _get_key_doc(request)
    key     = key_doc["key"]
    rpm_limit = key_doc.get("rpm_limit", _RL_DEFAULT_RPM)

    entry = _RL.get(key)
    now   = time.time()
    if entry and (now - entry[1]) < _RL_WINDOW:
        count     = entry[0]
        reset_in  = int(_RL_WINDOW - (now - entry[1]))
    else:
        count    = 0
        reset_in = _RL_WINDOW

    return {
        "object":        "rate_limit",
        "limit_rpm":     rpm_limit,
        "used_rpm":      count,
        "remaining_rpm": max(rpm_limit - count, 0),
        "reset_in_seconds": reset_in,
    }


# ─────────────────────────────────────────────────────────────────────────────
# POST /v1/completions  (legacy text completion — OpenAI compatible)
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/v1/completions")
async def v1_completions(request: Request):
    """Legacy text completions. Wraps into chat completions internally."""
    key_doc = await _get_key_doc(request)
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail={"error": {"message": "Invalid JSON", "type": "invalid_request_error"}})

    prompt  = body.get("prompt", "")
    model   = body.get("model", "maars/auto")

    # Wrap as chat completion internally
    messages = [{"role": "user", "content": prompt}]
    body["messages"] = messages
    body["model"]    = model

    # Proxy to chat completions handler
    resp = await v1_chat_completions(request)
    return resp


# ─────────────────────────────────────────────────────────────────────────────
# POST /v1/embeddings
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/v1/embeddings")
async def v1_embeddings(request: Request):
    """
    Text embeddings — proxies to OpenAI, Cohere, or HuggingFace.
    OpenAI-compatible request/response format.
    """
    key_doc = await _get_key_doc(request)
    api_keys = await get_api_keys()

    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail={"error": {"message": "Invalid JSON", "type": "invalid_request_error"}})

    input_text = body.get("input", "")
    model_raw  = body.get("model", "text-embedding-3-small")
    dimensions = body.get("dimensions")

    # Determine provider from model name
    if "embed" in model_raw.lower() or "embedding" in model_raw.lower():
        if "cohere" in model_raw or model_raw.startswith("embed-"):
            provider, model_id = "cohere", model_raw
        elif "bge" in model_raw or "e5" in model_raw or "gte" in model_raw:
            provider, model_id = "huggingface", model_raw
        else:
            provider, model_id = "openai", model_raw
    else:
        provider, model_id = "openai", "text-embedding-3-small"

    api_key = api_keys.get(provider, "")
    if not api_key:
        # Fallback to openai
        provider = "openai"
        api_key  = api_keys.get("openai", "")
        model_id = "text-embedding-3-small"

    if not api_key:
        raise HTTPException(status_code=503, detail={"error": {"message": "No embedding provider configured.", "type": "provider_not_configured"}})

    if provider == "openai":
        payload = {"model": model_id, "input": input_text, "encoding_format": "float"}
        if dimensions:
            payload["dimensions"] = dimensions
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                "https://api.openai.com/v1/embeddings",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json=payload
            )
            resp.raise_for_status()
            return resp.json()

    elif provider == "cohere":
        texts = input_text if isinstance(input_text, list) else [input_text]
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                "https://api.cohere.com/v2/embed",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={"model": model_id or "embed-english-v3.0", "texts": texts,
                      "input_type": "search_query", "embedding_types": ["float"]}
            )
            resp.raise_for_status()
            data = resp.json()
            embeddings = data.get("embeddings", {}).get("float", [[]])
            return {
                "object": "list",
                "data":   [{"object": "embedding", "embedding": e, "index": i} for i, e in enumerate(embeddings)],
                "model":  model_id,
                "usage":  {"prompt_tokens": 0, "total_tokens": 0},
            }

    raise HTTPException(status_code=503, detail={"error": {"message": "Embedding provider unavailable", "type": "provider_error"}})


# ─────────────────────────────────────────────────────────────────────────────
# GET /v1/providers
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/v1/providers")
async def v1_list_providers(request: Request):
    """List all 33 providers with configuration status and model count. Registry: 175,000+ models."""
    # Auth optional for listing, required for seeing key status
    authed = False
    try:
        await _get_key_doc(request)
        authed = True
    except Exception:
        pass

    api_keys = await get_api_keys()

    provider_meta = {
        "openai":      {"name": "OpenAI",              "url": "https://api.openai.com",                   "docs": "https://platform.openai.com/docs",     "tier": "frontier",    "supports_vision": True,  "supports_tools": True,  "streaming": "native"},
        "anthropic":   {"name": "Anthropic (Claude)",  "url": "https://api.anthropic.com",                "docs": "https://docs.anthropic.com",           "tier": "frontier",    "supports_vision": True,  "supports_tools": True,  "streaming": "native"},
        "gemini":      {"name": "Google Gemini",       "url": "https://generativelanguage.googleapis.com","docs": "https://ai.google.dev",                "tier": "frontier",    "supports_vision": True,  "supports_tools": True,  "streaming": "native"},
        "xai":         {"name": "xAI (Grok)",          "url": "https://api.x.ai",                         "docs": "https://docs.x.ai",                    "tier": "frontier",    "supports_vision": True,  "supports_tools": True,  "streaming": "native"},
        "deepseek":    {"name": "DeepSeek",            "url": "https://api.deepseek.com",                 "docs": "https://platform.deepseek.com/docs",   "tier": "value",       "supports_vision": False, "supports_tools": True,  "streaming": "native"},
        "mistral":     {"name": "Mistral AI",          "url": "https://api.mistral.ai",                   "docs": "https://docs.mistral.ai",              "tier": "frontier",    "supports_vision": True,  "supports_tools": True,  "streaming": "native"},
        "perplexity":  {"name": "Perplexity",          "url": "https://api.perplexity.ai",                "docs": "https://docs.perplexity.ai",           "tier": "search",      "supports_vision": False, "supports_tools": False, "streaming": "native"},
        "cohere":      {"name": "Cohere",              "url": "https://api.cohere.com",                   "docs": "https://docs.cohere.com",              "tier": "enterprise",  "supports_vision": False, "supports_tools": True,  "streaming": "simulated"},
        "groq":        {"name": "Groq",                "url": "https://api.groq.com",                     "docs": "https://console.groq.com/docs",        "tier": "speed",       "supports_vision": True,  "supports_tools": True,  "streaming": "native"},
        "cerebras":    {"name": "Cerebras",            "url": "https://api.cerebras.ai",                  "docs": "https://inference-docs.cerebras.ai",   "tier": "speed",       "supports_vision": False, "supports_tools": False, "streaming": "native"},
        "together":    {"name": "Together AI",         "url": "https://api.together.xyz",                 "docs": "https://docs.together.ai",             "tier": "open-source", "supports_vision": True,  "supports_tools": True,  "streaming": "native"},
        "fireworks":   {"name": "Fireworks AI",        "url": "https://api.fireworks.ai",                 "docs": "https://readme.fireworks.ai",          "tier": "open-source", "supports_vision": True,  "supports_tools": True,  "streaming": "native"},
        "ai21":        {"name": "AI21 Labs (Jamba)",   "url": "https://api.ai21.com",                     "docs": "https://docs.ai21.com",                "tier": "specialized", "supports_vision": False, "supports_tools": False, "streaming": "native"},
        "sambanova":   {"name": "SambaNova",           "url": "https://api.sambanova.ai",                 "docs": "https://community.sambanova.ai",       "tier": "speed",       "supports_vision": False, "supports_tools": False, "streaming": "native"},
        "novita":      {"name": "Novita AI",            "url": "https://novita.ai",                        "docs": "https://novita.ai/docs",               "tier": "speed",       "supports_vision": False, "supports_tools": True,  "streaming": "native"},
        "lepton":      {"name": "Lepton AI",            "url": "https://lepton.ai",                        "docs": "https://lepton.ai/docs",               "tier": "speed",       "supports_vision": False, "supports_tools": False, "streaming": "native"},
        "lambda":      {"name": "Lambda Labs",          "url": "https://lambdalabs.com",                   "docs": "https://docs.lambda.ai",               "tier": "speed",       "supports_vision": False, "supports_tools": False, "streaming": "native"},
        "minimax":     {"name": "Minimax AI",           "url": "https://api.minimaxi.chat",                "docs": "https://platform.minimaxi.com/docs",   "tier": "standard",    "supports_vision": True,  "supports_tools": False, "streaming": "native"},
        "inception":   {"name": "Inception AI",         "url": "https://api.inception.ai",                 "docs": "https://api.inception.ai/docs",        "tier": "speed",       "supports_vision": False, "supports_tools": False, "streaming": "native"},
        "arcee":       {"name": "Arcee AI",             "url": "https://arcee.ai",                         "docs": "https://docs.arcee.ai",                "tier": "standard",    "supports_vision": False, "supports_tools": True,  "streaming": "native"},
        "amazon":      {"name": "Amazon Bedrock",       "url": "https://aws.amazon.com/bedrock",           "docs": "https://docs.aws.amazon.com/bedrock",  "tier": "enterprise",  "supports_vision": True,  "supports_tools": True,  "streaming": "native"},
        "nvidia":      {"name": "NVIDIA NIM",          "url": "https://integrate.api.nvidia.com",         "docs": "https://docs.api.nvidia.com",          "tier": "enterprise",  "supports_vision": True,  "supports_tools": True,  "streaming": "native"},
        "moonshot":    {"name": "Moonshot AI (Kimi)",  "url": "https://api.moonshot.cn",                  "docs": "https://platform.moonshot.cn/docs",    "tier": "specialized", "supports_vision": False, "supports_tools": True,  "streaming": "native"},
        "qwen":        {"name": "Qwen / Alibaba",      "url": "https://dashscope-intl.aliyuncs.com",      "docs": "https://help.aliyun.com/en/dashscope", "tier": "value",       "supports_vision": False, "supports_tools": True,  "streaming": "native"},
        "yi":          {"name": "01.AI (Yi)",          "url": "https://api.lingyiwanwu.com",              "docs": "https://platform.01.ai",               "tier": "value",       "supports_vision": False, "supports_tools": False, "streaming": "native"},
        "zhipu":       {"name": "Zhipu AI (GLM)",      "url": "https://open.bigmodel.cn",                 "docs": "https://open.bigmodel.cn/dev/api",     "tier": "specialized", "supports_vision": False, "supports_tools": True,  "streaming": "native"},
        "doubao":      {"name": "ByteDance Doubao",    "url": "https://ark.cn-beijing.volces.com",        "docs": "https://www.volcengine.com/docs",       "tier": "value",       "supports_vision": False, "supports_tools": False, "streaming": "native"},
        "hyperbolic":  {"name": "Hyperbolic",          "url": "https://api.hyperbolic.xyz",               "docs": "https://docs.hyperbolic.xyz",          "tier": "open-source", "supports_vision": False, "supports_tools": False, "streaming": "native"},
        "upstage":     {"name": "Upstage (Solar)",     "url": "https://api.upstage.ai",                   "docs": "https://developers.upstage.ai",        "tier": "specialized", "supports_vision": False, "supports_tools": False, "streaming": "native"},
        "writer":      {"name": "Writer (Palmyra)",    "url": "https://api.writer.com",                   "docs": "https://dev.writer.com",               "tier": "enterprise",  "supports_vision": False, "supports_tools": True,  "streaming": "native"},
        "huggingface": {"name": "HuggingFace Inference","url": "https://api-inference.huggingface.co",    "docs": "https://huggingface.co/docs/api-inference","tier": "open-source","supports_vision": False,"supports_tools": False, "streaming": "native"},
        "llama":       {"name": "Meta Llama API",      "url": "https://api.llama.com",                    "docs": "https://llama.developer.meta.com",     "tier": "open-source", "supports_vision": False, "supports_tools": True,  "streaming": "native"},
    }

    # Count models per provider
    model_counts = {}
    for entry in MODEL_REGISTRY:
        p = entry[1]
        if p:
            model_counts[p] = model_counts.get(p, 0) + 1

    data = []
    for p_id, meta in provider_meta.items():
        configured = bool(api_keys.get(p_id))
        data.append({
            "id":              p_id,
            "name":            meta["name"],
            "configured":      configured,
            "model_count":     model_counts.get(p_id, 0),
            "tier":            meta["tier"],
            "docs_url":        meta["docs"],
            "supports_vision": meta["supports_vision"],
            "supports_tools":  meta["supports_tools"],
            "streaming":       meta["streaming"],
            "status":          "active" if configured else "requires_api_key",
        })

    configured_count = sum(1 for d in data if d["configured"])
    return {
        "object":           "list",
        "data":             data,
        "total_providers":  len(data),
        "configured":       configured_count,
        "unconfigured":     len(data) - configured_count,
        "total_models":     sum(d["model_count"] for d in data),
    }


# ─────────────────────────────────────────────────────────────────────────────
# POST /v1/models/compare
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/v1/models/compare")
async def v1_compare_models(request: Request):
    """
    Run the same prompt against multiple models in parallel for side-by-side comparison.

    Request body:
        models   : list[str]  — up to 4 model IDs (e.g. ["openai/gpt-4o", "anthropic/claude-sonnet-4-6"])
        messages : list[dict] — standard chat messages
        + any standard params (temperature, max_tokens, etc.)

    Response:
        {
          "object": "comparison",
          "request_id": "compare-maars-...",
          "prompt_preview": "...",
          "results": [
            {
              "model": "openai/gpt-4o",
              "provider": "openai",
              "native_model": "gpt-4o",
              "content": "...",
              "usage": {...},
              "latency_ms": 1234,
              "cost_usd": 0.000123,
              "finish_reason": "stop",
              "error": null
            },
            ...
          ]
        }
    """
    import uuid as _uuid
    req_id = f"compare-maars-{_uuid.uuid4().hex[:12]}"

    key_doc = await _get_key_doc(request)
    user_id = key_doc["user_id"]

    ok, _, _ = await _check_budget(key_doc)
    if not ok:
        raise HTTPException(status_code=402, detail={"error": {"message": "Budget exhausted", "type": "budget_error"}})

    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail={"error": {"message": "Invalid JSON", "type": "invalid_request_error"}})

    models_list = body.get("models", [])
    messages    = body.get("messages", [])

    if not models_list:
        raise HTTPException(status_code=400, detail={"error": {"message": "'models' array is required", "type": "invalid_request_error"}})
    if not messages:
        raise HTTPException(status_code=400, detail={"error": {"message": "'messages' array is required", "type": "invalid_request_error"}})

    models_list = models_list[:4]  # cap at 4

    params: dict = {}
    for p in ["temperature", "top_p", "max_tokens", "stop", "seed"]:
        val = body.get(p)
        if val is not None:
            params[p] = val
    if "max_tokens" not in params:
        params["max_tokens"] = 2048

    api_keys     = await get_api_keys()
    prompt_text  = _extract_prompt_text(messages)

    async def run_one(model_raw: str) -> dict:
        start = time.time()
        result: dict = {"model": model_raw, "provider": None, "native_model": None,
                        "content": None, "usage": {}, "latency_ms": 0,
                        "cost_usd": 0, "finish_reason": None, "error": None}
        try:
            if model_raw in _MAARS_ALIASES:
                user_doc = await db.users.find_one({"user_id": user_id}, {"_id": 0, "credits": 1})
                credits  = (user_doc or {}).get("credits", 50)
                prov, native = await _resolve_maars_alias(model_raw, prompt_text, credits, api_keys)
            else:
                entry = _parse_model_id(model_raw) or _ID_TO_ENTRY.get(model_raw)
                if not entry:
                    raise ValueError(f"Unknown model '{model_raw}'")
                _, prov, native, _, _ = entry

            api_key = api_keys.get(prov, "")
            data, actual_prov, actual_native, mw = await _call_with_fallback(
                prov, native, messages, api_key, params, api_keys
            )
            latency = int((time.time() - start) * 1000)

            usage    = data.get("usage", {})
            pt       = usage.get("prompt_tokens", 0)
            ct       = usage.get("completion_tokens", 0)
            cost_inf = _get_pricing(actual_native)
            cost     = round((cost_inf.get("input", 0.003) * pt + cost_inf.get("output", 0.003) * ct) / 1_000_000, 8)

            content = ""
            choices = data.get("choices", [])
            if choices:
                content = choices[0].get("message", {}).get("content", "") or ""

            result.update({
                "provider":      actual_prov,
                "native_model":  actual_native,
                "content":       content,
                "usage":         usage,
                "latency_ms":    latency,
                "cost_usd":      cost,
                "finish_reason": choices[0].get("finish_reason") if choices else None,
                "model_warning": mw,
            })
        except Exception as exc:
            result["error"]      = str(exc)
            result["latency_ms"] = int((time.time() - start) * 1000)
        return result

    results = await asyncio.gather(*[run_one(m) for m in models_list])

    total_cost = sum(r.get("cost_usd", 0) for r in results)
    await _record_usage(user_id, key_doc["key"], "compare", "multi", "compare",
                        total_cost, 0, prompt_text, False)

    return {
        "object":         "comparison",
        "request_id":     req_id,
        "model_count":    len(models_list),
        "prompt_preview": prompt_text[:200],
        "results":        list(results),
        "total_cost_usd": total_cost,
    }


# ─────────────────────────────────────────────────────────────────────────────
# WEBHOOK SYSTEM  — /v1/webhooks
# ─────────────────────────────────────────────────────────────────────────────
import hmac as _hmac
import hashlib as _hashlib

WEBHOOK_EVENTS = {"budget.75", "budget.90", "budget.100", "rate_limit.exceeded", "request.completed"}


@router.post("/v1/webhooks")
async def v1_create_webhook(request: Request):
    """
    Register a webhook URL for this API key.

    Body: { "url": "https://...", "events": ["budget.75", "budget.90", "budget.100"], "description": "..." }
    Events: budget.75 (75% used), budget.90 (90%), budget.100 (100%), rate_limit.exceeded, request.completed
    """
    import uuid as _uuid
    key_doc = await _get_key_doc(request)
    user_id = key_doc["user_id"]
    key     = key_doc["key"]

    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail={"error": {"message": "Invalid JSON", "type": "invalid_request_error"}})

    url    = body.get("url", "").strip()
    events = body.get("events", ["budget.90", "budget.100"])
    desc   = body.get("description", "")

    if not url or not url.startswith("https://"):
        raise HTTPException(status_code=400, detail={"error": {"message": "url must be a valid HTTPS URL", "type": "invalid_request_error"}})

    invalid = [e for e in events if e not in WEBHOOK_EVENTS]
    if invalid:
        raise HTTPException(status_code=400, detail={"error": {
            "message": f"Invalid events: {invalid}. Valid: {sorted(WEBHOOK_EVENTS)}",
            "type": "invalid_request_error"
        }})

    # Check limit: max 5 webhooks per key
    existing = await db.gateway_webhooks.count_documents({"user_id": user_id, "active": True})
    if existing >= 5:
        raise HTTPException(status_code=400, detail={"error": {"message": "Maximum 5 webhooks per key", "type": "invalid_request_error"}})

    secret = _uuid.uuid4().hex
    wh_id  = f"wh_{_uuid.uuid4().hex[:12]}"

    doc = {
        "webhook_id":  wh_id,
        "user_id":     user_id,
        "key_prefix":  key[:16],
        "url":         url,
        "events":      events,
        "description": desc,
        "secret":      secret,
        "active":      True,
        "created_at":  datetime.now(timezone.utc).isoformat(),
        "last_fired":  None,
        "fire_count":  0,
    }
    await db.gateway_webhooks.insert_one(doc)

    return {
        "object":      "webhook",
        "id":          wh_id,
        "url":         url,
        "events":      events,
        "description": desc,
        "secret":      secret,
        "active":      True,
        "created_at":  doc["created_at"],
        "note":        "Store your secret — it will not be shown again. Use it to verify HMAC-SHA256 signatures."
    }


@router.get("/v1/webhooks")
async def v1_list_webhooks(request: Request):
    """List all webhooks for this API key."""
    key_doc = await _get_key_doc(request)
    user_id = key_doc["user_id"]

    docs = await db.gateway_webhooks.find(
        {"user_id": user_id, "active": True}, {"_id": 0, "secret": 0}
    ).to_list(50)

    return {"object": "list", "data": docs, "total": len(docs)}


@router.delete("/v1/webhooks/{webhook_id}")
async def v1_delete_webhook(webhook_id: str, request: Request):
    """Delete (deactivate) a webhook."""
    key_doc = await _get_key_doc(request)
    user_id = key_doc["user_id"]

    result = await db.gateway_webhooks.update_one(
        {"webhook_id": webhook_id, "user_id": user_id},
        {"$set": {"active": False, "deleted_at": datetime.now(timezone.utc).isoformat()}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail={"error": {"message": "Webhook not found", "type": "not_found"}})

    return {"object": "webhook", "id": webhook_id, "deleted": True}


@router.post("/v1/webhooks/{webhook_id}/test")
async def v1_test_webhook(webhook_id: str, request: Request):
    """Send a test ping to a webhook."""
    key_doc = await _get_key_doc(request)
    user_id = key_doc["user_id"]

    doc = await db.gateway_webhooks.find_one({"webhook_id": webhook_id, "user_id": user_id, "active": True})
    if not doc:
        raise HTTPException(status_code=404, detail={"error": {"message": "Webhook not found", "type": "not_found"}})

    payload = {
        "event": "test",
        "webhook_id": webhook_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": {"message": "MAARS webhook test ping — configuration verified"}
    }
    success = await _fire_webhook(doc, payload)

    return {"object": "webhook_test", "webhook_id": webhook_id, "success": success}


async def _fire_webhook(doc: dict, payload: dict) -> bool:
    """Fire a webhook with HMAC-SHA256 signature."""
    try:
        body_bytes = json.dumps(payload).encode()
        sig = _hmac.new(doc["secret"].encode(), body_bytes, _hashlib.sha256).hexdigest()

        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                doc["url"],
                content=body_bytes,
                headers={
                    "Content-Type":           "application/json",
                    "X-MAARS-Signature":      f"sha256={sig}",
                    "X-MAARS-Webhook-ID":     doc["webhook_id"],
                    "X-MAARS-Event":          payload.get("event", ""),
                    "User-Agent":             "MAARS-Webhooks/1.0",
                }
            )
        await db.gateway_webhooks.update_one(
            {"webhook_id": doc["webhook_id"]},
            {"$set": {"last_fired": datetime.now(timezone.utc).isoformat()}, "$inc": {"fire_count": 1}}
        )
        return resp.status_code < 400
    except Exception as e:
        logger.warning(f"Webhook fire failed for {doc['webhook_id']}: {e}")
        return False


async def _check_and_fire_budget_webhooks(user_id: str, key_prefix: str, budget_usd: float, used_usd: float):
    """Called after each usage record. Fires budget threshold webhooks."""
    if budget_usd <= 0:
        return
    pct = used_usd / budget_usd * 100

    # Determine which threshold events to fire
    events_to_fire = []
    if pct >= 100:
        events_to_fire.append("budget.100")
    elif pct >= 90:
        events_to_fire.append("budget.90")
    elif pct >= 75:
        events_to_fire.append("budget.75")

    if not events_to_fire:
        return

    webhooks = await db.gateway_webhooks.find(
        {"user_id": user_id, "active": True, "events": {"$in": events_to_fire}},
        {"_id": 0}
    ).to_list(10)

    for wh in webhooks:
        for evt in events_to_fire:
            if evt in wh.get("events", []):
                payload = {
                    "event": evt,
                    "webhook_id": wh["webhook_id"],
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "data": {
                        "budget_usd":   budget_usd,
                        "used_usd":     round(used_usd, 6),
                        "used_pct":     round(pct, 1),
                        "key_prefix":   key_prefix,
                    }
                }
                asyncio.create_task(_fire_webhook(wh, payload))
