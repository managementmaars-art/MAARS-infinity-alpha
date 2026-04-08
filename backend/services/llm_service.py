"""LLM service - model selection, calling, fallback, file generation, credit costs."""
import os
import re
import uuid
import logging
import httpx
from pathlib import Path
from typing import Optional

from shared.constants import EMERGENT_LLM_KEY, UPLOAD_DIR

logger = logging.getLogger(__name__)


# ============== MODEL COST MAPS ==============

MODEL_COSTS_MAP = {
    "gpt-5": {"input": 2.50, "output": 10.00, "provider": "openai"},
    "gpt-4o": {"input": 2.50, "output": 10.00, "provider": "openai"},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60, "provider": "openai"},
    "o3": {"input": 10.00, "output": 40.00, "provider": "openai"},
    "o3-mini": {"input": 1.10, "output": 4.40, "provider": "openai"},
    "claude-sonnet-4-5-20250929": {"input": 3.00, "output": 15.00, "provider": "anthropic"},
    "claude-opus-4-5-20251101": {"input": 15.00, "output": 75.00, "provider": "anthropic"},
    "claude-haiku-4-5-20250929": {"input": 0.80, "output": 4.00, "provider": "anthropic"},
    "gemini-3-flash-preview": {"input": 0.075, "output": 0.30, "provider": "gemini"},
    "gemini-3-pro-preview": {"input": 1.25, "output": 5.00, "provider": "gemini"},
    "gemini-3-pro-image-preview": {"input": 0.02, "output": 0.0, "provider": "gemini", "per_unit": "image"},
    "gemini-nano-banana-2": {"input": 0.02, "output": 0.0, "provider": "gemini", "per_unit": "image"},
    "grok-3": {"input": 3.00, "output": 15.00, "provider": "xai"},
    "grok-3-mini": {"input": 0.30, "output": 0.50, "provider": "xai"},
    "grok-2": {"input": 2.00, "output": 10.00, "provider": "xai"},
    "deepseek-chat": {"input": 0.14, "output": 0.28, "provider": "deepseek"},
    "deepseek-reasoner": {"input": 0.55, "output": 2.19, "provider": "deepseek"},
    "mistral-large-latest": {"input": 2.00, "output": 6.00, "provider": "mistral"},
    "mistral-medium-latest": {"input": 0.40, "output": 2.00, "provider": "mistral"},
    "mistral-small-latest": {"input": 0.10, "output": 0.30, "provider": "mistral"},
    "sonar": {"input": 1.00, "output": 1.00, "provider": "perplexity"},
    "sonar-pro": {"input": 3.00, "output": 15.00, "provider": "perplexity"},
    "command-r-plus": {"input": 2.50, "output": 10.00, "provider": "cohere"},
    "command-r": {"input": 0.15, "output": 0.60, "provider": "cohere"},
    "gpt-image-1": {"input": 0.02, "output": 0.0, "provider": "openai", "per_unit": "image"},
    "dall-e-3": {"input": 0.04, "output": 0.0, "provider": "openai", "per_unit": "image"},
    "sora-2": {"input": 0.10, "output": 0.0, "provider": "openai", "per_unit": "second"},
    # Groq (Meta Llama 4)
    "llama-4-scout-17b-16e-instruct": {"input": 0.11, "output": 0.34, "provider": "groq"},
    "llama-4-maverick-17b-128e-instruct": {"input": 0.50, "output": 0.77, "provider": "groq"},
    "llama-3.3-70b-versatile": {"input": 0.59, "output": 0.79, "provider": "groq"},
    # Together AI
    "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8": {"input": 0.27, "output": 0.85, "provider": "together"},
    "meta-llama/Llama-3.3-70B-Instruct-Turbo": {"input": 0.88, "output": 0.88, "provider": "together"},
    "deepseek-ai/DeepSeek-R1": {"input": 3.00, "output": 7.00, "provider": "together"},
    # Fireworks AI
    "accounts/fireworks/models/llama4-scout-instruct-basic": {"input": 0.15, "output": 0.60, "provider": "fireworks"},
    "accounts/fireworks/models/llama4-maverick-instruct-basic": {"input": 0.50, "output": 0.77, "provider": "fireworks"},
    "accounts/fireworks/models/deepseek-v3": {"input": 0.56, "output": 1.68, "provider": "fireworks"},
    # AI21 Jamba
    "jamba-large-1.7": {"input": 2.00, "output": 8.00, "provider": "ai21"},
    "jamba-mini-1.7": {"input": 0.20, "output": 0.40, "provider": "ai21"},
    # OpenAI GPT-4.1 family (April 2025)
    "gpt-4.1": {"input": 2.00, "output": 8.00, "provider": "openai"},
    "gpt-4.1-mini": {"input": 0.40, "output": 1.60, "provider": "openai"},
    "gpt-4.1-nano": {"input": 0.10, "output": 0.40, "provider": "openai"},
    # OpenAI o4 family
    "o4-mini": {"input": 1.10, "output": 4.40, "provider": "openai"},
    "o4": {"input": 15.00, "output": 60.00, "provider": "openai"},
    # Anthropic Claude latest
    "claude-opus-4-6": {"input": 15.00, "output": 75.00, "provider": "anthropic"},
    "claude-sonnet-4-6": {"input": 3.00, "output": 15.00, "provider": "anthropic"},
    "claude-haiku-4-5-20251001": {"input": 0.80, "output": 4.00, "provider": "anthropic"},
    # Gemini 2.5 family
    "gemini-2.5-pro": {"input": 1.25, "output": 10.00, "provider": "gemini"},
    "gemini-2.5-flash": {"input": 0.075, "output": 0.30, "provider": "gemini"},
    "gemini-2.5-flash-lite": {"input": 0.0375, "output": 0.15, "provider": "gemini"},
    # DeepSeek latest
    "deepseek-v3-0324": {"input": 0.14, "output": 0.28, "provider": "deepseek"},
    "deepseek-r1-0528": {"input": 0.55, "output": 2.19, "provider": "deepseek"},
    # Mistral additions
    "codestral-latest": {"input": 0.30, "output": 0.90, "provider": "mistral"},
    "pixtral-large-latest": {"input": 2.00, "output": 6.00, "provider": "mistral"},
    "mistral-nemo": {"input": 0.15, "output": 0.15, "provider": "mistral"},
    # Perplexity additions
    "sonar-reasoning": {"input": 1.00, "output": 5.00, "provider": "perplexity"},
    "sonar-reasoning-pro": {"input": 2.00, "output": 8.00, "provider": "perplexity"},
    "sonar-deep-research": {"input": 2.00, "output": 8.00, "provider": "perplexity"},
    # Cohere additions
    "command-a-03-2025": {"input": 2.50, "output": 10.00, "provider": "cohere"},
    # Groq additions
    "qwen-qwq-32b": {"input": 0.29, "output": 0.39, "provider": "groq"},
    "gemma2-9b-it": {"input": 0.20, "output": 0.20, "provider": "groq"},
    "llama-3.1-8b-instant": {"input": 0.05, "output": 0.08, "provider": "groq"},
    # Together AI additions
    "Qwen/Qwen2.5-72B-Instruct-Turbo": {"input": 0.72, "output": 0.72, "provider": "together"},
    "Qwen/Qwen3-235B-A22B-Instruct-FP8": {"input": 0.20, "output": 0.60, "provider": "together"},
    # Fireworks AI additions
    "accounts/fireworks/models/qwen3-30b-a3b-instruct": {"input": 0.15, "output": 0.60, "provider": "fireworks"},
    "accounts/fireworks/models/phi-4": {"input": 0.90, "output": 0.90, "provider": "fireworks"},
    # Cerebras (ultra-fast open-source inference)
    "llama-3.3-70b": {"input": 0.60, "output": 0.60, "provider": "cerebras"},
    "llama3.1-8b": {"input": 0.10, "output": 0.10, "provider": "cerebras"},
    "qwen-3-32b": {"input": 0.40, "output": 0.40, "provider": "cerebras"},
    # Sambanova (fast open-source inference)
    "Meta-Llama-3.3-70B-Instruct": {"input": 0.60, "output": 0.60, "provider": "sambanova"},
    "Qwen2.5-72B-Instruct": {"input": 0.70, "output": 0.70, "provider": "sambanova"},
    "DeepSeek-R1-0528": {"input": 1.30, "output": 1.30, "provider": "sambanova"},
    # Novita AI
    "hermes-3-llama-3.1-70b": {"input": 0.40, "output": 0.40, "provider": "novita"},
    # Lambda Labs
    "hermes-3-405b": {"input": 0.80, "output": 0.80, "provider": "lambda"},
    # Minimax AI
    "minimax-text-01": {"input": 0.20, "output": 1.10, "provider": "minimax"},
    "minimax-vl-01":   {"input": 0.20, "output": 1.10, "provider": "minimax"},
    # Inception AI (Mercury)
    "mercury-coder-small": {"input": 0.25, "output": 1.00, "provider": "inception"},
    "mercury-coder-large": {"input": 0.50, "output": 2.00, "provider": "inception"},
    # Arcee AI
    "arcee-maestro":   {"input": 1.20, "output": 5.00, "provider": "arcee"},
    "arcee-blaze":     {"input": 0.50, "output": 1.50, "provider": "arcee"},
    # Amazon Bedrock (Nova)
    "amazon.nova-pro-v1:0":   {"input": 0.80, "output": 3.20, "provider": "amazon"},
    "amazon.nova-lite-v1:0":  {"input": 0.06, "output": 0.24, "provider": "amazon"},
    "amazon.nova-micro-v1:0": {"input": 0.035, "output": 0.14, "provider": "amazon"},
    # Nvidia NIM (Nvidia-hosted accelerated inference)
    "meta/llama-3.1-8b-instruct": {"input": 0.10, "output": 0.10, "provider": "nvidia"},
    "meta/llama-3.3-70b-instruct": {"input": 0.60, "output": 0.60, "provider": "nvidia"},
    "nvidia/llama-3.1-nemotron-70b-instruct": {"input": 0.35, "output": 0.35, "provider": "nvidia"},
    "nvidia/llama-3.1-nemotron-ultra-253b-v1": {"input": 0.55, "output": 3.25, "provider": "nvidia"},
    "microsoft/phi-4-multimodal-instruct": {"input": 0.20, "output": 0.20, "provider": "nvidia"},
    # Moonshot AI / Kimi (long-context specialist, up to 1M tokens)
    "moonshot-v1-8k": {"input": 0.18, "output": 0.18, "provider": "moonshot"},
    "moonshot-v1-32k": {"input": 0.44, "output": 0.44, "provider": "moonshot"},
    "moonshot-v1-128k": {"input": 0.73, "output": 0.73, "provider": "moonshot"},
    # Qwen / Alibaba DashScope
    "qwen-turbo": {"input": 0.15, "output": 0.15, "provider": "qwen"},
    "qwen-plus": {"input": 0.80, "output": 0.80, "provider": "qwen"},
    "qwen-max": {"input": 2.40, "output": 9.60, "provider": "qwen"},
    "qwen2.5-72b-instruct": {"input": 0.72, "output": 0.72, "provider": "qwen"},
    "qwen3-235b-a22b": {"input": 0.22, "output": 0.88, "provider": "qwen"},
    # ── 01.AI / Yi ───────────────────────────────────────────────────────────
    "yi-lightning":       {"input": 0.14,  "output": 0.14,  "provider": "yi"},
    "yi-large-fc":        {"input": 3.00,  "output": 3.00,  "provider": "yi"},
    "yi-medium-200k":     {"input": 12.00, "output": 12.00, "provider": "yi"},
    # ── Zhipu AI / GLM ───────────────────────────────────────────────────────
    "glm-4-plus":         {"input": 7.00,  "output": 7.00,  "provider": "zhipu"},
    "glm-4-0520":         {"input": 1.00,  "output": 1.00,  "provider": "zhipu"},
    "glm-4-air":          {"input": 0.13,  "output": 0.13,  "provider": "zhipu"},
    "glm-z1-air":         {"input": 0.13,  "output": 0.13,  "provider": "zhipu"},
    # ── ByteDance Doubao ─────────────────────────────────────────────────────
    "doubao-pro-128k":    {"input": 0.80,  "output": 0.80,  "provider": "doubao"},
    "doubao-pro-32k":     {"input": 0.12,  "output": 0.12,  "provider": "doubao"},
    "doubao-lite-128k":   {"input": 0.11,  "output": 0.11,  "provider": "doubao"},
    "doubao-lite-32k":    {"input": 0.04,  "output": 0.04,  "provider": "doubao"},
    # ── Hyperbolic ───────────────────────────────────────────────────────────
    "meta-llama/Llama-3.3-70B-Instruct":       {"input": 0.40, "output": 0.40, "provider": "hyperbolic"},
    "meta-llama/Meta-Llama-3.1-405B-Instruct": {"input": 2.00, "output": 2.00, "provider": "hyperbolic"},
    "deepseek-ai/DeepSeek-R1-hyperbolic":      {"input": 0.50, "output": 2.18, "provider": "hyperbolic"},
    "Qwen/Qwen2.5-72B-Instruct-hyperbolic":    {"input": 0.40, "output": 0.40, "provider": "hyperbolic"},
    # ── Upstage Solar ────────────────────────────────────────────────────────
    "solar-pro":          {"input": 9.00,  "output": 9.00,  "provider": "upstage"},
    "solar-mini":         {"input": 0.29,  "output": 0.29,  "provider": "upstage"},
    # ── Writer Palmyra ────────────────────────────────────────────────────────
    "palmyra-x-004":      {"input": 0.50,  "output": 2.50,  "provider": "writer"},
    "palmyra-med":        {"input": 0.80,  "output": 4.00,  "provider": "writer"},
    "palmyra-fin":        {"input": 0.80,  "output": 4.00,  "provider": "writer"},
    # ── OpenAI legacy + o1 series ─────────────────────────────────────────────
    "o1":                 {"input": 15.00, "output": 60.00, "provider": "openai"},
    "o1-mini":            {"input": 3.00,  "output": 12.00, "provider": "openai"},
    "o1-pro":             {"input": 150.00,"output": 600.00,"provider": "openai"},
    "gpt-4-turbo":        {"input": 10.00, "output": 30.00, "provider": "openai"},
    "gpt-3.5-turbo":      {"input": 0.50,  "output": 1.50,  "provider": "openai"},
    # ── Anthropic legacy ─────────────────────────────────────────────────────
    "claude-3-5-sonnet-20241022": {"input": 3.00,  "output": 15.00, "provider": "anthropic"},
    "claude-3-5-haiku-20241022":  {"input": 0.80,  "output": 4.00,  "provider": "anthropic"},
    "claude-3-opus-20240229":     {"input": 15.00, "output": 75.00, "provider": "anthropic"},
    # ── Google Gemini legacy + 2.0 ───────────────────────────────────────────
    "gemini-2.0-flash":      {"input": 0.075, "output": 0.30, "provider": "gemini"},
    "gemini-2.0-flash-lite": {"input": 0.075, "output": 0.30, "provider": "gemini"},
    "gemini-1.5-pro":        {"input": 1.25,  "output": 5.00, "provider": "gemini"},
    "gemini-1.5-flash":      {"input": 0.075, "output": 0.30, "provider": "gemini"},
    # ── xAI vision ───────────────────────────────────────────────────────────
    "grok-2-vision-1212":    {"input": 2.00, "output": 10.00, "provider": "xai"},
    # ── Mistral additions ────────────────────────────────────────────────────
    "pixtral-12b-2409":      {"input": 0.15, "output": 0.15, "provider": "mistral"},
    "ministral-8b-latest":   {"input": 0.10, "output": 0.10, "provider": "mistral"},
    "ministral-3b-latest":   {"input": 0.04, "output": 0.04, "provider": "mistral"},
    # ── Groq expanded ────────────────────────────────────────────────────────
    "llama-3.2-90b-vision-preview":    {"input": 0.90, "output": 0.90, "provider": "groq"},
    "llama-3.2-11b-vision-preview":    {"input": 0.18, "output": 0.18, "provider": "groq"},
    "llama-3.2-3b-preview":            {"input": 0.06, "output": 0.06, "provider": "groq"},
    "llama-3.1-70b-versatile":         {"input": 0.59, "output": 0.79, "provider": "groq"},
    "mistral-saba-24b":                {"input": 0.79, "output": 0.79, "provider": "groq"},
    "deepseek-r1-distill-llama-70b":   {"input": 0.75, "output": 0.99, "provider": "groq"},
    "deepseek-r1-distill-qwen-32b":    {"input": 0.69, "output": 0.69, "provider": "groq"},
    # ── Cerebras expanded ────────────────────────────────────────────────────
    "llama-3.1-70b":         {"input": 0.60, "output": 0.60, "provider": "cerebras"},
    "llama-3.1-8b":          {"input": 0.10, "output": 0.10, "provider": "cerebras"},
    "qwen-3-8b":             {"input": 0.10, "output": 0.10, "provider": "cerebras"},
    # ── Together AI expanded ─────────────────────────────────────────────────
    "meta-llama/Llama-4-Scout-17B-16E-Instruct-FP8":      {"input": 0.18, "output": 0.59, "provider": "together"},
    "meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo":     {"input": 1.20, "output": 1.20, "provider": "together"},
    "meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo":     {"input": 0.18, "output": 0.18, "provider": "together"},
    "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo":      {"input": 3.50, "output": 3.50, "provider": "together"},
    "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo":       {"input": 0.88, "output": 0.88, "provider": "together"},
    "deepseek-ai/DeepSeek-V3":                             {"input": 1.28, "output": 1.28, "provider": "together"},
    "mistralai/Mixtral-8x7B-Instruct-v0.1":               {"input": 0.60, "output": 0.60, "provider": "together"},
    "mistralai/Mixtral-8x22B-Instruct-v0.1":              {"input": 1.20, "output": 1.20, "provider": "together"},
    "microsoft/WizardLM-2-8x22B":                          {"input": 1.20, "output": 1.20, "provider": "together"},
    "NousResearch/Hermes-3-Llama-3.1-70B":                {"input": 0.88, "output": 0.88, "provider": "together"},
    "NousResearch/Hermes-3-Llama-3.1-405B":               {"input": 3.50, "output": 3.50, "provider": "together"},
    "google/gemma-2-27b-it":                               {"input": 0.80, "output": 0.80, "provider": "together"},
    "Qwen/QwQ-32B":                                        {"input": 1.20, "output": 1.20, "provider": "together"},
    # ── Fireworks expanded ───────────────────────────────────────────────────
    "accounts/fireworks/models/qwen3-235b-a22b":           {"input": 0.20, "output": 0.60, "provider": "fireworks"},
    "accounts/fireworks/models/mixtral-8x7b-instruct-hf":  {"input": 0.50, "output": 0.50, "provider": "fireworks"},
    # ── SambaNova expanded ───────────────────────────────────────────────────
    "Meta-Llama-4-Scout-17B-16E-Instruct":  {"input": 0.10, "output": 0.10, "provider": "sambanova"},
    "DeepSeek-V3-0324":                     {"input": 0.70, "output": 0.70, "provider": "sambanova"},
    "Qwen2.5-32B-Instruct":                 {"input": 0.40, "output": 0.40, "provider": "sambanova"},
    # ── Nvidia NIM expanded ──────────────────────────────────────────────────
    "meta/llama-3.2-90b-vision-instruct":   {"input": 0.90, "output": 0.90, "provider": "nvidia"},
    "mistralai/mistral-nemo-instruct-2407": {"input": 0.15, "output": 0.15, "provider": "nvidia"},
    # ── Moonshot Kimi K2 ─────────────────────────────────────────────────────
    "kimi-k2-instruct":       {"input": 0.14, "output": 0.60, "provider": "moonshot"},
    # ── HuggingFace Inference API ────────────────────────────────────────────
    "microsoft/phi-4":                       {"input": 0.05, "output": 0.05, "provider": "huggingface"},
    "google/gemma-2-9b-it":                  {"input": 0.05, "output": 0.05, "provider": "huggingface"},
    "mistralai/Mistral-7B-Instruct-v0.3":    {"input": 0.05, "output": 0.05, "provider": "huggingface"},
    "meta-llama/Llama-3.1-8B-Instruct":      {"input": 0.05, "output": 0.05, "provider": "huggingface"},
    # ── Meta Llama API (official) ────────────────────────────────────────────
    "Llama-4-Scout-17B-16E-Instruct":          {"input": 0.18, "output": 0.59, "provider": "llama"},
    "Llama-4-Maverick-17B-128E-Instruct-FP8":  {"input": 0.27, "output": 0.85, "provider": "llama"},
    "Llama-3.3-70B-Instruct":                  {"input": 0.59, "output": 0.79, "provider": "llama"},
}

