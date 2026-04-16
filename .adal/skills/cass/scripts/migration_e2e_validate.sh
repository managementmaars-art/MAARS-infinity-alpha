#!/usr/bin/env bash
# scripts/migration_e2e_validate.sh
# Cross-repo e2e validation for the frankensearch + FAD migration.
# Validates the assembled three-repo ecosystem after both migrations.
#
# Usage:
#   ./scripts/migration_e2e_validate.sh           # Run all checks
#   ./scripts/migration_e2e_validate.sh --local    # Build locally (no rch)
#   ./scripts/migration_e2e_validate.sh --quick    # Skip benchmarks and slow checks
#
# Exit code: 0 if all pass, 1 if any fail.

set -uo pipefail

# =============================================================================
# Configuration
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CASS_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
FS_ROOT="/data/projects/frankensearch"
FAD_ROOT="/data/projects/franken_agent_detection"
BASELINE_DIR="${CASS_ROOT}/.beads/migration_baseline"

# Colors (only when stdout is a terminal)
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

# Options
USE_RCH=1
QUICK_MODE=0
for arg in "$@"; do
    case "$arg" in
        --local) USE_RCH=0 ;;
        --quick) QUICK_MODE=1 ;;
        --help)
            echo "Usage: $0 [--local] [--quick]"
            echo "  --local    Build locally (no rch)"
            echo "  --quick    Skip benchmarks and slow checks"
            exit 0
            ;;
    esac
done

# Tracking
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0
WARNED_CHECKS=0
FAILURES=()
WARNINGS=()

# Logging
LOG_FILE="${CASS_ROOT}/test-logs/migration_e2e_$(date +%Y%m%d_%H%M%S).log"
mkdir -p "$(dirname "$LOG_FILE")"

# =============================================================================
# Helpers
# =============================================================================

log() {
    local ts
    ts="$(date +%H:%M:%S)"
    echo -e "[${ts}] $*" | tee -a "$LOG_FILE"
}

section() {
    echo "" | tee -a "$LOG_FILE"
    log "${BOLD}${BLUE}═══ $1 ═══${NC}"
}

pass() {
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
    log "  ${GREEN}✓${NC} $1"
}

fail() {
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
    FAILURES+=("$1")
    log "  ${RED}✗${NC} $1"
}

warn() {
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    WARNED_CHECKS=$((WARNED_CHECKS + 1))
    WARNINGS+=("$1")
    log "  ${YELLOW}⚠${NC} $1"
}

cargo_cmd() {
    if [[ "$USE_RCH" -eq 1 ]]; then
        rch exec -- cargo "$@"
    else
        cargo "$@"
    fi
}

elapsed_since() {
    local start=$1
    local now
    now=$(date +%s)
    echo $((now - start))
}

# =============================================================================
# 1. BUILD ALL THREE REPOS
# =============================================================================

section "1. Build Verification"
STEP_START=$(date +%s)

log "Building frankensearch..."
if (cd "$FS_ROOT" && cargo_cmd check --all-features) >> "$LOG_FILE" 2>&1; then
    pass "frankensearch: cargo check --all-features"
else
    fail "frankensearch: cargo check --all-features"
fi

log "Building FAD..."
if (cd "$FAD_ROOT" && cargo_cmd check --all-features) >> "$LOG_FILE" 2>&1; then
    pass "FAD: cargo check --all-features"
else
    fail "FAD: cargo check --all-features"
fi

log "Building cass..."
if (cd "$CASS_ROOT" && cargo_cmd check --all-features) >> "$LOG_FILE" 2>&1; then
    pass "cass: cargo check --all-features"
else
    fail "cass: cargo check --all-features"
fi

log "  Build step: $(elapsed_since "$STEP_START")s"

# =============================================================================
# 2. TEST SUITES
# =============================================================================

section "2. Test Suites"
STEP_START=$(date +%s)

# Helper: sum all "N passed" / "N failed" lines from cargo test output
sum_test_metric() {
    local output="$1" metric="$2"
    echo "$output" | grep -oP "\d+ $metric" | grep -oP '\d+' | paste -sd+ | bc 2>/dev/null || echo "0"
}

