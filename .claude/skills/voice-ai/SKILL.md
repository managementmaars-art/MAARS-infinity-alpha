---
name: voice-ai
description: AI voice synthesis, cloning, STT, real-time voice agents — ElevenLabs, Deepgram, Cartesia, PlayHT, Whisper, VAPI for MAARS voice agents
---

# Voice AI — MAARS Reference

## TTS Provider Comparison
```python
TTS_PROVIDERS = {
    "elevenlabs": {
        "quality": "Best-in-class naturalness",
        "voices": "3000+ + custom clones",
        "latency": "~300ms streaming",
        "pricing": "$0.15-0.30/1k chars",
        "features": ["Voice cloning", "Emotion control", "Multilingual", "Studio"],
        "best_for": "High-quality production audio",
    },
    "cartesia": {
        "quality": "Fastest with excellent quality",
        "latency": "<100ms TTFB",
        "pricing": "$0.065/1k chars",
        "features": ["Ultra-low latency", "Real-time voice", "Custom voices"],
        "best_for": "Real-time conversational AI",
    },
    "playht": {
        "quality": "Very good, ultra-realistic",
        "voices": "900+ voices, 142 languages",
        "pricing": "$0.06-0.10/1k chars",
        "features": ["Voice cloning (instant)", "Emotion", "Podcast"],
        "best_for": "Podcast/long-form production",
    },
    "openai_tts": {
        "quality": "Good, consistent",
        "voices": ["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
        "pricing": "$15/1M chars (HD: $30/1M)",
        "models": ["tts-1", "tts-1-hd"],
        "best_for": "Quick integration, cost-effective at scale",
    },
    "google_tts": {
        "quality": "Good",
        "voices": "380+ voices, 50+ languages",
        "pricing": "$4-16/1M chars",
        "features": ["WaveNet", "Neural2", "Custom voice"],
        "best_for": "Enterprise, Google Cloud users",
    },
    "azure_tts": {
        "voices": "500+ voices, 140+ languages",
        "features": ["Neural voices", "Custom Neural Voice", "Avatar"],
        "pricing": "$4/1M chars (Neural: $16/1M)",
        "best_for": "Microsoft/Azure stack, compliance",
    },
}
```

## ElevenLabs Streaming
```python
from elevenlabs import ElevenLabs, stream

client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

# Streaming TTS (real-time)
def stream_tts(text: str, voice_id: str = "EXAVITQu4vr4xnSDxMaL"):
    audio = client.text_to_speech.convert_as_stream(
        voice_id=voice_id,
        text=text,
        model_id="eleven_turbo_v2_5",  # fastest
        voice_settings={
            "stability": 0.5,
            "similarity_boost": 0.8,
            "style": 0.3,
            "use_speaker_boost": True,
        },
    )
    stream(audio)

# Voice cloning
def clone_voice(name: str, audio_files: list[str]):
    voice = client.clone(
        name=name,
        description="Custom voice clone",
        files=audio_files,  # 1-30 min of audio
    )
    return voice.voice_id

# Conversational AI (WebSocket)
conversation = client.conversational_ai.create_conversation(
    agent_id=AGENT_ID,
    requires_auth=True,
)
```

## Deepgram — STT (Best for Real-time)
```python
from deepgram import DeepgramClient, PrerecordedOptions, LiveOptions

dg = DeepgramClient(DEEPGRAM_API_KEY)

# Pre-recorded transcription
def transcribe_file(audio_path: str):
    with open(audio_path, "rb") as f:
        source = {"buffer": f.read(), "mimetype": "audio/mp3"}
    opts = PrerecordedOptions(
        model="nova-3",      # best accuracy
        smart_format=True,   # punctuation, numbers
        diarize=True,        # speaker labels
        language="en-US",
        summarize="v2",      # auto summary
        topics=True,         # topic detection
    )
    return dg.listen.rest.v("1").transcribe_file(source, opts)

# Real-time streaming STT
async def live_transcription(ws_connection):
    dg_connection = dg.listen.asyncwebsocket.v("1")
    await dg_connection.start(LiveOptions(
        model="nova-3",
        language="en-US",
        smart_format=True,
        interim_results=True,
        endpointing=300,      # ms silence = end of speech
    ))
    # Stream audio chunks from ws_connection
    async for chunk in ws_connection:
        await dg_connection.send(chunk)
```

