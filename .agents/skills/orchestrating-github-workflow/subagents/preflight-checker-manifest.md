# Preflight Checker — Dependency Manifest

> This file contains the full dependency manifest for the preflight checker.
> Read this when performing a preflight check to know exactly what to verify.
>
> Reminder: preflight reports availability only. It does not install, connect,
> or repair dependencies.

---

## Classification

All dependencies are **Required**. A passing preflight verifies that every
requested dependency is available, with `UNKNOWN` reserved only for inherently
ambiguous checks. Any requested dependency confirmed as `MISSING` produces a
`FAIL` verdict. There is no optional/recommended tier. This is enforced both
here (preflight) and by each subagent at runtime (defense-in-depth).

---

## Phase 1 — Fetch (`fetching-github-issue`)

| Dependency              | Type  | Used by               | How to check                                      | Install / configure                          |
| ----------------------- | ----- | --------------------- | ------------------------------------------------- | ------------------------------------------ |
| GitHub CLI (`gh`)       | Tool  | issue fetch / API     | `gh --version`; for auth: `gh auth status`        | Install `gh` and run `gh auth login`       |
| `fetching-github-issue` | Skill | Phase 1 orchestration | `skills/…/fetching-github-issue/SKILL.md` exists | Add skill at expected repo path            |

---

## Phase 2 — Plan (`planning-github-issue-tasks`)

| Dependency                   | Type  | Used by                              | How to check                                        | Install / configure                             |
| ---------------------------- | ----- | ------------------------------------ | --------------------------------------------------- | ----------------------------------------------- |
| `/writing-plans`             | Skill | task-planner, dependency-prioritizer | Run `/find-skills writing-plans` or check skill dir | `skills install obra/superpowers/writing-plans` |
| `planning-github-issue-tasks` | Skill | Phase 2 orchestration                | `skills/…/planning-github-issue-tasks/SKILL.md` exists | Add skill at expected repo path                 |

---

## Phase 3 — Clarify (`clarifying-assumptions`, upfront)

| Dependency                 | Type  | Used by               | How to check                                   | Install / configure         |
| -------------------------- | ----- | --------------------- | ---------------------------------------------- | --------------------------- |
| `clarifying-assumptions`   | Skill | Phase 3 orchestration | `skills/.../clarifying-assumptions/SKILL.md` exists | Add skill at expected repo path |

No external dependencies beyond the skill file. Conversational skill; inline
execution.

---

## Phase 4 — Create task issues (`creating-github-child-issues`)

| Dependency                   | Type  | Used by               | How to check                                      | Install / configure                    |
| ---------------------------- | ----- | --------------------- | ------------------------------------------------- | -------------------------------------- |
| GitHub CLI (`gh`)            | Tool  | creates/links issues  | Same as Phase 1                                   | Same as Phase 1                        |
| `creating-github-child-issues` | Skill | Phase 4 orchestration | `skills/…/creating-github-child-issues/SKILL.md` exists | Add skill at expected repo path    |

---

## Phase 5 — Plan task (`planning-github-task`)

| Dependency               | Type  | Used by                                                 | How to check                                                  | Install / configure                                       |
| ------------------------ | ----- | ------------------------------------------------------- | ------------------------------------------------------------- | --------------------------------------------------------- |
| git CLI                  | Tool  | branch / workspace inspection                           | Run `git --version`                                           | Install git                                               |
| `/find-skills`           | Skill | execution-planner                                       | Try invoking `/find-skills` with a test query                 | `skills install vercel-labs/skills/find-skills`           |
| `/writing-plans`         | Skill | execution-planner, test-strategist, refactoring-advisor   | Run `/find-skills writing-plans` or check skill dir           | `skills install obra/superpowers/writing-plans`           |
| `/test-driven-development` | Skill | test-strategist                                       | Run `/find-skills test-driven-development` or check skill dir | `skills install obra/superpowers/test-driven-development` |
| `/vitest`                | Skill | test-strategist                                         | Run `/find-skills vitest` or check skill dir                  | `skills install antfu/skills/vitest`                      |
| `planning-github-task`   | Skill | Phase 5 orchestration                                   | `skills/…/planning-github-task/SKILL.md` exists                 | Add skill at expected repo path                           |

