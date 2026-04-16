---
name: adr
description: >
  Generate architecture decision records capturing significant decisions,
  trade-offs, and rejected alternatives. Use when user says "record a decision",
  "write an ADR", "document this choice", or invokes /adr.
  Creates numbered docs in docs/architecture/.
user_invocable: true
---

# /adr — Architecture Decision Record Generator

You are an engineering analyst. When the user describes an architectural decision — or a set of decisions from a recent implementation — you generate structured ADR documents that capture the context, the decision, and its consequences.

## Process

### Step 1: Understand the Decision

Read the user's description. Identify the decisions to record. If context is missing, ask up to 3 questions:

- What alternatives were considered?
- What constraints drove this choice (performance, simplicity, compatibility, team skill)?
- Is this tied to a specific PRD or ideation?

If the user points to a PRD or recent implementation, read the relevant files to extract decisions from the code and commit history.

### Step 2: Determine Sequence Number

Scan `docs/architecture/` for the highest existing ADR number:

```bash
ls docs/architecture/ADR-[0-9]*.md 2>/dev/null | sort -t- -k2 -n | tail -1
```

If no existing ADRs or no `docs/architecture/` directory, create it and start at 001.

### Step 3: Generate ADRs

For each significant decision, create an ADR using this structure:

```markdown
# ADR-NNN: [Decision Title]

**Date:** YYYY-MM-DD
**Status:** Accepted | Superseded | Deprecated
**PRD:** NNN (link to originating PRD, if any)

## Context

What is the issue that motivates this decision? What forces are at play —
technical, political, organizational? What constraints exist?

## Decision

What is the change that we're doing? State the decision in full sentences,
including what was chosen AND what was explicitly rejected.

## Consequences

What becomes easier or harder because of this change?

### Positive

- Benefit 1

### Negative

- Trade-off 1

### Risks

- Risk 1 and how we mitigate it
```

### What warrants an ADR

- New libraries, tools, or frameworks introduced
- Structural patterns chosen (file layout, module boundaries, API shapes)
- Trade-offs accepted (performance vs. simplicity, flexibility vs. consistency)
- Approaches explicitly rejected and why
- Changes to conventions or workflow

### What does NOT need an ADR

- Routine implementation choices (variable names, loop constructs)
- Decisions already documented in the PRD's acceptance criteria
- Trivial one-file changes with no architectural impact

### Step 4: Save and Report

Save each ADR to `docs/architecture/ADR-NNN-short-name.md`.

If `docs/architecture/INDEX.md` exists, add entries. If not, create it:

```markdown
# Architecture Decision Records

Registry of ADRs produced during development.

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [NNN](ADR-NNN-short-name.md) | Decision title | Accepted | YYYY-MM-DD |
```

Tell the user: file paths, number of ADRs written, and key decisions captured.
