#!/usr/bin/env bash
# check-tradeoffs.sh — Detect explicit trade-off statements in Level 2
# Usage: bash check-tradeoffs.sh <spec-dir>
# Output: findings or "OK"

set -euo pipefail

SPEC_DIR="${1:-.}"
L2_FILE="$SPEC_DIR/02.TRUTHS.md"

if [[ ! -f "$L2_FILE" ]]; then
  echo "ERROR: 02.TRUTHS.md not found in $SPEC_DIR"
  exit 1
fi

COUNT=0

# Check for trade-off patterns in body text (case-insensitive)
# "over" as a trade-off: "X over Y" — require word boundaries to avoid false positives
while IFS= read -r line; do
  # Skip headings and empty lines for pattern matches
  [[ -z "$line" ]] && continue
  [[ "$line" =~ ^# ]] && continue

  matched=0
  echo "$line" | grep -qiE '\bover\b' && matched=1
  [[ "$matched" -eq 0 ]] && echo "$line" | grep -qiE '\binstead of\b' && matched=1
  [[ "$matched" -eq 0 ]] && echo "$line" | grep -qiE '\brather than\b' && matched=1
  [[ "$matched" -eq 0 ]] && echo "$line" | grep -qiE '\bat the cost of\b' && matched=1

  if [[ "$matched" -eq 1 ]]; then
    COUNT=$((COUNT + 1))
  fi
done < "$L2_FILE"

# Also count section headers containing "Trade"
TRADE_HEADERS=$(grep -ciE '^#+.*trade' "$L2_FILE" || true)
COUNT=$((COUNT + TRADE_HEADERS))

echo "TRADEOFF_COUNT=$COUNT"

if [[ "$COUNT" -eq 0 ]]; then
  echo "WARNING: No explicit trade-offs found in L2. Trade-offs are important — they show what you're choosing and what you're giving up."
else
  echo "OK: Found $COUNT trade-off statement(s)"
fi
