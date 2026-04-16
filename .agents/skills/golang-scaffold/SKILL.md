---
name: golang-scaffold
description: "Scaffold a new Go HTTP service with chi, httpin, pgx, and clean layered architecture. Use when creating a new Go service from scratch."
---

# Go Service Scaffold

Generate a complete, production-ready Go HTTP service skeleton. This skill creates all infrastructure files — config, database, HTTP layer, middleware, error handling, pagination, build tooling, Docker, and migrations.

## When to use

When the user asks to create/scaffold/bootstrap a new Go service or API.

## Required inputs

Ask the user for:

1. **Module path** — e.g., `github.com/openserbia/my-service`
2. **Service directory name** — e.g., `my-service` (where files will be created)
3. **Organization prefix** — for gci import grouping (default: `github.com/openserbia`)

## What to generate

Create ALL of the following files. Do not skip any. Replace `{{MODULE}}` with the module path and `{{ORG_PREFIX}}` with the organization prefix throughout.

## Directory structure

```
{{SERVICE_DIR}}/
├── cmd/server/main.go
├── internal/
│   ├── config/config.go
│   ├── db/provider.go
│   ├── domain/errors.go
│   ├── httpapi/
│   │   ├── server.go
│   │   ├── setup.go
│   │   └── middleware/
│   │       ├── api_key_auth.go
│   │       ├── cors.go
│   │       ├── heartbeat.go
│   │       ├── request_id_header.go
│   │       └── security_headers.go
│   └── httpx/
│       ├── error.go
│       ├── response.go
│       ├── validation.go
│       ├── pagination.go
│       └── cursor.go
├── migrations/
│   └── <timestamp>_init.sql
├── .golangci.yml
├── .env.example
├── .dockerignore
├── Taskfile.yml
├── Taskfile.migration.yml
├── Taskfile.docker.yml
├── Dockerfile
├── entrypoint.sh
└── go.mod
```

---

## File templates

### cmd/server/main.go

```go
package main

import (
	"context"
	"errors"
	"fmt"
	"log/slog"
	"net/http"
	"os"
	"os/signal"
	"syscall"

	"github.com/go-chi/httplog/v3"
	"github.com/golang-cz/devslog"
	"github.com/joho/godotenv"

	"{{MODULE}}/internal/config"
	dbpkg "{{MODULE}}/internal/db"
	"{{MODULE}}/internal/httpapi"
)

func logHandler(isProd bool) slog.Handler {
	handlerOpts := &slog.HandlerOptions{
		AddSource:   true,
		ReplaceAttr: httplog.SchemaECS.Concise(true).ReplaceAttr,
	}

	if isProd {
		return slog.NewJSONHandler(os.Stdout, handlerOpts)
	}

	//nolint:mnd // dev logging defaults
	return devslog.NewHandler(os.Stdout, &devslog.Options{
		SortKeys:           true,
		MaxErrorStackTrace: 5,
		MaxSlicePrintSize:  20,
		HandlerOptions:     handlerOpts,
	})
}

func main() {
	_ = godotenv.Load()

	cfg := config.Load()

	ctx, stop := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM)
	defer stop()

	log := slog.New(logHandler(cfg.Production))

	provider, err := dbpkg.NewProvider(ctx, dbpkg.Options{
		URL:      cfg.DatabaseURL,
		URLRW:    cfg.DatabaseURLRW,
		URLRO:    cfg.DatabaseURLRO,
		MaxConns: cfg.DatabaseMaxConns,
	})
	if err != nil {
		log.Error(fmt.Sprintf("db connect: %v", err))
		return
	}
	defer provider.Close()

	// TODO: Create repositories and services here
	// Example:
	// repo := pg.NewExampleRepo(provider)
	// svc := service.NewExampleService(repo)

	handler := httpapi.NewServer(httpapi.ServerDeps{
		Cfg:    cfg,
		Health: provider,
		Log:    log,
	})

	srv := &http.Server{
		Addr:         cfg.ServerAddr,
		Handler:      handler,
		ReadTimeout:  cfg.ReadTimeout,
		WriteTimeout: cfg.WriteTimeout,
		IdleTimeout:  cfg.IdleTimeout,
	}

	errCh := make(chan error, 1)
	go func() {
		log.Info(fmt.Sprintf("HTTP server listening on %s", cfg.ServerAddr))
		if err = srv.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
			errCh <- err
		}
	}()

	select {
	case <-ctx.Done():
	case err := <-errCh:
		log.Error(fmt.Sprintf("server error: %v", err))
	}

	ctxShutdown, cancel := context.WithTimeout(context.Background(), cfg.ShutdownTimeout)
	defer cancel()
	if err := srv.Shutdown(ctxShutdown); err != nil {
		log.Error(fmt.Sprintf("graceful shutdown error: %v", err))
		_ = srv.Close()
	}
	log.Info("server stopped")
}
```

