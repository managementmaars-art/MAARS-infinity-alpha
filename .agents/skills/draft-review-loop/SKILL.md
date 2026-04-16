---
name: draft-review-loop
description: >
  Run the local-first authoring plus Draft review handoff loop for workspace markdown files.
  Use this skill when the user asks to write or revise a document and explicitly wants human review in Draft,
  or when the task is to apply Draft comments back to a local file.
  DO NOT use this skill for pure Draft command questions (use draft-cli) or generic writing tasks with no Draft review intent.
  Keep local workspace markdown as source of truth and use Draft GUI as the human review surface.
compatibility: >
  Requires the draft-cli skill and @innosage/draft-cli (Node.js >= 18).
metadata:
  author: innosage-llc
  version: "1.0"
---

# Draft Review Loop Skill

Use this skill to run a human-agent review loop where authorship stays in local markdown and Draft is the review surface.

## Trigger Guidance

Trigger this skill when the user intent matches collaboration workflow requests such as:

- "Write a doc and let me review it in Draft."
- "Prepare a proposal for review in Draft."
- "Revise this workspace file based on Draft comments."
- "Use Draft as the review surface while keeping the repo file as source of truth."

Do not trigger this skill when:

- the user only asks how to run Draft commands (`draft status`, `draft page ls`, `draft page patch`, etc.)
- the user uses "draft" only as a verb for generic writing (for example, "draft an email")
- the user requests direct Draft-page mutation as the primary authoring surface

## Boundaries

- Source of truth: local workspace markdown file.
- Review surface: Draft GUI page opened from that file.
- Transport and command handling: `draft-cli` skill.
- This skill defines workflow behavior, not low-level CLI troubleshooting.

## Required Workflow

Follow this sequence unless the user explicitly asks for a different flow.

1. Create or update the local markdown file first.
2. Ensure Draft connection through `draft-cli` connection-first pattern (`draft status --json` and recovery if needed).
3. Open the local file in Draft review surface:

```bash
draft open <path> --json
```

4. Explicitly hand off to human review in Draft.
5. Read review artifacts from Draft comments:

```bash
draft workspace comments <path> --json
```

6. Apply accepted feedback back to the local markdown file with normal file-editing tools.

## Human Handoff Language

Use direct handoff language after `draft open <path> --json`, for example:

- "I updated `<path>` locally and opened it in Draft for your review."
- "Please leave comments in Draft; I will apply accepted feedback back to the local file."

## Reusable Handoff Templates

Copy and adapt these phrases when handing off review:

- "I wrote `<path>` locally (source of truth) and opened it in Draft for your review."
- "Please review in Draft and leave comments there; I will update the local markdown file from accepted feedback."
- "I read the Draft comments for `<path>` and applied the accepted changes to the workspace file."

## Example Patterns

Use these compact patterns to keep trigger intent and workflow behavior aligned.

### Proposal Review (Trigger: yes)

Prompt shape:
- "Prepare a proposal in my repo and let me review it in Draft."

Execution pattern:

```bash
# 1) Write local source artifact first
$EDITOR docs/proposals/q2-partner-plan.md

# 2) Ensure Draft connection
draft status --json

# 3) Open local file in Draft as review surface
draft open docs/proposals/q2-partner-plan.md --json
```

Handoff phrase:
- "I wrote `docs/proposals/q2-partner-plan.md` locally and opened it in Draft for your review."

### Spec Review (Trigger: yes)

Prompt shape:
- "Revise docs/spec.md and use Draft for my review comments."

Execution pattern:

```bash
draft status --json
draft open docs/spec.md --json
draft workspace comments docs/spec.md --json
```

Handoff phrase:
- "Please comment in Draft on `docs/spec.md`; I will apply accepted feedback to the local file."

### Release Notes Review (Trigger: yes)

Prompt shape:
- "Prepare release notes locally and ask me to review them in Draft."

Execution pattern:

```bash
$EDITOR docs/releases/2026-04-12.md
draft status --json
draft open docs/releases/2026-04-12.md --json
```

Handoff phrase:
- "Release notes are authored locally in `docs/releases/2026-04-12.md` and ready for your Draft review."

### Non-Trigger Contrast (Trigger: no)

Prompt shape:
- "How do I run `draft status --json`?" -> `draft-review-loop` should decline; use `draft-cli`.
- "Please draft an email update." -> decline; generic writing intent.

## Full Loop Example (Draft To Comment Resolution)

1. Agent writes `docs/spec.md` locally.
2. Agent runs `draft status --json`.
3. Agent runs `draft open docs/spec.md --json`.
4. Agent handoff: "I wrote `docs/spec.md` locally and opened it in Draft for your review."
5. Human leaves Draft comments.
6. Agent runs `draft workspace comments docs/spec.md --json`.
7. Agent applies accepted changes to `docs/spec.md` with normal file-edit tools.
8. Agent reports resolution: "I applied accepted Draft feedback to `docs/spec.md`; local markdown remains the source of truth."

## Revision Application Rule

When comments arrive, edit the local file by default. Do not default to mutating Draft page content directly unless the user explicitly requests page-first mutation.

## Non-Goals

- Do not imply fully headless live collaboration.
- Do not move source of truth from workspace markdown to Draft pages.
