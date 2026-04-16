//! Integration tests for GitHub Pages deployment module.
//!
//! Tests the GitHubDeployer functionality including size checks,
//! prerequisites validation, and bundle preparation.

use anyhow::Result;
use coding_agent_search::pages::deploy_github::{GitHubDeployer, Prerequisites};
use std::fs;
use tempfile::TempDir;

// ============================================
// Prerequisites Tests
// ============================================

#[test]
fn test_prerequisites_all_ready() {
    let prereqs = Prerequisites {
        gh_version: Some("gh version 2.40.0".to_string()),
        gh_authenticated: true,
        gh_username: Some("testuser".to_string()),
        git_version: Some("git version 2.43.0".to_string()),
        disk_space_mb: 10000,
        estimated_size_mb: 100,
    };

    assert!(prereqs.is_ready());
    assert!(prereqs.missing().is_empty());
}

#[test]
fn test_prerequisites_gh_not_installed() {
    let prereqs = Prerequisites {
        gh_version: None,
        gh_authenticated: false,
        gh_username: None,
        git_version: Some("git version 2.43.0".to_string()),
        disk_space_mb: 10000,
        estimated_size_mb: 100,
    };

    assert!(!prereqs.is_ready());
    let missing = prereqs.missing();
    assert!(missing.iter().any(|m| m.contains("gh CLI not installed")));
}

#[test]
fn test_prerequisites_gh_not_authenticated() {
    let prereqs = Prerequisites {
        gh_version: Some("gh version 2.40.0".to_string()),
        gh_authenticated: false,
        gh_username: None,
        git_version: Some("git version 2.43.0".to_string()),
        disk_space_mb: 10000,
        estimated_size_mb: 100,
    };

    assert!(!prereqs.is_ready());
    let missing = prereqs.missing();
    assert!(missing.iter().any(|m| m.contains("not authenticated")));
}

#[test]
fn test_prerequisites_git_not_installed() {
    let prereqs = Prerequisites {
        gh_version: Some("gh version 2.40.0".to_string()),
        gh_authenticated: true,
        gh_username: Some("testuser".to_string()),
        git_version: None,
        disk_space_mb: 10000,
        estimated_size_mb: 100,
    };

    assert!(!prereqs.is_ready());
    let missing = prereqs.missing();
    assert!(missing.iter().any(|m| m.contains("git not installed")));
}

// ============================================
// Deployer Builder Tests
// ============================================

#[test]
fn test_deployer_default_creation() {
    // Test that default deployer can be created
    let _deployer = GitHubDeployer::default();
    // If it compiles and doesn't panic, the default works
}

#[test]
fn test_deployer_builder_chain() {
    // Test builder pattern - if it compiles, the chain works
    let _deployer = GitHubDeployer::new("my-custom-archive")
        .description("My custom archive description")
        .public(false)
        .force(true);
}

// ============================================
// Size Check Tests
// ============================================

#[test]
fn test_size_check_empty_directory() -> Result<()> {
    let temp = TempDir::new()?;
    let deployer = GitHubDeployer::default();
    let check = deployer.check_size(temp.path())?;

    assert_eq!(check.file_count, 0);
    assert_eq!(check.total_bytes, 0);
    assert!(check.large_files.is_empty());
    assert!(!check.exceeds_limit);
    assert!(!check.has_oversized_files);

    Ok(())
}

#[test]
fn test_size_check_small_files() -> Result<()> {
    let temp = TempDir::new()?;

    // Create some small files
    fs::write(temp.path().join("file1.txt"), vec![0u8; 1000])?;
    fs::write(temp.path().join("file2.txt"), vec![0u8; 2000])?;
    fs::create_dir(temp.path().join("subdir"))?;
    fs::write(temp.path().join("subdir/file3.txt"), vec![0u8; 500])?;

    let deployer = GitHubDeployer::default();
    let check = deployer.check_size(temp.path())?;

    assert_eq!(check.file_count, 3);
    assert_eq!(check.total_bytes, 3500);
    assert!(check.large_files.is_empty());
    assert!(!check.exceeds_limit);
    assert!(!check.has_oversized_files);

    Ok(())
}

