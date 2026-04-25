"""Universal media gateway — single entry point for image/video/music.

The chat gateway exposes `complete_text(model="maars/auto", ...)`. This
module exposes the parallel `complete_media(modality=..., model=..., ...)`
so every media call — from vibe-coded apps, agent SOPs, admin panels,
anywhere — goes through ONE door with ONE set of:

  - bucket-aware wallet reserve/settle   (image / video / voice pools)
  - ledger attribution                    (source + provider + model)
  - circuit-breaker aware fallback        (per media_router chains)
  - cost observability                    (cost_usd / cost_credits in meta)

Callers never touch `route_image` / `route_video` directly anymore; they
call `complete_media` which wraps the router, applies the wallet flow,
and returns (bytes, meta, billing).

`model` can be a canonical alias:
    maars/image         — cheapest usable image model
    maars/image/premium — top-quality image (dall-e-3 / flux-pro)
    maars/video         — cheapest usable video clip (Fal LTX / Zhipu)
    maars/video/premium — top-quality video (Sora / Kling / Veo)
    maars/voice         — TTS (Edge → ElevenLabs fallback)
    maars/music         — music / ambient (MusicGen → Stable Audio)
    maars/stt           — speech-to-text (Groq Whisper → Deepgram → OpenAI)

Or a concrete provider/model string like `fal/fal-ai/ltx-video` to
override routing.
"""
from __future__ import annotations
import logging
import uuid
from typing import Any, Optional
from fastapi import HTTPException

from services.billing import wallet_service
from services.llm_service import media_credit_cost

logger = logging.getLogger(__name__)


# Alias → (router_fn_name, tier, default_units) tuples.
# tier maps to quality preference inside the router's chain selection;
# default_units are the fallback estimate used for the upfront reserve.
_ALIAS_MAP: dict[str, tuple[str, str, float]] = {
    "maars/image":           ("image", "standard", 1.0),
    "maars/image/standard":  ("image", "standard", 1.0),
    "maars/image/premium":   ("image", "premium",  1.0),
    "maars/video":           ("video", "standard", 4.0),   # 4 seconds
    "maars/video/standard":  ("video", "standard", 4.0),
    "maars/video/premium":   ("video", "premium",  4.0),
    "maars/voice":           ("tts",   "standard", 500.0), # 500 chars
    "maars/voice/premium":   ("tts",   "premium",  500.0),
    "maars/music":           ("music", "standard", 15.0),  # 15 seconds
    "maars/stt":             ("stt",   "standard", 60.0),  # 60 seconds audio
}

# Modality → bucket mapping for wallet debits
_MODALITY_TO_BUCKET = {
    "image": "image", "video": "video",
    "tts":   "voice", "voiceover": "voice",
    "music": "voice",           # music bills against voice pool — same $ / token economics
    "stt":   "stt",
}


