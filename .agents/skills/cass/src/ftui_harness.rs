//! Lightweight in-repo FTUI test harness.
//!
//! This shim replaces the external `ftui-harness` dev-dependency so the cass
//! repo no longer pulls legacy crossterm compatibility into its test graph.

use std::fmt::Write as _;
use std::path::{Path, PathBuf};

use ftui::render::buffer::Buffer;
use ftui::render::cell::{PackedRgba, StyleFlags};

/// Comparison mode for snapshot testing.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum MatchMode {
    /// Byte-exact string comparison.
    Exact,
    /// Trim trailing whitespace on each line before comparing.
    TrimTrailing,
    /// Collapse all whitespace runs to single spaces and trim each line.
    Fuzzy,
}

/// Convert a render buffer to plain text.
pub fn buffer_to_text(buf: &Buffer) -> String {
    let capacity = (buf.width() as usize + 1) * buf.height() as usize;
    let mut out = String::with_capacity(capacity);

    for y in 0..buf.height() {
        if y > 0 {
            out.push('\n');
        }
        for x in 0..buf.width() {
            let cell = buf.get(x, y).expect("buffer coordinate should be valid");
            if cell.is_continuation() {
                continue;
            }
            if cell.is_empty() {
                out.push(' ');
            } else if let Some(c) = cell.content.as_char() {
                out.push(c);
            } else {
                let w = cell.content.width();
                for _ in 0..w.max(1) {
                    out.push('?');
                }
            }
        }
    }
    out
}

fn buffer_to_ansi(buf: &Buffer) -> String {
    let capacity = (buf.width() as usize + 32) * buf.height() as usize;
    let mut out = String::with_capacity(capacity);

    for y in 0..buf.height() {
        if y > 0 {
            out.push('\n');
        }

        let mut prev_fg = PackedRgba::WHITE;
        let mut prev_bg = PackedRgba::TRANSPARENT;
        let mut prev_flags = StyleFlags::empty();
        let mut style_active = false;

        for x in 0..buf.width() {
            let cell = buf.get(x, y).expect("buffer coordinate should be valid");
            if cell.is_continuation() {
                continue;
            }

            let fg = cell.fg;
            let bg = cell.bg;
            let flags = cell.attrs.flags();
            let style_changed = fg != prev_fg || bg != prev_bg || flags != prev_flags;

            if style_changed {
                let has_style =
                    fg != PackedRgba::WHITE || bg != PackedRgba::TRANSPARENT || !flags.is_empty();

                if has_style {
                    if style_active {
                        out.push_str("\x1b[0m");
                    }

                    let mut params: Vec<String> = Vec::new();
                    if !flags.is_empty() {
                        if flags.contains(StyleFlags::BOLD) {
                            params.push("1".into());
                        }
                        if flags.contains(StyleFlags::DIM) {
                            params.push("2".into());
                        }
                        if flags.contains(StyleFlags::ITALIC) {
                            params.push("3".into());
                        }
                        if flags.contains(StyleFlags::UNDERLINE) {
                            params.push("4".into());
                        }
                        if flags.contains(StyleFlags::BLINK) {
                            params.push("5".into());
                        }
                        if flags.contains(StyleFlags::REVERSE) {
                            params.push("7".into());
                        }
                        if flags.contains(StyleFlags::HIDDEN) {
                            params.push("8".into());
                        }
                        if flags.contains(StyleFlags::STRIKETHROUGH) {
                            params.push("9".into());
                        }
                    }
                    if fg.a() > 0 && fg != PackedRgba::WHITE {
                        params.push(format!("38;2;{};{};{}", fg.r(), fg.g(), fg.b()));
                    }
                    if bg.a() > 0 && bg != PackedRgba::TRANSPARENT {
                        params.push(format!("48;2;{};{};{}", bg.r(), bg.g(), bg.b()));
                    }

                    if !params.is_empty() {
                        write!(out, "\x1b[{}m", params.join(";")).expect("write to String");
                        style_active = true;
                    }
                } else if style_active {
                    out.push_str("\x1b[0m");
                    style_active = false;
                }

                prev_fg = fg;
                prev_bg = bg;
                prev_flags = flags;
            }

            if cell.is_empty() {
                out.push(' ');
            } else if let Some(c) = cell.content.as_char() {
                out.push(c);
            } else {
                let w = cell.content.width();
                for _ in 0..w.max(1) {
                    out.push('?');
                }
            }
        }

        if style_active {
            out.push_str("\x1b[0m");
        }
    }
    out
}

fn normalize(text: &str, mode: MatchMode) -> String {
    match mode {
        MatchMode::Exact => text.to_string(),
        MatchMode::TrimTrailing => text
            .lines()
            .map(str::trim_end)
            .collect::<Vec<_>>()
            .join("\n"),
        MatchMode::Fuzzy => text
            .lines()
            .map(|line| line.split_whitespace().collect::<Vec<_>>().join(" "))
            .collect::<Vec<_>>()
            .join("\n"),
    }
}