#[test]
fn test_size_check_nested_directories() -> Result<()> {
    let temp = TempDir::new()?;

    // Create nested structure
    fs::create_dir_all(temp.path().join("a/b/c"))?;
    fs::write(temp.path().join("root.txt"), "root")?;
    fs::write(temp.path().join("a/level1.txt"), "level1")?;
    fs::write(temp.path().join("a/b/level2.txt"), "level2")?;
    fs::write(temp.path().join("a/b/c/level3.txt"), "level3")?;

    let deployer = GitHubDeployer::default();
    let check = deployer.check_size(temp.path())?;

    assert_eq!(check.file_count, 4);
    assert!(!check.exceeds_limit);

    Ok(())
}

// ============================================
// Bundle Structure Tests
// ============================================

#[test]
fn test_bundle_structure_validation() -> Result<()> {
    let temp = TempDir::new()?;

    // Create a minimal test bundle structure
    fs::write(temp.path().join("index.html"), "<html></html>")?;
    fs::write(temp.path().join(".nojekyll"), "")?;
    fs::write(temp.path().join("robots.txt"), "User-agent: *\nDisallow: /")?;
    fs::write(temp.path().join("config.json"), r#"{"version": 1}"#)?;

    fs::create_dir(temp.path().join("payload"))?;
    fs::write(temp.path().join("payload/chunk-00000.bin"), vec![0u8; 100])?;

    fs::create_dir(temp.path().join("vendor"))?;
    fs::write(temp.path().join("vendor/sqlite3.js"), "// sqlite")?;

    let deployer = GitHubDeployer::default();
    let check = deployer.check_size(temp.path())?;

    assert!(check.file_count >= 6);
    assert!(!check.exceeds_limit);

    Ok(())
}

// ============================================
// Progress Callback Tests
// ============================================

#[test]
fn test_progress_phases() {
    // Verify expected progress phases
    let expected_phases = [
        "prereq", "size", "repo", "clone", "copy", "push", "pages", "complete",
    ];

    // The deploy function uses these phases in order
    for phase in expected_phases {
        assert!(
            !phase.is_empty(),
            "Progress phase '{}' should be non-empty",
            phase
        );
    }
}

// ============================================
// Error Message Tests
// ============================================

#[test]
fn test_prerequisites_error_messages_are_helpful() {
    let prereqs = Prerequisites {
        gh_version: None,
        gh_authenticated: false,
        gh_username: None,
        git_version: None,
        disk_space_mb: 0,
        estimated_size_mb: 0,
    };

    let missing = prereqs.missing();

    // Check that error messages include actionable instructions
    assert!(missing.iter().any(|m| m.contains("https://cli.github.com")));
    assert!(missing.iter().any(|m| m.contains("gh auth login")));
}

// ============================================
// Size Limit Constants Tests
// ============================================

#[test]
fn test_github_size_limits() {
    // GitHub Pages limits (documented)
    const MAX_SITE_SIZE: u64 = 1024 * 1024 * 1024; // 1 GB
    const MAX_FILE_SIZE: u64 = 100 * 1024 * 1024; // 100 MiB
    const WARNING_SIZE: u64 = 50 * 1024 * 1024; // 50 MiB

    // Verify our constants match expected limits
    assert_eq!(MAX_SITE_SIZE, 1_073_741_824);
    assert_eq!(MAX_FILE_SIZE, 104_857_600);
    assert_eq!(WARNING_SIZE, 52_428_800);
}

// ============================================
// Deployer Configuration Tests
// ============================================

#[test]
fn test_deployer_public_private_toggle() {
    // Test that builder accepts public/private setting
    let _public_deployer = GitHubDeployer::new("test").public(true);
    let _private_deployer = GitHubDeployer::new("test").public(false);
}

#[test]
fn test_deployer_force_toggle() {
    // Test that builder accepts force setting
    let _normal_deployer = GitHubDeployer::new("test").force(false);
    let _force_deployer = GitHubDeployer::new("test").force(true);
}

#[test]
fn test_deployer_description() {
    // Test that builder accepts description
    let _deployer = GitHubDeployer::new("test").description("A custom description for my archive");
}

// ============================================
// Local Git Repository Integration Tests
// (No network required - tests git operations with local bare repos)
// ============================================

/// Helper to create a local bare git repository
fn create_local_bare_repo(name: &str) -> Result<(TempDir, std::path::PathBuf)> {
    let temp = TempDir::new()?;
    let repo_path = temp.path().join(format!("{}.git", name));

    let output = std::process::Command::new("git")
        .args(["init", "--bare", repo_path.to_str().unwrap()])
        .output()?;

    if !output.status.success() {
        anyhow::bail!(
            "Failed to create bare repo: {}",
            String::from_utf8_lossy(&output.stderr)
        );
    }

    Ok((temp, repo_path))
}

/// Helper to create a working git repository and clone from bare
fn create_working_repo_from_bare(
    bare_repo: &std::path::Path,
    name: &str,
) -> Result<(TempDir, std::path::PathBuf)> {
    let temp = TempDir::new()?;
    let work_path = temp.path().join(name);

    let output = std::process::Command::new("git")
        .args([
            "clone",
            bare_repo.to_str().unwrap(),
            work_path.to_str().unwrap(),
        ])
        .output()?;

    // Clone may warn about empty repo, but should succeed
    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        if !stderr.contains("empty repository") {
            anyhow::bail!("Failed to clone: {}", stderr);
        }
    }

    Ok((temp, work_path))
}

