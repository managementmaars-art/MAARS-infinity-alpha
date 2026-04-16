# Eve Auth SDK Reference

## Use When
- You need to add SSO login or token verification to an Eve-deployed app.
- You need to protect backend routes with Eve org membership checks.
- You need to migrate from custom auth to the `@eve-horizon/auth` SDK.

## Load Next
- `references/secrets-auth.md` for token types, scopes, and identity providers.
- `references/integrations.md` for external identity resolution and Slack/GitHub connect.
- `references/cli-auth.md` for CLI-level auth commands and service accounts.

## Ask If Missing
- Confirm whether the app is backend-only (Express/NestJS) or includes a React frontend.
- Confirm whether the app needs user-only auth (`eveUserAuth`), agent-only auth (`eveAuthMiddleware`), or unified auth for both (`eveAuth`).
- Confirm the target org ID and whether `EVE_SSO_URL` / `EVE_API_URL` are already injected.

Two shared packages that eliminate auth boilerplate in Eve-compatible apps.

| Package | Scope | Purpose |
|---------|-------|---------|
| `@eve-horizon/auth` | Backend (Express/NestJS) | Token verification, org check, route protection |
| `@eve-horizon/auth-react` | Frontend (React) | SSO session bootstrap, login gate, token cache |

## Architecture

```
Browser                               Backend (Express)                      Eve Platform
-------                               -----------------                      ------------
EveAuthProvider                        eveUserAuth()                          Eve API
  |-- sessionStorage check             |-- Extract Bearer token               |-- /.well-known/jwks.json
  |-- GET /auth/config ------------>   |   eveAuthConfig()                    |-- /auth/token/verify
  |-- GET {sso_url}/session ------->   |   -> { sso_url, eve_api_url, ... }   \-- /auth/config
  |   (root-domain cookie)             |-- Verify RS256 (JWKS, 15-min cache)
  |-- Store token in sessionStorage    |-- Check orgs claim for org membership
  \-- GET /auth/me ---------------->   |-- Attach req.eveUser
      (Authorization: Bearer)          |   eveAuthGuard()
                                       \-- 401 if no req.eveUser
```

## Backend: `@eve-horizon/auth`

### Setup (Express)

```bash
npm install @eve-horizon/auth
```

```typescript
import { eveUserAuth, eveAuthGuard, eveAuthConfig, eveAuthMe } from '@eve-horizon/auth';

app.use(eveUserAuth());                                     // Parse tokens (non-blocking)
app.get('/auth/config', eveAuthConfig());                   // Serve SSO discovery
app.get('/auth/me', eveAuthMe());                           // Full /auth/me for React SDK
app.use('/api', eveAuthGuard());                            // Protect all API routes
```

**Important**: Use `eveAuthMe()` for `/auth/me` instead of returning `req.eveUser` directly. The handler returns snake_case fields with org memberships — the format the React SDK expects. Returning `req.eveUser` directly (camelCase, no memberships) will break the React SDK.

### Exports

| Export | Type | Purpose |
|--------|------|---------|
| `eveAuth(options?)` | Middleware | **Recommended.** Unified auth for both user and agent tokens, attach `req.eveIdentity` |
| `eveIdentityGuard()` | Middleware | Return 401 if `req.eveIdentity` not set |
| `eveUserAuth(options?)` | Middleware | User-only: verify user token, check org membership, attach `req.eveUser` |
| `eveAuthGuard()` | Middleware | Return 401 if `req.eveUser` not set |
| `eveAuthConfig()` | Handler | Serve `{ sso_url, eve_api_url, ... }` from env vars |
| `eveAuthMe(options?)` | Handler | Serve `/auth/me` with full user claims (memberships + project role) |
| `eveAuthMiddleware(options?)` | Middleware | Agent-only: blocking token verification, attach `req.agent` |
| `verifyEveToken(token, url?)` | Function | JWKS-based local verification (15-min cache) |
| `verifyEveTokenRemote(token, url?)` | Function | HTTP verification via `/auth/token/verify` |

