#!/usr/bin/env bash
# check-duplicate-ids.sh — Find duplicate user story IDs in L5
# Usage: bash check-duplicate-ids.sh <spec-dir>
# Output: duplicates with file:line format
#
# Handles two layouts:
#   - View directories (by_phase/, by_journey/, etc.): cross-file dupes checked per view dir
#     (stories are intentionally duplicated across view dirs)
#   - Flat layout: cross-file dupes checked across all files
# Intra-file duplicates are always checked.

set -euo pipefail

SPEC_DIR="${1:-.}"
STORIES_DIR="$SPEC_DIR/05.IMPLEMENTATION/USER_STORIES"
FOUND=0

if [[ ! -d "$STORIES_DIR" ]]; then
  echo "OK: No USER_STORIES directory found"
  exit 0
fi

# Extract story IDs from files, output just the ID portion
extract_ids() {
  grep -h '^id: US-' "$@" 2>/dev/null | sed 's/^id: //' || true
}

# --- Detect layout: view directories vs flat ---
VIEW_DIRS=()
for d in "$STORIES_DIR"/*/; do
  [[ -d "$d" ]] && VIEW_DIRS+=("$d")
done

# --- Cross-file duplicates ---
if [[ ${#VIEW_DIRS[@]} -gt 0 ]]; then
  # View directory layout: check within each view dir
  for view_dir in "${VIEW_DIRS[@]}"; do
    yaml_files=()
    while IFS= read -r f; do
      yaml_files+=("$f")
    done < <(find "$view_dir" -name "*.yaml" -o -name "*.yml" 2>/dev/null | sort)
    [[ ${#yaml_files[@]} -eq 0 ]] && continue

    dupes=$(extract_ids "${yaml_files[@]}" | sort | uniq -d) || true
    if [[ -n "$dupes" ]]; then
      while IFS= read -r id; do
        # Find which files contain this duplicate
        for f in "${yaml_files[@]}"; do
          lineno=$(grep -n "^id: ${id}$" "$f" 2>/dev/null | head -1 | cut -d: -f1) || true
          [[ -n "$lineno" ]] && echo "DUPLICATE ${f}:${lineno} ${id} (cross-file in $(basename "${view_dir%/}"))"
        done
        FOUND=1
      done <<< "$dupes"
    fi
  done
else
  # Flat layout: check across all files
  yaml_files=()
  while IFS= read -r f; do
    yaml_files+=("$f")
  done < <(find "$STORIES_DIR" -maxdepth 1 -name "*.yaml" -o -name "*.yml" 2>/dev/null | sort)

  if [[ ${#yaml_files[@]} -gt 0 ]]; then
    dupes=$(extract_ids "${yaml_files[@]}" | sort | uniq -d) || true
    if [[ -n "$dupes" ]]; then
      while IFS= read -r id; do
        for f in "${yaml_files[@]}"; do
          lineno=$(grep -n "^id: ${id}$" "$f" 2>/dev/null | head -1 | cut -d: -f1) || true
          [[ -n "$lineno" ]] && echo "DUPLICATE ${f}:${lineno} ${id} (cross-file)"
        done
        FOUND=1
      done <<< "$dupes"
    fi
  fi
fi

# --- Intra-file duplicates (always checked) ---
while IFS= read -r file; do
  dupes=$(extract_ids "$file" | sort | uniq -d) || true
  if [[ -n "$dupes" ]]; then
    while IFS= read -r id; do
      # Report each occurrence
      while IFS= read -r match; do
        lineno=$(echo "$match" | cut -d: -f1)
        echo "DUPLICATE ${file}:${lineno} ${id} (intra-file)"
      done < <(grep -n "^id: ${id}$" "$file" 2>/dev/null || true)
      FOUND=1
    done <<< "$dupes"
  fi
done < <(find "$STORIES_DIR" -name "*.yaml" -o -name "*.yml" 2>/dev/null | sort)

if [[ "$FOUND" -eq 0 ]]; then
  echo "OK: No duplicate story IDs found"
fi

exit $FOUND
