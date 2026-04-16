#!/usr/bin/env bash
# Batch scan multiple images in parallel
# Usage: batch_scan.sh <image1> <image2> [image3] ...

set -euo pipefail

if [ $# -lt 1 ]; then
    echo "Usage: $0 <image1> <image2> [image3] ..."
    echo "Example: $0 alpine:latest nginx:latest postgres:16"
    exit 1
fi

IMAGES=("$@")
SEVERITY="${TRIVY_SEVERITY:-HIGH,CRITICAL}"
OUTPUT_DIR="${TRIVY_OUTPUT_DIR:-./trivy-scans}"
MAX_PARALLEL="${TRIVY_MAX_PARALLEL:-5}"

mkdir -p "$OUTPUT_DIR"

echo "Scanning ${#IMAGES[@]} images with severity filter: $SEVERITY"
echo "Max parallel scans: $MAX_PARALLEL"
echo "Output directory: $OUTPUT_DIR"
echo ""

# Function to scan a single image
scan_image() {
    local image="$1"
    local output_file="${OUTPUT_DIR}/scan-${image//[:\/]/-}.txt"

    echo "Scanning $image..."
    if trivy image --severity "$SEVERITY" "$image" > "$output_file" 2>&1; then
        echo "  ✓ $image complete"
    else
        echo "  ✗ $image failed"
    fi
}

export -f scan_image
export SEVERITY OUTPUT_DIR

# Run scans in parallel
printf '%s\n' "${IMAGES[@]}" | xargs -n 1 -P "$MAX_PARALLEL" -I {} bash -c 'scan_image "$@"' _ {}

echo ""
echo "✓ All scans complete. Results in $OUTPUT_DIR/"