MODEL_CREDIT_COSTS = {
    "gpt-4o-mini": 1, "claude-haiku-4-5-20250929": 1, "gemini-3-flash-preview": 1,
    "deepseek-chat": 1, "mistral-small-latest": 1, "command-r": 1, "grok-3-mini": 1,
    "gpt-4o": 2, "grok-2": 2, "mistral-medium-latest": 2, "sonar": 2,
    "gemini-3-pro-preview": 2, "deepseek-reasoner": 2,
    "gpt-5": 3, "claude-sonnet-4-5-20250929": 3, "grok-3": 3,
    "mistral-large-latest": 3, "command-r-plus": 3, "sonar-pro": 3,
    "claude-opus-4-5-20251101": 5, "o3": 5,
    "o3-mini": 2,
    "gemini-3-pro-image-preview": 5, "gemini-nano-banana-2": 5,
    "gpt-image-1": 5, "dall-e-3": 5,
    "sora-2": 10,
    # Groq (Meta Llama 4)
    "llama-4-scout-17b-16e-instruct": 1, "llama-4-maverick-17b-128e-instruct": 1,
    "llama-3.3-70b-versatile": 1,
    # Together AI
    "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8": 1,
    "meta-llama/Llama-3.3-70B-Instruct-Turbo": 2,
    "deepseek-ai/DeepSeek-R1": 3,
    # Fireworks AI
    "accounts/fireworks/models/llama4-scout-instruct-basic": 1,
    "accounts/fireworks/models/llama4-maverick-instruct-basic": 1,
    "accounts/fireworks/models/deepseek-v3": 2,
    # AI21 Jamba
    "jamba-large-1.7": 3, "jamba-mini-1.7": 1,
    # OpenAI GPT-4.1 family
    "gpt-4.1": 2, "gpt-4.1-mini": 1, "gpt-4.1-nano": 1,
    # OpenAI o4
    "o4-mini": 2, "o4": 5,
    # Anthropic latest
    "claude-opus-4-6": 5, "claude-sonnet-4-6": 3, "claude-haiku-4-5-20251001": 1,
    # Gemini 2.5
    "gemini-2.5-pro": 2, "gemini-2.5-flash": 1, "gemini-2.5-flash-lite": 1,
    # DeepSeek latest
    "deepseek-v3-0324": 1, "deepseek-r1-0528": 2,
    # Mistral additions
    "codestral-latest": 1, "pixtral-large-latest": 3, "mistral-nemo": 1,
    # Perplexity additions
    "sonar-reasoning": 2, "sonar-reasoning-pro": 3, "sonar-deep-research": 3,
    # Cohere additions
    "command-a-03-2025": 3,
    # Groq additions
    "qwen-qwq-32b": 1, "gemma2-9b-it": 1, "llama-3.1-8b-instant": 1,
    # Together AI additions
    "Qwen/Qwen2.5-72B-Instruct-Turbo": 1, "Qwen/Qwen3-235B-A22B-Instruct-FP8": 2,
    # Fireworks AI additions
    "accounts/fireworks/models/qwen3-30b-a3b-instruct": 1, "accounts/fireworks/models/phi-4": 1,
    # Cerebras
    "llama-3.3-70b": 1, "llama3.1-8b": 1, "qwen-3-32b": 1,
    # Sambanova
    "Meta-Llama-3.3-70B-Instruct": 1, "Qwen2.5-72B-Instruct": 1, "DeepSeek-R1-0528": 2,
    # Novita AI / Lambda Labs (open-source hosting)
    "nousresearch/hermes-3-llama-3.1-70b": 1, "meta-llama/llama-4-maverick": 1,
    "anthropic/claude-sonnet-4-6": 3, "openai/gpt-4.1": 2, "google/gemini-2.5-flash": 1,
    "deepseek/deepseek-r1": 2, "qwen/qwen3-235b-a22b": 1,
    # Nvidia NIM
    "meta/llama-3.1-8b-instruct": 1, "meta/llama-3.3-70b-instruct": 1,
    "nvidia/llama-3.1-nemotron-70b-instruct": 1, "nvidia/llama-3.1-nemotron-ultra-253b-v1": 2,
    "microsoft/phi-4-multimodal-instruct": 1,
    # Moonshot AI (Kimi)
    "moonshot-v1-8k": 1, "moonshot-v1-32k": 1, "moonshot-v1-128k": 2,
    # Qwen / Alibaba
    "qwen-turbo": 1, "qwen-plus": 1, "qwen-max": 3, "qwen2.5-72b-instruct": 1, "qwen3-235b-a22b": 1,
}


