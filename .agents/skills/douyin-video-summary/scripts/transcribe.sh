#!/bin/bash
# Transcribe audio using whisper.cpp
# Usage: transcribe.sh <input_audio> <output_prefix> [model_path] [language]
# Converts to WAV if needed, then runs whisper-cli

set -euo pipefail

INPUT="${1:?Usage: transcribe.sh <input_audio> <output_prefix> [model_path] [language]}"
OUTPUT_PREFIX="${2:?Usage: transcribe.sh <input_audio> <output_prefix> [model_path] [language]}"
MODEL="${3:-models/ggml-small.bin}"
LANG="${4:-zh}"

WAV_FILE="${OUTPUT_PREFIX}.wav"

# Convert to 16kHz mono WAV
echo "Converting to WAV..."
ffmpeg -y -i "$INPUT" -ar 16000 -ac 1 -c:a pcm_s16le "$WAV_FILE" 2>/dev/null

DURATION=$(ffprobe -i "$WAV_FILE" -show_entries format=duration -v quiet -of csv="p=0" | cut -d. -f1)
echo "Audio duration: ${DURATION}s"

# Transcribe
echo "Transcribing with whisper.cpp (model: $(basename $MODEL), lang: $LANG)..."
time whisper-cli -m "$MODEL" -l "$LANG" -f "$WAV_FILE" -otxt -of "$OUTPUT_PREFIX" 2>&1 | tail -5

echo "Output: ${OUTPUT_PREFIX}.txt"
