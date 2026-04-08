---
name: golang-programming
description: Go expert patterns — goroutines, channels, interfaces, error handling, HTTP servers, gRPC, testing, performance for MAARS Go agents
---

# Go Programming — MAARS Reference

## Goroutines & Channels
```go
package main

import (
    "context"
    "sync"
    "time"
)

// Fan-out/fan-in pattern
func pipeline(ctx context.Context, urls []string) <-chan Result {
    results := make(chan Result, len(urls))
    var wg sync.WaitGroup
    
    for _, url := range urls {
        wg.Add(1)
        go func(u string) {
            defer wg.Done()
            select {
            case <-ctx.Done():
                return
            case results <- fetch(u):
            }
        }(url)
    }
    
    go func() {
        wg.Wait()
        close(results)
    }()
    
    return results
}

// Worker pool
func workerPool(ctx context.Context, jobs <-chan Job, numWorkers int) <-chan Result {
    results := make(chan Result)
    var wg sync.WaitGroup
    
    for i := 0; i < numWorkers; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            for job := range jobs {
                select {
                case <-ctx.Done():
                    return
                case results <- process(job):
                }
            }
        }()
    }
    
    go func() { wg.Wait(); close(results) }()
    return results
}
```

## Error Handling
```go
import "errors"

// Sentinel errors
var (
    ErrNotFound    = errors.New("not found")
    ErrUnauthorized = errors.New("unauthorized")
)

// Custom error type
type AppError struct {
    Code    int
    Message string
    Cause   error
}

func (e *AppError) Error() string {
    if e.Cause != nil {
        return fmt.Sprintf("%s: %v", e.Message, e.Cause)
    }
    return e.Message
}

func (e *AppError) Unwrap() error { return e.Cause }

func NewNotFoundError(msg string) *AppError {
    return &AppError{Code: 404, Message: msg}
}

// Usage
func GetUser(id int) (*User, error) {
    user, err := db.Find(id)
    if err != nil {
        return nil, fmt.Errorf("GetUser(%d): %w", id, err)
    }
    if user == nil {
        return nil, fmt.Errorf("GetUser(%d): %w", id, ErrNotFound)
    }
    return user, nil
}

// Check error type
if errors.Is(err, ErrNotFound) { /* handle */ }
var appErr *AppError
if errors.As(err, &appErr) { fmt.Println(appErr.Code) }
```

## Interfaces
```go
// Implicit interface satisfaction
type Storage interface {
    Get(ctx context.Context, key string) ([]byte, error)
    Set(ctx context.Context, key string, value []byte, ttl time.Duration) error
    Delete(ctx context.Context, key string) error
}

// Any type implementing these methods satisfies Storage
type RedisStorage struct { client *redis.Client }
type MemoryStorage struct { data sync.Map }

// io.Reader / io.Writer pattern
type Reader interface { Read(p []byte) (n int, err error) }
type Writer interface { Write(p []byte) (n int, err error) }
type ReadWriter interface { Reader; Writer }  // embedding

// Functional options pattern
type Server struct { host string; port int; timeout time.Duration }
type Option func(*Server)

func WithHost(host string) Option { return func(s *Server) { s.host = host } }
func WithTimeout(d time.Duration) Option { return func(s *Server) { s.timeout = d } }

func NewServer(opts ...Option) *Server {
    s := &Server{host: "localhost", port: 8080, timeout: 30*time.Second}
    for _, opt := range opts {
        opt(s)
    }
    return s
}
```

## HTTP Server (net/http + chi)
```go
import (
    "encoding/json"
    "net/http"
    "github.com/go-chi/chi/v5"
    "github.com/go-chi/chi/v5/middleware"
)

func NewRouter(h *Handler) *chi.Mux {
    r := chi.NewRouter()
    r.Use(middleware.Logger)
    r.Use(middleware.Recoverer)
    r.Use(middleware.RequestID)
    r.Use(middleware.Compress(5))
    
    r.Route("/api/v1", func(r chi.Router) {
        r.Use(AuthMiddleware)
        r.Get("/users/{id}", h.GetUser)
        r.Post("/users", h.CreateUser)
        r.Put("/users/{id}", h.UpdateUser)
        r.Delete("/users/{id}", h.DeleteUser)
    })
    
    return r
}

func (h *Handler) GetUser(w http.ResponseWriter, r *http.Request) {
    id := chi.URLParam(r, "id")
    user, err := h.svc.GetUser(r.Context(), id)
    if err != nil {
        if errors.Is(err, ErrNotFound) {
            http.Error(w, "not found", http.StatusNotFound)
            return
        }
        http.Error(w, "internal error", http.StatusInternalServerError)
        return
    }
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(user)
}
```

## Testing
```go
import (
    "testing"
    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/mock"
    "github.com/stretchr/testify/require"
)

// Table-driven tests
func TestGetUser(t *testing.T) {
    cases := []struct {
        name    string
        id      int
        wantErr bool
        want    *User
    }{
        {"valid user", 1, false, &User{ID: 1}},
        {"not found", 999, true, nil},
    }
    
    for _, tc := range cases {
        t.Run(tc.name, func(t *testing.T) {
            result, err := GetUser(tc.id)
            if tc.wantErr {
                require.Error(t, err)
                return
            }
            require.NoError(t, err)
            assert.Equal(t, tc.want.ID, result.ID)
        })
    }
}

// Mock interface
type MockStorage struct { mock.Mock }
func (m *MockStorage) Get(ctx context.Context, key string) ([]byte, error) {
    args := m.Called(ctx, key)
    return args.Get(0).([]byte), args.Error(1)
}
```

## Context & Cancellation
```go
// Always pass context as first arg
func ProcessRequest(ctx context.Context, data []byte) error {
    // Check if cancelled
    select {
    case <-ctx.Done():
        return ctx.Err()
    default:
    }
    
    // With timeout
    ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
    defer cancel()
    
    // With value (use typed keys)
    type contextKey string
    const userKey contextKey = "user"
    ctx = context.WithValue(ctx, userKey, user)
    user := ctx.Value(userKey).(*User)
    
    return nil
}
```

## Models to Use
- **Go code generation**: `claude-opus-4-6` (understands Go idioms)
- **Concurrency design**: `claude-opus-4-6`
- **Performance optimization**: `claude-sonnet-4-6`