def get_credit_cost(model_name: str, has_image: bool = False, has_video: bool = False) -> int:
    model_clean = model_name.split("/")[-1] if "/" in model_name else model_name
    base_cost = MODEL_CREDIT_COSTS.get(model_clean, 2)
    if has_image:
        base_cost += MODEL_CREDIT_COSTS.get("gemini-nano-banana-2", 5)
    if has_video:
        base_cost += MODEL_CREDIT_COSTS.get("sora-2", 10)
    return base_cost


# ============== DETECTION FUNCTIONS ==============

def detect_video_generation_request(content: str, agent_role: str) -> bool:
    video_roles = ['video content specialist', 'videographer', 'filmmaker', 'animator']
    is_video_agent = any(r in agent_role.lower() for r in video_roles)
    if not is_video_agent:
        return False
    content_lower = content.lower()
    generation_verbs = ['generate', 'create', 'make', 'produce', 'render', 'build me', 'give me', 'shoot', 'film', 'record']
    return any(v in content_lower for v in generation_verbs)


def detect_image_generation_request(content: str, agent_role: str) -> bool:
    visual_roles = ['graphic designer', 'designer', 'illustrator', 'artist']
    is_visual_agent = any(r in agent_role.lower() for r in visual_roles)
    if not is_visual_agent:
        return False
    content_lower = content.lower()
    generation_verbs = ['generate', 'create', 'make', 'design', 'draw', 'sketch', 'produce',
                        'illustrate', 'render', 'build me', 'give me', 'show me', 'craft']
    has_verb = any(v in content_lower for v in generation_verbs)
    return has_verb


