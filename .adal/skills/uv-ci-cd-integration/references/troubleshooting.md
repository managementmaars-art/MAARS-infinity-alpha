# uv CI/CD Troubleshooting Guide

This guide covers common issues when using uv in CI/CD pipelines and their solutions.

## GitHub Actions Issues

### setup-uv Action Not Found

**Error:**
```
Error: Could not find version for astral-sh/setup-uv@v6
```

**Solution:**
```yaml
# Use correct action path
- uses: astral-sh/setup-uv@v6  # Correct

# Not this:
# - uses: setup-uv@v6  # Wrong
# - uses: astral-sh/uv@v6  # Wrong
```

**Verify:** Check https://github.com/astral-sh/setup-uv/releases for available versions

### Cache Not Working

**Symptoms:**
- Cache-hit shows false
- Dependencies reinstalled every run
- Slow CI times

**Diagnosis:**
```yaml
- name: Debug cache
  run: |
    echo "Cache location: ${{ runner.temp }}/_github_home"
    du -sh ~/.cache/uv/ 2>/dev/null || echo "Cache empty"
    uv cache dir
```

**Solutions:**

1. **Check cache-dependency-glob:**
   ```yaml
   - uses: astral-sh/setup-uv@v6
     with:
       cache-dependency-glob: "uv.lock"  # Must match actual file
   ```

2. **Verify uv.lock exists:**
   ```yaml
   - name: Verify lockfile
     run: test -f uv.lock || (echo "uv.lock missing"; exit 1)
   ```

3. **Check cache size limits:**
   - GitHub Actions: 5 GB per repository
   - If exceeded, oldest entries deleted
   - Solution: Prune cache regularly

4. **Reset cache:**
   ```bash
   # GitHub CLI
   gh actions-cache delete <cache-key> -R owner/repo

   # Or re-run job (GitHub UI)
   ```

### Matrix Jobs Not Using Cache

**Problem:** Each matrix job has separate cache

**Expected behavior:**
```yaml
strategy:
  matrix:
    python-version: ["3.11", "3.12", "3.13"]
```

Each Python version gets its own cache entry:
- `uv-3.11-<hash>`
- `uv-3.12-<hash>`
- `uv-3.13-<hash>`

**Solution:** First run might be slow per Python version, subsequent runs use cache

### Frozen Lockfile Out of Sync

**Error:**
```
error: lockfile is out of sync with dependencies
```

**Cause:** `uv.lock` doesn't match `pyproject.toml`

**Solution:**
```bash
# Update lockfile locally before committing
uv lock

# Or detect mismatch in CI
- name: Check lockfile
  run: uv lock --check
```

**In CI:**
```yaml
- name: Verify lockfile is up-to-date
  run: |
    uv lock --check || {
      echo "Run 'uv lock' locally to update uv.lock"
      exit 1
    }
```

### Permission Denied Installing

**Error:**
```
PermissionError: [Errno 13] Permission denied: '/.venv/lib/...'
```

**Cause:** Running as non-root, permissions issue

**Solution:**
```yaml
# For self-hosted runners
- name: Fix permissions
  run: |
    sudo chown -R $(whoami) ~/.cache/uv
    sudo chown -R $(whoami) .venv

# Or use setup-uv with proper isolation
- uses: astral-sh/setup-uv@v6
  with:
    enable-cache: true
```

## GitLab CI Issues

### Cache Directory Not Found

**Error:**
```
WARNING: cache.paths: ... does not exist
```

**Solution:**
```yaml
# Set cache directory before building
variables:
  UV_CACHE_DIR: .uv-cache

before_script:
  - mkdir -p .uv-cache
  - uv sync --all-extras --dev
```

### uv Command Not Found in After_script

**Error:**
```
sh: 1: uv: not found
```

**Solution:**
```yaml
variables:
  PATH: "${HOME}/.cargo/bin:${PATH}"

after_script:
  - uv cache prune
```

Or install in after_script:
```yaml
after_script:
  - curl -LsSf https://astral.sh/uv/install.sh | sh
  - export PATH="$HOME/.cargo/bin:$PATH"
  - uv cache prune
```

### Cache Key Conflicts Between Branches

**Problem:** Different branches share cache

**Solution:**
```yaml
cache:
  key: ${CI_COMMIT_REF_SLUG}  # Separate per branch
  paths:
    - .uv-cache
```

Or per-job:
```yaml
test:
  cache:
    key: test-${CI_COMMIT_REF_SLUG}
    paths:
      - .uv-cache
```

## Docker Build Issues

### uv Binary Not Found in Runtime Stage

**Error:**
```
/bin/sh: uv: not found
```

**Dockerfile:**
```dockerfile
FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
# ... build stage

FROM python:3.12-slim

# Missing: uv only copied in builder, not runtime
```

**Fix:**
```dockerfile
FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

FROM python:3.12-slim

WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
# uv not needed in runtime, only .venv
```

### Virtual Environment Not Active

**Error:**
```
ModuleNotFoundError: No module named 'requests'
```

**Dockerfile:**
```dockerfile
COPY --from=builder /app/.venv /app/.venv

# Missing: PATH not updated
CMD ["python", "-m", "myapp"]  # Uses system python, not .venv
```

**Fix:**
```dockerfile
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"
CMD ["python", "-m", "myapp"]  # Now uses .venv python
```

### Layer Cache Not Working

**Symptoms:** Docker rebuilds all layers despite unchanged dependencies

**Cause:** Wrong layer order
```dockerfile
# Wrong: application code before dependencies
COPY . .
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen
```

**Fix:**
```dockerfile
# Correct: dependencies before application code
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen
COPY . .
```

### Large Docker Image Size

**Diagnosis:**
```bash
docker history myapp:latest

# Check venv size
docker run --rm myapp:latest du -sh /.venv
```

