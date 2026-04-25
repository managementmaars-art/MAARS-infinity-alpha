"""Direct provider calls for image / video / TTS / STT.

These are the low-level helpers the MAARS media router calls after selecting
a provider. No third-party wrapper (no emergentintegrations) — pure httpx
against each provider's REST API.

Each function returns raw bytes (for image/video/audio) or plain text (for STT).
All functions raise on failure; the router catches and tries fallbacks.
"""
from __future__ import annotations
import asyncio
import base64
import logging
import os
from pathlib import Path
from typing import Optional
import httpx

logger = logging.getLogger(__name__)

# Timeouts (seconds). Video can take a while; Sora-2 docs quote up to 10 min.
IMAGE_TIMEOUT = 120
VIDEO_TIMEOUT = 900
TTS_TIMEOUT = 60
STT_TIMEOUT = 120


def _api_key(env: str, fallback: Optional[str] = None) -> str:
    key = os.environ.get(env, "") or (fallback or "")
    if not key:
        raise RuntimeError(f"{env} not configured")
    return key


# ─────────────────────────────────────────────────────────── OpenAI images
async def call_openai_image(
    prompt: str,
    model: str = "gpt-image-1",
    size: str = "1024x1024",
    quality: str = "high",
    api_key: Optional[str] = None,
) -> bytes:
    """Generate one image via OpenAI; returns raw PNG bytes.

    model: "gpt-image-1" ($0.02) or "dall-e-3" ($0.04).
    """
    key = api_key or _api_key("OPENAI_API_KEY")
    # gpt-image-1 uses /v1/images/generations; response has b64_json
    url = "https://api.openai.com/v1/images/generations"
    payload = {
        "model": model,
        "prompt": prompt,
        "size": size,
        "n": 1,
    }
    # gpt-image-1 supports quality; dall-e-3 uses "standard" | "hd"
    if model == "gpt-image-1":
        payload["quality"] = quality  # "high" | "medium" | "low" | "auto"
    elif model == "dall-e-3":
        payload["quality"] = "hd" if quality in ("hd", "high") else "standard"
        payload["response_format"] = "b64_json"

    async with httpx.AsyncClient(timeout=IMAGE_TIMEOUT) as client:
        r = await client.post(url, json=payload,
                              headers={"Authorization": f"Bearer {key}"})
    if r.status_code != 200:
        raise RuntimeError(f"openai image {r.status_code}: {r.text[:300]}")
    data = r.json().get("data", [])
    if not data:
        raise RuntimeError("openai image: empty data array")
    b64 = data[0].get("b64_json")
    if not b64:
        url_out = data[0].get("url")
        if url_out:
            async with httpx.AsyncClient(timeout=IMAGE_TIMEOUT) as client:
                img = await client.get(url_out)
            return img.content
        raise RuntimeError("openai image: no b64_json and no url")
    return base64.b64decode(b64)


# ─────────────────────────────────────────────────────────── Gemini images
async def call_gemini_image(
    prompt: str,
    model: str = "gemini-3-pro-image-preview",
    api_key: Optional[str] = None,
) -> bytes:
    """Generate one image via Google Gemini image-preview model."""
    key = api_key or _api_key("GEMINI_API_KEY") or _api_key("GOOGLE_API_KEY")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseModalities": ["IMAGE"]},
    }
    async with httpx.AsyncClient(timeout=IMAGE_TIMEOUT) as client:
        r = await client.post(url, json=payload)
    if r.status_code != 200:
        raise RuntimeError(f"gemini image {r.status_code}: {r.text[:300]}")
    body = r.json()
    parts = (body.get("candidates") or [{}])[0].get("content", {}).get("parts", [])
    for p in parts:
        if "inlineData" in p:
            return base64.b64decode(p["inlineData"]["data"])
    raise RuntimeError("gemini image: no inlineData in response")


# ─────────────────────────────────────────────────────────── OpenAI video
async def call_openai_video(
    prompt: str,
    model: str = "sora-2",
    size: str = "1280x720",
    duration: int = 4,
    image_path: Optional[str] = None,
    mime_type: str = "image/jpeg",
    api_key: Optional[str] = None,
) -> bytes:
    """Generate a video via OpenAI Sora; blocks until ready. Returns mp4 bytes.

    If `image_path` is provided, performs image-to-video (multipart upload with
    `input_reference`). Otherwise text-to-video.
    """
    key = api_key or _api_key("OPENAI_API_KEY")
    create_url = "https://api.openai.com/v1/videos"
    headers = {"Authorization": f"Bearer {key}"}
    async with httpx.AsyncClient(timeout=VIDEO_TIMEOUT) as client:
        if image_path:
            with open(image_path, "rb") as f:
                img_bytes = f.read()
            form_data = {
                "model": model,
                "prompt": prompt,
                "size": size,
                "seconds": str(duration),
            }
            files = {"input_reference": (image_path.split("/")[-1], img_bytes, mime_type)}
            r = await client.post(create_url, data=form_data, files=files, headers=headers)
        else:
            r = await client.post(create_url, json={
                "model": model, "prompt": prompt, "size": size, "seconds": str(duration),
            }, headers=headers)
        if r.status_code not in (200, 201):
            raise RuntimeError(f"sora create {r.status_code}: {r.text[:300]}")
        job = r.json()
        job_id = job.get("id")
        if not job_id:
            raise RuntimeError(f"sora create: no id in {job}")

        poll_url = f"https://api.openai.com/v1/videos/{job_id}"
        status = job.get("status", "queued")
        deadline = asyncio.get_event_loop().time() + VIDEO_TIMEOUT
        while status not in ("completed", "failed", "cancelled"):
            if asyncio.get_event_loop().time() > deadline:
                raise RuntimeError(f"sora poll timeout after {VIDEO_TIMEOUT}s")
            await asyncio.sleep(5)
            pr = await client.get(poll_url, headers=headers)
            if pr.status_code != 200:
                raise RuntimeError(f"sora poll {pr.status_code}: {pr.text[:300]}")
            status = pr.json().get("status", status)

        if status != "completed":
            raise RuntimeError(f"sora job terminal status={status}")

        dl = await client.get(f"{poll_url}/content", headers=headers)
        if dl.status_code != 200:
            raise RuntimeError(f"sora download {dl.status_code}: {dl.text[:300]}")
        return dl.content


