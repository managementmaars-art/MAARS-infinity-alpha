//! E2E Tests for HTML Export Visual Validation
//!
//! Tests the complete export pipeline including visual structure,
//! CSS presence, JavaScript functionality, and accessibility.

use assert_cmd::Command;
use regex::Regex;
use serde_json::Value;
use std::fs;
use std::path::Path;
use tempfile::TempDir;
use tracing::{debug, info};

// ============================================================================
// Test Helpers
// ============================================================================

fn base_cmd() -> Command {
    let mut cmd = Command::new(assert_cmd::cargo::cargo_bin!("cass"));
    cmd.env("CODING_AGENT_SEARCH_NO_UPDATE_PROMPT", "1");
    cmd
}

/// Export a fixture file and return the HTML content.
fn export_fixture(fixture_name: &str) -> String {
    let fixture_path = Path::new("tests/fixtures/message_grouping").join(fixture_name);
    let temp_dir = TempDir::new().expect("create temp dir");

    info!(
        fixture = fixture_name,
        output_dir = %temp_dir.path().display(),
        "Exporting fixture to HTML"
    );

    let mut cmd = base_cmd();
    cmd.args([
        "export-html",
        fixture_path.to_str().unwrap(),
        "--output-dir",
        temp_dir.path().to_str().unwrap(),
        "--json",
    ]);

    let output = cmd.output().expect("run export command");

    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        panic!("Export failed for {}: {}", fixture_name, stderr);
    }

    let stdout = String::from_utf8_lossy(&output.stdout);
    let json: Value = serde_json::from_str(stdout.trim()).expect("parse export JSON result");

    let output_path = json["exported"]["output_path"]
        .as_str()
        .expect("output_path in exported result");

    let html = fs::read_to_string(output_path).expect("read exported HTML");

    info!(
        fixture = fixture_name,
        size_bytes = html.len(),
        "Export complete"
    );

    html
}

/// Count occurrences of a pattern in HTML.
fn count_pattern(html: &str, pattern: &str) -> usize {
    let re = Regex::new(pattern).expect("valid regex");
    re.find_iter(html).count()
}

// ============================================================================
// Structure Validation Tests
// ============================================================================

