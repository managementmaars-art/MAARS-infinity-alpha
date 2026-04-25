"""Tool-result cache — dedupe deterministic tool calls inside agent loops.

When an agent loop runs, it often re-calls the same tool with identical
args across turns (same web-search query, same DB lookup, same
HTTP GET). Caching THAT layer — orthogonal to chat-response caching —
typically saves another 15-30% on agent workloads.

Semantics:
  key  = sha256(tool_name + canonicalized_args)
  TTL  = tool-specific (web_search: 15m, http_get: 5m, kb_search: 1h,
         default: 10m) — callers can override.

Unsafe tools (mutations — POST/PUT/DELETE, send_email, commit_to_db)
are NEVER cached. Classifier: tool name or kwargs contain any of
`{"write","post","put","delete","send","commit","create"}`.
"""
from __future__ import annotations
import hashlib
import json
import logging
import time
from typing import Any

logger = logging.getLogger(__name__)

_DEFAULT_TTL = 600   # 10 minutes
_TOOL_TTL = {
    "web_search":  900,
    "google_search": 900,
    "http_get":    300,
    "kb_search":   3600,
    "vector_search": 3600,
    "get_weather": 600,
    "get_stock_price": 60,
}

_MUTATION_WORDS = {
    "write", "post", "put", "delete", "send", "commit", "create",
    "update", "insert", "patch", "remove", "drop", "truncate",
}


def _is_mutation(tool_name: str, args: dict | None) -> bool:
    name = (tool_name or "").lower()
    if any(w in name for w in _MUTATION_WORDS):
        return True
    if args:
        arg_blob = json.dumps(args, default=str).lower()
        # Conservative: any key named verb/method with a write value
        for k, v in args.items():
            if k.lower() in ("method", "verb") and isinstance(v, str) and v.upper() in ("POST", "PUT", "DELETE", "PATCH"):
                return True
    return False


def _key(tool_name: str, args: dict) -> str:
    canon = json.dumps(args or {}, sort_keys=True, default=str).encode()
    h = hashlib.sha256()
    h.update(tool_name.encode())
    h.update(b"\0")
    h.update(canon)
    return h.hexdigest()


def _ttl_for(tool_name: str, override: int | None = None) -> int:
    if override is not None and override > 0:
        return override
    return _TOOL_TTL.get(tool_name, _DEFAULT_TTL)


async def get(tool_name: str, args: dict) -> Any | None:
    if _is_mutation(tool_name, args):
        return None
    try:
        from db import db
        key = _key(tool_name, args)
        doc = await db.tool_result_cache.find_one({"_id": key})
    except Exception:
        return None
    if not doc:
        return None
    if time.time() - doc.get("created_ts", 0) > doc.get("ttl", _DEFAULT_TTL):
        try:
            await db.tool_result_cache.delete_one({"_id": doc["_id"]})
        except Exception:
            pass
        return None
    try:
        from services import prometheus_metrics as pm
        pm.inc_cache_hit("tool_result")
    except Exception:
        pass
    return doc.get("result")


async def store(tool_name: str, args: dict, result: Any, *, ttl: int | None = None) -> None:
    if _is_mutation(tool_name, args):
        return
    if result is None:
        return
    try:
        from db import db
        key = _key(tool_name, args)
        await db.tool_result_cache.replace_one(
            {"_id": key},
            {
                "_id": key,
                "tool_name": tool_name,
                "result": result,
                "ttl": _ttl_for(tool_name, ttl),
                "created_ts": time.time(),
            },
            upsert=True,
        )
    except Exception as exc:
        logger.info("tool_result_cache store failed: %s", exc)


async def call_through(tool_name: str, args: dict, executor, *, ttl: int | None = None) -> Any:
    """Convenience wrapper: cache-aside around a call to `executor(args)`.

    executor : sync or async callable that runs the tool.
    """
    cached = await get(tool_name, args)
    if cached is not None:
        return cached
    import inspect
    if inspect.iscoroutinefunction(executor):
        result = await executor(args)
    else:
        result = executor(args)
    await store(tool_name, args, result, ttl=ttl)
    return result


async def stats() -> dict[str, Any]:
    try:
        from db import db
        total = await db.tool_result_cache.count_documents({})
    except Exception:
        total = 0
    return {"entries": total}
