"""MAARS Universal LLM Gateway.

Smart-routes across all 33 providers using:
  - Task-type classification (code, math, reasoning, creative, translation, ...)
  - Credit-budget awareness (micro / tight / normal / generous)
  - Per-task model preference tables (best model for that task goes first)
  - Cheapest-first fallback chain within each quality tier

Endpoints:
  POST /api/universal/chat              — smart-routed completion
  GET  /api/universal/models            — full catalog with cost / tier / availability
  GET  /api/universal/stats             — aggregated usage & savings report
  GET  /api/universal/key/status        — PAYG gateway key status & budget
  POST /api/universal/key/topup         — pay-as-you-go credit top-up
  GET  /api/universal/key/pricing       — pricing tiers and allocation breakdown
  GET  /api/universal/key/transactions  — top-up history
"""
import time
import uuid
import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from auth import get_current_user
from db import db
from models.schemas import User
from services.llm_service import call_direct_llm, MODEL_COSTS_MAP, MODEL_CREDIT_COSTS
from shared.utils import get_api_keys
from shared.constants import PAYG_CONFIG

logger = logging.getLogger(__name__)
router = APIRouter()

# ─────────────────────────────────────────────────────────────────────────────
# MODEL ROSTER  — cheapest-first within each tier
# blended_cost ≈ (input + output) / 2  per 1M tokens
# ─────────────────────────────────────────────────────────────────────────────

ECONOMY_MODELS = [
    # ≤ $0.80 / 1M blended
    ("groq",       "llama-3.1-8b-instant"),                                    # $0.065
    ("cerebras",   "llama3.1-8b"),                                             # $0.10
    ("nvidia",     "meta/llama-3.1-8b-instruct"),                              # $0.10
    ("gemini",     "gemini-2.5-flash-lite"),                                   # $0.094
    ("qwen",       "qwen-turbo"),                                              # $0.15
    ("mistral",    "mistral-nemo"),                                            # $0.15
    ("groq",       "gemma2-9b-it"),                                            # $0.20
    ("mistral",    "mistral-small-latest"),                                    # $0.20
    ("deepseek",   "deepseek-chat"),                                           # $0.21
    ("deepseek",   "deepseek-v3-0324"),                                        # $0.21
    ("gemini",     "gemini-2.5-flash"),                                        # $0.19
    ("gemini",     "gemini-3-flash-preview"),                                  # $0.19
    ("moonshot",   "moonshot-v1-8k"),                                          # $0.18
    ("groq",       "llama-4-scout-17b-16e-instruct"),                          # $0.23
    ("openai",     "gpt-4.1-nano"),                                            # $0.25
    ("ai21",       "jamba-mini-1.7"),                                          # $0.30
    ("groq",       "qwen-qwq-32b"),                                            # $0.34
    ("cerebras",   "qwen-3-32b"),                                              # $0.40
    ("cohere",     "command-r"),                                               # $0.38
    ("openai",     "gpt-4o-mini"),                                             # $0.38
    ("fireworks",  "accounts/fireworks/models/llama4-scout-instruct-basic"),   # $0.38
    ("fireworks",  "accounts/fireworks/models/qwen3-30b-a3b-instruct"),        # $0.38
    ("together",   "Qwen/Qwen3-235B-A22B-Instruct-FP8"),                      # $0.40
    ("xai",        "grok-3-mini"),                                             # $0.40
    ("novita",     "meta-llama/hermes-3-llama-3.1-70b"),                       # $0.40
    ("cerebras",   "llama-3.3-70b"),                                           # $0.60
    ("nvidia",     "meta/llama-3.3-70b-instruct"),                             # $0.60
    ("sambanova",  "Meta-Llama-3.3-70B-Instruct"),                             # $0.60
    ("groq",       "llama-4-maverick-17b-128e-instruct"),                      # $0.64
    ("together",   "Qwen/Qwen2.5-72B-Instruct-Turbo"),                        # $0.72
    ("qwen",       "qwen2.5-72b-instruct"),                                    # $0.72
]

STANDARD_MODELS = [
    # $0.80 – $6 / 1M blended
    ("openai",     "gpt-4.1-mini"),                                            # $1.00
    ("qwen",       "qwen-plus"),                                               # $0.80
    ("moonshot",   "moonshot-v1-32k"),                                         # $0.44
    ("nvidia",     "nvidia/llama-3.1-nemotron-70b-instruct"),                  # $0.35
    ("mistral",    "codestral-latest"),                                        # $0.60
    ("together",   "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8"),      # $0.56
    ("together",   "meta-llama/Llama-3.3-70B-Instruct-Turbo"),                # $0.88
    ("fireworks",  "accounts/fireworks/models/llama4-maverick-instruct-basic"), # $0.64
    ("sambanova",  "Qwen2.5-72B-Instruct"),                                    # $0.70
    ("fireworks",  "accounts/fireworks/models/phi-4"),                         # $0.90
    ("perplexity", "sonar"),                                                   # $1.00
    ("novita",     "meta-llama/llama-4-maverick"),                              # $0.56
    ("mistral",    "mistral-medium-latest"),                                   # $1.20
    ("deepseek",   "deepseek-reasoner"),                                       # $1.37
    ("deepseek",   "deepseek-r1-0528"),                                        # $1.37
    ("sambanova",  "DeepSeek-R1-0528"),                                        # $1.30
    ("fireworks",  "accounts/fireworks/models/deepseek-v3"),                   # $1.12
    ("moonshot",   "moonshot-v1-128k"),                                        # $0.73
    ("anthropic",  "claude-haiku-4-5-20251001"),                               # $2.40
    ("qwen",       "qwen-max"),                                                # $6.00
    ("qwen",       "qwen3-235b-a22b"),                                         # $0.55
    ("perplexity", "sonar-reasoning"),                                         # $3.00
    ("gemini",     "gemini-2.5-pro"),                                          # $5.63
    ("gemini",     "gemini-3-pro-preview"),                                    # $3.13
    ("mistral",    "mistral-large-latest"),                                    # $4.00
    ("mistral",    "pixtral-large-latest"),                                    # $4.00
    ("ai21",       "jamba-large-1.7"),                                         # $5.00
    ("openai",     "gpt-4.1"),                                                 # $5.00
    ("openai",     "gpt-4o"),                                                  # $6.25
    ("cohere",     "command-r-plus"),                                          # $6.25
    ("cohere",     "command-a-03-2025"),                                       # $6.25
    ("xai",        "grok-2"),                                                  # $6.00
]

