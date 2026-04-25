"""Cross-encoder reranker — second-pass scoring of retrieval candidates.

Bi-encoder retrieval (what `semantic_cache._embed` does) is fast but
approximates relevance by cosine-of-independent-embeddings. A cross-
encoder reads the query AND each candidate together and scores them
jointly — slower but systematically better ranking.

Cohere's published numbers: cross-encoder rerank on top-50 bi-encoder
candidates lifts recall@3 by 10-25 points on TREC-DL. That's the
difference between "retrieved the right doc but ranked it 8th" and
"returned it first."

We implement two backends:

  1. Cohere /rerank       — one API call, handles the scoring model for us.
                            Uses rerank-multilingual-v3.0 (128 lang).
  2. LLM-judge reranker   — fallback: ask maars/economy to score
                            query-candidate pairs 0-10. ~10× slower
                            than Cohere, but no new dependency.

Caller passes query + candidate list; we return candidates reordered
with a `rerank_score` field attached.
"""
from __future__ import annotations
import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable

logger = logging.getLogger(__name__)


@dataclass
class RerankedHit:
    text: str
    meta: dict[str, Any] = field(default_factory=dict)
    rerank_score: float = 0.0


async def rerank_with_cohere(
    query: str,
    candidates: list[str],
    *,
    top_n: int = 10,
    model: str = "rerank-multilingual-v3.0",
) -> list[RerankedHit]:
    """Uses the Cohere rerank endpoint. Falls through to LLM judge on error."""
    from shared.utils import get_api_keys
    keys = await get_api_keys()
    cohere_key = keys.get("cohere") if isinstance(keys, dict) else None
    if not cohere_key:
        return []
    try:
        from services.http_client import get_client
        client = await get_client()
        r = await client.post(
            "https://api.cohere.com/v2/rerank",
            headers={
                "Authorization": f"Bearer {cohere_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "query": query,
                "documents": candidates,
                "top_n": min(top_n, len(candidates)),
            },
            timeout=20,
        )
        r.raise_for_status()
        data = r.json()
    except Exception as exc:
        logger.info("cohere rerank failed: %s", exc)
        return []
    results = data.get("results") or []
    return [
        RerankedHit(
            text=candidates[hit["index"]],
            rerank_score=float(hit.get("relevance_score", 0.0)),
        )
        for hit in results
    ]


async def rerank_with_llm(
    query: str,
    candidates: list[str],
    *,
    complete_fn: Callable[..., Awaitable[Any]],
    user_id: str,
    top_n: int = 10,
    model: str = "maars/economy",
) -> list[RerankedHit]:
    """Fallback: cheap LLM scores each candidate 0-10."""
    system = (
        "Score how relevant the PASSAGE is to the QUERY on a 0-10 scale. "
        "Reply with ONLY the number. No prose."
    )

    async def _score(cand: str) -> float:
        try:
            r = await complete_fn(
                user_id,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user",   "content": f"QUERY: {query[:400]}\n\nPASSAGE: {cand[:2000]}"},
                ],
                model=model, temperature=0.0, max_tokens=5,
                source="reranker_llm", enable_cache=False, verify_injection=False,
            )
            txt = r["choices"][0]["message"]["content"].strip()
            # Pull leading number.
            num = ""
            for ch in txt:
                if ch.isdigit() or ch == ".":
                    num += ch
                elif num:
                    break
            return float(num) if num else 0.0
        except Exception:
            return 0.0

    scores = await asyncio.gather(*(_score(c) for c in candidates))
    ranked = sorted(
        zip(candidates, scores), key=lambda t: t[1], reverse=True
    )[:top_n]
    return [RerankedHit(text=t, rerank_score=s) for t, s in ranked]


async def rerank(
    query: str,
    candidates: list[str],
    *,
    complete_fn: Callable[..., Awaitable[Any]] | None = None,
    user_id: str | None = None,
    top_n: int = 10,
) -> list[RerankedHit]:
    """Smart dispatch: Cohere first, LLM fallback, else pass-through."""
    if not candidates:
        return []
    hits = await rerank_with_cohere(query, candidates, top_n=top_n)
    if hits:
        return hits
    if complete_fn and user_id:
        return await rerank_with_llm(
            query, candidates,
            complete_fn=complete_fn, user_id=user_id, top_n=top_n,
        )
    # Final fallback: return candidates unranked.
    return [RerankedHit(text=c, rerank_score=0.0) for c in candidates[:top_n]]
