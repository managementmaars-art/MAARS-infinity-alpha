---
name: "planning-jira-task"
description: 'Plan how to execute one task from `docs/<TICKET_KEY>-tasks.md`. Runs a four-subagent pipeline that validates the task, writes an execution brief, inspects the codebase, defines behavior-driven tests, and evaluates refactoring needs. Produces `docs/<TICKET_KEY>-task-<N>-{brief,execution-plan,test-spec,refactoring-plan}.md` for one task only. Use when the user says "plan task 3", "prepare task 2 for execution", "how should we implement task 1", or when `orchestrating-jira-workflow` enters Phase 5. This skill creates planning artifacts only; it does not change git state, transition Jira issues, or modify product code.'
---

# Planning Jira Task

Plan exactly how to execute one task from the ticket task plan. This
orchestrator does three things: **think** (interpret summaries and plan state),
**decide** (choose the next planning dispatch or re-plan path), and
**dispatch** (hand execution-heavy work to co-located subagents). The planning
artifacts live on disk; the orchestrator keeps only concise summaries in
context.

Success means the four planning artifacts exist and are ready for Phase 6
critique and Phase 7 execution. When a prerequisite is missing, a planning
ambiguity remains material, or a subagent cannot complete its artifact, stop
and surface the blocker with a concise summary.

## Inputs

| Input | Required | Example |
| ----- | -------- | ------- |
| `TICKET_KEY` | Yes | `JNS-6065` |
| `TASK_NUMBER` | Yes | `3` |
| `RE_PLAN` | No | `true` |
| `DECISIONS_FILE` | No | `docs/JNS-6065-task-3-decisions.md` |

Read `./references/data-contracts.md` when you need the upstream prerequisites
or downstream artifact expectations.

Use `RE_PLAN` and `DECISIONS_FILE` only for critique-driven reruns. Read
`./references/pipeline.md` when deciding which stages to rerun.

## Workflow Overview

1. `execution-prepper` validates the task and writes the execution brief.
2. `execution-planner` inspects the codebase and writes the execution plan.
3. `test-strategist` writes the behavior-driven test specification.
4. `refactoring-advisor` writes the refactoring recommendation.
5. The skill returns only a concise planning summary and the artifact paths
   needed for Phase 6 critique and Phase 7 execution.

## Output Contract

This skill writes only Category A orchestration artifacts:

| Artifact | Produced by | Consumed by |
| -------- | ----------- | ----------- |
| `docs/<KEY>-task-<N>-brief.md` | `execution-prepper` | All downstream planning subagents, critique, execution |
| `docs/<KEY>-task-<N>-execution-plan.md` | `execution-planner` | critique, execution |
| `docs/<KEY>-task-<N>-test-spec.md` | `test-strategist` | critique, execution |
| `docs/<KEY>-task-<N>-refactoring-plan.md` | `refactoring-advisor` | critique, execution |

On a successful run, all four files exist. On a re-plan, overwrite only the
files owned by the subagents that are re-run. These files stay on disk for the
life of the workflow and are never committed to git.

## Subagent Registry

| Subagent | Path | Purpose |
| -------- | ---- | ------- |
| `execution-prepper` | `./subagents/execution-prepper.md` | Validate task readiness and assemble the execution brief |
| `execution-planner` | `./subagents/execution-planner.md` | Inspect the codebase and write the implementation plan |
| `test-strategist` | `./subagents/test-strategist.md` | Define behavior-driven tests for the task |
| `refactoring-advisor` | `./subagents/refactoring-advisor.md` | Recommend only the refactoring needed for this task |

Read a subagent definition only when you are about to dispatch that subagent.

## How This Skill Works

- Read `./references/data-contracts.md` when checking prerequisites or artifact
  expectations.
- Read `./references/pipeline.md` when running the standard planning pipeline
  or a critique-driven re-plan.
- At each boundary, validate that the current input artifact exists before
  dispatch, then confirm that the expected output artifact was written before
  advancing.
- Pass only explicit handoffs between steps: ticket key, task number, decision
  file path, and artifact file paths.
- Keep only verdicts, file paths, and next-step-relevant notes from each
  subagent.
- Advance sequentially. Rerun only the subagents invalidated by critique, plus
  their downstream dependents.
- Surface blockers and pause for resolution when ambiguity remains.

## Phase Guide

This table tells you which reference to load. `## Execution Steps` remains the
source of truth for the actual orchestration order.

| Situation | Reference file | Purpose |
| --------- | -------------- | ------- |
| Standard Phase 5 run | `./references/pipeline.md` | Dispatch order, handoffs, and success criteria |
| Re-plan after Phase 6 critique | `./references/pipeline.md` | Targeted rerun rules and retry limit |
| Contract questions | `./references/data-contracts.md` | Upstream prerequisites and downstream consumers |

## Execution Steps

1. Read `./references/data-contracts.md` and confirm the task-plan prerequisites
   exist for `TICKET_KEY` and `TASK_NUMBER`.
2. Read `./references/pipeline.md`.
3. Dispatch the first required subagent from the registry with explicit inputs
   only.
4. Retain only its verdict, artifact path, and the notes needed for the next
   decision.
5. Continue until all required planning artifacts are written and confirmed, or
   a blocker is surfaced.
6. Report the artifact paths and key planning decisions to the user.

## Example

<example>
Input:
- `TICKET_KEY=PROJ-123`
- `TASK_NUMBER=2`

1. Dispatch `execution-prepper`
2. Subagent returns:
   `PREP: PASS`
   `Brief: docs/PROJ-123-task-2-brief.md`
3. Dispatch `execution-planner` with the brief path
4. Subagent returns:
   `PLAN: PASS`
   `Plan: docs/PROJ-123-task-2-execution-plan.md`
5. Dispatch `test-strategist`
6. Subagent returns:
   `TEST_SPEC: PASS`
   `Spec: docs/PROJ-123-task-2-test-spec.md`
7. Dispatch `refactoring-advisor`
8. Subagent returns:
   `REFACTORING: PASS`
   `Plan: docs/PROJ-123-task-2-refactoring-plan.md`
9. Tell the user:
   "Task 2 planning complete. Four planning artifacts are ready for critique."

The orchestrator keeps only those summaries and the artifact paths.
</example>
