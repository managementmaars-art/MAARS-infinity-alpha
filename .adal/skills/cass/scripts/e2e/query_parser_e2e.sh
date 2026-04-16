#!/usr/bin/env bash
# scripts/e2e/query_parser_e2e.sh
#
# E2E test for query parsing through the full search pipeline.
# Validates that different query types (simple, phrase, boolean, wildcard,
# filtered, unicode, edge cases) parse and execute correctly against a real index.
#
# Usage: ./scripts/e2e/query_parser_e2e.sh
#
# Part of br-wwl0: Create query_parser_e2e.sh E2E Script

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Source the E2E logging library
source "${PROJECT_ROOT}/scripts/lib/e2e_log.sh"

# Initialize logging
e2e_init "shell" "query_parser_e2e"
e2e_run_start

# ─── Counters ───────────────────────────────────────────────────────────────
total=0
passed=0
failed=0
skipped=0
SUITE="query_parser"

# ─── Helpers ────────────────────────────────────────────────────────────────

CASS_BIN="${PROJECT_ROOT}/target/debug/cass"
SANDBOX_DIR=""

ensure_cass_binary() {
    if [[ ! -x "$CASS_BIN" ]]; then
        e2e_info "Building cass binary..."
        (cd "$PROJECT_ROOT" && cargo build --quiet 2>/dev/null)
    fi
    if [[ ! -x "$CASS_BIN" ]]; then
        e2e_error "cass binary not found at $CASS_BIN"
        exit 1
    fi
}

# Run a query and assert it completes successfully (exit 0).
# Usage: run_query_ok test_name query [extra_args...]
run_query_ok() {
    local test_name="$1"
    local query="$2"
    shift 2
    local extra_args=("$@")

    ((total++)) || true
    e2e_test_start "$test_name" "$SUITE"

    local start_time end_time duration
    start_time=$(date +%s%3N 2>/dev/null || echo $(($(date +%s) * 1000)))

    local output exit_code=0
    output=$(env "${CASS_ENV[@]}" "$CASS_BIN" \
        --db "${DB_PATH}" search "$query" \
        --robot --data-dir "${DATA_DIR}" \
        "${extra_args[@]}" 2>&1) || exit_code=$?

    end_time=$(date +%s%3N 2>/dev/null || echo $(($(date +%s) * 1000)))
    duration=$((end_time - start_time))

    if [[ $exit_code -eq 0 ]]; then
        ((passed++)) || true
        e2e_test_pass "$test_name" "$SUITE" "$duration"
        e2e_info "PASS: $test_name (${duration}ms, query='$query')" "test_$test_name"
    else
        ((failed++)) || true
        local err_msg
        err_msg=$(echo "$output" | tail -3 | tr '\n' ' ')
        e2e_test_fail "$test_name" "$SUITE" "$duration" 0 \
            "Query failed (exit=$exit_code): $err_msg" "QueryError"
        e2e_error "FAIL: $test_name — query='$query' exit=$exit_code" "test_$test_name"
    fi
}

# Run a query with --dry-run and assert the parsed query_type matches.
# Usage: run_query_type_check test_name query expected_type [extra_args...]
run_query_type_check() {
    local test_name="$1"
    local query="$2"
    local expected_type="$3"
    shift 3
    local extra_args=("$@")

    ((total++)) || true
    e2e_test_start "$test_name" "$SUITE"

    local start_time end_time duration
    start_time=$(date +%s%3N 2>/dev/null || echo $(($(date +%s) * 1000)))

    local output exit_code=0
    output=$(env "${CASS_ENV[@]}" "$CASS_BIN" \
        --db "${DB_PATH}" search "$query" \
        --dry-run --data-dir "${DATA_DIR}" \
        "${extra_args[@]}" 2>&1) || exit_code=$?

    end_time=$(date +%s%3N 2>/dev/null || echo $(($(date +%s) * 1000)))
    duration=$((end_time - start_time))

    if [[ $exit_code -ne 0 ]]; then
        ((failed++)) || true
        local err_msg
        err_msg=$(echo "$output" | tail -3 | tr '\n' ' ')
        e2e_test_fail "$test_name" "$SUITE" "$duration" 0 \
            "Dry-run failed (exit=$exit_code): $err_msg" "QueryError"
        e2e_error "FAIL: $test_name — dry-run failed for query='$query'" "test_$test_name"
        return
    fi

    # Check that the expected query_type appears in the dry-run JSON output
    if echo "$output" | grep -q "\"query_type\": \"$expected_type\""; then
        ((passed++)) || true
        e2e_test_pass "$test_name" "$SUITE" "$duration"
        e2e_info "PASS: $test_name — query_type='$expected_type' (${duration}ms)" "test_$test_name"
    else
        ((failed++)) || true
        local actual_type
        actual_type=$(echo "$output" | grep -o '"query_type": "[^"]*"' | head -1)
        e2e_test_fail "$test_name" "$SUITE" "$duration" 0 \
            "Expected query_type='$expected_type', got: $actual_type" "QueryTypeError"
        e2e_error "FAIL: $test_name — expected query_type='$expected_type', got: $actual_type" "test_$test_name"
    fi
}