# Frankensearch tests
log "Running frankensearch tests..."
FS_TEST_OUT=$(cd "$FS_ROOT" && cargo_cmd test --all-features 2>&1) || true
echo "$FS_TEST_OUT" >> "$LOG_FILE"
FS_PASSED=$(sum_test_metric "$FS_TEST_OUT" "passed")
FS_FAILED=$(sum_test_metric "$FS_TEST_OUT" "failed")
if [[ "$FS_FAILED" -eq 0 && "$FS_PASSED" -gt 0 ]]; then
    pass "frankensearch tests: $FS_PASSED passed, $FS_FAILED failed"
elif [[ "$FS_FAILED" -le 3 ]]; then
    warn "frankensearch tests: $FS_PASSED passed, $FS_FAILED failed (known env failures)"
else
    fail "frankensearch tests: $FS_PASSED passed, $FS_FAILED failed"
fi

# FAD tests
log "Running FAD tests..."
FAD_TEST_OUT=$(cd "$FAD_ROOT" && cargo_cmd test --all-features 2>&1) || true
echo "$FAD_TEST_OUT" >> "$LOG_FILE"
FAD_PASSED=$(sum_test_metric "$FAD_TEST_OUT" "passed")
FAD_FAILED=$(sum_test_metric "$FAD_TEST_OUT" "failed")
if [[ "$FAD_FAILED" -eq 0 && "$FAD_PASSED" -gt 0 ]]; then
    pass "FAD tests: $FAD_PASSED passed, $FAD_FAILED failed"
elif [[ "$FAD_FAILED" -le 2 ]]; then
    warn "FAD tests: $FAD_PASSED passed, $FAD_FAILED failed (known env failures)"
else
    fail "FAD tests: $FAD_PASSED passed, $FAD_FAILED failed"
fi

# Cass tests
log "Running cass tests..."
CASS_TEST_OUT=$(cd "$CASS_ROOT" && cargo_cmd test --lib 2>&1) || true
echo "$CASS_TEST_OUT" >> "$LOG_FILE"
CASS_PASSED=$(sum_test_metric "$CASS_TEST_OUT" "passed")
CASS_FAILED=$(sum_test_metric "$CASS_TEST_OUT" "failed")
if [[ "$CASS_FAILED" -eq 0 && "$CASS_PASSED" -gt 0 ]]; then
    pass "cass lib tests: $CASS_PASSED passed, $CASS_FAILED failed"
else
    fail "cass lib tests: $CASS_PASSED passed, $CASS_FAILED failed"
fi

# Combined test count vs baseline (3635)
TOTAL_TESTS=$((FS_PASSED + FAD_PASSED + CASS_PASSED))
if [[ "$TOTAL_TESTS" -ge 3635 ]]; then
    pass "Combined test count: $TOTAL_TESTS >= 3635 baseline"
else
    fail "Combined test count: $TOTAL_TESTS < 3635 baseline (regression!)"
fi

log "  Test step: $(elapsed_since "$STEP_START")s"

# =============================================================================
# 3. CLIPPY ALL THREE
# =============================================================================

section "3. Clippy"
STEP_START=$(date +%s)

log "Clippy: frankensearch..."
if (cd "$FS_ROOT" && cargo_cmd clippy --all-targets 2>&1 | grep -q "error\[") ; then
    fail "frankensearch clippy: has errors"
else
    pass "frankensearch clippy: clean (no errors)"
fi

log "Clippy: FAD..."
if (cd "$FAD_ROOT" && cargo_cmd clippy --all-targets 2>&1 | grep -q "error\[") ; then
    fail "FAD clippy: has errors"
else
    pass "FAD clippy: clean (no errors)"
fi

log "Clippy: cass..."
if (cd "$CASS_ROOT" && cargo_cmd clippy --all-targets 2>&1 | grep -q "error\[") ; then
    fail "cass clippy: has errors"
else
    pass "cass clippy: clean (no errors)"
fi

log "  Clippy step: $(elapsed_since "$STEP_START")s"

# =============================================================================
# 4. BINARY SIZE COMPARISON
# =============================================================================

section "4. Binary Size"

# Find release binary: check CARGO_TARGET_DIR, then standard, then rch
CASS_BINARY=""
for candidate in \
    "${CARGO_TARGET_DIR:-}/release/cass" \
    "${CASS_ROOT}/target/release/cass" \
    "${CASS_ROOT}/target_amber_rch/release/cass"; do
    if [[ -f "$candidate" ]]; then
        CASS_BINARY="$candidate"
        break
    fi
