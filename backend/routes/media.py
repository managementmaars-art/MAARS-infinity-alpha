"""Upload, audio, TTS, STT, and available models endpoints."""
import io
import uuid
import base64
import logging
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Request
from typing import Optional
from db import db
from auth import get_current_user, User
from shared.constants import UPLOAD_DIR, EMERGENT_LLM_KEY
from shared.utils import get_api_keys

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
    """Transcribe audio to text using OpenAI Whisper"""
    try:
        contents = await audio_file.read()
        if len(contents) > 25 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Audio file too large. Max 25MB.")
        
        from emergentintegrations.llm.openai import OpenAISpeechToText
        
        api_keys = await get_api_keys()
        stt_key = api_keys.get("emergent", EMERGENT_LLM_KEY)
        
        stt = OpenAISpeechToText(api_key=stt_key)
        
        audio_io = io.BytesIO(contents)
        audio_io.name = audio_file.filename or "audio.webm"
        
        kwargs = {"file": audio_io, "model": "whisper-1", "response_format": "json"}
        if language:
            kwargs["language"] = language
        
        response = await stt.transcribe(**kwargs)
        
        return {"text": response.text, "language": language}
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
    """Generate text-to-speech audio using OpenAI TTS (works with Emergent key)"""
    body = await request.json()
    text = body.get("text", "")
    voice = body.get("voice", "nova")
    
    if not text:
        raise HTTPException(status_code=400, detail="Text is required")
    
    # Truncate to 4096 chars (OpenAI TTS limit)
    text = text[:4096]
    
    try:
        from emergentintegrations.llm.openai import OpenAITextToSpeech
        
        # Use Emergent key or admin-configured OpenAI key
        api_key = EMERGENT_LLM_KEY
        if not api_key:
            admin_keys = await db.platform_config.find_one({"config_type": "api_keys"}, {"_id": 0})
            if admin_keys:
                api_key = admin_keys.get("openai", "")
        
        if not api_key:
            raise HTTPException(400, "No API key available for TTS")
        
        tts = OpenAITextToSpeech(api_key=api_key)
        audio_bytes = await tts.generate_speech(
            text=text,
            model="tts-1",
            voice=voice,
            response_format="mp3",
            speed=1.0
        )
        
        import base64
        audio_b64 = base64.b64encode(audio_bytes).decode()
        return {"audio_url": f"data:audio/mpeg;base64,{audio_b64}", "text": text, "voice": voice}
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

