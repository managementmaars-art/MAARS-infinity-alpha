"""Local-GPU media adapters — zero-marginal-cost tier.

When the operator runs local inference servers (SDXL via A1111/ComfyUI,
whisper.cpp, XTTS, stable-video-diffusion), these adapters become the
first stop for every image / video / TTS / STT call. On any failure —
server not running, connection refused, HTTP 5xx — the adapter raises,
and the existing chain falls through to the paid providers.

Zero config = zero impact: if MAARS_LOCAL_*_URL env vars aren't set,
each adapter immediately signals "unavailable" so the chain skips it.

Servers supported (pick one each):

  Image:
    * A1111 / Automatic1111 WebUI   — http://localhost:7860
    * ComfyUI                        — http://localhost:8188
    * Any OpenAI-compatible image server (LocalAI, etc.)

  Video:
    * ComfyUI with SVD / CogVideo workflow
    * Any OpenAI-compatible video server (rare but emerging)

  TTS:
    * XTTS-v2 server (Coqui)         — typically http://localhost:8020
    * Piper server                   — typically http://localhost:5000

  STT:
    * whisper.cpp server             — typically http://localhost:9000
    * OpenAI-compatible Whisper      — http://localhost:8000/v1/audio

Env vars:
  MAARS_LOCAL_IMAGE_URL             (e.g. http://localhost:7860)
  MAARS_LOCAL_IMAGE_BACKEND         a1111 | comfy | openai
  MAARS_LOCAL_IMAGE_MODEL           override model id
  MAARS_LOCAL_VIDEO_URL
  MAARS_LOCAL_VIDEO_BACKEND         comfy | openai
  MAARS_LOCAL_TTS_URL
  MAARS_LOCAL_TTS_BACKEND           xtts | piper | openai
  MAARS_LOCAL_STT_URL
  MAARS_LOCAL_STT_BACKEND           whispercpp | openai
"""
from __future__ import annotations
import base64
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


class LocalUnavailable(RuntimeError):
    """Raised when a local server isn't configured or isn't reachable.
    The media_router fallthrough treats this as 'skip'."""


def _env(name: str, *fallbacks: str) -> str | None:
    for n in (name, *fallbacks):
        v = os.environ.get(n)
        if v: return v
    return None


async def _client():
    from services.http_client import get_client
    return await get_client()


# ── Image ────────────────────────────────────────────────────────────

