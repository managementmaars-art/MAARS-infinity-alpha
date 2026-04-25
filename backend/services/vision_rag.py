"""Vision-first document retrieval via ColiVara (hosted ColPali).

Pattern from deepseek-multimodal-RAG + Colivara-deepseek-website-RAG:
for PDFs, scanned docs, slides, charts — skip OCR/text-chunking entirely.
Rendered page images go through ColPali's late-interaction encoder.
Retrieval returns page images; a vision LLM (Gemini / Claude / GPT-4o)
answers directly from the visual content.

Required env:
  COLIVARA_API_KEY   — https://colivara.com signup → API keys page
  (or) COLIVARA_BASE_URL for self-hosted

Public API:
  ingest_document(user_id, file_path, collection="default")
  vision_search(user_id, query, top_k=5, collection=None)
  answer_with_vision(user_id, query, collection=None, model="gemini/...")

Persists to db.colivara_docs so we know what's indexed remotely.
"""
from __future__ import annotations
import base64
import logging
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_API = "https://api.colivara.com/v1"


def _key() -> str | None:
    return os.environ.get("COLIVARA_API_KEY")


async def ingest_document(
    *, user_id: str, file_path: str,
    collection: str = "default",
) -> dict[str, Any]:
    """Upload a PDF/image to ColiVara. ColiVara renders each page,
    embeds it with ColPali, and indexes to Qdrant on their side."""
    key = _key()
    if not key:
        return {"ok": False, "error": "no_colivara_api_key"}
    p = Path(file_path)
    if not p.exists():
        return {"ok": False, "error": "file_not_found"}
    import httpx
    async with httpx.AsyncClient(timeout=300) as client:
        # Encode file as base64; ColiVara accepts base64-in-JSON uploads
        b64 = base64.b64encode(p.read_bytes()).decode("ascii")
        r = await client.post(
            f"{_API}/documents/upsert",
            headers={"Authorization": f"Bearer {key}",
                     "Content-Type":  "application/json"},
            json={
                "name":            p.name,
                "collection_name": f"{user_id}__{collection}",
                "document_base64": b64,
                "metadata":        {"source": "maars", "user_id": user_id},
            },
        )
    if r.status_code >= 400:
        return {"ok": False, "error": f"colivara_error: {r.status_code} {r.text[:300]}"}
    data = r.json() or {}
    doc_id = data.get("id") or data.get("document_id") or f"cv_{uuid.uuid4().hex[:10]}"
    # Mirror in Mongo
    from db import db
    await db.colivara_docs.insert_one({
        "doc_id":      doc_id,
        "user_id":     user_id,
        "name":        p.name,
        "collection":  collection,
        "colivara_id": data.get("id"),
        "pages":       data.get("num_pages"),
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
    })
    return {"ok": True, "doc_id": doc_id, "name": p.name,
            "pages": data.get("num_pages")}


async def vision_search(
    *, user_id: str, query: str, top_k: int = 5,
    collection: str | None = None,
) -> list[dict[str, Any]]:
    """Retrieve matching PAGES (as images) for a query."""
    key = _key()
    if not key:
        return []
    import httpx
    coll_name = f"{user_id}__{collection or 'default'}"
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(
            f"{_API}/search",
            headers={"Authorization": f"Bearer {key}",
                     "Content-Type":  "application/json"},
            json={"query": query, "collection_name": coll_name, "top_k": top_k},
        )
    if r.status_code >= 400:
        return []
    data = r.json() or {}
    results = data.get("results") or []
    out: list[dict] = []
    for rez in results:
        out.append({
            "doc_id":    rez.get("document_id") or rez.get("id"),
            "page":      rez.get("page_num"),
            "score":     rez.get("score"),
            "image_b64": rez.get("image"),  # base64 page render
            "text_ocr":  rez.get("text"),   # OCR'd text if available
        })
    return out


async def answer_with_vision(
    *, user_id: str, query: str,
    collection: str | None = None,
    model: str = "gemini/gemini-2.5-flash",
    top_k: int = 3,
) -> dict[str, Any]:
    """Retrieve top pages → hand images to a vision LLM → synthesize."""
    hits = await vision_search(
        user_id=user_id, query=query, top_k=top_k, collection=collection,
    )
    if not hits:
        return {"ok": False, "error": "no_hits",
                "hint": "ingest documents first via ingest_document()"}
    # Build vision-capable message content
    content_parts: list[dict] = [{"type": "text", "text":
        f"Answer the query using ONLY these document pages. Cite [page N] inline.\n\nQUERY: {query}"}]
    for h in hits:
        if h.get("image_b64"):
            content_parts.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{h['image_b64']}"},
            })
    from services.llm_gateway import complete
    resp = await complete(
        user_id,
        messages=[{"role": "user", "content": content_parts}],
        model=model,
        max_tokens=1200, temperature=0.2,
        source="vision_rag.answer",
    )
    answer = ""
    try:
        answer = resp["choices"][0]["message"]["content"]
    except Exception:
        answer = ""
    return {
        "ok":        True,
        "answer":    answer,
        "citations": [
            {"ref": f"[p{h.get('page')}]", "doc_id": h.get("doc_id"),
             "page": h.get("page"), "score": h.get("score")}
            for h in hits
        ],
    }
