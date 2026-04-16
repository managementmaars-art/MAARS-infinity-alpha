# Add Subdomain - Reference Guide

Complete reference for all configuration options, validation rules, and advanced patterns.

## Table of Contents

1. [Configuration Field Reference](#configuration-field-reference)
2. [Validation Rules](#validation-rules)
3. [Service Type Matrix](#service-type-matrix)
4. [Backend Format Guide](#backend-format-guide)
5. [Advanced Configuration Options](#advanced-configuration-options)
6. [Cloudflare Tunnel Routing](#cloudflare-tunnel-routing)
7. [Troubleshooting Reference](#troubleshooting-reference)

---

## Configuration Field Reference

### Required Fields

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `name` | string | Human-readable service name | Non-empty, descriptive |
| `subdomain` | string | Subdomain portion (without .temet.ai) | Lowercase, alphanumeric + hyphens, max 63 chars, empty string for root domain |
| `backend` | string | Target service address | IP:port or container:port format |

### Routing Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `enable_https` | boolean | false | Create HTTPS block in Caddyfile (local access with cert) |
| `enable_http` | boolean | false | Add to HTTP block (tunnel-only access) |

**Routing Decision Matrix:**

| enable_https | enable_http | Use Case |
|--------------|-------------|----------|
| true | false | Standard web service (local HTTPS) |
| false | true | IoT device / tunnel-only service |
| true | true | Service needs both paths (rare) |
| false | false | Invalid - service unreachable |

### DNS Configuration

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `dns_ip` | string | global.pi_ip | IP for Pi-hole DNS resolution |

**Common DNS IP Values:**
- `192.168.68.135` - Services on the Pi itself
- `192.168.68.XXX` - Services on other LAN devices
- Device's actual IP for IoT devices (so local access is direct)

### Authentication

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `require_auth` | boolean | false | Enable Cloudflare Access with Google OAuth |

**Authentication Considerations:**
- Set `true` for all internal services
- Set `false` only for services that must be publicly accessible (webhooks, APIs)
- Authentication applies to remote access via Cloudflare Tunnel
- Local access (on home network) bypasses Cloudflare Access

### Advanced Caddy Options

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `root_redirect` | string | none | Redirect `/` to specified path |
| `proxy_headers` | boolean | false | Add X-Forwarded-* headers |
| `strip_cf_headers` | boolean | false | Remove Cloudflare headers (for IoT) |
| `tls_insecure` | boolean | false | Skip TLS verification for backend |
| `custom_caddy` | string | none | Custom Caddy directives |

---

## Validation Rules

### Subdomain Validation

```python
import re

def validate_subdomain(subdomain: str) -> tuple[bool, str]:
    """
    Validate subdomain according to DNS rules.
    Returns (is_valid, error_message).
    """
    # Empty string is valid (root domain)
    if subdomain == "":
        return True, ""

    # Check length
    if len(subdomain) > 63:
        return False, "Subdomain must be 63 characters or less"

    # Check format: lowercase alphanumeric, can contain hyphens
    # Must not start or end with hyphen
    pattern = r'^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$'
    if not re.match(pattern, subdomain):
        if subdomain != subdomain.lower():
            return False, "Subdomain must be lowercase"
        if subdomain.startswith('-') or subdomain.endswith('-'):
            return False, "Subdomain cannot start or end with hyphen"
        return False, "Subdomain must contain only lowercase letters, numbers, and hyphens"

    return True, ""
```

### IP Address Validation

```python
import re

def validate_ip(ip: str) -> tuple[bool, str]:
    """
    Validate IPv4 address format.
    """
    pattern = r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$'
    match = re.match(pattern, ip)
    if not match:
        return False, "Invalid IP address format"

    octets = [int(g) for g in match.groups()]
    for i, octet in enumerate(octets):
        if octet < 0 or octet > 255:
            return False, f"IP octet {i+1} out of range (0-255)"

    # Warn about special addresses
    if octets[0] == 127:
        return True, "Warning: localhost address - may not work from other hosts"
    if octets[0] == 0:
        return False, "Invalid IP address (0.x.x.x)"

    return True, ""
```

### Port Validation

```python
def validate_port(port: str) -> tuple[bool, str]:
    """
    Validate port number.
    """
    try:
        port_num = int(port)
        if port_num < 1 or port_num > 65535:
            return False, "Port must be between 1 and 65535"
        if port_num < 1024:
            return True, "Note: privileged port (requires root)"
        return True, ""
    except ValueError:
        return False, "Port must be a number"
```

### Backend Format Validation

```python
def validate_backend(backend: str) -> tuple[bool, str, str]:
    """
    Validate backend format and determine type.
    Returns (is_valid, error_message, backend_type).
    backend_type: 'ip', 'container', or 'special'
    """
    # Special backends
    if backend.startswith("file_server:"):
        return True, "", "special"

    # Must have :port
    if ':' not in backend:
        return False, "Backend must include port (format: address:port)", ""

    address, port = backend.rsplit(':', 1)

    # Validate port
    valid, msg = validate_port(port)
    if not valid:
        return False, msg, ""

    # Check if IP address
    ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if re.match(ip_pattern, address):
        valid, msg = validate_ip(address)
        return valid, msg, "ip"

    # Must be container name
    container_pattern = r'^[a-z0-9][a-z0-9_-]*$'
    if re.match(container_pattern, address, re.IGNORECASE):
        return True, "", "container"

    return False, "Invalid backend format. Use IP:port or container:port", ""
```

### Duplicate Check

```bash
# Check if subdomain already exists in domains.toml
check_duplicate() {
    local subdomain="$1"
    local config_file="/home/dawiddutoit/projects/network/domains.toml"

    if grep -qE "^subdomain = \"${subdomain}\"$" "$config_file"; then
        echo "ERROR: Subdomain '${subdomain}' already exists"
        return 1
    fi
    return 0
}
```

---

## Service Type Matrix

Quick reference for choosing settings based on service type:

| Service Type | enable_https | enable_http | require_auth | strip_cf_headers | tls_insecure | proxy_headers |
|-------------|--------------|-------------|--------------|------------------|--------------|---------------|
| Web App | true | false | true | false | false | true |
| Docker Container | true | false | true | false | false | false |
| IoT Device | false | true | true | true | false | false |
| Self-Signed Cert | true | false | true | false | true | false |
| Public API | false | true | false | false | false | false |
| External LAN | true | false | true | false | false | true |

### Service Type Descriptions

**Web App (default)**
- Standard web application running on the Pi
- Full HTTPS with Let's Encrypt certificate
- Protected by Cloudflare Access

**Docker Container**
- Service running in Docker on the same network
- Uses container name for backend (e.g., `grafana:3000`)
- Network: docker network (`network_default`)

**IoT Device**
- Smart devices, embedded systems, appliances
- Often can't handle Cloudflare headers
- Usually HTTP-only on LAN
- Tunnel provides remote access

**Self-Signed Cert**
- Services with their own HTTPS (Portainer, Proxmox, etc.)
- Need `tls_insecure` to skip certificate verification
- Backend port is usually HTTPS port (9443, 8443, etc.)

**Public API**
- Webhooks, API endpoints that need public access
- No authentication (or custom auth)
- HTTP for simplicity

**External LAN**
- Service on another device on the network
- Uses LAN IP address for backend
- Pi acts as reverse proxy

---

## Backend Format Guide

### Container Backend

For Docker containers in the same network:

```toml
backend = "container-name:port"
```

**Examples:**
- `pihole:80` - Pi-hole container
- `grafana:3000` - Grafana container
- `portainer:9000` - Portainer (HTTP interface)

**Requirements:**
- Container must be on the same Docker network
- Port is the container's internal port (not host port)

### IP Backend

For services accessible via IP:

```toml
backend = "192.168.68.XXX:PORT"
```

**Examples:**
- `192.168.68.135:16686` - Jaeger on the Pi
- `192.168.68.105:80` - Sprinkler controller
- `192.168.68.123:8123` - Home Assistant on different Pi

**When to use:**
- Service running on host (not in Docker)
- Service on another device on LAN
- IoT devices

### Special Backends

```toml
backend = "file_server:/path"
```

For static file serving (used by root domain).

---

## Cloudflare Tunnel Routing

### Tunnel URL Selection

The URL you configure in Cloudflare Tunnel depends on the service type:

| Service Configuration | Tunnel URL |
|----------------------|------------|
| `enable_https = true` | `https://caddy:443` |
| `enable_http = true` (standard) | `http://caddy:80` |
| IoT with `strip_cf_headers` | Direct: `http://192.168.68.XXX:80` |

### Why Different URLs?

**HTTPS through Caddy (`https://caddy:443`):**
- Caddy handles TLS termination
- Provides consistent HTTPS internally
- Best for most services

**HTTP through Caddy (`http://caddy:80`):**
- Caddy routes based on Host header
- Used for HTTP-only services
- Tunnel provides HTTPS externally

**Direct to Device:**
- Bypasses Caddy entirely
- Required when Caddy can't handle the service
- IoT devices with header issues

### Cloudflare Tunnel Configuration Steps

1. Access: https://one.dash.cloudflare.com
2. Navigate: Access -> Tunnels
3. Select tunnel: "pi-home"
4. Configure -> Public Hostname -> Add

**Fields:**
- Subdomain: `myservice`
- Domain: `temet.ai`
- Type: `HTTP` or `HTTPS`
- URL: (see table above)

**Optional Settings:**
- TLS: Verify Origin (usually leave default)
- HTTP Settings: Usually defaults are fine

---

## Troubleshooting Reference

### Common Errors and Solutions

**Error: "Configuration has syntax errors"**
```bash
# Validate TOML syntax
python3 -c "import tomli; tomli.load(open('domains.toml', 'rb'))"
```
Cause: Invalid TOML syntax in domains.toml
Fix: Check for missing quotes, brackets, or invalid characters

**Error: "Failed to reload Caddy"**
```bash
# Validate Caddyfile
docker exec caddy caddy validate --config /etc/caddy/Caddyfile
# Check Caddy logs
docker logs caddy --tail 50
```
Cause: Generated Caddyfile has syntax error
Fix: Check service configuration in domains.toml

**Error: DNS not resolving**
```bash
# Test DNS resolution
dig @192.168.68.135 subdomain.temet.ai
# Check Pi-hole status
docker exec pihole pihole status
# Restart Pi-hole
docker compose restart pihole
```
Cause: Pi-hole DNS entries not updated or Pi-hole down
Fix: Restart Pi-hole or check docker-compose.yml

**Error: Certificate not issued**
```bash
# Check certificate status
docker logs caddy | grep certificate
# Test certificate
openssl s_client -connect subdomain.temet.ai:443 -servername subdomain.temet.ai
```
Cause: Cloudflare DNS challenge failing
Fix: Verify CLOUDFLARE_API_KEY in .env

**Error: "403 Forbidden" on remote access**
Cause: Cloudflare Access blocking
Fix: Check require_auth setting and allowed emails in .env

**Error: IoT device shows garbled data**
Cause: Device can't parse Cloudflare headers
Fix: Add `strip_cf_headers = true`

**Error: "Connection refused" to backend**
```bash
# Check if service is running
curl -v http://backend-ip:port
# Check Docker networking
docker network inspect network_default
```
Cause: Backend service not running or wrong port
Fix: Verify backend address and port

### Verification Commands

```bash
# List all configured domains
./scripts/manage-domains.sh list

# Validate configuration
./scripts/manage-domains.sh validate

# Test DNS (local)
dig @192.168.68.135 subdomain.temet.ai +short

# Test HTTPS certificate
echo | openssl s_client -servername subdomain.temet.ai \
  -connect subdomain.temet.ai:443 2>/dev/null | \
  openssl x509 -noout -dates -issuer

# Test HTTP response
curl -I https://subdomain.temet.ai

# Check Caddy logs
docker logs caddy --tail 50

# Check Cloudflare Access applications
./scripts/cf-access-setup.sh list
```