def detect_file_format_request(content: str) -> Optional[str]:
    content_lower = content.lower()
    format_patterns = {
        "pdf": [r'\bpdf\b', r'\bpdf format\b', r'\bas a pdf\b', r'\bin pdf\b', r'\bto pdf\b'],
        "docx": [r'\bdocx?\b', r'\bword\b', r'\bword doc\b', r'\bas a doc\b', r'\bin word\b', r'\bword format\b'],
        "csv": [r'\bcsv\b', r'\bcsv format\b', r'\bas a csv\b', r'\bin csv\b'],
        "xlsx": [r'\bxlsx?\b', r'\bexcel\b', r'\bspreadsheet\b', r'\bas an? excel\b', r'\bin excel\b'],
        "txt": [r'\btxt\b', r'\btext file\b', r'\bas a text file\b', r'\bin txt\b', r'\bplain text file\b'],
    }
    for fmt, patterns in format_patterns.items():
        for pattern in patterns:
            if re.search(pattern, content_lower):
                return fmt
    return None


def extract_document_content(raw_text: str) -> str:
    lines = raw_text.split('\n')
    doc_start_patterns = [
        r'^#{1,3}\s', r'^---+$', r'^\*\*\*+$',
        r'^\*\*[A-Z]', r'^[A-Z][A-Z\s]{5,}$',
    ]
    start_idx = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        for pattern in doc_start_patterns:
            if re.match(pattern, stripped):
                start_idx = i
                break
        if start_idx > 0:
            break
    content = '\n'.join(lines[start_idx:]) if start_idx > 0 else raw_text
    end_patterns = [r'\*\*Important Note', r'\*I am an AI', r'\*Please note:', r'\*Disclaimer:',
                    r'### Next Steps', r'\*\*Next Steps', r'Would you like me to']
    result_lines = content.split('\n')
    cut_idx = len(result_lines)
    for i, line in enumerate(result_lines):
        for pattern in end_patterns:
            if re.search(pattern, line):
                cut_idx = i
                break
        if cut_idx < len(result_lines):
            break
    return '\n'.join(result_lines[:cut_idx]).strip()


