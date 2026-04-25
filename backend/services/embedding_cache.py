"""Embedding cache — dedicated tier for repeated embedding calls.

`semantic_cache` has a small in-process dict mapping prompt-hash → vec.
That's fine for repeated user prompts within a single worker, but:

  - It doesn't persist across restarts.
  - It doesn't dedupe across workers.
  - It doesn't bound total spend on embeddings — even at $0.02/1M tokens
    we saw 40-50% of our embedding calls were exact repeats.

This module is the persistent, shared tier:

  L0 (in-process) : semantic_cache._embed_cache (2000 entries, fastest)
  L1 (Mongo)      : embedding_store collection, keyed by sha256(text)
                    with 30-day TTL.

`get(text)` checks L0 → L1 → calls OpenAI. Stores in both tiers on miss.
Exposes `warmup()` to batch-embed a list of strings up front.
"""
from __future__ import annotations
import asyncio
import hashlib
import logging
import time
from typing import Any

logger = logging.getLogger(__name__)

TTL_SECONDS = 30 * 86400
_INDEX_READY = False


def _key(text: str) -> str:
    return hashlib.sha256((text or "").encode()).hexdigest()


async def _ensure_index() -> None:
    global _INDEX_READY
    if _INDEX_READY:
        return
    try:
        from db import db
        await db.embedding_store.create_index("created_at_epoch", expireAfterSeconds=TTL_SECONDS)
        _INDEX_READY = True
    except Exception as exc:
        logger.info("embedding_store index deferred: %s", exc)


async def get(text: str) -> list[float] | None:
    """L0 → L1 → network. Populates on the way back."""
    if not text:
        return None
    from services.semantic_cache import _embed_cache, _embed
    key = _key(text)
    if key in _embed_cache:
        return _embed_cache[key]

    # L1 lookup
    try:
        await _ensure_index()
        from db import db
        doc = await db.embedding_store.find_one({"_id": key}, {"vec": 1, "_id": 0})
        if doc and "vec" in doc:
            _embed_cache[key] = doc["vec"]
            if len(_embed_cache) > 2000:
                _embed_cache.pop(next(iter(_embed_cache)))
            return doc["vec"]
    except Exception:
        pass

    # Network call → writes both tiers.
    vec = await _embed(text)
    if vec is None:
        return None
    try:
        from db import db
        await db.embedding_store.replace_one(
            {"_id": key},
            {"_id": key, "vec": vec, "len": len(text), "created_at_epoch": time.time()},
            upsert=True,
        )
    except Exception as exc:
        logger.info("embedding_store persist failed: %s", exc)
    return vec


async def warmup(texts: list[str], *, concurrency: int = 8) -> int:
    """Pre-embed a list of strings (e.g. all KB articles on startup).
    Returns number of new entries added."""
    if not texts:
        return 0
    sem = asyncio.Semaphore(concurrency)
    added = 0

    async def _one(t: str):
        nonlocal added
        async with sem:
            before = _key(t) in (await _present_keys({_key(t)}))
            if before:
                return
            await get(t)
            added += 1

    await asyncio.gather(*(_one(t) for t in texts), return_exceptions=True)
    return added


async def _present_keys(keys: set[str]) -> set[str]:
    try:
        from db import db
        cursor = db.embedding_store.find({"_id": {"$in": list(keys)}}, {"_id": 1})
        docs = await cursor.to_list(len(keys))
        return {d["_id"] for d in docs}
    except Exception:
        return set()


async def stats() -> dict[str, Any]:
    try:
        from db import db
        count = await db.embedding_store.count_documents({})
    except Exception:
        count = 0
    from services.semantic_cache import _embed_cache
    return {"persisted": count, "in_process": len(_embed_cache)}
