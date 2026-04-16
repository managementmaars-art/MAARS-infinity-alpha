use coding_agent_search::connectors::copilot::CopilotConnector;
use coding_agent_search::connectors::{Connector, ScanContext, ScanRoot};
use std::fs;
use std::path::Path;
use tempfile::TempDir;

// ============================================================================
// Helper
// ============================================================================

fn write_json(dir: &Path, filename: &str, content: &str) -> std::path::PathBuf {
    let path = dir.join(filename);
    if let Some(parent) = path.parent() {
        fs::create_dir_all(parent).unwrap();
    }
    fs::write(&path, content).unwrap();
    path
}

// ============================================================================
// Detection tests
// ============================================================================

#[test]
fn detect_does_not_panic() {
    let connector = CopilotConnector::new();
    let result = connector.detect();
    let _ = result.detected;
}

// ============================================================================
// Scan — turns format
// ============================================================================

#[test]
fn scan_parses_turns_format() {
    let tmp = TempDir::new().unwrap();
    let root = tmp.path().join("copilot-chat");
    fs::create_dir_all(&root).unwrap();

    let json = r#"[{
        "id": "conv-001",
        "workspaceFolder": "/home/user/project",
        "turns": [
            {
                "request": { "message": "How do I sort?", "timestamp": 1700000000000 },
                "response": { "message": "Use .sort().", "timestamp": 1700000001000 }
            }
        ]
    }]"#;

    write_json(&root, "conversations.json", json);

    let connector = CopilotConnector::new();
    let ctx = ScanContext::local_default(root, None);
    let convs = connector.scan(&ctx).unwrap();

    assert_eq!(convs.len(), 1);
    assert_eq!(convs[0].agent_slug, "copilot");
    assert_eq!(convs[0].external_id.as_deref(), Some("conv-001"));
    assert_eq!(convs[0].messages.len(), 2);
    assert_eq!(convs[0].messages[0].role, "user");
    assert!(convs[0].messages[0].content.contains("sort"));
    assert_eq!(convs[0].messages[1].role, "assistant");
    assert!(convs[0].started_at.is_some());
    assert!(convs[0].ended_at.is_some());
}

// ============================================================================
// Scan — messages format
// ============================================================================

#[test]
fn scan_parses_messages_format() {
    let tmp = TempDir::new().unwrap();
    let root = tmp.path().join("copilot-chat");
    fs::create_dir_all(&root).unwrap();

    let json = r#"{
        "id": "conv-002",
        "title": "Explain lifetimes",
        "messages": [
            { "role": "user", "content": "Explain lifetimes", "timestamp": 1700000010000 },
            { "role": "assistant", "content": "Lifetimes express scope validity.", "timestamp": 1700000011000 }
        ]
    }"#;

    write_json(&root, "session.json", json);

    let connector = CopilotConnector::new();
    let ctx = ScanContext::local_default(root, None);
    let convs = connector.scan(&ctx).unwrap();

    assert_eq!(convs.len(), 1);
    assert_eq!(convs[0].title.as_deref(), Some("Explain lifetimes"));
    assert_eq!(convs[0].messages.len(), 2);
}

// ============================================================================
// Scan — conversations wrapper
// ============================================================================

#[test]
fn scan_parses_conversations_wrapper() {
    let tmp = TempDir::new().unwrap();
    let root = tmp.path().join("copilot-chat");
    fs::create_dir_all(&root).unwrap();

    let json = r#"{
        "conversations": [
            { "id": "w1", "messages": [{"role": "user", "content": "Hello"}] },
            { "id": "w2", "messages": [{"role": "user", "content": "World"}] }
        ]
    }"#;

    write_json(&root, "all.json", json);

    let connector = CopilotConnector::new();
    let ctx = ScanContext::local_default(root, None);
    let convs = connector.scan(&ctx).unwrap();

    assert_eq!(convs.len(), 2);
}

// ============================================================================
// Edge cases
// ============================================================================

#[test]
fn scan_empty_dir_returns_empty() {
    let tmp = TempDir::new().unwrap();
    let root = tmp.path().join("copilot-chat");
    fs::create_dir_all(&root).unwrap();

    let connector = CopilotConnector::new();
    let ctx = ScanContext::local_default(root, None);
    let convs = connector.scan(&ctx).unwrap();
    assert!(convs.is_empty());
}

#[test]
fn scan_skips_invalid_json() {
    let tmp = TempDir::new().unwrap();
    let root = tmp.path().join("copilot-chat");
    fs::create_dir_all(&root).unwrap();

    write_json(&root, "invalid.json", "not valid json {{{");

    let connector = CopilotConnector::new();
    let ctx = ScanContext::local_default(root, None);
    let convs = connector.scan(&ctx).unwrap();
    assert!(convs.is_empty());
}

#[test]
fn scan_skips_empty_conversations() {
    let tmp = TempDir::new().unwrap();
    let root = tmp.path().join("copilot-chat");
    fs::create_dir_all(&root).unwrap();

    let json = r#"[
        {"id": "empty", "turns": []},
        {"id": "valid", "turns": [{"request": {"message": "Hi"}, "response": {"message": "Hello"}}]}
    ]"#;

    write_json(&root, "mixed.json", json);

    let connector = CopilotConnector::new();
    let ctx = ScanContext::local_default(root, None);
    let convs = connector.scan(&ctx).unwrap();

    assert_eq!(convs.len(), 1);
    assert_eq!(convs[0].external_id.as_deref(), Some("valid"));
}

#[test]
fn scan_respects_since_ts() {
    let tmp = TempDir::new().unwrap();
    let root = tmp.path().join("copilot-chat");
    fs::create_dir_all(&root).unwrap();

    write_json(
        &root,
        "old.json",
        r#"[{"id":"old","turns":[{"request":{"message":"old"},"response":{"message":"reply"}}]}]"#,
    );

    let connector = CopilotConnector::new();
    let far_future = chrono::Utc::now().timestamp_millis() + 86_400_000;
    let ctx = ScanContext::local_default(root, Some(far_future));
    let convs = connector.scan(&ctx).unwrap();
    assert!(convs.is_empty());
}

#[test]
fn scan_with_scan_roots() {
    let tmp = TempDir::new().unwrap();
    let home = tmp.path().join("fakehome");
    let copilot_dir = home.join(".config/Code/User/globalStorage/github.copilot-chat");
    fs::create_dir_all(&copilot_dir).unwrap();

    let json = r#"[{
        "id": "remote-001",
        "turns": [{"request": {"message": "test"}, "response": {"message": "reply"}}]
    }]"#;

    write_json(&copilot_dir, "conversations.json", json);

    let connector = CopilotConnector::new();
    let scan_root = ScanRoot::local(home);
    let ctx = ScanContext::with_roots(tmp.path().to_path_buf(), vec![scan_root], None);
    let convs = connector.scan(&ctx).unwrap();

    assert_eq!(convs.len(), 1);
    assert_eq!(convs[0].external_id.as_deref(), Some("remote-001"));
}
