#!/usr/bin/env bash
# scripts/tests/generate_evidence_bundle.sh
# Generate verification evidence bundle for release gate consumption (2dccg.11.8).
#
# Usage:
#   ./scripts/tests/generate_evidence_bundle.sh           # Full bundle
#   ./scripts/tests/generate_evidence_bundle.sh --quick    # Subset (stress + e2e only)
#
# Outputs:
#   test-results/evidence-bundle.json   - Structured JSON manifest
#   test-results/evidence-summary.md    - Human-readable summary
#
# Exit code: 0 if all P0 categories pass, 1 otherwise.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
OUTPUT_DIR="${PROJECT_ROOT}/test-results"
BUNDLE_FILE="${OUTPUT_DIR}/evidence-bundle.json"
SUMMARY_FILE="${OUTPUT_DIR}/evidence-summary.md"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
QUICK=0

# Colors
if [[ -t 1 ]]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    BOLD='\033[1m'
    NC='\033[0m'
else
    RED='' GREEN='' YELLOW='' BLUE='' BOLD='' NC=''
fi

for arg in "$@"; do
    case "$arg" in
        --quick) QUICK=1 ;;
        --help|-h)
            echo "Usage: $0 [--quick] [--help]"
            echo "  --quick  Run subset of test categories (faster)"
            exit 0 ;;
    esac
done

mkdir -p "$OUTPUT_DIR"

# =============================================================================
# Test Category Runner
# =============================================================================

declare -A CAT_PASSED CAT_FAILED CAT_TOTAL CAT_DURATION CAT_PRIORITY

run_category() {
    local name="$1"
    local priority="$2"  # P0 or P1
    local filter="$3"
    local test_args="${4:---lib}"

    echo -e "${BOLD}${BLUE}[${priority}] ${name}${NC} (filter: ${filter})"

    local start_s
    start_s=$(date +%s%3N 2>/dev/null || echo $(($(date +%s) * 1000)))

    local raw_output
    raw_output=$(cargo test ${test_args} "${filter}" -- --nocapture 2>&1) || true

    local end_s
    end_s=$(date +%s%3N 2>/dev/null || echo $(($(date +%s) * 1000)))
    local dur=$((end_s - start_s))

    # Parse pass/fail from cargo test output
    local passed=0 failed=0 total=0
    local result_line
    result_line=$(echo "$raw_output" | grep -E "^test result:" | tail -1) || true

    if [[ -n "$result_line" ]]; then
        passed=$(echo "$result_line" | grep -oP '\d+ passed' | grep -oP '\d+') || passed=0
        failed=$(echo "$result_line" | grep -oP '\d+ failed' | grep -oP '\d+') || failed=0
    fi
    total=$((passed + failed))

    CAT_PASSED[$name]=$passed
    CAT_FAILED[$name]=$failed
    CAT_TOTAL[$name]=$total
    CAT_DURATION[$name]=$dur
    CAT_PRIORITY[$name]=$priority

    if [[ $failed -gt 0 ]]; then
        echo -e "  ${RED}FAIL${NC}: ${passed}/${total} passed (${dur}ms)"
    else
        echo -e "  ${GREEN}PASS${NC}: ${passed}/${total} passed (${dur}ms)"
    fi
}

# =============================================================================
# Run Test Categories
# =============================================================================

echo -e "${BOLD}Evidence Bundle Generator${NC}"
echo "Output: ${BUNDLE_FILE}"
echo ""

# P0 categories — must all pass for release gate
run_category "stress_tests"              "P0" "stress_"
run_category "e2e_scenarios"             "P0" "e2e_scenario"
run_category "cross_theme_degradation"   "P0" "cross_theme_degradation"
run_category "density_modes"             "P0" "density_"
run_category "rendering_invariants"      "P0" "rendering_token_affordance"

if [[ $QUICK -eq 0 ]]; then
    # P1 categories — informational, not blocking
    run_category "interaction_state"        "P1" "palette_"
    run_category "style_tokens"             "P1" "style_token_registry\|all_tokens_resolve\|critical_fg_tokens\|critical_bg_tokens" "--lib"
    run_category "contrast_compliance"      "P1" "wcag\|contrast" "--lib --test ui_snap"
    run_category "degradation_policy"       "P1" "deco_\|decorative_policy\|degradation_affordance"
    run_category "animation_stress"         "P1" "reveal_springs\|animation_disabled\|focus_flash"
    run_category "responsive_layout"        "P1" "responsive_width_sweep\|search_topology\|analytics_topology\|size_matrix"
fi

# =============================================================================
# Collect Metadata
# =============================================================================

