//! FTS5 Query Utilities for Pages Export
//!
//! Provides query escaping and formatting for safe FTS5 search queries
//! in the exported SQLite database. Supports both natural language (porter)
//! and code-aware (unicode61) search modes.

/// Escape a query string for safe use with FTS5 MATCH.
///
/// FTS5 has special characters that must be escaped to prevent injection
/// or syntax errors. This function wraps each term in double-quotes,
/// escaping any internal double-quotes by doubling them.
///
/// # Examples
///
/// ```
/// use coding_agent_search::pages::fts::escape_fts5_query;
///
/// // Simple query
/// assert_eq!(escape_fts5_query("hello world"), r#""hello" "world""#);
///
/// // Query with special characters
/// assert_eq!(escape_fts5_query("foo\"bar"), r#""foo""bar""#);
///
/// // Code-like query
/// assert_eq!(escape_fts5_query("my_function"), r#""my_function""#);
/// ```
pub fn escape_fts5_query(query: &str) -> String {
    query
        .split_whitespace()
        .filter(|t| !t.is_empty())
        .map(|t| format!("\"{}\"", t.replace('"', "\"\"")))
        .collect::<Vec<_>>()
        .join(" ")
}

/// Query mode for FTS5 search routing
#[derive(Debug, Clone, Copy, Default, PartialEq, Eq)]
pub enum Fts5SearchMode {
    /// Natural language search using porter stemmer (messages_fts)
    /// Good for: English prose, documentation, explanations
    NaturalLanguage,
    /// Code-aware search using unicode61 with special tokenchars (messages_code_fts)
    /// Good for: identifiers, file paths, snake_case, camelCase
    Code,
    /// Automatic detection based on query content
    #[default]
    Auto,
}

/// Detect the appropriate search mode based on query content.
///
/// Returns `Code` mode if the query contains:
/// - Underscores (snake_case identifiers)
/// - Dots (file extensions, method calls)
/// - camelCase patterns (lowercase followed by uppercase)
/// - File path separators
/// - Colons (namespaces, type annotations)
/// - Hashes (CSS selectors, preprocessor directives)
/// - At-signs (decorators, email-like patterns)
/// - Dollar signs (variables in shell/PHP)
/// - Percent signs (URL encoding, format specifiers)
/// - Hyphens between letters (kebab-case)
///
/// Uses prose indicators to avoid false positives:
/// - Question words (how, what, why, when, where)
/// - Common articles (the, is, are, was, were)
/// - Multiple space-separated words (>3 words)
///
/// Otherwise returns `NaturalLanguage` mode.
///
/// # Examples
///
/// ```
/// use coding_agent_search::pages::fts::{detect_search_mode, Fts5SearchMode};
///
/// assert_eq!(detect_search_mode("hello world"), Fts5SearchMode::NaturalLanguage);
/// assert_eq!(detect_search_mode("my_function"), Fts5SearchMode::Code);
/// assert_eq!(detect_search_mode("AuthController.ts"), Fts5SearchMode::Code);
/// assert_eq!(detect_search_mode("getUserById"), Fts5SearchMode::Code);
/// assert_eq!(detect_search_mode("std::io::Result"), Fts5SearchMode::Code);
/// assert_eq!(detect_search_mode("my-component"), Fts5SearchMode::Code);
/// assert_eq!(detect_search_mode("how does auth work"), Fts5SearchMode::NaturalLanguage);
/// ```
pub fn detect_search_mode(query: &str) -> Fts5SearchMode {
    // Check for code-like patterns
    let has_code_chars = query.contains('_')
        || query.contains('.')
        || query.contains('/')
        || query.contains('\\')
        || query.contains("::")
        || query.contains('#')
        || query.contains('@')
        || query.contains('$')
        || query.contains('%');

    let has_code_patterns = has_camel_case(query) || has_kebab_case(query);

    let is_code_query = has_code_chars || has_code_patterns;

    // Check for prose indicators (to avoid false positives)
    let words: Vec<&str> = query.split_whitespace().collect();
    let word_count = words.len();
    let lower = query.to_lowercase();

    let has_prose_indicators = word_count > 3
        || lower.starts_with("how ")
        || lower.starts_with("what ")
        || lower.starts_with("why ")
        || lower.starts_with("when ")
        || lower.starts_with("where ")
        || lower.contains(" the ")
        || lower.contains(" is ")
        || lower.contains(" are ")
        || lower.contains(" was ")
        || lower.contains(" were ");

    // Code patterns win unless prose indicators are strong
    if is_code_query && !has_prose_indicators {
        Fts5SearchMode::Code
    } else if has_prose_indicators && !is_code_query {
        Fts5SearchMode::NaturalLanguage
    } else if is_code_query {
        // Both indicators present - code chars are more specific
        Fts5SearchMode::Code
    } else {
        Fts5SearchMode::NaturalLanguage
    }
}

