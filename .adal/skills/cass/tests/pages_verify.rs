use assert_cmd::cargo::cargo_bin_cmd;
use serde_json::Value;
use std::path::PathBuf;

fn fixture_root(name: &str) -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("tests/fixtures/pages_verify")
        .join(name)
}

#[test]
fn test_pages_verify_valid_bundle_json() {
    let fixture = fixture_root("valid");

    let output = cargo_bin_cmd!("cass")
        .args(["pages", "--verify"])
        .arg(&fixture)
        .arg("--json")
        .env("CODING_AGENT_SEARCH_NO_UPDATE_PROMPT", "1")
        .output()
        .expect("run cass pages --verify (valid)");

    assert!(output.status.success(), "verify should succeed");

    let json: Value = serde_json::from_slice(&output.stdout).expect("valid JSON output");
    assert_eq!(json.get("status").and_then(Value::as_str), Some("valid"));

    let checks = json.get("checks").expect("checks field");
    assert_eq!(
        checks
            .get("required_files")
            .and_then(|c| c.get("passed"))
            .and_then(Value::as_bool),
        Some(true)
    );
}

#[test]
fn test_pages_verify_missing_required_file_fails() {
    let fixture = fixture_root("missing_required_no_viewer");

    let output = cargo_bin_cmd!("cass")
        .args(["pages", "--verify"])
        .arg(&fixture)
        .arg("--json")
        .env("CODING_AGENT_SEARCH_NO_UPDATE_PROMPT", "1")
        .output()
        .expect("run cass pages --verify (missing required)");

    assert!(!output.status.success(), "verify should fail");

    let json: Value = serde_json::from_slice(&output.stdout).expect("valid JSON output");
    assert_eq!(json.get("status").and_then(Value::as_str), Some("invalid"));

    let checks = json.get("checks").expect("checks field");
    assert_eq!(
        checks
            .get("required_files")
            .and_then(|c| c.get("passed"))
            .and_then(Value::as_bool),
        Some(false)
    );
}

#[test]
fn test_pages_verify_secret_leak_fails() {
    let fixture = fixture_root("secret_leak");

    let output = cargo_bin_cmd!("cass")
        .args(["pages", "--verify"])
        .arg(&fixture)
        .arg("--json")
        .env("CODING_AGENT_SEARCH_NO_UPDATE_PROMPT", "1")
        .output()
        .expect("run cass pages --verify (secret leak)");

    assert!(!output.status.success(), "verify should fail on secrets");

    let json: Value = serde_json::from_slice(&output.stdout).expect("valid JSON output");
    assert_eq!(json.get("status").and_then(Value::as_str), Some("invalid"));

    let checks = json.get("checks").expect("checks field");
    assert_eq!(
        checks
            .get("no_secrets_in_site")
            .and_then(|c| c.get("passed"))
            .and_then(Value::as_bool),
        Some(false)
    );
}
