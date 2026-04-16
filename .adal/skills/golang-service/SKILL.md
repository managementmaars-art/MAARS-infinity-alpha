---
name: golang-service
description: "Architecture and patterns for building Go HTTP services with chi, httpin, pgx, and clean layered structure. Use when creating or modifying Go API services."
---

# Go HTTP Service Architecture

Opinionated patterns for production Go HTTP services. Applies to any service using chi router, httpin request binding, pgx for PostgreSQL, and a clean layered architecture.

## Project Structure

```
svc/
├── cmd/server/main.go          # Entry point, dependency wiring
├── internal/
│   ├── config/config.go        # Env-based configuration
│   ├── db/provider.go          # DB connection pools (RW/RO split)
│   ├── domain/                 # Domain entities & errors (match DB schema)
│   ├── httpapi/
│   │   ├── server.go           # Router setup & middleware chain
│   │   ├── setup.go            # Validator init & httpin integration
│   │   ├── interfaces.go       # Service interfaces for handlers
│   │   ├── middleware/         # Custom middleware (auth, CORS, etc.)
│   │   └── <resource>_*.go    # Handlers + request/response DTOs per resource
│   ├── httpx/                  # HTTP utilities (error envelope, pagination, responses)
│   ├── repository/
│   │   ├── pg/                 # PostgreSQL implementations (raw SQL via pgx)
│   │   └── metrics/           # Decorator pattern for observability
│   └── service/               # Business logic, delegates to repositories
├── migrations/                 # Goose SQL migrations (timestamped)
├── vendor/                     # Vendored dependencies
├── go.mod, go.sum
├── .golangci.yml
├── Taskfile.yml, Taskfile.migration.yml, Taskfile.docker.yml
├── Dockerfile
├── entrypoint.sh              # Runs migrations then starts app
└── .env.example
```

### Rules

- All application code lives under `internal/` — nothing is exported
- One handler file per resource (e.g., `telegram_user.go`, `residence.go`)
- Domain entities in `internal/domain/` match the DB schema — they are NOT transport DTOs
- Transport DTOs live next to handlers in `internal/httpapi/`
- Never expose DB entities directly over the wire

## Dependency Flow

```
main.go → config → db.Provider → repositories → services → handlers → router
```

Dependencies flow one direction. Handlers depend on service interfaces, services depend on repository interfaces. Concrete implementations are wired in `main.go`.

## Request Binding — httpin + validator

Use `github.com/ggicci/httpin` for all request decoding. Combine with `github.com/go-playground/validator/v10` for validation on typed DTOs.

### Setup (once, in `setup.go`)

```go
var validate = validator.New()

func init() {
    httpin_integration.UseGochiURLParam("path", chi.URLParam)
    httpin_core.RegisterErrorHandler(httpx.HTTPPinErrorHandler)

    // Use JSON tag names in validation error messages
    validate.RegisterTagNameFunc(func(fld reflect.StructField) string {
        tag := fld.Tag.Get("json")
        if tag == "-" || tag == "" {
            return fld.Name
        }
        if i := strings.Index(tag, ","); i != -1 {
            return tag[:i]
        }
        return tag
    })
}
```

### Request DTO pattern

```go
type UpsertItemRequest struct {
    ID   uuid.UUID `json:"id" in:"form=id" validate:"uuid4"`
    Name string    `json:"name" validate:"required,min=1,max=255"`
    Type string    `json:"type" validate:"required,oneof=online offline"`
}

// Always provide a conversion method to domain
func (r *UpsertItemRequest) ToDomain() *domain.Item {
    return &domain.Item{
        ID:   r.ID,
        Name: r.Name,
        Type: r.Type,
    }
}
```

### Filter DTO with pagination

```go
type ListItemsRequest struct {
    Status *string `in:"query=status" validate:"omitempty,oneof=active inactive"`
    httpx.PaginationParams
}

func (r *ListItemsRequest) ToFilter(offset int) *domain.ItemFilter {
    return &domain.ItemFilter{
        Status: r.Status,
        Limit:  r.DBLimit(),
        Offset: offset,
    }
}
```

