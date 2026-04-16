# Scenario NN: <Name>

**Time:** ~Nm
**Environment:** staging | local | both
**Parallel Safe:** Yes/No
**Requires:** LLM | Browser | None

<One paragraph describing what this scenario verifies and why it matters for Eve conformance.>

## Prerequisites

- Scenario 00-smoke passes
- Project deployed to target environment
- <Additional prerequisites>

## Fixtures

<!-- Remove this section if the scenario doesn't use file inputs -->

| File | Type | Purpose | Provenance |
|------|------|---------|------------|
| `fixtures/example.json` | JSON | Happy path test data | Hand-written |

## Setup

```bash
# Environment detection
if [[ "$EVE_API_URL" == https://* ]]; then
  ENV_TYPE="cloud"
  APP_SCHEME="https"
  APP_DOMAIN="${EVE_API_URL#https://api.}"
else
  ENV_TYPE="local"
  APP_SCHEME="http"
  APP_DOMAIN="lvh.me"
fi

# Auth
eve auth login --email "${EVE_EMAIL}" --ssh-key "${EVE_SSH_KEY}"
TOKEN=$(eve auth token --raw)

# Project variables
ORG_SLUG="your-org"
PROJECT_SLUG="your-project"
ENV_NAME="staging"
```

## Phases

### Phase 1: <Name>

```bash
# Commands to execute
```

**Expected:**
- Assertion 1 (pass/fail verifiable)
- Assertion 2

### Phase 2: <Name>

```bash
# Commands to execute
```

**Expected:**
- Assertion 1
- Assertion 2

## Success Criteria

### Phase 1
- [ ] Assertion 1
- [ ] Assertion 2

### Phase 2
- [ ] Assertion 1
- [ ] Assertion 2

## Debugging

| Symptom | Diagnostic | Fix |
|---------|-----------|-----|
| <Common failure> | <How to diagnose> | <How to fix> |
| <Common failure> | <How to diagnose> | <How to fix> |
| <Common failure> | <How to diagnose> | <How to fix> |

## Cleanup

```bash
# Teardown commands (if any)
```
