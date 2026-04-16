# ADR Template

This template follows the MADR (Markdown Architectural Decision Records) format.

## File Naming

`NNNN-title-in-kebab-case.md`

Where NNNN is a sequential number (0001, 0002, etc.)

## Template

```markdown
# ADR-NNNN: [Title]

## Status

[Proposed | Accepted | Deprecated | Superseded by ADR-XXXX]

## Date

YYYY-MM-DD

## Deciders

- [Name/Role]
- [Name/Role]

## Context

[Describe the problem, forces, and constraints that led to this decision.
What is the situation? What are the requirements? What are the constraints?]

## Decision

[State the decision clearly and concisely.
"We will..." or "The system will..."]

## Consequences

### Positive

- [Benefit 1]
- [Benefit 2]

### Negative

- [Drawback 1]
- [Drawback 2]

### Neutral

- [Observation that is neither positive nor negative]

## Alternatives Considered

### Alternative 1: [Name]

**Description**: [Brief description]

**Pros**:
- [Pro 1]
- [Pro 2]

**Cons**:
- [Con 1]
- [Con 2]

**Why rejected**: [Reason for not choosing this option]

### Alternative 2: [Name]

**Description**: [Brief description]

**Pros**:
- [Pro 1]

**Cons**:
- [Con 1]

**Why rejected**: [Reason for not choosing this option]

## Related Decisions

- ADR-XXXX: [Related decision and why it's related]
- ADR-YYYY: [Another related decision]

## References

- [Link to relevant documentation]
- [Link to research or analysis]
- [Link to standards or specifications]
```

## Quick Reference

### Status Values

| Status | When to Use |
| --- | --- |
| Proposed | Under discussion, not yet approved |
| Accepted | Approved and being implemented |
| Deprecated | No longer relevant, kept for history |
| Superseded | Replaced by a newer ADR |

### Best Practices

1. **One decision per ADR** - Keep focused
2. **Never delete ADRs** - Only supersede
3. **Be honest about trade-offs** - Document negatives
4. **Include context** - Future readers need background
5. **Link related decisions** - Build a decision graph
