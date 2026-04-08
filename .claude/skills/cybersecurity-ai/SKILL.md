---
name: cybersecurity-ai
description: AI cybersecurity skills — security audits, vulnerability assessment, OWASP compliance, threat modeling, penetration testing guidance, GDPR/SOC2 compliance for MAARS security agents
---

# Cybersecurity AI — MAARS Reference

## Security Audit Framework
```python
SECURITY_AUDIT_PROMPT = """
You are Damien Voss, MAARS Cybersecurity Officer.

Perform a security audit of this code/system:
{target}

Check for:
1. OWASP Top 10 (injection, broken auth, XSS, IDOR, etc.)
2. Authentication & authorization flaws
3. Data exposure (PII, secrets in code, logging sensitive data)
4. Cryptographic weaknesses
5. Security misconfigurations
6. Dependency vulnerabilities
7. Input validation gaps
8. Rate limiting & DDoS exposure

For each finding:
- Severity: CRITICAL/HIGH/MEDIUM/LOW/INFORMATIONAL
- Description: What's wrong
- Impact: What an attacker could do
- Remediation: Specific fix with code example
- References: CVE, CWE, or OWASP link
"""
```

## OWASP Top 10 Checklist
```python
OWASP_TOP_10 = {
    "A01_Broken_Access_Control": [
        "Verify all endpoints check authorization",
        "IDOR: Validate object ownership before returning data",
        "Directory traversal prevention",
        "CORS policy configured correctly",
    ],
    "A02_Cryptographic_Failures": [
        "No passwords stored in plaintext (use bcrypt/argon2)",
        "Sensitive data encrypted at rest (AES-256)",
        "TLS 1.2+ only, no weak ciphers",
        "No secrets in source code or logs",
    ],
    "A03_Injection": [
        "All SQL uses parameterized queries",
        "NoSQL injection prevention",
        "Command injection: never pass user input to shell",
        "LDAP injection checks",
    ],
    "A04_Insecure_Design": [
        "Threat modeling performed",
        "Security requirements in design phase",
        "Defense in depth",
    ],
    "A05_Security_Misconfiguration": [
        "No default credentials",
        "Error messages don't expose stack traces in production",
        "Security headers set (CSP, HSTS, X-Frame-Options)",
        "Unnecessary features disabled",
    ],
    "A07_Auth_Failures": [
        "Brute force protection (rate limiting, lockout)",
        "MFA available and encouraged",
        "Session tokens properly invalidated on logout",
        "JWT signatures verified, expiry checked",
    ],
    "A09_Security_Logging": [
        "Auth events logged",
        "Access control failures logged",
        "No sensitive data in logs",
        "Log tampering protection",
    ],
    "A10_SSRF": [
        "Validate and sanitize all URLs fetched server-side",
        "Block requests to internal/private IP ranges",
        "Allowlist external services",
    ],
}
```

## Secure Code Patterns
```python
# SQL — always parameterized
# BAD:  f"SELECT * FROM users WHERE id = {user_id}"
# GOOD:
await db.fetchrow("SELECT * FROM users WHERE id = $1", user_id)

# Password hashing
import bcrypt
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12))
valid = bcrypt.checkpw(password.encode(), hashed)

# JWT validation
import jwt
try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"],
                         options={"verify_exp": True})
except jwt.ExpiredSignatureError:
    raise HTTPException(401, "Token expired")
except jwt.InvalidTokenError:
    raise HTTPException(401, "Invalid token")

# Rate limiting
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)
@app.post("/api/login")
@limiter.limit("5/minute")
async def login(request: Request): ...

# Input sanitization
import bleach
safe_html = bleach.clean(user_html, tags=["b","i","u","p"], strip=True)

# Secrets management
import os
API_KEY = os.getenv("API_KEY")  # Never hardcode
assert API_KEY, "API_KEY environment variable not set"
```

## Threat Modeling (STRIDE)
```python
STRIDE = {
    "Spoofing": "Attacker impersonates another user/system",
    "Tampering": "Attacker modifies data in transit or at rest",
    "Repudiation": "User denies performing an action",
    "Information_Disclosure": "Sensitive data exposed to unauthorized parties",
    "Denial_of_Service": "Service made unavailable",
    "Elevation_of_Privilege": "User gains higher access than authorized",
}
```

## Compliance Frameworks
```python
COMPLIANCE = {
    "SOC2": {
        "criteria": ["Security", "Availability", "Processing Integrity",
                     "Confidentiality", "Privacy"],
        "key_controls": ["access_control", "encryption", "monitoring",
                         "incident_response", "change_management"],
    },
    "ISO_27001": {
        "controls": "114 controls across 14 domains",
        "focus": "Information Security Management System (ISMS)",
    },
    "PCI_DSS": {
        "applies_to": "Any system storing/processing payment card data",
        "key_requirements": ["network_segmentation", "encryption", "access_control",
                             "monitoring", "vulnerability_scanning"],
    },
    "HIPAA": {
        "applies_to": "US healthcare data (PHI)",
        "safeguards": ["administrative", "physical", "technical"],
        "key": ["encryption", "audit_controls", "access_management", "breach_notification"],
    },
}
```

## Models to Use
- **Security code review**: `claude-opus-4-6` (best at finding subtle bugs)
- **Threat modeling**: `gpt-5.2` or `o3`
- **Quick vulnerability scan**: `gpt-4o`
- **Compliance documentation**: `claude-sonnet-4-6`
