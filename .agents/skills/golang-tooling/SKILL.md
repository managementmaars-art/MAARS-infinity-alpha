---
name: golang-tooling
description: "Go project tooling, code quality, build pipeline, Docker, migrations, and testing conventions. Use when setting up or maintaining Go service infrastructure."
---

# Go Project Tooling & Code Quality

Opinionated tooling setup for Go services: formatting, linting, build pipeline, Docker, database migrations, and testing conventions.

## Code Formatting

### gofumpt — strict Go formatting

Use `gofumpt` instead of `gofmt`. It enforces stricter formatting rules (empty lines, composite literals, etc.).

### gci — import grouping

Imports are grouped in this exact order with blank lines between groups:

1. **Standard library** (`fmt`, `context`, `net/http`, etc.)
2. **Third-party** (everything else)
3. **Organization prefix** (`github.com/openserbia`)
4. **Current module** (the module from `go.mod`)

```go
import (
    "context"
    "fmt"
    "net/http"

    "github.com/go-chi/chi/v5"
    "github.com/jackc/pgx/v5"

    "github.com/openserbia/shared-lib/pkg/auth"

    "github.com/openserbia/my-service/internal/config"
    "github.com/openserbia/my-service/internal/domain"
)
```

### Formatting command

```bash
gci write -s standard -s default -s "prefix(github.com/openserbia)" -s "prefix(MODULE_NAME)" .
gofumpt -l -w .
```

## Linting — golangci-lint v2

### .golangci.yml

```yaml
linters:
  default: standard
  enable:
    - bodyclose # Unclosed HTTP response bodies
    - copyloopvar # Loop variable capture bugs
    - dupl # Duplicate code detection
    - errname # Error type naming (ErrFoo, FooError)
    - exhaustive # Missing enum switch cases
    - gocheckcompilerdirectives # Invalid //go: directives
    - goconst # Repeated strings that should be constants
    - gocritic # Opinionated Go checks (diagnostic, style, performance)
    - mnd # Magic number detection
    - misspell # Typos in comments and strings
    - nilerr # Returning nil when err != nil
    - noctx # HTTP requests without context
    - prealloc # Slice preallocation hints
    - predeclared # Shadowing predeclared identifiers
    - revive # Comprehensive Go linter
    - sqlclosecheck # Unclosed SQL rows/statements
    - unconvert # Unnecessary type conversions
    - unparam # Unused function parameters
    - usestdlibvars # Use stdlib constants (http.StatusOK vs 200)
    - wastedassign # Wasted variable assignments
    - whitespace # Unnecessary blank lines
  settings:
    dupl:
      threshold: 150
    goconst:
      min-len: 3
      min-occurrences: 3
    mnd:
      ignored-functions:
        - "strconv.FormatInt"
        - "strconv.ParseInt"

formatters:
  enable:
    - gofumpt
    - gci
  settings:
    gci:
      sections:
        - standard
        - default
        - prefix(github.com/openserbia)
```

### Rules

- Lint always runs AFTER formatting (`task lint` depends on `task fmt`)
- Fix lint issues, don't suppress them — only exclude metrics/generated code directories
- `mnd` exceptions: `strconv` parsing functions are allowed magic numbers

## JSON Conventions

- Field names: `snake_case`
- Timestamps: RFC3339 UTC (`"2025-01-01T00:00:00Z"`)
- Empty arrays: `[]` not `null` (initialize with `make([]T, 0)` or `[]T{}`)
- Omit zero-value optional fields: `json:"field,omitempty"`

## Taskfile — Build Automation

Use `go-task` (Taskfile.yml) for all build operations.

### Core Taskfile.yml

