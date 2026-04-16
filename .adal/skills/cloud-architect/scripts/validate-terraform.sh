#!/bin/bash
set -e

# Terraform Validation Script
# Validates Terraform configurations for syntax and best practices

TF_DIR="${1:-.}"
CHECK_FORMAT="${2:-true}"

# Input validation: TF_DIR must be an existing directory
if [ ! -d "$TF_DIR" ]; then
    echo "Error: Terraform directory '$TF_DIR' does not exist." >&2
    exit 1
fi

# Input validation: CHECK_FORMAT must be "true" or "false"
if [ "$CHECK_FORMAT" != "true" ] && [ "$CHECK_FORMAT" != "false" ]; then
    echo "Error: CHECK_FORMAT must be 'true' or 'false', got '$CHECK_FORMAT'." >&2
    exit 1
fi

echo "Validating Terraform configuration: $TF_DIR" >&2

cleanup() {
    echo "Validation completed" >&2
}
trap cleanup EXIT

show_usage() {
    cat << 'EOF'
Usage: validate-terraform.sh [tf-dir] [check-format]

Arguments:
  tf-dir        Path to Terraform directory (default: current directory)
  check-format  Check formatting: true/false (default: true)

Examples:
  validate-terraform.sh
  validate-terraform.sh ./infrastructure
  validate-terraform.sh ./infrastructure false

Checks:
  - Terraform init (provider validation)
  - terraform validate (syntax)
  - terraform fmt -check (formatting)
  - Basic security checks
EOF
}

# Check if terraform is installed
if ! command -v terraform &> /dev/null; then
    echo '{"success": false, "error": "terraform is not installed"}'
    exit 1
fi

cd "$TF_DIR"

RESULTS=()
ERRORS=0
WARNINGS=0

# Check if any .tf files exist
if ! ls *.tf 1> /dev/null 2>&1; then
    echo '{"success": false, "error": "No .tf files found in '"$TF_DIR"'"}'
    exit 1
fi

# 1. Terraform init (backend skip)
echo "Running terraform init..." >&2
if terraform init -backend=false -input=false > /dev/null 2>&1; then
    RESULTS+=('{"check": "terraform init", "status": "pass"}')
    echo "terraform init: PASS" >&2
else
    RESULTS+=('{"check": "terraform init", "status": "fail"}')
    echo "terraform init: FAIL" >&2
    ((ERRORS++))
fi

# 2. Terraform validate
echo "Running terraform validate..." >&2
VALIDATE_OUTPUT=$(terraform validate -json 2>&1 || true)
if echo "$VALIDATE_OUTPUT" | grep -q '"valid": true'; then
    RESULTS+=('{"check": "terraform validate", "status": "pass"}')
    echo "terraform validate: PASS" >&2
else
    ERROR_COUNT=$(echo "$VALIDATE_OUTPUT" | grep -o '"error_count": [0-9]*' | grep -o '[0-9]*' || echo "1")
    RESULTS+=('{"check": "terraform validate", "status": "fail", "errors": '"$ERROR_COUNT"'}')
    echo "terraform validate: FAIL ($ERROR_COUNT errors)" >&2
    ((ERRORS += ERROR_COUNT))
fi

# 3. Terraform fmt check
if [ "$CHECK_FORMAT" = "true" ]; then
    echo "Running terraform fmt -check..." >&2
    FMT_OUTPUT=$(terraform fmt -check -recursive 2>&1 || true)
    if [ -z "$FMT_OUTPUT" ]; then
        RESULTS+=('{"check": "terraform fmt", "status": "pass"}')
        echo "terraform fmt: PASS" >&2
    else
        UNFORMATTED=$(echo "$FMT_OUTPUT" | wc -l | tr -d ' ')
        RESULTS+=('{"check": "terraform fmt", "status": "fail", "unformatted_files": '"$UNFORMATTED"'}')
        echo "terraform fmt: FAIL ($UNFORMATTED files)" >&2
        ((ERRORS++))
    fi
fi

# 4. Security checks
echo "Running security checks..." >&2
SECURITY_ISSUES=0

# Check for hardcoded secrets
if grep -rE "(password|secret|api_key|access_key)\s*=\s*\"[^\"]+\"" *.tf 2>/dev/null | grep -v "var\." | grep -v "data\." > /dev/null; then
    echo "  WARNING: Possible hardcoded secrets found" >&2
    ((SECURITY_ISSUES++))
fi

# Check for public S3 buckets
if grep -r "acl.*=.*public" *.tf 2>/dev/null > /dev/null; then
    echo "  WARNING: Public ACL found" >&2
    ((SECURITY_ISSUES++))
fi

# Check for unencrypted resources
if grep -r "aws_ebs_volume\|aws_rds_instance" *.tf 2>/dev/null > /dev/null; then
    if ! grep -r "encrypted.*=.*true" *.tf 2>/dev/null > /dev/null; then
        echo "  WARNING: Resources may be unencrypted" >&2
        ((SECURITY_ISSUES++))
    fi
fi

if [ $SECURITY_ISSUES -eq 0 ]; then
    RESULTS+=('{"check": "security", "status": "pass"}')
    echo "security: PASS" >&2
else
    RESULTS+=('{"check": "security", "status": "warning", "issues": '"$SECURITY_ISSUES"'}')
    echo "security: WARNING ($SECURITY_ISSUES issues)" >&2
    ((WARNINGS += SECURITY_ISSUES))
fi

# 5. Check for required files
echo "Checking required files..." >&2
REQUIRED_FILES=("variables.tf" "outputs.tf")
MISSING_FILES=0
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "  WARNING: Missing recommended file: $file" >&2
        ((MISSING_FILES++))
    fi
done

if [ $MISSING_FILES -eq 0 ]; then
    RESULTS+=('{"check": "structure", "status": "pass"}')
else
    RESULTS+=('{"check": "structure", "status": "warning", "missing": '"$MISSING_FILES"'}')
    ((WARNINGS += MISSING_FILES))
fi

# Output results
RESULTS_JSON=$(printf '%s\n' "${RESULTS[@]}" | paste -sd, -)
TF_VERSION=$(terraform version -json 2>/dev/null | grep -o '"terraform_version": "[^"]*"' | cut -d'"' -f4 || echo "unknown")

if [ $ERRORS -eq 0 ]; then
    echo '{"success": true, "terraform_version": "'"$TF_VERSION"'", "errors": 0, "warnings": '"$WARNINGS"', "results": ['"$RESULTS_JSON"']}'
else
    echo '{"success": false, "terraform_version": "'"$TF_VERSION"'", "errors": '"$ERRORS"', "warnings": '"$WARNINGS"', "results": ['"$RESULTS_JSON"']}'
fi
