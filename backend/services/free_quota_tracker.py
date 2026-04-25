"""Per-provider free-tier quota tracker.

Most providers offer generous free quotas. We want to **fully exhaust
every free quota before any paid provider sees a call**. Without
tracking, the router has no signal and may send calls to a paid provider
while Groq still has 14k free requests left today.

This module persists one row per (provider, day) and exposes:

    has_quota(provider)   -> bool   (fast check for the router)
    record(provider, tokens=?)      (called after a successful call)
    snapshot_caps()        -> dict  (admin: see utilisation per provider)

Quotas below are current as of 2026-04 and are configured conservatively;
operator can override any of them in env to stay inside the real cap.
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


# ── Quotas ──────────────────────────────────────────────────────────
# Keep these conservative — better to leave 5% unused than to 429.
# Format: daily request cap + (optional) daily token cap.

@dataclass
class Quota:
    requests_per_day: int | None = None
    tokens_per_day:   int | None = None


PROVIDER_QUOTAS: dict[str, Quota] = {
    "groq":       Quota(requests_per_day=14_400),             # 14,400 req/day free
    "gemini":     Quota(requests_per_day=1_500),              # 15 rpm * 60 * 24 = 21,600 theoretical, use a soft cap
    "google":     Quota(requests_per_day=1_500),              # alias
    "cerebras":   Quota(tokens_per_day=30_000_000),           # 30M tokens/month / ~30 = 1M/day
    "together":   Quota(requests_per_day=100),                # generous free-credit signup; treat as 100/day trickle
    "fireworks":  Quota(requests_per_day=500),                # free tier exists but rate-limited
    "sambanova":  Quota(requests_per_day=500),
    "nvidia_nim": Quota(requests_per_day=1_000),
    "openrouter_free": Quota(requests_per_day=200),
}

# Env overrides — `FREE_QUOTA_GROQ_REQ=20000` etc.
for prov in list(PROVIDER_QUOTAS.keys()):
    r_env = os.environ.get(f"FREE_QUOTA_{prov.upper()}_REQ")
    t_env = os.environ.get(f"FREE_QUOTA_{prov.upper()}_TOK")
    q = PROVIDER_QUOTAS[prov]
    if r_env and r_env.isdigit():
        q.requests_per_day = int(r_env)
    if t_env and t_env.isdigit():
        q.tokens_per_day = int(t_env)


# ── Storage helpers ─────────────────────────────────────────────────

def _today_key() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


async def _get_usage(provider: str) -> dict:
    from db import db
    doc = await db.free_quota_usage.find_one(
        {"provider": provider, "day": _today_key()},
        {"_id": 0},
    )
    return doc or {"provider": provider, "day": _today_key(),
                   "calls": 0, "tokens": 0}


# ── Public API ──────────────────────────────────────────────────────

async def has_quota(provider: str) -> bool:
    """Fast check: does this provider still have free quota today?
    Unknown providers default to True (don't block on lack of info)."""
    q = PROVIDER_QUOTAS.get(provider)
    if q is None:
        return True
    usage = await _get_usage(provider)
    if q.requests_per_day is not None and usage.get("calls", 0) >= q.requests_per_day:
        return False
    if q.tokens_per_day is not None and usage.get("tokens", 0) >= q.tokens_per_day:
        return False
    return True


async def record(provider: str, *, tokens: int = 0) -> None:
    """Record one call against the provider's daily quota.
    Idempotent per-day at the row level; safe to call often."""
    from db import db
    try:
        await db.free_quota_usage.update_one(
            {"provider": provider, "day": _today_key()},
            {"$inc":          {"calls": 1, "tokens": int(tokens)},
             "$setOnInsert":  {"first_seen_at": datetime.now(timezone.utc).isoformat()}},
            upsert=True,
        )
    except Exception as exc:
        # Never block the hot path on quota-logging failure.
        logger.info("free_quota_tracker.record failed for %s: %s", provider, exc)


async def utilisation_snapshot() -> dict[str, dict]:
    """Per-provider utilisation snapshot for the admin cost-health dashboard."""
    from db import db
    out: dict[str, dict] = {}
    for prov, q in PROVIDER_QUOTAS.items():
        usage = await _get_usage(prov)
        calls = int(usage.get("calls", 0))
        toks  = int(usage.get("tokens", 0))
        util = None
        if q.requests_per_day:
            util = round(100.0 * calls / q.requests_per_day, 1)
        elif q.tokens_per_day:
            util = round(100.0 * toks / q.tokens_per_day, 1)
        out[prov] = {
            "cap":        q.requests_per_day or q.tokens_per_day,
            "cap_unit":   "req/day" if q.requests_per_day else "tok/day",
            "used":       calls if q.requests_per_day else toks,
            "util_pct":   util,
            "has_quota":  await has_quota(prov),
        }
    # Catch providers we don't have a configured quota for but did hit today.
    seen = set(out.keys())
    async for row in db.free_quota_usage.find({"day": _today_key()}):
        prov = row.get("provider")
        if prov and prov not in seen:
            out[prov] = {
                "cap": None, "cap_unit": None,
                "used": int(row.get("calls", 0)),
                "util_pct": None,
                "has_quota": True,
            }
    return out


async def providers_with_quota(candidates: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """Filter a (provider, model) candidate list to those still under
    daily free quota. Falls back to the original list if nothing
    qualifies, so the router never returns an empty candidate set."""
    out: list[tuple[str, str]] = []
    for pair in candidates:
        if await has_quota(pair[0]):
            out.append(pair)
    return out or candidates
