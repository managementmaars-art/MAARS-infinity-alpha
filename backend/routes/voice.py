"""Voice transcription endpoint — routes through MAARS media router (Whisper today)."""
import logging

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from auth import get_current_user, User

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/voice/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """Transcribe audio from browser microphone via the MAARS media router."""
    if not file.filename:
        raise HTTPException(400, "No audio file provided")

    content = await file.read()
    if len(content) > 25 * 1024 * 1024:
        raise HTTPException(400, "Audio file too large (max 25MB)")

    ext_map = {"audio/webm": ".webm", "audio/wav": ".wav", "audio/mp3": ".mp3",
               "audio/mpeg": ".mp3", "audio/mp4": ".mp4"}
    filename = f"audio{ext_map.get(file.content_type or '', '.webm')}"

    try:
        from services.media_router import route_stt
        from services.billing.media_billing import bill_and_run
        duration_guess = max(1.0, len(content) / 16_000)
        text, meta, billing = await bill_and_run(
            current_user.user_id, "stt", "whisper-1", duration_guess,
            route_stt,
            audio_bytes=content,
            filename=filename,
            language="en",
            prompt=("This is a voice command for MAARS Command AI platform. "
                    "Common commands: create project, generate content, open dashboard, "
                    "talk to agent, show settings."),
        )
        from shared.response_scrubber import scrub_meta, scrub
        return {"text": text, "router": scrub_meta(meta), "billing": scrub(billing)}
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        raise HTTPException(500, f"Transcription failed: {str(e)[:200]}")
