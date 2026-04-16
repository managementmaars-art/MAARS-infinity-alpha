//! Golden-file serialization compatibility tests for NormalizedConversation types.
//!
//! These tests ensure the JSON shape of NormalizedConversation, NormalizedMessage,
//! and NormalizedSnippet is preserved exactly. This is critical for:
//! - SQLite storage (serde_json::to_string and rmp_serde)
//! - Robot mode JSON output
//! - Daemon protocol messages
//! - HTML export data
//!
//! Run BEFORE and AFTER migrating types to FAD to prove compatibility.

use coding_agent_search::connectors::{
    NormalizedConversation, NormalizedMessage, NormalizedSnippet,
};
use std::path::PathBuf;

/// Load a golden fixture file from tests/fixtures/golden/
fn load_golden(name: &str) -> String {
    let path = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("tests/fixtures/golden")
        .join(name);
    std::fs::read_to_string(&path)
        .unwrap_or_else(|e| panic!("Failed to load golden file {}: {e}", path.display()))
}

/// Build a known NormalizedSnippet for testing.
fn make_test_snippet() -> NormalizedSnippet {
    NormalizedSnippet {
        file_path: Some(PathBuf::from("src/handlers/auth.rs")),
        start_line: Some(100),
        end_line: Some(120),
        language: Some("rust".to_string()),
        snippet_text: Some(
            "pub fn verify_token(token: &str) -> Result<Claims> {\n    \
             let key = load_signing_key()?;\n    \
             decode(token, &key, &Validation::default())\n        \
             .map(|data| data.claims)\n        \
             .map_err(|e| AuthError::InvalidToken(e.to_string()))\n}"
                .to_string(),
        ),
    }
}

/// Build a known NormalizedMessage for testing.
fn make_test_message() -> NormalizedMessage {
    NormalizedMessage {
        idx: 5,
        role: "assistant".to_string(),
        author: Some("gpt-4o".to_string()),
        created_at: Some(1_700_000_042_000),
        content: "Here's the fix for the race condition:\n\n```rust\nlet guard = mutex.lock().await;\n```".to_string(),
        extra: serde_json::json!({
            "model": "gpt-4o",
            "tool_use": true,
            "tokens_used": 150
        }),
        snippets: vec![
            NormalizedSnippet {
                file_path: Some(PathBuf::from("src/sync.rs")),
                start_line: Some(10),
                end_line: Some(15),
                language: Some("rust".to_string()),
                snippet_text: Some("let guard = mutex.lock().await;\nprocess(&guard).await;".to_string()),
            },
            NormalizedSnippet {
                file_path: None,
                start_line: None,
                end_line: None,
                language: Some("python".to_string()),
                snippet_text: Some("import asyncio".to_string()),
            },
        ],
        invocations: Vec::new(),
    }
}

/// Build a known NormalizedConversation for testing.
fn make_test_conversation() -> NormalizedConversation {
    NormalizedConversation {
        agent_slug: "claude_code".to_string(),
        external_id: Some("sess-abc-123".to_string()),
        title: Some("Fix authentication bug".to_string()),
        workspace: Some(PathBuf::from("/home/user/myproject")),
        source_path: PathBuf::from("/home/user/.claude/projects/myproject/sess-abc-123.jsonl"),
        started_at: Some(1_700_000_000_000),
        ended_at: Some(1_700_000_010_000),
        metadata: serde_json::json!({
            "source": "claude_code",
            "model": "claude-3-opus",
            "session_id": "sess-abc-123"
        }),
        messages: vec![
            NormalizedMessage {
                idx: 0,
                role: "user".to_string(),
                author: None,
                created_at: Some(1_700_000_000_000),
                content: "Fix the authentication bug in login.rs".to_string(),
                extra: serde_json::json!({"tool_calls": []}),
                snippets: vec![NormalizedSnippet {
                    file_path: Some(PathBuf::from("src/login.rs")),
                    start_line: Some(42),
                    end_line: Some(55),
                    language: Some("rust".to_string()),
                    snippet_text: Some(
                        "fn authenticate(user: &str) -> Result<Token> {\n    // BUG: missing validation\n}"
                            .to_string(),
                    ),
                }],
                invocations: Vec::new(),
            },
            NormalizedMessage {
                idx: 1,
                role: "assistant".to_string(),
                author: Some("claude-3-opus".to_string()),
                created_at: Some(1_700_000_005_000),
                content: "I'll fix the authentication bug by adding input validation.".to_string(),
                extra: serde_json::json!({"model": "claude-3-opus"}),
                snippets: vec![],
                invocations: Vec::new(),
            },
            NormalizedMessage {
                idx: 2,
                role: "user".to_string(),
                author: None,
                created_at: Some(1_700_000_010_000),
                content: "Thanks, that works!".to_string(),
                extra: serde_json::json!({}),
                snippets: vec![],
                invocations: Vec::new(),
            },
        ],
    }
}

