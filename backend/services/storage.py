"""Lightweight persistence helper for generated media.

Writes bytes to UPLOAD_DIR and returns a `/files/{name}` URL — the same
contract every other route already uses (routes/media.py, routes/chats.py,
routes/generation.py). Keeping it in one place lets the Video Creator's
compositor + voice-over steps use a single call site instead of
re-implementing the filesystem dance.
"""
from __future__ import annotations
import logging
import uuid
from pathlib import Path
from typing import Optional
from shared.constants import UPLOAD_DIR

logger = logging.getLogger(__name__)


EXT_BY_TYPE = {
    "audio/mpeg": "mp3",
    "audio/mp3":  "mp3",
    "audio/wav":  "wav",
    "audio/webm": "webm",
    "video/mp4":  "mp4",
    "video/quicktime": "mov",
    "video/webm": "webm",
    "image/png":  "png",
    "image/jpeg": "jpg",
    "image/webp": "webp",
    "application/x-subrip": "srt",
    "text/plain": "txt",
}


def _infer_ext(filename: Optional[str], content_type: Optional[str]) -> str:
    if filename and "." in filename:
        return filename.rsplit(".", 1)[-1].lower()
    if content_type:
        return EXT_BY_TYPE.get(content_type.lower(), "bin")
    return "bin"


async def upload_bytes(
    data: bytes,
    filename: Optional[str] = None,
    *,
    content_type: Optional[str] = None,
    user_id: Optional[str] = None,
) -> str:
    """Persist `data` to the UPLOAD_DIR and return its served URL.

    `user_id` is accepted for future multi-tenant isolation but not yet
    applied — today every file lands in the shared uploads dir. Caller
    may pass `filename` to pin the stored name; otherwise a uuid4 prefix
    is used so concurrent uploads don't collide.
    """
    ext = _infer_ext(filename, content_type)
    stored = filename
    if not stored or "/" in stored or "\\" in stored:
        stored = f"{uuid.uuid4().hex[:10]}.{ext}"
    elif "." not in stored:
        stored = f"{stored}.{ext}"
    path = Path(UPLOAD_DIR) / stored
    path.write_bytes(data)
    return f"/files/{stored}"


async def fetch_to_file(url: str, *, suffix: str = "") -> Path:
    """Download `url` to a temp file under UPLOAD_DIR and return the path.
    If `url` is already a local `/files/...` path, resolve it directly.
    """
    import httpx
    local_prefix = "/files/"
    if url.startswith(local_prefix):
        return Path(UPLOAD_DIR) / url[len(local_prefix):]
    name = f"{uuid.uuid4().hex[:10]}{suffix}"
    dest = Path(UPLOAD_DIR) / name
    async with httpx.AsyncClient(timeout=300, follow_redirects=True) as client:
        r = await client.get(url)
        r.raise_for_status()
        dest.write_bytes(r.content)
    return dest
