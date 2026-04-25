"""MAARS Media Router — picks the cheapest capable provider for non-chat modalities.

The router owns the decision "which model handles this image/video/TTS/STT request";
the low-level call happens in media_providers.py. Fallback chains try the next option
on failure so a single provider outage never kills the request.

Public surface:
    - route_image(prompt, quality="standard", api_key_override=None)  → (bytes, meta)
    - route_video(prompt, duration, size, ...)                        → (bytes, meta)
    - route_tts(text, voice, tier="standard")                          → (bytes, meta)
    - route_stt(audio_bytes, filename, language=None, ...)             → (text, meta)

`meta` always contains: provider, model, cost_usd, cost_credits, wall_s, attempt_count.
"""
from __future__ import annotations
import asyncio
import logging
import time
from typing import Optional

from services import media_providers as mp
from services.llm_service import MODEL_COSTS_MAP, MODEL_CREDIT_COSTS
from shared.utils import get_api_keys

logger = logging.getLogger(__name__)

# Credit price constant — 1 credit = $0.001 USD (see constants.py:370)
USD_PER_CREDIT = 0.001


# ──────────────────────────────────────────────────────────── chains
# Each chain is ordered cheapest → most expensive within a quality band.

# Local-GPU entry prepended to every chain. The caller raises
# LocalUnavailable when MAARS_LOCAL_*_URL is unset or the server is
# unreachable — the chain treats that as "skip" and falls through to
# hosted providers. When the operator runs local SDXL / whisper.cpp /
# XTTS / SVD, the marginal cost of every media call drops to ~$0.
from services.local_media import (
    call_local_image as _local_image,
    call_local_video as _local_video,
    call_local_tts   as _local_tts,
    call_local_stt   as _local_stt,
)

IMAGE_CHAIN_STANDARD = [
    # Zero-cost if MAARS_LOCAL_IMAGE_URL is set (local SDXL / Flux / ComfyUI).
    {"provider": "local",  "model": "local-image",               "caller": _local_image},
    # Free-first: Pollinations.ai has no API key, no rate limit that
    # matters, and uses Flux schnell which matches DALL-E 3 quality at
    # $0/image. Fal.ai Flux sits as a low-latency backup using free
    # signup credits. Then Gemini (generous free tier with key) and
    # finally paid providers.
    {"provider": "pollinations", "model": "flux",                 "caller": mp.call_pollinations_image},
    # --- paid providers, ordered cheapest→premium (see llm_service.MODEL_COSTS_MAP for rates) ---
    # Free/near-free FLUX-schnell tier across aggregators (~$0-0.003/img)
    {"provider": "together",    "model": "black-forest-labs/FLUX.1-schnell-Free",   "caller": mp.call_together_image},
    {"provider": "fireworks",   "model": "accounts/fireworks/models/flux-1-schnell-fp8",  "caller": mp.call_fireworks_image},
    {"provider": "huggingface", "model": "black-forest-labs/FLUX.1-schnell",        "caller": mp.call_huggingface_image},
    {"provider": "bytez",       "model": "black-forest-labs/FLUX.1-schnell",        "caller": mp.call_bytez_image},
    {"provider": "fal",         "model": "fal-ai/flux/schnell",                     "caller": mp.call_fal_image},
    # Cheap but paid tier (~$0.005-0.02/img)
    {"provider": "novita",      "model": "flux-1-schnell",                          "caller": mp.call_novita_image},
    {"provider": "zhipu",       "model": "cogview-3-flash",                         "caller": mp.call_zhipu_image},
    {"provider": "hyperbolic",  "model": "FLUX.1-dev",                              "caller": mp.call_hyperbolic_image},
    {"provider": "minimax",     "model": "image-01",                                "caller": mp.call_minimax_image},
    # Premium quality ($0.02-0.05/img)
    {"provider": "gemini",      "model": "gemini-3-pro-image-preview",              "caller": mp.call_gemini_image},
    {"provider": "openai",      "model": "gpt-image-1",                             "caller": mp.call_openai_image},
    {"provider": "openai",      "model": "dall-e-3",                                "caller": mp.call_openai_image},
]
IMAGE_CHAIN_PREMIUM = [
    # Premium: if local SDXL is configured it's the cheapest premium-
    # quality path (Flux-dev or SDXL lightning on your own GPU).
    {"provider": "local",       "model": "local-image-premium",       "caller": _local_image},
    # Premium tier prioritizes quality. Flux-pro via Fal is Midjourney-
    # level at credit cost. Then DALL-E 3, then Gemini, then the free
    # tiers as quality-verified fallbacks.
    {"provider": "fal",         "model": "fal-ai/flux-pro",           "caller": mp.call_fal_image},
    {"provider": "openai",      "model": "dall-e-3",                  "caller": mp.call_openai_image},
    {"provider": "openai",      "model": "gpt-image-1",               "caller": mp.call_openai_image},
    {"provider": "gemini",      "model": "gemini-3-pro-image-preview","caller": mp.call_gemini_image},
    # Together / Fireworks / HF all host FLUX.1-dev at lower cost than
    # DALL-E 3 with comparable quality. Keep them as quality-tier fall-
    # through so premium orders still land gracefully if Fal/OpenAI are
    # rate-limited.
    {"provider": "together",    "model": "black-forest-labs/FLUX.1-dev",           "caller": mp.call_together_image},
    {"provider": "fireworks",   "model": "accounts/fireworks/models/flux-1-dev-fp8","caller": mp.call_fireworks_image},
    {"provider": "huggingface", "model": "black-forest-labs/FLUX.1-dev",           "caller": mp.call_huggingface_image},
    {"provider": "hyperbolic",  "model": "SDXL1.0-base",                           "caller": mp.call_hyperbolic_image},
    {"provider": "pollinations","model": "flux",                                   "caller": mp.call_pollinations_image},
]

