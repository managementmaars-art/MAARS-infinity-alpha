# ADR Spike Reference Documentation

Detailed technical documentation for the create-adr-spike skill.

## Python Example Scripts

The following utility scripts demonstrate practical usage:

- [validate_adr.py](../examples/validate_adr.py) - ADR validation utility for checking format, status, and completeness

---

## Table of Contents

1. [ADR Template Deep-Dive](#adr-template-deep-dive)
2. [Research Phase Details](#research-phase-details)
3. [Analysis Framework](#analysis-framework)
4. [Memory Graph Schema](#memory-graph-schema)
5. [Tool Usage Guide](#tool-usage-guide)
6. [Validation Rules](#validation-rules)

---

## ADR Template Deep-Dive

### Required Sections

#### 1. Status
**Values:** Proposed | Accepted | In Progress | Completed | Superseded

**Meaning:**
- **Proposed:** Initial draft, seeking stakeholder approval
- **Accepted:** Decision approved, implementation plan agreed
- **In Progress:** Active implementation underway
- **Completed:** Fully implemented, verified, and quality gates passed
- **Superseded:** Decision replaced by newer ADR (reference replacement ADR)

**Rules:**
- New ADRs start as "Proposed"
- Move to "Accepted" after review/approval
- Move to "In Progress" when implementation begins
- Move to "Completed" only when ALL completion criteria met
- Set to "Superseded" if replaced (never delete old ADRs)

---

#### 2. Date
**Format:** YYYY-MM-DD

**Meaning:** Date of initial proposal (not implementation date)

**Rules:**
- Use ISO 8601 format
- Date does not change when status changes
- Implementation dates tracked in "Progress Log" section

---

#### 3. Context

**Purpose:** Explain WHY this decision is needed.

**Sub-sections:**
- **Problem Statement:** What issue are we addressing?
- **Current State:** What exists today?
- **Motivation:** Why now? What's driving this?

**Good Context Example:**
```markdown
### Problem Statement
Current error handling is inconsistent across services. Some methods throw exceptions,
others return None, and some use boolean flags. This leads to silent failures and
difficult debugging.

### Current State
Of 53 service methods analyzed:
- 23 (43%) return None on error
- 18 (34%) raise exceptions
- 12 (23%) return boolean success flags

### Motivation
Recent production incident (INCIDENT-2025-042) was caused by a silent None return
that propagated through 3 layers before causing a type error. We need explicit,
type-safe error handling.
```

**Bad Context Example:**
```markdown
### Problem Statement
Error handling is bad.

### Current State
We have some errors.

### Motivation
We should fix it.
```

---

#### 4. Decision

**Purpose:** State WHAT is being decided.

**Sub-sections:**
- **Scope:** What files/modules affected?
- **Pattern/Approach:** What are we adopting?
- **Implementation Strategy:** How will we roll this out?

**Good Decision Example:**
```markdown
### Decision
Adopt the ServiceResult[T] pattern for all service method returns across the
application layer.

### Scope
All methods in:
- src/application/services/*.py (12 files)
- src/application/commands/*.py (8 files)
- src/application/queries/*.py (6 files)

### Pattern/Approach
ServiceResult is a generic wrapper type:
- `ServiceResult.success(value)` for successful operations
- `ServiceResult.failure(error)` for failures
- Explicit is_success/is_failure checks required
- No exception-based control flow

### Implementation Strategy
1. Implement ServiceResult class in domain/common/
2. Migrate repository interfaces first
3. Update application services incrementally
4. Update all tests
5. Remove exception-based error handling
```

---

#### 5. Consequences

**Purpose:** Document IMPACTS of the decision.

**Sub-sections:**
- **Positive:** What improves?
- **Negative:** What gets harder?
- **Migration Strategy:** How to transition?

**Good Consequences Example:**
```markdown
### Positive
- Type-safe error handling (compiler enforces checks)
- Explicit control flow (no hidden exception paths)
- Better error context (error messages at point of failure)
- Composable (results chain together cleanly)

### Negative
- More verbose code (explicit success/failure checks)
- Learning curve for team (new pattern to learn)
- Refactoring cost (53 methods to update)

### Migration Strategy
- Phase 1 (Week 1): Implement ServiceResult, update repository interfaces
- Phase 2 (Week 2): Migrate application services
- Phase 3 (Week 3): Update tests, remove old error handling
- Run both patterns in parallel during Phase 2
```

**Why This Matters:**
- Forces honest assessment of trade-offs
- Prevents "silver bullet" thinking
- Surfaces hidden costs early
- Helps stakeholders make informed decisions

---

#### 6. Alternatives Considered

**Purpose:** Prove due diligence, justify choice.

**Required Elements:**
- At least 2-3 alternatives
- Pros and cons for each
- Reason for rejection

**Good Alternatives Example:**
```markdown
### Alternative 1: Continue with Exceptions
**Pros:**
- Standard Python approach
- No code changes required
- Familiar to all team members

**Cons:**
- Hidden control flow
- Easy to forget error handling
- Loses error context in deep call stacks

**Reason for rejection:** Recent production incident showed exceptions lead to
silent failures when not caught properly. Need explicit error handling.

### Alternative 2: Optional[T] Returns
**Pros:**
- Simple to implement
- Type-safe (None vs value)
- Minimal learning curve

**Cons:**
- No error context (just None)
- Can't distinguish different failure modes
- Temptation to ignore None checks

**Reason for rejection:** Lack of error context makes debugging difficult.
Need to know WHY something failed, not just that it failed.

### Alternative 3: Go-style (value, error) Tuples
**Pros:**
- Explicit error handling
- Error context preserved
- Familiar pattern from Go

**Cons:**
- Not type-safe in Python (can ignore error)
- Verbose unpacking required
- No multiple return value destructuring

**Reason for rejection:** Python lacks Go's multiple return value ergonomics.
Tuple unpacking is error-prone.
```

---

#### 7. Implementation Tracking (for Refactor/Migration ADRs)

**Purpose:** Track progress during implementation.

**Sub-sections:**
- **Files Under Refactor:** Table of affected files with status
- **Completion Criteria:** Checklist of requirements
- **Active Tracking:** Link to todo.md section
- **Blockers:** Issues blocking progress

**Files Under Refactor Table:**
| File | Status | Methods/Classes Affected | Notes |
|------|--------|--------------------------|-------|
| src/application/services/indexing_service.py | ✅ Complete | index_file, index_repository | Tests passing |
| src/application/services/graph_service.py | 🟡 In Progress | query_graph, update_graph | Needs test updates |
| src/application/services/search_service.py | ⭕ Not Started | search_code, search_semantic | Waiting on graph_service |

**Status Icons:**
- ⭕ Not Started
- 🟡 In Progress
- ✅ Complete

**Completion Criteria Checklist:**
- [ ] All affected files refactored
- [ ] All tests updated and passing
- [ ] Quality gates pass (pyright, ruff, pytest, vulture)
- [ ] Documentation updated
- [ ] Code review completed
- [ ] Refactor markers removed from code

---

#### 8. Progress Log

**Purpose:** Chronological record of implementation milestones.

**Format:**
```markdown
### YYYY-MM-DD - Milestone Title
Description of progress, blockers resolved, decisions made during implementation.

### YYYY-MM-DD - Milestone Title
...
```

**Example:**
```markdown
### 2025-10-10 - Started Infrastructure Layer Migration
Began migrating infrastructure services to ServiceResult pattern. Started with
CodeRepository as it has clear error cases.

### 2025-10-12 - CodeRepository Complete
Completed CodeRepository migration. All 8 methods now return ServiceResult.
Tests updated and passing. Discovered need for better error messages in
file parsing errors.

### 2025-10-14 - Blocker: Test Mocking
Tests failing due to mocks returning dict instead of ServiceResult. Created
helper function to create mock ServiceResults. Updated test infrastructure
documentation.

### 2025-10-15 - Application Layer Complete
All application services migrated. Quality gates passing. Ready for code review.
```

---

## Research Phase Details

### Internal Research (Existing Knowledge)

#### 1. Search Existing ADRs
```bash
# Search by keyword
find docs/adr -name "*.md" -type f -exec grep -l "keyword" {} \;

# Search by number
find docs/adr -name "*027*"

# List recent ADRs
find docs/adr -name "*.md" -type f -printf "%T+ %p\n" | sort -r | head -10
```

#### 2. Search Memory Graph
```python
# Search for related decisions
mcp__memory__search_memories(query="error handling patterns")

# Find specific ADR entity
mcp__memory__find_memories_by_name(names=["ADR-003: ServiceResult Pattern"])

# Expected results: entities with observations about the decision
```

#### 3. Search Codebase (if applicable)
```bash
# Find current pattern usage
grep -r "pattern_name" src/

# Count occurrences
grep -r "pattern_name" src/ | wc -l

# Find affected files
grep -rl "pattern_name" src/
```

---

### External Research (New Information)

#### 1. Library Documentation (Context7)
```python
# Resolve library ID
result = mcp__context7__resolve-library-id(libraryName="library-name")

# Get documentation
docs = mcp__context7__get-library-docs(
    context7CompatibleLibraryID="/org/project",
    topic="specific-topic",
    tokens=5000
)
```

**Use when:**
- Evaluating third-party libraries
- Checking API compatibility
- Understanding best practices

---

#### 2. Web Search (Recent Discussions)
```python
# Search for comparisons
WebSearch(query="PostgreSQL vs Neo4j performance benchmark 2025")

# Search for issues
WebSearch(query="library-name known issues production")

# Search for migration guides
WebSearch(query="migrating from X to Y best practices")
```

**Use when:**
- Finding recent benchmarks
- Checking community sentiment
- Discovering gotchas/edge cases

---

#### 3. Web Fetch (Specific Documentation)
```python
# Fetch specific page
WebFetch(
    url="https://docs.example.com/best-practices",
    prompt="Extract best practices for X"
)
```

**Use when:**
- Need specific documentation page
- Extract code examples
- Get official recommendations

---

## Analysis Framework

### Decision Matrix Template

| Criteria | Weight | Option A | Option B | Option C |
|----------|--------|----------|----------|----------|
| Performance | 30% | 9/10 | 7/10 | 5/10 |
| Maintainability | 25% | 7/10 | 9/10 | 6/10 |
| Cost | 20% | 8/10 | 5/10 | 9/10 |
| Team Fit | 15% | 9/10 | 6/10 | 7/10 |
| Scalability | 10% | 8/10 | 9/10 | 6/10 |
| **Total** | **100%** | **8.1** | **7.4** | **6.7** |

**How to Use:**
1. Identify evaluation criteria (what matters for this decision?)
2. Assign weights (what's most important?)
3. Score each option (0-10 scale)
4. Calculate weighted total
5. Use as input to decision (not final answer)

**Warning:** Matrix is a tool, not a replacement for judgment. Consider qualitative factors that don't fit neatly into scores.

---

### Risk Assessment Template

For each option, identify:

**Risks:**
- What could go wrong?
- What assumptions are we making?
- What don't we know?

**Impact:**
- High: Project-threatening
- Medium: Significant delay/rework
- Low: Minor inconvenience

**Probability:**
- High: >50% chance
- Medium: 20-50% chance
- Low: <20% chance

**Mitigation:**
- How can we reduce probability?
- How can we reduce impact?
- What's our fallback plan?

**Example:**
| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Library abandoned | High | Low | Check maintenance activity, have migration path |
| Performance issues at scale | High | Medium | Run benchmarks, prototype critical path |
| Team learning curve | Medium | High | Training plan, pair programming, documentation |

---

## Memory Graph Schema

### Entity Structure

```python
{
    "name": "ADR-{number}: {title}",
    "type": "ArchitectureDecision",
    "observations": [
        "Status: {status}",
        "Date: {date}",
        "Decision: {brief description of chosen option}",
        "Rationale: {key reason for choice}",
        "Alternatives: {comma-separated list of rejected options}",
        "Impact: {affected components/layers}",
        "Location: docs/adr/{status_dir}/{number}-{slug}.md"
    ]
}
```

### Relation Types

**supersedes:**
```python
{
    "source": "ADR-027: New Decision",
    "target": "ADR-015: Old Decision",
    "relationType": "supersedes"
}
```

**relates-to:**
```python
{
    "source": "ADR-027: Indexing Orchestrator",
    "target": "ADR-001: Clean Architecture",
    "relationType": "relates-to"
}
```

**impacts:**
```python
{
    "source": "ADR-003: ServiceResult Pattern",
    "target": "Application Layer",
    "relationType": "impacts"
}
```

**implements:**
```python
{
    "source": "ADR-003: ServiceResult Pattern",
    "target": "Fail-Fast Principle",
    "relationType": "implements"
}
```

---

## Tool Usage Guide

### Read Tool
**Use for:** Reading existing ADRs, templates, code files

```python
Read(file_path="/absolute/path/to/docs/adr/implemented/003-service-result-pattern.md")
```

### Grep Tool
**Use for:** Searching codebase for patterns, finding affected files

```python
Grep(
    pattern="ServiceResult",
    path="src/",
    output_mode="files_with_matches"
)
```

### Glob Tool
**Use for:** Finding files by pattern

```python
Glob(pattern="**/docs/adr/**/*.md")
```

### Bash Tool
**Use for:** Running scripts, finding ADR numbers

```bash
# Find next ADR number
find docs/adr -name "[0-9]*.md" | \
  sed 's/.*\/\([0-9]*\)-.*/\1/' | \
  sort -n | tail -1
```

### Write Tool
**Use for:** Creating new ADR files

```python
Write(
    file_path="/absolute/path/to/docs/adr/not_started/028-new-decision.md",
    content=adr_content
)
```

**Important:** Always use absolute paths, never relative paths.

---

## Validation Rules

### ADR Completeness Checklist

- [ ] Status is one of: Proposed | Accepted | In Progress | Completed | Superseded
- [ ] Date is in YYYY-MM-DD format
- [ ] Context section has Problem Statement, Current State, Motivation
- [ ] Decision section has Scope, Pattern/Approach
- [ ] Consequences section has Positive, Negative, Migration Strategy
- [ ] At least 2 alternatives documented with pros/cons
- [ ] All sections completed (no placeholder text like "[TODO]")
- [ ] Filename matches format: `{3-digit-number}-{kebab-case-title}.md`
- [ ] ADR number is sequential (check existing ADRs)
- [ ] ADR placed in correct directory based on status

### Memory Entity Validation

- [ ] Entity name follows format: "ADR-{number}: {title}"
- [ ] Entity type is "ArchitectureDecision"
- [ ] At least 5 observations (status, date, decision, rationale, location)
- [ ] Relations created to affected components (if applicable)
- [ ] Relations created to related ADRs (if applicable)

### Research Completeness

- [ ] Searched existing ADRs for related decisions
- [ ] Searched memory graph for patterns
- [ ] Consulted external resources if needed (Context7, WebSearch)
- [ ] Documented research artifacts in `.claude/artifacts/`
- [ ] Referenced research in ADR's "References" section

---

## Advanced Techniques

### Superseding an Existing ADR

When a new decision replaces an old one:

1. Create new ADR with next sequential number
2. Set old ADR's status to "Superseded"
3. Add note to old ADR: `**Superseded by:** ADR-XXX: New Decision`
4. Reference old ADR in new ADR's "Context" section
5. Create memory relation: new ADR supersedes old ADR
6. **Never delete old ADRs** (preserve history)

### Handling Blocked Decisions

When decision requires more information:

1. Create ADR with status "Proposed"
2. Document what's known so far
3. Add "Blockers" section listing unknowns
4. Create research tasks in todo.md
5. Update ADR as information discovered
6. Move to "Accepted" when blockers resolved

### Multi-ADR Decisions

When decision spans multiple areas:

1. Create parent ADR for overall decision
2. Create child ADRs for specific areas
3. Cross-reference in "References" section
4. Use memory relations to link parent/child

Example:
- Parent: ADR-027: Indexing Orchestrator Extraction
- Child: ADR-028: Phase 1 Implementation
- Child: ADR-029: Phase 2 Testing Strategy

---

## Troubleshooting

### "Can't find next ADR number"
**Problem:** Unsure what number to use for new ADR

**Solution:**
```bash
find docs/adr -name "[0-9]*.md" | \
  sed 's/.*\/\([0-9]*\)-.*/\1/' | \
  sort -n | tail -1
```
Use number + 1

---

### "ADR exists in multiple directories"
**Problem:** Same-numbered ADR in multiple status directories

**Solution:** This should never happen. Investigate:
```bash
find docs/adr -name "027-*"
```
If duplicates found, check git history to determine correct version.

---

### "Memory entity already exists"
**Problem:** ADR entity already in memory graph

**Solution:** Use add_observations to update instead of create_entities:
```python
mcp__memory__add_observations(observations=[{
    "entityName": "ADR-027: Title",
    "observations": ["New observation"]
}])
```

---

### "Template missing required section"
**Problem:** Project's template doesn't match expected structure

**Solution:** Adapt to project's template. Core required sections:
- Status
- Context (problem statement)
- Decision (chosen approach)
- Consequences (positive/negative)
- Alternatives (rejected options)

If project template missing a section, add it to ADR anyway.

---

## References

- [ADR Directory Guide](../../docs/ADR-DIRECTORY-GUIDE.md)
- [Refactor Marker Guide](../../detect-refactor-markers/references/refactor-marker-guide.md)
- [ARCHITECTURE.md](../../ARCHITECTURE.md)
- [Michael Nygard's ADR Template](https://github.com/joelparkerhenderson/architecture-decision-record/blob/main/templates/decision-record-template-by-michael-nygard/index.md)
- [ADR Tools](https://github.com/npryce/adr-tools)

---

**Last Updated:** 2025-10-17