async def call_local_image(*, prompt: str, api_key: str | None = None, **_kw) -> tuple[bytes, dict]:
    """Dispatches to whichever local image backend is configured.
    Returns (png_bytes, meta) on success; raises LocalUnavailable otherwise."""
    url = _env("MAARS_LOCAL_IMAGE_URL")
    if not url:
        raise LocalUnavailable("MAARS_LOCAL_IMAGE_URL not set")
    backend = (os.environ.get("MAARS_LOCAL_IMAGE_BACKEND") or "a1111").lower()
    model = os.environ.get("MAARS_LOCAL_IMAGE_MODEL")

    client = await _client()
    try:
        if backend == "a1111":
            # Automatic1111 Stable Diffusion WebUI
            payload = {
                "prompt": prompt,
                "steps": int(os.environ.get("MAARS_LOCAL_IMAGE_STEPS", 30)),
                "width": int(os.environ.get("MAARS_LOCAL_IMAGE_WIDTH", 1024)),
                "height": int(os.environ.get("MAARS_LOCAL_IMAGE_HEIGHT", 1024)),
                "cfg_scale": float(os.environ.get("MAARS_LOCAL_IMAGE_CFG", 7)),
                "sampler_name": os.environ.get("MAARS_LOCAL_IMAGE_SAMPLER", "DPM++ 2M Karras"),
            }
            r = await client.post(f"{url.rstrip('/')}/sdapi/v1/txt2img", json=payload, timeout=120)
            r.raise_for_status()
            data = r.json()
            imgs = data.get("images") or []
            if not imgs:
                raise LocalUnavailable("a1111 returned no images")
            return base64.b64decode(imgs[0]), {
                "provider": "local-a1111", "model": model or "local",
                "cost_usd": 0.0, "info": data.get("info", "")[:400],
            }

        if backend == "comfy":
            # ComfyUI — POST /prompt → get prompt_id → poll /history/{id}
            import json as _json
            workflow_path = os.environ.get("MAARS_LOCAL_COMFY_WORKFLOW")
            if not workflow_path or not os.path.exists(workflow_path):
                raise LocalUnavailable("MAARS_LOCAL_COMFY_WORKFLOW (path to workflow.json) required")
            with open(workflow_path, "r", encoding="utf-8") as f:
                wf = _json.load(f)
            # Substitute prompt in the first CLIPTextEncode node found.
            for node_id, node in wf.items():
                if isinstance(node, dict) and node.get("class_type") == "CLIPTextEncode":
                    node.setdefault("inputs", {})["text"] = prompt
                    break
            r = await client.post(f"{url.rstrip('/')}/prompt", json={"prompt": wf}, timeout=30)
            r.raise_for_status()
            prompt_id = r.json().get("prompt_id")
            if not prompt_id:
                raise LocalUnavailable("comfy did not return prompt_id")
            import asyncio as _a
            for _ in range(60):        # up to 5 min polling
                await _a.sleep(5)
                h = await client.get(f"{url.rstrip('/')}/history/{prompt_id}", timeout=10)
                if h.status_code >= 400: continue
                history = h.json().get(prompt_id, {})
                outputs = history.get("outputs", {})
                for node_out in outputs.values():
                    images = node_out.get("images") or []
                    if images:
                        img_meta = images[0]
                        img_r = await client.get(
                            f"{url.rstrip('/')}/view",
                            params={"filename": img_meta["filename"],
                                    "subfolder": img_meta.get("subfolder", ""),
                                    "type": img_meta.get("type", "output")},
                            timeout=30,
                        )
                        if img_r.status_code < 400 and img_r.content:
                            return img_r.content, {
                                "provider": "local-comfy", "model": model or "local",
                                "cost_usd": 0.0, "prompt_id": prompt_id,
                            }
            raise LocalUnavailable("comfy timed out waiting for image")

        if backend == "openai":
            # Any OpenAI-compatible local server (LocalAI, etc.)
            r = await client.post(
                f"{url.rstrip('/')}/v1/images/generations",
                json={"prompt": prompt, "model": model or "sdxl",
                      "size": os.environ.get("MAARS_LOCAL_IMAGE_SIZE", "1024x1024"),
                      "response_format": "b64_json"},
                timeout=120,
            )
            r.raise_for_status()
            blob = r.json()["data"][0]["b64_json"]
            return base64.b64decode(blob), {
                "provider": "local-openai-compat", "model": model or "sdxl",
                "cost_usd": 0.0,
            }
    except LocalUnavailable:
        raise
    except Exception as exc:
        raise LocalUnavailable(f"local image server error: {exc}") from exc

    raise LocalUnavailable(f"unknown backend '{backend}'")


# ── Video ────────────────────────────────────────────────────────────

async def call_local_video(*, prompt: str, duration: int = 4,
                           api_key: str | None = None, **_kw) -> tuple[bytes, dict]:
    url = _env("MAARS_LOCAL_VIDEO_URL")
    if not url:
        raise LocalUnavailable("MAARS_LOCAL_VIDEO_URL not set")
    backend = (os.environ.get("MAARS_LOCAL_VIDEO_BACKEND") or "openai").lower()
    model = os.environ.get("MAARS_LOCAL_VIDEO_MODEL", "svd")

    client = await _client()
    try:
        if backend == "openai":
            r = await client.post(
                f"{url.rstrip('/')}/v1/videos",
                json={"prompt": prompt, "model": model, "duration_seconds": duration},
                timeout=600,
            )
            r.raise_for_status()
            # Expect OpenAI-style polling OR direct bytes
            ct = (r.headers.get("content-type") or "").lower()
            if ct.startswith("video/") or ct == "application/octet-stream":
                return r.content, {"provider": "local-video-openai", "model": model, "cost_usd": 0.0}
            body = r.json()
            job_id = body.get("id") or body.get("job_id")
            if not job_id:
                raise LocalUnavailable("no job id from local video server")
            import asyncio as _a
            for _ in range(120):
                await _a.sleep(5)
                sr = await client.get(f"{url.rstrip('/')}/v1/videos/{job_id}", timeout=10)
                sr.raise_for_status()
                sb = sr.json()
                if sb.get("status") == "succeeded" and sb.get("url"):
                    vr = await client.get(sb["url"], timeout=60)
                    return vr.content, {"provider": "local-video", "model": model, "cost_usd": 0.0}
                if sb.get("status") == "failed":
                    raise LocalUnavailable("local video job failed")
            raise LocalUnavailable("local video timeout")
        if backend == "comfy":
            raise LocalUnavailable("comfy video backend: implement via workflow JSON")
    except LocalUnavailable:
        raise
    except Exception as exc:
        raise LocalUnavailable(f"local video server error: {exc}") from exc
    raise LocalUnavailable(f"unknown video backend '{backend}'")


