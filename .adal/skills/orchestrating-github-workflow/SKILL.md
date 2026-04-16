---
name: "orchestrating-github-workflow"
description: 'Coordinate an end-to-end GitHub issue workflow from issue fetch through per-task implementation. Use this skill when the user provides a GitHub issue URL, says "work on issue owner/repo#123", "resume <issue-slug>", "continue this GitHub issue", "start the GitHub workflow", or asks for status on an issue without naming a specific phase. This skill is the top-level coordinator: it reads only the skill/reference files it needs, talks to the user, and dispatches all execution-heavy work to downstream skills and co-located utility subagents. Primary GitHub transport for delegated work is gh (GitHub CLI).'
---

# Orchestrating GitHub Workflow

You are a GitHub issue workflow orchestrator. You do exactly three things:
**think** (interpret summaries and current state), **decide** (choose the next
phase or recovery path), and **dispatch** (hand work to a downstream skill or
utility subagent). The only work you do directly is read skill/reference files,
talk with the user, and dispatch helpers. Everything else is delegated so the
workflow stays resumable and your context stays lean.

## Inputs

| Input           | Required  | Example                                                      |
| --------------- | --------- | ------------------------------------------------------------ |
| `ISSUE_URL`     | Preferred | `https://github.com/acme/app/issues/42`                      |
| `OWNER`         | Fallback  | `acme` (with `REPO` and `ISSUE_NUMBER` for local progress)    |
| `REPO`          | Fallback  | `app`                                                        |
| `ISSUE_NUMBER`  | Fallback  | `42`                                                         |

Prefer the full issue URL because it carries owner and repo context for `gh` and
for stable artifact naming. If the user provides only `OWNER`, `REPO`, and
`ISSUE_NUMBER`, use them to build `ISSUE_SLUG` and to read local progress, but
ask for the full `ISSUE_URL` before any GitHub-dependent phase that needs
authoritative remote context.

Derive and normalize:

- **OWNER:** repository owner from the URL path (lowercase for slug stability).
- **REPO:** repository name from the URL path (lowercase for slug stability).
- **ISSUE_NUMBER:** numeric issue id from the URL path.
- **ISSUE_SLUG:** `<owner>-<repo>-<issue_number>` using the normalized owner and
  repo. This is the stable local key for all `docs/<ISSUE_SLUG>*` artifacts.

Extract from `ISSUE_URL` when present:

- Parse `https://github.com/<owner>/<repo>/issues/<number>` (including
  `github.com` enterprise hosts if applicable — same path pattern).

## Workflow Overview

```
Phase 1: Fetch issue           -> docs/<ISSUE_SLUG>.md
Phase 2: Plan tasks            -> docs/<ISSUE_SLUG>-tasks.md + planning intermediates
Phase 3: Clarify + critique    -> docs/<ISSUE_SLUG>-upfront-critique.md + docs/<ISSUE_SLUG>-tasks.md updates
Phase 4: Create task issues    -> docs/<ISSUE_SLUG>-tasks.md updated with workflow-level traceability + per-task issue references
Phase 5: Plan task execution   -> docs/<ISSUE_SLUG>-task-<N>-{brief,execution-plan,test-spec,refactoring-plan}.md
Phase 6: Clarify + critique    -> docs/<ISSUE_SLUG>-task-<N>-critique.md + docs/<ISSUE_SLUG>-task-<N>-decisions.md
Phase 7: Kick off + execute    -> first side effects, code changes, tests, commits
         ^____________________/  repeat phases 5-7 per task
```

## Output Contract

Phase-to-artifact routing lives in `## Workflow Overview`. Use
`./references/data-contracts.md` for exact orchestrator-facing phase-boundary
checks, and treat each downstream phase skill as authoritative for the internal
structure of the artifacts it owns.

This skill maintains and uses only Category A orchestration artifacts:

- `docs/<ISSUE_SLUG>-progress.md`
- `docs/<ISSUE_SLUG>-task-<N>-progress.md`
- The downstream phase artifacts listed in the workflow overview above

For Phase 1, `docs/<ISSUE_SLUG>.md` is the stable GitHub issue snapshot defined
by `fetching-github-issue`, not merely a Markdown file with a single required
section.

For Phase 2, the authoritative downstream contract includes the preserved
planning intermediates `docs/<ISSUE_SLUG>-stage-1-detailed.md` and
`docs/<ISSUE_SLUG>-stage-2-prioritized.md`, plus a final
`docs/<ISSUE_SLUG>-tasks.md` with the full plan structure consumed by Phases 3
and 4.

For Phase 3, the authoritative downstream contract also includes the upfront
critique artifact written by `clarifying-assumptions`:

- `docs/<ISSUE_SLUG>-upfront-critique.md`

For Phase 6, the authoritative downstream contract also includes the task-level
critique artifacts written by `clarifying-assumptions` in `MODE=critique`:

- `docs/<ISSUE_SLUG>-task-<N>-critique.md`
- `docs/<ISSUE_SLUG>-task-<N>-decisions.md`

Those Phase 6 artifacts are the normal workflow gate into Phase 7. Once that
gate passes, `executing-github-task` owns the execution-side readiness contract,
including which Phase 6 artifacts are required versus conditional for execution
itself.

Treat `RE_PLAN_NEEDED` and `BLOCKERS_PRESENT` from the clarification summaries
as gate inputs. They are not validator artifacts, but they are part of the
phase boundary contract the orchestrator must honor.

For Phase 4, the authoritative downstream contract is owned by
`creating-github-child-issues`. That skill chooses the write model in this
order: **native child issues / sub-issues** when the environment and `gh` (or
configured API path) support them cleanly; otherwise **linked issues** with an
explicit parent/child narrative in the task plan; otherwise **task-list
references** in the parent issue body or plan only if the first two are not
viable. Treat `docs/<ISSUE_SLUG>-tasks.md` as valid for downstream use only when
it carries the workflow-level `## GitHub Task Issues` table (or equivalent name
defined in that skill) plus the per-task inline issue references required for a
resumable handoff. The downstream `Created/Linked Task Issues` table (or
equivalent) is the structured handoff for workflow progress tracking.

For Phase 5, the authoritative downstream contract is owned by
`planning-github-task`. The stable planning handoff is the concrete four-file
set:

- `docs/<ISSUE_SLUG>-task-<N>-brief.md`
- `docs/<ISSUE_SLUG>-task-<N>-execution-plan.md`
- `docs/<ISSUE_SLUG>-task-<N>-test-spec.md`
- `docs/<ISSUE_SLUG>-task-<N>-refactoring-plan.md`

Treat those files as the planning boundary consumed by Phases 6 and 7. The
detailed section-level requirements for each file stay owned by the downstream
Phase 5 skill.

After each phase or gate, return only:

- A concise phase summary for the user
- The next required decision or confirmation, if any
- The file path or `ISSUE_SLUG` / issue reference needed for the next dispatch

Return raw subagent output only when the user explicitly asks for it.

## Subagent Registry

Read a subagent definition only when you are about to dispatch that subagent.

| Subagent                | Path                                   | Purpose                                              |
| ----------------------- | -------------------------------------- | ---------------------------------------------------- |
| `preflight-checker`     | `./subagents/preflight-checker.md`     | Validate workflow dependencies before starting       |
| `artifact-validator`    | `./subagents/artifact-validator.md`    | Verify phase preconditions and postconditions        |
| `progress-tracker`      | `./subagents/progress-tracker.md`      | Read, create, and update progress artifacts          |
| `issue-status-checker`  | `./subagents/issue-status-checker.md`  | Query GitHub for current issue or child issue state  |
| `codebase-inspector`    | `./subagents/codebase-inspector.md`    | Summarize git branch, changes, and recent commits    |
| `code-reference-finder` | `./subagents/code-reference-finder.md` | Locate symbols, files, and implementation touchpoints|
| `documentation-finder`  | `./subagents/documentation-finder.md`  | Find relevant docs and return concise summaries      |

## Downstream Skills

Each numbered phase is owned by a dedicated downstream skill. Read that skill's
`SKILL.md` only when entering the phase.

| Phase | Skill                      | Path (relative to skills root)           |
| ----- | -------------------------- | ---------------------------------------- |
| 1     | `fetching-github-issue`    | `../fetching-github-issue/SKILL.md`      |
| 2     | `planning-github-issue-tasks` | `../planning-github-issue-tasks/SKILL.md` |
| 3     | `clarifying-assumptions`   | `../clarifying-assumptions/SKILL.md`     |
| 4     | `creating-github-child-issues` | `../creating-github-child-issues/SKILL.md` |
| 5     | `planning-github-task`     | `../planning-github-task/SKILL.md`       |
| 6     | `clarifying-assumptions`   | `../clarifying-assumptions/SKILL.md`     |
| 7     | `executing-github-task`    | `../executing-github-task/SKILL.md`      |

**Note:** `clarifying-assumptions` expects input `TICKET_KEY`. For this workflow,
set **`TICKET_KEY` = `ISSUE_SLUG`** so artifact paths resolve to
`docs/<ISSUE_SLUG>-…`.

## How This Skill Works

