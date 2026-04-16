---
name: assess-hipaa
description: Conduct a HIPAA compliance assessment for healthcare systems handling PHI.
argument-hint: <scope-description>
allowed-tools: Task, Skill
---

# HIPAA Compliance Assessment

Conduct a comprehensive HIPAA compliance assessment.

## Workflow

### Step 1: Load Required Skills

Load these skills:

- `hipaa-compliance` - HIPAA requirements and safeguards
- `data-classification` - PHI identification
- `security-frameworks` - Security control mapping

### Step 2: Spawn Compliance Analyst Agent

Spawn the `compliance-analyst` agent with the following prompt:

```text
Conduct a comprehensive HIPAA compliance assessment for: $ARGUMENTS

Perform the following assessments:

1. PHI Identification
   - Identify all Protected Health Information
   - Map PHI data flows
   - Document storage locations
   - Identify all access points

2. Entity Classification
   - Determine if Covered Entity or Business Associate
   - Identify all Business Associate relationships
   - Review BAA coverage

3. Administrative Safeguards
   - Security management process
   - Workforce security
   - Information access management
   - Security awareness and training
   - Incident response procedures
   - Contingency planning

4. Physical Safeguards
   - Facility access controls
   - Workstation security
   - Device and media controls

5. Technical Safeguards
   - Access controls (unique user ID, MFA)
   - Audit controls
   - Integrity controls
   - Transmission security

6. Risk Assessment
   - Identify threats and vulnerabilities
   - Assess likelihood and impact
   - Calculate risk levels
   - Recommend mitigations

7. Breach Notification Readiness
   - Incident detection capabilities
   - Breach assessment procedures
   - Notification procedures

Provide a complete HIPAA assessment with:
- Safeguard compliance scores
- Gap analysis with severity
- Risk assessment summary
- Remediation priorities
```

### Step 3: Generate Assessment Report

Ensure the report includes:

- Executive summary with compliance posture
- Detailed safeguard assessment
- Risk register
- BAA inventory
- Remediation roadmap

## Example Usage

```bash
# Assess a patient portal
/compliance-planning:assess-hipaa "patient portal with PHI access and messaging"

# Assess a medical records system
/compliance-planning:assess-hipaa "electronic health record system with multi-provider access"

# Assess a healthcare analytics platform
/compliance-planning:assess-hipaa "healthcare analytics platform processing de-identified data"
```

## Output Format

```markdown
# HIPAA Compliance Assessment: [System Name]

## Executive Summary

### Entity Type: [Covered Entity / Business Associate]

### Overall Compliance: [COMPLIANT / PARTIAL / NON-COMPLIANT]

| Safeguard Category | Score | Status |
|--------------------|-------|--------|
| Administrative | [X/10] | [Status] |
| Physical | [X/10] | [Status] |
| Technical | [X/10] | [Status] |
| **Overall** | **[X/10]** | **[Status]** |

### Critical Findings
- [Finding 1]
- [Finding 2]

---

## PHI Inventory

| Data Element | HIPAA Identifier | Location | Access |
|--------------|------------------|----------|--------|

---

## Safeguard Assessment

### Administrative Safeguards
| Requirement | Status | Evidence | Gap |
|-------------|--------|----------|-----|

### Physical Safeguards
| Requirement | Status | Evidence | Gap |
|-------------|--------|----------|-----|

### Technical Safeguards
| Requirement | Status | Evidence | Gap |
|-------------|--------|----------|-----|

---

## Business Associate Analysis

| BA Name | Services | BAA Status | Last Review |
|---------|----------|------------|-------------|

---

## Risk Assessment

| Risk | Threat | Vulnerability | Likelihood | Impact | Score | Mitigation |
|------|--------|---------------|------------|--------|-------|------------|

---

## Gap Analysis

### Critical Gaps
| Gap | Safeguard | Risk | Priority | Remediation |
|-----|-----------|------|----------|-------------|

---

## Remediation Roadmap

### Phase 1: Critical (Immediate)
1. [Action with owner]

### Phase 2: High Priority (30 days)
1. [Action]

### Phase 3: Improvements (90 days)
1. [Action]

---

## Breach Notification Readiness

- [ ] Incident detection in place
- [ ] Breach assessment procedure documented
- [ ] Notification templates ready
- [ ] HHS reporting procedure defined
```
