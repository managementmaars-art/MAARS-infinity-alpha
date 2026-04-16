---
name: analyze-pyramid
description: Analyze test pyramid health by examining test distribution across unit, integration, and E2E levels. Use for test portfolio assessment and rebalancing recommendations.
allowed-tools: Read, Glob, Grep, Bash, Skill, Task
argument-hint: [test-directory]
---

# Analyze Test Pyramid Command

Analyze the current test distribution and recommend improvements for a healthier test pyramid.

## Process

### Step 1: Discover Tests

If a test directory is provided, use it. Otherwise, search for common test patterns:

```bash
# .NET projects
find . -name "*.Tests.csproj" -o -name "*Tests*.csproj"
find . -name "*Test*.cs" -type f

# Count tests
grep -r "\[Fact\]\|\[Theory\]" --include="*.cs" | wc -l
```

### Step 2: Categorize Tests

Identify test levels by project/folder naming:

- **Unit**: `*.Unit.Tests`, `*.Domain.Tests`
- **Integration**: `*.Integration.Tests`, `*.Api.Tests`
- **E2E**: `*.E2E.Tests`, `*.Acceptance.Tests`

Count tests at each level:

```markdown
| Level | Project | Test Count |
|-------|---------|------------|
| Unit | MyApp.Domain.Tests | 150 |
| Unit | MyApp.Application.Tests | 80 |
| Integration | MyApp.Api.Tests | 60 |
| E2E | MyApp.E2E.Tests | 40 |
```

### Step 3: Load Pyramid Skill

Invoke the `test-strategy:test-pyramid-design` skill for shape analysis patterns.

### Step 4: Analyze Distribution

Calculate percentages and identify shape:

```markdown
## Current Distribution

| Level | Count | Percentage | Target |
|-------|-------|------------|--------|
| Unit | 230 | 70% | 70% ✅ |
| Integration | 60 | 18% | 20% ✅ |
| E2E | 40 | 12% | 10% ⚠️ |

**Shape Assessment**: Near-healthy pyramid with slight E2E heaviness
```

### Step 5: Identify Anti-Patterns

Check for common issues:

- **Ice Cream Cone**: E2E > 30%
- **Hourglass**: Integration > 50%
- **Inverted Pyramid**: Unit < 50%
- **Missing Layer**: Any level at 0%

### Step 6: Generate Recommendations

Based on analysis:

```markdown
## Recommendations

### Immediate Actions
1. **Reduce E2E tests** by 2% (8 tests)
   - Review for tests that can be pushed to integration level
   - Identify tests duplicating lower-level coverage

### Test Migration Candidates
| Current Level | Candidate | Recommended Level | Reason |
|---------------|-----------|-------------------|--------|
| E2E | Login validation | Integration | API test sufficient |
| E2E | Form validation | Unit | Pure logic test |
| Integration | Data transform | Unit | No I/O needed |

### Coverage Gaps
- Unit tests needed for: [business logic areas]
- Integration tests needed for: [API boundaries]
```

### Step 7: Output Report

````markdown
## Test Pyramid Analysis Complete

**Current Shape**: [Shape name]

**Distribution**:
```text

     ▲
    ███  E2E: 12%
   █████ Integration: 18%
  ███████ Unit: 70%

```

**Health Score**: [X/10]

**Key Findings**:
1. [Finding 1]
2. [Finding 2]

**Recommended Actions**:
1. [Action 1]
2. [Action 2]
````

## Examples

**Analyze current directory:**

```bash
/test-strategy:analyze-pyramid
```

**Specify test directory:**

```bash
/test-strategy:analyze-pyramid tests/
```
