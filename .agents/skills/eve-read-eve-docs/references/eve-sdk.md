# Eve SDK

## Use When
- You need to add authentication to an Eve-deployed app (backend, frontend, or fullstack).
- You need to know which SDK packages exist and what they export.
- You need the quick-start install and wiring pattern for a new app.
- You need to understand the token flow between browser, backend, and Eve platform.

## Load Next
- `references/auth-sdk.md` for deep auth coverage: middleware behavior, verification strategies, token types, NestJS patterns, session bootstrap sequence, migration guide.
- `references/secrets-auth.md` for platform auth model, identity providers, and access control.
- `references/manifest.md` for environment variable interpolation in manifests.

## Ask If Missing
- Confirm whether the app is backend-only, frontend-only, or fullstack.
- Confirm the backend framework (Express or NestJS).
- Confirm whether the app serves browser users, agent jobs, or both.

## Overview

The Eve SDK is two npm packages that eliminate auth boilerplate in Eve-deployed apps.

| Package | Runtime | Purpose |
|---------|---------|---------|
| `@eve-horizon/auth` | Node.js (Express / NestJS) | Token verification, org membership, route protection |
| `@eve-horizon/auth-react` | Browser (React) | SSO session management, login UI, token cache |

## Install

```bash
# Backend
npm install @eve-horizon/auth

# Frontend
npm install @eve-horizon/auth-react
```

## Quick-Start: Backend (Express)

```typescript
import { eveAuth, eveIdentityGuard, eveAuthConfig, eveAuthMe } from '@eve-horizon/auth';

app.use(eveAuth());                                         // Parse any Eve token (non-blocking)
app.get('/auth/config', eveAuthConfig());                   // Serve SSO discovery
app.get('/auth/me', eveAuthMe());                           // Full /auth/me for React SDK
app.use('/api', eveIdentityGuard());                        // Protect all API routes
```

Use `eveAuth()` for apps serving both users and agents (most Eve apps). It normalizes both token types into `req.eveIdentity`. See `auth-sdk.md` for the full middleware comparison.

## Quick-Start: Frontend (React)

```tsx
import { EveAuthProvider, EveLoginGate, useEveAuth } from '@eve-horizon/auth-react';

function App() {
  return (
    <EveAuthProvider apiUrl="/api">
      <EveLoginGate>
        <Dashboard />
      </EveLoginGate>
    </EveAuthProvider>
  );
}

function Dashboard() {
  const { user, logout } = useEveAuth();
  return <div>Welcome {user?.email} <button onClick={logout}>Sign out</button></div>;
}
```

## Token Flow

1. User visits app -- `EveAuthProvider` checks `sessionStorage` for a cached token.
2. No cached token -- probes SSO broker `/session` using root-domain cookie.
3. SSO session exists -- receives fresh Eve RS256 token, caches in `sessionStorage`.
4. No SSO session -- shows login form (SSO redirect or token paste).
5. All API requests include `Authorization: Bearer <token>` header.

## Backend Exports

| Export | Type | Description |
|--------|------|-------------|
| `eveAuth(options?)` | Middleware | **Recommended.** Unified auth for user + agent tokens, attach `req.eveIdentity` (non-blocking) |
| `eveIdentityGuard()` | Middleware | Return 401 if `req.eveIdentity` not set |
| `eveUserAuth(options?)` | Middleware | User-only token verification, attach `req.eveUser` (non-blocking) |
| `eveAuthGuard()` | Middleware | Return 401 if `req.eveUser` not set |
| `eveAuthConfig()` | Handler | Serve `{ sso_url, eve_api_url, ... }` from env vars |
| `eveAuthMe(options?)` | Handler | Full `/auth/me` — memberships + project role for React SDK |
| `eveAuthMiddleware(options?)` | Middleware | Agent/job token verification (blocking), attach `req.agent` |
| `verifyEveToken(token, url?)` | Function | JWKS-based local verification (15-min cache) |
| `verifyEveTokenRemote(token, url?)` | Function | HTTP verification via `/auth/token/verify` |

## Frontend Exports

| Export | Type | Description |
|--------|------|-------------|
| `EveAuthProvider` | Component | Context provider, session bootstrap. Props: `apiUrl?`, `projectId?` |
| `useEveAuth()` | Hook | `{ user, loading, orgs, activeOrg, switchOrg, loginWithSso, loginWithToken, logout }` |
| `EveLoginGate` | Component | Render children when authed, login form when not |
| `EveLoginForm` | Component | SSO + token paste login UI |
| `createEveClient(baseUrl?)` | Function | Fetch wrapper with automatic Bearer injection |
| `getStoredToken()` / `storeToken()` / `clearToken()` | Functions | Direct sessionStorage access |

## Environment Variables

Auto-injected by the Eve deployer into every deployed app. No manual configuration needed.

| Variable | Used By | Purpose |
|----------|---------|---------|
| `EVE_API_URL` | `@eve-horizon/auth` | JWKS fetch, remote token verification |
| `EVE_ORG_ID` | `@eve-horizon/auth` | Org membership check |
| `EVE_SSO_URL` | Both | Auth config discovery, SSO session probe |
| `EVE_PUBLIC_API_URL` | Both | Public-facing API URL (optional) |

## Common Patterns

### Backend-Only API (Agent Jobs)

For APIs that only serve agent jobs with no browser users:

```typescript
import { eveAuthMiddleware } from '@eve-horizon/auth';

app.use('/api', eveAuthMiddleware({ strategy: 'local' }));

app.get('/api/data', (req, res) => {
  console.log(req.agent.project_id, req.agent.job_id);
});
```

### Fullstack React App

Combine both packages for SSO login with protected API routes:

```typescript
// Backend
app.use(eveUserAuth());
app.get('/auth/config', eveAuthConfig());
app.get('/auth/me', eveAuthMe());
app.use('/api', eveAuthGuard());
```

```tsx
// Frontend
import { EveAuthProvider, EveLoginGate, createEveClient } from '@eve-horizon/auth-react';

const client = createEveClient('/api');
const res = await client.fetch('/data');
```

### SSE Authentication

The middleware supports `?token=` query parameter for Server-Sent Events:

```
GET /api/events?token=eyJ...
```

## Deep Auth Reference

For middleware behavior details, verification strategies (`local` vs `remote`), token types (`EveUser` / `EveTokenClaims`), NestJS guard patterns, session bootstrap sequence, token lifecycle and TTLs, `orgs` claim mechanics, and migration from custom auth, see `references/auth-sdk.md`.
