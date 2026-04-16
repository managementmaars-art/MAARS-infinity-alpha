# Troubleshoot HTTPS - Reference Guide

Complete technical reference for HTTPS/SSL certificate troubleshooting, API token creation, and advanced diagnostics.

## Table of Contents

1. [Error Message Reference](#error-message-reference)
2. [API Token Creation Guide](#api-token-creation-guide)
3. [Cloudflare DNS Plugin Details](#cloudflare-dns-plugin-details)
4. [Let's Encrypt Rate Limits](#lets-encrypt-rate-limits)
5. [Certificate Lifecycle](#certificate-lifecycle)
6. [Advanced Diagnostics](#advanced-diagnostics)
7. [Recovery Procedures](#recovery-procedures)

---

## Error Message Reference

### Caddy Log Errors

#### "Invalid format for Authorization header"

**Full error:**
```
ERR Invalid format for Authorization header
```

**Root cause:** Using Cloudflare Global API Key instead of API Token.

**Diagnosis:**
```bash
# Check what type of key is being used
docker exec caddy env | grep CLOUDFLARE_API_KEY | head -c 20
```

- If starts with `v4:` or is a 37-character hex string -> Global API Key (WRONG)
- If alphanumeric string without prefix -> API Token (CORRECT)

**Technical explanation:**
The Caddy Cloudflare DNS plugin expects a scoped API Token, not the legacy Global API Key. The authentication header format differs:
- API Token: `Authorization: Bearer <token>`
- Global API Key: `X-Auth-Key: <key>` + `X-Auth-Email: <email>`

The plugin only supports the Bearer token format.

---

#### "missing API token"

**Full error:**
```
ERR error obtaining certificate {"error": "missing API token"}
```

**Root cause:** `CLOUDFLARE_API_KEY` environment variable not passed to container.

**Diagnosis:**
```bash
# Check if env var exists in container
docker exec caddy env | grep CLOUDFLARE_API_KEY

# Check if .env has the variable
grep CLOUDFLARE_API_KEY /home/dawiddutoit/projects/network/.env

# Check docker-compose.yml passes it
grep -A10 "caddy:" /home/dawiddutoit/projects/network/docker-compose.yml | grep -A5 environment
```

**Fix:** Ensure docker-compose.yml has:
```yaml
caddy:
  environment:
    CLOUDFLARE_API_KEY: "${CLOUDFLARE_API_KEY}"
```

Then recreate: `docker compose up -d --force-recreate caddy`

---

#### "unknown directive 'dns'"

**Full error:**
```
unknown directive 'dns'
```

**Root cause:** Cloudflare DNS plugin not compiled into Caddy binary.

**Diagnosis:**
```bash
# List all modules - should include dns.providers.cloudflare
docker exec caddy caddy list-modules | grep -E "dns|cloudflare"
```

**Expected output:**
```
dns.providers.cloudflare
```

**If missing:** The custom Dockerfile didn't build correctly or standard Caddy image was used.

**Fix:**
```bash
cd /home/dawiddutoit/projects/network
docker compose build --no-cache caddy
docker compose up -d --force-recreate caddy
```

---

#### "certificate obtain error" / "ACME challenge failed"

**Full error:**
```
ERR certificate obtain error {"error": "ACME challenge failed"}
```

**Possible causes:**
1. DNS propagation delay (TXT record not visible yet)
2. Cloudflare API rate limit hit
3. Let's Encrypt rate limit hit
4. Network connectivity issue

**Diagnosis:**
```bash
# Check if TXT record was created (during challenge)
dig TXT _acme-challenge.pihole.temet.ai @1.1.1.1

# Check Cloudflare API connectivity
curl -s -X GET "https://api.cloudflare.com/client/v4/user/tokens/verify" \
  -H "Authorization: Bearer $(grep CLOUDFLARE_API_KEY /home/dawiddutoit/projects/network/.env | cut -d'"' -f2)" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['result']['status'])"
```

**Fix:** Wait 5 minutes and restart Caddy:
```bash
sleep 300
docker compose restart caddy
```

---

#### "403 Forbidden" from Cloudflare API

**Root cause:** API token doesn't have correct permissions.

**Required permissions:**
- Zone -> DNS -> Edit
- Zone Resources -> Include -> Specific zone -> temet.ai

**Diagnosis:**
```bash
# Verify token permissions
curl -s -X GET "https://api.cloudflare.com/client/v4/user/tokens/verify" \
  -H "Authorization: Bearer $(grep CLOUDFLARE_API_KEY /home/dawiddutoit/projects/network/.env | cut -d'"' -f2)" \
  | python3 -m json.tool
```

**Fix:** Create new token with correct permissions (see API Token Creation Guide below).

---

#### Container Restart Loop

**Symptoms:**
- `docker ps` shows Caddy restarting repeatedly
- Logs show errors immediately on startup

**Diagnosis:**
```bash
# Watch container status
docker ps | grep caddy

# Get recent logs
docker logs caddy --tail 100 2>&1 | tail -50

# Common causes
docker logs caddy 2>&1 | grep -E "error|Caddyfile|syntax"
```

**Common causes:**
1. Caddyfile syntax error
2. Port already in use
3. Volume permission issues

---

## API Token Creation Guide

### Step-by-Step Instructions

1. **Access Cloudflare Dashboard**
   - URL: https://dash.cloudflare.com/profile/api-tokens

2. **Create Token**
   - Click "Create Token"
   - Select template: "Edit zone DNS"

3. **Configure Permissions**
   ```
   Permissions:
   - Zone | DNS | Edit

   Zone Resources:
   - Include | Specific zone | temet.ai
   ```

4. **Optional Security** (recommended)
   ```
   Client IP Address Filtering:
   - Is in | <your-home-public-IP>

   TTL:
   - Start Date: (leave empty for immediate)
   - End Date: (leave empty for no expiry)
   ```

5. **Create and Copy**
   - Click "Continue to summary"
   - Click "Create Token"
   - **Copy immediately** - shown only once!

6. **Update .env**
   ```bash
   # Edit .env
   nano /home/dawiddutoit/projects/network/.env

   # Set the new token
   CLOUDFLARE_API_KEY="your-new-token-here"
   ```

7. **Apply Change**
   ```bash
   docker compose -f /home/dawiddutoit/projects/network/docker-compose.yml up -d --force-recreate caddy
   ```

### Token Verification

```bash
# Verify token is valid
curl -s -X GET "https://api.cloudflare.com/client/v4/user/tokens/verify" \
  -H "Authorization: Bearer $(grep CLOUDFLARE_API_KEY /home/dawiddutoit/projects/network/.env | cut -d'"' -f2)" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('Status:', d['result']['status'])"
```

Expected: `Status: active`

---

## Cloudflare DNS Plugin Details

### How DNS-01 Challenge Works

```
1. Caddy requests certificate from Let's Encrypt for pihole.temet.ai
2. Let's Encrypt responds with challenge token
3. Caddy creates TXT record via Cloudflare API:
   _acme-challenge.pihole.temet.ai TXT "challenge-token"
4. Let's Encrypt queries DNS for TXT record
5. Let's Encrypt verifies token matches
6. Certificate issued to Caddy
7. Caddy deletes TXT record
8. Certificate stored in caddy_data volume
```

### Why DNS-01?

- Works for internal services (not exposed to internet)
- No need to open ports 80/443 publicly
- Works behind NAT/CGNAT
- Supports wildcard certificates

### Plugin Source

- Repository: https://github.com/caddy-dns/cloudflare
- Module name: `dns.providers.cloudflare`

### Custom Dockerfile

```dockerfile
FROM caddy:2-builder AS builder

RUN xcaddy build \
    --with github.com/caddy-dns/cloudflare

FROM caddy:2-alpine

COPY --from=builder /usr/bin/caddy /usr/bin/caddy
```

---

## Let's Encrypt Rate Limits

### Current Limits (as of 2024)

| Limit Type | Value | Window |
|------------|-------|--------|
| Certificates per Registered Domain | 50 | per week |
| Duplicate Certificates | 5 | per week |
| Failed Validations | 5 | per hour |
| New Orders | 300 | per 3 hours |

### Check Your Usage

```bash
# View certificates issued for domain
# https://crt.sh/?q=temet.ai

# Count recent certificates
curl -s "https://crt.sh/?q=temet.ai&output=json" | \
  python3 -c "import sys,json; certs=json.load(sys.stdin); print(f'Total: {len(certs)} certificates')"
```

### Avoiding Rate Limits

1. **Don't delete caddy_data volume unnecessarily**
   - Certificates persist here
   - Deleting forces re-issuance

2. **Use staging for testing** (add to Caddyfile global options):
   ```caddyfile
   {
     acme_ca https://acme-staging-v02.api.letsencrypt.org/directory
   }
   ```

3. **Wait before retrying**
   - Failed validation: wait 1 hour
   - Rate limit: wait until window resets (check crt.sh)

---

## Certificate Lifecycle

### Timeline

```
Day 0:   Certificate issued (valid 90 days)
Day 60:  Caddy begins renewal attempts (30 days before expiry)
Day 89:  Certificate expires if renewal failed
```

### Auto-Renewal Process

- Caddy checks certificates every 12 hours
- Renewal starts 30 days before expiry
- If renewal fails, Caddy retries on next check
- Logs show: `renewed successfully`

### Manual Renewal

```bash
# Force renewal by removing certificates
docker compose down caddy
docker volume rm network_caddy_data
docker volume create network_caddy_data
docker compose up -d caddy

# Watch for new certificates
docker logs caddy -f | grep "certificate obtained"
```

### Certificate Storage

```bash
# Location in container
/data/caddy/certificates/acme-v02.api.letsencrypt.org-directory/

# Docker volume
docker volume inspect network_caddy_data
```

---

## Advanced Diagnostics

### Full Diagnostic Script

```bash
#!/bin/bash
echo "=== HTTPS Diagnostic Report ==="
echo "Generated: $(date)"
echo

echo "=== 1. Container Status ==="
docker ps | grep -E "caddy|NAMES"
echo

echo "=== 2. Environment Variables ==="
docker exec caddy env | grep -E "CLOUDFLARE|EMAIL" | sed 's/=.*/=<REDACTED>/'
echo

echo "=== 3. DNS Plugin Status ==="
docker exec caddy caddy list-modules 2>/dev/null | grep cloudflare || echo "MISSING: cloudflare plugin not found"
echo

echo "=== 4. Caddyfile Validation ==="
docker exec caddy caddy validate --config /etc/caddy/Caddyfile 2>&1 || echo "FAILED: Caddyfile syntax error"
echo

echo "=== 5. Recent Certificate Events ==="
docker logs caddy 2>&1 | grep -i "certificate" | tail -10
echo

echo "=== 6. Recent Errors ==="
docker logs caddy 2>&1 | grep -E "error|ERR|failed" | tail -10
echo

echo "=== 7. Certificate Status ==="
for domain in pihole jaeger langfuse sprinkler ha; do
  echo "--- $domain.temet.ai ---"
  timeout 5 bash -c "echo | openssl s_client -servername $domain.temet.ai -connect $domain.temet.ai:443 2>/dev/null | openssl x509 -noout -dates 2>&1" || echo "FAILED"
done
echo

echo "=== 8. Cloudflare API Test ==="
if [ -f /home/dawiddutoit/projects/network/.env ]; then
  TOKEN=$(grep CLOUDFLARE_API_KEY /home/dawiddutoit/projects/network/.env | cut -d'"' -f2)
  curl -s -X GET "https://api.cloudflare.com/client/v4/user/tokens/verify" \
    -H "Authorization: Bearer $TOKEN" 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print('API Token Status:', d.get('result',{}).get('status','unknown'))" 2>/dev/null || echo "API check failed"
fi
echo

echo "=== End Diagnostic Report ==="
```

### Debug Logging

Enable verbose logging in Caddyfile:

```caddyfile
{
  debug
  email {env.CLOUDFLARE_EMAIL}
}
```

Then restart Caddy and watch logs:

```bash
docker logs caddy -f 2>&1 | grep -v "handled request"
```

---

## Recovery Procedures

### Complete Reset

Use only as last resort (will re-obtain all certificates):

```bash
cd /home/dawiddutoit/projects/network

# Stop Caddy
docker compose stop caddy

# Remove data volume
docker volume rm network_caddy_data

# Recreate volume
docker volume create network_caddy_data

# Rebuild Caddy (optional, if plugin issues)
docker compose build --no-cache caddy

# Start Caddy
docker compose up -d caddy

# Monitor certificate acquisition
docker logs caddy -f 2>&1 | grep -E "certificate|error"
```

### Restore from Backup

```bash
# If you have a caddy backup
docker compose stop caddy
docker volume rm network_caddy_data
docker volume create network_caddy_data
sudo tar -xzf caddy-backup-YYYYMMDD.tar.gz \
  -C /var/lib/docker/volumes/network_caddy_data/_data
docker compose start caddy
```

### Token Rotation

```bash
# 1. Create new token in Cloudflare dashboard

# 2. Update .env
nano /home/dawiddutoit/projects/network/.env
# Change CLOUDFLARE_API_KEY to new token

# 3. Recreate Caddy container
docker compose -f /home/dawiddutoit/projects/network/docker-compose.yml up -d --force-recreate caddy

# 4. Verify new token works
docker logs caddy 2>&1 | grep -E "certificate|error" | tail -10

# 5. Delete old token in Cloudflare dashboard
```

---

## Quick Command Reference

```bash
# Check API key in container
docker exec caddy env | grep CLOUDFLARE_API_KEY

# Verify plugin installed
docker exec caddy caddy list-modules | grep cloudflare

# View certificate logs
docker logs caddy 2>&1 | grep -i certificate

# Validate Caddyfile
docker exec caddy caddy validate --config /etc/caddy/Caddyfile

# Test certificate for domain
echo | openssl s_client -servername pihole.temet.ai -connect pihole.temet.ai:443 2>/dev/null | openssl x509 -noout -dates -issuer

# Recreate Caddy container
docker compose -f /home/dawiddutoit/projects/network/docker-compose.yml up -d --force-recreate caddy

# Rebuild Caddy with plugin
docker compose -f /home/dawiddutoit/projects/network/docker-compose.yml build --no-cache caddy

# Watch Caddy logs
docker logs caddy -f

# Full restart
docker compose -f /home/dawiddutoit/projects/network/docker-compose.yml restart caddy
```

---

**Last Updated:** December 2025
**Caddy Version:** 2.10.2
**Plugin:** caddy-dns/cloudflare
