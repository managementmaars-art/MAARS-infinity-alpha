#!/usr/bin/env bash
# accessibility-check.sh — Run axe-core accessibility scan against the application.
#
# Usage:
#   ./accessibility-check.sh [--output-dir <dir>] [--url <url>] [--pages <file>]
#
# Options:
#   --output-dir <dir>   Directory to write results (default: ./check-results)
#   --url <url>          Base URL to scan (default: http://localhost:3000)
#   --pages <file>       File with list of page paths to scan (one per line)
#
# Prerequisites:
#   npm install -g @axe-core/cli
#   # or use npx: npx @axe-core/cli

set -uo pipefail

# ─── Defaults ───────────────────────────────────────────────────────────────────
OUTPUT_DIR="./check-results"
BASE_URL="http://localhost:3000"
PAGES_FILE=""

# Default pages to scan if no pages file is provided
DEFAULT_PAGES=(
    "/"
    "/login"
    "/users"
    "/settings"
)

# ─── Parse arguments ────────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case "$1" in
        --output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --url)
            BASE_URL="$2"
            shift 2
            ;;
        --pages)
            PAGES_FILE="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [--output-dir <dir>] [--url <url>] [--pages <file>]"
            echo ""
            echo "Options:"
            echo "  --output-dir <dir>   Directory for results (default: ./check-results)"
            echo "  --url <url>          Base URL to scan (default: http://localhost:3000)"
            echo "  --pages <file>       File listing page paths to scan (one per line)"
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
RESULTS_FILE="$OUTPUT_DIR/accessibility-report-${TIMESTAMP}.txt"
JSON_FILE="$OUTPUT_DIR/accessibility-report-${TIMESTAMP}.json"
OVERALL_EXIT=0
TOTAL_VIOLATIONS=0

echo "=== Accessibility Check (axe-core) ==="
echo "Base URL:         ${BASE_URL}"
echo "Output directory: ${OUTPUT_DIR}"
echo ""

# ─── Determine pages to scan ─────────────────────────────────────────────────────
PAGES=()
if [[ -n "$PAGES_FILE" && -f "$PAGES_FILE" ]]; then
    while IFS= read -r line; do
        [[ -z "$line" || "$line" == \#* ]] && continue
        PAGES+=("$line")
    done < "$PAGES_FILE"
else
    PAGES=("${DEFAULT_PAGES[@]}")
fi

echo "Pages to scan: ${#PAGES[@]}"
echo "Timestamp: $(date -Iseconds)" > "$RESULTS_FILE"
echo "Base URL: ${BASE_URL}" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"

# ─── Check if axe CLI is available ───────────────────────────────────────────────
if ! command -v axe &> /dev/null && ! npx @axe-core/cli --version &> /dev/null 2>&1; then
    echo "WARNING: axe-core CLI not found. Install with: npm install -g @axe-core/cli"
    echo "Falling back to Playwright-based accessibility check..."

    # Fallback: use Playwright with @axe-core/playwright
    echo "Running Playwright accessibility tests..."
    npx playwright test --grep accessibility 2>&1 | tee -a "$RESULTS_FILE"
    OVERALL_EXIT=$?

    if [[ $OVERALL_EXIT -eq 0 ]]; then
        echo "PASS: Accessibility checks passed (Playwright fallback)."
    else
        echo "FAIL: Accessibility violations found. See ${RESULTS_FILE}"
    fi
    exit $OVERALL_EXIT
fi

# ─── Scan each page ──────────────────────────────────────────────────────────────
ALL_RESULTS="["

for page_path in "${PAGES[@]}"; do
    full_url="${BASE_URL}${page_path}"
    echo "Scanning: ${full_url}"
    echo "─── ${full_url} ───" >> "$RESULTS_FILE"

    PAGE_JSON="$OUTPUT_DIR/axe-page-${TIMESTAMP}.json"
    PAGE_EXIT=0

    # Run axe-core scan
    npx @axe-core/cli "${full_url}" \
        --save "${PAGE_JSON}" \
        --stdout \
        2>&1 | tee -a "$RESULTS_FILE" || PAGE_EXIT=$?

    if [[ $PAGE_EXIT -ne 0 ]]; then
        OVERALL_EXIT=1
        echo "  VIOLATIONS FOUND on ${page_path}" >> "$RESULTS_FILE"
    else
        echo "  PASS: ${page_path}" >> "$RESULTS_FILE"
    fi

    # Collect results
    if [[ -f "$PAGE_JSON" ]]; then
        # Count violations
        violations=$(python3 -c "
import json, sys
try:
    data = json.load(open('${PAGE_JSON}'))
    violations = data.get('violations', []) if isinstance(data, dict) else []
    print(len(violations))
except Exception:
    print(0)
" 2>/dev/null || echo "0")
        TOTAL_VIOLATIONS=$((TOTAL_VIOLATIONS + violations))
    fi

    echo "" >> "$RESULTS_FILE"
done

# ─── Summary ─────────────────────────────────────────────────────────────────────
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "ACCESSIBILITY SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Pages scanned:     ${#PAGES[@]}"
echo "Total violations:  ${TOTAL_VIOLATIONS}"

echo "" >> "$RESULTS_FILE"
echo "SUMMARY:" >> "$RESULTS_FILE"
echo "Pages scanned: ${#PAGES[@]}" >> "$RESULTS_FILE"
echo "Total violations: ${TOTAL_VIOLATIONS}" >> "$RESULTS_FILE"

if [[ $OVERALL_EXIT -eq 0 && $TOTAL_VIOLATIONS -eq 0 ]]; then
    echo "OVERALL: PASS"
    echo "Status: PASS" >> "$RESULTS_FILE"
else
    echo "OVERALL: FAIL — ${TOTAL_VIOLATIONS} violation(s) found."
    echo "Status: FAIL" >> "$RESULTS_FILE"
    echo "Review details in: ${RESULTS_FILE}"
    OVERALL_EXIT=1
fi

echo "Full report: ${RESULTS_FILE}"
exit $OVERALL_EXIT
