#!/usr/bin/env bash
# scripts/e2e/connector_stress.sh
#
# E2E stress test for connector resilience to malformed session data.
# Validates that `cass index --full` handles corrupted, truncated, empty,
# malformed, and large session files gracefully without crashing.
#
# Usage: ./scripts/e2e/connector_stress.sh
#
# Part of br-2l5g: Create connector_stress.sh E2E Script

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Source the E2E logging library
source "${PROJECT_ROOT}/scripts/lib/e2e_log.sh"

# Initialize logging
e2e_init "shell" "connector_stress"
e2e_run_start

# ─── Counters ───────────────────────────────────────────────────────────────
total=0
passed=0
failed=0
skipped=0
SUITE="connector_stress"

# ─── Globals ────────────────────────────────────────────────────────────────
CASS_BIN="${PROJECT_ROOT}/target/debug/cass"
stress_ok=true

CONNECTORS=(claude codex gemini cline amp aider opencode pi_agent factory cursor)
SCENARIOS=(truncated invalid_utf8 empty malformed large)

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

# ─── Format Mapping ────────────────────────────────────────────────────────
# Returns the data format category for each connector.
get_format() {
    case "$1" in
        claude|codex|pi_agent|factory) echo "jsonl" ;;
        gemini|cline|amp|opencode)     echo "json" ;;
        aider)                          echo "md" ;;
        cursor)                         echo "bin" ;;
    esac
}

# ─── Fixture Path Mapping ──────────────────────────────────────────────────
# Returns the filesystem path where a connector expects its session file.
fixture_path_for() {
    local connector="$1" home="$2" codex="$3" gemini="$4"
    local xdg="$5" aider="$6" opencode="$7" pi="$8"
    case "$connector" in
        claude)   echo "$home/.claude/projects/stress-project/session-stress.jsonl" ;;
        codex)    echo "$codex/sessions/2024/11/20/rollout-stress.jsonl" ;;
        gemini)   echo "$gemini/tmp/stresshash/chats/session-stress.json" ;;
        cline)    echo "$home/.config/Code/User/globalStorage/saoudrizwan.claude-dev/task_stress/ui_messages.json" ;;
        amp)      echo "$xdg/amp/cache/thread_stress.json" ;;
        aider)    echo "$aider/.aider.chat.history.md" ;;
        opencode) echo "$opencode/session/stress-proj/stress-session.json" ;;
        pi_agent) echo "$pi/sessions/--stress-workspace--/2024-01-15T10-30-00-000Z_00000000-0000-0000-0000-000000000000.jsonl" ;;
        factory)  echo "$home/.factory/sessions/-stress-workspace/stress-session.jsonl" ;;
        cursor)   echo "$home/.config/Cursor/User/globalStorage/state.vscdb" ;;
    esac
}

# ─── Content Writers ────────────────────────────────────────────────────────
# Write scenario-specific content directly to the target file.
# Arguments: $1=format, $2=scenario, $3=filepath

write_content() {
    local format="$1" scenario="$2" filepath="$3"
    mkdir -p "$(dirname "$filepath")"

    case "$scenario" in
        truncated) _write_truncated "$format" "$filepath" ;;
        invalid_utf8) _write_invalid_utf8 "$format" "$filepath" ;;
        empty) : > "$filepath" ;;
        malformed) _write_malformed "$format" "$filepath" ;;
        large) _write_large "$format" "$filepath" ;;
    esac

    # Cline needs a metadata file alongside ui_messages.json
    if [[ "$filepath" == *"/ui_messages.json" ]]; then
        echo '{"id":"task_stress","title":"Stress Test"}' \
            > "$(dirname "$filepath")/task_metadata.json"
    fi
}

_write_truncated() {
    local format="$1" filepath="$2"
    case "$format" in
        jsonl) printf '{"type":"user","timestamp":"2024-01-01T00:00:00Z","message":{"role":"us' > "$filepath" ;;
        json)  printf '{"messages":[{"role":"user","content":"trunc' > "$filepath" ;;
        md)    printf '# aider chat started at 2024-01-01 00:00:00\n\n#### trunc' > "$filepath" ;;
        bin)   printf 'SQLite format 3\000' > "$filepath" ;;
    esac
}