### internal/config/config.go

```go
package config

import (
	"os"
	"strconv"
	"strings"
	"time"
)

type Config struct {
	Production bool
	// Server
	ServerAddr      string
	ReadTimeout     time.Duration
	WriteTimeout    time.Duration
	IdleTimeout     time.Duration
	RequestTimeout  time.Duration
	ShutdownTimeout time.Duration

	// CORS
	CORSAllowedOrigins   []string
	CORSAllowCredentials bool

	// Auth
	APIKeys map[string]struct{}

	// DB
	DatabaseURL      string
	DatabaseURLRW    string
	DatabaseURLRO    string
	DatabaseMaxConns int32

	// Limits
	MaxBodyBytes int64
}

func getEnv(key, def string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return def
}

func parseDur(key string, def time.Duration) time.Duration {
	if v := os.Getenv(key); v != "" {
		if d, err := time.ParseDuration(v); err == nil {
			return d
		}
	}
	return def
}

func parseBool(key string, def bool) bool {
	if v := os.Getenv(key); v != "" {
		b, err := strconv.ParseBool(v)
		if err == nil {
			return b
		}
	}
	return def
}

func parseInt64(key string, def int64) int64 {
	if v := os.Getenv(key); v != "" {
		n, err := strconv.ParseInt(v, 10, 64)
		if err == nil {
			return n
		}
	}
	return def
}

func Load() *Config {
	apiKeysStr := strings.TrimSpace(os.Getenv("API_KEYS"))
	keys := map[string]struct{}{}
	if apiKeysStr != "" {
		for _, k := range strings.Split(apiKeysStr, ",") {
			k = strings.TrimSpace(k)
			if k != "" {
				keys[k] = struct{}{}
			}
		}
	}

	corsAllowed := strings.Split(getEnv("CORS_ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173"), ",")
	for i := range corsAllowed {
		corsAllowed[i] = strings.TrimSpace(corsAllowed[i])
	}

	//nolint:mnd // config defaults
	return &Config{
		ServerAddr:           getEnv("SERVER_ADDR", ":8080"),
		ReadTimeout:          parseDur("READ_TIMEOUT", 15*time.Second),
		WriteTimeout:         parseDur("WRITE_TIMEOUT", 15*time.Second),
		IdleTimeout:          parseDur("IDLE_TIMEOUT", 60*time.Second),
		RequestTimeout:       parseDur("REQUEST_TIMEOUT", 30*time.Second),
		ShutdownTimeout:      parseDur("SHUTDOWN_TIMEOUT", 20*time.Second),
		CORSAllowedOrigins:   corsAllowed,
		CORSAllowCredentials: parseBool("CORS_ALLOW_CREDENTIALS", false),
		APIKeys:              keys,
		DatabaseURL:          os.Getenv("DATABASE_URL"),
		DatabaseURLRW:        os.Getenv("DATABASE_URL_RW"),
		DatabaseURLRO:        os.Getenv("DATABASE_URL_RO"),
		DatabaseMaxConns:     int32(parseInt64("DATABASE_MAX_CONNS", 4)),
		MaxBodyBytes:         parseInt64("MAX_BODY_BYTES", 5*1024*1024),
		Production:           parseBool("PRODUCTION", true),
	}
}
```

### internal/db/provider.go