# ── TTS ──────────────────────────────────────────────────────────────

async def call_local_tts(*, text: str, voice: str | None = None,
                         api_key: str | None = None, **_kw) -> tuple[bytes, dict]:
    url = _env("MAARS_LOCAL_TTS_URL")
    if not url:
        raise LocalUnavailable("MAARS_LOCAL_TTS_URL not set")
    backend = (os.environ.get("MAARS_LOCAL_TTS_BACKEND") or "xtts").lower()
    model = os.environ.get("MAARS_LOCAL_TTS_MODEL", "xtts-v2")

    client = await _client()
    try:
        if backend == "xtts":
            # Coqui XTTS server — POST /tts_to_audio with {text, speaker_wav, language}
            r = await client.post(
                f"{url.rstrip('/')}/tts_to_audio",
                json={"text": text,
                      "language": os.environ.get("MAARS_LOCAL_TTS_LANG", "en"),
                      "speaker_wav": voice or os.environ.get("MAARS_LOCAL_TTS_SPEAKER")},
                timeout=90,
            )
            r.raise_for_status()
            return r.content, {"provider": "local-xtts", "model": model,
                               "cost_usd": 0.0, "voice": voice or "default"}
        if backend == "piper":
            r = await client.post(
                f"{url.rstrip('/')}/",
                content=text.encode(),
                headers={"Content-Type": "text/plain"}, timeout=60,
            )
            r.raise_for_status()
            return r.content, {"provider": "local-piper", "model": model, "cost_usd": 0.0}
        if backend == "openai":
            r = await client.post(
                f"{url.rstrip('/')}/v1/audio/speech",
                json={"model": model, "input": text, "voice": voice or "alloy"},
                timeout=60,
            )
            r.raise_for_status()
            return r.content, {"provider": "local-tts-openai", "model": model, "cost_usd": 0.0}
    except LocalUnavailable:
        raise
    except Exception as exc:
        raise LocalUnavailable(f"local tts server error: {exc}") from exc
    raise LocalUnavailable(f"unknown tts backend '{backend}'")


# ── STT ──────────────────────────────────────────────────────────────

async def call_local_stt(*, audio_bytes: bytes, filename: str = "audio.wav",
                         language: str | None = None,
                         api_key: str | None = None, **_kw) -> tuple[str, dict]:
    url = _env("MAARS_LOCAL_STT_URL")
    if not url:
        raise LocalUnavailable("MAARS_LOCAL_STT_URL not set")
    backend = (os.environ.get("MAARS_LOCAL_STT_BACKEND") or "whispercpp").lower()
    model = os.environ.get("MAARS_LOCAL_STT_MODEL", "whisper")

    client = await _client()
    try:
        if backend == "whispercpp":
            files = {"file": (filename, audio_bytes, "audio/wav")}
            data = {"temperature": "0.0", "response_format": "json"}
            if language: data["language"] = language
            r = await client.post(
                f"{url.rstrip('/')}/inference",
                files=files, data=data, timeout=180,
            )
            r.raise_for_status()
            body = r.json() if r.text else {}
            text = body.get("text") or body.get("transcription") or ""
            return text.strip(), {"provider": "local-whispercpp", "model": model,
                                  "cost_usd": 0.0, "duration": body.get("duration")}
        if backend == "openai":
            files = {"file": (filename, audio_bytes)}
            data = {"model": model, "response_format": "json"}
            if language: data["language"] = language
            r = await client.post(
                f"{url.rstrip('/')}/v1/audio/transcriptions",
                files=files, data=data, timeout=180,
            )
            r.raise_for_status()
            body = r.json() if r.text else {}
            return (body.get("text") or "").strip(), {"provider": "local-stt-openai",
                                                       "model": model, "cost_usd": 0.0}
    except LocalUnavailable:
        raise
    except Exception as exc:
        raise LocalUnavailable(f"local stt server error: {exc}") from exc
    raise LocalUnavailable(f"unknown stt backend '{backend}'")
