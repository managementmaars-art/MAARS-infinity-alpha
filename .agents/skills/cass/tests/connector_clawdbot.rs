use coding_agent_search::connectors::clawdbot::ClawdbotConnector;
use coding_agent_search::connectors::{Connector, ScanContext};
use std::fs;
use std::path::Path;
use tempfile::TempDir;

// ============================================================================
// Helper
// ============================================================================

fn write_session(root: &Path, name: &str, lines: &[&str]) -> std::path::PathBuf {
    let path = root.join(name);
    fs::write(&path, lines.join("\n")).unwrap();
    path
}

// ============================================================================
// Detection tests
// ============================================================================

#[test]
fn detect_does_not_panic() {
    let connector = ClawdbotConnector::new();
    let result = connector.detect();
    let _ = result.detected;
}

// ============================================================================
// Scan — happy path
// ============================================================================

#[test]
fn scan_parses_basic_conversation() {
    let tmp = TempDir::new().unwrap();
    let sessions = tmp.path().join(".clawdbot/sessions");
    fs::create_dir_all(&sessions).unwrap();

    write_session(
        &sessions,
        "session.jsonl",
        &[
            r#"{"role":"user","content":"Hello Clawdbot","timestamp":"2025-06-15T10:00:00.000Z"}"#,
            r#"{"role":"assistant","content":"Hi there!","timestamp":"2025-06-15T10:00:05.000Z"}"#,
        ],
    );

    let connector = ClawdbotConnector::new();
    let ctx = ScanContext::local_default(sessions.clone(), None);
    let convs = connector.scan(&ctx).unwrap();

    assert_eq!(convs.len(), 1);
    assert_eq!(convs[0].agent_slug, "clawdbot");
    assert_eq!(convs[0].messages.len(), 2);
    assert_eq!(convs[0].messages[0].role, "user");
    assert_eq!(convs[0].messages[0].content, "Hello Clawdbot");
    assert_eq!(convs[0].messages[1].role, "assistant");
    assert!(convs[0].started_at.is_some());
    assert!(convs[0].ended_at.is_some());
    assert_eq!(convs[0].title, Some("Hello Clawdbot".to_string()));
}

