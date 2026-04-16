# PMA-Rust Runtime And Data

## Error Handling

- use `thiserror` enums per crate or module boundary
- use `anyhow` only at top-level integration boundaries
- never panic for recoverable runtime errors
- translate internal errors to safe HTTP or CLI output at the edge

## Architecture Patterns

- services own business logic
- protocol or transport layers own request handling
- shared state should be cloneable and cheap to pass
- keep mutation behind explicit interfaces

## Database Strategy

### Default: Diesel Async Plus Deadpool

Prefer when:

- schema control matters
- compile-time safety matters
- the team accepts the Diesel macro model

### Alternative: SQLx

Prefer when:

- runtime SQL ergonomics matter more
- async SQL workflow needs are simpler with SQLx

Whatever path is chosen:

- keep migrations committed
- keep pool creation centralized
- keep DB-specific code in the data crate or module

## Configuration

Layer config with figment in this order:

```text
defaults -> config file -> environment -> CLI flags
```

Rules:

- keep config structs explicit
- use clap derive for CLI overrides
- validate after merge
- document env variable mapping

## Axum Runtime

Default guidance:

- centralize router composition
- keep handler functions thin
- store shared state in `AppState`
- use middleware for auth, tracing, and request shaping
- prefer graceful shutdown wired from `main`

## Signal Handling

- handle `SIGINT` and `SIGTERM`
- stop accepting new work before exit
- drain in-flight requests
- flush telemetry and close DB pools