```go
package db

import (
	"context"
	"errors"
	"fmt"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
)

type ConnProvider interface {
	RW() *pgxpool.Pool
	RO() *pgxpool.Pool
	Ping(ctx context.Context) (bool, error)
	Close()
}

type provider struct {
	rw *pgxpool.Pool
	ro *pgxpool.Pool
}

func (p *provider) RW() *pgxpool.Pool { return p.rw }
func (p *provider) RO() *pgxpool.Pool { return p.ro }
func (p *provider) Ping(ctx context.Context) (bool, error) {
	if err := p.rw.Ping(ctx); err != nil {
		return false, err
	}
	return true, nil
}

func (p *provider) Close() {
	if p.ro != nil && p.ro != p.rw {
		p.ro.Close()
	}
	if p.rw != nil {
		p.rw.Close()
	}
}

type Options struct {
	URL      string
	URLRW    string
	URLRO    string
	MaxConns int32
}

func NewProvider(ctx context.Context, opts Options) (ConnProvider, error) {
	rwURL := opts.URLRW
	roURL := opts.URLRO
	if rwURL == "" {
		rwURL = opts.URL
	}
	if roURL == "" {
		roURL = rwURL
	}
	if roURL == "" {
		roURL = opts.URL
	}

	if rwURL == "" {
		return nil, errors.New("database URL is required")
	}

	rwCfg, err := pgxpool.ParseConfig(rwURL)
	if err != nil {
		return nil, fmt.Errorf("parse RW DB URL: %w", err)
	}
	if opts.MaxConns > 0 {
		rwCfg.MaxConns = opts.MaxConns
	}
	rwCfg.MaxConnLifetime = 30 * time.Minute //nolint:mnd // reasonable default

	rwPool, err := pgxpool.NewWithConfig(ctx, rwCfg)
	if err != nil {
		return nil, fmt.Errorf("create RW pool: %w", err)
	}
	if err := rwPool.Ping(ctx); err != nil {
		rwPool.Close()
		return nil, fmt.Errorf("ping RW DB: %w", err)
	}

	roPool := rwPool
	if roURL != rwURL {
		roCfg, err := pgxpool.ParseConfig(roURL)
		if err != nil {
			rwPool.Close()
			return nil, fmt.Errorf("parse RO DB URL: %w", err)
		}
		if opts.MaxConns > 0 {
			roCfg.MaxConns = opts.MaxConns
		}
		roCfg.MaxConnLifetime = 30 * time.Minute //nolint:mnd // reasonable default
		roPool, err = pgxpool.NewWithConfig(ctx, roCfg)
		if err != nil {
			rwPool.Close()
			return nil, fmt.Errorf("create RO pool: %w", err)
		}
		if err := roPool.Ping(ctx); err != nil {
			roPool.Close()
			rwPool.Close()
			return nil, fmt.Errorf("ping RO DB: %w", err)
		}
	}

	return &provider{rw: rwPool, ro: roPool}, nil
}
```

### internal/domain/errors.go

```go
package domain

import "errors"

var (
	ErrNotFound = errors.New("not found")
)
```

### internal/httpapi/setup.go

```go
package httpapi

import (
	"reflect"
	"strings"

	httpin_core "github.com/ggicci/httpin/core"
	httpin_integration "github.com/ggicci/httpin/integration"
	"github.com/go-chi/chi/v5"
	"github.com/go-playground/validator/v10"

	"{{MODULE}}/internal/httpx"
)

var validate = validator.New()

func init() {
	httpin_integration.UseGochiURLParam("path", chi.URLParam)
	httpin_core.RegisterErrorHandler(httpx.HTTPPinErrorHandler)

	validate.RegisterTagNameFunc(func(fld reflect.StructField) string {
		tag := fld.Tag.Get("json")
		if tag == "-" || tag == "" {
			return fld.Name
		}
		comma := strings.Index(tag, ",")
		if comma != -1 {
			return tag[:comma]
		}
		return tag
	})

	// Register custom validators here:
	// _ = validate.RegisterValidation("myvalidator", func(fl validator.FieldLevel) bool { ... })
}
```

### internal/httpapi/server.go

