#!/usr/bin/env bash
# Find the next ADR number by scanning all status directories

set -euo pipefail

# Directory containing ADRs
ADR_DIR="${1:-docs/adr}"

# Find highest ADR number across all status directories
highest=$(find "$ADR_DIR" -name "[0-9]*.md" -type f 2>/dev/null | \
    sed 's/.*\/\([0-9]*\)-.*/\1/' | \
    sort -n | \
    tail -1)

if [ -z "$highest" ]; then
    echo "001"
else
    next=$(printf "%03d" $((10#$highest + 1)))
    echo "$next"
fi
