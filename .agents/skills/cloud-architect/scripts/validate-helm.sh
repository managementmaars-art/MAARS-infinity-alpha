#!/bin/bash
set -e

# Helm Chart Validation Script
# Validates Helm charts for syntax and best practices

CHART_PATH="${1:-.}"
VALUES_FILE="${2:-}"
KUBE_VERSION="${3:-1.28.0}"

# Input validation: CHART_PATH must be an existing directory
if [ ! -d "$CHART_PATH" ]; then
    echo "Error: Chart path '$CHART_PATH' is not a valid directory." >&2
    exit 1
fi

# Input validation: VALUES_FILE must exist if specified
if [ -n "$VALUES_FILE" ] && [ ! -f "$VALUES_FILE" ]; then
    echo "Error: Values file '$VALUES_FILE' does not exist." >&2
    exit 1
fi

# Input validation: KUBE_VERSION must be a valid semver-like version
if [[ ! "$KUBE_VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Error: Invalid Kubernetes version '$KUBE_VERSION'. Expected format: X.Y.Z" >&2
    exit 1
fi

echo "Validating Helm chart: $CHART_PATH" >&2

cleanup() {
    if [ -n "$TEMP_DIR" ] && [ -d "$TEMP_DIR" ]; then
        rm -rf "$TEMP_DIR"
    fi
}
trap cleanup EXIT

show_usage() {
    cat << 'EOF'
Usage: validate-helm.sh [chart-path] [values-file] [kube-version]

Arguments:
  chart-path    Path to Helm chart directory (default: current directory)
  values-file   Custom values file for validation (optional)
  kube-version  Kubernetes version to validate against (default: 1.28.0)

Examples:
  validate-helm.sh ./my-chart
  validate-helm.sh ./my-chart values-prod.yaml
  validate-helm.sh ./my-chart values-prod.yaml 1.29.0

Checks:
  - Chart.yaml validity
  - Template syntax
  - Kubernetes manifest validation
  - Best practices (via helm lint)
EOF
}

# Check if helm is installed
if ! command -v helm &> /dev/null; then
    echo '{"success": false, "error": "helm is not installed"}'
    exit 1
fi

RESULTS=()
ERRORS=0
WARNINGS=0

# Check if Chart.yaml exists
if [ ! -f "$CHART_PATH/Chart.yaml" ]; then
    echo '{"success": false, "error": "Chart.yaml not found in '"$CHART_PATH"'"}'
    exit 1
fi

# Extract chart info
CHART_NAME=$(grep "^name:" "$CHART_PATH/Chart.yaml" | awk '{print $2}')
CHART_VERSION=$(grep "^version:" "$CHART_PATH/Chart.yaml" | awk '{print $2}')
echo "Chart: $CHART_NAME v$CHART_VERSION" >&2

# 1. Helm lint (using arrays to prevent command injection)
echo "Running helm lint..." >&2
LINT_CMD=(helm lint "$CHART_PATH")
if [ -n "$VALUES_FILE" ]; then
    LINT_CMD+=(-f "$VALUES_FILE")
fi

LINT_OUTPUT=$("${LINT_CMD[@]}" 2>&1 || true)
if echo "$LINT_OUTPUT" | grep -q "Error:"; then
    RESULTS+=('{"check": "helm lint", "status": "fail"}')
    echo "helm lint: FAIL" >&2
    ((ERRORS++))
elif echo "$LINT_OUTPUT" | grep -q "WARNING"; then
    WARNING_COUNT=$(echo "$LINT_OUTPUT" | grep -c "WARNING" || echo "0")
    RESULTS+=('{"check": "helm lint", "status": "warning", "warnings": '"$WARNING_COUNT"'}')
    echo "helm lint: WARNING ($WARNING_COUNT)" >&2
    ((WARNINGS += WARNING_COUNT))
else
    RESULTS+=('{"check": "helm lint", "status": "pass"}')
    echo "helm lint: PASS" >&2
fi

# 2. Helm template (syntax validation, using arrays to prevent command injection)
echo "Running helm template..." >&2
TEMP_DIR=$(mktemp -d)
TEMPLATE_CMD=(helm template test-release "$CHART_PATH" --kube-version "$KUBE_VERSION")
if [ -n "$VALUES_FILE" ]; then
    TEMPLATE_CMD+=(-f "$VALUES_FILE")
fi

if "${TEMPLATE_CMD[@]}" > "$TEMP_DIR/rendered.yaml" 2>&1; then
    MANIFEST_COUNT=$(grep -c "^---" "$TEMP_DIR/rendered.yaml" || echo "0")
    RESULTS+=('{"check": "helm template", "status": "pass", "manifests": '"$MANIFEST_COUNT"'}')
    echo "helm template: PASS ($MANIFEST_COUNT manifests)" >&2
else
    RESULTS+=('{"check": "helm template", "status": "fail"}')
    echo "helm template: FAIL" >&2
    ((ERRORS++))
fi

# 3. Check for common issues
echo "Checking best practices..." >&2
BEST_PRACTICE_ISSUES=0

# Check for hardcoded images
if grep -r "image:" "$CHART_PATH/templates" 2>/dev/null | grep -v ".Values" | grep -v "{{" > /dev/null; then
    echo "  WARNING: Hardcoded image references found" >&2
    ((BEST_PRACTICE_ISSUES++))
fi

# Check for missing resource limits
if [ -f "$TEMP_DIR/rendered.yaml" ]; then
    DEPLOYMENTS=$(grep -c "kind: Deployment" "$TEMP_DIR/rendered.yaml" || echo "0")
    RESOURCES=$(grep -c "resources:" "$TEMP_DIR/rendered.yaml" || echo "0")
    if [ "$DEPLOYMENTS" -gt "$RESOURCES" ]; then
        echo "  WARNING: Some deployments missing resource limits" >&2
        ((BEST_PRACTICE_ISSUES++))
    fi
fi

if [ $BEST_PRACTICE_ISSUES -eq 0 ]; then
    RESULTS+=('{"check": "best practices", "status": "pass"}')
    echo "best practices: PASS" >&2
else
    RESULTS+=('{"check": "best practices", "status": "warning", "issues": '"$BEST_PRACTICE_ISSUES"'}')
    echo "best practices: WARNING ($BEST_PRACTICE_ISSUES issues)" >&2
    ((WARNINGS += BEST_PRACTICE_ISSUES))
fi

# 4. Dependency check (only with --skip-refresh to avoid unexpected network calls)
if [ -f "$CHART_PATH/Chart.lock" ]; then
    echo "Checking dependencies..." >&2
    if helm dependency build "$CHART_PATH" --skip-refresh > /dev/null 2>&1; then
        RESULTS+=('{"check": "dependencies", "status": "pass"}')
        echo "dependencies: PASS" >&2
    else
        RESULTS+=('{"check": "dependencies", "status": "fail"}')
        echo "dependencies: FAIL" >&2
        ((ERRORS++))
    fi
fi

# Output results
RESULTS_JSON=$(printf '%s\n' "${RESULTS[@]}" | paste -sd, -)
if [ $ERRORS -eq 0 ]; then
    echo '{"success": true, "chart": "'"$CHART_NAME"'", "version": "'"$CHART_VERSION"'", "errors": 0, "warnings": '"$WARNINGS"', "results": ['"$RESULTS_JSON"']}'
else
    echo '{"success": false, "chart": "'"$CHART_NAME"'", "version": "'"$CHART_VERSION"'", "errors": '"$ERRORS"', "warnings": '"$WARNINGS"', "results": ['"$RESULTS_JSON"']}'
fi