_write_invalid_utf8() {
    local format="$1" filepath="$2"
    case "$format" in
        jsonl) printf '{"type":"user","timestamp":"2024-01-01T00:00:00Z","message":{"role":"user","content":"bad \xff\xfe bytes"}}\n' > "$filepath" ;;
        json)  printf '{"messages":[{"role":"user","content":"bad \xff\xfe bytes"}]}' > "$filepath" ;;
        md)    printf '# aider chat\n\n#### bad \xff\xfe bytes\n\nresponse\n' > "$filepath" ;;
        bin)   head -c 512 /dev/urandom > "$filepath" ;;
    esac
}

_write_malformed() {
    local format="$1" filepath="$2"
    case "$format" in
        jsonl) printf 'this is not json at all\n{broken: json, here\n[[[invalid\n' > "$filepath" ;;
        json)  printf '{{{not valid json at all!!!' > "$filepath" ;;
        md)    printf '\x00\x01\x02\x03binary garbage in markdown file' > "$filepath" ;;
        bin)   printf 'definitely not a sqlite database' > "$filepath" ;;
    esac
}

_write_large() {
    local format="$1" filepath="$2"
    case "$format" in
        jsonl)
            {
                for i in $(seq 1 500); do
                    printf '{"type":"user","timestamp":"2024-01-01T00:00:00Z","message":{"role":"user","content":"large entry %d with padding text to increase file size aaaaaaaaaa"}}\n' "$i"
                done
            } > "$filepath" ;;
        json)
            {
                printf '{"messages":['
                for i in $(seq 1 500); do
                    [[ $i -gt 1 ]] && printf ','
                    printf '{"role":"user","content":"large entry %d with padding text to increase file size aaaaaaaaaa"}' "$i"
                done
                printf ']}'
            } > "$filepath" ;;
        md)
            {
                printf '# aider chat started at 2024-01-01 00:00:00\n\n'
                for i in $(seq 1 500); do
                    printf '#### large entry %d with padding text\n\nresponse %d with more padding text\n\n' "$i" "$i"
                done
            } > "$filepath" ;;
        bin)
            # ~1MB binary file with SQLite header prefix
            {
                printf 'SQLite format 3\000'
                dd if=/dev/zero bs=1024 count=1024 2>/dev/null
            } > "$filepath" ;;
    esac
}

# ─── Test Runner ────────────────────────────────────────────────────────────
# Runs a single stress test: creates isolated env, indexes malformed data,
# verifies no crash (exit code < 128).

run_stress_test() {
    local connector="$1" scenario="$2"
    local test_name="${scenario}_${connector}"

    local td
    td=$(mktemp -d)
    trap "rm -rf '$td'" RETURN

    # Create isolated directory structure
    local home="$td/home" codex="$td/codex" gemini="$td/gemini"
    local xdg="$td/xdg" aider="$td/aider" opencode="$td/opencode"
    local pi="$td/pi" data="$td/data"
    mkdir -p "$home" "$codex" "$gemini" "$xdg" "$aider" "$opencode" "$pi" "$data"

    # Create the malformed fixture
    local format filepath
    format=$(get_format "$connector")
    filepath=$(fixture_path_for "$connector" "$home" "$codex" "$gemini" "$xdg" "$aider" "$opencode" "$pi")
    write_content "$format" "$scenario" "$filepath"

    local start_time
    start_time=$(date +%s%3N 2>/dev/null || echo $(($(date +%s) * 1000)))

    # Run cass index with all connector env vars pointing at isolated dirs
    local exit_code=0
    env HOME="$home" \
        CODEX_HOME="$codex" \
        GEMINI_HOME="$gemini" \
        XDG_DATA_HOME="$xdg" \
        CASS_AIDER_DATA_ROOT="$aider" \
        OPENCODE_STORAGE_ROOT="$opencode" \
        PI_CODING_AGENT_DIR="$pi" \
        "$CASS_BIN" index --full --data-dir "$data" >/dev/null 2>&1 || exit_code=$?

    local end_time duration
    end_time=$(date +%s%3N 2>/dev/null || echo $(($(date +%s) * 1000)))
    duration=$((end_time - start_time))

    ((total++)) || true
    e2e_test_start "$test_name" "$SUITE"

    # Exit code < 128 means no signal-based crash (0=ok, 1=handled error, etc.)
    if [[ $exit_code -lt 128 ]]; then
        ((passed++)) || true
        e2e_test_pass "$test_name" "$SUITE" "$duration"
        e2e_info "PASS: $connector/$scenario (exit=$exit_code, ${duration}ms)" "test_$test_name"
        return 0
    else
        ((failed++)) || true
        local signal=$((exit_code - 128))
        e2e_test_fail "$test_name" "$SUITE" "$duration" 0 \
            "Crashed (signal $signal) on $scenario input" "CrashFailure"
        e2e_error "FAIL: $connector/$scenario crashed with signal $signal" "test_$test_name"
        return 1
    fi
}

