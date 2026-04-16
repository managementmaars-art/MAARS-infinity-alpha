//! CLI parsing tests for semantic search flags (bead bd-3bbv)
//!
//! Tests for the --model, --rerank, --reranker, --daemon, and --no-daemon flags
//! added to the search command.

use clap::Parser;
use coding_agent_search::{Cli, Commands};

#[test]
fn search_parses_model_flag() {
    let cli = Cli::try_parse_from(["cass", "search", "query", "--model", "minilm"])
        .expect("parse search flags");

    match cli.command {
        Some(Commands::Search { model, .. }) => {
            assert_eq!(model, Some("minilm".to_string()));
        }
        other => panic!("expected search command, got {other:?}"),
    }
}

#[test]
fn search_parses_rerank_flag() {
    let cli =
        Cli::try_parse_from(["cass", "search", "query", "--rerank"]).expect("parse search flags");

    match cli.command {
        Some(Commands::Search { rerank, .. }) => {
            assert!(rerank, "rerank flag should be true");
        }
        other => panic!("expected search command, got {other:?}"),
    }
}

#[test]
fn search_parses_reranker_flag() {
    let cli = Cli::try_parse_from(["cass", "search", "query", "--rerank", "--reranker", "bge"])
        .expect("parse search flags");

    match cli.command {
        Some(Commands::Search {
            rerank, reranker, ..
        }) => {
            assert!(rerank, "rerank flag should be true");
            assert_eq!(reranker, Some("bge".to_string()));
        }
        other => panic!("expected search command, got {other:?}"),
    }
}

#[test]
fn search_parses_daemon_flag() {
    let cli =
        Cli::try_parse_from(["cass", "search", "query", "--daemon"]).expect("parse search flags");

    match cli.command {
        Some(Commands::Search { daemon, .. }) => {
            assert!(daemon, "daemon flag should be true");
        }
        other => panic!("expected search command, got {other:?}"),
    }
}

#[test]
fn search_parses_no_daemon_flag() {
    let cli = Cli::try_parse_from(["cass", "search", "query", "--no-daemon"])
        .expect("parse search flags");

    match cli.command {
        Some(Commands::Search { no_daemon, .. }) => {
            assert!(no_daemon, "no_daemon flag should be true");
        }
        other => panic!("expected search command, got {other:?}"),
    }
}

#[test]
fn search_default_flags_are_false() {
    let cli = Cli::try_parse_from(["cass", "search", "query"]).expect("parse search flags");

    match cli.command {
        Some(Commands::Search {
            model,
            rerank,
            reranker,
            daemon,
            no_daemon,
            ..
        }) => {
            assert_eq!(model, None, "model should be None by default");
            assert!(!rerank, "rerank should be false by default");
            assert_eq!(reranker, None, "reranker should be None by default");
            assert!(!daemon, "daemon should be false by default");
            assert!(!no_daemon, "no_daemon should be false by default");
        }
        other => panic!("expected search command, got {other:?}"),
    }
}

#[test]
fn search_combines_mode_and_model_flags() {
    let cli = Cli::try_parse_from([
        "cass", "search", "query", "--mode", "semantic", "--model", "minilm",
    ])
    .expect("parse search flags");

    match cli.command {
        Some(Commands::Search { mode, model, .. }) => {
            assert!(mode.is_some());
            assert_eq!(model, Some("minilm".to_string()));
        }
        other => panic!("expected search command, got {other:?}"),
    }
}

#[test]
fn search_combines_rerank_and_daemon_flags() {
    let cli = Cli::try_parse_from([
        "cass",
        "search",
        "query",
        "--rerank",
        "--reranker",
        "bge",
        "--daemon",
    ])
    .expect("parse search flags");

    match cli.command {
        Some(Commands::Search {
            rerank,
            reranker,
            daemon,
            ..
        }) => {
            assert!(rerank);
            assert_eq!(reranker, Some("bge".to_string()));
            assert!(daemon);
        }
        other => panic!("expected search command, got {other:?}"),
    }
}

// Note: The mutual exclusivity of --daemon and --no-daemon is enforced at runtime,
// not at parse time, so we test that separately via integration tests.

#[test]
fn search_parses_approximate_flag() {
    let cli = Cli::try_parse_from(["cass", "search", "query", "--approximate"])
        .expect("parse search flags");

    match cli.command {
        Some(Commands::Search { approximate, .. }) => {
            assert!(approximate, "approximate flag should be true");
        }
        other => panic!("expected search command, got {other:?}"),
    }
}

#[test]
fn search_approximate_default_is_false() {
    let cli = Cli::try_parse_from(["cass", "search", "query"]).expect("parse search flags");

    match cli.command {
        Some(Commands::Search { approximate, .. }) => {
            assert!(!approximate, "approximate should be false by default");
        }
        other => panic!("expected search command, got {other:?}"),
    }
}

#[test]
fn search_combines_mode_semantic_and_approximate() {
    let cli = Cli::try_parse_from([
        "cass",
        "search",
        "query",
        "--mode",
        "semantic",
        "--approximate",
    ])
    .expect("parse search flags");

    match cli.command {
        Some(Commands::Search {
            mode, approximate, ..
        }) => {
            assert!(mode.is_some());
            assert!(approximate, "approximate should be true");
        }
        other => panic!("expected search command, got {other:?}"),
    }
}

#[test]
fn search_combines_mode_hybrid_and_approximate() {
    let cli = Cli::try_parse_from([
        "cass",
        "search",
        "query",
        "--mode",
        "hybrid",
        "--approximate",
    ])
    .expect("parse search flags");

    match cli.command {
        Some(Commands::Search {
            mode, approximate, ..
        }) => {
            assert!(mode.is_some());
            assert!(approximate, "approximate should be true");
        }
        other => panic!("expected search command, got {other:?}"),
    }
}
