# Ruff Rule Selection Reference

Comprehensive guide to selecting and configuring Ruff linting rules.

## Rule Code Structure

Ruff mirrors Flake8's rule code system. Each rule code consists of:
- **Prefix**: 1-3 letters indicating the source (e.g., `F` for Pyflakes, `E` for pycodestyle)
- **Number**: 3 digits identifying the specific rule (e.g., `401`)

Example: `F401` = Pyflakes rule 401 (unused import)

## Configuration Methods

### Using lint.select

The primary way to specify which rules to enable:

```toml
[tool.ruff.lint]
select = ["E", "F", "UP", "B"]
```

This **replaces** the default rule set with only the specified rules.

### Using lint.extend-select

Add rules to the existing selection (including defaults):

```toml
[tool.ruff.lint]
extend-select = ["UP", "B"]  # Add to defaults
```

### Using lint.ignore

Disable specific rules from the selected set:

```toml
[tool.ruff.lint]
select = ["E", "F"]
ignore = ["E501", "F401"]
```

### Priority Order

When rules are specified from multiple sources, priority is:

1. **CLI arguments** (highest priority)
   - `--select`, `--extend-select`, `--ignore`
2. **Current pyproject.toml**
3. **Inherited pyproject.toml files** (lowest priority)

Example:
```bash
# Config: select = ["E", "F"], ignore = ["F401"]

ruff check --select F401   # Only enforces F401
ruff check --extend-select B  # Enforces E, F, B (except F401)
```

## Complete Rule Prefix Reference

### Core Linting Rules

| Prefix | Source | Description | Recommended |
|--------|--------|-------------|-------------|
| **E** | pycodestyle | Style errors (indentation, whitespace) | ✅ Yes |
| **W** | pycodestyle | Style warnings | ⚠️ Optional |
| **F** | Pyflakes | Logical errors (undefined names, unused imports) | ✅ Yes |

### Code Quality

| Prefix | Source | Description | Recommended |
|--------|--------|-------------|-------------|
| **B** | flake8-bugbear | Common bugs and design problems | ✅ Yes |
| **C4** | flake8-comprehensions | Better comprehensions | ✅ Yes |
| **SIM** | flake8-simplify | Code simplification | ✅ Yes |
| **PIE** | flake8-pie | Misc lints | ⚠️ Optional |
| **RET** | flake8-return | Return statement issues | ⚠️ Optional |
| **ARG** | flake8-unused-arguments | Unused function arguments | ⚠️ Optional |

### Modern Python

| Prefix | Source | Description | Recommended |
|--------|--------|-------------|-------------|
| **UP** | pyupgrade | Python version upgrades | ✅ Yes |
| **FA** | flake8-future-annotations | Future annotations | ⚠️ If using `from __future__` |
| **YTT** | flake8-2020 | sys.version checks | ⚠️ Optional |

### Import Management

| Prefix | Source | Description | Recommended |
|--------|--------|-------------|-------------|
| **I** | isort | Import sorting and organization | ✅ Yes |
| **ICN** | flake8-import-conventions | Import alias conventions | ⚠️ Optional |
| **TID** | flake8-tidy-imports | Banned imports | ⚠️ Optional |

### Type Annotations

| Prefix | Source | Description | Recommended |
|--------|--------|-------------|-------------|
| **ANN** | flake8-annotations | Type annotation presence | ⚠️ If using type hints |
| **TCH** | flake8-type-checking | TYPE_CHECKING block usage | ⚠️ If using type hints |

### Naming Conventions

| Prefix | Source | Description | Recommended |
|--------|--------|-------------|-------------|
| **N** | pep8-naming | PEP 8 naming conventions | ⚠️ Optional |

### Documentation

| Prefix | Source | Description | Recommended |
|--------|--------|-------------|-------------|
| **D** | pydocstyle | Docstring conventions | ⚠️ If enforcing docs |

### Security

| Prefix | Source | Description | Recommended |
|--------|--------|-------------|-------------|
| **S** | flake8-bandit | Security issues | ✅ Yes |

### Testing

| Prefix | Source | Description | Recommended |
|--------|--------|-------------|-------------|
| **PT** | flake8-pytest-style | pytest best practices | ✅ If using pytest |

### Error Handling

| Prefix | Source | Description | Recommended |
|--------|--------|-------------|-------------|
| **EM** | flake8-errmsg | Error message formatting | ⚠️ Optional |
| **TRY** | tryceratops | Exception handling | ⚠️ Optional |
| **RSE** | flake8-raise | Raise statement issues | ⚠️ Optional |

