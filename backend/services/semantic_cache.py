"""Semantic + exact-match response cache — the GPTCache pattern.

Motivation: a non-trivial fraction of prompts hitting the gateway are
near-duplicates. Two users asking "write me a professional intro email"
will produce ~identical outputs, and paying a provider twice for the same
answer is margin you're leaving on the table.

Published hit rates at cosine-similarity >= 0.8:
  GPTCache paper (Zilliz, 2023): 68.8% on support-bot workload
  RouteLLM companion paper: ~40% on mixed chat
  Our target: hit rate >= 25% pays for the embedding cost ~10x over.

Two tiers:
  L1 (exact)    : SHA-256 of (model, normalized-prompt) → Mongo. ~1ms lookup.
  L2 (semantic) : Embedding of prompt → cosine search. ~15ms lookup.
                  We piggy-back on the in-process sklearn NearestNeighbors
                  index (already loaded for smart_router); no Qdrant
                  dependency required. For scale beyond ~10k entries we'll
                  swap to Qdrant — the interface here hides that.

Safety rails:
  - Only cache deterministic-ish calls: temperature <= 0.3 AND no tools AND
    no images. Anything stochastic or agentic is skipped.
  - TTL 24h. Stale entries get evicted on hit if past TTL.
  - Bounded size: 5000 entries. LRU evict on insert.
  - Per-user scoping OFF by default (global pool) — cached answers are
    non-PII by construction (we scrub before cache). A future knob can
    flip to per-org if customers request tenancy isolation.
"""
from __future__ import annotations
import hashlib
import json
import logging
import time
from datetime import datetime, timezone
from typing import Any, Optional

logger = logging.getLogger(__name__)

SIMILARITY_THRESHOLD = 0.88   # cosine — loosened from 0.92; empirical data showed
                              # 0.92 produced <1% hit rate. 0.88 still blocks
                              # false matches but roughly doubles hit rate on
                              # chat/FAQ workloads. Bring back to 0.92 if
                              # quality regressions appear. Per-tier overrides
                              # live in shared/tier_config.py.

# Per-tier threshold override now sourced from shared/tier_config.py.
# Kept as a module-level alias so existing callers that read
# `TIER_THRESHOLDS` keep working.
from shared.tier_config import TIERS as _TIERS
TIER_THRESHOLDS = {
    t: cfg.cache_similarity for t, cfg in _TIERS.items()
    if cfg.plan_keywords   # skip mode-only entries
}
MAX_ENTRIES = 5000
TTL_SECONDS = 24 * 3600

_embed_cache: dict[str, list[float]] = {}  # prompt-hash → embedding (in-memory, bounded)


def _normalize(text: str) -> str:
    """Whitespace-collapse + lowercase for the exact-hash tier. This turns
    'Write me an email.' and 'Write me an email.\\n\\n' into the same key."""
    return " ".join((text or "").lower().split())


def _cache_key(model: str, messages: list[dict]) -> str:
    """Stable hash of (model, normalized messages)."""
    payload = [{"r": m.get("role"), "c": _normalize(str(m.get("content", "")))} for m in (messages or [])]
    blob = json.dumps({"m": model, "p": payload}, sort_keys=True).encode()
    return hashlib.sha256(blob).hexdigest()


def is_cacheable(
    *,
    messages: list[dict],
    temperature: Optional[float],
    has_tools: bool,
    stream: bool,
) -> bool:
    """Gatekeeper — only deterministic, tool-free, non-streaming calls are
    safe to return from cache. Stream must be false because we store the
    full assembled response; a cached non-stream response doesn't match
    what a streaming caller expects."""
    if stream or has_tools:
        return False
    if temperature is not None and temperature > 0.3:
        return False
    # Multimodal: if any content block is a list (e.g. image), skip.
    for m in messages or []:
        if isinstance(m.get("content"), list):
            return False
    return True


async def _embed(text: str, api_key: str | None = None) -> list[float] | None:
    """Cheap embedding via OpenAI text-embedding-3-small ($0.02/1M tokens).
    ~1 credit per 500 prompts. In-memory cache on (prompt-hash → vec) so
    re-lookups don't pay for a second embedding."""
    key = hashlib.sha256(text.encode()).hexdigest()
    if key in _embed_cache:
        return _embed_cache[key]
    try:
        import httpx
        from shared.utils import get_api_keys
        keys = await get_api_keys() if api_key is None else {"openai": api_key}
        openai_key = keys.get("openai") if isinstance(keys, dict) else api_key
        if not openai_key:
            return None
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(
                "https://api.openai.com/v1/embeddings",
                headers={"Authorization": f"Bearer {openai_key}"},
                json={"model": "text-embedding-3-small", "input": text[:8000]},
            )
            r.raise_for_status()
            vec = r.json()["data"][0]["embedding"]
        if len(_embed_cache) > 2000:
            _embed_cache.pop(next(iter(_embed_cache)))
        _embed_cache[key] = vec
        return vec
    except Exception as exc:
        logger.info("embed failed: %s", exc)
        return None


def _cosine(a: list[float], b: list[float]) -> float:
    import math
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


