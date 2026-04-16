//! Fuzz target for manifest/config.json parsing.
//!
//! Tests that the EncryptionConfig deserializer handles malformed JSON
//! gracefully without panicking.

#![no_main]

use libfuzzer_sys::fuzz_target;

use coding_agent_search::pages::encrypt::EncryptionConfig;

fuzz_target!(|data: &[u8]| {
    // Try to parse arbitrary bytes as UTF-8 first
    if let Ok(json_str) = std::str::from_utf8(data) {
        // Attempt to deserialize as EncryptionConfig
        // This should never panic, only return parse errors
        let _: Result<EncryptionConfig, _> = serde_json::from_str(json_str);
    }

    // Also try direct byte parsing (for potential encoding issues)
    let _: Result<EncryptionConfig, _> = serde_json::from_slice(data);
});
