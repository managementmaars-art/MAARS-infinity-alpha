"""Upload, audio, TTS, STT, and available models endpoints."""
import io
import uuid
import base64
import logging
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Request
from typing import Optional
from db import db
from auth import get_current_user, User
from shared.constants import UPLOAD_DIR

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    """Upload any file and return base64 encoded data + save to disk for processing"""
    try:
        contents = await file.read()
        
        if len(contents) > 50 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large. Max 50MB.")
        
        b64_content = base64.b64encode(contents).decode('utf-8')
        content_type = file.content_type or "application/octet-stream"
        data_url = f"data:{content_type};base64,{b64_content}"
        
        # Also save to disk for image-to-video and other processing
        file_id = uuid.uuid4().hex[:10]
        ext = file.filename.rsplit('.', 1)[-1] if '.' in file.filename else 'bin'
        saved_filename = f"{file_id}_upload.{ext}"
        saved_path = UPLOAD_DIR / saved_filename
        with open(saved_path, 'wb') as f:
            f.write(contents)
        
        return {
            "filename": file.filename,
            "saved_filename": saved_filename,
            "file_url": f"/files/{saved_filename}",
            "content_type": content_type,
            "size": len(contents),
            "data_url": data_url
        }
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")



@router.post("/audio/speech-to-text")
async def speech_to_text(audio_file: UploadFile = File(...), language: Optional[str] = Form(None), current_user: User = Depends(get_current_user)):
    """Transcribe audio to text through the MAARS media router (Whisper today)."""
    try:
        contents = await audio_file.read()
        if len(contents) > 25 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Audio file too large. Max 25MB.")

        # Rough duration estimate: ~16 KB/sec for compressed audio at typical voice bitrates.
        duration_guess = max(1.0, len(contents) / 16_000)

        from services.media_router import route_stt
        from services.billing.media_billing import bill_and_run
        text, meta, billing = await bill_and_run(
            current_user.user_id, "stt", "whisper-1", duration_guess,
            route_stt,
            audio_bytes=contents,
            filename=audio_file.filename or "audio.webm",
            language=language,
        )
        from shared.response_scrubber import scrub_meta, scrub
        return {"text": text, "language": language, "router": scrub_meta(meta), "billing": scrub(billing)}
    except Exception as e:
        logger.error(f"STT error: {e}")
        raise HTTPException(status_code=500, detail=f"Speech-to-text failed: {str(e)}")

# ============== AVAILABLE MODELS ENDPOINT ==============