**Solutions:**

1. **Use multi-stage builds:**
   ```dockerfile
   FROM builder AS runtime
   COPY --from=builder /app/.venv /app/.venv
   # Only copy venv, not build artifacts
   ```

2. **Remove dev dependencies:**
   ```dockerfile
   RUN uv sync --frozen --no-dev
   ```

3. **Use slimmer base:**
   ```dockerfile
   FROM python:3.12-slim  # Not python:3.12
   ```

4. **Compile bytecode (advanced):**
   ```dockerfile
   RUN uv sync --frozen --compile-bytecode
   # Then delete .py files if not needed
   ```

### Timezone Issues in Container

**Problem:** Wrong time in logs

**Solution:**
```dockerfile
ENV TZ=UTC
# Or
RUN apt-get install -y tzdata
ENV TZ=America/New_York
```

## Dependency Resolution Issues

### "No solution found when resolving dependencies"

**Error:**
```
error: No solution found when resolving dependencies
```

**Cause:** Conflicting version constraints

**Debug:**
```bash
uv tree  # Show dependency tree
uv tree --depth 2 | grep package-name
```

**Solutions:**

1. **Check for conflicts:**
   ```bash
   uv lock  # Try to regenerate
   ```

2. **Relax version constraints:**
   ```bash
   # Change from "requests==2.31.0" to "requests>=2.31.0"
   uv add "requests>=2.31.0"
   uv lock
   ```

3. **Use specific resolution strategy:**
   ```bash
   uv sync --resolution lowest   # Use oldest compatible
   uv sync --resolution highest  # Use newest compatible
   ```

### Dependency Conflicts in CI vs Local

**Cause:** Different Python versions or platforms

**Solution:**
```bash
# Pin Python version
uv python pin 3.12

# Check markers match CI environment
uv tree --universal
```

### Build Failures for Native Extensions

**Error:**
```
error: command 'gcc' failed: No such file or directory
```

**Docker fix:**
```dockerfile
FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
RUN uv sync --no-dev
```

**GitHub Actions fix:**
```yaml
- uses: astral-sh/setup-uv@v6
- run: |
    sudo apt-get update
    sudo apt-get install -y build-essential python3-dev
    uv sync --all-extras --dev
```

## Performance Issues

### Very Slow First Run

**Expected:**
- Cold run: 30-60 seconds (resolution + download)
- Warm run: 3-10 seconds (from cache)

**If consistently slow:**

1. **Check network:**
   ```bash
   ping pypi.org
   curl -I https://pypi.org/simple/
   ```

2. **Check timeout:**
   ```bash
   # Increase if behind proxy
   UV_HTTP_TIMEOUT=300 uv sync
   ```

3. **Use custom mirror:**
   ```yaml
   # GitHub Actions
   - run: uv sync --index-url https://mirror.example.com/simple

   # Docker
   RUN uv sync --index-url https://mirror.example.com/simple
   ```

### Cache Hit But Still Slow

**Cause:** Re-resolving dependencies (no lockfile cache)

**Solution:** Ensure lockfile is cached

```yaml
# GitHub Actions
cache-dependency-glob: "uv.lock"

# GitLab
key: ${CI_COMMIT_REF_SLUG}
paths:
  - .uv-cache
```

## Environment Variable Issues

### Environment Variable Not Available in Container

**Dockerfile:**
```dockerfile
RUN echo $MY_VAR  # Empty during build
```

**Solution:**
```dockerfile
# Pass at build time
ARG MY_VAR
RUN echo $MY_VAR

# Or pass at runtime
CMD ["sh", "-c", "echo $MY_VAR && python -m myapp"]
```

**Usage:**
```bash
docker build --build-arg MY_VAR=value .
docker run -e MY_VAR=value myapp
```

### UV_PYTHON_PREFERENCE Not Respected

**Problem:** Still using system Python

**Solution:**
```bash
# Set before running uv
export UV_PYTHON_PREFERENCE=managed
uv python install 3.12
uv sync

# Or in pyproject.toml
[tool.uv]
python-preference = "managed"
```

## Debugging Commands

### Enable Verbose Output

```bash
# GitHub Actions
- name: Verbose sync
  run: uv --verbose sync

# Docker
RUN uv --verbose sync

# GitLab
script:
  - uv --verbose sync
```

### Check Installation Details

```bash
# Show what would be installed
uv sync --dry-run

# Show dependency tree
uv tree

# Show specific package
uv pip show requests

# Verify lockfile
uv lock --check
```

### Cache Diagnostics

```bash
# Show cache location
uv cache dir

# Show cache size
du -sh $(uv cache dir)

# List cache contents
uv cache dir | xargs ls -la

# Clear cache
uv cache clean
uv cache prune
```

## Common Solutions Summary

| Problem | Solution |
|---------|----------|
| Slow CI | Enable caching, use frozen lockfile |
| "Command not found" | Add to PATH, check installation |
| Large Docker image | Use multi-stage builds, `--no-dev` |
| Permission denied | Check file ownership, use non-root |
| Lockfile out of sync | Run `uv lock` locally |
| Dependency conflict | Check `uv tree`, relax constraints |
| Network timeout | Set `UV_HTTP_TIMEOUT`, use mirror |
| Matrix cache issues | Use `cache-dependency-glob` |
| Version mismatch | Pin Python with `.python-version` |

## Getting Help

1. **Check uv documentation:** https://docs.astral.sh/uv/
2. **GitHub Issues:** https://github.com/astral-sh/uv/issues
3. **Discord:** https://discord.gg/astral-sh
4. **Include when reporting:**
   - `uv --version`
   - `uv tree`
   - `uv lock --check`
   - Full error output with `--verbose`
