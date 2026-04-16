# Cloudflare Tunnel Setup - Examples

Common setup scenarios and configurations for Cloudflare Tunnel.

## Table of Contents

1. [Fresh Installation](#1-fresh-installation)
2. [Token Replacement](#2-token-replacement)
3. [Multi-Service Configuration](#3-multi-service-configuration)
4. [IoT Device Configuration](#4-iot-device-configuration)
5. [Verification Examples](#5-verification-examples)

---

## 1. Fresh Installation

### Scenario
Setting up Cloudflare Tunnel on a new Raspberry Pi installation.

### Step-by-Step

**1. Verify .env exists:**
```bash
ls -la /home/dawiddutoit/projects/network/.env
# If missing: cp .env.example .env
```

**2. Create tunnel in dashboard:**
- Go to: https://one.dash.cloudflare.com
- Access -> Tunnels -> Create tunnel
- Name: "pi-home"
- Connector: Docker
- Copy token (eyJhIjo...)

**3. Add token to .env:**
```bash
# Edit .env and add:
CLOUDFLARE_TUNNEL_TOKEN=eyJhIjoiMTIzNDU2Nzg5MGFiY2RlZjEyMzQ1Njc4OTBhYmNkZWYiLCJ0IjoiYTZkYTZmMDktYzYyNi00YzFiLWIzMTEtNWNiNGVmMTllYTExIiwicyI6IkFCQ0RFRkdISUpLTE1OT1BRUlNUVVZXWFlaYWJjZGVmZ2hpamtsbW5vcCJ9
```

**4. Start container:**
```bash
cd /home/dawiddutoit/projects/network
docker compose up -d cloudflared
```

**5. Verify connection:**
```bash
docker logs cloudflared --tail 20
# Look for: "Registered tunnel connection connIndex=0"
```

**6. Configure hostnames in dashboard:**
- Pi-hole: pihole.temet.ai -> HTTP -> pihole:80
- Webhook: webhook.temet.ai -> HTTP -> webhook:9000

---

## 2. Token Replacement

### Scenario
Existing token is invalid or needs to be rotated for security.

### Step-by-Step

**1. Check current status:**
```bash
docker logs cloudflared --tail 10
# If shows "token is invalid" - token needs replacement
```

**2. Generate new token:**
- Go to: https://one.dash.cloudflare.com
- Access -> Tunnels -> Your tunnel
- Configure -> Revoke and generate new token
- Copy new token

**3. Update .env:**
```bash
# Use Edit tool to replace CLOUDFLARE_TUNNEL_TOKEN value
# Old: CLOUDFLARE_TUNNEL_TOKEN=old-invalid-token
# New: CLOUDFLARE_TUNNEL_TOKEN=new-valid-token
```

**4. Restart container:**
```bash
docker compose restart cloudflared
```

**5. Verify new connection:**
```bash
docker logs cloudflared --tail 20
# Should show: "Registered tunnel connection"
```

### Example .env Update

Before:
```bash
CLOUDFLARE_TUNNEL_TOKEN=eyJhIjoib2xkLWludmFsaWQtdG9rZW4ifQ==
```

After:
```bash
CLOUDFLARE_TUNNEL_TOKEN=eyJhIjoiMTIzNDU2Nzg5MGFiY2RlZjEyMzQ1Njc4OTBhYmNkZWYiLCJ0IjoiYTZkYTZmMDktYzYyNi00YzFiLWIzMTEtNWNiNGVmMTllYTExIiwicyI6IkFCQ0RFRkdISUpLTE1OT1BRUlNUVVZXWFlaYWJjZGVmZ2hpamtsbW5vcCJ9
```

---

## 3. Multi-Service Configuration

### Scenario
Setting up tunnel access to multiple services at once.

### Dashboard Configuration

| Subdomain | Domain | Type | URL | Notes |
|-----------|--------|------|-----|-------|
| pihole | temet.ai | HTTP | pihole:80 | Docker container |
| jaeger | temet.ai | HTTP | 192.168.68.135:16686 | Host service |
| langfuse | temet.ai | HTTP | 192.168.68.135:3000 | Host service |
| ha | temet.ai | HTTP | 192.168.68.123:8123 | External Pi |
| webhook | temet.ai | HTTP | webhook:9000 | Docker container |
| (empty) | temet.ai | HTTP | caddy:80 | Root domain |

### API Configuration Alternative

```bash
./scripts/cf-tunnel-config.sh configure
```

This updates all routes via API with the predefined configuration.

### Expected Tunnel Config (show command output)

```
Tunnel configuration (Version: 15)

Ingress Rules:
  1. temet.ai                        -> http://caddy:80
  2. pihole.temet.ai                 -> http://pihole:80
  3. jaeger.temet.ai                 -> http://192.168.68.135:16686
  4. langfuse.temet.ai               -> http://192.168.68.135:3000
  5. sprinkler.temet.ai              -> http://192.168.68.105:80
  6. ha.temet.ai                     -> http://192.168.68.123:8123
  7. webhook.temet.ai                -> http://webhook:9000
  8. (catch-all)                     -> http_status:404
```

---

## 4. IoT Device Configuration

### Scenario
Adding an IoT device (like OpenSprinkler) that has special requirements.

### Issue
IoT devices often:
- Cannot handle Cloudflare headers
- Have slow response times
- Use HTTP only

### Dashboard Configuration

For sprinkler.temet.ai:
1. Subdomain: sprinkler
2. Domain: temet.ai
3. Type: HTTP
4. URL: 192.168.68.105:80

Then expand "Additional application settings":
- TLS: No TLS Verify (check)
- HTTP Settings: Connection Timeout: 30s

### API Configuration (with origin request options)

```json
{
    "hostname": "sprinkler.temet.ai",
    "service": "http://192.168.68.105:80",
    "originRequest": {
        "noTLSVerify": true,
        "connectTimeout": 30,
        "httpHostHeader": "sprinkler.temet.ai"
    }
}
```

### Verification

```bash
# Test from external network
curl -I https://sprinkler.temet.ai
# Should return: HTTP/2 302 (redirect to Cloudflare Access)
# Or HTTP/2 200 if no auth required
```

---

## 5. Verification Examples

### Example 1: Check Token Validity

```bash
# Extract and validate token
TUNNEL_TOKEN=$(grep "CLOUDFLARE_TUNNEL_TOKEN=" /home/dawiddutoit/projects/network/.env | cut -d'=' -f2)

# Decode and display
echo "$TUNNEL_TOKEN" | base64 -d 2>/dev/null | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print('Token Status: VALID')
    print(f'Account ID: {d.get(\"a\", \"unknown\")[:8]}...')
    print(f'Tunnel ID: {d.get(\"t\", \"unknown\")}')
except:
    print('Token Status: INVALID')
"
```

**Expected output (valid):**
```
Token Status: VALID
Account ID: 12345678...
Tunnel ID: a6da6f09-c626-4c1b-b311-5cb4ef19ea11
```

### Example 2: Check Container Status

```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep cloudflared
```

**Expected output:**
```
cloudflared   Up 5 hours
```

### Example 3: Check Tunnel Connections

```bash
docker logs cloudflared 2>&1 | grep -E "Registered tunnel|connIndex" | tail -4
```

**Expected output (healthy):**
```
INF Registered tunnel connection connIndex=0 connection=abc123 location=CPT
INF Registered tunnel connection connIndex=1 connection=def456 location=CPT
INF Registered tunnel connection connIndex=2 connection=ghi789 location=JNB
INF Registered tunnel connection connIndex=3 connection=jkl012 location=JNB
```

### Example 4: Test Service Reachability from Tunnel

```bash
# Test if tunnel can reach Pi-hole
docker exec cloudflared wget -q -O- http://pihole:80 | head -5

# Test if tunnel can reach host service
docker exec cloudflared wget -q -O- http://192.168.68.135:16686 | head -5
```

### Example 5: Full Diagnostic

```bash
echo "=== Token Check ==="
grep "CLOUDFLARE_TUNNEL_TOKEN" /home/dawiddutoit/projects/network/.env | cut -c1-50

echo -e "\n=== Container Status ==="
docker ps | grep cloudflared

echo -e "\n=== Connection Status ==="
docker logs cloudflared 2>&1 | grep "Registered tunnel" | tail -4

echo -e "\n=== Ingress Config ==="
./scripts/cf-tunnel-config.sh show 2>/dev/null || echo "Script not available"
```

---

## Common Patterns

### Pattern: Token Not Set

**Symptom:**
```bash
docker logs cloudflared
# Shows: TUNNEL_TOKEN environment variable not set
```

**Fix:**
1. Verify .env has CLOUDFLARE_TUNNEL_TOKEN
2. Restart container: `docker compose restart cloudflared`

### Pattern: Container Restarts Repeatedly

**Symptom:**
```bash
docker ps
# Shows: Restarting (1) 5 seconds ago
```

**Fix:**
1. Check logs: `docker logs cloudflared`
2. Usually indicates invalid token
3. Re-copy token from dashboard

### Pattern: Services Return 502

**Symptom:**
- Tunnel connected (4 connections)
- But services show "Bad Gateway"

**Fix:**
1. Verify service is running: `docker ps | grep pihole`
2. Test from tunnel: `docker exec cloudflared wget -O- http://pihole:80`
3. Check ingress URL is correct (HTTP not HTTPS)
