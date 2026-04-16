# Ruff Linting Quickstart

A comprehensive guide to getting started with Ruff for Python linting.

## Installation

### Using uv (Recommended)

```bash
uv pip install ruff
```

### Using pip

```bash
pip install ruff
```

### Using pipx (Global Installation)

```bash
pipx install ruff
```

### Using Homebrew (macOS)

```bash
brew install ruff
```

### Verify Installation

```bash
ruff --version
```

## Basic Usage

### Lint Current Directory

```bash
ruff check .
```

### Lint Specific Files or Directories

```bash
ruff check src/
ruff check src/main.py src/utils.py
ruff check path/to/project/
```

### Auto-fix Issues

```bash
# Apply safe fixes only (default)
ruff check . --fix

# Apply all fixes including unsafe ones
ruff check . --fix --unsafe-fixes
```

### Watch Mode (Development)

```bash
ruff check --watch
```

Ruff will automatically re-lint files when they change.

## Quick Configuration

### Minimal pyproject.toml

```toml
[tool.ruff]
line-length = 88
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F"]
```

### Recommended pyproject.toml

```toml
[tool.ruff]
line-length = 88
target-version = "py311"
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
]

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors
    "F",    # Pyflakes
    "UP",   # pyupgrade
    "B",    # flake8-bugbear
    "SIM",  # flake8-simplify
    "I",    # isort
]
ignore = [
    "E501",  # Line too long (handled by formatter)
]
fixable = ["ALL"]
unfixable = []

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["S101"]  # Allow assert in tests

[tool.ruff.lint.isort]
known-first-party = ["your_package_name"]
```

## Output Formats

### Human-Readable (Default)

```bash
ruff check .
```

Output:
```
src/main.py:10:5: F841 Local variable `x` is assigned to but never used
src/utils.py:25:1: E302 Expected 2 blank lines, found 1
Found 2 errors.
```

### GitHub Actions Format

```bash
ruff check . --output-format github
```

Creates inline annotations in GitHub pull requests.

### JSON Format

```bash
ruff check . --output-format json
```

Useful for programmatic processing.

### SARIF Format

```bash
ruff check . --output-format sarif
```

For security scanning tools and code analysis platforms.

## CI Integration

### GitHub Actions

```yaml
name: Lint

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install uv
        uses: astral-sh/setup-uv@v4
      
      - name: Install dependencies
        run: uv sync
      
      - name: Run Ruff linter
        run: uv run ruff check . --output-format github
      
      - name: Run Ruff formatter check
        run: uv run ruff format --check
```

### Using Official Ruff Action

```yaml
name: Lint

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/ruff-action@v3
```

### GitLab CI

```yaml
lint:
  image: python:3.11
  before_script:
    - pip install ruff
  script:
    - ruff check .
    - ruff format --check
```

## Pre-commit Integration

### Install pre-commit

```bash
pip install pre-commit
```

### Configure .pre-commit-config.yaml

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.0
    hooks:
      # Run the linter with auto-fix
      - id: ruff
        args: [--fix]
      # Run the formatter
      - id: ruff-format
```

### Install Hooks

```bash
pre-commit install
```

### Run Manually

```bash
pre-commit run --all-files
```

## Common Commands Reference

| Command | Description |
|---------|-------------|
| `ruff check .` | Lint all files |
| `ruff check . --fix` | Lint and apply safe fixes |
| `ruff check . --fix --unsafe-fixes` | Apply all fixes |
| `ruff check . --diff` | Show diff of what would change |
| `ruff check . --show-fixes` | Show available fixes |
| `ruff check . --statistics` | Show violation statistics |
| `ruff check --watch` | Watch mode |
| `ruff rule F401` | Explain rule F401 |
| `ruff check . --add-noqa` | Add noqa comments to all violations |
| `ruff format .` | Format all files |
| `ruff format --check` | Check if files are formatted |

## Editor Integration

### VS Code

Install the official [Ruff extension](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff).

Settings (`.vscode/settings.json`):
```json
{
    "[python]": {
        "editor.formatOnSave": true,
        "editor.defaultFormatter": "charliermarsh.ruff",
        "editor.codeActionsOnSave": {
            "source.fixAll.ruff": "explicit",
            "source.organizeImports.ruff": "explicit"
        }
    }
}
```

### Cursor

Install the Ruff extension from the marketplace.

Settings:
```json
{
    "[python]": {
        "editor.formatOnSave": true,
        "editor.defaultFormatter": "charliermarsh.ruff",
        "editor.codeActionsOnSave": {
            "source.fixAll.ruff": "explicit"
        }
    }
}
```

### Neovim (with nvim-lspconfig)

```lua
require('lspconfig').ruff.setup({
  init_options = {
    settings = {
      lint = {
        enable = true,
      },
      format = {
        enable = true,
      },
    },
  },
})
```

## Next Steps

1. Start with minimal rules (`E`, `F`) and run `ruff check .`
2. Fix existing issues with `ruff check . --fix`
3. Gradually enable more rules (see [rule_selection.md](rule_selection.md))
4. Set up pre-commit hooks for automatic linting
5. Integrate into CI/CD pipeline
