#!/usr/bin/env bash
# generate-gap-report.sh - Generate coverage gap report from coverage.json
#
# Reads coverage.json (cargo-llvm-cov JSON format) and produces a markdown
# report highlighting coverage gaps, uncovered modules, and recommendations.
#
# Usage:
#   ./scripts/generate-gap-report.sh [coverage.json] [output.md]
#
# Environment:
#   COVERAGE_THRESHOLD - Target coverage % (default: 60)

set -euo pipefail

# Defaults
COVERAGE_JSON="${1:-coverage.json}"
OUTPUT_FILE="${2:-gap-report.md}"
THRESHOLD="${COVERAGE_THRESHOLD:-60}"

# Check dependencies
if ! command -v jq &> /dev/null; then
    echo "Error: jq is required but not installed"
    echo "Install with: apt install jq (Linux) or brew install jq (macOS)"
    exit 1
fi

# Check input file
if [ ! -f "$COVERAGE_JSON" ]; then
    echo "Error: Coverage file not found: $COVERAGE_JSON"
    echo ""
    echo "Generate it first with:"
    echo "  cargo llvm-cov --lib --json --output-path $COVERAGE_JSON"
    exit 1
fi

# Extract totals
TOTAL_LINES=$(jq -r '.data[0].totals.lines.count // 0' "$COVERAGE_JSON")
COVERED_LINES=$(jq -r '.data[0].totals.lines.covered // 0' "$COVERAGE_JSON")
TOTAL_FUNCTIONS=$(jq -r '.data[0].totals.functions.count // 0' "$COVERAGE_JSON")
COVERED_FUNCTIONS=$(jq -r '.data[0].totals.functions.covered // 0' "$COVERAGE_JSON")

# Calculate percentages
if [ "$TOTAL_LINES" -gt 0 ]; then
    LINE_COVERAGE=$(awk "BEGIN {printf \"%.2f\", $COVERED_LINES * 100 / $TOTAL_LINES}")
else
    LINE_COVERAGE="0.00"
fi

if [ "$TOTAL_FUNCTIONS" -gt 0 ]; then
    FUNCTION_COVERAGE=$(awk "BEGIN {printf \"%.2f\", $COVERED_FUNCTIONS * 100 / $TOTAL_FUNCTIONS}")
else
    FUNCTION_COVERAGE="0.00"
fi

UNCOVERED_LINES=$((TOTAL_LINES - COVERED_LINES))

# Generate report
cat > "$OUTPUT_FILE" << EOF
# Coverage Gap Report

Generated: $(date -I)

## Summary

| Metric | Value |
|--------|-------|
| Total Lines | ${TOTAL_LINES} |
| Covered Lines | ${COVERED_LINES} |
| Line Coverage | **${LINE_COVERAGE}%** |
| Function Coverage | ${FUNCTION_COVERAGE}% |
| Threshold | ${THRESHOLD}% |

EOF

# Status indicator
if (( $(echo "$LINE_COVERAGE >= 90" | bc -l) )); then
    echo ":trophy: **Excellent** - Phase 4 target achieved (90%+)" >> "$OUTPUT_FILE"
elif (( $(echo "$LINE_COVERAGE >= 80" | bc -l) )); then
    echo ":star: **Good** - Phase 3 target achieved (80%+)" >> "$OUTPUT_FILE"
elif (( $(echo "$LINE_COVERAGE >= 70" | bc -l) )); then
    echo ":white_check_mark: **Adequate** - Phase 2 target achieved (70%+)" >> "$OUTPUT_FILE"
elif (( $(echo "$LINE_COVERAGE >= $THRESHOLD" | bc -l) )); then
    echo ":heavy_check_mark: **Foundation** - Phase 1 target met (${THRESHOLD}%+)" >> "$OUTPUT_FILE"
else
    echo ":x: **Below Threshold** - Coverage ${LINE_COVERAGE}% < ${THRESHOLD}%" >> "$OUTPUT_FILE"
fi

echo "" >> "$OUTPUT_FILE"

# Top uncovered modules (by uncovered lines)
cat >> "$OUTPUT_FILE" << 'EOF'
## Top 20 Uncovered Modules (by uncovered lines)

| Coverage | Uncovered | Module | Category |
|----------|-----------|--------|----------|
EOF

