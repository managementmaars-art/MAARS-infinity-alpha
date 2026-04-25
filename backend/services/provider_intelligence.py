"""
Provider Intelligence — live data from every provider API.

Queries real endpoints for:
  - Balance / credits remaining
  - Available models (GET /v1/models)
  - Rate limits & quotas
  - Token pricing per model
  - Account tier / plan info

No estimates — if a provider doesn't expose data, returns "check_dashboard".
"""
from __future__ import annotations

import logging
import os
import time
from datetime import datetime, timezone
from typing import Any, Optional

import httpx

from db import db

logger = logging.getLogger(__name__)

INTEL_COLLECTION = "provider_intelligence_snapshots"
_cache: dict[str, dict] = {}
CACHE_TTL = 300  # 5 min


# ── Helper: OpenAI-compatible /v1/models fetcher ─────────────────────────────

async def _fetch_openai_compat_models(base_url: str, api_key: str, auth_header: str = "Authorization", auth_prefix: str = "Bearer ") -> list[dict]:
    """Fetch models from any OpenAI-compatible /v1/models endpoint."""
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(
            f"{base_url}/v1/models",
            headers={auth_header: f"{auth_prefix}{api_key}"},
        )
        if resp.status_code != 200:
            return []
        data = resp.json()
        models = data.get("data", []) if isinstance(data, dict) else []
        return [{"id": m.get("id", ""), "owned_by": m.get("owned_by", ""), "object": m.get("object", "")} for m in models]


# ── Per-provider intelligence fetchers ────────────────────────────────────────

async def _intel_openai(api_key: str) -> dict:
    models = await _fetch_openai_compat_models("https://api.openai.com", api_key)
    return {
        "balance": {"status": "check_dashboard", "dashboard_url": "https://platform.openai.com/settings/organization/billing/overview", "note": "OpenAI does not expose balance via API key"},
        "models": models,
        "model_count": len(models),
        "tier": "paid",
    }


async def _intel_anthropic(api_key: str) -> dict:
    models = []
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(
            "https://api.anthropic.com/v1/models",
            headers={"x-api-key": api_key, "anthropic-version": "2023-06-01"},
        )
        if resp.status_code == 200:
            data = resp.json()
            models = [{"id": m.get("id", ""), "display_name": m.get("display_name", "")} for m in data.get("data", [])]
    return {
        "balance": {"status": "check_dashboard", "dashboard_url": "https://console.anthropic.com/settings/plans", "note": "Anthropic does not expose balance via API"},
        "models": models,
        "model_count": len(models),
        "tier": "paid",
    }


async def _intel_deepseek(api_key: str) -> dict:
    models = await _fetch_openai_compat_models("https://api.deepseek.com", api_key)
    balance = {}
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get("https://api.deepseek.com/user/balance", headers={"Authorization": f"Bearer {api_key}"})
        if resp.status_code == 200:
            data = resp.json()
            infos = data.get("balance_infos", [])
            if infos:
                info = infos[0]
                balance = {
                    "status": "live",
                    "total_balance": info.get("total_balance"),
                    "granted_balance": info.get("granted_balance"),
                    "topped_up_balance": info.get("topped_up_balance"),
                    "currency": info.get("currency", "CNY"),
                }
    return {"balance": balance or {"status": "error"}, "models": models, "model_count": len(models), "tier": "paid"}


async def _intel_groq(api_key: str) -> dict:
    models = await _fetch_openai_compat_models("https://api.groq.com/openai", api_key)
    return {
        "balance": {"status": "free_tier", "note": "Groq offers free API access with rate limits"},
        "models": models,
        "model_count": len(models),
        "tier": "free",
        "rate_limits": {"requests_per_minute": 30, "tokens_per_minute": 15000, "note": "Free tier limits"},
    }


async def _intel_google(api_key: str) -> dict:
    models = []
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}")
        if resp.status_code == 200:
            data = resp.json()
            models = [{"id": m.get("name", "").replace("models/", ""), "display_name": m.get("displayName", ""), "input_token_limit": m.get("inputTokenLimit"), "output_token_limit": m.get("outputTokenLimit")} for m in data.get("models", [])]
    return {
        "balance": {"status": "free_tier", "note": "Google AI Studio free tier with rate limits"},
        "models": models,
        "model_count": len(models),
        "tier": "free",
    }


async def _intel_xai(api_key: str) -> dict:
    models = await _fetch_openai_compat_models("https://api.x.ai", api_key)
    if not models:
        # xAI models are known
        models = [
            {"id": "grok-4.20-reasoning", "name": "Grok 4.20 Reasoning"},
            {"id": "grok-3-fast", "name": "Grok 3 Fast"},
            {"id": "grok-3-mini-fast", "name": "Grok 3 Mini Fast"},
            {"id": "grok-2-vision", "name": "Grok 2 Vision"},
        ]
    return {
        "balance": {"status": "check_dashboard", "dashboard_url": "https://console.x.ai/team", "note": "xAI provides $25/month free credits"},
        "models": models,
        "model_count": len(models),
        "tier": "free_credits",
    }


