//! Daemon client integration re-exports.
//!
//! Canonical daemon abstractions now live in frankensearch:
//! - `frankensearch-core`: `DaemonClient`, `DaemonError`, `DaemonRetryConfig`
//! - `frankensearch-fusion`: `NoopDaemonClient`, `DaemonFallbackEmbedder`, `DaemonFallbackReranker`

pub use frankensearch::{
    DaemonClient, DaemonError, DaemonFallbackEmbedder, DaemonFallbackReranker, DaemonRetryConfig,
    NoopDaemonClient,
};
