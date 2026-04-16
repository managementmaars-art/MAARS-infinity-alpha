# Claude Code Proxy Anti-Patterns

<!-- PROCESS-STORM-OK: This file documents anti-patterns including gh CLI recursion as a WARNING, not as executable code -->
<!-- SSoT-OK: version references below are documentation of binary analysis findings, not package versions -->

Gotchas discovered during multi-provider proxy implementation (2026-02-22 to 2026-02-23). Severity ratings indicate impact of hitting each issue without prior knowledge.

---

## CCP-01: ANTHROPIC_BASE_URL Alone Without ANTHROPIC_API_KEY [HIGH]

**Symptom**: Claude Code shows "API Usage Billing" instead of subscription, or ignores `ANTHROPIC_BASE_URL` entirely. Proxy receives no requests.

**Root cause**: In OAuth mode, Claude Code only honors `ANTHROPIC_BASE_URL` when `ANTHROPIC_API_KEY` is also set. Without the API key, Claude Code stays in pure OAuth mode and talks directly to `api.anthropic.com`, bypassing the proxy.

**Fix**: Set `ANTHROPIC_API_KEY` to a dummy sentinel value.

```bash
# WRONG - Claude Code ignores ANTHROPIC_BASE_URL in OAuth mode
export ANTHROPIC_BASE_URL="http://127.0.0.1:8083"

# RIGHT - forces Claude Code to use ANTHROPIC_BASE_URL
export ANTHROPIC_BASE_URL="http://127.0.0.1:8083"
export ANTHROPIC_API_KEY="proxy-managed"
```

The proxy detects `"proxy-managed"` and never forwards it to providers.

---

## CCP-02: Missing anthropic-beta: oauth-2025-04-20 Header [HIGH]

**Symptom**: Anthropic returns 401 Unauthorized or "invalid token" when forwarding OAuth Bearer tokens through the proxy.

**Root cause**: Anthropic requires the `anthropic-beta: oauth-2025-04-20` header alongside the `Authorization: Bearer {token}` header. Without this beta flag, the API endpoint does not recognize OAuth tokens and rejects them.

**Fix**: Append `oauth-2025-04-20` to the existing beta headers. Do NOT replace them.

```python
# WRONG - replaces all existing beta features
target_headers["anthropic-beta"] = "oauth-2025-04-20"

# RIGHT - appends to existing beta features
existing_beta = original_headers.get("anthropic-beta", "")
beta_parts = [b.strip() for b in existing_beta.split(",") if b.strip()] if existing_beta else []
if "oauth-2025-04-20" not in beta_parts:
    beta_parts.append("oauth-2025-04-20")
target_headers["anthropic-beta"] = ",".join(beta_parts)
```

Claude Code sends other beta features (like extended thinking) that must be preserved.

---

## CCP-03: Using /api/oauth/claude_cli/create_api_key Endpoint [MEDIUM]

**Symptom**: Attempting to create an API key from an OAuth token fails with a permission error.

**Root cause**: The `/api/oauth/claude_cli/create_api_key` endpoint requires the `org:create_api_key` OAuth scope. Free/Pro/Max subscription users are granted `user:inference` scope only. This endpoint is reserved for organization administrators.

**Fix**: Do not attempt to convert OAuth tokens to API keys. Use the OAuth token directly with the `Authorization: Bearer` header plus the `anthropic-beta: oauth-2025-04-20` header.

```bash
# WRONG - trying to create API key from OAuth token
curl https://api.anthropic.com/api/oauth/claude_cli/create_api_key \
  -H "Authorization: Bearer $OAUTH_TOKEN"
# Returns: 403 Forbidden (insufficient scope)

# RIGHT - use OAuth token directly for inference
curl https://api.anthropic.com/v1/messages \
  -H "Authorization: Bearer $OAUTH_TOKEN" \
  -H "anthropic-beta: oauth-2025-04-20" \
  -H "anthropic-version: 2023-06-01" \
  -d '{"model": "claude-sonnet-4-6", "max_tokens": 100, "messages": [...]}'
```

---

## CCP-04: Lowercase Keychain Service Name [HIGH]

**Symptom**: `security find-generic-password` returns "The specified item could not be found in the keychain."

**Root cause**: The Keychain service name is `"Claude Code-credentials"` with a capital C, capital C, and a space before the hyphen. Using `"claude-code-credentials"` (all lowercase) or `"claude code-credentials"` (lowercase c) will not find the item.

