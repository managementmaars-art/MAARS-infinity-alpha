#!/usr/bin/env python3
"""
Analyze a video thumbnail (or full MP4) using Gemini and produce an engineer-grade report.

Usage:
  # Thumbnail only (no disk space needed for video):
  python3 analyze_video.py --thumb /tmp/thumb.gif --title "Bug report" --description "..." --duration 143

  # Full video:
  python3 analyze_video.py --video /tmp/video.mp4 --title "..." --context "This is a bug report for..."

Requires: GOOGLE_GENERATIVE_AI_API_KEY in environment
"""

import argparse, base64, json, os, sys, urllib.request

MODEL = "gemini-2.5-flash"
API_KEY = os.environ.get("GOOGLE_GENERATIVE_AI_API_KEY", "")


def build_prompt(title: str, description: str, duration: int, context: str) -> str:
    meta = f"Title: {title}\nDuration: ~{duration // 60}:{duration % 60:02d}\n"
    if description:
        meta += f"Auto-description: {description}\n"
    if context:
        meta += f"Context: {context}\n"

    return f"""You are analyzing a screen recording video.

{meta}

Describe what you see AND hear in vivid detail:

1. **What's on screen** — every visible UI element, text, number, error message, panel name, data value. Be exhaustive.
2. **What was said** — transcript or close paraphrase of narration (if audio available)
3. **Summary** — 1-2 sentences on what this video demonstrates or reports
4. **Key data points** — exact numbers, names, states in a markdown table
5. **Action items** — what an engineer/PM should do based on this

Be precise. Quote exact values. This analysis is for someone who cannot watch the video."""


def call_gemini(parts: list) -> str:
    if not API_KEY:
        sys.exit("ERROR: GOOGLE_GENERATIVE_AI_API_KEY not set")

    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {"temperature": 0.1, "maxOutputTokens": 4096}
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=90) as resp:
        result = json.load(resp)
    return result["candidates"][0]["content"]["parts"][0]["text"]


def analyze_thumbnail(thumb_path: str, prompt: str) -> str:
    ext = thumb_path.lower().split(".")[-1]
    mime = {"gif": "image/gif", "jpg": "image/jpeg", "jpeg": "image/jpeg",
            "png": "image/png", "webp": "image/webp"}.get(ext, "image/jpeg")
    with open(thumb_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return call_gemini([
        {"inline_data": {"mime_type": mime, "data": b64}},
        {"text": prompt}
    ])


def analyze_video_inline(video_path: str, prompt: str) -> str:
    size_mb = os.path.getsize(video_path) / 1024 / 1024
    if size_mb > 20:
        print(f"Warning: {size_mb:.1f}MB file — consider File API for files > 20MB")
    with open(video_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return call_gemini([
        {"inline_data": {"mime_type": "video/mp4", "data": b64}},
        {"text": prompt}
    ])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--thumb", help="Path to thumbnail image (gif/jpg/png)")
    parser.add_argument("--video", help="Path to video file (mp4)")
    parser.add_argument("--title", default="", help="Video title")
    parser.add_argument("--description", default="", help="Auto-generated description")
    parser.add_argument("--duration", type=int, default=0, help="Duration in seconds")
    parser.add_argument("--context", default="", help="Extra context for Gemini")
    args = parser.parse_args()

    if not args.thumb and not args.video:
        parser.error("Provide --thumb or --video")

    prompt = build_prompt(args.title, args.description, args.duration, args.context)

    if args.video:
        result = analyze_video_inline(args.video, prompt)
    else:
        result = analyze_thumbnail(args.thumb, prompt)

    print(result)


if __name__ == "__main__":
    main()