# ───────────────────────────────────────────────────────────── OpenAI TTS
OPENAI_TTS_VOICES = {"alloy", "nova", "shimmer", "echo", "onyx", "fable", "coral", "sage", "ash"}


async def call_openai_tts(
    text: str,
    voice: str = "nova",
    model: str = "tts-1",
    fmt: str = "mp3",
    speed: float = 1.0,
    api_key: Optional[str] = None,
) -> bytes:
    """Generate TTS audio via OpenAI; returns audio bytes (mp3 by default).

    If a non-OpenAI voice name is passed (e.g. router fell over from ElevenLabs
    with "rachel"), substitute the default "nova" rather than 400.
    """
    key = api_key or _api_key("OPENAI_API_KEY")
    safe_voice = voice if voice in OPENAI_TTS_VOICES else "nova"
    url = "https://api.openai.com/v1/audio/speech"
    payload = {
        "model": model,
        "input": text[:4096],
        "voice": safe_voice,
        "response_format": fmt,
        "speed": speed,
    }
    async with httpx.AsyncClient(timeout=TTS_TIMEOUT) as client:
        r = await client.post(url, json=payload,
                              headers={"Authorization": f"Bearer {key}"})
    if r.status_code != 200:
        raise RuntimeError(f"openai tts {r.status_code}: {r.text[:300]}")
    return r.content


# ────────────────────────────────────────────────────────── ElevenLabs TTS
ELEVEN_VOICES = {
    # Common defaults
    "rachel":  "21m00Tcm4TlvDq8ikWAM",
    "domi":    "AZnzlk1XvdvUeBnXmlld",
    "bella":   "EXAVITQu4vr4xnSDxMaL",
    "antoni":  "ErXwobaYiN019PkySvjV",
    "adam":    "pNInz6obpgDQGcFmaJgB",
    "sam":     "yoZ06aMxZJJ28mfd3POQ",
}


async def call_elevenlabs_tts(
    text: str,
    voice: str = "rachel",
    model: Optional[str] = None,
    language: Optional[str] = None,
    api_key: Optional[str] = None,
) -> bytes:
    """Generate premium TTS via ElevenLabs; returns mp3 bytes.

    voice:    friendly name (rachel / domi / bella / ...) or raw voice_id.
    model:    eleven_flash_v2_5 (cheapest) | eleven_turbo_v2_5 (fast+quality) |
              eleven_multilingual_v2 (native multi-lang). Auto-selects
              multilingual when `language` is non-English.
    language: ISO-639 code (en, es, fr, de, pt, ja, zh, ar, hi, it, nl,
              pl, ru, tr, id, vi, ko, ...). Forces multilingual model.
    """
    key = api_key or _api_key("ELEVENLABS_API_KEY")
    voice_id = ELEVEN_VOICES.get((voice or "").lower(), voice)
    # Auto-upgrade to multilingual model when a non-English language
    # is requested. Eleven Multilingual v2 supports 29 languages natively.
    is_non_english = bool(language) and language.lower() not in ("en", "en-us", "en-gb")
    effective_model = model or ("eleven_multilingual_v2" if is_non_english else "eleven_turbo_v2_5")
    payload: dict = {"text": text, "model_id": effective_model}
    if language:
        # ElevenLabs v2 accepts `language_code` for better pronunciation
        payload["language_code"] = language.split("-")[0].lower()
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    async with httpx.AsyncClient(timeout=TTS_TIMEOUT) as client:
        r = await client.post(
            url,
            headers={"xi-api-key": key, "Content-Type": "application/json"},
            json=payload,
        )
    if r.status_code != 200:
        raise RuntimeError(f"elevenlabs {r.status_code}: {r.text[:300]}")
    return r.content


# ───────────────────────────────────────────── Edge TTS (FREE, premium)
# Microsoft Edge's cloud TTS exposed via the `edge-tts` python package.
# 400+ voices across every major language. Quality rivals ElevenLabs
# Turbo. Cost: $0. No API key. This is the single biggest free-tier
# unlock in the platform — it replaces ElevenLabs for 95% of use cases.
#
# Common premium-sounding voices:
#   en-US-JennyNeural        — female, warm narration
#   en-US-GuyNeural          — male, authoritative
#   en-US-AriaNeural         — female, conversational
#   en-US-ChristopherNeural  — male, news anchor
#   en-GB-RyanNeural         — male, British
#   en-GB-SoniaNeural        — female, British
EDGE_VOICE_ALIAS = {
    "rachel":       "en-US-JennyNeural",
    "bella":        "en-US-AriaNeural",
    "elli":         "en-US-AnaNeural",
    "domi":         "en-US-AshleyNeural",
    "antoni":       "en-US-GuyNeural",
    "josh":         "en-US-ChristopherNeural",
    "arnold":       "en-US-EricNeural",
    "adam":         "en-US-BrandonNeural",
    "british_male": "en-GB-RyanNeural",
    "british_female":"en-GB-SoniaNeural",
    "female":       "en-US-JennyNeural",
    "male":         "en-US-GuyNeural",
    "narrator":     "en-US-ChristopherNeural",
}


async def call_edge_tts(
    text: str,
    voice: str = "en-US-JennyNeural",
    rate: str = "+0%",      # "-50%" to "+100%" for pace control
    volume: str = "+0%",
    api_key: Optional[str] = None,
) -> bytes:
    """Generate TTS via Microsoft Edge (free, unlimited, 400+ voices).

    Returns mp3 bytes, same shape as every other TTS provider so the
    router can swap them transparently.
    """
    try:
        import edge_tts
    except ImportError:
        raise RuntimeError("edge-tts package not installed. pip install edge-tts")

    # Accept friendly aliases for voices to match our ElevenLabs UX.
    resolved = EDGE_VOICE_ALIAS.get(voice.lower(), voice)
    # If someone passes 'rachel' but it's already mapped in ELEVEN_VOICES,
    # the resolved string becomes an Azure neural voice id — always valid.

    communicator = edge_tts.Communicate(text, voice=resolved, rate=rate, volume=volume)
    chunks: list[bytes] = []
    async for part in communicator.stream():
        if part.get("type") == "audio":
            chunks.append(part.get("data", b""))
    out = b"".join(chunks)
    if not out:
        raise RuntimeError(f"edge_tts returned empty audio for voice={resolved}")
    return out