def generate_file_from_content(content: str, file_format: str, filename_base: str) -> tuple:
    file_id = uuid.uuid4().hex[:10]
    doc_content = extract_document_content(content)
    if not doc_content.strip():
        doc_content = content

    if file_format == "pdf":
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
        from reportlab.lib.units import mm
        from reportlab.lib.enums import TA_LEFT
        filename = f"{file_id}_{filename_base}.pdf"
        filepath = UPLOAD_DIR / filename
        doc_pdf = SimpleDocTemplate(str(filepath), pagesize=A4,
                                     leftMargin=25*mm, rightMargin=25*mm,
                                     topMargin=20*mm, bottomMargin=20*mm)
        styles = getSampleStyleSheet()
        style_body = ParagraphStyle('Body', parent=styles['Normal'], fontSize=11, leading=15, spaceAfter=4)
        style_h1 = ParagraphStyle('H1', parent=styles['Heading1'], fontSize=18, leading=22, spaceAfter=8, spaceBefore=12)
        style_h2 = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=15, leading=19, spaceAfter=6, spaceBefore=10)
        style_h3 = ParagraphStyle('H3', parent=styles['Heading3'], fontSize=13, leading=17, spaceAfter=4, spaceBefore=8)
        style_bullet = ParagraphStyle('Bullet', parent=style_body, leftIndent=15, bulletIndent=5)

        def clean_md(t):
            t = t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            t = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', t)
            t = re.sub(r'\*(.*?)\*', r'<i>\1</i>', t)
            t = re.sub(r'`(.*?)`', r'<font face="Courier">\1</font>', t)
            return t

        story = []
        for line in doc_content.split('\n'):
            s = line.strip()
            if s.startswith('# '):
                story.append(Paragraph(clean_md(s[2:].strip('*')), style_h1))
            elif s.startswith('## '):
                story.append(Paragraph(clean_md(s[3:].strip('*')), style_h2))
            elif s.startswith('### '):
                story.append(Paragraph(clean_md(s[4:].strip('*')), style_h3))
            elif re.match(r'^---+$', s) or re.match(r'^\*\*\*+$', s):
                story.append(HRFlowable(width="100%", thickness=1, color="grey"))
                story.append(Spacer(1, 4*mm))
            elif s == '':
                story.append(Spacer(1, 3*mm))
            elif s.startswith('- ') or s.startswith('* '):
                story.append(Paragraph(clean_md(s[2:]), style_bullet, bulletText='\u2022'))
            elif re.match(r'^(\d+[\.\)])\s(.+)', s):
                m = re.match(r'^(\d+[\.\)])\s(.+)', s)
                story.append(Paragraph(clean_md(m.group(2)), style_bullet, bulletText=m.group(1)))
            elif s:
                story.append(Paragraph(clean_md(s), style_body))
        if not story:
            story.append(Paragraph("(Empty document)", style_body))
        doc_pdf.build(story)
        return filepath, filename, "application/pdf"

    elif file_format == "docx":
        from docx import Document
        from docx.shared import Pt, Inches
        doc = Document()
        for line in doc_content.split('\n'):
            clean = line.strip()
            if clean.startswith('# '):
                doc.add_heading(clean[2:].strip('*'), level=1)
            elif clean.startswith('## '):
                doc.add_heading(clean[3:].strip('*'), level=2)
            elif clean.startswith('### '):
                doc.add_heading(clean[4:].strip('*'), level=3)
            elif clean.startswith('---') or clean.startswith('***'):
                doc.add_paragraph('_' * 50)
            elif clean.startswith('- ') or clean.startswith('* '):
                doc.add_paragraph(clean[2:], style='List Bullet')
            elif re.match(r'^\d+\.', clean):
                doc.add_paragraph(clean, style='List Number')
            elif clean:
                text = re.sub(r'\*\*(.*?)\*\*', r'\1', clean)
                text = re.sub(r'\*(.*?)\*', r'\1', text)
                doc.add_paragraph(text)
        filename = f"{file_id}_{filename_base}.docx"
        filepath = UPLOAD_DIR / filename
        doc.save(str(filepath))
        return filepath, filename, "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    elif file_format == "csv":
        filename = f"{file_id}_{filename_base}.csv"
        filepath = UPLOAD_DIR / filename
        lines = doc_content.strip().split('\n')
        with open(filepath, 'w', encoding='utf-8') as f:
            for line in lines:
                if '|' in line and not line.strip().startswith('---'):
                    cells = [c.strip().strip('*') for c in line.split('|') if c.strip() and c.strip() != '---']
                    if cells:
                        f.write(','.join(f'"{c}"' for c in cells) + '\n')
                elif line.strip():
                    f.write(line.strip() + '\n')
        return filepath, filename, "text/csv"

    elif file_format == "xlsx":
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Sheet1"
        row_num = 1
        for line in doc_content.strip().split('\n'):
            if '|' in line and not line.strip().replace('-', '').replace('|', '').strip() == '':
                cells = [c.strip().strip('*') for c in line.split('|') if c.strip()]
                if cells and not all(c.replace('-', '').strip() == '' for c in cells):
                    for col, cell in enumerate(cells, 1):
                        ws.cell(row=row_num, column=col, value=cell)
                    row_num += 1
            elif line.strip():
                ws.cell(row=row_num, column=1, value=line.strip())
                row_num += 1
        filename = f"{file_id}_{filename_base}.xlsx"
        filepath = UPLOAD_DIR / filename
        wb.save(str(filepath))
        return filepath, filename, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    else:  # txt
        filename = f"{file_id}_{filename_base}.txt"
        filepath = UPLOAD_DIR / filename
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', doc_content)
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(text)
        return filepath, filename, "text/plain"


