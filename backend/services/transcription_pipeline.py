"""Multilingual meeting-notes pipeline.

Pattern from multilingual-meeting-notes-generator + notebook-lm-clone:
upload audio/video → AssemblyAI Universal (99-language auto-detect +
diarization) → per-speaker English summary + action items → optional
TTS podcast via Kokoro/Cartesia.

Required env:
  ASSEMBLYAI_API_KEY    — already used by existing adapters
  (optional) CARTESIA_API_KEY — for TTS podcast recap

Public API:
  transcribe_and_summarize(user_id, file_path, language="auto",
                            diarize=True, action_items=True)
    → { transcript, speakers[], summary, action_items[], language_detected }

All persisted to `db.meeting_notes` keyed by user_id + timestamp.
"""
from __future__ import annotations
import asyncio
import json
import logging
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


async def _upload_and_transcribe(file_path: str, language: str = "auto",
                                   diarize: bool = True) -> dict[str, Any]:
    """AssemblyAI upload + transcribe. Returns the finished transcript."""
    key = os.environ.get("ASSEMBLYAI_API_KEY")
    if not key:
        return {"ok": False, "error": "no_assemblyai_api_key"}
    import httpx
    p = Path(file_path)
    if not p.exists():
        return {"ok": False, "error": "file_not_found"}

    async with httpx.AsyncClient(timeout=600) as client:
        # 1. Upload
        with p.open("rb") as f:
            upload = await client.post(
                "https://api.assemblyai.com/v2/upload",
                headers={"authorization": key},
                content=f.read(),
            )
        if upload.status_code >= 400:
            return {"ok": False, "error": f"upload_failed: {upload.status_code}"}
        audio_url = upload.json().get("upload_url")

        # 2. Submit transcription job
        payload = {
            "audio_url": audio_url,
            "speaker_labels": bool(diarize),
            "auto_chapters": True,
            "sentiment_analysis": False,
        }
        if language and language != "auto":
            payload["language_code"] = language
        else:
            payload["language_detection"] = True
        submit = await client.post(
            "https://api.assemblyai.com/v2/transcript",
            headers={"authorization": key,
                     "content-type": "application/json"},
            json=payload,
        )
        if submit.status_code >= 400:
            return {"ok": False, "error": f"submit_failed: {submit.status_code} {submit.text[:300]}"}
        tid = submit.json().get("id")

        # 3. Poll until done (max 20 min)
        for _ in range(60):
            await asyncio.sleep(20)
            poll = await client.get(
                f"https://api.assemblyai.com/v2/transcript/{tid}",
                headers={"authorization": key},
            )
            if poll.status_code >= 400:
                return {"ok": False, "error": f"poll_failed: {poll.status_code}"}
            data = poll.json()
            status = data.get("status")
            if status == "completed":
                return {"ok": True, "transcript": data}
            if status == "error":
                return {"ok": False, "error": data.get("error", "transcribe_failed")}
    return {"ok": False, "error": "timeout_after_20min"}


async def _summarize_and_extract_actions(
    user_id: str, transcript: str,
    detected_language: str | None = None,
) -> dict[str, Any]:
    """Use MAARS gateway to summarize + extract action items. English
    summary even when source language differs, so global teams can share."""
    from services.llm_gateway import complete_text
    ref_note = (f"Source language: {detected_language}. "
                "Produce the summary and action items in English.\n\n"
                if detected_language and detected_language != "en" else "")
    prompt = (
        f"{ref_note}TRANSCRIPT:\n{transcript[:12000]}\n\n"
        "Return ONLY JSON with keys: "
        '{"summary": "<5-8 sentence recap>", '
        '"action_items": [{"owner": "<person|team>", "action": "<verb-led>"}], '
        '"decisions": ["<key decisions made>"], '
        '"open_questions": ["<unresolved>"]}'
    )
    try:
        raw = await complete_text(
            user_id,
            system_prompt="You are a precise meeting-notes summarizer. Output strict JSON.",
            user_prompt=prompt,
            model="maars/auto",
            max_tokens=1500, temperature=0.2,
            source="transcription_pipeline.summarize",
            enable_cache=False,
        )
    except Exception as exc:
        return {"summary": f"LLM error: {exc}", "action_items": [],
                "decisions": [], "open_questions": []}
    import re as _re
    m = _re.search(r"\{[\s\S]*\}", raw or "")
    try:
        return json.loads(m.group(0)) if m else {}
    except Exception:
        return {"summary": raw[:2000], "action_items": [],
                "decisions": [], "open_questions": []}


async def transcribe_and_summarize(
    *, user_id: str, file_path: str,
    language: str = "auto", diarize: bool = True,
    title: str | None = None,
) -> dict[str, Any]:
    """Full pipeline. Persists to db.meeting_notes."""
    tr = await _upload_and_transcribe(file_path, language=language, diarize=diarize)
    if not tr.get("ok"):
        return tr
    t = tr["transcript"]
    text = t.get("text") or ""
    if not text:
        return {"ok": False, "error": "empty_transcript"}
    lang = t.get("language_code") or language
    summary = await _summarize_and_extract_actions(user_id, text, detected_language=lang)

    # Speaker summaries (if diarization succeeded)
    speakers: list[dict] = []
    utter = t.get("utterances") or []
    if diarize and utter:
        agg: dict[str, str] = {}
        for u in utter:
            s = u.get("speaker") or "?"
            agg.setdefault(s, "")
            agg[s] += " " + (u.get("text") or "")
        speakers = [{"speaker": k, "sample": v.strip()[:800]} for k, v in agg.items()]

    doc = {
        "note_id":            f"note_{uuid.uuid4().hex[:12]}",
        "user_id":            user_id,
        "title":              title or Path(file_path).name,
        "language_detected":  lang,
        "transcript":         text,
        "speakers":           speakers,
        "summary":            summary.get("summary"),
        "action_items":       summary.get("action_items") or [],
        "decisions":          summary.get("decisions") or [],
        "open_questions":     summary.get("open_questions") or [],
        "created_at":         datetime.now(timezone.utc).isoformat(),
        "assemblyai_id":      t.get("id"),
    }
    from db import db
    await db.meeting_notes.insert_one(dict(doc))
    doc.pop("_id", None)
    return {"ok": True, **doc}


async def list_notes(user_id: str, limit: int = 50) -> list[dict]:
    from db import db
    cursor = db.meeting_notes.find(
        {"user_id": user_id}, {"_id": 0, "transcript": 0},
    ).sort("created_at", -1).limit(limit)
    return await cursor.to_list(length=limit)