/// Compute a simple line-by-line diff between two text strings.
pub fn diff_text(expected: &str, actual: &str) -> String {
    let expected_lines: Vec<&str> = expected.lines().collect();
    let actual_lines: Vec<&str> = actual.lines().collect();
    let max_lines = expected_lines.len().max(actual_lines.len());
    let mut out = String::new();
    let mut has_diff = false;

    for i in 0..max_lines {
        let exp = expected_lines.get(i).copied();
        let act = actual_lines.get(i).copied();
        match (exp, act) {
            (Some(e), Some(a)) if e == a => {
                writeln!(out, " {e}").expect("write to String");
            }
            (Some(e), Some(a)) => {
                writeln!(out, "-{e}").expect("write to String");
                writeln!(out, "+{a}").expect("write to String");
                has_diff = true;
            }
            (Some(e), None) => {
                writeln!(out, "-{e}").expect("write to String");
                has_diff = true;
            }
            (None, Some(a)) => {
                writeln!(out, "+{a}").expect("write to String");
                has_diff = true;
            }
            (None, None) => {}
        }
    }

    if has_diff { out } else { String::new() }
}

fn snapshot_name_with_profile(name: &str) -> String {
    let profile = std::env::var("FTUI_TEST_PROFILE").ok();
    if let Some(profile) = profile {
        let profile = profile.trim();
        if !profile.is_empty() && !profile.eq_ignore_ascii_case("detected") {
            let suffix = format!("__{profile}");
            if name.ends_with(&suffix) {
                return name.to_string();
            }
            return format!("{name}{suffix}");
        }
    }
    name.to_string()
}

fn snapshot_path(base_dir: &Path, name: &str) -> PathBuf {
    let resolved_name = snapshot_name_with_profile(name);
    base_dir
        .join("tests")
        .join("snapshots")
        .join(format!("{resolved_name}.snap"))
}

fn is_bless() -> bool {
    std::env::var("BLESS")
        .map(|v| v == "1" || v.eq_ignore_ascii_case("true"))
        .unwrap_or(false)
}

/// Assert that a buffer's text representation matches a stored snapshot.
pub fn assert_buffer_snapshot(name: &str, buf: &Buffer, base_dir: &str, mode: MatchMode) {
    let base = Path::new(base_dir);
    let path = snapshot_path(base, name);
    let actual = buffer_to_text(buf);

    if is_bless() {
        if let Some(parent) = path.parent() {
            std::fs::create_dir_all(parent).expect("failed to create snapshot directory");
        }
        std::fs::write(&path, &actual).expect("failed to write snapshot");
        return;
    }

    match std::fs::read_to_string(&path) {
        Ok(expected) => {
            let norm_expected = normalize(&expected, mode);
            let norm_actual = normalize(&actual, mode);
            if norm_expected != norm_actual {
                let diff = diff_text(&norm_expected, &norm_actual);
                panic!(
                    "\n=== Snapshot mismatch: '{name}' ===\nFile: {}\nMode: {mode:?}\nSet BLESS=1 to update.\n\nDiff (- expected, + actual):\n{diff}",
                    path.display()
                );
            }
        }
        Err(e) if e.kind() == std::io::ErrorKind::NotFound => {
            panic!(
                "\n=== No snapshot found: '{name}' ===\nExpected at: {}\nRun with BLESS=1 to create it.\n\nActual output ({w}x{h}):\n{actual}",
                path.display(),
                w = buf.width(),
                h = buf.height(),
            );
        }
        Err(e) => {
            panic!("Failed to read snapshot '{}': {e}", path.display());
        }
    }
}

/// Assert that a buffer's ANSI-styled representation matches a stored snapshot.
pub fn assert_buffer_snapshot_ansi(name: &str, buf: &Buffer, base_dir: &str) {
    let base = Path::new(base_dir);
    let resolved_name = snapshot_name_with_profile(name);
    let path = base
        .join("tests")
        .join("snapshots")
        .join(format!("{resolved_name}.ansi.snap"));
    let actual = buffer_to_ansi(buf);

    if is_bless() {
        if let Some(parent) = path.parent() {
            std::fs::create_dir_all(parent).expect("failed to create snapshot directory");
        }
        std::fs::write(&path, &actual).expect("failed to write snapshot");
        return;
    }

    match std::fs::read_to_string(&path) {
        Ok(expected) => {
            if expected != actual {
                let diff = diff_text(&expected, &actual);
                panic!(
                    "\n=== ANSI snapshot mismatch: '{name}' ===\nFile: {}\nSet BLESS=1 to update.\n\nDiff (- expected, + actual):\n{diff}",
                    path.display()
                );
            }
        }
        Err(e) if e.kind() == std::io::ErrorKind::NotFound => {
            panic!(
                "\n=== No ANSI snapshot found: '{resolved_name}' ===\nExpected at: {}\nRun with BLESS=1 to create it.\n\nActual output:\n{actual}",
                path.display(),
            );
        }
        Err(e) => {
            panic!("Failed to read snapshot '{}': {e}", path.display());
        }
    }
}
