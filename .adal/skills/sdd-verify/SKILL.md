---
name: sdd-verify
description: >
  Verifies that the implementation complies with the specs, design, and task plan. Produces verify-report.md.
  Trigger: /sdd-verify <change-name>, verify implementation, quality gate, validate change.
format: procedural
model: sonnet
metadata:
  version: "3.0"
---

# sdd-verify

> Verifies that the implementation complies with the specs, design, and task plan.

**Triggers**: `/sdd-verify <change-name>`, verify implementation, quality gate, validate change, sdd verify

---

### Step 0 — Load project context + Spec context preload

Follow `skills/_shared/sdd-phase-common.md` **Section F** (Project Context Load) and **Section G** (Spec Context Preload). Both are non-blocking.

---

## Purpose

Verification is the **quality gate** before archiving. It objectively validates that what was implemented meets what was specified. It fixes nothing — it only reports.

---

## Process

### Skill Resolution

When the orchestrator launches this sub-agent, it resolves the skill path using:

```
1. .claude/skills/sdd-verify/SKILL.md     (project-local — highest priority)
2. ~/.claude/skills/sdd-verify/SKILL.md   (global catalog — fallback)
```

Project-local skills override the global catalog. See `docs/SKILL-RESOLUTION.md` for the full algorithm.

---

### Step 1 — Load all artifacts

I read:

- The tasks artifact — what was planned:
  - `mem_search(query: "sdd/{change-name}/tasks")` → `mem_get_observation(id)`.
  - If not found and Engram not reachable: tasks content passed inline from orchestrator.
- The spec artifact — what was required:
  - `mem_search(query: "sdd/{change-name}/spec")` → `mem_get_observation(id)`.
  - If not found and Engram not reachable: spec content passed inline from orchestrator.
- The design artifact — how it was designed:
  - `mem_search(query: "sdd/{change-name}/design")` → `mem_get_observation(id)`.
  - If not found and Engram not reachable: design content passed inline from orchestrator.
- The code files that were created/modified

### Step 2 — Completeness Check (Tasks)

I count total tasks vs completed tasks:

```markdown
### Completeness

| Metric               | Value |
| -------------------- | ----- |
| Total tasks          | [N]   |
| Completed tasks [x]  | [M]   |
| Incomplete tasks [ ] | [K]   |

Incomplete tasks:

- [ ] [number and description of each one]
```

**Severity:**

- Incomplete core logic tasks → CRITICAL
- Incomplete cleanup/docs tasks → WARNING

### Step 3 — Correctness Check (Specs)

For EACH requirement in the spec.md files:

1. I look for evidence in the code that it is implemented
2. For EACH Given/When/Then scenario:
   - Is the GIVEN handled? (precondition/guard)
   - Is the WHEN implemented? (the action/endpoint)
   - Is the THEN verifiable? (the correct result)

```markdown
### Correctness (Specs)

| Requirement | Status             | Notes                                 |
| ----------- | ------------------ | ------------------------------------- |
| [Req 1]     | ✅ Implemented     |                                       |
| [Req 2]     | ⚠️ Partial         | Missing 401 error scenario            |
| [Req 3]     | ❌ Not implemented | Endpoint /auth/refresh does not exist |

### Scenario Coverage

| Scenario                           | Status                               |
| ---------------------------------- | ------------------------------------ |
| Successful login                   | ✅ Covered                           |
| Failed login — incorrect password  | ✅ Covered                           |
| Failed login — user does not exist | ⚠️ Partial — implemented but no test |
| Expired token                      | ❌ Not covered                       |
```

### Step 4 — Coherence Check (Design)

I verify that the design decisions were followed:

```markdown
### Coherence (Design)

| Decision            | Followed?    | Notes                                       |
| ------------------- | ------------ | ------------------------------------------- |
| Validation with Zod | ✅ Yes       |                                             |
| JWT with RS256      | ⚠️ Deviation | HS256 was used. Dev documented it in tasks. |
| Repository pattern  | ✅ Yes       |                                             |
```

### Step 5 — Testing Check

```markdown
### Testing

| Area                | Tests Exist | Scenarios Covered |
| ------------------- | ----------- | ----------------- |
| AuthService.login() | ✅ Yes      | 3/4 scenarios     |
| AuthController      | ✅ Yes      | Happy paths only  |
| JWT Middleware      | ❌ No       | —                 |
```

### Step 6 — Run Tests

I resolve test commands using a three-level priority model. I check `config.yaml (at project root)` in order:

**Level 1 — `verify_commands` config key (highest priority — checked first):**

