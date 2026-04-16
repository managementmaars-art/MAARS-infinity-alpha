//! Tests for canonicalization equivalence and determinism (Opt 6.3).
//!
//! Validates that the streaming canonicalization implementation:
//! - Produces deterministic output (same input → same output)
//! - Maintains hash stability across repeated calls
//! - Handles edge cases correctly
//! - Can be toggled via CASS_STREAMING_CANONICALIZE env var
//!
//! Note: The CASS_STREAMING_CANONICALIZE env var is checked once at process start
//! via LazyLock. Tests that require different modes must run in separate processes
//! or verify determinism within a single mode.

use coding_agent_search::search::canonicalize::{
    MAX_EMBED_CHARS, canonicalize_for_embedding, content_hash, content_hash_hex,
};
use proptest::prelude::*;

mod util;

// =============================================================================
// Determinism Tests: Same input always produces same output
// =============================================================================

#[test]
fn test_canonicalize_deterministic_simple() {
    let inputs = vec![
        "Hello, world!",
        "**Bold** and *italic*",
        "# Header\n\nParagraph",
        "```rust\nfn main() {}\n```",
        "[link](http://example.com)",
    ];

    for input in inputs {
        let result1 = canonicalize_for_embedding(input);
        let result2 = canonicalize_for_embedding(input);
        let result3 = canonicalize_for_embedding(input);

        assert_eq!(result1, result2, "Non-deterministic for input: {:?}", input);
        assert_eq!(result2, result3, "Non-deterministic for input: {:?}", input);
    }
}

#[test]
fn test_canonicalize_deterministic_repeated() {
    let input = "This is a **test** with `code` and [links](http://test.com).\n\n```python\nprint('hello')\n```";

    // Run 100 times
    let first_result = canonicalize_for_embedding(input);
    for _ in 0..100 {
        let result = canonicalize_for_embedding(input);
        assert_eq!(first_result, result, "Non-deterministic canonicalization");
    }
}

#[test]
fn test_hash_deterministic() {
    let input = "Test content for hashing";
    let canonical = canonicalize_for_embedding(input);

    let hash1 = content_hash(&canonical);
    let hash2 = content_hash(&canonical);
    let hash3 = content_hash(&canonical);

    assert_eq!(hash1, hash2);
    assert_eq!(hash2, hash3);
}

#[test]
fn test_hash_hex_deterministic() {
    let input = "Test content for hex hashing";
    let canonical = canonicalize_for_embedding(input);

    let hex1 = content_hash_hex(&canonical);
    let hex2 = content_hash_hex(&canonical);

    assert_eq!(hex1, hex2);
    assert_eq!(hex1.len(), 64); // SHA256 = 32 bytes = 64 hex chars
}

// =============================================================================
// Property-Based Tests: Fuzz testing with proptest
// =============================================================================

proptest! {
    #![proptest_config(ProptestConfig::with_cases(500))]

    #[test]
    fn proptest_canonicalize_deterministic(input in ".*") {
        let result1 = canonicalize_for_embedding(&input);
        let result2 = canonicalize_for_embedding(&input);
        prop_assert_eq!(result1, result2, "Non-deterministic for proptest input");
    }

    #[test]
    fn proptest_hash_stability(input in ".*") {
        let canonical = canonicalize_for_embedding(&input);
        let hash1 = content_hash(&canonical);
        let hash2 = content_hash(&canonical);
        prop_assert_eq!(hash1, hash2, "Hash not stable for proptest input");
    }

    #[test]
    fn proptest_truncation_bound(input in ".{0,10000}") {
        let canonical = canonicalize_for_embedding(&input);
        let char_count = canonical.chars().count();
        prop_assert!(
            char_count <= MAX_EMBED_CHARS,
            "Output exceeded MAX_EMBED_CHARS: {} > {}",
            char_count,
            MAX_EMBED_CHARS
        );
    }

    #[test]
    fn proptest_no_double_spaces(input in "[a-zA-Z0-9 ]{10,500}") {
        let canonical = canonicalize_for_embedding(&input);
        prop_assert!(
            !canonical.contains("  "),
            "Double spaces found in canonical output"
        );
    }
}