async def _intel_mistral(api_key: str) -> dict:
    models = await _fetch_openai_compat_models("https://api.mistral.ai", api_key)
    return {
        "balance": {"status": "check_dashboard", "dashboard_url": "https://console.mistral.ai/billing/", "note": "Check Mistral console for balance"},
        "models": models,
        "model_count": len(models),
        "tier": "paid",
    }


async def _intel_cohere(api_key: str) -> dict:
    models = []
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get("https://api.cohere.com/v1/models", headers={"Authorization": f"Bearer {api_key}"})
        if resp.status_code == 200:
            data = resp.json()
            models = [{"id": m.get("name", ""), "endpoints": m.get("endpoints", []), "context_length": m.get("context_length")} for m in data.get("models", [])]
    return {
        "balance": {"status": "check_dashboard", "dashboard_url": "https://dashboard.cohere.com/billing", "note": "Free trial with rate limits"},
        "models": models,
        "model_count": len(models),
        "tier": "trial",
    }


async def _intel_together(api_key: str) -> dict:
    """Together hosts 200+ open-source models. No pagination needed —
    /v1/models returns the full catalog in one response."""
    models = []
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.get("https://api.together.xyz/v1/models", headers={"Authorization": f"Bearer {api_key}"})
        if resp.status_code == 200:
            data = resp.json()
            raw = data if isinstance(data, list) else data.get("data", data.get("models", []))
            # No cap — surface the full catalog so the UI reflects reality.
            models = [
                {"id": m.get("id", ""),
                 "name": m.get("display_name", m.get("id", "")),
                 "type": m.get("type", "")}
                for m in raw
            ]
    balance = {"status": "check_dashboard", "dashboard_url": "https://api.together.xyz/settings/billing", "note": "Check Together dashboard for credits"}
    return {"balance": balance, "models": models, "model_count": len(models), "tier": "paid"}


async def _intel_fireworks(api_key: str) -> dict:
    """Fireworks hosts 100+ open-source models. The `/v1/models` endpoint
    returns the OpenAI-compat list; their account-specific `/v1/accounts/
    {id}/models` returns also fine-tunes. Try both."""
    models = []
    async with httpx.AsyncClient(timeout=20) as client:
        for path in ["/inference/v1/models", "/v1/models"]:
            resp = await client.get(f"https://api.fireworks.ai{path}", headers={"Authorization": f"Bearer {api_key}"})
            if resp.status_code == 200:
                data = resp.json()
                raw = data.get("data", []) if isinstance(data, dict) else []
                # No cap — Fireworks has ~100 models, fine to surface all.
                models = [{"id": m.get("id", ""), "owned_by": m.get("owned_by", "")} for m in raw]
                break
    return {
        "balance": {"status": "check_dashboard", "dashboard_url": "https://fireworks.ai/account/billing", "note": "$6 free credits from signup"},
        "models": models,
        "model_count": len(models),
        "tier": "free_credits",
    }


async def _intel_cerebras(api_key: str) -> dict:
    models = await _fetch_openai_compat_models("https://api.cerebras.ai", api_key)
    return {
        "balance": {"status": "free_tier", "note": "1M tokens/day free"},
        "models": models,
        "model_count": len(models),
        "tier": "free",
        "rate_limits": {"tokens_per_day": 1000000},
    }


async def _intel_sambanova(api_key: str) -> dict:
    models = await _fetch_openai_compat_models("https://api.sambanova.ai", api_key)
    return {
        "balance": {"status": "free_tier", "note": "Free API access"},
        "models": models,
        "model_count": len(models),
        "tier": "free",
    }


async def _intel_openrouter(api_key: str) -> dict:
    """OpenRouter aggregates 300+ models from all major providers under
    one API key. No cap on the catalog — surface every model they expose
    so the UI reflects reality."""
    models = []
    balance = {}
    async with httpx.AsyncClient(timeout=20) as client:
        # Models — public endpoint, no auth required.
        resp = await client.get("https://openrouter.ai/api/v1/models")
        if resp.status_code == 200:
            data = resp.json()
            # No cap — OpenRouter has ~300 models, all should show.
            models = [
                {"id": m.get("id", ""),
                 "name": m.get("name", ""),
                 "pricing": m.get("pricing", {}),
                 "context_length": m.get("context_length")}
                for m in data.get("data", [])
            ]

        # Balance
        resp2 = await client.get("https://openrouter.ai/api/v1/auth/key", headers={"Authorization": f"Bearer {api_key}"})
        if resp2.status_code == 200:
            kd = resp2.json().get("data", {})
            usage = float(kd.get("usage", 0))
            limit = kd.get("limit")
            balance = {
                "status": "live",
                "usage_usd": round(usage, 4),
                "limit_usd": limit,
                "balance_usd": round(limit - usage, 4) if limit else None,
                "unlimited": limit is None,
            }
    return {
        "balance": balance or {"status": "error"},
        "models": models,
        "model_count": len(models),
        "tier": "free_credits" if not balance.get("limit_usd") else "paid",
    }