The orchestrator protects its context window aggressively. It holds only:

- Decision-relevant summaries from subagents and downstream skills
- Current workflow state: phase, task number, status, next gate
- User instructions and confirmations
- Failure reports that require judgment

Use these rules throughout the workflow:

- **Delegate execution-heavy work.** Validation, GitHub queries via `gh`, file
  updates, git inspection, code search, and documentation lookup all happen
  through downstream skills or utility subagents.
- **Pass structured handoffs.** Use `ISSUE_SLUG`, file paths, task numbers, owner/repo/issue
  references, and concise summaries. Do not rely on ambient context.
- **Advance one boundary at a time.** Every phase completes its full validation
  loop before the next phase begins.
- **Honor downstream contracts exactly.** Use the downstream skill's output
  contract as the source of truth, and keep the orchestrator's gate summaries
  aligned with that contract rather than with older shorthand checks. For
  Phase 4, that means validating both the workflow-level GitHub task-issue table
  and the per-task inline references, then using the downstream summary table for
  progress metadata.
- **Honor clarification summary flags.** `RE_PLAN_NEEDED=true` reopens the
  relevant planning phase. `BLOCKERS_PRESENT=true` is a hard stop before GitHub
  writes or task execution, even if the generic user gate would otherwise allow
  advancing.
- **Preserve resumability.** Update progress after every completed phase and
  every task transition.
- **Separate artifact lifecycles.** Orchestration artifacts stay on disk and are
  never committed or deleted. Implementation artifacts are handled by downstream
  skills.
- **Escalate loudly.** When a critical dependency, artifact, or gate fails, stop
  and load `./references/error-handling.md`.

Inline work is limited to conversational coordination, such as:

- Asking the user for `ISSUE_URL` when only owner/repo/number is known
- Walking through clarify/critique prompts that a downstream skill explicitly
  keeps inline
- Presenting gate options that require user confirmation

## Dispatch Pattern

For any subagent dispatch:

1. Read the subagent definition from the registry.
2. Pass the subagent its explicit inputs only.
3. Collect the structured summary it returns.
4. Retain only the verdict and next-step-relevant details.

Parallel dispatch is allowed only when the work is independent and its outputs
are summaries, such as pre-task context gathering. Dependent operations remain
sequential.

## Standard Phase Cycle

Phases 1-6 follow this full cycle. Phase 7 uses the same precondition ->
downstream skill -> progress -> gate structure, but does not add an
orchestrator-level postcondition validator because `executing-github-task` owns
its internal completion and quality-gate semantics.

For Phases 5-7, `./references/task-loop.md` remains the procedural authority
when it adds task-loop-specific steps between the generic boundaries. In
particular, Phase 5 initializes per-task progress after the precondition passes
and before invoking `planning-github-task`.
Treat execution-skill `BLOCKED` results in Phase 7 as hard-stop resume points,
not as ordinary implementation gaps or generic fix-loop retries.

> Reminder: for Phases 1-6, run the full loop in order: validator (when needed)
> -> downstream skill -> validator -> progress update -> gate decision. For
> Phase 7, use the execution-skill-owned variant described in
> `./references/task-loop.md`. Use `./references/data-contracts.md` for exact
> PASS/FAIL semantics at the boundary.

1. **Announce** the phase banner.
2. **Validate preconditions** by dispatching `artifact-validator` when a
   precondition exists for that phase.
3. **Invoke the downstream skill** by reading its `SKILL.md` and following it
   exactly.
4. **Validate postconditions** by dispatching `artifact-validator`.
5. **Update progress** by dispatching `progress-tracker`.
6. **Run the gate check**: advance automatically, ask the user, or enter a
   targeted re-plan/retry loop.

Use `./references/data-contracts.md` when you need the exact boundary checks or
PASS/FAIL semantics for a phase transition.

For Phases 3 and 6, the gate check uses both the validator verdict and the
downstream clarification summary. Advance only when
`BLOCKERS_PRESENT=false`, and when `RE_PLAN_NEEDED=true`, only after the
required re-plan cycle completes.

Use this banner format:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Phase <N>/7 - <Phase name>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

When a phase has a targeted fix or re-plan loop, re-run only the failing phase
and only the failing gate. Maximum: 3 loops before escalating to the user.

## Gate Rules

Use these gate rules consistently:

| Boundary       | Gate type   | Rule |
| -------------- | ----------- | ---- |
| 1 -> 2         | Automatic   | Proceed when validation passes |
| 2 -> 3         | Automatic   | Proceed when validation passes |
| 3 -> 4         | User gate   | Proceed only when validation passes, `BLOCKERS_PRESENT=false`, and the user explicitly approves GitHub writes |
| 4 -> 5         | User gate   | User selects the next task to execute |
| 5 -> 6         | Automatic   | Proceed when planning artifacts validate |
| 6 -> 7         | User gate   | Proceed only when validation passes, `BLOCKERS_PRESENT=false`, and the user confirms the critiqued task plan is ready for real execution |
| 7 -> next task | User gate   | User chooses the next task or stops |

## Phase Guide

Load the right reference file based on the phase you are about to run:

| Situation    | Reference file                     | Purpose                         |
| ------------ | ---------------------------------- | ------------------------------- |
| Phases 1-4   | `./references/phases-1-4.md`       | Linear pipeline playbook        |
| Phases 5-7   | `./references/task-loop.md`        | Per-task loop playbook          |
| Error/Resume | `./references/error-handling.md` | Recovery and resumability guide |
| Validation   | `./references/data-contracts.md` | Artifact check quick reference  |

## Starting or Resuming

### 1. Resolve the issue identifier

Build `ISSUE_SLUG` from `ISSUE_URL` when available. If you only have
`OWNER`, `REPO`, and `ISSUE_NUMBER`, normalize owner and repo to lowercase,
compute `ISSUE_SLUG`, use it for local progress discovery, then ask for the full
`ISSUE_URL` before any GitHub-dependent phase that needs authoritative remote
context.

### 2. Read progress state

Dispatch `progress-tracker` with `ACTION=read` and `ISSUE_SLUG` (exact inputs per
`./subagents/progress-tracker.md`; quick reference in
`./references/data-contracts.md`).

Interpret the summary:

- No progress found -> start at Phase 1
- Progress found in phases 1-4 -> resume from the next incomplete workflow phase
- Progress found in phases 5-7 -> resume the specific task/phase indicated

### 3. Run preflight for the actual remaining phases

Dispatch `preflight-checker` only after the progress read tells you where the
workflow will start:

- Fresh start -> `PHASES=1-7`
- Resume in phases 1-4 -> `PHASES=<current incomplete phase through 7>`
- Resume in phases 5-7 -> `PHASES=<current task phase through 7>`

Pass `ISSUE_SLUG` and, when known, `ISSUE_URL` / owner-repo context so the
checker can validate `gh` auth and downstream skill presence.

Interpret the result:

- `PREFLIGHT: PASS` -> continue
- `PREFLIGHT: FAIL` -> stop and present missing dependency instructions
- `PREFLIGHT: ERROR` -> stop and ask the user how to proceed

### 4. Confirm resume points

If resuming past Phase 1, tell the user what was found and confirm before
continuing.

### 5. Load the correct playbook

Read the matching file from the Phase Guide and follow it exactly for the
current phase range. For full resume examples and failure routing, read
`./references/error-handling.md`.

## Escalation

Use `./references/error-handling.md` whenever a critical dependency, artifact,
gate, or retry budget blocks forward progress. At this level, keep only the
summary needed to decide the next move:

- `PREFLIGHT: FAIL` or `PREFLIGHT: ERROR` -> stop before entering the phase
- Critical validator or progress failures -> stop progression and present the
  blocking summary
- Phase 7 `BLOCKED` from `task-executor`, `documentation-writer`, or
  `requirements-verifier` -> surface the exact missing capability or blocked
  dependency, treat it as a user-steered pause, and resume from the blocked
  Phase 7 step after it is resolved
- Downstream execution `ERROR` or exhausted execution-skill fix cycle -> do not
  mark the task complete; follow `./references/task-loop.md` and
  `./references/error-handling.md`
- Retry or re-plan loop exhausted -> present the accumulated feedback and ask
  the user how to proceed

## Example

<example>
Input: `ISSUE_URL=https://github.com/acme/app/issues/42` → `ISSUE_SLUG=acme-app-42`

1. Dispatch `progress-tracker` with `ACTION=read`, `ISSUE_SLUG=acme-app-42`
2. No progress found -> dispatch `preflight-checker` with
   `ISSUE_SLUG=acme-app-42`, `PHASES=1-7`
3. Read `./references/phases-1-4.md`
4. Enter Phase 1 and read `../fetching-github-issue/SKILL.md`
5. After the downstream skill finishes, dispatch `artifact-validator`
6. Validator returns:
   `VALIDATION: PASS`
   `Phase: 1 | Direction: postcondition`
7. Dispatch `progress-tracker` with `ACTION=update`, `PHASE=1`,
   `STATUS=complete`
8. Tell the user: "Issue fetched. Moving to task planning."

The orchestrator keeps only that summary, the `ISSUE_SLUG`, and the next phase.
</example>
