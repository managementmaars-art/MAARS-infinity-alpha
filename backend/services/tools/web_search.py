"""Web search tool — uses DuckDuckGo HTML (no API key required)."""
from __future__ import annotations

import re
import time
from html import unescape
from typing import Any

import httpx

from .base import Tool, ToolResult

_RESULT_RE = re.compile(
    r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>.*?'
    r'<a[^>]+class="result__snippet"[^>]*>(.*?)</a>',
    re.DOTALL | re.IGNORECASE,
)
_STRIP_TAGS = re.compile(r"<[^>]+>")


class WebSearchTool(Tool):
    name = "web_search"
    description = "Search the public web and return a list of ranked results."
    argument_schema = {
        "type": "object",
        "required": ["query"],
        "properties": {
            "query": {"type": "string", "description": "Search query"},
            "max_results": {"type": "integer", "minimum": 1, "maximum": 20, "default": 5},
        },
    }
    credit_cost = 1
    timeout_seconds = 10.0

    async def run(self, args: dict[str, Any]) -> ToolResult:
        query = (args.get("query") or "").strip()
        if not query:
            return ToolResult(ok=False, error="query is required")
        max_results = min(int(args.get("max_results", 5)), 20)

        t0 = time.time()
        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds, follow_redirects=True) as c:
                r = await c.get(
                    "https://html.duckduckgo.com/html/",
                    params={"q": query},
                    headers={"User-Agent": "Mozilla/5.0 (MAARS; +https://maarsglobal.com)"},
                )
        except Exception as exc:
            return ToolResult(ok=False, error=f"{type(exc).__name__}: {exc}",
                              latency_ms=int((time.time() - t0) * 1000))

        results: list[dict[str, str]] = []
        for m in _RESULT_RE.finditer(r.text or ""):
            if len(results) >= max_results:
                break
            href, title_html, snippet_html = m.group(1), m.group(2), m.group(3)
            results.append({
                "url": unescape(href),
                "title": unescape(_STRIP_TAGS.sub("", title_html)).strip(),
                "snippet": unescape(_STRIP_TAGS.sub("", snippet_html)).strip(),
            })

        return ToolResult(
            ok=True,
            data={"query": query, "results": results},
            latency_ms=int((time.time() - t0) * 1000),
            metadata={"source": "duckduckgo", "hits": len(results)},
        )