### Middleware Behavior

**`eveUserAuth()`** is non-blocking. It passes through without setting `req.eveUser` when:
- No token present
- Token is invalid or expired
- Token type is not `user`
- `orgs` claim missing or target org not found

This lets you mix public and protected routes on the same app — apply `eveUserAuth()` globally, then add `eveAuthGuard()` only on routes that require authentication.

**`eveAuthMe()`** is an Express handler for `/auth/me`. Unlike returning `req.eveUser` directly (which is camelCase and lacks memberships), `eveAuthMe()` reads JWT claims and returns the full response the React SDK expects — snake_case fields, org memberships array, and optional project role. Options:
- `orgId?: string` -- override `EVE_ORG_ID`
- `eveApiUrl?: string` -- override `EVE_API_URL`
- `strategy?: 'local' | 'remote'` -- verification strategy
- `projectHeader?: string` -- request header name containing a project ID (e.g. `'x-eve-project-id'`). When set, proxies to Eve API to resolve the user's project-level role.

**`eveAuthMiddleware()`** is blocking — returns 401 immediately on any verification failure. Use for agent-only APIs where every request must be authenticated.

### Unified Auth: `eveAuth()` (Recommended for New Apps)

Use `eveAuth()` when your app serves both browser users AND agent API calls. It handles both token types and normalizes identity into a single `req.eveIdentity` object.

```typescript
import { eveAuth, eveIdentityGuard, eveAuthConfig, eveAuthMe } from '@eve-horizon/auth';

app.use(eveAuth());                                         // Parse any Eve token
app.get('/auth/config', eveAuthConfig());                   // SSO discovery
app.get('/auth/me', eveAuthMe());                           // React SDK /auth/me
app.get('/protected', eveIdentityGuard(), (req, res) => {   // Both users and agents
  if (req.eveIdentity.isAgent) {
    // Agent-specific logic — req.eveIdentity.agentSlug, .jobId, .permissions
  } else {
    // User-specific logic — req.eveIdentity.email, .role
  }
});
```

**`eveAuth()`** is non-blocking (like `eveUserAuth`). It sets `req.eveIdentity` for:
- **User tokens** (`type: 'user'`): resolves org membership, sets `isAgent: false`
- **Job tokens** (`type: 'job'`): uses job claims directly, sets `isAgent: true` with agent identity

```typescript
interface EveIdentity {
  id: string;                    // User ID or actor user ID
  email: string;                 // Real email (users) or {agent_slug}@eve.agent (agents)
  orgId: string;                 // Organization scope
  role: 'owner' | 'admin' | 'member';
  isAgent: boolean;              // True for agent/job tokens
  agentSlug?: string;            // Which agent is calling (agents only)
  jobId?: string;                // Job ID (agents only)
  projectId?: string;            // Project ID (agents only)
  permissions?: string[];        // Granted permissions (agents only)
}
```

**When to use which middleware:**

| Middleware | Use case | Token types | Blocking? |
|-----------|----------|-------------|-----------|
| `eveAuth()` | Apps serving both users and agents | User + Job | No |
| `eveUserAuth()` | User-only web apps | User only | No |
| `eveAuthMiddleware()` | Agent-only APIs | Any | Yes (401) |

### Agent Identity in Job Tokens

Job tokens now include `agent_slug` and a stable `email` claim when the job targets a specific agent:

```json
{
  "type": "job",
  "sub": "user_01abc...",
  "user_id": "user_01abc...",
  "org_id": "org_Incept5",
  "project_id": "proj_01xyz...",
  "job_id": "eden-08c64625",
  "agent_slug": "map-generator",
  "email": "map-generator@eve.agent",
  "permissions": ["jobs:read", "jobs:write", "projects:read", ...]
}
```

- `agent_slug` identifies which agent is calling — stable across jobs
- `email` is `{agent_slug}@eve.agent` — stable per agent, usable for RLS policies and audit
- Both fields are absent for jobs that don't target a specific agent