PREMIUM_MODELS = [
    # $6+ / 1M blended — highest quality / specialised reasoning
    ("openai",     "o4-mini"),                                                 # $2.75
    ("openai",     "o3-mini"),                                                 # $2.75
    ("nvidia",     "nvidia/llama-3.1-nemotron-ultra-253b-v1"),                 # $1.90
    ("perplexity", "sonar-reasoning-pro"),                                     # $5.00
    ("perplexity", "sonar-deep-research"),                                     # $5.00
    ("together",   "deepseek-ai/DeepSeek-R1"),                                # $5.00
    ("perplexity", "sonar-pro"),                                               # $9.00
    ("openai",     "gpt-5.2"),                                                 # $6.25
    ("openai",     "gpt-4o"),                                                  # $6.25 (multimodal)
    ("anthropic",  "claude-sonnet-4-6"),                                       # $9.00
    ("anthropic",  "claude-sonnet-4-5-20250929"),                              # $9.00
    ("arcee",      "arcee-maestro"),                                            # $9.00
    ("minimax",    "minimax-text-01"),                                          # $5.00
    ("xai",        "grok-3"),                                                  # $9.00
    ("openai",     "o3"),                                                      # $25.00
    ("openai",     "o4"),                                                      # $37.50
    ("anthropic",  "claude-opus-4-6"),                                         # $45.00
    ("anthropic",  "claude-opus-4-5-20251101"),                                # $45.00
]

ALL_TIERS = {
    "economy":  ECONOMY_MODELS,
    "standard": STANDARD_MODELS,
    "premium":  PREMIUM_MODELS,
}

# Flat list for the /models endpoint
ALL_MODELS_FLAT = [
    *[(*m, "economy")  for m in ECONOMY_MODELS],
    *[(*m, "standard") for m in STANDARD_MODELS],
    *[(*m, "premium")  for m in PREMIUM_MODELS],
]

# Quick tier lookup: model_id → tier
_MODEL_TO_TIER: dict = {}
for _m in ECONOMY_MODELS:  _MODEL_TO_TIER[_m[1]] = "economy"
for _m in STANDARD_MODELS: _MODEL_TO_TIER[_m[1]] = "standard"
for _m in PREMIUM_MODELS:  _MODEL_TO_TIER[_m[1]] = "premium"


# ─────────────────────────────────────────────────────────────────────────────
# SMART ROUTING ENGINE
# ─────────────────────────────────────────────────────────────────────────────

# Task-type keyword banks (scored by keyword count hit)
_TASK_SIGNALS = {
    "code": [
        "code", "function", "debug", "python", "javascript", "typescript", "react", "vue",
        "angular", "api", "algorithm", "implement", "refactor", "sql", "git", "bug", "deploy",
        "docker", "kubernetes", "backend", "frontend", "html", "css", "class", "method",
        "variable", "loop", "recursion", "binary", "script", "bash", "shell", "regex",
    ],
    "math": [
        "calculate", "equation", "formula", "solve", "math", "statistics", "probability",
        "integral", "derivative", "proof", "algebra", "geometry", "calculus", "matrix",
        "vector", "eigenvalue", "factorial", "fibonacci", "prime", "modulo", "sum of",
        "mean", "median", "variance", "standard deviation", "permutation", "combination",
    ],
    "reasoning": [
        "analyze", "analyse", "reason", "evaluate", "compare", "assess", "strategy",
        "decision", "pros and cons", "trade-off", "tradeoff", "think through", "explain why",
        "because", "therefore", "hypothesis", "infer", "deduce", "conclusion", "argument",
        "logical", "implication", "cause and effect", "critique", "justify",
    ],
    "legal": [
        "contract", "legal", "compliance", "regulation", "law", "clause", "liability",
        "jurisdiction", "terms", "policy", "agreement", "gdpr", "hipaa", "intellectual property",
        "trademark", "copyright", "patent", "lawsuit", "litigation", "nda", "indemnify",
        "arbitration", "statute", "amendment", "breach",
    ],
    "creative": [
        "write", "story", "poem", "blog", "article", "creative", "narrative", "script",
        "compelling", "engaging", "tone", "voice", "ad copy", "headline", "tagline",
        "character", "plot", "novel", "fiction", "marketing copy", "email campaign",
        "slogan", "caption", "pitch", "sales page", "copywrite",
    ],
    "translation": [
        "translate", "translation", "in french", "in spanish", "in german", "in arabic",
        "in chinese", "in japanese", "in hindi", "in portuguese", "in russian", "in korean",
        "from english", "to english", "localize", "multilingual", "언어", "traduction",
        "übersetzen", "翻译", "traducir",
    ],
    "summary": [
        "summarize", "summary", "tldr", "tl;dr", "brief", "key points", "main points",
        "condense", "shorten", "highlights", "recap", "overview", "in a nutshell",
        "bullet points of", "give me the gist",
    ],
    "research": [
        "research", "comprehensive", "in-depth", "detailed report", "whitepaper", "study",
        "literature review", "find information", "what are the latest", "current news",
        "recent developments", "search for", "look up", "fact check", "citations",
        "sources", "references", "wikipedia", "news about",
    ],
    "data": [
        "data", "analytics", "metrics", "csv", "spreadsheet", "chart", "statistics",
        "dashboard", "kpi", "forecast", "regression", "correlation", "table", "excel",
        "pandas", "dataframe", "json", "xml", "parse", "extract", "pivot", "aggregate",
        "group by", "filter rows", "column",
    ],
    "vision": [
        "image", "photo", "picture", "visual", "describe this", "what do you see",
        "identify", "recognize", "ocr", "diagram", "chart shows", "screenshot",
        "look at this", "in the picture", "from the image",
    ],
    "chat": [
        "hello", "hi ", "hey ", "how are you", "what's up", "thanks", "thank you",
        "good morning", "good night", "tell me a joke", "how do you feel", "nice to meet",
        "greetings", "pleased to",
    ],
}

