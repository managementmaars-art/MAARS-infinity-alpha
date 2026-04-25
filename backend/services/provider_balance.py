"""
External provider balance & quota monitoring for MAARS operators.

Three tiers:
  Tier 1 — Real balance API exists (DeepSeek, OpenRouter, ElevenLabs, Together)
  Tier 2 — Estimate from MAARS usage_logs minus operator-set starting balance
  Tier 3 — Free/unlimited tier (Groq, Cerebras, SambaNova, Google free key)

Results are cached (5 min TTL) and snapshotted to MongoDB for burn-rate charts.
"""
from __future__ import annotations

import logging
import os
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import httpx

from db import db

logger = logging.getLogger(__name__)

BALANCE_COLLECTION = "provider_balance_history"
CONFIG_COLLECTION = "provider_balance_config"

# In-memory cache: slug -> {data, fetched_at}
_cache: dict[str, dict] = {}
CACHE_TTL = 300  # 5 minutes

# ── Provider tier classification ─────────────────────────────────────────────

from shared.free_providers import FREE_PROVIDERS as FREE_TIER_PROVIDERS

# Providers with real balance/usage APIs
TIER1_PROVIDERS = {
    "deepseek", "openrouter", "elevenlabs", "together",
}

# Everything else — estimate from usage_logs
# (openai, anthropic, mistral, cohere, xai, fireworks, ai21, nvidia_nim,
#  novita, hyperbolic, perplexity, upstage, etc.)


# ── Tier 1: Real balance API fetchers ────────────────────────────────────────

async def _fetch_deepseek_balance(api_key: str) -> dict:
    """DeepSeek: GET /user/balance returns available + total."""
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            "https://api.deepseek.com/user/balance",
            headers={"Authorization": f"Bearer {api_key}"},
        )
        resp.raise_for_status()
        data = resp.json()
        info = data.get("balance_infos", [{}])[0] if data.get("balance_infos") else {}
        available = float(info.get("total_balance", 0))
        return {"balance_usd": round(available, 4), "source": "api", "currency": "CNY"}


async def _fetch_openrouter_balance(api_key: str) -> dict:
    """OpenRouter: GET /api/v1/auth/key returns usage and limit."""
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            "https://openrouter.ai/api/v1/auth/key",
            headers={"Authorization": f"Bearer {api_key}"},
        )
        resp.raise_for_status()
        data = resp.json().get("data", {})
        usage = float(data.get("usage", 0))
        limit = data.get("limit")  # None means unlimited
        balance = round(limit - usage, 4) if limit else None
        return {
            "balance_usd": balance,
            "usage_usd": round(usage, 4),
            "limit_usd": limit,
            "source": "api",
            "unlimited": limit is None,
        }


async def _fetch_elevenlabs_balance(api_key: str) -> dict:
    """ElevenLabs: GET /v1/user returns character usage/limits."""
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            "https://api.elevenlabs.io/v1/user",
            headers={"xi-api-key": api_key},
        )
        resp.raise_for_status()
        data = resp.json()
        sub = data.get("subscription", {})
        limit = sub.get("character_limit", 0)
        used = sub.get("character_count", 0)
        remaining = max(0, limit - used)
        return {
            "characters_remaining": remaining,
            "characters_limit": limit,
            "characters_used": used,
            "tier": sub.get("tier", "free"),
            "source": "api",
        }


async def _fetch_together_balance(api_key: str) -> dict:
    """Together AI: Try multiple billing endpoints."""
    async with httpx.AsyncClient(timeout=10) as client:
        # Try /v1/billing/credits first, then /billing
        for path in ["/v1/billing/credits", "/v1/billing", "/billing"]:
            try:
                resp = await client.get(
                    f"https://api.together.xyz{path}",
                    headers={"Authorization": f"Bearer {api_key}"},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    balance = float(data.get("total_balance", data.get("balance", 0)))
                    return {"balance_usd": round(balance, 4), "source": "api"}
            except Exception:
                continue
        # Fallback to estimation
        raise Exception("No billing endpoint available")


async def _fetch_moonshot_balance(api_key: str) -> dict:
    """Moonshot (intl Kimi Open Platform): GET /v1/users/me/balance.
    Returns {available_balance, voucher_balance, cash_balance}."""
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            "https://api.moonshot.ai/v1/users/me/balance",
            headers={"Authorization": f"Bearer {api_key}"},
        )
        resp.raise_for_status()
        d = resp.json().get("data", {})
        return {
            "balance_usd": round(float(d.get("available_balance", 0)), 4),
            "cash_balance_usd": round(float(d.get("cash_balance", 0)), 4),
            "voucher_balance_usd": round(float(d.get("voucher_balance", 0)), 4),
            "source": "api",
        }