# Run a query with --dry-run and assert it completes successfully.
# Usage: run_query_dryrun test_name query [extra_args...]
run_query_dryrun() {
    local test_name="$1"
    local query="$2"
    shift 2
    local extra_args=("$@")

    ((total++)) || true
    e2e_test_start "$test_name" "$SUITE"

    local start_time end_time duration
    start_time=$(date +%s%3N 2>/dev/null || echo $(($(date +%s) * 1000)))

    local output exit_code=0
    output=$(env "${CASS_ENV[@]}" "$CASS_BIN" \
        --db "${DB_PATH}" search "$query" \
        --dry-run --data-dir "${DATA_DIR}" \
        "${extra_args[@]}" 2>&1) || exit_code=$?

    end_time=$(date +%s%3N 2>/dev/null || echo $(($(date +%s) * 1000)))
    duration=$((end_time - start_time))

    if [[ $exit_code -eq 0 ]]; then
        ((passed++)) || true
        e2e_test_pass "$test_name" "$SUITE" "$duration"
        e2e_info "PASS: $test_name — dry-run OK (${duration}ms)" "test_$test_name"
    else
        ((failed++)) || true
        local err_msg
        err_msg=$(echo "$output" | tail -3 | tr '\n' ' ')
        e2e_test_fail "$test_name" "$SUITE" "$duration" 0 \
            "Dry-run failed (exit=$exit_code): $err_msg" "DryRunError"
        e2e_error "FAIL: $test_name — dry-run failed for query='$query'" "test_$test_name"
    fi
}

# ─── Setup ──────────────────────────────────────────────────────────────────

e2e_phase_start "setup" "Building binary and creating test corpus"
setup_start=$(date +%s%3N 2>/dev/null || echo $(($(date +%s) * 1000)))

ensure_cass_binary
e2e_info "Using cass binary: $CASS_BIN"

# Create isolated sandbox
SANDBOX_DIR=$(mktemp -d)
trap "rm -rf '$SANDBOX_DIR'" EXIT

DATA_DIR="${SANDBOX_DIR}/cass_data"
DB_PATH="${DATA_DIR}/agent_search.db"
CODEX_HOME="${SANDBOX_DIR}/.codex"
CLAUDE_HOME="${SANDBOX_DIR}/.claude"

mkdir -p "${DATA_DIR}"
mkdir -p "${CODEX_HOME}/sessions/2024/12/01"
mkdir -p "${CLAUDE_HOME}/projects/webapp"

# Create Codex session with diverse content for query testing
cat <<'EOSESSION' > "${CODEX_HOME}/sessions/2024/12/01/query-test.jsonl"
{"type":"event_msg","timestamp":1733011200000,"payload":{"type":"user_message","message":"fix the authentication error in login module"}}
{"type":"response_item","timestamp":1733011201000,"payload":{"role":"assistant","content":"The authentication error is caused by an expired JWT token in the session middleware. Let me fix the token validation logic."}}
{"type":"event_msg","timestamp":1733011300000,"payload":{"type":"user_message","message":"now add database connection pooling for PostgreSQL"}}
{"type":"response_item","timestamp":1733011301000,"payload":{"role":"assistant","content":"I'll configure the database connection pool using sqlx with PostgreSQL. Setting max_connections=10 and idle_timeout=300s."}}
{"type":"event_msg","timestamp":1733011400000,"payload":{"type":"user_message","message":"write unit tests for the user registration endpoint"}}
{"type":"response_item","timestamp":1733011401000,"payload":{"role":"assistant","content":"Here are comprehensive unit tests for the /api/users/register endpoint covering valid input, duplicate email, weak password, and missing required fields."}}
EOSESSION

