---
name: product-designer
description: Design entire feature flows end-to-end with user needs, user stories, and ASCII prototypes. Explores codebase to understand existing patterns, reuses existing components and modals, asks alignment questions, then designs world-class Linear/Stripe/Vercel-quality UI/UX. Writes final PRD into .todo/[feat-name]/PRD.md. Use when designing a new feature, flow, or screen — especially before implementation.
---

# Product Designer Skill

## What This Skill Does

Build it end to end plus billing logic, plus UI/UX design and billing recurring billing logic via pgboss.

Use ASCII to draw the design of the UI.
Ensure world-class Linear/Stripe UI UX. Reuse existing components and design layouts — ensure simple, clear, exactly copying existing deploy claw agent and deploy production hosting modals wherever applicable. Make the whole experience smooth. Consider all user needs and user stories for the whole flow. Start by listing the user needs and all the screens and flows supporting them, then design in ASCII. Iterate until it is world-class Linear/Stripe/Vercel style UI/UX and on-brand fitting existing framework and navigation logic. Then present to the user.

First explore codebase to understand all relevant files and existing logic flow. Frontend + backend + infra, everything.
Then, ask the user any important questions using the `askUserQuestions` tool to align design decisions.

Finally, based on the feature name (kebab case) write into existing or new `.todo/[feat-name]/PRD.md` file.

---

## Workflow

### Phase 1: Codebase Exploration

Explore frontend + backend + infra simultaneously using parallel subagents:

- Find existing modals, flows, and components most similar to the feature
- Identify existing billing, pgboss job patterns, and API structure
- Note the navigation patterns, layout components, design system tokens in use
- Find any existing related logic to reuse

Key places to check:
- `src/components/` — existing modals, dialogs, UI primitives
- `src/app/api/` — existing API routes and patterns
- `src/lib/` — billing, jobs, business logic utilities
- `blink-apis/` — backend service patterns
- `.todo/` — any existing PRD or todo context

### Phase 2: List User Needs & Stories

Before any design, enumerate:

```
USER NEEDS:
1. [Primary need — the "why" behind this feature]
2. [Secondary need — what else supports their goal]
3. ...

USER STORIES:
- As a [persona], I want to [action] so that [outcome]
- As a [persona], I want to [action] so that [outcome]
- ...

SCREENS & FLOWS:
1. [Screen name] — [what it does, which user story it serves]
2. [Screen name] — [what it does, which user story it serves]
3. ...
```

### Phase 3: Ask Alignment Questions

Use the `askUserQuestions` tool to clarify critical design decisions before designing. Focus on:
- Scope (what's in/out for v1)
- Billing model specifics (if applicable)
- Target personas or edge cases
- Any existing UX patterns to strictly follow or avoid
- Priority of screens if time-boxed

### Phase 4: ASCII Prototype

Design every screen and state in ASCII. Iterate until world-class quality.

**Design standards:**
- Match Linear/Stripe/Vercel aesthetics: clean, minimal, high information density
- Reuse existing modal shells, button styles, and layout primitives exactly
- Show all states: empty, loading, error, success, edge cases
- Include hover/focus/active indicators where meaningful

**ASCII format conventions:**
```
┌─────────────────────────────────────────┐
│ Modal Title                         [X] │
├─────────────────────────────────────────┤
│                                         │
│  Section header                         │
│  ┌───────────────────────────────────┐  │
│  │ Input field               [icon]  │  │
│  └───────────────────────────────────┘  │
│                                         │
│  [Secondary action]     [Primary CTA →] │
└─────────────────────────────────────────┘
```

Design the full flow as connected screens:

```
[Screen A] ──→ [Screen B] ──→ [Screen C: Success]
                    │
                    └──→ [Screen B2: Error state]
```

### Phase 5: Write PRD

Write the finalized design into `.todo/[feat-name]/PRD.md`:

```markdown
# [Feature Name] PRD

## Overview
[1-2 sentence summary]

## User Needs
[List from Phase 2]

## User Stories
[List from Phase 2]

## Screens & Flows
[List with descriptions]

## ASCII Designs
[All ASCII prototypes from Phase 4]

## Component Reuse
[Which existing components/modals/patterns to reuse]

## API & Backend
[Required endpoints, pgboss jobs, billing logic]

## Open Questions
[Unresolved decisions or edge cases]
```

---

## Quality Bar

Before presenting, self-check:
- [ ] All user stories have a corresponding screen/flow
- [ ] Empty, loading, and error states are designed
- [ ] Existing components are explicitly reused (not reimagined)
- [ ] Billing/recurring logic is fully mapped if applicable
- [ ] ASCII designs look clean at fixed-width font rendering
- [ ] PRD is written and saved to `.todo/[feat-name]/PRD.md`
