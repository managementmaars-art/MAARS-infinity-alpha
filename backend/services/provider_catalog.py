"""
Central provider catalog for MAARS — data-driven, single source of truth.

Replaces the scattered hardcoded provider knowledge that previously lived in
setup_orchestrator.py, llm_service._OPENAI_COMPAT_STREAM_URLS, and the
SetupWizard.jsx PROVIDERS array.

Structure
─────────
Each entry is a `ProviderEntry`:
    slug                — stable lowercase identifier ("openai", "xai", "qwen")
    display_name        — UI label
    env_var             — the env var the rest of the system reads
    dashboard_url       — the page the user clicks "Open dashboard" to reach
    validation_strategy — see VALIDATION_STRATEGIES below
    api_format          — wire format the model-call code uses
    category            — llm | search | audio | image | multimodal | infra
    quick               — True for the four-provider quick-setup tier
    supports_models_listing — True when the provider exposes a /models endpoint
    base_url            — used by the openai_compatible_models validator
    notes               — operator-facing free text

Validation strategies
─────────────────────
    openai_compatible_models     GET {base_url}/v1/models  with Bearer auth
    anthropic_models             GET /v1/models  with x-api-key + anthropic-version
    google_models                GET /v1beta/models?key=…
    cohere_check                 GET /v1/check-api-key
    huggingface_whoami           GET /api/whoami-v2 with Bearer
    placeholder_manual           store the key, but no live validation possible
                                 (e.g. AWS Bedrock — needs SigV4)
    env_detect_only              we honor the env value but never call out
    coming_soon                  adapter not yet implemented; UI surfaces this honestly

The catalog is intentionally curated from the MAARS PDF — it is NOT every
provider on Earth. Adding a new provider is a single dict-entry edit.
"""
from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from typing import Any, Optional

import httpx

# -----------------------------------------------------------------------------
# strategy constants
# -----------------------------------------------------------------------------

VALIDATION_STRATEGIES = (
    "openai_compatible_models",
    "anthropic_models",
    "google_models",
    "cohere_check",
    "huggingface_whoami",
    "custom_http_ping",        # provider-specific endpoint (ElevenLabs /v1/user, etc.)
    "placeholder_manual",
    "env_detect_only",
    "coming_soon",
)

CATEGORIES = ("llm", "search", "audio", "image", "multimodal", "infra")


# -----------------------------------------------------------------------------
# data shape
# -----------------------------------------------------------------------------

@dataclass(frozen=True)
class ProviderEntry:
    slug: str
    display_name: str
    env_var: str
    dashboard_url: str
    validation_strategy: str
    api_format: str
    category: str
    quick: bool = False
    supports_models_listing: bool = True
    base_url: str = ""
    notes: str = ""

    def to_public_dict(self) -> dict[str, Any]:
        d = asdict(self)
        # Public dict — never includes the actual key value.
        return d


# -----------------------------------------------------------------------------
# catalog — 33 providers from the PDF
# -----------------------------------------------------------------------------

