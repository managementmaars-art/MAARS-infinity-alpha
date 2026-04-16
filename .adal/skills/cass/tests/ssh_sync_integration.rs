//! Integration tests for SSH sync operations.
//!
//! These tests require Docker to be available and will be skipped if not.
//! Run with: `cargo test --test ssh_sync_integration -- --ignored`
//!
//! The tests use a Docker container with an SSH server to test real
//! SSH operations without requiring external infrastructure.

mod ssh_test_helper;
mod util;

use assert_cmd::cargo::cargo_bin_cmd;
use coding_agent_search::sources::provenance::SourceKind;
use coding_agent_search::storage::sqlite::SqliteStorage;
use ssh_test_helper::{SshTestServer, docker_available};
use util::EnvGuard;

/// Skip tests if Docker is not available.
fn require_docker() {
    if !docker_available() {
        eprintln!("Skipping test: Docker not available");
    }
}

/// Integration test: Full sync cycle against real SSH server.
///
/// This test verifies that we can:
/// 1. Connect to a real SSH server
/// 2. Sync files using rsync over SSH
/// 3. Get correct file counts and bytes transferred
#[test]
#[ignore = "requires Docker"]
fn test_sync_source_real_ssh() {
    require_docker();

    let server = SshTestServer::start().expect("SSH server should start");
    let tmp = tempfile::TempDir::new().unwrap();

    // Create a minimal source.toml config in memory
    // We need to manually configure rsync options since SourceDefinition doesn't
    // expose the SSH port directly

    // For this test, we'll run rsync directly with the server's settings
    let local_dest = tmp.path().join("mirror");
    std::fs::create_dir_all(&local_dest).unwrap();

    // Run rsync with explicit SSH options
    let ssh_opts = server.rsync_ssh_opts();
    let remote_path = format!("{}:/root/.claude/projects/", server.ssh_target());

    let output = std::process::Command::new("rsync")
        .args([
            "-avz",
            "--stats",
            "-e",
            &ssh_opts,
            &remote_path,
            local_dest.to_str().unwrap(),
        ])
        .output()
        .expect("rsync should execute");

    assert!(
        output.status.success(),
        "rsync should succeed: {}",
        String::from_utf8_lossy(&output.stderr)
    );

    // Verify files were transferred
    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(
        stdout.contains("test-project") || stdout.contains("session.jsonl"),
        "Should transfer test files: {}",
        stdout
    );

    // Verify local files exist
    let test_file = local_dest.join("test-project/session.jsonl");
    assert!(test_file.exists(), "Session file should exist locally");

    // Read and verify content
    let content = std::fs::read_to_string(&test_file).unwrap();
    assert!(
        content.contains("hello world"),
        "File should contain test content"
    );
}

/// Integration test: Sync multiple paths from remote.
#[test]
#[ignore = "requires Docker"]
fn test_sync_multiple_paths() {
    require_docker();

    let server = SshTestServer::start().expect("SSH server should start");
    let tmp = tempfile::TempDir::new().unwrap();
    let local_dest = tmp.path().join("mirror");
    std::fs::create_dir_all(&local_dest).unwrap();

    let ssh_opts = server.rsync_ssh_opts();

    // Sync Claude projects
    let claude_dest = local_dest.join("claude");
    std::fs::create_dir_all(&claude_dest).unwrap();

    let output1 = std::process::Command::new("rsync")
        .args([
            "-avz",
            "-e",
            &ssh_opts,
            &format!("{}:/root/.claude/", server.ssh_target()),
            claude_dest.to_str().unwrap(),
        ])
        .output()
        .expect("rsync should execute");

    assert!(output1.status.success(), "Claude sync should succeed");

    // Sync Codex sessions
    let codex_dest = local_dest.join("codex");
    std::fs::create_dir_all(&codex_dest).unwrap();

    let output2 = std::process::Command::new("rsync")
        .args([
            "-avz",
            "-e",
            &ssh_opts,
            &format!("{}:/root/.codex/", server.ssh_target()),
            codex_dest.to_str().unwrap(),
        ])
        .output()
        .expect("rsync should execute");

    assert!(output2.status.success(), "Codex sync should succeed");

    // Verify both sets of files exist
    assert!(
        claude_dest
            .join("projects/test-project/session.jsonl")
            .exists(),
        "Claude session should exist"
    );
    assert!(
        codex_dest.join("sessions/session1.json").exists(),
        "Codex session should exist"
    );
}

