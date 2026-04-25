"""Client-facing + admin RAG endpoints.

All user-scoped: doc ingest/list/delete, corrective-RAG query,
memory-graph fact record/recall, SME-correction queue.
"""
from __future__ import annotations
import logging
import tempfile
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel

from auth import get_current_user
from models.schemas import User

logger = logging.getLogger(__name__)
router = APIRouter()


# ── Document ingest ────────────────────────────────────────────────

@router.post("/rag/ingest")
async def rag_ingest(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
):
    from services import doc_ingest
    suffix = Path(file.filename or "").suffix or ".bin"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        path = tmp.name
    try:
        return await doc_ingest.ingest_file(
            user_id=current_user.user_id,
            file_path=path,
            title=title or file.filename,
        )
    finally:
        try:
            Path(path).unlink(missing_ok=True)
        except Exception:
            pass


class _TextIngest(BaseModel):
    text: str
    title: Optional[str] = None


@router.post("/rag/ingest-text")
async def rag_ingest_text(body: _TextIngest, current_user: User = Depends(get_current_user)):
    from services import doc_ingest
    return await doc_ingest.ingest_text(
        user_id=current_user.user_id, text=body.text, title=body.title,
    )


@router.get("/rag/documents")
async def rag_documents(current_user: User = Depends(get_current_user)):
    from services import doc_ingest
    return {"docs": await doc_ingest.list_docs(current_user.user_id)}


@router.delete("/rag/documents/{doc_id}")
async def rag_document_delete(doc_id: str, current_user: User = Depends(get_current_user)):
    from services import doc_ingest
    return await doc_ingest.delete_doc(current_user.user_id, doc_id)


# ── Query ──────────────────────────────────────────────────────────

class _RagQuery(BaseModel):
    query: str
    doc_ids: Optional[list[str]] = None
    top_k: int = 8
    enable_web_fallback: bool = True
    agent_id: Optional[str] = None


@router.post("/rag/query")
async def rag_query(body: _RagQuery, current_user: User = Depends(get_current_user)):
    from services import rag_workflow
    return await rag_workflow.corrective_rag(
        user_id=current_user.user_id,
        query=body.query,
        doc_ids=body.doc_ids,
        top_k=body.top_k,
        enable_web_fallback=body.enable_web_fallback,
        agent_id=body.agent_id,
    )


# ── Memory graph ────────────────────────────────────────────────────

class _FactIn(BaseModel):
    subject: str
    predicate: str
    object: Any
    topic: Optional[str] = None
    agent_id: Optional[str] = None


@router.post("/memory/facts")
async def memory_record(body: _FactIn, current_user: User = Depends(get_current_user)):
    from services import memory_graph
    return await memory_graph.record_fact(
        user_id=current_user.user_id,
        subject=body.subject, predicate=body.predicate, obj=body.object,
        topic=body.topic, agent_id=body.agent_id,
    )


@router.get("/memory/recall")
async def memory_recall(
    topic: Optional[str] = None,
    subject: Optional[str] = None,
    predicate: Optional[str] = None,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
):
    from services import memory_graph
    return {"facts": await memory_graph.recall(
        user_id=current_user.user_id, topic=topic,
        subject=subject, predicate=predicate, limit=limit,
    )}


class _ExtractIn(BaseModel):
    text: str
    agent_id: Optional[str] = None


@router.post("/memory/extract")
async def memory_extract(body: _ExtractIn, current_user: User = Depends(get_current_user)):
    from services import memory_graph
    return {"recorded": await memory_graph.extract_and_record(
        user_id=current_user.user_id, text=body.text, agent_id=body.agent_id,
    )}


# ── SME correction queue ────────────────────────────────────────────

@router.get("/sme/queue")
async def sme_queue(
    status: str = "pending", limit: int = 50,
    current_user: User = Depends(get_current_user),
):
    from services import sme_corrections
    return {"items": await sme_corrections.list_queue(
        status=status, limit=limit, user_id=current_user.user_id,
    )}


class _SmeApprove(BaseModel):
    correction_id: str
    corrected_answer: Optional[str] = None


