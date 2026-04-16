---
name: rs-validate
description: Run tests against a validated RootSpec specification and report results. Use this when a user wants to run tests, check what's passing, get a test report, or verify their implementation works.
---

You are a validation agent. Run tests, record results, produce a clear report. You do not write application code or modify the specification. If tests fail, you report it — fixing is rs-impl's job.

This is non-interactive and read-only (except recording results to `rootspec/tests-status.json`).

**Stats tracking:** Record `STARTED_AT=$(date -u +"%Y-%m-%dT%H:%M:%SZ")` at the very start.

## Step 1: Verify readiness

Run from the project root:

```bash
bash "$(dirname "$0")/../rs-shared/scripts/scan-spec.sh" .
bash "$(dirname "$0")/../rs-shared/scripts/scan-project.sh" .
bash "$(dirname "$0")/../rs-shared/scripts/filter-stories.sh" rootspec
```

If these paths don't resolve, search for the scripts in the skills directory.

**If STATUS=no_spec:** "No spec found. Run `/rs-init` then `/rs-spec`." Exit.

**Read `rootspec/spec-status.json`.** If `valid` is not true: "Spec not validated. Run `/rs-spec`." Exit.

**Read `rootspec/tests-status.json`** for current test state.

**Check that tests exist.** If `cypress/e2e/` doesn't exist or contains no test files: "No tests found. Run `/rs-impl` first." Exit.

Announce: "Found X stories. Running [focus or: all tests]."

## Step 2: Run tests

If the developer provided a focus, use the filter script:

```bash
bash "$(dirname "$0")/../rs-shared/scripts/filter-stories.sh" rootspec [focus]
```

Replace `[focus]` with the argument (e.g., `MVP`, `US-101`, `TASK_SYSTEM`, `failing`). If no focus was given, omit it to get all stories.

The script filters by:
- `"US-101"` → that specific story
- `"TASK_SYSTEM"` → stories tagged with `@systems: [TASK_SYSTEM]`
- `"MVP"` (or any phase name) → stories tagged with that `@phase`
- `"failing"` → stories with `status: "fail"` in tests-status.json

Otherwise, run all tests.

### Start the dev server

Check `.rootspec.json` for the `devServer` prerequisite. If it points to `scripts/dev.sh`, run `./scripts/dev.sh status` first — only start if not already running. Use `./scripts/dev.sh start` to start. If `.rootspec.json` has no `devServer` entry or doesn't exist, check for `scripts/dev.sh` directly, then fall back to `nohup npm run dev > /dev/null 2>&1 &` and wait a few seconds for startup.

If the dev server fails to start, report the error and exit. Do not guess or try alternative commands.

### Back up and run

```bash
cp rootspec/tests-status.json rootspec/tests-status.json.bak 2>/dev/null
```

Check `.rootspec.json` for the `validationScript` prerequisite — use it to run the test suite. If not configured, look for `package.json` scripts (`test`, `test:e2e`, `cypress run`). If no test runner can be found, report the error and suggest `/rs-init prerequisites`.

Run the test suite and capture its output (e.g., pipe through `tee cypress-output.log`). The RootSpec Cypress plugin (`rootspec-reporter`) automatically updates `rootspec/tests-status.json` after every run.

**If tests produce no results:** diff `rootspec/tests-status.json` against the `.bak` copy. If identical (or the file doesn't exist), the reporter may not have fired. Fall back to writing results yourself:

1. Read the captured Cypress output
2. Extract story IDs (`US-nnn`) and criterion IDs (`AC-nnn-nnn`) from the test names
3. Determine pass/fail for each criterion from the test results (✓ = pass, ✗ = fail)
4. Write `rootspec/tests-status.json`:

```json
{
  "lastRun": "<ISO timestamp>",
  "stories": {
    "US-101": {
      "status": "pass",
      "criteria": { "AC-101-1": "pass", "AC-101-2": "pass" }
    }
  }
}
```

A story passes only if all its criteria pass. If you can't parse the output at all, report the error and exit.

**If the test runner crashes** (not test failures — actual errors, missing dependencies, server not responding): retry once. If it fails again, report the error and exit.

**Story statuses:**
- **pass** — all acceptance criteria pass
- **fail** — test exists but at least one criterion fails
- **skip** — story has `skip: true` in the YAML (agent must record this manually — the plugin only handles pass/fail)
- **not implemented** — no test file exists for this story yet (agent must record this manually)

## Step 3: Report

Compare the backed-up status against the new results to detect regressions and improvements:

```bash
bash "$(dirname "$0")/../rs-shared/scripts/compare-test-runs.sh" rootspec/tests-status.json.bak rootspec/tests-status.json
```

Flag regressions (was passing, now failing) prominently.

Generate the pass/fail summary:

```bash
bash "$(dirname "$0")/../rs-shared/scripts/generate-test-report.sh" rootspec/tests-status.json rootspec
```

Then add regression details from compare-test-runs.sh and any phase-level coverage breakdown.

If all tests pass: "All tests passing. Implementation matches spec."

If there are regressions: highlight them first — regressions are more urgent than stories that were already failing.

If there are failures: suggest `/rs-impl failing` to address them.

**Brownfield projects (HAS_CODE=true from scan-project.sh):** When reporting failures, distinguish baseline stories (`@phase: baseline`) from feature stories. Read the YAML to check each failing story's phase.

```
Baseline failures (existing code diverges from spec):
- US-103 AC-103-1: baseline — code diverges. Run /rs-spec to reconcile.

Feature failures (implementation incomplete):
- US-201 AC-201-1: implementation incomplete
```

This distinction helps developers know whether to fix the spec (baseline) or fix the code (feature).

**Record stats:**

```bash
COMPLETED_AT=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
bash "$(dirname "$0")/../rs-shared/scripts/write-stats.sh" rootspec/stats.json rs-validate "$STARTED_AT" "$COMPLETED_AT"
```

## Focus

Arguments narrow what the skill tests:
- No focus → all tests
- `"US-101"` → specific story
- `"TASK_SYSTEM"` → stories for a system
- `"MVP"` (or any phase name) → stories tagged with that phase
- `"failing"` → re-run previously failing stories

## Scope

- **CAN read:** All project files
- **CAN run:** Test commands, dev server
- **CAN write:** `rootspec/tests-status.json` only
- **CANNOT write:** Application code, spec files, config files, anything else