### Verification Strategies

| Strategy | Default for | Latency | Freshness |
|----------|-------------|---------|-----------|
| `'local'` | `eveUserAuth` | Fast (JWKS cached 15 min) | Stale up to 15 min |
| `'remote'` | `eveAuthMiddleware` | ~50ms per request | Always current |

### Token Types

```typescript
interface EveTokenClaims {
  valid: true;
  type: 'user' | 'job' | 'service_principal';
  user_id: string;
  email?: string;
  org_id?: string | null;     // Job tokens: single org
  orgs?: Array<{              // User tokens: all memberships
    id: string;
    role: string;
  }>;
  project_id?: string;
  job_id?: string;
  agent_slug?: string;        // Job tokens: agent identity (e.g. "map-generator")
  permissions?: string[];
  is_admin?: boolean;
  role?: string;
}

interface EveUser {
  id: string;
  email: string;
  orgId: string;
  role: 'owner' | 'admin' | 'member';
  projectRole?: 'owner' | 'admin' | 'member' | null;  // When project context available
}
```

## Frontend: `@eve-horizon/auth-react`

### Setup (React)

```bash
npm install @eve-horizon/auth-react
```

```tsx
import { EveAuthProvider, EveLoginGate } from '@eve-horizon/auth-react';

function App() {
  return (
    <EveAuthProvider apiUrl="/api">
      <EveLoginGate>
        <ProtectedApp />
      </EveLoginGate>
    </EveAuthProvider>
  );
}
```

### Exports

| Export | Type | Purpose |
|--------|------|---------|
| `EveAuthProvider` | Component | Context provider, session bootstrap. Props: `apiUrl?`, `projectId?` |
| `useEveAuth()` | Hook | `{ user, loading, error, config, orgs, activeOrg, switchOrg, loginWithSso, loginWithToken, logout }` |
| `EveLoginGate` | Component | Render children when authed, login form when not |
| `EveLoginForm` | Component | SSO + token paste login UI |
| `createEveClient(baseUrl?)` | Function | Fetch wrapper with Bearer injection |
| `getStoredToken()` / `storeToken()` / `clearToken()` | Functions | Direct sessionStorage access |

### Session Bootstrap Sequence

1. Check `sessionStorage` for cached token → validate via `GET /auth/me`
2. Fetch `GET /auth/config` to get `sso_url`
3. Probe `GET {sso_url}/session` (root-domain cookie) → get fresh token via Eve `/auth/exchange`
4. If no session → show login form

### Token Lifecycle

| Token | Storage | TTL | Refresh Path |
|-------|---------|-----|--------------|
| Eve RS256 access token | `sessionStorage` | 1 day | Re-probe SSO `/session` |
| SSO refresh cookie | httpOnly cookie (root domain) | 30 days | GoTrue refresh |
| GoTrue refresh token | httpOnly cookie (SSO broker) | 30 days | Re-login |

When the cached access token expires, the bootstrap re-probes the SSO session. If the SSO refresh token is also expired, the user sees the login form. No manual token refresh logic is needed in apps.

### App-Initiated Invite Redirects

Apps can create org-scoped email invites through the Eve API, then rely on the SSO exchange flow to land the invited user back in the app after password setup.

**Required permissions:**
- `orgs:invite` -- create and list org-scoped invites
- `orgs:members:read` -- list org members and query the member picker API

**Org-scoped invite API:**

```http
POST /orgs/:org_id/invites
GET /orgs/:org_id/invites
GET /orgs/:org_id/members/search?q=<prefix>
```

Invite payload fields:

| Field | Purpose |
|-------|---------|
| `email` | Invite target |
| `role` | Org role to grant on acceptance (`owner`, `admin`, `member`) |
| `send_email` | Send the GoTrue invite email immediately (default `true`) |
| `redirect_to` | Final app URL after onboarding completes |
| `app_context` | Opaque JSON for the originating app to persist with the invite |

