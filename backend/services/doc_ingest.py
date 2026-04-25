"""Document ingestion — layout-aware parsing with Docling fallback.

For now a lightweight wrapper: if `docling` is installed (IBM's
table-preserving parser), use it; otherwise fall back to pypdf for
PDFs and plain-text read for others. Either way, returns a uniform
`{doc_id, chunks: [{chunk_id, text, page, section}]}` shape.

Chunks are stored in `db.rag_docs` and `db.rag_chunks`. The
`agentic_rag` service reads from these collections.
"""
from __future__ import annotations
import hashlib
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def _chunk_text(text: str, max_chars: int = 1800, overlap: int = 150) -> list[str]:
    """Simple sliding-window chunker. Good enough for the 80% case."""
    if not text:
        return []
    text = text.strip()
    if len(text) <= max_chars:
        return [text]
    out: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        # Try to cut on a paragraph boundary near the end
        if end < len(text):
            nl = text.rfind("\n\n", start, end)
            if nl > start + max_chars // 2:
                end = nl
        out.append(text[start:end].strip())
        start = max(start + 1, end - overlap)
    return [c for c in out if c]


def _parse_with_docling(path: Path) -> list[dict[str, Any]]:
    """Use IBM Docling for layout-aware chunking (tables, headings).
    Returns [] when docling isn't installed so caller falls through."""
    try:
        from docling.document_converter import DocumentConverter
    except ImportError:
        return []
    try:
        conv = DocumentConverter()
        result = conv.convert(str(path))
        doc = result.document
        out: list[dict] = []
        for item in doc.iterate_items():
            text = getattr(item, "text", None) or ""
            if not text.strip():
                continue
            out.append({
                "text":    text,
                "section": getattr(item, "label", "body"),
                "page":    getattr(item, "page", None),
            })
        return out
    except Exception as exc:
        logger.info("docling parse failed, falling back: %s", exc)
        return []


def _parse_with_pypdf(path: Path) -> list[dict[str, Any]]:
    try:
        from pypdf import PdfReader
    except ImportError:
        return []
    try:
        reader = PdfReader(str(path))
        out: list[dict] = []
        for i, page in enumerate(reader.pages):
            txt = (page.extract_text() or "").strip()
            if not txt:
                continue
            for chunk in _chunk_text(txt):
                out.append({"text": chunk, "section": "body", "page": i + 1})
        return out
    except Exception as exc:
        logger.info("pypdf parse failed: %s", exc)
        return []


async def ingest_file(
    *, user_id: str, file_path: str, title: str | None = None,
    metadata: dict | None = None,
) -> dict[str, Any]:
    """Parse → chunk → persist to Mongo. Returns doc summary."""
    from db import db
    p = Path(file_path)
    if not p.exists():
        return {"ok": False, "error": "file_not_found"}
    # Try docling first (best for tables/PDF structure), then pypdf, then text
    items = _parse_with_docling(p)
    if not items and p.suffix.lower() == ".pdf":
        items = _parse_with_pypdf(p)
    if not items:
        try:
            txt = p.read_text(encoding="utf-8", errors="replace")
            items = [{"text": c, "section": "body", "page": None}
                     for c in _chunk_text(txt)]
        except Exception as exc:
            return {"ok": False, "error": f"read_failed: {exc}"}
    if not items:
        return {"ok": False, "error": "no_extractable_text"}

    doc_id = f"doc_{uuid.uuid4().hex[:12]}"
    now = datetime.now(timezone.utc).isoformat()
    await db.rag_docs.insert_one({
        "doc_id":     doc_id,
        "user_id":    user_id,
        "title":      title or p.name,
        "source_path": str(p),
        "chunk_count": len(items),
        "parser":     "docling" if _parse_with_docling.__name__ else "fallback",
        "metadata":   metadata or {},
        "created_at": now,
    })
    chunks_docs = []
    for i, item in enumerate(items):
        cid = f"ch_{doc_id[4:]}_{i:04d}"
        chunks_docs.append({
            "chunk_id":  cid,
            "doc_id":    doc_id,
            "user_id":   user_id,
            "index":     i,
            "text":      item["text"],
            "section":   item.get("section"),
            "page":      item.get("page"),
            "text_hash": hashlib.sha1(item["text"].encode("utf-8")).hexdigest()[:16],
            "created_at": now,
        })
    if chunks_docs:
        await db.rag_chunks.insert_many(chunks_docs)
    return {"ok": True, "doc_id": doc_id, "chunks": len(chunks_docs),
            "title": title or p.name}


async def ingest_text(
    *, user_id: str, text: str, title: str | None = None,
    metadata: dict | None = None,
) -> dict[str, Any]:
    """Ingest a raw-text blob (e.g. scraped page)."""
    from db import db
    if not text.strip():
        return {"ok": False, "error": "empty_text"}
    doc_id = f"doc_{uuid.uuid4().hex[:12]}"
    now = datetime.now(timezone.utc).isoformat()
    chunks = _chunk_text(text)
    await db.rag_docs.insert_one({
        "doc_id":      doc_id,
        "user_id":     user_id,
        "title":       title or "untitled",
        "chunk_count": len(chunks),
        "parser":      "text",
        "metadata":    metadata or {},
        "created_at":  now,
    })
    chunks_docs = [{
        "chunk_id":  f"ch_{doc_id[4:]}_{i:04d}",
        "doc_id":    doc_id,
        "user_id":   user_id,
        "index":     i,
        "text":      c,
        "section":   "body",
        "page":      None,
        "text_hash": hashlib.sha1(c.encode("utf-8")).hexdigest()[:16],
        "created_at": now,
    } for i, c in enumerate(chunks)]
    if chunks_docs:
        await db.rag_chunks.insert_many(chunks_docs)
    return {"ok": True, "doc_id": doc_id, "chunks": len(chunks_docs),
            "title": title or "untitled"}


async def list_docs(user_id: str, limit: int = 100) -> list[dict]:
    from db import db
    cursor = db.rag_docs.find(
        {"user_id": user_id}, {"_id": 0},
    ).sort("created_at", -1).limit(limit)
    return await cursor.to_list(length=limit)


async def delete_doc(user_id: str, doc_id: str) -> dict:
    from db import db
    d = await db.rag_docs.delete_one({"user_id": user_id, "doc_id": doc_id})
    c = await db.rag_chunks.delete_many({"user_id": user_id, "doc_id": doc_id})
    return {"ok": bool(d.deleted_count),
            "doc_deleted": d.deleted_count, "chunks_deleted": c.deleted_count}