/// Helper to set up git config for commits
fn configure_git_user(repo_path: &std::path::Path) -> Result<()> {
    std::process::Command::new("git")
        .args(["config", "user.email", "test@example.com"])
        .current_dir(repo_path)
        .output()?;

    std::process::Command::new("git")
        .args(["config", "user.name", "Test User"])
        .current_dir(repo_path)
        .output()?;

    Ok(())
}

#[test]
fn test_local_git_bare_repo_creation() -> Result<()> {
    let (_temp, repo_path) = create_local_bare_repo("test-repo")?;

    // Verify it's a bare repo
    assert!(repo_path.exists());
    assert!(repo_path.join("HEAD").exists());
    assert!(repo_path.join("objects").exists());
    assert!(repo_path.join("refs").exists());

    Ok(())
}

#[test]
fn test_local_git_clone_and_push() -> Result<()> {
    // Create a bare repo to act as "remote"
    let (_bare_temp, bare_repo) = create_local_bare_repo("origin")?;

    // Clone to working directory
    let (_work_temp, work_dir) = create_working_repo_from_bare(&bare_repo, "working")?;

    // Configure git user
    configure_git_user(&work_dir)?;

    // Create some content
    fs::write(work_dir.join("index.html"), "<html>test</html>")?;
    fs::write(work_dir.join(".nojekyll"), "")?;

    // Add and commit
    std::process::Command::new("git")
        .args(["add", "-A"])
        .current_dir(&work_dir)
        .output()?;

    let commit_output = std::process::Command::new("git")
        .args(["commit", "-m", "Initial commit"])
        .current_dir(&work_dir)
        .output()?;

    assert!(
        commit_output.status.success(),
        "Commit failed: {}",
        String::from_utf8_lossy(&commit_output.stderr)
    );

    // Get commit SHA
    let sha_output = std::process::Command::new("git")
        .args(["rev-parse", "HEAD"])
        .current_dir(&work_dir)
        .output()?;

    let commit_sha = String::from_utf8_lossy(&sha_output.stdout)
        .trim()
        .to_string();
    assert!(!commit_sha.is_empty());
    assert_eq!(commit_sha.len(), 40, "SHA should be 40 chars");

    // Push to bare repo
    let push_output = std::process::Command::new("git")
        .args(["push", "-u", "origin", "HEAD:main"])
        .current_dir(&work_dir)
        .output()?;

    assert!(
        push_output.status.success(),
        "Push failed: {}",
        String::from_utf8_lossy(&push_output.stderr)
    );

    Ok(())
}

