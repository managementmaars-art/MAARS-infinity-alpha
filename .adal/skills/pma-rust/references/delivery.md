# PMA-Rust Delivery

## Security

Review:

- constant-time secret comparison
- SSRF risk in outbound HTTP
- concurrent cache correctness
- secret redaction
- rustls-only TLS usage

Pre-commit checklist:

- no hardcoded secrets
- no panic-based error handling in runtime paths
- auth boundaries reviewed
- unsafe code either absent or justified explicitly

## Logging And Observability

- use `tracing` for logs and spans
- add OpenTelemetry only when the deployment context benefits from it
- keep correlation between traces and logs
- expose health or readiness endpoints where the runtime needs them

## Testing

Recommended layers:

- unit tests in crate modules
- integration tests under `tests/` when cross-crate behavior matters
- async tests using Tokio test utilities
- property-based tests only where invariants benefit from them

## CI Pipeline

Typical stages:

- fmt
- clippy and cranky
- tests
- release build
- dependency policy checks

## Git Conventions

- use English remote-visible metadata
- use conventional commits
- keep PR summaries concise and test plans explicit

## Review Focus

Prioritize:

- panic boundaries
- blocking work inside async code
- resource lifetime
- error translation
- security-sensitive outbound IO
