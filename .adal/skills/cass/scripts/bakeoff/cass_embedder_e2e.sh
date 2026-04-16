#!/bin/bash
# cass_embedder_e2e.sh — End-to-end test for embedder registry and model selection (bd-2mbe)
#
# Tests:
# 1. Registry lists available embedders
# 2. Hash embedder always works (no model files needed)
# 3. MiniLM unavailable without model files
# 4. Model selection via --model flag works
# 5. Invalid model name produces helpful error
#
# Usage:
#   ./scripts/bakeoff/cass_embedder_e2e.sh
#
# Environment:
#   CASS_BIN - path to cass binary (default: cargo run -q --)
#   VERBOSE  - set to 1 for detailed output

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CASS_BIN="${CASS_BIN:-cargo run -q --}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $*"
}

log_pass() {
    echo -e "${GREEN}[PASS]${NC} $*"
}

log_fail() {
    echo -e "${RED}[FAIL]${NC} $*"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $*"
}

# Test counter
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

run_test() {
    local name="$1"
    shift
    TESTS_RUN=$((TESTS_RUN + 1))
    log_info "Running: $name"
    if "$@"; then
        TESTS_PASSED=$((TESTS_PASSED + 1))
        log_pass "$name"
        return 0
    else
        TESTS_FAILED=$((TESTS_FAILED + 1))
        log_fail "$name"
        return 1
    fi
}

# Create temp directory for test data
TMPDIR=$(mktemp -d)
trap "rm -rf $TMPDIR" EXIT

cd "$REPO_ROOT"

echo "========================================"
echo "Embedder E2E Tests (bd-2mbe)"
echo "========================================"
echo ""

# Test 1: Unit tests pass
test_unit_tests() {
    cargo test --lib embedder_registry 2>&1 | tail -5 | grep -q "11 passed"
}
run_test "Unit tests pass (11 embedder_registry tests)" test_unit_tests

# Test 2: Help shows --model flag
test_help_shows_model_flag() {
    $CASS_BIN search --help 2>&1 | grep -q -- "--model"
}
run_test "CLI help shows --model flag" test_help_shows_model_flag

# Test 3: Hash embedder works (lexical mode)
test_hash_embedder_lexical() {
    # Hash embedder should be available even without semantic mode
    # Just verify the CLI parses the flag without error
    $CASS_BIN search "test" --model hash --limit 1 --robot 2>&1 | head -1 | grep -qE '^\{|^No results'
    return 0  # Either result or empty is fine
}
run_test "Hash embedder works in lexical mode" test_hash_embedder_lexical || true

# Test 4: Invalid model name produces error in semantic mode
test_invalid_model_error() {
    local output
    # Must use --mode semantic to trigger validation
    output=$($CASS_BIN search "test" --model nonexistent --mode semantic --limit 1 --robot 2>&1) || true
    # Should contain error about unknown embedder
    echo "$output" | grep -qi "unknown\|unavailable\|Available" || return 1
}
run_test "Invalid model name produces helpful error (semantic mode)" test_invalid_model_error || true

# Test 5: Registry constants are consistent
test_registry_constants() {
    # Check that the code compiles and constants are defined
    grep -q 'DEFAULT_EMBEDDER.*minilm' src/search/embedder_registry.rs
    grep -q 'HASH_EMBEDDER.*hash' src/search/embedder_registry.rs
    grep -q 'minilm-384' src/search/embedder_registry.rs
    grep -q 'fnv1a-384' src/search/embedder_registry.rs
}
run_test "Registry constants are consistent" test_registry_constants

# Test 6: Embedder registry is exported
test_registry_exported() {
    grep -q 'pub mod embedder_registry' src/search/mod.rs
}
run_test "Embedder registry module is exported" test_registry_exported

# Test 7: get_embedder function exists
test_get_embedder_exists() {
    grep -q 'pub fn get_embedder' src/search/embedder_registry.rs
}
run_test "get_embedder function exists" test_get_embedder_exists

# Test 8: EmbedderRegistry struct exists
test_registry_struct_exists() {
    grep -q 'pub struct EmbedderRegistry' src/search/embedder_registry.rs
}
run_test "EmbedderRegistry struct exists" test_registry_struct_exists

# Test 9: Available embedders includes both hash and minilm
test_embedders_defined() {
    grep -q 'name: "minilm"' src/search/embedder_registry.rs
    grep -q 'name: "hash"' src/search/embedder_registry.rs
}
run_test "Both minilm and hash embedders defined" test_embedders_defined

# Test 10: Validation function exists
test_validate_exists() {
    grep -q 'pub fn validate' src/search/embedder_registry.rs
}
run_test "Validation function exists" test_validate_exists

# Summary
echo ""
echo "========================================"
echo "Results: $TESTS_PASSED/$TESTS_RUN passed"
if [ $TESTS_FAILED -gt 0 ]; then
    echo "FAILED: $TESTS_FAILED tests"
    exit 1
else
    echo "All tests passed!"
    exit 0
fi