# ────────────────────────────────────────── Pollinations.ai (FREE images)
# Pollinations is a community-operated inference gateway running Flux
# (schnell + dev) with no API key, no rate limit that matters at SaaS
# scale, and roughly DALL-E 3 quality. URL-based — GET the prompt and
# receive PNG bytes. When paid providers are saturated or the operator's
# monthly budget is tight, this keeps generation unlimited.
# Docs: https://github.com/pollinations/pollinations
async def call_pollinations_image(
    prompt: str,
    model: str = "flux",          # flux | flux-realism | flux-anime | flux-3d | turbo
    width: int = 1024,
    height: int = 1024,
    seed: int | None = None,
    api_key: Optional[str] = None,  # accepted for chain compatibility; unused
) -> bytes:
    """Generate an image via Pollinations.ai. Returns PNG bytes.

    This is the 'always-free premium fallback'. Flux schnell through
    Pollinations produces comparable output to $0.02/image providers.
    """
    from urllib.parse import quote
    base = "https://image.pollinations.ai/prompt"
    # Pollinations encodes the prompt in the URL path. Prompts can be
    # long (hundreds of chars) — it handles them fine.
    params = {
        "model": model,
        "width": str(width),
        "height": str(height),
        "nologo": "true",   # strip their watermark (allowed for all users)
        "enhance": "false", # we already enhance prompts upstream
    }
    if seed is not None:
        params["seed"] = str(seed)
    qs = "&".join(f"{k}={quote(v)}" for k, v in params.items())
    url = f"{base}/{quote(prompt)}?{qs}"

    async with httpx.AsyncClient(timeout=IMAGE_TIMEOUT, follow_redirects=True) as client:
        r = await client.get(url)
        if r.status_code != 200 or not r.content:
            raise RuntimeError(f"pollinations {r.status_code}: {r.text[:200] if r.text else 'empty'}")
        # Sanity: must be PNG/JPEG bytes, not an HTML error page.
        if not (r.content[:4] == b"\x89PNG" or r.content[:3] == b"\xff\xd8\xff"):
            raise RuntimeError("pollinations returned non-image bytes")
        return r.content


# ─────────────────────────────────────────────────────────── OpenAI STT
async def call_openai_stt(
    audio_bytes: bytes,
    filename: str = "audio.webm",
    model: str = "whisper-1",
    language: Optional[str] = None,
    prompt: Optional[str] = None,
    api_key: Optional[str] = None,
) -> str:
    """Transcribe audio via OpenAI Whisper; returns plain text."""
    key = api_key or _api_key("OPENAI_API_KEY")
    url = "https://api.openai.com/v1/audio/transcriptions"
    data = {"model": model, "response_format": "json"}
    if language:
        data["language"] = language
    if prompt:
        data["prompt"] = prompt
    files = {"file": (filename, audio_bytes)}
    async with httpx.AsyncClient(timeout=STT_TIMEOUT) as client:
        r = await client.post(url, data=data, files=files,
                              headers={"Authorization": f"Bearer {key}"})
    if r.status_code != 200:
        raise RuntimeError(f"openai stt {r.status_code}: {r.text[:300]}")
    return (r.json() or {}).get("text", "").strip()


# ───────────────────────────────────────────── Deepgram STT (FREE tier)
# Deepgram's Nova-2 model gives 45,000 minutes/month free — enough to
# handle the vast majority of transcription volume with ZERO operator
# cost. Latency is ~300ms vs Whisper's 2-5s per minute of audio. This
# becomes the preferred STT for live use; Whisper stays as fallback
# for long-form where batch latency doesn't matter.
#
# Setup: https://console.deepgram.com/signup (no CC) → API Keys tab.
# Add DEEPGRAM_API_KEY to .env.
async def call_deepgram_stt(
    audio_bytes: bytes,
    filename: str = "audio.webm",
    model: str = "nova-2",           # nova-2 | nova | enhanced | base
    language: Optional[str] = None,
    prompt: Optional[str] = None,    # Deepgram calls this `keywords`
    api_key: Optional[str] = None,
) -> str:
    """Transcribe via Deepgram. Returns plain text (same contract as
    call_openai_stt so the STT_CHAIN can try this first)."""
    key = api_key or os.environ.get("DEEPGRAM_API_KEY", "")
    if not key:
        raise RuntimeError("DEEPGRAM_API_KEY not configured")
    # Deepgram auto-detects content type from the Content-Type header.
    ctype = "audio/webm"
    if filename.endswith(".mp3"): ctype = "audio/mpeg"
    elif filename.endswith(".wav"): ctype = "audio/wav"
    elif filename.endswith(".mp4"): ctype = "audio/mp4"
    elif filename.endswith(".m4a"): ctype = "audio/mp4"
    elif filename.endswith(".ogg"): ctype = "audio/ogg"
    params: dict[str, Any] = {"model": model, "smart_format": "true", "punctuate": "true"}
    if language:
        params["language"] = language
    if prompt:
        # Deepgram boosts recognition for these terms
        params["keywords"] = prompt
    try:
        async with httpx.AsyncClient(timeout=STT_TIMEOUT) as client:
            r = await client.post(
                "https://api.deepgram.com/v1/listen",
                headers={"Authorization": f"Token {key}", "Content-Type": ctype},
                params=params,
                content=audio_bytes,
            )
    except Exception as exc:
        raise RuntimeError(f"deepgram stt error: {type(exc).__name__}: {exc}")
    if r.status_code != 200:
        raise RuntimeError(f"deepgram {r.status_code}: {r.text[:300]}")
    try:
        alts = r.json()["results"]["channels"][0]["alternatives"][0]
        return alts.get("transcript", "").strip()
    except (KeyError, IndexError, TypeError):
        raise RuntimeError(f"deepgram: unexpected response shape — {r.text[:300]}")


