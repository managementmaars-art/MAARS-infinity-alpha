# ServiceResult Automation Scripts

This directory contains three powerful automation utilities to detect and fix ServiceResult pattern issues in Python codebases.

## Available Scripts

### 1. fix_serviceresult_mocks.py

**Purpose:** Automatically fix test mock configuration errors.

**Usage:**
```bash
# Fix all test mocks in a directory
python scripts/fix_serviceresult_mocks.py --all tests/

# Dry run (preview changes without modifying files)
python scripts/fix_serviceresult_mocks.py --dry-run tests/

# Fix specific file
python scripts/fix_serviceresult_mocks.py tests/unit/test_service.py

# Limit to specific patterns
python scripts/fix_serviceresult_mocks.py --pattern "return_value=" tests/
```

**What it fixes:**
- Mock returns dict instead of ServiceResult.ok(dict)
- Missing AsyncMock for async methods
- Incorrect mock configuration patterns
- Missing ServiceResult import statements

**Example transformation:**
```python
# BEFORE (incorrect)
mock_service.get_data = AsyncMock(return_value={"items": []})

# AFTER (correct)
from project_watch_mcp.domain.common import ServiceResult
mock_service.get_data = AsyncMock(return_value=ServiceResult.ok({"items": []}))
```

### 2. validate_serviceresult_usage.py

**Purpose:** Validate ServiceResult usage patterns across the codebase.

**Usage:**
```bash
# Validate entire source directory
python scripts/validate_serviceresult_usage.py src/

# Check specific module
python scripts/validate_serviceresult_usage.py src/services/

# Output detailed report
python scripts/validate_serviceresult_usage.py --verbose src/

# Export violations to JSON
python scripts/validate_serviceresult_usage.py --format json src/ > violations.json
```

**What it validates:**
- ServiceResult return type annotations
- Proper success/failure checks before data access
- Correct unwrap() usage with None checks
- Error propagation patterns
- Type safety in ServiceResult[T] usage

**Example violations detected:**
```python
# VIOLATION 1: Missing success check
result = service.get_data()
data = result.data  # Unsafe - could be None on failure

# VIOLATION 2: Unsafe unwrap
result = ServiceResult.ok(None)
value = result.unwrap()  # Raises ValueError

# VIOLATION 3: Missing error propagation
if not result.success:
    pass  # Should return or raise
```

### 3. find_serviceresult_chains.py

**Purpose:** Identify refactoring opportunities for ServiceResult chaining.

**Usage:**
```bash
# Find chaining opportunities in source
python scripts/find_serviceresult_chains.py src/

# Get refactoring suggestions
python scripts/find_serviceresult_chains.py --suggest-refactor src/

# Minimum chain length (default 3)
python scripts/find_serviceresult_chains.py --min-length 5 src/

# Output detailed metrics
python scripts/find_serviceresult_chains.py --metrics src/
```

**What it identifies:**
- Sequential ServiceResult checks (if result.success: ...)
- Manual error propagation patterns
- Opportunities to use composition utilities (map, bind, flatmap)
- Code complexity reduction potential

**Example refactoring:**
```python
# BEFORE (manual chaining - 17 lines)
result1 = await service1.operation()
if not result1.success:
    return ServiceResult.fail(result1.error)
result2 = await service2.operation(result1.data)
if not result2.success:
    return ServiceResult.fail(result2.error)
result3 = await service3.operation(result2.data)
if not result3.success:
    return ServiceResult.fail(result3.error)
return result3

# AFTER (composition utilities - 8 lines)
from project_watch_mcp.domain.common.service_result_utils import compose_results

result = await service1.operation()
if result.success:
    result = await compose_results(lambda d: service2.operation(d), result)
if result.success:
    result = await compose_results(lambda d: service3.operation(d), result)
return result
```

## Common Workflows

### Workflow 1: Fix All Test Mocks

```bash
# 1. Preview changes
python scripts/fix_serviceresult_mocks.py --dry-run tests/

# 2. Apply fixes
python scripts/fix_serviceresult_mocks.py --all tests/

# 3. Run tests to verify
uv run pytest tests/
```

### Workflow 2: Validate Entire Codebase

```bash
# 1. Run validation
python scripts/validate_serviceresult_usage.py src/ > validation_report.txt

# 2. Review violations
cat validation_report.txt

# 3. Fix violations manually or with fix_serviceresult_mocks.py
```

### Workflow 3: Identify Refactoring Opportunities

```bash
# 1. Find chains
python scripts/find_serviceresult_chains.py --suggest-refactor src/ > refactoring.txt

# 2. Review suggestions
cat refactoring.txt

# 3. Apply composition utilities where beneficial
# (Manual refactoring based on suggestions)
```

## Script Options Reference

### Common Options (All Scripts)

- `--help` - Show help message and exit
- `--verbose` - Enable detailed output
- `--quiet` - Suppress non-error output

### fix_serviceresult_mocks.py Options

- `--all` - Process all files in directory
- `--dry-run` - Preview changes without modifying files
- `--pattern <pattern>` - Limit to specific code patterns
- `--backup` - Create .bak files before modification

### validate_serviceresult_usage.py Options

- `--format <format>` - Output format (text, json, csv)
- `--fail-on-violations` - Exit with error code if violations found
- `--exclude <pattern>` - Exclude files matching pattern

### find_serviceresult_chains.py Options

- `--suggest-refactor` - Include refactoring suggestions
- `--min-length <n>` - Minimum chain length to report (default: 3)
- `--metrics` - Include complexity metrics
- `--sort-by <metric>` - Sort results by metric (length, complexity, file)

## Integration with CI/CD

### Pre-commit Hook

```bash
# .git/hooks/pre-commit
#!/bin/bash
python scripts/validate_serviceresult_usage.py --fail-on-violations src/
```

### GitHub Actions

```yaml
# .github/workflows/validate.yml
name: Validate ServiceResult Usage
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: python scripts/validate_serviceresult_usage.py --fail-on-violations src/
```

## Performance Considerations

- **fix_serviceresult_mocks.py**: Processes ~100 files/second
- **validate_serviceresult_usage.py**: Processes ~50 files/second
- **find_serviceresult_chains.py**: Processes ~30 files/second (more complex analysis)

For large codebases (>1000 files), consider parallel execution:

```bash
# Process directories in parallel
find src/ -type d -maxdepth 1 | \
  xargs -P 4 -I {} python scripts/validate_serviceresult_usage.py {}
```

## Troubleshooting

### Script fails with "Module not found"

**Solution:** Ensure you're running from the project root:
```bash
cd /path/to/project
python scripts/validate_serviceresult_usage.py src/
```

### Changes not applied in dry-run mode

**Expected behavior:** `--dry-run` only previews changes. Remove the flag to apply:
```bash
python scripts/fix_serviceresult_mocks.py --all tests/
```

### Too many violations reported

**Filter by severity:** Most scripts support filtering:
```bash
python scripts/validate_serviceresult_usage.py --severity error src/
```

## See Also

- [EXAMPLES.md](./EXAMPLES.md) - Real-world usage examples
- [SCRIPT_SUMMARY.md](./SCRIPT_SUMMARY.md) - Technical details and test results
- [examples.md](./examples.md) - Comprehensive examples gallery
- [../SKILL.md](../SKILL.md) - Main ServiceResult resolution skill documentation
