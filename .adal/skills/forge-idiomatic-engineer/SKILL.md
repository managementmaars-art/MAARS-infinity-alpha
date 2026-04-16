---
name: forge-idiomatic-engineer
description: "Forge-focused engineering workflow for Rust apps with generated frontend bindings. Activate when the repo contains `forge.toml`, Forge macros, or Forge CLI-driven generation."
---

# Forge Idiomatic Engineer

## What is Forge

Forge is a full-stack Rust framework. Everything compiles into a single binary backed by PostgreSQL. There is no separate API server, job runner, or cron scheduler -- one binary does it all.

The framework is macro-driven. You write annotated Rust functions and Forge generates the runtime wiring, frontend bindings, and type-safe clients.

**Core abstractions:**

| Concept | Purpose | Macro | Registration |
|---|---|---|---|
| Query | Read data | `#[forge::query]` | `.register_query::<FnNameQuery>()` |
| Mutation | Write data | `#[forge::mutation]` | `.register_mutation::<FnNameMutation>()` |
| Job | Background task | `#[forge::job]` | `.register_job::<FnNameJob>()` |
| Cron | Scheduled task | `#[forge::cron]` | `.register_cron::<FnNameCron>()` |
| Workflow | Durable multi-step | `#[forge::workflow]` | `.register_workflow::<FnNameWorkflow>()` |
| Daemon | Long-running process | `#[forge::daemon]` | `.register_daemon::<FnNameDaemon>()` |
| Webhook | External events | `#[forge::webhook]` | `.register_webhook::<FnNameWebhook>()` |
| MCP Tool | AI agent tool | `#[forge::mcp_tool]` | `.register_mcp_tool::<FnNameMcpTool>()` |

Naming rule: PascalCase of the function name + type suffix. Declare handlers as `pub async fn` so generated structs are accessible via `functions::StructName`. Avoid redundant suffixes (e.g., `heartbeat` not `heartbeat_daemon`).

Every handler must be registered in `src/main.rs`. Macros alone do not make handlers reachable.

## Workflow

### 1. Orient

Read `forge.toml` and `Cargo.toml` to understand the project shape. Check `src/main.rs` for registered handlers. For frontend work, check `frontend/package.json` (SvelteKit) or `frontend/Cargo.toml` (Dioxus).

### 2. Build backend first

Make the backend contract real, add tests, then run `forge generate` to produce frontend bindings. Wire the frontend against the generated output. Never hand-edit generated files (`frontend/src/lib/forge/*` or `frontend/src/forge/*`).

### 3. Verify after every change

Run `forge check` after every backend change, not just at the end. It validates formatting, clippy, SQLx cache, and frontend bindings in one command. If it fails, fix the issue before moving on. For UI changes, also run `forge test` for Playwright coverage.

### 4. Stop on blockers

If a port is occupied, DB is unreachable, or a tool is missing: report it and stop. Do not kill processes, change ports, or invent workarounds.

## When to load references

**Always load `references/pitfalls.md` AND `references/resilience.md` before starting any implementation.** Pitfalls contains critical mistakes; resilience contains patterns for handling failure modes. Both are mandatory reading.

| Working on | Load |
|---|---|
| Any new feature or handler | `references/resilience.md` (mandatory) |
| Macro attributes, context methods, error types, config | `references/api.md` |
| Jobs, workflows, crons, daemons, auth, testing, deploys | `references/patterns.md` |
| Frontend patterns (shared principles) | `references/frontend.md` |
| SvelteKit: stores, runes, bindings | `references/frontend/svelte.md` |
| Dioxus: hooks, signals, bindings | `references/frontend/dioxus.md` |
| Writing tests (especially failure cases) | `references/testing.md` |
| Common mistakes, build failures, runtime errors | `references/pitfalls.md` |

## Key principles

**Murphy's Law drives everything.** Anything that can go wrong will go wrong. Users will lose auth mid-action. Entities will be deleted while being viewed. Networks will drop during mutations. Tokens will expire at the worst moment. Jobs will reference data that no longer exists. Two users will edit the same thing simultaneously. Design every handler assuming the worst happens. Never trust that prior state still holds. Check existence, handle conflicts, degrade gracefully, inform the user.

**Compile-time checked SQL only.** Always use `sqlx::query!()` and `sqlx::query_as!()` macros. Never use the runtime forms (`sqlx::query()`, `sqlx::query_as::<_, T>()`). Compile-time checking catches typos, type mismatches, and missing columns before deployment. After adding or modifying queries, run `forge migrate prepare` to regenerate the `.sqlx/` cache, then `forge check` to verify.

**Thin vertical slices.** Make the smallest change that solves the problem. Do not upgrade a bug fix into a redesign.

**Tests close to code.** Handlers get `#[cfg(test)] mod tests` in the same file. Test the weird cases by name. Bug fix means regression test. UI change means Playwright test (import `test` from `tests/fixtures.ts`).

**Boundary validation at handler entry.** Validate inputs at the handler level. Use `ForgeError` types, not panics. Never `unwrap()` or `expect()` in handler code -- use `?`.

**Never edit generated files.** If generated output is wrong, fix the Rust source or the codegen.

**User scoping is enforced at compile time.** Private queries must filter by `user_id` or `owner_id` in SQL. Use `ctx.user_id()` to get the authenticated user's UUID. The macro rejects queries that touch tables without identity filtering. Use `#[query(unscoped)]` to opt out for shared or admin data.

**Transactional integrity.** Never call `dispatch_job` or `start_workflow` outside a `transactional` mutation. Without it, jobs execute against uncommitted data.

**Migrations use markers.** Write `-- @up` / `-- @down` in migration files. Do not edit `forge_migrations` directly. Enable reactivity with `SELECT forge_enable_reactivity('table_name')`, never hand-write PG triggers.

**No fake inputs.** If a handler has no business input, omit the parameter. No `Option<()>`, `()`, or dummy structs.

**Test failures, not just success.** Every handler needs tests for: missing auth, wrong role, missing entity, invalid input, constraint violations, concurrent modification. If you only have time for one test, write the failure test. Success paths are obvious; graceful failure is not.

**Every query must handle "not found".** Use `fetch_optional` + `ok_or_else(|| ForgeError::NotFound(...))`. Never assume the entity exists just because the user has an ID for it. Include the ID in error messages so users can report issues.

**Frontend must survive stale state.** User views item, another user deletes it, first user acts on it. SSE pushes update for entity that no longer exists. Token expires during a mutation. Handle all of these gracefully with clear user feedback, not console errors or blank screens.

## Output contract

For implementation: what changed, failure modes handled (list each), tests added (including failure tests), commands run, blockers hit, `forge check` result.

For review: findings with file references, failure modes identified, resilience gaps, assumptions, short summary.

Before marking complete, verify against the resilience checklist in `references/resilience.md`. Every handler must answer: "What happens when auth is revoked? When the entity is deleted? When another user modifies it? When the network drops?"
