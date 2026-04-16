# ADR Template

## Purpose
An Architecture Decision Record (ADR) documents a significant architectural decision, including context, decision, and consequences. ADRs are immutable records that capture the "why" behind major technical choices.

## When to Create an ADR
- Significant architectural changes (layers, boundaries, patterns)
- Technology selection (frameworks, databases, libraries)
- Major refactorings that affect system structure
- API design decisions with long-term impact
- Performance optimization strategies affecting multiple components

## ADR Numbering
ADRs are numbered sequentially: `001`, `002`, `003`, etc.
Check existing ADRs in `/docs/adr/` to assign next available number.

## ADR Categories
- **feature**: New capability or user-facing functionality
- **refactor**: Code restructuring without behavior change
- **migrate**: Data/schema changes, version upgrades
- **bug**: Bug fixes with architectural implications

## Template Structure

```markdown
# ADR-XXX: <Decision Title>

**Status:** Proposed | Accepted | Deprecated | Superseded by ADR-YYY
**Date:** YYYY-MM-DD
**Deciders:** <Team/Person who makes final decision>
**Category:** feature | refactor | migrate | bug
**Context:** <One sentence: Spike that led to this ADR>

## Context

<What is the issue or situation we're addressing?>

### Background

<Historical context>
- What existed before this decision
- Why the current approach is insufficient
- What changed to necessitate this decision

### Problem Statement

<Clear, specific problem this ADR solves>

**Impact:**
- Who is affected (users, developers, systems)
- Severity (critical, high, medium, low)
- Urgency (immediate, short-term, long-term)

### Constraints

<Boundaries that limit our options>

**Technical Constraints:**
- Language/framework limitations
- Infrastructure requirements
- Performance requirements
- Compatibility requirements

**Business Constraints:**
- Time constraints (deadlines)
- Resource constraints (team size, budget)
- Compliance requirements
- SLA requirements

### Forces

<Conflicting concerns that must be balanced>

**Quality Attributes:**
- Performance vs Maintainability
- Flexibility vs Simplicity
- Speed vs Safety
- etc.

**Stakeholder Concerns:**
- Development team priorities
- Operations team priorities
- Business requirements
- User needs

## Decision

<What we've decided to do>

### Chosen Approach: <Name>

<Clear, specific description of the decision>

**Core Components:**
1. Component 1: Purpose and responsibilities
2. Component 2: Purpose and responsibilities
3. Component 3: Purpose and responsibilities

**Key Patterns:**
- Pattern 1: When and why to use it
- Pattern 2: When and why to use it

**Integration Points:**
- How this fits into existing architecture
- What existing code changes
- What new code is added

### Implementation Strategy

**Phase 1: <Phase Name>** (Timeline: X days/weeks)
- [ ] Task 1: Specific deliverable
- [ ] Task 2: Specific deliverable
- [ ] Task 3: Specific deliverable

**Success Criteria:**
- Measurable outcome 1
- Measurable outcome 2

**Phase 2: <Phase Name>** (Timeline: X days/weeks)
- [ ] Task 1: Specific deliverable
- [ ] Task 2: Specific deliverable

**Success Criteria:**
- Measurable outcome 1
- Measurable outcome 2

**Rollback Plan:**
If implementation fails or problems discovered:
1. Rollback step 1
2. Rollback step 2
3. Fallback approach

### Migration Path

<If this changes existing code>

**Before → After:**
```python
# Before (old pattern)
<code example>

