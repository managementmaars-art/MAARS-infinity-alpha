# Secrets + Auth Reference

## Use When
- You need to manage secret scope, interpolation, and environment overrides.
- You need to configure auth, identities, roles, or policy behavior.
- You need to onboard service principals or troubleshoot permission failures.

## Load Next
- `references/cli.md` for secret and auth command workflows.
- `references/manifest.md` for manifest `x-eve.requires` and interpolation.
- `references/skills-system.md` when auth affects installed capabilities.

## Ask If Missing
- Confirm scope needed (project, org, user, or system) before setting values.
- Confirm whether values come from `.eve/dev-secrets.yaml`, API sources, or CI inputs.
- Confirm required roles/access groups when permission checks are failing.

## Secrets

### Scope Hierarchy

Secrets resolve in priority order: **project > user > org > system**. Values are encrypted at rest and never returned in plaintext. The `show` endpoint returns a masked value (first/last characters only).

API paths: `/system/secrets`, `/users/:id/secrets`, `/orgs/:id/secrets`, `/projects/:id/secrets`.

### CLI

```bash
eve secrets list --project proj_xxx
eve secrets set KEY value --project proj_xxx
eve secrets show KEY --project proj_xxx

eve secrets ensure --project proj_xxx --keys GITHUB_WEBHOOK_SECRET
eve secrets export --project proj_xxx --keys GITHUB_WEBHOOK_SECRET
```

`ensure` auto-generates allowlisted secrets (e.g., `GITHUB_WEBHOOK_SECRET`). `export` returns the plaintext value for external configuration -- treat it as sensitive.

### Import Secrets from File

Batch-import secrets from a `KEY=VALUE` env file:

```bash
eve secrets import --org org_xxx --file ./secrets.env
eve secrets import --project proj_xxx --file .env
```

Supported scopes: `--project`, `--org`, `--user`, `--system` (admin only). Lines starting with `#` and blank lines are ignored. Values are read verbatim after `=` (quotes are not stripped). Each key is upserted as `env_var`.

### Manifest Validation

Declare required secrets in `eve.yaml`:

```yaml
x-eve:
  requires:
    secrets: [GITHUB_TOKEN, REGISTRY_TOKEN]
```

Validate with:
```bash
eve project sync --validate-secrets
eve project sync --strict
eve secrets validate --project proj_xxx
```

Validation reports missing secrets with scope-aware remediation hints.

### Interpolation

Reference secrets in manifest environment blocks:

```yaml
environment:
  DATABASE_URL: postgres://user:${secret.DB_PASSWORD}@db:5432/app
  API_KEY: ${secret.EXTERNAL_API_KEY}
```

### Local Dev Secrets

Create `.eve/dev-secrets.yaml` (gitignored) for local overrides:

```yaml
secrets:
  default:
    DB_PASSWORD: dev_password
  staging:
    DB_PASSWORD: staging_password
```

API secrets overlaid by local dev-secrets. Local takes precedence. For k8s production, set secrets via the API.

### Host Env Files

Two host-level files for local development (never committed):

- **`.env`** (repo root) -- Local secrets and internal tokens.
- **`system-secrets.env.local`** -- System-level defaults, bootstrapped on API startup. Restart API to pick up changes.

### Required System Vars

| Variable | Where | Purpose |
|----------|-------|---------|
| `EVE_SECRETS_MASTER_KEY` | API | Encryption key for secrets at rest |
| `EVE_INTERNAL_API_KEY` | Worker + API | Internal token for resolve endpoint |

### Worker Injection

- Resolved secrets are injected as **environment variables** for the worker and deployer (allowlisted).
- File and `ssh_key` secrets are written outside the repo workspace and are not available to agent processes.
- The worker does **not** write `.eve/secrets.env` into the workspace and does **not** set `EVE_SECRETS_FILE`.

### Git Auth Injection

