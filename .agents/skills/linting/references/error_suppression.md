# Ruff Error Suppression Patterns

Comprehensive guide to suppressing lint errors in Ruff.

## Overview

Ruff supports multiple mechanisms for suppressing lint errors:
1. **Configuration-based**: Global or per-file ignores in config files
2. **Comment-based**: Inline, file-level, and block-level suppressions

## Configuration-Based Suppression

### Global Ignores

Ignore rules across the entire project:

```toml
[tool.ruff.lint]
ignore = [
    "E501",   # Line too long
    "W503",   # Line break before binary operator
]
```

### Per-File Ignores

Ignore rules for specific files or directories:

```toml
[tool.ruff.lint.per-file-ignores]
# Single file
"src/generated/parser.py" = ["E501", "F401"]

# All files matching pattern
"__init__.py" = ["F401"]

# All files in directory (recursive)
"tests/**/*.py" = ["S101", "PLR2004"]

# Multiple directories
"**/{tests,docs,tools}/*" = ["E402"]

# By file suffix
"*_test.py" = ["S101"]
"test_*.py" = ["S101"]
```

### Pattern Examples

| Pattern | Matches |
|---------|---------|
| `"file.py"` | Any file named `file.py` |
| `"path/to/file.py"` | Specific file at that path |
| `"*.py"` | All Python files |
| `"tests/*.py"` | Python files directly in tests/ |
| `"tests/**/*.py"` | All Python files in tests/ (recursive) |
| `"**/__init__.py"` | All __init__.py files anywhere |

## Comment-Based Suppression

### Line-Level Suppression (noqa)

Suppress violations on a single line:

```python
# Suppress specific rule
x = 1  # noqa: F841

# Suppress multiple rules
i = 1  # noqa: E741, F841

# Suppress all rules (avoid this pattern)
x = 1  # noqa
```

### noqa Syntax Rules

1. **Case insensitive**: `noqa`, `NOQA`, `NoQa` all work
2. **Colon required for codes**: `# noqa: F401` (not `# noqa F401`)
3. **Comma-separated**: `# noqa: F401, E501`
4. **Whitespace optional**: `#noqa:F401` works but `# noqa: F401` is clearer

### Correct vs Incorrect Examples

```python
# ✅ Correct
x = 1  # noqa: F841
x = 1  # noqa: F841, E501
x = 1  #noqa: F841  # Works but less readable

# ❌ Incorrect
x = 1  # noqa F841    # Missing colon
x = 1  # noqa:F841    # Works, but add space after colon for readability
```

### Multi-line Strings

For docstrings and multi-line strings, place noqa at the end:

```python
"""This is a very long docstring that exceeds the line length limit
and needs to be suppressed because it contains important information.
"""  # noqa: E501
```

### Import Blocks

For isort suppressions, place noqa on the first import:

```python
import os  # noqa: I001
import abc

# The noqa applies to the entire import block
```

## File-Level Suppression

Suppress violations across an entire file:

```python
# At the top of the file

# Suppress all violations
# ruff: noqa

# Suppress specific rule
# ruff: noqa: F841

# Suppress multiple rules
# ruff: noqa: F841, E501
```

### Placement

File-level noqa comments must be on their own line (not inline):

```python
# ✅ Correct - own line
# ruff: noqa: F401

# ❌ Incorrect - inline
import os  # ruff: noqa  # This is line-level, not file-level
```

### Flake8 Compatibility

Ruff also respects Flake8's file-level suppression:

```python
# flake8: noqa
# flake8: noqa: F401
```

## Block-Level Suppression (Preview Mode)

Suppress violations within a range of code using disable/enable comments.

**Note**: This feature is only available in preview mode.

### Basic Usage

```python
# ruff: disable[E501]
VALUE_1 = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod"
VALUE_2 = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod"
VALUE_3 = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod"
# ruff: enable[E501]
```

### Multiple Rules

```python
# ruff: disable[E741, F841]
i = 1
l = 2  # noqa: E741 would also work
O = 3
# ruff: enable[E741, F841]
```

### Syntax Rules

1. **Case sensitive**: Must use `disable` and `enable` exactly
2. **Square brackets**: `[E501]` not `(E501)` or `: E501`
3. **Matching codes**: Enable must have same codes as disable
4. **Same indentation**: Must be at same indentation level

### Implicit Range End

If no matching enable comment is found, the range ends at the next less-indented scope:

```python
def foo():
    # ruff: disable[E741, F841]
    i = 1
    if True:
        O = 1
    l = 1
# implicit end of range

foo()  # Not suppressed
```

**Warning**: A `RUF104` diagnostic is produced for implicit ranges. Use explicit enable comments.