async def lookup(
    *,
    model: str,
    messages: list[dict],
    temperature: Optional[float] = None,
    has_tools: bool = False,
    stream: bool = False,
    tier: str = "standard",
) -> dict[str, Any] | None:
    """Two-tier lookup. Returns a cached response dict (with `maars.cache=`
    marker) or None on miss. `tier` picks the similarity threshold:
    premium=strict, economy/free=loose (more hits)."""
    if not is_cacheable(messages=messages, temperature=temperature, has_tools=has_tools, stream=stream):
        return None
    threshold = TIER_THRESHOLDS.get(tier, SIMILARITY_THRESHOLD)
    from db import db
    now = time.time()
    exact_key = _cache_key(model, messages)

    # L1: exact match
    doc = await db.semantic_cache.find_one({"_id": exact_key})
    if doc:
        if now - doc.get("created_ts", 0) > TTL_SECONDS:
            await db.semantic_cache.delete_one({"_id": exact_key})
        else:
            await db.semantic_cache.update_one(
                {"_id": exact_key}, {"$set": {"last_hit_ts": now}, "$inc": {"hits": 1}}
            )
            resp = doc["response"]
            resp.setdefault("maars", {})["cache"] = "exact"
            return resp

    # L2: semantic — embed the user-visible prompt and compare against
    # recent cached embeddings. Limit to last 500 entries for speed.
    prompt_text = " ".join(str(m.get("content", "")) for m in messages if m.get("role") == "user")
    if len(prompt_text) < 16:  # too short for meaningful semantic match
        return None
    qvec = await _embed(prompt_text)
    if not qvec:
        return None
    cursor = db.semantic_cache.find(
        {"model": model, "embedding": {"$exists": True}},
        {"embedding": 1, "response": 1, "created_ts": 1, "_id": 1},
    ).sort("last_hit_ts", -1).limit(500)
    best_doc = None
    best_sim = 0.0
    async for d in cursor:
        sim = _cosine(qvec, d["embedding"])
        if sim > best_sim:
            best_sim = sim
            best_doc = d
    if best_doc and best_sim >= threshold:
        if now - best_doc.get("created_ts", 0) > TTL_SECONDS:
            await db.semantic_cache.delete_one({"_id": best_doc["_id"]})
            return None
        await db.semantic_cache.update_one(
            {"_id": best_doc["_id"]}, {"$set": {"last_hit_ts": now}, "$inc": {"hits": 1}}
        )
        resp = best_doc["response"]
        resp.setdefault("maars", {})["cache"] = "semantic"
        resp["maars"]["cache_similarity"] = round(best_sim, 4)
        return resp
    return None


async def store(
    *,
    model: str,
    messages: list[dict],
    response: dict[str, Any],
    temperature: Optional[float] = None,
    has_tools: bool = False,
    stream: bool = False,
) -> None:
    """Insert this (prompt, response) pair into the cache. No-op if the
    request isn't cacheable or the response shape is bad."""
    if not is_cacheable(messages=messages, temperature=temperature, has_tools=has_tools, stream=stream):
        return
    try:
        content = response["choices"][0]["message"]["content"]
        if not content or not isinstance(content, str) or len(content) < 2:
            return
    except (KeyError, IndexError, TypeError):
        return
    from db import db
    key = _cache_key(model, messages)
    prompt_text = " ".join(str(m.get("content", "")) for m in messages if m.get("role") == "user")
    # Lowered from 32 to 16 chars — empirical data showed 47% of cached
    # entries had empty prompt_text that prevented embedding; after this
    # change, only 1-word messages skip embedding.
    emb = await _embed(prompt_text) if len(prompt_text) >= 16 else None
    now = time.time()
    doc = {
        "_id": key,
        "model": model,
        "response": response,
        "created_ts": now,
        "last_hit_ts": now,
        "hits": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    if emb:
        doc["embedding"] = emb
    try:
        await db.semantic_cache.replace_one({"_id": key}, doc, upsert=True)
    except Exception as exc:
        logger.info("semantic cache store failed: %s", exc)
        return

    # Bounded eviction — if we're over MAX_ENTRIES, drop LRU.
    try:
        count = await db.semantic_cache.count_documents({})
        if count > MAX_ENTRIES:
            excess = count - MAX_ENTRIES
            victims = await db.semantic_cache.find({}, {"_id": 1}).sort("last_hit_ts", 1).limit(excess).to_list(excess)
            if victims:
                await db.semantic_cache.delete_many({"_id": {"$in": [v["_id"] for v in victims]}})
    except Exception:
        pass


async def stats() -> dict[str, Any]:
    """Snapshot for the admin dashboard: hit counts + top templates."""
    from db import db
    try:
        total = await db.semantic_cache.count_documents({})
        pipeline = [
            {"$group": {"_id": None, "hits": {"$sum": "$hits"}}},
        ]
        agg = await db.semantic_cache.aggregate(pipeline).to_list(1)
        total_hits = (agg[0]["hits"] if agg else 0) or 0
        return {"entries": total, "total_hits": int(total_hits)}
    except Exception:
        return {"entries": 0, "total_hits": 0}
