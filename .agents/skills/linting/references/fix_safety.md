# Ruff Fix Safety Guide

Comprehensive documentation on Ruff's safe and unsafe fix system.

## Understanding Fix Safety

Ruff categorizes automatic fixes into two categories:

| Category | Description | Default Behavior |
|----------|-------------|------------------|
| **Safe** | Preserves code semantics and runtime behavior | Enabled with `--fix` |
| **Unsafe** | May change runtime behavior or remove comments | Requires `--unsafe-fixes` |

## Safe Fixes

Safe fixes guarantee that:
1. The meaning of your code is preserved
2. Runtime behavior remains unchanged
3. Comments are only removed when deleting entire statements/expressions

### Examples of Safe Fixes

```python
# Before: Unused variable (F841)
x = 1  # This variable is never used
y = 2
print(y)

# After safe fix: Removes the unused assignment
y = 2
print(y)
```

```python
# Before: Unnecessary pass (PIE790)
def foo():
    pass
    return 1

# After safe fix:
def foo():
    return 1
```

```python
# Before: Duplicate key (F601)
d = {"a": 1, "a": 2}

# After safe fix:
d = {"a": 2}
```

## Unsafe Fixes

Unsafe fixes may:
1. Change runtime behavior
2. Change the type of exceptions raised
3. Remove comments
4. Alter control flow in edge cases

### Examples of Unsafe Fixes

#### RUF015: Unnecessary Iterable Allocation

```python
# Before
head = list(range(99999999))[0]

# After unsafe fix
head = next(iter(range(99999999)))
```

**Why unsafe?** Changes exception from `IndexError` to `StopIteration` when collection is empty:

```python
list(range(0))[0]  # Raises IndexError
next(iter(range(0)))  # Raises StopIteration
```

#### UP038: Use isinstance() union type

```python
# Before
isinstance(x, (int, float))

# After unsafe fix (Python 3.10+)
isinstance(x, int | float)
```

**Why unsafe?** May fail at runtime on Python < 3.10.

## Applying Fixes

### Safe Fixes Only (Default)

```bash
ruff check . --fix
```

Only applies fixes that are guaranteed to preserve code semantics.

### Preview Changes Before Applying

```bash
ruff check . --diff
```

Shows what would change without making modifications.

### Include Unsafe Fixes

```bash
# Show unsafe fixes without applying
ruff check . --unsafe-fixes

# Apply all fixes including unsafe
ruff check . --fix --unsafe-fixes
```

### Disable Unsafe Fix Hints

By default, Ruff shows hints when unsafe fixes are available. To silence:

```bash
ruff check . --no-unsafe-fixes
```

Or in configuration:

```toml
[tool.ruff]
unsafe-fixes = false
```

## Configuring Fix Safety

### Promoting Unsafe Fixes to Safe

If you trust certain unsafe fixes, promote them to safe:

```toml
[tool.ruff.lint]
extend-safe-fixes = [
    "F601",   # Duplicate keys
    "RUF015", # Unnecessary iterable allocation
    "UP038",  # isinstance union type
]
```

You can use prefixes to promote entire categories:

```toml
[tool.ruff.lint]
extend-safe-fixes = ["F"]  # All Pyflakes fixes become safe
```

### Demoting Safe Fixes to Unsafe

For extra caution, demote safe fixes:

```toml
[tool.ruff.lint]
extend-unsafe-fixes = [
    "UP034",  # Extraneous parentheses
    "SIM",    # All simplify rules
]
```

### Preventing Fixes Entirely

Use `unfixable` to completely disable fixes for certain rules:

```toml
[tool.ruff.lint]
unfixable = [
    "F401",   # Never auto-remove unused imports
    "F841",   # Never auto-remove unused variables
    "B",      # Never auto-fix any bugbear rules
]
```

### Allowing Only Specific Fixes

Use `fixable` to whitelist which rules can be fixed:

```toml
[tool.ruff.lint]
# Only these rules can be auto-fixed
fixable = ["I", "UP", "F401"]
```

Or fix everything except specific rules:

```toml
[tool.ruff.lint]
fixable = ["ALL"]
unfixable = ["F401", "F841"]
```

