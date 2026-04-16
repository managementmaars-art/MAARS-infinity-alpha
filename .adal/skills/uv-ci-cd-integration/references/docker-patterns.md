# Advanced Docker Patterns with uv

This guide covers production-grade Docker patterns using uv for building, testing, and deploying Python applications.

## Multi-Stage Build Optimization

### Standard Production Pattern

```dockerfile
# Build stage - compile and install dependencies
FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Runtime stage - minimal production image
FROM python:3.12-slim

WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY . .

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

CMD ["python", "-m", "gunicorn", "main:app"]
```

**Size comparison:**
- Single-stage build: 800 MB - 1.2 GB
- Multi-stage build: 250 MB - 400 MB
- Reduction: 70%

### Three-Stage Build (Builder + Tester + Runtime)

```dockerfile
# Stage 1: Builder
FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --dev --no-install-project

# Stage 2: Tester (validate before shipping)
FROM builder AS tester

COPY . .
RUN uv run pytest tests/ --cov=src && \
    uv run ruff check . && \
    uv run mypy src/

# Stage 3: Runtime (minimal production)
FROM python:3.12-slim AS runtime

WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY --from=tester /app/src /app/src

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

CMD ["python", "-m", "myapp"]
```

**Advantages:**
- Tests run during build, fail fast
- Failed tests prevent image push
- Final image is minimal (no test dependencies)

### Build Arguments for Environment-Specific Builds

```dockerfile
ARG PYTHON_VERSION=3.12
ARG INSTALL_DEV=false

FROM python:${PYTHON_VERSION}-slim AS base

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN if [ "$INSTALL_DEV" = "true" ] ; then \
      uv sync --frozen --all-extras --dev ; \
    else \
      uv sync --frozen --no-dev ; \
    fi

# ... rest of build
```

**Usage:**
```bash
# Production build
docker build -t myapp:latest .

# Development build
docker build -t myapp:dev --build-arg INSTALL_DEV=true .

# Different Python version
docker build -t myapp:py311 --build-arg PYTHON_VERSION=3.11 .
```

## Bytecode Compilation

### Pre-compile for Faster Startup

```dockerfile
FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project --compile-bytecode
```

**Performance impact:**
- Startup time: -20-30%
- Image size: +5-10%
- Warmup time: Reduced
- Trade-off: Worth it for production

## Non-Root User Security

```dockerfile
FROM python:3.12-slim

# Create unprivileged user
RUN groupadd -r appuser && useradd -r -g appuser appuser

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
WORKDIR /app

# Change ownership to appuser
COPY --chown=appuser:appuser pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

ENV PATH="/app/.venv/bin:$PATH"
CMD ["python", "-m", "gunicorn", "main:app"]
```

**Security benefits:**
- Container runs as non-root
- Limits damage if container compromised
- Satisfies corporate security policies
- Required for some Kubernetes clusters

## Health Checks

```dockerfile
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY . .

ENV PATH="/app/.venv/bin:$PATH"

# HTTP-based health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=2)" || exit 1

# Alternative: Command-based health check
# HEALTHCHECK --interval=30s --timeout=3s \
#     CMD python -m myapp.healthcheck

CMD ["python", "-m", "gunicorn", "main:app"]
```

**Health check configuration:**
- `--interval`: Check frequency (30s default)
- `--timeout`: Max wait time (3s default)
- `--start-period`: Grace period before checks start (0s default)
- `--retries`: Failures before unhealthy (3 default)

## Environment-Specific Images

### Development Image

```dockerfile
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
WORKDIR /app

# Install all dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --all-extras --dev

COPY . .

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Development tools in PATH
RUN uv tool install ipython jupyter

EXPOSE 8000 8888
CMD ["bash"]
```

**Use:**
```bash
docker build -f Dockerfile.dev -t myapp-dev .
docker run -it -v $PWD:/app myapp-dev
```

### Staging/Testing Image

```dockerfile
FROM python:3.12-slim AS builder
# ... build stage

FROM builder AS test

COPY . .
RUN uv run pytest --cov && \
    uv run ruff check . && \
    uv run mypy src/

FROM python:3.12-slim AS staging

WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY --from=test /app . # Assumes tests pass

ENV PATH="/app/.venv/bin:$PATH"
CMD ["python", "-m", "gunicorn", "main:app", "--workers", "2"]
```

## Container Composition

### Docker Compose with Services

```yaml
version: '3.8'

services:
  app:
    build:
      context: .
      target: runtime  # Use multi-stage target
    ports:
      - "8000:8000"
    environment:
      - DEBUG=false
      - DATABASE_URL=postgresql://user:pass@db:5432/mydb
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./config:/app/config:ro  # Read-only config

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: mydb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s

volumes:
  postgres_data:
```