CATALOG: list[ProviderEntry] = [
    # ── Quick tier (matches the 4 providers in services/providers/) ──────────
    ProviderEntry("openai",     "OpenAI",     "OPENAI_API_KEY",     "https://platform.openai.com/api-keys",
                  "openai_compatible_models", "openai_compat", "llm", quick=True,
                  base_url="https://api.openai.com"),
    ProviderEntry("anthropic",  "Anthropic",  "ANTHROPIC_API_KEY",  "https://console.anthropic.com/settings/keys",
                  "anthropic_models", "anthropic", "llm", quick=True,
                  base_url="https://api.anthropic.com"),
    ProviderEntry("groq",       "Groq",       "GROQ_API_KEY",       "https://console.groq.com/keys",
                  "openai_compatible_models", "openai_compat", "llm", quick=True,
                  base_url="https://api.groq.com/openai", notes="Fast inference (LPU)."),
    ProviderEntry("deepseek",   "DeepSeek",   "DEEPSEEK_API_KEY",   "https://platform.deepseek.com/api_keys",
                  "openai_compatible_models", "openai_compat", "llm", quick=True,
                  base_url="https://api.deepseek.com", notes="Economy reasoning."),

    # ── Advanced — frontier LLM providers ────────────────────────────────────
    ProviderEntry("google",     "Google Gemini", "GOOGLE_API_KEY", "https://aistudio.google.com/app/apikey",
                  "google_models", "google", "llm",
                  base_url="https://generativelanguage.googleapis.com",
                  notes="Gemini 2.5 Pro/Flash, multimodal."),
    ProviderEntry("xai",        "xAI (Grok)", "XAI_API_KEY", "https://console.x.ai/",
                  "openai_compatible_models", "openai_compat", "llm",
                  base_url="https://api.x.ai", notes="Grok-4, Grok-3 family."),
    ProviderEntry("mistral",    "Mistral",    "MISTRAL_API_KEY",    "https://console.mistral.ai/api-keys/",
                  "openai_compatible_models", "openai_compat", "llm",
                  base_url="https://api.mistral.ai", notes="Mistral Large, Codestral, Pixtral."),
    ProviderEntry("perplexity", "Perplexity", "PERPLEXITY_API_KEY", "https://www.perplexity.ai/settings/api",
                  "openai_compatible_models", "openai_compat", "search",
                  base_url="https://api.perplexity.ai", notes="Sonar family — research-grade web search."),
    ProviderEntry("cohere",     "Cohere",     "COHERE_API_KEY",     "https://dashboard.cohere.com/api-keys",
                  "cohere_check", "cohere", "llm",
                  base_url="https://api.cohere.com", notes="Command family + retrieval."),
    ProviderEntry("ai21",       "AI21 Labs",  "AI21_API_KEY",       "https://studio.ai21.com/account/api-key",
                  "openai_compatible_models", "openai_compat", "llm",
                  base_url="https://api.ai21.com/studio", notes="Jamba family."),

    # ── Advanced — open-model hosts (OpenAI-compatible) ──────────────────────
    ProviderEntry("together",   "Together AI", "TOGETHER_API_KEY",  "https://api.together.xyz/settings/api-keys",
                  "openai_compatible_models", "openai_compat", "llm",
                  base_url="https://api.together.xyz", notes="Hosts Llama, DeepSeek, Qwen open models."),
    ProviderEntry("fireworks",  "Fireworks AI", "FIREWORKS_API_KEY","https://app.fireworks.ai/settings/users/api-keys",
                  "openai_compatible_models", "openai_compat", "llm",
                  base_url="https://api.fireworks.ai/inference"),
    ProviderEntry("huggingface","HuggingFace","HF_TOKEN",           "https://huggingface.co/settings/tokens",
                  "huggingface_whoami", "huggingface", "llm",
                  base_url="https://huggingface.co", notes="Pass-through to 175k+ models."),
    ProviderEntry("sambanova",  "SambaNova",  "SAMBANOVA_API_KEY",  "https://cloud.sambanova.ai/apis",
                  "openai_compatible_models", "openai_compat", "llm",
                  base_url="https://api.sambanova.ai"),
    ProviderEntry("nvidia_nim", "NVIDIA NIM", "NVIDIA_API_KEY",     "https://build.nvidia.com/",
                  "openai_compatible_models", "openai_compat", "llm",
                  base_url="https://integrate.api.nvidia.com", notes="Hosts Nemotron, Llama variants."),
    ProviderEntry("novita",     "Novita AI",  "NOVITA_API_KEY",     "https://novita.ai/settings/key-management",
                  "openai_compatible_models", "openai_compat", "llm",
                  base_url="https://api.novita.ai"),
    ProviderEntry("lepton",     "Lepton AI",  "LEPTON_API_KEY",     "https://dashboard.lepton.ai/",
                  "openai_compatible_models", "openai_compat", "llm",
                  base_url="https://api.lepton.ai"),
    ProviderEntry("lambda",     "Lambda Labs","LAMBDA_API_KEY",     "https://cloud.lambdalabs.com/api-keys",
                  "openai_compatible_models", "openai_compat", "llm",
                  base_url="https://api.lambdalabs.com/v1"),
    ProviderEntry("cerebras",   "Cerebras",   "CEREBRAS_API_KEY",   "https://cloud.cerebras.ai/",
                  "openai_compatible_models", "openai_compat", "llm",
                  base_url="https://api.cerebras.ai", notes="Wafer-scale fast inference."),
    ProviderEntry("hyperbolic", "Hyperbolic", "HYPERBOLIC_API_KEY", "https://app.hyperbolic.xyz/settings",
                  "openai_compatible_models", "openai_compat", "llm",
                  base_url="https://api.hyperbolic.xyz"),

    # ── Advanced — Chinese LLM providers ─────────────────────────────────────
    ProviderEntry("zhipu",      "Zhipu / GLM","ZHIPU_API_KEY",      "https://open.bigmodel.cn/usercenter/apikeys",
                  "openai_compatible_models", "openai_compat", "llm",
                  base_url="https://open.bigmodel.cn/api/paas", notes="GLM-4 family."),
    ProviderEntry("qwen",       "Qwen / Alibaba","DASHSCOPE_API_KEY","https://dashscope.console.aliyun.com/apiKey",
                  "openai_compatible_models", "openai_compat", "llm",
                  base_url="https://dashscope.aliyuncs.com/compatible-mode",
                  notes="Qwen Max/Plus/Turbo/QwQ via DashScope."),
    ProviderEntry("moonshot",   "Moonshot / Kimi","MOONSHOT_API_KEY","https://platform.moonshot.cn/console/api-keys",
                  "openai_compatible_models", "openai_compat", "llm",
                  base_url="https://api.moonshot.cn"),
    ProviderEntry("yi",         "Yi / 01.AI", "YI_API_KEY",         "https://platform.lingyiwanwu.com/apikeys",
                  "openai_compatible_models", "openai_compat", "llm",
                  base_url="https://api.lingyiwanwu.com"),
    ProviderEntry("doubao",     "Doubao / ByteDance","DOUBAO_API_KEY","https://www.volcengine.com/",
                  "placeholder_manual", "custom", "llm",
                  notes="Volcengine SigV4 auth — adapter pending."),
    ProviderEntry("minimax",    "MiniMax",    "MINIMAX_API_KEY",    "https://api.minimax.chat/user-center/basic-information/interface-key",
                  "placeholder_manual", "custom", "llm",
                  notes="Custom authentication shape — adapter pending."),
    ProviderEntry("reka",       "Reka",       "REKA_API_KEY",       "https://platform.reka.ai/",
                  "openai_compatible_models", "openai_compat", "llm",
                  base_url="https://api.reka.ai/v1", notes="Reka Edge/Flash/Core — multimodal text+vision+video."),

    # ── Advanced — specialty / vertical LLMs ─────────────────────────────────
    ProviderEntry("upstage",    "Upstage / Solar","UPSTAGE_API_KEY","https://console.upstage.ai/api-keys",
                  "openai_compatible_models", "openai_compat", "llm",
                  base_url="https://api.upstage.ai", notes="Solar Pro/Mini."),
    ProviderEntry("writer",     "Writer / Palmyra","WRITER_API_KEY","https://app.writer.com/aistudio/organization/keys",
                  "openai_compatible_models", "openai_compat", "llm",
                  base_url="https://api.writer.com/v1", notes="Palmyra family — enterprise writing."),
    ProviderEntry("arcee",      "Arcee AI",   "ARCEE_API_KEY",      "https://app.arcee.ai/",
                  "coming_soon", "openai_compat", "llm",
                  notes="Adapter pending — env detect only."),
    ProviderEntry("inception",  "Inception AI","INCEPTION_API_KEY", "https://www.inceptionlabs.ai/",
                  "coming_soon", "openai_compat", "llm",
                  notes="Adapter pending — env detect only."),

    # ── Advanced — meta / cloud distributors ─────────────────────────────────
    ProviderEntry("meta_llama_api","Meta Llama API","LLAMA_API_KEY","https://llama.developer.meta.com/",
                  "openai_compatible_models", "openai_compat", "llm",
                  base_url="https://api.llama.com", notes="Meta-hosted Llama family."),
    ProviderEntry("bedrock",    "AWS Bedrock","AWS_BEDROCK_KEY",    "https://console.aws.amazon.com/bedrock",
                  "placeholder_manual", "custom", "llm",
                  supports_models_listing=False,
                  notes="Requires AWS SigV4 (AWS_ACCESS_KEY_ID + AWS_SECRET_ACCESS_KEY)."),

    # ── Meta-routers (aggregate providers) ────────────────────────────────────
    ProviderEntry("openrouter", "OpenRouter", "OPENROUTER_API_KEY", "https://openrouter.ai/settings/keys",
                  "openai_compatible_models", "openai_compat", "llm",
                  base_url="https://openrouter.ai/api",
                  notes="Meta-router aggregating 200+ models. OpenAI-compatible. Free tier for some models."),
    ProviderEntry("bytez",      "Bytez",      "BYTEZ_API_KEY",      "https://bytez.com/auth",
                  "openai_compatible_models", "openai_compat", "llm",
                  base_url="https://api.bytez.com",
                  notes="Open-source model hub with 222k models. Free tier available."),

    # ── Non-LLM (audio / multimodal) — wired for completeness ────────────────
    ProviderEntry("elevenlabs", "ElevenLabs","ELEVENLABS_API_KEY",  "https://elevenlabs.io/app/settings/api-keys",
                  "custom_http_ping", "custom", "audio",
                  base_url="https://api.elevenlabs.io",
                  notes="TTS / voice cloning. Auth: xi-api-key header."),
]

