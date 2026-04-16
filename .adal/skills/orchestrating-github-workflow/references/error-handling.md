# Error Handling and Resumability

> Read this file when something goes wrong, or when resuming a previously
> interrupted workflow.
>
> Reminder: keep the orchestrator at summary level. Record the failure state,
> present the decision, and re-dispatch the relevant skill or subagent instead
> of pulling raw execution details into context.

---

## Error Response Table

When errors occur, the orchestrator's response depends on the type and
severity. The guiding principle: surface failures immediately and let progress
files handle recovery.

| Error                               | Response                                                                                                                                                                               | Example                                                                               |
| ----------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| **Skill failure**                   | Record via `progress-tracker` with `STATUS=failed` using `ACTION=update` for phases 1-4 or `ACTION=update_task` for phases 5-7. Report to user with options: retry the phase, skip it, or abort the workflow. | Phase 2 planning skill crashes mid-execution.                                         |
| **Missing artifact**                | `artifact-validator` reports FAIL → do not proceed. Tell the user which phase needs to run or re-run, and offer to run it.                                                             | `docs/<ISSUE_SLUG>-tasks.md` missing before Phase 3.                                  |
| **`gh` / GitHub unavailable**       | Tell the user to run `gh auth login`, fix network or token scopes, or restore API access. Offer to resume when ready. The workflow pauses — it does not fail.                          | `gh` not authenticated between Phase 3 and Phase 4.                                   |
| **Subagent failure (non-critical)** | Proceed without the result. Non-critical subagents are utilities that provide context but are not required for phase advancement.                                                      | `documentation-finder` returns an error — planning can continue without docs context. |
| **Subagent failure (critical)**     | Halt the phase. Critical subagents produce results required for the next step.                                                                                                         | `artifact-validator` fails — cannot determine whether to advance.                     |
| **User interruption**               | Progress files ensure resumability. Tell the user: "Say 'resume issue <ISSUE_SLUG>' or provide the issue URL to pick up where we left off."                                               | User closes the IDE mid-Phase 5.                                                      |
| **Quality gate failure**            | Handled internally by `executing-github-task` via targeted fix cycles. The orchestrator only acts if the fix cycle limit (3 attempts) is exhausted — then escalate to user with options. | All 3 fix cycles fail on clean-code-reviewer.                                         |
| **Execution kickoff blocker**       | Handled initially inside `executing-github-task`. If kickoff reports the workspace or GitHub state is not safely ready, stop before implementation and present the blocker to the user. | Phase 7 kickoff finds a dirty worktree that needs user direction.                     |
| **Phase 7 capability blocker**      | If `task-executor`, `documentation-writer`, or `requirements-verifier` reports `BLOCKED` because a required tool, runtime, permission, credential, or environment capability is unavailable, stop the task and present the blocker to the user as a steering decision. Do not treat it as an ordinary implementation gap or silently skip the blocked work. Resume from the blocked Phase 7 step after the capability is restored. | Task execution requires Docker, but the Docker CLI is unavailable.                     |
| **Execution-skill ambiguity**      | `executing-github-task` stops and reports back. Resolve the ambiguity with the user, update the execution brief, and re-dispatch. Max 3 retry cycles.                                   | Executor encounters conflicting requirements in the brief.                            |
| **Re-plan cycle exhausted**         | After 3 re-plan iterations (Phase 3→2 or Phase 6→5), present accumulated critique to the user and ask how to proceed.                                                                  | Phase 3 keeps triggering re-plans due to fundamental disagreement on approach.        |

### Distinguishing critical from non-critical subagents

| Critical (halt on failure)                | Non-critical (proceed without)             |
| ----------------------------------------- | ------------------------------------------ |
| `artifact-validator`                      | `documentation-finder`                     |
| `progress-tracker`                        | `code-reference-finder`                    |
| `preflight-checker`                       | `codebase-inspector`                       |
| `issue-status-checker` (Phase 1/4 only)   | `issue-status-checker` (pre-task context)  |

The same subagent can be critical or non-critical depending on context. When
dispatched as part of the phase execution cycle (validate preconditions /
postconditions), `artifact-validator` is always critical. When
`issue-status-checker` is dispatched for pre-task context gathering, it is
non-critical — the task can proceed without fresh GitHub status.

---

## Resumability

The workflow can be interrupted and resumed at any point. Two levels of
progress files maintain state:

- `docs/<ISSUE_SLUG>-progress.md` — workflow-level (phases 1–4 + task summary table)
- `docs/<ISSUE_SLUG>-task-<N>-progress.md` — per-task (phases 5–7 for each task)

### Resume procedure

1. **Read progress.** Dispatch `progress-tracker` with `ACTION=read`:

   ```
   ISSUE_SLUG: <slug>
   ACTION: read
   ```

2. **Determine starting phase** from the progress summary:

   | Progress indicates                           | Resume from         |
   | -------------------------------------------- | ------------------- |
   | No artifacts found                           | Phase 1             |
   | Phase 1 complete, Phase 2 not started        | Phase 2             |
   | Phases 1–2 complete, Phase 3 not done        | Phase 3             |
   | Phases 1–3 complete, Phase 4 not done        | Phase 4             |
   | Phases 1–4 complete, no tasks started        | Phase 5 (pick task) |
   | Task N at Phase 5 complete, Phase 6 not done | Phase 6, Task N     |
   | Task N at Phase 6 complete, Phase 7 not done | Phase 7, Task N     |
   | Task N complete, other tasks remaining       | Phase 5 (pick task) |

3. **Run preflight for the actual remaining phases.** After you know the
   starting phase, dispatch `preflight-checker` only for that phase onward.
   Dependencies for already-completed phases do not need re-checking.

4. **Inform and confirm.** Tell the user what was found and which phase will
   start. If resuming past Phase 1, ask for confirmation before proceeding.

<example>
Resume scenario:

progress-tracker returns:
"Phases: 1 ✅ | 2 ✅ | 3 ✅ | 4 ✅
Tasks: 1/3 complete | Task 2: Phase 5 (Plan) 🔄
Resume from: Phase 5, Task 2"

Orchestrator to user:
"Found existing progress for acme-app-42. Phases 1–4 are complete (3 tasks
planned). Task 1 is done. Task 2 was in progress at Phase 5 (planning).
Shall I resume from Phase 5 for Task 2?"
</example>

5. **Load the right reference file.** Based on the starting phase:

   | Starting at | Read              |
   | ----------- | ----------------- |
   | Phase 1–4   | `./phases-1-4.md` |
   | Phase 5–7   | `./task-loop.md`  |
