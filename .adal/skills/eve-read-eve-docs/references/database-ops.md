# Database Operations

## Use When
- You need to provision, inspect, or manage environment databases.
- You need to run migrations, SQL queries, or schema inspections.
- You need managed DB status, credential rotation, or scaling.
- You need to set up RLS policies with group-aware helpers.

## Load Next
- `references/manifest.md` for managed DB declaration in `x-eve.role: managed_db`.
- `references/deploy-debug.md` for environment-level diagnostics.
- `references/secrets-auth.md` for DB credential secrets and interpolation.

## Ask If Missing
- Confirm the environment name and project context.
- Confirm access mode: `--env` (API-proxied) or `--url` (direct connection).
- Confirm whether this is a managed DB or a self-hosted database.

## Managed DB Provisioning

Declare a managed database in the manifest:

```yaml
services:
  db:
    x-eve:
      role: managed_db
      managed:
        class: db.p1
        engine: postgres
        engine_version: "16"
```

Provisioning occurs automatically when an environment is deployed. Managed DB services are not rendered into K8s manifests.

### Tiers

| Class | Description |
|---|---|
| `db.p1` | Starter (shared resources) |
| `db.p2` | Standard (dedicated CPU) |
| `db.p3` | Performance (dedicated CPU + memory) |

### Interpolation

Reference managed DB values in environment blocks:

```yaml
environment:
  DATABASE_URL: ${managed.db.url}
  DB_HOST: ${managed.db.host}
  DB_PASSWORD: ${managed.db.password}
```

Available fields: `url`, `host`, `port`, `database`, `username`, `password`.

## Status + Credential Rotation

```bash
eve db status --env <name>                          # Managed DB status and tenant readiness
eve db rotate-credentials --env <name>              # Rotate managed DB credentials
```

Always check `eve db status` before relying on managed values. Rotation replaces credentials and updates the stored secret -- redeploy services to pick up new values.

## Migrations

### Create a Migration

```bash
eve db new <description> [--path db/migrations]
```

Creates `YYYYMMDDHHmmss_description.sql` in `db/migrations/` (default).

### Run Migrations

```bash
eve db migrate --env <name> [--path db/migrations]          # API-proxied
eve db migrate --url <postgres-url> [--path db/migrations]  # Direct connection
```

### List Applied

```bash
eve db migrations --env <name>
```

### Conventions

- Migration files: `YYYYMMDDHHmmss_description.sql` format.
- Default path: `db/migrations/` relative to project root.
- Migrations run sequentially by timestamp.
- Use `--url` mode with `@eve/migrate` library for direct operations.
- `EVE_DB_URL` env var (or `.env` file) is fallback for `sql` and `migrate`.

### Pipeline Step

Add a migration step in pipelines for automated deployment:

```yaml
pipelines:
  deploy:
    steps:
      - name: migrate
        action: { type: migrate, env_name: staging }
      - name: deploy
        depends_on: [migrate]
        action: { type: deploy, env_name: staging }
```

## Schema Inspection + RLS

```bash
eve db schema --env <name> [--project <id>]         # Show DB schema
eve db schema --url <postgres-url>                  # Direct connection

eve db rls --env <name>                             # RLS policies + group context diagnostics
eve db rls init --with-groups [--out <path>] [--force]  # Scaffold group-aware RLS helpers
```

`rls` shows resolved principal, org, project, env, group IDs, and permissions for the current session. Useful for debugging why RLS policies are not matching.

`rls init --with-groups` scaffolds these SQL functions to `db/rls/helpers.sql`:
- `app.current_user_id()`
- `app.current_group_ids()`
- `app.has_group()`

Apply the output SQL to your target DB, then reference helpers in RLS policies.

## SQL Access

```bash
eve db sql --env <name> --sql "SELECT count(*) FROM users"         # Read-only (default)
eve db sql --env <name> --sql "UPDATE users SET active = true" --write  # Mutations
eve db sql --env <name> --file ./query.sql                         # From file
eve db sql --env <name> --sql "SELECT * FROM users WHERE id = $1" \
  --params '["user_abc"]'                                          # Parameterized
eve db sql --url <postgres-url> --sql "SELECT 1"                   # Direct connection
```

| Access Mode | Flag | Default |
|---|---|---|
| Read-only | (none) | Yes |
| Read-write | `--write` | No |
| Parameterized | `--params '["arg"]'` | No |
| From file | `--file <path>` | No |
| Direct | `--url <postgres-url>` | No |

Both `--env` (API-proxied) and `--url` (direct) modes are supported for all `sql` operations.

## Scaling, Reset, Wipe, Destroy

```bash
eve db scale --env <name> --class db.p2             # Scale to higher tier
eve db reset --env <name> --force [--no-migrate]    # Drop + recreate schema, re-apply migrations
eve db reset --env <name> --force --danger-reset-production  # Required for production envs
eve db wipe --env <name> --force                    # Reset schema WITHOUT re-applying migrations
eve db destroy --env <name> --force                 # Destroy managed DB entirely
```

- `reset` drops all schemas except `pg_catalog` and `information_schema`, then re-applies migrations.
- `--no-migrate` (or use `wipe`) skips migration re-apply after schema drop.
- `--danger-reset-production` is required when resetting production environments via the API.
- `destroy` is irreversible -- removes the managed tenant entirely.

## Admin APIs

| Endpoint | Method | Purpose |
|---|---|---|
| `/admin/managed-db/instances` | GET | List all managed DB instances |
| `/admin/managed-db/instances` | POST | Register a new instance |
| `/admin/managed-db/instances/:id` | GET | Instance details |
| `/projects/:id/envs/:env/db/managed` | GET | Tenant status |
| `/projects/:id/envs/:env/db/managed/rotate` | POST | Rotate credentials |
| `/projects/:id/envs/:env/db/managed/scale` | POST | Scale tier |
| `/projects/:id/envs/:env/db/managed` | DELETE | Destroy tenant |

## CLI Quick Reference

| Intent | Command |
|---|---|
| Check managed DB readiness | `eve db status --env <name>` |
| View schema | `eve db schema --env <name>` |
| Run read-only query | `eve db sql --env <name> --sql "..."` |
| Run mutation | `eve db sql --env <name> --sql "..." --write` |
| Create migration | `eve db new <description>` |
| Apply migrations | `eve db migrate --env <name>` |
| List applied migrations | `eve db migrations --env <name>` |
| Inspect RLS policies | `eve db rls --env <name>` |
| Scaffold RLS helpers | `eve db rls init --with-groups` |
| Rotate credentials | `eve db rotate-credentials --env <name>` |
| Scale tier | `eve db scale --env <name> --class db.p2` |
| Reset schema | `eve db reset --env <name> --force` |
| Wipe without remigrate | `eve db wipe --env <name> --force` |
| Destroy managed DB | `eve db destroy --env <name> --force` |
