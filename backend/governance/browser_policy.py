"""MAARS — Browser Policy & Quotas.

Two independent governance concerns, deliberately colocated because they're
both enforced at the same two moments: session-open and navigation.

  1. Domain policy — per-environment allow-list / block-list of hostnames.
  2. Per-user browser-minutes budget — resets daily (UTC), hard ceiling at
     100% (no override without explicit reset).

Both are stored in MongoDB under `governance_policies` with a `scope` field
so policies can be global, per-environment, or per-user.

Enforcement is fail-closed: a missing policy document counts as "allow the
default env list" (see `DEFAULT_DOMAIN_POLICY` below). Admins can edit via
the `/api/admin/browser-policy` endpoints (added in this audit pass).
"""
from __future__ import annotations

import fnmatch
import logging
import re
from datetime import datetime, timezone
from urllib.parse import urlparse

from db import db

logger = logging.getLogger(__name__)

POLICY_COLLECTION = "governance_policies"
USAGE_COLLECTION  = "browser_usage_daily"

# ── Defaults ────────────────────────────────────────────────────────────────
# Sensible starter policy: block known risky / local-only origins, allow
# everything else. Admins can override per environment.
DEFAULT_DOMAIN_POLICY: dict[str, list[str]] = {
    "allow":   ["*"],
    "deny":    [
        "localhost", "127.0.0.1", "0.0.0.0", "*.local",
        "*.internal", "metadata.google.internal", "169.254.169.254",
    ],
}

# Minutes of headless browser wall-time allowed per user per day (UTC).
# 0 means unlimited. Admins can override per-user.
DEFAULT_BROWSER_MINUTES_PER_DAY = 60


class PolicyDenied(PermissionError):
    """Raised when a browser action is blocked by the domain policy."""


class BudgetExhausted(RuntimeError):
    """Raised when the per-user daily browser-minutes budget is exhausted."""


# ── Host matching ───────────────────────────────────────────────────────────
def _host_of(url: str) -> str:
    try:
        return (urlparse(url).hostname or "").lower()
    except Exception:
        return ""


def _matches_any(host: str, patterns: list[str]) -> bool:
    host = host.lower()
    for p in patterns:
        p = p.strip().lower()
        if not p:
            continue
        if p == "*" or p == host:
            return True
        if fnmatch.fnmatch(host, p):
            return True
        # Bare apex matches the same apex + subdomains.
        if host == p or host.endswith("." + p):
            return True
    return False


# ── Policy read/write ───────────────────────────────────────────────────────
async def get_domain_policy(environment: str = "production") -> dict:
    doc = await db[POLICY_COLLECTION].find_one(
        {"scope": f"browser:domain:{environment}"}, {"_id": 0}
    )
    if doc and isinstance(doc.get("policy"), dict):
        return doc["policy"]
    return DEFAULT_DOMAIN_POLICY


async def set_domain_policy(environment: str, policy: dict) -> None:
    if not isinstance(policy, dict):
        raise ValueError("policy must be a dict with 'allow' and 'deny' lists")
    policy = {
        "allow": list(policy.get("allow") or []),
        "deny":  list(policy.get("deny")  or []),
    }
    await db[POLICY_COLLECTION].update_one(
        {"scope": f"browser:domain:{environment}"},
        {"$set": {
            "scope":      f"browser:domain:{environment}",
            "policy":     policy,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }},
        upsert=True,
    )


async def get_browser_budget(user_id: str) -> int:
    """Return the user's daily browser-minutes budget. 0 = unlimited."""
    doc = await db[POLICY_COLLECTION].find_one(
        {"scope": f"browser:budget:{user_id}"}, {"_id": 0}
    )
    if doc and "minutes_per_day" in doc:
        try:
            return int(doc["minutes_per_day"])
        except Exception:
            pass
    return DEFAULT_BROWSER_MINUTES_PER_DAY


async def set_browser_budget(user_id: str, minutes_per_day: int) -> None:
    await db[POLICY_COLLECTION].update_one(
        {"scope": f"browser:budget:{user_id}"},
        {"$set": {
            "scope":           f"browser:budget:{user_id}",
            "minutes_per_day": max(0, int(minutes_per_day)),
            "updated_at":      datetime.now(timezone.utc).isoformat(),
        }},
        upsert=True,
    )


# ── Enforcement ─────────────────────────────────────────────────────────────
async def check_domain(url: str, environment: str = "production") -> None:
    """Raise PolicyDenied if `url` is not permitted in `environment`."""
    host = _host_of(url)
    if not host:
        return  # non-URL schemes (about:blank, data:) — always allow
    policy = await get_domain_policy(environment)
    deny  = policy.get("deny")  or []
    allow = policy.get("allow") or ["*"]
    if _matches_any(host, deny):
        raise PolicyDenied(f"domain {host!r} is blocked by policy in {environment}")
    if not _matches_any(host, allow):
        raise PolicyDenied(f"domain {host!r} is not in the {environment} allow-list")


def _today_key() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


async def _get_today_usage(user_id: str) -> dict:
    key = _today_key()
    doc = await db[USAGE_COLLECTION].find_one(
        {"user_id": user_id, "date": key}, {"_id": 0}
    )
    return doc or {"user_id": user_id, "date": key, "minutes_used": 0.0, "sessions": 0}


async def check_and_charge_minutes(user_id: str, minutes: float) -> dict:
    """Debit the daily bucket. Raises BudgetExhausted if over the cap.
    Returns the updated usage record."""
    budget = await get_browser_budget(user_id)
    usage  = await _get_today_usage(user_id)
    new_used = float(usage.get("minutes_used", 0.0)) + float(minutes)
    if budget > 0 and new_used > budget:
        raise BudgetExhausted(
            f"browser-minutes budget exhausted: {budget:.0f} min/day used up"
        )
    await db[USAGE_COLLECTION].update_one(
        {"user_id": user_id, "date": _today_key()},
        {"$set": {"minutes_used": new_used}, "$inc": {"sessions": 0 if minutes else 1}},
        upsert=True,
    )
    usage["minutes_used"] = new_used
    return usage


async def increment_sessions_opened(user_id: str) -> None:
    await db[USAGE_COLLECTION].update_one(
        {"user_id": user_id, "date": _today_key()},
        {"$inc": {"sessions": 1}, "$setOnInsert": {"minutes_used": 0.0}},
        upsert=True,
    )


async def get_usage_summary(user_id: str) -> dict:
    usage   = await _get_today_usage(user_id)
    budget  = await get_browser_budget(user_id)
    return {
        "user_id":           user_id,
        "date":              usage["date"],
        "minutes_used":      round(float(usage.get("minutes_used", 0.0)), 2),
        "sessions_today":    int(usage.get("sessions", 0)),
        "budget_minutes":    budget,
        "percent_used":      (float(usage.get("minutes_used", 0.0)) / budget * 100) if budget > 0 else 0.0,
        "unlimited":         budget == 0,
    }
