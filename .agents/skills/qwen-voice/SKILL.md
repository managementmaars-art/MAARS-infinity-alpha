---
name: qwen-voice
description: Use when cloud Qwen speech features are needed through DashScope, especially for ASR transcription of user audio, Telegram voice-note TTS, or reusable clone-voice workflows that local-only TTS does not cover.
---

# qwen-voice

Use DashScope-backed Qwen speech scripts for cloud ASR, cloud TTS, and optional voice cloning.

## Use this skill for the right cases

- Prefer this skill when local-whisper or local-qwen-tts is not the right fit.
- Use it for cloud ASR on audio files.
- Use it for cloud TTS voices or clone profiles.
- Expect network/API dependency and possible cost.

## Config

Expect `DASHSCOPE_API_KEY` in one of:

- `~/.config/qwen-voice/.env`
- `<repo>/.qwen-voice/.env`

If missing, stop and report missing auth instead of guessing.

## Scripts

```bash
# ASR
python3 "$SKILL_DIR/scripts/qwen_asr.py" --in /path/to/audio.ogg
python3 "$SKILL_DIR/scripts/qwen_asr.py" --in /path/to/audio.ogg --timestamps --chunk-sec 3

# preset voice TTS
python3 "$SKILL_DIR/scripts/qwen_tts.py" --text '你好，我是 Pi。' --voice Cherry --out /tmp/out.ogg

# create clone profile
python3 "$SKILL_DIR/scripts/qwen_voice_clone.py" --in ./voice_sample.ogg --name george --out "$SKILL_DIR/work/qwen-voice/george.voice.json"

# synthesize with clone profile
python3 "$SKILL_DIR/scripts/qwen_tts.py" --text '你好，我是 George。' --voice-profile "$SKILL_DIR/work/qwen-voice/george.voice.json" --out /tmp/out.ogg
```

## Operational notes

- Output `.ogg` is suitable for Telegram voice notes.
- Timestamp mode is chunk-based, not true word alignment.
- Scripts create work files and venv inside `$SKILL_DIR/work/` (not the project's cwd).
- Prefer sending larger batched requests over many tiny API calls when possible.

## Failure rules

- If API key is missing: report auth missing.
- If audio conversion fails: check ffmpeg/input format first.
- If clone creation fails: separate clone-profile failure from normal preset-voice TTS.
- If ASR works but timestamps are messy: report they are coarse chunk timestamps, not exact word timings.