# After (new pattern)
<code example>
```

**Migration Steps:**
1. Create new components (non-breaking)
2. Add adapters for old code to use new components
3. Migrate module 1 (can be done incrementally)
4. Migrate module 2
5. Remove old code once all migrations complete
6. Remove adapters

**Compatibility Period:**
- Old and new patterns supported: X weeks
- Deprecation warnings added: Week Y
- Old pattern removed: Week Z

### Validation Plan

**Tests Required:**
- [ ] Unit tests for new components
- [ ] Integration tests for boundaries
- [ ] E2E tests for workflows
- [ ] Performance tests (if applicable)
- [ ] Migration tests (old → new)

**Metrics to Monitor:**
- Metric 1: Baseline = X, Target = Y
- Metric 2: Baseline = X, Target = Y

**Review Gates:**
- [ ] Gate 1: Code review by @architecture-guardian
- [ ] Gate 2: Performance benchmarks meet targets
- [ ] Gate 3: All tests passing

## Consequences

<What happens as a result of this decision>

### Positive Consequences

**Technical Benefits:**
- ✓ Benefit 1
  - Specific impact (quantified if possible)
  - Why this is valuable
  - Example: "40% faster query times (from 500ms to 300ms)"

- ✓ Benefit 2
  - Specific impact
  - Why this is valuable

**Process Benefits:**
- ✓ Developer experience improvement
- ✓ Maintenance burden reduction
- ✓ Testing becomes easier

**Business Benefits:**
- ✓ Cost savings
- ✓ Faster feature delivery
- ✓ Better user experience

### Negative Consequences

**Technical Costs:**
- ✗ Cost 1
  - Specific impact
  - Why this is problematic
  - Mitigation strategy

- ✗ Cost 2
  - Specific impact
  - Mitigation strategy

**Process Costs:**
- ✗ Learning curve for team
- ✗ Migration effort required
- ✗ Documentation needs updating

**Business Costs:**
- ✗ Development time investment
- ✗ Risk of bugs during migration
- ✗ Opportunity cost (not doing other work)

### Trade-off Analysis

**What We Gain vs What We Lose:**

| Aspect | Gain | Lose | Net Assessment |
|--------|------|------|----------------|
| Performance | +40% query speed | +10% memory usage | Net positive |
| Maintainability | +Clean separation | +More files | Net positive |
| Complexity | +Clear patterns | +Initial learning | Net positive |

**Why These Trade-offs Are Acceptable:**

<Justification for accepting the negative consequences>

## Alternatives Considered

### Alternative 1: <Approach Name>

**Description:**
<What this approach would entail>

**Pros:**
- Advantage 1
- Advantage 2

**Cons:**
- Disadvantage 1
- Disadvantage 2

**Why Not Chosen:**
<Specific reason this was rejected>

### Alternative 2: <Approach Name>

<Repeat structure>

### Alternative 3: Do Nothing

**Current State:**
<What happens if we don't make this decision>

**Why Not Acceptable:**
<Specific reasons status quo is insufficient>

## Related Decisions

### Supersedes
- ADR-XXX: <Title> - Why this replaces that decision

### Superseded By
- ADR-YYY: <Title> - Why a newer decision replaces this one

### Related
- ADR-XXX: <Title> - How this relates
- ADR-YYY: <Title> - How this relates

### Depends On
- ADR-XXX: <Title> - Must be implemented first

### Influences
- ADR-YYY: <Title> - This decision affects that decision

## References

### Research
- Spike: [spike_name.md](.claude/artifacts/YYYY-MM-DD/analysis/{topic-slug}/spike_name.md) - Research that led to this ADR
- Note: Multi-file research uses topic subfolders (e.g., `analysis/langgraph-research/`)

### Internal
- Codebase: `path/to/file.py:123` - Relevant implementation
- Related docs: `/docs/other_doc.md` - Additional context

### External
- Documentation: [Title](URL) - Why this is relevant
- Blog post: [Title](URL) - Insight gained
- Academic paper: [Title](URL) - Research backing

### Standards
- CLAUDE.md: <Relevant section> - How this aligns with project principles
- Clean Architecture: <Principle> - How this respects boundaries
- ServiceResult Pattern: <Usage> - How this uses project patterns

## Review Notes

### Review Cycle 1 (YYYY-MM-DD)
**Reviewers:** @person1, @person2

**Feedback:**
- Concern 1: <Issue raised>
  - Resolution: <How addressed>
- Concern 2: <Issue raised>
  - Resolution: <How addressed>

**Outcome:** Approved | Needs revision | Rejected

### Review Cycle 2 (YYYY-MM-DD)
<If needed>

---

**Status:** Proposed
**Decision Date:** <When status changed to Accepted>
**Implemented By:** @person (when status = Accepted)
**Implementation Date:** <When fully implemented>
```