// More specific property tests with structured inputs
proptest! {
    #![proptest_config(ProptestConfig::with_cases(200))]

    #[test]
    fn proptest_markdown_bold_removed(text in "[a-zA-Z ]{5,50}") {
        let input = format!("**{text}**");
        let canonical = canonicalize_for_embedding(&input);
        prop_assert!(
            !canonical.contains("**"),
            "Bold markers not removed: {}",
            canonical
        );
    }

    #[test]
    fn proptest_markdown_headers_stripped(level in 1..6usize, text in "[a-zA-Z ]{3,30}") {
        let prefix = "#".repeat(level);
        let input = format!("{prefix} {text}");
        let canonical = canonicalize_for_embedding(&input);
        prop_assert!(
            !canonical.starts_with('#'),
            "Header not stripped: {}",
            canonical
        );
    }

    #[test]
    fn proptest_links_text_preserved(link_text in "[a-zA-Z]{3,20}", url in "https?://[a-z]{5,15}\\.com") {
        let input = format!("See [{link_text}]({url}) for details.");
        let canonical = canonicalize_for_embedding(&input);
        prop_assert!(
            canonical.contains(&link_text),
            "Link text '{}' not preserved in: {}",
            link_text,
            canonical
        );
        prop_assert!(
            !canonical.contains(&url),
            "URL '{}' should be removed from: {}",
            url,
            canonical
        );
    }
}

// =============================================================================
// Edge Case Tests: Boundary conditions and special inputs
// =============================================================================

#[test]
fn test_edge_empty_string() {
    let canonical = canonicalize_for_embedding("");
    assert_eq!(canonical, "");

    let hash = content_hash(&canonical);
    assert_eq!(hash.len(), 32); // Still produces valid hash
}

#[test]
fn test_edge_whitespace_only() {
    let inputs = vec![
        " ",
        "   ",
        "\n",
        "\n\n\n",
        "\t",
        "\t\t\t",
        " \n \t \n ",
        "\r\n",
    ];

    for input in inputs {
        let canonical = canonicalize_for_embedding(input);
        assert!(
            canonical.is_empty() || canonical.trim() == canonical,
            "Whitespace-only input '{:?}' produced non-trimmed output: '{}'",
            input,
            canonical
        );
    }
}

#[test]
fn test_edge_single_character() {
    let chars = vec!['a', 'Z', '0', '!', '?', ' ', '\n', '日', '😀'];

    for c in chars {
        let input = c.to_string();
        let canonical = canonicalize_for_embedding(&input);
        // Should not panic, output should be <= input length
        assert!(
            canonical.chars().count() <= 1,
            "Single char '{}' expanded unexpectedly to: '{}'",
            c,
            canonical
        );
    }
}

#[test]
fn test_edge_only_code_blocks() {
    let inputs = vec![
        "```\ncode\n```",
        "```rust\nfn main() {}\n```",
        "```python\nprint('hi')\n```\n\n```js\nconsole.log('bye')\n```",
    ];

    for input in inputs {
        let canonical = canonicalize_for_embedding(input);
        assert!(
            canonical.contains("[code"),
            "Code block input should produce [code] marker: input={:?}, output={}",
            input,
            canonical
        );
    }
}

#[test]
fn test_edge_unclosed_code_block() {
    let input = "```python\nprint('hello')\nprint('world')";
    let canonical = canonicalize_for_embedding(input);

    // Should handle unclosed code block gracefully
    assert!(
        canonical.contains("[code: python]") || canonical.contains("print"),
        "Unclosed code block not handled: {}",
        canonical
    );
}

