//! Performance sanity tests for robot mode CLI flows.
//!
//! These tests verify that robot-help, robot-docs, and trace mode
//! execute within acceptable latency bounds for AI agent usage.
//! Targets: <200ms for --robot-help, <300ms for robot-docs topics.

use assert_cmd::Command;
use std::path::PathBuf;
use std::time::{Duration, Instant};

fn base_cmd() -> Command {
    let mut cmd = Command::new(assert_cmd::cargo::cargo_bin!("cass"));
    cmd.env("CODING_AGENT_SEARCH_NO_UPDATE_PROMPT", "1");
    cmd
}

fn health_fixture_data_dir() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("tests")
        .join("fixtures")
        .join("search_demo_data")
}

/// Measure execution time of a command.
fn measure_cmd(cmd: &mut Command) -> (Duration, bool) {
    let start = Instant::now();
    let result = cmd.output();
    let elapsed = start.elapsed();
    let success = result.map(|o| o.status.success()).unwrap_or(false);
    (elapsed, success)
}

/// Run a command multiple times and return the median duration.
fn measure_median(args: &[&str], runs: usize) -> Duration {
    let mut durations: Vec<Duration> = Vec::with_capacity(runs);

    for _ in 0..runs {
        let mut cmd = base_cmd();
        cmd.args(args);
        let (elapsed, _) = measure_cmd(&mut cmd);
        durations.push(elapsed);
    }

    durations.sort();
    durations[runs / 2]
}

// =============================================================================
// Robot-help latency tests
// =============================================================================

#[test]
fn robot_help_latency_under_200ms() {
    // Warm-up run (cold start may be slower)
    let _ = base_cmd().args(["--robot-help"]).output();

    let median = measure_median(&["--robot-help"], 5);

    assert!(
        median < Duration::from_millis(200),
        "robot-help median latency {}ms exceeds 200ms threshold",
        median.as_millis()
    );
}

#[test]
fn robot_help_with_color_never_latency() {
    let _ = base_cmd().args(["--color=never", "--robot-help"]).output();

    let median = measure_median(&["--color=never", "--robot-help"], 5);

    assert!(
        median < Duration::from_millis(200),
        "robot-help (--color=never) median latency {}ms exceeds 200ms threshold",
        median.as_millis()
    );
}

// =============================================================================
// Robot-docs latency tests
// =============================================================================

#[test]
fn robot_docs_guide_latency_under_300ms() {
    let _ = base_cmd().args(["robot-docs", "guide"]).output();

    let median = measure_median(&["robot-docs", "guide"], 5);

    assert!(
        median < Duration::from_millis(300),
        "robot-docs guide median latency {}ms exceeds 300ms threshold",
        median.as_millis()
    );
}

#[test]
fn robot_docs_commands_latency_under_300ms() {
    let _ = base_cmd().args(["robot-docs", "commands"]).output();

    let median = measure_median(&["robot-docs", "commands"], 5);

    assert!(
        median < Duration::from_millis(300),
        "robot-docs commands median latency {}ms exceeds 300ms threshold",
        median.as_millis()
    );
}

#[test]
fn robot_docs_topics_latency_under_200ms() {
    let _ = base_cmd().args(["robot-docs", "topics"]).output();

    let median = measure_median(&["robot-docs", "topics"], 5);

    assert!(
        median < Duration::from_millis(200),
        "robot-docs topics median latency {}ms exceeds 200ms threshold",
        median.as_millis()
    );
}

#[test]
fn robot_docs_exit_codes_latency_under_200ms() {
    let _ = base_cmd().args(["robot-docs", "exit-codes"]).output();

    let median = measure_median(&["robot-docs", "exit-codes"], 5);

    assert!(
        median < Duration::from_millis(200),
        "robot-docs exit-codes median latency {}ms exceeds 200ms threshold",
        median.as_millis()
    );
}

#[test]
fn robot_docs_wrap_latency_under_200ms() {
    let _ = base_cmd().args(["robot-docs", "wrap"]).output();

    let median = measure_median(&["robot-docs", "wrap"], 5);

    assert!(
        median < Duration::from_millis(200),
        "robot-docs wrap median latency {}ms exceeds 200ms threshold",
        median.as_millis()
    );
}

// =============================================================================
// Introspection latency tests
// =============================================================================

#[test]
fn introspect_latency_under_300ms() {
    let _ = base_cmd().args(["introspect", "--json"]).output();

    let median = measure_median(&["introspect", "--json"], 5);

    assert!(
        median < Duration::from_millis(300),
        "introspect median latency {}ms exceeds 300ms threshold",
        median.as_millis()
    );
}

