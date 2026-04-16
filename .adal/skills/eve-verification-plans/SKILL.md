---
name: eve-verification-plans
description: Author agentic verification plans for Eve-compatible apps. Use when building structured test suites that verify app correctness AND Eve platform conformance — CLI parity, manifest conventions, SSO auth, managed migrations, fixture-driven ingestion, and agent efficiency.
---

# Eve Verification Plans

Author **agentic verification plans** — markdown documents that fully specify the steps to verify an Eve-compatible app works correctly AND conforms to Eve platform conventions. Plans are actionable by humans or agents.

## When to Use

- Building verification for a new Eve-compatible app
- Auditing an existing app for Eve platform conformance
- After significant feature work that needs structured validation
- Before handoff — proving the app works the Eve way, end to end
- Onboarding a new team to understand what "correctly built on Eve" looks like

## Quick Start

```bash
# 1. Create the verification directory in your project
mkdir -p e2e-verification/00-smoke

# 2. Copy the smoke template
cp templates/00-smoke-test-plan.md e2e-verification/00-smoke/

# 3. Customize for your app (endpoints, services, agents)
# 4. Run it
```

## The Six Verification Dimensions

Every Eve app has up to six dimensions to verify. Cover all that apply.

| Dimension | Tool | When | Conformance Check |
|-----------|------|------|--------------------|
| **Platform conformance** | Eve CLI + manifest inspection | Always | CLI parity, manifest conventions, secrets model |
| **Service layer** | Eve CLI + REST API | Always | Every endpoint reachable via CLI; no kubectl needed |
| **Input / ingestion** | Repo fixtures + upload commands | When app accepts files | Deterministic fixtures, real parsing flows |
| **Data layer** | Eve CLI + DB migrations | When app has DB | Migrations via Eve pipeline, not manual SQL |
| **UI / visual** | agent-browser or Playwright | When frontend exists | SSO login, dark/light mode, agent-testable |
| **Agent behavior** | `eve job follow` + optimization | When app has agents | Efficient completion, no blind alleys |

## Verification Plan Format

Each scenario is a self-contained markdown document:

```markdown
# Scenario NN: <Name>

**Time:** ~Nm
**Environment:** staging | local | both
**Parallel Safe:** Yes/No
**Requires:** LLM | Browser | None

<one-paragraph description>

## Prerequisites

- What must be true before running
- Required secrets, auth, prior scenarios

## Fixtures

- File paths used by this scenario
- Provenance or generation command for each
- Why these files are representative

## Setup

\```bash
# Environment detection + auth
# Project/org setup
# Fixture validation or generation
\```

## Phases

### Phase 1: <Name>

\```bash
# Commands to execute
\```

**Expected:**
- Bullet list of assertions
- Each assertion is pass/fail verifiable

### Phase 2: ...

## Success Criteria

- [ ] Checkboxes for every pass/fail assertion
- [ ] Grouped by phase

## Debugging

| Symptom | Diagnostic | Fix |
|---------|-----------|-----|
| ... | ... | ... |

## Cleanup

\```bash
# Teardown commands
\```
```

### Format Rules

- **Environment-aware**: Every plan starts with environment detection — `EVE_API_URL` determines cloud vs local
- **Self-contained**: No assumed state beyond documented prerequisites
- **Fixture-explicit**: Every uploaded/imported artifact is checked in or generated from documented commands
- **Phased**: Break into phases that can run independently (parallel where safe)
- **Assertion-driven**: Every step has explicit `Expected:` with pass/fail criteria
- **Debuggable**: Troubleshooting section with symptom → diagnostic → fix

## Platform Conformance Verification

Before testing functionality, verify the app is built the Eve way. Every verification suite starts with this checklist:

- [ ] `.eve/manifest.yaml` exists and passes `eve project sync --dry-run`
- [ ] Manifest follows current conventions (`name` preferred over legacy `project`)
- [ ] All services have health endpoints reachable via Eve ingress
- [ ] CLI can interact with every API endpoint (no "UI-only" functionality)
- [ ] Secrets managed via `eve secrets`, not hardcoded or env-file-based
- [ ] DB migrations run as pipeline steps, not manual scripts
- [ ] Agents (if any) defined in `agents.yaml` with harness profiles
- [ ] Pipelines (if any) defined in manifest and runnable via `eve pipeline run`
- [ ] Frontend (if any) authenticates via Eve SSO, not custom auth
- [ ] Upload/import flows (if any) have deterministic fixtures checked in or generated locally

