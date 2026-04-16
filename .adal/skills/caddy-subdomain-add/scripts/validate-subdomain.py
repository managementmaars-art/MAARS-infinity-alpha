#!/usr/bin/env python3
"""
Validate subdomain configuration before adding to domains.toml.

Usage:
    python3 validate-subdomain.py <subdomain> <backend>

Examples:
    python3 validate-subdomain.py grafana 192.168.68.135:3001
    python3 validate-subdomain.py uptime uptime-kuma:3001
"""

import re
import sys


def validate_subdomain(subdomain: str) -> tuple[bool, str]:
    """Validate subdomain according to DNS rules."""
    # Empty string is valid (root domain)
    if subdomain == "":
        return True, "Valid (root domain)"

    # Check length
    if len(subdomain) > 63:
        return False, "Subdomain must be 63 characters or less"

    # Check format
    pattern = r'^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$'
    if not re.match(pattern, subdomain):
        if subdomain != subdomain.lower():
            return False, "Subdomain must be lowercase"
        if subdomain.startswith('-') or subdomain.endswith('-'):
            return False, "Subdomain cannot start or end with hyphen"
        return False, "Subdomain must contain only lowercase letters, numbers, and hyphens"

    return True, "Valid"


def validate_ip(ip: str) -> tuple[bool, str]:
    """Validate IPv4 address format."""
    pattern = r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$'
    match = re.match(pattern, ip)
    if not match:
        return False, "Invalid IP address format"

    octets = [int(g) for g in match.groups()]
    for i, octet in enumerate(octets):
        if octet < 0 or octet > 255:
            return False, f"IP octet {i+1} out of range (0-255)"

    if octets[0] == 127:
        return True, "Warning: localhost address - may not work from other hosts"
    if octets[0] == 0:
        return False, "Invalid IP address (0.x.x.x)"

    return True, "Valid"


def validate_port(port: str) -> tuple[bool, str]:
    """Validate port number."""
    try:
        port_num = int(port)
        if port_num < 1 or port_num > 65535:
            return False, "Port must be between 1 and 65535"
        if port_num < 1024:
            return True, "Note: privileged port (requires root)"
        return True, "Valid"
    except ValueError:
        return False, "Port must be a number"


def validate_backend(backend: str) -> tuple[bool, str, str]:
    """
    Validate backend format and determine type.
    Returns (is_valid, message, backend_type).
    """
    # Special backends
    if backend.startswith("file_server:"):
        return True, "Valid (file server)", "special"

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
        return True, "Valid (container)", "container"

    return False, "Invalid backend format. Use IP:port or container:port", ""


def check_duplicate(subdomain: str, config_file: str = "/home/dawiddutoit/projects/network/domains.toml") -> bool:
    """Check if subdomain already exists in config."""
    try:
        with open(config_file, 'r') as f:
            content = f.read()
            pattern = f'^subdomain = "{subdomain}"$'
            if re.search(pattern, content, re.MULTILINE):
                return True
    except FileNotFoundError:
        pass
    return False


def main():
    if len(sys.argv) < 3:
        print("Usage: validate-subdomain.py <subdomain> <backend>")
        print("\nExamples:")
        print("  validate-subdomain.py grafana 192.168.68.135:3001")
        print("  validate-subdomain.py uptime uptime-kuma:3001")
        sys.exit(1)

    subdomain = sys.argv[1]
    backend = sys.argv[2]

    print(f"Validating subdomain configuration...")
    print(f"  Subdomain: {subdomain}")
    print(f"  Backend: {backend}")
    print()

    errors = []
    warnings = []

    # Validate subdomain
    valid, msg = validate_subdomain(subdomain)
    if valid:
        if "Warning" in msg:
            warnings.append(f"Subdomain: {msg}")
        else:
            print(f"[OK] Subdomain: {msg}")
    else:
        errors.append(f"Subdomain: {msg}")
        print(f"[ERROR] Subdomain: {msg}")

    # Check for duplicates
    if check_duplicate(subdomain):
        errors.append(f"Subdomain '{subdomain}' already exists in domains.toml")
        print(f"[ERROR] Subdomain '{subdomain}' already exists")
    else:
        print(f"[OK] No duplicate found")

    # Validate backend
    valid, msg, backend_type = validate_backend(backend)
    if valid:
        if "Warning" in msg or "Note" in msg:
            warnings.append(f"Backend: {msg}")
        print(f"[OK] Backend: {msg} (type: {backend_type})")
    else:
        errors.append(f"Backend: {msg}")
        print(f"[ERROR] Backend: {msg}")

    # Summary
    print()
    if errors:
        print(f"Validation FAILED with {len(errors)} error(s):")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print("Validation PASSED")
        if warnings:
            print(f"Warnings ({len(warnings)}):")
            for w in warnings:
                print(f"  - {w}")
        sys.exit(0)


if __name__ == "__main__":
    main()