# ────────────────────────────────────────────── Fal.ai (free credits)
# Fal.ai gives $5-10 in free credits on signup + has extremely fast
# inference for Flux (dev, pro, schnell) and video models (LTX, Veo).
# Treated as a paid provider BUT with zero-cost cold start until the
# credits are consumed. Good third-tier image fallback after
# Pollinations (unlimited free) and Gemini.
#
# Setup: https://fal.ai/dashboard/keys — add FAL_KEY to .env.
async def call_fal_image(
    prompt: str,
    model: str = "fal-ai/flux/dev",   # fal-ai/flux/dev | fal-ai/flux/schnell | fal-ai/flux-pro
    width: int = 1024,
    height: int = 1024,
    api_key: Optional[str] = None,
) -> bytes:
    """Generate an image via Fal.ai. Returns PNG/JPEG bytes.

    Fal's API is synchronous for flux/schnell (sub-2s) and async for
    flux/pro. We use the sync `run` endpoint for simplicity.
    """
    key = api_key or os.environ.get("FAL_KEY", "")
    if not key:
        raise RuntimeError("FAL_KEY not configured")
    url = f"https://fal.run/{model}"
    payload = {
        "prompt": prompt,
        "image_size": {"width": width, "height": height},
        "num_images": 1,
        "enable_safety_checker": False,  # we enhance prompts upstream
    }
    async with httpx.AsyncClient(timeout=IMAGE_TIMEOUT) as client:
        r = await client.post(
            url,
            headers={"Authorization": f"Key {key}", "Content-Type": "application/json"},
            json=payload,
        )
        if r.status_code not in (200, 201):
            raise RuntimeError(f"fal {r.status_code}: {r.text[:300]}")
        data = r.json()
        # Response: { images: [{url: "..."}], ... }
        images = data.get("images") or []
        if not images:
            raise RuntimeError(f"fal: no images in response — {r.text[:200]}")
        img_url = images[0].get("url")
        if not img_url:
            raise RuntimeError("fal: image without url")
        # Download the binary
        img_resp = await client.get(img_url)
        if img_resp.status_code != 200:
            raise RuntimeError(f"fal image fetch {img_resp.status_code}")
        return img_resp.content


# ───────────────────────────────────────────── Together.ai images (FLUX/SDXL)
# Together hosts FLUX (schnell + dev + pro), SDXL, Playground 2.5, and
# several other image models at production-tier prices. FLUX.schnell is
# $0.003/image — cheaper than Gemini, cheaper than DALL-E, sub-2s cold
# latency. Treat as the second-cheapest image fallback after Pollinations.
async def call_together_image(
    prompt: str,
    model: str = "black-forest-labs/FLUX.1-schnell-Free",
    width: int = 1024,
    height: int = 1024,
    api_key: Optional[str] = None,
) -> bytes:
    """Generate an image via Together.ai. Returns PNG bytes.

    Common model slugs:
      black-forest-labs/FLUX.1-schnell-Free  — free tier, ~1-2s
      black-forest-labs/FLUX.1-dev            — $0.025/img, higher quality
      black-forest-labs/FLUX.1-pro            — $0.05/img, top tier
      stabilityai/stable-diffusion-xl-base-1.0 — SDXL
    """
    key = api_key or _api_key("TOGETHER_API_KEY")
    url = "https://api.together.xyz/v1/images/generations"
    payload = {
        "model": model,
        "prompt": prompt,
        "width": width,
        "height": height,
        "n": 1,
        "response_format": "b64_json",
    }
    async with httpx.AsyncClient(timeout=IMAGE_TIMEOUT) as client:
        r = await client.post(url, json=payload,
                              headers={"Authorization": f"Bearer {key}"})
    if r.status_code != 200:
        raise RuntimeError(f"together image {r.status_code}: {r.text[:300]}")
    data = (r.json() or {}).get("data") or []
    if not data:
        raise RuntimeError("together image: empty data array")
    b64 = data[0].get("b64_json")
    if not b64:
        img_url = data[0].get("url")
        if img_url:
            async with httpx.AsyncClient(timeout=IMAGE_TIMEOUT) as client2:
                img = await client2.get(img_url)
            return img.content
        raise RuntimeError("together image: no b64_json / url")
    return base64.b64decode(b64)


# ───────────────────────────────────────────── Fireworks.ai images
# Fireworks hosts SDXL, FLUX.schnell, FLUX.dev, Playground 2.5. Prices
# similar to Together; API shape uses /workflows/accounts/fireworks/models/...
async def call_fireworks_image(
    prompt: str,
    model: str = "accounts/fireworks/models/flux-1-schnell-fp8",
    width: int = 1024,
    height: int = 1024,
    api_key: Optional[str] = None,
) -> bytes:
    key = api_key or _api_key("FIREWORKS_API_KEY")
    # Fireworks exposes /image_generation for image models.
    url = f"https://api.fireworks.ai/inference/v1/{model}/image_generation"
    payload = {
        "prompt": prompt,
        "width": width, "height": height, "n": 1,
    }
    async with httpx.AsyncClient(timeout=IMAGE_TIMEOUT) as client:
        r = await client.post(
            url, json=payload,
            headers={"Authorization": f"Bearer {key}",
                     "Accept": "image/jpeg"},
        )
    if r.status_code != 200:
        raise RuntimeError(f"fireworks image {r.status_code}: {r.text[:300]}")
    # Fireworks returns the raw image bytes directly when Accept=image/jpeg.
    return r.content


# ───────────────────────────────────────────── Hyperbolic images
# Hyperbolic hosts FLUX.1-dev + SDXL at $0.01-0.02/image after the $1
# phone-verification credit. Good cheap fallback for operators who
# can't fund Fal or don't want to.
async def call_hyperbolic_image(
    prompt: str,
    model: str = "FLUX.1-dev",
    width: int = 1024,
    height: int = 1024,
    api_key: Optional[str] = None,
) -> bytes:
    key = api_key or _api_key("HYPERBOLIC_API_KEY")
    url = "https://api.hyperbolic.xyz/v1/image/generation"
    payload = {
        "model_name": model,
        "prompt": prompt,
        "height": height, "width": width, "steps": 30, "cfg_scale": 5,
    }
    async with httpx.AsyncClient(timeout=IMAGE_TIMEOUT) as client:
        r = await client.post(url, json=payload,
                              headers={"Authorization": f"Bearer {key}"})
    if r.status_code != 200:
        raise RuntimeError(f"hyperbolic image {r.status_code}: {r.text[:300]}")
    data = r.json()
    # Response: {images: [{image: b64, ...}]}
    imgs = data.get("images") or []
    if not imgs:
        raise RuntimeError("hyperbolic image: empty images")
    b64 = imgs[0].get("image") or imgs[0].get("b64") or imgs[0].get("b64_json")
    if not b64:
        raise RuntimeError("hyperbolic image: no b64 payload")
    return base64.b64decode(b64)


