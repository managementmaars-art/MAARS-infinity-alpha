# Cloudflare Tunnel Setup - Reference Guide

Complete reference for Cloudflare Tunnel configuration, token format, and docker-compose setup.

## Table of Contents

1. [Docker-Compose Service Definition](#docker-compose-service-definition)
2. [Token Format and Structure](#token-format-and-structure)
3. [Environment Variables](#environment-variables)
4. [Ingress Configuration](#ingress-configuration)
5. [Network Architecture](#network-architecture)
6. [Cloudflare Dashboard Navigation](#cloudflare-dashboard-navigation)
7. [API Configuration](#api-configuration)
8. [Troubleshooting Reference](#troubleshooting-reference)

---

## Docker-Compose Service Definition

If cloudflared service is missing from docker-compose.yml, add this definition:

```yaml
services:
  # ... other services ...

  # =============================================================================
  # Cloudflared - Secure Tunnel to Cloudflare
  # =============================================================================
  cloudflared:
    image: cloudflare/cloudflared:latest
    container_name: cloudflared
    restart: unless-stopped
    command: tunnel run
    environment:
      TUNNEL_TOKEN: "${CLOUDFLARE_TUNNEL_TOKEN}"
    networks:
      - default
    depends_on:
      - caddy
      - pihole
```

### Service Configuration Options

| Option | Value | Purpose |
|--------|-------|---------|
| `image` | cloudflare/cloudflared:latest | Official Cloudflare image |
| `command` | tunnel run | Runs tunnel using token-based auth |
| `restart` | unless-stopped | Auto-restart on failure |
| `TUNNEL_TOKEN` | From .env | Authentication token |

### Network Considerations

The cloudflared container must be able to reach:
- Other containers by name (pihole, caddy, webhook)
- Host machine services by IP (not host.docker.internal on Linux)
- External LAN devices by IP

---

## Token Format and Structure

### Token Anatomy

The tunnel token is a base64-encoded JSON object:

```json
{
  "a": "account-id-here",
  "t": "tunnel-id-here",
  "s": "secret-key-here"
}
```

### Decoding Token (for debugging)

```bash
# Extract and decode token
TUNNEL_TOKEN=$(grep "CLOUDFLARE_TUNNEL_TOKEN=" .env | cut -d'=' -f2)
echo "$TUNNEL_TOKEN" | base64 -d | python3 -m json.tool
```

**Expected output:**
```json
{
    "a": "1234567890abcdef1234567890abcdef",
    "t": "a6da6f09-c626-4c1b-b311-5cb4ef19ea11",
    "s": "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnop"
}
```

### Extracting Tunnel ID

```bash
TUNNEL_ID=$(echo "$CLOUDFLARE_TUNNEL_TOKEN" | base64 -d 2>/dev/null | \
  python3 -c "import sys, json; print(json.load(sys.stdin).get('t', ''))")
echo "Tunnel ID: $TUNNEL_ID"
```

---

## Environment Variables

### Required Variables

| Variable | Example | Purpose |
|----------|---------|---------|
| `CLOUDFLARE_TUNNEL_TOKEN` | eyJhIjo... | Tunnel authentication token |

### Optional Variables (for API scripts)

| Variable | Example | Purpose |
|----------|---------|---------|
| `CLOUDFLARE_ACCOUNT_ID` | 1234567890abcdef... | Account identifier |
| `CLOUDFLARE_EMAIL` | user@example.com | Cloudflare account email |
| `CLOUDFLARE_GLOBAL_API_KEY` | abcdef... | Global API key (for scripts) |

### .env Template

```bash
# Cloudflare Tunnel
# Get from: https://one.dash.cloudflare.com -> Access -> Tunnels
CLOUDFLARE_TUNNEL_TOKEN=your-token-here

# Optional: For API-based configuration
CLOUDFLARE_ACCOUNT_ID=your-account-id
CLOUDFLARE_EMAIL=your-email@example.com
CLOUDFLARE_GLOBAL_API_KEY=your-global-api-key
```

---

## Ingress Configuration

### Manual Configuration (Dashboard)

Each public hostname creates an ingress rule:

| Subdomain | Domain | Service Type | URL |
|-----------|--------|--------------|-----|
| pihole | temet.ai | HTTP | pihole:80 |
| jaeger | temet.ai | HTTP | 192.168.68.135:16686 |
| langfuse | temet.ai | HTTP | 192.168.68.135:3000 |
| sprinkler | temet.ai | HTTP | 192.168.68.105:80 |
| ha | temet.ai | HTTP | 192.168.68.123:8123 |
| webhook | temet.ai | HTTP | webhook:9000 |
| (root) | temet.ai | HTTP | caddy:80 |

### API Configuration

Use the script to configure all routes at once:

```bash
./scripts/cf-tunnel-config.sh configure
```

### Ingress Rule Priority

Rules are evaluated in order:
1. Most specific hostname first
2. Catch-all rule last (`http_status:404`)

### Special Origin Request Options

For problematic backends (IoT, self-signed certs):

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

| Option | Purpose |
|--------|---------|
| `noTLSVerify` | Skip TLS certificate verification |
| `connectTimeout` | Seconds to wait for connection |
| `httpHostHeader` | Override Host header sent to origin |

---

## Network Architecture

### Traffic Flow (Remote Access)

```
External User
    |
    v (HTTPS)
Cloudflare Edge
    |
    v (Cloudflare Protocol)
cloudflared container
    |
    +---> pihole:80 (Docker network)
    +---> webhook:9000 (Docker network)
    +---> 192.168.68.135:16686 (Host IP)
    +---> 192.168.68.105:80 (LAN device)
```

### Backend Addressing

| Backend Location | Address Format | Example |
|-----------------|----------------|---------|
| Docker container | container-name:port | pihole:80 |
| Host machine (Linux) | host-ip:port | 192.168.68.135:3000 |
| Host machine (Docker Desktop) | host.docker.internal:port | N/A on Linux |
| LAN device | device-ip:port | 192.168.68.105:80 |

### Finding Host IP

```bash
# Get primary host IP
hostname -I | awk '{print $1}'
# Example output: 192.168.68.135
```

---

## Cloudflare Dashboard Navigation

### Creating a Tunnel

1. **Zero Trust Dashboard:** https://one.dash.cloudflare.com
2. **Navigate:** Access -> Tunnels
3. **Click:** Create a tunnel
4. **Select:** Cloudflared connector type
5. **Name:** Enter tunnel name (e.g., "pi-home")
6. **Install:** Choose Docker, copy token

### Managing Tunnel

1. **Dashboard:** https://one.dash.cloudflare.com
2. **Navigate:** Access -> Tunnels
3. **Click:** Tunnel name
4. **Tabs:**
   - Overview: Status and metrics
   - Configure: Settings
   - Public Hostname: Add/edit routes

### Viewing Tunnel Status

| Status | Meaning |
|--------|---------|
| HEALTHY | All connectors active |
| DEGRADED | Some connectors offline |
| DOWN | No active connectors |
| INACTIVE | Tunnel created but never connected |

### Revoking/Replacing Token

1. Go to tunnel configuration
2. Click "Revoke token" (stops all current connectors)
3. Generate new token
4. Update .env with new token
5. Restart cloudflared container

---

## API Configuration

### Using cf-tunnel-config.sh

```bash
# Show current configuration
./scripts/cf-tunnel-config.sh show

# Update all ingress routes
./scripts/cf-tunnel-config.sh configure
```

### API Endpoint

```
PUT /accounts/{account_id}/cfd_tunnel/{tunnel_id}/configurations
```

### Example API Request

```bash
curl -X PUT \
  "https://api.cloudflare.com/client/v4/accounts/${CLOUDFLARE_ACCOUNT_ID}/cfd_tunnel/${TUNNEL_ID}/configurations" \
  -H "X-Auth-Email: ${CLOUDFLARE_EMAIL}" \
  -H "X-Auth-Key: ${CLOUDFLARE_GLOBAL_API_KEY}" \
  -H "Content-Type: application/json" \
  --data '{
    "config": {
      "ingress": [
        {"hostname": "pihole.temet.ai", "service": "http://pihole:80"},
        {"service": "http_status:404"}
      ]
    }
  }'
```

---

## Troubleshooting Reference

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `token is invalid` | Token corrupted or expired | Re-copy from dashboard |
| `already registered` | Another instance running | Stop other instances |
| `no such host` | Container/host unreachable | Check network/DNS |
| `connection refused` | Service not running | Start backend service |
| `tls: internal error` | Wrong protocol | Use HTTP not HTTPS |

### Diagnostic Commands

```bash
# Check container status
docker ps | grep cloudflared

# View logs
docker logs cloudflared --tail 50

# Check token is set
docker exec cloudflared env | grep TUNNEL_TOKEN

# Test connectivity from container
docker exec cloudflared wget -O- http://pihole:80

# Force restart
docker compose up -d --force-recreate cloudflared
```

### Log Messages Explained

| Message | Meaning |
|---------|---------|
| `Registered tunnel connection` | Successful connection to Cloudflare |
| `connIndex=0..3` | Connection number (4 is healthy) |
| `location=CPT` or `JNB` | Cloudflare edge location (Cape Town, Johannesburg) |
| `Updated to new configuration` | Ingress rules reloaded |
| `ERR` | Error occurred (read message for details) |

### Healthy Tunnel Indicators

```
INF Registered tunnel connection connIndex=0 connection=... location=CPT
INF Registered tunnel connection connIndex=1 connection=... location=CPT
INF Registered tunnel connection connIndex=2 connection=... location=JNB
INF Registered tunnel connection connIndex=3 connection=... location=JNB
```

Four registered connections with multiple edge locations = optimal setup.

---

## Related Resources

- **Cloudflare Tunnel Docs:** https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/
- **Zero Trust Dashboard:** https://one.dash.cloudflare.com
- **Project CLAUDE.md:** `/home/dawiddutoit/projects/network/CLAUDE.md`
- **Troubleshooting Guide:** `/home/dawiddutoit/projects/network/cloudflare/docs/troubleshooting.md`