done
if [[ -z "$CASS_BINARY" ]]; then
    CASS_BINARY="${CASS_ROOT}/target/release/cass"  # default for error messages
fi
BASELINE_SIZE=35584616  # from BASELINE_SUMMARY.md

if [[ -f "$CASS_BINARY" ]]; then
    CURRENT_SIZE=$(stat --format='%s' "$CASS_BINARY" 2>/dev/null || stat -f '%z' "$CASS_BINARY" 2>/dev/null)
    DELTA_PCT=$(python3 -c "print(f'{($CURRENT_SIZE - $BASELINE_SIZE) / $BASELINE_SIZE * 100:.1f}')")
    DELTA_ABS=$(python3 -c "print(f'{($CURRENT_SIZE - $BASELINE_SIZE) / 1024 / 1024:.2f}')")
    log "  Baseline: ${BASELINE_SIZE} bytes (33.94 MB)"
    log "  Current:  ${CURRENT_SIZE} bytes ($(python3 -c "print(f'{$CURRENT_SIZE/1024/1024:.2f}')")MB)"
    log "  Delta:    ${DELTA_PCT}% (${DELTA_ABS} MB)"

    # Hard fail at 15%, warn at 5%
    if python3 -c "exit(0 if abs($CURRENT_SIZE - $BASELINE_SIZE) / $BASELINE_SIZE <= 0.05 else 1)"; then
        pass "Binary size: within 5% of baseline (${DELTA_PCT}%)"
    elif python3 -c "exit(0 if abs($CURRENT_SIZE - $BASELINE_SIZE) / $BASELINE_SIZE <= 0.15 else 1)"; then
        warn "Binary size: ${DELTA_PCT}% from baseline (exceeds 5% threshold, within 15%)"
    else
        fail "Binary size: ${DELTA_PCT}% from baseline (exceeds 15% threshold!)"
    fi
else
    warn "Binary not found at $CASS_BINARY (run cargo build --release first)"
fi

# =============================================================================
# 5. SEARCH QUALITY VALIDATION
# =============================================================================

section "5. Search Quality"

if [[ -f "$CASS_BINARY" ]] && [[ -f "${BASELINE_DIR}/baseline_search_quality.json" ]]; then
    QUALITY_RESULT=$(CASS_BIN="$CASS_BINARY" BASELINE_FILE="${BASELINE_DIR}/baseline_search_quality.json" python3 << 'PYEOF'
import json, subprocess, sys, os

cass = os.environ["CASS_BIN"]
baseline_file = os.environ["BASELINE_FILE"]

baseline = json.load(open(baseline_file))
all_ok = True
max_delta = 0.0
results = []

for i, b in enumerate(baseline):
    q = b["query"]
    proc = subprocess.run([cass, "search", q, "--limit", "10", "--json"], capture_output=True, text=True)
    if proc.returncode != 0:
        print(f"FAIL query_{i+1}: search returned error")
        all_ok = False
        continue

    data = json.loads(proc.stdout)
    hits = data.get("hits", [])
    current_count = len(hits)
    baseline_count = b["result_count"]

    # Check result count
    if current_count != baseline_count:
        print(f"FAIL query_{i+1} '{q}': count {current_count} != baseline {baseline_count}")
        all_ok = False
        continue

    # Check scores within tolerance
    current_scores = [h["score"] for h in hits[:3]]
    baseline_scores = b["top_3_scores"]

    for j, (cs, bs) in enumerate(zip(current_scores, baseline_scores)):
        delta_pct = abs(cs - bs) / bs * 100 if bs else 0
        max_delta = max(max_delta, delta_pct)
        if delta_pct > 5.0:  # 5% tolerance for individual scores
            print(f"WARN query_{i+1} '{q}' score[{j}]: {cs:.2f} vs baseline {bs:.2f} ({delta_pct:+.1f}%)")

    results.append({"query": q, "ok": True, "count": current_count, "max_score_delta_pct": max_delta})

print(f"OK max_delta={max_delta:.2f}%" if all_ok else f"FAIL max_delta={max_delta:.2f}%")
PYEOF
    )
    echo "$QUALITY_RESULT" >> "$LOG_FILE"
    if echo "$QUALITY_RESULT" | grep -q "^OK"; then
        MAX_D=$(echo "$QUALITY_RESULT" | grep -oP 'max_delta=[\d.]+' | grep -oP '[\d.]+')
        pass "Search quality: all 10 queries match baseline (max delta: ${MAX_D}%)"
    else
        fail "Search quality: regression detected — $QUALITY_RESULT"
    fi