```yaml
version: "3"
dotenv: [".env", "{{.ENV}}/.env"]

vars:
  PACKAGE_NAME:
    sh: grep -m 1 "^module" go.mod | awk '{print $2}'
  COMMIT_HASH:
    sh: '[ -n "$SOURCE_COMMIT" ] && echo "$SOURCE_COMMIT" || git rev-parse HEAD'
  BUILD_TIME:
    sh: date -u +"%Y-%m-%dT%H:%M:%SZ"
  BUILD_PATH: "{{ .PWD }}/build"

env:
  PACKAGE_NAME: "{{.PACKAGE_NAME}}"
  GOOS: linux
  GOARCH: amd64
  CGO_ENABLED: 0

tasks:
  cleanup:
    cmds:
      - rm -rf {{.BUILD_PATH}}/

  build:
    deps: [deps, cleanup]
    cmds:
      - go build -ldflags="-w -s -X 'main.Version=1.0.0' -X 'main.Commit={{.COMMIT_HASH}}' -X 'main.BuildTime={{.BUILD_TIME}}'" -trimpath -mod vendor -o {{.BUILD_PATH}}/app ./cmd/server

  deps:
    sources: [go.mod, go.sum]
    generates: [vendor/modules.txt]
    cmds:
      - go env -w GOPROXY=https://proxy.golang.org,direct
      - go mod download
      - go mod tidy
      - go mod vendor

  fmt:
    deps: [deps]
    cmds:
      - gci write -s standard -s default -s "prefix(github.com/openserbia)" -s "prefix({{.PACKAGE_NAME}})" .
      - gofumpt -l -w .

  lint:
    deps: [fmt]
    cmds:
      - golangci-lint run

  test:
    deps: [deps]
    cmds:
      - go test -mod vendor -covermode=count -coverprofile=coverage.out ./...

  default:
    cmds:
      - task -l
```

### Build flags

- `-w -s` — strip debug info and symbol table
- `-trimpath` — remove local paths from binary
- `-mod vendor` — use vendored dependencies
- `-X 'main.Version/Commit/BuildTime'` — inject build metadata

### Migration Taskfile (Taskfile.migration.yml)

```yaml
version: "3"
env:
  GOOSE_DRIVER: postgres
  GOOSE_DBSTRING: "{{.DATABASE_URL}}"
  GOOSE_MIGRATION_DIR: "{{.USER_WORKING_DIR}}/migrations"

tasks:
  build:goose:
    cmds:
      - |
        git clone https://github.com/pressly/goose
        cd goose && go mod tidy
        go build -ldflags="-s -w"
          -tags='no_clickhouse no_libsql no_mssql no_mysql no_sqlite3 no_vertica no_ydb'
          -o {{.BUILD_PATH}}/goose ./cmd/goose
        rm -rf goose

  up:
    cmds: ["{{.BUILD_PATH}}/goose up"]

  down:
    cmds: ["{{.BUILD_PATH}}/goose down"]

  new:
    vars:
      name: '{{.name | default "new_migration"}}'
    cmds: ["{{.BUILD_PATH}}/goose create {{.name}} sql"]
```

## Database Migrations — Goose

### Migration file conventions

- Filename: `YYYYMMDDHHMMSS_description.sql` (timestamp-based)
- Always provide both `Up` and `Down` migrations
- Wrap in `StatementBegin`/`StatementEnd`
- Use `IF NOT EXISTS` / `IF EXISTS` for idempotency

```sql
-- +goose Up
-- +goose StatementBegin
CREATE TABLE IF NOT EXISTS items (
    id          UUID        NOT NULL PRIMARY KEY,
    name        TEXT        NOT NULL DEFAULT '',
    type        TEXT        NOT NULL DEFAULT '',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- updated_at trigger
DROP TRIGGER IF EXISTS trg_items_updated_at ON items;
CREATE TRIGGER trg_items_updated_at
    BEFORE UPDATE ON items
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE INDEX IF NOT EXISTS idx_items_type ON items(type);
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
DROP INDEX IF EXISTS idx_items_type;
DROP TRIGGER IF EXISTS trg_items_updated_at ON items;
DROP TABLE IF EXISTS items;
-- +goose StatementEnd
```

### Rules

- Use `TIMESTAMPTZ` for all timestamp columns, default `now()`
- Create `updated_at` triggers on mutable tables
- Add indexes for common query patterns
- Down migration must reverse Up completely (drop in reverse order)

## Dockerfile — Multi-stage with Devbox