# Create Claude session with different content
cat <<'EOSESSION' > "${CLAUDE_HOME}/projects/webapp/session.jsonl"
{"type":"user","timestamp":"2024-12-01T10:00:00Z","message":{"role":"user","content":"refactor the React component to use TypeScript generics"}}
{"type":"assistant","timestamp":"2024-12-01T10:01:00Z","message":{"role":"assistant","content":"I'll convert the component props to use TypeScript generics for better type safety. The interface will be generic over the data type parameter."}}
{"type":"user","timestamp":"2024-12-01T10:05:00Z","message":{"role":"user","content":"deploy to production using Docker and Kubernetes"}}
{"type":"assistant","timestamp":"2024-12-01T10:06:00Z","message":{"role":"assistant","content":"Creating a multi-stage Dockerfile and Kubernetes deployment manifest with health checks, resource limits, and rolling update strategy."}}
EOSESSION

# Set up environment for cass commands
CASS_ENV=(
    "HOME=${SANDBOX_DIR}"
    "CODEX_HOME=${CODEX_HOME}"
    "CASS_DATA_DIR=${DATA_DIR}"
    "CASS_DB_PATH=${DB_PATH}"
    "CODING_AGENT_SEARCH_NO_UPDATE_PROMPT=1"
    "NO_COLOR=1"
    "CASS_NO_COLOR=1"
)

# Index the test corpus
e2e_info "Indexing test corpus..."
index_output=$(env "${CASS_ENV[@]}" "$CASS_BIN" \
    --db "${DB_PATH}" index --full --json --data-dir "${DATA_DIR}" 2>&1) || {
    e2e_error "Failed to index test corpus: $index_output"
    exit 1
}
e2e_info "Index complete"

setup_end=$(date +%s%3N 2>/dev/null || echo $(($(date +%s) * 1000)))
e2e_phase_end "setup" $((setup_end - setup_start))

# ─── Test Category 1: Simple Keyword Queries ────────────────────────────────

e2e_phase_start "simple_queries" "Testing simple keyword queries"
phase_start=$(date +%s%3N 2>/dev/null || echo $(($(date +%s) * 1000)))

run_query_ok "simple_single_word" "authentication"
run_query_ok "simple_common_term" "database"
run_query_ok "simple_case_insensitive" "PostgreSQL"
run_query_ok "simple_no_results" "xyznonexistentterm42"

phase_end=$(date +%s%3N 2>/dev/null || echo $(($(date +%s) * 1000)))
e2e_phase_end "simple_queries" $((phase_end - phase_start))

# ─── Test Category 2: Phrase Queries ────────────────────────────────────────

e2e_phase_start "phrase_queries" "Testing quoted phrase queries"
phase_start=$(date +%s%3N 2>/dev/null || echo $(($(date +%s) * 1000)))

run_query_ok "phrase_exact_match" '"authentication error"'
run_query_ok "phrase_multi_word" '"connection pooling"'
run_query_ok "phrase_no_match" '"nonexistent exact phrase here"'

phase_end=$(date +%s%3N 2>/dev/null || echo $(($(date +%s) * 1000)))
e2e_phase_end "phrase_queries" $((phase_end - phase_start))

# ─── Test Category 3: Boolean Queries ───────────────────────────────────────

e2e_phase_start "boolean_queries" "Testing boolean operator queries"
phase_start=$(date +%s%3N 2>/dev/null || echo $(($(date +%s) * 1000)))

run_query_ok "boolean_and" "authentication AND error"
run_query_ok "boolean_or" "Docker OR Kubernetes"
run_query_ok "boolean_not" "database NOT PostgreSQL"
run_query_ok "boolean_complex" "(authentication OR database) AND error"

phase_end=$(date +%s%3N 2>/dev/null || echo $(($(date +%s) * 1000)))
e2e_phase_end "boolean_queries" $((phase_end - phase_start))

# ─── Test Category 4: Wildcard Queries ──────────────────────────────────────

e2e_phase_start "wildcard_queries" "Testing wildcard prefix/suffix queries"
phase_start=$(date +%s%3N 2>/dev/null || echo $(($(date +%s) * 1000)))

run_query_ok "wildcard_prefix" "auth*"
run_query_ok "wildcard_suffix" "*pool"
run_query_ok "wildcard_middle" "*connect*"

phase_end=$(date +%s%3N 2>/dev/null || echo $(($(date +%s) * 1000)))
e2e_phase_end "wildcard_queries" $((phase_end - phase_start))

