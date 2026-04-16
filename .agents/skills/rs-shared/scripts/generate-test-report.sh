#!/usr/bin/env bash
# generate-test-report.sh — Parse tests-status.json into a formatted report
# Usage: bash generate-test-report.sh <tests-status-path> [spec-dir]
#
# Reads tests-status.json and outputs pass/fail counts with story lists.
# If spec-dir is provided, also identifies "not tested" stories (in spec but
# no entry in tests-status.json).

set -euo pipefail

STATUS_PATH="${1:?Usage: generate-test-report.sh <tests-status-path> [spec-dir]}"
SPEC_DIR="${2:-}"

if [[ ! -f "$STATUS_PATH" ]]; then
  echo "ERROR: $STATUS_PATH not found" >&2
  exit 1
fi

# Parse tests-status.json
# Use node if available (more reliable JSON parsing), fall back to jq
parse_status() {
  if command -v node &>/dev/null; then
    node -e "
      const fs = require('fs');
      const data = JSON.parse(fs.readFileSync('$STATUS_PATH', 'utf8'));
      const stories = data.stories || {};
      const passing = [];
      const failing = [];
      for (const [id, info] of Object.entries(stories)) {
        if (info.status === 'pass') passing.push(id);
        else failing.push({ id, criteria: info.criteria || {} });
      }
      // Sort by numeric ID
      const sortId = (a, b) => {
        const na = parseInt((typeof a === 'string' ? a : a.id).match(/\d+/)?.[0] || '0');
        const nb = parseInt((typeof b === 'string' ? b : b.id).match(/\d+/)?.[0] || '0');
        return na - nb;
      };
      passing.sort(sortId);
      failing.sort(sortId);
      console.log(JSON.stringify({ passing, failing }));
    "
  elif command -v jq &>/dev/null; then
    jq -c '{
      passing: [.stories | to_entries[] | select(.value.status == "pass") | .key] | sort,
      failing: [.stories | to_entries[] | select(.value.status == "fail") | {id: .key, criteria: .value.criteria}] | sort_by(.id)
    }' "$STATUS_PATH"
  else
    echo "ERROR: need node or jq" >&2
    exit 1
  fi
}

PARSED=$(parse_status)

PASS_IDS=$(echo "$PARSED" | node -e "const d=JSON.parse(require('fs').readFileSync(0,'utf8')); console.log(d.passing.join(', '))" 2>/dev/null || echo "$PARSED" | jq -r '.passing | join(", ")')
PASS_COUNT=$(echo "$PARSED" | node -e "const d=JSON.parse(require('fs').readFileSync(0,'utf8')); console.log(d.passing.length)" 2>/dev/null || echo "$PARSED" | jq '.passing | length')

FAIL_COUNT=$(echo "$PARSED" | node -e "const d=JSON.parse(require('fs').readFileSync(0,'utf8')); console.log(d.failing.length)" 2>/dev/null || echo "$PARSED" | jq '.failing | length')
FAIL_DETAILS=$(echo "$PARSED" | node -e "
  const d=JSON.parse(require('fs').readFileSync(0,'utf8'));
  for (const f of d.failing) {
    const failCriteria = Object.entries(f.criteria).filter(([,s]) => s === 'fail').map(([id]) => id);
    console.log('  ' + f.id + ': ' + failCriteria.join(', ') + ' — fail');
  }
" 2>/dev/null || echo "$PARSED" | jq -r '.failing[] | "  \(.id): \([.criteria | to_entries[] | select(.value == "fail") | .key] | join(", ")) — fail"')

# Find not-tested stories if spec-dir provided
NOT_TESTED=""
NOT_TESTED_COUNT=0
if [[ -n "$SPEC_DIR" ]]; then
  STORIES_DIR="$SPEC_DIR/05.IMPLEMENTATION/USER_STORIES"
  if [[ -d "$STORIES_DIR" ]]; then
    # Get all story IDs from spec YAML files
    SPEC_IDS=$(find "$STORIES_DIR" \( -name "*.yaml" -o -name "*.yml" \) 2>/dev/null | xargs grep -hE '^\s*-?\s*id:\s*(US-[0-9]+)' 2>/dev/null | grep -oE 'US-[0-9]+' | sort -u)
    # Get all story IDs from tests-status.json
    TESTED_IDS=$(echo "$PARSED" | node -e "
      const d=JSON.parse(require('fs').readFileSync(0,'utf8'));
      const all = [...d.passing, ...d.failing.map(f=>f.id)];
      console.log(all.join('\n'));
    " 2>/dev/null || echo "$PARSED" | jq -r '(.passing + [.failing[].id]) | .[]')

    # Find IDs in spec but not in tests
    NOT_TESTED_IDS=$(comm -23 <(echo "$SPEC_IDS") <(echo "$TESTED_IDS" | sort -u) 2>/dev/null || true)
    if [[ -n "$NOT_TESTED_IDS" ]]; then
      NOT_TESTED_COUNT=$(echo "$NOT_TESTED_IDS" | wc -l | tr -d ' ')
      NOT_TESTED=$(echo "$NOT_TESTED_IDS" | tr '\n' ',' | sed 's/,$//' | sed 's/,/, /g')
    fi
  fi
fi

# Output report
echo "PASS: $PASS_COUNT stories"
echo "FAIL: $FAIL_COUNT stories"
[[ $NOT_TESTED_COUNT -gt 0 ]] && echo "NOT TESTED: $NOT_TESTED_COUNT stories"
echo ""

if [[ -n "$PASS_IDS" ]]; then
  echo "Passing: $PASS_IDS"
fi

if [[ $FAIL_COUNT -gt 0 ]]; then
  echo "Failing:"
  echo "$FAIL_DETAILS"
fi

if [[ -n "$NOT_TESTED" ]]; then
  echo "Not tested: $NOT_TESTED"
fi
