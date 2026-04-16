# OAuth Token Auto-Refresh

The Go proxy automatically refreshes OAuth tokens before they expire.

**Use case**: Prevent auth failures when tokens expire during long-running Claude Code sessions.

**Implementation**: Background goroutine runs every 30 minutes, checks if token expires within 5 minutes, and refreshes using the refresh token.

```go
// oauth_refresh.go
func startTokenRefreshLoop() {
    ticker := time.NewTicker(30 * time.Minute)
    defer ticker.Stop()
    refreshTokenIfNeeded() // Run immediately on startup
    for {
        select {
        case <-ticker.C:
            refreshTokenIfNeeded()
        }
    }
}

func refreshTokenIfNeeded() {
    // Check if token expires within 5 minutes
    needsRefresh := oauthCache.token == "" ||
        (!oauthCache.expiresAt.IsZero() && time.Now().Add(5*time.Minute).After(oauthCache.expiresAt))

    if !needsRefresh {
        return // Token still valid
    }

    // Try API refresh first
    newToken, newRefreshToken, newExpiresAt, err := refreshOAuthToken(refreshToken)
    if err != nil {
        // Fallback: get fresh token from Keychain
        tryKeychainRefresh()
        return
    }

    // Update cache and persist
    oauthCache.token = newToken
    oauthCache.refreshToken = newRefreshToken
    oauthCache.expiresAt = newExpiresAt
    saveOAuthToFile(newToken, newRefreshToken, newExpiresAt)
}
```

## Refresh Logic

1. Runs every 30 minutes in background goroutine
2. Checks if token expires within 5 minutes
3. If refresh token available -> calls Anthropic OAuth refresh endpoint
4. If API fails -> falls back to Keychain retrieval
5. Saves new tokens to `.oauth.json` for persistence

## Key Files

- `oauth_refresh.go` - Auto-refresh logic (~80 lines)
- `main.go` - Token cache + refreshOAuthToken function