Invite emails now enter through GoTrue's `/verify` path, which lands on the SSO root with the session tokens in the URL hash. When an invite is auto-applied during Supabase token exchange, Eve includes `invite_redirect_to` in the exchange response. The SSO callback uses it as a fallback redirect target when the email flow strips nested `redirect_to` query parameters, then sends invited users through `/set-password` before redirecting back to the app.

## Org Awareness (Auth-React)

`@eve-horizon/auth-react` exposes org memberships and provides org switching for multi-org apps.

```typescript
const { orgs, activeOrg, switchOrg } = useEveAuth();
```

| Field | Source | Persistence |
|-------|--------|-------------|
| `orgs` | `/auth/me` `memberships` field | Refreshed on session bootstrap |
| `activeOrg` | First org from `orgs`, or restored from `localStorage` | `localStorage` (survives reload) |
| `switchOrg(orgId)` | Validates `orgId` is in `orgs` before switching | Updates `localStorage` |

`user.orgId` continues to work for single-org apps. The `orgs` / `activeOrg` fields are additive — apps that don't reference them are unaffected.

## Auto-Injected Environment Variables

The platform deployer injects these into every deployed app:

| Variable | Purpose |
|----------|---------|
| `EVE_API_URL` | Internal API URL (JWKS fetch, remote verify) |
| `EVE_PUBLIC_API_URL` | Public-facing API URL |
| `EVE_SSO_URL` | SSO broker URL (`eveAuthConfig()` response) |
| `EVE_ORG_ID` | Org membership check |

Use `${SSO_URL}` in manifest env blocks for frontend-accessible SSO URL:

```yaml
services:
  web:
    environment:
      NEXT_PUBLIC_SSO_URL: "${SSO_URL}"
```

## JWT `orgs` Claim

User tokens include an `orgs` array populated at mint time:

```json
{
  "sub": "user_xxx",
  "type": "user",
  "orgs": [
    { "id": "org_ManualTestOrg", "role": "owner" },
    { "id": "org_Incept5", "role": "admin" }
  ]
}
```

Limited to 50 most-recent memberships (`EVE_AUTH_ORGS_CLAIM_LIMIT`). The claim can become stale if membership changes after token mint. With the default 1-day TTL this is acceptable. For immediate revocation, use `strategy: 'remote'`.

## Project Role Resolution

The Eve API `/auth/me` endpoint supports an optional `X-Eve-Project-Id` header. When present, it resolves the user's project-level role from the `project_memberships` table and returns it as `project_role`:

```json
{
  "user_id": "user_abc",
  "email": "alice@co.com",
  "org_id": "org_xyz",
  "role": "admin",
  "memberships": [{ "org_id": "org_xyz", "role": "admin" }],
  "project_role": "owner"
}
```

`project_role` is `null` if the user has no explicit project membership.

### Backend: Resolve Project Role

Use `eveAuthMe()` with the `projectHeader` option to automatically forward the project context to the Eve API:

```typescript
app.get('/auth/me', eveAuthMe({ projectHeader: 'x-eve-project-id' }));
```

When the frontend sends `X-Eve-Project-Id`, the handler proxies to the Eve API and returns the response including `project_role`.

### Frontend: Send Project Context

Pass `projectId` to `EveAuthProvider` to include the header in `/auth/me` requests:

```tsx
<EveAuthProvider apiUrl="/api" projectId={currentProjectId}>
  <App />
</EveAuthProvider>
```

The resolved project role is available on `user.projectRole`:

```typescript
const { user } = useEveAuth();
if (user?.projectRole === 'owner' || user?.projectRole === 'admin') {
  // editor access
}
```

### Custom App-Level Roles

Apps that need roles beyond `owner/admin/member` (e.g. `editor/viewer`) should map platform roles in middleware:

```typescript
app.use((req, _res, next) => {
  if (req.eveUser) {
    const orgRole = req.eveUser.role;
    const projectRole = req.eveUser.projectRole;
    // Org owners/admins are always editors
    if (['owner', 'admin'].includes(orgRole)) {
      req.appRole = 'editor';
    } else {
      // Map project role or default to viewer
      req.appRole = projectRole && ['owner', 'admin'].includes(projectRole) ? 'editor' : 'viewer';
    }
  }
  next();
});
```

