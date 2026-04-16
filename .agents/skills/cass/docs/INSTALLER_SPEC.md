# Installer Spec (UBS-style) for coding-agent-search

## Goals
- One-line curl|bash / pwsh that installs coding-agent-search safely.
- Default: cautious, prompts before installs/ PATH edits; checksum required.
- Easy mode: fully non-interactive with safe defaults.
- Works on Linux/macOS; PowerShell path for Windows.
- Ensures Rust nightly toolchain + rustfmt/clippy available.
- Uses only tar.gz/zip + sha256; optional minisign later.
- No destructive actions; never deletes user files.

## UX
- Colorful logging (✓/✗/→/⚠); quiet flag to silence info.
- Lock file to prevent concurrent runs; temp workdir cleaned on exit.
- DEST default: ~/.local/bin (user) or --system for /usr/local/bin.
- PATH guidance; easy mode can append PATH (optional prompt in normal mode).
- Self-test flag `--verify` runs `coding-agent-search --version` and prints usage hint; `--quickstart` runs `index --full` against provided/auto data dir.

## Inputs
- Flags: --easy-mode, --dest DIR, --system, --quiet, --verify, --quickstart, --version vX, --owner/--repo, --artifact-url, --checksum, --checksum-url, --no-path-modify, --rustup-host, --force.
- Env: ARTIFACT_URL, CHECKSUM, CHECKSUM_URL (override), RUSTUP_INIT_SKIP to skip rustup (power users).

## Safety invariants
- Always verify checksum; fail closed if checksum missing/unreadable.
- If rustup install required: prompt in normal mode; proceed silently in easy mode.
- Do not rm existing files; overwrite only target binary via install(1) with 0755.
- Exit non-zero on any verification failure.

## Flow (bash)
1) Preflight: bash>=4, curl present, install/sha256sum present.
2) Resolve artifact URL: default GitHub release `coding-agent-search-${VERSION}-${OS}-${ARCH}.tar.gz`; allow override.
3) Fetch artifact to temp dir; fetch checksum (or use env/flag); verify via sha256sum -c.
4) Install rustup nightly if `cargo` missing or `rustc --version` not nightly; add rustfmt/clippy components.
5) Extract tar, install binary to DEST; optional PATH adjust (appending to shell rc when easy-mode with consent).
6) Self-test if --verify; quickstart if --quickstart (uses provided data dir or default, runs index --full).
7) Print next steps + how to run TUI/headless.

## Flow (PowerShell)
- Mirrors bash: download zip, checksum required, optional ArtifactUrl/Checksum flags, EasyMode toggles prompts. Installs rustup nightly via rustup-init.exe if needed. PATH guidance.

## Open items
- Minisign integration (fail-closed when pubkey provided).
- Windows rustup install may require x86 vs x64 detection; prefer native rustup-init.exe.
- Watch-mode e2e quickstart optional.
