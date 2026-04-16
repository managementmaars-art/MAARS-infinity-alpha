# Add Subdomain - Configuration Examples

Real-world examples of adding various types of services to the network infrastructure.

## Table of Contents

1. [Standard Web Application](#1-standard-web-application)
2. [Docker Container](#2-docker-container)
3. [IoT Device](#3-iot-device)
4. [Service with Self-Signed Certificate](#4-service-with-self-signed-certificate)
5. [Public API / Webhook](#5-public-api--webhook)
6. [External Device on LAN](#6-external-device-on-lan)
7. [Service with Root Redirect](#7-service-with-root-redirect)
8. [Service Needing Custom Headers](#8-service-needing-custom-headers)
9. [Root Domain Configuration](#9-root-domain-configuration)
10. [Dual-Access Service](#10-dual-access-service)

---

## 1. Standard Web Application

**Scenario:** Adding Grafana monitoring dashboard running on port 3001.

**User Request:** "Add grafana running on port 3001"

**Questions to Ask:**
1. Service name? -> "Grafana Dashboard"
2. Subdomain? -> "grafana"
3. Backend? -> "192.168.68.135:3001"
4. Need authentication? -> Yes (default)

**Configuration:**
```toml
[[services]]
name = "Grafana Dashboard"
subdomain = "grafana"
backend = "192.168.68.135:3001"
enable_https = true
enable_http = false
dns_ip = "192.168.68.135"
require_auth = true
```

**Tunnel Configuration:**
- Subdomain: grafana
- Domain: temet.ai
- Type: HTTPS
- URL: https://caddy:443

**Verification:**
```bash
dig @192.168.68.135 grafana.temet.ai +short
# Expected: 192.168.68.135

curl -I https://grafana.temet.ai
# Expected: HTTP/2 302 (redirect to Cloudflare login)
```

---

## 2. Docker Container

**Scenario:** Adding Uptime Kuma monitoring running in Docker container.

**User Request:** "Add uptime kuma container"

**Configuration:**
```toml
[[services]]
name = "Uptime Kuma"
subdomain = "uptime"
backend = "uptime-kuma:3001"
enable_https = true
enable_http = false
dns_ip = "192.168.68.135"
require_auth = true
```

**Notes:**
- `backend` uses container name, not IP
- Container must be on same Docker network
- Port is container's internal port

**docker-compose.yml entry needed:**
```yaml
uptime-kuma:
  image: louislam/uptime-kuma:1
  container_name: uptime-kuma
  volumes:
    - ./volumes/uptime-kuma:/app/data
  networks:
    - default
  restart: unless-stopped
```

---

## 3. IoT Device

**Scenario:** Adding a smart thermostat at 192.168.68.110.

**User Request:** "Add my ecobee thermostat at 192.168.68.110"

**Questions:**
1. Does the device have its own web interface? -> Yes
2. Does it support HTTPS? -> No (HTTP only)
3. Can it handle custom headers? -> No (IoT limitation)

**Configuration:**
```toml
[[services]]
name = "Ecobee Thermostat"
subdomain = "thermostat"
backend = "192.168.68.110:80"
enable_https = false
enable_http = true
dns_ip = "192.168.68.110"
require_auth = true
strip_cf_headers = true
```

**Key Settings:**
- `enable_https = false` - IoT devices often can't do HTTPS
- `enable_http = true` - Use HTTP block for tunnel routing
- `strip_cf_headers = true` - Remove Cloudflare headers device can't handle
- `dns_ip` - Device's actual IP for direct local access

**Tunnel Configuration:**
- Subdomain: thermostat
- Domain: temet.ai
- Type: HTTP
- URL: http://192.168.68.110:80 (direct to device)

---

## 4. Service with Self-Signed Certificate

**Scenario:** Adding Portainer at port 9443 with self-signed cert.

**User Request:** "Add portainer which runs on HTTPS 9443"

**Configuration:**
```toml
[[services]]
name = "Portainer"
subdomain = "portainer"
backend = "192.168.68.135:9443"
enable_https = true
enable_http = false
dns_ip = "192.168.68.135"
require_auth = true
tls_insecure = true
```

**Key Settings:**
- `tls_insecure = true` - Skip TLS verification for self-signed cert
- Backend port is the HTTPS port (9443 not 9000)

**Tunnel Configuration:**
- Type: HTTPS
- URL: https://caddy:443
- Caddy handles TLS termination and connects to Portainer's HTTPS

**Caddyfile generates:**
```caddyfile
portainer.temet.ai {
    tls {
        dns cloudflare {env.CLOUDFLARE_API_KEY}
    }
    reverse_proxy 192.168.68.135:9443 {
        transport http {
            tls_insecure_skip_verify
        }
    }
}
```

---

## 5. Public API / Webhook

**Scenario:** Adding a webhook endpoint for external service integration.

**User Request:** "Add webhook endpoint that doesn't need authentication"

**Configuration:**
```toml
[[services]]
name = "Integration Webhook"
subdomain = "hook"
backend = "webhook-service:8080"
enable_https = false
enable_http = true
dns_ip = "192.168.68.135"
require_auth = false
```

**Key Settings:**
- `require_auth = false` - Allows unauthenticated access
- Usually HTTP-only for simplicity

**Security Note:**
Implement authentication in the service itself (API keys, HMAC signatures, etc.)

---

## 6. External Device on LAN

**Scenario:** Adding Home Assistant running on a different Raspberry Pi.

**User Request:** "Add home assistant at 192.168.68.123 port 8123"

**Configuration:**
```toml
[[services]]
name = "Home Assistant"
subdomain = "ha"
backend = "192.168.68.123:8123"
enable_https = true
enable_http = false
dns_ip = "192.168.68.135"
require_auth = true
proxy_headers = true
```

**Key Settings:**
- Backend is the other device's IP
- `dns_ip = "192.168.68.135"` - Still points to Pi (Caddy) for local HTTPS
- `proxy_headers = true` - HA uses these for trusted proxies

**Home Assistant configuration.yaml needed:**
```yaml
http:
  use_x_forwarded_for: true
  trusted_proxies:
    - 192.168.68.135
```

---

## 7. Service with Root Redirect

**Scenario:** Adding Pi-hole which has its UI at /admin/.

**User Request:** "Add pihole admin interface with redirect to /admin/"

**Configuration:**
```toml
[[services]]
name = "Pi-hole Admin"
subdomain = "pihole"
backend = "pihole:80"
enable_https = true
enable_http = false
dns_ip = "192.168.68.135"
require_auth = true
root_redirect = "/admin/"
proxy_headers = true
```

**Key Settings:**
- `root_redirect = "/admin/"` - Visiting https://pihole.temet.ai redirects to /admin/

**Caddyfile generates:**
```caddyfile
pihole.temet.ai {
    tls {
        dns cloudflare {env.CLOUDFLARE_API_KEY}
    }
    route {
        @root path /
        redir @root /admin/ permanent
        reverse_proxy pihole:80 {
            header_up X-Forwarded-For {remote_host}
            header_up X-Forwarded-Proto {scheme}
            header_up X-Real-IP {remote_host}
        }
    }
}
```

---

## 8. Service Needing Custom Headers

**Scenario:** Adding a service that requires specific headers.

**User Request:** "Add myapp that needs custom X-Custom-Header"

**Configuration:**
```toml
[[services]]
name = "Custom App"
subdomain = "myapp"
backend = "192.168.68.135:8000"
enable_https = true
enable_http = false
dns_ip = "192.168.68.135"
require_auth = true
custom_caddy = """
    header_up X-Custom-Header "custom-value"
    header_up X-App-Name "MyApp"
"""
```

**Key Settings:**
- `custom_caddy` - Injects raw Caddy directives
- Useful for special requirements not covered by standard options

---

## 9. Root Domain Configuration

**Scenario:** Setting up temet.ai (no subdomain) as a services dashboard.

**Configuration:**
```toml
[[services]]
name = "Services Dashboard"
subdomain = ""
backend = "file_server:/srv"
enable_https = true
enable_http = true
dns_ip = "192.168.68.135"
require_auth = true
```

**Key Settings:**
- `subdomain = ""` - Empty string = root domain
- `backend = "file_server:/srv"` - Special: serves static files
- Both HTTPS and HTTP enabled for flexibility

---

## 10. Dual-Access Service

**Scenario:** Service needs both local HTTPS and tunnel HTTP access.

**User Request:** "Add code server that needs both HTTPS locally and HTTP via tunnel"

**Configuration:**
```toml
[[services]]
name = "Code Server"
subdomain = "code"
backend = "192.168.68.135:8080"
enable_https = true
enable_http = true
dns_ip = "192.168.68.135"
require_auth = true
proxy_headers = true
```

**Key Settings:**
- `enable_https = true` - Local access with Let's Encrypt cert
- `enable_http = true` - Also added to HTTP block for tunnel

**Why both?**
- HTTPS for direct local access (faster)
- HTTP for Cloudflare tunnel routing

**Tunnel Configuration:**
- Type: HTTPS
- URL: https://caddy:443

---

## Quick Reference: Configuration by Use Case

| Use Case | enable_https | enable_http | require_auth | Special Options |
|----------|--------------|-------------|--------------|-----------------|
| Standard web app | true | false | true | - |
| Docker container | true | false | true | container:port backend |
| IoT device | false | true | true | strip_cf_headers = true |
| Self-signed cert | true | false | true | tls_insecure = true |
| Public webhook | false | true | false | - |
| External device | true | false | true | proxy_headers = true |
| With redirect | true | false | true | root_redirect = "/path/" |
| Custom headers | true | false | true | custom_caddy = "..." |
| Root domain | true | true | true | subdomain = "" |
| Dual access | true | true | true | - |

---

## Interactive Question Flow

When adding a new subdomain, ask these questions in order:

1. **"What is the service name?"** (e.g., "Grafana Dashboard")

2. **"What subdomain do you want?"** (e.g., "grafana")
   - Validate: lowercase, alphanumeric + hyphens
   - Check for duplicates

3. **"Where is the service running?"**
   - Docker container on same network -> container:port
   - Service on the Pi -> 192.168.68.135:port
   - Service on another device -> IP:port

4. **"What type of service is this?"**
   - Web application (standard HTTPS)
   - IoT device (needs header stripping)
   - Has self-signed certificate
   - Public/webhook (no auth needed)

5. **"Does it need authentication?"** (usually yes)

6. **"Any special requirements?"**
   - Root redirect path
   - Custom headers
   - Both HTTP and HTTPS

Based on answers, generate configuration and apply.