# Per-task preferred models — best-first for that specific task type.
# The router intersects these with credit-allowed tiers.
TASK_PREFERRED_MODELS: dict = {
    "code": [
        ("openai",     "gpt-4.1"),
        ("anthropic",  "claude-sonnet-4-6"),
        ("deepseek",   "deepseek-v3-0324"),
        ("openai",     "gpt-5.2"),
        ("fireworks",  "accounts/fireworks/models/llama4-maverick-instruct-basic"),
        ("cerebras",   "llama-3.3-70b"),
        ("groq",       "llama-4-maverick-17b-128e-instruct"),
        ("mistral",    "codestral-latest"),
        ("openai",     "gpt-4.1-mini"),
        ("deepseek",   "deepseek-chat"),
        ("groq",       "llama-4-scout-17b-16e-instruct"),
        ("cerebras",   "llama3.1-8b"),
    ],
    "math": [
        ("openai",     "o4-mini"),
        ("openai",     "o3-mini"),
        ("deepseek",   "deepseek-r1-0528"),
        ("deepseek",   "deepseek-reasoner"),
        ("groq",       "qwen-qwq-32b"),
        ("together",   "deepseek-ai/DeepSeek-R1"),
        ("openai",     "o4"),
        ("sambanova",  "DeepSeek-R1-0528"),
        ("anthropic",  "claude-sonnet-4-6"),
        ("openai",     "gpt-4.1"),
    ],
    "reasoning": [
        ("openai",     "o4-mini"),
        ("deepseek",   "deepseek-r1-0528"),
        ("anthropic",  "claude-sonnet-4-6"),
        ("openai",     "gpt-4.1"),
        ("groq",       "qwen-qwq-32b"),
        ("openai",     "o3"),
        ("perplexity", "sonar-reasoning-pro"),
        ("anthropic",  "claude-opus-4-6"),
        ("xai",        "grok-3"),
        ("deepseek",   "deepseek-reasoner"),
        ("nvidia",     "nvidia/llama-3.1-nemotron-ultra-253b-v1"),
    ],
    "legal": [
        ("anthropic",  "claude-sonnet-4-6"),
        ("anthropic",  "claude-opus-4-6"),
        ("openai",     "gpt-5.2"),
        ("openai",     "gpt-4.1"),
        ("cohere",     "command-a-03-2025"),
        ("xai",        "grok-3"),
        ("openai",     "o4-mini"),
        ("anthropic",  "claude-haiku-4-5-20251001"),
        ("openai",     "gpt-4o"),
    ],
    "creative": [
        ("anthropic",  "claude-sonnet-4-6"),
        ("anthropic",  "claude-opus-4-6"),
        ("openai",     "gpt-5.2"),
        ("openai",     "gpt-4.1"),
        ("xai",        "grok-3"),
        ("mistral",    "mistral-large-latest"),
        ("openai",     "gpt-4.1-mini"),
        ("deepseek",   "deepseek-chat"),
        ("cerebras",   "llama-3.3-70b"),
    ],
    "translation": [
        ("deepseek",   "deepseek-chat"),
        ("qwen",       "qwen-plus"),
        ("qwen",       "qwen-turbo"),
        ("mistral",    "mistral-small-latest"),
        ("groq",       "llama-4-scout-17b-16e-instruct"),
        ("gemini",     "gemini-2.5-flash"),
        ("moonshot",   "moonshot-v1-8k"),
        ("openai",     "gpt-4.1-nano"),
        ("cerebras",   "llama3.1-8b"),
    ],
    "summary": [
        ("groq",       "llama-4-scout-17b-16e-instruct"),
        ("gemini",     "gemini-2.5-flash"),
        ("cerebras",   "llama-3.3-70b"),
        ("deepseek",   "deepseek-chat"),
        ("openai",     "gpt-4.1-nano"),
        ("mistral",    "mistral-nemo"),
        ("anthropic",  "claude-haiku-4-5-20251001"),
        ("groq",       "llama-3.1-8b-instant"),
    ],
    "research": [
        ("perplexity", "sonar-deep-research"),
        ("perplexity", "sonar-pro"),
        ("perplexity", "sonar-reasoning"),
        ("anthropic",  "claude-opus-4-6"),
        ("openai",     "gpt-5.2"),
        ("anthropic",  "claude-sonnet-4-6"),
        ("openai",     "gpt-4.1"),
        ("moonshot",   "moonshot-v1-128k"),
    ],
    "data": [
        ("openai",     "gpt-4o"),
        ("gemini",     "gemini-2.5-pro"),
        ("openai",     "gpt-4.1"),
        ("anthropic",  "claude-sonnet-4-6"),
        ("deepseek",   "deepseek-chat"),
        ("openai",     "gpt-4.1-mini"),
        ("groq",       "llama-4-maverick-17b-128e-instruct"),
        ("qwen",       "qwen-max"),
    ],
    "vision": [
        ("openai",     "gpt-4o"),
        ("gemini",     "gemini-2.5-pro"),
        ("anthropic",  "claude-sonnet-4-6"),
        ("mistral",    "pixtral-large-latest"),
        ("openai",     "gpt-5.2"),
        ("xai",        "grok-3"),
    ],
    "chat": [
        ("groq",       "llama-4-scout-17b-16e-instruct"),
        ("cerebras",   "llama3.1-8b"),
        ("gemini",     "gemini-2.5-flash"),
        ("openai",     "gpt-4.1-nano"),
        ("deepseek",   "deepseek-chat"),
        ("mistral",    "mistral-nemo"),
        ("xai",        "grok-3-mini"),
        ("groq",       "llama-3.1-8b-instant"),
    ],
    "general": [
        ("openai",     "gpt-4.1-mini"),
        ("gemini",     "gemini-2.5-flash"),
        ("deepseek",   "deepseek-chat"),
        ("cerebras",   "llama-3.3-70b"),
        ("openai",     "gpt-4.1"),
        ("anthropic",  "claude-sonnet-4-6"),
    ],
}


