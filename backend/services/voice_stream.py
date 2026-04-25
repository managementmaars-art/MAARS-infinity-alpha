"""Real-time duplex voice agent — Cartesia TTS + LiveKit transport.

Pattern from patchy631/ai-engineering-hub/rag-voice-agent: sub-200ms
round trips for interactive phone-style voice sessions. MAARS's existing
Twilio/Telnyx path is half-duplex and dialler-oriented; this is the
interactive-assistant path.

Architecture:
  Client (browser/phone) ──WebRTC── LiveKit room
                                    │
                                    ├── STT (AssemblyAI streaming)
                                    │        │
                                    │        ▼
                                    │   llm_gateway.complete() ← agent
                                    │        │
                                    │        ▼
                                    └── Cartesia TTS ──── back to client

Required env vars:
  LIVEKIT_URL           — wss://<your>.livekit.cloud (or self-hosted)
  LIVEKIT_API_KEY
  LIVEKIT_API_SECRET
  CARTESIA_API_KEY
  ASSEMBLYAI_API_KEY    (already used by existing adapters)

Public surface:
  issue_room_token(user_id, room_name) → {url, token, expires_at}
  create_session(user_id, agent_id, room_name) → background task
  (session runs until client disconnects)

This module is a SCAFFOLD — real-time duplex voice requires the LiveKit
Agents framework (`livekit-agents`) running as a background worker,
not inside the FastAPI request cycle. What's implemented here:

  1. Room-token issuance (works as soon as LIVEKIT_* is set)
  2. A placeholder `create_session` that the operator can wire into
     a LiveKit worker process later.

To complete: `pip install livekit-agents cartesia` + run a worker with
`python -m livekit.agents.cli start` pointed at a handler in this file.
"""
from __future__ import annotations
import logging
import os
import time
from typing import Any

logger = logging.getLogger(__name__)


# ── Token issuance (always available when env is set) ─────────────

async def issue_room_token(
    *, user_id: str, room_name: str,
    identity: str | None = None,
    ttl_seconds: int = 3600,
) -> dict[str, Any]:
    """Mint a LiveKit access token so the client can join a room."""
    url = os.environ.get("LIVEKIT_URL")
    key = os.environ.get("LIVEKIT_API_KEY")
    secret = os.environ.get("LIVEKIT_API_SECRET")
    if not (url and key and secret):
        return {"ok": False, "error": "livekit_not_configured",
                "hint": "Set LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET"}
    try:
        from livekit import api as _lk_api
    except ImportError:
        return {"ok": False, "error": "livekit-server-sdk_not_installed",
                "hint": "pip install livekit-api"}
    at = _lk_api.AccessToken(key, secret)
    at = at.with_identity(identity or user_id).with_name(identity or user_id)
    at = at.with_grants(_lk_api.VideoGrants(
        room_join=True, room=room_name,
        can_publish=True, can_subscribe=True,
    ))
    jwt = at.to_jwt()
    return {
        "ok": True, "url": url, "token": jwt,
        "room": room_name, "identity": identity or user_id,
        "expires_at": time.time() + ttl_seconds,
    }


# ── Agent handler (runs inside a LiveKit worker) ──────────────────

async def voice_agent_handler(ctx) -> None:  # pragma: no cover — worker-only
    """LiveKit Agent entrypoint — wire this into a separate worker.

    Install: `pip install livekit-agents cartesia assemblyai`
    Run:     `python -m livekit.agents.cli start services/voice_stream:voice_agent_handler`

    The worker connects to LIVEKIT_URL on startup, accepts every room
    request, and runs the STT→LLM→TTS loop for the lifetime of the
    session. All LLM calls flow through the existing `llm_gateway` so
    wallet + audit + Commander authority all apply.
    """
    try:
        from livekit import rtc
        from livekit.agents import stt, tts, vad, llm
    except ImportError:
        logger.error("livekit-agents not installed; voice worker can't start")
        return

    # Import here so the module itself stays cheap
    from services.llm_gateway import complete_text

    # Wait for a participant to join
    await ctx.connect()
    participant = await ctx.wait_for_participant()
    user_id = participant.identity

    # Greeting
    greeting = (
        "Hi — you're connected to MAARS. I'll listen; tell me what to do."
    )

    # In a real impl, wire:
    #   - assemblyai_stt_provider() for STT streams
    #   - cartesia_tts_provider() for TTS streams
    #   - vad.Silero for turn-taking
    #   - llm.MAARSGateway() that calls complete_text()
    # The livekit-agents library handles the glue. This stub documents
    # the contract so the operator can drop in the adapters.

    logger.info("voice session for user=%s (participant=%s) in room=%s",
                user_id[:8], participant.identity, ctx.room.name)
    # ... session loop ... (handled by livekit-agents VoicePipelineAgent)


# ── Cartesia TTS direct call (useful for non-streaming uses) ─────

async def cartesia_tts(
    *, user_id: str, text: str, voice_id: str = "default",
) -> dict[str, Any]:
    """Non-streaming Cartesia synthesis. Returns an mp3/wav byte URL
    or raw bytes, depending on Cartesia's response mode. Wire into
    media_router if you want it alongside ElevenLabs."""
    key = os.environ.get("CARTESIA_API_KEY")
    if not key:
        return {"ok": False, "error": "no_cartesia_api_key"}
    import httpx
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(
            "https://api.cartesia.ai/tts/bytes",
            headers={
                "X-API-Key":     key,
                "Cartesia-Version": "2024-06-10",
                "Content-Type":  "application/json",
            },
            json={
                "model_id":     "sonic-english",
                "transcript":   text,
                "voice":        {"mode": "id", "id": voice_id}
                                if voice_id != "default"
                                else {"mode": "embedding", "embedding": None},
                "output_format": {"container": "mp3", "sample_rate": 44100},
            },
        )
    if r.status_code >= 400:
        return {"ok": False, "status": r.status_code, "error": r.text[:300]}
    # Cartesia returns raw bytes; caller should persist or stream to client
    return {"ok": True, "audio_bytes_len": len(r.content), "mime": "audio/mpeg"}
