//! Remote sources management for cass.
//!
//! This module provides functionality for configuring and syncing agent session
//! data from remote machines via SSH. It enables cass to search across conversation
//! history from multiple machines.
//!
//! # Architecture
//!
//! - **config**: Configuration types for defining remote sources
//! - **provenance**: Types for tracking conversation origins
//! - **sync**: Sync engine for pulling sessions from remotes via rsync/SSH
//! - **status** (future): Sync status tracking
//!
//! # Configuration
//!
//! Sources are configured in `~/.config/cass/sources.toml`:
//!
//! ```toml
//! [[sources]]
//! name = "laptop"
//! type = "ssh"
//! host = "user@laptop.local"
//! paths = ["~/.claude/projects", "~/.cursor"]
//! ```
//!
//! # Provenance
//!
//! Each conversation tracks where it came from via [`provenance::Origin`]:
//!
//! ```rust,ignore
//! use coding_agent_search::sources::provenance::{Origin, SourceKind};
//!
//! // Local conversation
//! let local = Origin::local();
//!
//! // Remote conversation
//! let remote = Origin::remote("work-laptop");
//! ```
//!
//! # Syncing
//!
//! The sync engine uses rsync over SSH for efficient delta transfers:
//!
//! ```rust,ignore
//! use coding_agent_search::sources::sync::SyncEngine;
//! use coding_agent_search::sources::config::SourcesConfig;
//!
//! let config = SourcesConfig::load()?;
//! let engine = SyncEngine::new(&data_dir);
//!
//! for source in config.remote_sources() {
//!     let report = engine.sync_source(source)?;
//!     println!("Synced {}: {} files", source.name, report.total_files());
//! }
//! ```
//!
//! # Usage
//!
//! ```rust,ignore
//! use coding_agent_search::sources::config::SourcesConfig;
//!
//! // Load configuration
//! let config = SourcesConfig::load()?;
//!
//! // Iterate remote sources
//! for source in config.remote_sources() {
//!     println!("Source: {} ({})", source.name, source.host.as_deref().unwrap_or("-"));
//! }
//! ```

pub mod config;
pub mod index;
pub mod install;
pub mod interactive;
pub mod probe;
pub mod provenance;
pub mod setup;
pub mod sync;

/// Canonical SSH stderr marker for host-key verification failures.
pub(crate) const HOST_KEY_VERIFICATION_FAILED: &str = "Host key verification failed";

/// Build strict SSH CLI tokens with consistent trust policy.
///
/// The returned vector contains full `ssh` argument tokens:
/// `-o BatchMode=yes -o ConnectTimeout=<secs> -o StrictHostKeyChecking=yes`.
pub(crate) fn strict_ssh_cli_tokens(connect_timeout_secs: u64) -> Vec<String> {
    vec![
        "-o".to_string(),
        "BatchMode=yes".to_string(),
        "-o".to_string(),
        format!("ConnectTimeout={connect_timeout_secs}"),
        "-o".to_string(),
        "ServerAliveInterval=15".to_string(),
        "-o".to_string(),
        "ServerAliveCountMax=3".to_string(),
        "-o".to_string(),
        "StrictHostKeyChecking=yes".to_string(),
    ]
}

/// Build strict SSH command string for tools that require a single shell fragment.
pub(crate) fn strict_ssh_command_for_rsync(connect_timeout_secs: u64) -> String {
    format!(
        "ssh -o BatchMode=yes -o ConnectTimeout={connect_timeout_secs} -o ServerAliveInterval=15 -o ServerAliveCountMax=3 -o StrictHostKeyChecking=yes"
    )
}

/// Whether stderr indicates SSH host-key verification failure.
pub(crate) fn is_host_key_verification_failure(stderr: &str) -> bool {
    stderr.contains(HOST_KEY_VERIFICATION_FAILED)
}

/// Standard user-facing error for host-key verification failures.
pub(crate) fn host_key_verification_error(host: &str) -> String {
    format!(
        "Host key verification failed for {host} (add/verify host key in ~/.ssh/known_hosts first)"
    )
}

// Re-export commonly used config types
pub use config::{
    BackupInfo, ConfigError, ConfigPreview, DiscoveredHost, MergeResult, PathMapping, Platform,
    SkipReason, SourceConfigGenerator, SourceDefinition, SourcesConfig, SyncSchedule,
    discover_ssh_hosts, get_preset_paths,
};

// Re-export commonly used provenance types
pub use provenance::{LOCAL_SOURCE_ID, Origin, Source, SourceFilter, SourceKind};

// Re-export commonly used sync types
pub use sync::{
    PathSyncResult, SourceSyncInfo, SyncEngine, SyncError, SyncMethod, SyncReport, SyncResult,
    SyncStatus,
};

// Re-export commonly used probe types
pub use probe::{
    CassStatus, DetectedAgent, HostProbeResult, ProbeCache, ResourceInfo, SystemInfo, probe_host,
    probe_hosts_parallel,
};

// Re-export commonly used install types
pub use install::{
    InstallError, InstallMethod, InstallProgress, InstallResult, InstallStage, RemoteInstaller,
};

// Re-export commonly used index types
pub use index::{IndexError, IndexProgress, IndexResult, IndexStage, RemoteIndexer};

// Re-export commonly used interactive types
pub use interactive::{
    CassStatusDisplay, HostDisplayInfo, HostSelectionResult, HostSelector, HostState,
    InteractiveError, confirm_action, confirm_with_details, probe_to_display_info,
    run_host_selection,
};

// Re-export commonly used setup types
pub use setup::{SetupError, SetupOptions, SetupResult, SetupState, run_setup};
