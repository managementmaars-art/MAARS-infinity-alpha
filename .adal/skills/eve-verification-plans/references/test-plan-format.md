# Test Plan Format Specification

Complete format reference for Eve verification plan documents.

## Document Structure

Every test plan follows this structure. All sections are required unless marked optional.

```markdown
# Scenario NN: <Name>

**Time:** ~Nm
**Environment:** staging | local | both
**Parallel Safe:** Yes/No
**Requires:** LLM | Browser | None

<one-paragraph description of what this scenario verifies and why it matters>

## Prerequisites
## Fixtures (if applicable)
## Setup
## Phases
## Success Criteria
## Debugging
## Cleanup
```

## Metadata Fields

| Field | Values | Purpose |
|-------|--------|---------|
| **Time** | `~5m`, `~15m`, `~30m` | Rough estimate for planning parallel execution |
| **Environment** | `staging`, `local`, `both` | Which environment the plan targets |
| **Parallel Safe** | `Yes`, `No` | Whether this scenario can run alongside others |
| **Requires** | `LLM`, `Browser`, `None` | External dependencies beyond CLI + API |

## Environment Detection Boilerplate

Every plan starts setup with environment detection:

```bash
# Environment detection
if [[ "$EVE_API_URL" == https://* ]]; then
  ENV_TYPE="cloud"
  APP_SCHEME="https"
  APP_DOMAIN="${EVE_API_URL#https://api.}"  # e.g., eh1.incept5.dev
else
  ENV_TYPE="local"
  APP_SCHEME="http"
  APP_DOMAIN="lvh.me"
fi

echo "Environment: $ENV_TYPE ($EVE_API_URL)"

# Auth
eve auth login --email "${EVE_EMAIL}" --ssh-key "${EVE_SSH_KEY}"
TOKEN=$(eve auth token --raw)
```

This pattern ensures the same plan works against staging or local k3d.

## Prerequisites Section

List everything that must be true before running:

```markdown
## Prerequisites

- Scenario 00-smoke passes (API healthy, auth works)
- Project deployed to target environment
- Secrets set: `ANTHROPIC_API_KEY`, `GITHUB_TOKEN`
- Org filesystem synced: `eve fs sync`
```

Be explicit. "The app is deployed" is too vague. "Project `myapp` deployed to `staging` environment with `eve env deploy`" is correct.

## Fixtures Section

Required when the scenario uploads, imports, or processes files:

```markdown
## Fixtures

| File | Type | Purpose | Provenance |
|------|------|---------|------------|
| `fixtures/sample-doc.md` | Markdown | Happy path ingest | Hand-written, 500 words |
| `fixtures/sample-report.pdf` | PDF | Cross-format coverage | Generated via `scripts/make-fixtures.sh` |
| `fixtures/bad-format.txt` | Plain text | Rejection test | Hand-written, wrong MIME type |

All fixtures are deterministic and committed to the repo. See `fixtures/README.md` for generation details.
```

Omit this section entirely for scenarios that don't involve file inputs.

## Setup Section

Executable commands that prepare the environment:

```bash
## Setup

# Ensure org and project exist
ORG_ID=$(eve org ensure "test-org" --slug test-org --json | jq -r '.id')
PROJ_ID=$(eve project ensure --name "myapp" --slug myapp \
  --repo-url https://github.com/org/myapp --json | jq -r '.id')

# Import test secrets
eve secrets import --org $ORG_ID --file test.secrets

# Validate fixtures exist
for f in fixtures/sample-doc.md fixtures/sample-report.pdf; do
  [[ -f "$f" ]] || { echo "MISSING: $f"; exit 1; }
done
```

## Phases Section

Break verification into discrete, independently-runnable phases:

```markdown
### Phase 1: Health and Connectivity

\```bash
# API health
curl -sf "${APP_SCHEME}://api.${APP_DOMAIN}/health" | jq '.'

# CLI connectivity
eve system health --json
\```

**Expected:**
- Health endpoint returns `{"status":"ok"}`
- CLI reports all services healthy
- Response time under 2 seconds

### Phase 2: Core CRUD Flow

\```bash
# Create
ITEM_ID=$(curl -sf -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"test-item"}' \
  "${APP_SCHEME}://api.${APP_DOMAIN}/items" | jq -r '.id')

# Read
curl -sf -H "Authorization: Bearer $TOKEN" \
  "${APP_SCHEME}://api.${APP_DOMAIN}/items/$ITEM_ID" | jq '.'
\```

**Expected:**
- Create returns 201 with valid ID
- Read returns the created item with correct name
- Item ID follows expected format
```

### Assertion Writing

Every `Expected:` block must contain pass/fail verifiable statements:

- **Good**: "Response status is 200" / "JSON field `.status` equals `active`" / "Screenshot shows dashboard with 3 cards"
- **Bad**: "It works" / "Response looks correct" / "UI is nice"

Assertions should be checkable by an agent without human judgment.

## Success Criteria Section

Aggregate all assertions as checkboxes:

```markdown
## Success Criteria

### Phase 1
- [ ] Health endpoint returns `{"status":"ok"}`
- [ ] CLI reports all services healthy

### Phase 2
- [ ] Create returns 201 with valid ID
- [ ] Read returns created item with correct name
- [ ] Update modifies the item
- [ ] Delete removes the item (404 on re-read)
```

## Debugging Section

Map symptoms to diagnostics and fixes:

```markdown
## Debugging

| Symptom | Diagnostic | Fix |
|---------|-----------|-----|
| Health returns 503 | `eve env diagnose myapp staging` | Check pod health, restart if OOMKilled |
| Auth token rejected | `eve auth token --raw` and decode JWT | Re-login, check token expiry |
| Upload returns 413 | Check ingress body-size annotation | Add `proxy-body-size: "50m"` to manifest |
| Agent job stuck | `eve job diagnose <id>` | Check harness logs, verify secrets |
```

Include at least 3 rows covering the most likely failure modes for the scenario.

## Cleanup Section

Teardown commands that restore the environment:

```bash
## Cleanup

# Remove test data
curl -sf -X DELETE -H "Authorization: Bearer $TOKEN" \
  "${APP_SCHEME}://api.${APP_DOMAIN}/items/$ITEM_ID"

# Remove test org (if created for this run)
# eve org delete $ORG_ID  # Uncomment if safe
```

Cleanup is optional but recommended. Mark destructive cleanup with comments explaining impact.

## Artifact Output Convention

Screenshots, logs, and JSON dumps go to `./e2e-verification/artifacts/`:

```bash
# Screenshots
agent-browser --session verify screenshot ./e2e-verification/artifacts/dashboard-light.png
agent-browser --session verify screenshot ./e2e-verification/artifacts/dashboard-dark.png

# JSON dumps
eve job show $JOB_ID --verbose --json > ./e2e-verification/artifacts/job-result.json

# Logs
eve job logs $JOB_ID > ./e2e-verification/artifacts/job-logs.txt
```

Add `e2e-verification/artifacts/` to `.gitignore` — artifacts are generated, not committed.
