use coding_agent_search::connectors::{NormalizedConversation, NormalizedMessage};
use coding_agent_search::search::query::{FieldMask, SearchClient, SearchFilters};
use coding_agent_search::search::tantivy::TantivyIndex;
use std::path::PathBuf;
use tempfile::TempDir;

/// Regression test for "NOT ... OR ..." boolean query semantics.
/// Ensures a query like `NOT apple OR orange` does not regress to `apple OR orange`.
#[test]
fn test_not_or_semantics_regression() -> anyhow::Result<()> {
    let dir = TempDir::new()?;
    let mut index = TantivyIndex::open_or_create(dir.path())?;

    // Doc 1: "apple" (Should match "apple OR orange", should NOT match "NOT apple OR orange"?)
    // "NOT apple OR orange" means "Anything except apple" OR "orange".
    // "apple" doc: "NOT apple" is false. "orange" is false. Result False.
    // If bug makes it "apple OR orange", Result True.
    let doc1 = NormalizedConversation {
        agent_slug: "test".into(),
        source_path: PathBuf::from("/doc1"),
        messages: vec![NormalizedMessage {
            idx: 0,
            role: "user".into(),
            content: "apple".into(),
            author: None,
            created_at: None,
            extra: serde_json::Value::Null,
            snippets: vec![],
            invocations: Vec::new(),
        }],
        external_id: None,
        title: None,
        workspace: None,
        started_at: None,
        ended_at: None,
        metadata: serde_json::Value::Null,
    };

    // Doc 2: "banana" (Should match "NOT apple OR orange")
    // "NOT apple" is true. Result True.
    // If bug makes it "apple OR orange", Result False.
    let doc2 = NormalizedConversation {
        agent_slug: "test".into(),
        source_path: PathBuf::from("/doc2"),
        messages: vec![NormalizedMessage {
            idx: 0,
            role: "user".into(),
            content: "banana".into(),
            author: None,
            created_at: None,
            extra: serde_json::Value::Null,
            snippets: vec![],
            invocations: Vec::new(),
        }],
        external_id: None,
        title: None,
        workspace: None,
        started_at: None,
        ended_at: None,
        metadata: serde_json::Value::Null,
    };

    index.add_conversation(&doc1)?;
    index.add_conversation(&doc2)?;
    index.commit()?;

    let client = SearchClient::open(dir.path(), None)?.expect("index");

    // Query: "NOT apple OR orange"
    // Expected:
    // - doc1 ("apple"): No match.
    // - doc2 ("banana"): Match.
    //
    // Actual (if bug exists: "apple OR orange"):
    // - doc1 ("apple"): Match.
    // - doc2 ("banana"): No match.

    let hits = client.search(
        "NOT apple OR orange",
        SearchFilters::default(),
        10,
        0,
        FieldMask::FULL,
    )?;

    let found_doc1 = hits.iter().any(|h| h.content.contains("apple"));
    let found_doc2 = hits.iter().any(|h| h.content.contains("banana"));

    println!("Found doc1 (apple): {}", found_doc1);
    println!("Found doc2 (banana): {}", found_doc2);

    assert!(
        !found_doc1,
        "'NOT apple OR orange' matched 'apple' (should be excluded)"
    );
    assert!(
        found_doc2,
        "'NOT apple OR orange' did not match 'banana' (should match via NOT apple)"
    );

    Ok(())
}