## Cartesia — Ultra-Low Latency
```python
import httpx

def cartesia_tts_stream(text: str, voice_id: str):
    with httpx.stream("POST",
        "https://api.cartesia.ai/tts/bytes",
        headers={"X-API-Key": CARTESIA_API_KEY, "Cartesia-Version": "2024-06-10"},
        json={
            "transcript": text,
            "model_id": "sonic-english",
            "voice": {"mode": "id", "id": voice_id},
            "output_format": {"container": "raw", "encoding": "pcm_f32le", "sample_rate": 44100},
        }
    ) as r:
        for chunk in r.iter_bytes(chunk_size=4096):
            yield chunk  # stream to audio player
```

## VAPI — Voice Agent Platform
```python
VAPI_AGENT_CONFIG = {
    "name": "MAARS Voice Agent",
    "model": {
        "provider": "anthropic",
        "model": "claude-sonnet-4-6",
        "systemPrompt": "You are a helpful MAARS assistant. Keep responses concise for voice.",
    },
    "voice": {
        "provider": "elevenlabs",
        "voiceId": "EXAVITQu4vr4xnSDxMaL",
    },
    "transcriber": {
        "provider": "deepgram",
        "model": "nova-3",
        "language": "en-US",
    },
    "firstMessage": "Hi! How can I help you today?",
    "endCallPhrases": ["goodbye", "bye", "hang up", "end call"],
    "functions": [
        {
            "name": "transfer_call",
            "description": "Transfer to human agent",
            "parameters": {"department": {"type": "string"}},
        }
    ],
}

# Create VAPI call
import requests

def create_vapi_call(phone_number: str, agent_config: dict):
    return requests.post(
        "https://api.vapi.ai/call/phone",
        headers={"Authorization": f"Bearer {VAPI_API_KEY}"},
        json={"phoneNumberId": PHONE_ID, "customer": {"number": phone_number},
              "assistant": agent_config}
    ).json()
```

## Real-Time Voice Pipeline
```python
VOICE_PIPELINE = {
    "architecture": "WebSocket → STT → LLM → TTS → WebSocket",
    "latency_budget": {
        "stt_ttfb": "100-300ms (Deepgram Nova-3)",
        "llm_ttft": "200-500ms (Claude Sonnet streaming)",
        "tts_ttfb": "50-100ms (Cartesia Sonic)",
        "total_perceived": "<1 second response",
    },
    "optimizations": [
        "Stream LLM output sentence-by-sentence to TTS",
        "Start TTS on first sentence while LLM generates rest",
        "Use endpointing (300ms silence) for fast STT cutoff",
        "Keep system prompt under 500 tokens for speed",
        "Cache TTS for common phrases (greetings, transitions)",
    ],
}

# Sentence streamer for LLM→TTS pipeline
import re

def stream_sentences(text_generator):
    """Buffer LLM stream and emit complete sentences to TTS"""
    buffer = ""
    for chunk in text_generator:
        buffer += chunk
        sentences = re.split(r'(?<=[.!?])\s+', buffer)
        for sentence in sentences[:-1]:
            if len(sentence) > 10:  # skip fragments
                yield sentence
        buffer = sentences[-1]
    if buffer.strip():
        yield buffer
```

## Voice Cloning Best Practices
```python
CLONING_TIPS = {
    "audio_requirements": {
        "duration": "10-30 minutes for best quality",
        "quality": "Studio or near-studio (minimal background noise)",
        "variety": "Different sentences, emotions, pacing",
        "format": "WAV 44.1kHz or MP3 320kbps",
    },
    "instant_clone": {
        "providers": ["ElevenLabs", "PlayHT", "Resemble AI"],
        "min_audio": "30 seconds (reduced quality)",
        "use_case": "Demos, prototypes, non-critical voice",
    },
    "professional_clone": {
        "providers": ["ElevenLabs Professional", "Murf", "Respeecher"],
        "min_audio": "2+ hours",
        "use_case": "Brand voice, celebrity, long-term deployment",
    },
    "consent_required": True,  # Always get written consent for voice cloning
}
```

## Models to Use
- **Production TTS**: `elevenlabs/eleven_turbo_v2_5` (quality) or `cartesia/sonic` (speed)
- **Real-time STT**: `deepgram/nova-3` (best accuracy + speed)
- **Batch STT**: `openai/whisper-1` (cost-effective)
- **Voice agents**: VAPI platform + ElevenLabs + Deepgram + Claude Sonnet
- **Voice cloning**: ElevenLabs (quality), PlayHT (instant)
- **Multilingual**: `azure/neural` or `google/wavenet`
