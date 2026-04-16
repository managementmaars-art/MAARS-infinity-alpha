---
name: adr-create
description: "Create Architecture Decision Record from specification context."
argument-hint: "<spec file> [--decision <decision summary>]"
allowed-tools: Read, Glob, Grep, Write, Edit, Skill, Task
---

# Create Architecture Decision Record

Create an ADR (Architecture Decision Record) from specification context.

## When to Create ADRs

Create an ADR when a specification contains:

- Technology choices (database, framework, library)
- Architectural patterns (microservices, CQRS, event sourcing)
- Integration approaches (sync vs async, REST vs GraphQL)
- Security decisions (auth method, encryption)
- Significant trade-offs (performance vs simplicity)
- Deviations from existing patterns

## MADR Format

Uses Markdown Any Decision Records (MADR) format:

```markdown
# ADR-NNN: [Title in Imperative Form]

## Status
[Proposed | Accepted | Deprecated | Superseded by ADR-XXX]

## Context
[Forces at play, situation motivating this decision]

## Decision
We will [decision in imperative form].

## Consequences
### Positive
- [Benefits]

### Negative
- [Drawbacks]

### Neutral
- [Trade-offs]

## Alternatives Considered
### [Alternative 1]
**Pros:** [advantages]
**Cons:** [disadvantages]
**Why Rejected:** [reason]
```

## Workflow

1. **Load Specification**
   - Read the specification file
   - Identify decision points

2. **Extract Decisions**
   - Spawn `adr-creator` agent
   - Find explicit decisions ("We will use X")
   - Find implicit decisions (tech mentioned)
   - Gather context and constraints

3. **Research Alternatives**
   - If alternatives not documented:
     - Identify reasonable alternatives
     - Research pros and cons
     - Document rejection reasons

4. **Generate ADR**
   - Apply MADR format
   - Link to specification
   - Cross-reference requirements

5. **Save ADR**
   - Assign ADR number
   - Save to `docs/adr/` (or user-specified location)
   - Update ADR index

## Arguments

- `$1` - Specification file path
- `--decision` - Specific decision to document
- `--output` - Output directory (default: `docs/adr/`)
- `--number` - ADR number (auto-assigned if not provided)

## Examples

```bash
# Extract ADRs from specification
/spec-driven-development:adr-create .specs/auth/spec.md

# Create specific decision ADR
/spec-driven-development:adr-create .specs/auth/spec.md --decision "Use JWT for session tokens"

# Specify output location
/spec-driven-development:adr-create .specs/auth/spec.md --output docs/adr/

# Assign specific number
/spec-driven-development:adr-create .specs/auth/spec.md --number 42
```

## ADR Example

```markdown
# ADR-015: Use Redis for Session Caching

<!--
Generated from: SPEC-AUTH-001
Requirements: NFR-1 (Performance), FR-3 (Session Management)
Created: 2024-01-15
-->

## Status

Proposed

## Context

The authentication specification (SPEC-AUTH-001) requires session tokens
to be validated within 50ms (NFR-1). Current database-only approach
shows p95 latency of 150ms, exceeding the requirement.

We need a caching strategy to reduce session validation latency.

## Decision

We will use Redis as an in-memory cache for session tokens.

- Cache session data with TTL matching session expiry
- Use cache-aside pattern (lazy loading)
- Invalidate on logout and password change

## Consequences

### Positive

- Expected 80% reduction in session validation latency
- Reduced database load for session queries
- Industry-standard solution with extensive documentation
- Team has Redis experience

### Negative

- Additional infrastructure component
- Cache invalidation complexity
- Memory costs scale with active sessions

### Neutral

- Requires Redis cluster for high availability
- Monitoring and alerting setup needed

## Alternatives Considered

### In-Memory Application Cache

Local cache in each application instance.

**Pros:** No additional infrastructure
**Cons:** Not shared across instances, lost on restart
**Why Rejected:** Multi-instance deployment requires shared cache

### Database Materialized Views

Pre-computed session data in database.

**Pros:** No new technology
**Cons:** Still has database latency, complex refresh logic
**Why Rejected:** Doesn't meet 50ms latency requirement

## Related

- **Specification:** SPEC-AUTH-001
- **Requirements:** NFR-1, FR-3
- **Related ADRs:** ADR-012 (Redis Infrastructure)
```

## ADR Index Update

When creating an ADR, the index is updated:

```markdown
## ADR Index

| ADR | Title | Status | Spec | Date |
| --- | --- | --- | --- | --- |
| ADR-014 | Use PostgreSQL | Accepted | SPEC-001 | 2024-01-10 |
| ADR-015 | Use Redis for Sessions | Proposed | SPEC-AUTH | 2024-01-15 |
```

## Related Commands

- `/spec-driven-development:specify` - Generate specification
- `/spec-driven-development:plan` - Generate design
- `/spec-driven-development:validate` - Validate specification
