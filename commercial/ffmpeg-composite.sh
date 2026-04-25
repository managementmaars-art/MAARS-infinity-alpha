#!/bin/bash
# Composite Higgsfield clips UNDER the chroma-keyed hyperframes base
# Pass 1: build Higgsfield layer (196s, clips at their correct times, black elsewhere)
# Pass 2: chromakey the base (magenta -> transparent) + overlay onto Higgsfield layer

set -e
cd "$(dirname "$0")"
export PATH="/c/Users/Yaleena Yara/AppData/Roaming/npm:$PATH"

BASE="renders/v3-base-chromakey.mp4"
HIGG_LAYER="renders/higg-layer.mp4"
FINAL="renders/maars-commercial-v3-FINAL.mp4"

if [ ! -f "$BASE" ]; then
  echo "ERROR: Base render missing: $BASE"; exit 1
fi

echo "=== PASS 1: Building Higgsfield layer ==="
# Each clip scaled to 1920x1080, shifted to its output time, overlaid on black canvas
ffmpeg -y -hide_banner -loglevel warning \
  -f lavfi -i color=c=black:s=1920x1080:d=196:r=30 \
  -i clips/01-jamal-pain.mp4 \
  -i clips/02-david-pain.mp4 \
  -i clips/02b-aisha-pain.mp4 \
  -i clips/03-question-hook.mp4 \
  -i clips/26-david-inbox-flood.mp4 \
  -i clips/25-jamal-first-sale.mp4 \
  -i clips/32-aisha-orders-flooding.mp4 \
  -i clips/27-david-empty-office.mp4 \
  -i clips/33-aisha-wholesale-deal.mp4 \
  -i clips/28-jamal-momentum.mp4 \
  -i clips/21-david-family-lunch.mp4 \
  -i clips/21B-aisha-sephora.mp4 \
  -i clips/22-three-lives-converge.mp4 \
  -i clips/23-logo-reveal.mp4 \
  -i clips/24-cta-button.mp4 \
  -filter_complex "\
[1:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setpts=PTS-STARTPTS+0/TB[v1]; \
[2:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setpts=PTS-STARTPTS+4/TB[v2]; \
[3:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setpts=PTS-STARTPTS+8/TB[v3]; \
[4:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setpts=PTS-STARTPTS+12/TB[v4]; \
[5:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setpts=PTS-STARTPTS+71/TB[v5]; \
[6:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setpts=PTS-STARTPTS+86/TB[v6]; \
[7:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setpts=PTS-STARTPTS+89/TB[v7]; \
[8:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setpts=PTS-STARTPTS+117/TB[v8]; \
[9:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setpts=PTS-STARTPTS+121/TB[v9]; \
[10:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setpts=PTS-STARTPTS+167/TB[v10]; \
[11:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setpts=PTS-STARTPTS+171/TB[v11]; \
[12:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setpts=PTS-STARTPTS+176/TB[v12]; \
[13:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setpts=PTS-STARTPTS+181/TB[v13]; \
[14:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setpts=PTS-STARTPTS+187/TB[v14]; \
[15:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setpts=PTS-STARTPTS+191/TB[v15]; \
[0:v][v1]overlay=enable='between(t,0,4)':eof_action=pass[x1]; \
[x1][v2]overlay=enable='between(t,4,8)':eof_action=pass[x2]; \
[x2][v3]overlay=enable='between(t,8,12)':eof_action=pass[x3]; \
[x3][v4]overlay=enable='between(t,12,17)':eof_action=pass[x4]; \
[x4][v5]overlay=enable='between(t,71,74)':eof_action=pass[x5]; \
[x5][v6]overlay=enable='between(t,86,89)':eof_action=pass[x6]; \
[x6][v7]overlay=enable='between(t,89,93)':eof_action=pass[x7]; \
[x7][v8]overlay=enable='between(t,117,121)':eof_action=pass[x8]; \
[x8][v9]overlay=enable='between(t,121,125)':eof_action=pass[x9]; \
[x9][v10]overlay=enable='between(t,167,171)':eof_action=pass[x10]; \
[x10][v11]overlay=enable='between(t,171,176)':eof_action=pass[x11]; \
[x11][v12]overlay=enable='between(t,176,181)':eof_action=pass[x12]; \
[x12][v13]overlay=enable='between(t,181,187)':eof_action=pass[x13]; \
[x13][v14]overlay=enable='between(t,187,191)':eof_action=pass[x14]; \
[x14][v15]overlay=enable='between(t,191,196)':eof_action=pass[out]" \
  -map "[out]" -t 196 -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p "$HIGG_LAYER"

echo "=== PASS 2: Chroma-key base + overlay onto Higgsfield layer ==="
ffmpeg -y -hide_banner -loglevel warning \
  -i "$HIGG_LAYER" -i "$BASE" \
  -filter_complex "[1:v]chromakey=color=0xFF00FF:similarity=0.3:blend=0.05[keyed]; [0:v][keyed]overlay[out]" \
  -map "[out]" -c:v libx264 -preset medium -crf 20 -movflags +faststart -pix_fmt yuv420p "$FINAL"

echo "=== DONE ==="
ls -lh "$FINAL"
ffprobe -v error -show_entries format=duration,size -of default=noprint_wrappers=1 "$FINAL"