@router.get("/models")
async def get_available_models(current_user: User = Depends(get_current_user)):
    """Get all available AI models for switching"""
    models = [
        # OpenAI
        {"provider": "openai", "model": "gpt-5", "name": "GPT-5", "category": "flagship", "cost_per_credit": 0.006, "credits": 3, "best_for": "Coding, analysis, general tasks"},
        {"provider": "openai", "model": "gpt-4o", "name": "GPT-4o", "category": "fast", "cost_per_credit": 0.003, "credits": 2, "best_for": "Balanced speed and quality"},
        {"provider": "openai", "model": "gpt-4o-mini", "name": "GPT-4o Mini", "category": "economy", "cost_per_credit": 0.001, "credits": 1, "best_for": "Simple tasks, quick answers"},
        {"provider": "openai", "model": "o3", "name": "O3", "category": "reasoning", "cost_per_credit": 0.012, "credits": 5, "best_for": "Complex reasoning, math, logic"},
        {"provider": "openai", "model": "o3-mini", "name": "O3 Mini", "category": "reasoning", "cost_per_credit": 0.005, "credits": 2, "best_for": "Light reasoning tasks"},
        # Anthropic
        {"provider": "anthropic", "model": "claude-sonnet-4-5-20250929", "name": "Claude Sonnet 4.5", "category": "flagship", "cost_per_credit": 0.005, "credits": 3, "best_for": "Creative writing, analysis"},
        {"provider": "anthropic", "model": "claude-opus-4-5-20251101", "name": "Claude Opus 4.5", "category": "premium", "cost_per_credit": 0.025, "credits": 5, "best_for": "Long-form, deep research"},
        {"provider": "anthropic", "model": "claude-haiku-4-5-20250929", "name": "Claude Haiku 4.5", "category": "economy", "cost_per_credit": 0.001, "credits": 1, "best_for": "Quick responses, summaries"},
        # Google
        {"provider": "gemini", "model": "gemini-3-flash-preview", "name": "Gemini 3 Flash", "category": "fast", "cost_per_credit": 0.002, "credits": 1, "best_for": "Fast responses, simple tasks"},
        {"provider": "gemini", "model": "gemini-3-pro-preview", "name": "Gemini 3 Pro", "category": "flagship", "cost_per_credit": 0.005, "credits": 2, "best_for": "Multimodal, research"},
        # Generation models
        {"provider": "gemini", "model": "gemini-3-pro-image-preview", "name": "Nano Banana 2", "category": "image_gen", "cost_per_credit": 0.01, "credits": 5, "best_for": "AI image generation (Gemini 3.1 Flash)"},
        {"provider": "openai", "model": "sora-2", "name": "Sora 2", "category": "video_gen", "cost_per_credit": 0.10, "credits": 10, "best_for": "AI video generation from text"},
        # xAI Grok
        {"provider": "xai", "model": "grok-3", "name": "Grok 3", "category": "flagship", "cost_per_credit": 0.005, "credits": 3, "best_for": "Reasoning, analysis, 1M context"},
        {"provider": "xai", "model": "grok-3-mini", "name": "Grok 3 Mini", "category": "economy", "cost_per_credit": 0.001, "credits": 1, "best_for": "Cost-efficient reasoning"},
        {"provider": "xai", "model": "grok-2", "name": "Grok 2", "category": "fast", "cost_per_credit": 0.003, "credits": 2, "best_for": "General tasks, competitive with GPT-4o"},
        # DeepSeek
        {"provider": "deepseek", "model": "deepseek-chat", "name": "DeepSeek Chat", "category": "economy", "cost_per_credit": 0.001, "credits": 1, "best_for": "Cost-efficient chat, 128K context"},
        {"provider": "deepseek", "model": "deepseek-reasoner", "name": "DeepSeek Reasoner", "category": "reasoning", "cost_per_credit": 0.001, "credits": 2, "best_for": "Deep reasoning, math, logic"},
        # Mistral
        {"provider": "mistral", "model": "mistral-large-latest", "name": "Mistral Large", "category": "flagship", "cost_per_credit": 0.004, "credits": 3, "best_for": "Complex reasoning, enterprise"},
        {"provider": "mistral", "model": "mistral-medium-latest", "name": "Mistral Medium", "category": "fast", "cost_per_credit": 0.002, "credits": 2, "best_for": "Balanced performance"},
        {"provider": "mistral", "model": "mistral-small-latest", "name": "Mistral Small", "category": "economy", "cost_per_credit": 0.001, "credits": 1, "best_for": "Simple tasks, very fast"},
        # Perplexity
        {"provider": "perplexity", "model": "sonar", "name": "Perplexity Sonar", "category": "search", "cost_per_credit": 0.002, "credits": 2, "best_for": "Web-grounded answers, search"},
        {"provider": "perplexity", "model": "sonar-pro", "name": "Perplexity Sonar Pro", "category": "search", "cost_per_credit": 0.008, "credits": 3, "best_for": "Deep web research"},
        # Cohere
        {"provider": "cohere", "model": "command-r-plus", "name": "Cohere Command R+", "category": "flagship", "cost_per_credit": 0.005, "credits": 3, "best_for": "RAG, enterprise tasks"},
        {"provider": "cohere", "model": "command-r", "name": "Cohere Command R", "category": "fast", "cost_per_credit": 0.001, "credits": 1, "best_for": "Cost-efficient RAG, summaries"},
    ]
    # Strip USD cost basis (`cost_per_credit`) so clients never see what
    # each credit actually costs the operator. Keep provider + model
    # names — these are industry-standard (GPT-5, Claude, Gemini) and
    # clients expect them in the picker. Only the hidden free-tier
    # backends (Pollinations, Edge, Hunter) are shielded — and those
    # aren't in this list, they're only in the routing chains.
    models = [
        {k: v for k, v in m.items() if k not in ("cost_per_credit", "cost_usd")}
        for m in models
    ]
    return {
        "models": models,
        "credit_tiers": {
            "economy": {"credits": 1, "label": "1 credit"},
            "fast": {"credits": 2, "label": "2 credits"},
            "flagship": {"credits": 3, "label": "3 credits"},
            "premium": {"credits": 5, "label": "5 credits"},
            "reasoning": {"credits": "2-5", "label": "2-5 credits"},
            "image_gen": {"credits": 5, "label": "+5 credits"},
            "video_gen": {"credits": 10, "label": "+10 credits"},
        },
        "default": {"provider": "openai", "model": "gpt-5"}
    }

@router.post("/tts/generate")
async def generate_tts(request: Request, current_user: User = Depends(get_current_user)):
    """Generate TTS through the MAARS media router (OpenAI tts-1 → ElevenLabs fallback)."""
    body = await request.json()
    text = body.get("text", "")
    voice = body.get("voice", "nova")
    tier = body.get("tier", "standard")  # "standard" | "premium" (ElevenLabs voice-over)

    if not text:
        raise HTTPException(status_code=400, detail="Text is required")
    text = text[:4096]

    try:
        from services.media_router import route_tts
        from services.billing.media_billing import bill_and_run
        est_model = "eleven_turbo_v2_5" if tier == "premium" else "tts-1"
        audio_bytes, meta, billing = await bill_and_run(
            current_user.user_id, "tts", est_model, len(text),
            route_tts, text=text, voice=voice, tier=tier,
        )
        import base64
        audio_b64 = base64.b64encode(audio_bytes).decode()
        from shared.response_scrubber import scrub_meta, scrub
        return {
            "audio_url": f"data:audio/mpeg;base64,{audio_b64}",
            "text": text,
            "voice": voice,
            "router": scrub_meta(meta),
            "billing": scrub(billing),
        }
    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise HTTPException(status_code=500, detail=f"TTS failed: {str(e)}")

@router.get("/tts/voices")
async def get_tts_voices(current_user: User = Depends(get_current_user)):
    """Get available OpenAI TTS voices"""
    return {"voices": [
        {"voice_id": "alloy", "name": "Alloy", "description": "Neutral, balanced"},
        {"voice_id": "nova", "name": "Nova", "description": "Energetic, upbeat"},
        {"voice_id": "shimmer", "name": "Shimmer", "description": "Bright, cheerful"},
        {"voice_id": "echo", "name": "Echo", "description": "Smooth, calm"},
        {"voice_id": "onyx", "name": "Onyx", "description": "Deep, authoritative"},
        {"voice_id": "fable", "name": "Fable", "description": "Expressive, storytelling"},
        {"voice_id": "coral", "name": "Coral", "description": "Warm, friendly"},
        {"voice_id": "sage", "name": "Sage", "description": "Wise, measured"},
        {"voice_id": "ash", "name": "Ash", "description": "Clear, articulate"},
    ]}