### httpin tags reference

- `in:"body=json"` — JSON request body
- `in:"query=param_name"` — Query string (`default=` supported)
- `in:"path=param_name"` — URL path parameter (via chi)
- `in:"form=field_name"` — Form field
- `in:"header=Header-Name"` — HTTP header

## Handler Pattern

Handlers are thin: parse input, validate, call service, map response. Each handler struct has a `Register(r chi.Router)` method.

```go
type ItemHandler struct {
    svc ItemService
    log *slog.Logger
}

func NewItemHandler(svc ItemService, log *slog.Logger) *ItemHandler {
    return &ItemHandler{svc: svc, log: log.With("handler", "item")}
}

func (h *ItemHandler) Register(r chi.Router) {
    r.With(httpin.NewInput(ListItemsRequest{})).Get("/items", h.list)
    r.With(httpin.NewInput(UpsertItemRequest{})).Post("/items", h.upsert)
}

func (h *ItemHandler) list(w http.ResponseWriter, r *http.Request) {
    req := r.Context().Value(httpin.Input).(*ListItemsRequest)

    offset, err := req.Offset()
    if err != nil {
        httpx.WriteError(w, r, http.StatusBadRequest, httpx.CodeValidation, "invalid cursor", nil)
        return
    }

    if err := validate.StructCtx(r.Context(), req); err != nil {
        httpx.WriteValidationError(w, r, err)
        return
    }

    items, err := h.svc.ListItems(r.Context(), req.ToFilter(offset))
    if err != nil {
        h.log.ErrorContext(r.Context(), "failed to list items", "error", err)
        httpx.WriteError(w, r, http.StatusInternalServerError, httpx.CodeInternal, "failed to list items", nil)
        return
    }

    httpx.WriteJSON(w, http.StatusOK, httpx.NewPaginatedResponse(items, req.Limit, offset))
}
```

### Split read/write registration for granular rate limiting

```go
func (h *ItemHandler) RegisterRead(r chi.Router) {
    r.With(httpin.NewInput(ListItemsRequest{})).Get("/items", h.list)
}

func (h *ItemHandler) RegisterWrite(r chi.Router) {
    r.With(httpin.NewInput(UpsertItemRequest{})).Post("/items", h.upsert)
}
```

## Error Handling — Unified Envelope

All error responses use the same JSON envelope:

```go
type ErrorCode string

const (
    CodeValidation    ErrorCode = "VALIDATION_ERROR"
    CodeUnauthorized  ErrorCode = "UNAUTHORIZED"
    CodeForbidden     ErrorCode = "FORBIDDEN"
    CodeNotFound      ErrorCode = "NOT_FOUND"
    CodeConflict      ErrorCode = "CONFLICT"
    CodeUnprocessable ErrorCode = "UNPROCESSABLE_ENTITY"
    CodeRateLimited   ErrorCode = "RATE_LIMITED"
    CodeInternal      ErrorCode = "INTERNAL_ERROR"
)
```

Response shape:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "invalid input",
    "details": { "fields": [{ "path": "name", "message": "is required" }] }
  },
  "request_id": "abc-123",
  "timestamp": "2025-01-01T00:00:00Z"
}
```

### Error codes are UPPER_SNAKE_CASE. Error messages are human-readable lowercase.

### Validation errors transform validator tags to friendly messages

```go
func humanizeTag(tag string, fe validator.FieldError) string {
    switch tag {
    case "required":
        return "is required"
    case "gte":
        return "must be greater than or equal to " + fe.Param()
    case "oneof":
        return "must be one of: " + fe.Param()
    case "min":
        return "must be at least " + fe.Param() + " characters"
    // ... extend per custom validator
    }
}
```

### Error propagation: domain errors → handler mapping

```go
// In domain/errors.go
var (
    ErrNotFound   = errors.New("not found")
    ErrConflict   = errors.New("conflict")
)