# ───────────────────────────────────────────── Novita.ai images
# Novita proxies FLUX + SDXL + Realistic Vision. $0.005-0.01/image.
async def call_novita_image(
    prompt: str,
    model: str = "flux-1-schnell",
    width: int = 1024,
    height: int = 1024,
    api_key: Optional[str] = None,
) -> bytes:
    key = api_key or _api_key("NOVITA_API_KEY")
    url = "https://api.novita.ai/v3/async/txt2img"
    payload = {
        "extra": {"response_image_type": "png"},
        "request": {
            "model_name": model, "prompt": prompt,
            "width": width, "height": height,
            "image_num": 1, "steps": 25,
        },
    }
    async with httpx.AsyncClient(timeout=IMAGE_TIMEOUT) as client:
        r = await client.post(url, json=payload,
                              headers={"Authorization": f"Bearer {key}",
                                       "Content-Type": "application/json"})
        if r.status_code != 200:
            raise RuntimeError(f"novita image {r.status_code}: {r.text[:300]}")
        task_id = (r.json() or {}).get("task_id")
        if not task_id:
            raise RuntimeError("novita image: no task_id")
        # Poll up to ~60s for the job.
        poll_url = f"https://api.novita.ai/v3/async/task-result?task_id={task_id}"
        import asyncio as _asyncio
        for _ in range(30):
            await _asyncio.sleep(2)
            pr = await client.get(
                poll_url, headers={"Authorization": f"Bearer {key}"},
            )
            if pr.status_code != 200:
                continue
            body = pr.json()
            status = (body.get("task") or {}).get("status")
            if status == "TASK_STATUS_SUCCEED":
                imgs = body.get("images") or []
                if not imgs:
                    raise RuntimeError("novita image: empty images")
                img_url = imgs[0].get("image_url")
                if not img_url:
                    raise RuntimeError("novita image: no url")
                img = await client.get(img_url)
                return img.content
            if status == "TASK_STATUS_FAILED":
                raise RuntimeError(f"novita image failed: {body}")
        raise RuntimeError("novita image poll timeout")


# ───────────────────────────────────────────── HuggingFace Inference images
# HF Inference Router hosts thousands of diffusion models with pay-as-
# you-go pricing AND a generous free tier. Any `text-to-image` model on
# the Hub works through the router. Free-tier quota auto-rotates
# per-model; paid is $0.001-0.01/image depending on model.
async def call_huggingface_image(
    prompt: str,
    model: str = "black-forest-labs/FLUX.1-schnell",
    width: int = 1024,
    height: int = 1024,
    api_key: Optional[str] = None,
) -> bytes:
    key = api_key or os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_API_KEY") or ""
    if not key:
        raise RuntimeError("HF_TOKEN / HUGGINGFACE_API_KEY not configured")
    url = f"https://router.huggingface.co/hf-inference/models/{model}"
    payload = {
        "inputs": prompt,
        "parameters": {"width": width, "height": height},
    }
    async with httpx.AsyncClient(timeout=IMAGE_TIMEOUT) as client:
        r = await client.post(
            url, json=payload,
            headers={"Authorization": f"Bearer {key}",
                     "Accept": "image/png"},
        )
    if r.status_code != 200:
        raise RuntimeError(f"huggingface image {r.status_code}: {r.text[:300]}")
    return r.content


async def call_fal_video(
    prompt: str,
    duration: int = 5,
    size: str = "1280x720",
    image_path: Optional[str] = None,
    mime_type: str = "image/jpeg",
    api_key: Optional[str] = None,
) -> bytes:
    """Generate a short video clip via Fal.ai LTX or Veo (depending on
    availability). Returns MP4 bytes."""
    key = api_key or os.environ.get("FAL_KEY", "")
    if not key:
        raise RuntimeError("FAL_KEY not configured")
    # LTX is the cheapest/fastest video model on Fal; Veo is higher
    # quality but costs more credits. Start with LTX.
    model = "fal-ai/ltx-video"
    try:
        w, h = (int(x) for x in size.lower().split("x"))
    except Exception:
        w, h = 1280, 720
    payload: dict[str, Any] = {
        "prompt": prompt,
        "num_frames": max(25, duration * 25),  # 25 fps
        "resolution": f"{w}x{h}",
    }
    async with httpx.AsyncClient(timeout=VIDEO_TIMEOUT) as client:
        r = await client.post(
            f"https://fal.run/{model}",
            headers={"Authorization": f"Key {key}", "Content-Type": "application/json"},
            json=payload,
        )
        if r.status_code not in (200, 201):
            raise RuntimeError(f"fal video {r.status_code}: {r.text[:300]}")
        data = r.json()
        video = (data.get("video") or {}).get("url") or (data.get("videos") or [{}])[0].get("url")
        if not video:
            raise RuntimeError(f"fal: no video in response — {r.text[:200]}")
        vid_resp = await client.get(video)
        if vid_resp.status_code != 200:
            raise RuntimeError(f"fal video fetch {vid_resp.status_code}")
        return vid_resp.content


# ───────────────────────────────────────────── Fal additional video models
# Fal hosts Kling, Veo-3, Hailuo, MiniMax, CogVideoX-5B, Luma Ray, Pika,
# Mochi. Accept any Fal model slug — same /fal.run/<model> endpoint as
# LTX. The media_router.VIDEO_CHAIN wraps each slug in its own entry so
# the router can fall through them in priority order.
FAL_VIDEO_MODELS = (
    "fal-ai/kling-video/v2/master/text-to-video",   # premium Kling 2.0
    "fal-ai/minimax/hailuo-02/standard/text-to-video",
    "fal-ai/veo3/fast",                              # fastest Veo-3
    "fal-ai/pika/v2/turbo/text-to-video",
    "fal-ai/luma-dream-machine/ray-2",
    "fal-ai/cogvideox-5b",
    "fal-ai/mochi-v1",
    "fal-ai/ltx-video",
)