```go
package httpapi

import (
	"context"
	"log/slog"
	"net/http"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
	"github.com/go-chi/httplog/v3"
	"github.com/go-chi/metrics"

	"{{MODULE}}/internal/config"
	api_middleware "{{MODULE}}/internal/httpapi/middleware"
)

// HealthChecker is used by the heartbeat middleware to verify database connectivity.
type HealthChecker interface {
	Ping(ctx context.Context) (bool, error)
}

type ServerDeps struct {
	Cfg    *config.Config
	Health HealthChecker
	Log    *slog.Logger
	// TODO: Add service dependencies here
}

func NewServer(deps ServerDeps) http.Handler {
	r := chi.NewRouter()

	r.Use(metrics.Collector(metrics.CollectorOpts{
		Host:  false,
		Proto: true,
		Skip: func(r *http.Request) bool {
			return r.Method == http.MethodOptions || r.URL.Path == "/metrics" || r.URL.Path == "/healthz"
		},
	}))

	r.Use(middleware.RequestID)
	r.Use(api_middleware.RequestIDHeader())
	r.Use(middleware.Recoverer)
	r.Use(middleware.Timeout(deps.Cfg.RequestTimeout))
	r.Use(api_middleware.Cors(deps.Cfg.CORSAllowedOrigins, deps.Cfg.CORSAllowCredentials))
	r.Use(api_middleware.SecurityHeaders())
	r.Use(middleware.RequestSize(deps.Cfg.MaxBodyBytes))
	r.Use(api_middleware.Heartbeat(deps.Health, "/healthz"))

	r.Use(httplog.RequestLogger(deps.Log, &httplog.Options{
		Level:         slog.LevelInfo,
		Schema:        httplog.SchemaECS.Concise(true),
		RecoverPanics: true,
		Skip: func(r *http.Request, httpStatus int) bool {
			return r.Method == http.MethodOptions || r.URL.Path == "/metrics"
		},
	}))

	r.Handle("/metrics", metrics.Handler())

	// Protected API routes
	r.Route("/api", func(api chi.Router) {
		api.Use(api_middleware.APIKeyAuth(deps.Cfg))

		// TODO: Register handlers here
		// exampleH := NewExampleHandler(deps.ExampleSvc, deps.Log)
		// exampleH.Register(api)
	})

	return r
}
```

### internal/httpapi/middleware/api_key_auth.go

```go
package middleware

import (
	"context"
	"net/http"
	"strconv"

	"{{MODULE}}/internal/config"
	"{{MODULE}}/internal/httpx"
)

type apiKeyContextKey int

const (
	APIKeyBotID apiKeyContextKey = iota
)

func APIKeyAuth(cfg *config.Config) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			key := r.Header.Get("x-api-key")
			if key == "" {
				key = r.Header.Get("X-API-Key")
			}
			if key == "" {
				httpx.WriteError(w, r, http.StatusUnauthorized, httpx.CodeUnauthorized, "missing X-API-Key header", nil)
				return
			}
			if _, ok := cfg.APIKeys[key]; !ok {
				httpx.WriteError(w, r, http.StatusForbidden, httpx.CodeForbidden, "invalid X-API-Key header", nil)
				return
			}

			botID := r.Header.Get("x-api-bot-id")
			if botID == "" {
				botID = r.Header.Get("X-API-BOT-ID")
			}

			if botID == "" {
				httpx.WriteError(w, r, http.StatusUnauthorized, httpx.CodeUnauthorized, "missing X-API-BOT-ID header", nil)
				return
			}

			id, err := strconv.ParseInt(botID, 10, 64)
			if err != nil {
				httpx.WriteError(w, r, http.StatusUnauthorized, httpx.CodeUnauthorized, "invalid X-API-BOT-ID header", nil)
				return
			}

			ctx := context.WithValue(r.Context(), APIKeyBotID, id)
			next.ServeHTTP(w, r.WithContext(ctx))
		})
	}
}
```

### internal/httpapi/middleware/cors.go

```go
package middleware

import "net/http"

func Cors(allowedOrigins []string, allowCredentials bool) func(http.Handler) http.Handler {
	allow := make(map[string]struct{}, len(allowedOrigins))
	for _, o := range allowedOrigins {
		allow[o] = struct{}{}
	}
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			origin := r.Header.Get("Origin")
			if origin != "" {
				if _, ok := allow[origin]; ok {
					w.Header().Set("Access-Control-Allow-Origin", origin)
					if allowCredentials {
						w.Header().Set("Access-Control-Allow-Credentials", "true")
					}
				}
				w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, PATCH, DELETE, OPTIONS")
				w.Header().Set("Access-Control-Allow-Headers", "Authorization, Content-Type, X-Requested-With, X-Signature, X-Timestamp, x-api-key, X-API-Key, X-Request-Id")
				w.Header().Set("Access-Control-Expose-Headers", "X-Request-Id, X-Trace-Id")
				w.Header().Set("Access-Control-Max-Age", "600")
			}
			if r.Method == http.MethodOptions {
				w.WriteHeader(http.StatusNoContent)
				return
			}
			next.ServeHTTP(w, r)
		})
	}
}
```

### internal/httpapi/middleware/security_headers.go

```go
package middleware

import "net/http"

func SecurityHeaders() func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.Header().Set("X-Content-Type-Options", "nosniff")
			w.Header().Set("X-Frame-Options", "DENY")
			w.Header().Set("Referrer-Policy", "no-referrer")
			w.Header().Set("Permissions-Policy", "camera=(), geolocation=()")
			next.ServeHTTP(w, r)
		})
	}
}
```