## Fix Safety by Rule Category

### Generally Safe to Auto-Fix

| Rule | Description |
|------|-------------|
| I (isort) | Import sorting |
| UP (pyupgrade) | Most Python upgrades |
| F401 | Unused imports |
| W (pycodestyle warnings) | Whitespace issues |
| SIM1XX | Simple simplifications |

### Proceed with Caution

| Rule | Description | Why Careful? |
|------|-------------|--------------|
| B | flake8-bugbear | May change error handling |
| RUF015 | Iterable allocation | Changes exception types |
| F841 | Unused variables | May remove intentional assignments |
| TCH | Type checking | May break runtime type checks |

### Recommended Configuration for Teams

```toml
[tool.ruff.lint]
# Enable all auto-fixes
fixable = ["ALL"]

# Prevent accidental removal of important code
unfixable = [
    "F401",   # Unused imports - may be intentional re-exports
    "F841",   # Unused variables - may be intentional
    "ERA",    # Commented code - may be needed
]

# Be extra careful with these
extend-unsafe-fixes = [
    "B",      # Bugbear changes may affect error handling
]
```

## Workflow Recommendations

### Individual Development

```bash
# 1. Run with safe fixes
ruff check . --fix

# 2. Review remaining issues
ruff check .

# 3. Preview unsafe fixes
ruff check . --diff --unsafe-fixes

# 4. Apply unsafe fixes after review
ruff check . --fix --unsafe-fixes
```

### CI/CD Pipeline

```yaml
# In CI, never apply unsafe fixes automatically
- name: Lint with auto-fix
  run: ruff check . --fix  # Safe fixes only

# Check for remaining issues
- name: Check lint
  run: ruff check .
```

### Pre-commit Hook

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.0
    hooks:
      - id: ruff
        args: [--fix]  # Safe fixes only
```

For unsafe fixes in pre-commit (use with caution):

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.0
    hooks:
      - id: ruff
        args: [--fix, --unsafe-fixes]
```

## JSON Output

When using JSON output format, all fixes (safe and unsafe) are always displayed:

```bash
ruff check . --output-format json
```

The safety of each fix is available in the `applicability` field:

```json
{
  "code": "F401",
  "message": "'os' imported but unused",
  "fix": {
    "applicability": "safe",
    "message": "Remove unused import: `os`",
    "edits": [...]
  }
}
```

Possible `applicability` values:
- `safe`: Safe to apply automatically
- `unsafe`: May change behavior
- `display-only`: For informational purposes only

## Troubleshooting

### Fix Not Being Applied

1. **Rule is in unfixable list**:
   ```bash
   ruff check --show-settings | grep unfixable
   ```

2. **Fix is unsafe and --unsafe-fixes not specified**:
   ```bash
   ruff check . --unsafe-fixes  # Check what's available
   ```

3. **Rule doesn't support fixing**:
   ```bash
   ruff rule F401  # Check if rule supports auto-fix
   ```

### Unexpected Changes After Fix

1. **Review what was changed**:
   ```bash
   git diff
   ```

2. **Check if unsafe fix was applied**:
   ```bash
   # Run again to see if issues remain
   ruff check .
   ```

3. **Revert and be more selective**:
   ```bash
   git checkout -- .
   ruff check . --diff  # Preview first
   ```

### Preventing Specific Fixes

```toml
[tool.ruff.lint]
# Don't fix these even with --fix
unfixable = ["F401"]
```

Or use per-file configuration:

```toml
[tool.ruff.lint.per-file-ignores]
# In these files, F401 violations are ignored entirely
"__init__.py" = ["F401"]
```

## Best Practices

1. **Start Conservative**: Begin with safe fixes only
2. **Review First**: Use `--diff` before applying any fixes
3. **Test After Fixing**: Run tests after applying fixes
4. **Pin Rule Versions**: Ensure consistent behavior across environments
5. **Document Decisions**: Comment why certain rules are in unfixable
6. **Team Agreement**: Align on fix safety configuration with your team
7. **CI Safety**: Never use `--unsafe-fixes` in automated pipelines