See `references/eve-conformance-checks.md` for the full checklist with rationale.

## Service Layer Verification

Test every API surface CLI-first:

```bash
TOKEN=$(eve auth token --raw)

# Health check (always first)
curl -sf "${APP_SCHEME}://api.${APP_DOMAIN}/health" | jq '.'

# App API via auth token
curl -sf -H "Authorization: Bearer $TOKEN" \
  "${APP_SCHEME}://api.${APP_DOMAIN}/endpoint" | jq '.field'
```

**CLI parity assertion**: For every `curl` call in a test plan, ask: "Can this also be done via a CLI command?" If not, file an issue — don't accept it.

Pattern:
1. **Eve CLI** commands where they exist (deploy, env, job, secrets)
2. **App CLI** if the app follows `eve-app-cli` patterns
3. **REST API** via `curl` with auth tokens for custom endpoints
4. **Auth**: Mint tokens via `eve auth mint` or `eve auth token --raw`

## Input / Ingestion Verification

When the app accepts uploads, imports, or document bundles, verification must include a fixture plan.

### Fixture Selection Order

1. Reuse existing repo fixtures if they match accepted file types and are deterministic
2. Manufacture synthetic fixtures locally with committed scripts
3. Source small public-domain fixtures only when local manufacture would reduce realism

### Fixture Matrix

- **Minimal valid** — smallest acceptable file that exercises the happy path
- **Typical real-world** — representative document/media/import file
- **Boundary / invalid** — wrong type, malformed structure, or size edge
- **Cross-format** — if the app accepts multiple types (PDF + Markdown + CSV), verify each

### What to Check

- File accepted through the real app surface (CLI, REST endpoint, or browser upload)
- MIME/type detection and metadata are correct
- Storage/persistence path is correct
- Downstream processing produces expected results
- Error handling is explicit for rejected or malformed fixtures

**Rule**: If a plan says "upload a sample PDF", it must include an actual file path or generator step. "Find a PDF online" is not acceptable.

See `references/fixture-patterns.md` for detailed guidance.

## UI Verification

When the app has a frontend, verify visual quality and interaction flows.

### SSO Token Injection

```bash
# Mint an SSO token via CLI
SSO_TOKEN=$(eve auth mint --email user@example.com --org $ORG_ID --format sso-jwt)

# Use agent-browser with the token
agent-browser --session verify open "${APP_URL}/auth/callback?token=${SSO_TOKEN}"
agent-browser --session verify wait --url "**/dashboard"
agent-browser --session verify screenshot ./e2e-verification/artifacts/dashboard.png
```

### What to Check

- Pages render without console errors
- Dark mode and light mode both work (screenshot both)
- Key user flows complete (login → dashboard → action → result)
- Responsive layout at standard breakpoints
- Forms submit correctly and validation fires

See `references/ui-verification-patterns.md` for tool choice guidance and patterns.

## Agent Verification

When the app includes Eve agents, verification extends to behavior quality.

1. Create a job that exercises the agent's primary workflow
2. Follow execution: `eve job follow <job-id>`
3. Check receipt: `eve job receipt <job-id>` (tokens, cost, duration)
4. Apply `eve-agent-optimisation` diagnostic workflow
5. Record baseline metrics in the test plan for regression detection

### What to Check

- Agent completes its task (correct output)
- Token usage within acceptable bounds
- No unnecessary tool calls or blind alleys
- Error cases handled gracefully (bad input, missing secrets)
- Multi-agent coordination works (jobs complete in dependency order)

See `references/agent-verification-patterns.md` for integration with optimization.

## Deploy Cycle Patterns

Verification often reveals issues. The fix/deploy loop:

### Cloud (Staging) — Default

```
discover bug → fix code → commit → tag release-v* → push tag →
  wait for CI (publish-images → infra dispatch → deploy) →
  re-run failed scenario
```

### Local (k3d)

```
discover bug → fix code → pnpm build →
  ./bin/eh k8s-image push → ./bin/eh k8s deploy →
  re-run failed scenario
```

See `references/deploy-cycle-patterns.md` for environment detection and wait patterns.

## Scenario Discovery

How to identify what scenarios to create for a given app:

1. **Read the manifest** — every service is a verification target
2. **Read agents config** — every agent needs a behavioral test
3. **Read the API spec** — every endpoint group is a potential scenario
4. **Check upload/import surfaces** — every accepted file class needs fixtures
5. **Check pipelines** — build/deploy/workflow pipelines need end-to-end verification
6. **Check the UI** — every page/route needs visual verification
7. **Check integrations** — webhooks, chat gateways, external APIs

