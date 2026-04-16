#!/usr/bin/env bash
# check-numerics.sh — Find hardcoded numeric values in L1-L4
# Usage: bash check-numerics.sh <spec-dir>
# Output: violations with file:line format

set -euo pipefail

SPEC_DIR="${1:-.}"
VIOLATIONS=0

check_file() {
  local file="$1"
  local label="$2"
  local lineno=0

  while IFS= read -r line; do
    lineno=$((lineno + 1))

    # Skip empty lines, headers, and code blocks
    [[ -z "$line" ]] && continue
    [[ "$line" =~ ^# ]] && continue
    [[ "$line" =~ ^\`\`\` ]] && continue

    # Look for numeric patterns that suggest hardcoded values
    # Match: digits followed by units (ms, s, px, points, etc.)
    if echo "$line" | grep -qE '\b[0-9]+\s*(ms|milliseconds?|seconds?|minutes?|hours?|days?|px|points?|%|items?|times?|attempts?)\b'; then
      echo "NUMERIC ${label}:${lineno} $(echo "$line" | head -c 80)"
      VIOLATIONS=$((VIOLATIONS + 1))
    fi

    # Match: standalone numbers that look like configuration values
    if echo "$line" | grep -qE '\b(of|at|within|after|every|max|min|limit|threshold|timeout|delay|duration|interval|count|size|rate|score)\b.*\b[0-9]+\b'; then
      echo "NUMERIC ${label}:${lineno} $(echo "$line" | head -c 80)"
      VIOLATIONS=$((VIOLATIONS + 1))
    fi
  done < "$file"
}

# Check L1-L4 files only (L5 is allowed to have numbers)
[[ -f "$SPEC_DIR/01.PHILOSOPHY.md" ]] && check_file "$SPEC_DIR/01.PHILOSOPHY.md" "L1"
[[ -f "$SPEC_DIR/02.TRUTHS.md" ]] && check_file "$SPEC_DIR/02.TRUTHS.md" "L2"
[[ -f "$SPEC_DIR/03.INTERACTIONS.md" ]] && check_file "$SPEC_DIR/03.INTERACTIONS.md" "L3"

if [[ -d "$SPEC_DIR/04.SYSTEMS" ]]; then
  for f in "$SPEC_DIR"/04.SYSTEMS/*.md; do
    check_file "$f" "L4/$(basename "$f")"
  done
fi

if [[ "$VIOLATIONS" -eq 0 ]]; then
  echo "OK: No hardcoded numeric values found in L1-L4"
fi
