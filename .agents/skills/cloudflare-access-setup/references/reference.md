# Cloudflare Access Setup - Reference Guide

Complete technical reference for Cloudflare Access configuration, API details, and troubleshooting.

## Table of Contents

1. [Environment Variables Reference](#environment-variables-reference)
2. [API Token Configuration](#api-token-configuration)
3. [Google OAuth Setup Details](#google-oauth-setup-details)
4. [Script Command Reference](#script-command-reference)
5. [Cloudflare API Endpoints](#cloudflare-api-endpoints)
6. [Troubleshooting Guide](#troubleshooting-guide)
7. [Advanced Configuration](#advanced-configuration)

---

## Environment Variables Reference

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `GOOGLE_OAUTH_CLIENT_ID` | OAuth 2.0 Client ID from Google Console | `123456789.apps.googleusercontent.com` |
| `GOOGLE_OAUTH_CLIENT_SECRET` | OAuth 2.0 Client Secret | `GOCSPX-xxxxx` |
| `ACCESS_ALLOWED_EMAIL` | Email(s) allowed to access services | `user@domain.com` or `user1@domain.com,user2@domain.com` |
| `CLOUDFLARE_ACCESS_API_TOKEN` | API token for Zero Trust configuration | `Xv5MOdOT...` |
| `CLOUDFLARE_ACCOUNT_ID` | Cloudflare account identifier | `abc123def456...` |
| `CLOUDFLARE_TEAM_NAME` | Zero Trust team/organization name | `temetai` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ACCESS_SESSION_DURATION` | How long sessions last | `24h` |

### Retrieving Account Information

**Get Account ID:**
```bash
curl -s -X GET "https://api.cloudflare.com/client/v4/accounts" \
  -H "Authorization: Bearer ${CLOUDFLARE_ACCESS_API_TOKEN}" \
  -H "Content-Type: application/json" | jq -r '.result[0].id'
```

**Get Team Name:**
```bash
curl -s -X GET "https://api.cloudflare.com/client/v4/accounts/${CLOUDFLARE_ACCOUNT_ID}/access/organizations" \
  -H "Authorization: Bearer ${CLOUDFLARE_ACCESS_API_TOKEN}" \
  -H "Content-Type: application/json" | jq -r '.result.name'
```

---

## API Token Configuration

### Creating the Access API Token

1. Go to: https://dash.cloudflare.com/profile/api-tokens
2. Click "Create Token"
3. Select "Custom token"
4. Configure permissions:

**Required Permissions:**

| Resource | Permission Level |
|----------|-----------------|
| Account -> Zero Trust | Edit |
| Account -> Access: Apps and Policies | Edit |
| Account -> Access: Organizations, Identity Providers, and Groups | Edit |

**Optional but Recommended:**

| Resource | Permission Level |
|----------|-----------------|
| Account -> Zero Trust | Read (for listing) |
| Zone -> DNS | Edit (if managing DNS) |

### Token Validation

Test token validity:
```bash
curl -s -X GET "https://api.cloudflare.com/client/v4/user/tokens/verify" \
  -H "Authorization: Bearer ${CLOUDFLARE_ACCESS_API_TOKEN}" | jq '.success'
```

---

## Google OAuth Setup Details

### Consent Screen Configuration

**Internal vs External:**

| Type | Use Case | Requirements |
|------|----------|--------------|
| Internal | Google Workspace users only | Must be same organization |
| External | Personal Gmail accounts | Requires app verification for production |

**For Home Lab (External with Testing):**
- Select "External"
- Add test users manually
- No verification needed for test users

### OAuth Client Configuration

**Authorized JavaScript Origins:** (optional)
- `https://temetai.cloudflareaccess.com`

**Authorized Redirect URIs:** (required)
- `https://temetai.cloudflareaccess.com/cdn-cgi/access/callback`

**Important:** The redirect URI must match exactly, including the team name.

### Common OAuth Errors

| Error | Cause | Solution |
|-------|-------|----------|
| "redirect_uri_mismatch" | URI doesn't match Console | Verify exact URI in Google Console |
| "access_denied" | User not in test users | Add email to test users (External) |
| "invalid_client" | Wrong client ID/secret | Regenerate credentials |
| "org_internal" | Internal app, external user | Change to External type |

---

## Script Command Reference

### cf-access-setup.sh

**Location:** `/home/dawiddutoit/projects/network/scripts/cf-access-setup.sh`

**Commands:**

```bash
# Complete setup (creates IDP, applications, policies)
./scripts/cf-access-setup.sh setup

# List all Access applications
./scripts/cf-access-setup.sh list

# Delete specific application
./scripts/cf-access-setup.sh delete pihole.temet.ai

# Show usage
./scripts/cf-access-setup.sh
```

### Setup Process Flow

```
check_prerequisites()
       |
       v
setup_google_idp()
       |
       v
create_access_app() x N (for each service)
       |
       v
create_allow_policy() x N (for protected services)
       |
       v
create_bypass_policy() (for webhook)
```

### update-access-emails.sh

**Location:** `/home/dawiddutoit/projects/network/scripts/update-access-emails.sh`

Updates policies when ACCESS_ALLOWED_EMAIL changes:
```bash
./scripts/update-access-emails.sh
```

---

## Cloudflare API Endpoints

### Identity Providers

**List IDPs:**
```bash
curl -X GET "https://api.cloudflare.com/client/v4/accounts/${ACCOUNT_ID}/access/identity_providers" \
  -H "Authorization: Bearer ${API_TOKEN}"
```

**Create Google IDP:**
```bash
curl -X POST "https://api.cloudflare.com/client/v4/accounts/${ACCOUNT_ID}/access/identity_providers" \
  -H "Authorization: Bearer ${API_TOKEN}" \
  -H "Content-Type: application/json" \
  --data '{
    "name": "Google OAuth",
    "type": "google",
    "config": {
      "client_id": "'${GOOGLE_CLIENT_ID}'",
      "client_secret": "'${GOOGLE_CLIENT_SECRET}'"
    }
  }'
```

### Access Applications

**List Applications:**
```bash
curl -X GET "https://api.cloudflare.com/client/v4/accounts/${ACCOUNT_ID}/access/apps" \
  -H "Authorization: Bearer ${API_TOKEN}"
```

**Create Application:**
```bash
curl -X POST "https://api.cloudflare.com/client/v4/accounts/${ACCOUNT_ID}/access/apps" \
  -H "Authorization: Bearer ${API_TOKEN}" \
  -H "Content-Type: application/json" \
  --data '{
    "name": "Service Name",
    "domain": "service.temet.ai",
    "type": "self_hosted",
    "session_duration": "24h",
    "allowed_idps": ["'${IDP_ID}'"],
    "auto_redirect_to_identity": true,
    "http_only_cookie_attribute": true,
    "same_site_cookie_attribute": "lax"
  }'
```

**Delete Application:**
```bash
curl -X DELETE "https://api.cloudflare.com/client/v4/accounts/${ACCOUNT_ID}/access/apps/${APP_ID}" \
  -H "Authorization: Bearer ${API_TOKEN}"
```

### Access Policies

**List Policies for App:**
```bash
curl -X GET "https://api.cloudflare.com/client/v4/accounts/${ACCOUNT_ID}/access/apps/${APP_ID}/policies" \
  -H "Authorization: Bearer ${API_TOKEN}"
```

**Create Allow Policy:**
```bash
curl -X POST "https://api.cloudflare.com/client/v4/accounts/${ACCOUNT_ID}/access/apps/${APP_ID}/policies" \
  -H "Authorization: Bearer ${API_TOKEN}" \
  -H "Content-Type: application/json" \
  --data '{
    "name": "Allow user@domain.com",
    "decision": "allow",
    "include": [
      {"email": {"email": "user@domain.com"}}
    ]
  }'
```

**Create Bypass Policy:**
```bash
curl -X POST "https://api.cloudflare.com/client/v4/accounts/${ACCOUNT_ID}/access/apps/${APP_ID}/policies" \
  -H "Authorization: Bearer ${API_TOKEN}" \
  -H "Content-Type: application/json" \
  --data '{
    "name": "Bypass All",
    "decision": "bypass",
    "include": [{"everyone": {}}]
  }'
```

---

## Troubleshooting Guide

### Diagnostic Commands

**Check current Access applications:**
```bash
./scripts/cf-access-setup.sh list
```

**Verify OAuth credentials in .env:**
```bash
cd /home/dawiddutoit/projects/network && source .env
echo "Client ID: ${GOOGLE_OAUTH_CLIENT_ID:0:20}..."
echo "Client Secret: ${GOOGLE_OAUTH_CLIENT_SECRET:0:10}..."
echo "Allowed Email: ${ACCESS_ALLOWED_EMAIL}"
```

**Test API token:**
```bash
source .env && curl -s "https://api.cloudflare.com/client/v4/user/tokens/verify" \
  -H "Authorization: Bearer ${CLOUDFLARE_ACCESS_API_TOKEN}" | jq '.success'
```

### Common Issues

#### "Access Denied" Error

**Symptoms:** User sees "Access Denied" when trying to access service

**Causes:**
1. Email not in allowed list
2. Using wrong Google account
3. Policy not created

**Solutions:**
```bash
# Check allowed emails
source .env && echo $ACCESS_ALLOWED_EMAIL

# Update if needed
# Edit .env, then:
./scripts/update-access-emails.sh

# Or re-run full setup
./scripts/cf-access-setup.sh setup
```

#### OAuth Redirect Loop

**Symptoms:** Browser keeps redirecting between Google and service

**Causes:**
1. Cookies blocked
2. Wrong redirect URI
3. Session issues

**Solutions:**
1. Clear browser cookies for the domain
2. Use incognito window
3. Verify redirect URI matches exactly

#### "Can only be used within its organization"

**Symptoms:** Error when non-workspace user tries to login

**Cause:** OAuth consent screen set to "Internal"

**Solution:**
1. Go to: https://console.cloud.google.com/apis/credentials/consent
2. Change from "Internal" to "External"
3. Add users to test users list (if in testing mode)

#### Pi-hole Blocking Google Domains

**Symptoms:** OAuth fails with cookie or session errors

**Cause:** Pi-hole blocking required Google domains

**Solution:**
```bash
docker exec pihole pihole allow accounts.google.com accounts.google.co.uk \
  ssl.gstatic.com www.googleapis.com apis.google.com gstatic.com www.gstatic.com \
  google.com www.google.com www.google.co.uk googleusercontent.com \
  clients1.google.com clients2.google.com clients3.google.com \
  clients4.google.com clients5.google.com clients6.google.com

docker exec pihole pihole reloaddns
```

#### Application Not Created

**Symptoms:** Service not appearing in list

**Cause:** API error during creation (often silent)

**Solution:**
```bash
# Re-run setup (idempotent)
./scripts/cf-access-setup.sh setup

# Or check for API errors
./scripts/cf-access-setup.sh setup 2>&1 | grep -i error
```

---

## Advanced Configuration

### Multiple Allowed Users

```bash
# In .env
ACCESS_ALLOWED_EMAIL="user1@domain.com,user2@domain.com,user3@gmail.com"
```

Then update policies:
```bash
./scripts/update-access-emails.sh
```

### Custom Session Duration

Edit the application after creation via Cloudflare dashboard:
1. Go to: https://one.dash.cloudflare.com
2. Access -> Applications
3. Click application -> Edit
4. Change "Session Duration"

Options: 30m, 1h, 6h, 12h, 24h, 1w

### Adding New Services

When adding a new service that needs Access protection:

1. Add to domains.toml with `require_auth = true`
2. Run: `./scripts/manage-domains.sh apply`
3. Or manually: `./scripts/cf-access-setup.sh setup`

### Revoking Access

**Remove user from all applications:**
```bash
# Edit .env to remove email from ACCESS_ALLOWED_EMAIL
# Then:
./scripts/update-access-emails.sh
```

**Revoke active sessions:**
1. Go to: https://one.dash.cloudflare.com
2. Settings -> Sessions
3. Revoke sessions for specific user

### Access Logs Query

View recent access attempts via dashboard:
1. https://one.dash.cloudflare.com
2. Logs -> Access
3. Filter by:
   - Application
   - User email
   - Decision (allow/deny)
   - Time range

### Service Tokens (Machine-to-Machine)

For automated access without user login:

1. Go to: Access -> Service Auth
2. Create Service Token
3. Use token in requests:
```bash
curl -H "CF-Access-Client-Id: ${CLIENT_ID}" \
     -H "CF-Access-Client-Secret: ${CLIENT_SECRET}" \
     https://service.temet.ai/api/endpoint
```

---

## Security Best Practices

1. **Rotate OAuth credentials periodically** - Regenerate in Google Console
2. **Use specific email policies** - Don't use wildcards unless necessary
3. **Monitor access logs** - Check for unauthorized attempts
4. **Keep API tokens scoped** - Minimum permissions needed
5. **Use incognito for testing** - Avoid session confusion
6. **Enable MFA on Google accounts** - Additional security layer
7. **Review allowed users regularly** - Remove inactive accounts