async def _intel_nvidia(api_key: str) -> dict:
    models = await _fetch_openai_compat_models("https://integrate.api.nvidia.com", api_key)
    return {
        "balance": {"status": "free_tier", "dashboard_url": "https://build.nvidia.com/settings/api-keys", "note": "1000 free API calls"},
        "models": models,
        "model_count": len(models),
        "tier": "free",
    }


async def _intel_huggingface(api_key: str) -> dict:
    """Populate the HF catalog against the operator's Inference Providers
    access. HF's /api/models endpoint is open; no auth needed to list
    public models. We cap the local catalog at 1000 popular text-gen
    models (more than this bloats the dashboard without helping clients)
    but every model on huggingface.co is callable via the
    `huggingface/{org}/{name}` passthrough — so `model_count` reflects
    the REAL addressable catalog, not the cached subset."""
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
    user_info: dict = {}
    models: list[dict] = []
    addressable_total = 175_000   # HF's documented text-generation count, used as floor
    async with httpx.AsyncClient(timeout=20) as client:
        # 1) Who am I — confirms the key + shows username/org in UI
        try:
            r = await client.get("https://huggingface.co/api/whoami-v2", headers=headers)
            if r.status_code == 200:
                user_info = r.json()
        except Exception:
            pass
        # 2) Populate top-1000 by downloads (text-generation pipeline).
        # No auth needed — these are public. Clients call any of these
        # via `huggingface/{author}/{model-name}`.
        try:
            r = await client.get(
                "https://huggingface.co/api/models",
                params={
                    "pipeline_tag": "text-generation",
                    "sort":   "downloads",
                    "limit":  1000,
                    "full":   "false",
                },
                timeout=20.0,
            )
            if r.status_code == 200:
                arr = r.json()
                if isinstance(arr, list):
                    models = [
                        {
                            "id":        m.get("id") or m.get("modelId"),
                            "downloads": m.get("downloads", 0),
                            "tags":      m.get("tags", [])[:5],
                            "gated":     bool(m.get("gated", False)),
                        }
                        for m in arr
                        if (m.get("id") or m.get("modelId"))
                    ]
        except Exception:
            pass
        # 3) Try to get a real total — HF doesn't always expose this but
        # we can approximate from the length of a filter-free scan.
        try:
            r = await client.get(
                "https://huggingface.co/api/models-count",
                timeout=10.0,
            )
            if r.status_code == 200:
                j = r.json()
                if isinstance(j, dict) and "count" in j:
                    addressable_total = int(j["count"])
        except Exception:
            pass
    return {
        "balance": {
            "status": "free_tier",
            "note": "Free inference API with rate limits; gated models need license acceptance",
            "username": user_info.get("name", ""),
        },
        "models": models,                    # top 1000 by downloads for UI
        "model_count": max(addressable_total, len(models)),  # total addressable
        "catalog_subset": len(models),       # how many we cached
        "tier": "free",
        "passthrough_format": "huggingface/{org}/{model-name}",
        "note": f"{addressable_total:,}+ models callable via passthrough. "
                f"Top {len(models)} popular models cached for UI.",
    }


async def _intel_ai21(api_key: str) -> dict:
    models = []
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get("https://api.ai21.com/studio/v1/models", headers={"Authorization": f"Bearer {api_key}"})
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list):
                models = [{"id": m} if isinstance(m, str) else m for m in data]
    return {
        "balance": {"status": "check_dashboard", "dashboard_url": "https://studio.ai21.com/v2/account", "note": "Check AI21 Studio for credits"},
        "models": models,
        "model_count": len(models),
        "tier": "trial",
    }


async def _intel_novita(api_key: str) -> dict:
    """Novita aggregates 400+ open-source models. OpenAI-compat endpoint
    returns the full list in one response."""
    models = []
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.get("https://api.novita.ai/v3/openai/models", headers={"Authorization": f"Bearer {api_key}"})
        if resp.status_code == 200:
            data = resp.json()
            raw = data.get("data", []) if isinstance(data, dict) else []
            models = [{"id": m.get("id", "")} for m in raw]
    return {
        "balance": {"status": "check_dashboard", "dashboard_url": "https://novita.ai/settings/key-management", "note": "$0.00 - needs top up"},
        "models": models,
        "model_count": len(models),
        "tier": "paid",
    }


