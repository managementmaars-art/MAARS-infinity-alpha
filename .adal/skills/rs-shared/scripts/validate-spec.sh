#!/usr/bin/env bash
# validate-spec.sh — Run all spec validation checks in one call
# Usage: bash validate-spec.sh <spec-dir> [shared-dir]
# Output: combined results from all checks, with section delimiters
# Exit code: 0 if all pass, 1 if any violations found

set -euo pipefail

SPEC_DIR="${1:-rootspec}"
SHARED_DIR="${2:-$(cd "$(dirname "$0")/.." && pwd)}"
SCRIPTS="$SHARED_DIR/scripts"
HAS_VIOLATIONS=0

section() { printf '\n===== %s =====\n' "$1"; }

for check in check-hierarchy check-numerics check-duplicate-ids check-pillar-quality check-tradeoffs check-coverage; do
  section "$check"
  if bash "$SCRIPTS/$check.sh" "$SPEC_DIR" 2>&1; then
    echo "OK"
  else
    HAS_VIOLATIONS=1
  fi
done

section "RESULT"
if [[ $HAS_VIOLATIONS -eq 0 ]]; then
  echo "ALL_PASSED=true"
else
  echo "ALL_PASSED=false"
fi
exit $HAS_VIOLATIONS
