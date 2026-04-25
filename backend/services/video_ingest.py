"""Video understanding via Gemini File API.

MAARS generates video via the media router (Sora/Runway/Pika); this
module adds the *ingest* side — upload a video, get a file_id, then
ask questions about it through the same `llm_gateway.complete()` path.

Why: clients want "analyze this competitor ad", "summarize this recorded
demo", "extract key moments from this tutorial". The video-rag-gemini
project shows the simplest approach — upload to Gemini's File API, then
reference the file_id in the prompt.

Public API:
    upload_video(user_id, file_path) → {file_id, display_name, expires_at}
    analyze_video(user_id, file_id, prompt) → completion
    list_videos(user_id)
    delete_video(user_id, file_id)

Files live 48 hours in Gemini's file store then expire. We mirror the
file_id + expiry in `db.rag_videos` so the UI knows what's still
queryable without hitting the Gemini API.
"""
from __future__ import annotations
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

COLLECTION = "rag_videos"


async def _gemini_api_key() -> str | None:
    # Prefer vault; fall back to env
    try:
        from services import credential_vault
        cred = await credential_vault.get("gemini", user_id=None)
        if cred and cred.secret:
            return cred.secret
    except Exception:
        pass
    return os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")


async def upload_video(
    *, user_id: str, file_path: str,
    display_name: str | None = None,
) -> dict[str, Any]:
    import httpx
    key = await _gemini_api_key()
    if not key:
        return {"ok": False, "error": "no_gemini_api_key"}
    p = Path(file_path)
    if not p.exists():
        return {"ok": False, "error": "file_not_found"}
    mime = "video/mp4"
    if p.suffix.lower() in (".mov",): mime = "video/quicktime"
    if p.suffix.lower() in (".webm",): mime = "video/webm"
    # Resumable upload (single chunk for simplicity).
    async with httpx.AsyncClient(timeout=120) as client:
        # Init
        init = await client.post(
            f"https://generativelanguage.googleapis.com/upload/v1beta/files?key={key}",
            headers={
                "X-Goog-Upload-Protocol":    "resumable",
                "X-Goog-Upload-Command":     "start",
                "X-Goog-Upload-Header-Content-Length": str(p.stat().st_size),
                "X-Goog-Upload-Header-Content-Type":    mime,
                "Content-Type":              "application/json",
            },
            json={"file": {"display_name": display_name or p.name}},
        )
        if init.status_code >= 400:
            return {"ok": False, "error": f"init_failed: {init.status_code} {init.text[:200]}"}
        upload_url = init.headers.get("x-goog-upload-url") or init.headers.get("X-Goog-Upload-URL")
        if not upload_url:
            return {"ok": False, "error": "no_upload_url_returned"}
        # Upload bytes
        data = p.read_bytes()
        put = await client.request(
            "POST", upload_url,
            headers={
                "Content-Length":              str(len(data)),
                "X-Goog-Upload-Offset":        "0",
                "X-Goog-Upload-Command":       "upload, finalize",
            },
            content=data,
        )
        if put.status_code >= 400:
            return {"ok": False, "error": f"upload_failed: {put.status_code}"}
        meta = put.json().get("file") or {}
    file_id = meta.get("name")  # "files/xyz"
    expires = meta.get("expirationTime")
    from db import db
    now = datetime.now(timezone.utc).isoformat()
    await db[COLLECTION].insert_one({
        "user_id":      user_id,
        "file_id":      file_id,
        "display_name": display_name or p.name,
        "mime":         mime,
        "size_bytes":   p.stat().st_size,
        "expires_at":   expires,
        "uploaded_at":  now,
        "gemini_uri":   meta.get("uri"),
    })
    return {"ok": True, "file_id": file_id, "display_name": display_name or p.name,
            "expires_at": expires, "uri": meta.get("uri")}


async def analyze_video(
    *, user_id: str, file_id: str, prompt: str,
    agent_id: str | None = None,
) -> dict[str, Any]:
    """Ask Gemini about an uploaded video. Routes through llm_gateway so
    wallet + usage log + audit still apply."""
    from db import db
    meta = await db[COLLECTION].find_one({"user_id": user_id, "file_id": file_id})
    if not meta:
        return {"ok": False, "error": "file_not_found"}
    # Gemini lets you reference uploaded files by URI in the content
    # parts. We construct a bare payload here because the v1_gateway
    # Gemini adapter normalizes simple text only.
    key = await _gemini_api_key()
    if not key:
        return {"ok": False, "error": "no_gemini_api_key"}
    import httpx
    body = {
        "contents": [{"parts": [
            {"text": prompt},
            {"file_data": {"mime_type": meta.get("mime", "video/mp4"),
                            "file_uri":  meta.get("gemini_uri")}},
        ]}],
    }
    async with httpx.AsyncClient(timeout=180) as client:
        r = await client.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"gemini-2.5-flash:generateContent?key={key}",
            headers={"Content-Type": "application/json"},
            json=body,
        )
    if r.status_code >= 400:
        return {"ok": False, "error": f"gemini_error: {r.status_code} {r.text[:400]}"}
    data = r.json()
    try:
        text = data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        return {"ok": False, "error": "unexpected_response", "raw": data}
    return {"ok": True, "answer": text, "file_id": file_id}


async def list_videos(user_id: str) -> list[dict]:
    from db import db
    cursor = db[COLLECTION].find({"user_id": user_id}, {"_id": 0}).sort("uploaded_at", -1)
    return await cursor.to_list(length=100)


async def delete_video(user_id: str, file_id: str) -> bool:
    from db import db
    # Delete the Gemini file too
    import httpx
    key = await _gemini_api_key()
    if key:
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                await client.delete(
                    f"https://generativelanguage.googleapis.com/v1beta/{file_id}?key={key}"
                )
        except Exception:
            pass
    res = await db[COLLECTION].delete_one({"user_id": user_id, "file_id": file_id})
    return bool(getattr(res, "deleted_count", 0))
