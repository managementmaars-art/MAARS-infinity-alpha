# Prerequisites

Prerequisites are project infrastructure that RootSpec skills depend on. They are NOT part of the specification — they're the operational plumbing that makes implementation and validation possible.

## The four prerequisites

### Dev server script
**What:** A script that manages the development server lifecycle (start, stop, restart, status, logs).
**Why:** rs-impl and rs-validate need a running app to test against. Multiple skills may invoke the dev server — the script prevents duplicate processes and provides clean lifecycle control.
**Detect:** Look for `scripts/dev.sh` first, then `package.json` scripts (`dev`, `start`, `serve`), `Makefile` targets.
**Template:** Bundled at `rs-shared/scripts/dev.sh`. Copy into the project as `scripts/dev.sh`. The template:
- Tracks PID in `.dev-server.pid` and logs to `.dev-server.log` (both gitignored)
- Checks both PID file and port (`lsof`) before starting — prevents duplicates
- Auto-detects port from vite/next/astro config, falls back to 3000
- Commands: `start` (default), `stop`, `restart`, `status`, `logs`
**Package.json integration:** When `package.json` exists, add convenience scripts:
- `"dev:start": "./scripts/dev.sh start"`
- `"dev:stop": "./scripts/dev.sh stop"`
- `"dev:restart": "./scripts/dev.sh restart"`
**Example path:** `./scripts/dev.sh`

### Pre-commit hook
**What:** A git hook that runs before commits.
**Why:** Catches spec violations and test failures before they're committed.
**Detect:** Look for `.husky/pre-commit`, `.git/hooks/pre-commit`, `lefthook.yml`, `lint-staged` config.
**Template:** A husky-based pre-commit hook that runs spec validation.

### Release script
**What:** A script that handles versioning and release.
**Why:** Ensures spec version and app version stay in sync.
**Detect:** Look for `scripts/release.sh`, `release-it` config, `semantic-release` config.
**Template:** A shell script that bumps version, updates changelog, tags, and pushes.

### Validation/testing script
**What:** A command that runs the full test suite.
**Why:** rs-validate needs to know how to invoke tests.
**Detect:** Look for `package.json` scripts (`test`, `test:e2e`, `cypress`), `Makefile` targets, CI config.
**Template:** A shell script that starts the dev server and runs Cypress.
**Example path:** `./scripts/test.sh`, or record `"npm run test:e2e"` as the command.

### RootSpec Cypress plugin
**What:** A Cypress plugin that automatically updates `rootspec/tests-status.json` after each test run.
**Why:** Removes the agent from the test results pipeline — status is written as a side effect of running Cypress.
**Setup:** Copy `rs-shared/cypress/rootspec-reporter.ts` to `cypress/support/rootspec-reporter.ts` in the project. Wire it into `cypress.config.ts`:
```ts
import { rootspecReporter } from './cypress/support/rootspec-reporter';

export default defineConfig({
  e2e: {
    setupNodeEvents(on) {
      rootspecReporter(on, { statusPath: 'rootspec/tests-status.json' });
    }
  }
});
```
The plugin extracts story IDs from `describe("US-nnn: ...")` blocks and criterion IDs from `it("AC-nnn-nnn: ...")` tests, computes pass/fail, and merges with the existing status file.

## Detection strategy

For each prerequisite:
1. Check common locations and patterns
2. If found → confirm with developer, record path in `.rootspec.json`
3. If not found → ask: "No dev server script detected. Want me to create a template, or skip for now?"
4. If created → write the template, record path
5. If skipped → record `null` in `.rootspec.json`

## `.rootspec.json` prerequisites section

```json
{
  "prerequisites": {
    "devServer": "./scripts/dev.sh",
    "preCommitHook": ".husky/pre-commit",
    "releaseScript": null,
    "validationScript": "npm run test:e2e"
  }
}
```

Values can be file paths (for scripts) or shell commands (for npm scripts, etc.). Null means not configured.

## Advisory for interactive use

When running skills interactively (Claude Code), developers may want to configure permissions to match skill scopes:
- rs-spec: allow writes to `rootspec/` only
- rs-impl: allow writes everywhere except `rootspec/` spec files
- rs-validate: read-only (except `rootspec/tests-status.json`)

This is not enforced by the skills — it's operational guidance for security-conscious teams.
