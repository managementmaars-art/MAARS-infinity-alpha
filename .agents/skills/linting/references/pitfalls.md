# Ruff Linting Pitfalls

Common issues and solutions when using Ruff for Python linting.

## Configuration Issues

### Conflicting Formatter and Linter Rules

**Problem**: Ruff linter and Ruff formatter (or Black) have conflicting rules.

**Symptoms**:
- Formatter changes trigger linter violations
- Linter auto-fix changes trigger formatter violations
- Endless loop of fixes

**Solution**: Disable linter rules that conflict with formatter:

```toml
[tool.ruff.lint]
ignore = [
    "E501",   # Line too long - formatter handles this
    "W291",   # Trailing whitespace - formatter handles this
    "W292",   # No newline at end of file - formatter handles this
    "W293",   # Blank line contains whitespace - formatter handles this
]
```

Or use the recommended approach - let Ruff manage both:

```toml
[tool.ruff]
line-length = 88

[tool.ruff.lint]
select = ["E", "F", "UP", "B", "SIM", "I"]
ignore = ["E501"]  # Formatter handles line length

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

### Configuration Not Being Applied

**Problem**: Changes to configuration don't seem to take effect.

**Causes**:
1. Wrong configuration file location
2. Syntax errors in TOML
3. Wrong section names
4. Cached results

**Solutions**:

1. Verify configuration file location:
```bash
ruff check . --show-settings
```

2. Check for TOML syntax errors:
```bash
python -c "import tomllib; tomllib.load(open('pyproject.toml', 'rb'))"
```

3. Ensure correct section names:
```toml
# Correct
[tool.ruff.lint]
select = ["E", "F"]

# Wrong
[tool.ruff]
lint.select = ["E", "F"]  # This doesn't work
```

4. Clear cache:
```bash
rm -rf .ruff_cache
ruff check .
```

### Per-file Ignores Not Working

**Problem**: Per-file ignore patterns don't match expected files.

**Solution**: Use correct glob patterns:

```toml
[tool.ruff.lint.per-file-ignores]
# Match any file named __init__.py
"__init__.py" = ["F401"]

# Match all Python files in tests directory (recursive)
"tests/**/*.py" = ["S101"]

# Match files in specific directories
"**/{tests,docs,tools}/*" = ["E402"]

# Match specific file
"src/generated/parser.py" = ["E501", "F401"]
```

## Rule Selection Issues

### Too Many Violations Initially

**Problem**: Enabling rules creates hundreds/thousands of violations.

**Solution**: Start minimal and expand gradually:

```toml
# Week 1: Start here
[tool.ruff.lint]
select = ["E", "F"]

# Week 2: Add import sorting
select = ["E", "F", "I"]

# Week 3: Add pyupgrade
select = ["E", "F", "I", "UP"]

# Week 4+: Continue expanding
select = ["E", "F", "I", "UP", "B", "SIM"]
```

### Rules Too Strict for Project

**Problem**: Some rules don't fit the project's coding style.

**Solution**: Ignore specific rules rather than disabling entire categories:

```toml
[tool.ruff.lint]
select = ["E", "F", "B", "SIM"]
ignore = [
    "SIM108",  # Use ternary operator - sometimes if/else is clearer
    "B008",    # Function call in default argument - needed for FastAPI
]
```

### Missing Rules After Migration from Flake8

**Problem**: Some Flake8 rules aren't being enforced after switching to Ruff.

**Solution**: Explicitly enable equivalent rule sets:

```toml
[tool.ruff.lint]
select = [
    # Core Flake8
    "E",      # pycodestyle errors
    "W",      # pycodestyle warnings
    "F",      # Pyflakes
    
    # Common plugins you may have been using
    "B",      # flake8-bugbear
    "C4",     # flake8-comprehensions
    "DTZ",    # flake8-datetimez
    "I",      # isort
    "S",      # flake8-bandit
    "T20",    # flake8-print
]
```

Check [Ruff rules documentation](https://docs.astral.sh/ruff/rules/) for Flake8 equivalents.

## Fix-Related Issues

### Unsafe Fixes Breaking Code

**Problem**: Auto-fix with `--unsafe-fixes` changed code behavior.

**Symptoms**:
- Tests fail after auto-fix
- Runtime errors after auto-fix
- Different exception types raised

**Solution**: Be cautious with unsafe fixes:

```bash
# Preview changes first
ruff check . --diff --unsafe-fixes

# Apply fixes selectively
ruff check . --fix  # Safe only first

