//! Golden-file serialization compatibility tests for NormalizedConversation types.
//!
//! These tests ensure that the JSON shape of connector types is preserved across
//! the FAD migration. They serve as the "before" baseline: run once before migration
//! (must pass), then again after migration (must still pass).

use coding_agent_search::connectors::{
    DetectionResult, NormalizedConversation, NormalizedMessage, NormalizedSnippet,
};
use std::path::PathBuf;

// ============================================================================
// Helpers
// ============================================================================

fn golden_path(name: &str) -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("tests/fixtures/golden")
        .join(name)
}

fn load_golden(name: &str) -> String {
    std::fs::read_to_string(golden_path(name))
        .unwrap_or_else(|e| panic!("Failed to read golden file {name}: {e}"))
}

/// Build a representative NormalizedConversation with all fields populated.
fn build_full_conversation() -> NormalizedConversation {
    NormalizedConversation {
        agent_slug: "claude_code".into(),
        external_id: Some("sess-abc-123".into()),
        title: Some("Fix authentication bug".into()),
        workspace: Some(PathBuf::from("/home/user/myproject")),
        source_path: PathBuf::from(
            "/home/user/.claude/projects/myproject/sess-abc-123.jsonl",
        ),
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
                role: "user".into(),
                author: None,
                created_at: Some(1_700_000_000_000),
                content: "Fix the authentication bug in login.rs".into(),
                extra: serde_json::json!({"tool_calls": []}),
                snippets: vec![NormalizedSnippet {
                    file_path: Some(PathBuf::from("src/login.rs")),
                    start_line: Some(42),
                    end_line: Some(55),
                    language: Some("rust".into()),
                    snippet_text: Some(
                        "fn authenticate(user: &str) -> Result<Token> {\n    // BUG: missing validation\n}"
                            .into(),
                    ),
                }],
                invocations: Vec::new(),
            },
            NormalizedMessage {
                idx: 1,
                role: "assistant".into(),
                author: Some("claude-3-opus".into()),
                created_at: Some(1_700_000_005_000),
                content: "I'll fix the authentication bug by adding input validation.".into(),
                extra: serde_json::json!({"model": "claude-3-opus"}),
                snippets: vec![],
                invocations: Vec::new(),
            },
            NormalizedMessage {
                idx: 2,
                role: "user".into(),
                author: None,
                created_at: Some(1_700_000_010_000),
                content: "Thanks, that works!".into(),
                extra: serde_json::json!({}),
                snippets: vec![],
                invocations: Vec::new(),
            },
        ],
    }
}

/// Build a minimal NormalizedConversation with all optional fields as None.
fn build_minimal_conversation() -> NormalizedConversation {
    NormalizedConversation {
        agent_slug: "chatgpt".into(),
        external_id: None,
        title: None,
        workspace: None,
        source_path: PathBuf::from("/tmp/conv.json"),
        started_at: None,
        ended_at: None,
        metadata: serde_json::json!({}),
        messages: vec![NormalizedMessage {
            idx: 0,
            role: "user".into(),
            author: None,
            created_at: None,
            content: "Hello".into(),
            extra: serde_json::json!({}),
            snippets: vec![],
            invocations: Vec::new(),
        }],
    }
}

/// Build a NormalizedMessage with rich content.
fn build_full_message() -> NormalizedMessage {
    NormalizedMessage {
        idx: 5,
        role: "assistant".into(),
        author: Some("gpt-4o".into()),
        created_at: Some(1_700_000_042_000),
        content:
            "Here's the fix for the race condition:\n\n```rust\nlet guard = mutex.lock().await;\n```"
                .into(),
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
                language: Some("rust".into()),
                snippet_text: Some(
                    "let guard = mutex.lock().await;\nprocess(&guard).await;".into(),
                ),
            },
            NormalizedSnippet {
                file_path: None,
                start_line: None,
                end_line: None,
                language: Some("python".into()),
                snippet_text: Some("import asyncio".into()),
            },
        ],
        invocations: Vec::new(),
    }
}

/// Build a NormalizedSnippet with all fields.
fn build_full_snippet() -> NormalizedSnippet {
    NormalizedSnippet {
        file_path: Some(PathBuf::from("src/handlers/auth.rs")),
        start_line: Some(100),
        end_line: Some(120),
        language: Some("rust".into()),
        snippet_text: Some(
            "pub fn verify_token(token: &str) -> Result<Claims> {\n    \
             let key = load_signing_key()?;\n    \
             decode(token, &key, &Validation::default())\n        \
             .map(|data| data.claims)\n        \
             .map_err(|e| AuthError::InvalidToken(e.to_string()))\n}"
                .into(),
        ),
    }
}

