//! Fuzz target for config.json structure validation.
//!
//! Tests that the load_config function handles malformed config files
//! gracefully, including edge cases like missing fields, wrong types,
//! and deeply nested structures.

#![no_main]

use arbitrary::Arbitrary;
use libfuzzer_sys::fuzz_target;
use std::fs;
use tempfile::TempDir;

use coding_agent_search::pages::encrypt::load_config;

/// Fuzzer input for config loading.
#[derive(Arbitrary, Debug)]
struct ConfigInput {
    /// Raw JSON content
    json_content: String,
    /// Whether to create payload directory
    create_payload_dir: bool,
    /// Payload file contents (if created)
    payload_content: Vec<u8>,
}

fuzz_target!(|input: ConfigInput| {
    // Create temp directory
    let temp_dir = match TempDir::new() {
        Ok(dir) => dir,
        Err(_) => return,
    };

    // Write config.json
    let config_path = temp_dir.path().join("config.json");
    if fs::write(&config_path, &input.json_content).is_err() {
        return;
    }

    // Optionally create payload directory with a chunk
    if input.create_payload_dir && !input.payload_content.is_empty() {
        let payload_dir = temp_dir.path().join("payload");
        if fs::create_dir_all(&payload_dir).is_ok() {
            let _ = fs::write(payload_dir.join("chunk-00000.bin"), &input.payload_content);
        }
    }

    // Try to load config - should never panic
    let _ = load_config(temp_dir.path());
});