TIER1_FETCHERS = {
    "deepseek": _fetch_deepseek_balance,
    "openrouter": _fetch_openrouter_balance,
    "elevenlabs": _fetch_elevenlabs_balance,
    "together": _fetch_together_balance,
    "moonshot": _fetch_moonshot_balance,
}


# ── Tier 2: Estimate from MAARS usage logs ───────────────────────────────────

async def _estimate_from_logs(slug: str) -> dict:
    """
    Estimate remaining balance by subtracting total internal cost from
    operator-configured starting balance.
    """
    config = await db[CONFIG_COLLECTION].find_one(
        {"slug": slug}, {"_id": 0}
    )
    starting_balance = float((config or {}).get("starting_balance_usd", 0))

    # Sum all estimated_cost_usd for this provider from usage_logs
    pipeline = [
        {"$match": {"provider": slug}},
        {"$group": {"_id": None, "total_cost": {"$sum": "$estimated_cost_usd"}}},
    ]
    total_cost = 0.0
    async for row in db.usage_logs.aggregate(pipeline):
        total_cost = float(row.get("total_cost", 0))

    remaining = round(starting_balance - total_cost, 4)
    return {
        "balance_usd": max(0, remaining),
        "starting_balance_usd": starting_balance,
        "total_spent_usd": round(total_cost, 4),
        "source": "estimated",
        "needs_starting_balance": starting_balance == 0,
    }


# ── Core: fetch balance for one provider ─────────────────────────────────────

async def fetch_balance(slug: str, api_key: str = "") -> dict:
    """Get balance info for a single provider. Uses cache."""
    now = time.time()

    # Check cache
    cached = _cache.get(slug)
    if cached and (now - cached["fetched_at"]) < CACHE_TTL:
        return cached["data"]

    result: dict[str, Any] = {"slug": slug, "status": "ok"}

    try:
        if slug in FREE_TIER_PROVIDERS:
            result.update({
                "tier": "free",
                "source": "static",
                "balance_usd": None,
                "note": "Free tier — no balance tracking needed",
            })
        elif slug in TIER1_FETCHERS and api_key:
            fetcher = TIER1_FETCHERS[slug]
            try:
                data = await fetcher(api_key)
                result.update(data)
                result["tier"] = "tier1_api"
            except Exception:
                # Tier 1 failed, fall back to Tier 2 estimation
                data = await _estimate_from_logs(slug)
                result.update(data)
                result["tier"] = "tier2_estimated"
        else:
            data = await _estimate_from_logs(slug)
            result.update(data)
            result["tier"] = "tier2_estimated"
    except Exception as exc:
        logger.warning("balance check failed for %s: %s", slug, exc)
        result.update({
            "status": "error",
            "error": str(exc),
            "tier": "unknown",
        })

    result["checked_at"] = datetime.now(timezone.utc).isoformat()
    _cache[slug] = {"data": result, "fetched_at": now}
    return result


# ── Fetch all provider balances ──────────────────────────────────────────────

async def fetch_all_balances() -> list[dict]:
    """Query balances for all configured providers."""
    from shared.utils import get_api_keys
    from services.provider_catalog import CATALOG

    api_keys = await get_api_keys()
    results = []

    for provider in CATALOG:
        slug = provider.slug
        # Get the API key for this provider
        key = api_keys.get(slug, "") or api_keys.get(provider.env_var, "")
        if not key:
            # Try direct env var
            key = os.environ.get(provider.env_var, "")

        if not key and slug not in FREE_TIER_PROVIDERS:
            results.append({
                "slug": slug,
                "display_name": provider.display_name,
                "status": "no_key",
                "tier": "unconfigured",
                "checked_at": datetime.now(timezone.utc).isoformat(),
            })
            continue

        balance = await fetch_balance(slug, key)
        balance["display_name"] = provider.display_name
        balance["dashboard_url"] = provider.dashboard_url
        balance["category"] = provider.category
        results.append(balance)

    return results


# ── Snapshot balances to MongoDB for history/burn-rate ────────────────────────