@router.post("/sme/approve")
async def sme_approve(body: _SmeApprove, current_user: User = Depends(get_current_user)):
    from services import sme_corrections
    doc = await sme_corrections.approve(
        body.correction_id, corrected_answer=body.corrected_answer,
        reviewer=current_user.user_id,
    )
    if not doc:
        raise HTTPException(404, "not_found")
    return doc


class _SmeReject(BaseModel):
    correction_id: str


@router.post("/sme/reject")
async def sme_reject(body: _SmeReject, current_user: User = Depends(get_current_user)):
    from services import sme_corrections
    ok = await sme_corrections.reject(body.correction_id, reviewer=current_user.user_id)
    if not ok:
        raise HTTPException(404, "not_found")
    return {"ok": True}


# ── Eval harness ───────────────────────────────────────────────────

class _GoldenIn(BaseModel):
    prompt: str
    task: str = "general"
    reference: Optional[str] = None
    rubric: Optional[list[str]] = None


@router.post("/eval/golden")
async def eval_golden_add(body: _GoldenIn, current_user: User = Depends(get_current_user)):
    from services import eval_harness
    return await eval_harness.add_golden(
        prompt=body.prompt, task=body.task,
        reference=body.reference, rubric=body.rubric,
        updated_by=current_user.user_id,
    )


@router.get("/eval/golden")
async def eval_golden_list(task: Optional[str] = None,
                            current_user: User = Depends(get_current_user)):
    from services import eval_harness
    return {"items": await eval_harness.list_golden(task=task)}


class _EvalRunBody(BaseModel):
    models: list[str]
    judge_model: str = "maars/auto"
    pass_threshold: float = 0.7
    task: Optional[str] = None
    limit: int = 20


@router.post("/eval/run")
async def eval_run(body: _EvalRunBody, current_user: User = Depends(get_current_user)):
    from services import eval_harness
    return await eval_harness.run_eval(
        models=body.models, user_id=current_user.user_id,
        judge_model=body.judge_model,
        pass_threshold=body.pass_threshold,
        task=body.task, limit=body.limit,
    )


@router.get("/eval/latest")
async def eval_latest(current_user: User = Depends(get_current_user)):
    from services import eval_harness
    return {"summary": await eval_harness.latest_per_model()}


# ── Retrieval router ───────────────────────────────────────────────

class _RouteIn(BaseModel):
    query: str


@router.post("/retrieval/route")
async def retrieval_route(body: _RouteIn, current_user: User = Depends(get_current_user)):
    from services.routing import retrieval_router
    return await retrieval_router.route_query(
        user_id=current_user.user_id, query=body.query,
    )


# ── Video ingest (Gemini File API) ─────────────────────────────────