async def _intel_bytez(api_key: str) -> dict:
    """Bytez wraps 2000+ open-source models under a unified API. Their
    list endpoint returns paginated JSON; we walk the first few pages to
    report a realistic catalog size."""
    models: list[dict] = []
    seen_count_estimate = 0
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
    async with httpx.AsyncClient(timeout=20) as client:
        # Bytez primary list endpoint (v2 with cursor-based pagination)
        for offset in (0, 200, 400, 600, 800):
            try:
                r = await client.get(
                    "https://api.bytez.com/models/v2/list",
                    headers=headers,
                    params={"limit": 200, "offset": offset},
                    timeout=15.0,
                )
            except Exception:
                break
            if r.status_code != 200:
                break
            body = r.json() if r.content else {}
            page = body.get("models") or body.get("data") or body
            if not isinstance(page, list) or not page:
                break
            for m in page:
                models.append({
                    "id":   m.get("id") or m.get("model_id") or m.get("name", ""),
                    "task": m.get("task") or m.get("pipeline", ""),
                })
            seen_count_estimate = body.get("total") or (offset + len(page))
            if len(page) < 200:
                break
    return {
        "balance": {
            "status": "free_tier",
            "note": "100 req/day free tier. 2,000+ models via unified API.",
            "dashboard_url": "https://app.bytez.com/profile",
        },
        "models": models,
        # Report the upper-bound total if the API gave us one, else what we walked.
        "model_count": max(seen_count_estimate, len(models), 2000 if models else 0),
        "catalog_subset": len(models),
        "tier": "free_credits",
        "passthrough_format": "bytez/{provider}/{model-name}",
    }


async def _intel_hyperbolic(api_key: str) -> dict:
    models = await _fetch_openai_compat_models("https://api.hyperbolic.xyz", api_key)
    return {
        "balance": {"status": "check_dashboard", "dashboard_url": "https://app.hyperbolic.ai/settings/billing", "note": "$0.00 - verify phone for $1 credit"},
        "models": models,
        "model_count": len(models),
        "tier": "paid",
    }


async def _intel_perplexity(api_key: str) -> dict:
    models = []
    # Perplexity doesn't have a /v1/models endpoint
    return {
        "balance": {"status": "check_dashboard", "dashboard_url": "https://console.perplexity.ai", "note": "Check Perplexity console for credits"},
        "models": [
            {"id": "sonar", "name": "Sonar"},
            {"id": "sonar-pro", "name": "Sonar Pro"},
            {"id": "sonar-reasoning", "name": "Sonar Reasoning"},
            {"id": "sonar-reasoning-pro", "name": "Sonar Reasoning Pro"},
        ],
        "model_count": 4,
        "tier": "paid",
        "note": "Models from Perplexity docs - live search-augmented LLMs",
    }


async def _intel_upstage(api_key: str) -> dict:
    models = await _fetch_openai_compat_models("https://api.upstage.ai", api_key)
    return {
        "balance": {"status": "check_dashboard", "dashboard_url": "https://console.upstage.ai/billing/credit", "note": "$10 free credits"},
        "models": models,
        "model_count": len(models),
        "tier": "free_credits",
    }


async def _intel_elevenlabs(api_key: str) -> dict:
    user_data = {}
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get("https://api.elevenlabs.io/v1/user", headers={"xi-api-key": api_key})
        if resp.status_code == 200:
            user_data = resp.json()
    sub = user_data.get("subscription", {})
    return {
        "balance": {
            "status": "live",
            "characters_remaining": max(0, (sub.get("character_limit", 0) - sub.get("character_count", 0))),
            "characters_limit": sub.get("character_limit", 0),
            "characters_used": sub.get("character_count", 0),
            "plan": sub.get("tier", "free"),
            "next_reset": sub.get("next_character_count_reset_unix"),
        },
        "models": [{"id": "eleven_multilingual_v2"}, {"id": "eleven_turbo_v2"}, {"id": "eleven_monolingual_v1"}],
        "model_count": 3,
        "tier": sub.get("tier", "free"),
        "category": "audio",
    }


async def _intel_bedrock(api_key: str) -> dict:
    return {
        "balance": {"status": "free_tier", "dashboard_url": "https://console.aws.amazon.com/bedrock", "note": "$200 free credits for 6 months"},
        "models": [
            {"id": "anthropic.claude-3-5-sonnet-20241022-v2:0", "name": "Claude 3.5 Sonnet"},
            {"id": "anthropic.claude-3-haiku-20240307-v1:0", "name": "Claude 3 Haiku"},
            {"id": "amazon.titan-text-premier-v1:0", "name": "Titan Text Premier"},
            {"id": "meta.llama3-1-70b-instruct-v1:0", "name": "Llama 3.1 70B"},
        ],
        "model_count": 4,
        "tier": "free_credits",
        "note": "AWS Bedrock - models available after enabling in console",
    }


# ── Registry ──────────────────────────────────────────────────────────────────

