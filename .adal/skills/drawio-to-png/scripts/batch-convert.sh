#!/bin/bash

# Batch convert all draw.io files in a directory to PNG

set -e

# Configuration
SCALE=${SCALE:-2}
TRANSPARENT=${TRANSPARENT:-true}
BORDER=${BORDER:-0}
INPUT_DIR=${INPUT_DIR:-"."}
OUTPUT_DIR=${OUTPUT_DIR:-"./output"}

# draw.io CLI path
if [[ "$OSTYPE" == "darwin"* ]]; then
  DRAWIO_CLI="/Applications/draw.io.app/Contents/MacOS/draw.io"
else
  DRAWIO_CLI="drawio"
fi

# Check if draw.io CLI is available
if ! command -v "$DRAWIO_CLI" &> /dev/null && [ ! -f "$DRAWIO_CLI" ]; then
  echo "Error: draw.io CLI not found"
  echo "Please install draw.io desktop from: https://github.com/jgraph/drawio-desktop/releases"
  exit 1
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Counters
total=0
success=0
failed=0

echo "Scanning for draw.io files in: $INPUT_DIR"
echo "Output directory: $OUTPUT_DIR"
echo "Scale: ${SCALE}x, Transparent: $TRANSPARENT, Border: ${BORDER}px"
echo ""

# Find and convert all draw.io files
while IFS= read -r -d '' file; do
  total=$((total + 1))
  
  basename=$(basename "$file")
  filename="${basename%.*}"
  output="$OUTPUT_DIR/${filename}.png"
  
  echo "[$total] Converting: $file"
  
  cmd=("$DRAWIO_CLI" -x -f png -s "$SCALE" -o "$output")
  
  if [ "$TRANSPARENT" = "true" ]; then
    cmd+=(--transparent)
  fi
  
  if [ "$BORDER" -gt 0 ]; then
    cmd+=(--border "$BORDER")
  fi
  
  cmd+=("$file")
  
  if "${cmd[@]}" 2>/dev/null; then
    echo "  ✓ Success: $output"
    success=$((success + 1))
  else
    echo "  ✗ Failed: $file"
    failed=$((failed + 1))
  fi
  
  echo ""
done < <(find "$INPUT_DIR" -type f \( -name "*.drawio" -o -name "*.dio" \) -print0)

# Summary
echo "================================"
echo "Conversion Summary"
echo "================================"
echo "Total files: $total"
echo "Successful: $success"
echo "Failed: $failed"
echo "Output directory: $OUTPUT_DIR"

if [ $failed -gt 0 ]; then
  exit 1
fi