/// Integration test: End-to-end sources sync via cass CLI with real SSH.
///
/// Validates:
/// - `cass sources sync` reports no sources when config is empty
/// - `cass sources add` works against real SSH (via ssh config)
/// - `cass sources sync --json` reports transfer stats
/// - SQLite provenance + workspace path mappings are applied
#[test]
#[ignore = "requires Docker"]
fn test_sources_sync_e2e_real_ssh() {
    require_docker();

    let server = SshTestServer::start().expect("SSH server should start");
    let tmp = tempfile::TempDir::new().unwrap();
    let home_dir = tmp.path().join("home");
    let config_dir = tmp.path().join("config");
    let data_dir = tmp.path().join("data");

    std::fs::create_dir_all(home_dir.join(".ssh")).unwrap();
    std::fs::create_dir_all(&config_dir).unwrap();
    std::fs::create_dir_all(&data_dir).unwrap();

    // Write SSH config so `cass sources add` can connect via alias with port/key.
    let ssh_config = format!(
        "Host cass-test\n  HostName 127.0.0.1\n  User root\n  Port {}\n  IdentityFile {}\n  StrictHostKeyChecking no\n  UserKnownHostsFile /dev/null\n",
        server.port(),
        server.private_key_path().display()
    );
    let ssh_config_path = home_dir.join(".ssh/config");
    std::fs::write(&ssh_config_path, ssh_config).unwrap();

    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        std::fs::set_permissions(
            home_dir.join(".ssh"),
            std::fs::Permissions::from_mode(0o700),
        )
        .unwrap();
        std::fs::set_permissions(&ssh_config_path, std::fs::Permissions::from_mode(0o600)).unwrap();
    }

    // Seed a session with workspace metadata for path mapping verification.
    let seed_script = r#"mkdir -p /root/.claude/projects/workspace-a
cat > /root/.claude/projects/workspace-a/session.jsonl <<'EOF'
{"type":"user","cwd":"/root/projects/workspace-a","message":{"content":"Workspace mapping test"}}
{"type":"assistant","message":{"content":"ok"}}
EOF
"#;
    server
        .ssh_exec_with_stdin(seed_script)
        .expect("seed remote session");

    let _guard_home = EnvGuard::set("HOME", home_dir.to_string_lossy());
    let _guard_config = EnvGuard::set("XDG_CONFIG_HOME", config_dir.to_string_lossy());
    let _guard_data = EnvGuard::set("CASS_DATA_DIR", data_dir.to_string_lossy());

    // 1) Sync with no sources configured should return a friendly JSON status.
    let no_sources = cargo_bin_cmd!("cass")
        .args(["sources", "sync", "--json"])
        .env("HOME", &home_dir)
        .env("XDG_CONFIG_HOME", &config_dir)
        .env("CASS_DATA_DIR", &data_dir)
        .output()
        .expect("sources sync (no sources)");
    assert!(no_sources.status.success());
    let no_sources_json: serde_json::Value =
        serde_json::from_slice(&no_sources.stdout).expect("valid JSON");
    assert_eq!(no_sources_json["status"], "no_sources");

    // 2) Add a real SSH source (uses ssh config alias).
    let add_output = cargo_bin_cmd!("cass")
        .args([
            "sources",
            "add",
            "root@cass-test",
            "--name",
            "cass-test",
            "--path",
            "~/.claude/projects",
        ])
        .env("HOME", &home_dir)
        .env("XDG_CONFIG_HOME", &config_dir)
        .env("CASS_DATA_DIR", &data_dir)
        .output()
        .expect("sources add");
    assert!(
        add_output.status.success(),
        "sources add should succeed: {}",
        String::from_utf8_lossy(&add_output.stderr)
    );

    // 3) Add a path mapping for workspace rewrite.
    let map_output = cargo_bin_cmd!("cass")
        .args([
            "sources",
            "mappings",
            "add",
            "cass-test",
            "--from",
            "/root/projects",
            "--to",
            "/local/projects",
        ])
        .env("HOME", &home_dir)
        .env("XDG_CONFIG_HOME", &config_dir)
        .env("CASS_DATA_DIR", &data_dir)
        .output()
        .expect("sources mappings add");
    assert!(
        map_output.status.success(),
        "sources mappings add should succeed: {}",
        String::from_utf8_lossy(&map_output.stderr)
    );

    // 4) Sync via CLI (no-index for clean JSON output) and assert transfer metrics.
    let sync_output = cargo_bin_cmd!("cass")
        .args([
            "sources",
            "sync",
            "--source",
            "cass-test",
            "--json",
            "--no-index",
        ])
        .env("HOME", &home_dir)
        .env("XDG_CONFIG_HOME", &config_dir)
        .env("CASS_DATA_DIR", &data_dir)
        .output()
        .expect("sources sync");
    assert!(
        sync_output.status.success(),
        "sources sync should succeed: {}",
        String::from_utf8_lossy(&sync_output.stderr)
    );
    let sync_json: serde_json::Value =
        serde_json::from_slice(&sync_output.stdout).expect("valid JSON");
    assert_eq!(sync_json["status"], "complete");
    assert!(
        sync_json["total_files"].as_u64().unwrap_or(0) > 0,
        "expected transferred files in sync report"
    );

    // 5) Build index after sync, then validate provenance + path mappings in SQLite.
    let index_output = cargo_bin_cmd!("cass")
        .args(["index", "--full", "--data-dir", data_dir.to_str().unwrap()])
        .env("HOME", &home_dir)
        .env("XDG_CONFIG_HOME", &config_dir)
        .env("CASS_DATA_DIR", &data_dir)
        .output()
        .expect("cass index --full");
    assert!(
        index_output.status.success(),
        "index should succeed: {}",
        String::from_utf8_lossy(&index_output.stderr)
    );

    let db_path = data_dir.join("agent_search.db");
    let storage = SqliteStorage::open(&db_path).expect("open sqlite");

    let sources = storage.list_sources().expect("list sources");
    let remote_source = sources
        .iter()
        .find(|s| s.id == "cass-test")
        .expect("remote source should exist");
    assert_eq!(remote_source.kind, SourceKind::Ssh);

    let conversations = storage
        .list_conversations(200, 0)
        .expect("list conversations");
    let remote_conv = conversations
        .into_iter()
        .find(|c| c.source_id == "cass-test")
        .expect("remote conversation should exist");
    assert_eq!(
        remote_conv.workspace,
        Some(std::path::PathBuf::from("/local/projects/workspace-a"))
    );
    assert_eq!(
        remote_conv.metadata_json["cass"]["workspace_original"],
        "/root/projects/workspace-a"
    );
}

