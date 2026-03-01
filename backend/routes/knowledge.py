"""Knowledge Base API routes for MAARS Command RAG system."""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from typing import Optional
import uuid
import logging
import asyncio
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

router = APIRouter()

UPLOAD_DIR = Path(__file__).parent.parent / "uploads"


async def process_document_async(db, doc_id: str, agent_id: str, file_path: str, filename: str, api_key: str):
    """Background task to process a document: extract text, chunk, embed, store."""
    try:
        from services.rag_service import extract_text_from_pdf, chunk_text, generate_embeddings_batch

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

        # Generate embeddings
        chunk_texts = [c["text"] for c in chunks]
        embeddings = await generate_embeddings_batch(chunk_texts, api_key)

        # Store chunks with embeddings
        chunk_docs = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            doc_meta = await db.knowledge_docs.find_one({"doc_id": doc_id}, {"_id": 0, "title": 1})
            chunk_docs.append({
                "chunk_id": f"chunk_{uuid.uuid4().hex[:10]}",
                "doc_id": doc_id,
                "agent_id": agent_id,
                "doc_title": doc_meta.get("title", filename) if doc_meta else filename,
                "text": chunk["text"],
                "pages": chunk.get("pages", []),
                "chunk_index": i,
                "embedding": embedding,
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