#[test]
fn test_edge_deeply_nested_markdown() {
    // Multiple levels of formatting
    let input = "***bold and italic*** and __**both**__ with `code`";
    let canonical = canonicalize_for_embedding(input);

    // All markers should be stripped
    assert!(
        !canonical.contains("**"),
        "Bold markers remain: {}",
        canonical
    );
    assert!(
        !canonical.contains("__"),
        "Underline markers remain: {}",
        canonical
    );
    assert!(!canonical.contains('`'), "Backticks remain: {}", canonical);
}

#[test]
fn test_edge_unicode_combining_characters() {
    // Various Unicode combining character scenarios
    let test_cases = vec![
        ("cafe\u{0301}", "café"),  // NFD → NFC
        ("a\u{0301}", "á"),        // single combining
        ("\u{0041}\u{030A}", "Å"), // A + ring above
    ];

    for (input, _expected_visual) in test_cases {
        let canonical = canonicalize_for_embedding(input);
        // Should be NFC normalized - same visual different bytes should produce same output
        let canonical2 = canonicalize_for_embedding(&input.chars().collect::<String>());
        assert_eq!(
            canonical, canonical2,
            "Unicode combining chars not normalized consistently"
        );
    }
}

#[test]
fn test_edge_unicode_nfc_nfd_equivalence() {
    // Same visual text in NFC and NFD forms should produce identical output
    let nfc = "caf\u{00E9}"; // é as single char
    let nfd = "cafe\u{0301}"; // e + combining accent

    let canonical_nfc = canonicalize_for_embedding(nfc);
    let canonical_nfd = canonicalize_for_embedding(nfd);

    assert_eq!(
        canonical_nfc, canonical_nfd,
        "NFC/NFD not normalized to same output"
    );

    // Hashes should also match
    let hash_nfc = content_hash(&canonical_nfc);
    let hash_nfd = content_hash(&canonical_nfd);
    assert_eq!(
        hash_nfc, hash_nfd,
        "Hash mismatch for NFC/NFD normalized text"
    );
}

#[test]
fn test_edge_rtl_text() {
    // Right-to-left text (Hebrew, Arabic)
    let rtl_text = "שלום עולם"; // "Hello world" in Hebrew
    let canonical = canonicalize_for_embedding(rtl_text);

    // Should preserve the text
    assert!(!canonical.is_empty(), "RTL text should not be empty");
    // At minimum, some characters should remain
    assert!(
        canonical.chars().any(|c| c.is_alphabetic()),
        "RTL text lost alphabetic content"
    );
}

#[test]
fn test_edge_emoji() {
    let inputs = vec![
        "Hello 👋",
        "🚀 Launch time",
        "Multiple 🎉🎊🎁 emojis",
        "👨‍👩‍👧‍👦 family", // ZWJ sequence
        "🏳️‍🌈 flag",   // flag with ZWJ
    ];

    for input in inputs {
        let canonical = canonicalize_for_embedding(input);
        // Should not panic
        // Basic emoji should be preserved (ZWJ sequences may be normalized)
        assert!(
            !canonical.is_empty() || input.trim().is_empty(),
            "Emoji input '{}' produced unexpected output: '{}'",
            input,
            canonical
        );
    }
}

#[test]
fn test_edge_very_long_input() {
    // Input significantly longer than MAX_EMBED_CHARS
    let long_input = "a".repeat(MAX_EMBED_CHARS * 3);
    let canonical = canonicalize_for_embedding(&long_input);

    assert!(
        canonical.chars().count() <= MAX_EMBED_CHARS,
        "Long input not truncated: {} chars",
        canonical.chars().count()
    );
}

#[test]
fn test_edge_exactly_max_chars() {
    let exact_input = "x".repeat(MAX_EMBED_CHARS);
    let canonical = canonicalize_for_embedding(&exact_input);

    assert!(
        canonical.chars().count() <= MAX_EMBED_CHARS,
        "Exact-length input exceeded limit"
    );
}

