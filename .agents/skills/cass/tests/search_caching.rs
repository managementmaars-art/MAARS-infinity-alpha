use coding_agent_search::search::query::{FieldMask, SearchClient, SearchFilters};
use coding_agent_search::search::tantivy::TantivyIndex;
use tempfile::TempDir;

mod util;

#[test]
fn search_client_caches_repeated_queries() {
    let dir = TempDir::new().unwrap();
    let mut index = TantivyIndex::open_or_create(dir.path()).unwrap();

    // Seed index
    let conv = util::ConversationFixtureBuilder::new("tester")
        .title("cache test")
        .source_path(dir.path().join("log.jsonl"))
        .base_ts(1000)
        .messages(1)
        .with_content(0, "unique_term_for_cache_test")
        .build_normalized();

    index.add_conversation(&conv).unwrap();
    index.commit().unwrap();

    let client = SearchClient::open(dir.path(), None)
        .unwrap()
        .expect("client");
    let filters = SearchFilters::default();

    // First search: Miss
    let hits1 = client
        .search("unique_term", filters.clone(), 1, 0, FieldMask::FULL)
        .unwrap();
    assert_eq!(hits1.len(), 1);

    let stats1 = client.cache_stats();
    assert_eq!(stats1.cache_hits, 0);
    // We expect a miss (and maybe a shortfall if it was partial, but here it's full search)
    // Actually, for prefix "unique_term", if we typed it...
    // The client.search() logic checks cache for "unique_term" first. It's empty. Miss.
    // Then it runs Tantivy. Then it puts result in cache.

    // Second search: Hit
    // We use limit 1 so the single cached result satisfies the requirement
    let hits2 = client
        .search("unique_term", filters.clone(), 1, 0, FieldMask::FULL)
        .unwrap();
    assert_eq!(hits2.len(), 1);

    let stats2 = client.cache_stats();
    assert!(
        stats2.cache_hits >= 1,
        "Should have at least 1 cache hit (stats: {stats2:?})"
    );
}

#[test]
fn search_client_prefix_cache_works() {
    let dir = TempDir::new().unwrap();
    let mut index = TantivyIndex::open_or_create(dir.path()).unwrap();

    let conv = util::ConversationFixtureBuilder::new("tester")
        .title("prefix test")
        .source_path(dir.path().join("log.jsonl"))
        .base_ts(1000)
        .messages(1)
        .with_content(0, "apple banana cherry")
        .build_normalized();

    index.add_conversation(&conv).unwrap();
    index.commit().unwrap();

    let client = SearchClient::open(dir.path(), None)
        .unwrap()
        .expect("client");
    let filters = SearchFilters::default();

    // Search "app": populates cache for "app". Use limit 1.
    let hits_app = client
        .search("app", filters.clone(), 1, 0, FieldMask::FULL)
        .unwrap();
    assert_eq!(hits_app.len(), 1);

    // Search "appl": should hit cache for "app" via prefix matching logic.
    // Use limit 1 to be satisfied by the single cached hit.
    let hits_appl = client
        .search("appl", filters.clone(), 1, 0, FieldMask::FULL)
        .unwrap();
    assert_eq!(hits_appl.len(), 1);

    let stats = client.cache_stats();
    // Depending on implementation details, this might be a hit or a shortfall if the cache logic
    // is strictly checking >= limit.
    assert!(
        stats.cache_hits > 0,
        "Should hit cache for 'appl' using 'app' entry (stats: {stats:?})"
    );
}
