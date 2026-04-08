---
name: video-ai
description: AI video generation, editing, transcription, analysis — Runway, Kling, Sora, Pika, HeyGen, Synthesia, Whisper for MAARS video production agents
---

# Video AI — MAARS Reference

## Video Generation Models
```python
VIDEO_MODELS = {
    "runway_gen4": {
        "api": "https://api.runwayml.com/v1",
        "strengths": "Cinematic quality, motion control, camera moves",
        "max_duration": "16 seconds",
        "resolutions": ["1280x768", "768x1280"],
        "pricing": "$0.05/second",
        "use_cases": ["Product demos", "Ad creative", "B-roll"],
    },
    "kling_2.0": {
        "provider": "Kuaishou via fal.ai or replicate",
        "strengths": "Long form (3-5 min), realistic motion, lip sync",
        "max_duration": "5 minutes",
        "pricing": "$0.03/second",
        "use_cases": ["Long ads", "Explainer videos", "Social content"],
    },
    "pika_2.2": {
        "api": "https://api.pika.art",
        "strengths": "Fast gen, style control, image-to-video",
        "max_duration": "10 seconds",
        "use_cases": ["Quick social clips", "Product animations"],
    },
    "sora": {
        "provider": "OpenAI",
        "strengths": "Highest quality, physics understanding",
        "access": "ChatGPT Plus / API (limited)",
        "use_cases": ["Brand films", "High-end production"],
    },
    "luma_dream_machine": {
        "api": "https://lumaai.com/api",
        "strengths": "3D-consistent video, loop generation",
        "use_cases": ["Product 360 views", "Loop animations"],
    },
    "minimax_video": {
        "strengths": "Chinese market, multilingual lip sync",
        "use_cases": ["Localization", "Asian market content"],
    },
}
```

## Runway API Integration
```python
import requests

def generate_runway_video(prompt: str, image_url: str = None, duration: int = 10):
    headers = {
        "Authorization": f"Bearer {RUNWAY_API_KEY}",
        "Content-Type": "application/json",
        "X-Runway-Version": "2024-11-06",
    }
    payload = {
        "model": "gen4_turbo",
        "promptText": prompt,
        "duration": duration,
        "ratio": "1280:768",
    }
    if image_url:
        payload["promptImage"] = image_url  # image-to-video

    # Submit task
    resp = requests.post("https://api.runwayml.com/v1/image_to_video",
                        json=payload, headers=headers)
    task_id = resp.json()["id"]

    # Poll for completion
    import time
    while True:
        status = requests.get(f"https://api.runwayml.com/v1/tasks/{task_id}",
                             headers=headers).json()
        if status["status"] == "SUCCEEDED":
            return status["output"][0]  # video URL
        elif status["status"] == "FAILED":
            raise Exception(status["error"])
        time.sleep(5)
```

## HeyGen / Synthesia — AI Avatars
```python
AVATAR_VIDEO_PROMPT = """
Script for avatar video:
Product: {product}
Avatar: {avatar_style} (professional/casual/custom)
Voice: {voice} (language + accent)
Duration: {target_minutes} minutes
Platform: {platform} (YouTube/LinkedIn/Website)

Script structure:
- Hook (0-10s): Bold statement or question
- Problem (10-40s): Pain point empathy
- Solution (40s-2min): Product demonstration
- Social proof (2-2.5min): Stats or testimonial
- CTA (last 20s): Clear next step + urgency

Keep sentences short (max 15 words) for avatar lip sync.
Avoid jargon. Use "you" language.
"""

# HeyGen API
import requests

def create_heygen_video(script: str, avatar_id: str, voice_id: str):
    resp = requests.post(
        "https://api.heygen.com/v2/video/generate",
        headers={"X-Api-Key": HEYGEN_API_KEY},
        json={
            "video_inputs": [{
                "character": {"type": "avatar", "avatar_id": avatar_id},
                "voice": {"type": "text", "input_text": script, "voice_id": voice_id},
                "background": {"type": "color", "value": "#f0f0f0"},
            }],
            "dimension": {"width": 1920, "height": 1080},
        }
    )
    return resp.json()["data"]["video_id"]
```

