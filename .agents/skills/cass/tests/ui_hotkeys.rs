//! Hotkey / shortcut integration tests.
//!
//! Tests that depended on the removed `footer_legend()` / `help_lines()`
//! functions have been removed.  Equivalent coverage now lives in the
//! ftui-based `CassApp` tests in `src/ui/app.rs`.

use coding_agent_search::sources::provenance::SourceFilter;

#[test]
fn source_filter_cycle_api_exists() {
    // Verify the cycle() method exists and behaves correctly
    // This tests the same API the TUI uses for F11 handling
    let filter = SourceFilter::All;
    let cycled = filter.cycle();
    assert_eq!(cycled, SourceFilter::Local, "All should cycle to Local");
}

#[test]
fn source_filter_display_for_status_messages() {
    // The TUI shows status like "Source: all sources", "Source: local only"
    // Verify SourceFilter::to_string() produces expected values for status display
    assert_eq!(SourceFilter::All.to_string(), "all");
    assert_eq!(SourceFilter::Local.to_string(), "local");
    assert_eq!(SourceFilter::Remote.to_string(), "remote");
    assert_eq!(
        SourceFilter::SourceId("laptop".to_string()).to_string(),
        "laptop"
    );
}