VIDEO_CHAIN = [
    # Zero-cost if MAARS_LOCAL_VIDEO_URL is set (local SVD / CogVideo).
    {"provider": "local",       "model": "local-video",                             "caller": _local_video},
    # --- Cheapest cloud tier (~$0.005-0.02/sec) ---
    # Fal LTX is $0.005/sec — cheapest text-to-video API on the planet.
    {"provider": "fal",         "model": "fal-ai/ltx-video",                        "caller": mp.call_fal_video},
    {"provider": "fal",         "model": "fal-ai/cogvideox-5b",                     "caller": mp.call_fal_video_model},
    # Zhipu CogVideoX-flash and Novita Wan-v2-1 compete in the cheap tier
    # and give us independence from Fal when it's rate-limited.
    {"provider": "zhipu",       "model": "cogvideox-flash",                         "caller": mp.call_zhipu_video},
    {"provider": "novita",      "model": "wan-v2-1",                                "caller": mp.call_novita_video},
    # --- Mid tier (~$0.04-0.10/sec) ---
    {"provider": "fal",         "model": "fal-ai/mochi-v1",                         "caller": mp.call_fal_video_model},
    {"provider": "fal",         "model": "fal-ai/pika/v2/turbo/text-to-video",      "caller": mp.call_fal_video_model},
    # MiniMax Hailuo direct — Sora-tier quality at ~$0.30/clip, skip the
    # Fal proxy margin when we have a direct MINIMAX_API_KEY.
    {"provider": "minimax",     "model": "MiniMax-Hailuo-02",                       "caller": mp.call_minimax_video},
    {"provider": "fal",         "model": "fal-ai/minimax/hailuo-02/standard/text-to-video", "caller": mp.call_fal_video_model},
    {"provider": "fal",         "model": "fal-ai/luma-dream-machine/ray-2",         "caller": mp.call_fal_video_model},
    # --- Premium tier (~$0.10+/sec) ---
    {"provider": "fal",         "model": "fal-ai/kling-video/v2/master/text-to-video", "caller": mp.call_fal_video_model},
    {"provider": "fal",         "model": "fal-ai/veo3/fast",                        "caller": mp.call_fal_video_model},
    # Sora-2 as the quality-premium final fallback ($0.40/4-sec).
    {"provider": "openai",      "model": "sora-2",                                  "caller": mp.call_openai_video},
]