## ADR Lifecycle

### Status Flow
```
Proposed → Accepted → Implemented
         ↓
         Rejected
         ↓
         Deprecated
         ↓
         Superseded by ADR-XXX
```

### Status Definitions
- **Proposed**: Under review, not yet approved
- **Accepted**: Approved, ready for implementation
- **Implemented**: Fully implemented and validated
- **Rejected**: Reviewed and decided against
- **Deprecated**: Previously accepted, no longer recommended
- **Superseded**: Replaced by a newer ADR

## Best Practices

### Context Section
- **DO** explain the problem from first principles
- **DO** include metrics/evidence of the problem
- **DO** explain constraints honestly
- **DON'T** assume reader knows the background

### Decision Section
- **DO** be specific and concrete
- **DO** include code examples when helpful
- **DO** provide phased implementation plan
- **DON'T** be vague or abstract

### Consequences Section
- **DO** be honest about negative consequences
- **DO** quantify impacts when possible
- **DO** provide mitigation strategies
- **DON'T** oversell or hide downsides

### Alternatives Section
- **DO** seriously consider at least 3 alternatives
- **DO** explain why rejected fairly
- **DON'T** strawman alternatives

## Anti-Patterns

❌ **Decision without context**
```markdown
## Decision
Use Neo4j for graph queries.
```

✅ **Decision with full context**
```markdown
## Context
Current SQL database requires 5-join queries for relationship traversal,
resulting in 2000ms response times. User complaints increased 40%.

## Decision
Use Neo4j for graph queries to reduce relationship query time by 80%.
```

❌ **Vague consequences**
```markdown
## Consequences
This will be better.
```

✅ **Specific, measurable consequences**
```markdown
## Consequences
- ✓ Query times: 2000ms → 400ms (80% improvement)
- ✗ Adds second database to maintain (ops complexity)
- Trade-off acceptable: Performance is critical user need
```

❌ **No alternatives considered**
```markdown
## Alternatives
None. This is the only way.
```

✅ **Honest alternatives evaluation**
```markdown
## Alternatives
1. Optimize SQL with denormalization: Faster but harder to maintain
2. Add caching layer: Helps reads but stale data issues
3. Use graph database: Best for traversal, adds infrastructure

Why graph chosen: Traversal is core use case, justifies infra cost
```

## Example: Complete ADR

See ADR-012 in `/docs/adr/012-context-management-integration.md` for a reference implementation.

## Promoting from Spike

When creating an ADR from a spike:

1. **Map sections:**
   - Spike "Background" → ADR "Context"
   - Spike "Recommendations" → ADR "Decision"
   - Spike "Options Considered" → ADR "Alternatives Considered"
   - Spike "Trade-offs" → ADR "Consequences"

2. **Transform tone:**
   - Spike: "We could..." → ADR: "We will..."
   - Spike: "Options are..." → ADR: "We chose X because..."
   - Spike: Exploratory → ADR: Decisive

3. **Add missing sections:**
   - Implementation strategy (from spike's "Next Steps")
   - Validation plan (tests, metrics, gates)
   - Review notes (capture feedback during review)

4. **Update metadata:**
   - Set status to "Proposed"
   - Assign next ADR number
   - Add category (feature/refactor/migrate/bug)
   - Reference source spike

## ADR Maintenance

### When to Update
- **NEVER** edit Context, Decision, or Alternatives (immutable record)
- **CAN** add review notes
- **CAN** update status
- **CAN** add "Superseded by" when replaced
- **CAN** add implementation notes

### When to Deprecate
- Decision no longer recommended
- Better approach discovered
- Requirements changed making decision obsolete

### When to Supersede
- Create new ADR with improved approach
- Link new ADR in "Superseded by" field
- Keep old ADR for historical context