/// Build a DetectionResult.
fn build_detection_result() -> DetectionResult {
    DetectionResult {
        detected: true,
        evidence: vec![
            "Found ~/.claude directory".into(),
            "Contains 15 session files".into(),
            "Active since 2025-01-01".into(),
        ],
        root_paths: vec![
            PathBuf::from("/home/user/.claude"),
            PathBuf::from("/home/user/.claude/projects/myproject"),
        ],
    }
}

// ============================================================================
// JSON Deserialization from Golden Files
// ============================================================================

#[test]
fn deserialize_golden_conversation() {
    let json = load_golden("normalized_conversation.json");
    let conv: NormalizedConversation =
        serde_json::from_str(&json).expect("Failed to deserialize golden conversation");

    assert_eq!(conv.agent_slug, "claude_code");
    assert_eq!(conv.external_id.as_deref(), Some("sess-abc-123"));
    assert_eq!(conv.title.as_deref(), Some("Fix authentication bug"));
    assert_eq!(conv.workspace, Some(PathBuf::from("/home/user/myproject")));
    assert_eq!(conv.started_at, Some(1_700_000_000_000));
    assert_eq!(conv.ended_at, Some(1_700_000_010_000));
    assert_eq!(conv.messages.len(), 3);

    // Verify first message
    assert_eq!(conv.messages[0].idx, 0);
    assert_eq!(conv.messages[0].role, "user");
    assert!(conv.messages[0].author.is_none());
    assert_eq!(conv.messages[0].created_at, Some(1_700_000_000_000));
    assert!(conv.messages[0].content.contains("authentication bug"));

    // Verify snippet on first message
    assert_eq!(conv.messages[0].snippets.len(), 1);
    assert_eq!(
        conv.messages[0].snippets[0].file_path,
        Some(PathBuf::from("src/login.rs"))
    );
    assert_eq!(conv.messages[0].snippets[0].start_line, Some(42));
    assert_eq!(conv.messages[0].snippets[0].end_line, Some(55));
    assert_eq!(
        conv.messages[0].snippets[0].language.as_deref(),
        Some("rust")
    );

    // Verify second message (assistant with author)
    assert_eq!(conv.messages[1].role, "assistant");
    assert_eq!(conv.messages[1].author.as_deref(), Some("claude-3-opus"));

    // Verify metadata
    assert_eq!(conv.metadata["source"], "claude_code");
}

#[test]
fn deserialize_golden_conversation_minimal() {
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
    assert!(conv.messages[0].author.is_none());
    assert!(conv.messages[0].created_at.is_none());
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

    // First snippet: fully populated
    assert_eq!(
        msg.snippets[0].file_path,
        Some(PathBuf::from("src/sync.rs"))
    );
    assert_eq!(msg.snippets[0].start_line, Some(10));

    // Second snippet: nullable file_path
    assert!(msg.snippets[1].file_path.is_none());
    assert!(msg.snippets[1].start_line.is_none());
    assert_eq!(msg.snippets[1].language.as_deref(), Some("python"));
}

#[test]
fn deserialize_golden_snippet() {
    let json = load_golden("normalized_snippet.json");
    let snippet: NormalizedSnippet =
        serde_json::from_str(&json).expect("Failed to deserialize golden snippet");

    assert_eq!(
        snippet.file_path,
        Some(PathBuf::from("src/handlers/auth.rs"))
    );
    assert_eq!(snippet.start_line, Some(100));
    assert_eq!(snippet.end_line, Some(120));
    assert_eq!(snippet.language.as_deref(), Some("rust"));
    assert!(
        snippet
            .snippet_text
            .as_ref()
            .unwrap()
            .contains("verify_token")
    );
}

#[test]
fn deserialize_golden_detection_result() {
    let json = load_golden("detection_result.json");
    let result: DetectionResult =
        serde_json::from_str(&json).expect("Failed to deserialize golden detection result");

    assert!(result.detected);
    assert_eq!(result.evidence.len(), 3);
    assert!(result.evidence[0].contains("~/.claude"));
    assert_eq!(result.root_paths.len(), 2);
}

// ============================================================================
// JSON Serialization — verify output matches golden files
// ============================================================================