# ============== AUTO MODEL SELECTION ==============

def auto_select_model(content: str, agent_role: str) -> tuple:
    content_lower = content.lower()
    coding_keywords = ['code', 'programming', 'function', 'api', 'debug', 'error', 'python', 'javascript',
                       'react', 'database', 'sql', 'algorithm', 'deploy', 'github', 'bug', 'script',
                       'html', 'css', 'backend', 'frontend', 'app', 'software', 'developer', 'build',
                       'implement', 'refactor', 'regex', 'json', 'xml', 'yaml', 'docker', 'server']
    reasoning_keywords = ['analyze', 'compare', 'evaluate', 'why', 'how does', 'explain', 'reasoning',
                          'logic', 'problem', 'solve', 'calculate', 'math', 'strategy', 'decision',
                          'pros and cons', 'trade-off', 'complex', 'think through', 'proof', 'theorem',
                          'equation', 'formula', 'deduce', 'infer', 'hypothesis']
    creative_keywords = ['write', 'story', 'creative', 'blog', 'article', 'content', 'copy',
                         'headline', 'tagline', 'slogan', 'narrative', 'engaging', 'compelling',
                         'persuasive', 'emotional', 'brand voice', 'tone', 'poem', 'script',
                         'dialogue', 'marketing', 'campaign', 'ad']
    quick_keywords = ['quick', 'simple', 'brief', 'short', 'summarize', 'list', 'bullet points',
                      'yes or no', 'define', 'what is', 'translate', 'convert', 'format',
                      'hello', 'hi', 'thanks', 'how are you']
    long_form_keywords = ['detailed', 'comprehensive', 'in-depth', 'thorough', 'research',
                          'report', 'whitepaper', 'documentation', 'guide', 'tutorial', 'essay',
                          'paper', 'thesis', 'literature review', 'case study']
    data_keywords = ['data', 'analytics', 'metrics', 'dashboard', 'visualization', 'chart',
                     'statistics', 'trends', 'forecast', 'numbers', 'spreadsheet', 'excel',
                     'csv', 'graph', 'table', 'pivot', 'regression']
    legal_keywords = ['contract', 'legal', 'compliance', 'regulation', 'law', 'clause',
                      'terms', 'policy', 'agreement', 'liability', 'jurisdiction']

    coding_roles = ['app developer', 'web designer', 'developer', 'engineer', 'technical']
    creative_roles = ['copywriter', 'content writer', 'marketing', 'social media', 'video', 'graphic', 'email marketing']
    analytical_roles = ['strategist', 'analyst', 'research', 'financial', 'data']
    support_roles = ['customer service', 'secretary', 'hr', 'project manager']
    legal_roles = ['legal']

    coding_score = sum(1 for kw in coding_keywords if kw in content_lower)
    reasoning_score = sum(1 for kw in reasoning_keywords if kw in content_lower)
    creative_score = sum(1 for kw in creative_keywords if kw in content_lower)
    quick_score = sum(1 for kw in quick_keywords if kw in content_lower)
    long_form_score = sum(1 for kw in long_form_keywords if kw in content_lower)
    data_score = sum(1 for kw in data_keywords if kw in content_lower)
    legal_score = sum(1 for kw in legal_keywords if kw in content_lower)

    agent_role_lower = agent_role.lower()
    if any(r in agent_role_lower for r in coding_roles): coding_score += 3
    if any(r in agent_role_lower for r in creative_roles): creative_score += 3
    if any(r in agent_role_lower for r in analytical_roles): reasoning_score += 2; data_score += 2
    if any(r in agent_role_lower for r in support_roles): quick_score += 2
    if any(r in agent_role_lower for r in legal_roles): legal_score += 3; reasoning_score += 1

    scores = {'coding': coding_score, 'reasoning': reasoning_score, 'creative': creative_score,
              'quick': quick_score, 'long_form': long_form_score, 'data': data_score, 'legal': legal_score}
    best_task = max(scores, key=scores.get)
    best_score = scores[best_task]

    if best_score >= 2:
        model_map = {
            'coding': ('openai', 'gpt-5', 'GPT-5 selected - best for coding & technical tasks'),
            'reasoning': ('openai', 'gpt-5', 'GPT-5 selected - best for complex reasoning & analysis'),
            'creative': ('openai', 'gpt-5', 'GPT-5 selected - best for creative work'),
            'quick': ('openai', 'gpt-4o-mini', 'GPT-4o Mini selected - fastest for simple tasks'),
            'long_form': ('openai', 'gpt-5', 'GPT-5 selected - best for detailed long-form content'),
            'data': ('openai', 'gpt-4o', 'GPT-4o selected - best for data analysis & multimodal'),
            'legal': ('openai', 'gpt-5', 'GPT-5 selected - precise for legal analysis'),
        }
        if best_task in model_map:
            return model_map[best_task]

    if len(content) < 50:
        return ('openai', 'gpt-4o-mini', 'GPT-4o Mini selected - efficient for short messages')
    return ('openai', 'gpt-5', 'GPT-5 selected - best all-around model')