def _classify_task(prompt: str) -> dict:
    """Score the prompt against all task-type keyword banks.
    Returns the winning task type, complexity bucket, and full scores."""
    lower = prompt.lower()
    words = len(prompt.split())

    scores = {task: sum(1 for kw in kws if kw in lower) for task, kws in _TASK_SIGNALS.items()}
    best_task = max(scores, key=scores.get) if max(scores.values()) > 0 else "general"

    complexity = (
        "micro"    if words < 10  else
        "simple"   if words < 40  else
        "moderate" if words < 150 else
        "complex"  if words < 400 else
        "extensive"
    )

    return {
        "type":       best_task,
        "score":      scores.get(best_task, 0),
        "complexity": complexity,
        "words":      words,
        "all_scores": scores,
    }


def _credit_budget(available: int) -> str:
    """Translate current credit balance into a budget label."""
    if available <= 3:   return "micro"    # economy only, absolute cheapest
    if available <= 10:  return "tight"    # economy first, standard as fallback
    if available <= 50:  return "normal"   # full task-aware routing
    return "generous"                      # no cost constraints, route by quality


def _tier_order(task_type: str, complexity: str, budget: str, quality_override: str) -> list:
    """Return the ordered quality tiers to attempt for this request."""
    if quality_override and quality_override not in ("auto", ""):
        others = [t for t in ("economy", "standard", "premium") if t != quality_override]
        return [quality_override] + others

    # Budget overrides task preference when credits are low
    if budget == "micro":
        return ["economy"]
    if budget == "tight":
        return ["economy", "standard"]

    HIGH_QUALITY_TASKS = {"code", "math", "reasoning", "legal", "research", "vision"}
    CHEAP_TASKS        = {"translation", "summary", "chat"}

    if task_type in HIGH_QUALITY_TASKS and complexity in ("complex", "extensive"):
        return ["premium", "standard", "economy"]
    if task_type in HIGH_QUALITY_TASKS and complexity == "moderate":
        return ["standard", "premium", "economy"]
    if task_type in CHEAP_TASKS or complexity in ("micro", "simple"):
        return ["economy", "standard", "premium"]
    # Default: standard → economy → premium
    return ["standard", "economy", "premium"]


# ─────────────────────────────────────────────────────────────────────────────
# FREE-FIRST ROUTING — aggressive free-tier preference for the cost-conscious
# gateway. "Route clients to free models silently whenever the task can be
# handled by them; escalate to paid only when free genuinely can't deliver.
# Client sees same output, same credit cost, margin goes to MAARS."
#
# Two variables decide whether to go free-first:
#   1. Task complexity (light / medium / heavy) — inferred from the prompt
#   2. Quality override (client-set) — if client explicitly asks "premium" or
#      "flagship", we honor it and skip the free-first stage.
#
# The free-first candidate list is hand-curated from PROVIDER_ALLIES.md — the
# production-quality free-tier models that handle 90%+ of real prompts
# (Cerebras = 1800 tok/s, Groq = LPU, SambaNova = RDU DeepSeek, Gemini Flash,
# OpenRouter :free tier, HF router).
# ─────────────────────────────────────────────────────────────────────────────

# Ordered from "most-likely-to-succeed-fast" to "broadest-catalog-fallback".
# Model IDs are the EXACT strings each provider's /v1/models returns — this
# is critical because _call_with_fallback validates the requested model
# against the provider's live list and skips to the FALLBACK_CHAIN (which
# defaults to OpenAI) on mismatch. The hyphenation style varies per provider:
#   Cerebras:   llama3.1-8b       (no hyphen after "llama")
#   Groq:       llama-3.1-8b-instant
#   SambaNova:  Meta-Llama-3.3-70B-Instruct (CapCase)
#   NVIDIA:     meta/llama-3.1-8b-instruct
_FREE_FIRST_CHAIN_LIGHT = [
    # Fastest + cheapest: free inference hardware (LPU, RDU, WSE)
    # (Cerebras has only llama3.1-8b in their current Llama lineup — no 3.3-70b)
    ("cerebras",    "llama3.1-8b"),
    ("groq",        "llama-3.1-8b-instant"),
    ("groq",        "llama-3.3-70b-versatile"),
    ("sambanova",   "Meta-Llama-3.3-70B-Instruct"),
    # Free-tier commercial-quality models
    ("gemini",      "gemini-2.5-flash"),
    ("gemini",      "gemini-2.0-flash-lite"),
    # NVIDIA free tier
    ("nvidia",      "meta/llama-3.1-8b-instruct"),
    ("nvidia",      "meta/llama-3.3-70b-instruct"),
    # Free pass-throughs on OpenRouter
    ("openrouter",  "openai/gpt-oss-120b:free"),
    # HF router free tier (OpenAI-compatible model slugs)
    ("huggingface", "meta-llama/Llama-3.1-8B-Instruct"),
    # Zhipu free tier
    ("zhipu",       "glm-4.5-flash"),
]

