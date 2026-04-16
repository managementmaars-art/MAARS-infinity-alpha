use coding_agent_search::connectors::{Connector, ScanContext, amp::AmpConnector};
use coding_agent_search::connectors::{NormalizedConversation, NormalizedMessage};
use coding_agent_search::indexer::{IndexOptions, persist::persist_conversation, run_index};
use coding_agent_search::search::query::{FieldMask, SearchClient, SearchFilters};
use coding_agent_search::search::tantivy::{TantivyIndex, index_dir};
use coding_agent_search::storage::sqlite::SqliteStorage;
use serial_test::serial;
use tempfile::TempDir;

fn norm_msg(idx: i64) -> NormalizedMessage {
    NormalizedMessage {
        idx,
        role: "user".into(),
        author: None,
        created_at: Some(1_700_000_000_000 + idx),
        content: format!("hello-{idx}"),
        extra: serde_json::json!({}),
        snippets: Vec::new(),
        invocations: Vec::new(),
    }
}

#[test]
fn search_logs_backend_selection() {
    let trace = TestTracing::new();
    let _guard = trace.install();

    let dir = TempDir::new().unwrap();
    let mut index = TantivyIndex::open_or_create(dir.path()).unwrap();
    let conv = NormalizedConversation {
        agent_slug: "codex".into(),
        external_id: None,
        title: Some("log test".into()),
        workspace: None,
        source_path: dir.path().join("rollout.jsonl"),
        started_at: Some(1),
        ended_at: Some(2),
        metadata: serde_json::json!({}),
        messages: vec![norm_msg(0)],
    };
    index.add_conversation(&conv).unwrap();
    index.commit().unwrap();

    let client = SearchClient::open(dir.path(), None)
        .unwrap()
        .expect("client");
    client
        .search("hello", SearchFilters::default(), 5, 0, FieldMask::FULL)
        .unwrap();

    let out = trace.output();
    eprintln!("logs: {out}");
    assert!(out.contains("backend=\"tantivy\""));
    assert!(out.contains("search_start"));
}

#[test]
fn amp_connector_emits_scan_span() {
    let trace = TestTracing::new();
    let _guard = trace.install();

    let fixture_root = std::path::PathBuf::from("tests/fixtures/amp");
    let conn = AmpConnector::new();
    let ctx = ScanContext {
        data_dir: fixture_root,
        scan_roots: Vec::new(),
        since_ts: None,
    };
    let convs = conn.scan(&ctx).unwrap();
    assert!(!convs.is_empty());

    let out = trace.output();
    assert!(out.contains("connector::amp"));
    assert!(out.contains("amp_scan"));
}

#[test]
fn persist_conversation_logs_counts() {
    let trace = TestTracing::new();
    let _guard = trace.install();

    let tmp = TempDir::new().unwrap();
    let data_dir = tmp.path().join("data");
    std::fs::create_dir_all(&data_dir).unwrap();
    let db_path = data_dir.join("db.sqlite");
    let storage = SqliteStorage::open(&db_path).unwrap();
    let mut index = TantivyIndex::open_or_create(&index_dir(&data_dir).unwrap()).unwrap();

    let conv = NormalizedConversation {
        agent_slug: "tester".into(),
        external_id: Some("ext-log".into()),
        title: Some("persist".into()),
        workspace: None,
        source_path: data_dir.join("src.log"),
        started_at: Some(10),
        ended_at: Some(20),
        metadata: serde_json::json!({}),
        messages: vec![norm_msg(0), norm_msg(1)],
    };

    persist_conversation(&storage, &mut index, &conv).unwrap();

    let out = trace.output();
    assert!(out.contains("persist_conversation"));
    assert!(out.contains("messages=2"));
}

struct EnvVarGuard {
    key: &'static str,
    previous: Option<String>,
}

impl EnvVarGuard {
    fn set(key: &'static str, value: &std::path::Path) -> Self {
        let previous = std::env::var(key).ok();
        unsafe {
            std::env::set_var(key, value);
        }
        Self { key, previous }
    }
}

impl Drop for EnvVarGuard {
    fn drop(&mut self) {
        match &self.previous {
            Some(value) => unsafe { std::env::set_var(self.key, value) },
            None => unsafe { std::env::remove_var(self.key) },
        }
    }
}

#[test]
#[serial]
fn run_index_does_not_drop_storage_without_explicit_close() {
    let trace = TestTracing::new();
    let _guard = trace.install();

    let tmp = TempDir::new().unwrap();
    let data_dir = tmp.path().join("data");
    let home_dir = tmp.path().join("home");
    let xdg_dir = tmp.path().join("xdg");
    std::fs::create_dir_all(&home_dir).unwrap();
    std::fs::create_dir_all(&xdg_dir).unwrap();
    let amp_dir = data_dir.join("amp");
    std::fs::create_dir_all(&amp_dir).unwrap();
    std::fs::write(
        amp_dir.join("thread-log.json"),
        r#"{
  "id": "thread-log",
  "title": "Amp test",
  "messages": [
    {"role":"user","text":"hi","createdAt":1700000000100},
    {"role":"assistant","text":"hello","createdAt":1700000000200}
  ]
}"#,
    )
    .unwrap();

    let _home_guard = EnvVarGuard::set("HOME", &home_dir);
    let _xdg_guard = EnvVarGuard::set("XDG_DATA_HOME", &xdg_dir);
    let prev_ignore_sources = std::env::var("CASS_IGNORE_SOURCES_CONFIG").ok();
    unsafe {
        std::env::set_var("CASS_IGNORE_SOURCES_CONFIG", "1");
    }

    let opts = IndexOptions {
        full: false,
        force_rebuild: false,
        watch: false,
        watch_once_paths: None,
        db_path: data_dir.join("agent_search.db"),
        data_dir,
        semantic: false,
        build_hnsw: false,
        embedder: "fastembed".to_string(),
        progress: None,
        watch_interval_secs: 30,
    };

    let result = run_index(opts, None);
    match prev_ignore_sources {
        Some(value) => unsafe { std::env::set_var("CASS_IGNORE_SOURCES_CONFIG", value) },
        None => unsafe { std::env::remove_var("CASS_IGNORE_SOURCES_CONFIG") },
    }
    result.unwrap();

    let out = trace.output();
    assert!(
        !out.contains("drop_close"),
        "run_index should explicitly close storage instead of relying on Drop: {out}"
    );
}

// Re-export util module so tests can find helpers without extra path noise.
mod util;
use util::TestTracing;