- **HTTPS clone**: `github_token` secrets are injected into the clone URL for private repo access.
- **SSH clone**: `ssh_key` secrets are written to a temp key and wired via `GIT_SSH_COMMAND`.
- Missing auth surfaces explicit errors with remediation hints (`eve secrets set`).

### Fail-Fast on Resolution Failure

The worker fails fast on secret resolution failure instead of silently substituting
empty strings. Provider credentials are resolved at the platform layer, not cached
in the worker. If `EVE_INTERNAL_API_KEY` is missing or incorrect, the attempt fails
immediately with a descriptive error.

### Troubleshooting Secret Resolution

If a job fails during clone or secret resolution:

1. Confirm the secret exists: `eve secrets show <KEY> --project <id>`
2. Ensure `EVE_INTERNAL_API_KEY` and `EVE_SECRETS_MASTER_KEY` are set for API/worker
3. Check orchestrator/worker logs for `[resolveSecrets]` warnings
4. Re-run with corrected secret scope (project > org > system)

### Incident Response

If you suspect a secret leak:

1. **Contain** -- Rotate the affected secret at the source. Update via `eve secrets set` or `eve secrets import`.
2. **Invalidate** -- Restart affected services to flush cached credentials. If a token was printed to logs, assume compromise.
3. **Audit** -- Review job and pipeline logs for leakage patterns. Check correlation IDs.
4. **Recover** -- Re-run failed jobs after rotation.
5. **Document** -- Record what leaked, where, and why. Add guardrails if due to missing redaction.

---

## Auth

Eve uses **RS256 JWT** tokens with pluggable identity providers (SSH, Nostr). Supabase (HS256) mode is optional when `SUPABASE_JWT_SECRET` is set.

### Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| `EVE_AUTH_ENABLED` | No | Enable auth (default `true`) |
| `EVE_AUTH_PRIVATE_KEY` | Yes | RSA private key (PEM string or file path) |
| `EVE_BOOTSTRAP_TOKEN` | Prod | One-time token for initial admin creation |
| `EVE_AUTH_PUBLIC_KEY` | No | Derived from private if omitted |
| `EVE_AUTH_CHALLENGE_TTL_SECONDS` | No | Challenge validity (default `300`) |
| `EVE_AUTH_TOKEN_TTL_DAYS` | No | User token TTL in days (default `1`, max `90`) |
| `EVE_AUTH_KEY_ID` | No | Key identifier in JWKS (default `key-1`) |

Generate keys:
```bash
openssl genrsa -out eve-auth.key 2048
openssl rsa -in eve-auth.key -pubout -out eve-auth.pub
export EVE_AUTH_PRIVATE_KEY="$(cat eve-auth.key)"
```

### Bootstrap

Create the first admin user. Three security modes:

| Mode | Trigger | Token Required |
|------|---------|----------------|
| **auto-open** | Fresh deploy, no users | No (10-min window) |
| **recovery** | Trigger file on host (`/tmp/eve-bootstrap-enable`) | No |
| **secure** | `EVE_BOOTSTRAP_TOKEN` set | Yes |

```bash
eve auth bootstrap --email admin@example.com --token $EVE_BOOTSTRAP_TOKEN
eve auth bootstrap --status
```

Production requires `EVE_BOOTSTRAP_TOKEN`. Use your real email -- it becomes your login identity.
In local/non-production environments, `eve auth bootstrap` attempts the API recovery path even when bootstrap is marked completed, and can return an existing admin token when recovery mode is allowed.

### Challenge-Response Login

Users authenticate by signing a challenge with a registered identity. The server selects the appropriate verifier based on identity type.

**CLI (recommended):**
```bash
eve auth login --email you@example.com
eve auth login --email you@example.com --ttl 30
```

The CLI requests a challenge, signs the nonce with your SSH key, submits the signature, and stores the token in `~/.eve/credentials.json`.

