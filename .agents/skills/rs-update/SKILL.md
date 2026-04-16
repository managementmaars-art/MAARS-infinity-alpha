---
name: rs-update
description: Upgrade a RootSpec project to the latest framework version — detects version gap, updates framework files, creates missing prerequisites, flags changed prerequisites for reconciliation. Run this after `npx skills add rootspec/rootspec`.
---

You are upgrading a RootSpec project to the latest framework version. Start by telling the developer what you're about to do:

"I'll check your project against the latest framework version and upgrade what's needed — framework files, prerequisites, and config."

## Step 1: Detect the gap

Run the scanning and gap analysis scripts:

```bash
bash "$(dirname "$0")/../rs-shared/scripts/scan-spec.sh" .
bash "$(dirname "$0")/../rs-shared/scripts/gap-analysis.sh" .
```

If these paths don't resolve, find the scripts by searching for `gap-analysis.sh` in the skills directory.

Based on the output:

- **`GAP=no_project`** — No `.rootspec.json` found. Tell the developer: "No RootSpec project found. Run `/rs-init` first." Exit.
- **`GAP=none`** — Already on the latest version. Tell the developer: "Project is already on version X.Y.Z. Nothing to update." Exit.
- **`GAP=patch|minor|major`** — Upgrade needed. Continue.

## Step 2: Show what changed

Read the update guide:

```
skills/rs-update/UPDATE.md
```

Find it relative to this skill file: `"$(dirname "$0")/UPDATE.md"`

Extract all version sections between PROJECT_VERSION (exclusive) and BUNDLED_VERSION (inclusive). Present:

- The version gap (e.g., "6.2.1 → 6.2.3")
- Summary of each version's changes
- Any manual instructions
- Whether there are breaking changes

## Step 3: Present the upgrade plan

Based on the gap analysis output, present a clear plan:

```
Upgrade plan (6.2.1 → 6.2.3):

Will update:
  - rootspec/00.FRAMEWORK.md (replace with vX.Y.Z)
  - rootspec/00.AXIOMS.md (replace with latest)
  - .rootspec.json version field

Will create (new prerequisites):
  - [list from NEW_PREREQUISITES, if any]

Needs reconciliation (changed prerequisites):
  - [list from CHANGED_PREREQUISITES, if any]

Will NOT touch:
  - Spec files (01.PHILOSOPHY.md through 05.IMPLEMENTATION/)
  - CONVENTIONS/ (owned by /rs-impl)

[If HAS_BREAKING=true]
⚠ Breaking changes detected — see details above.
```

Wait for the developer to confirm. They can exclude items (e.g., "skip dev.sh").

## Step 4: Execute the upgrade

For each item in the confirmed plan:

### Framework files

1. **`00.FRAMEWORK.md`** — Read from `../rs-shared/00.FRAMEWORK.md` (relative to this skill), write to `{specDirectory}/00.FRAMEWORK.md`.
2. **`00.AXIOMS.md`** — Read from `../rs-shared/00.AXIOMS.md`, write to `{specDirectory}/00.AXIOMS.md`.

### Config

3. **`.rootspec.json`** — Read the current file, update only the `version` field to BUNDLED_VERSION. Preserve all other fields (specDirectory, prerequisites).

### New prerequisites

4. For each entry in `NEW_PREREQUISITES`: check if the file/config exists in the project. If missing, create it using the same logic as `/rs-init`. Read `../rs-shared/fragments/prerequisites.md` for creation instructions.

### Changed prerequisites

5. For each entry in `CHANGED_PREREQUISITES`: the prerequisite exists but has updated requirements. Show the developer what changed and why (from UPDATE.md). Do NOT auto-overwrite — the developer's copy may have project-specific customizations.

   For template scripts (e.g., `scripts/dev.sh`): show a diff between the project's copy and the bundled template. Let the developer decide how to reconcile.

   For config wiring (e.g., `cypress.config.ts`): describe the required change and let the developer confirm before applying.

### Spec status

6. Run `write-spec-status.sh` to update the version in spec-status.json:

```bash
bash "$(dirname "$0")/../rs-shared/scripts/write-spec-status.sh" {specDirectory}
```

If breaking changes were detected (`HAS_BREAKING=true`): pass `false` as the second argument to mark the spec as invalid, and tell the developer to re-run `/rs-spec`.

```bash
bash "$(dirname "$0")/../rs-shared/scripts/write-spec-status.sh" {specDirectory} false
```

## Step 5: Report

Summarize what was done:

```
Update complete (6.2.1 → 6.2.3).

Updated:
  - rootspec/00.FRAMEWORK.md
  - rootspec/00.AXIOMS.md
  - .rootspec.json version

Created:
  - [any new prerequisites]

Flagged for review:
  - [any changed prerequisites with reconciliation notes]

Next steps:
  - [Re-run /rs-impl to update conventions if needed]
  - [Any manual instructions from UPDATE.md]
```

## Focus

If the developer passes an argument:
- A version number (e.g., `"6.2.2"`) → show what changed in that specific version only
- `"check"` → run gap analysis only, don't execute any changes (dry run)
- `"prerequisites"` → only handle prerequisite updates (skip framework files)

## Scope

- **CAN read:** all project files, all bundled skill files
- **CAN write:** `{specDirectory}/00.FRAMEWORK.md`, `{specDirectory}/00.AXIOMS.md`, `{specDirectory}/spec-status.json`, `.rootspec.json`, new prerequisite files
- **SHOULD NOT write:** spec files (01-05), application source code, existing test files
- **SHOULD NOT overwrite:** existing prerequisite files without developer confirmation
