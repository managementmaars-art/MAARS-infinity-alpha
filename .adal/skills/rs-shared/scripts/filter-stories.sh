#!/usr/bin/env bash
# filter-stories.sh — Filter L5 user story YAML files by focus criteria
# Usage: bash filter-stories.sh <spec-dir> [focus]
# Output: one YAML file path per line matching the focus
#
# Focus types:
#   (none)       → all YAML files
#   US-101       → file containing that story ID
#   TASK_SYSTEM  → files with @systems annotation containing that name
#   MVP          → files with @phase: MVP (or any user-defined phase name)
#   failing      → files containing stories that failed in tests-status.json

set -euo pipefail

SPEC_DIR="${1:-.}"
FOCUS="${2:-}"
STORIES_DIR="$SPEC_DIR/05.IMPLEMENTATION/USER_STORIES"

if [[ ! -d "$STORIES_DIR" ]]; then
  exit 0
fi

# Collect all YAML files
yaml_files=()
while IFS= read -r f; do
  yaml_files+=("$f")
done < <(find "$STORIES_DIR" -name "*.yaml" -o -name "*.yml" 2>/dev/null | sort)

if [[ ${#yaml_files[@]} -eq 0 ]]; then
  exit 0
fi

# No focus: output all
if [[ -z "$FOCUS" ]]; then
  printf '%s\n' "${yaml_files[@]}"
  exit 0
fi

# Story ID focus (US-nnn pattern)
if echo "$FOCUS" | grep -qE '^US-[0-9]+$'; then
  for f in "${yaml_files[@]}"; do
    if grep -q "^id: ${FOCUS}$" "$f" 2>/dev/null; then
      echo "$f"
    fi
  done
  exit 0
fi

# Failing stories focus (checked before phase to avoid matching "failing" as a phase)
if [[ "$FOCUS" == "failing" ]]; then
  STATUS_FILE="$SPEC_DIR/tests-status.json"
  if [[ ! -f "$STATUS_FILE" ]]; then
    exit 0
  fi

  # Extract story IDs with "fail" status from tests-status.json
  # Pattern: "US-nnn": {..., "status": "fail", ...}
  # Use grep to find lines with story IDs, then check if their status is fail
  fail_ids=()
  while IFS= read -r id; do
    fail_ids+=("$id")
  done < <(grep -oE '"(US-[0-9]+)"[^}]*"status"[[:space:]]*:[[:space:]]*"fail"' "$STATUS_FILE" 2>/dev/null | grep -oE 'US-[0-9]+' || true)

  if [[ ${#fail_ids[@]} -eq 0 ]]; then
    exit 0
  fi

  for f in "${yaml_files[@]}"; do
    for id in "${fail_ids[@]}"; do
      if grep -q "^id: ${id}$" "$f" 2>/dev/null; then
        echo "$f"
        break
      fi
    done
  done
  exit 0
fi

# Phase focus: try @phase annotation match first
phase_matches=()
for f in "${yaml_files[@]}"; do
  if grep -qi "@phase:.*${FOCUS}" "$f" 2>/dev/null; then
    phase_matches+=("$f")
  fi
done

if [[ ${#phase_matches[@]} -gt 0 ]]; then
  printf '%s\n' "${phase_matches[@]}"
  exit 0
fi

# System name focus (fallback: treat as @systems annotation match)
for f in "${yaml_files[@]}"; do
  if grep -qi "@systems:.*${FOCUS}" "$f" 2>/dev/null; then
    echo "$f"
  fi
done
