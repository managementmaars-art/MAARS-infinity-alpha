#!/usr/bin/env bash
# type-check.sh — Run Python (mypy --strict) and TypeScript (tsc --noEmit) type checks.
#
# Usage:
#   ./type-check.sh [--output-dir <dir>] [--python-only] [--ts-only]
#
# Options:
#   --output-dir <dir>   Directory to write results (default: ./check-results)
#   --python-only        Run only Python type checking (mypy)
#   --ts-only            Run only TypeScript type checking (tsc)

set -uo pipefail

# ─── Defaults ───────────────────────────────────────────────────────────────────
OUTPUT_DIR="./check-results"
RUN_PYTHON=true
RUN_TS=true

# ─── Parse arguments ────────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case "$1" in
        --output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --python-only)
            RUN_TS=false
            shift
            ;;
        --ts-only)
            RUN_PYTHON=false
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [--output-dir <dir>] [--python-only] [--ts-only]"
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
OVERALL_EXIT=0

echo "=== Type Check Suite ==="
echo "Output directory: ${OUTPUT_DIR}"
echo ""

# ─── Python Type Checking (mypy) ─────────────────────────────────────────────────
if [[ "$RUN_PYTHON" == true ]]; then
    echo "─── Python (mypy --strict) ───"
    MYPY_FILE="$OUTPUT_DIR/mypy-report-${TIMESTAMP}.txt"

    mypy app/ --strict \
        --no-error-summary \
        --show-column-numbers \
        --show-error-codes \
        --pretty \
        2>&1 | tee "$MYPY_FILE"
    MYPY_EXIT=${PIPESTATUS[0]}

    echo "" >> "$MYPY_FILE"
    echo "Timestamp: $(date -Iseconds)" >> "$MYPY_FILE"

    if [[ $MYPY_EXIT -eq 0 ]]; then
        echo "Python type check: PASS"
        echo "Status: PASS" >> "$MYPY_FILE"
    else
        echo "Python type check: FAIL"
        echo "Status: FAIL" >> "$MYPY_FILE"
        OVERALL_EXIT=1
    fi
    echo ""
fi

# ─── TypeScript Type Checking (tsc) ──────────────────────────────────────────────
if [[ "$RUN_TS" == true ]]; then
    echo "─── TypeScript (tsc --noEmit) ───"
    TSC_FILE="$OUTPUT_DIR/tsc-report-${TIMESTAMP}.txt"

    npx tsc --noEmit --pretty 2>&1 | tee "$TSC_FILE"
    TSC_EXIT=${PIPESTATUS[0]}

    echo "" >> "$TSC_FILE"
    echo "Timestamp: $(date -Iseconds)" >> "$TSC_FILE"

    if [[ $TSC_EXIT -eq 0 ]]; then
        echo "TypeScript type check: PASS"
        echo "Status: PASS" >> "$TSC_FILE"
    else
        echo "TypeScript type check: FAIL"
        echo "Status: FAIL" >> "$TSC_FILE"
        OVERALL_EXIT=1
    fi
    echo ""
fi

# ─── Summary ─────────────────────────────────────────────────────────────────────
if [[ $OVERALL_EXIT -eq 0 ]]; then
    echo "OVERALL: PASS — All type checks passed."
else
    echo "OVERALL: FAIL — One or more type checks failed. See reports in ${OUTPUT_DIR}/"
fi

exit $OVERALL_EXIT
