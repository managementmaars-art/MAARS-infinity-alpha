**Skill**: [Code Clone Assistant](../SKILL.md)

## Complete Detection Workflow

### Phase 1: Detection

```bash
/usr/bin/env bash << 'CONFIG_EOF'
# Create working directory
mkdir -p /tmp/dry-audit-$(date +%Y%m%d)
cd /tmp/dry-audit-$(date +%Y%m%d)

# Run both tools
pmd cpd -d /path/to/project -l python --minimum-tokens 20 -f markdown > pmd-cpd.md
semgrep --config=/path/to/clone-rules.yaml --sarif --quiet /path/to/project > semgrep.sarif
CONFIG_EOF
```

### Phase 2: Analysis

```bash
# Parse PMD CPD (direct read - LLM-native format)
cat pmd-cpd.md

# Parse Semgrep SARIF
jq -r '.runs[0].results[] | "\(.ruleId): \(.message.text) at \(.locations[0].physicalLocation.artifactLocation.uri):\(.locations[0].physicalLocation.region.startLine)"' semgrep.sarif
```

**Combine findings**:

1. List PMD CPD duplications by severity (tokens/lines)
1. List Semgrep violations by file
1. **Check for accepted exceptions** — read the project's `CLAUDE.md` for a "Code Clone Exceptions" section. Also check if the duplication matches any known acceptable pattern (see [Accepted Exceptions](../SKILL.md#accepted-exceptions-known-intentional-duplication))
1. Classify each finding as **actionable** or **accepted exception**
1. Prioritize actionable findings: Exact duplicates across files > Large within-file > Patterns

### Phase 3: Presentation

Present to user:

- Total findings (PMD + Semgrep)
- Breakdown: **actionable** vs **accepted exceptions**
- For actionable: files affected, estimated effort, suggested approach
- For accepted: which exception pattern applies and why refactoring is not recommended

**Example (with accepted exceptions)**:

```
Code Clone Analysis Results
===========================
PMD CPD: 5 duplications found
  Actionable: 2
  Accepted exceptions: 3

Accepted Exceptions:
1. 115 lines — base_bars → signals CTEs (gen610 ↔ gen710)
   Exception: generation-per-directory experiment (immutable provenance)
2. 36 lines — metrics aggregation SELECT (gen610 ↔ gen710)
   Exception: SQL template without include mechanism
3. 20 lines — trade_outcomes exit logic (gen610 ↔ gen710)
   Exception: generation-per-directory experiment (immutable provenance)

Actionable Findings:
1. process_user_data() duplicated in file1.py:5 and file2.py:5 (21 lines)
2. Duplicate validation logic across 6 locations (Semgrep)

Recommended Refactoring:
- Extract process_user_data() to shared utils module
- Create validate_input() function for validation logic

Proceed with refactoring? (y/n)
```

### Phase 4: Refactoring (With User Approval)

1. Read affected files using Read tool
1. Create shared functions/classes
1. Replace duplicates using Edit tool
1. Run tests using Bash tool
1. Commit changes if tests pass

---

## Best Practices

**DO**:

- ✅ Run both PMD CPD and Semgrep (complementary coverage)
- ✅ Check for accepted exceptions before recommending refactoring
- ✅ Read the project's `CLAUDE.md` for exception declarations
- ✅ Start with conservative thresholds (PMD: 50 tokens)
- ✅ Review results before refactoring
- ✅ Run full test suite after refactoring
- ✅ Commit incrementally

**DON'T**:

- ❌ Only use one tool (miss ~70% of violations)
- ❌ Set thresholds too low (noise overwhelms signal)
- ❌ Refactor without understanding context
- ❌ Recommend refactoring for accepted exceptions (intentional duplication)
- ❌ Skip test verification