# For medium tasks, free-first list plus stronger open models still on free tiers.
_FREE_FIRST_CHAIN_MEDIUM = _FREE_FIRST_CHAIN_LIGHT + [
    # Free RDU inference on frontier reasoning models
    ("sambanova",   "DeepSeek-V3.1"),
    # Cheapest paid fallback — DeepSeek V3 at $0.27/M tokens is near-free
    ("deepseek",    "deepseek-chat"),
]

# Keywords that force a "heavy" classification — skip free-first, use smart
# ranking directly so premium providers can win the score.
_HEAVY_KEYWORDS = {
    "legal", "medical", "compliance", "contract", "regulation", "fiduciary",
    "audit", "diagnose", "diagnosis", "prescription",
    "prove", "theorem", "proof", "lemma",
    "architect", "design the system", "production-ready", "enterprise-grade",
    "complex reasoning", "deep analysis", "thorough analysis", "multi-step reasoning",
    "research paper", "academic", "peer-reviewed",
    "refactor the entire", "rewrite this codebase",
}

# Long prompts (> N words) are heavy by default.
_HEAVY_WORD_THRESHOLD = 400


def _classify_complexity(prompt: str) -> str:
    """Return 'light', 'medium', or 'heavy' — drives free-first decision."""
    words = len((prompt or "").split())
    lower = (prompt or "").lower()

    # Heavy signals override everything
    if any(kw in lower for kw in _HEAVY_KEYWORDS):
        return "heavy"
    if words >= _HEAVY_WORD_THRESHOLD:
        return "heavy"

    # Light = quick Q&A, greetings, reformat, translate
    if words < 30:
        return "light"

    # Medium = most real-world prompts (code assist, summaries, multi-step tool use)
    if words < 200:
        return "medium"

    # Everything else defaults to medium — free tier handles it well
    return "medium"


def _smart_candidates(
    prompt: str,
    available_credits: int,
    quality_override: str = None,
) -> tuple:
    """Build an ordered (provider, model) candidate list.

    Strategy (in order):
      0. FREE-FIRST bias — if task is light/medium AND client hasn't asked
         for premium/flagship quality, prepend free-tier providers so they
         get tried first. The fallback chain in _call_with_fallback takes
         care of auto-escalation if a free provider errors out.
      A. Smart Router (ML-scored) — scores ALL 169+ models using composite
         scoring (task_fit + cost + quality + health + latency).
      B. Legacy Router (keyword + tier) — deep fallback.

    Client transparency: regardless of which provider ends up serving, the
    response shape (`/v1/chat/completions` format) is identical, and credit
    cost is set by the MAARS plan, not the underlying provider cost —
    so the client experience and billing are invariant.

    Returns: (candidates: list[tuple], task_info: dict)
    """
    complexity = _classify_complexity(prompt)
    force_paid = quality_override in ("premium", "flagship")

    free_first: list[tuple[str, str]] = []
    if not force_paid and complexity in ("light", "medium"):
        free_first = list(
            _FREE_FIRST_CHAIN_LIGHT if complexity == "light" else _FREE_FIRST_CHAIN_MEDIUM
        )

    # ── Path A: Smart Router (scores every model in the catalog) ────────
    try:
        from services.routing import smart_router
        ranked = smart_router.rank(
            prompt,
            quality_override=quality_override,
        )
        if ranked:
            ml_candidates = [(r["provider"], r["model_id"]) for r in ranked]
            task_info = {
                "type": smart_router.classify_prompt(prompt),
                "complexity": complexity,
                "router": "smart",
                "free_first": bool(free_first),
                "top_score": ranked[0]["score"] if ranked else 0,
            }
            # Compose: free_first → smart ranked → legacy deep-fallback.
            combined: list[tuple[str, str]] = []
            seen: set = set()
            for pair in free_first:
                if pair not in seen:
                    combined.append(pair); seen.add(pair)
            for pair in ml_candidates:
                if pair not in seen:
                    combined.append(pair); seen.add(pair)
            legacy, _ = _legacy_smart_candidates(prompt, available_credits, quality_override)
            for pair in legacy:
                if pair not in seen:
                    combined.append(pair); seen.add(pair)
            return combined, task_info
    except Exception as exc:
        import logging
        logging.getLogger(__name__).warning("smart_router failed, falling back to legacy: %s", exc)

    # ── Path B: Legacy Router (keyword + tier intersection) ─────────────
    legacy_candidates, task_info = _legacy_smart_candidates(prompt, available_credits, quality_override)
    if free_first:
        seen: set = set()
        combined: list[tuple[str, str]] = []
        for pair in free_first + legacy_candidates:
            if pair not in seen:
                combined.append(pair); seen.add(pair)
        task_info["free_first"] = True
        return combined, task_info
    return legacy_candidates, task_info


def _legacy_smart_candidates(
    prompt: str,
    available_credits: int,
    quality_override: str = None,
) -> tuple:
    """Original keyword-based routing — preserved as fallback."""
    task = _classify_task(prompt)
    budget = _credit_budget(available_credits)
    tiers = _tier_order(task["type"], task["complexity"], budget, quality_override or "")

    seen: set = set()
    candidates: list = []

    def _add(pair):
        if pair not in seen:
            candidates.append(pair)
            seen.add(pair)

    for pair in TASK_PREFERRED_MODELS.get(task["type"], []):
        model_tier = _MODEL_TO_TIER.get(pair[1], "standard")
        if model_tier in tiers:
            _add(pair)

    for tier in tiers:
        # ALL_TIERS only has economy/standard/premium. "flagship" maps to
        # premium here for candidate expansion — smart router handles the
        # genuine flagship weighting upstream.
        effective_tier = "premium" if tier == "flagship" else tier
        for pair in ALL_TIERS.get(effective_tier, []):
            _add(pair)

    task["router"] = "legacy"
    return candidates, task


