---
name: analyze-automation-roi
description: Analyze automation ROI for test cases and recommend which tests to automate based on value and effort. Use for prioritizing test automation investments.
allowed-tools: Read, Glob, Grep, Skill
argument-hint: [test-inventory-or-feature]
---

# Analyze Automation ROI Command

Evaluate test cases for automation potential and calculate ROI to prioritize automation efforts.

## Process

### Step 1: Gather Test Inventory

Collect test cases to evaluate:

- From test documentation
- From existing manual test scripts
- From user description

### Step 2: Load Skills

Invoke the `test-strategy:automation-strategy` skill for ROI calculation patterns.

### Step 3: Evaluate Each Test

For each test case, assess:

**Selection Criteria (Score 1-5):**

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Execution Frequency | 25% | How often is it run? |
| Business Criticality | 25% | How important to business? |
| Stability | 20% | How stable is the feature? |
| Automation Complexity | 15% | How hard to automate? |
| Data Availability | 15% | Is test data available? |

### Step 4: Calculate Scores

```markdown
| Test Case | Freq | Crit | Stable | Complex | Data | Score |
|-----------|------|------|--------|---------|------|-------|
| TC-001 Login | 5 | 5 | 5 | 4 | 5 | 4.8 |
| TC-002 Checkout | 4 | 5 | 4 | 3 | 4 | 4.1 |
| TC-003 Reporting | 2 | 3 | 5 | 2 | 3 | 2.9 |
```

### Step 5: Calculate ROI

For high-scoring candidates:

```markdown
## ROI Analysis: TC-001 Login

**Manual Execution:**
- Time per run: 15 minutes
- Runs per month: 20
- Duration: 12 months
- Total manual time: 15 × 20 × 12 = 3,600 minutes = 60 hours

**Automation Cost:**
- Development: 4 hours
- Monthly maintenance: 0.5 hours
- Total maintenance: 0.5 × 12 = 6 hours
- Total cost: 4 + 6 = 10 hours

**ROI Calculation:**
- Time saved: 60 - 10 = 50 hours
- ROI: (50 / 10) × 100 = 500%
- Breakeven: 4 / (0.25 - 0.04) = 19 executions (1 month)
```

### Step 6: Prioritize Recommendations

Categorize by decision:

```markdown
## Automation Recommendations

### Automate First (Score ≥ 4.0, ROI > 300%)
| Test | Score | ROI | Est. Effort |
|------|-------|-----|-------------|
| TC-001 Login | 4.8 | 500% | 4 hours |
| TC-004 Cart | 4.2 | 400% | 6 hours |

### Automate Later (Score 3.0-3.9, ROI 100-300%)
| Test | Score | ROI | Est. Effort |
|------|-------|-----|-------------|
| TC-002 Checkout | 4.1 | 250% | 8 hours |

### Keep Manual (Score < 3.0 or ROI < 100%)
| Test | Score | ROI | Reason |
|------|-------|-----|--------|
| TC-003 Reporting | 2.9 | 80% | Complex, rarely run |
| TC-005 Admin config | 2.5 | 50% | Changes frequently |

### Technical Blockers
| Test | Issue | Resolution |
|------|-------|------------|
| TC-006 External API | Rate limited | Mock service needed |
```

### Step 7: Output Report

```markdown
## Automation ROI Analysis Complete

**Tests Analyzed**: [count]
**Recommended for Automation**: [count] ([%])
**Total Potential Hours Saved**: [X] hours/year
**Investment Required**: [Y] hours

### Summary

| Category | Count | % |
|----------|-------|---|
| Automate First | X | X% |
| Automate Later | Y | Y% |
| Keep Manual | Z | Z% |

### Priority Roadmap

**Sprint 1** (Est. 20 hours):
1. TC-001 Login - 4 hours
2. TC-004 Cart - 6 hours
3. TC-007 Search - 10 hours

**Sprint 2** (Est. 24 hours):
4. TC-002 Checkout - 8 hours
5. TC-008 Profile - 8 hours
6. TC-009 History - 8 hours

### Expected Benefits
- Year 1 savings: [X] hours
- Year 2 savings: [Y] hours (with maintained suite)
- Regression time reduction: [Z]%
```

## Examples

**Analyze test inventory:**

```bash
/test-strategy:analyze-automation-roi docs/test-cases/
```

**Specific feature:**

```bash
/test-strategy:analyze-automation-roi checkout flow tests
```

**Quick assessment:**

```bash
/test-strategy:analyze-automation-roi "Login, cart, checkout, order history"
```