**Fix**: Use the exact service name with correct casing.

```bash
# WRONG - lowercase
security find-generic-password -s "claude-code-credentials" -a "$USER" -w

# WRONG - wrong capitalization
security find-generic-password -s "Claude code-credentials" -a "$USER" -w

# RIGHT - exact casing from Claude Code binary
security find-generic-password -s "Claude Code-credentials" -a "$USER" -w
```

This was discovered by reverse-engineering the compiled Claude Code binary where `_d()` generates the service name string.

---

## CCP-05: Reading ~/.claude/.credentials.json as Primary Auth Source [MEDIUM]

**Symptom**: Stale or expired tokens used for authentication. Intermittent auth failures that resolve after Claude Code restart.

**Root cause**: `~/.claude/.credentials.json` is a plaintext fallback that may not be updated when Claude Code refreshes its OAuth token. The macOS Keychain is the primary (SSoT) token store. Claude Code writes to both, but the credential file may lag behind Keychain updates.

**Fix**: Always try Keychain first, fall back to credential file only if Keychain read fails.

```python
# WRONG - credential file as primary
cred_path = Path.home() / ".claude" / ".credentials.json"
data = json.loads(cred_path.read_text())
token = data["claudeAiOauth"]["accessToken"]

# RIGHT - Keychain first, credential file as fallback
token_data = _read_keychain_oauth()  # Keychain (SSoT)
if not token_data:
    # Fallback: try credential file
    for cred_path in _OAUTH_CREDENTIAL_PATHS:
        ...
```

See [oauth-internals.md](./oauth-internals.md) for the full auth priority chain.

---

## CCP-06: Hardcoding OAuth Tokens [HIGH]

**Symptom**: Proxy works for a while, then all Anthropic-bound requests return 401 Unauthorized.

**Root cause**: OAuth tokens have an `expiresAt` timestamp. Hardcoded tokens will eventually expire. Claude Code refreshes tokens automatically via the OAuth flow, but a hardcoded token in a config file or environment variable will go stale.

**Fix**: Read tokens dynamically from Keychain with a cache TTL.

```python
# WRONG - hardcoded token
OAUTH_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."

# WRONG - read once at startup
OAUTH_TOKEN = _read_keychain_oauth()["accessToken"]

# RIGHT - dynamic read with 5-minute cache
_OAUTH_CACHE_TTL = 300
def _get_oauth_token():
    now = time.time()
    if _oauth_cache["token"] and (now - _oauth_cache["fetched_at"]) < _OAUTH_CACHE_TTL:
        token_expires = _oauth_cache["expires_at"]
        if token_expires == 0 or (token_expires / 1000) > now:
            return _oauth_cache["token"]
    # Re-read from Keychain
    token_data = _read_keychain_oauth()
    ...
```

---

## CCP-07: Using gh auth token in Proxy or Hooks [HIGH]

**Symptom**: System freeze. macOS becomes unresponsive. Hundreds of `gh` and `git-credential-osxkeychain` processes spawn.

**Root cause**: `gh auth token` triggers the Git credential helper, which may invoke Claude Code hooks, which may invoke `gh` again, creating a recursive process storm. This is especially dangerous in `.zshenv` or any code path that runs on every shell invocation.

**Fix**: Never call `gh` CLI in proxy code, hooks, or credential helpers. Use direct API calls or 1Password for credential resolution.

```bash
# WRONG - causes recursive process storm (DO NOT RUN)
# PROCESS-STORM-OK: documenting anti-pattern, not executable
# GH_TOKEN="$(gh auth token)"

# RIGHT - use 1Password or direct file read
GH_TOKEN=$(op read "op://vault/item/token")
```

See the itp-hooks plugin CLAUDE.md (Process Storm Prevention section) for details.

---

## CCP-08: Setting ANTHROPIC_API_KEY to Real Key While Proxy Runs [MEDIUM]

**Symptom**: Your real Anthropic API key appears in proxy logs for MiniMax-routed requests. Potential key leakage to third-party providers.

**Root cause**: Claude Code sends `x-api-key` header to `ANTHROPIC_BASE_URL`. If `ANTHROPIC_API_KEY` contains a real Anthropic key, the proxy receives it and may forward it to all providers, including third-party ones.

**Fix**: Always use the sentinel value `"proxy-managed"`. The proxy checks for this value and strips it (`proxy.py:324`).

