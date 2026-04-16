---
name: pma-bun
description: Bun implementation guide for PMA-managed backend and full-stack monorepos. Covers Bun workspaces with `apps/*` and `packages/*`, API modules under `src/modules`, strict linting with ESLint + @antfu/eslint-config, Drizzle over SQLite-first storage, OpenAPIHono on top of `Bun.serve()`, validated env config, Vite dev integration, standalone binary compilation with embedded assets and migrations, and CI quality gates.
---

# Bun Project Implementation Guide

Use this skill together with `/pma`. `/pma` controls workflow, approval, and task tracking; this guide defines the implementation baseline after approval.

Keep this entry file small. Load only the relevant reference packs.

## Scope

For PMA-managed Bun backends, API services, internal tools, and Bun-based full-stack monorepos.

Not for frontend-only SPAs, Node-specific runtime guides, or non-PMA workflows.

## Loading Order

1. Always load `references/baseline.md` first.
2. Load `references/runtime.md` for bootstrap flow, config, root resolution, HTTP server, docs, logging, PID lock, and dev/prod split.
3. Load `references/data-and-testing.md` for Drizzle, SQLite-first storage, libSQL driver setup, migration fallback, repository patterns, and testing.
4. Load `references/delivery.md` for compile flow, embedded assets, CI gates, observability, Docker, security, and Git workflow.

## Quick Routing

- New Bun workspace setup or repo restructuring: `references/baseline.md`
- `app.ts` / `index.ts` / `dev.ts`, OpenAPIHono, config, startup, graceful shutdown, logging, PID lock: `references/runtime.md`
- Schema design, SQLite setup, migration embedding, repositories, test setup: `references/data-and-testing.md`
- Compile pipeline, binary delivery, static assets, CI, Docker, PR readiness: `references/delivery.md`

## Reference Packs

- `references/baseline.md`
  Scope, workspace defaults, required quality gates, project layout, scripts, conventions, and implementation workflow.
- `references/runtime.md`
  Formatting and TypeScript defaults, config loading, bootstrap structure, OpenAPIHono setup, middleware, logging, docs routes, and runtime lifecycle.
- `references/data-and-testing.md`
  Drizzle with SQLite-first storage, migration strategy, repository boundaries, and testing rules.
- `references/delivery.md`
  Compile pipeline, security patterns, observability, CI pipeline, Docker, workspace rules, and Git conventions.

If the repository intentionally diverges, keep the deviation explicit in the proposal and consistent across scripts, docs, and CI.
