# Dependencies

## Skills (Claude Code)

| Skill | Purpose | Path |
|-------|---------|------|
| `/transcribe` | Generates SRT + readable text from audio/video | `~/.claude/skills/transcribe/` |
| `/embed-subtitles` | Burns SRT onto video with FFmpeg | `~/.claude/skills/embed-subtitles/` |

Both skills must be installed with their `node_modules` (`cd scripts && npm install`).

## System Tools

| Tool | Purpose | Install |
|------|---------|---------|
| **FFmpeg** | Video/audio processing, subtitle embedding | `brew install ffmpeg` |
| **Python 3** | RTL Unicode mark injection script | Pre-installed on macOS |
| **Node.js** | Runs transcribe + embed-subtitles scripts | `brew install node` |

## APIs (via transcribe skill)

| API | Purpose | Config |
|-----|---------|--------|
| ElevenLabs Scribe v2 | Transcription (default, best quality) | `~/.claude/skills/transcribe/scripts/.env` |
| Groq whisper-large-v3 | Transcription (`--cheap` mode) | Same `.env` |

## No Additional APIs Needed

Translation and refinement are done by Claude directly (no translation API required).
RTL fix uses Python's built-in Unicode support (no packages needed).
