#!/usr/bin/env bash
# compare-test-runs.sh — Compare two tests-status.json files for regressions/fixes
# Usage: bash compare-test-runs.sh <old-tests-status.json> <new-tests-status.json>
# Output: one line per story: REGRESSION|FIXED|UNCHANGED|NEW|REMOVED <story-id>

set -euo pipefail

OLD_FILE="${1:-}"
NEW_FILE="${2:-}"

if [[ -z "$OLD_FILE" || -z "$NEW_FILE" ]]; then
  echo "ERROR: usage: compare-test-runs.sh <old-json> <new-json>" >&2
  exit 1
fi

if [[ ! -f "$OLD_FILE" ]]; then
  echo "ERROR: old file not found: $OLD_FILE" >&2
  exit 1
fi

if [[ ! -f "$NEW_FILE" ]]; then
  echo "ERROR: new file not found: $NEW_FILE" >&2
  exit 1
fi

TMPDIR_WORK=$(mktemp -d)
trap 'rm -rf "$TMPDIR_WORK"' EXIT

# Extract story ID → status mappings from a tests-status.json
# Pattern: "US-nnn": {..., "status": "pass|fail", ...}
extract_statuses() {
  local file="$1"
  local outfile="$2"
  grep -oE '"(US-[0-9]+)"[^}]*"status"[[:space:]]*:[[:space:]]*"(pass|fail)"' "$file" 2>/dev/null | \
    sed -E 's/"(US-[0-9]+)".*"status"[[:space:]]*:[[:space:]]*"(pass|fail)"/\1 \2/' | \
    sort > "$outfile" || true
}

extract_statuses "$OLD_FILE" "$TMPDIR_WORK/old"
extract_statuses "$NEW_FILE" "$TMPDIR_WORK/new"

# Build lookup: old statuses
declare -A OLD_STATUS
while IFS=' ' read -r sid status; do
  [[ -z "$sid" ]] && continue
  OLD_STATUS["$sid"]="$status"
done < "$TMPDIR_WORK/old"

# Build lookup: new statuses
declare -A NEW_STATUS
while IFS=' ' read -r sid status; do
  [[ -z "$sid" ]] && continue
  NEW_STATUS["$sid"]="$status"
done < "$TMPDIR_WORK/new"

# Collect all story IDs
{
  awk '{print $1}' "$TMPDIR_WORK/old"
  awk '{print $1}' "$TMPDIR_WORK/new"
} | sort -u > "$TMPDIR_WORK/all_ids"

# Compare
while IFS= read -r sid; do
  [[ -z "$sid" ]] && continue
  old="${OLD_STATUS[$sid]:-}"
  new="${NEW_STATUS[$sid]:-}"

  if [[ -z "$old" && -n "$new" ]]; then
    echo "NEW $sid"
  elif [[ -n "$old" && -z "$new" ]]; then
    echo "REMOVED $sid"
  elif [[ "$old" == "pass" && "$new" == "fail" ]]; then
    echo "REGRESSION $sid"
  elif [[ "$old" == "fail" && "$new" == "pass" ]]; then
    echo "FIXED $sid"
  else
    echo "UNCHANGED $sid"
  fi
done < "$TMPDIR_WORK/all_ids"
