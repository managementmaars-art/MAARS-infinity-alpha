#!/usr/bin/env bash
# check-hierarchy.sh — Find downward references across spec files
# Usage: bash check-hierarchy.sh <spec-dir>
# Output: violations with file:line format

set -euo pipefail

SPEC_DIR="${1:-.}"
VIOLATIONS=0

# Build list of L4 system names (for detecting upward refs in L1-L3)
SYSTEM_NAMES=()
if [[ -d "$SPEC_DIR/04.SYSTEMS" ]]; then
  for f in "$SPEC_DIR"/04.SYSTEMS/*.md; do
    [[ "$(basename "$f")" == "SYSTEMS_OVERVIEW.md" ]] && continue
    name=$(basename "$f" .md)
    SYSTEM_NAMES+=("$name")
  done
fi

check_file() {
  local file="$1"
  local level="$2"
  local lineno=0

  while IFS= read -r line; do
    lineno=$((lineno + 1))

    # Skip empty lines and markdown headers
    [[ -z "$line" ]] && continue

    # Check for L4 system name references in L1-L3
    if [[ "$level" -le 3 ]]; then
      for sysname in "${SYSTEM_NAMES[@]}"; do
        if echo "$line" | grep -qi "$sysname"; then
          echo "VIOLATION L${level}:${lineno} references L4 system '${sysname}': $(echo "$line" | head -c 80)"
          VIOLATIONS=$((VIOLATIONS + 1))
        fi
      done
    fi

    # Check for L5 references in L1-L4 (user story IDs, fine-tuning file refs)
    if [[ "$level" -le 4 ]]; then
      if echo "$line" | grep -qiE '(USER_STORIES|FINE_TUNING|\.yml|\.yaml|@phase|@journey)'; then
        echo "VIOLATION L${level}:${lineno} references L5 concept: $(echo "$line" | head -c 80)"
        VIOLATIONS=$((VIOLATIONS + 1))
      fi
    fi
  done < "$file"
}

# Check each level
[[ -f "$SPEC_DIR/01.PHILOSOPHY.md" ]] && check_file "$SPEC_DIR/01.PHILOSOPHY.md" 1
[[ -f "$SPEC_DIR/02.TRUTHS.md" ]] && check_file "$SPEC_DIR/02.TRUTHS.md" 2
[[ -f "$SPEC_DIR/03.INTERACTIONS.md" ]] && check_file "$SPEC_DIR/03.INTERACTIONS.md" 3

if [[ -d "$SPEC_DIR/04.SYSTEMS" ]]; then
  for f in "$SPEC_DIR"/04.SYSTEMS/*.md; do
    check_file "$f" 4
  done
fi

if [[ "$VIOLATIONS" -eq 0 ]]; then
  echo "OK: No hierarchy violations found"
fi
