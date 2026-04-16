<!-- # SSoT-OK: version references are documentation of binary analysis findings, not package versions -->

# Claude Code OAuth Internals

Deep dive into how Claude Code stores, retrieves, and transmits OAuth tokens. Based on reverse-engineering of the Claude Code v2.1.50 compiled binary and empirical testing (2026-02-22).

---

## macOS Keychain Storage

Claude Code stores OAuth credentials in the macOS Keychain using the `security` CLI.

| Field   | Value                                        |
| ------- | -------------------------------------------- |
| Service | `"Claude Code-credentials"`                  |
| Account | Current macOS username (`getpass.getuser()`) |
| Type    | Generic password                             |
| Content | JSON string (see Token JSON Envelope below)  |

### Reading from Keychain

```bash
# CLI read (returns JSON string)
security find-generic-password \
  -s "Claude Code-credentials" \
  -a "$(whoami)" \
  -w
```

```python
# Python read
import subprocess, json, getpass

result = subprocess.run(
    ["security", "find-generic-password",
     "-s", "Claude Code-credentials",
     "-a", getpass.getuser(), "-w"],
    capture_output=True, text=True, timeout=5, check=False,
)
if result.returncode == 0:
    data = json.loads(result.stdout.strip())
    oauth = data.get("claudeAiOauth")
    if oauth and oauth.get("accessToken"):
        token = oauth["accessToken"]
```

### Keychain Item Metadata

The Keychain item also stores metadata accessible via `security find-generic-password -s "Claude Code-credentials" -a "$(whoami)"` (without `-w`):

- `svce` (service): `"Claude Code-credentials"`
- `acct` (account): username
- `cdat`/`mdat`: creation/modification timestamps
- Access control: application-specific (Claude Code binary)

**Note**: First-time Keychain access from a proxy may trigger a macOS authorization prompt. The user must click "Always Allow" or "Allow" to grant the proxy's Python process access.

---

## Token JSON Envelope

The Keychain stores a JSON object with the following structure:

```json
{
  "claudeAiOauth": {
    "accessToken": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refreshToken": "rt_abc123...",
    "expiresAt": 1740268800000,
    "subscriptionType": "claude_pro_2025",
    "accountUuid": "uuid-...",
    "organizationUuid": "uuid-..."
  }
}
```

| Field              | Type         | Notes                                     |
| ------------------ | ------------ | ----------------------------------------- |
| `accessToken`      | string (JWT) | Bearer token for API calls                |
| `refreshToken`     | string       | Used to obtain new access tokens          |
| `expiresAt`        | number       | **Milliseconds** since Unix epoch         |
| `subscriptionType` | string       | Plan identifier (e.g., `claude_pro_2025`) |

### Expiration Handling

```python
# expiresAt is in MILLISECONDS
now = time.time()  # seconds
token_expires_ms = oauth_data.get("expiresAt", 0)

if token_expires_ms == 0:
    # No expiry set, assume valid
    pass
elif (token_expires_ms / 1000) > now:
    # Token is still valid
    pass
else:
    # Token expired, need to re-read from Keychain
    # Claude Code may have refreshed it in the background
    pass
```

---

## Binary Reverse-Engineering Findings

From decompiling the Claude Code v2.1.50 native binary:

| Symbol | Purpose                                                                  |
| ------ | ------------------------------------------------------------------------ |
| `_d()` | Generates the Keychain service name string (`"Claude Code-credentials"`) |
| `hW()` | Storage backend selector (Keychain on macOS, different on Linux)         |
| `WL`   | Constant: `"oauth-2025-04-20"` (the required beta header value)          |

### Key Observations

1. **Service name construction**: `_d()` concatenates the app name `"Claude Code"` with `"-credentials"`. This is why the service name has a space (from the app name) before the hyphen.

2. **Beta header**: The `WL="oauth-2025-04-20"` constant confirms this header is hardcoded in the binary. It is not dynamically generated or versioned per-request.

3. **Storage abstraction**: `hW()` provides a platform-agnostic credential storage interface. On macOS it uses Keychain; on Linux it may use `libsecret` or a file-based fallback.

---

## CLAUDE_CODE_OAUTH_TOKEN Environment Variable