# ============== DIRECT LLM CALLING ==============

async def call_direct_llm(provider: str, model_name: str, system_prompt: str, content: str, attachments: list, api_key: str) -> str:
    import json as json_lib
    if provider == "openai":
        async with httpx.AsyncClient(timeout=120) as client:
            messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": content}]
            resp = await client.post("https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={"model": model_name, "messages": messages, "max_tokens": 4096})
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]
    elif provider == "anthropic":
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post("https://api.anthropic.com/v1/messages",
                headers={"x-api-key": api_key, "anthropic-version": "2023-06-01", "Content-Type": "application/json"},
                json={"model": model_name, "max_tokens": 4096, "system": system_prompt,
                      "messages": [{"role": "user", "content": content}]})
            resp.raise_for_status()
            return resp.json()["content"][0]["text"]
    elif provider == "gemini":
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}",
                headers={"Content-Type": "application/json"},
                json={"systemInstruction": {"parts": [{"text": system_prompt}]},
                      "contents": [{"parts": [{"text": content}]}],
                      "generationConfig": {"maxOutputTokens": 4096}})
            resp.raise_for_status()
            return resp.json()["candidates"][0]["content"]["parts"][0]["text"]
    elif provider == "xai":
        return await _call_openai_compatible("https://api.x.ai/v1/chat/completions", model_name, system_prompt, content, api_key)
    elif provider == "deepseek":
        return await _call_openai_compatible("https://api.deepseek.com/chat/completions", model_name, system_prompt, content, api_key)
    elif provider == "mistral":
        return await _call_openai_compatible("https://api.mistral.ai/v1/chat/completions", model_name, system_prompt, content, api_key)
    elif provider == "perplexity":
        return await _call_openai_compatible("https://api.perplexity.ai/chat/completions", model_name, system_prompt, content, api_key)
    elif provider == "cohere":
        async with httpx.AsyncClient(timeout=120) as http:
            resp = await http.post("https://api.cohere.com/v2/chat",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={"model": model_name, "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": content}], "max_tokens": 4096})
            resp.raise_for_status()
            data = resp.json()
            parts = data.get("message", {}).get("content", [])
            return parts[0].get("text", "") if parts else ""
    elif provider == "groq":
        return await _call_openai_compatible("https://api.groq.com/openai/v1/chat/completions", model_name, system_prompt, content, api_key)
    elif provider == "together":
        return await _call_openai_compatible("https://api.together.xyz/v1/chat/completions", model_name, system_prompt, content, api_key)
    elif provider == "fireworks":
        return await _call_openai_compatible("https://api.fireworks.ai/inference/v1/chat/completions", model_name, system_prompt, content, api_key)
    elif provider == "ai21":
        return await _call_openai_compatible("https://api.ai21.com/studio/v1/chat/completions", model_name, system_prompt, content, api_key)
    elif provider == "cerebras":
        return await _call_openai_compatible("https://api.cerebras.ai/v1/chat/completions", model_name, system_prompt, content, api_key)
    elif provider == "sambanova":
        return await _call_openai_compatible("https://api.sambanova.ai/v1/chat/completions", model_name, system_prompt, content, api_key)
    elif provider == "novita":
        return await _call_openai_compatible("https://api.novita.ai/v3/openai/chat/completions", model_name, system_prompt, content, api_key)
    elif provider == "lepton":
        return await _call_openai_compatible(f"https://{model_name.split('/')[0]}.lepton.run/api/v1/chat/completions", model_name, system_prompt, content, api_key)
    elif provider == "lambda":
        return await _call_openai_compatible("https://api.lambda.ai/v1/chat/completions", model_name, system_prompt, content, api_key)
    elif provider == "minimax":
        return await _call_openai_compatible("https://api.minimaxi.chat/v1/chat/completions", model_name, system_prompt, content, api_key)
    elif provider == "inception":
        return await _call_openai_compatible("https://api.inception.ai/v1/chat/completions", model_name, system_prompt, content, api_key)
    elif provider == "arcee":
        return await _call_openai_compatible("https://api.arcee.ai/v1/chat/completions", model_name, system_prompt, content, api_key)
    elif provider == "amazon":
        return await _call_openai_compatible("https://bedrock-runtime.us-east-1.amazonaws.com/v1/chat/completions", model_name, system_prompt, content, api_key)
    elif provider == "nvidia":
        return await _call_openai_compatible("https://integrate.api.nvidia.com/v1/chat/completions", model_name, system_prompt, content, api_key)
    elif provider == "moonshot":
        return await _call_openai_compatible("https://api.moonshot.cn/v1/chat/completions", model_name, system_prompt, content, api_key)
    elif provider == "qwen":
        return await _call_openai_compatible("https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions", model_name, system_prompt, content, api_key)
    elif provider == "yi":
        return await _call_openai_compatible("https://api.lingyiwanwu.com/v1/chat/completions", model_name, system_prompt, content, api_key)
    elif provider == "zhipu":
        return await _call_openai_compatible("https://open.bigmodel.cn/api/paas/v4/chat/completions", model_name, system_prompt, content, api_key)
    elif provider == "doubao":
        return await _call_openai_compatible("https://ark.cn-beijing.volces.com/api/v3/chat/completions", model_name, system_prompt, content, api_key)
    elif provider == "hyperbolic":
        return await _call_openai_compatible("https://api.hyperbolic.xyz/v1/chat/completions", model_name, system_prompt, content, api_key)
    elif provider == "upstage":
        return await _call_openai_compatible("https://api.upstage.ai/v1/chat/completions", model_name, system_prompt, content, api_key)
    elif provider == "writer":
        return await _call_openai_compatible("https://api.writer.com/v1/chat", model_name, system_prompt, content, api_key)
    elif provider == "huggingface":
        return await _call_openai_compatible("https://api-inference.huggingface.co/v1/chat/completions", model_name, system_prompt, content, api_key)
    elif provider == "llama":
        return await _call_openai_compatible("https://api.llama.com/v1/chat/completions", model_name, system_prompt, content, api_key)
    raise ValueError(f"Unsupported provider: {provider}")