### What Doesn't Work

```python
# ❌ Wrong - blanket suppression not supported
# ruff: disable

# ❌ Wrong - mismatched codes
# ruff: disable[E501]
# ruff: enable[E741]  # Doesn't match

# ❌ Wrong - different order
# ruff: disable[E501, F841]
# ruff: enable[F841, E501]  # Order must match
```

## isort Action Comments

Ruff respects isort's action comments for import sorting:

### Skip Entire File

```python
# isort: skip_file
import sys
import os
import abc
```

### Skip Single Import

```python
import os
import sys  # isort: skip
import abc
```

### Enable/Disable Regions

```python
import os

# isort: off
import module_b  # Must be before module_a
import module_a
# isort: on

import abc
```

### Force Split

```python
import os

# isort: split

import sys  # New import group after split
```

### Ruff-Prefixed Variants

These variants work identically and are clearer:

```python
# ruff: isort: skip_file
# ruff: isort: on
# ruff: isort: off
# ruff: isort: skip
# ruff: isort: split
```

## Detecting Unused Suppressions

Ruff includes `RUF100` to detect unused noqa comments:

```bash
# Find unused noqa comments
ruff check . --extend-select RUF100

# Remove unused noqa comments
ruff check . --extend-select RUF100 --fix
```

Example:

```python
# Before: noqa is unused (violation doesn't exist)
x = 1  # noqa: E501  # Line isn't actually too long

# After --fix:
x = 1
```

## Adding noqa Comments Automatically

Ruff can automatically add noqa comments to all violations:

```bash
ruff check . --add-noqa
```

This adds appropriate noqa comments to all lines with violations:

```python
# Before
x = 1  # Unused variable

# After --add-noqa
x = 1  # noqa: F841
```

**Caution**: This is useful for migrations but can hide real issues. Review manually.

## Best Practices

### 1. Prefer Configuration Over Comments

```toml
# Instead of many noqa comments
[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["S101"]
```

### 2. Be Specific with Codes

```python
# ✅ Good - specific
x = 1  # noqa: F841

# ❌ Avoid - blanket suppression
x = 1  # noqa
```

### 3. Add Explanations

```python
# ✅ Good - explains why
x = 1  # noqa: F841 - Required for side effect

# ❌ Less helpful
x = 1  # noqa: F841
```

### 4. Minimize Suppressions

Review if you have many noqa comments for the same rule - consider:
- Adjusting the rule configuration
- Adding to per-file ignores
- Disabling the rule if it's too noisy

### 5. Audit Regularly

```bash
# Count noqa usage
grep -r "noqa" src/ | wc -l

# Find unused noqa
ruff check . --extend-select RUF100
```

### 6. Document Team Decisions

```toml
[tool.ruff.lint]
ignore = [
    # E501: We use a formatter that handles line length
    "E501",
    # S101: We use assert extensively in tests
    "S101",
]
```

## Suppression Priority

When multiple suppression methods apply:

1. **Line-level noqa** (highest priority)
2. **Block-level disable/enable**
3. **File-level noqa**
4. **Per-file ignores in config**
5. **Global ignore in config** (lowest priority)

Example:

```python
# ruff: noqa: F841  # File-level suppression

def foo():
    x = 1  # F841 is suppressed by file-level comment
    y = 2  # noqa: F841  # Would also suppress (line-level)
```

## Troubleshooting

### noqa Not Working

1. **Check syntax**:
   ```python
   # ✅ Correct
   x = 1  # noqa: F841
   
   # ❌ Missing colon
   x = 1  # noqa F841
   ```

2. **Check rule code**:
   ```bash
   ruff rule F841  # Verify rule code exists
   ```

3. **Check file is being linted**:
   ```bash
   ruff check path/to/file.py
   ```

### Per-file Ignore Not Working

1. **Check glob pattern**:
   ```toml
   # For recursive matching, use **
   "tests/**/*.py" = ["S101"]  # ✅
   "tests/*.py" = ["S101"]  # Only direct children
   ```

2. **Check file is included**:
   ```bash
   ruff check path/to/file.py --show-settings
   ```

### Block Suppression Not Working

1. **Ensure preview mode is enabled**:
   ```toml
   [tool.ruff]
   preview = true
   ```

2. **Check matching codes and indentation**

### Too Many Violations After Migration

1. **Start with global ignore, then refine**:
   ```toml
   [tool.ruff.lint]
   ignore = ["E501"]  # Temporarily ignore all
   ```

2. **Add noqa comments for remaining issues**:
   ```bash
   ruff check . --add-noqa
   ```

3. **Review and reduce suppressions over time**
