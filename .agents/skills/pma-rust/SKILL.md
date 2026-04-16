---
name: pma-rust
description: Rust implementation guide for PMA-managed multi-crate workspace projects. Covers workspace config, pinned stable toolchains, strict linting with clippy and cargo-cranky, async data access (Diesel-async or SQLx), Axum/Tokio service patterns, layered config with figment + clap, rustls-only TLS, OpenTelemetry observability, and CI quality gates.
---

# Rust Project Implementation Guide

Use this skill together with `/pma`. `/pma` controls workflow, approval, and task tracking; this guide defines the implementation baseline after approval.

Keep this entry file small. Load only the reference packs needed for the task.

## Scope

For PMA-managed Rust workspace projects, especially services and CLIs built from multiple crates.

Not for ad hoc one-file Rust examples, embedded targets, or non-PMA workflows.

## Loading Order

1. Always load `references/baseline.md` first.
2. Load `references/toolchain-and-workspace.md` for workspace structure, Cargo defaults, toolchain pinning, lint setup, and common crate conventions.
3. Load `references/runtime-and-data.md` for error handling, architecture, Axum, Diesel, SQLx, config loading, and signal handling.
4. Load `references/delivery.md` for security, logging, observability, testing, CI, and Git workflow.

## Quick Routing

- New workspace or crate layout: `references/toolchain-and-workspace.md`
- Axum services, config layering, DB access, signal handling: `references/runtime-and-data.md`
- security review, telemetry, testing, CI, release readiness: `references/delivery.md`
- default stack, quality gates, naming, core conventions: `references/baseline.md`

## Reference Packs

- `references/baseline.md`
  Scope, stack defaults, quality gates, naming, and core code quality expectations.
- `references/toolchain-and-workspace.md`
  Workspace layout, `Cargo.toml`, toolchain pinning, compiler flags, and lint configuration.
- `references/runtime-and-data.md`
  Error handling, architecture patterns, database strategy, config layering, Axum runtime, and shutdown.
- `references/delivery.md`
  Security, logging, observability, testing, CI, and Git conventions.

If the repository has already chosen a different path, keep that choice explicit and apply it consistently across code, scripts, docs, and CI.
