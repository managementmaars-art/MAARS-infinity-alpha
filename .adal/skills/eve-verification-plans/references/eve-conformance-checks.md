# Eve Conformance Checks

What makes an app correctly built on Eve. Use this checklist in the `00-smoke` scenario to verify platform conformance before testing functionality.

## The Eve Way

Eve-compatible apps follow specific conventions. Conformance checks verify the app adheres to these conventions — violations are filed as issues, not accepted as quirks.

## Manifest Conformance

```bash
# Manifest exists and parses
eve project sync --dry-run

# Check manifest structure
cat .eve/manifest.yaml | yq '.name'           # Should exist (preferred over legacy 'project')
cat .eve/manifest.yaml | yq '.services'       # Services declared
cat .eve/manifest.yaml | yq '.environments'   # Environments declared
```

### What to Check

- [ ] `.eve/manifest.yaml` exists at project root
- [ ] `eve project sync --dry-run` succeeds without errors
- [ ] Uses `name` field (not legacy `project` — tolerate but flag)
- [ ] All deployed services are declared in `services:`
- [ ] Environments match deployment targets (e.g., `staging`, `production`)
- [ ] Pipelines declared if build/deploy automation exists
- [ ] Variable interpolation uses `${EVE_*}` patterns, not hardcoded values

### Why This Matters

The manifest is the single source of truth for what Eve deploys. If a service exists in k8s but not in the manifest, it was deployed manually — a conformance violation.

## CLI Parity

```bash
# List all app API endpoints
# For each endpoint, verify it's reachable via:
# 1. Eve CLI command (eve job, eve env, eve secrets, etc.)
# 2. App CLI command (if app follows eve-app-cli patterns)
# 3. curl with auth token (for custom API endpoints)
```

### What to Check

- [ ] Every REST API endpoint the app exposes has a corresponding CLI path
- [ ] No "UI-only" functionality — everything the UI does is also CLI-accessible
- [ ] App CLI (if exists) follows `eve-app-cli` patterns (structured output, `--json` flag, auth integration)
- [ ] Error responses include actionable messages, not stack traces

### Why This Matters

Agents interact via CLI, not browsers. UI-only functionality is invisible to agents. Every UI-only feature is an agent-accessibility gap.

## Secrets Management

```bash
# Check secrets are managed via Eve
eve secrets list --org $ORG_ID --project $PROJ_ID

# Verify no hardcoded secrets
grep -r "API_KEY\|SECRET\|PASSWORD" .env* || echo "No .env files (good)"
grep -r "sk-\|ghp_\|xoxb-" src/ || echo "No hardcoded tokens (good)"
```

### What to Check

- [ ] All credentials managed via `eve secrets set` or `eve secrets import`
- [ ] No `.env` files committed to the repo
- [ ] No hardcoded API keys, tokens, or passwords in source code
- [ ] Secrets referenced in manifest via `${EVE_SECRET_*}` interpolation
- [ ] Sensitive values not logged or exposed in API responses

### Why This Matters

Eve manages secret lifecycle (rotation, scoping, audit). Hardcoded secrets bypass all of this and create security + operational risks.

## Database Migrations

```bash
# Check migrations run via Eve pipeline
cat .eve/manifest.yaml | yq '.pipelines'

# Verify no manual migration scripts
ls db/migrate/ scripts/migrate* 2>/dev/null
```

### What to Check

- [ ] DB schema changes defined as pipeline steps in the manifest
- [ ] Migrations runnable via `eve pipeline run <pipeline>`
- [ ] No manual `psql`, `prisma migrate`, or ORM CLI commands required
- [ ] Migration order is deterministic (numbered or timestamped)
- [ ] Rollback strategy documented (if applicable)

### Why This Matters

Eve manages database lifecycle. Manual migrations are invisible to the platform — they can't be tracked, audited, or rolled back through Eve.

## Ingress and Routing

```bash
# Check services are reachable via Eve-managed ingress
for svc in $(cat .eve/manifest.yaml | yq -r '.services | keys[]'); do
  curl -sf "${APP_SCHEME}://${svc}.${APP_DOMAIN}/health" && echo "$svc: OK" || echo "$svc: FAIL"
done
```

### What to Check

- [ ] All services reachable via Eve-managed ingress (not manual port-forward)
- [ ] Health endpoints respond on all services
- [ ] Mechanical ingress names follow `{service}.{org}-{project}-{env}.{domain}` pattern
- [ ] Vanity aliases (if configured) resolve correctly
- [ ] Custom domains (if configured) have valid TLS certificates
- [ ] No services require `kubectl port-forward` to access

### Why This Matters

Eve manages ingress automatically from the manifest. Services that require manual port-forward or direct pod access are not properly declared.

## Authentication

```bash
# Mint a token
TOKEN=$(eve auth token --raw)

# Verify SSO flow (if frontend exists)
SSO_TOKEN=$(eve auth mint --email test@example.com --org $ORG_ID --format sso-jwt)

# Test API auth
curl -sf -H "Authorization: Bearer $TOKEN" "${APP_SCHEME}://api.${APP_DOMAIN}/health"
```

### What to Check

- [ ] App authenticates via Eve SSO, not custom auth
- [ ] API accepts Eve-minted bearer tokens
- [ ] Frontend uses SSO callback flow (`/auth/callback?token=...`)
- [ ] Token expiry is handled gracefully (re-auth prompt, not crash)
- [ ] Unauthorized requests return 401, not 500

### Why This Matters

Eve SSO provides unified identity across the platform. Custom auth creates identity silos that agents can't navigate.

## Agents

```bash
# Check agent definitions
cat agents.yaml 2>/dev/null || cat .eve/agents.yaml 2>/dev/null

# Verify agents are registered
eve agent list --project $PROJ_ID
```

### What to Check (if app has agents)

- [ ] Agents defined in `agents.yaml` with harness profiles
- [ ] Each agent has a clear purpose and scope
- [ ] Agent slugs are unique within the project
- [ ] Harness profiles specify model and provider
- [ ] Agent jobs complete within expected time/token bounds

### Why This Matters

Agents defined in YAML are discoverable, configurable, and auditable. Ad-hoc agent invocations bypass all of this.

## Pipelines

```bash
# Check pipeline definitions
cat .eve/manifest.yaml | yq '.pipelines'

# List available pipelines
eve pipeline list --project $PROJ_ID
```

### What to Check (if app has pipelines)

- [ ] Pipelines defined in manifest under `pipelines:`
- [ ] Each pipeline is runnable via `eve pipeline run <name>`
- [ ] Build pipeline produces correct artifacts
- [ ] Deploy pipeline targets correct environment
- [ ] Pipeline steps have clear names and error handling

### Why This Matters

Pipelines in the manifest are reproducible and auditable. Shell scripts or manual deploy steps are neither.

## Filing Conformance Gaps

When a check fails, classify it:

| Classification | Action |
|---------------|--------|
| **Bug** | File an issue, fix in current cycle |
| **Conformance gap** | File an issue with `conformance` label, prioritize for next cycle |
| **Platform limitation** | File against eve-horizon-2, not the app — the platform should support this |
| **Intentional deviation** | Document in the app's README with rationale |

The default assumption is conformance. Deviations require justification.
