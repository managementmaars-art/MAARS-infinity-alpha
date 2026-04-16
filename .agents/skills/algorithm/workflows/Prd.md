# PRD Template

Create a new PRD file using this template. Replace all `{placeholders}` with actual values.

## Location

- **In a git project:** `.prd/PRD-{YYYYMMDD}-{slug}.md`
- **No git project:** `~/.claude/MEMORY/WORK/{session-slug}/PRD-{YYYYMMDD}-{slug}.md`
- **Child PRDs:** `PRD-{date}-{parent-slug}--{child-slug}.md`

## Slug Rules

Task description lowercased, special chars stripped, spaces to hyphens, max 40 chars.

## Template

```markdown
---
prd: true
id: PRD-{YYYYMMDD}-{slug}
status: DRAFT
mode: interactive
effort_level: Standard
created: {YYYY-MM-DD}
updated: {YYYY-MM-DD}
iteration: 0
maxIterations: 128
loopStatus: null
last_phase: null
failing_criteria: []
verification_summary: "0/0"
parent: null
children: []
---

# {Task Title}

> {One sentence: what this achieves and why it matters.}

## STATUS

| What | State |
|------|-------|
| Progress | 0/{N} criteria passing |
| Phase | {current Algorithm phase} |
| Next action | {what happens next} |
| Blocked by | {nothing, or specific blockers} |

## CONTEXT

### Problem Space
{What problem is being solved and why it matters. 2-3 sentences max.}

### Key Files
{Files that a fresh agent must read to resume. Paths + 1-line role description each.}

### Constraints
{Hard constraints: backwards compatibility, performance budgets, API contracts, dependencies.}

### Decisions Made
{Technical decisions from previous iterations that must be preserved.}

## PLAN

{Execution approach, technical decisions, task breakdown.
Written during PLAN phase. MANDATORY — no PRD is valid without a plan.
For Extended+ effort level: written in plan mode for structured codebase exploration.}

## IDEAL STATE CRITERIA (Verification Criteria)

{Criteria format: ISC-{Domain}-{N} for grouped (17+), ISC-C{N} for flat (<=16)}
{Each criterion: 8-12 words, state not action, binary testable}
{Each carries inline verification method via | Verify: suffix}
{Anti-criteria prefixed ISC-A-}

### {Domain} (for grouped PRDs, 17+ criteria)

- [ ] ISC-C1: {8-12 word state criterion} | Verify: {CLI|Test|Static|Browser|Grep|Read|Custom}: {method}
- [ ] ISC-C2: {8-12 word state criterion} | Verify: {type}: {method}
- [ ] ISC-A1: {8-12 word anti-criterion} | Verify: {type}: {method}

## DECISIONS

{Non-obvious technical decisions made during BUILD/EXECUTE.
Each entry: date, decision, rationale, alternatives considered.}

## LOG

### Iteration {N} — {YYYY-MM-DD}
- Phase reached: {OBSERVE|THINK|PLAN|BUILD|EXECUTE|VERIFY|LEARN}
- Criteria progress: {passing}/{total}
- Work done: {summary}
- Failing: {list of still-failing criteria IDs}
- Context for next iteration: {what the next agent needs to know}
```

## Status Progression

```
DRAFT → CRITERIA_DEFINED → PLANNED → IN_PROGRESS → VERIFYING → COMPLETE
                                                                → FAILED
                                                                → BLOCKED
```

## ISC Scale Tiers

| Tier | ISC Count | Structure | When |
|------|-----------|-----------|------|
| Simple | 4-16 | Flat list | Single-file fix, skill invocation |
| Medium | 17-32 | Grouped by domain | Multi-file feature, API endpoint |
| Large | 33-99 | Grouped + child PRDs | Multi-system feature, major refactor |
| Massive | 100-500+ | Multi-level hierarchy | Platform redesign, full product build |
