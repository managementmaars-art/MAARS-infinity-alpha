"""Lightweight browser-like tools for agent SOPs.

Agents' research steps call `web_search`, `browser_open`,
`browser_navigate`, `browser_extract`, `browser_screenshot`. We wire
httpx + a tiny HTML→text extractor so every research pipeline can
actually fetch + read the web — no headless Chromium required.

For visual (JavaScript-rendered) pages, the operator can separately
run the MCP Playwright bridge; that registers richer tools that
supersede these. The fallbacks here cover plain HTML / static sites
which is what most citation-grade research actually needs.

Tool contracts (all async, all return dicts):
  web_search(query, count=10, freshness=None) → {ok, results[{title,url,snippet,age}], query}
  browser_open(url, max_chars=12000)           → {ok, url, title, text, status_code}
  browser_navigate(url, max_chars=12000)       → alias for browser_open
  browser_extract(url, selector=None, max_chars=12000) → {ok, url, title, text, selector}
  browser_screenshot(url)                      → {ok, url, note} (text-only fallback;
                                                  real screenshots require MCP Playwright)
"""
from __future__ import annotations
import logging
import re
from typing import Any, Optional

import httpx

logger = logging.getLogger(__name__)

_USER_AGENT = (
    "Mozilla/5.0 (compatible; MAARS-Agent/1.0; +https://maars.ai/bot)"
)
_REQUEST_TIMEOUT = 20


# ── Utility ──────────────────────────────────────────────────────────

_SCRIPT_STYLE = re.compile(r"<(script|style)[^>]*>.*?</\1>", re.DOTALL | re.IGNORECASE)
_TAG = re.compile(r"<[^>]+>")
_WHITESPACE = re.compile(r"\s+")
_TITLE = re.compile(r"<title[^>]*>([\s\S]*?)</title>", re.IGNORECASE)


def _html_to_text(html: str, max_chars: int = 12000) -> tuple[str, str]:
    """Cheap server-side HTML → readable-text extraction.

    Prefers BeautifulSoup if installed (handles broken HTML better);
    falls back to regex strip when bs4 isn't available.

    Returns: (title, text) — text is trimmed to max_chars.
    """
    title = ""
    # Try bs4 first for cleaner extraction
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        if soup.title and soup.title.string:
            title = soup.title.string.strip()
        # Drop script / style / nav / aside
        for tag in soup(["script", "style", "nav", "aside", "footer", "header"]):
            tag.decompose()
        text = soup.get_text(separator=" ", strip=True)
    except Exception:
        # Regex fallback
        m = _TITLE.search(html)
        if m:
            title = _WHITESPACE.sub(" ", _TAG.sub("", m.group(1))).strip()
        stripped = _SCRIPT_STYLE.sub(" ", html)
        text = _TAG.sub(" ", stripped)
    text = _WHITESPACE.sub(" ", text).strip()
    if max_chars and len(text) > max_chars:
        text = text[:max_chars].rstrip() + "…"
    return title, text


# ── Public tool surface ─────────────────────────────────────────────

async def browser_open(url: str, max_chars: int = 12000) -> dict:
    """Fetch a URL and return its readable text + title. Agent-facing."""
    if not url or not url.lower().startswith(("http://", "https://")):
        return {"ok": False, "url": url, "error": "invalid url"}
    try:
        async with httpx.AsyncClient(
            timeout=_REQUEST_TIMEOUT, follow_redirects=True,
            headers={"User-Agent": _USER_AGENT, "Accept": "text/html,application/xhtml+xml"},
        ) as client:
            r = await client.get(url)
    except Exception as exc:
        return {"ok": False, "url": url, "error": f"{type(exc).__name__}: {exc}"}
    if r.status_code != 200:
        return {"ok": False, "url": url, "status_code": r.status_code,
                "error": f"HTTP {r.status_code}"}
    ct = (r.headers.get("content-type") or "").lower()
    if "text/html" not in ct and "application/xhtml" not in ct:
        # Non-HTML: return raw if short (JSON, text), else stub
        body = r.text[:max_chars] if r.text else ""
        return {"ok": True, "url": str(r.url), "title": "",
                "text": body, "content_type": ct, "status_code": r.status_code}
    title, text = _html_to_text(r.text, max_chars=max_chars)
    return {"ok": True, "url": str(r.url), "title": title,
            "text": text, "status_code": r.status_code}


async def browser_navigate(url: str, max_chars: int = 12000) -> dict:
    """Alias of browser_open — agents often say 'navigate' in SOPs."""
    return await browser_open(url, max_chars=max_chars)


async def browser_extract(url: str, selector: Optional[str] = None,
                          max_chars: int = 12000) -> dict:
    """Fetch a URL and optionally extract a CSS-selector's text. Without
    a selector this matches browser_open. With one, returns the
    concatenated text of all matching elements."""
    result = await browser_open(url, max_chars=max_chars * 3)  # get more raw room
    if not result.get("ok"):
        return result
    if not selector:
        result["text"] = (result.get("text") or "")[:max_chars]
        return result
    try:
        from bs4 import BeautifulSoup
        # Re-fetch raw HTML for selector — browser_open returned cleaned text.
        async with httpx.AsyncClient(
            timeout=_REQUEST_TIMEOUT, follow_redirects=True,
            headers={"User-Agent": _USER_AGENT},
        ) as client:
            r = await client.get(url)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            matches = soup.select(selector)
            text = "\n".join(m.get_text(separator=" ", strip=True) for m in matches)
            text = _WHITESPACE.sub(" ", text).strip()
            if len(text) > max_chars:
                text = text[:max_chars] + "…"
            return {"ok": True, "url": url, "selector": selector,
                    "match_count": len(matches), "text": text,
                    "title": result.get("title", "")}
    except Exception as exc:
        return {"ok": False, "url": url, "selector": selector,
                "error": f"selector failed: {type(exc).__name__}: {exc}"}
    return result


async def browser_screenshot(url: str) -> dict:
    """Lightweight fallback — returns page title + first 400 chars as a
    text "snapshot" since headless Chromium isn't wired server-side.
    Operators wanting pixel-level screenshots run MCP Playwright which
    registers richer tools that supersede this one."""
    page = await browser_open(url, max_chars=400)
    if not page.get("ok"):
        return page
    return {
        "ok": True,
        "url": page.get("url"),
        "title": page.get("title", ""),
        "snapshot_text": page.get("text", ""),
        "note": "Text snapshot only. Install Playwright MCP for pixel screenshots.",
    }
