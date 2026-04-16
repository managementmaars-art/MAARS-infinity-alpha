# PMA-Bun Baseline

## Scope

Use this pack for PMA-managed Bun backends, API services, and Bun-based full-stack monorepos.

Goals:

- Bun-native runtime and workspace conventions
- strict TypeScript with zero `any`
- explicit module and bootstrap boundaries
- reproducible builds with lockfile and predictable scripts
- operational and security conventions that are easy to review

## Tech Stack

### Required

| Category | Technology | Notes |
|---|---|---|
| Runtime | Bun 1.2+ | latest stable |
| Language | TypeScript 5.9+ | strict mode, `noUncheckedIndexedAccess` |
| Package manager | bun | commit `bun.lock` |
| Lint / format | ESLint + @antfu/eslint-config | no Prettier |
| Validation | Zod 3 | API-boundary validation |
| Errors | typed error classes | `AppError` hierarchy at transport boundaries |
| Test | bun:test | built-in runner |

### Default

| Category | Technology | Notes |
|---|---|---|
| HTTP server | OpenAPIHono | from `@hono/zod-openapi` |
| API docs | `@scalar/hono-api-reference` | serve docs at `/docs` |
| Data access | Drizzle ORM + drizzle-kit | schema-as-code |
| Database | SQLite | default for local-first internal services |
| Driver | libSQL client + Drizzle | supports file DB plus encryption features when needed |
| Config | environment variables + Zod | validate at startup |
| Logging | consola + pino | console plus structured file output |
| Hot reload | `bun --watch` + Vite integration | API-only or full-stack development |

### Optional

| Category | Technology | When to adopt |
|---|---|---|
| Observability | OpenTelemetry | production tracing and metrics |
| Queue | BullMQ | background jobs |
| Cache | Redis | shared cache |
| CLI | Commander.js | richer command surface |
| E2E test | Playwright | browser-level flows |
| Process lock | PID lock file | prevent duplicate listeners |
| Single binary | `bun build --compile` | embed assets and migrations |

### Alternative

| Replaces | Technology | Notes |
|---|---|---|
| OpenAPIHono | plain Hono | lighter when OpenAPI generation is unnecessary |
| OpenAPIHono | Elysia | Bun-native alternative |
| SQLite | PostgreSQL via `postgres` or managed libSQL | multi-instance writes or shared DB needs |
| Drizzle ORM | Prisma | heavier but broader ORM feature set |
| consola + pino | pino only | headless services |
| ESLint | Biome | faster, smaller ecosystem |

## Required Quality Gates

Every PMA-Bun project should expose:

- `bun run lint`
- `bun run typecheck`
- `bun run build`
- `bun test`
- `bun test --coverage` or package-local coverage equivalent
- security review for auth, secrets, outbound HTTP, and config changes

For monorepos, also expose a root `check` command that sequences the main gates.

## Monorepo Layout

```text
package.json
apps/
  api/
    package.json
    tsconfig.json
    drizzle.config.ts
    src/
      app.ts
      index.ts
      dev.ts
      config.ts
      root.ts
      pid-lock.ts
      db/
      modules/
      shared/
    drizzle/
  web/
    package.json
    vite.config.ts
packages/
  config/
  shared/
scripts/
  compile.ts
```

For smaller API-only services, flatten the workspace if needed, but keep the same role split: bootstrap, db, modules, and shared cross-cutting code.

## API Layout

```text
src/
  app.ts
  index.ts
  dev.ts
  config.ts
  root.ts
  pid-lock.ts
  db/
    index.ts
    schema.ts
    embedded-migrations.ts
  modules/
    health/
    docs/
    <domain>/
  shared/
    lib/
    middleware/
    static-assets.ts
```

## Required Conventions

| Area | Convention |
|---|---|
| Workspace layout | `apps/*` for runnable apps, `packages/*` for shared config and code |
| Project layout | `src/modules/` for domain modules, `src/shared/` for cross-cutting concerns |
| Module structure | co-locate routes, service, types, and tests; keep transport thin |
| Bootstrap split | `app.ts` builds the app, `index.ts` runs production startup, `dev.ts` bridges dev integration |
| Errors | never throw raw strings |
| Validation | Zod at boundaries |
| Config | never read `Bun.env` directly in business logic |
| Database | parameterized queries only |
| Logging | no `console.log` in production paths |
| Imports | prefer `import type` for type-only imports |
| Aliases | use `@/*` only when it maps to the real `src/` tree |

## Code Quality Standards

- prefer immutable updates
- keep functions under 50 lines when possible
- keep files focused and usually under 800 lines
- avoid deep nesting
- avoid hardcoded values when config or constants fit better
- no `any` in application code

## Baseline Scripts

At the workspace root:

```json
{
  "scripts": {
    "dev": "bun run --filter <web-app> dev",
    "lint": "eslint apps/ packages/ --ext .ts,.tsx",
    "typecheck": "bun run --filter '*' typecheck",
    "test": "bun run --filter '*' test",
    "build": "bun run --filter '*' build",
    "check": "bun run lint && bun run typecheck && bun run test && bun run build"
  }
}
```

For the API package:

```json
{
  "scripts": {
    "dev": "bun --watch src/index.ts",
    "build": "bun build src/index.ts --outdir dist --target bun --minify",
    "start": "bun dist/index.js",
    "typecheck": "tsc --noEmit",
    "test": "bun test",
    "test:coverage": "bun test --coverage",
    "db:generate": "drizzle-kit generate"
  }
}
```

## Implementation Workflow

Within approved implementation work:

1. Research and reuse existing libraries first.
2. Plan interfaces and failure modes before coding.
3. Keep module boundaries explicit before adding new routes or services.
4. Run review passes focused on correctness, security, and missing tests.