// In handler
result, err := h.svc.GetItem(r.Context(), id)
if err != nil {
    if errors.Is(err, domain.ErrNotFound) {
        httpx.WriteError(w, r, http.StatusNotFound, httpx.CodeNotFound, "item not found", nil)
        return
    }
    h.log.ErrorContext(r.Context(), "failed to get item", "error", err)
    httpx.WriteError(w, r, http.StatusInternalServerError, httpx.CodeInternal, "failed to get item", nil)
    return
}
```

## Repository Pattern — RW/RO Split

### Database connection provider

```go
type ConnProvider interface {
    RW() *pgxpool.Pool  // Write operations
    RO() *pgxpool.Pool  // Read operations
    Close()
}
```

Fallback: if `DATABASE_URL_RO` is not set, RO pool reuses the RW pool.

### Interface segregation — separate Reader/Writer

```go
type ItemReader interface {
    GetByID(ctx context.Context, id uuid.UUID) (domain.Item, error)
    List(ctx context.Context, filter *domain.ItemFilter) ([]domain.Item, error)
}

type ItemWriter interface {
    Upsert(ctx context.Context, item *domain.Item) error
    Delete(ctx context.Context, id uuid.UUID) error
}

type ItemRepo interface {
    ItemReader
    ItemWriter
}
```

### Repository implementation — raw SQL with pgx

```go
type ItemRepo struct {
    db db.ConnProvider
}

func (r *ItemRepo) GetByID(ctx context.Context, id uuid.UUID) (domain.Item, error) {
    var item domain.Item
    err := r.db.RO().QueryRow(ctx,
        `SELECT id, name, type, created_at FROM items WHERE id = $1`, id,
    ).Scan(&item.ID, &item.Name, &item.Type, &item.CreatedAt)

    if errors.Is(err, pgx.ErrNoRows) {
        return item, domain.ErrNotFound
    }
    return item, err
}

func (r *ItemRepo) Upsert(ctx context.Context, item *domain.Item) error {
    _, err := r.db.RW().Exec(ctx,
        `INSERT INTO items (id, name, type) VALUES ($1, $2, $3)
         ON CONFLICT (id) DO UPDATE SET name = $2, type = $3, updated_at = now()`,
        item.ID, item.Name, item.Type,
    )
    return err
}
```

### Rules

- Use `r.db.RO()` for all SELECT queries
- Use `r.db.RW()` for INSERT/UPDATE/DELETE
- Map `pgx.ErrNoRows` to `domain.ErrNotFound`
- Use parameterized queries (`$1, $2`) — never string interpolation
- Use `sql.NullXxx` or pointer helpers for nullable columns
- No ORM — raw SQL only

### Metrics decorator

Wrap every repository with a metrics decorator that measures timing via Prometheus:

```go
type ItemRepoMetrics struct {
    next service.ItemRepo
}

func (m *ItemRepoMetrics) GetByID(ctx context.Context, id uuid.UUID) (item domain.Item, err error) {
    defer func(start time.Time) { observe("item", "get_by_id", start, err) }(time.Now())
    return m.next.GetByID(ctx, id)
}
```

## Router & Middleware Chain

```go
func NewServer(deps ServerDeps) http.Handler {
    r := chi.NewRouter()

    // Global middleware (order matters)
    r.Use(metrics.Collector(...))
    r.Use(middleware.RequestID)
    r.Use(api_middleware.RequestIDHeader())
    r.Use(middleware.Recoverer)
    r.Use(middleware.Timeout(deps.Cfg.RequestTimeout))
    r.Use(api_middleware.Cors(deps.Cfg.CORSAllowedOrigins, deps.Cfg.CORSAllowCredentials))
    r.Use(api_middleware.SecurityHeaders())
    r.Use(middleware.RequestSize(deps.Cfg.MaxBodyBytes))
    r.Use(api_middleware.Heartbeat(deps.Health, "/healthz"))
    r.Use(httplog.RequestLogger(...))

    r.Handle("/metrics", metrics.Handler())

    // Nested route groups with independent middleware
    r.Route("/api", func(api chi.Router) {
        api.Route("/", func(r chi.Router) {
            r.Use(api_middleware.APIKeyAuth(deps.Cfg))
            // Bot-facing endpoints
        })
        api.Route("/stat", func(r chi.Router) {
            r.Use(httprate.LimitByIP(100, time.Minute))
            // Public stat endpoints
            r.Route("/", func(r chi.Router) {
                r.Use(api_middleware.TelegramAuth(...))
                // Authenticated endpoints with tighter rate limits
            })
        })
    })

    return r
}
```

### Security headers middleware always includes:

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: no-referrer`
- `Permissions-Policy: camera=(), geolocation=()`

