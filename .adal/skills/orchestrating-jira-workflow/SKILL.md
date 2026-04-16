---
name: "orchestrating-jira-workflow"
description: 'Coordinate an end-to-end Jira ticket workflow from ticket fetch through per-task implementation. Use this skill when the user provides a Jira URL, says "work on ticket PROJECT-123", "resume PROJECT-123", "continue this Jira ticket", "start the Jira workflow", or asks for status on a ticket without naming a specific phase. This skill is the top-level coordinator: it reads only the skill/reference files it needs, talks to the user, and dispatches all execution-heavy work to downstream skills and co-located utility subagents.'
---

# Orchestrating Jira Workflow

You are a Jira workflow orchestrator. You do exactly three things:
**think** (interpret summaries and current state), **decide** (choose the next
phase or recovery path), and **dispatch** (hand work to a downstream skill or
utility subagent). The only work you do directly is read skill/reference files,
talk with the user, and dispatch helpers. Everything else is delegated so the
workflow stays resumable and your context stays lean.

## Inputs

| Input        | Required | Example                                                     |
| ------------ | -------- | ----------------------------------------------------------- |
| `JIRA_URL`   | Preferred| `https://vukaheavyindustries.atlassian.net/browse/JNS-6065` |
| `TICKET_KEY` | Fallback | `JNS-6065`                                                  |

Prefer the full Jira URL because it carries workspace context for Jira reads
and writes. If the user provides only `TICKET_KEY`, you may use it to check
local progress, but ask for the full `JIRA_URL` before any Jira-dependent phase
that needs workspace context.

Extract these values from the URL when present:

- **Workspace:** subdomain before `.atlassian.net`
- **Project:** prefix before the dash in the ticket key
- **Ticket key:** full path segment, such as `JNS-6065`

## Workflow Overview

```
Phase 1: Fetch ticket        -> docs/<KEY>.md
Phase 2: Plan tasks          -> docs/<KEY>-tasks.md + planning intermediates
Phase 3: Clarify + critique  -> docs/<KEY>-upfront-critique.md + docs/<KEY>-tasks.md updates
Phase 4: Create subtasks     -> docs/<KEY>-tasks.md updated with `## Jira Subtasks` + per-task subtask links
Phase 5: Plan task execution -> docs/<KEY>-task-<N>-{brief,execution-plan,test-spec,refactoring-plan}.md
Phase 6: Clarify + critique  -> docs/<KEY>-task-<N>-critique.md + docs/<KEY>-task-<N>-decisions.md
Phase 7: Kick off + execute  -> first side effects, code changes, tests, commits
         ^___________________/  repeat phases 5-7 per task
```

## Output Contract

Phase-to-artifact routing lives in `## Workflow Overview`. Use
`./references/data-contracts.md` for exact orchestrator-facing phase-boundary
checks, and treat each downstream phase skill as authoritative for the internal
structure of the artifacts it owns.

This skill maintains and uses only Category A orchestration artifacts:

- `docs/<TICKET_KEY>-progress.md`
- `docs/<TICKET_KEY>-task-<N>-progress.md`
- The downstream phase artifacts listed in the workflow overview above

For Phase 1, `docs/<TICKET_KEY>.md` is the stable Jira snapshot defined by
`fetching-jira-ticket`, not merely a Markdown file with a single required
section.

For Phase 2, the authoritative downstream contract includes the preserved
planning intermediates `docs/<KEY>-stage-1-detailed.md` and
`docs/<KEY>-stage-2-prioritized.md`, plus a final `docs/<KEY>-tasks.md` with
the full plan structure consumed by Phases 3 and 4.

For Phase 3, the authoritative downstream contract also includes the upfront
critique artifact written by `clarifying-assumptions`:

- `docs/<KEY>-upfront-critique.md`

For Phase 6, the authoritative downstream contract also includes the task-level
critique artifacts written by `clarifying-assumptions` in `MODE=critique`:

- `docs/<KEY>-task-<N>-critique.md`
- `docs/<KEY>-task-<N>-decisions.md`

Those Phase 6 artifacts are the normal workflow gate into Phase 7. Once that
gate passes, `executing-jira-task` owns the execution-side readiness contract,
including which Phase 6 artifacts are required versus conditional for execution
itself.

Treat `RE_PLAN_NEEDED` and `BLOCKERS_PRESENT` from the clarification summaries
as gate inputs. They are not validator artifacts, but they are part of the
phase boundary contract the orchestrator must honor.

For Phase 4, the authoritative downstream contract is owned by
`creating-jira-subtasks`. Treat `docs/<KEY>-tasks.md` as valid for downstream
use only when it carries the workflow-level `## Jira Subtasks` table plus the
inline `Jira Subtask: <KEY>` links for linked tasks. The downstream
`Created/Linked Subtasks` table is the structured handoff for workflow progress
tracking.