/// Build a minimal conversation with all optional fields set to None.
fn make_minimal_conversation() -> NormalizedConversation {
    NormalizedConversation {
        agent_slug: "chatgpt".to_string(),
        external_id: None,
        title: None,
        workspace: None,
        source_path: PathBuf::from("/tmp/conv.json"),
        started_at: None,
        ended_at: None,
        metadata: serde_json::json!({}),
        messages: vec![NormalizedMessage {
            idx: 0,
            role: "user".to_string(),
            author: None,
            created_at: None,
            content: "Hello".to_string(),
            extra: serde_json::json!({}),
            snippets: vec![],
            invocations: Vec::new(),
        }],
    }
}

// ─── Golden file deserialization ─────────────────────────────────────────

#[test]
fn deserialize_golden_conversation() {
    let json = load_golden("normalized_conversation.json");
    let conv: NormalizedConversation =
        serde_json::from_str(&json).expect("Failed to deserialize golden conversation");

    assert_eq!(conv.agent_slug, "claude_code");
    assert_eq!(conv.external_id.as_deref(), Some("sess-abc-123"));
    assert_eq!(conv.title.as_deref(), Some("Fix authentication bug"));
    assert_eq!(
        conv.workspace.as_ref().map(|p| p.to_str().unwrap()),
        Some("/home/user/myproject")
    );
    assert_eq!(conv.started_at, Some(1_700_000_000_000));
    assert_eq!(conv.ended_at, Some(1_700_000_010_000));
    assert_eq!(conv.messages.len(), 3);

    // Verify first message has a snippet
    assert_eq!(conv.messages[0].role, "user");
    assert_eq!(conv.messages[0].snippets.len(), 1);
    assert_eq!(
        conv.messages[0].snippets[0]
            .file_path
            .as_ref()
            .map(|p| p.to_str().unwrap()),
        Some("src/login.rs")
    );
}

#[test]
fn deserialize_golden_message() {
    let json = load_golden("normalized_message.json");
    let msg: NormalizedMessage =
        serde_json::from_str(&json).expect("Failed to deserialize golden message");

    assert_eq!(msg.idx, 5);
    assert_eq!(msg.role, "assistant");
    assert_eq!(msg.author.as_deref(), Some("gpt-4o"));
    assert_eq!(msg.created_at, Some(1_700_000_042_000));
    assert!(msg.content.contains("race condition"));
    assert_eq!(msg.snippets.len(), 2);

    // Second snippet has null file_path and line numbers
    assert!(msg.snippets[1].file_path.is_none());
    assert!(msg.snippets[1].start_line.is_none());
    assert_eq!(msg.snippets[1].language.as_deref(), Some("python"));
}

#[test]
fn deserialize_golden_snippet() {
    let json = load_golden("normalized_snippet.json");
    let snip: NormalizedSnippet =
        serde_json::from_str(&json).expect("Failed to deserialize golden snippet");

    assert_eq!(
        snip.file_path.as_ref().map(|p| p.to_str().unwrap()),
        Some("src/handlers/auth.rs")
    );
    assert_eq!(snip.start_line, Some(100));
    assert_eq!(snip.end_line, Some(120));
    assert_eq!(snip.language.as_deref(), Some("rust"));
    assert!(snip.snippet_text.as_ref().unwrap().contains("verify_token"));
}

#[test]
fn deserialize_golden_minimal_conversation() {
    let json = load_golden("normalized_conversation_minimal.json");
    let conv: NormalizedConversation =
        serde_json::from_str(&json).expect("Failed to deserialize minimal golden conversation");

    assert_eq!(conv.agent_slug, "chatgpt");
    assert!(conv.external_id.is_none());
    assert!(conv.title.is_none());
    assert!(conv.workspace.is_none());
    assert!(conv.started_at.is_none());
    assert!(conv.ended_at.is_none());
    assert_eq!(conv.messages.len(), 1);
    assert_eq!(conv.messages[0].content, "Hello");
}

// ─── Serialize → golden comparison ──────────────────────────────────────

#[test]
fn serialize_matches_golden_conversation() {
    let conv = make_test_conversation();
    let serialized = serde_json::to_value(&conv).expect("Failed to serialize conversation");
    let golden_json = load_golden("normalized_conversation.json");
    let golden: serde_json::Value =
        serde_json::from_str(&golden_json).expect("Failed to parse golden JSON");
    assert_eq!(
        serialized, golden,
        "Serialized conversation does not match golden file"
    );
}

