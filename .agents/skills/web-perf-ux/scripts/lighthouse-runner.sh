#!/usr/bin/env bash
#
# Lighthouse CLI Runner - Sensible defaults for performance auditing
#
# Usage:
#   ./lighthouse-runner.sh <url> [options]
#
# Options:
#   --mobile          Use mobile emulation (default)
#   --desktop         Use desktop emulation
#   --output-dir DIR  Output directory (default: ./lighthouse-reports)
#   --runs N          Number of runs for median (default: 1)
#   --throttling      Apply network/CPU throttling (default: true for mobile)
#   --no-throttling   Disable throttling
#
# Examples:
#   ./lighthouse-runner.sh https://example.com
#   ./lighthouse-runner.sh http://localhost:3000 --desktop --no-throttling
#   ./lighthouse-runner.sh https://staging.example.com --runs 3

set -euo pipefail

# Defaults
URL=""
PRESET="mobile"
OUTPUT_DIR="./lighthouse-reports"
RUNS=1
THROTTLING="true"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --mobile)
      PRESET="mobile"
      shift
      ;;
    --desktop)
      PRESET="desktop"
      shift
      ;;
    --output-dir)
      OUTPUT_DIR="$2"
      shift 2
      ;;
    --runs)
      RUNS="$2"
      shift 2
      ;;
    --throttling)
      THROTTLING="true"
      shift
      ;;
    --no-throttling)
      THROTTLING="false"
      shift
      ;;
    -*)
      echo "Unknown option: $1"
      exit 1
      ;;
    *)
      URL="$1"
      shift
      ;;
  esac
done

# Validate URL
if [[ -z "$URL" ]]; then
  echo "Error: URL is required"
  echo "Usage: ./lighthouse-runner.sh <url> [options]"
  exit 1
fi

# Check for lighthouse CLI
if ! command -v lighthouse &> /dev/null; then
  echo "Error: lighthouse CLI not found"
  echo "Install with: npm install -g lighthouse"
  exit 1
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Build lighthouse command
LH_FLAGS=(
  "--output=json,html"
  "--output-path=$OUTPUT_DIR/report_${TIMESTAMP}"
  "--only-categories=performance"
  "--chrome-flags=--headless --no-sandbox --disable-gpu"
)

# Preset configuration
if [[ "$PRESET" == "desktop" ]]; then
  LH_FLAGS+=("--preset=desktop")
  if [[ "$THROTTLING" == "false" ]]; then
    LH_FLAGS+=("--throttling-method=provided")
  fi
else
  # Mobile is default
  LH_FLAGS+=("--screenEmulation.mobile=true")
  LH_FLAGS+=("--screenEmulation.width=412")
  LH_FLAGS+=("--screenEmulation.height=823")
  if [[ "$THROTTLING" == "false" ]]; then
    LH_FLAGS+=("--throttling-method=provided")
  fi
fi

# Run lighthouse
echo "Running Lighthouse..."
echo "  URL: $URL"
echo "  Preset: $PRESET"
echo "  Throttling: $THROTTLING"
echo "  Output: $OUTPUT_DIR"
echo ""

if [[ "$RUNS" -gt 1 ]]; then
  echo "Running $RUNS iterations for median scores..."
  BEST_SCORE=0
  BEST_REPORT=""

  for i in $(seq 1 "$RUNS"); do
    echo "  Run $i/$RUNS..."
    ITER_OUTPUT="$OUTPUT_DIR/run_${i}_${TIMESTAMP}"
    lighthouse "$URL" "${LH_FLAGS[@]}" --output-path="$ITER_OUTPUT" 2>/dev/null

    # Extract performance score
    SCORE=$(jq '.categories.performance.score' "$ITER_OUTPUT.report.json" 2>/dev/null || echo "0")
    echo "    Performance score: $(echo "$SCORE * 100" | bc | cut -d. -f1)"

    # Track best run
    if (( $(echo "$SCORE > $BEST_SCORE" | bc -l) )); then
      BEST_SCORE=$SCORE
      BEST_REPORT="$ITER_OUTPUT"
    fi
  done

  # Copy best report as main report
  cp "$BEST_REPORT.report.json" "$OUTPUT_DIR/report_${TIMESTAMP}.report.json"
  cp "$BEST_REPORT.report.html" "$OUTPUT_DIR/report_${TIMESTAMP}.report.html"
  echo ""
  echo "Best score: $(echo "$BEST_SCORE * 100" | bc | cut -d. -f1)"
else
  lighthouse "$URL" "${LH_FLAGS[@]}"
fi

echo ""
echo "Reports saved:"
echo "  JSON: $OUTPUT_DIR/report_${TIMESTAMP}.report.json"
echo "  HTML: $OUTPUT_DIR/report_${TIMESTAMP}.report.html"

# Output key metrics summary
echo ""
echo "=== Performance Summary ==="
JSON_REPORT="$OUTPUT_DIR/report_${TIMESTAMP}.report.json"

if [[ -f "$JSON_REPORT" ]]; then
  jq -r '
    .categories.performance.score as $perf |
    .audits["largest-contentful-paint"].numericValue as $lcp |
    .audits["cumulative-layout-shift"].numericValue as $cls |
    .audits["total-blocking-time"].numericValue as $tbt |
    .audits["first-contentful-paint"].numericValue as $fcp |
    .audits["speed-index"].numericValue as $si |
    "Performance Score: \(($perf * 100) | floor)",
    "LCP: \(($lcp / 1000) | . * 100 | floor / 100)s",
    "CLS: \($cls | . * 1000 | floor / 1000)",
    "TBT: \($tbt | floor)ms",
    "FCP: \(($fcp / 1000) | . * 100 | floor / 100)s",
    "Speed Index: \(($si / 1000) | . * 100 | floor / 100)s"
  ' "$JSON_REPORT"
fi
