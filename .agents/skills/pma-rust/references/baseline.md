# PMA-Rust Baseline

## Scope

This pack is for PMA-managed Rust workspace projects, especially service and CLI codebases.

Goals:

- pinned stable toolchain
- strict linting and reproducible builds
- explicit error boundaries
- async runtime and HTTP defaults that are easy to review
- security-first networking and config defaults

## Tech Stack

### Required

| Category | Technology | Notes |
|---|---|---|
| Toolchain | stable Rust | pinned via `rust-toolchain.toml` |
| Runtime | Tokio | async foundation |
| HTTP | Axum | default service framework |
| Config | figment + clap | layered config and CLI overrides |
| Errors | `thiserror` plus `anyhow` at boundaries | keep typed domain errors |
| Lint | clippy + cargo-cranky | strict linting |
| Security | rustls only | OpenSSL disallowed |

### Default

| Category | Technology | Notes |
|---|---|---|
| Workspace | multi-crate Cargo workspace | shared dependency policy |
| Data access | Diesel async + deadpool | default DB path |
| Alternative data access | SQLx | supported alternative |
| Serialization | serde | derive-based serialization |
| Logging | tracing | structured logs |
| Observability | OpenTelemetry | when deployment context needs it |

## Required Quality Gates

Every PMA-Rust project should define:

- `cargo fmt --check`
- `cargo clippy --workspace --all-targets -- -D warnings`
- `cargo cranky --all-targets --all-features -- -D warnings`
- `cargo test --workspace`
- release build verification
- dependency and policy checks such as `cargo deny` when the repo uses them

## Required Conventions

| Area | Convention |
|---|---|
| Error types | per-crate `thiserror` enums, `anyhow` only at boundaries |
| Shared state | `Arc<T>` and immutable config by default |
| Secrets | redact from debug output |
| CLI | clap derive |
| Shutdown | handle signals and drain work cleanly |
| Unsafe | forbid unless there is a documented reason |

## Naming

| Element | Convention |
|---|---|
| Types and traits | `PascalCase` |
| Functions and modules | `snake_case` |
| Constants | `SCREAMING_SNAKE_CASE` |
| Crates | stable, project-prefixed names |

## Code Quality

- prefer immutable data by default
- keep files focused
- keep functions small when practical
- avoid `unwrap` and `expect` in library and runtime code
- prefer borrowing over cloning when ownership does not require a move
