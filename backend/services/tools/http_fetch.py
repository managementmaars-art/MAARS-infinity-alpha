"""HTTP fetch tool — safe GET with size + timeout caps."""
from __future__ import annotations

import time
from typing import Any
from urllib.parse import urlparse

import httpx

from .base import Tool, ToolResult

_MAX_BYTES = 512 * 1024  # 512 KiB — enough for most pages, blocks accidental firehoses
_BLOCKED_HOSTS = {"localhost", "127.0.0.1", "0.0.0.0", "169.254.169.254"}


class HttpFetchTool(Tool):
    name = "http_fetch"
    description = "Fetch the contents of a public URL via HTTP GET (512KB cap)."
    argument_schema = {
        "type": "object",
        "required": ["url"],
        "properties": {
            "url":    {"type": "string", "description": "Public URL to fetch"},
            "accept": {"type": "string", "default": "text/plain, application/json"},
        },
    }
    credit_cost = 1
    timeout_seconds = 10.0

    async def run(self, args: dict[str, Any]) -> ToolResult:
        url = (args.get("url") or "").strip()
        if not url:
            return ToolResult(ok=False, error="url is required")

        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return ToolResult(ok=False, error="only http/https schemes allowed")
        if parsed.hostname and parsed.hostname.lower() in _BLOCKED_HOSTS:
            return ToolResult(ok=False, error=f"host not allowed: {parsed.hostname}")

        t0 = time.time()
        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds, follow_redirects=True) as c:
                r = await c.get(url, headers={"Accept": args.get("accept", "text/plain")})
        except Exception as exc:
            return ToolResult(ok=False, error=f"{type(exc).__name__}: {exc}",
                              latency_ms=int((time.time() - t0) * 1000))

        body = r.content[:_MAX_BYTES]
        truncated = len(r.content) > _MAX_BYTES
        return ToolResult(
            ok=(200 <= r.status_code < 300),
            data={
                "status": r.status_code,
                "headers": dict(r.headers),
                "body": body.decode("utf-8", errors="replace"),
                "truncated": truncated,
            },
            latency_ms=int((time.time() - t0) * 1000),
            metadata={"url": url, "bytes": len(body)},
        )