### internal/httpapi/middleware/request_id_header.go

```go
package middleware

import (
	"net/http"

	"github.com/go-chi/chi/v5/middleware"
)

func RequestIDHeader() func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			rid := r.Header.Get("X-Request-Id")
			if rid == "" {
				rid = middleware.GetReqID(r.Context())
			}
			if rid != "" {
				w.Header().Set("X-Request-Id", rid)
			}
			next.ServeHTTP(w, r)
		})
	}
}
```

### internal/httpapi/middleware/heartbeat.go

```go
package middleware

import (
	"context"
	"net/http"
	"strings"

	"{{MODULE}}/internal/httpx"
)

// HealthChecker verifies backend connectivity.
type HealthChecker interface {
	Ping(ctx context.Context) (bool, error)
}

func Heartbeat(health HealthChecker, endpoint string) func(http.Handler) http.Handler {
	return func(h http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			if (r.Method == http.MethodGet || r.Method == http.MethodHead) && strings.EqualFold(r.URL.Path, endpoint) {
				_, err := health.Ping(context.Background())
				if err != nil {
					httpx.WriteError(w, r, http.StatusInternalServerError, httpx.CodeInternal, "failed to ping database", nil)
					return
				}

				httpx.WriteJSON(w, http.StatusOK, map[string]string{"status": "ok"})
				return
			}
			h.ServeHTTP(w, r)
		})
	}
}
```

### internal/httpx/error.go

```go
package httpx

import (
	"encoding/json"
	"errors"
	"net/http"
	"time"

	"github.com/go-chi/chi/v5/middleware"
	"github.com/go-playground/validator/v10"
)

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

type errorBody struct {
	Error struct {
		Code    ErrorCode   `json:"code"`
		Message string      `json:"message"`
		Details interface{} `json:"details,omitempty"`
	} `json:"error"`
	RequestID string    `json:"request_id"`
	Timestamp time.Time `json:"timestamp"`
}

func WriteJSON(w http.ResponseWriter, status int, v interface{}) {
	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(v)
}

func WriteError(w http.ResponseWriter, r *http.Request, status int, code ErrorCode, message string, details interface{}) {
	rid := r.Header.Get("X-Request-Id")
	if rid == "" {
		rid = middleware.GetReqID(r.Context())
	}
	body := errorBody{RequestID: rid, Timestamp: time.Now().UTC()}
	body.Error.Code = code
	body.Error.Message = message
	if details != nil {
		body.Error.Details = details
	}
	WriteJSON(w, status, body)
}

func WriteValidationError(w http.ResponseWriter, r *http.Request, err error) {
	var verrs validator.ValidationErrors
	if errors.As(err, &verrs) {
		fields := TransformValidationErrors(verrs)
		WriteError(w, r, http.StatusBadRequest, CodeValidation, "validation failed", fields)
		return
	}

	WriteError(w, r, http.StatusUnprocessableEntity, CodeValidation, "validation failed", nil)
}

func HTTPPinErrorHandler(w http.ResponseWriter, r *http.Request, err error) {
	WriteError(w, r, http.StatusUnprocessableEntity, CodeUnprocessable, "validation failed", err.Error())
}
```

### internal/httpx/response.go

```go
package httpx

// DataResponse wraps a single resource.
type DataResponse[T any] struct {
	Data T `json:"data"`
}

// PaginationMeta contains cursor-based pagination metadata.
type PaginationMeta struct {
	Cursor  string `json:"cursor"`
	HasMore bool   `json:"has_more"`
}

// PaginatedResponse wraps a list of items with pagination metadata.
type PaginatedResponse[T any] struct {
	Items      []T            `json:"items"`
	Pagination PaginationMeta `json:"pagination"`
}

// NewPaginatedResponse builds a PaginatedResponse from items fetched with DBLimit() (limit+1).
func NewPaginatedResponse[T any](items []T, limit, offset int) PaginatedResponse[T] {
	hasMore := len(items) > limit
	if hasMore {
		items = items[:limit]
	}

	if items == nil {
		items = []T{}
	}

	var cursor string
	if hasMore {
		cursor = EncodeCursor(offset + limit)
	}

	return PaginatedResponse[T]{
		Items: items,
		Pagination: PaginationMeta{
			Cursor:  cursor,
			HasMore: hasMore,
		},
	}
}
```

