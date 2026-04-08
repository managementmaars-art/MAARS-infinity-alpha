---
name: minimax-api
description: MiniMax AI — MiniMax-Text-01, video generation Hailuo, voice synthesis, long context models for MAARS multimodal agents
---

# MiniMax API — MAARS Reference

## Models
```python
MINIMAX_MODELS = {
    "MiniMax-Text-01": {
        "context": "1M tokens",
        "strengths": "Ultra-long context, strong multilingual",
        "architecture": "Lightning Attention hybrid",
        "pricing": "$0.20/1M input, $1.10/1M output",
        "best_for": "Book-length documents, long RAG, Chinese + English",
    },
    "MiniMax-VL-01": {
        "multimodal": True,
        "context": "512K",
        "strengths": "Vision + long text, Chinese language vision",
        "best_for": "Document image analysis, Chinese market vision tasks",
    },
    "hailuo-video": {
        "type": "Video generation",
        "strengths": "High quality video, competitive with Kling/Runway",
        "duration": "6 seconds",
        "best_for": "Short video clips, social content",
    },
}
```

## API Integration
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.minimax.chat/v1",
    api_key=MINIMAX_API_KEY,
)

def call_minimax(prompt: str, system: str = "") -> str:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    
    response = client.chat.completions.create(
        model="MiniMax-Text-01",
        messages=messages,
        max_tokens=4096,
        temperature=0.7,
    )
    return response.choices[0].message.content

# Long document processing (1M context)
def process_long_document(document: str, task: str) -> str:
    """Process book-length documents in single call"""
    prompt = f"Task: {task}\n\nDocument:\n{document}"
    
    # Check token estimate (1 token ≈ 4 chars)
    estimated_tokens = len(prompt) // 4
    if estimated_tokens > 900_000:
        raise ValueError(f"Document too long: ~{estimated_tokens:,} tokens")
    
    return call_minimax(prompt)
```

## MiniMax TTS (High-Quality Voice)
```python
import requests, base64

def minimax_tts(text: str, voice_id: str = "Wise_Woman", 
                 output_path: str = "output.mp3"):
    """MiniMax speech synthesis — high quality multilingual"""
    resp = requests.post(
        "https://api.minimax.chat/v1/t2a_v2",
        headers={
            "Authorization": f"Bearer {MINIMAX_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "speech-01-turbo",
            "text": text,
            "stream": False,
            "voice_setting": {
                "voice_id": voice_id,
                "speed": 1.0,
                "vol": 1.0,
                "pitch": 0,
            },
            "audio_setting": {
                "audio_sample_rate": 32000,
                "bitrate": 128000,
                "format": "mp3",
            },
        }
    )
    data = resp.json()
    audio_b64 = data["data"]["audio"]
    with open(output_path, "wb") as f:
        f.write(base64.b64decode(audio_b64))
    return output_path

MINIMAX_VOICES = [
    "Wise_Woman", "Friendly_Person", "Inspirational_girl",
    "Deep_Voice_Man", "Calm_Woman", "Casual_Guy", "Lively_Girl",
    "Patient_Man", "Sweet_Girl_2", "Elegant_Man",
]
```

## Hailuo Video Generation
```python
def generate_hailuo_video(prompt: str, image_url: str = None) -> str:
    """Generate video with MiniMax Hailuo"""
    payload = {
        "model": "video-01",
        "prompt": prompt,
    }
    if image_url:
        payload["first_frame_image"] = image_url
    
    resp = requests.post(
        "https://api.minimax.chat/v1/video_generation",
        headers={"Authorization": f"Bearer {MINIMAX_API_KEY}"},
        json=payload,
    )
    task_id = resp.json()["task_id"]
    
    # Poll for completion
    import time
    while True:
        status = requests.get(
            f"https://api.minimax.chat/v1/query/video_generation?task_id={task_id}",
            headers={"Authorization": f"Bearer {MINIMAX_API_KEY}"}
        ).json()
        if status["status"] == "Success":
            return status["file_id"]
        time.sleep(5)
```

## When to Use MiniMax
- **1M context**: Cheaper than alternatives for ultra-long documents
- **Chinese market**: Strong Chinese language capabilities
- **TTS for Chinese content**: Native Chinese voice synthesis
- **Video generation**: Hailuo competitive with top-tier video models
- **Cost**: $0.20/1M tokens cheaper than most 1M context models
