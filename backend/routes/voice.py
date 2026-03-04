"""Voice transcription endpoint using OpenAI Whisper via Emergent Integrations."""
import os
import tempfile
import logging

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from auth import get_current_user, User

logger = logging.getLogger(__name__)
router = APIRouter()
EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY", "")


@router.post("/voice/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """Transcribe audio from browser microphone using Whisper."""
    if not file.filename:
        raise HTTPException(400, "No audio file provided")

    content = await file.read()
    if len(content) > 25 * 1024 * 1024:
        raise HTTPException(400, "Audio file too large (max 25MB)")

    # Save to temp file (Whisper needs a file path)
    suffix = ".webm"
    if file.content_type:
        ext_map = {"audio/webm": ".webm", "audio/wav": ".wav", "audio/mp3": ".mp3", "audio/mpeg": ".mp3", "audio/mp4": ".mp4"}
        suffix = ext_map.get(file.content_type, ".webm")

    try:
        from emergentintegrations.llm.openai import OpenAISpeechToText

        stt = OpenAISpeechToText(api_key=EMERGENT_LLM_KEY)

        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        with open(tmp_path, "rb") as audio_file:
            response = await stt.transcribe(
                file=audio_file,
                model="whisper-1",
                response_format="json",
                language="en",
                prompt="This is a voice command for MAARS Command AI platform. Common commands: create project, generate content, open dashboard, talk to agent, show settings.",
            )

        os.unlink(tmp_path)
        text = response.text.strip() if hasattr(response, "text") else str(response).strip()
        return {"text": text}

    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        raise HTTPException(500, f"Transcription failed: {str(e)[:200]}")