```
if config.yaml (at project root) exists and has key verify_commands:
    → use the listed commands in order
    → do NOT check level 2 or run auto-detection
    → for each command:
         run the command via Bash tool
         capture exit code + stdout/stderr
         record in ## Tool Execution section with source label "verify_commands (config level 1)"
    → skip levels 2 and 3 entirely
else:
    → proceed to level 2 check
```

When `verify_commands` is present, it overrides all lower levels — it is NOT additive.
Commands are assumed non-destructive; the user is responsible for this.

**Level 2 — `verify.test_commands` config key (checked when verify_commands is absent):**

```
if config.yaml (at project root) exists and has key verify.test_commands:
    if verify.test_commands is not a list:
        → emit WARNING: "verify.test_commands is not a list — treating as absent"
        → proceed to level 3 (auto-detection)
    else if verify.test_commands is an empty list []:
        → treat as absent (empty list falls through — prevents silent zero-command success)
        → proceed to level 3 (auto-detection)
    else:
        → use the listed commands in order
        → do NOT run auto-detection
        → for each command:
             run the command via Bash tool
             capture exit code + stdout/stderr
             record in ## Tool Execution section with source label "verify.test_commands (config level 2)"
        → skip level 3 entirely
else:
    → proceed to level 3 (auto-detection)
```

**Level 3 — Auto-detection (only when both `verify_commands` and `verify.test_commands` are absent or invalid — prioritized — use the first match):**

| Priority | File to check                                 | Condition                 | Command                                                                                   |
| -------- | --------------------------------------------- | ------------------------- | ----------------------------------------------------------------------------------------- |
| 1        | `package.json`                                | `scripts.test` exists     | `npm test` (or `yarn test` if `yarn.lock` exists, `pnpm test` if `pnpm-lock.yaml` exists) |
| 2        | `pyproject.toml` / `pytest.ini` / `setup.cfg` | pytest indicators present | `pytest`                                                                                  |
| 3        | `Makefile`                                    | `test` target exists      | `make test`                                                                               |
| 4        | `build.gradle` / `gradlew`                    | file exists               | `./gradlew test`                                                                          |
| 5        | `mix.exs`                                     | file exists               | `mix test`                                                                                |
| —        | none of the above                             | —                         | **Skip** with WARNING                                                                     |

**Execution:**

1. I execute the detected command via Bash tool
2. I capture the exit code (0 = pass, non-zero = failure)
3. I capture stdout/stderr output for analysis
4. I record: runner name, command executed, exit code, summary of failures (if any)

**Error handling:**

- If the command cannot be executed (missing dependencies, command not found): I report "Test Execution: ERROR — [error message]" with status WARNING and continue to subsequent steps
- If tests run but some fail: I report the failure count and list failing test names if parseable from the output
- If no test runner is detected: I report "Test Execution: SKIPPED — no test runner detected" with status WARNING

I save the full test output for use in Step 8 (Coverage Validation) and Step 9 (Spec Compliance Matrix).

### Step 7 — Build & Type Check

I detect the project's build/type-check command and execute it.

**Config override check — `verify.build_command` and `verify.type_check_command` (checked before auto-detection):**

```
if config.yaml (at project root) exists and has key verify.build_command:
    if verify.build_command is not a string:
        → emit WARNING: "verify.build_command is not a string — treating as absent"
        → proceed to auto-detection for build command
    else:
        → use verify.build_command as the build/type-check command
        → skip the auto-detection table below for the build/type-check command

if config.yaml (at project root) exists and has key verify.type_check_command:
    if verify.type_check_command is not a string:
        → emit WARNING: "verify.type_check_command is not a string — treating as absent"
        → proceed to auto-detection for type check command
    else:
        → use verify.type_check_command as the type-check command
        → skip auto-detection for type check command
```

When either config override is present and valid, it replaces the corresponding auto-detected command.
Both overrides are independent — one can be set without the other.

**Build command auto-detection (only when `verify.build_command` is absent or invalid — prioritized — use the first match):**

| Priority | File to check              | Condition                                   | Command                            |
| -------- | -------------------------- | ------------------------------------------- | ---------------------------------- |
| 1        | `package.json`             | `scripts.typecheck` exists                  | `npm run typecheck`                |
| 2        | `package.json`             | `scripts.build` exists                      | `npm run build`                    |
| 3        | `tsconfig.json`            | file exists + TypeScript in devDependencies | `npx tsc --noEmit`                 |
| 4        | `Makefile`                 | `build` target exists                       | `make build`                       |
| 5        | `build.gradle` / `gradlew` | file exists                                 | `./gradlew build`                  |
| 6        | `mix.exs`                  | file exists                                 | `mix compile --warnings-as-errors` |
| —        | none of the above          | —                                           | **Skip** with INFO                 |

**Execution:**

