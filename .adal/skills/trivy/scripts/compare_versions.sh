#!/usr/bin/env bash
# Compare vulnerabilities across multiple image versions
# Usage: compare_versions.sh <base-image> <version1> [version2] [version3] ...

set -euo pipefail

if [ $# -lt 2 ]; then
    echo "Usage: $0 <base-image> <version1> [version2] [version3] ..."
    echo "Example: $0 public.ecr.aws/org/image 18.3.2 18.4.0 18.5.0"
    exit 1
fi

BASE_IMAGE="$1"
shift
VERSIONS=("$@")

SEVERITY="${TRIVY_SEVERITY:-HIGH,CRITICAL}"
OUTPUT_DIR="${TRIVY_OUTPUT_DIR:-./trivy-scans}"

mkdir -p "$OUTPUT_DIR"

echo "Scanning ${#VERSIONS[@]} versions with severity filter: $SEVERITY"
echo "Output directory: $OUTPUT_DIR"
echo ""

# Scan each version
for version in "${VERSIONS[@]}"; do
    image="${BASE_IMAGE}:${version}"
    output_file="${OUTPUT_DIR}/scan-${version//[:\/]/-}.txt"

    echo "Scanning $image..."
    trivy image --severity "$SEVERITY" "$image" > "$output_file" 2>&1
    echo "  → Saved to $output_file"
done

echo ""
echo "✓ All scans complete. Results in $OUTPUT_DIR/"
echo ""
echo "Compare results with:"
echo "  diff $OUTPUT_DIR/scan-${VERSIONS[0]//[:\/]/-}.txt $OUTPUT_DIR/scan-${VERSIONS[1]//[:\/]/-}.txt"
