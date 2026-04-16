#!/bin/bash
set -e

# TypeScript Type Check Script
# Runs TypeScript compiler for type checking with enhanced output

PROJECT_DIR="${1:-.}"
STRICT_MODE="${2:-true}"

cd "$PROJECT_DIR"

echo "Running TypeScript type check in: $(pwd)" >&2

cleanup() {
    echo "Type check completed" >&2
}
trap cleanup EXIT

show_usage() {
    cat << 'EOF'
Usage: type-check.sh [project-dir] [strict-mode]

Arguments:
  project-dir  Project directory (default: current directory)
  strict-mode  Enable strict checks: true/false (default: true)

Examples:
  type-check.sh
  type-check.sh ./my-project
  type-check.sh ./my-project false

Checks:
  - TypeScript compilation (noEmit)
  - Strict type checking
  - Unused variables/imports
  - Type coverage estimation

Requirements:
  - TypeScript installed (npx tsc or global tsc)
EOF
}

# Check for tsconfig.json
if [ ! -f "tsconfig.json" ]; then
    echo '{"success": false, "error": "tsconfig.json not found"}'
    exit 1
fi

RESULTS=()
ERRORS=0
WARNINGS=0
TOTAL_ERRORS=0

# Determine tsc command
if command -v tsc &> /dev/null; then
    TSC_CMD="tsc"
elif [ -f "node_modules/.bin/tsc" ]; then
    TSC_CMD="node_modules/.bin/tsc"
else
    TSC_CMD="npx tsc"
fi

echo "Using: $TSC_CMD" >&2

# 1. Basic type check
echo "Running type check..." >&2
TYPE_OUTPUT=$($TSC_CMD --noEmit 2>&1 || true)

if [ -z "$TYPE_OUTPUT" ]; then
    RESULTS+=('{"check": "tsc --noEmit", "status": "pass", "errors": 0}')
    echo "tsc --noEmit: PASS" >&2
else
    ERROR_COUNT=$(echo "$TYPE_OUTPUT" | grep -c "error TS" || echo "0")
    TOTAL_ERRORS=$ERROR_COUNT
    RESULTS+=('{"check": "tsc --noEmit", "status": "fail", "errors": '"$ERROR_COUNT"'}')
    echo "tsc --noEmit: FAIL ($ERROR_COUNT errors)" >&2
    ((ERRORS++))
fi

# 2. Strict mode check (if enabled and not already in tsconfig)
if [ "$STRICT_MODE" = "true" ]; then
    echo "Running strict mode check..." >&2
    STRICT_OUTPUT=$($TSC_CMD --noEmit --strict 2>&1 || true)
    STRICT_ERRORS=$(echo "$STRICT_OUTPUT" | grep -c "error TS" || echo "0")

    if [ "$STRICT_ERRORS" = "0" ]; then
        RESULTS+=('{"check": "strict mode", "status": "pass"}')
        echo "strict mode: PASS" >&2
    else
        # Calculate additional errors from strict mode
        ADDITIONAL=$((STRICT_ERRORS - TOTAL_ERRORS))
        if [ $ADDITIONAL -gt 0 ]; then
            RESULTS+=('{"check": "strict mode", "status": "warning", "additional_errors": '"$ADDITIONAL"'}')
            echo "strict mode: WARNING (+$ADDITIONAL errors with strict)" >&2
            ((WARNINGS++))
        else
            RESULTS+=('{"check": "strict mode", "status": "pass"}')
            echo "strict mode: PASS" >&2
        fi
    fi
fi

# 3. Check for unused variables
echo "Checking for unused code..." >&2
UNUSED_OUTPUT=$($TSC_CMD --noEmit --noUnusedLocals --noUnusedParameters 2>&1 || true)
UNUSED_ERRORS=$(echo "$UNUSED_OUTPUT" | grep -c "error TS" || echo "0")
UNUSED_ADDITIONAL=$((UNUSED_ERRORS - TOTAL_ERRORS))

if [ $UNUSED_ADDITIONAL -le 0 ]; then
    RESULTS+=('{"check": "unused code", "status": "pass"}')
    echo "unused code: PASS" >&2
else
    RESULTS+=('{"check": "unused code", "status": "warning", "unused": '"$UNUSED_ADDITIONAL"'}')
    echo "unused code: WARNING ($UNUSED_ADDITIONAL unused)" >&2
    ((WARNINGS++))
fi

# 4. Check tsconfig settings
echo "Checking tsconfig.json settings..." >&2
TSCONFIG_ISSUES=0

# Check for recommended settings
if ! grep -q '"strict":\s*true' tsconfig.json 2>/dev/null; then
    echo "  INFO: 'strict' is not enabled" >&2
fi

if ! grep -q '"noUncheckedIndexedAccess":\s*true' tsconfig.json 2>/dev/null; then
    echo "  INFO: 'noUncheckedIndexedAccess' is not enabled" >&2
    ((TSCONFIG_ISSUES++))
fi

if [ $TSCONFIG_ISSUES -eq 0 ]; then
    RESULTS+=('{"check": "tsconfig", "status": "pass"}')
else
    RESULTS+=('{"check": "tsconfig", "status": "info", "suggestions": '"$TSCONFIG_ISSUES"'}')
fi

# 5. Count TypeScript files
TS_FILES=$(find . -name "*.ts" -o -name "*.tsx" 2>/dev/null | grep -v node_modules | wc -l | tr -d ' ')
echo "TypeScript files: $TS_FILES" >&2

# Output results
RESULTS_JSON=$(printf '%s\n' "${RESULTS[@]}" | paste -sd, -)
TS_VERSION=$($TSC_CMD --version 2>/dev/null | grep -o '[0-9]\+\.[0-9]\+\.[0-9]\+' || echo "unknown")

if [ $ERRORS -eq 0 ]; then
    echo '{"success": true, "typescript_version": "'"$TS_VERSION"'", "files": '"$TS_FILES"', "errors": '"$TOTAL_ERRORS"', "warnings": '"$WARNINGS"', "results": ['"$RESULTS_JSON"']}'
else
    # Include error details
    ERROR_SAMPLE=$(echo "$TYPE_OUTPUT" | head -10 | tr '\n' ' ' | sed 's/"/\\"/g')
    echo '{"success": false, "typescript_version": "'"$TS_VERSION"'", "files": '"$TS_FILES"', "errors": '"$TOTAL_ERRORS"', "warnings": '"$WARNINGS"', "error_sample": "'"$ERROR_SAMPLE"'", "results": ['"$RESULTS_JSON"']}'
fi
