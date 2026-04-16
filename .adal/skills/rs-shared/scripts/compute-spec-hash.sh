#!/usr/bin/env bash
# compute-spec-hash.sh — Compute a deterministic sha256 hash of all spec files
# Usage: bash compute-spec-hash.sh <spec-dir>
# Output: single line — the sha256 hash (or "none" if no spec files exist)

set -euo pipefail

SPEC_DIR="${1:-.}"

# Collect all spec files in deterministic (sorted) order
FILES=()

for f in \
  "$SPEC_DIR/01.PHILOSOPHY.md" \
  "$SPEC_DIR/02.TRUTHS.md" \
  "$SPEC_DIR/03.INTERACTIONS.md"; do
  [[ -f "$f" ]] && FILES+=("$f")
done

if [[ -d "$SPEC_DIR/04.SYSTEMS" ]]; then
  while IFS= read -r f; do
    FILES+=("$f")
  done < <(find "$SPEC_DIR/04.SYSTEMS" -maxdepth 1 -name "*.md" 2>/dev/null | sort)
fi

if [[ -d "$SPEC_DIR/05.IMPLEMENTATION/USER_STORIES" ]]; then
  while IFS= read -r f; do
    FILES+=("$f")
  done < <(find "$SPEC_DIR/05.IMPLEMENTATION/USER_STORIES" -name "*.yaml" -o -name "*.yml" 2>/dev/null | sort)
fi

if [[ -d "$SPEC_DIR/05.IMPLEMENTATION/FINE_TUNING" ]]; then
  while IFS= read -r f; do
    FILES+=("$f")
  done < <(find "$SPEC_DIR/05.IMPLEMENTATION/FINE_TUNING" -name "*.yaml" -o -name "*.yml" 2>/dev/null | sort)
fi

if [[ ${#FILES[@]} -eq 0 ]]; then
  echo "none"
  exit 0
fi

cat "${FILES[@]}" | shasum -a 256 | awk '{print $1}'