# ─────────────────────────────────────────────────────────────────────────────
# REQUEST / RESPONSE SCHEMAS
# ─────────────────────────────────────────────────────────────────────────────

class UniversalChatRequest(BaseModel):
    prompt: str
    system_message: Optional[str] = "You are a helpful AI assistant."
    model:    Optional[str] = None   # explicit model override
    provider: Optional[str] = None   # explicit provider override
    quality:  Optional[str] = None   # economy | standard | premium | auto
    max_tokens: Optional[int] = 4096


class UniversalChatResponse(BaseModel):
    response: str
    model: str
    provider: str
    quality_tier: str
    task_type: str
    task_complexity: str
    credits_used: int
    cost_usd: float
    latency_ms: int
    fallback_used: bool
    attempts: int


# ─────────────────────────────────────────────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/universal/chat", response_model=UniversalChatResponse)
async def universal_chat(
    body: UniversalChatRequest,
    current_user: User = Depends(get_current_user),
):
    """Universal LLM gateway with smart routing.

    Routing priority:
      1. Explicit model+provider override (if both provided)
      2. Task-type preferred models (filtered by credit budget)
      3. Full tier fallback chain

    Quality tiers auto-selected based on prompt complexity + credit balance.
    Specify quality='economy'|'standard'|'premium' to override."""

    user_doc = await db.users.find_one(
        {"user_id": current_user.user_id}, {"_id": 0, "credits": 1}
    )
    available_credits = (user_doc or {}).get("credits", 0)
    if available_credits <= 0:
        raise HTTPException(status_code=402, detail="Insufficient credits")

    api_keys = await get_api_keys()
    quality_override = body.quality if body.quality not in (None, "auto", "") else None

    # Build candidate list
    candidates, task_info = _smart_candidates(body.prompt, available_credits, quality_override)

    # If explicit model+provider override, put it first
    if body.model and body.provider:
        explicit = (body.provider, body.model)
        candidates = [explicit] + [c for c in candidates if c != explicit]

    # Derive the effective quality tier label for logging
    budget = _credit_budget(available_credits)
    effective_tier = _tier_order(
        task_info["type"], task_info["complexity"], budget, quality_override or ""
    )[0]

    start = time.time()
    last_error = None
    attempts = 0

    for provider, model_id in candidates:
        api_key = api_keys.get(provider, "") or api_keys.get("emergent", "")
        if not api_key:
            continue

        attempts += 1
        try:
            response_text = await call_direct_llm(
                provider=provider,
                model_name=model_id,
                system_prompt=body.system_message,
                content=body.prompt,
                attachments=[],
                api_key=api_key,
            )

            latency_ms = int((time.time() - start) * 1000)
            model_key = model_id.split("/")[-1]
            credits_used = MODEL_CREDIT_COSTS.get(model_key, 2)
            cost_info = MODEL_COSTS_MAP.get(model_id, {"input": 0.003, "output": 0.003})
            est_tokens = max(len(body.prompt.split()) * 1.3, 100)
            cost_usd = round(
                (cost_info["input"] + cost_info["output"]) / 2 * est_tokens / 1_000_000, 6
            )

            # Deduct credits
            await db.users.update_one(
                {"user_id": current_user.user_id},
                {"$inc": {"credits": -credits_used}},
            )

            # Track actual USD cost against client's AI budget allocation
            await db.client_gateway_keys.update_one(
                {"user_id": current_user.user_id},
                {"$inc": {"used_usd": cost_usd}},
            )

            # Log usage with full routing metadata
            await db.llm_usage_logs.insert_one({
                "log_id": f"ulg_{current_user.user_id[:8]}_{int(time.time())}",
                "user_id": current_user.user_id,
                "source": "universal_gateway",
                "provider": provider,
                "model": model_id,
                "quality_tier": effective_tier,
                "task_type": task_info["type"],
                "task_complexity": task_info["complexity"],
                "credit_budget": budget,
                "credits_used": credits_used,
                "cost_usd": cost_usd,
                "latency_ms": latency_ms,
                "attempts": attempts,
                "fallback_used": attempts > 1,
                "prompt_words": task_info["words"],
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })

            return UniversalChatResponse(
                response=response_text,
                model=model_id,
                provider=provider,
                quality_tier=effective_tier,
                task_type=task_info["type"],
                task_complexity=task_info["complexity"],
                credits_used=credits_used,
                cost_usd=cost_usd,
                latency_ms=latency_ms,
                fallback_used=attempts > 1,
                attempts=attempts,
            )

        except Exception as e:
            last_error = str(e)
            logger.warning(f"Universal gateway: {provider}/{model_id} failed — {e}")
            continue

    raise HTTPException(
        status_code=503,
        detail=f"All providers exhausted after {attempts} attempts. Last error: {last_error}",
    )