# Convenience indexes built once at import.
BY_SLUG: dict[str, ProviderEntry] = {p.slug: p for p in CATALOG}
QUICK_PROVIDERS: list[ProviderEntry] = [p for p in CATALOG if p.quick]
ADVANCED_PROVIDERS: list[ProviderEntry] = [p for p in CATALOG if not p.quick]


def get(slug: str) -> Optional[ProviderEntry]:
    return BY_SLUG.get(slug)


def env_var_for(slug: str) -> str:
    e = BY_SLUG.get(slug)
    return e.env_var if e else ""


# -----------------------------------------------------------------------------
# validators — one per validation_strategy
# -----------------------------------------------------------------------------

_DEFAULT_TIMEOUT = 8.0


async def _http_get_ok(url: str, headers: dict[str, str]) -> tuple[bool, int, str]:
    t0 = time.time()
    try:
        async with httpx.AsyncClient(timeout=_DEFAULT_TIMEOUT) as c:
            r = await c.get(url, headers=headers)
        ok = 200 <= r.status_code < 300
        return ok, int((time.time() - t0) * 1000), f"HTTP {r.status_code}"
    except Exception as exc:
        return False, int((time.time() - t0) * 1000), f"{type(exc).__name__}: {exc}"


async def _validate_openai_compat(base_url: str, key: str) -> tuple[bool, str, dict[str, Any]]:
    if not base_url:
        return False, "no base_url configured for this provider", {}
    ok, latency, detail = await _http_get_ok(
        f"{base_url.rstrip('/')}/v1/models",
        {"Authorization": f"Bearer {key}"},
    )
    return ok, detail, {"latency_ms": latency}