#[test]
fn serialize_matches_golden_message() {
    let msg = make_test_message();
    let serialized = serde_json::to_value(&msg).expect("Failed to serialize message");
    let golden_json = load_golden("normalized_message.json");
    let golden: serde_json::Value =
        serde_json::from_str(&golden_json).expect("Failed to parse golden JSON");
    assert_eq!(
        serialized, golden,
        "Serialized message does not match golden file"
    );
}

#[test]
fn serialize_matches_golden_snippet() {
    let snip = make_test_snippet();
    let serialized = serde_json::to_value(&snip).expect("Failed to serialize snippet");
    let golden_json = load_golden("normalized_snippet.json");
    let golden: serde_json::Value =
        serde_json::from_str(&golden_json).expect("Failed to parse golden JSON");
    assert_eq!(
        serialized, golden,
        "Serialized snippet does not match golden file"
    );
}

#[test]
fn serialize_matches_golden_minimal() {
    let conv = make_minimal_conversation();
    let serialized = serde_json::to_value(&conv).expect("Failed to serialize minimal conversation");
    let golden_json = load_golden("normalized_conversation_minimal.json");
    let golden: serde_json::Value =
        serde_json::from_str(&golden_json).expect("Failed to parse golden JSON");
    assert_eq!(
        serialized, golden,
        "Serialized minimal conversation does not match golden file"
    );
}

// ─── JSON roundtrip ─────────────────────────────────────────────────────

#[test]
fn json_roundtrip_conversation() {
    let original = make_test_conversation();
    let json = serde_json::to_string(&original).expect("serialize");
    let restored: NormalizedConversation = serde_json::from_str(&json).expect("deserialize");

    assert_eq!(original.agent_slug, restored.agent_slug);
    assert_eq!(original.external_id, restored.external_id);
    assert_eq!(original.title, restored.title);
    assert_eq!(original.workspace, restored.workspace);
    assert_eq!(original.source_path, restored.source_path);
    assert_eq!(original.started_at, restored.started_at);
    assert_eq!(original.ended_at, restored.ended_at);
    assert_eq!(original.metadata, restored.metadata);
    assert_eq!(original.messages.len(), restored.messages.len());
    for (orig, rest) in original.messages.iter().zip(restored.messages.iter()) {
        assert_eq!(orig.idx, rest.idx);
        assert_eq!(orig.role, rest.role);
        assert_eq!(orig.author, rest.author);
        assert_eq!(orig.created_at, rest.created_at);
        assert_eq!(orig.content, rest.content);
        assert_eq!(orig.extra, rest.extra);
        assert_eq!(orig.snippets.len(), rest.snippets.len());
    }
}

#[test]
fn json_roundtrip_message() {
    let original = make_test_message();
    let json = serde_json::to_string(&original).expect("serialize");
    let restored: NormalizedMessage = serde_json::from_str(&json).expect("deserialize");

    assert_eq!(original.idx, restored.idx);
    assert_eq!(original.role, restored.role);
    assert_eq!(original.author, restored.author);
    assert_eq!(original.created_at, restored.created_at);
    assert_eq!(original.content, restored.content);
    assert_eq!(original.extra, restored.extra);
    assert_eq!(original.snippets.len(), restored.snippets.len());
}

#[test]
fn json_roundtrip_snippet() {
    let original = make_test_snippet();
    let json = serde_json::to_string(&original).expect("serialize");
    let restored: NormalizedSnippet = serde_json::from_str(&json).expect("deserialize");

    assert_eq!(original.file_path, restored.file_path);
    assert_eq!(original.start_line, restored.start_line);
    assert_eq!(original.end_line, restored.end_line);
    assert_eq!(original.language, restored.language);
    assert_eq!(original.snippet_text, restored.snippet_text);
}

// ─── MessagePack roundtrip ──────────────────────────────────────────────

#[test]
fn messagepack_roundtrip_conversation() {
    let original = make_test_conversation();
    let bytes = rmp_serde::to_vec(&original).expect("msgpack serialize");
    let restored: NormalizedConversation =
        rmp_serde::from_slice(&bytes).expect("msgpack deserialize");

    assert_eq!(original.agent_slug, restored.agent_slug);
    assert_eq!(original.external_id, restored.external_id);
    assert_eq!(original.title, restored.title);
    assert_eq!(original.source_path, restored.source_path);
    assert_eq!(original.started_at, restored.started_at);
    assert_eq!(original.messages.len(), restored.messages.len());
}