@router.get("/universal/models")
async def list_universal_models(current_user: User = Depends(get_current_user)):
    """Return every model in the registry with cost, tier, task strengths, and availability."""
    api_keys = await get_api_keys()

    # Task strengths by model (for UI display)
    MODEL_STRENGTHS = {
        "gpt-5.2": ["code", "reasoning", "creative", "legal"],
        "gpt-4.1": ["code", "reasoning", "data"],
        "gpt-4.1-mini": ["code", "general", "chat"],
        "gpt-4.1-nano": ["summary", "translation", "chat"],
        "gpt-4o": ["vision", "data", "multimodal"],
        "gpt-4o-mini": ["chat", "summary"],
        "o4": ["math", "reasoning"],
        "o4-mini": ["math", "reasoning", "code"],
        "o3": ["math", "reasoning"],
        "o3-mini": ["math", "code"],
        "claude-opus-4-6": ["reasoning", "creative", "legal", "research"],
        "claude-sonnet-4-6": ["creative", "reasoning", "code", "legal"],
        "claude-haiku-4-5-20251001": ["summary", "chat", "translation"],
        "gemini-2.5-pro": ["data", "reasoning", "vision"],
        "gemini-2.5-flash": ["summary", "translation", "chat"],
        "gemini-2.5-flash-lite": ["chat", "translation"],
        "deepseek-v3-0324": ["code", "data", "translation"],
        "deepseek-r1-0528": ["math", "reasoning", "code"],
        "grok-3": ["reasoning", "creative", "research"],
        "grok-3-mini": ["chat", "summary"],
        "codestral-latest": ["code"],
        "mistral-large-latest": ["creative", "reasoning"],
        "mistral-nemo": ["chat", "translation", "summary"],
        "sonar-deep-research": ["research"],
        "sonar-pro": ["research", "factual"],
        "sonar-reasoning": ["research", "reasoning"],
        "qwen-max": ["data", "reasoning", "translation"],
        "qwen-plus": ["translation", "code"],
        "qwen-turbo": ["translation", "summary", "chat"],
        "moonshot-v1-128k": ["research", "long-context"],
        "moonshot-v1-32k": ["research", "creative"],
        "llama-3.3-70b": ["code", "reasoning", "chat"],  # cerebras
        "llama3.1-8b": ["chat", "summary", "translation"],  # cerebras
        "qwen-qwq-32b": ["math", "reasoning"],
    }

    result = []
    for provider, model_id, tier in ALL_MODELS_FLAT:
        has_key = bool(api_keys.get(provider) or api_keys.get("emergent"))
        cost_info = MODEL_COSTS_MAP.get(model_id, {})
        model_key = model_id.split("/")[-1]
        result.append({
            "model_id": model_id,
            "provider": provider,
            "tier": tier,
            "task_strengths": MODEL_STRENGTHS.get(model_key, ["general"]),
            "credits_per_call": MODEL_CREDIT_COSTS.get(model_key, 2),
            "input_cost_per_1m": cost_info.get("input", 0),
            "output_cost_per_1m": cost_info.get("output", 0),
            "blended_cost_per_1m": round((cost_info.get("input", 0) + cost_info.get("output", 0)) / 2, 4),
            "available": has_key,
        })

    providers_active = len({r["provider"] for r in result if r["available"]})
    return {
        "total": len(result),
        "providers_configured": providers_active,
        "providers_total": 19,
        "models": result,
        "routing": "Smart router — task-aware, credit-budget-aware, cheapest-capable model selected",
    }


@router.get("/universal/stats")
async def universal_stats(current_user: User = Depends(get_current_user)):
    """Aggregated usage stats including task-type and complexity breakdowns."""
    logs = await db.llm_usage_logs.find(
        {"source": "universal_gateway"},
        {"_id": 0}
    ).sort("timestamp", -1).limit(1000).to_list(1000)

    total_calls  = len(logs)
    total_cost   = round(sum(l.get("cost_usd", 0) for l in logs), 6)
    total_credits= sum(l.get("credits_used", 0) for l in logs)
    fallback_cnt = sum(1 for l in logs if l.get("fallback_used"))

    by_provider: dict = {}
    by_tier: dict = {}
    by_task: dict = {}
    by_budget: dict = {}

    for l in logs:
        p = l.get("provider", "unknown")
        t = l.get("quality_tier", "standard")
        tt = l.get("task_type", "general")
        b = l.get("credit_budget", "normal")
        by_provider[p] = by_provider.get(p, 0) + 1
        by_tier[t]     = by_tier.get(t, 0) + 1
        by_task[tt]    = by_task.get(tt, 0) + 1
        by_budget[b]   = by_budget.get(b, 0) + 1

    return {
        "total_calls": total_calls,
        "total_cost_usd": total_cost,
        "total_credits_used": total_credits,
        "fallback_rate_pct": round(fallback_cnt / max(total_calls, 1) * 100, 1),
        "avg_cost_per_call_usd": round(total_cost / max(total_calls, 1), 6),
        "calls_by_provider": by_provider,
        "calls_by_tier": by_tier,
        "calls_by_task_type": by_task,
        "calls_by_credit_budget": by_budget,
    }


# ─────────────────────────────────────────────────────────────────────────────
# UNIVERSAL KEY — PAY AS YOU GO
# ─────────────────────────────────────────────────────────────────────────────

class TopupRequest(BaseModel):
    amount_usd: float = Field(gt=0, le=10000, description="Top-up amount in USD")
    currency: str = Field(default="usd", description="usd or bdt")
    amount_bdt: Optional[float] = None


@router.get("/universal/key/pricing")
async def get_key_pricing(current_user: User = Depends(get_current_user)):
    """Return PAYG pricing tiers, cost allocation breakdown, and example credit calculations."""
    cfg = PAYG_CONFIG
    model_pct = cfg["model_allocation_pct"]
    profit_pct = cfg["platform_profit_pct"]
    credits_per_usd = cfg["credits_per_usd"]

    examples = []
    for amount in [5, 10, 25, 50, 100, 250, 500]:
        ai_budget = round(amount * model_pct, 2)
        profit = round(amount * profit_pct, 2)
        credits = int(ai_budget * credits_per_usd)
        examples.append({
            "amount_usd": amount,
            "ai_budget_usd": ai_budget,
            "platform_profit_usd": profit,
            "credits_issued": credits,
            "cost_per_credit_usd": round(amount / max(credits, 1), 4),
        })

    return {
        "model_allocation_pct": model_pct * 100,
        "platform_profit_pct": profit_pct * 100,
        "credits_per_ai_dollar": credits_per_usd,
        "min_topup_usd": cfg["min_topup_usd"],
        "max_topup_usd": cfg["max_topup_usd"],
        "examples": examples,
        "description": (
            f"{int(model_pct * 100)}% of your payment goes directly to AI model costs "
            f"(OpenAI, Anthropic, Gemini, etc.). "
            f"The remaining {int(profit_pct * 100)}% covers platform infrastructure, "
            f"routing, monitoring, and support. "
            f"Each credit is worth ~${round(1 / credits_per_usd, 4)} USD in AI compute."
        ),
    }


