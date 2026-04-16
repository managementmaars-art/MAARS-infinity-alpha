# Cache Optimization Strategies for uv in CI/CD

Proper caching can reduce CI/CD pipeline time from 2-3 minutes to 10-30 seconds on warm runs. This guide covers cache strategies across different platforms.

## GitHub Actions Cache Optimization

### Basic Cache Configuration

```yaml
- name: Install uv
  uses: astral-sh/setup-uv@v6
  with:
    enable-cache: true
    cache-dependency-glob: "uv.lock"  # Track changes to lockfile
```

**How it works:**
- Caches `~/.cache/uv/` (default uv cache location)
- Cache key: `uv-<python-version>-<uv.lock hash>`
- Invalidates when: Python version changes OR uv.lock changes

### Advanced: Multiple Dependency Groups

```yaml
steps:
  - uses: actions/checkout@v4

  - name: Install uv
    uses: astral-sh/setup-uv@v6
    with:
      enable-cache: true
      cache-dependency-glob: "uv.lock"

  # Cache is used here automatically
  - name: Install all dependencies
    run: uv sync --all-extras --dev

  # Separate cache keys for different groups
  - name: Install specific groups
    run: |
      uv sync --group lint --group test
      uv sync --group docs
```

### Cache Size Management

```yaml
# Monitor cache hit/miss ratio
- name: Show cache stats
  run: |
    uv cache dir          # Show cache location
    du -sh ~/.cache/uv/   # Show cache size
```

**Cache is typically:**
- First run: 200-500 MB (depends on dependencies)
- Subsequent runs: 50-200 MB increase per new package

**Reduce cache size:**
```yaml
- name: Clean cache before archiving
  run: |
    uv cache prune         # Remove unused entries
    uv cache clean         # Nuclear option (clears everything)
```

### Matrix Testing Cache Isolation

```yaml
strategy:
  matrix:
    python-version: ["3.11", "3.12", "3.13"]

steps:
  - uses: astral-sh/setup-uv@v6
    with:
      enable-cache: true
      cache-dependency-glob: "uv.lock"
      # Each Python version gets separate cache automatically
```

**Cache keys per Python:**
- Python 3.11: `uv-3.11-<hash>`
- Python 3.12: `uv-3.12-<hash>`
- Python 3.13: `uv-3.13-<hash>`

Each matrix job maintains its own cache, preventing cross-contamination.

### Force Cache Refresh

```yaml
# Option 1: Include timestamp (manual refresh)
- name: Install uv
  uses: astral-sh/setup-uv@v6
  with:
    enable-cache: true
    cache-dependency-glob: "uv.lock"
  env:
    CACHE_BUSTER: ${{ secrets.CACHE_BUSTER_TOKEN }}

# Option 2: Re-run failed job (automatic refresh via GitHub UI)
# Option 3: Use workflow_dispatch with cache clear
```

## GitLab CI Cache Optimization

### Basic GitLab Cache

```yaml
variables:
  UV_CACHE_DIR: .uv-cache

cache:
  key: ${CI_COMMIT_REF_SLUG}
  paths:
    - .uv-cache

before_script:
  - uv sync --all-extras --dev
```

**Key components:**
- `${CI_COMMIT_REF_SLUG}`: Separate cache per branch
- `.uv-cache`: uv's cache directory (relative to project root)

### Per-Job Cache Control

```yaml
# Merge default cache with custom paths
test:
  stage: test
  cache:
    key: ${CI_COMMIT_REF_SLUG}-test
    paths:
      - .uv-cache
      - .pytest-cache
  script:
    - uv run pytest

lint:
  stage: lint
  cache:
    key: ${CI_COMMIT_REF_SLUG}-lint
    paths:
      - .uv-cache
  script:
    - uv run ruff check .
```

### Disable Cache for Specific Jobs

```yaml
# Force fresh install (useful for validation)
test:fresh:
  stage: test
  cache: {}  # Disable caching
  script:
    - rm -rf .uv-cache
    - uv sync --all-extras --dev
    - uv run pytest
```

### Matrix Caching in GitLab

```yaml
# Use matrix with different cache keys
test:
  stage: test
  parallel:
    matrix:
      - PYTHON_VERSION: ["3.11", "3.12", "3.13"]
  image: python:${PYTHON_VERSION}
  cache:
    key: cache-${CI_COMMIT_REF_SLUG}-${PYTHON_VERSION}
    paths:
      - .uv-cache
  before_script:
    - curl -LsSf https://astral.sh/uv/install.sh | sh
    - export PATH="$HOME/.cargo/bin:$PATH"
    - uv python install ${PYTHON_VERSION}
  script:
    - uv sync --all-extras --dev
    - uv run pytest
```

### Large Cache Management

```yaml
# Prune before caching
after_script:
  - uv cache prune --ci  # Optimized for CI environments

# Or set explicit cache size limit
variables:
  UV_CACHE_DIR: .uv-cache
  # Note: uv doesn't have built-in size limit, but you can monitor
```

## Docker Layer Caching

### Optimal Layer Structure

