# Planning Pipeline

> Read this file when running Phase 5 or a Phase 6-triggered re-plan.
>
> Reminder: dispatch one subagent at a time, keep only summaries, and rerun only
> the steps invalidated by critique.

## Standard Run

### 1. Dispatch `execution-prepper`

Inputs:

- `TICKET_KEY`
- `TASK_NUMBER`
- `RE_PLAN` when applicable
- `DECISIONS_FILE` when applicable

Interpret the result:

- `PREP: PASS` -> continue with the returned brief path
- `PREP: FAIL` -> stop and surface the dependency or ambiguity to the user
- `PREP: BLOCKED` -> stop and surface the missing prerequisite artifact
- `PREP: ERROR` -> stop and ask the user how to proceed

### 2. Dispatch `execution-planner`

Inputs:

- `BRIEF_FILE`
- `DECISIONS_FILE` when applicable

Interpret the result:

- `PLAN: PASS` -> continue with the returned plan path
- `PLAN: FAIL` -> stop and surface the ambiguity or planning gap
- `PLAN: BLOCKED` -> stop and surface the missing input artifact
- `PLAN: ERROR` -> stop and ask the user how to proceed

### 3. Dispatch `test-strategist`

Inputs:

- `BRIEF_FILE`
- `PLAN_FILE`
- `DECISIONS_FILE` when applicable

Interpret the result:

- `TEST_SPEC: PASS` -> continue with the returned spec path
- `TEST_SPEC: FAIL` -> stop and surface the behavior gap
- `TEST_SPEC: BLOCKED` -> stop and surface the missing input artifact
- `TEST_SPEC: ERROR` -> stop and ask the user how to proceed

### 4. Dispatch `refactoring-advisor`

Inputs:

- `BRIEF_FILE`
- `PLAN_FILE`
- `TEST_SPEC_FILE`
- `DECISIONS_FILE` when applicable

Interpret the result:

- `REFACTORING: PASS` -> planning is complete
- `REFACTORING: FAIL` -> stop and surface the ambiguity or risk
- `REFACTORING: BLOCKED` -> stop and surface the missing input artifact
- `REFACTORING: ERROR` -> stop and ask the user how to proceed

### 5. Report completion

Return a short summary containing:

- Task number and title
- The four artifact paths
- One or two sentences on the recommended approach
- The number or shape of tests specified
- The refactoring verdict

## Re-Plan Rules

Use targeted reruns instead of replaying the entire pipeline by default.

- If critique changes task scope, definition of done, resolved questions, or the
  brief's task context, rerun `execution-prepper` and every downstream subagent.
- If critique changes implementation approach, file strategy, or recommended
  skills, rerun `execution-planner`, `test-strategist`, and
  `refactoring-advisor`.
- If critique changes only test expectations, rerun `test-strategist`, then
  rerun `refactoring-advisor` only if the testing change affects its advice.
- If critique changes only refactoring guidance, rerun `refactoring-advisor`
  alone.

Whenever a subagent is re-run:

- Pass `DECISIONS_FILE`
- Let the subagent read its existing artifact if it needs prior context
- Overwrite only that subagent's owned file
- Re-run any downstream artifact that now depends on the updated output

Maximum re-plan loops: 3. If critique still reports unresolved high-severity
issues after the third loop, escalate to the user with the remaining concerns.