# ─── Combined Stress Test ─────────────────────────────────────────────────
# Tests all connectors simultaneously with mixed malformed data, then
# verifies that search still works after indexing corrupted files.

run_combined_stress_test() {
    local td
    td=$(mktemp -d)
    trap "rm -rf '$td'" RETURN

    local home="$td/home" codex="$td/codex" gemini="$td/gemini"
    local xdg="$td/xdg" aider="$td/aider" opencode="$td/opencode"
    local pi="$td/pi" data="$td/data"
    mkdir -p "$home" "$codex" "$gemini" "$xdg" "$aider" "$opencode" "$pi" "$data"

    # Create mixed malformed fixtures (different scenarios per connector)
    local fp
    fp=$(fixture_path_for "claude" "$home" "$codex" "$gemini" "$xdg" "$aider" "$opencode" "$pi")
    write_content "jsonl" "truncated" "$fp"

    fp=$(fixture_path_for "codex" "$home" "$codex" "$gemini" "$xdg" "$aider" "$opencode" "$pi")
    write_content "jsonl" "invalid_utf8" "$fp"

    fp=$(fixture_path_for "gemini" "$home" "$codex" "$gemini" "$xdg" "$aider" "$opencode" "$pi")
    write_content "json" "malformed" "$fp"

    fp=$(fixture_path_for "cline" "$home" "$codex" "$gemini" "$xdg" "$aider" "$opencode" "$pi")
    write_content "json" "empty" "$fp"

    fp=$(fixture_path_for "amp" "$home" "$codex" "$gemini" "$xdg" "$aider" "$opencode" "$pi")
    write_content "json" "truncated" "$fp"

    fp=$(fixture_path_for "aider" "$home" "$codex" "$gemini" "$xdg" "$aider" "$opencode" "$pi")
    write_content "md" "invalid_utf8" "$fp"

    fp=$(fixture_path_for "opencode" "$home" "$codex" "$gemini" "$xdg" "$aider" "$opencode" "$pi")
    write_content "json" "malformed" "$fp"

    fp=$(fixture_path_for "pi_agent" "$home" "$codex" "$gemini" "$xdg" "$aider" "$opencode" "$pi")
    write_content "jsonl" "empty" "$fp"

    fp=$(fixture_path_for "factory" "$home" "$codex" "$gemini" "$xdg" "$aider" "$opencode" "$pi")
    write_content "jsonl" "truncated" "$fp"

    fp=$(fixture_path_for "cursor" "$home" "$codex" "$gemini" "$xdg" "$aider" "$opencode" "$pi")
    write_content "bin" "malformed" "$fp"

    # Test: index with all connectors having malformed data
    local start_time
    start_time=$(date +%s%3N 2>/dev/null || echo $(($(date +%s) * 1000)))

    local exit_code=0
    env HOME="$home" \
        CODEX_HOME="$codex" \
        GEMINI_HOME="$gemini" \
        XDG_DATA_HOME="$xdg" \
        CASS_AIDER_DATA_ROOT="$aider" \
        OPENCODE_STORAGE_ROOT="$opencode" \
        PI_CODING_AGENT_DIR="$pi" \
        "$CASS_BIN" index --full --data-dir "$data" >/dev/null 2>&1 || exit_code=$?

    local end_time duration
    end_time=$(date +%s%3N 2>/dev/null || echo $(($(date +%s) * 1000)))
    duration=$((end_time - start_time))

    ((total++)) || true
    e2e_test_start "combined_all_connectors" "$SUITE"

    if [[ $exit_code -lt 128 ]]; then
        ((passed++)) || true
        e2e_test_pass "combined_all_connectors" "$SUITE" "$duration"
        e2e_info "PASS: Combined stress (exit=$exit_code, ${duration}ms)" "test_combined"
    else
        ((failed++)) || true
        e2e_test_fail "combined_all_connectors" "$SUITE" "$duration" 0 \
            "Combined stress crashed (signal $((exit_code-128)))" "CrashFailure"
        e2e_error "FAIL: Combined stress crashed" "test_combined"
        return 1
    fi

    # Test: search integrity after indexing malformed data
    local search_exit=0
    env HOME="$home" \
        XDG_DATA_HOME="$xdg" \
        "$CASS_BIN" search "test" --robot --data-dir "$data" >/dev/null 2>&1 || search_exit=$?

    ((total++)) || true
    e2e_test_start "combined_search_integrity" "$SUITE"

    if [[ $search_exit -lt 128 ]]; then
        ((passed++)) || true
        e2e_test_pass "combined_search_integrity" "$SUITE" "0"
        e2e_info "PASS: Search intact after malformed index" "test_combined_search"
    else
        ((failed++)) || true
        e2e_test_fail "combined_search_integrity" "$SUITE" "0" 0 \
            "Search crashed after indexing malformed data" "CrashFailure"
        e2e_error "FAIL: Search crashed after malformed index" "test_combined_search"
        return 1
    fi

    return 0
}