# ─── Test Category 5: Filtered Queries ──────────────────────────────────────

e2e_phase_start "filtered_queries" "Testing queries with filters"
phase_start=$(date +%s%3N 2>/dev/null || echo $(($(date +%s) * 1000)))

run_query_ok "filter_with_limit" "database" --limit 1
run_query_ok "filter_with_days" "authentication" --days 365
run_query_ok "filter_with_agent" "database" --agent codex
run_query_ok "filter_with_since" "authentication" --since "2024-01-01"
run_query_ok "filter_combined" "database" --limit 5 --days 365

phase_end=$(date +%s%3N 2>/dev/null || echo $(($(date +%s) * 1000)))
e2e_phase_end "filtered_queries" $((phase_end - phase_start))

# ─── Test Category 6: Explain + Dry-Run Verification ────────────────────────

e2e_phase_start "explain_dryrun" "Testing --explain and --dry-run modes"
phase_start=$(date +%s%3N 2>/dev/null || echo $(($(date +%s) * 1000)))

run_query_type_check "typecheck_simple" "authentication" "simple"
run_query_type_check "typecheck_phrase" '"exact match"' "phrase"
run_query_type_check "typecheck_boolean" "foo AND bar" "boolean"
run_query_type_check "typecheck_wildcard" "auth*" "wildcard"

run_query_dryrun "dryrun_simple" "authentication"
run_query_dryrun "dryrun_phrase" '"connection pooling"'
run_query_dryrun "dryrun_boolean" "Docker AND Kubernetes"

phase_end=$(date +%s%3N 2>/dev/null || echo $(($(date +%s) * 1000)))
e2e_phase_end "explain_dryrun" $((phase_end - phase_start))

# ─── Test Category 7: Special Characters ────────────────────────────────────

e2e_phase_start "special_chars" "Testing queries with special characters"
phase_start=$(date +%s%3N 2>/dev/null || echo $(($(date +%s) * 1000)))

run_query_ok "special_hyphen" "multi-stage"
run_query_ok "special_slash" "api/users/register"
run_query_ok "special_underscore" "idle_timeout"
run_query_ok "special_at_sign" "user@example"
run_query_ok "special_dot_notation" "sqlx.pool"

phase_end=$(date +%s%3N 2>/dev/null || echo $(($(date +%s) * 1000)))
e2e_phase_end "special_chars" $((phase_end - phase_start))

# ─── Test Category 8: Edge Cases ────────────────────────────────────────────

e2e_phase_start "edge_cases" "Testing query edge cases"
phase_start=$(date +%s%3N 2>/dev/null || echo $(($(date +%s) * 1000)))

# Very long query (100+ characters)
long_query="authentication error database connection pooling PostgreSQL Docker Kubernetes TypeScript React deployment production login module session middleware"
run_query_ok "edge_long_query" "$long_query"

# Single character query
run_query_ok "edge_single_char" "a"

# Numeric query
run_query_ok "edge_numeric" "10"

# Query with extra whitespace
run_query_ok "edge_extra_whitespace" "  authentication   error  "

# Output format variants
run_query_ok "format_json" "authentication" --robot-format json
run_query_ok "format_jsonl" "authentication" --robot-format jsonl

phase_end=$(date +%s%3N 2>/dev/null || echo $(($(date +%s) * 1000)))
e2e_phase_end "edge_cases" $((phase_end - phase_start))

# ─── Audit ──────────────────────────────────────────────────────────────────

e2e_phase_start "audit" "Auditing test results"
phase_start=$(date +%s%3N 2>/dev/null || echo $(($(date +%s) * 1000)))

e2e_info "Test results: total=$total passed=$passed failed=$failed skipped=$skipped"
e2e_info "Output file: $(e2e_output_file)"

phase_end=$(date +%s%3N 2>/dev/null || echo $(($(date +%s) * 1000)))
e2e_phase_end "audit" $((phase_end - phase_start))

# ─── Summary ────────────────────────────────────────────────────────────────

total_duration=$(e2e_duration_since_start)
e2e_run_end "$total" "$passed" "$failed" "$skipped" "$total_duration"

if [[ $failed -gt 0 ]]; then
    echo ""
    echo "QUERY PARSER TEST FAILURE: $failed test(s) failed!"
    echo "See $(e2e_output_file) for details."
    exit 1
fi

echo ""
echo "All $total query parser tests passed ($passed/$total)."
echo "JSONL log: $(e2e_output_file)"
exit 0
