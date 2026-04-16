#!/bin/bash
#
# HTTPS/SSL Certificate Diagnostic Script
# Diagnoses common issues with Caddy, Cloudflare DNS challenge, and Let's Encrypt
#
# Usage: ./diagnose-https.sh [--verbose]
#

set -e

VERBOSE=${1:-""}
PROJECT_DIR="/home/dawiddutoit/projects/network"
DOMAINS="pihole jaeger langfuse sprinkler ha"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
PASS=0
FAIL=0
WARN=0

print_header() {
    echo ""
    echo "========================================"
    echo "  HTTPS/SSL Certificate Diagnostics"
    echo "========================================"
    echo "  Date: $(date)"
    echo "========================================"
    echo ""
}

check_pass() {
    echo -e "[${GREEN}PASS${NC}] $1"
    ((PASS++))
}

check_fail() {
    echo -e "[${RED}FAIL${NC}] $1"
    ((FAIL++))
}

check_warn() {
    echo -e "[${YELLOW}WARN${NC}] $1"
    ((WARN++))
}

check_info() {
    echo -e "[INFO] $1"
}

# Check 1: Container Status
check_container_status() {
    echo "--- Check 1: Container Status ---"

    if docker ps --format '{{.Names}}' | grep -q "^caddy$"; then
        STATUS=$(docker inspect --format='{{.State.Status}}' caddy 2>/dev/null)
        if [ "$STATUS" = "running" ]; then
            RESTARTS=$(docker inspect --format='{{.RestartCount}}' caddy 2>/dev/null)
            if [ "$RESTARTS" -gt 5 ]; then
                check_warn "Caddy container running but has restarted $RESTARTS times"
            else
                check_pass "Caddy container is running"
            fi
        else
            check_fail "Caddy container status: $STATUS"
        fi
    else
        check_fail "Caddy container not found"
    fi
    echo ""
}