Found in the decompiled binary: Claude Code checks for `CLAUDE_CODE_OAUTH_TOKEN` as an alternative OAuth token source.

```bash
# Override OAuth token via environment (bypasses Keychain)
export CLAUDE_CODE_OAUTH_TOKEN="eyJhbG..."
```

**Use cases**:

- CI/CD environments without Keychain access
- Testing with specific tokens
- Headless Linux servers

**Warning**: This token is not auto-refreshed. It will expire based on its `expiresAt` value. Use for short-lived automation only.

---

## Cache TTL Pattern

The proxy caches Keychain reads to avoid subprocess overhead on every request.

```python
_oauth_cache: dict = {"token": None, "expires_at": 0.0, "fetched_at": 0.0}
_OAUTH_CACHE_TTL = 300  # 5 minutes

def _get_oauth_token() -> str | None:
    now = time.time()

    # Return cached if fresh and not expired
    if _oauth_cache["token"] and (now - _oauth_cache["fetched_at"]) < _OAUTH_CACHE_TTL:
        token_expires = _oauth_cache["expires_at"]
        if token_expires == 0 or (token_expires / 1000) > now:
            return _oauth_cache["token"]

    # Re-read from Keychain
    token_data = _read_keychain_oauth()
    if token_data:
        _oauth_cache["token"] = token_data["accessToken"]
        _oauth_cache["expires_at"] = token_data.get("expiresAt", 0)
        _oauth_cache["fetched_at"] = now
        return token_data["accessToken"]

    # Fallback to credential file...
```

**Why 5 minutes?**: Balance between freshness and performance. Keychain reads spawn a subprocess (`security` CLI), which costs ~50ms. At proxy scale (dozens of requests/minute), this adds up. 5 minutes is short enough that expired tokens are caught quickly but long enough to avoid constant subprocess overhead.

---

## Auth Header Format

For Anthropic API calls with OAuth tokens:

```http
POST /v1/messages HTTP/1.1
Host: api.anthropic.com
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
anthropic-beta: oauth-2025-04-20
anthropic-version: 2023-06-01
Content-Type: application/json
```

**Both** the `Authorization: Bearer` header AND the `anthropic-beta: oauth-2025-04-20` header are required. Missing either one results in 401 Unauthorized.

---

## Credential File Fallback

Location: `~/.claude/.credentials.json` (permissions: `chmod 0600`)

```json
{
  "claudeAiOauth": {
    "accessToken": "eyJhbG...",
    "refreshToken": "rt_...",
    "expiresAt": 1740268800000
  }
}
```

This file mirrors the Keychain content but is a **plaintext fallback**. It exists for:

- Linux systems without Keychain
- Debugging and inspection
- Recovery if Keychain access is broken

**Security note**: This file contains plaintext tokens. Ensure `chmod 0600` permissions. The Keychain is the preferred and more secure storage.

---

## OAuth Token Lifecycle

```
1. User runs `claude` CLI for first time
2. Claude Code opens browser for OAuth consent
3. Anthropic returns access_token + refresh_token
4. Claude Code stores both in Keychain (and credential file)
5. On each API call, Claude Code reads from Keychain
6. When access_token expires, Claude Code uses refresh_token to get new one
7. New tokens stored back to Keychain
8. Proxy reads from Keychain with 5-min cache, tracks expiresAt
```

**Important**: The proxy does NOT handle token refresh. Claude Code handles refresh automatically. The proxy just reads whatever current token is in Keychain.

---

## The OAuth Lockdown Context (January 2026)

Anthropic banned third-party tools from using OAuth tokens in January 2026. Key details:

- OAuth tokens from Free/Pro/Max plans are scoped to Claude Code and Claude.ai only
- Server-side validation checks client identity and request origin
- Third-party tools that spoofed Claude Code headers were blocked

**Why the proxy still works**: The proxy is a localhost passthrough, not a third-party tool. Claude Code itself makes the API calls, which route through the proxy to `api.anthropic.com`. Anthropic's servers see a legitimate Claude Code OAuth request.

**Risk**: If Anthropic adds certificate pinning or response signing, the proxy approach could break. As of 2026-02-22, no such validation exists.
