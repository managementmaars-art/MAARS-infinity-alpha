---
name: rs-shared
description: Shared scripts, fragments, and bundled files used by all RootSpec skills — not meant to be invoked directly
---

This skill contains shared resources for all RootSpec skills. Do not invoke directly.

## Skills

| Skill | Purpose | Mode |
|-------|---------|------|
| `/rs-init` | Initialize project — directories, base files, prerequisites | Interactive |
| `/rs-spec` | Create or update specification — interview + validation loop | Interactive (skippable) |
| `/rs-impl` | Implement from spec — test-driven, autonomous | Non-interactive |
| `/rs-validate` | Run tests and report results | Non-interactive |
| `/rs-update` | Upgrade project to latest framework version | Interactive |

## Scripts

### Project scanning
- `scripts/scan-spec.sh` — Find spec directory, list found/missing files, detect version
- `scripts/scan-project.sh` — Detect framework, source dirs, config files

### Spec validation
- `scripts/validate-spec.sh` — Run all 6 validation checks in one call (hierarchy, numerics, duplicate IDs, pillar quality, tradeoffs, coverage)
- `scripts/check-hierarchy.sh` — Find downward references across spec levels
- `scripts/check-numerics.sh` — Find hardcoded numbers in L1-L4
- `scripts/check-duplicate-ids.sh` — Find duplicate story IDs in L5
- `scripts/check-pillar-quality.sh` — Check L1 pillar count and format
- `scripts/check-tradeoffs.sh` — Check L2 for explicit trade-off statements
- `scripts/check-coverage.sh` — Cross-reference L4 systems with L5 stories
- `scripts/compute-spec-hash.sh` — Compute deterministic hash of all spec files

### Initialization and upgrade
- `scripts/detect-prerequisites.sh` — Detect dev server, hooks, release/test scripts
- `scripts/verify-init.sh` — Check all expected init files exist
- `scripts/gap-analysis.sh` — Compare project version against bundled framework version

### Implementation support
- `scripts/assess.sh` — Front-load all reading for rs-impl in one call (spec, project, stories, conventions, fragments)
- `scripts/scaffold-cypress.sh` — Create all Cypress infrastructure files in one call (config, support, DSL, reporter)
- `scripts/generate-test-file.sh` — Build Cypress test file from spec YAML (embeds stories with loadAndRun pattern)
- `scripts/init-conventions.sh` — Extract conventions from package.json, tsconfig, Tailwind config, and source code
- `scripts/generate-test-report.sh` — Parse tests-status.json into formatted pass/fail/not-tested report

### Stories and testing
- `scripts/filter-stories.sh` — Filter L5 stories by ID, system, priority, or status
- `scripts/parse-cypress-results.sh` — Parse Cypress JSON output to story/criterion results
- `scripts/build-tests-status.sh` — Merge test results into tests-status.json
- `scripts/compare-test-runs.sh` — Diff two test runs, report regressions/fixes

## Bundled Files
- `00.AXIOMS.md` — Foundational beliefs (copied to user projects by rs-init)
- `00.FRAMEWORK.md` — Framework definition (copied to user projects by rs-init)

## Fragments
- `fragments/framework-rules.md` — Reference hierarchy and placeholder rules
- `fragments/interview-protocol.md` — Interview methodology
- `fragments/anti-patterns.md` — Common anti-patterns by level
- `fragments/prerequisites.md` — Prerequisite detection and creation
- `fragments/l5-yaml-format.md` — YAML syntax for user stories and fine-tuning
- `fragments/l5-test-dsl.md` — Test DSL step reference and extensions