**SSH manual flow (curl):**
```bash
# 1. Request challenge
curl -X POST "$EVE_API_URL/auth/challenge" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'
# Response: { "challenge_id": "...", "nonce": "...", "expires_at": "..." }

# 2. Sign the nonce (namespace must be "eve-auth")
echo -n "$NONCE" | ssh-keygen -Y sign -f ~/.ssh/id_ed25519 -n eve-auth

# 3. Verify signature
curl -X POST "$EVE_API_URL/auth/verify" \
  -H "Content-Type: application/json" \
  -d '{"challenge_id": "...", "signature": "-----BEGIN SSH SIGNATURE-----\n..."}'
# Response: { "access_token": "...", "user_id": "...", "expires_at": ... }
```

**Nostr manual flow (curl):**
```bash
# 1. Request challenge (note: provider + pubkey, not email)
curl -X POST "$EVE_API_URL/auth/challenge" \
  -H "Content-Type: application/json" \
  -d '{"provider": "nostr", "pubkey": "<64-char-hex-pubkey>"}'

# 2. Sign a kind-22242 event with ["challenge", "<nonce>"] tag (client-side)

# 3. Submit signed event
curl -X POST "$EVE_API_URL/auth/verify" \
  -H "Content-Type: application/json" \
  -d '{"challenge_id": "...", "signature": "<kind-22242-event-json>"}'

# With invite code (for unregistered pubkeys):
curl -X POST "$EVE_API_URL/auth/verify" \
  -d '{"challenge_id": "...", "signature": "...", "invite_code": "abc123..."}'
```

### Self-Service Access Requests

Users can submit access requests without an invite:

```bash
eve auth request-access --org "My Company" --email you@example.com
eve auth request-access --org "My Company" --ssh-key ~/.ssh/id_ed25519.pub
eve auth request-access --status <request_id>
```

Admins review requests via:

```bash
eve admin access-requests list
eve admin access-requests approve <request_id>
eve admin access-requests reject <request_id> --reason "..."
```

List responses use the canonical `{ "data": [...] }` envelope. `eve auth list-service-accounts` output also uses the data envelope.

Approval semantics:
- Approval is transactional (no partial org/user leftovers on failure).
- Duplicate fingerprints reuse the existing identity owner instead of failing.
- Re-approving an already-approved request is idempotent.
- Legacy partial orgs with matching slug+name are reused during approval.

### Access Groups + Scoped Bindings

First-class access groups provide fine-grained data-plane authorization. Groups contain users and service principals, and bindings can carry scoped access constraints for org filesystem paths, org document paths, and environment DB schemas/tables.

#### Groups CLI

```bash
eve access groups create --org org_xxx --slug eng-team --name "Engineering Team" \
  [--description "Backend engineering group"]
eve access groups list --org org_xxx
eve access groups show eng-team --org org_xxx
eve access groups update eng-team --org org_xxx --name "Platform Engineering"
eve access groups delete eng-team --org org_xxx

# Group membership
eve access groups members list eng-team --org org_xxx
eve access groups members add eng-team --org org_xxx --user user_abc
eve access groups members add eng-team --org org_xxx --service-principal sp_xxx
eve access groups members remove eng-team --org org_xxx --user user_abc
```

#### Scoped Bindings

Bindings can carry `--scope-json` to restrict data-plane access:

```bash
eve access bind --org org_xxx --group grp_xxx --role data-reader \
  --scope-json '{"orgfs":{"allow_prefixes":["/shared/","/reports/"]}}'

eve access bind --org org_xxx --user user_abc --role db-analyst \
  --scope-json '{"envdb":{"schemas":["public"],"tables":["analytics_*"]}}'
```

Scope structure supports three resource types:
- `orgfs`: `allow_prefixes`, `read_only_prefixes` for org filesystem paths
- `orgdocs`: `allow_prefixes`, `read_only_prefixes` for org document paths
- `envdb`: `schemas`, `tables` for environment database access

#### Resource-Specific Access Checks

Check access against specific resources:

```bash
eve access can --org org_xxx --user user_abc --permission orgfs:read \
  --resource-type orgfs --resource /reports/q4.md --action read

eve access can --org org_xxx --group grp_xxx --permission envdb:read \
  --resource-type envdb --resource public.analytics --action read
```

`explain` also shows scope match details:

```bash
eve access explain --org org_xxx --user user_abc --permission orgfs:write
```

#### Memberships Introspection

Inspect the full effective access for any principal:

```bash
eve access memberships --org org_xxx --user user_abc
eve access memberships --org org_xxx --service-principal sp_xxx
```

Returns: base roles, group memberships, direct bindings, effective bindings (with role expansion and group resolution), effective permissions, and effective scopes for orgfs/orgdocs/envdb.

#### Policy-as-Code (Groups + Scoped Bindings)

The `.eve/access.yaml` format now supports groups and scoped bindings:

```yaml
access:
  groups:
    eng-team:
      name: Engineering Team
      description: Backend engineering group
      members:
        - type: user
          id: user_abc
        - type: service_principal
          id: sp_xxx
    data-team:
      name: Data Analytics Team
      members:
        - type: user
          id: user_def

  roles:
    data-reader:
      scope: org
      permissions: [orgfs:read, orgdocs:read, envdb:read]

  bindings:
    - roles: [data-reader]
      subject:
        type: group
        id: data-team
      scope:
        orgfs:
          allow_prefixes: ["/shared/", "/reports/"]
        envdb:
          schemas: [public]
```

`validate`, `plan`, and `sync` now handle groups, group members, and scoped bindings. The plan output includes group creates/updates/prunes, member adds/removes, and binding scope replacements.

### Credential Check

Inspect local AI tool credential availability:

```bash
eve auth creds                # Show Claude + Codex cred status
eve auth creds --claude       # Only Claude
eve auth creds --codex        # Only Codex
```

### OAuth Token Sync

Sync local OAuth tokens into Eve secrets:

```bash
eve auth sync                 # Sync to user-level (default)
eve auth sync --org org_xxx   # Sync to org-level
eve auth sync --project proj_xxx  # Sync to project-level
eve auth sync --dry-run       # Preview without syncing
```

This sets `CLAUDE_CODE_OAUTH_TOKEN` / `CLAUDE_OAUTH_REFRESH_TOKEN` (Claude) and `CODEX_AUTH_JSON_B64` (Codex/Code) at the requested scope.

#### Token Types and Lifetimes

| Token prefix | Type | Lifetime | Recommendation |
|---|---|---|---|
| `sk-ant-oat01-*` | `setup-token` (long-lived) | Long-lived | Preferred for jobs and automation |
| Other `sk-ant-*` | `oauth` (short-lived) | ~15h | Use for interactive dev; regenerate with `claude setup-token` |

`eve auth sync` warns when syncing a short-lived OAuth token. Use `eve auth creds` to inspect token type before syncing:

```bash
eve auth creds                # Shows token type (setup-token vs oauth) and Codex expiry
```

#### Automatic Codex/Code Token Write-Back

After each harness invocation, the worker checks if the Codex/Code CLI refreshed `auth.json` during the session. If the token changed, it is automatically written back to the originating secret scope (user/org/project) so the next job starts with a fresh token. This is transparent and non-fatal -- a write-back failure logs a warning but does not affect the job result.

#### Internal Secret Update Endpoint

The platform exposes `PATCH /internal/secrets/:scope_type/:scope_id/:key` for worker-to-API token write-back:
- Requires `x-eve-internal-token` header (same `EVE_INTERNAL_API_KEY` used by secret resolution)
- **Update-only** -- returns 404 if the secret does not already exist (no create semantics)
- Accepts `{ "value": "..." }` body

### Token Types

**User Tokens** -- Issued on successful login. Used for API access.
```json
{ "sub": "user_abc123", "email": "user@example.com", "type": "user", "iat": 1706000000, "exp": 1706086400 }
```