/// Integration test: Get remote home directory.
#[test]
#[ignore = "requires Docker"]
fn test_get_remote_home() {
    require_docker();

    let server = SshTestServer::start().expect("SSH server should start");

    // Execute `echo $HOME` on the remote
    let home = server.ssh_exec("echo $HOME").expect("Should get home");

    assert_eq!(home.trim(), "/root", "Remote home should be /root");
}

/// Integration test: Verify tilde expansion works with rsync.
#[test]
#[ignore = "requires Docker"]
fn test_tilde_expansion_with_rsync() {
    require_docker();

    let server = SshTestServer::start().expect("SSH server should start");
    let tmp = tempfile::TempDir::new().unwrap();
    let local_dest = tmp.path().join("mirror");
    std::fs::create_dir_all(&local_dest).unwrap();

    // Get remote home
    let home = server
        .ssh_exec("echo $HOME")
        .expect("Should get home")
        .trim()
        .to_string();

    // Expand ~/... to actual path
    let expanded_path = format!("{}/.claude/projects/", home);

    let ssh_opts = server.rsync_ssh_opts();
    let remote_path = format!("{}:{}", server.ssh_target(), expanded_path);

    let output = std::process::Command::new("rsync")
        .args([
            "-avz",
            "-e",
            &ssh_opts,
            &remote_path,
            local_dest.to_str().unwrap(),
        ])
        .output()
        .expect("rsync should execute");

    assert!(
        output.status.success(),
        "Expanded path rsync should succeed"
    );

    // Verify files were transferred
    assert!(
        local_dest.join("test-project/session.jsonl").exists(),
        "Session file should exist after tilde expansion"
    );
}

