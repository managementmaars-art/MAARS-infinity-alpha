---
name: elevenlabs-tts
description: ElevenLabs TTS API — voice synthesis, streaming audio, voice cloning — used in MAARS for agent voice output, voice chat, and audio content generation
---

# ElevenLabs TTS API — MAARS Reference

## Why ElevenLabs in MAARS
MAARS supports voice output for agents. Users can hear agent responses in realistic voices. Each agent has an assigned voice ID matching their persona.

## Models
| Model | Quality | Latency | Use Case |
|-------|---------|---------|----------|
| `eleven_multilingual_v2` | Highest | ~1.5s | Premium voice output |
| `eleven_turbo_v2_5` | High | ~400ms | Real-time voice chat |
| `eleven_flash_v2_5` | Good | ~75ms | Ultra-low latency |
| `eleven_monolingual_v1` | Standard | ~800ms | English-only content |

## Agent Voice Assignments (MAARS)
```python
AGENT_VOICES = {
    "agent_commander": "pNInz6obpgDQGcFmaJgB",  # Adam — authoritative
    "agent_secretary":  "EXAVITQu4vr4xnSDxMaL",  # Bella — warm, professional
    "agent_marketing":  "AZnzlk1XvdvUeBnXmlld",  # Domi — energetic
    "agent_strategist": "VR6AewLTigWG4xSOukaG",  # Arnold — deep, confident
    "agent_webdesigner":"ThT5KcBeYPX3keUQqHPh",  # Dorothy — creative
    "agent_appdev":     "g5CIjZEefAph4nQFvHAz",  # Harry — technical
    "agent_copywriter": "jBpfuIE2acCO8z3wKNLl",  # Gigi — persuasive
}
```

## Streaming TTS (MAARS pattern)
```python
import httpx

async def stream_tts(text: str, voice_id: str, model: str = "eleven_turbo_v2_5"):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream"
    
    async with httpx.AsyncClient() as client:
        async with client.stream(
            "POST", url,
            headers={"xi-api-key": ELEVENLABS_API_KEY},
            json={
                "text": text,
                "model_id": model,
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75,
                    "style": 0.0,
                    "use_speaker_boost": True,
                },
                "output_format": "mp3_44100_128",
            }
        ) as response:
            async for chunk in response.aiter_bytes(chunk_size=4096):
                yield chunk
```

## Non-streaming (for short clips)
```python
from elevenlabs import ElevenLabs

client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

audio = client.text_to_speech.convert(
    voice_id=voice_id,
    text=text,
    model_id="eleven_multilingual_v2",
    output_format="mp3_44100_128",
)
# Returns bytes
```

## Speech-to-Text (Scribe)
```python
with open("audio.mp3", "rb") as f:
    result = client.speech_to_text.convert(
        file=f,
        model_id="scribe_v1",
        language_code="en",
        diarize=True,  # speaker separation
    )
text = result.text
```

## Voice Cloning
```python
voice = client.voices.add(
    name="Custom Agent Voice",
    files=[open("sample.mp3", "rb")],
    description="Voice for MAARS agent",
)
voice_id = voice.voice_id
```

## MAARS Route: `/api/voice/synthesize`
```python
# backend/routes/voice.py
@router.post("/synthesize")
async def synthesize_voice(
    text: str,
    agent_id: str,
    model: str = "eleven_turbo_v2_5",
):
    voice_id = AGENT_VOICES.get(agent_id, "pNInz6obpgDQGcFmaJgB")
    # Stream audio back to client
    return StreamingResponse(
        stream_tts(text, voice_id, model),
        media_type="audio/mpeg",
    )
```

## Pricing
| Model | Cost per 1K chars |
|-------|------------------|
| Multilingual v2 | $0.30 |
| Turbo v2.5 | $0.15 |
| Flash v2.5 | $0.08 |

## MAARS Config
```python
{
    "provider": "elevenlabs",
    "api_key_env": "ELEVENLABS_API_KEY",
    "default_model": "eleven_turbo_v2_5",
    "default_voice": "pNInz6obpgDQGcFmaJgB",
}
```