# New — music / audio generation chain. Exposed via route_music() so the
# compositor step can drop brand music into a product ad without reaching
# outside MAARS.
MUSIC_CHAIN = [
    {"provider": "huggingface", "model": "facebook/musicgen-medium",  "caller": mp.call_huggingface_music},
    {"provider": "huggingface", "model": "facebook/musicgen-large",   "caller": mp.call_huggingface_music},
    {"provider": "fal",         "model": "fal-ai/stable-audio",        "caller": mp.call_fal_music},
    {"provider": "fal",         "model": "fal-ai/musicgen",            "caller": mp.call_fal_music},
]

TTS_CHAIN_STANDARD = [
    # Local XTTS / Piper if MAARS_LOCAL_TTS_URL is set — $0/char.
    {"provider": "local",      "model": "local-tts",            "caller": _local_tts},
    # FREE-first: Edge TTS (Microsoft) is unlimited, 400+ voices, quality
    # matches OpenAI tts-1. Zero cost. Falls back to paid only if the
    # edge-tts package or network fails.
    {"provider": "edge",       "model": "en-US-JennyNeural",   "caller": mp.call_edge_tts},
    {"provider": "openai",     "model": "tts-1",                "caller": mp.call_openai_tts},
    {"provider": "elevenlabs", "model": "eleven_flash_v2_5",    "caller": mp.call_elevenlabs_tts},
]
TTS_CHAIN_PREMIUM = [
    # Premium still prefers local XTTS when configured (voice cloning +
    # emotion control rival ElevenLabs). ElevenLabs retained as paid
    # failover with brand-voice library.
    {"provider": "local",      "model": "local-tts-premium",    "caller": _local_tts},
    # Voice-over / narration / brand voice — ElevenLabs quality first
    # when the key is funded; Edge is a very close 2nd at $0 so it acts
    # as the failover if ElevenLabs quota is exhausted.
    {"provider": "elevenlabs", "model": "eleven_turbo_v2_5",    "caller": mp.call_elevenlabs_tts},
    {"provider": "elevenlabs", "model": "eleven_multilingual_v2", "caller": mp.call_elevenlabs_tts},
    {"provider": "edge",       "model": "en-US-ChristopherNeural", "caller": mp.call_edge_tts},
    {"provider": "openai",     "model": "tts-1-hd",              "caller": mp.call_openai_tts},
]

STT_CHAIN = [
    # Local whisper.cpp — $0 / minute, stays on the box.
    {"provider": "local",    "model": "local-whispercpp",        "caller": _local_stt},
    # Groq runs Whisper on their LPU — 100x faster than OpenAI, free tier
    # covers a generous monthly quota. Pushed to top because latency AND
    # cost both beat Deepgram here.
    {"provider": "groq",     "model": "whisper-large-v3-turbo",  "caller": mp.call_groq_stt},
    # Deepgram Nova-2: 45K free minutes/mo, ~300ms latency. Second choice
    # if Groq is tripped or the operator hasn't set GROQ_API_KEY.
    {"provider": "deepgram", "model": "nova-2",                  "caller": mp.call_deepgram_stt},
    {"provider": "openai",   "model": "whisper-1",               "caller": mp.call_openai_stt},
]


# ───────────────────────────────────────────────────────── cost helpers
def _image_cost_usd(model: str) -> float:
    return MODEL_COSTS_MAP.get(model, {}).get("input", 0.02)


def _video_cost_usd(model: str, duration: int) -> float:
    per_sec = MODEL_COSTS_MAP.get(model, {}).get("input", 0.10)
    return per_sec * max(duration, 1)


def _tts_cost_usd(model: str, chars: int) -> float:
    per_1k = MODEL_COSTS_MAP.get(model, {}).get("input", 0.015)
    return per_1k * (max(chars, 1) / 1000)