### Logging

| Prefix | Source | Description | Recommended |
|--------|--------|-------------|-------------|
| **G** | flake8-logging-format | Logging format strings | ⚠️ Optional |
| **LOG** | flake8-logging | Logging best practices | ⚠️ Optional |

### Debugging

| Prefix | Source | Description | Recommended |
|--------|--------|-------------|-------------|
| **T10** | flake8-debugger | Debugger imports | ✅ Yes |
| **T20** | flake8-print | Print statements | ✅ Yes |

### Datetime

| Prefix | Source | Description | Recommended |
|--------|--------|-------------|-------------|
| **DTZ** | flake8-datetimez | Timezone-aware datetime | ✅ Yes |

### Async

| Prefix | Source | Description | Recommended |
|--------|--------|-------------|-------------|
| **ASYNC** | flake8-async | Async best practices | ⚠️ If using async |

### Django

| Prefix | Source | Description | Recommended |
|--------|--------|-------------|-------------|
| **DJ** | flake8-django | Django best practices | ✅ If using Django |

### NumPy/Pandas

| Prefix | Source | Description | Recommended |
|--------|--------|-------------|-------------|
| **NPY** | NumPy-specific | NumPy deprecations | ✅ If using NumPy |
| **PD** | pandas-vet | pandas best practices | ✅ If using pandas |

### Ruff-Specific

| Prefix | Source | Description | Recommended |
|--------|--------|-------------|-------------|
| **RUF** | Ruff | Ruff-specific rules | ✅ Yes |

### Special

| Prefix | Description |
|--------|-------------|
| **ALL** | Enable all rules (use with caution) |

## Recommended Configurations

### Minimal (Getting Started)

For new projects or migrating from no linter:

```toml
[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "F",   # Pyflakes
]
```

### Balanced (Recommended for Most Projects)

Good coverage without being overwhelming:

```toml
[tool.ruff.lint]
select = [
    "E",     # pycodestyle errors
    "F",     # Pyflakes
    "UP",    # pyupgrade
    "B",     # flake8-bugbear
    "SIM",   # flake8-simplify
    "I",     # isort
]
ignore = [
    "E501",  # Line too long (formatter handles)
]
```

### Comprehensive (Strict Projects)

Maximum coverage for strict codebases:

```toml
[tool.ruff.lint]
select = [
    # Core
    "E",      # pycodestyle errors
    "W",      # pycodestyle warnings
    "F",      # Pyflakes
    
    # Code quality
    "B",      # flake8-bugbear
    "C4",     # flake8-comprehensions
    "SIM",    # flake8-simplify
    "PIE",    # flake8-pie
    
    # Modern Python
    "UP",     # pyupgrade
    
    # Imports
    "I",      # isort
    
    # Naming
    "N",      # pep8-naming
    
    # Security
    "S",      # flake8-bandit
    
    # Debugging
    "T10",    # flake8-debugger
    "T20",    # flake8-print
    
    # Datetime
    "DTZ",    # flake8-datetimez
    
    # Ruff-specific
    "RUF",    # Ruff rules
]
ignore = [
    "E501",   # Line length (formatter)
    "S101",   # Assert usage (tests)
]

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["S101", "PLR2004"]
"conftest.py" = ["S101"]
```

### Web Application (FastAPI/Flask)

Optimized for web frameworks:

```toml
[tool.ruff.lint]
select = [
    "E", "F", "UP", "B", "SIM", "I",
    "S",      # Security (important for web)
    "DTZ",    # Timezone-aware dates
    "T20",    # No print statements
    "RUF",
]
ignore = [
    "E501",
    "B008",   # Function calls in default arguments (needed for Depends())
]

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["S101"]
"alembic/**/*.py" = ["E501"]
```

### Data Science / ML

For pandas, numpy, and ML projects:

```toml
[tool.ruff.lint]
select = [
    "E", "F", "UP", "B", "SIM", "I",
    "NPY",    # NumPy
    "PD",     # pandas
    "RUF",
]
ignore = [
    "E501",   # Long lines common in data work
    "PD901",  # Generic variable name 'df'
]

[tool.ruff.lint.per-file-ignores]
"notebooks/**/*.py" = ["E402", "T20"]
```

### Library / Package

For reusable Python packages:

```toml
[tool.ruff.lint]
select = [
    "E", "W", "F", "UP", "B", "SIM", "I",
    "N",      # Strict naming
    "D",      # Docstrings
    "ANN",    # Type annotations
    "C4",     # Comprehensions
    "RUF",
]
ignore = [
    "E501",
    "D100",   # Module docstring
    "D104",   # Package docstring
    "ANN101", # Self type annotation
    "ANN102", # cls type annotation
]

[tool.ruff.lint.pydocstyle]
convention = "google"  # or "numpy"
```

## Per-File Ignores

Override rules for specific files or directories:

```toml
[tool.ruff.lint.per-file-ignores]
# Allow assert in tests
"tests/**/*.py" = ["S101", "PLR2004"]
"test_*.py" = ["S101"]
"*_test.py" = ["S101"]
"conftest.py" = ["S101"]

# Allow unused imports in __init__.py (re-exports)
"__init__.py" = ["F401"]

# Allow late imports in specific directories
"**/{tests,docs,tools}/*" = ["E402"]

# Generated code
"**/generated/**/*.py" = ["E501", "F401", "E402"]

# Migrations (often auto-generated)
"**/migrations/**/*.py" = ["E501"]

# Scripts may use print
"scripts/**/*.py" = ["T20"]

# Notebooks exported to Python
"notebooks/**/*.py" = ["E402", "T20", "F401"]
```

## Extending with Additional Rules

### Adding Rules Incrementally

Start minimal and add rules over time:

```toml
# Phase 1: Core
[tool.ruff.lint]
select = ["E", "F"]

# Phase 2: Add quality rules
select = ["E", "F", "B", "SIM"]

# Phase 3: Add import sorting
select = ["E", "F", "B", "SIM", "I"]

# Phase 4: Add pyupgrade
select = ["E", "F", "B", "SIM", "I", "UP"]
```

### Using extend-select for Additive Changes

```toml
[tool.ruff.lint]
# Keep defaults and add more
extend-select = [
    "UP",   # pyupgrade
    "B",    # flake8-bugbear
]
```

## Plugin-Specific Configuration

### isort Configuration

```toml
[tool.ruff.lint.isort]
known-first-party = ["mypackage", "myotherpackage"]
known-third-party = ["requests", "fastapi"]
force-single-line = false
force-sort-within-sections = true
split-on-trailing-comma = true
section-order = ["future", "standard-library", "third-party", "first-party", "local-folder"]
```

### pydocstyle Configuration

```toml
[tool.ruff.lint.pydocstyle]
convention = "google"  # or "numpy" or "pep257"
```

### flake8-annotations Configuration

```toml
[tool.ruff.lint.flake8-annotations]
allow-star-arg-any = true
ignore-fully-untyped = true
mypy-init-return = true
```

### flake8-bugbear Configuration

```toml
[tool.ruff.lint.flake8-bugbear]
extend-immutable-calls = ["fastapi.Depends", "fastapi.Query"]
```

### flake8-quotes Configuration

```toml
[tool.ruff.lint.flake8-quotes]
docstring-quotes = "double"
inline-quotes = "double"
multiline-quotes = "double"
```

## Viewing Available Rules

### List All Rules

```bash
ruff linter  # Show all available rules
```

### Explain a Specific Rule

```bash
ruff rule F401  # Show detailed explanation of F401
```

### Show Applied Rules

```bash
ruff check . --show-settings  # Show full configuration
```

### Show Statistics

```bash
ruff check . --statistics  # Show violation counts by rule
```

## Migration from Flake8

### Common Flake8 Plugin Mappings

| Flake8 Plugin | Ruff Prefix |
|---------------|-------------|
| flake8 core | E, W |
| pyflakes | F |
| flake8-bugbear | B |
| flake8-comprehensions | C4 |
| flake8-simplify | SIM |
| isort | I |
| pyupgrade | UP |
| flake8-bandit | S |
| pep8-naming | N |
| pydocstyle | D |
| flake8-annotations | ANN |
| flake8-pytest-style | PT |
| flake8-print | T20 |
| flake8-debugger | T10 |

### Converting .flake8 to pyproject.toml

Before (.flake8):
```ini
[flake8]
max-line-length = 88
select = E,F,W,B,B9
ignore = E501,W503
per-file-ignores =
    __init__.py:F401
    tests/*:S101
```

After (pyproject.toml):
```toml
[tool.ruff]
line-length = 88

[tool.ruff.lint]
select = ["E", "F", "W", "B"]
ignore = ["E501"]

[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["F401"]
"tests/**/*.py" = ["S101"]
```