## Migration from Custom Auth

Replace ~750 lines of hand-rolled auth with ~50 lines:

| Delete | Replacement |
|--------|-------------|
| JWKS setup, org check, role mapping | `eveUserAuth()` |
| Bearer extraction middleware | Built into `eveUserAuth()` |
| Route protection guard | `eveAuthGuard()` |
| SSO URL discovery (api. → sso. hack) | `eveAuthConfig()` reads `EVE_SSO_URL` |
| Frontend `useAuth` hook | `useEveAuth()` |
| Token storage and Bearer injection | `createEveClient()` |
| Login form | `EveLoginGate` / `EveLoginForm` |

## NestJS Integration

Wrap the Express middleware in a thin NestJS guard:

```typescript
import { CanActivate, ExecutionContext, Injectable } from '@nestjs/common';

@Injectable()
export class EveGuard implements CanActivate {
  canActivate(ctx: ExecutionContext): boolean {
    return !!ctx.switchToHttp().getRequest().eveUser;
  }
}
```

## SSE Authentication

The middleware supports `?token=` query parameter for Server-Sent Events:
```
GET /api/events?token=eyJ...
```

## Implementation Pattern (NestJS + React)

Distilled from a real migration (sentinel-mgr: 777 lines of custom auth replaced by ~50 lines of SDK usage).

**Backend — `main.ts`:**
Apply `eveUserAuth()` as global Express middleware. If the app has existing controllers that expect a different shape on `req.user`, add a thin bridge middleware to map fields:

```typescript
app.use(eveUserAuth());
app.use((req, _res, next) => {
  if (req.eveUser) {
    req.user = {
      id: req.eveUser.id,
      org_id: req.eveUser.orgId,
      email: req.eveUser.email,
      role: req.eveUser.role === 'member' ? 'viewer' : 'admin',
    };
  }
  next();
});
```

**Backend — Auth config + /auth/me controllers:**
Wrap `eveAuthConfig()` and `eveAuthMe()` in NestJS controllers:

```typescript
@Controller()
export class AuthConfigController {
  private configHandler = eveAuthConfig();
  private meHandler = eveAuthMe({ projectHeader: 'x-eve-project-id' });

  @Get('auth/config')
  getConfig(@Req() req, @Res() res) { this.configHandler(req, res); }

  @Get('auth/me')
  getMe(@Req() req, @Res() res) { this.meHandler(req, res); }
}
```

**Backend — NestJS guard:**
The existing `AuthGuard` checks `req.user` (or `req.eveUser`) — no SDK import needed in the guard itself, because `eveUserAuth()` already ran as global middleware upstream.

**Frontend — Custom `AuthGate`:**
Rather than using the built-in `EveLoginGate`, wrap `useEveAuth()` to control loading/login/app rendering with your own UI:

```tsx
function AuthGate() {
  const { user, loading, error, loginWithToken, loginWithSso, logout } = useEveAuth();
  if (loading) return <Spinner />;
  if (!user) return <LoginPage onLoginWithToken={loginWithToken} onStartSsoLogin={loginWithSso} />;
  return <AppShell user={user} onLogout={logout}>...</AppShell>;
}

export default function App() {
  return (
    <EveAuthProvider apiUrl={API_BASE}>
      <AuthGate />
    </EveAuthProvider>
  );
}
```

**Key takeaways:**
- `eveUserAuth()` goes in `main.ts` as global middleware — every request gets token parsing
- Bridge middleware lets you adopt the SDK without rewriting every controller that reads `req.user`
- `eveAuthConfig()` replaces hand-rolled SSO URL discovery (no more `api. -> sso.` hostname hacks)
- Frontend uses `useEveAuth()` for full control, or `EveLoginGate` for zero-config login gating