@router.post("/rag/video/upload")
async def rag_video_upload(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    from services import video_ingest
    import tempfile
    from pathlib import Path as _P
    suffix = _P(file.filename or "video.mp4").suffix or ".mp4"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        path = tmp.name
    try:
        return await video_ingest.upload_video(
            user_id=current_user.user_id, file_path=path,
            display_name=file.filename,
        )
    finally:
        try: _P(path).unlink(missing_ok=True)
        except Exception: pass


class _VideoAsk(BaseModel):
    file_id: str
    prompt: str


@router.post("/rag/video/analyze")
async def rag_video_analyze(body: _VideoAsk, current_user: User = Depends(get_current_user)):
    from services import video_ingest
    return await video_ingest.analyze_video(
        user_id=current_user.user_id, file_id=body.file_id, prompt=body.prompt,
    )


@router.get("/rag/videos")
async def rag_video_list(current_user: User = Depends(get_current_user)):
    from services import video_ingest
    return {"videos": await video_ingest.list_videos(current_user.user_id)}


@router.delete("/rag/videos/{file_id:path}")
async def rag_video_delete(file_id: str, current_user: User = Depends(get_current_user)):
    from services import video_ingest
    return {"ok": await video_ingest.delete_video(current_user.user_id, file_id)}


# ── GitIngest ─────────────────────────────────────────────────────

class _GitIn(BaseModel):
    repo_url: str
    max_bytes: int = 2_000_000


@router.post("/rag/gitingest")
async def rag_gitingest(body: _GitIn, current_user: User = Depends(get_current_user)):
    from services import git_ingest
    return await git_ingest.ingest_repo(
        user_id=current_user.user_id, repo_url=body.repo_url,
        max_bytes=body.max_bytes,
    )


# ── Fine-tuning pipeline scaffold ─────────────────────────────────

class _FinetuneExport(BaseModel):
    agent_id: Optional[str] = None
    min_examples: int = 20
    include_sources: Optional[list[str]] = None


@router.post("/finetune/export")
async def finetune_export(body: _FinetuneExport, current_user: User = Depends(get_current_user)):
    """Admin-scoped in practice; keeps simple auth for now since the
    export is read-only from Mongo."""
    from services import finetune_pipeline
    return await finetune_pipeline.export_dataset(
        agent_id=body.agent_id,
        min_examples=body.min_examples,
        include_sources=body.include_sources,
    )


@router.get("/finetune/preview")
async def finetune_preview(
    agent_id: Optional[str] = None,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
):
    from services import finetune_pipeline
    return {"preview": await finetune_pipeline.preview_dataset(
        agent_id=agent_id, limit=limit,
    )}


# ── Twitter OAuth1 credential storage ─────────────────────────────

class _TwitterOAuth1(BaseModel):
    consumer_key: str
    consumer_secret: str
    access_token: str
    access_token_secret: str


@router.post("/integrations/twitter/oauth1")
async def twitter_oauth1_store(body: _TwitterOAuth1, current_user: User = Depends(get_current_user)):
    """Store Twitter OAuth 1.0a user-context credentials (required for
    v1.1 media/upload). These sit alongside v2 bearer tokens in the
    credential vault under metadata.oauth1."""
    from services import credential_vault
    existing = await credential_vault.get("x", user_id=current_user.user_id)
    meta = (existing.metadata if existing else {}) or {}
    meta["oauth1"] = {
        "consumer_key":        body.consumer_key,
        "consumer_secret":     body.consumer_secret,
        "access_token":        body.access_token,
        "access_token_secret": body.access_token_secret,
    }
    cred = credential_vault.Credential(
        scope="user", scope_id=current_user.user_id,
        provider="x", kind=(existing.kind if existing else "oauth"),
        secret=(existing.secret if existing else ""),
        public=(existing.public if existing else {}),
        metadata=meta,
    )
    await credential_vault.put(cred)
    return {"ok": True, "provider": "x", "oauth1_configured": True}


# ── Webhook payload schema auto-generation ────────────────────────

@router.get("/workflows/{workflow_id}/webhook-schema")
async def workflow_webhook_schema(
    workflow_id: str,
    current_user: User = Depends(get_current_user),
):
    """Walk the most recent successful runs and infer a JSON-schema-ish
    shape for incoming webhook payloads. Useful when you forget what
    your upstream provider sends."""
    from db import db
    wf = await db.workflows.find_one({"workflow_id": workflow_id}, {"_id": 0})
    if not wf:
        raise HTTPException(404, "workflow_not_found")
    runs = await db.workflow_runs.find(
        {"workflow_id": workflow_id, "status": "completed"},
        {"_id": 0, "overrides": 1, "trigger": 1},
    ).sort("finished_at", -1).limit(20).to_list(length=20)
    schema: dict[str, Any] = {}
    seen_samples: list[dict] = []
    for r in runs:
        payload = (r.get("overrides") or {}).get("webhook_payload") or {}
        if isinstance(payload, dict):
            seen_samples.append(payload)
            _merge_schema(schema, payload)
    return {
        "workflow_id":    workflow_id,
        "samples_seen":   len(seen_samples),
        "inferred_schema": schema,
        "sample":         seen_samples[0] if seen_samples else None,
    }


# ── Meeting notes (AssemblyAI) ────────────────────────────────────

@router.post("/meetings/transcribe")
async def meetings_transcribe(
    file: UploadFile = File(...),
    language: str = Form("auto"),
    diarize: bool = Form(True),
    current_user: User = Depends(get_current_user),
):
    from services import transcription_pipeline
    import tempfile
    from pathlib import Path as _P
    suffix = _P(file.filename or "audio.mp3").suffix or ".mp3"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        path = tmp.name
    try:
        return await transcription_pipeline.transcribe_and_summarize(
            user_id=current_user.user_id, file_path=path,
            language=language, diarize=diarize,
            title=file.filename,
        )
    finally:
        try: _P(path).unlink(missing_ok=True)
        except Exception: pass


@router.get("/meetings")
async def meetings_list(current_user: User = Depends(get_current_user)):
    from services import transcription_pipeline
    return {"notes": await transcription_pipeline.list_notes(current_user.user_id)}


# ── Vision RAG (ColiVara) ─────────────────────────────────────────

@router.post("/vision-rag/ingest")
async def vision_rag_ingest(
    file: UploadFile = File(...),
    collection: str = Form("default"),
    current_user: User = Depends(get_current_user),
):
    from services import vision_rag
    import tempfile
    from pathlib import Path as _P
    suffix = _P(file.filename or "doc.pdf").suffix or ".pdf"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        path = tmp.name
    try:
        return await vision_rag.ingest_document(
            user_id=current_user.user_id, file_path=path, collection=collection,
        )
    finally:
        try: _P(path).unlink(missing_ok=True)
        except Exception: pass


class _VisionQuery(BaseModel):
    query: str
    collection: Optional[str] = None
    top_k: int = 3
    model: str = "gemini/gemini-2.5-flash"


@router.post("/vision-rag/query")
async def vision_rag_query(body: _VisionQuery, current_user: User = Depends(get_current_user)):
    from services import vision_rag
    return await vision_rag.answer_with_vision(
        user_id=current_user.user_id, query=body.query,
        collection=body.collection, top_k=body.top_k, model=body.model,
    )


# ── Voice (Cartesia + LiveKit) ────────────────────────────────────

class _VoiceRoom(BaseModel):
    room_name: str
    identity: Optional[str] = None


@router.post("/voice/room-token")
async def voice_room_token(body: _VoiceRoom, current_user: User = Depends(get_current_user)):
    from services import voice_stream
    return await voice_stream.issue_room_token(
        user_id=current_user.user_id, room_name=body.room_name,
        identity=body.identity,
    )


# ── Parlant journey turns ─────────────────────────────────────────

class _ParlantTurn(BaseModel):
    journey_id: str
    message: str
    session_id: Optional[str] = None


@router.post("/parlant/chat")
async def parlant_chat(body: _ParlantTurn, current_user: User = Depends(get_current_user)):
    from services import parlant_bridge
    return await parlant_bridge.chat(
        user_id=current_user.user_id,
        journey_id=body.journey_id, message=body.message, session_id=body.session_id,
    )


@router.get("/parlant/journeys")
async def parlant_journeys(current_user: User = Depends(get_current_user)):
    from services import parlant_bridge
    return {"journeys": await parlant_bridge.list_journeys()}


def _merge_schema(acc: dict, sample: dict, depth: int = 0) -> None:
    if depth > 4:
        return
    for k, v in (sample or {}).items():
        if isinstance(v, dict):
            acc.setdefault(k, {"type": "object", "fields": {}})
            if acc[k].get("type") != "object":
                acc[k] = {"type": "mixed", "seen": [acc[k].get("type"), "object"]}
            _merge_schema(acc[k]["fields"], v, depth + 1)
        elif isinstance(v, list):
            acc.setdefault(k, {"type": "array", "items": {}})
            if v and isinstance(v[0], dict):
                acc[k].setdefault("items", {})
                _merge_schema(acc[k]["items"], v[0], depth + 1)
        else:
            tname = type(v).__name__
            existing = acc.get(k)
            if existing and existing.get("type") != tname:
                acc[k] = {"type": "mixed", "seen": list(set([existing.get("type"), tname]))}
            else:
                acc[k] = {"type": tname, "example": (str(v)[:80] if v else None)}
