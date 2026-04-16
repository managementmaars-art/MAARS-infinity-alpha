#!/usr/bin/env bash
# write-spec-status.sh — Compute hash and write spec-status.json atomically
# Usage: bash write-spec-status.sh <spec-dir> [valid]
#   spec-dir: path to the rootspec directory
#   valid: "true" or "false" (default: true)
# Output: writes spec-status.json to spec-dir, prints the path

set -euo pipefail

SPEC_DIR="${1:-.}"
VALID="${2:-true}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Compute hash
HASH=$("$SCRIPT_DIR/compute-spec-hash.sh" "$SPEC_DIR")

if [[ "$HASH" == "none" ]]; then
  echo "ERROR: No spec files found in $SPEC_DIR" >&2
  exit 1
fi

# Detect version from framework file
VERSION="unknown"
FRAMEWORK_FILE="$SPEC_DIR/00.FRAMEWORK.md"
if [[ -f "$FRAMEWORK_FILE" ]]; then
  VERSION=$(grep -oE 'v[0-9]+\.[0-9]+(\.[0-9]+)?' "$FRAMEWORK_FILE" | head -1 || echo "unknown")
fi

# ISO timestamp
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Write spec-status.json
OUTPUT="$SPEC_DIR/spec-status.json"
cat > "$OUTPUT" <<EOF
{
  "hash": "$HASH",
  "validatedAt": "$TIMESTAMP",
  "valid": $VALID,
  "version": "$VERSION"
}
EOF

echo "$OUTPUT"
