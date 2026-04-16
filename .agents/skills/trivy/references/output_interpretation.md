# Trivy Output Interpretation Guide

## Understanding Scan Results

### Report Summary Section

```
Report Summary
┌──────────────────┬──────────┬─────────────────┐
│      Target      │   Type   │ Vulnerabilities │
├──────────────────┼──────────┼─────────────────┤
│ image:tag        │  debian  │        2        │
│ usr/bin/app      │ gobinary │        5        │
└──────────────────┴──────────┴─────────────────┘
```

**Fields:**
- **Target**: The artifact being scanned (OS layer, binary, library)
- **Type**: Artifact type (debian, alpine, gobinary, jar, etc.)
- **Vulnerabilities**: Count of HIGH/CRITICAL findings (when filtered)

### Vulnerability Detail Section

```
public.ecr.aws/image:tag (debian 12.12)
Total: 2 (HIGH: 2, CRITICAL: 0)

┌──────────┬───────────────┬──────────┬──────────┬───────────────────┬───────────────┐
│ Library  │ Vulnerability │ Severity │  Status  │ Installed Version │ Fixed Version │
├──────────┼───────────────┼──────────┼──────────┼───────────────────┼───────────────┤
│ libc6    │ CVE-2025-4802 │ HIGH     │ fixed    │ 2.36-9+deb12u10   │ 2.36-9+deb12u11 │
│ libpam0g │ CVE-2025-6020 │ HIGH     │ affected │ 1.5.2-6+deb12u1   │               │
└──────────┴───────────────┴──────────┴──────────┴───────────────────┴───────────────┘
```

**Column Definitions:**

- **Library**: Package or dependency name
- **Vulnerability**: CVE identifier
- **Severity**: CRITICAL > HIGH > MEDIUM > LOW > UNKNOWN
- **Status**: Current state of the vulnerability
- **Installed Version**: Version present in the scanned artifact
- **Fixed Version**: Version that resolves the CVE (if available)

## Status Field Values

### `fixed`
A patched version exists and is available.

**Action:** Check if upgrading to Fixed Version is feasible.

**Example:**
```
│ libc6 │ CVE-2025-4802 │ HIGH │ fixed │ 2.36-9+deb12u10 │ 2.36-9+deb12u11 │
```
Upgrade from 2.36-9+deb12u10 → 2.36-9+deb12u11 to resolve.

### `affected`
No fix available yet; vulnerability is present and unfixed.

**Action:** Monitor for updates. Consider compensating controls.

**Example:**
```
│ libpam0g │ CVE-2025-6020 │ HIGH │ affected │ 1.5.2-6+deb12u1 │ │
```
No patch available. Check CVE details for workarounds.

### `will_not_fix`
Vendor has decided not to patch this vulnerability.

**Reasons:**
- Low exploitability
- Design limitation
- EOL software

**Action:** Assess risk and consider alternative packages.

### `end_of_life`
Package or version has reached end of life.

**Action:** Upgrade to supported version/package.

## Common Patterns

### False Positives

Sometimes Trivy reports fixed CVEs:

```
│ github.com/gravitational/teleport │ CVE-2022-36633 │ HIGH │ fixed │ v0.0.0-20251107... │ 8.3.17, 9.3.13, 10.1.2 │
```

**Indicators:**
- Status shows `fixed`
- Installed version appears much newer than Fixed Version
- CVE is several years old

**Cause:** Version detection issues with Go modules or vendored dependencies.

**Action:** Verify actual installed version. If version >= fixed version, likely false positive.

### Base Image Vulnerabilities

Vulnerabilities in base OS packages (debian, alpine) appear across all derived images:

```
public.ecr.aws/image:18.3.2 (debian 12.12)
│ libpam0g │ CVE-2025-6020 │ HIGH │ affected │ 1.5.2-6+deb12u1 │ │

public.ecr.aws/image:18.4.0 (debian 12.12)
│ libpam0g │ CVE-2025-6020 │ HIGH │ affected │ 1.5.2-6+deb12u1 │ │
```

**Pattern:** Same CVE, same debian version = base layer issue.

**Action:** Wait for upstream debian patch, or switch to different base image.

### Application Binary Vulnerabilities

Go binaries, Java JARs, etc. have separate vulnerability listings:

```
usr/local/bin/teleport (gobinary)
Total: 5 (HIGH: 5, CRITICAL: 0)
```

**Pattern:** Different target type from OS layer.

**Action:** Update application dependencies or rebuild with updated toolchain.

## Severity Interpretation

### CRITICAL
Remotely exploitable, no authentication required, or RCE vulnerabilities.

**Action:** Prioritize patching immediately.

### HIGH
Significant impact but may require local access or specific conditions.

**Action:** Patch within normal maintenance window.

### MEDIUM
Moderate impact with limited exploitability.

**Action:** Patch during regular updates.

### LOW
Minimal impact or theoretical vulnerabilities.

**Action:** Patch opportunistically.

## Comparison Analysis

When comparing two scan results:

### Vulnerabilities Fixed Between Versions

```diff
- │ libc6 │ CVE-2025-1234 │ HIGH │ fixed │ 2.36-9+deb12u10 │ 2.36-9+deb12u11 │
```

Appears in old version, absent in new version = **Fixed**.

### Vulnerabilities Introduced

```diff
+ │ openssl │ CVE-2025-5678 │ HIGH │ affected │ 3.0.1 │ │
```

Absent in old version, appears in new version = **Introduced**.

### Persistent Vulnerabilities

```
Both versions:
│ libpam0g │ CVE-2025-6020 │ HIGH │ affected │ 1.5.2-6+deb12u1 │ │
```

Appears in both = **Unfixed/Persistent**.

## Zero Vulnerabilities

```
usr/local/bin/tbot (gobinary)
Total: 0 (HIGH: 0, CRITICAL: 0)
```

**Meaning:** No HIGH or CRITICAL vulnerabilities found with current filters.

**Note:** May still have MEDIUM/LOW vulnerabilities not shown with `--severity HIGH,CRITICAL`.