RUSTC_VERSION=$(rustc --version 2>/dev/null || echo "unknown")
GIT_SHA=$(git -C "$PROJECT_ROOT" rev-parse HEAD 2>/dev/null || echo "unknown")
GIT_BRANCH=$(git -C "$PROJECT_ROOT" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")

# =============================================================================
# Generate JSON Bundle
# =============================================================================

{
    echo "{"
    echo "  \"schema_version\": 1,"
    echo "  \"generated_at\": \"${TIMESTAMP}\","
    echo "  \"commit_sha\": \"${GIT_SHA}\","
    echo "  \"branch\": \"${GIT_BRANCH}\","
    echo "  \"rustc_version\": \"${RUSTC_VERSION}\","
    echo "  \"mode\": \"$( [[ $QUICK -eq 1 ]] && echo quick || echo full)\","
    echo "  \"categories\": {"

    first=true
    for name in "${!CAT_PASSED[@]}"; do
        if [[ "$first" == "true" ]]; then first=false; else echo ","; fi
        printf "    \"%s\": {\"priority\": \"%s\", \"passed\": %d, \"failed\": %d, \"total\": %d, \"duration_ms\": %d}" \
            "$name" "${CAT_PRIORITY[$name]}" "${CAT_PASSED[$name]}" "${CAT_FAILED[$name]}" "${CAT_TOTAL[$name]}" "${CAT_DURATION[$name]}"
    done

    echo ""
    echo "  },"

    # Compute totals
    total_passed=0; total_failed=0; total_total=0; p0_failed=0
    for name in "${!CAT_PASSED[@]}"; do
        total_passed=$((total_passed + ${CAT_PASSED[$name]}))
        total_failed=$((total_failed + ${CAT_FAILED[$name]}))
        total_total=$((total_total + ${CAT_TOTAL[$name]}))
        if [[ "${CAT_PRIORITY[$name]}" == "P0" && ${CAT_FAILED[$name]} -gt 0 ]]; then
            p0_failed=$((p0_failed + ${CAT_FAILED[$name]}))
        fi
    done

    echo "  \"totals\": {"
    echo "    \"passed\": ${total_passed},"
    echo "    \"failed\": ${total_failed},"
    echo "    \"total\": ${total_total},"
    echo "    \"p0_failed\": ${p0_failed},"
    echo "    \"release_gate\": \"$( [[ $p0_failed -eq 0 ]] && echo PASS || echo FAIL)\""
    echo "  }"
    echo "}"
} > "$BUNDLE_FILE"

# =============================================================================
# Generate Markdown Summary
# =============================================================================

# Re-compute totals for summary
total_passed=0 total_failed=0 total_total=0 p0_failed=0
for name in "${!CAT_PASSED[@]}"; do
    total_passed=$((total_passed + ${CAT_PASSED[$name]}))
    total_failed=$((total_failed + ${CAT_FAILED[$name]}))
    total_total=$((total_total + ${CAT_TOTAL[$name]}))
    if [[ "${CAT_PRIORITY[$name]}" == "P0" && ${CAT_FAILED[$name]} -gt 0 ]]; then
        p0_failed=$((p0_failed + ${CAT_FAILED[$name]}))
    fi
done

{
    echo "# Verification Evidence Bundle"
    echo ""
    echo "**Generated:** ${TIMESTAMP}"
    echo "**Commit:** ${GIT_SHA}"
    echo "**Branch:** ${GIT_BRANCH}"
    echo "**Rust:** ${RUSTC_VERSION}"
    echo "**Mode:** $( [[ $QUICK -eq 1 ]] && echo Quick || echo Full)"
    echo ""
    if [[ $p0_failed -eq 0 ]]; then
        echo "## Release Gate: PASS"
    else
        echo "## Release Gate: FAIL (${p0_failed} P0 failures)"
    fi
    echo ""
    echo "## Test Categories"
    echo ""
    echo "| Category | Priority | Passed | Failed | Total | Duration |"
    echo "|----------|----------|--------|--------|-------|----------|"

    # Sort by priority then name
    for name in $(echo "${!CAT_PASSED[@]}" | tr ' ' '\n' | sort); do
        status_icon=""
        if [[ ${CAT_FAILED[$name]} -gt 0 ]]; then
            status_icon="FAIL"
        else
            status_icon="PASS"
        fi
        echo "| ${name} | ${CAT_PRIORITY[$name]} | ${CAT_PASSED[$name]} | ${CAT_FAILED[$name]} | ${CAT_TOTAL[$name]} | ${CAT_DURATION[$name]}ms |"
    done

    echo ""
    echo "## Summary"
    echo ""
    echo "- **Total Tests:** ${total_total}"
    echo "- **Passed:** ${total_passed}"
    echo "- **Failed:** ${total_failed}"
    echo "- **P0 Failures:** ${p0_failed}"
    echo ""
    echo "## Artifacts"
    echo ""
    echo "- JSON manifest: \`test-results/evidence-bundle.json\`"
    echo "- This summary: \`test-results/evidence-summary.md\`"
} > "$SUMMARY_FILE"

# =============================================================================
# Final Output
# =============================================================================

echo ""
echo -e "${BOLD}Evidence Bundle${NC}"
echo "  JSON: ${BUNDLE_FILE}"
echo "  Summary: ${SUMMARY_FILE}"
echo ""

cat "$SUMMARY_FILE"

if [[ $p0_failed -gt 0 ]]; then
    echo ""
    echo -e "${RED}${BOLD}Release gate FAILED: ${p0_failed} P0 test failure(s)${NC}"
    exit 1
else
    echo ""
    echo -e "${GREEN}${BOLD}Release gate PASSED${NC}"
    exit 0
fi