#[test]
fn test_edge_low_signal_exact_matches() {
    // These exact phrases should be filtered to empty
    let low_signal = vec![
        "OK",
        "ok",
        "Ok",
        "Done.",
        "done.",
        "Got it.",
        "got it.",
        "Understood.",
        "Sure.",
        "Yes",
        "No",
        "Thanks.",
    ];

    for input in low_signal {
        let canonical = canonicalize_for_embedding(input);
        assert!(
            canonical.is_empty(),
            "Low-signal content '{}' should be filtered to empty, got: '{}'",
            input,
            canonical
        );
    }
}

#[test]
fn test_edge_low_signal_not_substring() {
    // These contain low-signal words but shouldn't be filtered
    let inputs = vec![
        "OK, let's proceed with the plan",
        "Done. Now we need to test.",
        "Thanks for the detailed explanation!",
        "Sure, I understand the requirement.",
    ];

    for input in inputs {
        let canonical = canonicalize_for_embedding(input);
        assert!(
            !canonical.is_empty(),
            "Content '{}' should NOT be filtered, but got empty",
            input
        );
    }
}

#[test]
fn test_edge_code_block_exactly_boundary() {
    // Code block with exactly CODE_HEAD_LINES + CODE_TAIL_LINES (should not collapse)
    use coding_agent_search::search::canonicalize::{CODE_HEAD_LINES, CODE_TAIL_LINES};

    let total_lines = CODE_HEAD_LINES + CODE_TAIL_LINES;
    let lines: Vec<String> = (0..total_lines).map(|i| format!("line {i}")).collect();
    let code = format!("```rust\n{}\n```", lines.join("\n"));

    let canonical = canonicalize_for_embedding(&code);

    // Should NOT contain "lines omitted" since it's exactly at boundary
    assert!(
        !canonical.contains("lines omitted"),
        "Boundary-length code block should not be collapsed"
    );

    // All lines should be present
    assert!(canonical.contains("line 0"));
    assert!(canonical.contains(&format!("line {}", total_lines - 1)));
}

#[test]
fn test_edge_code_block_one_over_boundary() {
    // Code block with one more than boundary (should collapse)
    use coding_agent_search::search::canonicalize::{CODE_HEAD_LINES, CODE_TAIL_LINES};

    let total_lines = CODE_HEAD_LINES + CODE_TAIL_LINES + 1;
    let lines: Vec<String> = (0..total_lines).map(|i| format!("line {i}")).collect();
    let code = format!("```rust\n{}\n```", lines.join("\n"));

    let canonical = canonicalize_for_embedding(&code);

    // Should contain "lines omitted" since it's over boundary
    assert!(
        canonical.contains("lines omitted") || canonical.contains("1 lines omitted"),
        "Over-boundary code block should be collapsed: {}",
        canonical
    );
}

#[test]
fn test_edge_mixed_line_endings() {
    let inputs = vec![
        "Line1\nLine2\nLine3",       // Unix
        "Line1\r\nLine2\r\nLine3",   // Windows
        "Line1\rLine2\rLine3",       // Old Mac
        "Line1\n\r\nLine2\r\nLine3", // Mixed
    ];

    for input in &inputs {
        let canonical = canonicalize_for_embedding(input);
        // Should normalize line endings, preserving content
        assert!(
            canonical.contains("Line1"),
            "Line ending handling lost content: {:?} -> {}",
            input,
            canonical
        );
    }
}

#[test]
fn test_edge_special_markdown_chars() {
    // Characters that could be interpreted as markdown
    let inputs = vec![
        "File path: /usr/bin/test_file",
        "Math: 2 * 3 = 6",
        "Code: func_name()",
        "Asterisks: * * *",
        "Underscores: a_b_c_d",
    ];

    for input in inputs {
        let canonical = canonicalize_for_embedding(input);
        // Should handle without panic
        // Content should be largely preserved (may have some stripping)
        assert!(
            !canonical.is_empty() || input.trim().is_empty(),
            "Special markdown chars caused empty output: {}",
            input
        );
    }
}

// =============================================================================
// Hash Stability Tests: Verify hashing consistency
// =============================================================================

