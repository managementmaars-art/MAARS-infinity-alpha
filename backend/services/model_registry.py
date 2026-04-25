"""
Curated, normalized model registry for MAARS — the routing brain's input set.

This is NOT a complete enumeration of every model on every provider. It is a
curated, representative catalog drawn from the model families the MAARS PDF
calls out. Routing aliases (maars/auto, maars/code, maars/reasoning, …) score
candidates from this set; v1_gateway's existing 175k+ /v1/models endpoint
remains the wide pass-through for OpenAI-SDK clients.

Adding a new model is one dict-entry edit.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Optional

# -----------------------------------------------------------------------------
# constants
# -----------------------------------------------------------------------------

TIERS = ("economy", "standard", "premium", "flagship", "reasoning", "research", "vision", "code", "audio", "image")

CAPABILITIES = (
    "chat", "code", "reasoning", "math", "vision", "audio",
    "long_context", "search", "tools", "multilingual", "fast",
    "creative", "research",
)


# -----------------------------------------------------------------------------
# data shape
# -----------------------------------------------------------------------------

@dataclass(frozen=True)
class ModelEntry:
    model_id: str                       # the provider-native model id
    provider_slug: str                  # matches provider_catalog.ProviderEntry.slug
    display_name: str
    tier: str
    capabilities: tuple[str, ...] = ()
    routing_tags: tuple[str, ...] = ()
    context_window: int = 16_000
    cost_in_per_mtok: float = 0.0       # USD per million input tokens
    cost_out_per_mtok: float = 0.0      # USD per million output tokens
    avg_latency_ms: int = 1500
    default_visibility: bool = True
    supports_manual_selection: bool = True
    notes: str = ""

    @property
    def maars_id(self) -> str:
        """The id surfaced through /v1/models — `<provider>/<model>`."""
        return f"{self.provider_slug}/{self.model_id}"

    @property
    def cost_per_mtok_blended(self) -> float:
        """Crude blended cost used by the scoring router."""
        return (self.cost_in_per_mtok + self.cost_out_per_mtok) / 2.0

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["maars_id"] = self.maars_id
        d["cost_per_mtok_blended"] = self.cost_per_mtok_blended
        return d


# -----------------------------------------------------------------------------
# curated catalog — 80+ models across the PDF families
# -----------------------------------------------------------------------------

REGISTRY: list[ModelEntry] = [
    # ── OpenAI ───────────────────────────────────────────────────────────────
    ModelEntry("gpt-5",          "openai", "GPT-5",          "flagship",
               ("chat", "code", "reasoning", "vision", "tools"),
               ("flagship",), 256_000, 5.0, 15.0, 2200),
    ModelEntry("gpt-4.1",        "openai", "GPT-4.1",        "premium",
               ("chat", "code", "reasoning", "vision"),
               ("premium",), 1_000_000, 2.5, 10.0, 1700),
    ModelEntry("gpt-4.1-mini",   "openai", "GPT-4.1 mini",   "standard",
               ("chat", "code", "fast"),
               ("standard", "fast"), 1_000_000, 0.4, 1.6, 800),
    ModelEntry("gpt-4.1-nano",   "openai", "GPT-4.1 nano",   "economy",
               ("chat", "fast"), ("economy", "fast"), 1_000_000, 0.1, 0.4, 600),
    ModelEntry("gpt-4o",         "openai", "GPT-4o",         "premium",
               ("chat", "code", "vision", "audio", "tools"),
               ("premium", "vision"), 128_000, 2.5, 10.0, 1500),
    ModelEntry("gpt-4o-mini",    "openai", "GPT-4o mini",    "economy",
               ("chat", "code", "fast"),
               ("economy",), 128_000, 0.15, 0.6, 700),
    ModelEntry("o4",             "openai", "o4 (reasoning)", "reasoning",
               ("reasoning", "math", "code"), ("reasoning",), 200_000, 15.0, 60.0, 5500),
    ModelEntry("o4-mini",        "openai", "o4-mini",        "reasoning",
               ("reasoning", "math", "code"), ("reasoning",), 200_000, 3.0, 12.0, 3000),
    ModelEntry("o3",             "openai", "o3",             "reasoning",
               ("reasoning", "math"), ("reasoning",), 200_000, 15.0, 60.0, 5500),

    # ── Anthropic ────────────────────────────────────────────────────────────
    ModelEntry("claude-opus-4-6",     "anthropic", "Claude Opus 4.6",   "flagship",
               ("chat", "code", "reasoning", "vision", "long_context", "tools"),
               ("flagship",), 200_000, 15.0, 75.0, 2500),
    ModelEntry("claude-sonnet-4-6",   "anthropic", "Claude Sonnet 4.6", "premium",
               ("chat", "code", "reasoning", "vision", "long_context"),
               ("premium",), 200_000, 3.0, 15.0, 1500),
    ModelEntry("claude-haiku-4-5-20251001", "anthropic", "Claude Haiku 4.5", "standard",
               ("chat", "code", "fast"),
               ("standard", "fast"), 200_000, 0.8, 4.0, 700),

    # ── Google Gemini ────────────────────────────────────────────────────────
    ModelEntry("gemini-2.5-pro",   "google", "Gemini 2.5 Pro",   "premium",
               ("chat", "code", "reasoning", "vision", "audio", "long_context", "tools"),
               ("premium", "vision"), 2_000_000, 1.25, 10.0, 1800),
    ModelEntry("gemini-2.5-flash", "google", "Gemini 2.5 Flash", "standard",
               ("chat", "code", "vision", "fast"),
               ("standard", "fast", "vision"), 1_000_000, 0.075, 0.30, 800),

    # ── xAI Grok ─────────────────────────────────────────────────────────────
    ModelEntry("grok-4",          "xai", "Grok 4",          "flagship",
               ("chat", "reasoning", "code", "vision", "search"),
               ("flagship",), 256_000, 5.0, 15.0, 2300),
    ModelEntry("grok-3",          "xai", "Grok 3",          "premium",
               ("chat", "reasoning", "code"),
               ("premium",), 131_000, 3.0, 15.0, 1700),
    ModelEntry("grok-3-mini",     "xai", "Grok 3 mini",     "standard",
               ("chat", "fast"), ("standard", "fast"), 131_000, 0.3, 0.5, 800),

    # ── DeepSeek ─────────────────────────────────────────────────────────────
    ModelEntry("deepseek-r1-0528","deepseek", "DeepSeek R1", "reasoning",
               ("reasoning", "math", "code"), ("reasoning", "economy"), 64_000, 0.55, 2.19, 3500),
    ModelEntry("deepseek-v3-0324","deepseek", "DeepSeek V3", "standard",
               ("chat", "code", "reasoning"), ("standard",), 64_000, 0.27, 1.10, 1200),
    ModelEntry("deepseek-chat",   "deepseek", "DeepSeek Chat","economy",
               ("chat", "code", "fast"), ("economy",), 64_000, 0.14, 0.28, 900),

    # ── Mistral ──────────────────────────────────────────────────────────────
    ModelEntry("mistral-large-latest", "mistral", "Mistral Large", "premium",
               ("chat", "code", "reasoning"), ("premium",), 131_000, 2.0, 6.0, 1500),
    ModelEntry("codestral-latest",     "mistral", "Codestral",     "code",
               ("code", "chat"), ("code",), 32_000, 0.3, 0.9, 700),
    ModelEntry("pixtral-large-latest", "mistral", "Pixtral Large", "vision",
               ("chat", "vision", "code"), ("vision",), 128_000, 2.0, 6.0, 1700),
    ModelEntry("mistral-medium-latest","mistral", "Mistral Medium","standard",
               ("chat", "code"), ("standard",), 32_000, 0.4, 2.0, 1100),
    ModelEntry("mistral-small-latest", "mistral", "Mistral Small", "economy",
               ("chat", "fast"), ("economy",), 32_000, 0.2, 0.6, 700),

    # ── Perplexity Sonar ─────────────────────────────────────────────────────
    ModelEntry("sonar-pro",            "perplexity", "Sonar Pro",          "research",
               ("search", "research", "chat"), ("research",), 200_000, 3.0, 15.0, 4500),
    ModelEntry("sonar-reasoning-pro",  "perplexity", "Sonar Reasoning Pro","research",
               ("search", "research", "reasoning"), ("research",), 127_000, 2.0, 8.0, 5000),
    ModelEntry("sonar-deep-research",  "perplexity", "Sonar Deep Research","research",
               ("search", "research"), ("research",), 200_000, 5.0, 25.0, 8000),
    ModelEntry("sonar",                "perplexity", "Sonar",              "standard",
               ("search", "chat"), ("standard", "search"), 127_000, 1.0, 1.0, 2500),

    # ── Cohere Command ───────────────────────────────────────────────────────
    ModelEntry("command-a-03-2025", "cohere", "Command A",  "premium",
               ("chat", "code", "reasoning", "tools"), ("premium",), 256_000, 2.5, 10.0, 1600),
    ModelEntry("command-r-plus",    "cohere", "Command R+", "standard",
               ("chat", "code", "tools"), ("standard",), 128_000, 2.5, 10.0, 1500),
    ModelEntry("command-r",         "cohere", "Command R",  "economy",
               ("chat", "code"), ("economy",), 128_000, 0.5, 1.5, 1000),

    # ── Qwen / Alibaba ───────────────────────────────────────────────────────
    ModelEntry("qwen-max",     "qwen", "Qwen Max",     "premium",
               ("chat", "code", "reasoning", "multilingual"), ("premium",), 32_000, 2.0, 6.0, 1500),
    ModelEntry("qwen-plus",    "qwen", "Qwen Plus",    "standard",
               ("chat", "code", "multilingual"), ("standard",), 131_000, 0.4, 1.2, 1000),
    ModelEntry("qwen-turbo",   "qwen", "Qwen Turbo",   "economy",
               ("chat", "fast"), ("economy", "fast"), 1_008_000, 0.05, 0.20, 700),
    ModelEntry("qwq-32b",      "qwen", "QwQ 32B",      "reasoning",
               ("reasoning", "math", "code"), ("reasoning",), 131_000, 1.2, 4.8, 3500),

    # ── Zhipu / GLM ──────────────────────────────────────────────────────────
    ModelEntry("glm-4-plus",   "zhipu", "GLM-4 Plus", "premium",
               ("chat", "code", "reasoning", "multilingual"), ("premium",), 128_000, 0.7, 2.1, 1300),
    ModelEntry("glm-4-air",    "zhipu", "GLM-4 Air",  "standard",
               ("chat", "code"), ("standard",), 128_000, 0.1, 0.3, 900),
    ModelEntry("glm-4-flash",  "zhipu", "GLM-4 Flash","economy",
               ("chat", "fast"), ("economy", "fast"), 128_000, 0.05, 0.05, 600),

    # ── Moonshot Kimi ────────────────────────────────────────────────────────
    ModelEntry("kimi-latest",        "moonshot", "Kimi Latest",        "standard",
               ("chat", "long_context", "code"), ("standard",), 200_000, 2.0, 5.0, 1500),
    ModelEntry("moonshot-v1-128k",   "moonshot", "Moonshot V1 128K",   "standard",
               ("chat", "long_context"), ("standard",), 128_000, 1.7, 1.7, 1300),

    # ── AI21 Jamba ───────────────────────────────────────────────────────────
    ModelEntry("jamba-large-1.7", "ai21", "Jamba Large 1.7", "premium",
               ("chat", "code", "long_context"), ("premium",), 256_000, 2.0, 8.0, 1500),
    ModelEntry("jamba-mini-1.7",  "ai21", "Jamba Mini 1.7",  "economy",
               ("chat", "fast"), ("economy",), 256_000, 0.2, 0.4, 800),

    # ── Upstage Solar ────────────────────────────────────────────────────────
    ModelEntry("solar-pro",   "upstage", "Solar Pro",   "premium",
               ("chat", "code", "reasoning"), ("premium",), 32_000, 2.5, 5.0, 1400),
    ModelEntry("solar-mini",  "upstage", "Solar Mini",  "economy",
               ("chat", "fast"), ("economy",), 32_000, 0.15, 0.15, 700),

    # ── Writer / Palmyra ─────────────────────────────────────────────────────
    ModelEntry("palmyra-x5",      "writer", "Palmyra X5",      "premium",
               ("chat", "code", "creative"), ("premium",), 100_000, 1.5, 6.0, 1500),
    ModelEntry("palmyra-x4",      "writer", "Palmyra X4",      "standard",
               ("chat", "creative"), ("standard",), 128_000, 1.0, 3.0, 1200),
    ModelEntry("palmyra-creative","writer", "Palmyra Creative","standard",
               ("chat", "creative"), ("standard",), 128_000, 1.0, 3.0, 1200),

    # ── Yi / 01.AI ───────────────────────────────────────────────────────────
    ModelEntry("yi-large",     "yi", "Yi Large",     "standard",
               ("chat", "code", "multilingual"), ("standard",), 32_000, 0.6, 2.0, 1300),
    ModelEntry("yi-lightning", "yi", "Yi Lightning", "economy",
               ("chat", "fast"), ("economy", "fast"), 16_000, 0.1, 0.1, 700),

    # ── NVIDIA Nemotron (via NIM) ────────────────────────────────────────────
    ModelEntry("nvidia/llama-3.1-nemotron-70b-instruct", "nvidia_nim", "Nemotron 70B", "premium",
               ("chat", "reasoning"), ("premium",), 128_000, 0.35, 0.35, 1400),
    ModelEntry("nvidia/llama-3.1-nemotron-340b-instruct","nvidia_nim", "Nemotron 340B","flagship",
               ("chat", "reasoning"), ("flagship",), 128_000, 1.0, 1.0, 2200),

    # ── Meta Llama API ───────────────────────────────────────────────────────
    ModelEntry("llama-4-scout-17b-16e-instruct",     "meta_llama_api", "Llama 4 Scout",     "standard",
               ("chat", "code", "vision"), ("standard", "vision"), 1_000_000, 0.18, 0.59, 1200),
    ModelEntry("llama-4-maverick-17b-128e-instruct", "meta_llama_api", "Llama 4 Maverick",  "premium",
               ("chat", "code", "reasoning"), ("premium",), 1_000_000, 0.50, 1.50, 1500),
    ModelEntry("llama-3.3-70b-versatile",            "meta_llama_api", "Llama 3.3 70B",     "standard",
               ("chat", "code"), ("standard",), 128_000, 0.59, 0.79, 1100),

    # ── Together AI (open hosts) ─────────────────────────────────────────────
    ModelEntry("meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8", "together",
               "Llama 4 Maverick (Together)", "standard",
               ("chat", "code"), ("standard",), 1_000_000, 0.60, 1.80, 1300),
    ModelEntry("deepseek-ai/DeepSeek-R1", "together",
               "DeepSeek R1 (Together)", "reasoning",
               ("reasoning", "math", "code"), ("reasoning",), 64_000, 3.0, 7.0, 4000),

    # ── Fireworks AI (open hosts) ────────────────────────────────────────────
    ModelEntry("accounts/fireworks/models/llama4-scout-instruct-basic", "fireworks",
               "Llama 4 Scout (Fireworks)", "economy",
               ("chat", "code", "fast"), ("economy", "fast"), 1_000_000, 0.18, 0.59, 900),
    ModelEntry("accounts/fireworks/models/deepseek-v3", "fireworks",
               "DeepSeek V3 (Fireworks)", "standard",
               ("chat", "code", "reasoning"), ("standard",), 64_000, 0.90, 0.90, 1500),

    # ── Cerebras (fast inference) ────────────────────────────────────────────
    ModelEntry("llama-3.3-70b", "cerebras", "Llama 3.3 70B (Cerebras)", "economy",
               ("chat", "code", "fast"), ("economy", "fast"), 128_000, 0.85, 1.20, 300),
    ModelEntry("llama-3.1-8b",  "cerebras", "Llama 3.1 8B (Cerebras)",  "economy",
               ("chat", "fast"), ("economy", "fast"), 128_000, 0.10, 0.10, 200),

    # ── Groq (LPU fast inference) ────────────────────────────────────────────
    ModelEntry("llama-3.3-70b-versatile",        "groq", "Llama 3.3 70B (Groq)", "economy",
               ("chat", "code", "fast"), ("economy", "fast"), 128_000, 0.59, 0.79, 350),
    ModelEntry("deepseek-r1-distill-llama-70b",  "groq", "DeepSeek R1 Distill (Groq)", "reasoning",
               ("reasoning", "math", "fast"), ("reasoning", "fast"), 128_000, 0.75, 0.99, 500),
    ModelEntry("llama-3.1-8b-instant",           "groq", "Llama 3.1 8B Instant (Groq)", "economy",
               ("chat", "fast"), ("economy", "fast"), 128_000, 0.05, 0.08, 200),

    # ── ElevenLabs (audio-only — visible but not selectable for chat) ────────
    ModelEntry("eleven_multilingual_v2", "elevenlabs", "ElevenLabs Multilingual v2", "audio",
               ("audio", "multilingual"), ("audio",), 0, 0.0, 0.0, 1500,
               supports_manual_selection=False),
]


# -----------------------------------------------------------------------------
# indexes + lookups
# -----------------------------------------------------------------------------

BY_MAARS_ID: dict[str, ModelEntry] = {m.maars_id: m for m in REGISTRY}
BY_PROVIDER: dict[str, list[ModelEntry]] = {}
for _m in REGISTRY:
    BY_PROVIDER.setdefault(_m.provider_slug, []).append(_m)


def get(maars_id: str) -> Optional[ModelEntry]:
    return BY_MAARS_ID.get(maars_id)


def list_all() -> list[ModelEntry]:
    return list(REGISTRY)


def list_for_provider(slug: str) -> list[ModelEntry]:
    return BY_PROVIDER.get(slug, [])


def list_by_capability(cap: str) -> list[ModelEntry]:
    return [m for m in REGISTRY if cap in m.capabilities]


def list_by_tier(tier: str) -> list[ModelEntry]:
    return [m for m in REGISTRY if m.tier == tier]


def filter_visible_for(*, configured_providers: set[str], package_visible_models: Optional[set[str]] = None) -> list[ModelEntry]:
    """
    Return models the caller is allowed to see / select.

    `configured_providers`     — set of provider slugs whose env vars are populated
    `package_visible_models`   — optional whitelist from the user's package; if None, all visible models pass
    """
    out: list[ModelEntry] = []
    for m in REGISTRY:
        if not m.default_visibility:
            continue
        if m.provider_slug not in configured_providers:
            continue
        if package_visible_models is not None and m.maars_id not in package_visible_models:
            continue
        out.append(m)
    return out


def routing_candidates() -> list[ModelEntry]:
    """Models eligible for the scoring router (excludes audio-only entries)."""
    return [m for m in REGISTRY if m.supports_manual_selection and "audio" not in m.tier]