### Minimum Scenario Set

| Scenario | Required | What It Covers |
|----------|----------|----------------|
| `00-smoke` | Always | Health, auth, connectivity + Eve conformance checklist |
| `01-deploy` | Always | Build, release, deploy via pipeline, verify endpoints |
| `02-core-flow` | Always | Primary user journey end-to-end (CLI + API) |
| `03-ui-visual` | If frontend | Screenshot verification, SSO login, dark/light mode |
| `04-input-ingestion` | If uploads/imports | Fixture upload, parsing, storage, error handling |
| `05-data-layer` | If database | Migrations via pipeline, schema correct, data integrity |
| `06-agent-execution` | If agents | Agents complete primary tasks correctly |
| `07-agent-optimization` | If agents | Baseline metrics + optimization pass |
| `08-pipeline-flows` | If pipelines | Each pipeline runs end-to-end, steps succeed in order |

## Running Verification Plans

### Sequential Execution

```bash
# Run scenarios in order
for plan in e2e-verification/*/; do
  echo "=== Running: $plan ==="
  # Agent reads and executes the plan document
done
```

### Parallel Execution

Scenarios marked `Parallel Safe: Yes` can run concurrently. Typically:
- `00-smoke` runs first (validates prerequisites)
- `01-deploy` through `03-ui-visual` can parallelize
- Agent scenarios (`06-07`) depend on deploy completing

### CI Integration

```bash
# In CI, set environment and run
export EVE_API_URL=https://api.eh1.incept5.dev
eve auth login --email $CI_EMAIL --ssh-key $CI_SSH_KEY

# Run all scenarios, collect artifacts
mkdir -p e2e-verification/artifacts
# Agent executes each plan, screenshots/logs go to artifacts/
```

## File Structure

```
<project-root>/
  e2e-verification/
    README.md                    # Index of all scenarios
    00-smoke/
      00-smoke-test-plan.md
    01-deploy/
      01-deploy-test-plan.md
    02-core-flow/
      02-core-flow-test-plan.md
      fixtures/
        README.md
        test-data.json
    03-ui-visual/
      03-ui-visual-test-plan.md
    04-input-ingestion/
      04-input-ingestion-test-plan.md
      fixtures/
        README.md
        sample-document.pdf
        sample-import.csv
        scripts/
          make-fixtures.sh
    artifacts/                   # Generated during runs (gitignored)
```

**Numbering**: `NN-kebab-name/` directories with matching `NN-kebab-name-test-plan.md`. Numbers imply execution order. Gaps are fine — they allow insertion without renaming.

**Fixtures**: Every scenario that depends on uploaded or imported inputs gets a sibling `fixtures/` directory. `fixtures/README.md` records provenance, generation steps, and sensitivity notes.

## References

- `references/test-plan-format.md` — Full format specification with annotated examples
- `references/eve-conformance-checks.md` — The Eve way: what to verify and why
- `references/fixture-patterns.md` — Fixture sourcing, manufacture, and documentation
- `references/deploy-cycle-patterns.md` — Fix/deploy loop for cloud and local
- `references/ui-verification-patterns.md` — Browser automation and SSO auth patterns
- `references/agent-verification-patterns.md` — Agent testing and optimization integration

## Templates

- `templates/00-smoke-test-plan.md` — Starter smoke + conformance template
- `templates/scenario-test-plan.md` — General scenario skeleton
- `templates/upload-ingest-test-plan.md` — Input-heavy scenario with fixture matrix

## Related Skills

| Skill | Relationship |
|-------|-------------|
| `eve-agent-optimisation` | Called from agent verification scenarios |
| `eve-web-ui-testing-agent-browser` | UI verification tool |
| `eve-deploy-debugging` | Deploy cycle troubleshooting |
| `eve-cli-primitives` | CLI commands used in service-layer tests |
| `eve-manifest-authoring` | Manifest conventions that conformance checks validate |
| `eve-app-cli` | App CLI patterns — verification asserts CLI parity |
| `eve-pipelines-workflows` | Pipeline conventions tested by pipeline scenarios |
| `eve-auth-and-secrets` | Auth + secrets model validated by conformance checks |
| `eve-troubleshooting` | General debugging when verification fails |
| `eve-read-eve-docs` | Reference source for current CLI/manifest/auth behavior |
| `eve-agent-native-design` | Design principles encoded in conformance checks |
