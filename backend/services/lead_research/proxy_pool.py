"""Residential proxy rotation for the scraper fleet.

LinkedIn detects datacenter IPs within minutes at scale and throws
challenge pages. Residential / mobile proxies (IPRoyal, SmartProxy,
BrightData, Oxylabs) make the traffic look like a real user. This
module reads a configured pool, rotates per session, tracks which
proxies get challenged, and cools them off.

Sources (first match wins):
  1. `MAARS_PROXY_POOL` env var — comma-separated URLs:
     http://user:pass@host:port,http://user2:pass2@host2:port2
  2. Mongo collection `proxy_pool` with docs
     {_id, url, state:'idle'|'cooldown'|'dead', pulls:int, last_used_ts:float, last_error}

State machine per proxy:
  idle → pulled → (success → idle) | (failure → cooldown 15 min → idle) | (3 failures → dead)

Public API:
  async get_next() -> {"url":..., "playwright":{"server":..., "username":..., "password":...}} | None
  async mark_success(proxy_id)
  async mark_failure(proxy_id, reason)
  async snapshot() -> list for admin dashboard
"""
from __future__ import annotations
import logging
import os
import time
from typing import Any
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

COOLDOWN_SECONDS = 15 * 60
MAX_FAILURES = 3


def _env_pool() -> list[str]:
    raw = os.environ.get("MAARS_PROXY_POOL", "")
    return [u.strip() for u in raw.split(",") if u.strip()]


def _url_to_id(url: str) -> str:
    p = urlparse(url)
    return f"{p.hostname}:{p.port or ''}"


def _url_to_playwright(url: str) -> dict[str, Any]:
    """Playwright proxy arg shape:
        {server: "http://host:port", username, password}
    httpx/playwright both accept the flattened URL, but Chromium via
    Playwright prefers the dict form."""
    p = urlparse(url)
    out = {"server": f"{p.scheme}://{p.hostname}:{p.port or (443 if p.scheme == 'https' else 80)}"}
    if p.username: out["username"] = p.username
    if p.password: out["password"] = p.password
    return out


async def _ensure_seeded() -> None:
    """Seed env proxies into Mongo once so state persists across restarts."""
    from db import db
    try:
        existing = await db.proxy_pool.count_documents({})
    except Exception:
        return
    if existing > 0:
        return
    for url in _env_pool():
        pid = _url_to_id(url)
        try:
            await db.proxy_pool.update_one(
                {"_id": pid},
                {"$set": {"_id": pid, "url": url, "state": "idle",
                          "pulls": 0, "failures": 0,
                          "seeded_at": time.time()}},
                upsert=True,
            )
        except Exception as exc:
            logger.info("proxy seed failed: %s", exc)


async def get_next() -> dict[str, Any] | None:
    """Return the least-recently-used idle proxy. Transitions proxies
    out of cooldown when their cooldown window expires. Returns None
    if no proxy is configured — caller falls back to direct IP."""
    await _ensure_seeded()
    from db import db
    now = time.time()

    # Revive cooldown'd proxies whose timer expired.
    try:
        await db.proxy_pool.update_many(
            {"state": "cooldown",
             "cooldown_until": {"$lte": now}},
            {"$set": {"state": "idle"}},
        )
    except Exception:
        pass

    try:
        doc = await db.proxy_pool.find_one_and_update(
            {"state": "idle"},
            {"$set": {"last_used_ts": now, "state": "in_use"},
             "$inc": {"pulls": 1}},
            sort=[("last_used_ts", 1)],
            return_document=True,
        )
    except Exception:
        doc = None
    if not doc:
        return None
    return {
        "id":         doc["_id"],
        "url":        doc["url"],
        "playwright": _url_to_playwright(doc["url"]),
    }


async def mark_success(proxy_id: str) -> None:
    from db import db
    try:
        await db.proxy_pool.update_one(
            {"_id": proxy_id},
            {"$set": {"state": "idle", "last_success_ts": time.time(),
                      "failures": 0}},
        )
    except Exception:
        pass


async def mark_failure(proxy_id: str, reason: str = "") -> None:
    """Increment failure count; cooldown for 15 min; after MAX_FAILURES
    mark dead (admin must revive)."""
    from db import db
    try:
        doc = await db.proxy_pool.find_one({"_id": proxy_id})
        if not doc: return
        failures = int(doc.get("failures", 0)) + 1
        update: dict[str, Any] = {
            "failures": failures,
            "last_failure_ts": time.time(),
            "last_error": (reason or "")[:200],
        }
        if failures >= MAX_FAILURES:
            update["state"] = "dead"
        else:
            update["state"] = "cooldown"
            update["cooldown_until"] = time.time() + COOLDOWN_SECONDS
        await db.proxy_pool.update_one({"_id": proxy_id}, {"$set": update})
    except Exception as exc:
        logger.info("proxy mark_failure failed: %s", exc)


async def release(proxy_id: str) -> None:
    """Return an in_use proxy to idle without marking success/fail — e.g.
    caller completed work cleanly but doesn't want to claim success."""
    from db import db
    try:
        await db.proxy_pool.update_one(
            {"_id": proxy_id, "state": "in_use"},
            {"$set": {"state": "idle"}},
        )
    except Exception:
        pass


async def revive(proxy_id: str) -> bool:
    """Admin-hook: bring a dead proxy back to idle (after the operator
    verifies the credentials or swapped gateways)."""
    from db import db
    r = await db.proxy_pool.update_one(
        {"_id": proxy_id},
        {"$set": {"state": "idle", "failures": 0}},
    )
    return bool(r.modified_count)


async def snapshot() -> list[dict[str, Any]]:
    from db import db
    try:
        rows = await db.proxy_pool.find(
            {}, {"url": 0},     # hide creds in dashboard
        ).to_list(500)
    except Exception:
        return []
    return [{k: v for k, v in r.items() if k != "_id"} | {"id": r["_id"]} for r in rows]
