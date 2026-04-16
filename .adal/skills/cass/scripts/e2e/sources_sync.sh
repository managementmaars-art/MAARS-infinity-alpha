#!/usr/bin/env bash
# scripts/e2e/sources_sync.sh
# End-to-end test for sources list/doctor commands with structured logging.
#
# Usage:
#   ./scripts/e2e/sources_sync.sh
#   CASS_BIN=target/debug/cass ./scripts/e2e/sources_sync.sh
#   ./scripts/e2e/sources_sync.sh --no-build --fail-fast
#
# Artifacts:
#   test-results/e2e/shell_sources_sync_<timestamp>.jsonl

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Source the E2E logging library
source "${PROJECT_ROOT}/scripts/lib/e2e_log.sh"

# Initialize logging
e2e_init "shell" "sources_sync"

# Configuration
NO_BUILD=0
FAIL_FAST=0

for arg in "$@"; do
    case "$arg" in
        --no-build)
            NO_BUILD=1
            ;;
        --fail-fast)
            FAIL_FAST=1
            ;;
        --help|-h)
            echo "Usage: $0 [--no-build] [--fail-fast]"
            exit 0
            ;;
    esac
done

# Sandbox directories
SANDBOX_DIR="${PROJECT_ROOT}/target/e2e-sources-sync/run_$(e2e_run_id)"
HOME_DIR="${SANDBOX_DIR}/home"
DATA_DIR="${SANDBOX_DIR}/data"
CODEX_HOME="${SANDBOX_DIR}/.codex"
STDOUT_DIR="${SANDBOX_DIR}/stdout"
STDERR_DIR="${SANDBOX_DIR}/stderr"

mkdir -p "${HOME_DIR}" "${DATA_DIR}" "${CODEX_HOME}" "${STDOUT_DIR}" "${STDERR_DIR}"

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Resolve cass binary
if [[ -n "${CASS_BIN:-}" ]]; then
    CASS_BIN_RESOLVED="$CASS_BIN"
else
    CASS_BIN_RESOLVED="${PROJECT_ROOT}/target/debug/cass"
fi

cass_env() {
    env \
        HOME="${HOME_DIR}" \
        CODEX_HOME="${CODEX_HOME}" \
        CASS_DATA_DIR="${DATA_DIR}" \
        CODING_AGENT_SEARCH_NO_UPDATE_PROMPT=1 \
        NO_COLOR=1 \
        CASS_NO_COLOR=1 \
        "$@"
}

run_test() {
    local test_name="$1"
    shift
    local stdout_file="${STDOUT_DIR}/${test_name}.out"
    local stderr_file="${STDERR_DIR}/${test_name}.err"

    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    e2e_test_start "$test_name" "sources_sync"

    local start_ms
    start_ms=$(date +%s%3N 2>/dev/null || echo $(($(date +%s) * 1000)))

    local exit_code=0
    set +e
    "$@" >"${stdout_file}" 2>"${stderr_file}"
    exit_code=$?
    set -e

    local end_ms
    end_ms=$(date +%s%3N 2>/dev/null || echo $(($(date +%s) * 1000)))
    local duration=$((end_ms - start_ms))

    if [[ $exit_code -eq 0 ]]; then
        e2e_test_pass "$test_name" "sources_sync" "$duration"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        e2e_info "PASS: ${test_name} (${duration}ms)" "$test_name"
    else
        e2e_test_fail "$test_name" "sources_sync" "$duration" 0 "exit code $exit_code" "CommandFailed"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        e2e_error "FAIL: ${test_name} (exit $exit_code, ${duration}ms)" "$test_name"
        if [[ $FAIL_FAST -eq 1 ]]; then
            local total_duration
            total_duration=$(e2e_duration_since_start)
            e2e_run_end "$TOTAL_TESTS" "$PASSED_TESTS" "$FAILED_TESTS" 0 "$total_duration"
            exit 1
        fi
    fi
}

# =============================================================================
# Main Flow
# =============================================================================

e2e_run_start

# Phase: Build
if [[ $NO_BUILD -eq 0 && ! -x "$CASS_BIN_RESOLVED" ]]; then
    e2e_phase_start "build" "Compile cass binary"
    BUILD_START=$(date +%s%3N 2>/dev/null || echo $(($(date +%s) * 1000)))
    cargo build --bin cass 2>&1
    BUILD_END=$(date +%s%3N 2>/dev/null || echo $(($(date +%s) * 1000)))
    e2e_phase_end "build" "$((BUILD_END - BUILD_START))"
fi

if [[ ! -x "$CASS_BIN_RESOLVED" ]]; then
    e2e_error "cass binary not found at ${CASS_BIN_RESOLVED}" "setup"
    total_duration=$(e2e_duration_since_start)
    e2e_run_end 0 0 0 0 "$total_duration"
    exit 1
fi

# Phase: Setup fixtures
e2e_phase_start "setup_fixtures" "Create Codex session fixture"
mkdir -p "${CODEX_HOME}/sessions/2024/11/20"
cat > "${CODEX_HOME}/sessions/2024/11/20/rollout-sources.jsonl" <<'JSONL'
{"type":"event_msg","timestamp":1732118400000,"payload":{"type":"user_message","message":"test sources sync flow"}}
{"type":"response_item","timestamp":1732118401000,"payload":{"role":"assistant","content":"sources sync response"}}
JSONL
e2e_phase_end "setup_fixtures" 0

# Phase: Index (needed before sources work properly)
e2e_phase_start "index" "Build initial index"
run_test "index_full" cass_env "${CASS_BIN_RESOLVED}" index --full --data-dir "${DATA_DIR}"
e2e_phase_end "index" 0

# Phase: Sources commands
e2e_phase_start "sources_commands" "Test sources CLI commands"

run_test "sources_list" cass_env "${CASS_BIN_RESOLVED}" sources list --json

run_test "sources_doctor" cass_env "${CASS_BIN_RESOLVED}" sources doctor --json --data-dir "${DATA_DIR}"

e2e_phase_end "sources_commands" 0

# Emit run end
total_duration=$(e2e_duration_since_start)
e2e_run_end "$TOTAL_TESTS" "$PASSED_TESTS" "$FAILED_TESTS" 0 "$total_duration"

if [[ $FAILED_TESTS -gt 0 ]]; then
    echo "FAIL: ${FAILED_TESTS}/${TOTAL_TESTS} tests failed"
    echo "Logs: $(e2e_output_file)"
    exit 1
fi

echo "PASS: All ${TOTAL_TESTS} tests passed"
echo "Logs: $(e2e_output_file)"
exit 0
