---
name: vibe-coding-standard-workflow
description: Standardized AI-assisted product delivery workflow for turning a new idea or messy repository into a disciplined build loop with `design-document.md`, `tech-stack.md`, `implementation-plan.md`, and a persistent `memory-bank/`. Use in Codex or Claude Code when bootstrapping greenfield work, normalizing a repository into a document-first process, or executing implementation one validated step at a time with `progress.md` and `architecture.md` kept current.
---

# Vibe Coding Standard Workflow

Turn a rough idea into a controlled delivery loop. Use this skill to force document-first planning, explicit clarification, small testable implementation steps, and durable project memory for later handoffs.

## Target Artifacts

Create and maintain these files:

- `PRD.md` as the temporary idea capture file
- `memory-bank/design-document.md`
- `memory-bank/tech-stack.md`
- `memory-bank/implementation-plan.md`
- `memory-bank/progress.md`
- `memory-bank/architecture.md`
- `AGENTS.md` and/or `CLAUDE.md`, depending on the agent environment

Treat `memory-bank/` as the long-lived source of truth after the bootstrap phase.

## Bootstrap Workflow

### 1. Normalize the initial idea

Start by producing a short `PRD.md` that captures:

- product name
- target user
- user problem
- primary user flows
- major features
- key constraints or assumptions

Keep it lightweight. The purpose is to create enough structure for deeper questioning, not to finish the specification.

### 2. Convert the PRD into a real design document

Read `PRD.md`, then ask targeted clarification questions before writing `design-document.md`. Do not jump directly into the design document if the PRD is still ambiguous.

The resulting design document should make implementation decisions possible. Cover at least:

- scope and non-goals
- user journeys
- feature behavior
- edge cases
- data or state model
- acceptance criteria

If the user answers questions incrementally, keep refining the document until the design is executable.

### 3. Recommend the technology stack

Derive `tech-stack.md` from `design-document.md`, not from guesses. Optimize for simple and robust over trendy and broad.

For each major layer, choose the minimum viable stack:

- application framework
- backend/runtime
- storage
- auth
- deployment
- testing

Keep rationale short but explicit.

### 4. Bootstrap project memory and agent instructions

After the design and stack are stable:

- remove the now-superseded `PRD.md` if the workflow or user instruction allows it
- run the repository init flow if the environment supports it
- ensure `AGENTS.md` and/or `CLAUDE.md` include the required memory-bank rules
- create `memory-bank/`
- move `design-document.md`, `tech-stack.md`, and `implementation-plan.md` into `memory-bank/`
- create empty `memory-bank/progress.md` and `memory-bank/architecture.md`
- fix paths in docs after files are moved

If only one of `AGENTS.md` or `CLAUDE.md` exists, update that file. If both exist, keep them aligned.

Append this block:

```md
## 重要提示

- 写任何代码前必须完整阅读 memory-bank/@architecture.md
- 写任何代码前必须完整阅读 memory-bank/@design-document.md
- 每完成一个重大功能或里程碑后，必须更新 memory-bank/@architecture.md
```

### 5. Produce the implementation plan

Generate `implementation-plan.md` from `design-document.md` and `tech-stack.md`.

Every step in the plan must be:

- small
- concrete
- ordered
- code-free
- independently verifiable

Each step must include its own validation instruction or test expectation. Do not allow vague steps like "build the backend" or "finish the frontend."

### 6. Refine the plan until it is executable

Read the full `memory-bank/` and ask whatever questions are still necessary to make the plan unambiguous. Continue until the implementation plan is clear enough that another agent could execute it without re-discovering product intent.

Update the documents after every clarification round.

## Execution Loop

### 7. Execute exactly one plan step at a time

Before writing code, read:

- `memory-bank/architecture.md`
- `memory-bank/design-document.md`
- `memory-bank/implementation-plan.md`
- `memory-bank/progress.md`

Then execute only the current plan step.

Assume the user is the test gate unless they explicitly delegate test execution. Do not start the next step until the current one is verified.

After the user confirms the step:

- append a concise record to `memory-bank/progress.md`
- update `memory-bank/architecture.md` with new or changed files and why they exist

### 8. Repeat with a fresh context load

For every later step, reload the `memory-bank/` files and the latest `progress.md` before continuing. If context quality has degraded, explicitly clear and rebuild context instead of relying on memory.

## Non-Negotiable Rules

- Ask clarification questions when requirements are underspecified.
- Keep `implementation-plan.md` free of code.
- Do not begin step `N+1` before step `N` is validated.
- Keep `progress.md` as the execution log, not as a design document.
- Keep `architecture.md` as a current map of important files and responsibilities.
- Prefer checkpoint commits after bootstrap or major milestones when git is available and the user wants a restore point.
- Preserve the file names in this workflow unless the user explicitly wants a different convention.

## Agent-Specific Notes

- Read [references/codex.md](references/codex.md) for Codex-specific behavior and packaging notes.
- Read [references/claude-code.md](references/claude-code.md) for Claude Code-specific behavior and marketplace notes.
- Read [references/prompts.md](references/prompts.md) when you want ready-to-send prompt templates for each stage of the workflow.