# Extract per-file data and compute uncovered lines
# Note: filenames may be full paths, so we check for "src/" anywhere in the path
jq -r '.data[0].files[] |
    select(.filename | contains("/src/")) |
    {
        filename: (.filename | split("/src/") | last | "src/" + .),
        total: .summary.lines.count,
        covered: .summary.lines.covered,
        uncovered: (.summary.lines.count - .summary.lines.covered),
        percent: (if .summary.lines.count > 0 then (.summary.lines.covered * 100 / .summary.lines.count) else 0 end)
    } |
    select(.uncovered > 50) |
    "\(.percent | floor)%|\(.uncovered)|\(.filename)"' "$COVERAGE_JSON" | \
    sort -t'|' -k2 -nr | head -20 | \
    while IFS='|' read -r percent uncovered filename; do
        # Categorize the file
        case "$filename" in
            src/lib.rs) category="CLI entry point" ;;
            src/ui/*) category="UI" ;;
            src/pages/wizard*) category="Export wizard" ;;
            src/pages/secret*) category="Security" ;;
            src/pages/deploy*) category="Deploy" ;;
            src/pages/*) category="Pages" ;;
            src/sources/*) category="Sources" ;;
            src/search/*) category="Search" ;;
            src/connectors/*) category="Connectors" ;;
            src/storage/*) category="Storage" ;;
            src/indexer/*) category="Indexer" ;;
            src/model/*) category="Model" ;;
            *) category="Other" ;;
        esac
        echo "| ${percent} | ${uncovered} | ${filename} | ${category} |" >> "$OUTPUT_FILE"
    done

echo "" >> "$OUTPUT_FILE"

# Analysis by category
cat >> "$OUTPUT_FILE" << 'EOF'
## Analysis by Category

### Critical Gaps (Security/Reliability)
EOF

# Find modules with 0% or very low coverage that are critical
jq -r '.data[0].files[] |
    select(.filename | contains("/src/")) |
    select(.summary.lines.count > 100) |
    {
        filename: (.filename | split("/src/") | last | "src/" + .),
        total: .summary.lines.count,
        covered: .summary.lines.covered,
        percent: (if .summary.lines.count > 0 then (.summary.lines.covered * 100 / .summary.lines.count) else 0 end)
    } |
    select(.percent < 30) |
    "- **\(.filename)**: \(.percent | floor)% coverage (\(.total - .covered) uncovered lines)"' "$COVERAGE_JSON" >> "$OUTPUT_FILE"

echo "" >> "$OUTPUT_FILE"

# Well-covered modules
cat >> "$OUTPUT_FILE" << 'EOF'
## Well-Covered Modules (>80%)

| Coverage | Module |
|----------|--------|
EOF

jq -r '.data[0].files[] |
    select(.filename | contains("/src/")) |
    select(.summary.lines.count > 50) |
    {
        filename: (.filename | split("/src/") | last | "src/" + .),
        percent: (if .summary.lines.count > 0 then (.summary.lines.covered * 100 / .summary.lines.count) else 0 end)
    } |
    select(.percent > 80) |
    "| \(.percent | . * 100 | floor / 100)% | \(.filename) |"' "$COVERAGE_JSON" | \
    sort -t'|' -k2 -nr | head -15 >> "$OUTPUT_FILE"

echo "" >> "$OUTPUT_FILE"

# Recommendations
cat >> "$OUTPUT_FILE" << 'EOF'
## Recommendations

### High Priority
1. Add tests for security-critical modules (secret scanning, encryption)
2. Increase coverage for modules with 0% coverage and >100 lines
3. Focus on error handling paths

### Medium Priority
4. Add integration tests for source management
5. Improve UI component coverage with snapshot tests
6. Add tests for deploy functionality

### Testing Notes
- Use real fixtures where possible (avoid mocks)
- Prefer integration tests over unit tests for I/O-heavy code
- E2E tests can cover CLI dispatch and wizard flows

---

*Report generated by scripts/generate-gap-report.sh*
*See docs/COVERAGE_POLICY.md for coverage targets and exclusions*
EOF

echo "Gap report generated: $OUTPUT_FILE"
echo "Line coverage: ${LINE_COVERAGE}% (threshold: ${THRESHOLD}%)"