#[test]
fn scan_multiple_sessions() {
    let tmp = TempDir::new().unwrap();
    let sessions = tmp.path().join(".clawdbot/sessions");
    fs::create_dir_all(&sessions).unwrap();

    write_session(
        &sessions,
        "a.jsonl",
        &[r#"{"role":"user","content":"Session A","timestamp":"2025-06-15T09:00:00.000Z"}"#],
    );
    write_session(
        &sessions,
        "b.jsonl",
        &[r#"{"role":"user","content":"Session B","timestamp":"2025-06-15T10:00:00.000Z"}"#],
    );

    let connector = ClawdbotConnector::new();
    let ctx = ScanContext::local_default(sessions.clone(), None);
    let convs = connector.scan(&ctx).unwrap();

    assert_eq!(convs.len(), 2);
    let contents: Vec<&str> = convs
        .iter()
        .map(|c| c.messages[0].content.as_str())
        .collect();
    assert!(contents.contains(&"Session A"));
    assert!(contents.contains(&"Session B"));
}

// ============================================================================
// Scan — edge cases
// ============================================================================

#[test]
fn scan_skips_invalid_json_and_empty_lines() {
    let tmp = TempDir::new().unwrap();
    let sessions = tmp.path().join(".clawdbot/sessions");
    fs::create_dir_all(&sessions).unwrap();

    write_session(
        &sessions,
        "mixed.jsonl",
        &[
            "",
            "not-json-at-all",
            r#"{"role":"user","content":"Valid","timestamp":"2025-06-15T10:00:00.000Z"}"#,
            r#"{"role":"assistant","content":"","timestamp":"2025-06-15T10:00:01.000Z"}"#,
        ],
    );

    let connector = ClawdbotConnector::new();
    let ctx = ScanContext::local_default(sessions.clone(), None);
    let convs = connector.scan(&ctx).unwrap();

    assert_eq!(convs.len(), 1);
    assert_eq!(
        convs[0].messages.len(),
        1,
        "empty content should be skipped"
    );
    assert_eq!(convs[0].messages[0].content, "Valid");
}

#[test]
fn scan_empty_directory_returns_empty() {
    let tmp = TempDir::new().unwrap();
    let sessions = tmp.path().join(".clawdbot/sessions");
    fs::create_dir_all(&sessions).unwrap();

    let connector = ClawdbotConnector::new();
    let ctx = ScanContext::local_default(sessions.clone(), None);
    let convs = connector.scan(&ctx).unwrap();

    assert!(convs.is_empty());
}

#[test]
fn scan_handles_malformed_json() {
    let tmp = TempDir::new().unwrap();
    let sessions = tmp.path().join(".clawdbot/sessions");
    fs::create_dir_all(&sessions).unwrap();

    write_session(
        &sessions,
        "bad.jsonl",
        &[
            r#"{"broken json ..."#,
            r#"{"role":"user","content":"After malformed","timestamp":"2025-06-15T10:00:00.000Z"}"#,
        ],
    );

    let connector = ClawdbotConnector::new();
    let ctx = ScanContext::local_default(sessions.clone(), None);
    let convs = connector.scan(&ctx).unwrap();

    assert_eq!(convs.len(), 1);
    assert_eq!(convs[0].messages[0].content, "After malformed");
}

#[test]
fn scan_preserves_message_ordering() {
    let tmp = TempDir::new().unwrap();
    let sessions = tmp.path().join(".clawdbot/sessions");
    fs::create_dir_all(&sessions).unwrap();

    write_session(
        &sessions,
        "ordered.jsonl",
        &[
            r#"{"role":"user","content":"First","timestamp":"2025-06-15T10:00:00.000Z"}"#,
            r#"{"role":"assistant","content":"Second","timestamp":"2025-06-15T10:00:01.000Z"}"#,
            r#"{"role":"user","content":"Third","timestamp":"2025-06-15T10:00:02.000Z"}"#,
        ],
    );

    let connector = ClawdbotConnector::new();
    let ctx = ScanContext::local_default(sessions.clone(), None);
    let convs = connector.scan(&ctx).unwrap();

    assert_eq!(convs[0].messages[0].idx, 0);
    assert_eq!(convs[0].messages[0].content, "First");
    assert_eq!(convs[0].messages[1].idx, 1);
    assert_eq!(convs[0].messages[1].content, "Second");
    assert_eq!(convs[0].messages[2].idx, 2);
    assert_eq!(convs[0].messages[2].content, "Third");
}

// ============================================================================
// Incremental scanning (since_ts)
// ============================================================================

#[test]
fn scan_incremental_since_ts() {
    let tmp = TempDir::new().unwrap();
    let sessions = tmp.path().join(".clawdbot/sessions");
    fs::create_dir_all(&sessions).unwrap();

    write_session(
        &sessions,
        "recent.jsonl",
        &[r#"{"role":"user","content":"Recent","timestamp":"2025-06-15T10:00:00.000Z"}"#],
    );

    let connector = ClawdbotConnector::new();

    // Far-future since_ts should filter out everything.
    let far_future = chrono::Utc::now().timestamp_millis() + 86_400_000;
    let ctx = ScanContext::local_default(sessions.clone(), Some(far_future));
    let convs = connector.scan(&ctx).unwrap();

    assert!(
        convs.is_empty(),
        "far-future since_ts should filter out old files"
    );
}

// ============================================================================
// External ID extraction
// ============================================================================

#[test]
fn scan_extracts_external_id_from_filename() {
    let tmp = TempDir::new().unwrap();
    let sessions = tmp.path().join(".clawdbot/sessions");
    fs::create_dir_all(&sessions).unwrap();

    write_session(
        &sessions,
        "my-session-42.jsonl",
        &[r#"{"role":"user","content":"Test","timestamp":"2025-06-15T10:00:00.000Z"}"#],
    );

    let connector = ClawdbotConnector::new();
    let ctx = ScanContext::local_default(sessions.clone(), None);
    let convs = connector.scan(&ctx).unwrap();

    assert_eq!(convs.len(), 1);
    assert!(
        convs[0]
            .external_id
            .as_ref()
            .unwrap()
            .contains("my-session-42"),
        "external_id should be derived from filename stem"
    );
}
