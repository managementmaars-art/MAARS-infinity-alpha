# Project Conventions Template

Copy this file to your project's conventions directory as three separate files:
- `frontend.md`
- `backend.md`
- `database.md`

Place them under your agent's config folder:

| Agent | 路径 |
|-------|------|
| Claude Code | `.claude/conventions/` |
| Cursor | `.cursor/conventions/` |
| Windsurf | `.windsurf/conventions/` |
| Cline | `.cline/conventions/` |
| 通用 | `.agents/conventions/` |

Fill in the sections relevant to your project. spec-writer and the coding agent both read these before generating specs and writing code.

---

## frontend.md

```markdown
# Frontend Conventions

## Framework & Runtime
- Framework: [e.g. Next.js 14, Vite + React 18, Nuxt 3]
- Language: [TypeScript / JavaScript]
- Package manager: [npm / pnpm / yarn]

## Component Structure
- Component location: [e.g. src/components/, src/features/]
- Naming convention: [e.g. PascalCase, feature-scoped directories]
- State management: [e.g. Zustand, Jotai, Redux Toolkit, React Query]

## Styling
- System: [e.g. Tailwind CSS, CSS Modules, styled-components]
- Design tokens: [location or "none"]
- Component library: [e.g. shadcn/ui, MUI, "none"]

## Routing
- Router: [e.g. Next.js App Router, React Router v6]
- Route convention: [e.g. file-based, config-based]

## API Communication
- Client: [e.g. fetch, axios, tRPC, GraphQL]
- API base URL config: [e.g. NEXT_PUBLIC_API_URL env var]
- Auth: [e.g. JWT in Authorization header, cookie-based]

## Testing
- Unit: [e.g. Vitest, Jest + Testing Library]
- E2E: [e.g. Playwright, Cypress, agent-browser]
- Test file location: [e.g. alongside source, __tests__ directory]
```

---

## backend.md

```markdown
# Backend Conventions

## Runtime & Framework
- Runtime: [e.g. Node.js 20, Python 3.12, Go 1.22]
- Framework: [e.g. Express, Fastify, FastAPI, Gin]
- Language: [TypeScript / Python / Go]

## API Style
- Protocol: [REST / GraphQL / tRPC / gRPC]
- Versioning: [e.g. /api/v1/, header-based, "none"]
- Response format:
  ```json
  { "data": ..., "error": null }  // success
  { "data": null, "error": { "code": "...", "message": "..." } }  // error
  ```

## Authentication & Authorization
- Auth method: [e.g. JWT, session cookies, API keys]
- Token location: [e.g. Authorization header, httpOnly cookie]
- Permission model: [e.g. RBAC with roles: admin/user/guest]

## Error Handling
- HTTP status codes: [list conventions, e.g. 422 for validation]
- Error logging: [e.g. Pino, Winston, console.error]

## Service Structure
- Directory layout: [e.g. src/routes/, src/services/, src/models/]
- Dependency injection: [e.g. manual, inversify, "none"]

## Testing
- Framework: [e.g. Jest, pytest, Go test]
- Test DB: [e.g. SQLite in-memory, Postgres test database]
- Mocking: [e.g. MSW, unittest.mock]
```

---

## database.md

```markdown
# Database Conventions

## Database
- Type: [e.g. PostgreSQL 16, MySQL 8, SQLite, MongoDB]
- ORM/Query builder: [e.g. Prisma, Drizzle, SQLAlchemy, GORM]
- Migration tool: [e.g. Prisma Migrate, Flyway, Alembic, golang-migrate]

## Naming
- Tables: [e.g. snake_case plural — users, order_items]
- Columns: [e.g. snake_case — created_at, user_id]
- Foreign keys: [e.g. {table_singular}_id — user_id, order_id]
- Indexes: [e.g. idx_{table}_{column} — idx_users_email]
- Timestamps: [e.g. all tables have created_at, updated_at]

## Schema Conventions
- Soft delete: [e.g. deleted_at nullable timestamp / hard delete]
- IDs: [e.g. UUID v4, auto-increment bigint, CUID]
- Enums: [e.g. stored as VARCHAR, Postgres ENUM type, int with constants]

## Migration Rules
- Each migration is reversible (has up + down)
- Never rename columns in place — add new, backfill, drop old
- No multi-table migrations without explicit review
- Migration files: [e.g. timestamp prefix — 20240101_add_users_table.sql]

## Query Patterns
- N+1 prevention: [e.g. always use include/join for relations]
- Pagination: [e.g. cursor-based, offset/limit]
- Transactions: [e.g. use for any multi-table writes]
```