**Job Tokens** -- Scoped tokens issued to running jobs with limited permissions.
```json
{ "user_id": "user_abc123", "org_id": "org_xyz789", "permissions": ["job:read", "job:write"], "type": "job", "iat": 1706000000, "exp": 1706086400 }
```

**Service Principal Tokens** -- RS256 JWT with `sub: sp:{principal_id}`, `type: service_principal`, explicit `scopes` array. No implicit role expansion.

### Permissions

Eve uses a unified permission model. Job tokens carry a limited `permissions` list scoped to the project/job. Custom roles are additive only.

```bash
eve auth permissions          # Full permission catalog
eve auth whoami               # Current user + effective permissions
```

API: `GET /auth/permissions` (catalog), `GET /auth/me` (current user).

Permission resolution: `effective = expand(base_role) UNION all(bound_custom_role_permissions)`.

### Identity Management

Identities can be SSH public keys, Nostr pubkeys, or other provider-specific credentials. Each is linked to a user account.

Register additional identities:
```bash
curl -X POST "$EVE_API_URL/auth/identities" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"public_key": "ssh-ed25519 AAAA... user@laptop", "label": "laptop"}'
```

Admins can register keys for other users by including `"email": "user@example.com"` in the body.

### JWKS Endpoint

Public keys for token verification:
```bash
curl "$EVE_API_URL/.well-known/jwks.json"
# Returns: { "keys": [{ "kty": "RSA", "kid": "key-1", "use": "sig", "alg": "RS256", ... }] }
```

During key rotation, both old and new keys appear in JWKS.

### Key Rotation

**Standard rotation (with grace period):**
```bash
# 1. Generate new key pair
openssl genrsa -out eve-auth-new.key 2048
openssl rsa -in eve-auth-new.key -pubout -out eve-auth-new.pub

# 2. Configure grace period
export EVE_AUTH_PRIVATE_KEY="$(cat eve-auth-new.key)"
export EVE_AUTH_PUBLIC_KEY="$(cat eve-auth-new.pub)"
export EVE_AUTH_PUBLIC_KEY_OLD="$(cat eve-auth-old.pub)"
export EVE_AUTH_KEY_ID="key-2"
export EVE_AUTH_KEY_ID_OLD="key-1"

# 3. Restart API. New tokens use key-2; old tokens still verify via key-1.
# 4. After old tokens expire (default 24h), remove OLD vars and restart.
```

**Emergency rotation (key compromise):**
```bash
export EVE_AUTH_PRIVATE_KEY="$(cat eve-auth-new.key)"
export EVE_AUTH_KEY_ID="key-emergency-$(date +%s)"
unset EVE_AUTH_PUBLIC_KEY_OLD   # Do not honor old tokens
# Restart. All existing tokens are immediately invalidated.
```

---

## Identity Providers

Eve uses a pluggable identity provider framework. Providers register at startup and the auth guard evaluates them in a two-stage chain: **Bearer JWT first**, then provider-specific request auth.

### Provider Interface

Every provider implements:

```typescript
interface IdentityProvider {
  readonly name: string;
  createChallenge(params): Promise<ChallengeData>;
  verifyChallenge(challenge, proof, identities): Promise<VerifiedIdentity | null>;
  fingerprint(publicKey: string): Promise<string>;
  // Optional: per-request auth (no login required)
  extractFromRequest?(req): ExtractedCredential | null;
  verifyRequestCredential?(credential): Promise<VerifiedIdentity | null>;
}
```

`fingerprint` computes a deterministic dedup key to prevent duplicate registrations. `VerifiedIdentity` with `identity: null` triggers invite-gated provisioning.

### Auth Chain

```
Request --> @Public route? --> allow
        --> Stage 1: Bearer JWT (RS256/HS256) --> success: allow
        --> Stage 2: Provider request auth (registry iterates all providers) --> success: allow
        --> 401 Unauthorized
```

Stage 2 catches all errors and logs warnings. A broken provider does not cause a 500.

### SSH Provider (`github_ssh`)

