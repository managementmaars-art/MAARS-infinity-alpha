//! Upgrade and backwards compatibility testing module.
//!
//! This module tests:
//! - Reading archives from older versions
//! - Schema migration between versions
//! - Graceful handling of unknown versions
//! - Feature detection and degradation
//!
//! Run with:
//!   cargo test --test upgrade

mod compatibility;
mod migration;