/// Check if string contains kebab-case pattern (letter-hyphen-letter).
fn has_kebab_case(s: &str) -> bool {
    let chars: Vec<char> = s.chars().collect();
    for i in 2..chars.len() {
        if chars[i - 1] == '-' && chars[i - 2].is_alphabetic() && chars[i].is_alphabetic() {
            return true;
        }
    }
    false
}

/// Check if string contains camelCase pattern (lowercase followed by uppercase).
fn has_camel_case(s: &str) -> bool {
    let chars: Vec<char> = s.chars().collect();
    for i in 1..chars.len() {
        if chars[i - 1].is_lowercase() && chars[i].is_uppercase() {
            return true;
        }
    }
    false
}

/// Format a query for the appropriate FTS5 table based on mode.
///
/// Returns a tuple of (table_name, escaped_query).
///
/// # Examples
///
/// ```
/// use coding_agent_search::pages::fts::{format_fts5_query, Fts5SearchMode};
///
/// let (table, query) = format_fts5_query("error handling", Fts5SearchMode::NaturalLanguage);
/// assert_eq!(table, "messages_fts");
///
/// let (table, query) = format_fts5_query("my_function", Fts5SearchMode::Code);
/// assert_eq!(table, "messages_code_fts");
/// ```
pub fn format_fts5_query(query: &str, mode: Fts5SearchMode) -> (&'static str, String) {
    let actual_mode = match mode {
        Fts5SearchMode::Auto => detect_search_mode(query),
        other => other,
    };

    let table = match actual_mode {
        Fts5SearchMode::NaturalLanguage | Fts5SearchMode::Auto => "messages_fts",
        Fts5SearchMode::Code => "messages_code_fts",
    };

    (table, escape_fts5_query(query))
}

/// Build a complete FTS5 search SQL query.
///
/// Generates a SELECT statement with JOIN to messages and conversations tables,
/// including BM25 ranking, snippets, and optional agent filtering.
///
/// # Arguments
///
/// * `fts_table` - The FTS5 table name ("messages_fts" or "messages_code_fts")
/// * `snippet_length` - Maximum snippet length (passed to FTS5 snippet())
/// * `with_agent_filter` - Whether to include agent filter placeholder
///
/// # Example SQL Generated
///
/// ```sql
/// SELECT
///     m.conversation_id,
///     m.id as message_id,
///     m.role,
///     snippet(messages_fts, 0, '<mark>', '</mark>', '...', 64) as snippet,
///     c.agent,
///     c.workspace,
///     c.title,
///     c.started_at,
///     bm25(messages_fts) as score
/// FROM messages_fts
/// JOIN messages m ON messages_fts.rowid = m.id
/// JOIN conversations c ON m.conversation_id = c.id
/// WHERE messages_fts MATCH ?
/// ORDER BY score
/// LIMIT ? OFFSET ?
/// ```
pub fn build_fts5_search_sql(
    fts_table: &str,
    snippet_length: u32,
    with_agent_filter: bool,
) -> String {
    let mut sql = format!(
        r#"SELECT
    m.conversation_id,
    m.id as message_id,
    m.role,
    snippet({fts_table}, 0, '<mark>', '</mark>', '...', {snippet_length}) as snippet,
    c.agent,
    c.workspace,
    c.title,
    c.started_at,
    bm25({fts_table}) as score
FROM {fts_table}
JOIN messages m ON {fts_table}.rowid = m.id
JOIN conversations c ON m.conversation_id = c.id
WHERE {fts_table} MATCH ?"#
    );

    if with_agent_filter {
        sql.push_str("\n    AND c.agent = ?");
    }

    sql.push_str("\nORDER BY score\nLIMIT ? OFFSET ?");

    sql
}