#[test]
fn serialize_matches_golden_conversation() {
    let conv = build_full_conversation();
    let serialized = serde_json::to_value(&conv).unwrap();
    let golden: serde_json::Value =
        serde_json::from_str(&load_golden("normalized_conversation.json")).unwrap();

    assert_eq!(
        serialized, golden,
        "Serialized conversation does not match golden file"
    );
}

#[test]
fn serialize_matches_golden_conversation_minimal() {
    let conv = build_minimal_conversation();
    let serialized = serde_json::to_value(&conv).unwrap();
    let golden: serde_json::Value =
        serde_json::from_str(&load_golden("normalized_conversation_minimal.json")).unwrap();

    assert_eq!(
        serialized, golden,
        "Serialized minimal conversation does not match golden file"
    );
}

#[test]
fn serialize_matches_golden_message() {
    let msg = build_full_message();
    let serialized = serde_json::to_value(&msg).unwrap();
    let golden: serde_json::Value =
        serde_json::from_str(&load_golden("normalized_message.json")).unwrap();

    assert_eq!(
        serialized, golden,
        "Serialized message does not match golden file"
    );
}

#[test]
fn serialize_matches_golden_snippet() {
    let snippet = build_full_snippet();
    let serialized = serde_json::to_value(&snippet).unwrap();
    let golden: serde_json::Value =
        serde_json::from_str(&load_golden("normalized_snippet.json")).unwrap();

    assert_eq!(
        serialized, golden,
        "Serialized snippet does not match golden file"
    );
}

#[test]
fn serialize_matches_golden_detection_result() {
    let result = build_detection_result();
    let serialized = serde_json::to_value(&result).unwrap();
    let golden: serde_json::Value =
        serde_json::from_str(&load_golden("detection_result.json")).unwrap();

    assert_eq!(
        serialized, golden,
        "Serialized detection result does not match golden file"
    );
}

// ============================================================================
// JSON Roundtrip Tests
// ============================================================================

#[test]
fn roundtrip_conversation_json() {
    let original = build_full_conversation();
    let json = serde_json::to_string(&original).unwrap();
    let deserialized: NormalizedConversation = serde_json::from_str(&json).unwrap();

    assert_eq!(original.agent_slug, deserialized.agent_slug);
    assert_eq!(original.external_id, deserialized.external_id);
    assert_eq!(original.title, deserialized.title);
    assert_eq!(original.workspace, deserialized.workspace);
    assert_eq!(original.source_path, deserialized.source_path);
    assert_eq!(original.started_at, deserialized.started_at);
    assert_eq!(original.ended_at, deserialized.ended_at);
    assert_eq!(original.messages.len(), deserialized.messages.len());

    for (orig, deser) in original.messages.iter().zip(deserialized.messages.iter()) {
        assert_eq!(orig.idx, deser.idx);
        assert_eq!(orig.role, deser.role);
        assert_eq!(orig.author, deser.author);
        assert_eq!(orig.created_at, deser.created_at);
        assert_eq!(orig.content, deser.content);
        assert_eq!(orig.snippets.len(), deser.snippets.len());
    }
}

#[test]
fn roundtrip_minimal_conversation_json() {
    let original = build_minimal_conversation();
    let json = serde_json::to_string(&original).unwrap();
    let deserialized: NormalizedConversation = serde_json::from_str(&json).unwrap();

    assert_eq!(original.agent_slug, deserialized.agent_slug);
    assert!(deserialized.external_id.is_none());
    assert!(deserialized.title.is_none());
    assert!(deserialized.workspace.is_none());
    assert!(deserialized.started_at.is_none());
    assert!(deserialized.ended_at.is_none());
    assert_eq!(deserialized.messages.len(), 1);
}

#[test]
fn roundtrip_message_json() {
    let original = build_full_message();
    let json = serde_json::to_string(&original).unwrap();
    let deserialized: NormalizedMessage = serde_json::from_str(&json).unwrap();

    assert_eq!(original.idx, deserialized.idx);
    assert_eq!(original.role, deserialized.role);
    assert_eq!(original.author, deserialized.author);
    assert_eq!(original.created_at, deserialized.created_at);
    assert_eq!(original.content, deserialized.content);
    assert_eq!(original.snippets.len(), deserialized.snippets.len());
}

#[test]
fn roundtrip_snippet_json() {
    let original = build_full_snippet();
    let json = serde_json::to_string(&original).unwrap();
    let deserialized: NormalizedSnippet = serde_json::from_str(&json).unwrap();

    assert_eq!(original.file_path, deserialized.file_path);
    assert_eq!(original.start_line, deserialized.start_line);
    assert_eq!(original.end_line, deserialized.end_line);
    assert_eq!(original.language, deserialized.language);
    assert_eq!(original.snippet_text, deserialized.snippet_text);
}

