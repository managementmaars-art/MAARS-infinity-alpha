# PMA-Web Runtime And Data

## State Boundaries

- TanStack Query owns request lifecycle, caching, retries, and invalidation.
- Zustand is for UI-only interaction state.
- Do not mirror server data into Zustand without a clear reason.

## Query Client

Use a shared query client module with stable defaults:

```typescript
import { QueryClient } from "@tanstack/react-query";

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60_000,
      retry: 1,
    },
  },
});
```

Tune defaults per product; do not scatter ad hoc query config across unrelated components.

## HTTP Client

- Centralize fetch logic in `shared/lib/http.ts`.
- Use `/api` as the default base path unless the repo already standardizes differently.
- Normalize error handling, headers, and JSON parsing in one place.
- Keep feature `api.ts` files thin wrappers around shared transport.

## i18n

Use only when the product needs multiple locales.

Recommended stack:

- `react-i18next`
- `i18next-http-backend`
- `i18next-browser-languagedetector`

Rules:

- keep locale files under `public/locales/{{lng}}/{{ns}}.json`
- initialize in `app/i18n.ts`
- mount through `I18nextProvider`
- set fallback language based on the product's primary language
- use detection order such as `localStorage -> navigator`

## Vite Configuration

Use Vite 8 defaults that match the repo layout:

```typescript
import devServer from "@hono/vite-dev-server";
import tailwindcss from "@tailwindcss/vite";
import { TanStackRouterVite } from "@tanstack/router-plugin/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";
```

Recommended rules:

- enable `resolve.tsconfigPaths: true`
- point TanStack Router plugin at `src/app/routes`
- keep server host on `0.0.0.0`
- enable `allowedHosts: true` only when required by the dev environment

## Backend Integration In Dev

When the repo uses Hono for local API work:

- use `@hono/vite-dev-server`
- proxy or run only `/api/*` through the backend entry
- keep frontend and backend development on one Vite process when that reduces setup cost

## Shared Packages

Use `packages/shared` for:

- API response types
- shared enums and value objects
- constants reused by multiple apps

Keep shared packages dependency-light and prefer `import type` on the consuming side.
