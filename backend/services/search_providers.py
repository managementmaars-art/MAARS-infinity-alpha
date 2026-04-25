"""Web search providers — Brave-first, DuckDuckGo fallback.

Brave Search API gives 2,000 queries/month free — actually indexed and
ranked results, not the "crawl DuckDuckGo HTML" workaround. Falls back
to DuckDuckGo (via the existing `ddgs` package) when Brave is either
not keyed or rate-limited.

Agents use this via the `web_search` tool transparently — they don't
care which provider served; the response shape is normalized.

Setup:
  1. https://api.search.brave.com/app/keys  — free signup, no credit card
  2. Add to .env:
        BRAVE_SEARCH_API_KEY=...
  3. Leave unconfigured → DuckDuckGo still works (zero keys needed).
"""
from __future__ import annotations
import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)


def is_brave_configured() -> bool:
    return bool(os.environ.get("BRAVE_SEARCH_API_KEY"))


async def _search_brave(query: str, count: int = 10, freshness: str | None = None) -> dict:
    """Call Brave's /web/search endpoint. Returns normalized shape."""
    key = os.environ.get("BRAVE_SEARCH_API_KEY")
    if not key:
        return {"ok": False, "error": "Brave not configured"}
    params = {"q": query, "count": min(count, 20)}
    if freshness:
        # freshness = 'pd' (24h), 'pw' (week), 'pm' (month), 'py' (year)
        params["freshness"] = freshness
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                "https://api.search.brave.com/res/v1/web/search",
                headers={
                    "Accept": "application/json",
                    "X-Subscription-Token": key,
                },
                params=params,
            )
            if resp.status_code != 200:
                return {
                    "ok": False,
                    "error": f"Brave {resp.status_code}: {resp.text[:200]}",
                    "status_code": resp.status_code,
                }
            data = resp.json()
            results = []
            for item in (data.get("web", {}) or {}).get("results", [])[:count]:
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "snippet": item.get("description", ""),
                    "age": item.get("age"),
                })
            return {"ok": True, "results": results, "query": query}
    except Exception as exc:
        logger.exception("Brave search failed")
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}


async def _search_duckduckgo(query: str, count: int = 10) -> dict:
    """Existing DDG fallback via the `ddgs` package. Zero-key, community-run."""
    try:
        from ddgs import DDGS
        with DDGS() as ddgs:
            raw = list(ddgs.text(query, max_results=count))
        results = [{
            "title": r.get("title", ""),
            "url": r.get("href", ""),
            "snippet": r.get("body", ""),
            "age": None,
        } for r in raw]
        return {"ok": True, "results": results, "query": query}
    except Exception as exc:
        logger.exception("DDG search failed")
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}


async def search_web(query: str, count: int = 10, freshness: str | None = None) -> dict:
    """Public entry: Brave if keyed, DDG otherwise.

    Response shape:
      {ok: bool, results: [{title, url, snippet, age}], query: str, error: str|None}

    Never identifies which backend served — the agent-facing contract is
    "MAARS web search", period.
    """
    if is_brave_configured():
        result = await _search_brave(query, count=count, freshness=freshness)
        if result.get("ok"):
            return result
        # If Brave failed (rate-limited, outage) fall through to DDG
        logger.info("Brave search failed, falling back: %s", result.get("error"))
    return await _search_duckduckgo(query, count=count)