/// Validate that a query is safe and non-empty for FTS5.
///
/// Returns `None` if the query is empty or contains only whitespace.
/// Returns `Some(cleaned_query)` with trimmed whitespace otherwise.
///
/// # Examples
///
/// ```
/// use coding_agent_search::pages::fts::validate_fts5_query;
///
/// assert_eq!(validate_fts5_query("  hello  "), Some("hello".to_string()));
/// assert_eq!(validate_fts5_query("   "), None);
/// assert_eq!(validate_fts5_query(""), None);
/// ```
pub fn validate_fts5_query(query: &str) -> Option<String> {
    let trimmed = query.trim();
    if trimmed.is_empty() {
        None
    } else {
        Some(trimmed.to_string())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_escape_fts5_query_simple() {
        assert_eq!(escape_fts5_query("hello"), r#""hello""#);
        assert_eq!(escape_fts5_query("hello world"), r#""hello" "world""#);
    }

    #[test]
    fn test_escape_fts5_query_with_quotes() {
        // Internal quotes are doubled
        // Input: foo"bar → Output: "foo""bar" (quote doubled, then wrapped)
        assert_eq!(escape_fts5_query(r#"foo"bar"#), r#""foo""bar""#);
        // Input: say "hello" → Output: "say" """hello"""
        // The token "hello" has quotes at both ends, each doubled = ""hello""
        // Then wrapped in outer quotes = """hello"""
        assert_eq!(
            escape_fts5_query("say \"hello\""),
            "\"say\" \"\"\"hello\"\"\""
        );
    }

    #[test]
    fn test_escape_fts5_query_special_chars() {
        // FTS5 operators should be safely quoted
        assert_eq!(escape_fts5_query("foo*"), r#""foo*""#);
        assert_eq!(escape_fts5_query("foo+bar"), r#""foo+bar""#);
        assert_eq!(escape_fts5_query("foo-bar"), r#""foo-bar""#);
        assert_eq!(escape_fts5_query("foo:bar"), r#""foo:bar""#);
        assert_eq!(escape_fts5_query("(foo)"), r#""(foo)""#);
    }

    #[test]
    fn test_escape_fts5_query_empty() {
        assert_eq!(escape_fts5_query(""), "");
        assert_eq!(escape_fts5_query("   "), "");
    }

    #[test]
    fn test_escape_fts5_query_code_identifiers() {
        assert_eq!(escape_fts5_query("my_function"), r#""my_function""#);
        assert_eq!(
            escape_fts5_query("AuthController.ts"),
            r#""AuthController.ts""#
        );
        assert_eq!(escape_fts5_query("src/lib.rs"), r#""src/lib.rs""#);
    }

    #[test]
    fn test_detect_search_mode_natural() {
        assert_eq!(detect_search_mode("hello"), Fts5SearchMode::NaturalLanguage);
        assert_eq!(
            detect_search_mode("error handling"),
            Fts5SearchMode::NaturalLanguage
        );
        assert_eq!(
            detect_search_mode("running test"),
            Fts5SearchMode::NaturalLanguage
        );
    }

    #[test]
    fn test_detect_search_mode_code_underscore() {
        assert_eq!(detect_search_mode("my_function"), Fts5SearchMode::Code);
        assert_eq!(detect_search_mode("get_user_by_id"), Fts5SearchMode::Code);
    }

    #[test]
    fn test_detect_search_mode_code_dot() {
        assert_eq!(
            detect_search_mode("AuthController.ts"),
            Fts5SearchMode::Code
        );
        assert_eq!(detect_search_mode("file.rs"), Fts5SearchMode::Code);
    }

    #[test]
    fn test_detect_search_mode_code_camelcase() {
        assert_eq!(detect_search_mode("getUserById"), Fts5SearchMode::Code);
        assert_eq!(detect_search_mode("AuthController"), Fts5SearchMode::Code);
    }

    #[test]
    fn test_detect_search_mode_code_path() {
        assert_eq!(detect_search_mode("src/lib.rs"), Fts5SearchMode::Code);
        assert_eq!(detect_search_mode("path\\to\\file"), Fts5SearchMode::Code);
    }

    #[test]
    fn test_detect_search_mode_code_namespace() {
        assert_eq!(detect_search_mode("std::io::Result"), Fts5SearchMode::Code);
        assert_eq!(detect_search_mode("Vec::new()"), Fts5SearchMode::Code);
    }

    #[test]
    fn test_detect_search_mode_code_kebab() {
        assert_eq!(detect_search_mode("my-component"), Fts5SearchMode::Code);
        assert_eq!(detect_search_mode("button-primary"), Fts5SearchMode::Code);
    }

    #[test]
    fn test_detect_search_mode_code_special_chars() {
        assert_eq!(detect_search_mode("#define"), Fts5SearchMode::Code);
        assert_eq!(detect_search_mode("@decorator"), Fts5SearchMode::Code);
        assert_eq!(detect_search_mode("$variable"), Fts5SearchMode::Code);
        assert_eq!(detect_search_mode("%s"), Fts5SearchMode::Code);
    }

    #[test]
    fn test_detect_search_mode_prose_questions() {
        assert_eq!(
            detect_search_mode("how does auth work"),
            Fts5SearchMode::NaturalLanguage
        );
        assert_eq!(
            detect_search_mode("what is the error"),
            Fts5SearchMode::NaturalLanguage
        );
        assert_eq!(
            detect_search_mode("why is it failing"),
            Fts5SearchMode::NaturalLanguage
        );
    }

    #[test]
    fn test_detect_search_mode_prose_multiword() {
        assert_eq!(
            detect_search_mode("the quick brown fox jumps"),
            Fts5SearchMode::NaturalLanguage
        );
    }

    #[test]
    fn test_has_kebab_case() {
        assert!(has_kebab_case("my-component"));
        assert!(has_kebab_case("button-primary"));
        assert!(has_kebab_case("a-b"));
        assert!(!has_kebab_case("hello"));
        assert!(!has_kebab_case("-start"));
        assert!(!has_kebab_case("end-"));
        assert!(!has_kebab_case("1-2"));
    }

    #[test]
    fn test_format_fts5_query_auto() {
        let (table, _) = format_fts5_query("hello world", Fts5SearchMode::Auto);
        assert_eq!(table, "messages_fts");

        let (table, _) = format_fts5_query("my_function", Fts5SearchMode::Auto);
        assert_eq!(table, "messages_code_fts");
    }

    #[test]
    fn test_format_fts5_query_explicit() {
        let (table, query) = format_fts5_query("running", Fts5SearchMode::NaturalLanguage);
        assert_eq!(table, "messages_fts");
        assert_eq!(query, r#""running""#);

        let (table, query) = format_fts5_query("running", Fts5SearchMode::Code);
        assert_eq!(table, "messages_code_fts");
        assert_eq!(query, r#""running""#);
    }

    #[test]
    fn test_build_fts5_search_sql() {
        let sql = build_fts5_search_sql("messages_fts", 64, false);
        assert!(sql.contains("FROM messages_fts"));
        assert!(sql.contains("snippet(messages_fts"));
        assert!(sql.contains("bm25(messages_fts)"));
        assert!(sql.contains("WHERE messages_fts MATCH ?"));
        assert!(!sql.contains("AND c.agent = ?"));

        let sql_with_agent = build_fts5_search_sql("messages_code_fts", 32, true);
        assert!(sql_with_agent.contains("FROM messages_code_fts"));
        assert!(sql_with_agent.contains("AND c.agent = ?"));
    }

    #[test]
    fn test_validate_fts5_query() {
        assert_eq!(validate_fts5_query("hello"), Some("hello".to_string()));
        assert_eq!(validate_fts5_query("  hello  "), Some("hello".to_string()));
        assert_eq!(validate_fts5_query(""), None);
        assert_eq!(validate_fts5_query("   "), None);
        assert_eq!(validate_fts5_query("\t\n"), None);
    }

    #[test]
    fn test_has_camel_case() {
        assert!(has_camel_case("getUserById"));
        assert!(has_camel_case("AuthController"));
        assert!(has_camel_case("aB"));
        assert!(!has_camel_case("hello"));
        assert!(!has_camel_case("HELLO"));
        assert!(!has_camel_case("hello_world"));
        assert!(!has_camel_case(""));
    }
}