def _stt_cost_usd(model: str, seconds: float) -> float:
    per_min = MODEL_COSTS_MAP.get(model, {}).get("input", 0.006)
    return per_min * (max(seconds, 1) / 60)


def _credits(usd: float) -> int:
    """Ceiling-rounded credits. Floor of 1 credit for any billed call."""
    import math
    if usd <= 0:
        return 1
    return max(1, math.ceil(usd / USD_PER_CREDIT))


# ─────────────────────────────────────────────────────────── routers
async def _run_chain(chain: list[dict], call_kwargs: dict, cost_fn, cost_args: tuple):
    """Walk the chain, try each entry, return (bytes_or_text, meta) on first success.

    Looks up admin-configured API keys from DB once and passes per-provider key
    into each helper so the router works regardless of env-var state.
    """
    start = time.time()
    errors = []
    # Pull admin keys once per request (DB or env fallback).
    try:
        keys = await get_api_keys()
    except Exception:
        keys = {}
    # Override-wins: if caller passed api_key in call_kwargs, keep it.
    override = call_kwargs.pop("api_key", None)
    for idx, entry in enumerate(chain):
        caller = entry["caller"]
        provider = entry["provider"]
        provider_key = override or keys.get(provider) or None
        try:
            # Filter call_kwargs to what the caller actually accepts so
            # optional params (e.g. `language` on ElevenLabs, `model`
            # rejected by call_fal_video) don't break sibling providers
            # that don't share that signature.
            import inspect
            sig = inspect.signature(caller)
            accepts = set(sig.parameters.keys())
            safe_kwargs = {k: v for k, v in call_kwargs.items() if k in accepts}
            extra = {}
            if "model" in accepts:
                extra["model"] = entry["model"]
            if "api_key" in accepts:
                extra["api_key"] = provider_key
            result = await caller(**safe_kwargs, **extra)
            usd = cost_fn(entry["model"], *cost_args)
            return result, {
                "provider": entry["provider"],
                "model": entry["model"],
                "cost_usd": round(usd, 6),
                "cost_credits": _credits(usd),
                "wall_s": round(time.time() - start, 2),
                "attempt": idx + 1,
                "chain_len": len(chain),
                "prior_errors": errors,
            }
        except Exception as e:
            errors.append(f"{entry['provider']}/{entry['model']}: {type(e).__name__}: {str(e)[:200]}")
            logger.warning(f"media router fallback #{idx+1}: {errors[-1]}")
            continue
    raise RuntimeError(f"media router: all {len(chain)} providers failed: {' | '.join(errors)}")


async def route_image(
    prompt: str,
    quality: str = "standard",  # "draft" | "standard" | "premium"
    size: str = "1024x1024",
    api_key_override: Optional[str] = None,
    enhance: bool = True,
    user_id: Optional[str] = None,
) -> tuple[bytes, dict]:
    """Pick cheapest capable image provider, call it, fall back on failure.

    Prompt enhancement layer (services.prompt_enhancer) rewrites the
    caller's prompt into a production-quality brief before dispatch
    unless `enhance=False` or `quality="draft"`. This is what makes
    generated output look art-directed instead of generic-stock.
    """
    effective_prompt = prompt
    enhance_meta: dict = {"enhanced": False}
    if enhance and quality != "draft":
        from services.prompt_enhancer import enhance_prompt
        effective_prompt, enhance_meta = await enhance_prompt(
            prompt, modality="image", quality=quality, user_id=user_id,
        )
        enhance_meta["enhanced"] = enhance_meta.get("ok", False)

    chain = IMAGE_CHAIN_PREMIUM if quality == "premium" else IMAGE_CHAIN_STANDARD
    content, meta = await _run_chain(
        chain,
        {"prompt": effective_prompt, "api_key": api_key_override},
        _image_cost_usd,
        (),
    )
    meta["prompt_enhancement"] = enhance_meta
    meta["original_prompt"] = prompt
    meta["effective_prompt"] = effective_prompt
    return content, meta


