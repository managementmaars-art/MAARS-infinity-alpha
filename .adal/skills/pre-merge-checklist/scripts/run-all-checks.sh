#!/usr/bin/env bash
# run-all-checks.sh — Orchestrate all pre-merge checks with pass/fail reporting.
#
# Usage:
#   ./run-all-checks.sh [--output-dir <dir>]
#
# Options:
#   --output-dir <dir>   Directory to write results (default: ./check-results)
#
# Runs in order: linting, type checking, tests, coverage, security scan.
# Continues through all checks even if one fails, then reports overall status.

set -uo pipefail

# ─── Defaults ───────────────────────────────────────────────────────────────────
OUTPUT_DIR="./check-results"

# ─── Parse arguments ────────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case "$1" in
        --output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [--output-dir <dir>]"
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
done

# ─── Setup ───────────────────────────────────────────────────────────────────────
mkdir -p "$OUTPUT_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_FILE="$OUTPUT_DIR/all-checks-${TIMESTAMP}.txt"
FAILED_CHECKS=()
PASSED_CHECKS=()

# ─── Helper: run a check and record result ───────────────────────────────────────
run_check() {
    local name="$1"
    shift
    local cmd="$*"

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "CHECK: ${name}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    local check_file="$OUTPUT_DIR/${name// /-}-${TIMESTAMP}.txt"
    local exit_code=0

    eval "$cmd" 2>&1 | tee "$check_file" || exit_code=$?

    if [[ $exit_code -eq 0 ]]; then
        echo "RESULT: PASS"
        PASSED_CHECKS+=("$name")
        echo "PASS: ${name}" >> "$REPORT_FILE"
    else
        echo "RESULT: FAIL (exit code: ${exit_code})"
        FAILED_CHECKS+=("$name")
        echo "FAIL: ${name}" >> "$REPORT_FILE"
    fi

    return 0  # Always continue to next check
}

# ─── Header ──────────────────────────────────────────────────────────────────────
echo "=== Pre-Merge Check Suite ==="
echo "Output directory: ${OUTPUT_DIR}"
echo "Timestamp: $(date -Iseconds)"
echo ""
echo "Timestamp: $(date -Iseconds)" > "$REPORT_FILE"
echo "Output directory: ${OUTPUT_DIR}" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# ─── 1. Python Linting (ruff) ────────────────────────────────────────────────────
run_check "python-lint" "ruff check app/ tests/ 2>&1; ruff format --check app/ tests/ 2>&1"

# ─── 2. TypeScript/React Linting (eslint + prettier) ─────────────────────────────
run_check "ts-lint" "npx eslint 'src/**/*.{ts,tsx}' --max-warnings 0 2>&1; npx prettier --check 'src/**/*.{ts,tsx}' 2>&1"

# ─── 3. Python Type Checking (mypy) ──────────────────────────────────────────────
run_check "python-types" "mypy app/ --strict --no-error-summary 2>&1"

# ─── 4. TypeScript Type Checking (tsc) ───────────────────────────────────────────
run_check "ts-types" "npx tsc --noEmit 2>&1"

# ─── 5. Python Tests ─────────────────────────────────────────────────────────────
run_check "python-tests" "pytest tests/ -q --tb=short 2>&1"

# ─── 6. React Tests ──────────────────────────────────────────────────────────────
run_check "react-tests" "npm test -- --run --reporter=verbose 2>&1"

# ─── 7. Python Coverage ──────────────────────────────────────────────────────────
run_check "python-coverage" "pytest --cov=app --cov-report=term-missing --cov-fail-under=80 -q 2>&1"

# ─── 8. Dependency Security (pip-audit + npm audit) ───────────────────────────────
run_check "dep-security" "pip-audit --requirement requirements.txt 2>&1; npm audit --audit-level=high 2>&1"

# ─── Summary ─────────────────────────────────────────────────────────────────────
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "" >> "$REPORT_FILE"
echo "SUMMARY:" >> "$REPORT_FILE"

TOTAL=$((${#PASSED_CHECKS[@]} + ${#FAILED_CHECKS[@]}))
echo "Total checks: ${TOTAL}"
echo "Passed:       ${#PASSED_CHECKS[@]}"
echo "Failed:       ${#FAILED_CHECKS[@]}"

echo "Total: ${TOTAL}" >> "$REPORT_FILE"
echo "Passed: ${#PASSED_CHECKS[@]}" >> "$REPORT_FILE"
echo "Failed: ${#FAILED_CHECKS[@]}" >> "$REPORT_FILE"

if [[ ${#PASSED_CHECKS[@]} -gt 0 ]]; then
    echo ""
    echo "Passed checks:"
    for check in "${PASSED_CHECKS[@]}"; do
        echo "  [PASS] ${check}"
    done
fi

if [[ ${#FAILED_CHECKS[@]} -gt 0 ]]; then
    echo ""
    echo "Failed checks:"
    for check in "${FAILED_CHECKS[@]}"; do
        echo "  [FAIL] ${check}"
    done
    echo ""
    echo "OVERALL: FAIL"
    echo "Overall: FAIL" >> "$REPORT_FILE"
    echo "Full report: ${REPORT_FILE}"
    exit 1
else
    echo ""
    echo "OVERALL: PASS"
    echo "Overall: PASS" >> "$REPORT_FILE"
    echo "Full report: ${REPORT_FILE}"
    exit 0
fi
