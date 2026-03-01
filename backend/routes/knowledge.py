"""Knowledge Base API routes - document processing background tasks."""

import uuid
import logging
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)


async def process_document_async(db, doc_id: str, agent_id: str, file_path: str, filename: str, api_key: str):
    """Background task to process a document: extract text, chunk, store."""
    try:
        from services.rag_service import extract_text_from_pdf, chunk_text

        await db.knowledge_docs.update_one(
            {"doc_id": doc_id}, {"$set": {"status": "processing"}}
        )

        # Extract text
        if filename.lower().endswith(".pdf"):
            text = extract_text_from_pdf(file_path)
        else:
            with open(file_path, "r", errors="ignore") as f:
                text = f.read()

        if not text.strip():
            await db.knowledge_docs.update_one(
                {"doc_id": doc_id}, {"$set": {"status": "error", "error": "No text extracted from document"}}
            )
            return

        # Chunk
        chunks = chunk_text(text)
        logger.info(f"Document {doc_id}: extracted {len(text)} chars, {len(chunks)} chunks")

        # Get doc title
        doc_meta = await db.knowledge_docs.find_one({"doc_id": doc_id}, {"_id": 0, "title": 1})
        doc_title = doc_meta.get("title", filename) if doc_meta else filename

        # Store chunks (no embeddings needed - TF-IDF computes at query time)
        chunk_docs = []
        for i, chunk in enumerate(chunks):
            chunk_docs.append({
                "chunk_id": f"chunk_{uuid.uuid4().hex[:10]}",
                "doc_id": doc_id,
                "agent_id": agent_id,
                "doc_title": doc_title,
                "text": chunk["text"],
                "pages": chunk.get("pages", []),
                "chunk_index": i,
                "created_at": datetime.now(timezone.utc).isoformat(),
            })

        if chunk_docs:
            await db.knowledge_chunks.insert_many(chunk_docs)

        # Update doc status
        await db.knowledge_docs.update_one(
            {"doc_id": doc_id},
            {"$set": {
                "status": "ready",
                "chunk_count": len(chunks),
                "text_length": len(text),
                "processed_at": datetime.now(timezone.utc).isoformat(),
            }}
        )
        logger.info(f"Document {doc_id} processed: {len(chunks)} chunks stored")

    except Exception as e:
        logger.error(f"Document processing failed for {doc_id}: {e}")
        await db.knowledge_docs.update_one(
            {"doc_id": doc_id}, {"$set": {"status": "error", "error": str(e)[:500]}}
        )