### Auth middleware stores identity in context

```go
ctx := context.WithValue(r.Context(), APIKeyBotID, botID)
// or
ctx := context.WithValue(r.Context(), TelegramUserID, userID)
```

## Pagination — Cursor-based

Over-fetch by 1 to detect `has_more`:

```go
type PaginationParams struct {
    Cursor string `in:"query=cursor" validate:"omitempty"`
    Limit  int    `in:"query=limit;default=20" validate:"min=1,max=100"`
}

func (p *PaginationParams) DBLimit() int { return p.Limit + 1 }
func (p *PaginationParams) Offset() (int, error) { return DecodeCursor(p.Cursor) }
```

Cursor is base64-encoded offset. Response:

```json
{
  "items": [...],
  "pagination": { "cursor": "MjA=", "has_more": true }
}
```

## Service Layer

Services are thin — delegate to repos, set defaults, aggregate:

```go
type ItemService struct {
    Items ItemRepo
}

func (s *ItemService) UpsertItem(ctx context.Context, item *domain.Item) error {
    if item.ID == uuid.Nil {
        item.ID = uuid.New()
    }
    return s.Items.Upsert(ctx, item)
}
```

## Response DTOs

```go
// Single item
httpx.WriteJSON(w, http.StatusOK, httpx.DataResponse[domain.Item]{Data: item})

// Paginated list
httpx.WriteJSON(w, http.StatusOK, httpx.NewPaginatedResponse(items, req.Limit, offset))

// Created
httpx.WriteJSON(w, http.StatusCreated, httpx.DataResponse[*domain.Item]{Data: item})
```

## Configuration — Environment Variables

```go
type Config struct {
    Production       bool
    ServerAddr       string
    ReadTimeout      time.Duration
    DatabaseURL      string
    DatabaseURLRW    string
    DatabaseURLRO    string
    DatabaseMaxConns int32
    APIKeys          map[string]struct{}
    // ...
}

func Load() *Config {
    _ = godotenv.Load()
    return &Config{
        ServerAddr:  getEnv("SERVER_ADDR", ":8080"),
        ReadTimeout: parseDur("READ_TIMEOUT", 15*time.Second),
        // ...
    }
}
```

Helper functions: `getEnv(key, default)`, `parseDur`, `parseBool`, `parseInt64`.

## Graceful Shutdown

```go
ctx, stop := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM)
defer stop()

errCh := make(chan error, 1)
go func() {
    if err := srv.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
        errCh <- err
    }
}()

select {
case <-ctx.Done():
case err := <-errCh:
    log.Error("server error", "error", err)
}

ctxShutdown, cancel := context.WithTimeout(context.Background(), cfg.ShutdownTimeout)
defer cancel()
_ = srv.Shutdown(ctxShutdown)
```

## Key Dependencies

| Package                                  | Purpose                                     |
| ---------------------------------------- | ------------------------------------------- |
| `github.com/go-chi/chi/v5`               | HTTP router                                 |
| `github.com/ggicci/httpin`               | Request binding (query, path, body, header) |
| `github.com/go-playground/validator/v10` | Struct validation                           |
| `github.com/jackc/pgx/v5`                | PostgreSQL driver + connection pool         |
| `github.com/go-chi/httplog/v3`           | Structured HTTP logging                     |
| `github.com/go-chi/httprate`             | Rate limiting                               |
| `github.com/prometheus/client_golang`    | Prometheus metrics                          |
| `github.com/joho/godotenv`               | .env file loading                           |
| `github.com/google/uuid`                 | UUID generation                             |
| `log/slog`                               | Structured logging (stdlib)                 |