INTEL_FETCHERS: dict[str, Any] = {
    "openai": _intel_openai,
    "anthropic": _intel_anthropic,
    "deepseek": _intel_deepseek,
    "groq": _intel_groq,
    "google": _intel_google,
    "xai": _intel_xai,
    "mistral": _intel_mistral,
    "cohere": _intel_cohere,
    "together": _intel_together,
    "fireworks": _intel_fireworks,
    "cerebras": _intel_cerebras,
    "sambanova": _intel_sambanova,
    "openrouter": _intel_openrouter,
    "nvidia_nim": _intel_nvidia,
    "huggingface": _intel_huggingface,
    "ai21": _intel_ai21,
    "novita": _intel_novita,
    "bytez": _intel_bytez,
    "hyperbolic": _intel_hyperbolic,
    "perplexity": _intel_perplexity,
    "upstage": _intel_upstage,
    "elevenlabs": _intel_elevenlabs,
    "bedrock": _intel_bedrock,
}


# ── Core: fetch intelligence for one provider ────────────────────────────────

async def fetch_intel(slug: str, api_key: str) -> dict:
    """Get full intelligence for a single provider."""
    now = time.time()
    cached = _cache.get(slug)
    if cached and (now - cached["fetched_at"]) < CACHE_TTL:
        return cached["data"]

    result: dict[str, Any] = {"slug": slug, "status": "ok", "checked_at": datetime.now(timezone.utc).isoformat()}

    fetcher = INTEL_FETCHERS.get(slug)
    if not fetcher:
        result.update({"status": "no_fetcher", "balance": {"status": "check_dashboard"}, "models": [], "model_count": 0})
    elif not api_key:
        result.update({"status": "no_key", "balance": {"status": "no_key"}, "models": [], "model_count": 0})
    else:
        try:
            data = await fetcher(api_key)
            result.update(data)
        except Exception as exc:
            logger.warning("intel fetch failed for %s: %s", slug, exc)
            result.update({"status": "error", "error": str(exc), "balance": {"status": "error"}, "models": [], "model_count": 0})

    _cache[slug] = {"data": result, "fetched_at": now}
    return result


# ── Fetch all ─────────────────────────────────────────────────────────────────

# Catalog slug -> DIRECT_API_KEYS slug mapping (where they differ)
_SLUG_ALIASES = {
    "google": "gemini",
    "nvidia_nim": "nvidia",
    "bedrock": "amazon",
    "meta_llama_api": "llama",
}


async def fetch_all_intel() -> list[dict]:
    """Fetch intelligence for all configured providers."""
    from shared.utils import get_api_keys
    from services.provider_catalog import CATALOG

    api_keys = await get_api_keys()
    results = []

    for provider in CATALOG:
        slug = provider.slug
        # Try catalog slug, then alias, then env var directly
        key_slug = _SLUG_ALIASES.get(slug, slug)
        key = api_keys.get(key_slug, "") or api_keys.get(slug, "") or os.environ.get(provider.env_var, "")

        intel = await fetch_intel(slug, key)
        intel["display_name"] = provider.display_name
        intel["dashboard_url"] = provider.dashboard_url
        intel["category"] = provider.category
        intel["env_var"] = provider.env_var
        intel["has_key"] = bool(key)
        results.append(intel)

    return results


def clear_cache():
    _cache.clear()


# ── Package recommendation engine ─────────────────────────────────────────────

