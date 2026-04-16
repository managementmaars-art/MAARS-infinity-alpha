# UI Verification Patterns

Browser automation and SSO auth patterns for verifying Eve app frontends.

## Tool Choice

| Tool | Best For | Tradeoffs |
|------|----------|-----------|
| **agent-browser** (default) | CLI-driven checks, screenshot capture, form fill | Snapshot-based, less precise assertions |
| **Playwright MCP** | Programmatic assertions, complex interactions, CI | Heavier setup, more powerful |

Use `agent-browser` for most verification. Switch to Playwright when you need precise DOM assertions or complex multi-step interactions.

## SSO Authentication

Eve apps authenticate via Eve SSO. Verification plans must bypass the interactive login flow with a minted token.

### Mint and Inject

```bash
# Mint an SSO token
SSO_TOKEN=$(eve auth mint --email test@example.com --org $ORG_ID --format sso-jwt)

# Inject via callback URL
agent-browser --session verify open "${APP_URL}/auth/callback?token=${SSO_TOKEN}"

# Wait for redirect to authenticated page
agent-browser --session verify wait --url "**/dashboard"
```

### Verify Auth State

```bash
# Confirm authenticated state
agent-browser --session verify snapshot
# Should show authenticated UI (user name, dashboard content)

# Screenshot for evidence
agent-browser --session verify screenshot ./e2e-verification/artifacts/authenticated.png
```

### Token Expiry Testing

```bash
# Mint a short-lived token
SHORT_TOKEN=$(eve auth mint --email test@example.com --org $ORG_ID --format sso-jwt --ttl 60)

# Inject and use
agent-browser --session expiry open "${APP_URL}/auth/callback?token=${SHORT_TOKEN}"

# Wait for expiry (60s)
sleep 65

# Navigate — should trigger re-auth
agent-browser --session expiry open "${APP_URL}/dashboard"
agent-browser --session expiry snapshot
# Should show login prompt or redirect, not error page
```

## Screenshot Verification

### Light and Dark Mode

```bash
# Light mode (default)
agent-browser --session verify screenshot ./e2e-verification/artifacts/dashboard-light.png

# Toggle dark mode
agent-browser --session verify click "[data-testid='theme-toggle']"
# Or via system preference
agent-browser --session verify evaluate "document.documentElement.classList.add('dark')"
agent-browser --session verify screenshot ./e2e-verification/artifacts/dashboard-dark.png
```

### Responsive Breakpoints

```bash
# Desktop (1920x1080)
agent-browser --session verify resize 1920 1080
agent-browser --session verify screenshot ./e2e-verification/artifacts/desktop.png

# Tablet (768x1024)
agent-browser --session verify resize 768 1024
agent-browser --session verify screenshot ./e2e-verification/artifacts/tablet.png

# Mobile (375x812)
agent-browser --session verify resize 375 812
agent-browser --session verify screenshot ./e2e-verification/artifacts/mobile.png
```

### Key Pages

Screenshot every important page/state:

```bash
PAGES=("dashboard" "settings" "items" "items/new" "profile")

for page in "${PAGES[@]}"; do
  agent-browser --session verify open "${APP_URL}/${page}"
  agent-browser --session verify wait --network-idle
  agent-browser --session verify screenshot "./e2e-verification/artifacts/${page//\//-}.png"
done
```

## Form Interaction

### Fill and Submit

```bash
# Navigate to form
agent-browser --session verify open "${APP_URL}/items/new"

# Fill fields
agent-browser --session verify fill "[name='title']" "Test Item"
agent-browser --session verify fill "[name='description']" "Created by verification plan"
agent-browser --session verify select "[name='status']" "active"

# Submit
agent-browser --session verify click "[type='submit']"

# Verify success
agent-browser --session verify wait --url "**/items/*"
agent-browser --session verify snapshot
```

### Validation Testing

```bash
# Submit empty form
agent-browser --session verify open "${APP_URL}/items/new"
agent-browser --session verify click "[type='submit']"

# Check for validation errors
agent-browser --session verify snapshot
# Should show validation messages, not a server error
```

## Console Error Capture

```bash
# Start capturing console
agent-browser --session verify open "${APP_URL}/dashboard"

# Check for errors
agent-browser --session verify evaluate "
  const errors = [];
  const originalError = console.error;
  console.error = (...args) => { errors.push(args.join(' ')); originalError(...args); };
  window.__capturedErrors = errors;
"

# Navigate through key pages
for page in dashboard settings items; do
  agent-browser --session verify open "${APP_URL}/${page}"
  agent-browser --session verify wait --network-idle
done

# Retrieve errors
agent-browser --session verify evaluate "JSON.stringify(window.__capturedErrors)"
# Should return [] (no console errors)
```

## Playwright MCP Alternative

When `agent-browser` isn't sufficient, use Playwright MCP tools:

```bash
# Navigate
mcp__pw__browser_navigate --url "${APP_URL}/auth/callback?token=${SSO_TOKEN}"

# Wait for navigation
mcp__pw__browser_wait_for --state "networkidle"

# Take screenshot
mcp__pw__browser_take_screenshot --path "./e2e-verification/artifacts/dashboard.png"

# Snapshot DOM
mcp__pw__browser_snapshot

# Fill form
mcp__pw__browser_fill_form --selector "[name='title']" --value "Test Item"

# Click
mcp__pw__browser_click --selector "[type='submit']"

# Assert text visible
mcp__pw__browser_evaluate --expression "document.body.innerText.includes('Success')"
```

## Assertions Checklist

For every UI verification scenario, check:

- [ ] Pages render without console errors
- [ ] Dark mode and light mode both display correctly
- [ ] Login flow completes via SSO token injection
- [ ] Key user flows complete end-to-end
- [ ] Forms submit and validate correctly
- [ ] Responsive layout works at desktop, tablet, and mobile
- [ ] No broken images or missing assets
- [ ] Navigation between pages works without errors

## Artifact Organization

```
e2e-verification/artifacts/
  dashboard-light.png
  dashboard-dark.png
  desktop.png
  tablet.png
  mobile.png
  authenticated.png
  form-validation.png
  ...
```

Add `e2e-verification/artifacts/` to `.gitignore`.