#[test]
fn roundtrip_detection_result_json() {
    let original = build_detection_result();
    let json = serde_json::to_string(&original).unwrap();
    let deserialized: DetectionResult = serde_json::from_str(&json).unwrap();

    assert_eq!(original.detected, deserialized.detected);
    assert_eq!(original.evidence, deserialized.evidence);
    assert_eq!(original.root_paths, deserialized.root_paths);
}

// ============================================================================
// MessagePack Roundtrip Tests
// ============================================================================

#[test]
fn roundtrip_conversation_messagepack() {
    let original = build_full_conversation();
    let packed = rmp_serde::to_vec(&original).expect("MessagePack serialize failed");
    let deserialized: NormalizedConversation =
        rmp_serde::from_slice(&packed).expect("MessagePack deserialize failed");

    assert_eq!(original.agent_slug, deserialized.agent_slug);
    assert_eq!(original.external_id, deserialized.external_id);
    assert_eq!(original.title, deserialized.title);
    assert_eq!(original.workspace, deserialized.workspace);
    assert_eq!(original.source_path, deserialized.source_path);
    assert_eq!(original.started_at, deserialized.started_at);
    assert_eq!(original.ended_at, deserialized.ended_at);
    assert_eq!(original.messages.len(), deserialized.messages.len());

    for (orig, deser) in original.messages.iter().zip(deserialized.messages.iter()) {
        assert_eq!(orig.idx, deser.idx);
        assert_eq!(orig.role, deser.role);
        assert_eq!(orig.author, deser.author);
        assert_eq!(orig.created_at, deser.created_at);
        assert_eq!(orig.content, deser.content);
        assert_eq!(orig.snippets.len(), deser.snippets.len());
    }
}

#[test]
fn roundtrip_minimal_conversation_messagepack() {
    let original = build_minimal_conversation();
    let packed = rmp_serde::to_vec(&original).expect("MessagePack serialize failed");
    let deserialized: NormalizedConversation =
        rmp_serde::from_slice(&packed).expect("MessagePack deserialize failed");

    assert_eq!(original.agent_slug, deserialized.agent_slug);
    assert!(deserialized.external_id.is_none());
    assert!(deserialized.title.is_none());
    assert!(deserialized.workspace.is_none());
}

#[test]
fn roundtrip_message_messagepack() {
    let original = build_full_message();
    let packed = rmp_serde::to_vec(&original).expect("MessagePack serialize failed");
    let deserialized: NormalizedMessage =
        rmp_serde::from_slice(&packed).expect("MessagePack deserialize failed");

    assert_eq!(original.idx, deserialized.idx);
    assert_eq!(original.role, deserialized.role);
    assert_eq!(original.author, deserialized.author);
    assert_eq!(original.content, deserialized.content);
}

#[test]
fn roundtrip_snippet_messagepack() {
    let original = build_full_snippet();
    let packed = rmp_serde::to_vec(&original).expect("MessagePack serialize failed");
    let deserialized: NormalizedSnippet =
        rmp_serde::from_slice(&packed).expect("MessagePack deserialize failed");

    assert_eq!(original.file_path, deserialized.file_path);
    assert_eq!(original.start_line, deserialized.start_line);
    assert_eq!(original.end_line, deserialized.end_line);
    assert_eq!(original.language, deserialized.language);
    assert_eq!(original.snippet_text, deserialized.snippet_text);
}

// ============================================================================
// Cross-format: JSON -> MessagePack -> JSON (verify no data loss)
// ============================================================================

