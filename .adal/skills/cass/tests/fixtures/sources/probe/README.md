# Probe Fixtures

This directory contains JSON fixtures representing real `HostProbeResult` data
for testing the sources/probe functionality without mocks.

## Fixture Files

| File | Description | Use Case |
|------|-------------|----------|
| `indexed_host.json` | Host with cass installed and indexed with 847 sessions | Test normal indexed state |
| `not_indexed_host.json` | Host with cass installed but not yet indexed | Test needs-indexing detection |
| `no_cass_host.json` | Host without cass installed | Test cass-not-found handling |
| `empty_index_host.json` | Host with cass indexed but 0 sessions | Test empty-index re-indexing |
| `unreachable_host.json` | Host that couldn't be reached via SSH | Test connection failure handling |
| `unknown_status_host.json` | Host where cass status couldn't be determined | Test fallback behavior |

## Loading Fixtures in Tests

```rust
use std::path::PathBuf;
use crate::sources::probe::HostProbeResult;

fn load_probe_fixture(name: &str) -> HostProbeResult {
    let path = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("tests/fixtures/sources/probe")
        .join(format!("{}.json", name));
    let content = std::fs::read_to_string(&path).expect("fixture file");
    serde_json::from_str(&content).expect("valid JSON")
}
```

## No-Mock Policy

These fixtures replace the former `mock_probe_*` helper functions that manually
constructed `HostProbeResult` structs. The fixture approach:

1. Uses realistic data captured from actual probe operations
2. Validates the full serde round-trip (JSON parsing)
3. Is easier to maintain and extend
4. Follows the project's no-mock testing policy

See `test-results/no_mock_audit.md` for the full audit.