async def route_video(
    prompt: str,
    duration: int = 4,
    size: str = "1280x720",
    image_path: Optional[str] = None,
    mime_type: str = "image/jpeg",
    api_key_override: Optional[str] = None,
    quality: str = "standard",
    enhance: bool = True,
    user_id: Optional[str] = None,
) -> tuple[bytes, dict]:
    """Video generation with prompt enhancement + fallback chain.

    Sora-2 is prompt-sensitive — the difference between a mediocre and
    great clip is almost entirely the prompt. Enhancement is on by
    default; pass `enhance=False` for speed or when the caller has
    already written a detailed brief.
    """
    effective_prompt = prompt
    enhance_meta: dict = {"enhanced": False}
    if enhance and quality != "draft":
        from services.prompt_enhancer import enhance_prompt
        effective_prompt, enhance_meta = await enhance_prompt(
            prompt, modality="video", quality=quality, duration=duration, user_id=user_id,
        )
        enhance_meta["enhanced"] = enhance_meta.get("ok", False)

    call_kwargs = {"prompt": effective_prompt, "size": size, "duration": duration, "api_key": api_key_override}
    if image_path:
        call_kwargs["image_path"] = image_path
        call_kwargs["mime_type"] = mime_type
    content, meta = await _run_chain(
        VIDEO_CHAIN,
        call_kwargs,
        _video_cost_usd,
        (duration,),
    )
    meta["prompt_enhancement"] = enhance_meta
    meta["original_prompt"] = prompt
    meta["effective_prompt"] = effective_prompt
    return content, meta


async def route_tts(
    text: str,
    voice: str = "nova",
    tier: str = "standard",  # "standard" | "premium"
    language: Optional[str] = None,
    api_key_override: Optional[str] = None,
) -> tuple[bytes, dict]:
    """Pick cheapest capable TTS. 'premium' forces ElevenLabs voice-over quality.

    When `language` is non-English and tier is premium, prefer the
    eleven_multilingual_v2 entry at the head of the chain so pronunciation
    comes from a model actually trained on that language rather than
    English-tuned Turbo. Edge TTS is natively multilingual across 400+
    voices, so it's a safe free fallback. OpenAI TTS doesn't take a
    language hint and is filtered out by `inspect.signature` in _run_chain.
    """
    chain = TTS_CHAIN_PREMIUM if tier == "premium" else TTS_CHAIN_STANDARD
    is_non_english = bool(language) and language.lower() not in ("en", "en-us", "en-gb")
    if is_non_english and tier == "premium":
        # Promote eleven_multilingual_v2 ahead of Turbo since Turbo is
        # English-tuned. Copy the chain so we don't mutate the module-level list.
        reordered = sorted(
            chain,
            key=lambda e: 0 if e["model"] == "eleven_multilingual_v2" else 1,
        )
        chain = reordered
    return await _run_chain(
        chain,
        {"text": text, "voice": voice, "language": language,
         "api_key": api_key_override},
        _tts_cost_usd,
        (len(text),),
    )


async def route_music(
    prompt: str,
    duration: int = 15,
    api_key_override: Optional[str] = None,
) -> tuple[bytes, dict]:
    """Generate music / ambient audio via MUSIC_CHAIN (MusicGen → Stable
    Audio → Fal MusicGen). Used by the Video-Creator compositor step
    when the brief asks for a music bed, and as a standalone endpoint."""
    content, meta = await _run_chain(
        MUSIC_CHAIN,
        {"prompt": prompt, "duration": duration, "api_key": api_key_override},
        lambda *_a, **_k: 0.02,   # rough estimate: MusicGen ≈ $0.02/15s
        (),
    )
    return content, meta


async def route_stt(
    audio_bytes: bytes,
    filename: str = "audio.webm",
    language: Optional[str] = None,
    prompt: Optional[str] = None,
    duration_seconds: float = 0.0,
    api_key_override: Optional[str] = None,
) -> tuple[str, dict]:
    return await _run_chain(
        STT_CHAIN,
        {"audio_bytes": audio_bytes, "filename": filename,
         "language": language, "prompt": prompt, "api_key": api_key_override},
        _stt_cost_usd,
        (duration_seconds,),
    )