1. I execute the detected command via Bash tool
2. I capture the exit code (0 = pass, non-zero = failure)
3. I capture error output for analysis
4. I record: command executed, exit code, error summary (if any)

**Error handling:**

- If the command cannot be executed: I report "Build/Type Check: ERROR — [error message]" with status WARNING and continue
- If the build fails: I report "Build/Type Check: FAILING" and include error output in the detail section
- If no build command is detected: I report "Build/Type Check: SKIPPED — no build command detected" with status INFO (not WARNING)

### Step 8 — Coverage Validation (optional)

This step is **only active** when a coverage threshold is configured. It is advisory only — it never produces CRITICAL status and never blocks verification.

**Process:**

1. I read `config.yaml (at project root)` and look for `coverage.threshold` (e.g., `coverage: { threshold: 80 }`)
2. **If no threshold is configured**: I skip this step entirely and report "Coverage Validation: SKIPPED — no threshold configured"
3. **If a threshold is configured**:
   a. I parse the coverage percentage from the Step 6 test output (looking for common coverage summary formats)
   b. I compare the actual coverage against the configured threshold
   c. I report the result:
   - Actual >= threshold: "Coverage: [X]% (threshold: [Y]%) — PASS"
   - Actual < threshold: "Coverage: [X]% (threshold: [Y]%) — BELOW THRESHOLD" with status WARNING
4. **If coverage data cannot be parsed** from the test output: I report "Coverage Validation: SKIPPED — could not parse coverage from test output" with status WARNING

### Step 9 — Spec Compliance Matrix

I produce a Spec Compliance Matrix that cross-references every Given/When/Then scenario from the change's spec files against the verification evidence.

**Process:**

1. I read all spec content from the active persistence mode (same source as Step 1)
2. For each spec file, I extract every Given/When/Then scenario
3. For each scenario, I cross-reference against:
   - **Code implementation evidence** from Step 3 (Correctness Check)
   - **Test results** from Step 6 (Run Tests) — if tests were executed
4. I assign a compliance status per scenario:

| Status        | Meaning                          | Criteria                                                                                                           |
| ------------- | -------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| **COMPLIANT** | Fully implemented and verified   | Code implements the scenario + test passes (or code inspection confirms correctness when no test runner exists)    |
| **FAILING**   | Implemented but test fails       | Code implements the scenario + corresponding test fails                                                            |
| **UNTESTED**  | Implemented but no test coverage | Code implements the scenario + no test covers this scenario (only when a test runner exists but no test covers it) |
| **PARTIAL**   | Partially implemented            | Code covers some but not all THEN/AND clauses of the scenario                                                      |

**When no test runner exists:**

- The matrix is still produced using code inspection evidence from Step 3
- Scenarios verified only by code inspection receive COMPLIANT or PARTIAL (never UNTESTED, since code evidence was checked)

**Output format:**

```markdown
## Spec Compliance Matrix

| Spec Domain | Requirement        | Scenario        | Status    | Evidence                                      |
| ----------- | ------------------ | --------------- | --------- | --------------------------------------------- |
| [domain]    | [requirement name] | [scenario name] | COMPLIANT | [evidence description]                        |
| [domain]    | [requirement name] | [scenario name] | FAILING   | [failing test name or output]                 |
| [domain]    | [requirement name] | [scenario name] | UNTESTED  | No test coverage found                        |
| [domain]    | [requirement name] | [scenario name] | PARTIAL   | [which clauses are covered and which are not] |
```

The matrix MUST include scenarios from ALL spec domains affected by the change.

### Step 10 — Create verify-report.md

**Evidence rule — applies to every criterion in `verify-report.md`:**

A criterion MUST only be marked `[x]` when:
1. A tool command was run and its output confirms the criterion, OR
2. The user provided an explicit evidence statement

When neither condition is met: leave `[ ]` with note: "Manual confirmation required — no tool output available".
Abstract reasoning or code inspection alone MUST NOT suffice to mark a criterion `[x]`.

**The `## Tool Execution` section is mandatory in every `verify-report.md` — even when tool execution was skipped.** When skipped, the section MUST still appear with: "Test Execution: SKIPPED — no test runner detected".

I persist the verify report to engram:

Call `mem_save` with `topic_key: sdd/{change-name}/verify-report`, `type: architecture`, `project: {project}`, content = full report markdown. Do NOT write any file.

If Engram MCP is not reachable: skip persistence. Return report content inline only.

**Persisted artifact** (compact — only what sdd-archive and the orchestrator consume):

