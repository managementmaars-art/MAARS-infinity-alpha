Write the plan using this structure exactly. The `## Problem Framing` section and its six subsections feed into Phase 3 Socratic questioning. The per-task subsections must be complete enough for zero-context execution. If the plan has no content for a section, keep the heading and write a note explaining why.

```markdown
# <TICKET_KEY> — Detailed Task Plan

> Source: docs/<TICKET_KEY>.md
> Generated on: <YYYY-MM-DD HH:MM UTC>

## Ticket Summary

<3–5 sentence summary of the ticket goal, scope, and key constraints.>

## Problem Framing

### End User

<Who the end user is, based on ticket analysis. If the ticket does not state
this, write: "Not stated in ticket — requires developer input.">

### Underlying Need

<The user problem or need this ticket addresses, described in user terms. If
the ticket only describes a solution without articulating the need, state what
you can infer and flag what is assumed.>

### Proposed Solution

<The solution the ticket prescribes — what the ticket says to build.>

### Solution-Problem Fit

<Assessment of how directly the proposed solution addresses the underlying need.
Gaps, assumptions about user behaviour, edge cases the solution might miss.>

### Alternative Approaches Not Explored

<Other ways the underlying need could be met. "None identified" is acceptable
for well-scoped bug fixes or tightly constrained work.>

### Evidence Basis

<What evidence the ticket cites for why this solution is correct — user research,
analytics data, stakeholder request, technical constraint. If the ticket provides
no evidence, write: "Not stated in ticket — requires developer input.">

## Assumptions and Constraints

<Numbered list of every assumption made while planning. Include both explicit
constraints from the ticket and implicit assumptions you've inferred.>

1. …
2. …

## Cross-Cutting Open Questions

<Questions that affect multiple tasks or the overall approach.>

1. **<Question>** — <Why it matters>
2. …

## Tasks

### Task A: <Short descriptive title>

**Objective:**
<One to two sentences on what this task accomplishes.>

**Relevant requirements and context:**
<Bullet list of ONLY the requirements, constraints, and background needed for
THIS task. Reference assumption numbers or ticket sections.>

- Traces to: <Which part of the ticket description, acceptance criteria, or
  comment this task addresses. Be specific — quote or reference section names.>

**Questions to answer before starting:**
<Uncertainties or team questions. For each, include why it matters and what the
fallback is if unanswered. If none, write `None`.>

**Implementation notes:**
<Expected approach, boundaries, and technical considerations. Be specific about
files, modules, APIs, or patterns where possible. If the codebase is unknown,
describe what to look for.>

**Definition of done:**
<Concrete, verifiable conditions as checkboxes.>

- [ ] …
- [ ] …

**Likely files / artifacts affected:**
<List files, modules, or systems. If unknown, write `Unknown — requires
codebase exploration`.>

### Task B: …

## Notes

<Observations about the plan: tasks that might be combinable, areas of
ambiguity, things the ticket doesn't specify but that will need to be done.>
```

Downstream skills parse these headings programmatically — changing or omitting headings breaks the pipeline.