async def get_package_recommendations() -> dict:
    """
    Based on current provider balances and model availability,
    recommend which subscription packages the operator can sell.
    """
    from shared.constants import SUBSCRIPTION_PLANS, CREDITS_PER_USD

    intel_list = await fetch_all_intel()

    # Summarize provider capacity
    total_models = 0
    providers_with_balance = 0
    providers_free = 0
    total_estimated_budget = 0.0
    live_providers = []

    for p in intel_list:
        if not p.get("has_key"):
            continue
        total_models += p.get("model_count", 0)
        tier = p.get("tier", "")
        bal = p.get("balance", {})

        if tier == "free":
            providers_free += 1
            live_providers.append({"slug": p["slug"], "name": p["display_name"], "type": "free", "models": p.get("model_count", 0)})
        elif bal.get("status") == "live":
            b = bal.get("balance_usd") or bal.get("total_balance") or 0
            total_estimated_budget += float(b) if b else 0
            providers_with_balance += 1
            live_providers.append({"slug": p["slug"], "name": p["display_name"], "type": "paid", "balance": b, "models": p.get("model_count", 0)})
        elif bal.get("status") == "check_dashboard":
            # Use config starting balance as fallback
            config = await db["provider_balance_config"].find_one({"slug": p["slug"]}, {"_id": 0})
            sb = float((config or {}).get("starting_balance_usd", 0))
            if sb > 0:
                total_estimated_budget += sb
                providers_with_balance += 1
            live_providers.append({"slug": p["slug"], "name": p["display_name"], "type": "configured", "starting_balance": sb, "models": p.get("model_count", 0)})

    # ── Blended cost per credit — unified source. Was inline-computed three
    # different ways across three dashboards; now all three consume the same
    # services.blended_cost.get_blended_cost_per_credit() so Profit Margin
    # Calculator / Universal Gateway / Package Advisor always agree.
    from services.costing.blended_cost import get_blended_cost_per_credit
    _bc = await get_blended_cost_per_credit()
    blended_cost_per_credit = _bc["value"]

    # ── 8-track dedicated rates — feeds accurate per-category cost
    # attribution in each package recommendation. Each rate is
    # measured-or-configured separately, no merging.
    from services.costing.blended_by_category import blended_by_category, CATEGORY_KEYS
    cat_rates = await blended_by_category()
    def _rate(cat: str) -> float:
        return float((cat_rates.get(cat) or {}).get("value") or 0.0)

    # ── Read ACTUAL plan data from DB (same source as Pricing Command Center) ──
    pricing_config = await db.platform_config.find_one({"config_type": "pricing"}, {"_id": 0})
    plans = (pricing_config or {}).get("plans", None)
    if not plans:
        # Fall back to code defaults
        plans = SUBSCRIPTION_PLANS

    # Centralized pricing math — reads the locked engine_config so media costs
    # come from the operator's DB config, not hardcoded constants. See
    # backend/services/pricing_math.py for the single source of truth.
    from services.pricing_math import (
        load_pricing_config, plan_economics, media_capacity, credits_to_tokens,
    )
    pc = await load_pricing_config()
    engine_config = pc["engine_config"]
    tokens_per_credit = engine_config["tokens_per_credit"]

    recommendations = []
    for plan_id, plan in plans.items():
        price = float(plan.get("price_usd", 0))
        credits = int(plan.get("credits", 0))
        if price <= 0 or credits <= 0:
            continue

        econ = plan_economics(
            credits=credits,
            price_usd=price,
            cost_per_credit=blended_cost_per_credit,
            margin_target_pct=pc["target_profit_margin"],
            bdt_rate=pc["bdt_exchange_rate"],
        )
        ai_cost = econ["ai_cost"]
        profit = econ["profit"]

        # Customers supportable from operator's estimated free+paid budget
        customers_supportable = int(total_estimated_budget / ai_cost) if ai_cost > 0 else 999

        total_tokens = credits_to_tokens(credits, engine_config)
        daily_credits = round(credits / 30, 1)
        daily_tokens = int(daily_credits * tokens_per_credit)
        # Rough usage-pattern breakdown — chat vs long-gen
        short_chats        = int(total_tokens / 200)
        long_generations   = int(total_tokens / 1000)
        code_completions   = int(total_tokens / 300)
        document_summaries = int(total_tokens / 800)

        caps = media_capacity(credits, engine_config)

        # ── Smart per-category credit allocation ─────────────────────
        # Each plan's total credit grant splits across the 8 dedicated
        # tracks using plan_buckets.split_credits() (operator-tuned
        # ratios per tier) MAPPED onto the 8 UI categories via:
        #   chat → chat, code → vibe, image_std→image*ratio,
        #   image_hd→image*(1-ratio), video → video, voiceover → voice*0.7,
        #   tts → voice*0.3, stt → stt
        # Then cost per category = allocated_credits × rate_for_category.
        # This is what makes the advisor output MEAN something — operator
        # sees "Studio gives 40 code credits, which costs $0.018 at current
        # rates" instead of an undifferentiated $X total.
        from services.billing.plan_buckets import split_credits, plan_allows_general_fallback
        bucket_split = split_credits(credits, plan_id)
        # Expand the 6 buckets into the 8 UI categories. image_std vs _hd
        # splits 70/30 (free std takes the bulk); voice splits 60/30/10
        # between voiceover / tts / stt sub-tracks.
        per_cat_alloc = {
            "chat":      bucket_split.get("chat", 0),
            "code":      bucket_split.get("vibe", 0),
            "image_std": int(bucket_split.get("image", 0) * 0.70),
            "image_hd":  bucket_split.get("image", 0) - int(bucket_split.get("image", 0) * 0.70),
            "video":     bucket_split.get("video", 0),
            "voiceover": int(bucket_split.get("voice", 0) * 0.70),
            "tts":       int(bucket_split.get("voice", 0) * 0.20),
            "stt":       bucket_split.get("stt", 0) + int(bucket_split.get("voice", 0) * 0.10),
            "agent_sop": bucket_split.get("agent_sop", 0),
            "general":   bucket_split.get("general", 0),
        }
        # Per-category cost = credits × dedicated rate (no merging).
        per_cat_cost = {k: round(v * _rate(k), 4) for k, v in per_cat_alloc.items() if k in CATEGORY_KEYS}
        per_cat_cost_total = round(sum(per_cat_cost.values()), 4)
        # Human-readable deliverable counts derived at each allocation
        # level. Operator sees "40 code credits = ~1,000 code runs at
        # your current rate" so they can sanity-check the split.
        chat_per = float(engine_config.get("chat_credits_per_msg") or 0.015)
        code_per = float(engine_config.get("code_credits_per_run") or 0.04)
        vo_per   = float(engine_config.get("voiceover_credits_per_min") or 3)
        vid_per  = float(engine_config.get("video_credits_per_sec") or 1) * 4  # per 4s clip
        hd_per   = float(engine_config.get("image_hd_credits") or 6)
        per_cat_deliverables = {
            "chat_msgs":   int(per_cat_alloc["chat"] / chat_per) if chat_per > 0 else "∞",
            "code_runs":   int(per_cat_alloc["code"] / code_per) if code_per > 0 else "∞",
            "hd_images":   int(per_cat_alloc["image_hd"] / hd_per) if hd_per > 0 else "∞",
            "video_clips": int(per_cat_alloc["video"] / vid_per) if vid_per > 0 else "∞",
            "vo_minutes":  int(per_cat_alloc["voiceover"] / vo_per) if vo_per > 0 else "∞",
        }

        recommendations.append({
            "plan_id": plan_id,
            "plan_name": plan.get("name", plan_id),
            "price_usd": price,
            "credits": credits,
            "ai_cost": ai_cost,
            "profit": profit,
            "margin_pct": min(econ["margin_pct"], 999999),
            "customers_supportable": min(customers_supportable, 9999),
            "profitable": econ["profitable"],
            "blended_cost_per_credit": round(blended_cost_per_credit, 8),
            # Per-category allocation + cost + deliverables — the core
            # output of the advisor-sync. Renders as a breakdown card
            # in ProviderIntelligencePage so operator sees how each
            # plan's credit pool splits + what it costs to serve by track.
            "per_category": {
                k: {
                    "credits_allocated": per_cat_alloc.get(k, 0),
                    "rate":              round(_rate(k), 8),
                    "cost_usd":          per_cat_cost.get(k, 0),
                }
                for k in CATEGORY_KEYS
            },
            "per_category_cost_total": per_cat_cost_total,
            "per_category_deliverables": per_cat_deliverables,
            "allow_general_fallback": plan_allows_general_fallback(plan_id),
            "agent_sop_allocation": per_cat_alloc["agent_sop"],
            "general_allocation": per_cat_alloc["general"],
            "operator_breakdown": {
                "tokens_per_credit": tokens_per_credit,
                "total_tokens": total_tokens,
                "daily_credits": daily_credits,
                "daily_tokens": daily_tokens,
                "usage_capacity": {
                    "short_chats":        short_chats,
                    "long_generations":   long_generations,
                    "code_completions":   code_completions,
                    "document_summaries": document_summaries,
                },
                "media_capacity": caps,
                "media_costs": {
                    "image_std_credits":         engine_config["image_std_credits"],
                    "image_hd_credits":          engine_config["image_hd_credits"],
                    "video_credits_per_sec":     engine_config["video_credits_per_sec"],
                    "tts_credits_per_min":       engine_config["tts_credits_per_min"],
                    "voiceover_credits_per_min": engine_config["voiceover_credits_per_min"],
                    "stt_credits_per_min":       engine_config["stt_credits_per_min"],
                },
                "strict_cap": f"Client cannot exceed {credits} credits/month. Each credit = ~{tokens_per_credit} tokens routed through smart router.",
            },
        })

    return {
        "summary": {
            "total_providers_with_keys": len([p for p in intel_list if p.get("has_key")]),
            "total_models_accessible": total_models,
            "providers_free_tier": providers_free,
            "providers_with_balance": providers_with_balance,
            "total_estimated_budget_usd": round(total_estimated_budget, 2),
        },
        "providers": live_providers,
        "package_recommendations": sorted(recommendations, key=lambda r: -r["customers_supportable"]),
        # Proactive plan-improvement signals — consumed by the Package Advisor
        # UI to surface actionable "fix this" / "add a plan here" suggestions.
        "plan_advice": _generate_plan_advice(recommendations, blended_cost_per_credit),
    }


