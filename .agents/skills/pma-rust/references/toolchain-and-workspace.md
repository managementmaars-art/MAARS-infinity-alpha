# PMA-Rust Toolchain And Workspace

## Workspace Structure

Typical layout:

```text
Cargo.toml
rust-toolchain.toml
.cargo/
crates/
  app/
  core/
  db/
  common/
tests/
```

Rules:

- centralize shared dependencies in `[workspace.dependencies]`
- keep crate responsibilities explicit
- avoid circular crate relationships

## Workspace Cargo Defaults

- set resolver to `"2"`
- define `default-members`
- keep edition and license at workspace level when appropriate
- use shared dependency versions instead of drifting crate-local versions

## Toolchain Pinning

- pin stable Rust in `rust-toolchain.toml`
- keep target toolchain and CI toolchain aligned
- document any required components such as `clippy` or `rustfmt`

## Compiler And Cargo Flags

- keep reproducible flags in `.cargo/config.toml`
- prefer rustls-backed dependencies
- forbid hidden platform-specific behavior unless the product needs it

## Lint Configuration

Common files:

- `rustfmt.toml`
- `clippy.toml`
- `Cranky.toml`
- `deny.toml`

Use them to keep policy centralized rather than repeating flags across scripts.