async def snapshot_balances() -> int:
    """Take a point-in-time snapshot of all balances. Called periodically."""
    balances = await fetch_all_balances()
    now = datetime.now(timezone.utc).isoformat()
    count = 0

    for b in balances:
        if b.get("status") == "no_key":
            continue
        doc = {
            "slug": b["slug"],
            "balance_usd": b.get("balance_usd"),
            "source": b.get("source", "unknown"),
            "snapshot_at": now,
            "raw": {k: v for k, v in b.items() if k not in ("slug", "display_name", "dashboard_url")},
        }
        await db[BALANCE_COLLECTION].insert_one(doc)
        count += 1

    return count


# ── Balance history for burn-rate charts ──────────────────────────────────────

async def get_balance_history(slug: str, days: int = 30) -> list[dict]:
    """Get historical balance snapshots for a provider."""
    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    cursor = db[BALANCE_COLLECTION].find(
        {"slug": slug, "snapshot_at": {"$gte": since}},
        {"_id": 0, "slug": 1, "balance_usd": 1, "snapshot_at": 1},
    ).sort("snapshot_at", 1)
    return [doc async for doc in cursor]


# ── Alerts: providers below threshold ─────────────────────────────────────────

async def get_alerts() -> list[dict]:
    """Return providers whose balance is below their configured threshold."""
    balances = await fetch_all_balances()
    alerts = []

    for b in balances:
        if b.get("tier") in ("free", "unconfigured") or b.get("status") == "no_key":
            continue

        balance = b.get("balance_usd")
        if balance is None:
            continue

        # Get threshold for this provider (default $2)
        config = await db[CONFIG_COLLECTION].find_one(
            {"slug": b["slug"]}, {"_id": 0}
        )
        threshold = float((config or {}).get("alert_threshold_usd", 2.0))

        if balance < threshold:
            alerts.append({
                "slug": b["slug"],
                "display_name": b.get("display_name", b["slug"]),
                "balance_usd": balance,
                "threshold_usd": threshold,
                "dashboard_url": b.get("dashboard_url", ""),
                "severity": "critical" if balance < 0.5 else "warning",
            })

    return sorted(alerts, key=lambda a: a.get("balance_usd", 0))


# ── Burn rate calculation ─────────────────────────────────────────────────────

async def get_burn_rates() -> dict[str, dict]:
    """Calculate daily burn rate and days-until-empty per provider."""
    balances = await fetch_all_balances()
    rates = {}

    for b in balances:
        slug = b["slug"]
        balance = b.get("balance_usd")
        if balance is None or b.get("tier") in ("free", "unconfigured"):
            continue

        # Get balance from 7 days ago
        week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
        old_snap = await db[BALANCE_COLLECTION].find_one(
            {"slug": slug, "snapshot_at": {"$lte": week_ago}},
            {"_id": 0, "balance_usd": 1},
            sort=[("snapshot_at", -1)],
        )

        if old_snap and old_snap.get("balance_usd") is not None:
            old_balance = float(old_snap["balance_usd"])
            daily_burn = round((old_balance - balance) / 7, 4)
            days_left = round(balance / daily_burn, 1) if daily_burn > 0 else None
        else:
            daily_burn = None
            days_left = None

        rates[slug] = {
            "display_name": b.get("display_name", slug),
            "balance_usd": balance,
            "daily_burn_usd": daily_burn,
            "days_until_empty": days_left,
            "dashboard_url": b.get("dashboard_url", ""),
        }

    return rates


# ── Config: set starting balance / thresholds ─────────────────────────────────

async def set_provider_config(
    slug: str,
    starting_balance_usd: Optional[float] = None,
    alert_threshold_usd: Optional[float] = None,
) -> dict:
    """Set or update balance config for a provider."""
    update: dict[str, Any] = {"slug": slug, "updated_at": datetime.now(timezone.utc).isoformat()}
    if starting_balance_usd is not None:
        update["starting_balance_usd"] = starting_balance_usd
    if alert_threshold_usd is not None:
        update["alert_threshold_usd"] = alert_threshold_usd

    await db[CONFIG_COLLECTION].update_one(
        {"slug": slug}, {"$set": update}, upsert=True
    )
    return update


async def get_all_configs() -> list[dict]:
    """Get all provider balance configs."""
    cursor = db[CONFIG_COLLECTION].find({}, {"_id": 0})
    return [doc async for doc in cursor]


# ── Clear cache (for force refresh) ──────────────────────────────────────────

def clear_cache():
    """Clear the in-memory balance cache."""
    _cache.clear()
