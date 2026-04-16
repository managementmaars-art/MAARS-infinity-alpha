#!/bin/bash
# Extract audio from a Douyin video URL using curl with Referer header
# Usage: download_audio.sh <audio_direct_url> <output_file>
# Note: The audio URL must be obtained via browser interception (see SKILL.md Step 2)

set -euo pipefail

AUDIO_URL="${1:?Usage: download_audio.sh <audio_url> <output_file>}"
OUTPUT="${2:?Usage: download_audio.sh <audio_url> <output_file>}"

echo "Downloading audio..."
curl -sS -H "Referer: https://www.douyin.com/" -o "$OUTPUT" "$AUDIO_URL"

SIZE=$(stat -f%z "$OUTPUT" 2>/dev/null || stat -c%s "$OUTPUT" 2>/dev/null)
echo "Done: $OUTPUT ($(echo "scale=1; $SIZE/1024/1024" | bc)MB)"