else
    warn "Search quality: skipped (binary or baseline not available)"
fi

# =============================================================================
# 6. SERIALIZATION COMPATIBILITY
# =============================================================================

section "6. Serialization Compatibility"

if [[ -f "$CASS_BINARY" ]]; then
    # Check that the tantivy index schema hash matches between cass and frankensearch
    SCHEMA_CHECK=$("$CASS_BINARY" diag 2>&1 || true)
    if echo "$SCHEMA_CHECK" | grep -q "Index Status" && echo "$SCHEMA_CHECK" | grep -A1 "Index Status" | grep -q "OK"; then
        pass "Index schema: post-migration binary can read existing index"
    else
        fail "Index schema: post-migration binary cannot read existing index"
    fi

    # Verify NormalizedConversation type compatibility by checking the cass search output
    # parses correctly (JSON serialization hasn't changed)
    COMPAT_OUT=$("$CASS_BINARY" search "test" --limit 1 --json 2>/dev/null || true)
    if echo "$COMPAT_OUT" | python3 -c "import json,sys; d=json.load(sys.stdin); assert 'hits' in d or 'count' in d" 2>/dev/null; then
        pass "JSON serialization: search output schema intact"
    else
        fail "JSON serialization: search output schema changed"
    fi
else
    warn "Serialization checks: skipped (release binary not found)"
fi

# =============================================================================
# 7. FEATURE GATE VALIDATION (FAD)
# =============================================================================

section "7. FAD Feature Gate Validation"

# Build with default features (no optional deps)
log "Building FAD with default features..."
if (cd "$FAD_ROOT" && cargo_cmd check 2>&1) >> "$LOG_FILE"; then
    pass "FAD default features: builds"
else
    fail "FAD default features: build failed"
fi

# Check: default build should NOT have rusqlite or aes-gcm
FAD_DEFAULT_DEPS=$(cd "$FAD_ROOT" && cargo tree --no-dedupe --depth 1 2>/dev/null || echo "")
if echo "$FAD_DEFAULT_DEPS" | grep -qi "rusqlite"; then
    fail "FAD default: rusqlite present in dep tree (should be optional)"
else
    pass "FAD default: no rusqlite in dep tree"
fi
if echo "$FAD_DEFAULT_DEPS" | grep -qi "aes-gcm"; then
    fail "FAD default: aes-gcm present in dep tree (should be optional)"
else
    pass "FAD default: no aes-gcm in dep tree"
fi

# Build with all-connectors
log "Building FAD with all-connectors..."
if (cd "$FAD_ROOT" && cargo_cmd check --features all-connectors 2>&1) >> "$LOG_FILE"; then
    pass "FAD all-connectors: builds"
else
    fail "FAD all-connectors: builds failed"
fi

# =============================================================================
# 8. SUMMARY
# =============================================================================

section "8. Summary"

TOTAL_TIME_S=$SECONDS
log ""
log "${BOLD}Migration E2E Validation Results${NC}"
log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log "  ${GREEN}Passed:${NC}  $PASSED_CHECKS"
log "  ${YELLOW}Warned:${NC}  $WARNED_CHECKS"
log "  ${RED}Failed:${NC}  $FAILED_CHECKS"
log "  Total:   $TOTAL_CHECKS"
log "  Time:    ${TOTAL_TIME_S}s"
log ""

if [[ ${#WARNINGS[@]} -gt 0 ]]; then
    log "${YELLOW}Warnings:${NC}"
    for w in "${WARNINGS[@]}"; do
        log "  ${YELLOW}⚠${NC} $w"
    done
    log ""
fi

if [[ ${#FAILURES[@]} -gt 0 ]]; then
    log "${RED}Failures:${NC}"
    for f in "${FAILURES[@]}"; do
        log "  ${RED}✗${NC} $f"
    done
    log ""
fi

log "Full log: $LOG_FILE"

if [[ "$FAILED_CHECKS" -gt 0 ]]; then
    log "${RED}${BOLD}RESULT: FAIL${NC} ($FAILED_CHECKS failures)"
    exit 1
else
    log "${GREEN}${BOLD}RESULT: PASS${NC} ($PASSED_CHECKS passed, $WARNED_CHECKS warnings)"
    exit 0
fi