async def call_fal_video_model(
    prompt: str,
    duration: int = 5,
    size: str = "1280x720",
    model: str = "fal-ai/kling-video/v2/master/text-to-video",
    api_key: Optional[str] = None,
) -> bytes:
    """Thin wrapper — run ANY Fal video model slug through the same
    sync `/fal.run` endpoint. The router picks the slug; the helper
    normalizes the response shape."""
    key = api_key or os.environ.get("FAL_KEY", "")
    if not key:
        raise RuntimeError("FAL_KEY not configured")
    try:
        w, h = (int(x) for x in size.lower().split("x"))
    except Exception:
        w, h = 1280, 720
    payload: dict[str, Any] = {
        "prompt": prompt,
        "num_frames": max(25, duration * 25),
        "resolution": f"{w}x{h}",
        "duration": str(duration),
    }
    async with httpx.AsyncClient(timeout=VIDEO_TIMEOUT) as client:
        r = await client.post(
            f"https://fal.run/{model}",
            headers={"Authorization": f"Key {key}", "Content-Type": "application/json"},
            json=payload,
        )
        if r.status_code not in (200, 201):
            raise RuntimeError(f"fal {model} {r.status_code}: {r.text[:300]}")
        data = r.json()
        url = (data.get("video") or {}).get("url") or (data.get("videos") or [{}])[0].get("url")
        if not url:
            raise RuntimeError(f"fal {model}: no video url — {r.text[:200]}")
        vid_resp = await client.get(url)
        if vid_resp.status_code != 200:
            raise RuntimeError(f"fal {model} video fetch {vid_resp.status_code}")
        return vid_resp.content


# ───────────────────────────────────────────── HuggingFace Inference video
# HF Inference router hosts CogVideoX, Zeroscope, AnimateDiff, and
# dozens of other video models. Same /router.huggingface.co/hf-inference
# path as image, accepts binary output.
async def call_huggingface_video(
    prompt: str,
    model: str = "THUDM/CogVideoX-5b",
    duration: int = 4,
    api_key: Optional[str] = None,
) -> bytes:
    key = api_key or os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_API_KEY") or ""
    if not key:
        raise RuntimeError("HF_TOKEN / HUGGINGFACE_API_KEY not configured")
    url = f"https://router.huggingface.co/hf-inference/models/{model}"
    payload = {
        "inputs": prompt,
        "parameters": {"num_frames": max(16, duration * 8)},
    }
    async with httpx.AsyncClient(timeout=VIDEO_TIMEOUT) as client:
        r = await client.post(
            url, json=payload,
            headers={"Authorization": f"Bearer {key}",
                     "Accept": "video/mp4"},
        )
    if r.status_code != 200:
        raise RuntimeError(f"huggingface video {r.status_code}: {r.text[:300]}")
    return r.content


# ───────────────────────────────────────────── Music / audio generation
# Suno (via third-party APIs), MusicGen, Stable Audio, Bark — all
# available through Fal + HF. Default to MusicGen on HF (free tier).

async def call_huggingface_music(
    prompt: str,
    model: str = "facebook/musicgen-medium",
    duration: int = 10,
    api_key: Optional[str] = None,
) -> bytes:
    """Generate music/audio via HuggingFace. Returns WAV bytes."""
    key = api_key or os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_API_KEY") or ""
    if not key:
        raise RuntimeError("HF_TOKEN / HUGGINGFACE_API_KEY not configured")
    url = f"https://router.huggingface.co/hf-inference/models/{model}"
    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": duration * 50},
    }
    async with httpx.AsyncClient(timeout=VIDEO_TIMEOUT) as client:
        r = await client.post(
            url, json=payload,
            headers={"Authorization": f"Bearer {key}",
                     "Accept": "audio/wav"},
        )
    if r.status_code != 200:
        raise RuntimeError(f"hf music {r.status_code}: {r.text[:300]}")
    return r.content


async def call_fal_music(
    prompt: str,
    duration: int = 15,
    model: str = "fal-ai/stable-audio",
    api_key: Optional[str] = None,
) -> bytes:
    """Generate music/audio via Fal.ai (Stable Audio, MusicGen, etc.)."""
    key = api_key or os.environ.get("FAL_KEY", "")
    if not key:
        raise RuntimeError("FAL_KEY not configured")
    async with httpx.AsyncClient(timeout=VIDEO_TIMEOUT) as client:
        r = await client.post(
            f"https://fal.run/{model}",
            headers={"Authorization": f"Key {key}", "Content-Type": "application/json"},
            json={"prompt": prompt, "seconds_total": duration},
        )
        if r.status_code not in (200, 201):
            raise RuntimeError(f"fal music {r.status_code}: {r.text[:300]}")
        data = r.json()
        url = (data.get("audio_file") or {}).get("url") or (data.get("audio") or {}).get("url")
        if not url:
            raise RuntimeError(f"fal music: no url — {r.text[:200]}")
        aud = await client.get(url)
        if aud.status_code != 200:
            raise RuntimeError(f"fal music fetch {aud.status_code}")
        return aud.content


