# Gemini API — Video Analysis

## Analyze with thumbnail (no download needed)

```python
import base64, json, urllib.request

API_KEY = "YOUR_GOOGLE_GENERATIVE_AI_API_KEY"  # from .env.local: GOOGLE_GENERATIVE_AI_API_KEY

with open("/tmp/video_thumb.gif", "rb") as f:
    thumb_b64 = base64.b64encode(f.read()).decode()

payload = {
    "contents": [{
        "parts": [
            {"inline_data": {"mime_type": "image/gif", "data": thumb_b64}},
            {"text": YOUR_PROMPT}
        ]
    }],
    "generationConfig": {"temperature": 0.1, "maxOutputTokens": 4096}
}

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"
req = urllib.request.Request(url,
    data=json.dumps(payload).encode(),
    headers={"Content-Type": "application/json"},
    method="POST")

with urllib.request.urlopen(req, timeout=60) as resp:
    result = json.load(resp)
    print(result["candidates"][0]["content"]["parts"][0]["text"])
```

Supported mime types for inline: `image/gif`, `image/jpeg`, `image/png`, `image/webp`

---

## Analyze a full video file (MP4)

For files < 20MB, use inline. For larger files, use the File API.

### Inline (< 20MB):
```python
with open("/tmp/video.mp4", "rb") as f:
    video_b64 = base64.b64encode(f.read()).decode()

payload = {
    "contents": [{
        "parts": [
            {"inline_data": {"mime_type": "video/mp4", "data": video_b64}},
            {"text": YOUR_PROMPT}
        ]
    }]
}
```

### File API (any size):
```python
import urllib.request, json, os

API_KEY = "YOUR_KEY"
video_path = "/tmp/video.mp4"
file_size = os.path.getsize(video_path)

# 1. Upload
with open(video_path, "rb") as f:
    upload_req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/upload/v1beta/files?key={API_KEY}",
        data=f.read(),
        headers={
            "Content-Type": "video/mp4",
            "X-Goog-Upload-Command": "start, upload, finalize",
            "X-Goog-Upload-Header-Content-Length": str(file_size),
            "X-Goog-Upload-Header-Content-Type": "video/mp4",
        },
        method="POST"
    )
    with urllib.request.urlopen(upload_req) as r:
        file_info = json.load(r)
        file_uri = file_info["file"]["uri"]

# 2. Analyze
payload = {
    "contents": [{
        "parts": [
            {"file_data": {"mime_type": "video/mp4", "file_uri": file_uri}},
            {"text": YOUR_PROMPT}
        ]
    }]
}
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"
req = urllib.request.Request(url, data=json.dumps(payload).encode(),
    headers={"Content-Type": "application/json"}, method="POST")
with urllib.request.urlopen(req, timeout=120) as resp:
    result = json.load(resp)
    print(result["candidates"][0]["content"]["parts"][0]["text"])
```

---

## Recommended Prompt Template

```python
PROMPT = """You are analyzing a screen recording video.

Describe what you see AND hear in vivid detail:

1. **What's on screen** — every visible UI element, text, number, error message, panel name, data value. Be exhaustive.
2. **What was said** — transcript or close paraphrase of narration
3. **Summary** — 1-2 sentences on what this video demonstrates or reports
4. **Key data points** — exact numbers, names, states in a table
5. **Action items** — what an engineer/PM should do based on this

Context: {CONTEXT}

Be precise. Quote exact values. This is for someone who cannot watch the video."""
```
