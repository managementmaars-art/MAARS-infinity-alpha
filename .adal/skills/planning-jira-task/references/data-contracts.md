# Planning Jira Task Contracts

> Read this file when checking prerequisites or artifact handoffs.
>
> Reminder: the orchestrator keeps summaries and file paths, not raw task-plan
> content.

## Upstream Prerequisites

Required file:

- `docs/<TICKET_KEY>-tasks.md`

Required content inside that file for `TASK_NUMBER=<N>`:

- `## Task <N>:` section exists
- Task title exists
- `Objective` content exists
- `Relevant requirements and context` content exists
- `Implementation notes` content exists
- `Definition of done` content exists
- `Likely files / artifacts affected` content exists
- `Dependencies / prerequisites` content exists, even if the value is `None`
- `Questions to answer before starting` content exists, even if the value is
  `None`

Expected upstream workflow state:

- Any task listed as a dependency for task `<N>` is already marked complete
- Questions for task `<N>` are resolved, explicitly waived, or recorded as
  conscious follow-up decisions
- If a `## Decisions Log` section exists, treat it as the latest authority over
  earlier task-plan wording
- In the full Jira workflow, Phase 4 has already added a `## Jira Subtasks`
  table, but planning does not depend on Jira linkage to assemble the brief

Optional upstream context:

- `docs/<TICKET_KEY>.md` may provide extra ticket context if a subagent needs it
- `docs/<TICKET_KEY>-task-<N>-decisions.md` is available on critique-driven
  re-plan cycles
- `Jira Subtask: <KEY>` lines may already be present from Phase 4; planning
  should tolerate them when present, but it does not require them

## Downstream Artifacts

### `docs/<TICKET_KEY>-task-<N>-brief.md`

Owner: `execution-prepper`

Must contain:

- `# Execution Brief - <TICKET_KEY> Task <N>: <Title>`
- `## Objective`
- `## Relevant Requirements and Context`
- `## Implementation Notes`
- `## Definition of Done`
- `## Likely Files / Artifacts Affected`
- `## Resolved Questions and Decisions`
- `## Constraints`

### `docs/<TICKET_KEY>-task-<N>-execution-plan.md`

Owner: `execution-planner`

Must contain:

- `# Execution Plan - <TICKET_KEY> Task <N>: <Title>`
- `## Codebase Summary`
- `## Recommended Skills`
- `## Implementation Approach`
- `## File-Level Strategy`
- `## Risks and Considerations`
- `## User Impact Assessment`
- `## Blockers / Ambiguities`

### `docs/<TICKET_KEY>-task-<N>-test-spec.md`

Owner: `test-strategist`

Must contain:

- `# Test Specification - <TICKET_KEY> Task <N>: <Title>`
- `## Test Framework and Conventions`
- `## Test Groups`
- `## Definition of Done Coverage`
- `## Notes for Task Executor`
- `## Blockers / Ambiguities`

### `docs/<TICKET_KEY>-task-<N>-refactoring-plan.md`

Owner: `refactoring-advisor`

Must contain:

- `# Refactoring Recommendation - <TICKET_KEY> Task <N>: <Title>`
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