- **Challenge**: Random 32-byte `base64url` nonce.
- **Verify**: Runs `ssh-keygen -Y verify` as subprocess. Iterates all registered SSH identities for the user until one matches.
- **Fingerprint**: `ssh-keygen -lf`, returns MD5 fingerprint (e.g., `MD5:ab:cd:...`).
- **Request-level auth**: Not supported. SSH requires the challenge/response flow.

### Nostr Provider (`nostr`)

Two authentication paths:

**Challenge/Verify (login)**: Client signs a kind-22242 event containing a `["challenge", "<nonce>"]` tag. Server verifies event ID + Schnorr signature (BIP-340), checks the challenge tag, matches pubkey to registered identities. Unregistered pubkeys trigger invite-gated provisioning.

**NIP-98 Request Auth**: Per-request auth via `Authorization: Nostr <base64>` header. Client creates a kind-27235 event with URL, method, and body hash tags. Server validates:
1. Event ID + Schnorr signature
2. `kind === 27235`
3. URL tag matches canonical request URL
4. Method tag matches request method
5. For non-GET: `payload` tag equals `sha256(body)`
6. Timestamp within +/-60s of server time
7. Replay protection via `auth_request_replays` table (120s TTL)

### Invite-Gated Provisioning

When an unregistered identity authenticates, the system attempts to provision via org invites.

**Create an invite (admin):**
```bash
curl -X POST "$EVE_API_URL/auth/invites" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"org_id": "org_xxx", "provider_hint": "nostr", "identity_hint": "<pubkey>", "role": "member", "expires_in_hours": 72}'
```

**Provisioning flow:**
1. Unregistered identity authenticates (challenge/verify or NIP-98)
2. Provider returns `VerifiedIdentity` with `identity: null`
3. Invite lookup: explicit `invite_code` takes priority, then `identity_hint` matching
4. Atomic provisioning: create user (synthetic email), create identity row, create org membership with invite role, mark invite used

**List invites:**
```bash
curl "$EVE_API_URL/auth/invites/org_xxx" -H "Authorization: Bearer $ADMIN_TOKEN"
```

### Org-Scoped Email Invites

Use the org-scoped invite API when an Eve-compatible app needs to invite a user by email, optionally send the Supabase email immediately, and preserve an app return URL through SSO onboarding.

**Permissions:**
- `orgs:invite` -- create and list org-scoped invites
- `orgs:members:read` -- list org members and search by email/display-name prefix

**Create an org-scoped invite:**
```bash
curl -X POST "$EVE_API_URL/orgs/org_xxx/invites" \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "role": "member",
    "redirect_to": "https://app.example.com/invite/complete",
    "app_context": { "project_id": "proj_123" }
  }'
```

**List org-scoped invites:**
```bash
curl "$EVE_API_URL/orgs/org_xxx/invites" -H "Authorization: Bearer $USER_TOKEN"
```

**Member picker lookup:**
```bash
curl "$EVE_API_URL/orgs/org_xxx/members/search?q=ali" \
  -H "Authorization: Bearer $USER_TOKEN"
```

`redirect_to` is stored on the invite record. Invite emails should flow through GoTrue's `/verify` endpoint, which returns to the SSO root with tokens in the hash fragment. If the invite is auto-applied during Supabase token exchange, Eve returns `invite_redirect_to` from `/auth/exchange`, and the SSO callback uses it as a fallback destination when nested redirect params are stripped from the email link. For invite accepts, the SSO broker establishes the session, routes the user through `/set-password`, then redirects to the final app URL.

---

## App Auth SDKs

For adding Eve SSO login to deployed apps, use the shared auth packages:

- **`@eve-horizon/auth`** -- Backend middleware (Express). **Recommended**: `eveAuth()` (unified, handles both user and agent tokens, attaches `req.eveIdentity` with `isAgent` boolean) + `eveIdentityGuard()`. Also provides `eveUserAuth()` (user-only), `eveAuthGuard()`, `eveAuthConfig()`, `eveAuthMe()`, `eveAuthMiddleware()` (agent-only, blocking), and lower-level `verifyEveToken()`/`verifyEveTokenRemote()`. Agent job tokens now include `agent_slug` and stable `email` (`{agent_slug}@eve.agent`) claims for agent identity.
- **`@eve-horizon/auth-react`** -- Frontend SDK (React). Provides `<EveAuthProvider>` (with optional `projectId` prop for project role resolution), `useEveAuth()` hook (with `orgs`, `activeOrg`, `switchOrg`), `<EveLoginGate>`, `<EveLoginForm>`, and `createEveClient()` fetch wrapper. Also exposes `getStoredToken()`/`storeToken()`/`clearToken()` for direct `sessionStorage` access.

### Auto-Injected Environment Variables

Apps deployed to Eve receive these env vars automatically from the platform deployer:

| Variable | Description |
|----------|-------------|
| `EVE_API_URL` | Internal API URL (server-to-server) |
| `EVE_PUBLIC_API_URL` | Public-facing API URL (optional) |
| `EVE_SSO_URL` | SSO broker URL |
| `EVE_ORG_ID` | Organization ID |
| `EVE_PROJECT_ID` | Project ID |
| `EVE_ENV_NAME` | Environment name |

The backend middleware reads these automatically. The frontend provider discovers auth config via the backend's `/auth/config` endpoint. Use `${SSO_URL}` in manifest `environment:` blocks for interpolation.

### Token Flow

1. `EveAuthProvider` checks `sessionStorage` for a cached token.
2. If none, probes the SSO broker `/session` endpoint (root-domain cookie).
3. If an SSO session exists, gets a fresh RS256 token and caches it.
4. If no SSO session, shows the login form (SSO redirect or token paste).
5. All API requests include `Authorization: Bearer <token>`.

For SSE endpoints, the middleware also accepts `?token=` query parameter.

For development or headless environments, use `eve auth token` to obtain a token for pasting.

**Token staleness**: The `orgs` claim reflects membership at token mint time. With the default 1-day TTL, membership changes can take up to 24h to reflect. Use `strategy: 'remote'` for immediate membership checks.

### Auth-React Org Awareness

`@eve-horizon/auth-react` exposes org membership and switching via the `useEveAuth()` hook:

```typescript
const { orgs, activeOrg, switchOrg } = useEveAuth();
// orgs: EveAuthOrg[]  — all orgs the user belongs to
// activeOrg: EveAuthOrg | null  — currently selected org
// switchOrg(orgId: string): void  — switch active org

type EveAuthOrg = {
  id: string;
  role: 'owner' | 'admin' | 'member';
};
```

- The backend already returns memberships in the token/session; the SDK now exposes them.
- Active org persists in `localStorage` across sessions.
- Backward compatible: `user.orgId` still works for single-org apps.

### Project Role Resolution

The `/auth/me` endpoint accepts an `X-Eve-Project-Id` header. When present, it resolves the user's project membership and returns `project_role` (`'owner' | 'admin' | 'member' | null`).

- **Backend**: Use `eveAuthMe({ projectHeader: 'x-eve-project-id' })` to forward the header and include project role in the response.
- **Frontend**: Pass `projectId` to `<EveAuthProvider>` to send the header automatically. Access via `user.projectRole`.
- **Custom roles**: Map `project_role` to app-specific roles (e.g. `editor/viewer`) in backend middleware.

See `references/auth-sdk.md` for full details.

---

## Harness Credentials (BYOK Model)

Eve does not manage inference endpoints or proxy LLM traffic. Apps and agents bring their own API keys (BYOK) via Eve secrets. Harnesses call upstream providers directly using resolved secrets — no platform-managed models, no managed catalog, no inference proxy.

### Required Secrets by Harness

