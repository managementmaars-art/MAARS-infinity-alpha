# Planning GitHub Task Contracts

> Read this file when checking prerequisites or artifact handoffs.
>
> Reminder: the orchestrator keeps summaries and file paths, not raw task-plan
> content.

## Upstream Prerequisites

Required file:

- `docs/<ISSUE_SLUG>-tasks.md`

Required content inside that file for `TASK_NUMBER=<N>`:

- `## Task <N>:` section exists
- Task title exists
- `Objective` content exists
- `Relevant requirements and context` content exists
- `Implementation notes` content exists
- `Definition of done` content exists
- `Likely files / artifacts affected` content exists
- `Dependencies / prerequisites` content exists, even if the value is `None`
- `Priority` content exists
- `Questions to answer before starting` content exists, even if the value is
  `None`

Expected upstream workflow state:

- Any task listed as a dependency for task `<N>` is already marked complete
- Questions for task `<N>` are resolved, explicitly waived, or recorded as
  conscious follow-up decisions
- If a `## Decisions Log` section exists, treat it as the latest authority over
  earlier task-plan wording
- In the normal orchestrated Phase 5 entry, `docs/<ISSUE_SLUG>-tasks.md` also
  satisfies the Phase 4 handoff contract from
  `../../orchestrating-github-workflow/references/data-contracts.md`: it
  contains `## GitHub Task Issues`, the workflow-level table has one row per
  numbered task, and any row with a concrete GitHub issue has a matching
  per-task inline reference

Optional upstream context:

- `docs/<ISSUE_SLUG>.md` may provide extra issue snapshot context if a subagent
  needs it
- `docs/<ISSUE_SLUG>-task-<N>-decisions.md` is available on critique-driven
  re-plan cycles (produced in Phase 6)
- Per-task lines or notes that reference a GitHub task issue (for example child
  issue URLs or numbers) may already be present from Phase 4; when this skill is
  invoked outside the normal orchestrated Phase 5 entry, tolerate their absence
  but do not invent them

## Downstream Artifacts

### `docs/<ISSUE_SLUG>-task-<N>-brief.md`

Owner: `execution-prepper`

Must contain:

- `# Execution Brief - <ISSUE_SLUG> Task <N>: <Title>`
- `## Objective`
- `## Relevant Requirements and Context`
- `## Implementation Notes`
- `## Definition of Done`
- `## Likely Files / Artifacts Affected`
- `## Resolved Questions and Decisions`
- `## Constraints`

### `docs/<ISSUE_SLUG>-task-<N>-execution-plan.md`

Owner: `execution-planner`

Must contain:

- `# Execution Plan - <ISSUE_SLUG> Task <N>: <Title>`
- `## Codebase Summary`
- `## Recommended Skills`
- `## Implementation Approach`
- `## File-Level Strategy`
- `## Risks and Considerations`
- `## User Impact Assessment`
- `## Blockers / Ambiguities`

### `docs/<ISSUE_SLUG>-task-<N>-test-spec.md`

Owner: `test-strategist`

Must contain:

- `# Test Specification - <ISSUE_SLUG> Task <N>: <Title>`
- `## Test Framework and Conventions`
- `## Test Groups`
- `## Definition of Done Coverage`
- `## Notes for Task Executor`
- `## Blockers / Ambiguities`

### `docs/<ISSUE_SLUG>-task-<N>-refactoring-plan.md`

Owner: `refactoring-advisor`

Must contain:

- `# Refactoring Recommendation - <ISSUE_SLUG> Task <N>: <Title>`
- `## Verdict`
- `## Before Implementation`
- `## During Implementation`
- `## Out of Scope`
- `## Impact on Existing Tests`
- `## Blockers / Ambiguities`

## Artifact Lifecycle

These planning files are Category A orchestration artifacts:

- Keep them on disk
- Overwrite them only when the owning subagent is intentionally re-run
- Do not delete them as cleanup
- Do not commit them to git

## Orchestrator alignment

Phase 5 postcondition and Phase 6 precondition in
`../../orchestrating-github-workflow/references/data-contracts.md` expect exactly
these four files. Section-level detail is owned by this skill and the subagents
above.
