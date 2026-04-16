#!/usr/bin/env bash
# run-tests.sh — Run jest + Playwright tests and write results to state.json
# Usage: bash run-tests.sh <run_dir> <project_dir>
set -euo pipefail

RUN_DIR="$1"
PROJECT_DIR="$2"
STATE_FILE="$RUN_DIR/state.json"

echo "Running tests in: $PROJECT_DIR"
cd "$PROJECT_DIR"

OVERALL_EXIT=0

# ── Jest ──────────────────────────────────────────────────────────────────────
JEST_EXIT=0
JEST_SUMMARY="skipped — no jest config"

if [ -f "package.json" ] && grep -q '"jest"' package.json 2>/dev/null; then
  RESULTS_FILE="$RUN_DIR/jest-results.json"
  npx jest --json --outputFile="$RESULTS_FILE" --passWithNoTests 2>/dev/null || JEST_EXIT=$?
  JEST_SUMMARY=$(python3 - "$RESULTS_FILE" << 'PYEOF'
import json, sys
try:
    r = json.load(open(sys.argv[1]))
    passed = r.get('numPassedTests', 0)
    failed = r.get('numFailedTests', 0)
    total  = r.get('numTotalTests', 0)
    print(f"{passed} passed, {failed} failed, {total} total")
except:
    print("jest results unavailable")
PYEOF
)
  [ $JEST_EXIT -ne 0 ] && OVERALL_EXIT=1
fi

# ── Playwright ────────────────────────────────────────────────────────────────
PW_EXIT=0
PW_SUMMARY="skipped — no playwright config"

if ls playwright.config.* 2>/dev/null | head -1 | grep -q .; then
  PW_RESULTS="$RUN_DIR/playwright-results.json"
  npx playwright test --reporter=json > "$PW_RESULTS" 2>&1 || PW_EXIT=$?
  PW_SUMMARY=$(python3 - "$PW_RESULTS" << 'PYEOF'
import json, sys
try:
    r = json.load(open(sys.argv[1]))
    stats = r.get('stats', {})
    passed = stats.get('expected', 0)
    failed = stats.get('unexpected', 0)
    total  = stats.get('total', 0)
    print(f"{passed} passed, {failed} failed, {total} total")
except:
    print("playwright results unavailable")
PYEOF
)
  [ $PW_EXIT -ne 0 ] && OVERALL_EXIT=1
fi

# ── Write results to state ────────────────────────────────────────────────────
python3 - "$STATE_FILE" "$JEST_EXIT" "$JEST_SUMMARY" "$PW_EXIT" "$PW_SUMMARY" "$OVERALL_EXIT" << 'PYEOF'
import json, os, sys
state_file = sys.argv[1]
jest_exit, jest_summary = int(sys.argv[2]), sys.argv[3]
pw_exit, pw_summary     = int(sys.argv[4]), sys.argv[5]
overall_exit            = int(sys.argv[6])

state = json.load(open(state_file, encoding='utf-8'))
state['phases']['test-runner']['jest_exit_code']       = jest_exit
state['phases']['test-runner']['jest_summary']         = jest_summary
state['phases']['test-runner']['playwright_exit_code'] = pw_exit
state['phases']['test-runner']['playwright_summary']   = pw_summary
state['phases']['test-runner']['summary']              = f"Jest: {jest_summary} | E2E: {pw_summary}"
state['phases']['test-runner']['status']               = 'done' if overall_exit == 0 else 'error'

tmp = state_file + '.tmp.' + str(os.getpid())
with open(tmp, 'w', encoding='utf-8') as f:
    json.dump(state, f, ensure_ascii=False, indent=2)
os.replace(tmp, state_file)
PYEOF

echo "Jest:       $JEST_SUMMARY"
echo "Playwright: $PW_SUMMARY"
exit $OVERALL_EXIT
