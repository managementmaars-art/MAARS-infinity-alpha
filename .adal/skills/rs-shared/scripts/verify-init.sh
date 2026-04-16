#!/usr/bin/env bash
# verify-init.sh — Check that all expected initialization files exist
# Usage: bash verify-init.sh [project-root]
# Output: FOUND/MISSING file lists and STATUS=complete|incomplete

set -euo pipefail

ROOT="${1:-.}"

EXPECTED_FILES=(
  ".rootspec.json"
  "rootspec/00.AXIOMS.md"
  "rootspec/00.FRAMEWORK.md"
  "rootspec/spec-status.json"
  "rootspec/tests-status.json"
)

FOUND=()
MISSING=()

for f in "${EXPECTED_FILES[@]}"; do
  if [[ -f "$ROOT/$f" ]]; then
    FOUND+=("$f")
  else
    MISSING+=("$f")
  fi
done

echo "FOUND="
if [[ ${#FOUND[@]} -gt 0 ]]; then
  for f in "${FOUND[@]}"; do
    echo "  $f"
  done
else
  echo "  (none)"
fi

echo "MISSING="
if [[ ${#MISSING[@]} -gt 0 ]]; then
  for f in "${MISSING[@]}"; do
    echo "  $f"
  done
else
  echo "  (none)"
fi

if [[ ${#MISSING[@]} -eq 0 ]]; then
  echo "STATUS=complete"
else
  echo "STATUS=incomplete"
fi
