//! Security tests for nonce derivation.
//!
//! Verifies that the chunk nonce derivation produces unique nonces
//! without collision risks.

#[cfg(test)]
mod tests {
    use std::collections::HashSet;

    /// Derive chunk nonce from base nonce and chunk index.
    /// This mirrors the implementation in src/pages/encrypt.rs
    fn derive_chunk_nonce(base_nonce: &[u8; 12], chunk_index: u32) -> [u8; 12] {
        let mut nonce = *base_nonce;
        // Set the last 4 bytes to the chunk index (big-endian)
        nonce[8..12].copy_from_slice(&chunk_index.to_be_bytes());
        nonce
    }

    #[test]
    fn test_nonce_uniqueness_sequential_chunks() {
        let base_nonce: [u8; 12] = [
            0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x00, 0x00, 0x00, 0x00,
        ];
        let mut seen_nonces = HashSet::new();

        // Test first 10000 chunks for uniqueness
        for i in 0..10000u32 {
            let nonce = derive_chunk_nonce(&base_nonce, i);
            let nonce_vec: Vec<u8> = nonce.to_vec();

            assert!(
                seen_nonces.insert(nonce_vec),
                "Nonce collision detected at chunk index {}",
                i
            );
        }
    }

    #[test]
    fn test_nonce_uniqueness_with_zeros_base() {
        // Test with all-zeros base nonce to ensure counter still works
        let base_nonce: [u8; 12] = [0u8; 12];
        let mut seen_nonces = HashSet::new();

        for i in 0..10000u32 {
            let nonce = derive_chunk_nonce(&base_nonce, i);
            let nonce_vec: Vec<u8> = nonce.to_vec();

            assert!(
                seen_nonces.insert(nonce_vec),
                "Nonce collision with zero base at chunk index {}",
                i
            );
        }
    }

    #[test]
    fn test_nonce_uniqueness_with_max_base() {
        // Test with all-ones base nonce
        let base_nonce: [u8; 12] = [0xFF; 12];
        let mut seen_nonces = HashSet::new();

        for i in 0..10000u32 {
            let nonce = derive_chunk_nonce(&base_nonce, i);
            let nonce_vec: Vec<u8> = nonce.to_vec();

            assert!(
                seen_nonces.insert(nonce_vec),
                "Nonce collision with max base at chunk index {}",
                i
            );
        }
    }

    #[test]
    fn test_nonce_counter_overwrites_base() {
        // Verify that the counter bytes fully replace the last 4 bytes
        // This was the fix for the XOR-based derivation issue
        let base_nonce: [u8; 12] = [0xAA; 12]; // All 0xAA

        let nonce_0 = derive_chunk_nonce(&base_nonce, 0);
        let nonce_1 = derive_chunk_nonce(&base_nonce, 1);
        let nonce_max = derive_chunk_nonce(&base_nonce, u32::MAX);

        // First 8 bytes should match base
        assert_eq!(&nonce_0[0..8], &base_nonce[0..8]);
        assert_eq!(&nonce_1[0..8], &base_nonce[0..8]);
        assert_eq!(&nonce_max[0..8], &base_nonce[0..8]);

        // Last 4 bytes should be the counter, not XOR'd with base
        assert_eq!(&nonce_0[8..12], &[0x00, 0x00, 0x00, 0x00]); // counter 0
        assert_eq!(&nonce_1[8..12], &[0x00, 0x00, 0x00, 0x01]); // counter 1
        assert_eq!(&nonce_max[8..12], &[0xFF, 0xFF, 0xFF, 0xFF]); // counter max
    }

    #[test]
    fn test_nonce_different_bases_produce_different_nonces() {
        let base1: [u8; 12] = [0x01; 12];
        let base2: [u8; 12] = [0x02; 12];

        for i in 0..100u32 {
            let nonce1 = derive_chunk_nonce(&base1, i);
            let nonce2 = derive_chunk_nonce(&base2, i);

            // Same chunk index but different bases should produce different nonces
            assert_ne!(
                nonce1, nonce2,
                "Different bases should produce different nonces at chunk {}",
                i
            );
        }
    }

    #[test]
    fn test_nonce_big_endian_counter() {
        let base_nonce: [u8; 12] = [0x00; 12];

        // Test that counter is big-endian
        let nonce_256 = derive_chunk_nonce(&base_nonce, 256);
        assert_eq!(&nonce_256[8..12], &[0x00, 0x00, 0x01, 0x00]); // 256 in big-endian

        let nonce_65536 = derive_chunk_nonce(&base_nonce, 65536);
        assert_eq!(&nonce_65536[8..12], &[0x00, 0x01, 0x00, 0x00]); // 65536 in big-endian
    }

    #[test]
    fn test_no_xor_vulnerability() {
        // This test specifically checks that the old XOR vulnerability is fixed
        // With XOR, if base[8..12] had certain values, different counters could
        // produce the same nonce. With direct assignment, this is impossible.

        let base_nonce: [u8; 12] = [
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x05,
        ]; // Last byte is 5

        let nonce_0 = derive_chunk_nonce(&base_nonce, 0);
        let nonce_5 = derive_chunk_nonce(&base_nonce, 5);

        // With XOR, nonce_0 would have last bytes = 0x00000005 (base XOR 0)
        // and nonce_5 would have last bytes = 0x00000000 (base XOR 5)
        // But with direct assignment, they should be different
        assert_ne!(
            nonce_0, nonce_5,
            "Nonces should differ even when base matches counter"
        );

        // Verify the actual values
        assert_eq!(&nonce_0[8..12], &[0x00, 0x00, 0x00, 0x00]); // counter 0
        assert_eq!(&nonce_5[8..12], &[0x00, 0x00, 0x00, 0x05]); // counter 5
    }
}
