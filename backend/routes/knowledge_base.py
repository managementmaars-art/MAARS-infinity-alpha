"""Knowledge base CRUD endpoints."""
import uuid
import asyncio
import logging
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Request, UploadFile, File, Form
from db import db
from auth import get_current_user, User
from shared.constants import UPLOAD_DIR
from datetime import datetime, timezone

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/agents/{agent_id}/knowledge")
async def list_knowledge_docs(agent_id: str, current_user: User = Depends(get_current_user)):
    docs = await db.knowledge_docs.find(
        {"agent_id": agent_id}, {"_id": 0, "embedding": 0}
    ).sort("created_at", -1).to_list(100)
    return docs


@router.post("/agents/{agent_id}/knowledge/upload")
async def upload_knowledge_doc(
    agent_id: str,
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user)
):
    agent = await db.agents.find_one({"agent_id": agent_id}, {"_id": 0, "agent_id": 1})
    if not agent:
        raise HTTPException(404, "Agent not found")

    allowed_extensions = {".pdf", ".txt", ".md", ".csv", ".docx"}
    filename = file.filename or "document"
    ext = Path(filename).suffix.lower()
    if ext not in allowed_extensions:
        raise HTTPException(400, f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}")

    contents = await file.read()
    if len(contents) > 25 * 1024 * 1024:
        raise HTTPException(400, "File too large. Max 25MB.")

    file_id = uuid.uuid4().hex[:10]
    saved_filename = f"kb_{file_id}_{filename}"
    filepath = UPLOAD_DIR / saved_filename
    with open(filepath, "wb") as f:
        f.write(contents)

    doc_id = f"doc_{uuid.uuid4().hex[:12]}"
    doc_title = title or Path(filename).stem.replace("_", " ").replace("-", " ").title()

    doc_record = {
        "doc_id": doc_id,
        "agent_id": agent_id,
        "title": doc_title,
        "filename": filename,
        "saved_filename": saved_filename,
        "file_size": len(contents),
        "file_type": ext,
        "status": "queued",
        "chunk_count": 0,
        "uploaded_by": current_user.user_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.knowledge_docs.insert_one(doc_record)

    from routes.knowledge import process_document_async
    asyncio.create_task(process_document_async(
        db, doc_id, agent_id, str(filepath), filename
    ))

    return {
        "doc_id": doc_id,
        "title": doc_title,
        "status": "queued",
        "message": "Document uploaded. Processing will begin shortly.",
    }


@router.delete("/agents/{agent_id}/knowledge/{doc_id}")
async def delete_knowledge_doc(agent_id: str, doc_id: str, current_user: User = Depends(get_current_user)):
    doc = await db.knowledge_docs.find_one({"doc_id": doc_id, "agent_id": agent_id})
    if not doc:
        raise HTTPException(404, "Document not found")
    saved = doc.get("saved_filename")
    if saved:
        fpath = UPLOAD_DIR / saved
        if fpath.exists():
            fpath.unlink()
    await db.knowledge_chunks.delete_many({"doc_id": doc_id})
    await db.knowledge_docs.delete_one({"doc_id": doc_id})
    return {"message": "Document deleted", "doc_id": doc_id}


@router.get("/agents/{agent_id}/knowledge/{doc_id}")
async def get_knowledge_doc_detail(agent_id: str, doc_id: str, current_user: User = Depends(get_current_user)):
    doc = await db.knowledge_docs.find_one(
        {"doc_id": doc_id, "agent_id": agent_id}, {"_id": 0}
    )
    if not doc:
        raise HTTPException(404, "Document not found")
    chunk_count = await db.knowledge_chunks.count_documents({"doc_id": doc_id})
    doc["chunk_count"] = chunk_count
    return doc


@router.post("/agents/{agent_id}/knowledge/search")
async def search_agent_knowledge(agent_id: str, request: Request, current_user: User = Depends(get_current_user)):
    body = await request.json()
    query = body.get("query", "")
    if not query:
        raise HTTPException(400, "Query is required")
    from services.rag_service import search_knowledge_base
    results = await search_knowledge_base(
        db, agent_id, query, top_k=5, threshold=0.05
    )
    return {"results": results, "count": len(results)}