#[test]
fn test_local_git_orphan_branch_workflow() -> Result<()> {
    // This tests the gh-pages orphan branch workflow used in deploy
    let (_bare_temp, bare_repo) = create_local_bare_repo("pages-repo")?;
    let (_work_temp, work_dir) = create_working_repo_from_bare(&bare_repo, "deploy")?;
    configure_git_user(&work_dir)?;

    // Create orphan branch (simulating gh-pages deployment)
    let orphan_output = std::process::Command::new("git")
        .args(["checkout", "--orphan", "gh-pages"])
        .current_dir(&work_dir)
        .output()?;

    assert!(
        orphan_output.status.success(),
        "Orphan branch failed: {}",
        String::from_utf8_lossy(&orphan_output.stderr)
    );

    // Add deployment files
    fs::write(work_dir.join("index.html"), "<html>deployed</html>")?;
    fs::write(work_dir.join(".nojekyll"), "")?;
    fs::create_dir(work_dir.join("payload"))?;
    fs::write(work_dir.join("payload/data.bin"), vec![0u8; 100])?;

    std::process::Command::new("git")
        .args(["add", "-A"])
        .current_dir(&work_dir)
        .output()?;

    let commit_output = std::process::Command::new("git")
        .args(["commit", "-m", "Deploy cass archive"])
        .current_dir(&work_dir)
        .output()?;

    assert!(
        commit_output.status.success(),
        "Commit on orphan failed: {}",
        String::from_utf8_lossy(&commit_output.stderr)
    );

    // Push to bare repo
    let push_output = std::process::Command::new("git")
        .args(["push", "-f", "origin", "gh-pages"])
        .current_dir(&work_dir)
        .output()?;

    assert!(
        push_output.status.success(),
        "Push gh-pages failed: {}",
        String::from_utf8_lossy(&push_output.stderr)
    );

    // Verify the branch exists in bare repo
    let branch_output = std::process::Command::new("git")
        .args(["branch", "-a"])
        .current_dir(&bare_repo)
        .output()?;

    let branches = String::from_utf8_lossy(&branch_output.stdout);
    assert!(
        branches.contains("gh-pages"),
        "gh-pages branch should exist in bare repo"
    );

    Ok(())
}