### internal/httpx/validation.go

```go
package httpx

import "github.com/go-playground/validator/v10"

type ValidationError struct {
	Path    string `json:"path"`
	Message string `json:"message"`
}

type ValidationErrors struct {
	Fields []ValidationError `json:"fields"`
}

func TransformValidationErrors(verrs validator.ValidationErrors) *ValidationErrors {
	fields := &ValidationErrors{
		Fields: make([]ValidationError, 0, len(verrs)),
	}

	for _, fe := range verrs {
		msg := humanizeTag(fe.Tag(), fe)
		fields.Fields = append(fields.Fields, ValidationError{
			Path:    fe.Field(),
			Message: msg,
		})
	}
	return fields
}

func humanizeTag(tag string, fe validator.FieldError) string {
	switch tag {
	case "required":
		return "is required"
	case "gt":
		if fe.Param() != "" {
			return "must be greater than " + fe.Param()
		}
		return "must be greater than 0"
	case "gte":
		if fe.Param() != "" {
			return "must be greater than or equal to " + fe.Param()
		}
		return "must be greater than or equal to 0"
	case "gtecsfield":
		return "must be greater than or equal to " + fe.Param()
	case "lt":
		if fe.Param() != "" {
			return "must be less than " + fe.Param()
		}
		return "must be less than the limit"
	case "lte":
		if fe.Param() != "" {
			return "must be less than or equal to " + fe.Param()
		}
		return "must be less than or equal to the limit"
	case "min":
		if fe.Param() != "" {
			return "is too short (min " + fe.Param() + ")"
		}
		return "is too short"
	case "max":
		if fe.Param() != "" {
			return "is too long (max " + fe.Param() + ")"
		}
		return "is too long"
	case "oneof":
		return "must be one of " + fe.Param()
	case "required_if":
		return "required if " + fe.Param()
	case "dive":
		return "contains invalid item(s)"
	default:
		return "invalid"
	}
}
```

### internal/httpx/pagination.go

```go
package httpx

// PaginationParams provides cursor-based pagination for list endpoints.
// Embed in request DTOs alongside httpin tags.
type PaginationParams struct {
	Cursor string `in:"query=cursor" json:"cursor" validate:"omitempty"`
	Limit  int    `in:"query=limit;default=20" json:"limit" validate:"min=1,max=100"`
}

// Offset decodes the cursor into an integer offset.
func (p *PaginationParams) Offset() (int, error) {
	return DecodeCursor(p.Cursor)
}

// DBLimit returns Limit+1 so callers can over-fetch one row to detect has_more.
func (p *PaginationParams) DBLimit() int {
	return p.Limit + 1
}
```

### internal/httpx/cursor.go

```go
package httpx

import (
	"encoding/base64"
	"fmt"
	"strconv"
)

func EncodeCursor(offset int) string {
	return base64.StdEncoding.EncodeToString([]byte(strconv.Itoa(offset)))
}

func DecodeCursor(cursor string) (int, error) {
	if cursor == "" {
		return 0, nil
	}

	b, err := base64.StdEncoding.DecodeString(cursor)
	if err != nil {
		return 0, fmt.Errorf("invalid cursor: %w", err)
	}

	offset, err := strconv.Atoi(string(b))
	if err != nil {
		return 0, fmt.Errorf("invalid cursor value: %w", err)
	}

	if offset < 0 {
		return 0, fmt.Errorf("invalid cursor: negative offset")
	}

	return offset, nil
}
```

### .golangci.yml

```yaml
version: "2"

linters:
  default: standard
  exclusions:
    rules:
      - path: internal/repository/metrics/
        linters:
          - revive
        text: "avoid package names"
  enable:
    - bodyclose
    - copyloopvar
    - dupl
    - errname
    - exhaustive
    - gocheckcompilerdirectives
    - goconst
    - gocritic
    - mnd
    - misspell
    - nilerr
    - noctx
    - prealloc
    - predeclared
    - revive
    - sqlclosecheck
    - unconvert
    - unparam
    - usestdlibvars
    - wastedassign
    - whitespace
  settings:
    dupl:
      threshold: 150
    exhaustive:
      default-signifies-exhaustive: true
    goconst:
      min-len: 3
      min-occurrences: 3
    gocritic:
      enabled-tags:
        - diagnostic
        - style
        - performance
      disabled-checks:
        - hugeParam
    mnd:
      ignored-functions:
        - "strconv.FormatInt"
        - "strconv.FormatFloat"
        - "strconv.ParseInt"
        - "strconv.ParseFloat"
    revive:
      rules:
        - name: blank-imports
        - name: context-as-argument
        - name: context-keys-type
        - name: dot-imports
        - name: error-return
        - name: error-strings
        - name: error-naming
        - name: exported
          disabled: true
        - name: increment-decrement
        - name: var-naming
        - name: package-comments
          disabled: true
        - name: range
        - name: receiver-naming
        - name: time-naming
        - name: unexported-return
        - name: indent-error-flow
        - name: errorf
        - name: empty-block
        - name: superfluous-else
        - name: unreachable-code

formatters:
  enable:
    - gofumpt
    - gci
  settings:
    gci:
      sections:
        - standard
        - default
        - prefix({{ORG_PREFIX}})

issues:
  max-same-issues: 5
```

