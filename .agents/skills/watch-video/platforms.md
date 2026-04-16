# Platform-Specific Notes

## Loom

**Metadata extraction (always free, no auth):**
```bash
# oembed — title, description, duration, thumbnail URL
curl -s "https://www.loom.com/v1/oembed?url=https://www.loom.com/share/VIDEO_ID"

# GraphQL — transcript URL paths
curl -s 'https://www.loom.com/graphql' \
  -H 'Content-Type: application/json' \
  --data '{
    "query": "query T($id: ID!) { fetchVideoTranscript(videoId: $id) { ... on VideoTranscriptDetails { transcript_url captions_url transcription_status } } }",
    "variables": { "videoId": "VIDEO_ID" }
  }'
```

**Transcript CDN requires CloudFront signed cookies** — the `transcript_url` paths like `mediametadata/transcription/VIDEO_ID-2.json` return 403 without auth. Cannot fetch directly without being logged in.

**Thumbnail GIF is always public:**
```
https://cdn.loom.com/sessions/thumbnails/VIDEO_ID-HASH.gif
```
Get the hash from the oembed `thumbnail_url` field.

**Loom API (paid Business/Enterprise plan only):**
```
GET https://api.loom.com/v1/recordings/{video_id}/transcription
Authorization: Bearer YOUR_LOOM_API_KEY
```
API key: Loom Workspace Settings → Integrations → Loom API → Generate API Key.
Not available on Free/Starter plans.

**yt-dlp works for Loom** — downloads HLS stream directly:
```bash
yt-dlp "https://www.loom.com/share/VIDEO_ID" -o /tmp/loom.mp4
```

---

## YouTube

**Always public metadata:**
```bash
yt-dlp --dump-json --no-download "https://www.youtube.com/watch?v=VIDEO_ID"
```

**Thumbnail (always public):**
```
https://img.youtube.com/vi/VIDEO_ID/maxresdefault.jpg
# Fallback if maxres not available:
https://img.youtube.com/vi/VIDEO_ID/hqdefault.jpg
```

**Download:**
```bash
# Audio only (faster, smaller, enough for transcription)
yt-dlp -f "bestaudio" -o /tmp/yt_audio.%(ext)s "YOUTUBE_URL"

# Full video (for visual analysis)
yt-dlp -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4" -o /tmp/yt_video.mp4 "YOUTUBE_URL"
```

**Auto-captions (free, no download):**
```bash
yt-dlp --write-auto-sub --sub-lang en --skip-download \
  --sub-format vtt -o /tmp/yt "YOUTUBE_URL"
# Creates /tmp/yt.en.vtt
```

Age-restricted or private videos will fail — no workaround without auth cookies.

---

## Gemini Video Models

Use `gemini-2.5-flash` (best balance) or `gemini-3-flash-preview` (latest):

- Accepts: MP4, MOV, AVI, MKV, GIF, JPEG, PNG, WEBP
- Max file size via inline: 20MB (use File API for larger)
- Native video understanding: sees screen content + hears audio simultaneously
- Best for: screen recordings, demos, bug reports, UI walkthroughs

**Model IDs (as of Mar 2026):**
```
gemini-2.5-flash        ← recommended default
gemini-2.5-pro          ← most capable, slower
gemini-3-flash-preview  ← latest preview
```

List available models:
```bash
curl -s "https://generativelanguage.googleapis.com/v1beta/models?key=$GOOGLE_GENERATIVE_AI_API_KEY" | \
  python3 -c "import sys,json; [print(m['name']) for m in json.load(sys.stdin)['models'] if 'generateContent' in m.get('supportedGenerationMethods',[])]"
```