```bash
# WRONG - real key gets forwarded to all providers
export ANTHROPIC_API_KEY="sk-ant-api03-..."

# RIGHT - sentinel value, proxy knows to ignore it
export ANTHROPIC_API_KEY="proxy-managed"
```

If you need to use a real API key for Anthropic-bound requests, set `REAL_ANTHROPIC_API_KEY` in the proxy's `.env` file instead.

---

## CCP-08b: ANTHROPIC_API_KEY Set in Environment With OAuth Token [HIGH]

**Symptom**: Claude Code shows "Auth conflict: Both a token (claude.ai) and an API key (ANTHROPIC_API_KEY) are set" warning in the header.

**Root cause**: Even setting `ANTHROPIC_API_KEY=proxy-managed` causes a conflict warning because Claude Code detects any ANTHROPIC_API_KEY as both a token AND an API key being present.

**Fix**: Unset ANTHROPIC_API_KEY entirely. The Go proxy handles the sentinel internally via request header `x-api-key: proxy-managed`, not environment variable.

```bash
# WRONG - causes auth conflict warning
export ANTHROPIC_BASE_URL="http://127.0.0.1:8082"
export ANTHROPIC_API_KEY="proxy-managed"

# RIGHT - unset ANTHROPIC_API_KEY, proxy uses x-api-key header
export ANTHROPIC_BASE_URL="http://127.0.0.1:8082"
unset ANTHROPIC_API_KEY
```

In `.zshenv`:

```bash
# Claude Code proxy configuration
unset ANTHROPIC_API_KEY  # CRITICAL: unset to avoid auth conflict
export ANTHROPIC_BASE_URL="http://127.0.0.1:8082"
```

---

## CCP-09: cache_control Parameter Sent to MiniMax [MEDIUM]

**Symptom**: API error: `system.2.cache_control.ephemeral.scope: Extra inputs are not permitted` or similar cache_control validation error.

**Root cause**: MiniMax (and some other Anthropic-compatible providers) does not support the `cache_control` parameter that Anthropic's API accepts. The Go proxy's `processBody` function was passing this through to MiniMax.

**Fix**: Remove `cache_control` from the allowed parameters map in the Go proxy.

```go
// WRONG - allows cache_control through to MiniMax
var allowedParams = map[string]bool{
    // ...
    "cache_control": true,  // Remove this
}

// RIGHT - filter out cache_control for all providers
var allowedParams = map[string]bool{
    "model": true, "messages": true, "system": true, "max_tokens": true,
    "metadata": true, "stream": true, "temperature": true, "top_p": true,
    "top_k": true, "stop_sequences": true, "tools": true, "tool_choice": true,
    "thinking": true, "prompt_truncation": true, "provider": true,
    "extra": true, "force_conclusive": true, "include_usage_for": true,
    "output": true,  // Note: cache_control removed
}
```

---

## CCP-11: Not Handling /v1/messages/count_tokens [MEDIUM]

**Symptom**: Claude Code shows errors during preflight token counting, or silently falls back to estimation. Auth failures appear in proxy logs for count_tokens requests.

**Root cause**: Claude Code calls `/v1/messages/count_tokens` before sending messages to verify they fit within context limits. If the proxy only handles `/v1/messages` and returns 404 for count_tokens, Claude Code's preflight check fails.

**Fix**: Add a dedicated handler for the count_tokens endpoint with the same auth logic.

```go
// Go proxy: handle count_tokens endpoint
case strings.HasPrefix(r.URL.Path, "/v1/messages/count_tokens"):
    // Same auth logic as /v1/messages
    // Return 501 for MiniMax (doesn't support it)
```

---

## CCP-12: Running Proxy on 0.0.0.0 [LOW]

**Symptom**: The proxy is accessible from other machines on the network. OAuth tokens in transit could be intercepted on the local network.

**Root cause**: Binding to `0.0.0.0` makes the proxy listen on all network interfaces, not just localhost.

**Fix**: Bind to `127.0.0.1` for local-only access.

```python
# WRONG - accessible from network
uvicorn.run(app, host="0.0.0.0", port=PORT)

# RIGHT - localhost only
uvicorn.run(app, host="127.0.0.1", port=PORT)
```

**Note**: The reference implementation (`proxy.py:658`) currently uses `0.0.0.0` for flexibility. Override with `HOST=127.0.0.1` env var or update the code if security is a concern.
