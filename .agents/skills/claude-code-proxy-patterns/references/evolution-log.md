# Evolution Log

## 2026-02-24: Auth Conflict & cache_control Fixes

Source: Debugging plan mode failure.

Key fixes:

- **CCP-08b**: Added ANTHROPIC_API_KEY unset in `.zshenv` - auth conflict warning fixed
- **CCP-09**: Removed `cache_control` from allowedParams - MiniMax compatibility fixed
- Added OAuth auto-refresh (`oauth_refresh.go`) - background token refresh every 30 minutes

Files changed:

- `~/.claude/tools/claude-code-proxy-go/main.go` - removed cache_control, added getTokenFromKeychain
- `~/.claude/tools/claude-code-proxy-go/oauth_refresh.go` - new file for auto-refresh
- `~/.zshenv` - added `unset ANTHROPIC_API_KEY`

New anti-patterns:

- CCP-08b: ANTHROPIC_API_KEY set in env with OAuth token → unset it
- CCP-09: cache_control param sent to MiniMax → remove from allowedParams

---

## 2026-02-23: Go-Only Implementation

Source: Migrated from Python to Go for launchd deployment.

Key changes:

- Go binary proxy deployed to `/usr/local/bin/claude-proxy` (port 8082)
- launchd plist for auto-restart: `/Library/LaunchDaemons/com.terryli.claude-proxy.plist`
- Uses `cenkalti/backoff/v4` for retry logic (no Python fallback)
- Python proxy deprecated

Reference implementation:

- Go proxy: `/usr/local/bin/claude-proxy`
- Source: `$HOME/eon/cc-skills/tools/claude-code-failover/main.go`

Port configuration:

- `:8082` - Go proxy (entry point, launchd-managed)
- `:8083` - Optional failover wrapper (deprecated)

MiniMax credentials configured via launchd EnvironmentVariables.

## 2026-02-22: Initial skill creation

Source: Empirical discovery during proxy implementation.
Key discoveries: OAuth Keychain storage (`"Claude Code-credentials"`), `anthropic-beta: oauth-2025-04-20` header requirement, `ANTHROPIC_API_KEY=proxy-managed` forcing pattern.
Reference implementation: `$HOME/.claude/tools/claude-code-proxy/proxy.py`
10 anti-patterns (CCP-01 through CCP-10) cataloged from real debugging sessions.
Provider compatibility tested: MiniMax M2.5-highspeed, Real Anthropic.
Binary reverse-engineering findings: `_d()` service name, `hW()` storage backend, `WL="oauth-2025-04-20"` constant.
