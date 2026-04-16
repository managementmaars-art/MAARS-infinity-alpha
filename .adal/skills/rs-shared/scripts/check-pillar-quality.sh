#!/usr/bin/env bash
# check-pillar-quality.sh — Validate Design Pillar count and brevity
# Usage: bash check-pillar-quality.sh <spec-dir>
# Output: violations or "OK"

set -euo pipefail

SPEC_DIR="${1:-.}"
L1_FILE="$SPEC_DIR/01.PHILOSOPHY.md"

if [[ ! -f "$L1_FILE" ]]; then
  echo "ERROR: 01.PHILOSOPHY.md not found in $SPEC_DIR"
  exit 1
fi

# Extract pillar names (### headings under ## Design Pillars)
PILLARS=()
while IFS= read -r name; do
  [[ -n "$name" ]] && PILLARS+=("$name")
done < <(awk '
  /^## Design Pillars/ { found=1; next }
  found && /^## / { found=0 }
  found && /^### / {
    sub(/^### +/, "")
    print
  }
' "$L1_FILE")

COUNT=${#PILLARS[@]}
echo "PILLAR_COUNT=$COUNT"

ISSUES=0

if [[ "$COUNT" -lt 3 ]]; then
  echo "WARNING: Only $COUNT pillars (recommend 3-5)"
  ISSUES=$((ISSUES + 1))
elif [[ "$COUNT" -gt 5 ]]; then
  echo "WARNING: $COUNT pillars (recommend 3-5, consider consolidating)"
  ISSUES=$((ISSUES + 1))
fi

# For each pillar, extract its body text and check sentence count
for pillar in "${PILLARS[@]}"; do
  # Extract text between this ### heading and the next ### or ## heading
  body=$(awk -v name="$pillar" '
    BEGIN { found=0 }
    found && /^##/ { exit }
    found { print }
    $0 ~ "^### +" name { found=1; next }
  ' "$L1_FILE")

  # Count sentences: periods followed by space or end-of-line (skip empty lines)
  # Collapse body to single line, count sentence-ending punctuation
  flat=$(echo "$body" | grep -v '^[[:space:]]*$' | tr '\n' ' ')
  sentence_count=$(echo "$flat" | grep -oE '[.!?](\s|$)' | wc -l | tr -d ' ')

  if [[ "$sentence_count" -gt 1 ]]; then
    echo "WARNING: Pillar '$pillar' is more than one sentence"
    ISSUES=$((ISSUES + 1))
  fi
done

if [[ "$ISSUES" -eq 0 ]]; then
  echo "OK: $COUNT pillars, all well-formed"
fi