# ───────────────────────────────────────────── MiniMax (Hailuo) video
# MiniMax Hailuo is one of the top-tier closed video models (competes
# with Sora). Direct API gives access to hailuo-02 + t2v-01 + i2v-01.
# Latency is 30-120s for a 6-sec clip; $0.30-0.50 per clip — expensive
# but quality matches Sora at a fraction of the cost.
#
# Setup: https://www.minimax.io/ → Account → API Keys (MINIMAX_API_KEY).
async def call_minimax_video(
    prompt: str,
    duration: int = 6,
    size: str = "1280x720",
    model: str = "MiniMax-Hailuo-02",
    image_path: Optional[str] = None,
    mime_type: str = "image/jpeg",
    api_key: Optional[str] = None,
) -> bytes:
    """Generate video via MiniMax Hailuo API. Returns MP4 bytes.

    Two-step async flow: POST /video_generation → poll /query/video_generation
    → GET file URL. Hailuo accepts model names like MiniMax-Hailuo-02, T2V-01,
    and I2V-01 (the last one needs image_path).
    """
    key = api_key or _api_key("MINIMAX_API_KEY")
    headers = {"Authorization": f"Bearer {key}",
               "Content-Type": "application/json"}
    payload: dict = {
        "model": model,
        "prompt": prompt,
        "duration": duration,
    }
    if image_path:
        import base64 as _b64
        with open(image_path, "rb") as f:
            img_b64 = _b64.b64encode(f.read()).decode()
        payload["first_frame_image"] = f"data:{mime_type};base64,{img_b64}"

    async with httpx.AsyncClient(timeout=VIDEO_TIMEOUT) as client:
        # 1. Submit the job
        r = await client.post(
            "https://api.minimaxi.chat/v1/video_generation",
            headers=headers, json=payload,
        )
        if r.status_code != 200:
            raise RuntimeError(f"minimax video submit {r.status_code}: {r.text[:300]}")
        body = r.json()
        task_id = body.get("task_id")
        if not task_id:
            raise RuntimeError(f"minimax: no task_id in {body}")

        # 2. Poll until ready (Hailuo typically 30-120s)
        deadline = asyncio.get_event_loop().time() + VIDEO_TIMEOUT
        file_id: Optional[str] = None
        while asyncio.get_event_loop().time() < deadline:
            await asyncio.sleep(5)
            qr = await client.get(
                f"https://api.minimaxi.chat/v1/query/video_generation?task_id={task_id}",
                headers=headers,
            )
            if qr.status_code != 200:
                continue
            qb = qr.json()
            status = qb.get("status", "")
            if status == "Success":
                file_id = qb.get("file_id")
                break
            if status == "Fail":
                raise RuntimeError(f"minimax video fail: {qb}")
        if not file_id:
            raise RuntimeError(f"minimax video poll timeout after {VIDEO_TIMEOUT}s")

        # 3. Retrieve the file URL
        fr = await client.get(
            f"https://api.minimaxi.chat/v1/files/retrieve?file_id={file_id}",
            headers={"Authorization": f"Bearer {key}"},
        )
        if fr.status_code != 200:
            raise RuntimeError(f"minimax file retrieve {fr.status_code}: {fr.text[:300]}")
        download_url = (fr.json().get("file") or {}).get("download_url")
        if not download_url:
            raise RuntimeError("minimax: no download_url")
        dl = await client.get(download_url)
        if dl.status_code != 200:
            raise RuntimeError(f"minimax download {dl.status_code}")
        return dl.content


async def call_minimax_image(
    prompt: str,
    model: str = "image-01",
    width: int = 1024,
    height: int = 1024,
    api_key: Optional[str] = None,
) -> bytes:
    """MiniMax image generation — image-01 is the T2I model."""
    key = api_key or _api_key("MINIMAX_API_KEY")
    payload = {
        "model": model, "prompt": prompt,
        "aspect_ratio": "1:1" if width == height else
                        ("16:9" if width > height else "9:16"),
        "response_format": "base64",
        "n": 1,
    }
    async with httpx.AsyncClient(timeout=IMAGE_TIMEOUT) as client:
        r = await client.post(
            "https://api.minimaxi.chat/v1/image_generation",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json=payload,
        )
    if r.status_code != 200:
        raise RuntimeError(f"minimax image {r.status_code}: {r.text[:300]}")
    body = r.json()
    data = body.get("data") or {}
    images = data.get("image_base64") or body.get("images") or []
    if not images:
        raise RuntimeError(f"minimax image: empty — {r.text[:200]}")
    b64 = images[0] if isinstance(images[0], str) else images[0].get("image")
    if not b64:
        raise RuntimeError("minimax image: no b64")
    return base64.b64decode(b64)


# ───────────────────────────────────────────── Zhipu GLM (CogView + CogVideoX)
# Z.ai (Zhipu AI) international tier — free to start. Hosts CogView-3-Plus
# (best Chinese-trained T2I) + CogVideoX (open-weight video champion).
# Cheap: CogView image ≈ $0.01, CogVideoX ≈ $0.05/5-sec clip.
async def call_zhipu_image(
    prompt: str,
    model: str = "cogview-3-plus",
    width: int = 1024,
    height: int = 1024,
    api_key: Optional[str] = None,
) -> bytes:
    """CogView-3-Plus via Z.ai. Supports `cogview-3`, `cogview-3-plus`,
    `cogview-3-flash` (fastest)."""
    key = api_key or _api_key("ZHIPU_API_KEY")
    payload = {
        "model": model,
        "prompt": prompt,
        "size": f"{width}x{height}",
        "n": 1,
    }
    async with httpx.AsyncClient(timeout=IMAGE_TIMEOUT) as client:
        r = await client.post(
            "https://open.bigmodel.cn/api/paas/v4/images/generations",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json=payload,
        )
        if r.status_code != 200:
            raise RuntimeError(f"zhipu image {r.status_code}: {r.text[:300]}")
        data = (r.json() or {}).get("data") or []
        if not data:
            raise RuntimeError("zhipu image: empty data")
        img_url = data[0].get("url")
        if not img_url:
            raise RuntimeError("zhipu image: no url")
        dl = await client.get(img_url)
        return dl.content


async def call_zhipu_video(
    prompt: str,
    duration: int = 5,
    size: str = "1280x720",
    model: str = "cogvideox-flash",
    image_path: Optional[str] = None,
    mime_type: str = "image/jpeg",
    api_key: Optional[str] = None,
) -> bytes:
    """CogVideoX via Z.ai. `cogvideox-flash` is fastest + cheapest;
    `cogvideox-3` is flagship quality."""
    key = api_key or _api_key("ZHIPU_API_KEY")
    try:
        w, h = (int(x) for x in size.lower().split("x"))
    except Exception:
        w, h = 1280, 720
    payload: dict = {
        "model": model, "prompt": prompt,
        "quality": "quality", "size": f"{w}x{h}",
        "duration": duration,
    }
    if image_path:
        import base64 as _b64
        with open(image_path, "rb") as f:
            payload["image_url"] = f"data:{mime_type};base64,{_b64.b64encode(f.read()).decode()}"
    async with httpx.AsyncClient(timeout=VIDEO_TIMEOUT) as client:
        r = await client.post(
            "https://open.bigmodel.cn/api/paas/v4/videos/generations",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json=payload,
        )
        if r.status_code != 200:
            raise RuntimeError(f"zhipu video submit {r.status_code}: {r.text[:300]}")
        task_id = (r.json() or {}).get("id")
        if not task_id:
            raise RuntimeError("zhipu video: no task id")

        deadline = asyncio.get_event_loop().time() + VIDEO_TIMEOUT
        video_url: Optional[str] = None
        while asyncio.get_event_loop().time() < deadline:
            await asyncio.sleep(5)
            qr = await client.get(
                f"https://open.bigmodel.cn/api/paas/v4/async-result/{task_id}",
                headers={"Authorization": f"Bearer {key}"},
            )
            if qr.status_code != 200:
                continue
            body = qr.json()
            status = body.get("task_status")
            if status == "SUCCESS":
                results = body.get("video_result") or []
                if results:
                    video_url = results[0].get("url")
                break
            if status == "FAIL":
                raise RuntimeError(f"zhipu video fail: {body}")
        if not video_url:
            raise RuntimeError(f"zhipu video poll timeout after {VIDEO_TIMEOUT}s")

        dl = await client.get(video_url)
        if dl.status_code != 200:
            raise RuntimeError(f"zhipu download {dl.status_code}")
        return dl.content


