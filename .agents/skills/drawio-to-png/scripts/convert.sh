#!/bin/bash

# Draw.io to PNG Converter Script
# Converts .drawio files to high-resolution PNG images

set -e

# Configuration
SCALE=${SCALE:-2}
TRANSPARENT=${TRANSPARENT:-true}
BORDER=${BORDER:-0}
OUTPUT_DIR=${OUTPUT_DIR:-"."}

# draw.io CLI path (adjust based on OS)
if [[ "$OSTYPE" == "darwin"* ]]; then
  DRAWIO_CLI="/Applications/draw.io.app/Contents/MacOS/draw.io"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
  DRAWIO_CLI="/opt/drawio/drawio"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
  DRAWIO_CLI="C:/Program Files/draw.io/draw.io.exe"
else
  DRAWIO_CLI="drawio"
fi

# Check if draw.io CLI is available
if ! command -v "$DRAWIO_CLI" &> /dev/null && [ ! -f "$DRAWIO_CLI" ]; then
  echo "Error: draw.io CLI not found at $DRAWIO_CLI"
  echo "Please install draw.io desktop from: https://github.com/jgraph/drawio-desktop/releases"
  exit 1
fi

# Function to convert single file
convert_file() {
  local input="$1"
  local output="$2"
  local page="${3:-}"
  
  echo "Converting: $input -> $output"
  
  local cmd=("$DRAWIO_CLI" -x -f png -s "$SCALE" -o "$output")
  
  if [ "$TRANSPARENT" = "true" ]; then
    cmd+=(--transparent)
  fi
  
  if [ "$BORDER" -gt 0 ]; then
    cmd+=(--border "$BORDER")
  fi
  
  if [ -n "$page" ]; then
    cmd+=(-p "$page")
  fi
  
  cmd+=("$input")
  
  "${cmd[@]}"
  
  if [ -f "$output" ]; then
    echo "✓ Successfully created: $output"
    return 0
  else
    echo "✗ Failed to create: $output"
    return 1
  fi
}

# Function to get output path
get_output_path() {
  local input="$1"
  local page="$2"
  
  local basename=$(basename "$input")
  local filename="${basename%.*}"
  
  if [ -n "$page" ]; then
    echo "$OUTPUT_DIR/${filename}-page-${page}.png"
  else
    echo "$OUTPUT_DIR/${filename}.png"
  fi
}

# Main conversion logic
main() {
  if [ $# -eq 0 ]; then
    echo "Usage: $0 <input.drawio> [output.png] [page]"
    echo ""
    echo "Options (via environment variables):"
    echo "  SCALE=<number>        Scale factor (default: 2)"
    echo "  TRANSPARENT=<bool>    Transparent background (default: true)"
    echo "  BORDER=<pixels>       Border size (default: 0)"
    echo "  OUTPUT_DIR=<path>     Output directory (default: current)"
    echo ""
    echo "Examples:"
    echo "  $0 diagram.drawio"
    echo "  $0 diagram.drawio output.png"
    echo "  SCALE=3 $0 diagram.drawio"
    echo "  $0 multi-page.drawio output.png 0"
    exit 1
  fi
  
  local input="$1"
  local output="${2:-}"
  local page="${3:-}"
  
  # Check if input file exists
  if [ ! -f "$input" ]; then
    echo "Error: Input file not found: $input"
    exit 1
  fi
  
  # Determine output path
  if [ -z "$output" ]; then
    output=$(get_output_path "$input" "$page")
  fi
  
  # Create output directory if needed
  mkdir -p "$(dirname "$output")"
  
  # Convert
  convert_file "$input" "$output" "$page"
}

main "$@"
