"""Database query tool — whitelisted read-only MongoDB access."""
from __future__ import annotations

import time
from typing import Any

from .base import Tool, ToolResult

# Agents may only read from these collections. Wallets, keys, auth data are off-limits.
_ALLOWED_COLLECTIONS = {
    "agents",
    "gateway_usage_logs",
    "knowledge_base",
    "products",
    "projects",
    "tasks",
    "teams",
    "usage_logs",
}

_MAX_LIMIT = 50


class DBQueryTool(Tool):
    name = "db_query"
    description = "Read-only MongoDB find against a whitelisted collection."
    argument_schema = {
        "type": "object",
        "required": ["collection"],
        "properties": {
            "collection": {"type": "string", "description": f"one of: {sorted(_ALLOWED_COLLECTIONS)}"},
            "filter":     {"type": "object", "default": {}},
            "projection": {"type": "object", "default": {}},
            "limit":      {"type": "integer", "default": 10, "minimum": 1, "maximum": _MAX_LIMIT},
            "sort":       {"type": "array", "default": []},
        },
    }
    credit_cost = 1
    timeout_seconds = 5.0

    async def run(self, args: dict[str, Any]) -> ToolResult:
        collection = (args.get("collection") or "").strip()
        if collection not in _ALLOWED_COLLECTIONS:
            return ToolResult(ok=False, error=f"collection '{collection}' not in whitelist")

        from db import db
        query = args.get("filter") or {}
        projection = args.get("projection") or {"_id": 0}
        projection.setdefault("_id", 0)
        limit = min(int(args.get("limit", 10)), _MAX_LIMIT)
        sort = args.get("sort") or []

        t0 = time.time()
        try:
            cursor = db[collection].find(query, projection).limit(limit)
            if sort:
                cursor = cursor.sort(sort)
            docs = [d async for d in cursor]
        except Exception as exc:
            return ToolResult(ok=False, error=f"{type(exc).__name__}: {exc}",
                              latency_ms=int((time.time() - t0) * 1000))

        return ToolResult(
            ok=True,
            data={"collection": collection, "documents": docs, "count": len(docs)},
            latency_ms=int((time.time() - t0) * 1000),
            metadata={"limit": limit, "filter_keys": list(query.keys())},
        )