### .env.example

```
PRODUCTION=false
SERVER_ADDR=:8080

CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
CORS_ALLOW_CREDENTIALS=false

API_KEYS=changeme-dev-key

DATABASE_URL=postgresql://user:password@localhost:5432/mydb?sslmode=disable
# DATABASE_URL_RW=
# DATABASE_URL_RO=
# DATABASE_MAX_CONNS=4

MAX_BODY_BYTES=5242880

READ_TIMEOUT=15s
WRITE_TIMEOUT=15s
IDLE_TIMEOUT=60s
REQUEST_TIMEOUT=30s
SHUTDOWN_TIMEOUT=20s
```

### .dockerignore

```
.env
.git
.idea
.vscode
build/
*.md
```

### Taskfile.yml

```yaml
version: "3"

dotenv: [".env", "{{.ENV}}/.env", "{{.HOME}}/.env"]

vars:
  PACKAGE_NAME:
    sh: grep -m 1 "^module" go.mod | awk '{print $2}'
  COMMIT_HASH:
    sh: '[ -n "$SOURCE_COMMIT" ] && echo "$SOURCE_COMMIT" || git rev-parse HEAD || echo "unknown"'
  BUILD_TIME:
    sh: date -u +"%Y-%m-%dT%H:%M:%SZ"
  BUILD_PATH: "{{ .PWD }}/build"

env:
  PACKAGE_NAME: "{{.PACKAGE_NAME}}"
  GOOS: linux
  GOARCH: amd64
  CGO_ENABLED: 0

includes:
  migrate:
    taskfile: Taskfile.migration.yml
    dir: .
  docker:
    taskfile: Taskfile.docker.yml
    dir: .

tasks:
  cleanup:
    desc: Cleanup build artifacts
    cmds:
      - rm -rf {{.BUILD_PATH}}/

  build:
    desc: Build service
    deps: [deps, cleanup]
    cmds:
      - cmd: go build -ldflags="-w -s -X 'main.Version=1.0.0' -X 'main.Commit=$COMMIT_HASH' -X 'main.BuildTime=$BUILD_TIME'" -trimpath -mod vendor -o {{.BUILD_PATH}}/app ./cmd/server
        platforms: [linux/amd64, linux/arm64]

  deps:
    desc: Install go vendor dependencies
    sources:
      - go.mod
      - go.sum
    cmds:
      - go env -w GOPROXY=https://proxy.golang.org,direct
      - go env -w GOSUMDB=off
      - go mod download
      - go mod tidy
      - go mod vendor
    generates:
      - vendor/modules.txt
    method: timestamp

  fmt:
    desc: Format go code
    deps: [deps]
    cmds:
      - gci write -s standard -s default -s "prefix({{ORG_PREFIX}})" -s "prefix({{.PACKAGE_NAME}})" --skip-generated cmd internal
      - gofumpt -l -w .

  lint:
    desc: Run go linters
    deps: [fmt]
    cmds:
      - golangci-lint run

  test:
    desc: Run go unit tests
    deps: [deps]
    cmds:
      - go test -mod vendor -covermode=count -coverprofile=coverage.out -coverpkg ./... ./...

  default:
    cmds:
      - task -l
```

### Taskfile.migration.yml