async def _validate_anthropic(key: str) -> tuple[bool, str, dict[str, Any]]:
    ok, latency, detail = await _http_get_ok(
        "https://api.anthropic.com/v1/models",
        {"x-api-key": key, "anthropic-version": "2023-06-01"},
    )
    return ok, detail, {"latency_ms": latency}


async def _validate_google(key: str) -> tuple[bool, str, dict[str, Any]]:
    ok, latency, detail = await _http_get_ok(
        f"https://generativelanguage.googleapis.com/v1beta/models?key={key}",
        {},
    )
    return ok, detail, {"latency_ms": latency}


async def _validate_cohere(key: str) -> tuple[bool, str, dict[str, Any]]:
    ok, latency, detail = await _http_get_ok(
        "https://api.cohere.com/v1/check-api-key",
        {"Authorization": f"Bearer {key}"},
    )
    return ok, detail, {"latency_ms": latency}


async def _validate_huggingface(key: str) -> tuple[bool, str, dict[str, Any]]:
    ok, latency, detail = await _http_get_ok(
        "https://huggingface.co/api/whoami-v2",
        {"Authorization": f"Bearer {key}"},
    )
    return ok, detail, {"latency_ms": latency}


async def _validate_elevenlabs(key: str) -> tuple[bool, str, dict[str, Any]]:
    ok, latency, detail = await _http_get_ok(
        "https://api.elevenlabs.io/v1/user",
        {"xi-api-key": key},
    )
    return ok, detail, {"latency_ms": latency}


async def validate_provider(slug: str, raw_key: str) -> tuple[bool, str, dict[str, Any]]:
    """
    Dispatch validation by strategy. Returns (ok, human_detail, metadata).

    Honest semantics for the wizard UI:
      * placeholder_manual → returns (True, "stored, manual validation required", ...)
      * coming_soon        → returns (False, "adapter not yet implemented", ...)
      * env_detect_only    → returns (True, "stored, no live validation", ...)
    """
    entry = BY_SLUG.get(slug)
    if entry is None:
        return False, f"unknown provider: {slug}", {}
    raw_key = (raw_key or "").strip()
    if not raw_key:
        return False, "API key is required", {}

    strat = entry.validation_strategy
    if strat == "openai_compatible_models":
        return await _validate_openai_compat(entry.base_url, raw_key)
    if strat == "anthropic_models":
        return await _validate_anthropic(raw_key)
    if strat == "google_models":
        return await _validate_google(raw_key)
    if strat == "cohere_check":
        return await _validate_cohere(raw_key)
    if strat == "huggingface_whoami":
        return await _validate_huggingface(raw_key)
    if strat == "custom_http_ping" and entry.slug == "elevenlabs":
        return await _validate_elevenlabs(raw_key)
    if strat == "placeholder_manual":
        return True, "Stored — provider doesn't expose a cheap validation endpoint, manual verification required.", {"validation": "manual"}
    if strat == "env_detect_only":
        return True, "Stored — env-detected, no live validation performed.", {"validation": "env_only"}
    if strat == "coming_soon":
        return False, "Provider adapter not yet implemented in MAARS — env will be saved but routing won't use this provider.", {"validation": "pending"}
    return False, f"unknown validation strategy: {strat}", {}