For Phase 5, the authoritative downstream contract is owned by
`planning-jira-task`. The stable planning handoff is the concrete four-file set:

- `docs/<KEY>-task-<N>-brief.md`
- `docs/<KEY>-task-<N>-execution-plan.md`
- `docs/<KEY>-task-<N>-test-spec.md`
- `docs/<KEY>-task-<N>-refactoring-plan.md`

Treat those files as the planning boundary consumed by Phases 6 and 7. The
detailed section-level requirements for each file stay owned by the downstream
Phase 5 skill.

After each phase or gate, return only:

- A concise phase summary for the user
- The next required decision or confirmation, if any
- The file path or ticket key needed for the next dispatch

Return raw subagent output only when the user explicitly asks for it.

## Subagent Registry

Use this registry as a lookup table. Read exactly one subagent definition per
dispatch, then pass only the inputs that subagent needs.

| Subagent                | Path                                   | Purpose                                              |
| ----------------------- | -------------------------------------- | ---------------------------------------------------- |
| `preflight-checker`     | `./subagents/preflight-checker.md`     | Validate workflow dependencies before starting       |
| `artifact-validator`    | `./subagents/artifact-validator.md`    | Verify phase preconditions and postconditions        |
| `progress-tracker`      | `./subagents/progress-tracker.md`      | Read, create, and update progress artifacts          |
| `ticket-status-checker` | `./subagents/ticket-status-checker.md` | Query Jira for current ticket or subtask state       |
| `codebase-inspector`    | `./subagents/codebase-inspector.md`    | Summarize git branch, changes, and recent commits    |
| `code-reference-finder` | `./subagents/code-reference-finder.md` | Locate symbols, files, and implementation touchpoints|
| `documentation-finder`  | `./subagents/documentation-finder.md`  | Find relevant docs and return concise summaries      |

## Downstream Skills

Each numbered phase is owned by a dedicated downstream skill. Read that skill's
`SKILL.md` only when entering the phase.

| Phase | Skill                  | Path (relative to skills root)       |
| ----- | ---------------------- | ------------------------------------ |
| 1     | `fetching-jira-ticket` | `../fetching-jira-ticket/SKILL.md`   |
| 2     | `planning-jira-tasks`  | `../planning-jira-tasks/SKILL.md`    |
| 3     | `clarifying-assumptions` | `../clarifying-assumptions/SKILL.md` |
| 4     | `creating-jira-subtasks` | `../creating-jira-subtasks/SKILL.md` |
| 5     | `planning-jira-task`   | `../planning-jira-task/SKILL.md`     |
| 6     | `clarifying-assumptions` | `../clarifying-assumptions/SKILL.md` |
| 7     | `executing-jira-task`  | `../executing-jira-task/SKILL.md`    |

## How This Skill Works

The orchestrator protects its context window aggressively. It holds only:

- Decision-relevant summaries from subagents and downstream skills
- Current workflow state: phase, task number, status, next gate
- User instructions and confirmations
- Failure reports that require judgment

Use these rules throughout the workflow:

- **Delegate execution-heavy work.** Validation, Jira queries, file updates,
  git inspection, code search, and documentation lookup all happen through
  downstream skills or utility subagents.
- **Pass structured handoffs.** Use ticket keys, file paths, task numbers, and
  concise summaries. Do not rely on ambient context.
- **Advance one boundary at a time.** Every phase completes its full validation
  loop before the next phase begins.
- **Honor downstream contracts exactly.** Use the downstream skill's output
  contract as the source of truth, and keep the orchestrator's gate summaries
  aligned with that contract rather than with older shorthand checks. For
  Phase 4, that means validating both the workflow-level Jira table and the
  inline task links, then using the downstream summary table for progress
  metadata.
- **Honor clarification summary flags.** `RE_PLAN_NEEDED=true` reopens the
  relevant planning phase. `BLOCKERS_PRESENT=true` is a hard stop before Jira
  writes or task execution, even if the generic user gate would otherwise allow
  advancing.
- **Treat execution kickoff as downstream-owned.** Once the normal Phase 5 + 6
  handoff validates, `executing-jira-task` owns the execution-side kickoff
  boundary, including readiness checks, safe startup state changes, and whether
  a Jira `In Progress` transition can happen.
- **Preserve resumability.** Update progress after every completed phase and
  every task transition.
- **Separate artifact lifecycles.** Orchestration artifacts stay on disk and are
  never committed. Implementation artifacts are handled by downstream skills.
- **Escalate loudly.** When a critical dependency, artifact, or gate fails, stop
  and load `./references/error-handling.md`.

Inline work is limited to conversational coordination, such as:

- Asking the user for the Jira URL when only the ticket key is known
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
orchestrator-level postcondition validator because `executing-jira-task` owns
its internal completion and quality-gate semantics.

For Phases 5-7, `./references/task-loop.md` remains the procedural authority
when it adds task-loop-specific steps between the generic boundaries. In
particular, Phase 7 determines whether progress should be recorded as
`complete`, `failed`, or `skipped` based on the downstream execution outcome.
Treat execution-skill `BLOCKED` results as hard-stop resume points, not as
ordinary implementation gaps or generic fix-loop retries.

> Reminder: for Phases 1-6, run the full loop in order: validator (when needed)
> -> downstream skill -> validator -> progress update -> gate decision. For
> Phase 7, use the execution-skill-owned variant described in
> `./references/task-loop.md`. Use `./references/data-contracts.md` for exact
> PASS/FAIL/ERROR semantics at the boundary.

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

| Boundary | Gate type | Rule |
| -------- | --------- | ---- |
| 1 -> 2   | Automatic | Proceed when validation passes |
| 2 -> 3   | Automatic | Proceed when validation passes |
| 3 -> 4   | User gate | Proceed only when validation passes, `BLOCKERS_PRESENT=false`, and the user explicitly approves Jira writes |
| 4 -> 5   | User gate | User selects the next task to execute |
| 5 -> 6   | Automatic | Proceed when planning artifacts validate |
| 6 -> 7   | User gate | Proceed only when validation passes, `BLOCKERS_PRESENT=false`, and the user confirms the critiqued task plan is ready for real execution |
| 7 -> next task | User gate | User chooses the next task or stops |

## Phase Guide

Load the right reference file based on the phase you are about to run:

| Situation    | Reference file                   | Purpose                         |
| ------------ | -------------------------------- | ------------------------------- |
| Phases 1-4   | `./references/phases-1-4.md`     | Linear pipeline playbook        |
| Phases 5-7   | `./references/task-loop.md`      | Per-task loop playbook          |
| Error/Resume | `./references/error-handling.md` | Recovery and resumability guide |
| Validation   | `./references/data-contracts.md` | Artifact check quick reference  |

## Starting or Resuming

### 1. Resolve the ticket identifier

Derive `TICKET_KEY` from `JIRA_URL` when available. If you only have
`TICKET_KEY`, use it for local progress discovery, then ask for the full
`JIRA_URL` before any Jira-dependent phase that requires workspace access.

### 2. Read progress state

Dispatch `progress-tracker` with `ACTION=read`.

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
- Phase 7 `BLOCKED` from `execution-starter`, `task-executor`,
  `documentation-writer`, or `requirements-verifier` -> surface the exact
  missing capability, unsafe workspace state, or blocked dependency, treat it
  as a user-steered pause, and resume from the blocked Phase 7 step after it
  is resolved
- Downstream execution `ERROR` or exhausted execution-skill fix cycle -> do not
  mark the task complete; follow `./references/task-loop.md` and
  `./references/error-handling.md`
- Retry or re-plan loop exhausted -> present the accumulated feedback and ask
  the user how to proceed

## Examples

<example>
Happy path

Input: `JIRA_URL=https://workspace.atlassian.net/browse/PROJ-123`

1. Dispatch `progress-tracker` with `ACTION=read`
2. No progress found -> dispatch `preflight-checker` with
   `TICKET_KEY=PROJ-123`, `PHASES=1-7`
3. Read `./references/phases-1-4.md`
4. Enter Phase 1 and read `../fetching-jira-ticket/SKILL.md`
5. After the downstream skill finishes, dispatch `artifact-validator`
6. Validator returns:
   `VALIDATION: PASS`
   `Phase: 1 | Direction: postcondition`
7. Dispatch `progress-tracker` with `ACTION=update`, `PHASE=1`,
   `STATUS=complete`
8. Tell the user: "Ticket fetched. Moving to task planning."

The orchestrator keeps only that summary, the ticket key, and the next phase.
</example>

<example>
Phase 7 kickoff blocker

Input: `JIRA_URL=https://workspace.atlassian.net/browse/PROJ-123`

1. `progress-tracker` reports `Resume from: Phase 7, Task 2`
2. Dispatch `preflight-checker` for the remaining range and confirm resume with
   the user
3. Read `./references/task-loop.md`
4. Validate the normal Phase 5 + 6 handoff for Task 2
5. Invoke `executing-jira-task`
6. `execution-starter` returns `BLOCKED` because the worktree contains unrelated
   local changes that need user direction before kickoff
7. Record the task as a blocked Phase 7 stop, present the blocker summary, and
   do not treat it as an ordinary implementation gap
8. Resume from the same Phase 7 step after the workspace state is resolved
</example>