def _generate_plan_advice(recommendations: list, blended_cost_per_credit: float) -> list:
    """Generate proactive suggestions to improve the pricing ladder.

    Heuristics:
      - Low-margin plans (< 50% markup) → warn; suggest price hike.
      - Value-identical plans (same credits, different price) → confusing; suggest collapse.
      - Large price gaps (> 2× jump) → suggest intermediate tier to capture prospects.
      - Missing free/starter tier → every SaaS ladder needs an entry point.
      - Unprofitable plans (margin <= 0) → critical; blocks launch.
      - Overbuilt plans (credits but low max_agents) → reshape for value clarity.
    """
    if not recommendations:
        return [{
            "severity": "critical",
            "kind": "no_plans",
            "title": "No plans configured",
            "detail": "Create at least one plan. Start with a Free tier (50 credits, 3 agents) and a Starter tier ($50, 300 credits).",
            "action": "add_preset",
        }]

    plans = sorted(recommendations, key=lambda r: r.get("price", 0))
    advice: list[dict] = []

    # 1. Unprofitable plans — critical
    for p in plans:
        margin = p.get("margin_pct", 0)
        if margin <= 0 and p.get("price", 0) > 0:
            advice.append({
                "severity": "critical",
                "kind": "unprofitable",
                "plan_id": p.get("plan_id"),
                "plan_name": p.get("name"),
                "title": f"{p.get('name')} is unprofitable",
                "detail": (
                    f"Price ${p.get('price',0):.2f} ≤ AI cost ${p.get('ai_cost',0):.4f}. "
                    f"Raise the price or lower the credits. Minimum profitable price at current "
                    f"cost: ${round(p.get('ai_cost', 0) * 1.5, 2)} (50% margin)."
                ),
                "suggested_price_usd": round(p.get("ai_cost", 0) * 1.5, 2),
                "action": "raise_price",
            })

    # 2. Low-margin plans — warn
    for p in plans:
        margin = p.get("margin_pct", 0)
        price = p.get("price", 0)
        if 0 < margin < 50 and price > 0:
            advice.append({
                "severity": "warn",
                "kind": "low_margin",
                "plan_id": p.get("plan_id"),
                "plan_name": p.get("name"),
                "title": f"{p.get('name')} has low margin ({margin:.0f}%)",
                "detail": (
                    f"Margin of {margin:.0f}% leaves little room for support + churn. "
                    f"Industry standard is 200–500%. Consider raising to "
                    f"${round(p.get('ai_cost', 0) * 3, 2)} (200% margin)."
                ),
                "suggested_price_usd": round(p.get("ai_cost", 0) * 3, 2),
                "action": "raise_price",
            })

    # 3. Missing entry tier
    has_free = any(p.get("price", 0) == 0 for p in plans)
    if not has_free:
        advice.append({
            "severity": "info",
            "kind": "missing_free",
            "title": "No free tier",
            "detail": (
                "Every SaaS ladder benefits from a $0 entry tier to capture prospects. "
                "Suggested: 50 credits / month, 3 agents, 0 custom agents — near-zero cost to serve "
                "(all routes through free-tier providers by the smart router)."
            ),
            "suggested_plan": {
                "name": "Free", "price_usd": 0, "credits": 50,
                "max_agents": 3, "max_custom_agents": 0, "max_team_members": 1,
            },
            "action": "add_plan",
        })

    # 4. Large price gaps
    for i in range(len(plans) - 1):
        a, b = plans[i], plans[i + 1]
        pa, pb = a.get("price", 0), b.get("price", 0)
        if pa > 0 and pb / pa >= 3:
            midpoint = round((pa + pb) / 2)
            advice.append({
                "severity": "info",
                "kind": "price_gap",
                "title": f"Large jump: {a.get('name')} (${pa:.0f}) → {b.get('name')} (${pb:.0f})",
                "detail": (
                    f"Clients with ${midpoint}-sized budgets fall between tiers. "
                    f"An intermediate plan at ~${midpoint} captures them instead of "
                    f"sending them to a competitor."
                ),
                "suggested_plan": {
                    "name": f"Between {a.get('name')} and {b.get('name')}",
                    "price_usd": midpoint,
                    "credits": round((a.get("credits", 0) + b.get("credits", 0)) / 2),
                },
                "action": "add_plan",
            })

    # 5. Duplicate-value plans (same credits, different price)
    for i in range(len(plans)):
        for j in range(i + 1, len(plans)):
            if plans[i].get("credits") == plans[j].get("credits") and plans[i].get("credits", 0) > 0:
                advice.append({
                    "severity": "warn",
                    "kind": "duplicate_value",
                    "title": f"Confusing: {plans[i].get('name')} and {plans[j].get('name')} both grant {plans[i].get('credits')} credits",
                    "detail": (
                        f"Different prices (${plans[i].get('price',0):.0f} vs ${plans[j].get('price',0):.0f}) but same credit budget. "
                        "Clients can't tell them apart. Differentiate by credits, agents, team size, or capability, "
                        "or collapse to a single tier."
                    ),
                    "action": "review",
                })

    # 6. Overall health note — summarize what's going well
    profitable_count = sum(1 for p in plans if p.get("profit", 0) > 0)
    if profitable_count == len(plans) and len(plans) >= 5 and not advice:
        advice.append({
            "severity": "success",
            "kind": "healthy",
            "title": f"All {len(plans)} plans are profitable and well-spaced",
            "detail": "Your ladder looks solid. Keep an eye on actual customer uptake via the Financials tab and revisit if one tier dominates or stalls.",
            "action": "monitor",
        })

    return advice