async def complete_media(
    *,
    user_id: str,
    modality: str,                         # "image"|"video"|"tts"|"stt"|"music"
    prompt: Optional[str] = None,
    model: str = "auto",                   # alias ("maars/video") or "auto"
    quality: Optional[str] = None,         # "standard" | "premium"
    duration: Optional[int] = None,        # for video/music/stt
    size: Optional[str] = None,
    voice: Optional[str] = None,           # for tts
    language: Optional[str] = None,        # for tts / stt
    audio_bytes: Optional[bytes] = None,   # for stt input
    filename: Optional[str] = None,        # for stt input naming
    source: str = "media.complete",
    api_key_override: Optional[str] = None,
    agent_id: Optional[str] = None,
    **kwargs: Any,
) -> tuple[Any, dict, dict]:
    """Universal-gateway-style wrapper around route_image/route_video/…

    Returns `(payload, router_meta, billing)` where payload is bytes (or
    text, for STT), `router_meta` is what the router chain returned
    (provider, model, cost_usd, attempt, chain_len), and `billing` has
    wallet reserve/actual/refunded credit counts.
    """
    from services import media_router

    # Resolve alias → (modality, tier, default_units)
    alias = model
    if model.startswith("maars/"):
        info = _ALIAS_MAP.get(model)
        if info:
            modality_from_alias, tier_from_alias, default_units = info
            # Caller can override modality; if not, honor the alias.
            modality = modality or modality_from_alias
            quality = quality or tier_from_alias
        else:
            raise ValueError(f"unknown media alias '{model}'")

    modality = modality.lower()
    quality = (quality or "standard").lower()

    # Pick the router function + a sensible units estimate for the reserve.
    if modality == "image":
        units = 1.0
        router_call = lambda: media_router.route_image(
            prompt=prompt or "", quality=quality,
            size=size or "1024x1024",
            api_key_override=api_key_override,
            enhance=kwargs.get("enhance", True),
            user_id=user_id,
        )
        cost_model_stub = "gpt-image-1" if quality != "premium" else "dall-e-3"
    elif modality == "video":
        units = float(duration or 4)
        router_call = lambda: media_router.route_video(
            prompt=prompt or "", duration=int(units),
            size=size or "1280x720",
            image_path=kwargs.get("image_path"),
            mime_type=kwargs.get("mime_type", "image/jpeg"),
            api_key_override=api_key_override,
            quality=quality,
            enhance=kwargs.get("enhance", True),
            user_id=user_id,
        )
        cost_model_stub = "fal-ai/ltx-video" if quality != "premium" else "sora-2"
    elif modality in ("tts", "voiceover"):
        units = float(len(prompt or ""))
        router_call = lambda: media_router.route_tts(
            text=prompt or "", voice=voice or "nova",
            tier=quality, language=language,
            api_key_override=api_key_override,
        )
        cost_model_stub = "tts-1" if quality != "premium" else "eleven_turbo_v2_5"
    elif modality == "music":
        units = float(duration or 15)
        router_call = lambda: media_router.route_music(
            prompt=prompt or "", duration=int(units),
            api_key_override=api_key_override,
        )
        cost_model_stub = "fal-ai/musicgen"
    elif modality == "stt":
        if audio_bytes is None:
            raise ValueError("stt requires audio_bytes")
        units = float(duration or 60)
        router_call = lambda: media_router.route_stt(
            audio_bytes=audio_bytes,
            filename=filename or "audio.webm",
            language=language,
            duration_seconds=units,
            api_key_override=api_key_override,
        )
        cost_model_stub = "whisper-large-v3-turbo"
    else:
        raise ValueError(f"unsupported modality: {modality}")

    # Bucket lookup + credit reserve (same flow as media_billing)
    bucket = _MODALITY_TO_BUCKET.get(modality, "general")
    estimate = media_credit_cost(modality, cost_model_stub, units)
    ref_id = f"{modality}_{uuid.uuid4().hex[:12]}"

    reserve_result = await wallet_service.reserve(
        user_id, estimate,
        reference_id=ref_id,
        description=f"Reserve {modality} (alias={alias}, ~{units} units)",
        metadata={"modality": modality, "alias": alias, "quality": quality,
                  "bucket": bucket, "agent_id": agent_id, "source": source},
        bucket=bucket,
        source=source or f"media_{modality}",
    )
    if reserve_result is None:
        raise HTTPException(status_code=402, detail={
            "error": {
                "message": (f"Insufficient {bucket} credits. Need ~{estimate}. "
                            f"Top up or switch to a cheaper alias."),
                "type": "insufficient_credits",
                "code": "insufficient_credits",
                "bucket": bucket,
                "credits_required": estimate,
                "modality": modality,
            }
        })

    try:
        result, meta = await router_call()
    except Exception as exc:
        logger.warning("complete_media(%s/%s) failed: %s", modality, alias, exc)
        try:
            await wallet_service.settle(
                user_id, reserved_amount=estimate, actual_amount=0,
                reference_id=ref_id,
                description=f"Refund {modality} alias={alias} (provider failed)",
                metadata={"modality": modality, "failed": True, "bucket": bucket},
                bucket=bucket,
            )
        except Exception as settle_err:
            logger.error("settle-on-fail failed for %s: %s", ref_id, settle_err)
        raise

    actual = int(meta.get("cost_credits") or estimate)
    wallet_after = await wallet_service.settle(
        user_id, reserved_amount=estimate, actual_amount=actual,
        reference_id=ref_id,
        description=f"Settle {modality} alias={alias} "
                    f"({meta.get('provider')}/{meta.get('model')})",
        metadata={"modality": modality, "alias": alias,
                  "router_meta": meta, "bucket": bucket},
        bucket=bucket,
    )

    billing = {
        "reference_id":      ref_id,
        "alias":             alias,
        "modality":          modality,
        "bucket":            bucket,
        "reserved_credits":  estimate,
        "actual_credits":    actual,
        "refunded_credits":  max(0, estimate - actual),
        "wallet":            wallet_after,
    }
    return result, meta, billing


def list_aliases() -> list[dict[str, Any]]:
    """Enumerate the media aliases for /admin/gateway/aliases + UI pickers."""
    out: list[dict[str, Any]] = []
    for alias, (modality, tier, _units) in _ALIAS_MAP.items():
        out.append({
            "alias":    alias,
            "modality": modality,
            "tier":     tier,
            "bucket":   _MODALITY_TO_BUCKET.get(modality, "general"),
        })
    return out
