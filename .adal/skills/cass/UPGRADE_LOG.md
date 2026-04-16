# Dependency Upgrade Log

**Date:** 2026-02-17  
**Project:** coding_agent_session_search (`cass`)  
**Language:** Rust

## Summary
- **Updated:** 3 direct dependency lines in `Cargo.toml` (`reqwest`, `rand`, `rand_chacha`)
- **Migrated code:** rand 0.10 API updates across runtime/test/bench callsites
- **Validated:** `cargo check --all-targets`, `cargo fmt --check`, `cargo clippy --all-targets -- -D warnings`
- **Remaining behind latest:** 3 transitive crates (`generic-array`, `hnsw_rs`, `libc`)

## Direct Dependency Updates

### reqwest: 0.12.28 -> 0.13.2
- **Manifest change:** `features = ["json", "rustls-tls", "blocking", "multipart"]` -> `features = ["json", "rustls", "blocking", "multipart"]`
- **Reason:** reqwest 0.13 removed `rustls-tls` feature name
- **Status:** ✅ Compiles and passes strict clippy

### rand: 0.8.5 -> 0.10.0
- **Manifest change:** `rand = "0.8"` -> `rand = "0.10"`
- **Code migration:** replaced old APIs (`thread_rng`, `gen`, `gen_range`) with rand 0.10 APIs (`rng`, `random`, `random_range`) and updated RNG callsites used by export/encryption helpers
- **Status:** ✅ Compiles and passes strict clippy

### rand_chacha: 0.3.1 -> 0.10.0
- **Manifest change:** dev dependency `rand_chacha = "0.3"` -> `rand_chacha = "0.10"`
- **Code migration:** updated deterministic test RNG usage in `tests/util/mod.rs`
- **Status:** ✅ Compiles and passes strict clippy

## Cargo Resolution Notes
- `cargo update --verbose` now reports only these unresolved transitive updates:
  - `generic-array v0.14.7` (available `0.14.9`)
  - `hnsw_rs v0.3.2` (available `0.3.3`)
  - `libc v0.2.180` (available `0.2.182`)

## Validation Run
- `cargo check --all-targets` ✅
- `cargo fmt --check` ✅
- `cargo clippy --all-targets -- -D warnings` ✅

## Files Touched for rand/reqwest Migration
- `Cargo.toml`
- `Cargo.lock`
- `src/lib.rs`
- `src/pages/encrypt.rs`
- `src/pages/key_management.rs`
- `src/pages/qr.rs`
- `src/pages/wizard.rs`
- `src/html_export/encryption.rs`
- `tests/util/mod.rs`
- `benches/crypto_perf.rs`
- `benches/export_perf.rs`

---

## 2026-02-18 Follow-up Update

### Summary
- Ran `cargo update --verbose` in `coding_agent_session_search`
- Updated lockfile to latest compatible crates available in this environment
- Re-validated code quality gates and targeted regression tests after updates

### Lockfile updates applied
- `aws-lc-rs`: `1.15.4 -> 1.16.0`
- `bumpalo`: `3.19.1 -> 3.20.1`
- `hnsw_rs`: `0.3.2 -> 0.3.3`
- `native-tls`: `0.2.16 -> 0.2.18`
- `toml`: `1.0.2+spec-1.1.0 -> 1.0.3+spec-1.1.0`
- resolver-selected transitive adjustment: `indexmap 2.13.0 -> 2.12.1`

### Remaining behind absolute latest (from cargo update output)
- `generic-array 0.14.7` (latest `0.14.9`)
- `libc 0.2.180` (latest `0.2.182`)

### Post-update validation
- `cargo fmt --check` ✅
- `cargo check --all-targets` ✅
- `cargo clippy --all-targets -- -D warnings` ✅
- Targeted regressions:
  - `cargo test --test connector_aider aider_detect_` ✅
  - `cargo test --test connector_codex codex_detect_` ✅
  - `cargo test --test connector_opencode opencode_computes_started_ended_at` ✅
  - `cargo test --test cross_workstream_integration inline_analytics_badges_match_detail_modal_metrics` ✅

### Full-suite note
- `cargo test` now advances deep into the suite and all newly touched regression areas pass.
- There is still an existing long-running/hanging case in `tests/e2e_error_recovery.rs` (`test_corrupted_index_triggers_rebuild`) that prevented a clean single-command completion in this session.

---

## 2026-02-19 Dependency Update

### Summary
- Ran `cargo update` in `coding_agent_session_search`
- **Updated:** 4 crates | **Unchanged behind latest:** 3 (transitive constraints)
- Build verification via code review (full `cargo check` blocked by pre-existing ftui-widgets errors in sibling repo)

### Lockfile updates applied

| Crate | Old | New | Type | Notes |
|-------|-----|-----|------|-------|
| bumpalo | 3.20.1 | 3.20.2 | Patch | Internal arena allocator (transitive). No API changes. |
| clap | 4.5.59 | 4.5.60 | Patch | Bug fixes only. Includes clap_builder 4.5.59→4.5.60. |
| fastembed | 5.9.0 | 5.11.0 | Minor | New `external_initializers` field on `UserDefinedEmbeddingModel` (v5.10). TLS backend selection (v5.9). Nomic v2 MoE support (v5.11). |
| security-framework | 3.6.0 | 3.7.0 | Minor | macOS-only. Includes security-framework-sys 2.16.0→2.17.0. |

### fastembed 5.9→5.11 compatibility verification
- v5.10 added `external_initializers` field to `UserDefinedEmbeddingModel` — breaks struct-literal construction
- Our code uses `UserDefinedEmbeddingModel::new()` constructor (not struct literals) in both `src/search/fastembed_embedder.rs` and `frankensearch-embed` — **not affected**
- `pooling` field remains `pub` with type `Option<Pooling>` — field assignment pattern unchanged

### Remaining behind absolute latest
| Crate | Current | Available | Reason |
|-------|---------|-----------|--------|
| generic-array | 0.14.7 | 0.14.9 | Transitive constraint |
| indexmap | 2.12.1 | 2.13.0 | Transitive constraint |
| libc | 0.2.180 | 0.2.182 | Transitive constraint |

### Build verification
- Full `cargo check` blocked by **pre-existing** compilation errors in `frankentui` sibling repo (`ftui-widgets`: 27 errors — missing lifetime specifiers, missing variables, unstable features). These errors exist independently of this update.
- Compatibility verified through code review of all 4 updated crates' changelogs and our usage patterns.