async def _call_openai_compatible(url: str, model_name: str, system_prompt: str, content: str, api_key: str) -> str:
    async with httpx.AsyncClient(timeout=120) as http:
        resp = await http.post(url,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": model_name, "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": content}], "max_tokens": 4096})
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]


async def call_llm_with_fallback(api_keys, model_provider, model_name, system_prompt, content, attachments, chat_id, temperature=None, max_tokens=None):
    fallback_models = [
        (model_provider, model_name),
        ("openai", "gpt-5"),
        ("openai", "gpt-4o"),
        ("openai", "gpt-4o-mini"),
        ("gemini", "gemini-3-flash-preview"),
    ]
    seen = set()
    unique_fallbacks = []
    for mp, mn in fallback_models:
        key = f"{mp}/{mn}"
        if key not in seen:
            seen.add(key)
            unique_fallbacks.append((mp, mn))

    last_error = None
    for fb_provider, fb_model in unique_fallbacks:
        try:
            if api_keys["active_provider"] == "direct":
                direct_key = api_keys.get(fb_provider, "")
                if direct_key:
                    result = await call_direct_llm(fb_provider, fb_model, system_prompt, content, attachments, direct_key)
                    return result, fb_provider, fb_model

            from emergentintegrations.llm.chat import LlmChat, UserMessage
            llm_chat = LlmChat(
                api_key=api_keys.get("emergent", EMERGENT_LLM_KEY),
                session_id=f"{chat_id}_{uuid.uuid4().hex[:6]}",
                system_message=system_prompt
            ).with_model(fb_provider, fb_model)
            extra_params = {}
            if temperature is not None:
                extra_params["temperature"] = temperature
            if max_tokens is not None:
                extra_params["max_tokens"] = max_tokens
            if extra_params:
                llm_chat = llm_chat.with_params(**extra_params)

            file_contents = []
            if attachments:
                from emergentintegrations.llm.chat import ImageContent
                for att in attachments:
                    if isinstance(att, str):
                        if att.startswith("data:image"):
                            b64data = att.split(",", 1)[1] if "," in att else att
                            file_contents.append(ImageContent(b64data))
                        elif att.startswith("/files/") or att.startswith("http"):
                            try:
                                img_path = UPLOAD_DIR / att.replace("/files/", "") if att.startswith("/files/") else None
                                if img_path and img_path.exists():
                                    import base64 as b64mod
                                    with open(img_path, "rb") as f:
                                        b64data = b64mod.b64encode(f.read()).decode()
                                    file_contents.append(ImageContent(b64data))
                            except Exception:
                                pass

            user_message = UserMessage(text=content, file_contents=file_contents if file_contents else None)
            result = await llm_chat.send_message(user_message)
            return result, fb_provider, fb_model
        except Exception as e:
            last_error = e
            logger.warning(f"LLM call failed for {fb_provider}/{fb_model}: {e}. Trying fallback...")
            continue

    raise last_error or Exception("All LLM models failed")
