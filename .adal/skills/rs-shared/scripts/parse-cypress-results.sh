#!/usr/bin/env bash
# parse-cypress-results.sh — Parse Cypress JSON reporter output into story/criterion/status lines
# Usage: bash parse-cypress-results.sh <cypress-json-output-file>
# Output: one line per acceptance criterion: <story-id> <criterion-id> <pass|fail>
#
# Expects Cypress --reporter json output with suites titled "US-nnn: ..."
# and tests titled "AC-nnn-nnn: ..."

set -euo pipefail

INPUT_FILE="${1:-}"

if [[ -z "$INPUT_FILE" || ! -f "$INPUT_FILE" ]]; then
  echo "ERROR: cypress JSON output file required" >&2
  exit 1
fi

# Strategy: extract suite titles to get current story ID, then extract test
# titles and pass/fail status to get criterion results.
#
# We scan line by line, tracking the current story ID from suite "title" lines,
# then matching test "title" lines and their adjacent "pass"/"fail" fields.

CURRENT_STORY=""
CURRENT_CRITERION=""

while IFS= read -r line; do
  # Match suite title containing a story ID
  suite_id=$(echo "$line" | grep -oE '"title"[[:space:]]*:[[:space:]]*"US-[0-9]+' | grep -oE 'US-[0-9]+' || true)
  if [[ -n "$suite_id" ]]; then
    CURRENT_STORY="$suite_id"
    continue
  fi

  # Match test title containing a criterion ID
  crit_id=$(echo "$line" | grep -oE '"title"[[:space:]]*:[[:space:]]*"AC-[0-9]+-[0-9]+' | grep -oE 'AC-[0-9]+-[0-9]+' || true)
  if [[ -n "$crit_id" ]]; then
    CURRENT_CRITERION="$crit_id"
    continue
  fi

  # Match pass/fail fields (immediately after a criterion title)
  if [[ -n "$CURRENT_STORY" && -n "$CURRENT_CRITERION" ]]; then
    if echo "$line" | grep -qE '"pass"[[:space:]]*:[[:space:]]*true'; then
      echo "$CURRENT_STORY $CURRENT_CRITERION pass"
      CURRENT_CRITERION=""
    elif echo "$line" | grep -qE '"fail"[[:space:]]*:[[:space:]]*true'; then
      echo "$CURRENT_STORY $CURRENT_CRITERION fail"
      CURRENT_CRITERION=""
    fi
  fi
done < "$INPUT_FILE"
