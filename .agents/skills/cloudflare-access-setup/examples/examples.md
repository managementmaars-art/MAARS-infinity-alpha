# Cloudflare Access Setup - Examples

Common scenarios and configuration examples for Cloudflare Access setup.

## Table of Contents

1. [First-Time Setup](#first-time-setup)
2. [Adding Multiple Users](#adding-multiple-users)
3. [Troubleshooting OAuth Errors](#troubleshooting-oauth-errors)
4. [Re-running Setup After Changes](#re-running-setup-after-changes)
5. [Testing Access Configuration](#testing-access-configuration)
6. [Checking Access Logs](#checking-access-logs)

---

## First-Time Setup

### Scenario
Setting up Cloudflare Access for the first time with no existing configuration.

### Steps

**1. Verify prerequisites are missing:**
```bash
cd /home/dawiddutoit/projects/network && source .env
echo "Client ID: ${GOOGLE_OAUTH_CLIENT_ID:-MISSING}"
echo "Client Secret: ${GOOGLE_OAUTH_CLIENT_SECRET:-MISSING}"
echo "Allowed Email: ${ACCESS_ALLOWED_EMAIL:-MISSING}"
```

Output (missing):
```
Client ID: MISSING
Client Secret: MISSING
Allowed Email: MISSING
```

**2. Create Google OAuth credentials:**
- Go to: https://console.cloud.google.com/apis/credentials
- Create OAuth 2.0 Client ID
- Application type: Web application
- Redirect URI: `https://temetai.cloudflareaccess.com/cdn-cgi/access/callback`
- Copy Client ID and Client Secret

**3. Update .env:**
```bash
# Add these lines to .env
GOOGLE_OAUTH_CLIENT_ID=123456789-abc.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=GOCSPX-xxxxxxxxxxxxxx
ACCESS_ALLOWED_EMAIL=dawiddutoit@temet.ai
```

**4. Run setup:**
```bash
./scripts/cf-access-setup.sh setup
```

Expected output:
```
=========================================
Cloudflare Access Complete Setup
=========================================

This will configure:
  * Google OAuth identity provider
  * Access applications for all services
  * Authentication policies

Protected services: pihole, jaeger, langfuse, sprinkler, home assistant
Allowed user: dawiddutoit@temet.ai
Bypass: webhook.temet.ai (for GitHub)

Continue? (y/n) y

Checking prerequisites...
[checkmark] CLOUDFLARE_ACCOUNT_ID
[checkmark] CLOUDFLARE_ACCESS_API_TOKEN
[checkmark] CLOUDFLARE_TEAM_NAME: temetai
[checkmark] GOOGLE_OAUTH_CLIENT_ID
[checkmark] GOOGLE_OAUTH_CLIENT_SECRET
[checkmark] ACCESS_ALLOWED_EMAIL: dawiddutoit@temet.ai

[checkmark] All prerequisites met

=========================================
Setting up Google OAuth Identity Provider
=========================================

Creating new Google identity provider...
[checkmark] Google identity provider configured successfully
  Provider ID: abc123...
  Auth Domain: https://temetai.cloudflareaccess.com

=========================================
Creating Access Applications
=========================================

Creating Access application: Pi-hole Admin (pihole.temet.ai)...
[checkmark] Application created: pihole.temet.ai
Creating allow policy for Pi-hole Admin...
[checkmark] Allow policy created for dawiddutoit@temet.ai
...
```

**5. Verify applications created:**
```bash
./scripts/cf-access-setup.sh list
```

**6. Test authentication:**
Open in incognito: https://pihole.temet.ai
- Should redirect to Google login
- Sign in with authorized email
- Should access Pi-hole admin

---

## Adding Multiple Users

### Scenario
Adding family members or colleagues to access protected services.

### Steps

**1. Edit .env to add emails:**
```bash
# Change from:
ACCESS_ALLOWED_EMAIL=dawiddutoit@temet.ai

# To:
ACCESS_ALLOWED_EMAIL=dawiddutoit@temet.ai,spouse@gmail.com,colleague@company.com
```

**2. Update access policies:**
```bash
./scripts/update-access-emails.sh
```

**3. Verify policies updated:**
```bash
./scripts/cf-access-setup.sh list
```

**4. If using External consent screen:**
If personal Gmail accounts get "can only be used within organization" error:
- Go to: https://console.cloud.google.com/apis/credentials/consent
- Edit consent screen
- Add test users (if in testing mode) or publish app

---

## Troubleshooting OAuth Errors

### Scenario: "redirect_uri_mismatch"

**Symptoms:**
Google shows error: "Error 400: redirect_uri_mismatch"

**Diagnosis:**
```bash
# Check team name
source .env && echo "Team: ${CLOUDFLARE_TEAM_NAME}"
# Expected redirect URI:
echo "Required URI: https://${CLOUDFLARE_TEAM_NAME}.cloudflareaccess.com/cdn-cgi/access/callback"
```

**Fix:**
1. Go to Google Console: https://console.cloud.google.com/apis/credentials
2. Edit OAuth 2.0 Client ID
3. Verify Authorized redirect URI matches exactly
4. Save and wait 5 minutes for propagation

### Scenario: "Access Denied"

**Symptoms:**
After Google login, see "Access Denied" page from Cloudflare

**Diagnosis:**
```bash
# Check which email is allowed
source .env && echo "Allowed: ${ACCESS_ALLOWED_EMAIL}"
```

**Fix:**
```bash
# Add the email to .env
ACCESS_ALLOWED_EMAIL=existing@email.com,new@email.com

# Update policies
./scripts/update-access-emails.sh
```

### Scenario: Login Loop

**Symptoms:**
Browser keeps redirecting between Google and service

**Fix:**
1. Clear all cookies for the domain
2. Open new incognito window
3. Try accessing the service again

```bash
# Alternative: revoke sessions via API (advanced)
# Go to Cloudflare dashboard: https://one.dash.cloudflare.com
# Settings -> Sessions -> Revoke
```

---

## Re-running Setup After Changes

### Scenario
Adding new services or reconfiguring after changes.

### Steps

**1. Add new service to domains.toml:**
```toml
[[services]]
name = "New Service"
subdomain = "newservice"
backend = "192.168.68.135:8080"
enable_https = true
enable_http = false
require_auth = true
```

**2. Apply domain changes:**
```bash
./scripts/manage-domains.sh apply
```
This automatically creates Access application if `require_auth = true`.

**3. Or re-run Access setup manually:**
```bash
./scripts/cf-access-setup.sh setup
```
Script is idempotent - existing applications are skipped.

**4. Verify new application exists:**
```bash
./scripts/cf-access-setup.sh list | grep newservice
```

---

## Testing Access Configuration

### Full Test Procedure

**1. List all applications:**
```bash
./scripts/cf-access-setup.sh list
```

**2. Test protected service (should require login):**
```bash
# From terminal (no auth - should get redirect)
curl -I https://pihole.temet.ai
# Expected: HTTP/2 302 (redirect to login)
```

**3. Test bypass service (should not require login):**
```bash
curl -I https://webhook.temet.ai/hooks/health
# Expected: HTTP/2 200 (or appropriate response)
```

**4. Test from incognito browser:**
1. Open incognito window
2. Go to https://pihole.temet.ai
3. Should see Cloudflare Access login page
4. Click "Google"
5. Sign in with authorized email
6. Should see Pi-hole admin interface

**5. Test unauthorized access:**
1. Sign in with different Google account
2. Should see "Access Denied" message

---

## Checking Access Logs

### Scenario
Reviewing who accessed services and when.

### Via Dashboard

1. Go to: https://one.dash.cloudflare.com
2. Navigate: Logs -> Access
3. Filter options:
   - Application: Select specific service
   - Action: allow, deny, bypass
   - User: Email address
   - Time: Last hour, day, week, etc.

### What Logs Show

| Field | Description |
|-------|-------------|
| Time | When access occurred |
| User | Email of user |
| Application | Which service accessed |
| Action | allow, deny, or bypass |
| Country | User's location |
| IP Address | Source IP |

### Example Log Entry

```
Time: 2025-12-06 10:30:45 UTC
User: dawiddutoit@temet.ai
Application: Pi-hole Admin
Action: allow
Country: ZA
IP: 102.xxx.xxx.xxx
```

### Monitoring for Security

**Check for:**
- Unexpected "deny" entries (unauthorized attempts)
- Access from unexpected countries
- Access at unusual times
- Unknown email addresses

---

## Quick Reference Commands

```bash
# Check prerequisites
cd /home/dawiddutoit/projects/network && source .env && \
  echo "OAuth: ${GOOGLE_OAUTH_CLIENT_ID:+Set}" && \
  echo "Email: ${ACCESS_ALLOWED_EMAIL}"

# Run full setup
./scripts/cf-access-setup.sh setup

# List applications
./scripts/cf-access-setup.sh list

# Update after changing emails
./scripts/update-access-emails.sh

# Delete specific application
./scripts/cf-access-setup.sh delete service.temet.ai

# Test API token
curl -s "https://api.cloudflare.com/client/v4/user/tokens/verify" \
  -H "Authorization: Bearer ${CLOUDFLARE_ACCESS_API_TOKEN}" | jq '.success'

# Quick test (expect redirect to login)
curl -I https://pihole.temet.ai 2>/dev/null | head -1
```
