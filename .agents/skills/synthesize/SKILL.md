---
name: synthesize
description: "Synthesize text to speech with Kokoro TTS. TRIGGERS - speak this, kokoro tts, text to speech, synthesize voice, say this."
allowed-tools: Read, Bash, Glob, AskUserQuestion
argument-hint: "[text to speak]"
---

# Synthesize Speech

Generate speech from text using the Kokoro TTS CLI tool. Supports single WAV output or chunked streaming for long text.

> **Self-Evolving Skill**: This skill improves through use. If instructions are wrong, parameters drifted, or a workaround was needed — fix this file immediately, don't defer. Only update for real, reproducible issues.

## Quick Usage

```bash
# Single WAV
~/.local/share/kokoro/.venv/bin/python ~/.local/share/kokoro/tts_generate.py \
  --text "Hello from Kokoro TTS" --voice af_heart --lang en-us --speed 1.0 \
  --output /tmp/kokoro-tts-$$.wav

# Play it
afplay /tmp/kokoro-tts-$$.wav
```

## Parameters

| Parameter  | Default    | Description                          |
| ---------- | ---------- | ------------------------------------ |
| `--text`   | (required) | Text to synthesize                   |
| `--voice`  | `af_heart` | Voice name (see voice catalog)       |
| `--lang`   | `en-us`    | Language code (en-us, zh, ja, etc.)  |
| `--speed`  | `1.0`      | Speech speed multiplier              |
| `--output` | (required) | Output WAV path                      |
| `--chunk`  | off        | Chunked streaming mode for long text |

## Voice Catalog

See [Voice Catalog](./references/voice-catalog.md) for all available voices with quality grades.

**Top voices**:

| Voice ID  | Name   | Grade | Gender |
| --------- | ------ | ----- | ------ |
| af_heart  | Heart  | A     | Female |
| af_bella  | Bella  | A-    | Female |
| af_nicole | Nicole | B-    | Female |

## Chunked Streaming

For long text, use `--chunk` to get progressive playback:

```bash
~/.local/share/kokoro/.venv/bin/python ~/.local/share/kokoro/tts_generate.py \
  --text "Long text here..." --voice af_heart --lang en-us --speed 1.0 \
  --output /tmp/kokoro-tts-$$.wav --chunk
```

Each chunk WAV path is printed to stdout as it becomes ready. The final line is `DONE <ms>`.

## Troubleshooting

| Issue            | Cause            | Solution                        |
| ---------------- | ---------------- | ------------------------------- |
| No audio output  | Model not loaded | Run `/kokoro-tts:install` first |
| Empty text error | Input was blank  | Provide non-empty `--text`      |
| Slow generation  | First-run warmup | Normal — subsequent runs faster |


## Post-Execution Reflection

After this skill completes, check before closing:

1. **Did the command succeed?** — If not, fix the instruction or error table that caused the failure.
2. **Did parameters or output change?** — If the underlying tool's interface drifted, update Usage examples and Parameters table to match.
3. **Was a workaround needed?** — If you had to improvise (different flags, extra steps), update this SKILL.md so the next invocation doesn't need the same workaround.

Only update if the issue is real and reproducible — not speculative.
