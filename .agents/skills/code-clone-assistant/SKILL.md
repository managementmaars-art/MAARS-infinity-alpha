---
name: code-clone-assistant
description: Detect and refactor code duplication with PMD CPD. TRIGGERS - code clones, DRY violations, duplicate code.
allowed-tools: Read, Grep, Bash, Edit, Write
---

# Code Clone Assistant

Detect code clones and guide refactoring using PMD CPD (exact duplicates) + Semgrep (patterns).

> **Self-Evolving Skill**: This skill improves through use. If instructions are wrong, parameters drifted, or a workaround was needed — fix this file immediately, don't defer. Only update for real, reproducible issues.

## Tools

- **PMD CPD v7.17.0+**: Exact duplicate detection
- **Semgrep v1.140.0+**: Pattern-based detection

**Tested**: October 2025 - 30 violations detected across 3 sample files
**Coverage**: ~3x more violations than using either tool alone

---

## When to Use This Skill

Use this skill when:

- Finding duplicate code in a codebase
- Detecting DRY violations
- Refactoring similar code patterns
- Identifying copy-paste code

---

## Why Two Tools?

PMD CPD and Semgrep detect different clone types:

| Aspect       | PMD CPD                          | Semgrep                          |
| ------------ | -------------------------------- | -------------------------------- |
| **Detects**  | Exact copy-paste duplicates      | Similar patterns with variations |
| **Scope**    | Across files ✅                  | Within/across files (Pro only)   |
| **Matching** | Token-based (ignores formatting) | Pattern-based (AST matching)     |
| **Rules**    | ❌ No custom rules               | ✅ Custom rules                  |

**Result**: Using both finds ~3x more DRY violations.

### Clone Types

| Type   | Description                     | PMD CPD         | Semgrep     |
| ------ | ------------------------------- | --------------- | ----------- |
| Type-1 | Exact copies                    | ✅ Default      | ✅          |
| Type-2 | Renamed identifiers             | ✅ `--ignore-*` | ✅          |
| Type-3 | Near-miss with variations       | ⚠️ Partial      | ✅ Patterns |
| Type-4 | Semantic clones (same behavior) | ❌              | ❌          |

---

## Quick Start Workflow

```bash
# Step 1: Detect exact duplicates (PMD CPD)
pmd cpd -d . -l python --minimum-tokens 20 -f markdown > pmd-results.md

# Step 2: Detect pattern violations (Semgrep)
semgrep --config=clone-rules.yaml --sarif --quiet > semgrep-results.sarif

# Step 3: Analyze combined results (Claude Code)
# Parse both outputs, prioritize by severity

# Step 4: Refactor (Claude Code with user approval)
# Extract shared functions, consolidate patterns, verify tests
```

---

---

## Accepted Exceptions (Known Intentional Duplication)

Not all code duplication is a problem. Some codebases deliberately use copy-and-adapt patterns where refactoring would be harmful. When running clone detection, **always check for accepted exceptions before recommending refactoring**.

### When Duplication Is Acceptable

| Pattern                                         | Why Acceptable                                                                                                                                                                                                    | Example                                                            |
| ----------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| **Generation-per-directory experiments**        | Each generation is an immutable, self-contained experiment. Sharing code across generations would break provenance and make past experiments non-reproducible.                                                    | SQL templates, sweep scripts where each `gen{NNN}/` is independent |
| **SQL templates with placeholder substitution** | SQL has no import/include mechanism. Templates use `sed` placeholder replacement (`__PLACEHOLDER__`), not function calls. Extracting shared CTEs into separate files would break the single-file execution model. | ClickHouse sweep templates sharing signal detection + metrics CTEs |
| **Protocol/schema boilerplate**                 | Serialization formats, API contracts, and wire protocols require exact structure in each location. Abstracting them hides the contract.                                                                           | NDJSON telemetry line construction in wrapper scripts              |
| **Test fixtures and golden files**              | Test data intentionally duplicates production patterns to verify behavior. Sharing fixtures creates brittle cross-test dependencies.                                                                              | Test setup code, expected output snapshots                         |

### How to Report Accepted Exceptions

When clone detection finds duplication that matches an accepted exception pattern:

1. **Report it** — always show the user what was found (lines, tokens, files)
2. **Flag as accepted** — explicitly state it matches a known exception pattern
3. **Explain why** — cite the specific reason refactoring is not recommended
4. **Do NOT recommend refactoring** — this is the key difference from actionable findings

**Example output format**:

```
Code Clone Analysis Results

PMD CPD Findings:
  Clone 1: 115 lines (575 tokens) — base_bars → signals CTEs
    gen610_template.sql:33 ↔ gen710_template.sql:38
    Status: ACCEPTED EXCEPTION (generation-per-directory experiment)
    Reason: Each generation is immutable. Shared CTEs would break
            experiment provenance and reproducibility.

  Clone 2: 36 lines (478 tokens) — metrics aggregation
    gen610_template.sql:207 ↔ gen710_template.sql:244
    Status: ACCEPTED EXCEPTION (SQL template without include mechanism)

Actionable Findings: 0
Accepted Exceptions: 2
```

### Project-Level Exception Configuration

Projects can declare accepted exception patterns in their `CLAUDE.md`:

```markdown
## Code Clone Exceptions

- `sql/gen*_template.sql` — generation-per-directory experiments (immutable)
- `scripts/gen*/` — copy-and-adapt sweep scripts (no shared infrastructure)
- `tests/fixtures/` — intentional duplication for test isolation
```

When this section exists in a project's `CLAUDE.md`, the code-clone-assistant should check it before classifying findings.

---

## Reference Documentation

For detailed information, see:

- [Detection Commands](./references/detection-commands.md) - PMD CPD and Semgrep command details
- [Complete Workflow](./references/complete-workflow.md) - Detection, analysis, and presentation phases
- [Refactoring Strategies](./references/refactoring-strategies.md) - Approaches for addressing violations

---

## Troubleshooting

| Issue                      | Cause                        | Solution                                         |
| -------------------------- | ---------------------------- | ------------------------------------------------ |
| PMD CPD not found          | Not installed or not in PATH | `brew install pmd` or download from PMD releases |
| Semgrep timeout            | Large codebase scan          | Use `--exclude` to limit scope                   |
| No duplicates detected     | minimum-tokens too high      | Lower `--minimum-tokens` value (try 15)          |
| Too many false positives   | minimum-tokens too low       | Increase `--minimum-tokens` (try 30+)            |
| Language not recognized    | Wrong `-l` flag              | Check PMD CPD supported languages list           |
| SARIF parse error          | Semgrep output malformed     | Upgrade Semgrep to latest version                |
| Memory error on large repo | Java heap too small          | Set `PMD_JAVA_OPTS=-Xmx4g`                       |
| Missing clone rules file   | Custom rules not created     | Create `clone-rules.yaml` or use default config  |


## Post-Execution Reflection

After this skill completes, check before closing:

1. **Did the command succeed?** — If not, fix the instruction or error table that caused the failure.
2. **Did parameters or output change?** — If the underlying tool's interface drifted, update Usage examples and Parameters table to match.
3. **Was a workaround needed?** — If you had to improvise (different flags, extra steps), update this SKILL.md so the next invocation doesn't need the same workaround.

Only update if the issue is real and reproducible — not speculative.