# Check 2: API Key Configuration
check_api_key() {
    echo "--- Check 2: API Key Configuration ---"

    # Check .env file
    if [ -f "$PROJECT_DIR/.env" ]; then
        if grep -q "CLOUDFLARE_API_KEY=" "$PROJECT_DIR/.env"; then
            KEY_VALUE=$(grep "CLOUDFLARE_API_KEY=" "$PROJECT_DIR/.env" | head -1 | cut -d'=' -f2 | tr -d '"')

            # Check if it looks like Global API Key (wrong format)
            if [[ "$KEY_VALUE" == v4:* ]] || [[ ${#KEY_VALUE} -eq 37 && "$KEY_VALUE" =~ ^[a-f0-9]+$ ]]; then
                check_fail "API key appears to be Global API Key (wrong type)"
                check_info "  -> Create an API Token with 'Edit zone DNS' template"
            elif [ -z "$KEY_VALUE" ]; then
                check_fail "CLOUDFLARE_API_KEY is empty in .env"
            else
                check_pass "CLOUDFLARE_API_KEY is set in .env"
            fi
        else
            check_fail "CLOUDFLARE_API_KEY not found in .env"
        fi
    else
        check_fail ".env file not found at $PROJECT_DIR/.env"
    fi

    # Check container environment
    CONTAINER_KEY=$(docker exec caddy env 2>/dev/null | grep "CLOUDFLARE_API_KEY=" | cut -d'=' -f2)
    if [ -n "$CONTAINER_KEY" ]; then
        check_pass "CLOUDFLARE_API_KEY is passed to container"
    else
        check_fail "CLOUDFLARE_API_KEY is NOT in container environment"
        check_info "  -> Run: docker compose up -d --force-recreate caddy"
    fi
    echo ""
}

# Check 3: Cloudflare DNS Plugin
check_dns_plugin() {
    echo "--- Check 3: Cloudflare DNS Plugin ---"

    MODULES=$(docker exec caddy caddy list-modules 2>/dev/null || echo "")
    if echo "$MODULES" | grep -q "dns.providers.cloudflare"; then
        check_pass "Cloudflare DNS plugin is installed"
    else
        check_fail "Cloudflare DNS plugin NOT found"
        check_info "  -> Run: docker compose build --no-cache caddy"
    fi
    echo ""
}

# Check 4: Caddyfile Validation
check_caddyfile() {
    echo "--- Check 4: Caddyfile Validation ---"

    VALIDATION=$(docker exec caddy caddy validate --config /etc/caddy/Caddyfile 2>&1)
    if echo "$VALIDATION" | grep -qi "valid"; then
        check_pass "Caddyfile syntax is valid"
    else
        check_fail "Caddyfile has syntax errors"
        if [ "$VERBOSE" = "--verbose" ]; then
            check_info "  Error: $VALIDATION"
        fi
    fi
    echo ""
}

# Check 5: Certificate Logs
check_cert_logs() {
    echo "--- Check 5: Certificate Logs ---"

    # Check for success messages
    SUCCESS_COUNT=$(docker logs caddy 2>&1 | grep -c "certificate obtained successfully" || echo "0")
    if [ "$SUCCESS_COUNT" -gt 0 ]; then
        check_pass "Found $SUCCESS_COUNT successful certificate acquisitions"
    else
        check_warn "No 'certificate obtained successfully' messages found"
    fi

    # Check for common errors
    LOGS=$(docker logs caddy 2>&1)

    if echo "$LOGS" | grep -q "Invalid format for Authorization header"; then
        check_fail "Error: Invalid format for Authorization header"
        check_info "  -> Using Global API Key instead of API Token"
        check_info "  -> Create new API Token with 'Edit zone DNS' template"
    fi

    if echo "$LOGS" | grep -q "missing API token"; then
        check_fail "Error: missing API token"
        check_info "  -> CLOUDFLARE_API_KEY not passed to container"
    fi

    if echo "$LOGS" | grep -q "unknown directive 'dns'"; then
        check_fail "Error: unknown directive 'dns'"
        check_info "  -> Cloudflare plugin not compiled into Caddy"
    fi

    if echo "$LOGS" | grep -q "403 Forbidden"; then
        check_warn "Found '403 Forbidden' error - may be permission issue"
    fi

    if echo "$LOGS" | grep -q "certificate obtain error"; then
        check_warn "Found certificate obtain error - check rate limits or DNS"
    fi

    echo ""
}

# Check 6: Certificate Validity
check_certificates() {
    echo "--- Check 6: Certificate Validity ---"

    for domain in $DOMAINS; do
        FQDN="${domain}.temet.ai"

        # Get certificate info with shorter timeout
        CERT_INFO=$(timeout 3 bash -c "echo | openssl s_client -servername $FQDN -connect $FQDN:443 2>/dev/null | openssl x509 -noout -dates -issuer 2>&1" 2>/dev/null || echo "FAILED")

        if echo "$CERT_INFO" | grep -q "FAILED"; then
            check_fail "$FQDN - Could not retrieve certificate"
        elif echo "$CERT_INFO" | grep -q "Let's Encrypt"; then
            # Extract expiry date
            EXPIRY=$(echo "$CERT_INFO" | grep "notAfter" | cut -d'=' -f2)
            check_pass "$FQDN - Valid (Let's Encrypt, expires: $EXPIRY)"
        elif echo "$CERT_INFO" | grep -q "notAfter"; then
            ISSUER=$(echo "$CERT_INFO" | grep "issuer" | cut -d'=' -f2-)
            check_warn "$FQDN - Certificate from: $ISSUER (not Let's Encrypt)"
        else
            check_fail "$FQDN - Invalid certificate response"
        fi
    done
    echo ""
}

# Check 7: Cloudflare API Connectivity
check_cloudflare_api() {
    echo "--- Check 7: Cloudflare API Connectivity ---"

    if [ -f "$PROJECT_DIR/.env" ]; then
        TOKEN=$(grep "CLOUDFLARE_API_KEY=" "$PROJECT_DIR/.env" | head -1 | cut -d'=' -f2 | tr -d '"')

        if [ -n "$TOKEN" ]; then
            RESPONSE=$(curl -s -X GET "https://api.cloudflare.com/client/v4/user/tokens/verify" \
                -H "Authorization: Bearer $TOKEN" 2>/dev/null || echo '{"success":false}')

            if echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d.get('result',{}).get('status')=='active' else 1)" 2>/dev/null; then
                check_pass "Cloudflare API token is valid and active"
            else
                check_fail "Cloudflare API token verification failed"
                check_info "  -> Token may be invalid, expired, or have wrong permissions"
            fi
        else
            check_warn "Could not extract token from .env for API check"
        fi
    fi
    echo ""
}

# Print Summary
print_summary() {
    echo "========================================"
    echo "  Summary"
    echo "========================================"
    echo -e "  ${GREEN}Passed:${NC}  $PASS"
    echo -e "  ${YELLOW}Warnings:${NC} $WARN"
    echo -e "  ${RED}Failed:${NC}  $FAIL"
    echo "========================================"
    echo ""

    if [ $FAIL -gt 0 ]; then
        echo "Next Steps:"
        echo "  1. Review failed checks above"
        echo "  2. See SKILL.md Section 3.7 for specific fixes"
        echo "  3. See references/reference.md for detailed troubleshooting"
        echo ""
    elif [ $WARN -gt 0 ]; then
        echo "Warnings detected - review items above."
        echo ""
    else
        echo "All checks passed! HTTPS should be working correctly."
        echo ""
    fi
}

# Main execution
print_header
check_container_status
check_api_key
check_dns_plugin
check_caddyfile
check_cert_logs
check_certificates
check_cloudflare_api
print_summary

# Exit with appropriate code
if [ $FAIL -gt 0 ]; then
    exit 1
elif [ $WARN -gt 0 ]; then
    exit 0
else
    exit 0
fi
