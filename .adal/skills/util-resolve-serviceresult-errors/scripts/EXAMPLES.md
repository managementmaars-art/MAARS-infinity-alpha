# ServiceResult Scripts: Real-World Examples

This document provides comprehensive real-world examples of using the ServiceResult automation scripts.

## Table of Contents

1. [Fixing Test Mock Errors](#fixing-test-mock-errors)
2. [Validating ServiceResult Usage](#validating-serviceresult-usage)
3. [Identifying Refactoring Opportunities](#identifying-refactoring-opportunities)
4. [CI/CD Integration](#cicd-integration)
5. [Large Codebase Workflows](#large-codebase-workflows)

---

## Fixing Test Mock Errors

### Example 1: Single File Fix

**Scenario:** Test fails with `'dict' object has no attribute 'success'`

```bash
# Run test to see error
uv run pytest tests/unit/test_file_service.py -v

# Output:
# AttributeError: 'dict' object has no attribute 'success'
# File: tests/unit/test_file_service.py, line 42

# Preview fix
python scripts/fix_serviceresult_mocks.py --dry-run tests/unit/test_file_service.py

# Output:
# [PREVIEW] tests/unit/test_file_service.py:42
#   - mock_repo.get_files = AsyncMock(return_value={"files": []})
#   + from project_watch_mcp.domain.common import ServiceResult
#   + mock_repo.get_files = AsyncMock(return_value=ServiceResult.ok({"files": []}))

# Apply fix
python scripts/fix_serviceresult_mocks.py tests/unit/test_file_service.py

# Verify
uv run pytest tests/unit/test_file_service.py -v
# ✅ PASSED
```

### Example 2: Batch Fix All Test Files

**Scenario:** Multiple tests failing with mock configuration errors

```bash
# Preview all changes
python scripts/fix_serviceresult_mocks.py --dry-run tests/

# Output:
# Found 15 mock configuration issues in 8 files
# [PREVIEW] tests/unit/test_chunking.py:23
# [PREVIEW] tests/unit/test_embedding.py:31
# [PREVIEW] tests/unit/test_file_service.py:42
# ... (12 more)

# Apply all fixes
python scripts/fix_serviceresult_mocks.py --all tests/

# Output:
# ✅ Fixed 15 mock configurations in 8 files
# Modified files:
#   - tests/unit/test_chunking.py
#   - tests/unit/test_embedding.py
#   - tests/unit/test_file_service.py
#   - tests/unit/test_indexing.py
#   - tests/unit/test_reader.py
#   - tests/unit/test_repository.py
#   - tests/unit/test_search.py
#   - tests/unit/test_vector_store.py

# Run all tests
uv run pytest tests/ -v
# ✅ All tests passing
```

### Example 3: Fix with Backup

**Scenario:** Fix mocks but keep backup of original files

```bash
# Create backups before modifying
python scripts/fix_serviceresult_mocks.py --backup --all tests/

# Output:
# Created backups:
#   tests/unit/test_file_service.py.bak
#   tests/unit/test_chunking.py.bak
# Modified 8 files

# If something breaks, restore from backup
cp tests/unit/test_file_service.py.bak tests/unit/test_file_service.py
```

---

## Validating ServiceResult Usage

### Example 4: Validate Source Directory

**Scenario:** Check entire source for ServiceResult violations

```bash
# Run validation
python scripts/validate_serviceresult_usage.py src/

# Output:
# ServiceResult Validation Report
# ================================
# Files analyzed: 47
# Violations found: 23
#
# CRITICAL VIOLATIONS (12):
# -------------------------
# src/services/file_service.py:42
#   Missing success check before data access
#   Code: data = result.data
#   Fix: if result.success: data = result.data
#
# src/services/chunking_service.py:67
#   Unsafe unwrap on optional data
#   Code: value = result.unwrap()
#   Fix: value = result.unwrap_or(default)
#
# ... (10 more critical)
#
# WARNINGS (11):
# --------------
# src/handlers/index_handler.py:89
#   Consider using compose_results for chaining
#   Manual chain length: 4 sequential checks
#
# ... (10 more warnings)
```

### Example 5: Export Violations to JSON

**Scenario:** Generate machine-readable violation report for tooling

```bash
# Export to JSON
python scripts/validate_serviceresult_usage.py --format json src/ > violations.json

# violations.json content:
{
  "summary": {
    "files_analyzed": 47,
    "total_violations": 23,
    "critical": 12,
    "warnings": 11
  },
  "violations": [
    {
      "severity": "critical",
      "file": "src/services/file_service.py",
      "line": 42,
      "type": "missing_success_check",
      "message": "Missing success check before data access",
      "code": "data = result.data",
      "suggestion": "if result.success: data = result.data"
    },
    ...
  ]
}

# Use in CI/CD or custom tooling
jq '.summary.critical' violations.json
# Output: 12
```

### Example 6: Fail CI on Violations

**Scenario:** Block pull requests with ServiceResult violations

```bash
# Run with --fail-on-violations flag
python scripts/validate_serviceresult_usage.py --fail-on-violations src/

# Exit code: 1 if violations found, 0 if clean
echo $?
# Output: 1 (violations found)

# Use in CI pipeline
# .github/workflows/validate.yml
python scripts/validate_serviceresult_usage.py --fail-on-violations src/ || exit 1
```

---

## Identifying Refactoring Opportunities

### Example 7: Find Complex ServiceResult Chains

**Scenario:** Identify code that would benefit from composition utilities

```bash
# Find chaining opportunities
python scripts/find_serviceresult_chains.py src/

# Output:
# ServiceResult Chaining Analysis
# ================================
# Files analyzed: 47
# Chains found: 8
#
# REFACTORING OPPORTUNITIES:
# --------------------------
# src/services/indexing_service.py:120-145 (25 lines)
#   Chain length: 5 sequential ServiceResult checks
#   Complexity: HIGH
#   Lines of code: 25
#   Suggested refactoring: Use compose_results utility
#   Estimated reduction: 17 lines → 8 lines (68% reduction)
#
# src/handlers/file_handler.py:67-85 (18 lines)
#   Chain length: 4 sequential ServiceResult checks
#   Complexity: MEDIUM
#   Lines of code: 18
#   Suggested refactoring: Use compose_results utility
#   Estimated reduction: 18 lines → 10 lines (44% reduction)
#
# ... (6 more chains)
#
# SUMMARY:
# Total reduction potential: 87 lines → 42 lines (52% reduction)
```

### Example 8: Get Detailed Refactoring Suggestions

**Scenario:** Get code examples for refactoring

```bash
# Get refactoring suggestions
python scripts/find_serviceresult_chains.py --suggest-refactor src/

# Output:
# REFACTORING SUGGESTION 1:
# File: src/services/indexing_service.py
# Lines: 120-145
#
# BEFORE (25 lines):
# ------------------
# result1 = await self.reader.read_file(file_path)
# if not result1.success:
#     return ServiceResult.fail(result1.error)
#
# result2 = await self.parser.parse(result1.data)
# if not result2.success:
#     return ServiceResult.fail(result2.error)
#
# result3 = await self.chunker.chunk(result2.data)
# if not result3.success:
#     return ServiceResult.fail(result3.error)
#
# result4 = await self.embedder.embed(result3.data)
# if not result4.success:
#     return ServiceResult.fail(result4.error)
#
# result5 = await self.repo.store(result4.data)
# if not result5.success:
#     return ServiceResult.fail(result5.error)
#
# return result5
#
# AFTER (8 lines):
# ----------------
# from project_watch_mcp.domain.common.service_result_utils import compose_results
#
# result = await self.reader.read_file(file_path)
# if result.success:
#     result = await compose_results(lambda d: self.parser.parse(d), result)
# if result.success:
#     result = await compose_results(lambda d: self.chunker.chunk(d), result)
# if result.success:
#     result = await compose_results(lambda d: self.embedder.embed(d), result)
# if result.success:
#     result = await compose_results(lambda d: self.repo.store(d), result)
# return result
#
# BENEFITS:
# - 68% reduction in lines of code
# - Improved readability (functional composition)
# - Easier to test (composition utilities handle error propagation)
# - More maintainable (add steps without nested if blocks)
```

### Example 9: Filter by Minimum Chain Length

**Scenario:** Only show chains worth refactoring (>= 5 checks)

```bash
# Only chains with 5+ sequential checks
python scripts/find_serviceresult_chains.py --min-length 5 src/

# Output:
# ServiceResult Chaining Analysis
# ================================
# Files analyzed: 47
# Chains found: 2 (filtered by min-length >= 5)
#
# src/services/indexing_service.py:120-145
#   Chain length: 5
#   Lines: 25
#
# src/handlers/migration_handler.py:89-110
#   Chain length: 6
#   Lines: 22
```

---

## CI/CD Integration

### Example 10: GitHub Actions Validation

**Scenario:** Validate ServiceResult usage in pull requests

```yaml
# .github/workflows/validate-serviceresult.yml
name: Validate ServiceResult Usage

on:
  pull_request:
    paths:
      - 'src/**/*.py'
      - 'tests/**/*.py'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Validate ServiceResult patterns
        run: |
          python scripts/validate_serviceresult_usage.py --fail-on-violations src/

      - name: Comment on PR with results
        if: failure()
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const violations = fs.readFileSync('violations.json', 'utf8');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `## ServiceResult Violations Found\n\`\`\`json\n${violations}\n\`\`\``
            });
```

### Example 11: Pre-commit Hook

**Scenario:** Catch violations before commit

```bash
# .git/hooks/pre-commit
#!/bin/bash

echo "Validating ServiceResult usage..."
python scripts/validate_serviceresult_usage.py --fail-on-violations src/

if [ $? -ne 0 ]; then
  echo "❌ ServiceResult violations found. Commit blocked."
  echo "Fix violations or use 'git commit --no-verify' to skip (not recommended)"
  exit 1
fi

echo "✅ ServiceResult validation passed"
exit 0
```

---

## Large Codebase Workflows

### Example 12: Parallel Processing

**Scenario:** Process large codebase (1000+ files) efficiently

```bash
# Find all Python modules
find src/ -type d -maxdepth 1

# Output:
# src/services
# src/handlers
# src/repositories
# src/domain
# src/infrastructure

# Process in parallel (4 workers)
find src/ -type d -maxdepth 1 | \
  xargs -P 4 -I {} python scripts/validate_serviceresult_usage.py {}

# Combine results
find src/ -type d -maxdepth 1 | \
  xargs -P 4 -I {} python scripts/validate_serviceresult_usage.py --format json {} > combined.json
```

### Example 13: Incremental Validation

**Scenario:** Only validate changed files in pull request

```bash
# Get changed Python files in PR
git diff --name-only origin/main...HEAD | grep '\.py$' > changed_files.txt

# Validate only changed files
cat changed_files.txt | xargs python scripts/validate_serviceresult_usage.py

# Output:
# Analyzing 5 changed files...
# violations.json
```

### Example 14: Generate Summary Report

**Scenario:** Weekly report on ServiceResult pattern health

```bash
# Generate full report
python scripts/validate_serviceresult_usage.py --verbose src/ > weekly_report.txt
python scripts/find_serviceresult_chains.py --metrics src/ >> weekly_report.txt

# Extract metrics
echo "## Weekly ServiceResult Health Report ($(date))" > summary.md
echo "" >> summary.md
echo "### Validation Results" >> summary.md
grep "Files analyzed" weekly_report.txt >> summary.md
grep "Violations found" weekly_report.txt >> summary.md
echo "" >> summary.md
echo "### Refactoring Opportunities" >> summary.md
grep "Total reduction potential" weekly_report.txt >> summary.md

# Send report (e.g., email, Slack)
cat summary.md | mail -s "ServiceResult Health Report" team@example.com
```

---

## Complete Workflow Example

### Example 15: Full ServiceResult Cleanup Workflow

**Scenario:** New team member onboarding - clean up existing violations

```bash
# Step 1: Assess current state
echo "📊 Step 1: Assessing codebase..."
python scripts/validate_serviceresult_usage.py src/ > baseline_report.txt
python scripts/find_serviceresult_chains.py src/ > chains_report.txt

# Step 2: Fix all test mocks
echo "🔧 Step 2: Fixing test mocks..."
python scripts/fix_serviceresult_mocks.py --backup --all tests/

# Step 3: Run tests to verify fixes
echo "🧪 Step 3: Running tests..."
uv run pytest tests/ -v

# Step 4: Validate again (should have fewer violations)
echo "✅ Step 4: Re-validating..."
python scripts/validate_serviceresult_usage.py src/ > post_fix_report.txt

# Step 5: Compare before/after
echo "📈 Step 5: Comparing results..."
echo "BEFORE:"
grep "Violations found" baseline_report.txt
echo "AFTER:"
grep "Violations found" post_fix_report.txt

# Step 6: Identify top refactoring priorities
echo "🎯 Step 6: Top refactoring priorities..."
python scripts/find_serviceresult_chains.py --min-length 4 --suggest-refactor src/ > refactor_plan.txt

# Step 7: Commit improvements
echo "💾 Step 7: Committing fixes..."
git add .
git commit -m "Fix ServiceResult mock configurations

- Fixed 15 mock configurations in test files
- Reduced violations from 23 to 11
- Identified 8 refactoring opportunities

See refactor_plan.txt for next steps"

echo "✅ ServiceResult cleanup complete!"
echo "Next: Review refactor_plan.txt and prioritize composition utility refactorings"
```

---

## See Also

- [README.md](./README.md) - Script documentation and common options
- [SCRIPT_SUMMARY.md](./SCRIPT_SUMMARY.md) - Technical implementation details
- [examples.md](./examples.md) - Additional examples gallery
- [../SKILL.md](../SKILL.md) - Main ServiceResult resolution skill
