"""Lightweight vector store.

Phase 1: numpy-based cosine similarity over chunks stored in Mongo
`rag_chunks`. Good enough for thousands of chunks per user; ~10ms
retrieval on 10k chunks. Phase 2 (deferred) swaps in Milvus with
binary-quantized index per the fastest-rag-milvus-groq pattern.

Embeddings go through MAARS's existing `embedding_cache` so we only
embed once per chunk even if it's searched repeatedly.
"""
from __future__ import annotations
import logging
from typing import Any

logger = logging.getLogger(__name__)

DEFAULT_EMBED_MODEL = "text-embedding-3-small"  # OpenAI, 1536-dim


async def _embed(text: str, model: str = DEFAULT_EMBED_MODEL):
    """Use MAARS embedding_cache (L0 mem → L1 Mongo → network) if
    available, else call OpenAI directly."""
    try:
        from services import embedding_cache
        vec = await embedding_cache.get(text)
        if vec:
            return vec
    except Exception as exc:
        logger.info("embedding_cache unavailable (%s), falling back to direct call", exc)
    # Direct fallback via openai
    import os
    import httpx
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        return None
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(
            "https://api.openai.com/v1/embeddings",
            headers={"Authorization": f"Bearer {key}",
                     "Content-Type": "application/json"},
            json={"input": text[:8000], "model": model},
        )
    try:
        return r.json()["data"][0]["embedding"]
    except Exception:
        return None


def _cosine(a, b) -> float:
    import math
    if not a or not b:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


async def embed_pending_chunks(user_id: str, batch_size: int = 50) -> int:
    """Embed any rag_chunks for this user that don't have an embedding
    yet. Called lazily on first search after an ingest; also safe to
    run periodically."""
    from db import db
    q = {"user_id": user_id, "embedding": {"$exists": False}}
    pending = await db.rag_chunks.find(q, {"chunk_id": 1, "text": 1}).limit(batch_size).to_list(length=batch_size)
    done = 0
    for ch in pending:
        vec = await _embed(ch["text"])
        if vec is None:
            continue
        await db.rag_chunks.update_one(
            {"chunk_id": ch["chunk_id"]},
            {"$set": {"embedding": vec, "embed_dim": len(vec)}},
        )
        done += 1
    return done


async def search(
    user_id: str, query: str, *,
    top_k: int = 5, doc_ids: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Cosine-similarity search over this user's rag_chunks."""
    from db import db
    # Ensure chunks are embedded
    await embed_pending_chunks(user_id, batch_size=500)
    q_vec = await _embed(query)
    if q_vec is None:
        return []
    q: dict[str, Any] = {"user_id": user_id, "embedding": {"$exists": True}}
    if doc_ids:
        q["doc_id"] = {"$in": doc_ids}
    cursor = db.rag_chunks.find(
        q, {"_id": 0, "chunk_id": 1, "doc_id": 1, "text": 1,
            "page": 1, "section": 1, "embedding": 1},
    )
    results: list[dict] = []
    async for ch in cursor:
        vec = ch.get("embedding")
        if not vec:
            continue
        score = _cosine(q_vec, vec)
        results.append({
            "chunk_id": ch["chunk_id"],
            "doc_id":   ch["doc_id"],
            "text":     ch["text"],
            "page":     ch.get("page"),
            "section":  ch.get("section"),
            "score":    round(score, 4),
        })
    results.sort(key=lambda r: r["score"], reverse=True)
    return results[: max(1, min(int(top_k), 25))]
