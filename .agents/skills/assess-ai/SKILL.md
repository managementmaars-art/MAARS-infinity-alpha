---
name: assess-ai
description: Conduct an AI governance and responsible AI assessment using EU AI Act and NIST AI RMF.
argument-hint: <system-description>
allowed-tools: Task, Skill
---

# AI Governance Assessment

Conduct a comprehensive AI governance and responsible AI assessment.

## Workflow

### Step 1: Load Required Skills

Load these skills:

- `ai-governance` - EU AI Act and NIST AI RMF
- `ethics-review` - Ethical impact assessment

### Step 2: Conduct Risk Classification

First, determine the AI system's risk classification under EU AI Act:

**Classification Criteria:**

- Unacceptable Risk (Prohibited)
- High Risk (Strict requirements)
- Limited Risk (Transparency obligations)
- Minimal Risk (No specific requirements)

### Step 3: Conduct AI Safety Assessment

Research AI safety frameworks using MCP servers (perplexity for NIST AI RMF, EU AI Act guidance) and conduct assessment based on current standards.

```text
Conduct a comprehensive AI governance assessment for: $ARGUMENTS

Perform the following assessments:

1. EU AI Act Classification
   - Determine risk category
   - Identify applicable requirements
   - Check for prohibited use cases

2. NIST AI RMF Evaluation
   - Govern: Policies, accountability, oversight
   - Map: Stakeholders, impacts, constraints
   - Measure: Metrics, testing, monitoring
   - Manage: Mitigations, responses

3. Responsible AI Assessment
   - Fairness evaluation
   - Transparency requirements
   - Accountability structures
   - Privacy considerations
   - Safety measures
   - Human oversight mechanisms

4. Ethical Impact Assessment
   - Stakeholder analysis
   - Potential harms identification
   - Benefit-harm balance
   - Vulnerable population impact

5. Documentation Requirements
   - Technical documentation
   - Model card
   - Risk assessments
   - Human oversight procedures

6. Compliance Roadmap
   - Gap identification
   - Remediation priorities
   - Timeline for compliance

Provide a complete AI governance assessment with:
- Risk classification with justification
- Compliance gaps by framework
- Ethical risk evaluation
- Remediation roadmap
```

### Step 4: Generate Assessment Report

Ensure the report includes:

- Executive summary with risk classification
- Framework compliance assessment
- Ethical impact evaluation
- Prioritized remediation plan
- Ongoing monitoring requirements

## Example Usage

```bash
# Assess a hiring AI system
/compliance-planning:assess-ai "AI-powered resume screening and candidate ranking"

# Assess a customer service chatbot
/compliance-planning:assess-ai "customer service chatbot for financial services"

# Assess a content moderation system
/compliance-planning:assess-ai "automated content moderation for social platform"
```

## Output Format

```markdown
# AI Governance Assessment: [System Name]

## Executive Summary

### EU AI Act Classification: [UNACCEPTABLE / HIGH RISK / LIMITED / MINIMAL]

**Justification:**
[Why this classification applies]

### Overall Governance Readiness: [HIGH / MEDIUM / LOW]

| Framework | Score | Status |
|-----------|-------|--------|
| EU AI Act | [X/10] | [Status] |
| NIST AI RMF | [X/10] | [Status] |
| Responsible AI | [X/10] | [Status] |

### Key Findings
- [Finding 1]
- [Finding 2]

---

## EU AI Act Compliance

### Risk Classification

**Category:** [Category]

**Applicable Requirements:**
| Requirement | Status | Gap |
|-------------|--------|-----|

### Prohibited Use Check
- [ ] Not social scoring
- [ ] Not subliminal manipulation
- [ ] Not exploiting vulnerabilities
- [ ] [Other checks]

---

## NIST AI RMF Assessment

### Govern
| Requirement | Status | Gap |
|-------------|--------|-----|

### Map
| Requirement | Status | Gap |
|-------------|--------|-----|

### Measure
| Requirement | Status | Gap |
|-------------|--------|-----|

### Manage
| Requirement | Status | Gap |
|-------------|--------|-----|

---

## Responsible AI Assessment

### Fairness
| Metric | Status | Finding |
|--------|--------|---------|

### Transparency
| Requirement | Status | Gap |
|-------------|--------|-----|

### Accountability
| Requirement | Status | Gap |
|-------------|--------|-----|

### Human Oversight
| Mechanism | Status | Gap |
|-----------|--------|-----|

---

## Ethical Impact Assessment

### Stakeholder Impact
| Stakeholder | Impact Type | Severity | Mitigation |
|-------------|-------------|----------|------------|

### Potential Harms
| Harm | Likelihood | Severity | Mitigation |
|------|------------|----------|------------|

---

## Documentation Status

- [ ] Technical documentation
- [ ] Model card
- [ ] Data documentation
- [ ] Risk assessment
- [ ] Human oversight procedures
- [ ] Monitoring plan

---

## Remediation Roadmap

### Phase 1: Critical (High-Risk Systems)
1. [Action with owner and deadline]

### Phase 2: Compliance Requirements
1. [Action]

### Phase 3: Best Practices
1. [Action]

---

## Ongoing Monitoring

| Metric | Target | Frequency | Owner |
|--------|--------|-----------|-------|
```