```dockerfile
# Layer 1: Base image and uv
FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Layer 2: Dependencies (cached until pyproject.toml or uv.lock changes)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Layer 3: Application code (rebuilt on code changes only)
COPY . .

CMD ["python", "-m", "myapp"]
```

**Layer cache hits:**
- If only `.py` files change: reuse layers 1-2
- If dependencies change: rebuild only layer 2
- If base image version changes: rebuild all layers

### Buildkit Cache Mounts

```dockerfile
# Enable buildkit for better caching
# Set DOCKER_BUILDKIT=1 before building

FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app
COPY pyproject.toml uv.lock ./

# Cache uv's cache directory between builds
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# ... rest of build
```

**Usage:**
```bash
DOCKER_BUILDKIT=1 docker build -t myapp .
```

### Docker Compose Cache Strategy

```yaml
services:
  builder:
    build:
      context: .
      dockerfile: Dockerfile
      cache_from:
        - type=registry,ref=myregistry/myapp:latest
    image: myregistry/myapp:latest

  app:
    depends_on:
      - builder
```

## Cross-Platform Caching Best Practices

### 1. Lockfile Always in Cache Key

**GitHub Actions:**
```yaml
cache-dependency-glob: "uv.lock"
```

**GitLab:**
```yaml
key: ${CI_COMMIT_REF_SLUG}-${CI_COMMIT_SHA}
```

**Why:** Ensures reproducible builds when dependencies change.

### 2. Separate Development and Production Caches

```yaml
# Production: minimal dependencies
- name: Install (prod)
  run: uv sync --frozen --no-dev

# Development: all dependencies
- name: Install (dev)
  run: uv sync --frozen --all-extras --dev
```

Consider separate cache keys:
```yaml
# GitHub Actions
cache-dependency-glob: |
  uv.lock
  pyproject.toml
```

### 3. Cache Warming Strategy

**Proactive cache warming:** Run dependency install first

```yaml
jobs:
  cache-warmer:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v6
        with:
          enable-cache: true
          cache-dependency-glob: "uv.lock"
      - run: uv sync --all-extras --dev
    # Cache is now warm for subsequent jobs

  test:
    needs: cache-warmer
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v6
        with:
          enable-cache: true
      - run: uv sync --all-extras --dev  # Uses warm cache
      - run: uv run pytest
```

### 4. Cache Invalidation Strategy

**Automatic invalidation triggers:**
1. Python version changes (handled automatically in setup-uv)
2. `uv.lock` content changes
3. GitHub Actions default: 5 GB limit (oldest entries deleted first)
4. GitLab: 100 GB limit per project

**Manual invalidation:**
```bash
# GitHub Actions: Re-run failed job (clears that cache)
# GitLab: Delete cache via CI/CD settings
```

### 5. Monitor Cache Effectiveness

**GitHub Actions workflow:**
```yaml
- name: Report cache usage
  run: |
    echo "Cache hit: ${{ steps.setup-uv.outputs.cache-hit }}"
    du -sh ~/.cache/uv/
```

**Expected metrics:**
- Cache hit rate: 80-95% on active branches
- Cold run: 30-60 seconds
- Warm run: 3-10 seconds

## Performance Benchmarks

### Before Caching
```
Fresh install (no cache):      45-60 seconds
Dependency resolution:         15-20 seconds
Total CI time:                 2-3 minutes
```

### With Caching
```
Warm install (cache hit):      3-5 seconds
Dependency resolution:         0 seconds (skipped)
Total CI time:                 15-30 seconds
```

### Multi-Stage Docker with Cache
```
First build:                   60-90 seconds
Subsequent builds:             5-10 seconds (code change only)
Dependency change:             20-30 seconds
```

## Troubleshooting Cache Issues

### Cache Not Being Used

**Check:**
```yaml
- name: Debug cache
  run: |
    echo "Cache size: $(du -sh ~/.cache/uv/)"
    uv cache dir
    ls -la ~/.cache/uv/
```

**Common issues:**
1. Cache path mismatch: Ensure `UV_CACHE_DIR` is set correctly
2. Different runners: Self-hosted runners don't share GitHub Actions cache
3. Cache expired: GitHub Actions default is 7 days

### Cache Corruption

**Fix:**
```bash
# GitHub Actions
gh actions-cache delete <cache-key> -R <owner>/<repo>

# GitLab
# Delete via CI/CD > Caches in project settings

# Local
uv cache clean
```

### Large Cache Size

**Monitor:**
```bash
du -sh ~/.cache/uv/
uv cache dir
```

**Reduce:**
```bash
uv cache prune        # Remove unused entries
uv cache clean        # Nuclear option
```

## Recommendations Summary

| Scenario | Strategy |
|----------|----------|
| GitHub Actions, public repo | Use `setup-uv@v6` with `enable-cache: true` |
| GitLab CI | Set `UV_CACHE_DIR: .uv-cache` in variables |
| Docker production | Use multi-stage builds with layer caching |
| Matrix testing | Separate cache keys per Python version |
| Performance critical | Combine all strategies: action cache + docker buildkit + layer separation |
| Cost sensitive | Focus on lockfile caching to avoid re-resolving deps |