```markdown
# Verification Report: [change-name]

Date: [YYYY-MM-DD]
Verdict: PASS / PASS WITH WARNINGS / FAIL

## Summary
| Dimension | Status |
|---|---|
| Completeness | OK / WARNING / CRITICAL |
| Correctness | OK / WARNING / CRITICAL |
| Coherence | OK / WARNING / CRITICAL |
| Testing | OK / WARNING / CRITICAL |
| Test Execution | OK / WARNING / CRITICAL / SKIPPED |
| Build | OK / WARNING / SKIPPED |

## Tool Execution
| Command | Exit Code | Result |
|---|---|---|
| [command] | [code] | [PASS/FAIL/SKIPPED] |

## Issues

### CRITICAL
- [issue description]
[or: "None."]

### WARNINGS
- [issue description]
[or: "None."]
```

**Conversational output** (shown to user but NOT persisted):

The full detail sections — Completeness tables, Correctness requirement-by-requirement tables, Coherence decision tracking, Testing coverage tables, Spec Compliance Matrix, Coverage Validation, and SUGGESTIONS — are presented in the conversational response. This gives the user full visibility without inflating the persisted artifact.

The conversational output MUST still include all detail sections from Steps 2-9 — the user needs to see the full analysis. Only the **persisted artifact** is compact.

### WARNINGS (should be resolved):

- [description]
  [or: "None."]

### SUGGESTIONS (optional improvements):

- [description]
  [or: "None."]
```

---

## Verdict Criteria

| Verdict                | Condition               |
| ---------------------- | ----------------------- |
| **PASS**               | 0 critical, 0 warnings  |
| **PASS WITH WARNINGS** | 0 critical, 1+ warnings |
| **FAIL**               | 1+ critical             |

---

## Severities

| Severity       | Description                                                                                                       | Blocks archiving |
| -------------- | ----------------------------------------------------------------------------------------------------------------- | ---------------- |
| **CRITICAL**   | Requirement not implemented, main scenario not covered, core task incomplete                                      | Yes              |
| **WARNING**    | Edge case scenario without test, design deviation, pending cleanup task, test execution failure                   | No               |
| **SUGGESTION** | Optional quality improvement                                                                                      | No               |
| **SKIPPED**    | Step preconditions not met (no test runner, no build command, no coverage config) — does NOT count toward verdict | No               |
| **INFO**       | Informational note (e.g., no build command detected) — does NOT count toward verdict                              | No               |

**Verdict calculation note:** Only the original four dimensions (Completeness, Correctness, Coherence, Testing) plus Test Execution and Spec Compliance contribute CRITICAL/WARNING statuses. SKIPPED and INFO statuses from any dimension do NOT count as WARNING or CRITICAL for the verdict. This preserves identical verdict behavior for projects without test infrastructure.

---

## Output to Orchestrator

```json
{
  "status": "ok|warning|failed",
  "summary": "Verification [change-name]: [verdict]. [N] critical, [M] warnings.",
  "artifacts": ["engram:sdd/{change-name}/verify-report"],
  "test_execution": {
    "runner": "[detected runner or null]",
    "command": "[command or null]",
    "exit_code": "[0/1/N or null]",
    "result": "PASS|FAILING|ERROR|SKIPPED"
  },
  "build_check": {
    "command": "[command or null]",
    "exit_code": "[0/1/N or null]",
    "result": "PASS|FAILING|ERROR|SKIPPED"
  },
  "compliance_matrix": {
    "total_scenarios": "[N]",
    "compliant": "[N]",
    "failing": "[N]",
    "untested": "[N]",
    "partial": "[N]"
  },
  "next_recommended": ["sdd-archive (if PASS or PASS WITH WARNINGS)"],
  "risks": ["CRITICAL: [description if any]"]
}
```

Continue with archive? Reply **yes** to proceed or **no** to pause.
_(Manual: `/sdd-archive <slug>`)_

---

## Rules

- I ONLY report — I fix nothing during verification
- I read real code — I do not assume something works just because the file exists
- I am objective: I report what IS, not what should be
- If there are deviations documented in tasks.md, I evaluate them with context
- A FAIL is not personal — it is information for improvement
- I run tests if possible (via Bash tool): I report the actual results
- The `## Tool Execution` section is mandatory in every `verify-report.md` — even when skipped; when skipped it MUST state "Test Execution: SKIPPED — no test runner detected"
- A criterion marked `[x]` MUST have verifiable evidence: tool output or an explicit user evidence statement; abstract reasoning or code inspection alone MUST NOT suffice
- Test command resolution uses a three-level priority model: level 1 (`verify_commands`) > level 2 (`verify.test_commands`) > level 3 (auto-detection); each level is only consulted when all higher levels are absent or invalid
- Empty `verify.test_commands: []` falls through to auto-detection — it is NOT treated as zero-command success
- `verify.build_command` and `verify.type_check_command` override their respective auto-detected commands when present and are strings; non-string values emit a WARNING and fall back to auto-detection
