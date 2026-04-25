"""Corrective RAG workflow — retrieve → grade → (web-fallback) → synthesize.

Implements the agentic-RAG pattern from `firecrawl-agent` + `paralegal-
agent-crew` + `context-engineering-workflow`:

  1. Retrieve top-K chunks from `vector_store.search()`
  2. Grade each chunk's relevance (cheap classifier via `evaluator`)
  3. If the kept set is thin/empty, fall back to web search
  4. Synthesize an answer with citations + confidence

Returns:
  {
    answer:     "...",
    citations:  [{doc_id, chunk_id, page, section, score}],
    sources_used: ["rag"|"web"],
    confidence: 0-1,
    raw_retrieved: N,
    raw_kept:     M,
  }
"""
from __future__ import annotations
import logging
from typing import Any

logger = logging.getLogger(__name__)


async def _web_fallback(query: str, top_k: int = 5) -> list[dict[str, Any]]:
    """Best-effort web search for corrective-RAG fallback. Uses the
    existing MAARS web_search service which returns a list of dicts with
    {title, url, snippet, content?}."""
    try:
        from services.web_search import web_search
        results = await web_search(query, max_results=top_k)
    except Exception as exc:
        logger.info("web_search unavailable: %s", exc)
        return []
    out: list[dict] = []
    for i, r in enumerate(results or []):
        if not isinstance(r, dict):
            continue
        out.append({
            "chunk_id": f"web_{i}",
            "doc_id":   "web",
            "text":     r.get("snippet") or r.get("content") or r.get("title", ""),
            "page":     None,
            "section":  "web",
            "score":    None,
            "url":      r.get("url") or r.get("link"),
            "title":    r.get("title"),
        })
    return out


async def corrective_rag(
    *, user_id: str, query: str,
    doc_ids: list[str] | None = None,
    top_k: int = 8,
    min_relevance: float = 0.55,
    min_keep_count: int = 2,
    enable_web_fallback: bool = True,
    synth_model: str = "maars/auto",
    agent_id: str | None = None,
) -> dict[str, Any]:
    from services import vector_store
    from services.workflows.workflow_executor import _t_evaluator
    from services.llm_gateway import complete_text

    # 1. Retrieve
    retrieved = await vector_store.search(user_id, query, top_k=top_k, doc_ids=doc_ids)
    raw_count = len(retrieved)

    # 2. Grade
    eval_result = await _t_evaluator(
        user_id,
        params={
            "items": retrieved,
            "query": query,
            "min_score": min_relevance,
            "keep_top": top_k,
        },
        inp={},
    )
    kept = eval_result.get("kept") or []
    sources_used = ["rag"] if kept else []

    # 3. Web fallback if too thin
    if len(kept) < min_keep_count and enable_web_fallback:
        web = await _web_fallback(query, top_k=5)
        if web:
            # Grade web results the same way
            web_eval = await _t_evaluator(
                user_id,
                params={"items": web, "query": query,
                        "min_score": max(0.3, min_relevance - 0.15),
                        "keep_top": 5},
                inp={},
            )
            web_kept = web_eval.get("kept") or []
            if web_kept:
                kept.extend(web_kept)
                sources_used.append("web")

    # 4. Synthesize with citations
    if not kept:
        return {
            "answer":      "No relevant information found in your documents or on the web.",
            "citations":   [],
            "sources_used": sources_used,
            "confidence":  0.0,
            "raw_retrieved": raw_count,
            "raw_kept":    0,
        }
    context_lines = []
    cite_refs = []
    for i, c in enumerate(kept[:10], 1):
        text = c.get("text") or c.get("content") or ""
        cite_refs.append({
            "ref":       f"[{i}]",
            "doc_id":    c.get("doc_id"),
            "chunk_id":  c.get("chunk_id"),
            "page":      c.get("page"),
            "section":   c.get("section"),
            "score":     c.get("relevance_score") or c.get("score"),
            "url":       c.get("url"),
            "title":     c.get("title"),
        })
        context_lines.append(f"[{i}] {text}")
    context_block = "\n\n".join(context_lines)

    prompt = (
        f"Answer the QUERY using ONLY the CONTEXT chunks below. "
        f"Cite sources inline with [1], [2] etc matching the chunk numbers. "
        f"If context is insufficient, say so explicitly.\n\n"
        f"QUERY:\n{query}\n\n"
        f"CONTEXT:\n{context_block}"
    )
    answer = await complete_text(
        user_id,
        system_prompt=(
            "You are a grounded research assistant. Answer only from the "
            "provided context; never fabricate. Always cite sources inline."
        ),
        user_prompt=prompt,
        model=synth_model,
        max_tokens=1200, temperature=0.2,
        source="rag_workflow.synthesize",
        agent_id=agent_id,
    )

    # Confidence heuristic: mean relevance score of kept chunks
    relevance_scores = [
        (c.get("relevance_score") or c.get("score") or 0.0)
        for c in kept
    ]
    confidence = (
        sum(relevance_scores) / len(relevance_scores)
        if relevance_scores else 0.0
    )

    return {
        "answer":         answer,
        "citations":      cite_refs,
        "sources_used":   sources_used,
        "confidence":     round(confidence, 3),
        "raw_retrieved":  raw_count,
        "raw_kept":       len(kept),
    }
