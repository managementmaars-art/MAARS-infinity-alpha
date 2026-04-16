#!/usr/bin/env bash
# build-tests-status.sh — Merge parsed Cypress results into tests-status.json
# Usage: bash build-tests-status.sh <parsed-results-file> <existing-tests-status-json> <output-file>
# Output: merged tests-status.json written to output-file
#
# Input: parsed results from parse-cypress-results.sh (story criterion status lines)
# Merges with existing tests-status.json, preserving stories not in current run.

set -euo pipefail

PARSED_FILE="${1:-}"
EXISTING_FILE="${2:-}"
OUTPUT_FILE="${3:-}"

if [[ -z "$PARSED_FILE" || -z "$OUTPUT_FILE" ]]; then
  echo "ERROR: usage: build-tests-status.sh <parsed-results> <existing-json> <output-file>" >&2
  exit 1
fi

if [[ ! -f "$PARSED_FILE" ]]; then
  echo "ERROR: parsed results file not found: $PARSED_FILE" >&2
  exit 1
fi

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
TMPDIR_WORK=$(mktemp -d)
trap 'rm -rf "$TMPDIR_WORK"' EXIT

# --- Parse new results into per-story files ---
# Each line: US-101 AC-101-1 pass
while IFS=' ' read -r story_id crit_id status; do
  [[ -z "$story_id" ]] && continue
  echo "$crit_id $status" >> "$TMPDIR_WORK/new_${story_id}"
done < "$PARSED_FILE"

# Track which stories are in the new run
NEW_STORIES=()
for f in "$TMPDIR_WORK"/new_US-*; do
  [[ -f "$f" ]] || continue
  sid=$(basename "$f" | sed 's/^new_//')
  NEW_STORIES+=("$sid")
done

# --- Build JSON fragments for new stories ---
build_story_json() {
  local story_id="$1"
  local data_file="$2"
  local all_pass="true"
  local criteria_json=""

  while IFS=' ' read -r crit_id status; do
    [[ -z "$crit_id" ]] && continue
    if [[ "$status" != "pass" ]]; then
      all_pass="false"
    fi
    if [[ -n "$criteria_json" ]]; then
      criteria_json="${criteria_json}, "
    fi
    criteria_json="${criteria_json}\"${crit_id}\": \"${status}\""
  done < "$data_file"

  local story_status="pass"
  if [[ "$all_pass" == "false" ]]; then
    story_status="fail"
  fi

  printf '    "%s": {"status": "%s", "lastRun": "%s", "criteria": {%s}}' \
    "$story_id" "$story_status" "$TIMESTAMP" "$criteria_json"
}

# --- Extract existing stories not in current run ---
EXISTING_PRESERVED=""
if [[ -f "$EXISTING_FILE" ]] && [[ -s "$EXISTING_FILE" ]]; then
  # Extract each story block from existing JSON
  # Find story IDs in existing file
  existing_ids=()
  while IFS= read -r eid; do
    existing_ids+=("$eid")
  done < <(grep -oE '"US-[0-9]+"[[:space:]]*:' "$EXISTING_FILE" 2>/dev/null | grep -oE 'US-[0-9]+' || true)

  for eid in "${existing_ids[@]}"; do
    # Skip if this story is in the new run (will be replaced)
    skip="false"
    for nid in "${NEW_STORIES[@]}"; do
      if [[ "$eid" == "$nid" ]]; then
        skip="true"
        break
      fi
    done
    if [[ "$skip" == "true" ]]; then
      continue
    fi

    # Extract the story's JSON fragment from existing file
    # Match "US-nnn": {...} — grab from the key to the closing brace
    block=$(sed -n "s/.*\(\"${eid}\"[[:space:]]*:[[:space:]]*{[^}]*}\).*/\1/p" "$EXISTING_FILE" 2>/dev/null | head -1 || true)
    if [[ -n "$block" ]]; then
      if [[ -n "$EXISTING_PRESERVED" ]]; then
        EXISTING_PRESERVED="${EXISTING_PRESERVED}
,    ${block}"
      else
        EXISTING_PRESERVED="    ${block}"
      fi
    fi
  done
fi

# --- Assemble final JSON ---
{
  printf '{\n'
  printf '  "lastRun": "%s",\n' "$TIMESTAMP"
  printf '  "stories": {\n'

  # Write new story entries
  first="true"
  for sid in "${NEW_STORIES[@]}"; do
    if [[ "$first" == "true" ]]; then
      first="false"
    else
      printf ',\n'
    fi
    build_story_json "$sid" "$TMPDIR_WORK/new_${sid}"
  done

  # Write preserved existing entries
  if [[ -n "$EXISTING_PRESERVED" ]]; then
    if [[ "$first" == "false" ]]; then
      printf ',\n'
    fi
    printf '%s' "$EXISTING_PRESERVED"
  fi

  printf '\n  }\n'
  printf '}\n'
} > "$OUTPUT_FILE"

echo "OK: wrote $OUTPUT_FILE"