# Review and apply unsafe fixes manually
ruff check . --show-fixes --unsafe-fixes
```

Or limit which rules can be fixed:

```toml
[tool.ruff.lint]
fixable = ["ALL"]
unfixable = [
    "F401",   # Don't auto-remove unused imports
    "F841",   # Don't auto-remove unused variables
    "B",      # Don't auto-fix bugbear rules
]
```

### Auto-fix Removing Important Comments

**Problem**: Auto-fix removes comments along with code.

**Cause**: When removing unused code, associated comments may be removed.

**Solution**: Review diff before applying fixes:

```bash
ruff check . --diff --fix
# Review the output, then:
ruff check . --fix
```

### Import Sorting Breaking Circular Imports

**Problem**: isort rules reorganize imports causing circular import errors.

**Solution**: Use isort action comments:

```python
# isort: skip_file  # Skip entire file

import os
import sys

# isort: off
import module_b  # Must be after module_a
import module_a
# isort: on

from package import something
```

Or configure known dependencies:

```toml
[tool.ruff.lint.isort]
known-first-party = ["mypackage"]
force-sort-within-sections = true
```

## Suppression Issues

### noqa Comments Not Working

**Problem**: `# noqa` comments don't suppress violations.

**Causes**:
1. Wrong syntax
2. Wrong rule code
3. Wrong placement

**Correct Syntax**:

```python
# ✅ Correct
x = 1  # noqa: F841

# ❌ Wrong - missing colon
x = 1  # noqa F841

# ❌ Wrong - wrong case (though Ruff is case-insensitive for noqa)
x = 1  # NOQA: f841  # This actually works

# ✅ Multiple rules
x = 1  # noqa: F841, E501
```

**Multiline Strings**: Put noqa at end of string:

```python
"""Long docstring...
that spans multiple lines...
"""  # noqa: E501
```

**Import Blocks**: Put noqa on first import:

```python
import os  # noqa: I001
import abc
```

### Too Many noqa Comments

**Problem**: Codebase has excessive noqa comments hiding real issues.

**Solution**: 

1. Audit unused noqa comments:
```bash
ruff check . --extend-select RUF100
ruff check . --extend-select RUF100 --fix  # Remove unused noqa
```

2. Review and reduce noqa usage:
```bash
# Find all noqa comments
grep -r "# noqa" src/
```

3. Consider adjusting rules instead:
```toml
# Instead of many noqa comments for same rule
[tool.ruff.lint]
ignore = ["E501"]  # Ignore globally

# Or per-file
[tool.ruff.lint.per-file-ignores]
"legacy/**/*.py" = ["E501"]
```

## Performance Issues

### Slow on Large Codebase

**Problem**: Ruff takes too long on large projects.

**Causes**:
1. Linting `.venv` or `node_modules`
2. Very large files
3. Recursive symlinks

**Solution**:

```toml
[tool.ruff]
exclude = [
    ".bzr",
    ".direnv",
    ".eggs",
    ".git",
    ".git-rewrite",
    ".hg",
    ".mypy_cache",
    ".nox",
    ".pants.d",
    ".pytype",
    ".ruff_cache",
    ".svn",
    ".tox",
    ".venv",
    "__pypackages__",
    "_build",
    "buck-out",
    "build",
    "dist",
    "node_modules",
    "venv",
    "vendor",
]

# Extend default excludes rather than replacing
extend-exclude = ["generated/", "migrations/"]
```

### Cache Corruption

**Problem**: Inconsistent results between runs.

**Solution**: Clear and rebuild cache:

```bash
rm -rf .ruff_cache
ruff check .
```

## CI/CD Issues

### Different Results Locally vs CI

**Problem**: CI reports different violations than local development.

**Causes**:
1. Different Ruff versions
2. Different Python target versions
3. Missing configuration file in CI

**Solution**:

1. Pin Ruff version:
```toml
# pyproject.toml
[project.optional-dependencies]
dev = [
    "ruff==0.8.0",  # Pin specific version
]
```

2. Ensure consistent target version:
```toml
[tool.ruff]
target-version = "py311"  # Match CI Python version
```

3. Verify configuration is checked in:
```bash
git status pyproject.toml  # Should not be ignored
```

### Pre-commit Hook Not Fixing Files

**Problem**: Pre-commit runs ruff but doesn't show fixes.

**Solution**: Ensure `--fix` is passed:

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.0
    hooks:
      - id: ruff
        args: [--fix]  # This is required for auto-fix
```

## Best Practices Summary

1. **Start Small**: Begin with `["E", "F"]` and expand gradually
2. **Pin Versions**: Use exact version in CI and pre-commit
3. **Review Fixes**: Use `--diff` before applying fixes
4. **Minimize noqa**: Prefer configuration over inline suppressions
5. **Exclude Properly**: Ensure venv and generated code are excluded
6. **Sync Team Config**: Check pyproject.toml into version control
7. **Clear Cache**: When debugging, clear `.ruff_cache`
8. **Check Settings**: Use `ruff check --show-settings` to debug configuration