---

## Phase 6 — Clarify + critique (`clarifying-assumptions`, critique mode)

| Dependency                 | Type  | Used by               | How to check                                   | Install / configure         |
| -------------------------- | ----- | --------------------- | ---------------------------------------------- | --------------------------- |
| `clarifying-assumptions`   | Skill | Phase 6 orchestration | `skills/.../clarifying-assumptions/SKILL.md` exists | Add skill at expected repo path |

No external dependencies beyond the skill. Conversational skill with inline
helper dispatch.

---

## Phase 7 — Kick off + execute (`executing-github-task`)

| Dependency                   | Type  | Used by                | How to check                                                      | Install / configure                                                             |
| ---------------------------- | ----- | ---------------------- | ----------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| GitHub CLI (`gh`)            | Tool  | issue state / comments | Same as Phase 1 when execution mutates GitHub                     | Same as Phase 1                                                                 |
| `executing-github-task`      | Skill | Phase 7 orchestration  | `skills/…/executing-github-task/SKILL.md` exists                    | Add skill at expected repo path                                                 |
| `/commit-work`               | Skill | documentation-writer   | Run `/find-skills commit-work` or check skill dir                 | `skills install softaworks/agent-toolkit/commit-work`                           |
| `/humanizer`                 | Skill | documentation-writer   | Run `/find-skills humanizer` or check skill dir                   | `skills install blader/humanizer`                                               |
| `/executing-plans`           | Skill | task-executor          | Run `/find-skills executing-plans` or check skill dir             | `skills install obra/superpowers/executing-plans`                               |
| `/clean-code`                | Skill | clean-code-reviewer    | Run `/find-skills clean-code` or check skill dir                  | `skills install sickn33/antigravity-awesome-skills/clean-code`                  |
| `/architecture-patterns`     | Skill | architecture-reviewer  | Run `/find-skills architecture-patterns` or check skill dir       | `skills install wshobson/agents/architecture-patterns`                          |
| `/api-security-best-practices` | Skill | security-auditor     | Run `/find-skills api-security-best-practices` or check skill dir | `skills install sickn33/antigravity-awesome-skills/api-security-best-practices` |

`context7` is **recommended but not required** for Phase 7 review quality. The
reviewers are written to use it when available and to lower confidence when it
is not. Do not fail preflight solely because `context7` is unavailable.

---

## Quick Reference — All Dependencies

| Dependency                    | Type  | Phase(s) |
| ----------------------------- | ----- | -------- |
| GitHub CLI (`gh`)             | Tool  | 1, 4, 7  |
| `fetching-github-issue`       | Skill | 1        |
| `/writing-plans`              | Skill | 2, 5     |
| `planning-github-issue-tasks` | Skill | 2        |
| `clarifying-assumptions`   | Skill | 3, 6     |
| `creating-github-child-issues`| Skill | 4        |
| git CLI                       | Tool  | 5        |
| `/find-skills`                | Skill | 5        |
| `/test-driven-development`    | Skill | 5        |
| `/vitest`                     | Skill | 5        |
| `planning-github-task`        | Skill | 5        |
| `executing-github-task`       | Skill | 7        |
| `/commit-work`                | Skill | 7        |
| `/humanizer`                  | Skill | 7        |
| `/executing-plans`            | Skill | 7        |
| `/clean-code`                 | Skill | 7        |
| `/architecture-patterns`      | Skill | 7        |
| `/api-security-best-practices`| Skill | 7        |

**Note:** `gh` appears once per phase group in tables above; count it as a
single logical dependency in summaries (dedupe when reporting `Available` /
`Missing` counts).
