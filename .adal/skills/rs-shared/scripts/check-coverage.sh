#!/usr/bin/env bash
# check-coverage.sh — Find L4 systems with no L5 user stories
# Usage: bash check-coverage.sh <spec-dir>
# Output: uncovered items or "OK"

set -euo pipefail

SPEC_DIR="${1:-.}"
SYSTEMS_DIR="$SPEC_DIR/04.SYSTEMS"
STORIES_DIR="$SPEC_DIR/05.IMPLEMENTATION/USER_STORIES"

# Extract L4 system names (filenames minus .md, excluding SYSTEMS_OVERVIEW)
SYSTEMS=()
if [[ -d "$SYSTEMS_DIR" ]]; then
  while IFS= read -r f; do
    name=$(basename "$f" .md)
    SYSTEMS+=("$name")
  done < <(find "$SYSTEMS_DIR" -maxdepth 1 -name "*.md" ! -name "SYSTEMS_OVERVIEW.md" 2>/dev/null | sort)
fi

if [[ ${#SYSTEMS[@]} -eq 0 ]]; then
  echo "UNCOVERED_SYSTEMS=none"
  echo "OK: No L4 systems to check"
  exit 0
fi

# Extract all @systems annotations from L5 YAML story files
REFERENCED=""
if [[ -d "$STORIES_DIR" ]]; then
  REFERENCED=$(grep -rh '@systems' "$STORIES_DIR" 2>/dev/null || true)
fi

# Check each system for coverage
UNCOVERED=()
for sys in "${SYSTEMS[@]}"; do
  if ! echo "$REFERENCED" | grep -qi "$sys"; then
    UNCOVERED+=("$sys")
  fi
done

if [[ ${#UNCOVERED[@]} -eq 0 ]]; then
  echo "UNCOVERED_SYSTEMS=none"
  echo "OK: All L4 systems have user stories"
else
  # Join with commas
  UNCOVERED_LIST=$(printf '%s,' "${UNCOVERED[@]}")
  UNCOVERED_LIST="${UNCOVERED_LIST%,}"
  echo "UNCOVERED_SYSTEMS=$UNCOVERED_LIST"
  for sys in "${UNCOVERED[@]}"; do
    echo "WARNING: System '$sys' has no user stories"
  done
fi
