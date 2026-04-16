---
name: watch-video
description: Analyze any public video URL (Loom, YouTube, etc.) and produce a vivid, engineer-grade report of what was shown and said. Use when a user shares a Loom, YouTube, or other video URL and wants it analyzed, summarized, transcribed, or understood by an AI — without needing to watch it themselves.
---

# Watch Video

Analyze a public video URL and produce a vivid, detailed report of what was **seen on screen** AND **said aloud** — precise enough for an engineer, PM, or designer to act on without watching it.

## Workflow

### Step 1: Determine video platform

| Platform | Strategy |
|----------|----------|
| **Loom** | Extract metadata + thumbnail from page; use Gemini on thumbnail + description |
| **YouTube** | Use `yt-dlp` to download audio → Whisper transcription; or Gemini with thumbnail |
| **Other** | Try `yt-dlp` first; fall back to page scrape + thumbnail |

### Step 2: Extract what you can without downloading

Always try to get free data first (no disk needed):

```bash
# Get Loom metadata (title, description, duration, transcript status)
python3 scripts/loom_meta.py "https://www.loom.com/share/VIDEO_ID"

# Get YouTube metadata
yt-dlp --dump-json --no-download "YOUTUBE_URL" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print('Title:', d['title'])
print('Description:', d['description'][:500])
print('Duration:', d['duration'])
"
```

### Step 3: Get the thumbnail

Thumbnails are always public and reveal UI state, screen content, numbers.

```bash
# Loom: thumbnail URL is in oembed response
curl -s "https://www.loom.com/v1/oembed?url=LOOM_URL" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(d['thumbnail_url'])  # animated GIF — download this
"

# YouTube: predictable URL
# https://img.youtube.com/vi/VIDEO_ID/maxresdefault.jpg
```

Download the thumbnail:
```bash
curl -s "THUMBNAIL_URL" -o /tmp/video_thumb.gif  # or .jpg
```

### Step 4: Analyze with Gemini

Use `scripts/analyze_video.py` — pass the thumbnail + all metadata.

```bash
python3 scripts/analyze_video.py \
  --thumb /tmp/video_thumb.gif \
  --title "Video title" \
  --description "Auto-generated description text" \
  --duration 143
```

Or call the Gemini API directly (see [gemini-api.md](gemini-api.md)).

### Step 5: If disk space allows — download + full analysis

```bash
# Check disk first
df -h ~ | awk 'NR==2 {print $4}'

# Download with yt-dlp (works for Loom + YouTube + 1000+ sites)
yt-dlp "VIDEO_URL" -o /tmp/video.mp4

# Option A: Gemini video analysis (best for screen recordings)
python3 scripts/analyze_video.py --video /tmp/video.mp4

# Option B: Whisper transcription only (fast, audio-only)
curl -X POST https://api.openai.com/v1/audio/transcriptions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -F "file=@/tmp/video.mp4" \
  -F "model=whisper-1"
```

## Output Format

Produce this structure every time:

```markdown
## Video Analysis: [Title]

**URL:** [link] | **Duration:** [X:XX]

### What's on screen
[Vivid description of every visible UI element, number, text, state shown in the video/thumbnail. Be exhaustive — mention exact values, UI panel names, error messages, data shown.]

### What was said
[Transcript or paraphrase of the narration, with key quotes verbatim]

### Problem / Topic Summary
[1-2 sentences: what this video is about or demonstrating]

### Key Data Points
| Item | Value |
|------|-------|
| [exact numbers, names, states observed] | [value] |

### Action Items / Root Cause (if bug report)
[Specific things to investigate or do, based on the video content]
```

## Platform Notes

See [platforms.md](platforms.md) for platform-specific quirks (Loom CDN auth, YouTube age-gate, etc.)

## Disk Full Fallback

If disk is full (`df -h` shows < 500MB free):
1. Use thumbnail + metadata only (Steps 1–4 above)
2. Loom auto-descriptions are highly detailed — combine with thumbnail for good coverage
3. Never fail silently — always produce a report from whatever data is available
