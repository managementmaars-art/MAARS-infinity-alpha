"""HyDE — Hypothetical Document Embeddings for retrieval.

Gao et al. 2022: instead of embedding the QUERY and searching a doc
store, ask the LLM to HALLUCINATE a plausible answer, then embed THAT
and search. Why it works: the hallucination sits in the same "answer"
region of embedding space as real docs, so cosine similarity is better
than query-vs-doc (which compares question-shape to answer-shape).

Reported retrieval recall@5 improvement: 7-15% on BEIR benchmarks at
roughly 2× cost (one extra cheap LLM call per search).

Use from RAG callers:
    hypo = await generate_hypothetical(query, complete_fn, user_id)
    embedding_to_search = await embed(hypo)
    results = vector_store.search(embedding_to_search)
"""
from __future__ import annotations
import logging
from typing import Any, Awaitable, Callable

logger = logging.getLogger(__name__)


_HYDE_SYSTEM = (
    "You are given a user question. Write a brief, plausible answer that "
    "a well-informed assistant MIGHT give. It does not need to be correct — "
    "its role is to match the STYLE and CONTENT of real passages that would "
    "answer this question. Keep it 2-4 sentences, no preamble."
)


async def generate_hypothetical(
    query: str,
    complete_fn: Callable[..., Awaitable[Any]],
    user_id: str,
    *,
    model: str = "maars/economy",
) -> str:
    """Produce the hypothetical answer. Empty string on failure → caller
    falls back to embedding the query directly."""
    try:
        r = await complete_fn(
            user_id,
            messages=[
                {"role": "system", "content": _HYDE_SYSTEM},
                {"role": "user",   "content": query},
            ],
            model=model,
            temperature=0.3,
            max_tokens=200,
            source="hyde_retrieval",
            enable_cache=True,
            verify_injection=False,
        )
        return r["choices"][0]["message"]["content"].strip()
    except Exception as exc:
        logger.info("hyde generate failed, caller should fall back: %s", exc)
        return ""


async def embed_hypothetical(query: str, complete_fn, user_id: str) -> list[float] | None:
    """One-liner: generate hypothetical + embed it. Returns the embedding
    vector (list[float]) or None on failure."""
    hypo = await generate_hypothetical(query, complete_fn, user_id)
    if not hypo:
        hypo = query  # graceful fallback
    try:
        from services.semantic_cache import _embed
        return await _embed(hypo)
    except Exception:
        return None
