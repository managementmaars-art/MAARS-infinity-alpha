"""Content-level router.

Sits BEFORE the model-level `smart_router`. A cheap classifier decides
where to look for the answer:
  • direct     — no retrieval, just pass to the LLM
  • rag        — user has docs; search those via `vector_store`
  • web        — web search fallback
  • sql        — SQL-like structured query (future)

Returns a mode + optional pre-retrieved context the caller can inject
into the prompt. Stays out of `llm_gateway.complete()`'s hot path —
callers that want retrieval opt in by calling `route_query()` first
and attaching the context to their messages.
"""
from __future__ import annotations
import json
import logging
import re
from typing import Any

logger = logging.getLogger(__name__)


async def classify(query: str, user_id: str) -> dict[str, Any]:
    """Cheap classifier. Returns {mode, reasoning}. Falls back to
    'direct' on any parsing failure so workflows never block on this."""
    from services.llm_gateway import complete_text
    try:
        raw = await complete_text(
            user_id,
            system_prompt=(
                "Classify where the answer to the query should come from. "
                "Reply ONLY with JSON: "
                '{"mode": "direct"|"rag"|"web"|"sql", "reasoning": "<1 sentence>"}'
            ),
            user_prompt=(
                f"QUERY: {query}\n\n"
                "modes:\n"
                "  direct — general knowledge, creative writing, reasoning\n"
                "  rag    — user is asking about their own documents / internal data\n"
                "  web    — current events, latest prices, live data, today's news\n"
                "  sql    — structured query over records / analytics / counts"
            ),
            model="maars/auto",
            max_tokens=150, temperature=0.0,
            source="retrieval_router.classify",
            enable_cache=True,
        )
    except Exception as exc:
        logger.info("retrieval_router classify failed: %s", exc)
        return {"mode": "direct", "reasoning": f"classify_failed: {exc}"}
    m = re.search(r"\{[\s\S]*\}", raw or "")
    try:
        parsed = json.loads(m.group(0)) if m else {}
    except Exception:
        parsed = {}
    mode = (parsed.get("mode") or "direct").lower()
    if mode not in ("direct", "rag", "web", "sql"):
        mode = "direct"
    return {"mode": mode,
            "reasoning": (parsed.get("reasoning") or "")[:200]}


async def route_query(
    *, user_id: str, query: str,
    prefer_rag_if_docs_exist: bool = True,
    include_context: bool = True,
) -> dict[str, Any]:
    """Full route: classify → (optionally) pre-retrieve → return context.

    Returns:
      {
        mode:       "direct"|"rag"|"web"|"sql",
        context:    str (ready to inject into a prompt) or "",
        citations:  [...] or [],
        retrieved_from: same as mode when context present
      }
    """
    cls = await classify(query, user_id)
    mode = cls["mode"]

    # If user has documents ingested, prefer rag even when classifier says direct
    if prefer_rag_if_docs_exist and mode == "direct":
        try:
            from db import db
            has_docs = await db.rag_docs.count_documents({"user_id": user_id}) > 0
            if has_docs:
                mode = "rag"
                cls["reasoning"] = (
                    (cls.get("reasoning") or "") + " [upgraded to rag: user has indexed docs]"
                )
        except Exception:
            pass

    context = ""
    citations: list[dict] = []
    if include_context and mode == "rag":
        try:
            from services.rag_workflow import corrective_rag
            rag = await corrective_rag(
                user_id=user_id, query=query,
                enable_web_fallback=False,
                synth_model="maars/auto",
            )
            citations = rag.get("citations") or []
            context = "\n\n".join(
                f"[{i+1}] {c.get('text','')[:800]}"
                for i, c in enumerate(
                    (rag.get("raw_kept_chunks") or [])[:5]
                    or (rag.get("citations") or [])[:5]
                )
            )
        except Exception as exc:
            logger.info("rag pre-retrieval skipped: %s", exc)
    elif include_context and mode == "web":
        try:
            from services.web_search import web_search
            items = await web_search(query, max_results=5)
            if items:
                parts = []
                for i, r in enumerate(items, 1):
                    if not isinstance(r, dict):
                        continue
                    parts.append(
                        f"[{i}] {r.get('title','')}\n{r.get('snippet') or r.get('content','')}"
                    )
                    citations.append({
                        "ref": f"[{i}]", "url": r.get("url") or r.get("link"),
                        "title": r.get("title"),
                    })
                context = "\n\n".join(parts)
        except Exception as exc:
            logger.info("web pre-retrieval skipped: %s", exc)

    return {
        "mode":           mode,
        "reasoning":      cls.get("reasoning"),
        "context":        context,
        "citations":      citations,
        "retrieved_from": mode if context else None,
    }