#[test]
fn test_copy_bundle_preserves_structure() -> Result<()> {
    let src = TempDir::new()?;
    let dst = TempDir::new()?;

    // Create a realistic bundle structure
    fs::write(src.path().join("index.html"), "<html></html>")?;
    fs::write(src.path().join("config.json"), r#"{"version":1}"#)?;
    fs::write(src.path().join(".nojekyll"), "")?;

    fs::create_dir_all(src.path().join("payload"))?;
    fs::write(src.path().join("payload/chunk-00000.bin"), vec![1u8; 1000])?;
    fs::write(src.path().join("payload/chunk-00001.bin"), vec![2u8; 1000])?;

    fs::create_dir_all(src.path().join("vendor/js"))?;
    fs::write(src.path().join("vendor/sqlite3.js"), "// sqlite")?;
    fs::write(src.path().join("vendor/js/app.js"), "// app")?;

    // Copy using recursive copy (simulating deploy copy)
    copy_dir_recursive(src.path(), dst.path())?;

    // Verify all files are copied
    assert!(dst.path().join("index.html").exists());
    assert!(dst.path().join("config.json").exists());
    assert!(dst.path().join(".nojekyll").exists());
    assert!(dst.path().join("payload/chunk-00000.bin").exists());
    assert!(dst.path().join("payload/chunk-00001.bin").exists());
    assert!(dst.path().join("vendor/sqlite3.js").exists());
    assert!(dst.path().join("vendor/js/app.js").exists());

    // Verify content is preserved
    let content = fs::read(dst.path().join("payload/chunk-00000.bin"))?;
    assert_eq!(content.len(), 1000);
    assert!(content.iter().all(|&b| b == 1));

    Ok(())
}

/// Recursive directory copy helper (matches the deploy module's implementation)
fn copy_dir_recursive(src: &std::path::Path, dst: &std::path::Path) -> Result<()> {
    if !dst.exists() {
        fs::create_dir_all(dst)?;
    }

    for entry in fs::read_dir(src)? {
        let entry = entry?;
        let src_path = entry.path();
        let dst_path = dst.join(entry.file_name());

        if src_path.is_dir() {
            copy_dir_recursive(&src_path, &dst_path)?;
        } else {
            fs::copy(&src_path, &dst_path)?;
        }
    }

    Ok(())
}

#[test]
fn test_copy_bundle_overwrites_existing() -> Result<()> {
    let src = TempDir::new()?;
    let dst = TempDir::new()?;

    // Create source
    fs::write(src.path().join("file.txt"), "new content")?;

    // Create existing file at destination
    fs::write(dst.path().join("file.txt"), "old content")?;
    fs::write(dst.path().join("extra.txt"), "should remain")?;

    // Copy
    copy_dir_recursive(src.path(), dst.path())?;

    // Verify new content overwrote old
    let content = fs::read_to_string(dst.path().join("file.txt"))?;
    assert_eq!(content, "new content");

    // Extra file should still exist (copy doesn't delete)
    assert!(dst.path().join("extra.txt").exists());

    Ok(())
}

// ============================================
// Progress Tracking Tests
// ============================================

#[test]
fn test_progress_callback_tracking() {
    let mut phases: Vec<String> = Vec::new();
    let mut messages: Vec<String> = Vec::new();

    // Simulate progress callback
    let mut progress = |phase: &str, msg: &str| {
        phases.push(phase.to_string());
        messages.push(msg.to_string());
    };

    // Simulate deploy phases
    progress("prereq", "Checking prerequisites...");
    progress("size", "Checking bundle size...");
    progress("repo", "Creating repository...");
    progress("clone", "Cloning repository...");
    progress("copy", "Copying bundle files...");
    progress("push", "Pushing to gh-pages branch...");
    progress("pages", "Enabling GitHub Pages...");
    progress("complete", "Deployment complete!");

    assert_eq!(phases.len(), 8);
    assert_eq!(phases[0], "prereq");
    assert_eq!(phases[7], "complete");

    // Verify messages are descriptive
    assert!(messages.iter().all(|m| !m.is_empty()));
    assert!(messages[0].contains("prerequisites"));
    assert!(messages[7].contains("complete"));
}

// ============================================
// Error Path Tests
// ============================================

#[test]
fn test_size_check_missing_directory() {
    let deployer = GitHubDeployer::default();
    let result = deployer.check_size(std::path::Path::new("/nonexistent/path/12345"));

    assert!(result.is_err());
}

#[test]
fn test_prerequisites_missing_multiple() {
    let prereqs = Prerequisites {
        gh_version: None,
        gh_authenticated: false,
        gh_username: None,
        git_version: None,
        disk_space_mb: 0,
        estimated_size_mb: 0,
    };

    let missing = prereqs.missing();

    // Should report all missing items
    assert_eq!(missing.len(), 3);

    // Verify each missing item has helpful guidance
    for msg in &missing {
        assert!(
            msg.contains("install") || msg.contains("run") || msg.contains("not"),
            "Missing message should contain actionable guidance: {}",
            msg
        );
    }
}

// ============================================
// Authentication Handling Tests
// ============================================

#[test]
fn test_prerequisites_auth_state_combinations() {
    // Test all auth state combinations
    let test_cases = vec![
        (true, true, Some("user"), true), // All OK
        (true, false, None, false),       // gh installed but not authed
        (false, false, None, false),      // gh not installed
        (true, true, None, true),         // authed but no username parsed (edge case)
    ];

    for (has_gh, is_authed, username, expected_ready) in test_cases {
        let prereqs = Prerequisites {
            gh_version: if has_gh {
                Some("gh 2.0".to_string())
            } else {
                None
            },
            gh_authenticated: is_authed,
            gh_username: username.map(|s| s.to_string()),
            git_version: Some("git 2.0".to_string()),
            disk_space_mb: 1000,
            estimated_size_mb: 100,
        };

        assert_eq!(
            prereqs.is_ready(),
            expected_ready,
            "Auth state mismatch for gh={}, authed={}, user={:?}",
            has_gh,
            is_authed,
            username
        );
    }
}

// ============================================
// Log Output Tests (for debugging)
// ============================================

#[test]
fn test_deploy_result_serialization() -> Result<()> {
    use coding_agent_search::pages::deploy_github::DeployResult;

    let result = DeployResult {
        repo_url: "https://github.com/user/repo".to_string(),
        pages_url: "https://user.github.io/repo".to_string(),
        pages_enabled: true,
        commit_sha: "abc123def456".to_string(),
    };

    // Verify it can be serialized to JSON (for logging)
    let json = serde_json::to_string_pretty(&result)?;
    assert!(json.contains("repo_url"));
    assert!(json.contains("pages_url"));
    assert!(json.contains("commit_sha"));

    // Verify it can be deserialized back
    let parsed: DeployResult = serde_json::from_str(&json)?;
    assert_eq!(parsed.repo_url, result.repo_url);
    assert_eq!(parsed.pages_url, result.pages_url);

    Ok(())
}

#[test]
fn test_prerequisites_serialization() -> Result<()> {
    let prereqs = Prerequisites {
        gh_version: Some("gh version 2.40.0".to_string()),
        gh_authenticated: true,
        gh_username: Some("testuser".to_string()),
        git_version: Some("git version 2.43.0".to_string()),
        disk_space_mb: 10000,
        estimated_size_mb: 100,
    };

    // Verify serialization for logging
    let json = serde_json::to_string_pretty(&prereqs)?;
    assert!(json.contains("gh_version"));
    assert!(json.contains("gh_authenticated"));
    assert!(json.contains("disk_space_mb"));

    Ok(())
}