# ─── Main ───────────────────────────────────────────────────────────────────

e2e_phase_start "setup" "Building binary and preparing test environment"
setup_start=$(date +%s%3N 2>/dev/null || echo $(($(date +%s) * 1000)))
ensure_cass_binary
e2e_info "Using cass binary: $CASS_BIN"
e2e_info "Connectors: ${CONNECTORS[*]}"
e2e_info "Scenarios: ${SCENARIOS[*]}"
setup_end=$(date +%s%3N 2>/dev/null || echo $(($(date +%s) * 1000)))
e2e_phase_end "setup" $((setup_end - setup_start))

# ─── Per-scenario phases ────────────────────────────────────────────────────

for scenario in "${SCENARIOS[@]}"; do
    e2e_phase_start "$scenario" "Testing $scenario scenario across all connectors"
    phase_start=$(date +%s%3N 2>/dev/null || echo $(($(date +%s) * 1000)))

    for connector in "${CONNECTORS[@]}"; do
        run_stress_test "$connector" "$scenario" || stress_ok=false
    done

    phase_end=$(date +%s%3N 2>/dev/null || echo $(($(date +%s) * 1000)))
    e2e_phase_end "$scenario" $((phase_end - phase_start))
done

# ─── Combined stress test ──────────────────────────────────────────────────

e2e_phase_start "combined" "All connectors with mixed malformed data simultaneously"
phase_start=$(date +%s%3N 2>/dev/null || echo $(($(date +%s) * 1000)))
run_combined_stress_test || stress_ok=false
phase_end=$(date +%s%3N 2>/dev/null || echo $(($(date +%s) * 1000)))
e2e_phase_end "combined" $((phase_end - phase_start))

# ─── Summary ────────────────────────────────────────────────────────────────

total_duration=$(e2e_duration_since_start)
e2e_run_end "$total" "$passed" "$failed" "$skipped" "$total_duration"

if [[ "$stress_ok" != "true" ]]; then
    echo ""
    echo "STRESS TEST FAILURE: $failed test(s) detected crashes!"
    echo "See $(e2e_output_file) for details."
    exit 1
fi

echo ""
echo "All $total connector stress tests passed ($passed/$total)."
echo "JSONL log: $(e2e_output_file)"
exit 0