#[test]
fn messagepack_roundtrip_message() {
    let original = make_test_message();
    let bytes = rmp_serde::to_vec(&original).expect("msgpack serialize");
    let restored: NormalizedMessage = rmp_serde::from_slice(&bytes).expect("msgpack deserialize");

    assert_eq!(original.idx, restored.idx);
    assert_eq!(original.role, restored.role);
    assert_eq!(original.author, restored.author);
    assert_eq!(original.content, restored.content);
}

#[test]
fn messagepack_roundtrip_snippet() {
    let original = make_test_snippet();
    let bytes = rmp_serde::to_vec(&original).expect("msgpack serialize");
    let restored: NormalizedSnippet = rmp_serde::from_slice(&bytes).expect("msgpack deserialize");

    assert_eq!(original.file_path, restored.file_path);
    assert_eq!(original.start_line, restored.start_line);
    assert_eq!(original.language, restored.language);
    assert_eq!(original.snippet_text, restored.snippet_text);
}

// ─── Cross-format compatibility ─────────────────────────────────────────

#[test]
fn json_to_msgpack_to_json_conversation() {
    let original = make_test_conversation();

    // JSON -> struct -> MessagePack -> struct -> JSON -> compare
    let json1 = serde_json::to_value(&original).expect("json serialize 1");
    let bytes = rmp_serde::to_vec(&original).expect("msgpack serialize");
    let from_msgpack: NormalizedConversation =
        rmp_serde::from_slice(&bytes).expect("msgpack deserialize");
    let json2 = serde_json::to_value(&from_msgpack).expect("json serialize 2");

    assert_eq!(
        json1, json2,
        "Cross-format roundtrip should preserve JSON shape"
    );
}

// ─── Role variants ──────────────────────────────────────────────────────

#[test]
fn all_role_variants_roundtrip() {
    let roles = ["user", "assistant", "tool", "system", "other", "developer"];
    for role_str in &roles {
        let msg = NormalizedMessage {
            idx: 0,
            role: role_str.to_string(),
            author: None,
            created_at: None,
            content: format!("Test message with role {role_str}"),
            extra: serde_json::json!({}),
            snippets: vec![],
            invocations: Vec::new(),
        };
        let json = serde_json::to_string(&msg).expect("serialize");
        let restored: NormalizedMessage = serde_json::from_str(&json).expect("deserialize");
        assert_eq!(restored.role, *role_str);
    }
}

// ─── Edge cases ─────────────────────────────────────────────────────────

#[test]
fn empty_messages_roundtrip() {
    let conv = NormalizedConversation {
        agent_slug: "test".to_string(),
        external_id: None,
        title: None,
        workspace: None,
        source_path: PathBuf::from("/tmp/test.jsonl"),
        started_at: None,
        ended_at: None,
        metadata: serde_json::json!(null),
        messages: vec![],
    };
    let json = serde_json::to_string(&conv).expect("serialize");
    let restored: NormalizedConversation = serde_json::from_str(&json).expect("deserialize");
    assert!(restored.messages.is_empty());
    assert_eq!(restored.metadata, serde_json::json!(null));
}

#[test]
fn unicode_content_roundtrip() {
    let msg = NormalizedMessage {
        idx: 0,
        role: "user".to_string(),
        author: Some("用户".to_string()),
        created_at: None,
        content: "こんにちは世界 🌍 café naïve résumé".to_string(),
        extra: serde_json::json!({"emoji": "🦀"}),
        snippets: vec![NormalizedSnippet {
            file_path: Some(PathBuf::from("src/données.rs")),
            start_line: None,
            end_line: None,
            language: None,
            snippet_text: Some("let π = 3.14159;".to_string()),
        }],
        invocations: Vec::new(),
    };
    let json = serde_json::to_string(&msg).expect("serialize");
    let restored: NormalizedMessage = serde_json::from_str(&json).expect("deserialize");
    assert_eq!(restored.content, msg.content);
    assert_eq!(restored.author.as_deref(), Some("用户"));
    assert_eq!(
        restored.snippets[0].snippet_text.as_deref(),
        Some("let π = 3.14159;")
    );
}

#[test]
fn large_idx_roundtrip() {
    let msg = NormalizedMessage {
        idx: i64::MAX,
        role: "user".to_string(),
        author: None,
        created_at: Some(i64::MAX),
        content: "boundary test".to_string(),
        extra: serde_json::json!({}),
        snippets: vec![],
        invocations: Vec::new(),
    };
    let json = serde_json::to_string(&msg).expect("serialize");
    let restored: NormalizedMessage = serde_json::from_str(&json).expect("deserialize");
    assert_eq!(restored.idx, i64::MAX);
    assert_eq!(restored.created_at, Some(i64::MAX));
}