# ───────────────────────────────────────────── Novita.ai video
# Novita has a video API (text-to-video + image-to-video) at very cheap
# rates — $0.05-0.15 per 4-sec clip via their Wan/LTX/HunyuanVideo backends.
async def call_novita_video(
    prompt: str,
    duration: int = 4,
    size: str = "1280x720",
    model: str = "wan-v2-1",
    image_path: Optional[str] = None,
    mime_type: str = "image/jpeg",
    api_key: Optional[str] = None,
) -> bytes:
    """Novita video — models: `wan-v2-1`, `wan-v2-2`, `ltx-video-v2`,
    `hunyuan-video-fast`, `cogvideox-5b`."""
    key = api_key or _api_key("NOVITA_API_KEY")
    try:
        w, h = (int(x) for x in size.lower().split("x"))
    except Exception:
        w, h = 1280, 720
    payload: dict = {
        "extra": {"response_video_type": "mp4"},
        "request": {
            "model_name": model, "prompt": prompt,
            "width": w, "height": h,
            "seconds": duration, "steps": 30,
        },
    }
    if image_path:
        payload["request"]["image_path"] = image_path
    async with httpx.AsyncClient(timeout=VIDEO_TIMEOUT) as client:
        r = await client.post(
            "https://api.novita.ai/v3/async/txt2video",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json=payload,
        )
        if r.status_code != 200:
            raise RuntimeError(f"novita video submit {r.status_code}: {r.text[:300]}")
        task_id = (r.json() or {}).get("task_id")
        if not task_id:
            raise RuntimeError("novita video: no task id")

        poll_url = f"https://api.novita.ai/v3/async/task-result?task_id={task_id}"
        deadline = asyncio.get_event_loop().time() + VIDEO_TIMEOUT
        while asyncio.get_event_loop().time() < deadline:
            await asyncio.sleep(3)
            pr = await client.get(poll_url, headers={"Authorization": f"Bearer {key}"})
            if pr.status_code != 200:
                continue
            body = pr.json()
            status = (body.get("task") or {}).get("status")
            if status == "TASK_STATUS_SUCCEED":
                videos = body.get("videos") or []
                if not videos:
                    raise RuntimeError("novita video: no output videos")
                url = videos[0].get("video_url")
                if not url:
                    raise RuntimeError("novita video: no url")
                dl = await client.get(url)
                return dl.content
            if status == "TASK_STATUS_FAILED":
                raise RuntimeError(f"novita video failed: {body}")
        raise RuntimeError("novita video poll timeout")


# ───────────────────────────────────────────── Bytez aggregator
# Bytez is a meta-aggregator that proxies FLUX + SDXL + many diffusion
# models with a unified key. Good cheap image fallback when the primary
# chain (Pollinations → Together → Fal) is rate-limited.
async def call_bytez_image(
    prompt: str,
    model: str = "black-forest-labs/FLUX.1-schnell",
    width: int = 1024,
    height: int = 1024,
    api_key: Optional[str] = None,
) -> bytes:
    key = api_key or _api_key("BYTEZ_API_KEY")
    url = f"https://api.bytez.com/v1/models/{model}/predict"
    payload = {"prompt": prompt, "width": width, "height": height}
    async with httpx.AsyncClient(timeout=IMAGE_TIMEOUT) as client:
        r = await client.post(
            url, json=payload,
            headers={"Authorization": f"Key {key}",
                     "Content-Type": "application/json",
                     "Accept": "image/png"},
        )
    if r.status_code != 200:
        raise RuntimeError(f"bytez image {r.status_code}: {r.text[:300]}")
    # Bytez may return JSON with base64 or raw bytes depending on Accept
    ct = r.headers.get("content-type", "")
    if ct.startswith("image/"):
        return r.content
    body = r.json()
    b64 = body.get("image") or body.get("b64_json")
    if b64:
        return base64.b64decode(b64)
    url_out = body.get("url") or (body.get("output") or [{}])[0].get("url")
    if url_out:
        async with httpx.AsyncClient(timeout=IMAGE_TIMEOUT) as c2:
            img = await c2.get(url_out)
        return img.content
    raise RuntimeError(f"bytez image: no recognized payload — {r.text[:200]}")


# ───────────────────────────────────────────── Groq Whisper (super-fast STT)
# Groq serves Whisper on their LPU hardware — ~100x faster than OpenAI,
# FREE on their generous free tier. Becomes the primary STT choice.
async def call_groq_stt(
    audio_bytes: bytes,
    filename: str = "audio.webm",
    model: str = "whisper-large-v3-turbo",
    language: Optional[str] = None,
    prompt: Optional[str] = None,
    api_key: Optional[str] = None,
) -> str:
    key = api_key or _api_key("GROQ_API_KEY")
    url = "https://api.groq.com/openai/v1/audio/transcriptions"
    data = {"model": model, "response_format": "json"}
    if language: data["language"] = language
    if prompt:   data["prompt"] = prompt
    files = {"file": (filename, audio_bytes)}
    async with httpx.AsyncClient(timeout=STT_TIMEOUT) as client:
        r = await client.post(url, data=data, files=files,
                              headers={"Authorization": f"Bearer {key}"})
    if r.status_code != 200:
        raise RuntimeError(f"groq stt {r.status_code}: {r.text[:300]}")
    return (r.json() or {}).get("text", "").strip()
