#!/usr/bin/env bash
# scripts/e2e/full_coverage_validation.sh
# Master coverage validation script for unit + E2E + JSONL + coverage artifacts.
#
# Usage: ./scripts/e2e/full_coverage_validation.sh
#
# Part of br-jv3y: Create full_coverage_validation.sh Master Script

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Source the E2E logging library
source "${PROJECT_ROOT}/scripts/lib/e2e_log.sh"

# Initialize logging
e2e_init "shell" "full_coverage_validation"
e2e_run_start

# ─── Counters ───────────────────────────────────────────────────────────────
total=0
passed=0
failed=0
skipped=0

OUTPUT_DIR="${PROJECT_ROOT}/test-results"
E2E_DIR="${OUTPUT_DIR}/e2e"
UNIT_LOG="${OUTPUT_DIR}/unit_tests.log"
E2E_LOG="${OUTPUT_DIR}/e2e_scripts.log"
JSONL_LOG="${OUTPUT_DIR}/jsonl_validation.log"
COVERAGE_LOG="${OUTPUT_DIR}/coverage.log"
SUMMARY_FILE="${OUTPUT_DIR}/summary.md"

mkdir -p "${OUTPUT_DIR}" "${E2E_DIR}"
: > "${UNIT_LOG}"
: > "${E2E_LOG}"
: > "${JSONL_LOG}"
: > "${COVERAGE_LOG}"

now_ms() {
    date +%s%3N 2>/dev/null || echo $(($(date +%s) * 1000))
}

run_cmd() {
    local test_name="$1"
    local suite="$2"
    local log_file="$3"
    shift 3

    e2e_test_start "$test_name" "$suite"
    local start_time
    start_time=$(now_ms)

    set +e
    "$@" 2>&1 | tee -a "$log_file"
    local exit_code=${PIPESTATUS[0]}
    set -e

    local end_time
    end_time=$(now_ms)
    local duration=$((end_time - start_time))

    ((total++)) || true

    if [[ $exit_code -eq 0 ]]; then
        ((passed++)) || true
        e2e_test_pass "$test_name" "$suite" "$duration"
        return 0
    fi

    ((failed++)) || true
    local err_msg
    err_msg=$(tail -3 "$log_file" | tr '\n' ' ')
    e2e_test_fail "$test_name" "$suite" "$duration" 0 "$err_msg" "CommandFailure"
    return $exit_code
}

# ─── Phase 1: Unit Tests ───────────────────────────────────────────────────

phase_start=$(now_ms)
e2e_phase_start "unit_tests" "Running connector/query/security unit tests"

run_cmd "connector_edge_cases" "unit" "$UNIT_LOG" \
    cargo test connectors:: --no-fail-fast
run_cmd "query_parsing" "unit" "$UNIT_LOG" \
    cargo test search::query::tests --no-fail-fast
run_cmd "security_paths" "unit" "$UNIT_LOG" \
    cargo test pages::verify::tests --no-fail-fast

phase_end=$(now_ms)
e2e_phase_end "unit_tests" $((phase_end - phase_start))

# ─── Phase 2: E2E Scripts ──────────────────────────────────────────────────

phase_start=$(now_ms)
e2e_phase_start "e2e_scripts" "Running E2E shell scripts"

for script in connector_stress query_parser_e2e security_paths_e2e; do
    script_path="${PROJECT_ROOT}/scripts/e2e/${script}.sh"
    if [[ ! -x "$script_path" ]]; then
        ((total++)) || true
        ((failed++)) || true
        e2e_test_start "$script" "e2e"
        e2e_test_fail "$script" "e2e" 0 0 "Missing script: $script_path" "MissingScript"
        continue
    fi
    run_cmd "$script" "e2e" "$E2E_LOG" "$script_path"
done

phase_end=$(now_ms)
e2e_phase_end "e2e_scripts" $((phase_end - phase_start))

# ─── Phase 3: JSONL Validation ─────────────────────────────────────────────

phase_start=$(now_ms)
e2e_phase_start "jsonl_validation" "Validating E2E JSONL logs"

mapfile -t jsonl_files < <(find "${E2E_DIR}" -type f \( -name "*.jsonl" -o -name "cass.log" \) 2>/dev/null | sort)

if [[ ${#jsonl_files[@]} -eq 0 ]]; then
    ((total++)) || true
    ((failed++)) || true
    e2e_test_start "jsonl_logs_present" "validation"
    e2e_test_fail "jsonl_logs_present" "validation" 0 0 "No JSONL logs found in ${E2E_DIR}" "MissingLogs"
else
    for jsonl in "${jsonl_files[@]}"; do
        base="$(basename "$jsonl")"
        run_cmd "validate_${base}" "validation" "$JSONL_LOG" \
            "${PROJECT_ROOT}/scripts/validate-e2e-jsonl.sh" "$jsonl"
    done
fi

phase_end=$(now_ms)
e2e_phase_end "jsonl_validation" $((phase_end - phase_start))

# ─── Phase 4: Coverage Report ──────────────────────────────────────────────

phase_start=$(now_ms)
e2e_phase_start "coverage" "Generating coverage report"

run_cmd "coverage_report" "coverage" "$COVERAGE_LOG" \
    cargo +nightly llvm-cov --lib --html --output-dir "${OUTPUT_DIR}/coverage"

phase_end=$(now_ms)
e2e_phase_end "coverage" $((phase_end - phase_start))

# ─── Summary ───────────────────────────────────────────────────────────────

total_duration=$(e2e_duration_since_start)
e2e_run_end "$total" "$passed" "$failed" "$skipped" "$total_duration"

cat > "$SUMMARY_FILE" <<SUMMARY_EOF
# Full Coverage Validation Summary

**Generated:** $(date -u +"%Y-%m-%d %H:%M:%S UTC")
**Run ID:** $(e2e_run_id)

## Results

- Total: $total
- Passed: $passed
- Failed: $failed
- Skipped: $skipped
- Duration: ${total_duration} ms

## Logs

- Unit tests: ${UNIT_LOG}
- E2E scripts: ${E2E_LOG}
- JSONL validation: ${JSONL_LOG}
- Coverage: ${COVERAGE_LOG}
- JSONL run log: $(e2e_output_file)

## Artifacts

- Coverage report: ${OUTPUT_DIR}/coverage/
- E2E logs: ${E2E_DIR}
SUMMARY_EOF

if [[ $failed -gt 0 ]]; then
    echo "FAILED: $failed test(s) failed"
    echo "Summary: ${SUMMARY_FILE}"
    exit 1
fi

echo "SUCCESS: All $passed tests passed"
echo "Summary: ${SUMMARY_FILE}"
exit 0