## Build Performance

### BuildKit with Cache Mounts

```dockerfile
# Enable with: DOCKER_BUILDKIT=1 docker build ...

FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
WORKDIR /app

COPY pyproject.toml uv.lock ./

# Cache mounts persist between builds
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=cache,target=/app/.venv \
    uv sync --frozen --no-dev --no-install-project

COPY . .
CMD ["python", "-m", "myapp"]
```

**Usage:**
```bash
DOCKER_BUILDKIT=1 docker build -t myapp .
```

**Benefits:**
- Reuses uv cache between builds (15-20x faster)
- Reduces network requests for dependencies
- Optimal for CI/CD pipelines

### .dockerignore Optimization

```
# .dockerignore - reduce build context size

# Version control
.git
.gitignore
.github
.gitlab-ci.yml

# Development
.venv
.pytest_cache
.mypy_cache
*.egg-info
__pycache__
.ruff_cache
dist
build

# Documentation
docs
*.md
LICENSE

# CI/CD
.circleci
.travis.yml

# IDE
.vscode
.idea
*.swp

# Testing
.coverage
htmlcov
.tox

# Don't ignore these
!src/
!pyproject.toml
!uv.lock
```

**Impact:**
- Smaller build context = faster docker build
- Typical reduction: 90% of files ignored

## Scanning and Security

### Container Scanning with Trivy

```dockerfile
# Add to CI/CD pipeline
FROM python:3.12-slim AS scan

RUN apt-get update && apt-get install -y curl && \
    curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin

FROM builder AS runtime
# ... build runtime

FROM runtime
# Scan image during build
# This would be done externally in CI
```

### SBOM Generation

```bash
# Generate Software Bill of Materials
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  anchore/syft:latest myapp:latest -o spdx > sbom.spdx.json
```

## Debugging Container Builds

### Interactive Layer Debugging

```dockerfile
FROM python:3.12-slim

# ... various layers ...

# Add debug layer at problem point
RUN bash  # Opens shell to inspect layer state
```

**Inspect during build:**
```bash
docker build -t debug:latest .
# At RUN bash, container starts shell
# Type 'exit' to continue or Ctrl+C to stop
```

### Build Output Inspection

```bash
# Verbose build output
docker build -t myapp:latest --progress=plain .

# Check layer sizes
docker history myapp:latest

# Inspect image filesystem
docker run --rm myapp:latest find /app -type f -exec ls -lh {} \;
```

## Production Deployment Patterns

### Image Registry Best Practices

```bash
# Tag with version and latest
docker build -t myregistry/myapp:1.0.0 .
docker tag myregistry/myapp:1.0.0 myregistry/myapp:latest

# Push both tags
docker push myregistry/myapp:1.0.0
docker push myregistry/myapp:latest

# Use specific version in production
docker run myregistry/myapp:1.0.0

# Use latest in development
docker run myregistry/myapp:latest
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: myapp
        image: myregistry/myapp:1.0.0
        ports:
        - containerPort: 8000
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 2
          periodSeconds: 5
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

## Common Docker + uv Issues

### Issue: "uv: command not found"

**Cause:** uv binary not in PATH

**Fix:**
```dockerfile
# Ensure PATH includes uv
ENV PATH="/root/.cargo/bin:${PATH}"

# Or copy uv directly
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
```

### Issue: Large image size

**Diagnosis:**
```bash
docker history myapp:latest
docker run --rm myapp:latest du -sh /.venv/*
```

**Solutions:**
1. Use multi-stage builds
2. Remove test dependencies with `--no-dev`
3. Use slimmer base images
4. Compile bytecode to remove `.py` files (advanced)

### Issue: Permission denied in container

**Cause:** Running as root, files owned by root

**Fix:**
```dockerfile
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser
```

### Issue: Network timeouts during build

**Cause:** Slow PyPI mirrors or connectivity issues

**Fix:**
```dockerfile
# Use custom PyPI mirror
RUN uv sync --index-url https://mirror.example.com/simple

# Or retry with backoff
RUN uv sync --frozen || uv sync --frozen
```

## Recommendations

| Use Case | Pattern |
|----------|---------|
| Production | Multi-stage with non-root user + health checks |
| Development | Single stage with all dev dependencies |
| Testing | Three-stage with integrated tests |
| Performance critical | BuildKit + cache mounts + bytecode compilation |
| Security focused | Non-root + minimal base + SBOM generation |
| CI/CD | Layer caching + artifact caching + build targets |
