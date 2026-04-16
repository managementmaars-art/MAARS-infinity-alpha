# PMA-Web Baseline

## Scope

This skill is for PMA-managed SPA and internal-tool web applications using:

- React 19 + TypeScript + Vite 8
- TanStack Router
- TanStack Query
- Zustand
- shadcn/ui plus Tailwind CSS v4

Use `/pma` for workflow control. Use this pack for implementation defaults.

## Tech Stack

### Required

| Category | Technology | Version | Notes |
|---|---|---|---|
| Framework | React | 19 | default app framework |
| Language | TypeScript | 5.9+ | strict mode |
| Build tool | Vite | 8 | `host: "0.0.0.0"`, `allowedHosts: true` |
| Styling | Tailwind CSS | 4 | `@theme` plus CSS variables in oklch |
| Server state | TanStack Query | 5 | owns request lifecycle |
| Lint / format | ESLint + @antfu/eslint-config | 8+ | no Prettier; see notes below |
| Test | Vitest | 4 | unit and integration tests |

#### @antfu/eslint-config notes

- **v8+** requires `@eslint-react/eslint-plugin` v3. Ensure the project does not pin v2.
- **v7+** enables `react/prefer-namespace-import` by default — use `import * as React from 'react'` instead of `import React from 'react'`, or explicitly disable the rule in eslint config.
- The config is flat-config native. Do not use legacy `.eslintrc` format.

### Default

| Category | Technology | Notes |
|---|---|---|
| Package manager | bun workspaces | monorepo workspace management |
| Router | TanStack Router | file-based routing with generated route tree |
| Client state | Zustand | UI-only local state |
| UI | shadcn/ui | `base-nova` style with `@base-ui/react` primitives |
| Theming | ThemeProvider pattern | light, dark, system |
| Icons | lucide-react | consistent icon set |
| HTTP client | `shared/lib/http.ts` | typed fetch wrapper with `/api` base URL |
| API dev server | `@hono/vite-dev-server` | in-process backend for local development |

### Optional

| Category | Technology | When to adopt |
|---|---|---|
| i18n | react-i18next + i18next-http-backend | multi-locale products |
| Forms | react-hook-form | complex form validation |
| E2E test | Playwright | critical user flows |
| Fonts | @fontsource-variable | self-hosted variable fonts |

### Alternative

| Replaces | Technology | Notes |
|---|---|---|
| bun workspaces | pnpm workspaces | use consistently across docs and CI |
| react-i18next | LinguiJS | smaller bundle, compile-time approach |
| `@base-ui/react` | Radix UI | change shadcn setup consistently |

## Required Quality Gates

Every PMA-Web project should define:

- `bun run lint`
- `bun run typecheck`
- `bun run build`
- `bun run test`
- accessibility review for changed UI
- security review for changed auth, env usage, or unsafe rendering paths

If a repo is missing a gate, add it instead of leaving verification implicit.

## Monorepo Structure

```text
package.json                       # workspaces: ["apps/*", "packages/*"]
apps/
  web/
    src/
      main.tsx
      index.css
      app/
        providers.tsx
        i18n.ts
        routeTree.gen.ts
        routes/
      features/
      shared/
      styles/
    public/
      locales/
    vite.config.ts
    components.json
packages/
  config/
    tsconfig/
      base.json
      react.json
  shared/
    src/
      index.ts
```

## Required Conventions

| Area | Convention |
|---|---|
| Entry point | `main.tsx` creates router and renders providers |
| Routing | `src/app/routes/` with generated `routeTree.gen.ts` |
| Providers | composed in `app/providers.tsx` |
| API layer | each feature exposes `useXxxQuery` and `useXxxMutation` |
| HTTP client | centralized in `shared/lib/http.ts` |
| Server state | TanStack Query owns it |
| Client state | Zustand only for UI and interaction state |
| Components | shared UI primitives in `src/shared/components/ui/` |
| Imports | use `import type` where applicable |
| Naming | kebab-case files, PascalCase components |
| Aliases | `@/` maps to `src/` |
| Generated code | do not hand-edit `routeTree.gen.ts` blindly |

## Workspace Management

Default:

- use Bun workspaces
- use `workspace:*` for cross-package references
- keep root scripts and app-local scripts predictable

Alternative:

- use pnpm workspaces only when the repo already standardizes on pnpm
- update install, run, and CI commands consistently

## Baseline Scripts

Each PMA-Web app should expose at least:

```json
{
  "scripts": {
    "dev": "bunx --bun vite",
    "build": "vite build",
    "preview": "vite preview",
    "typecheck": "tsc --noEmit",
    "test": "vitest run"
  }
}
```
