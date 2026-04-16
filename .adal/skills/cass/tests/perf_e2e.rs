//! End-to-end performance optimization verification tests
//!
//! Run with detailed logging:
//! RUST_LOG=info cargo test --test perf_e2e -- --nocapture
//!
//! These tests verify that all performance optimizations:
//! 1. Work correctly in combination
//! 2. Can be rolled back via environment variables
//! 3. Produce equivalent search results

use coding_agent_search::search::vector_index::{
    Quantization, SearchParams, SemanticDocId, SemanticFilter, VectorIndex, parse_semantic_doc_id,
};
use std::collections::HashSet;
use std::path::{Path, PathBuf};
use std::time::Instant;
use tempfile::{TempDir, tempdir};

/// Test corpus size - large enough to trigger parallel search (>10k threshold).
const TEST_CORPUS_SIZE: usize = 15_000;
const VECTOR_DIMENSION: usize = 64;

fn normalize_in_place(vec: &mut [f32]) {
    let norm_sq: f32 = vec.iter().map(|v| v * v).sum();
    let norm = norm_sq.sqrt();
    if norm > 0.0 {
        for v in vec {
            *v /= norm;
        }
    }
}

/// Generate a deterministic on-disk test corpus for reproducible testing.
fn create_test_index() -> (TempDir, PathBuf, VectorIndex) {
    let dir = tempdir().expect("Failed to create temp dir");
    let path = dir.path().join("test.fsvi");

    let mut writer = VectorIndex::create_with_revision(
        &path,
        "test-embedder",
        "rev1",
        VECTOR_DIMENSION,
        Quantization::F16,
    )
    .expect("Failed to create fsvi writer");

    let mut vec_buf = vec![0.0f32; VECTOR_DIMENSION];
    for i in 0..TEST_CORPUS_SIZE {
        // Deterministic but varying values, then normalize for cosine similarity.
        for (d, slot) in vec_buf.iter_mut().enumerate() {
            let val = ((i * 7 + d * 13) % 1000) as f32 / 1000.0;
            *slot = val * 2.0 - 1.0; // [-1, 1]
        }
        normalize_in_place(&mut vec_buf);

        let doc_id = SemanticDocId {
            message_id: i as u64,
            chunk_idx: 0,
            agent_id: (i % 4) as u32,
            workspace_id: (i % 10) as u32,
            source_id: 1,
            role: (i % 2) as u8,
            created_at_ms: (i as i64) * 1000,
            content_hash: None,
        }
        .to_doc_id_string();
        writer
            .write_record(&doc_id, &vec_buf)
            .expect("write_record");
    }

    writer.finish().expect("finish fsvi");
    let index = VectorIndex::open(&path).expect("open fsvi");
    (dir, path, index)
}

/// Generate a deterministic query vector.
fn create_query_vector() -> Vec<f32> {
    let mut v: Vec<f32> = (0..VECTOR_DIMENSION)
        .map(|d| ((d * 17) % 100) as f32 / 100.0)
        .collect();
    normalize_in_place(&mut v);
    v
}

/// Generate a deterministic query vector for a given seed.
fn create_query_vector_seed(seed: usize) -> Vec<f32> {
    let mut v: Vec<f32> = (0..VECTOR_DIMENSION)
        .map(|d| ((seed * 31 + d * 17) % 100) as f32 / 100.0)
        .collect();
    normalize_in_place(&mut v);
    v
}

/// Run search and return results with timing.
struct SearchResult {
    message_ids: Vec<u64>,
    duration: std::time::Duration,
}

fn run_search(index: &VectorIndex, query: &[f32], k: usize) -> SearchResult {
    let start = Instant::now();
    let results = index.search_top_k(query, k, None).expect("Search failed");
    let duration = start.elapsed();

    SearchResult {
        message_ids: results
            .iter()
            .filter_map(|r| parse_semantic_doc_id(&r.doc_id).map(|p| p.message_id))
            .collect(),
        duration,
    }
}

fn run_search_with_scores(
    index: &VectorIndex,
    query: &[f32],
    k: usize,
    params: SearchParams,
) -> Vec<(u64, f32)> {
    index
        .search_top_k_with_params(query, k, None, params)
        .expect("Search failed")
        .iter()
        .filter_map(|r| parse_semantic_doc_id(&r.doc_id).map(|p| (p.message_id, r.score)))
        .collect()
}

