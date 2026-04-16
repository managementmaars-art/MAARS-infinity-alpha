---
name: write-a-spec
description: Create a feature spec or refactor RFC through user interview, codebase exploration, and module design, then publish it as a GitHub issue or local Markdown file. Use when the user wants to write a PRD, RFC, refactor plan, product requirements document, change proposal, or plan a large feature or refactor.
---

# Write a Spec

Create a durable planning document for a significant change. This skill covers both:

- feature specs / PRDs
- refactor RFCs / change plans

## 1. Pick the mode

Decide which mode fits the request:

- **Feature spec** when the user is planning new product behavior, a major feature, or a product requirement
- **Refactor RFC** when the user is restructuring an existing system, improving architecture, or breaking a refactor into safe incremental steps

If the request is ambiguous, ask one short question to resolve the mode.

## 2. Gather the problem space

Start with a detailed description from the user, then explore the repo to verify assumptions and understand the current state.

You are trying to understand:

- the real problem
- the affected users or developers
- current constraints
- existing interfaces and modules
- what is already working

## 3. Interview until the scope is clear

Work through open questions one at a time.

For **feature specs**, clarify:

- desired user outcomes
- key user stories
- boundaries of the feature
- major product and technical constraints

For **refactor RFCs**, clarify:

- what pain is being removed
- alternative options that were considered
- exact scope vs out-of-scope
- what a safe migration path looks like

## 4. Explore module boundaries and tests

Look for the major modules you would build or modify.

Actively prefer **deep modules**:

- small interfaces
- large implementation hidden behind them
- testable at the boundary

Check existing test coverage in the affected area and note what good new tests would verify.

## 5. Write the document

If GitHub is available, publish the result as an issue. Otherwise, write it to `./plans/`.

Use:

- `./plans/<slug>-spec.md` for feature specs
- `./plans/refactor-<slug>.md` for refactor RFCs

### Feature spec template

```md
## Problem Statement

[The problem from the user's perspective]

## Solution

[The proposed solution from the user's perspective]

## User Stories

1. As a <actor>, I want <feature>, so that <benefit>

## Implementation Decisions

- modules to build or modify
- interface changes
- architectural decisions
- schema or API contracts

## Testing Decisions

- what good tests verify
- which modules need tests
- prior art in the codebase

## Out of Scope

[Not included in this spec]

## Further Notes

[Anything else worth recording]
```

### Refactor RFC template

```md
## Problem Statement

[The developer-facing problem]

## Solution

[The proposed refactor approach]

## Commits

1. [Tiny commit that leaves the system working]
2. [Next tiny commit]

## Decision Document

- modules to build or modify
- interface changes
- architectural decisions
- migration or rollout constraints

## Testing Decisions

- what good tests verify
- what existing coverage exists
- what new boundary tests are needed

## Out of Scope

[Not included in this refactor]

## Further Notes

[Optional]
```

## Gotchas

- Do not include file paths or code snippets in the durable document.
- The value is in clarifying scope and decisions, not producing a long wall of text.
- Refactor plans should break work into tiny commits that keep the codebase working.
- Feature specs should be extensive on user stories, not just implementation notes.