#[test]
fn cross_format_json_to_msgpack_to_json() {
    let original = build_full_conversation();

    // JSON -> struct
    let json = serde_json::to_string(&original).unwrap();
    let from_json: NormalizedConversation = serde_json::from_str(&json).unwrap();

    // struct -> MessagePack -> struct
    let packed = rmp_serde::to_vec(&from_json).unwrap();
    let from_msgpack: NormalizedConversation = rmp_serde::from_slice(&packed).unwrap();

    // struct -> JSON again
    let json_again = serde_json::to_string(&from_msgpack).unwrap();
    let final_conv: NormalizedConversation = serde_json::from_str(&json_again).unwrap();

    // Compare first and last
    assert_eq!(original.agent_slug, final_conv.agent_slug);
    assert_eq!(original.external_id, final_conv.external_id);
    assert_eq!(original.title, final_conv.title);
    assert_eq!(original.workspace, final_conv.workspace);
    assert_eq!(original.source_path, final_conv.source_path);
    assert_eq!(original.started_at, final_conv.started_at);
    assert_eq!(original.ended_at, final_conv.ended_at);
    assert_eq!(original.messages.len(), final_conv.messages.len());

    for (orig, final_msg) in original.messages.iter().zip(final_conv.messages.iter()) {
        assert_eq!(orig.idx, final_msg.idx);
        assert_eq!(orig.role, final_msg.role);
        assert_eq!(orig.author, final_msg.author);
        assert_eq!(orig.created_at, final_msg.created_at);
        assert_eq!(orig.content, final_msg.content);
        assert_eq!(orig.snippets.len(), final_msg.snippets.len());
    }
}

// ============================================================================
// Field presence/ordering — ensure all fields are in expected JSON shape
// ============================================================================

#[test]
fn conversation_json_has_expected_top_level_fields() {
    let conv = build_full_conversation();
    let val = serde_json::to_value(&conv).unwrap();
    let obj = val.as_object().unwrap();

    let expected_fields = [
        "agent_slug",
        "external_id",
        "title",
        "workspace",
        "source_path",
        "started_at",
        "ended_at",
        "metadata",
        "messages",
    ];

    for field in &expected_fields {
        assert!(obj.contains_key(*field), "Missing expected field: {field}");
    }

    // No unexpected fields
    assert_eq!(
        obj.len(),
        expected_fields.len(),
        "Unexpected field count. Fields: {:?}",
        obj.keys().collect::<Vec<_>>()
    );
}

#[test]
fn message_json_has_expected_fields() {
    let msg = build_full_message();
    let val = serde_json::to_value(&msg).unwrap();
    let obj = val.as_object().unwrap();

    let expected_fields = [
        "idx",
        "role",
        "author",
        "created_at",
        "content",
        "extra",
        "snippets",
    ];

    for field in &expected_fields {
        assert!(obj.contains_key(*field), "Missing expected field: {field}");
    }

    assert_eq!(
        obj.len(),
        expected_fields.len(),
        "Unexpected field count. Fields: {:?}",
        obj.keys().collect::<Vec<_>>()
    );
}

#[test]
fn snippet_json_has_expected_fields() {
    let snippet = build_full_snippet();
    let val = serde_json::to_value(&snippet).unwrap();
    let obj = val.as_object().unwrap();

    let expected_fields = [
        "file_path",
        "start_line",
        "end_line",
        "language",
        "snippet_text",
    ];

    for field in &expected_fields {
        assert!(obj.contains_key(*field), "Missing expected field: {field}");
    }

    assert_eq!(
        obj.len(),
        expected_fields.len(),
        "Unexpected field count. Fields: {:?}",
        obj.keys().collect::<Vec<_>>()
    );
}

// ============================================================================
// Backwards compatibility — old data still deserializable
// ============================================================================

#[test]
fn backwards_compat_extra_fields_ignored() {
    // Simulate old JSON with an extra field that no longer exists in the struct
    let json = r#"{
        "agent_slug": "test",
        "external_id": null,
        "title": null,
        "workspace": null,
        "source_path": "/tmp/test",
        "started_at": null,
        "ended_at": null,
        "metadata": {},
        "messages": [],
        "legacy_field_that_no_longer_exists": "should be ignored"
    }"#;

    // This should NOT fail — serde by default ignores unknown fields
    let conv: Result<NormalizedConversation, _> = serde_json::from_str(json);
    assert!(
        conv.is_ok(),
        "Deserialization should tolerate extra fields: {:?}",
        conv.err()
    );
    assert_eq!(conv.unwrap().agent_slug, "test");
}

#[test]
fn backwards_compat_null_optionals() {
    // All Optional fields explicitly null
    let json = r#"{
        "agent_slug": "test",
        "external_id": null,
        "title": null,
        "workspace": null,
        "source_path": "/tmp/test",
        "started_at": null,
        "ended_at": null,
        "metadata": null,
        "messages": []
    }"#;

    let conv: NormalizedConversation = serde_json::from_str(json).unwrap();
    assert!(conv.external_id.is_none());
    assert!(conv.title.is_none());
    assert!(conv.workspace.is_none());
    assert!(conv.started_at.is_none());
    assert!(conv.ended_at.is_none());
}