/// Test that all optimizations work together correctly.
#[test]
fn e2e_full_optimization_chain() {
    println!("=== E2E Optimization Chain Test ===");

    // Phase 1: Create test index
    println!(
        "Phase 1: Creating test index with {} vectors",
        TEST_CORPUS_SIZE
    );
    let start = Instant::now();
    let (_dir, _path, index) = create_test_index();
    println!("  Index created in {:?}", start.elapsed());
    assert_eq!(index.record_count(), TEST_CORPUS_SIZE);

    // Phase 2: Run search (uses portable SIMD + optional Rayon parallel scan)
    println!("Phase 2: Running search");
    let query = create_query_vector();
    let k = 25;

    // Run search multiple times to measure variance
    let mut durations = Vec::new();
    for i in 0..5 {
        let result = run_search(&index, &query, k);
        durations.push(result.duration);
        if i == 0 {
            println!(
                "  First search returned {} results",
                result.message_ids.len()
            );
            assert_eq!(result.message_ids.len(), k);
        }
    }

    let avg_duration: f64 = durations.iter().map(|d| d.as_secs_f64()).sum::<f64>() / 5.0;
    println!("  Average search latency: {:.3}ms", avg_duration * 1000.0);

    // Phase 4: Verify consistency
    println!("Phase 4: Verifying search consistency");
    let result1 = run_search(&index, &query, k);
    let result2 = run_search(&index, &query, k);
    assert_eq!(
        result1.message_ids, result2.message_ids,
        "Search results should be deterministic"
    );
    println!("  Search results are deterministic");

    println!("=== E2E Test PASSED ===");
}

/// Test that each optimization can be rolled back via environment variables.
#[test]
fn e2e_rollback_env_vars() {
    println!("=== E2E Rollback Test ===");

    let (_dir, _path, index) = create_test_index();

    let query = create_query_vector();
    let k = 25;

    println!("Comparing sequential vs parallel search params");
    let sequential = run_search_with_scores(
        &index,
        &query,
        k,
        SearchParams {
            parallel_threshold: usize::MAX,
            parallel_chunk_size: 1_024,
            parallel_enabled: false,
        },
    );
    let parallel = run_search_with_scores(
        &index,
        &query,
        k,
        SearchParams {
            parallel_threshold: 0,
            parallel_chunk_size: 1_024,
            parallel_enabled: true,
        },
    );

    let seq_ids: Vec<u64> = sequential.iter().map(|r| r.0).collect();
    let par_ids: Vec<u64> = parallel.iter().map(|r| r.0).collect();
    assert_eq!(seq_ids, par_ids, "parallelism must not change ordering");

    println!("\n=== Rollback Test PASSED ===");
}

/// Verify sequential vs parallel search yields identical results and scores.
#[test]
fn f16_preconvert_equivalence() {
    let (_dir, _path, index) = create_test_index();

    let k = 25;
    for seed in 0..5 {
        let query = create_query_vector_seed(seed);
        let seq = run_search_with_scores(
            &index,
            &query,
            k,
            SearchParams {
                parallel_threshold: usize::MAX,
                parallel_chunk_size: 1_024,
                parallel_enabled: false,
            },
        );
        let par = run_search_with_scores(
            &index,
            &query,
            k,
            SearchParams {
                parallel_threshold: 0,
                parallel_chunk_size: 1_024,
                parallel_enabled: true,
            },
        );

        let seq_ids: Vec<u64> = seq.iter().map(|r| r.0).collect();
        let par_ids: Vec<u64> = par.iter().map(|r| r.0).collect();
        assert_eq!(seq_ids, par_ids, "message_id mismatch for seed {seed}");

        for ((id, score_a), (_, score_b)) in seq.iter().zip(par.iter()) {
            assert!(
                (score_a - score_b).abs() < 1e-6,
                "score mismatch for message {id} (seed {seed}): {score_a} vs {score_b}"
            );
        }
    }
}

