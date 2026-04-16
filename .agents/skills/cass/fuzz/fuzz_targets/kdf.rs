//! Fuzz target for key derivation through the encryption engine.
//!
//! Tests that the EncryptionEngine handles arbitrary passwords and
//! recovery secrets without panicking.

#![no_main]

use arbitrary::Arbitrary;
use libfuzzer_sys::fuzz_target;

use coding_agent_search::pages::encrypt::EncryptionEngine;

/// Fuzzer input for key derivation paths.
#[derive(Arbitrary, Debug)]
struct KdfInput {
    /// Password input (can be any UTF-8 string)
    password: String,
    /// Recovery secret (arbitrary bytes)
    recovery_secret: Vec<u8>,
    /// Chunk size for engine (will be clamped)
    chunk_size: usize,
    /// Whether to test password slot
    test_password: bool,
    /// Whether to test recovery slot
    test_recovery: bool,
}

fuzz_target!(|input: KdfInput| {
    // Clamp chunk size to reasonable range
    let chunk_size = input.chunk_size.clamp(1024, 8 * 1024 * 1024);

    let Ok(mut engine) = EncryptionEngine::new(chunk_size) else {
        return;
    };

    // Test password slot addition - should never panic
    if input.test_password {
        let _ = engine.add_password_slot(&input.password);
    }

    // Test recovery slot addition - should never panic
    if input.test_recovery && !input.recovery_secret.is_empty() {
        let _ = engine.add_recovery_slot(&input.recovery_secret);
    }

    // Try adding multiple slots
    if input.test_password && input.test_recovery {
        let Ok(mut engine2) = EncryptionEngine::new(chunk_size) else {
            return;
        };
        let _ = engine2.add_password_slot(&input.password);
        let _ = engine2.add_recovery_slot(&input.recovery_secret);
    }
});