/// Integration test: Handle non-existent remote path gracefully.
#[test]
#[ignore = "requires Docker"]
fn test_sync_nonexistent_path() {
    require_docker();

    let server = SshTestServer::start().expect("SSH server should start");
    let tmp = tempfile::TempDir::new().unwrap();

    let ssh_opts = server.rsync_ssh_opts();
    let remote_path = format!("{}:/nonexistent/path/", server.ssh_target());

    let output = std::process::Command::new("rsync")
        .args([
            "-avz",
            "-e",
            &ssh_opts,
            &remote_path,
            tmp.path().to_str().unwrap(),
        ])
        .output()
        .expect("rsync should execute");

    // rsync should fail for non-existent paths
    assert!(
        !output.status.success(),
        "rsync should fail for non-existent path"
    );
}

/// Integration test: SSH connection with wrong port fails.
#[test]
fn test_ssh_wrong_port_fails() {
    // This test doesn't need Docker - just verifies timeout behavior
    let _tmp = tempfile::TempDir::new().unwrap();

    let output = std::process::Command::new("ssh")
        .args([
            "-o",
            "StrictHostKeyChecking=no",
            "-o",
            "UserKnownHostsFile=/dev/null",
            "-o",
            "ConnectTimeout=2",
            "-o",
            "BatchMode=yes",
            "-p",
            "65535", // Unlikely to be in use
            "root@127.0.0.1",
            "echo test",
        ])
        .output()
        .expect("ssh should execute");

    assert!(!output.status.success(), "SSH to wrong port should fail");
}

/// Integration test: Probe host via SSH using the probe module.
#[test]
#[ignore = "requires Docker"]
fn test_probe_host_real_ssh() {
    require_docker();

    let server = SshTestServer::start().expect("SSH server should start");

    // Test basic probe-like operations via SSH
    // Note: Full probe testing would require custom SSH config for the port.
    // For now, verify we can execute the same commands the probe script uses.

    let output = server
        .ssh_exec("uname -s && uname -m && echo HOME=$HOME")
        .expect("Probe should succeed");

    assert!(output.contains("Linux") || output.contains("Darwin"));
    assert!(output.contains("HOME=/root"));
}

/// Integration test: List files on remote via SSH.
#[test]
#[ignore = "requires Docker"]
fn test_list_remote_files() {
    require_docker();

    let server = SshTestServer::start().expect("SSH server should start");

    // List agent directories
    let output = server
        .ssh_exec("ls -la ~/.claude/projects/")
        .expect("ls should succeed");

    assert!(
        output.contains("test-project"),
        "Should list test-project directory"
    );

    // List session files
    let output = server
        .ssh_exec("find ~/.claude -name '*.jsonl' -type f")
        .expect("find should succeed");

    assert!(
        output.contains("session.jsonl"),
        "Should find session.jsonl files"
    );
}

/// Integration test: Check rsync stats parsing.
#[test]
#[ignore = "requires Docker"]
fn test_rsync_stats_parsing() {
    require_docker();

    let server = SshTestServer::start().expect("SSH server should start");
    let tmp = tempfile::TempDir::new().unwrap();

    let ssh_opts = server.rsync_ssh_opts();
    let remote_path = format!("{}:/root/.claude/", server.ssh_target());

    let output = std::process::Command::new("rsync")
        .args([
            "-avz",
            "--stats",
            "-e",
            &ssh_opts,
            &remote_path,
            tmp.path().to_str().unwrap(),
        ])
        .output()
        .expect("rsync should execute");

    let stdout = String::from_utf8_lossy(&output.stdout);

    // Verify stats are present in output
    assert!(
        stdout.contains("Number of") || stdout.contains("files transferred"),
        "rsync output should contain stats: {}",
        stdout
    );
}

/// Integration test: Verify container cleanup on drop.
///
/// This test verifies that SshTestServer's Drop implementation doesn't panic.
/// The actual container cleanup is handled by Docker's --rm flag and the
/// explicit `docker stop` in Drop.
#[test]
#[ignore = "requires Docker"]
fn test_container_cleanup() {
    require_docker();

    // Create server in inner scope so Drop runs at block end
    {
        let server = SshTestServer::start().expect("SSH server should start");

        // Verify the server is actually working before we drop it
        let output = server
            .ssh_exec("echo cleanup_test")
            .expect("SSH should work");
        assert!(
            output.contains("cleanup_test"),
            "Server should be responsive"
        );

        // Server is dropped at end of this block
    }

    // After the server is dropped, wait a moment for cleanup
    std::thread::sleep(std::time::Duration::from_millis(500));

    // If we reach here without panic, Drop worked correctly.
    // The container is auto-removed by Docker's --rm flag.
}