```yaml
version: "3"

env:
  GOOSE_DRIVER: postgres
  GOOSE_DBSTRING: "{{.DATABASE_URL}}"
  GOOSE_MIGRATION_DIR: "{{.USER_WORKING_DIR}}/migrations"
  BUILD_PATH: "{{ .PWD }}/build"

tasks:
  build:goose:
    desc: Build goose
    cmds:
      - cmd: |
          git clone https://github.com/pressly/goose
          cd goose && go mod tidy
          go build \
            -ldflags="-s -w" \
            -tags='no_clickhouse no_libsql no_mssql no_mysql no_sqlite3 no_vertica no_ydb' \
            -o {{.BUILD_PATH}}/goose ./cmd/goose
      - cmd: rm -rf goose

  up:
    desc: "Apply all up migrations to the database"
    cmds:
      - "{{.BUILD_PATH}}/goose up"

  down:
    desc: "Roll back the last applied migration"
    cmds:
      - "{{.BUILD_PATH}}/goose down"

  new:
    desc: "Create a new timestamped migration pair; usage: task migrate:new name=<snake_case>"
    vars:
      name: '{{.name | default "new_migration"}}'
    cmds:
      - cmd: "{{.BUILD_PATH}}/goose create {{.name}} sql"
```

### Taskfile.docker.yml

```yaml
version: "3"

vars:
  PACKAGE_NAME:
    sh: grep -m 1 "^module" ./go.mod | awk '{print $2}' | xargs basename
  REPO: 3264cf45-honest-bittern.registry.twcstorage.ru
  NOW:
    sh: date -u +"%Y-%m-%dT%H:%M:%SZ"

tasks:
  build:
    desc: Build the docker image
    vars:
      TAG_LATEST: "{{.PACKAGE_NAME}}:latest"
      TAG_SHA: "{{.PACKAGE_NAME}}:{{.IMAGE_TAG}}"
    cmds:
      - docker rmi -f '{{.TAG_LATEST}}'
      - SOURCE_DATE_EPOCH= docker build --build-arg BUILD_TIME={{.NOW}} -t '{{.PACKAGE_NAME}}' ../ -f Dockerfile
      - docker tag '{{.TAG_LATEST}}' {{.REPO}}/{{.TAG_LATEST}}
      - docker push {{.REPO}}/{{.TAG_LATEST}}
      - echo "Build started at {{.NOW}}"
  default:
    cmds:
      - task -l
```

### Dockerfile

Replace `{{SERVICE_DIR}}` with the service directory name.

```dockerfile
FROM alpine:3.22.2 AS builder

WORKDIR /svc

RUN apk add --no-cache build-base libffi-dev openssl-dev zlib-dev curl bash openssh-client git

RUN mkdir -p ~/.ssh && ssh-keyscan github.com >> ~/.ssh/known_hosts

RUN curl -fsSL https://get.jetpack.io/devbox | FORCE=1 bash

COPY devbox.json devbox.lock ./

RUN devbox install

COPY ./{{SERVICE_DIR}} /svc

RUN --mount=type=ssh \
    --mount=type=cache,target=/root/.cache/go-build \
    devbox run -- task build migrate:build:goose

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

### entrypoint.sh

```sh
#!/bin/sh
set -e

/svc/goose -dir /svc/migrations postgres "$DATABASE_URL" up

exec /svc/app
```

### migrations/<timestamp>\_init.sql

Use the current timestamp for the filename (YYYYMMDDHHMMSS format).

```sql
-- +goose Up
-- +goose StatementBegin
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
DROP FUNCTION IF EXISTS set_updated_at();
-- +goose StatementEnd
```

### go.mod

```
module {{MODULE}}

go 1.26.1

require (
	github.com/ggicci/httpin v0.20.3
	github.com/go-chi/chi/v5 v5.2.5
	github.com/go-chi/httplog/v3 v3.3.0
	github.com/go-chi/httprate v0.15.0
	github.com/go-chi/metrics v0.1.1
	github.com/go-playground/validator/v10 v10.30.1
	github.com/golang-cz/devslog v0.0.15
	github.com/google/uuid v1.6.0
	github.com/jackc/pgx/v5 v5.9.1
	github.com/joho/godotenv v1.5.1
	github.com/prometheus/client_golang v1.23.2
)
```

## Post-scaffold steps

After generating all files, tell the user:

1. Run `cd {{SERVICE_DIR}} && devbox shell` to enter the dev environment
2. Run `task deps` to download and vendor dependencies
3. Copy `.env.example` to `.env` and adjust values
4. Run `task migrate:build:goose && task migrate:up` to apply the init migration
5. Run `task build` to verify the build
6. Run `task lint` to verify code quality
7. Start adding domain entities, repositories, services, and handlers following the patterns in the `golang-service` skill