@router.get("/universal/key/status")
async def get_key_status(current_user: User = Depends(get_current_user)):
    """Return the current Universal Gateway Key status, budget, and usage."""
    key_doc = await db.client_gateway_keys.find_one(
        {"user_id": current_user.user_id}, {"_id": 0}
    )
    user_doc = await db.users.find_one(
        {"user_id": current_user.user_id}, {"_id": 0, "credits": 1, "subscription": 1}
    )

    credits = (user_doc or {}).get("credits", 0)
    sub_plan = (user_doc or {}).get("subscription", {}).get("plan", "free")

    budget_usd = (key_doc or {}).get("budget_usd", 0.0)
    used_usd = (key_doc or {}).get("used_usd", 0.0)
    remaining_usd = max(budget_usd - used_usd, 0.0)
    total_topups = (key_doc or {}).get("total_topups_usd", 0.0)

    return {
        "key_id": (key_doc or {}).get("key_id", ""),
        "masked_key": f"maars-sk-{'*' * 20}{((key_doc or {}).get('key_id', '') or '')[-4:]}",
        "plan": sub_plan,
        "credits_remaining": credits,
        "budget_usd_total": budget_usd,
        "budget_usd_used": round(used_usd, 6),
        "budget_usd_remaining": round(remaining_usd, 6),
        "total_topups_usd": round(total_topups, 2),
        "utilization_pct": round(used_usd / max(budget_usd, 0.001) * 100, 1),
        "status": "active" if credits > 0 else "depleted",
        "payg_enabled": True,
    }


@router.post("/universal/key/topup")
async def topup_key(
    body: TopupRequest,
    current_user: User = Depends(get_current_user),
):
    """Pay-as-you-go top-up for the Universal Gateway Key.

    Allocation:
      • model_allocation_pct of payment → AI model budget (converted to credits)
      • platform_profit_pct of payment  → platform revenue (logged separately)

    Returns credit amount issued and updated key status.
    """
    cfg = PAYG_CONFIG
    amount_usd = body.amount_usd

    # Handle BDT conversion
    if body.currency.lower() == "bdt" and body.amount_bdt:
        amount_usd = round(body.amount_bdt / cfg.get("bdt_to_usd_rate", 110.0), 2)

    if amount_usd < cfg["min_topup_usd"]:
        raise HTTPException(status_code=400, detail=f"Minimum top-up is ${cfg['min_topup_usd']}")
    if amount_usd > cfg["max_topup_usd"]:
        raise HTTPException(status_code=400, detail=f"Maximum top-up is ${cfg['max_topup_usd']}")

    ai_budget_usd = round(amount_usd * cfg["model_allocation_pct"], 4)
    profit_usd = round(amount_usd * cfg["platform_profit_pct"], 4)
    credits_issued = int(ai_budget_usd * cfg["credits_per_usd"])

    transaction_id = f"payg_{uuid.uuid4().hex[:16]}"

    # Update credits and gateway key budget
    await db.users.update_one(
        {"user_id": current_user.user_id},
        {"$inc": {"credits": credits_issued}},
    )
    await db.client_gateway_keys.update_one(
        {"user_id": current_user.user_id},
        {"$inc": {"budget_usd": ai_budget_usd, "total_topups_usd": amount_usd}},
        upsert=True,
    )

    # Log the transaction
    await db.payg_transactions.insert_one({
        "transaction_id": transaction_id,
        "user_id": current_user.user_id,
        "amount_usd": amount_usd,
        "currency": body.currency,
        "ai_budget_usd": ai_budget_usd,
        "profit_usd": profit_usd,
        "credits_issued": credits_issued,
        "model_allocation_pct": cfg["model_allocation_pct"] * 100,
        "profit_pct": cfg["platform_profit_pct"] * 100,
        "status": "completed",
        "created_at": datetime.now(timezone.utc).isoformat(),
    })

    return {
        "transaction_id": transaction_id,
        "amount_paid_usd": amount_usd,
        "ai_budget_allocated_usd": ai_budget_usd,
        "platform_profit_usd": profit_usd,
        "credits_issued": credits_issued,
        "allocation_breakdown": {
            f"AI Model Budget ({int(cfg['model_allocation_pct']*100)}%)": f"${ai_budget_usd}",
            f"Platform & Infrastructure ({int(cfg['platform_profit_pct']*100)}%)": f"${profit_usd}",
        },
        "message": f"Success! {credits_issued} credits added to your account. ${ai_budget_usd} allocated to AI model budget.",
    }


@router.get("/universal/key/transactions")
async def get_key_transactions(current_user: User = Depends(get_current_user)):
    """Return pay-as-you-go top-up history for this user."""
    docs = await db.payg_transactions.find(
        {"user_id": current_user.user_id}, {"_id": 0}
    ).sort("created_at", -1).to_list(50)
    total_paid = sum(d.get("amount_usd", 0) for d in docs)
    total_credits = sum(d.get("credits_issued", 0) for d in docs)
    return {
        "transactions": docs,
        "total": len(docs),
        "total_paid_usd": round(total_paid, 2),
        "total_credits_purchased": total_credits,
    }