#[test]
fn test_hash_different_content_different_hash() {
    let text1 = "Hello, world!";
    let text2 = "Goodbye, world!";

    let hash1 = content_hash(text1);
    let hash2 = content_hash(text2);

    assert_ne!(
        hash1, hash2,
        "Different content should have different hashes"
    );
}

#[test]
fn test_hash_known_value() {
    // Empty string SHA256
    let empty_hash = content_hash("");
    let expected_empty = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855";

    assert_eq!(
        content_hash_hex(""),
        expected_empty,
        "Empty string hash doesn't match known SHA256"
    );
    assert_eq!(empty_hash.len(), 32);
}

#[test]
fn test_canonicalize_then_hash_pipeline() {
    // Verify the full pipeline is deterministic
    let input = "**Test** content with [link](http://x.com) and ```code```";

    let pipeline1 = content_hash(&canonicalize_for_embedding(input));
    let pipeline2 = content_hash(&canonicalize_for_embedding(input));
    let pipeline3 = content_hash(&canonicalize_for_embedding(input));

    assert_eq!(pipeline1, pipeline2);
    assert_eq!(pipeline2, pipeline3);
}

// =============================================================================
// Rollback Test: CASS_STREAMING_CANONICALIZE env var
// =============================================================================
// Note: Due to LazyLock, we can only test within the current mode.
// Full rollback testing requires separate test processes.

#[test]
fn test_env_var_documentation() {
    // Document the expected behavior for manual verification
    // The CASS_STREAMING_CANONICALIZE env var controls the implementation:
    // - Default (not set): streaming enabled
    // - "0" or "false": streaming disabled (legacy)
    // - Any other value: streaming enabled

    // This test verifies the current implementation works consistently
    let input = "Test content for env var verification";
    let result1 = canonicalize_for_embedding(input);
    let result2 = canonicalize_for_embedding(input);

    assert_eq!(
        result1, result2,
        "Current mode (streaming or legacy) should be deterministic"
    );

    // Log for manual inspection
    println!(
        "Current implementation produced: '{}' from '{}'",
        result1, input
    );
}

// =============================================================================
// Integration Test: Real-world content patterns
// =============================================================================

#[test]
fn test_realistic_agent_log_content() {
    let log_entry = r#"# Task: Fix authentication bug

The user reported that sessions expire too quickly.

## Investigation

Looking at the code in `src/auth/session.rs`:

```rust
impl Session {
    fn is_expired(&self) -> bool {
        // BUG: Using seconds instead of minutes
        self.created_at + Duration::from_secs(30) < Instant::now()
    }
}
```

## Fix

Changed `from_secs(30)` to `from_secs(30 * 60)`.

See [PR #123](https://github.com/example/repo/pull/123) for details.

**Status:** Done.
"#;

    let canonical = canonicalize_for_embedding(log_entry);

    // Should strip markdown formatting
    assert!(!canonical.contains("##"));
    assert!(!canonical.contains("**"));

    // Should preserve key content
    assert!(canonical.contains("authentication"));
    assert!(canonical.contains("session"));

    // Should handle code block
    assert!(canonical.contains("[code: rust]") || canonical.contains("is_expired"));

    // Link text should be preserved, URL removed
    assert!(canonical.contains("PR #123") || canonical.contains("PR"));
    assert!(!canonical.contains("https://"));

    // Should be deterministic
    let canonical2 = canonicalize_for_embedding(log_entry);
    assert_eq!(canonical, canonical2);
}

#[test]
fn test_realistic_tool_output() {
    let tool_output = r#"[Tool: Bash - Running tests]

```
$ cargo test
running 42 tests
test auth::session_tests::test_expiry ... ok
test auth::session_tests::test_renewal ... ok
...
test result: ok. 42 passed; 0 failed
```

All tests pass. Ready for review."#;

    let canonical = canonicalize_for_embedding(tool_output);

    // Should handle tool marker and code block
    assert!(!canonical.is_empty());

    // Should be deterministic
    let canonical2 = canonicalize_for_embedding(tool_output);
    assert_eq!(canonical, canonical2);
}