| Harness | Secret | Optional |
|---------|--------|----------|
| mclaude / claude / zai | `ANTHROPIC_API_KEY` | `ANTHROPIC_BASE_URL` (for custom endpoints) |
| code / codex | `OPENAI_API_KEY` or `CODEX_AUTH_JSON_B64` | `OPENAI_BASE_URL` |
| gemini | `GEMINI_API_KEY` or `GOOGLE_API_KEY` | |
| zai | `Z_AI_API_KEY` | |

For private repos: `GITHUB_TOKEN` (HTTPS) or `ssh_key` (SSH via `GIT_SSH_COMMAND`).

### Self-Hosted Models (RunPod, vLLM, LM Studio, etc.)

Users who run their own models store the endpoint URL and API key as Eve secrets. The harness or app uses standard env vars (`OPENAI_BASE_URL`, `OPENAI_API_KEY`) — Eve is not involved in the lifecycle of the GPU endpoint.

For Tailscale-only endpoints, use private endpoints (platform networking primitive) to make them reachable from cluster pods.

### How It Works

```
Job created with harness=mclaude
  -> Worker resolves project secrets (ANTHROPIC_API_KEY, etc.)
  -> Harness adapter injects env vars into the harness process
  -> Harness calls provider API directly
  -> Eve never touches inference traffic
```

---

## Per-Org OAuth Credentials

Orgs bring their own OAuth app credentials for external providers (Google Drive, Slack) instead of relying on cluster-level defaults. Credentials are stored in the `oauth_app_configs` table (one config per org per provider).

### Setup Flow

1. Admin creates an OAuth app in the provider's console (GCP for Google Drive, api.slack.com for Slack).
2. Admin registers the credentials with Eve:

```bash
eve integrations configure google-drive \
  --client-id "xxx.apps.googleusercontent.com" \
  --client-secret "GOCSPX-xxx" \
  --label "Acme Corp Google Drive"

eve integrations configure slack \
  --client-id "12345.67890" \
  --client-secret "abc123" \
  --signing-secret "def456" \
  --app-id "A0123ABC"
```

3. Initiate the OAuth connection: `eve integrations connect google-drive`

### How It Works

- A single callback URL per provider handles all orgs. Org routing uses the `state` parameter (signed JWT).
- Token refresh uses the org's own `client_id` + `client_secret` from `oauth_app_configs`.
- Slack webhook verification uses the org's own `signing_secret` (resolved via org-scoped webhook URL or `team_id` lookup).
- No cluster-level `EVE_GOOGLE_CLIENT_ID`, `EVE_SLACK_CLIENT_ID`, etc. required.

### CLI

```bash
eve integrations setup-info google-drive   # Shows redirect URI, required scopes
eve integrations config google-drive       # View current config (secrets redacted)
eve integrations unconfigure google-drive  # Remove config
```

### API

```
POST   /orgs/:org_id/integrations/providers/:provider/config   # Upsert credentials
GET    /orgs/:org_id/integrations/providers/:provider/config    # View (redacted)
DELETE /orgs/:org_id/integrations/providers/:provider/config    # Remove
GET    /orgs/:org_id/integrations/providers/:provider/setup-info
```

Permission: `integrations:write` for create/update/delete, `integrations:read` for view.

---

## Service Principals + Token Minting

App backends authenticate as services via scoped tokens:

```bash
eve auth create-service-account --name "pm-app-backend" --org org_xxx \
  --scopes "jobs:create,jobs:read,projects:read"
eve auth list-service-accounts --org org_xxx
eve auth revoke-service-account --name pm-app-backend --org org_xxx
```

API: `POST /orgs/:id/service-principals`, `POST .../service-principals/:sp_id/tokens` (mint), `DELETE .../tokens/:tok_id` (revoke).

Admins can also mint tokens without SSH login (useful for bots):

```bash
eve auth mint --email app-bot@example.com --org org_xxx --ttl 90
```

Creates user and membership if needed. TTL capped at server's `EVE_AUTH_TOKEN_TTL_DAYS`.
