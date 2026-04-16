# CASS Security Audit Report

## Executive Summary

**Project**: cass (Coding Agent Session Search)
**Version**: 0.1.55
**Audit Date**: 2026-01-12
**Audit Scope**: Encrypted Pages Export Feature

### Overall Assessment

The cryptographic implementation demonstrates strong security architecture with enterprise-grade envelope encryption. The design follows industry best practices with multi-slot key wrapping (LUKS-like), Argon2id for password-based key derivation, and AES-256-GCM for authenticated encryption.

**One high-severity issue was identified** in the nonce derivation logic that should be addressed.

---

## Summary Statistics

| Category | Count |
|----------|-------|
| **Total Items Reviewed** | 56 |
| **Passed** | 44 |
| **Critical Findings** | 0 |
| **High Findings** | 1 |
| **Medium Findings** | 2 |
| **Low Findings** | 2 |
| **Advisory** | 1 |
| **Pending Documentation** | 5 |
| **N/A** | 4 |

---

## Findings

### HIGH-001: XOR-Based Chunk Nonce Derivation

**Severity**: HIGH
**Status**: FIXED (2026-01-12)
**Location**: `src/pages/encrypt.rs:536-544`

**Description**:
The chunk nonce derivation uses XOR to combine a base nonce with the chunk index:

```rust
fn derive_chunk_nonce(base_nonce: &[u8; 12], chunk_index: u32) -> [u8; 12] {
    let mut nonce = *base_nonce;
    let idx_bytes = chunk_index.to_be_bytes();
    for i in 0..4 {
        nonce[8 + i] ^= idx_bytes[i];
    }
    nonce
}
```

**Risk**:
XOR-based nonce derivation is not the recommended approach for counter-mode nonces. While the random base nonce provides uniqueness across exports, the XOR operation could theoretically create collisions in edge cases. NIST SP 800-38D recommends either:
1. Random nonces (with proper collision resistance)
2. Deterministic counter nonces (with proper incrementing)

**Impact**:
With the current 32-bit chunk counter limit (~4 billion chunks) and random 12-byte base nonce, the practical collision risk is minimal. However, this deviates from best practices.

**Recommended Remediation**:
Replace XOR with direct byte assignment or proper counter increment:

```rust
fn derive_chunk_nonce(base_nonce: &[u8; 12], chunk_index: u32) -> [u8; 12] {
    let mut nonce = *base_nonce;
    // Direct assignment of counter bytes (safer pattern)
    nonce[8..12].copy_from_slice(&chunk_index.to_be_bytes());
    nonce
}
```

**Note**: The JavaScript implementation in `crypto_worker.js:328-342` must be updated in tandem.

---

### MEDIUM-001: Base64 Encoding Using Deprecated APIs

**Severity**: MEDIUM
**Status**: OPEN
**Location**: `src/pages_assets/crypto_worker.js:543-561`

**Description**:
The JavaScript implementation uses `atob()` and `btoa()` for base64 encoding, which are deprecated and have known issues with binary data and non-ASCII characters.

**Risk**:
While functional for the current use case (pure binary data), these APIs may cause issues with certain byte sequences and are not recommended for new code.

**Recommended Remediation**:
Consider using modern alternatives or the existing implementations are acceptable for binary-safe base64 (which is the current use case).

---

### MEDIUM-002: Optional LocalStorage DEK Persistence

**Severity**: MEDIUM
**Status**: ADVISORY
**Location**: `src/pages_assets/session.js:88-95`

**Description**:
Users can optionally store encrypted DEK in localStorage for session persistence. While the DEK is encrypted with a session key, localStorage persists indefinitely.

**Risk**:
An attacker with browser access could potentially recover the encrypted DEK blob. The session key provides protection, but this extends the attack surface.

**Recommended Remediation**:
- Document the risk clearly to users
- Consider enforcing memory-only storage for highest security
- Current implementation is acceptable as it's opt-in

---

### LOW-001: Session Key Without Domain Separation

**Severity**: LOW
**Status**: OPEN
**Location**: `src/pages_assets/session.js:295`

**Description**:
Session key generation uses only random bytes without domain separation:

```javascript
generateSessionKey() {
    return crypto.getRandomValues(new Uint8Array(32));
}
```

**Risk**:
Minimal. The random 32 bytes provide sufficient entropy. Domain separation would add defense-in-depth.

**Suggested Enhancement**:
Consider deriving session key with HKDF including page origin as context.

---

### LOW-002: Worker Library Loading Without SRI

**Severity**: LOW
**Status**: ADVISORY
**Location**: `src/pages_assets/crypto_worker.js:512-534`

**Description**:
Web Worker loads libraries via `importScripts()` without integrity verification.

**Risk**:
Relies on CSP and same-origin policy. Since all assets are bundled with the export, this is acceptable for the current deployment model.

**Recommended Remediation**:
No action required for static bundle deployment.

---

## Strengths Identified

### Cryptographic Architecture
- **Envelope Encryption**: Proper DEK/KEK separation
- **Multi-Slot Key Wrapping**: LUKS-inspired design allows multiple unlock methods
- **Argon2id**: Strong password-based KDF with appropriate parameters (64MB, t=3, p=4)
- **AES-256-GCM**: Industry-standard AEAD with proper key sizes

### Key Management
- **Unique Salts**: Each key slot uses unique random salt
- **AAD Usage**: Chunk and slot operations include authenticated additional data
- **Zeroization**: Keys are zeroed on drop (`ZeroizeOnDrop` trait)

### JavaScript Implementation
- **Web Worker Isolation**: Crypto operations isolated in worker thread
- **HKDF Interoperability**: Rust and JS implementations match
- **Session Management**: Proper timeout and cleanup

### Web Security
- **CSP**: Restrictive Content Security Policy
- **COOP/COEP**: Cross-origin isolation enabled
- **TOFU Fingerprinting**: Detects archive tampering

---

## Compliance Summary

| Standard | Status | Notes |
|----------|--------|-------|
| NIST SP 800-38D (AES-GCM) | PARTIAL | Nonce derivation needs review |
| RFC 9106 (Argon2) | COMPLIANT | Parameters meet recommendations |
| RFC 5869 (HKDF) | COMPLIANT | Proper usage with info string |
| OWASP Crypto Guidelines | COMPLIANT | Zeroization, AAD usage |

---

## Recommendations

### Priority 1 (Should Address)
1. **Fix chunk nonce derivation** - Replace XOR with direct counter bytes

### Priority 2 (Consider Addressing)
2. **Add threat model documentation**
3. **Add key rotation procedures documentation**
4. **Add incident response documentation**

### Priority 3 (Optional Enhancements)
5. Consider domain separation for session keys
6. Document localStorage risks more prominently

---

## Conclusion

The cass encrypted export feature demonstrates a well-engineered cryptographic system. The envelope encryption architecture with multiple key slots is sophisticated and follows established patterns (LUKS). All core cryptographic primitives (AES-256-GCM, Argon2id, HKDF-SHA256) are correctly configured.

The single high-severity finding (XOR-based nonce derivation) should be addressed, though the practical risk is low given the random base nonce and expected usage patterns. All other findings are advisory or low severity.

**Overall Security Rating**: **GOOD** with minor improvements recommended.

---

## Audit Artifacts

- `docs/SECURITY_AUDIT_CHECKLIST.md` - Full item-by-item checklist
- `docs/SECURITY_AUDIT_REPORT.md` - This report

## Reviewer

- **Auditor**: Claude Code (AI-Assisted Review)
- **Date**: 2026-01-12
