---
name: rs-init
description: Initialize a RootSpec project — create the rootspec/ directory, copy framework files, detect or create prerequisites. Use this when a user wants to start using RootSpec in a project, whether it's greenfield or has existing code.
---

You are setting up a project to use RootSpec. Start by telling the developer what you're about to do:

"I'll set up RootSpec for this project — create the spec directory, copy the framework files, and configure prerequisites (dev server, test runner, etc.). This takes a minute or two."

## Step 1: Scan the project

Understand what exists. Run these from the project root:

```bash
bash "$(dirname "$0")/../rs-shared/scripts/scan-spec.sh" .
bash "$(dirname "$0")/../rs-shared/scripts/scan-project.sh" .
```

If these paths don't resolve, find the scripts by searching for `scan-spec.sh` in the skills directory.

Based on the output, determine the situation:

- **Fresh init** — no `.rootspec.json`, no `rootspec/` directory. Most common case.
- **Partial init** — some files exist but others are missing (interrupted previous init).
- **Re-init** — `.rootspec.json` exists. If the version is behind the bundled framework, suggest `/rs-update` instead. Otherwise, ask the developer what they want to update. Do NOT overwrite existing spec files (01-05). You may update `00.AXIOMS.md` and `00.FRAMEWORK.md` to the latest bundled versions if the developer confirms.
- **Already initialized** — everything exists. Tell the developer and suggest `/rs-spec` instead.

Report what you found before proceeding.

## Step 2: Bootstrap the project

Run the bootstrap script to create the spec directory, base files, prerequisites, and `.rootspec.json`:

```bash
bash "$(dirname "$0")/../rs-shared/scripts/bootstrap-init.sh" . "$(dirname "$0")/../rs-shared"
```

If this path doesn't resolve, find the script by searching for `bootstrap-init.sh` in the skills directory.

This creates everything needed for a greenfield project: `rootspec/` with framework files, `scripts/dev.sh`, `scripts/test.sh`, `.githooks/pre-commit`, `scripts/release.sh`, Cypress reporter, `.rootspec.json`, and `package.json`. Files that already exist are skipped.

## Step 3: Detect and adapt prerequisites

Run the detection script to check what the bootstrap created vs what the project already had:

```bash
bash "$(dirname "$0")/../rs-shared/scripts/detect-prerequisites.sh" .
```

The script outputs `DEV_SERVER=`, `PRE_COMMIT_HOOK=`, `RELEASE_SCRIPT=`, `VALIDATION_SCRIPT=` lines with detected paths or `none`.

Read `../rs-shared/fragments/prerequisites.md` for the full reference on what each prerequisite is.

**Package.json rule:** NEVER write the `dependencies` or `devDependencies` sections of package.json directly. Always use `npm install <pkg>` or `npm install --save-dev <pkg>` to add packages — npm manages the dependency tree. You may edit the `scripts` section directly (e.g., to add `dev:start`).

Report what was detected. For brownfield projects, adapt the bootstrap defaults:

- **Dev server** — edit the `DEV_CMD` variable in `scripts/dev.sh` to match the project's actual dev command (e.g., `npm run dev`, `npx vite`).
- **Existing prerequisites** — if the project already had a dev server, test runner, etc., update `.rootspec.json` to point to them instead of the bootstrap defaults.
- **Package.json scripts** — add `dev:start`, `dev:stop`, `dev:restart` entries if not already present.

### Cypress plugin setup

Set up the RootSpec Cypress reporter (bootstrap already copied the file):

1. **Wire it into `cypress.config.ts`** — if the config exists, add the `setupNodeEvents` hook with the reporter. If creating a new config, include it from the start. See `../rs-shared/fragments/prerequisites.md` for the exact wiring.

This plugin automatically updates `rootspec/tests-status.json` after every Cypress run — the agent doesn't need to parse results or call scripts.

## Step 4: Update `.rootspec.json`

If Step 3 detected existing prerequisites that differ from the bootstrap defaults, update `.rootspec.json` with the correct paths.

## Step 5: Verify and hand off

Run the verification script:

```bash
bash "$(dirname "$0")/../rs-shared/scripts/verify-init.sh" .
```

If anything is reported missing, create it. Then report:

"Project initialized. Here's what was set up:
- [list files created]
- [list prerequisites configured or skipped]

Run `/rs-spec` to create your specification."

## Focus

If the developer passes an argument:
- `"resume"` → skip to whatever step is incomplete
- `"prerequisites"` → only run Steps 3-4 (detect/create prerequisites, update .rootspec.json)

## Scope

- **CAN read:** all project files
- **CAN write:** `rootspec/` directory (including `spec-status.json`, `tests-status.json`), `.rootspec.json`, prerequisite templates (e.g., `scripts/dev.sh`)
- **SHOULD NOT write:** application source code, existing test files
