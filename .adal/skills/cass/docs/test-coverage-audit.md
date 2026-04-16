# Test Coverage Audit: coding_agent_session_search (cass)

**Date**: 2026-01-12
**Bead**: coding_agent_session_search-vh1n

---

## Executive Summary

- **Total Tests**: ~1,938 tests
  - Inline unit tests (src/): ~1,091
  - External tests (tests/): ~847
- **Mock/Fake Usage**: All mocks are test helpers within `#[cfg(test)]` modules - **no external mock libraries**
- **Critical Gaps Identified**: 3 high-risk modules with 0 or minimal inline tests

---

## 1. Test Classification by Level

### Unit Tests (Single component/function isolation)
| Location | Count | Notes |
|----------|-------|-------|
| src/connectors/*.rs | 447 | Comprehensive - each connector has 14-57 tests |
| src/search/*.rs | 277 | Excellent coverage of query.rs (147 tests) |
| src/sources/*.rs | 159 | Good coverage of config, sync, provenance |
| src/ui/*.rs | 108 | tui.rs (89), data.rs (8), time_parser.rs (4) |
| src/pages/*.rs | 44 | fts.rs (15), size.rs (10), encrypt.rs (8) |
| src/storage/sqlite.rs | 36 | Storage layer coverage |
| src/indexer/mod.rs | 20 | Indexer logic |
| tests/connector_*.rs | 266 | Additional external connector tests |
| tests/storage.rs | 44 | Storage integration tests |
| tests/ui_*.rs | 73 | UI component tests |
| tests/search_*.rs | 8 | Search algorithm tests |
| **Unit Subtotal** | **~1,482** | |

### Integration Tests (Multiple modules together)
| File | Count | Coverage |
|------|-------|----------|
| tests/setup_workflow.rs | 26 | Setup wizard flow |
| tests/semantic_integration.rs | 21 | Semantic search pipeline |
| tests/pages_fts.rs | 15 | Pages full-text search |
| tests/multi_source_integration.rs | 14 | Multi-source handling |
| tests/pages_bundle.rs | 12 | Export bundling |
| tests/pages_export.rs | 10 | Export formats |
| tests/ssh_sync_integration.rs | 10 | SSH sync |
| tests/concurrent_search.rs | 6 | Concurrent access |
| tests/logging.rs | 3 | Log capture |
| tests/memory_tests.rs | 3 | Memory safety |
| tests/ssh_test_helper.rs | 2 | SSH utilities |
| **Integration Subtotal** | **122** | |

### End-to-End Tests (Full application flow)
| File | Count | Coverage |
|------|-------|----------|
| tests/cli_robot.rs | 138 | Robot mode CLI commands |
| tests/e2e_sources.rs | 37 | Source management |
| tests/e2e_filters.rs | 22 | Filter functionality |
| tests/e2e_cli_flows.rs | 20 | CLI workflows |
| tests/e2e_search_index.rs | 15 | Search + index |
| tests/e2e_multi_connector.rs | 8 | Multiple connectors |
| tests/install_scripts.rs | 7 | Installation |
| tests/cli_index.rs | 6 | Index commands |
| tests/perf_e2e.rs | 5 | Performance e2e |
| tests/watch_e2e.rs | 4 | Watch mode |
| tests/perf_proptest.rs | 3 | Property-based perf |
| tests/e2e_index_tui.rs | 1 | TUI indexing |
| tests/e2e_install_easy.rs | 1 | Easy install |
| **E2E Subtotal** | **267** | |

---

## 2. Coverage Gap Matrix by Module

| Module | Inline Tests | External Tests | Gap Level | Priority |
|--------|--------------|----------------|-----------|----------|
| **lib.rs** | **0** | CLI covered by e2e | **HIGH** | P0 |
| **model/** | **0** | None | **HIGH** | P1 |
| **encryption.rs** | **0** | crypto_vectors (3) | **MEDIUM** | P2 |
| **bookmarks.rs** | 8 | None in tests/ | LOW | P3 |
| **export.rs** | 7 | pages_export (10) | LOW | P3 |
| **update_check.rs** | 8 | None | MEDIUM | P2 |
| connectors/ | 447 | 266 | GOOD | - |
| search/ | 277 | 29 | GOOD | - |
| storage/ | 36 | 44 | GOOD | - |
| ui/ | 108 | 73 | GOOD | - |
| pages/ | 44 | 37 | GOOD | - |
| sources/ | 159 | 122 | GOOD | - |
| indexer/ | 20 | 5 | LOW | P3 |

### Critical Gap Details

#### lib.rs (0 tests) - P0 Critical
- **Size**: ~11,500 lines
- **Risk**: Main CLI entry point, arg parsing, command dispatch
- **Contains**: Error types, normalize_args(), execute_cli(), all command handlers
- **Recommendation**: Add unit tests for:
  - Argument normalization/auto-correction
  - Error type conversions
  - Individual command parsing

#### model/ (0 tests) - P1 High
- **Files**: `mod.rs`, `types.rs`
- **Risk**: Core data types (Agent, Conversation, Message, Snippet)
- **Recommendation**: Add tests for:
  - Serialization/deserialization
  - Type conversions
  - Default values

#### encryption.rs (0 inline tests) - P2 Medium
- **External coverage**: tests/crypto_vectors.rs (3 tests)
- **Risk**: Security-critical code
- **Recommendation**: Increase test coverage with:
  - More edge cases
  - Error path testing
  - Key derivation tests

---

## 3. Mock/Fake/Stub Analysis

### Summary
- **External mock libraries**: NONE (no mockall, mockito, etc.)
- **Internal test helpers**: All within `#[cfg(test)]` modules

### Identified Mock/Fake Usage

#### Acceptable Test Fixtures (No Replacement Needed)

| File | Pattern | Purpose |
|------|---------|---------|
| tests/connector_claude.rs | `mock-claude/` directory | Fixture directory for Claude connector tests |
| tests/parse_errors.rs | `mock-claude/` directory | Same fixture pattern |
| tests/e2e_install_easy.rs | `fake_bin/`, fake binaries | Simulates installed tools for install tests |
| tests/semantic_integration.rs | `fake_model.onnx` | Simulates ML model file |
| tests/install_scripts.rs | Fake binary | Upgrade path testing |

#### Internal Test Helpers (Within #[cfg(test)] - Acceptable)

| File | Helper | Purpose |
|------|--------|---------|
| src/search/embedder.rs:190-224 | `MockEmbedder` | Test embedder trait impl |
| src/ui/tui.rs:8976-9008 | `MockHit`, `MockPane` | TUI selection testing |
| src/sources/install.rs:935-1106 | `mock_system_info()`, `mock_resources()` | Install strategy tests |
| src/sources/index.rs:608-674 | `mock_probe_*` functions | Host probe testing |

### Verdict
**No prohibited mock usage found.** All mock/fake patterns are:
1. Test fixture directories (not behavioral mocks)
2. Internal test helpers within `#[cfg(test)]` modules
3. Simple data fixtures for testing

---

## 4. High-Risk Untested Paths

### Error Handling Paths
| Location | Risk | Current Coverage |
|----------|------|------------------|
| lib.rs error types | HIGH | E2E only |
| Storage migrations | MEDIUM | tests/storage.rs |
| Index corruption recovery | MEDIUM | Some in indexer tests |
| SSH connection failures | MEDIUM | ssh_sync_integration |

### Performance/Resource Paths
| Path | Risk | Current Coverage |
|------|------|------------------|
| Large archive (>10K convos) | HIGH | perf_e2e (limited) |
| Memory pressure | MEDIUM | memory_tests (3) |
| Concurrent access | MEDIUM | concurrent_search (6) |

### Security Paths
| Path | Risk | Current Coverage |
|------|------|------------------|
| AES-GCM encryption | HIGH | crypto_vectors (3) |
| Secret scanning | MEDIUM | secret_scan (3) |
| Nonce generation | MEDIUM | security_nonce (7) |

---

## 5. Remediation Priority Ordering

### P0 - Critical (Should block releases)
1. **Add lib.rs unit tests** - Argument parsing, error types, command dispatch
2. **Add model/ unit tests** - Core type serialization/conversion

### P1 - High (Next sprint)
3. **Expand encryption.rs tests** - More vectors, error paths
4. **Add update_check.rs integration tests** - Version comparison, network errors
5. **Large archive performance tests** - 10K+ conversation benchmarks

### P2 - Medium (Backlog)
6. **Migration rollback tests** - Storage schema downgrade paths
7. **TUI interaction coverage** - More keyboard/mouse event tests
8. **Error message quality tests** - User-facing error strings

### P3 - Low (Nice to have)
9. **Bookmarks module external tests**
10. **Indexer edge case coverage**
11. **Export format fidelity tests**

---

## 6. File Links for Key Test Locations

### Inline Tests (src/)
- `src/search/query.rs` - 147 tests (search engine)
- `src/ui/tui.rs` - 89 tests (TUI logic)
- `src/connectors/amp.rs` - 57 tests (Amp connector)
- `src/connectors/mod.rs` - 49 tests (connector framework)
- `src/connectors/gemini.rs` - 46 tests (Gemini connector)

### External Tests (tests/)
- `tests/cli_robot.rs` - 138 tests (robot mode)
- `tests/ui_snap.rs` - 50 tests (UI snapshots)
- `tests/storage.rs` - 44 tests (storage layer)
- `tests/connector_aider.rs` - 39 tests (Aider connector)
- `tests/e2e_sources.rs` - 37 tests (source management)

### Benchmarks (benches/)
- `benches/bench_utils.rs` - Performance benchmarks

---

## 7. Next Steps

1. Create beads for P0 remediation tasks
2. Add lib.rs test module with arg parsing tests
3. Add model/ serialization tests
4. Expand crypto test vectors
5. Schedule performance regression baseline

---

## 8. Connector Test Audit (bead mo6o)

### Fixture Strategy Analysis

**Real Fixture Files (tests/fixtures/):**
| Connector | Fixture Path | Format |
|-----------|--------------|--------|
| aider | fixtures/aider/.aider.chat.history.md | Markdown |
| amp | fixtures/amp/thread-001.json | JSON |
| cline | fixtures/cline/task1/ | JSON files |
| claude_code | fixtures/claude_code_real/projects/ | JSONL |
| codex | fixtures/codex_real/sessions/ | JSONL |
| gemini | fixtures/gemini/hash123/chats/ | JSON |
| opencode | fixtures/opencode_json/ | JSON |
| pi_agent | fixtures/pi_agent/sessions/ | JSONL |
| multi_source | fixtures/multi_source/ | JSONL |

**Inline Fixture Tests (no dedicated fixture files):**
| Connector | Inline Tests | Notes |
|-----------|--------------|-------|
| chatgpt | 30 | Uses inline JSON in test code |
| cursor | 43 | Uses inline data in test code |
| factory | 14 | Uses inline data in test code |

### Mock/Fake Pattern Analysis

**Acceptable Patterns Found:**
- `mock-claude/` - Directory name for test fixtures (NOT behavioral mock)
- `TempDir::new()` - Creates real temporary directories
- Inline JSONL/JSON literals - Mirror actual agent output formats

**No Prohibited Patterns Found:**
- No mockall/mockito library usage
- No trait mocks for Connector interface
- All tests use actual filesystem operations

### Edge Case Coverage (parse_errors.rs, fs_errors.rs)

| Category | Tests | Status |
|----------|-------|--------|
| Invalid JSON syntax | 4 | Covered |
| Missing required fields | 3 | Covered |
| Wrong field types | 2 | Covered |
| Truncated files | 2 | Covered |
| Binary/null bytes | 2 | Covered |
| Non-existent paths | 3 | Covered |
| Permission denied | 2 | Covered (Unix) |
| Symlink handling | 4 | Covered (Unix) |
| Unicode paths | 2 | Covered |
| Empty directories | 2 | Covered |

### Verdict

**Connector tests meet the requirements:**
1. All use real fixture data that mirrors actual on-disk formats
2. No behavioral mocks - only test fixture directories
3. Edge cases comprehensively covered in parse_errors.rs and fs_errors.rs
4. Tests use actual filesystem paths via TempDir

**Minor Improvements (Optional):**
- Add dedicated fixture files for chatgpt, cursor, factory connectors
- Add cross-platform path handling tests for Windows

---

*Generated by test coverage audit - beads vh1n, mo6o*