```dockerfile
FROM alpine:3.22.2 AS builder
WORKDIR /svc

RUN apk add --no-cache build-base libffi-dev openssl-dev zlib-dev curl bash openssh-client git
RUN mkdir -p ~/.ssh && ssh-keyscan github.com >> ~/.ssh/known_hosts
RUN curl -fsSL https://get.jetpack.io/devbox | FORCE=1 bash

# Cache devbox layer
COPY devbox.json devbox.lock ./
RUN devbox install

COPY ./svc /svc
RUN --mount=type=ssh \
    --mount=type=cache,target=/root/.cache/go-build \
    devbox run -- task build migrate:build:goose

# Runtime
FROM alpine:3.22.2
COPY --from=builder /svc/build /svc
COPY --from=builder /svc/migrations /svc/migrations
COPY --from=builder /svc/entrypoint.sh /svc/entrypoint.sh
WORKDIR /svc

RUN chmod +x /svc/goose /svc/app /svc/entrypoint.sh
RUN addgroup -g 1000 appgroup && adduser -u 1000 -G appgroup -D appuser
RUN chown -R appuser:appgroup /svc
USER 1000

ENTRYPOINT ["/svc/entrypoint.sh"]
EXPOSE 8080
```

### Entrypoint pattern — migrations before app

```sh
#!/bin/sh
set -e
/svc/goose -dir /svc/migrations postgres "$DATABASE_URL" up
exec /svc/app
```

### Docker rules

- Alpine base for minimal image size
- Non-root user (UID 1000)
- Devbox in builder for reproducible toolchain
- Go build cache mount for faster rebuilds
- SSH mount for private module access
- Migrations run automatically on container start

## Testing Conventions

### Table-driven tests with subtests

```go
func TestItemValidation(t *testing.T) {
    tests := []struct {
        name    string
        input   Item
        wantErr bool
    }{
        {"valid item", Item{Name: "test", Type: "online"}, false},
        {"empty name", Item{Name: "", Type: "online"}, true},
        {"invalid type", Item{Name: "test", Type: "bad"}, true},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            err := validate.Struct(tt.input)
            if (err != nil) != tt.wantErr {
                t.Errorf("validate(%+v) error = %v, wantErr %v", tt.input, err, tt.wantErr)
            }
        })
    }
}
```

### Rules

- Use `t.Run()` for subtests
- Use `t.Fatalf` for fatal errors, `t.Errorf` for non-fatal assertions
- Use stdlib `testing` — no assertion libraries unless already in the project
- Test files: `*_test.go` next to the code they test
- Coverage: `go test -covermode=count -coverprofile=coverage.out ./...`
- Use `-mod vendor` flag in all Go commands

## Vendoring

All Go builds use vendored dependencies:

- Run `go mod vendor` after any dependency change
- Always pass `-mod vendor` to `go build`, `go test`
- Vendor directory is committed to git
- `go.sum` must stay in sync with `go.mod`

## Logging

- Use `log/slog` (stdlib) for structured logging
- JSON handler in production, pretty handler (devslog) in development
- Always include context: `log.ErrorContext(r.Context(), "msg", "error", err)`
- Add handler-scoped fields: `log.With("handler", "item")`

## Devbox Toolchain

Use Devbox (`devbox.json`) for reproducible development environment across all services.

### Running tasks

Each service has its own `Taskfile.yml`. Always run tasks **from within the service directory** using Devbox:

```bash
# Option 1: enter Devbox shell, then run tasks
cd svc && devbox shell
task build
task lint

# Option 2: one-shot command
cd svc && devbox run -- task build
```

**Never run `go build`, `golangci-lint`, `gofumpt`, or `gci` directly** — always go through `task` commands inside Devbox to ensure correct tool versions and environment.

### CI/CD pattern

```bash
# From within each service directory
devbox run -- task docker:build IMAGE_TAG=$SHA
```

### devbox.json packages

```json
{
  "packages": {
    "go": "1.26.1",
    "golangci-lint": "latest",
    "gofumpt": "latest",
    "gci": "latest",
    "go-task": "latest",
    "gopls": "latest",
    "delve": "latest",
    "ginkgo": "latest",
    "nodejs_24": "latest",
    "bun": "latest",
    "ngrok": "latest",
    "git": "latest"
  },
  "shell": {
    "init_hook": ["export \"GOROOT=$(go env GOROOT)\""]
  }
}
```

### Rules

- `devbox.json` lives at the repo root, shared by all services
- Pin Go version explicitly (e.g., `1.26.1`), use `latest` for tooling
- Set `GOROOT` in init_hook for IDE compatibility
- All developers and CI use Devbox — no local tool installations