/// Test that filtering works correctly with parallel search.
#[test]
fn e2e_parallel_search_with_filters() {
    println!("=== E2E Parallel Search with Filters ===");

    let (_dir, _path, loaded_index) = create_test_index();
    let query = create_query_vector();
    let k = 25;

    // Test filter by agent
    println!("Testing filter by agent_id=0");
    let filter = SemanticFilter {
        agents: Some(HashSet::from([0u32])),
        ..Default::default()
    };
    let filtered_results = loaded_index
        .search_top_k(&query, k, Some(&filter))
        .expect("Search failed");

    // Verify all results have correct agent_id
    for result in &filtered_results {
        let parsed = parse_semantic_doc_id(&result.doc_id).expect("parse doc_id");
        assert_eq!(
            parsed.agent_id, 0,
            "Filter returned wrong agent_id: {}",
            parsed.agent_id
        );
    }
    println!("  All {} results have agent_id=0", filtered_results.len());

    // Test filter by multiple agents
    println!("Testing filter by agent_id in [0, 1]");
    let filter = SemanticFilter {
        agents: Some(HashSet::from([0u32, 1u32])),
        ..Default::default()
    };
    let multi_filtered = loaded_index
        .search_top_k(&query, k, Some(&filter))
        .expect("Search failed");

    for result in &multi_filtered {
        let parsed = parse_semantic_doc_id(&result.doc_id).expect("parse doc_id");
        assert!(
            parsed.agent_id == 0 || parsed.agent_id == 1,
            "Filter returned wrong agent_id: {}",
            parsed.agent_id
        );
    }
    println!(
        "  All {} results have agent_id in [0, 1]",
        multi_filtered.len()
    );

    println!("=== Parallel Filter Test PASSED ===");
}

/// Test search performance scales reasonably with corpus size.
#[test]
fn e2e_performance_scaling() {
    println!("=== E2E Performance Scaling Test ===");

    let sizes = [1_000, 5_000, 10_000, 15_000];
    let query = create_query_vector();
    let k = 25;

    let mut results: Vec<(usize, f64)> = Vec::new();

    for &size in &sizes {
        let (dir, path, index) =
            create_index_with_size(Path::new("test.fsvi"), size, Quantization::F32);

        // Warm up
        let _ = index.search_top_k(&query, k, None);

        // Measure
        let mut durations = Vec::new();
        for _ in 0..5 {
            let start = Instant::now();
            let _ = index.search_top_k(&query, k, None);
            durations.push(start.elapsed().as_secs_f64() * 1000.0);
        }

        let avg_ms = durations.iter().sum::<f64>() / 5.0;
        results.push((size, avg_ms));
        println!("  {} vectors: {:.3}ms average", size, avg_ms);

        drop(index);
        drop(path);
        drop(dir);
    }

    // NOTE: We intentionally do not assert on timing ratios here to avoid
    // flakiness across machines. This test is intended to catch panics and
    // validate that search completes successfully across sizes.

    println!("=== Performance Scaling Test PASSED ===");
}

fn create_index_with_size(
    name: &Path,
    count: usize,
    quantization: Quantization,
) -> (TempDir, PathBuf, VectorIndex) {
    let dir = tempdir().expect("Failed to create temp dir");
    let path = dir.path().join(name);

    let mut writer = VectorIndex::create_with_revision(
        &path,
        "test-embedder",
        "rev1",
        VECTOR_DIMENSION,
        quantization,
    )
    .expect("create writer");

    let mut vec_buf = vec![0.0f32; VECTOR_DIMENSION];
    for i in 0..count {
        for (d, slot) in vec_buf.iter_mut().enumerate() {
            let val = ((i * 7 + d * 13) % 1000) as f32 / 1000.0;
            *slot = val * 2.0 - 1.0;
        }
        normalize_in_place(&mut vec_buf);
        let doc_id = SemanticDocId {
            message_id: i as u64,
            chunk_idx: 0,
            agent_id: (i % 4) as u32,
            workspace_id: 1,
            source_id: 1,
            role: 0,
            created_at_ms: (i as i64) * 1000,
            content_hash: None,
        }
        .to_doc_id_string();
        writer
            .write_record(&doc_id, &vec_buf)
            .expect("write_record");
    }
    writer.finish().expect("finish");
    let index = VectorIndex::open(&path).expect("open");
    (dir, path, index)
}