## Video Transcription & Analysis
```python
import openai

def transcribe_video(audio_path: str, language: str = "en"):
    """Transcribe using OpenAI Whisper"""
    client = openai.OpenAI()
    with open(audio_path, "rb") as f:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            language=language,
            response_format="verbose_json",  # includes timestamps
        )
    return transcript

def analyze_video_with_vision(video_frames: list, question: str):
    """Analyze extracted video frames"""
    client = openai.OpenAI()
    messages = [{
        "role": "user",
        "content": [
            {"type": "text", "text": question},
            *[{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{frame}"}}
              for frame in video_frames[:10]]  # max 10 frames
        ]
    }]
    return client.chat.completions.create(model="gpt-4o", messages=messages)

# Extract frames from video
import cv2, base64

def extract_frames(video_path: str, num_frames: int = 10) -> list:
    cap = cv2.VideoCapture(video_path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frames = []
    for i in range(num_frames):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i * total // num_frames)
        ret, frame = cap.read()
        if ret:
            _, buf = cv2.imencode(".jpg", frame)
            frames.append(base64.b64encode(buf).decode())
    cap.release()
    return frames
```

## Video Editing Automation
```python
# FFmpeg wrapper for common tasks
import subprocess

def add_captions(video_path: str, srt_path: str, output: str):
    """Burn subtitles into video"""
    subprocess.run([
        "ffmpeg", "-i", video_path,
        "-vf", f"subtitles={srt_path}:force_style='FontSize=24,PrimaryColour=&Hffffff'",
        "-c:a", "copy", output
    ])

def clip_video(video_path: str, start: str, duration: str, output: str):
    """Cut a clip: start='00:01:30', duration='00:00:15'"""
    subprocess.run(["ffmpeg", "-i", video_path, "-ss", start, "-t", duration,
                    "-c", "copy", output])

def resize_for_platform(video_path: str, platform: str, output: str):
    formats = {
        "instagram_reel": "1080:1920",
        "youtube": "1920:1080",
        "tiktok": "1080:1920",
        "linkedin": "1920:1080",
        "twitter": "1280:720",
    }
    vf = f"scale={formats[platform]},setsar=1"
    subprocess.run(["ffmpeg", "-i", video_path, "-vf", vf, "-c:a", "copy", output])
```

## Content Strategy by Platform
```python
VIDEO_STRATEGY = {
    "youtube": {
        "optimal_length": "8-15 minutes (watch time)",
        "hook": "First 30 seconds critical — ask a question or make a claim",
        "cta": "Subscribe prompt at 30% mark, link in description",
        "seo": "Title: keyword first, Description: transcript excerpt",
    },
    "tiktok": {
        "optimal_length": "21-34 seconds (highest completion)",
        "hook": "First 2 seconds — visual pattern interrupt",
        "trending": "Use trending sounds even for brand content",
        "posting": "3-5x/day for growth phase",
    },
    "instagram_reels": {
        "optimal_length": "7-15 seconds",
        "hook": "Text overlay in first frame",
        "captions": "Always (85% watch muted)",
    },
    "linkedin": {
        "optimal_length": "30-90 seconds",
        "style": "Talking head, professional, no music",
        "best_time": "Tuesday-Thursday 8-10am",
    },
}
```

## Models to Use
- **Video generation**: `runway-gen4-turbo`, `kling-2.0` (fal.ai), `pika-2.2`
- **Transcription**: `whisper-1` (OpenAI)
- **Video analysis/understanding**: `gpt-4o` with frames, `claude-opus-4-6`
- **Script writing**: `claude-sonnet-4-6`
- **Avatar videos**: HeyGen API, Synthesia API
- **Lip sync**: `wav2lip` (open source), HeyGen