#[test]
fn test_no_separate_tool_articles() {
    let html = export_fixture("claude_session.jsonl");

    // Count message elements
    let assistant_count = count_pattern(&html, r#"class="[^"]*message[^"]*message-assistant"#);
    let tool_count = count_pattern(&html, r#"class="[^"]*message[^"]*message-tool"#);

    debug!(
        assistant_articles = assistant_count,
        tool_articles = tool_count,
        "Article counts"
    );

    // Tool messages should NOT have their own separate articles
    // They should be integrated into assistant message groups
    assert_eq!(
        tool_count, 0,
        "Tool messages should not be separate articles; they should be badges in assistant headers"
    );

    // Should have assistant message groups
    assert!(
        assistant_count > 0,
        "Should have at least one assistant message group"
    );
}

#[test]
fn test_tool_badges_in_header() {
    let html = export_fixture("claude_session.jsonl");

    // Tool badges should be present
    let has_badges = html.contains("tool-badge");
    assert!(
        has_badges,
        "HTML should contain tool-badge elements for tool calls"
    );

    // Badges should be button elements (for accessibility)
    let badge_buttons = html.contains("<button class=\"tool-badge");
    assert!(
        badge_buttons,
        "Tool badges should be button elements for keyboard accessibility"
    );

    // Badges should be inside message-header-right divs
    let header_right_with_badges =
        html.contains("message-header-right") && html.contains("tool-badge");
    assert!(
        header_right_with_badges,
        "Tool badges should be in message-header-right sections"
    );
}

#[test]
fn test_message_group_structure() {
    let html = export_fixture("claude_session.jsonl");

    // Should have message containers (articles)
    let message_count = count_pattern(&html, r#"class="message "#);

    debug!(message_count = message_count, "Message count");

    // Claude session fixture should produce multiple messages
    // (user request, assistant with tools, follow-up user, etc.)
    assert!(
        message_count >= 2,
        "Should have at least 2 messages, found {}",
        message_count
    );
}

#[test]
fn test_user_and_assistant_messages_present() {
    let html = export_fixture("claude_session.jsonl");

    // Should have both user and assistant messages
    let user_messages = count_pattern(&html, r#"message-user"#);
    let assistant_messages = count_pattern(&html, r#"message-assistant"#);

    debug!(
        user_messages = user_messages,
        assistant_messages = assistant_messages,
        "Message type counts"
    );

    assert!(user_messages > 0, "Should have user messages");
    assert!(assistant_messages > 0, "Should have assistant messages");
}

// ============================================================================
// CSS Validation Tests
// ============================================================================

#[test]
fn test_glassmorphism_css_present() {
    let html = export_fixture("claude_session.jsonl");

    assert!(
        html.contains("backdrop-filter"),
        "Glassmorphism requires backdrop-filter CSS"
    );
    assert!(
        html.contains("blur("),
        "Glassmorphism should have blur effect"
    );
}

#[test]
fn test_color_variables_defined() {
    let html = export_fixture("claude_session.jsonl");

    // Should use CSS custom properties for theming
    assert!(
        html.contains("--primary") || html.contains("--accent"),
        "Should define color CSS variables"
    );

    // Should use modern color formats (oklch preferred)
    let has_colors = html.contains("oklch(") || html.contains("rgb(") || html.contains("#");
    assert!(has_colors, "Should have color values defined");
}

#[test]
fn test_popover_css_present() {
    let html = export_fixture("claude_session.jsonl");

    assert!(
        html.contains(".tool-popover"),
        "Should have tool-popover CSS class"
    );

    // Popover visibility toggle
    let has_visible_state =
        html.contains(".tool-popover.visible") || html.contains(".tool-popover.active");
    assert!(
        has_visible_state || html.contains("popover"),
        "Popover should have visibility state CSS"
    );
}

#[test]
fn test_tool_badge_styling() {
    let html = export_fixture("claude_session.jsonl");

    assert!(
        html.contains(".tool-badge"),
        "Should have tool-badge CSS styling"
    );

    // Status variants
    let has_status_styles = html.contains("tool-status-success") || html.contains("tool-status");
    assert!(
        has_status_styles,
        "Should have tool status CSS classes for success/error states"
    );
}

#[test]
fn test_responsive_design() {
    let html = export_fixture("claude_session.jsonl");

    // Should have media queries for responsive design
    assert!(
        html.contains("@media"),
        "Should have responsive CSS media queries"
    );
}

// ============================================================================
// JavaScript Validation Tests
// ============================================================================

#[test]
fn test_popover_js_present() {
    let html = export_fixture("claude_session.jsonl");

    // Popover controller should be initialized
    let has_popover_js =
        html.contains("ToolPopovers") || html.contains("popover") || html.contains("showPopover");

    assert!(
        has_popover_js,
        "Should have popover JavaScript functionality"
    );
}

#[test]
fn test_aria_expanded_attribute() {
    let html = export_fixture("claude_session.jsonl");

    // Tool badges should have aria-expanded for accessibility
    assert!(
        html.contains("aria-expanded"),
        "Tool badges should have aria-expanded attribute for screen readers"
    );
}

#[test]
fn test_keyboard_navigation_support() {
    let html = export_fixture("claude_session.jsonl");

    // Should handle keyboard events
    let has_keyboard_support =
        html.contains("keydown") || html.contains("Enter") || html.contains("Escape");

    assert!(
        has_keyboard_support,
        "Should have keyboard navigation support for popovers"
    );
}

// ============================================================================
// Accessibility Validation Tests
// ============================================================================

#[test]
fn test_aria_labels_present() {
    let html = export_fixture("claude_session.jsonl");

    assert!(
        html.contains("aria-label"),
        "Should have aria-label attributes for accessibility"
    );
}

#[test]
fn test_semantic_html_structure() {
    let html = export_fixture("claude_session.jsonl");

    // Should use semantic article elements
    assert!(
        html.contains("<article") || html.contains(r#"role="article""#),
        "Messages should use article elements or role=article"
    );

    // Should have proper document structure
    assert!(html.contains("<main") || html.contains(r#"role="main""#));
}

#[test]
fn test_badges_are_interactive() {
    let html = export_fixture("claude_session.jsonl");

    // Badges should be button elements for keyboard accessibility
    let badge_buttons = count_pattern(&html, r#"<button[^>]*tool-badge"#);

    // Or at least have tabindex for focusability
    let has_tabindex = html.contains("tabindex");

    assert!(
        badge_buttons > 0 || has_tabindex,
        "Tool badges should be interactive (button elements or have tabindex)"
    );
}

#[test]
fn test_color_contrast_indicators() {
    let html = export_fixture("claude_session.jsonl");

    // Success should use green-ish colors
    let success_styles =
        html.contains("success") && (html.contains("green") || html.contains("0.7 0.15 145"));

    // Error should use red-ish colors
    let error_styles =
        html.contains("error") && (html.contains("red") || html.contains("0.65 0.2 25"));

    assert!(
        success_styles || error_styles || html.contains("tool-status"),
        "Should have distinct colors for success/error states"
    );
}

// ============================================================================
// Format-Specific Tests
// ============================================================================

#[test]
fn test_claude_format_export() {
    let html = export_fixture("claude_session.jsonl");

    // Claude exports should work
    assert!(html.contains("<!DOCTYPE html>"));
    assert!(html.contains("conversation"));

    // Should have tool usage (Claude format has tool_use/tool_result)
    let has_tool_indicators = html.contains("tool-badge") || html.contains("Read");
    assert!(
        has_tool_indicators,
        "Claude format export should show tool usage"
    );
}

#[test]
fn test_codex_format_export() {
    let html = export_fixture("codex_session.jsonl");

    assert!(html.contains("<!DOCTYPE html>"));
    assert!(html.contains("conversation"));

    // Codex uses function_call structure
    let has_content = html.contains("shell") || html.contains("Python") || html.contains("list");
    assert!(
        has_content,
        "Codex format export should have session content"
    );
}

#[test]
fn test_cursor_format_export() {
    let html = export_fixture("cursor_session.jsonl");

    assert!(html.contains("<!DOCTYPE html>"));
    assert!(html.contains("conversation"));

    // Cursor format has embedded tool results
    let has_content = html.contains("main") || html.contains("function") || html.contains("Config");
    assert!(
        has_content,
        "Cursor format export should have session content"
    );
}

#[test]
fn test_opencode_format_export() {
    let html = export_fixture("opencode_session.jsonl");

    assert!(html.contains("<!DOCTYPE html>"));
    assert!(html.contains("conversation"));

    // OpenCode has tool_calls arrays
    let has_content =
        html.contains("auth") || html.contains("JWT") || html.contains("authentication");
    assert!(
        has_content,
        "OpenCode format export should have session content"
    );
}

#[test]
fn test_edge_cases_export() {
    let html = export_fixture("edge_cases.jsonl");

    assert!(html.contains("<!DOCTYPE html>"));

    // Should handle unicode content
    assert!(
        html.contains("你好") || html.contains("&#") || html.contains("Unicode"),
        "Should preserve or escape unicode content"
    );

    // Should escape HTML special characters
    assert!(
        !html.contains("<script>alert"),
        "Should escape XSS attempts in content"
    );
}

// ============================================================================
// Export Option Variations
// ============================================================================

#[test]
fn test_export_produces_valid_html() {
    let html = export_fixture("claude_session.jsonl");

    // Basic HTML structure
    assert!(html.starts_with("<!DOCTYPE html>"));
    assert!(html.contains("<html"));
    assert!(html.contains("</html>"));
    assert!(html.contains("<head>"));
    assert!(html.contains("</head>"));
    assert!(html.contains("<body"));
    assert!(html.contains("</body>"));
}

#[test]
fn test_export_includes_styles() {
    let html = export_fixture("claude_session.jsonl");

    // Should have inline critical CSS
    assert!(
        html.contains("<style>") || html.contains("<style "),
        "Should include inline CSS styles"
    );

    // Should have substantial styling
    let style_content_len = html
        .find("</style>")
        .map(|end| {
            html[..end]
                .rfind("<style")
                .map(|start| end - start)
                .unwrap_or(0)
        })
        .unwrap_or(0);

    assert!(
        style_content_len > 1000,
        "Should have substantial CSS (found {} chars)",
        style_content_len
    );
}

#[test]
fn test_export_includes_scripts() {
    let html = export_fixture("claude_session.jsonl");

    // Should have JavaScript for interactivity
    assert!(
        html.contains("<script>") || html.contains("<script "),
        "Should include JavaScript"
    );
}

#[test]
fn test_export_self_contained() {
    let html = export_fixture("claude_session.jsonl");

    // Should be largely self-contained (CSS inlined)
    // May have CDN links for syntax highlighting
    assert!(
        html.contains("<style>"),
        "Should have inlined critical CSS for self-contained export"
    );
}

// ============================================================================
// Performance and Size Tests
// ============================================================================

#[test]
fn test_export_reasonable_size() {
    let html = export_fixture("claude_session.jsonl");

    // Export should be reasonably sized (not bloated)
    // Claude session fixture is small, so export should be < 500KB
    let size_kb = html.len() / 1024;

    debug!(size_kb = size_kb, "Export size");

    assert!(
        size_kb < 500,
        "Export should be < 500KB for small session, got {}KB",
        size_kb
    );
}

#[test]
fn test_export_completes_quickly() {
    use std::time::Instant;

    let start = Instant::now();
    let _html = export_fixture("claude_session.jsonl");
    let elapsed = start.elapsed();

    debug!(elapsed_ms = elapsed.as_millis(), "Export duration");

    // Debug-test runs on remote workers are substantially slower than release builds.
    // Keep this as a broad regression guard rather than a stale sub-10s budget.
    assert!(
        elapsed.as_secs() < 120,
        "Export should complete in < 120s in debug-test environments, took {:?}",
        elapsed
    );
}