#[test]
fn api_version_latency_under_150ms() {
    let _ = base_cmd().args(["api-version", "--json"]).output();

    let median = measure_median(&["api-version", "--json"], 5);

    assert!(
        median < Duration::from_millis(150),
        "api-version median latency {}ms exceeds 150ms threshold",
        median.as_millis()
    );
}

#[test]
fn capabilities_latency_under_300ms() {
    let _ = base_cmd().args(["capabilities", "--json"]).output();

    let median = measure_median(&["capabilities", "--json"], 5);

    assert!(
        median < Duration::from_millis(300),
        "capabilities median latency {}ms exceeds 300ms threshold",
        median.as_millis()
    );
}

// =============================================================================
// Trace mode overhead tests
// =============================================================================

#[test]
fn trace_mode_adds_minimal_overhead() {
    // Warm-up runs
    let _ = base_cmd().args(["--robot-help"]).output();
    let _ = base_cmd().args(["--trace", "--robot-help"]).output();

    // Measure without trace
    let baseline = measure_median(&["--robot-help"], 5);

    // Measure with trace
    let with_trace = measure_median(&["--trace", "--robot-help"], 5);

    // Trace should add at most 50ms overhead
    let overhead = with_trace.saturating_sub(baseline);
    assert!(
        overhead < Duration::from_millis(50),
        "trace mode adds {}ms overhead (threshold: 50ms), baseline: {}ms, with_trace: {}ms",
        overhead.as_millis(),
        baseline.as_millis(),
        with_trace.as_millis()
    );
}

#[test]
fn trace_mode_on_robot_docs_adds_minimal_overhead() {
    // Warm-up runs
    let _ = base_cmd().args(["robot-docs", "guide"]).output();
    let _ = base_cmd().args(["--trace", "robot-docs", "guide"]).output();

    // Measure without trace
    let baseline = measure_median(&["robot-docs", "guide"], 5);

    // Measure with trace
    let with_trace = measure_median(&["--trace", "robot-docs", "guide"], 5);

    // Trace should add at most 50ms overhead
    let overhead = with_trace.saturating_sub(baseline);
    assert!(
        overhead < Duration::from_millis(50),
        "trace mode on robot-docs adds {}ms overhead (threshold: 50ms), baseline: {}ms, with_trace: {}ms",
        overhead.as_millis(),
        baseline.as_millis(),
        with_trace.as_millis()
    );
}

// =============================================================================
// Startup latency tests
// =============================================================================

#[test]
fn help_flag_latency_under_200ms() {
    let _ = base_cmd().args(["--help"]).output();

    let median = measure_median(&["--help"], 5);

    assert!(
        median < Duration::from_millis(200),
        "--help median latency {}ms exceeds 200ms threshold",
        median.as_millis()
    );
}

#[test]
fn version_flag_latency_under_150ms() {
    let _ = base_cmd().args(["--version"]).output();

    let median = measure_median(&["--version"], 5);

    assert!(
        median < Duration::from_millis(150),
        "--version median latency {}ms exceeds 150ms threshold",
        median.as_millis()
    );
}

// =============================================================================
// Cold start tests (first invocation)
// =============================================================================

#[test]
fn robot_help_cold_start_under_500ms() {
    // Single invocation (no warm-up) - cold start scenario
    let mut cmd = base_cmd();
    cmd.args(["--robot-help"]);
    let (elapsed, success) = measure_cmd(&mut cmd);

    assert!(success, "robot-help command should succeed");
    assert!(
        elapsed < Duration::from_millis(500),
        "robot-help cold start latency {}ms exceeds 500ms threshold",
        elapsed.as_millis()
    );
}

// =============================================================================
// Combined workflow latency tests
// =============================================================================

#[test]
fn typical_agent_discovery_workflow_under_1sec() {
    // Simulate typical agent discovery workflow:
    // 1. api-version
    // 2. capabilities
    // 3. robot-docs guide

    let start = Instant::now();

    let _ = base_cmd().args(["api-version", "--json"]).output();
    let _ = base_cmd().args(["capabilities", "--json"]).output();
    let _ = base_cmd().args(["robot-docs", "guide"]).output();

    let total = start.elapsed();

    assert!(
        total < Duration::from_secs(1),
        "typical agent discovery workflow took {}ms (threshold: 1000ms)",
        total.as_millis()
    );
}

#[test]
fn health_check_latency_under_100ms() {
    let data_dir = health_fixture_data_dir();
    let data_dir = data_dir
        .to_str()
        .expect("fixture path should be valid UTF-8");

    let _ = base_cmd()
        .args(["health", "--json", "--data-dir", data_dir])
        .output();

    let median = measure_median(&["health", "--json", "--data-dir", data_dir], 5);

    assert!(
        median < Duration::from_millis(100),
        "health check median latency {}ms exceeds 100ms threshold",
        median.as_millis()
    );
}
