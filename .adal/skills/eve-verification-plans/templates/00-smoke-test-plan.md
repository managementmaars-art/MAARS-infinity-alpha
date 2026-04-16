# Scenario 00: Smoke Test + Eve Conformance

**Time:** ~5m
**Environment:** both
**Parallel Safe:** No (run first — validates prerequisites for all other scenarios)
**Requires:** None

Verifies API health, CLI connectivity, authentication, and Eve platform conformance. This scenario must pass before running any other verification scenarios.

## Prerequisites

- `EVE_API_URL` is set (cloud or local)
- Eve CLI is installed and on `$PATH`
- SSH key available for authentication
- Project is deployed to the target environment

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

echo "Environment: $ENV_TYPE ($EVE_API_URL)"

# Auth
eve auth login --email "${EVE_EMAIL}" --ssh-key "${EVE_SSH_KEY}"
TOKEN=$(eve auth token --raw)

# Project variables — CUSTOMIZE THESE
ORG_SLUG="your-org"
PROJECT_SLUG="your-project"
ENV_NAME="staging"  # or "test" for local
```

## Phases

### Phase 1: API Health

```bash
# Eve platform health
eve system health --json

# App API health (customize endpoint)
curl -sf "${APP_SCHEME}://api.${APP_DOMAIN}/health" | jq '.'
```

**Expected:**
- Eve system health returns `{"status":"ok"}`
- App health endpoint returns 200 with healthy status
- Response time under 2 seconds

### Phase 2: CLI Connectivity

```bash
# List orgs
eve org list --json | jq '.[].slug'

# Show project
eve project show $PROJECT_SLUG --json | jq '{name, slug, repo_url}'

# Show environment
eve env show $PROJECT_SLUG $ENV_NAME --json | jq '{name, status}'
```

**Expected:**
- Org list includes `$ORG_SLUG`
- Project shows correct name, slug, and repo URL
- Environment shows status `active` or `deployed`

### Phase 3: Authentication

```bash
# Verify token is valid
curl -sf -H "Authorization: Bearer $TOKEN" \
  "${APP_SCHEME}://api.${APP_DOMAIN}/health" -w "\n%{http_code}"

# Verify unauthorized request is rejected
curl -s "${APP_SCHEME}://api.${APP_DOMAIN}/protected-endpoint" -w "\n%{http_code}"
```

**Expected:**
- Authenticated request returns 200
- Unauthenticated request returns 401 (not 500 or 200)

### Phase 4: Eve Conformance Checklist

```bash
# Manifest exists and parses
cat .eve/manifest.yaml | head -5
eve project sync --dry-run

# Check manifest structure
cat .eve/manifest.yaml | yq '.name // .project'
cat .eve/manifest.yaml | yq '.services | keys'
cat .eve/manifest.yaml | yq '.environments | keys'

# Check for hardcoded secrets
grep -r "sk-\|ghp_\|xoxb-\|API_KEY=" src/ && echo "FAIL: Hardcoded secrets found" || echo "PASS: No hardcoded secrets"

# Check for .env files
ls .env* 2>/dev/null && echo "WARN: .env files present" || echo "PASS: No .env files"

# Secrets managed via Eve
eve secrets list --org $ORG_ID --project $PROJ_ID --json | jq 'length'
```

**Expected:**
- Manifest exists and `eve project sync --dry-run` succeeds
- Uses `name` field (flag if using legacy `project`)
- Services and environments are declared
- No hardcoded secrets in source code
- No `.env` files committed
- Secrets managed via Eve (at least 1 secret configured)

### Phase 5: Service Reachability

```bash
# Test each service endpoint — CUSTOMIZE for your app
SERVICES=("api" "web")  # Add your service names

for svc in "${SERVICES[@]}"; do
  URL="${APP_SCHEME}://${svc}.${ORG_SLUG}-${PROJECT_SLUG}-${ENV_NAME}.${APP_DOMAIN}/health"
  STATUS=$(curl -sf -o /dev/null -w "%{http_code}" "$URL" 2>/dev/null || echo "000")
  echo "${svc}: ${STATUS}"
done
```

**Expected:**
- All services return 200 on health endpoint
- No services require `kubectl port-forward`
- Services are reachable via Eve-managed ingress

## Success Criteria

### Phase 1
- [ ] Eve system health returns OK
- [ ] App health endpoint returns 200

### Phase 2
- [ ] Org exists and is listable
- [ ] Project shows correct configuration
- [ ] Environment is active/deployed

### Phase 3
- [ ] Authenticated requests succeed
- [ ] Unauthenticated requests return 401

### Phase 4
- [ ] Manifest exists and passes dry-run
- [ ] No hardcoded secrets
- [ ] No committed .env files
- [ ] Secrets managed via Eve

### Phase 5
- [ ] All services reachable via ingress
- [ ] Health endpoints return 200

## Debugging

| Symptom | Diagnostic | Fix |
|---------|-----------|-----|
| System health fails | `eve system health --json` | Check pod status, restart services |
| Auth token rejected | Decode JWT: `echo $TOKEN \| cut -d. -f2 \| base64 -d` | Re-login, check expiry |
| Manifest sync fails | Read error output | Fix manifest syntax, check `eve-manifest-authoring` |
| Service unreachable | `eve env diagnose $PROJECT $ENV` | Check ingress, pod health |
| Secrets list empty | `eve secrets list --org $ORG_ID` | Import secrets: `eve secrets import` |

## Cleanup

No cleanup needed — smoke test is read-only.
