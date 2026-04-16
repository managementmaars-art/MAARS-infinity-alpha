---
name: pma-web
description: Frontend implementation guide for PMA-managed React 19 + TypeScript + Vite 8 monorepo projects. Covers repository layout, required quality gates, file-based type-safe routing with TanStack Router, state conventions (TanStack Query + Zustand), shadcn/ui (Base UI + base-nova style) + Tailwind CSS v4 patterns, Vitest 4 testing, dual-channel theming, i18n, Vite dev server integration with backend, and delivery rules for frontend applications.
---

# Web Frontend Implementation Guide

Use this skill together with `/pma`. `/pma` controls workflow, approval, and task tracking; this guide defines the implementation baseline after work is approved.

Keep this entry file lean. Load only the reference packs needed for the current task.

## Scope

For PMA-managed SPA and internal-tool frontend projects using:

- React 19 + TypeScript + Vite 8
- TanStack Router for file-based type-safe routing
- TanStack Query for server state
- Zustand for UI-only client state
- shadcn/ui with `@base-ui/react` primitives and Tailwind CSS v4

Not for SSR-first sites, content sites, or non-PMA projects.

## Loading Order

1. Always load `references/baseline.md` first.
2. Load `references/routing-and-ui.md` when touching route structure, providers, theming, Tailwind, or shadcn/ui.
3. Load `references/runtime-and-data.md` when touching API integration, query state, i18n, Vite config, or frontend-backend dev integration.
4. Load `references/review.md` when touching release checks, tests, accessibility, or security-sensitive UI behavior.

## Quick Routing

- New app setup or repo restructuring: `references/baseline.md`
- Router, layouts, providers, entrypoint, shadcn, Tailwind, theme: `references/routing-and-ui.md`
- HTTP client, query client, i18n, Vite dev server, API proxying: `references/runtime-and-data.md`
- Lint, typecheck, build, test, accessibility, UI security review: `references/review.md`

## Reference Packs

- `references/baseline.md`
  Stack defaults, quality gates, workspace layout, conventions, and baseline scripts.
- `references/routing-and-ui.md`
  TanStack Router layout, provider composition, entry point, shadcn/ui, Tailwind v4, and theming.
- `references/runtime-and-data.md`
  Query client, HTTP layer, state boundaries, i18n, and Vite dev-server integration with backend APIs.
- `references/review.md`
  Verification gates and the accessibility and security review checklist for UI changes.

If the project intentionally diverges from these defaults, keep the divergence explicit in the proposal and match the repository's existing patterns consistently.
