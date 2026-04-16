# Manifest (Current)

## Use When
- You need to author, validate, or review `.eve/manifest.yaml`.
- You need to configure services, environments, pipelines, or harness defaults.
- You need to prepare manifest changes for deployable, reproducible builds.

## Load Next
- `references/pipelines-workflows.md` for pipeline/job wiring in manifests.
- `references/secrets-auth.md` for secret declaration and resolution order.
- `references/overview.md` for core platform concepts before editing complex files.

## Ask If Missing
- Confirm target manifest path and environment names.
- Confirm whether managed DBs, external services, or custom ingress are required.
- Confirm any required repository path, branch, or org/project identifiers.

The manifest (`.eve/manifest.yaml`) is the single source of truth for builds, deploys, pipelines, and workflows.
Schema is Compose-like with Eve extensions under `x-eve`.

## Minimal Example

The simplest possible deployable project. Uses the Eve-native registry so `image` fields are auto-derived from service keys:

```yaml
schema: eve/compose/v2
project: my-app

registry: "eve"

services:
  app:
    build:
      context: .
    ports: ["3000"]
    x-eve:
      ingress:
        public: true

environments:
  sandbox:
    pipeline: deploy

pipelines:
  deploy:
    steps:
      - name: build
        action: { type: build }
      - name: release
        depends_on: [build]
        action: { type: release }
      - name: deploy
        depends_on: [release]
        action: { type: deploy, env_name: sandbox }
```

Deploy with two commands:

```bash
eve project sync --dir .
eve env deploy sandbox --ref main
```

## Full Example

A complete manifest showing the standard SPA + API + managed DB pattern with eve-migrate, nginx reverse proxy, and the canonical pipeline:

```yaml
schema: eve/compose/v2
project: my-project

registry: "eve"

services:
  api:
    build:
      context: ./apps/api
      dockerfile: ./apps/api/Dockerfile
    ports: [3000]
    environment:
      NODE_ENV: production
      DATABASE_URL: ${managed.db.url}
      CORS_ORIGIN: "https://my-project.eh1.incept5.dev"
    # No x-eve.ingress — API is internal, reached via web's /api/ proxy

  web:
    build:
      context: ./apps/web
      dockerfile: ./apps/web/Dockerfile
    ports: [80]
    environment:
      API_SERVICE_HOST: ${ENV_NAME}-api
    depends_on:
      api:
        condition: service_healthy
    x-eve:
      ingress:
        public: true
        port: 80
        alias: my-project

  migrate:
    image: public.ecr.aws/w7c4v0w3/eve-horizon/migrate:latest
    environment:
      DATABASE_URL: ${managed.db.url}
      MIGRATIONS_DIR: /migrations
    x-eve:
      role: job
      files:
        - source: db/migrations
          target: /migrations

  db:
    x-eve:
      role: managed_db
      managed:
        class: db.p1
        engine: postgres
        engine_version: "16"

environments:
  sandbox:
    pipeline: deploy

pipelines:
  deploy:
    steps:
      - name: build
        action: { type: build }
      - name: release
        depends_on: [build]
        action: { type: release }
      - name: deploy
        depends_on: [release]
        action: { type: deploy }
      - name: migrate
        depends_on: [deploy]
        action:
          type: job
          service: migrate
      - name: smoke-test
        depends_on: [migrate]
        script:
          run: ./scripts/smoke-test.sh
          timeout: 300
```

Key patterns:
- **`eve-migrate`** for database migrations — plain SQL files mounted via `x-eve.files`. Runs after deploy because the managed DB must be provisioned first.
- **nginx reverse proxy** on the web service proxies `/api/` to the internal API via `API_SERVICE_HOST: ${ENV_NAME}-api` (k8s service DNS). No CORS, no hard-coded hostnames.
- **`${managed.db.url}`** — connection string injected by Eve for managed databases.
- **Smoke test** validates the deployed services end-to-end before pipeline success.

## Top-Level Fields

```yaml
schema: eve/compose/v2          # optional schema identifier
name: my-project                # project name (preferred)
description: "Short description" # optional project description
project: my-project             # legacy alias for name (either works)
registry:                        # optional container registry
services:                        # required
environments:                    # optional
pipelines:                       # optional
workflows:                       # optional
versioning:                      # optional
x-eve:                           # optional Eve extensions
```

Use `name` as the top-level project identifier. `project` is accepted as a legacy alias but `name` is preferred for new manifests.

Unknown fields are allowed for forward compatibility.

## Registry

```yaml
registry: "eve"   # Default Eve-managed registry
```

Use `registry: "eve"` unless your app must publish to a BYO registry.

For a private custom registry, switch to full object form:

```yaml
registry:
  host: public.ecr.aws/w7c4v0w3
  namespace: myorg
  auth:
    username_secret: REGISTRY_USERNAME
    token_secret: REGISTRY_PASSWORD
```

The deployer uses these secrets to create Kubernetes `imagePullSecrets` for private BYO registries. See container registry reference for setup details.

String modes:
```yaml
registry: "eve"   # Use Eve-managed registry (default)
registry: "none"  # Disable registry handling
registry:           # BYO registry (full object; see above)
```

## Services (Compose-Style)

```yaml
services:
  api:
    build:
      context: ./apps/api
    # image omitted (auto-derived as "api" when build is present)
    ports: [3000]
    environment:
      NODE_ENV: production
    depends_on:
      db:
        condition: service_healthy
    x-eve:
      ingress:
        public: true
        port: 3000
      api_spec:
        type: openapi
        spec_url: /openapi.json
```

Supported Compose fields: `image`, `build`, `environment`, `ports`, `depends_on`, `healthcheck`, `volumes`.

**Image auto-derivation**: When a service has `build` config and a `registry` is configured, the `image` field is optional. With Eve-managed default (`registry: "eve"`), platform derives the image name from the service key (for example, service `app` becomes `image: app`) and prefixes it at build time with the managed registry host.

### Eve Service Extensions (`x-eve`)

| Field | Type | Description |
|-------|------|-------------|
| `role` | string | `component` (default), `worker`, `job`, or `managed_db` |
| `ingress` | object | `{ public: true\|false, port: number, alias?: string, domains?: string[] }` |
| `api_spec` | object | Single API spec registration |
| `api_specs` | array | Multiple API spec registrations |
| `cli` | object | App CLI declaration (see CLI Declaration below) |
| `external` | boolean | External dependency (not deployed) |
| `connection_url` | string | Connection string for external services |
| `worker_type` | string | Worker pool type for this service |
| `files` | array | Mount source files into container |
| `storage` | object | Persistent volume configuration |
| `managed` | object | Managed DB config (requires `role: managed_db`) |
| `object_store` | object | App object store bucket declarations |
| `permissions` | array | Additional permissions for the service's `EVE_SERVICE_TOKEN` |

Notes:
- `x-eve.role: job` makes a service runnable as a one-off job (migrations, seeds).
- `x-eve.role: managed_db` marks a service as a platform-provisioned database.
- `spec_url` can be relative (resolved against service URL) or absolute.
- `spec_path` is supported only for local `file://` repos.
- If a service exposes ports and the cluster domain is configured, Eve creates ingress by default. Set `x-eve.ingress.public: false` to disable.
- `ingress.alias` creates a vanity hostname: `{alias}.{domain}` instead of the default `{service}.{orgSlug}-{projectSlug}-{env}.{domain}`. Useful for user-facing apps that need a clean URL.
- `ingress.domains` brings your own domain names (e.g., `["limelee.com", "www.limelee.com"]`). Each domain gets a separate K8s Ingress with per-domain TLS via cert-manager HTTP-01. Max 10 per service. Domains under the platform domain are rejected — use `alias` instead. All three ingress types (primary, alias, custom domain) coexist and route to the same backend.

### Managed DB Services

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

### App Object Store Buckets (`x-eve.object_store`)

Declare S3-compatible buckets for a service. Eve provisions each bucket at deploy time and injects credentials as env vars.

```yaml
services:
  api:
    x-eve:
      object_store:
        buckets:
          - name: uploads          # logical name → env var suffix
            visibility: private    # private (default) | public
            cors:
              origins: ["https://app.example.com"]
              methods: [GET, PUT, HEAD, DELETE]
              max_age_seconds: 3600
            lifecycle:
              abort_incomplete_uploads_days: 7
          - name: assets
            visibility: public
```

Injected env vars (per bucket, uppercased name):
- `STORAGE_ENDPOINT` — MinIO/S3 endpoint
- `STORAGE_REGION`
- `STORAGE_ACCESS_KEY_ID` / `STORAGE_SECRET_ACCESS_KEY` — per-deployment scoped credentials
- `STORAGE_BUCKET_<NAME>` — physical bucket name (e.g. `eve-org-myorg-myapp-test-uploads`)
- `STORAGE_FORCE_PATH_STYLE` — `true` for MinIO, omitted for AWS S3

Visibility `public` sets the bucket ACL for anonymous GET access (suitable for static assets).

### Service Token Permissions

Every deployed service receives an auto-injected `EVE_SERVICE_TOKEN` with **read-only defaults**. Services that need write access must declare additional permissions:

```yaml
services:
  api:
    x-eve:
      permissions: [jobs:write, events:write, threads:write]
```

**Default permissions** (always included, no declaration needed):
`projects:read`, `jobs:read`, `threads:read`, `envs:read`, `secrets:read`, `builds:read`, `pipelines:read`, `agents:read`, `events:read`

**Common write permissions to opt in to:**

| Permission | Use Case |
|-----------|----------|
| `jobs:write` | Create or update jobs (e.g., trigger workflows) |
| `events:write` | Emit app events (e.g., `question.answered`) |
| `threads:write` | Create or reply to threads |
| `envdb:write` | Write to managed databases via API |

Declared permissions are **merged** with defaults — you only need to list the additional write scopes your service needs.

### API Spec Schema

```yaml
api_spec:
  type: openapi              # openapi | postgrest | graphql
  spec_url: /openapi.json    # relative to service URL, or absolute
  spec_path: ./openapi.yaml  # local file path (file:// repos only)
  name: my-api               # optional display name
  auth: eve                  # eve (default) | none
  on_deploy: true            # refresh on deploy (default: true)
```

Multiple specs:

```yaml
api_specs:
  - type: openapi
    spec_url: /openapi.json
  - type: graphql
    spec_url: /graphql
```

### CLI Declaration

Declare a domain-specific CLI that agents use instead of raw REST calls:

```yaml
x-eve:
  api_spec:
    type: openapi
  cli:
    name: eden                  # binary name on $PATH (lowercase alphanumeric + hyphens)
    bin: cli/bin/eden            # path relative to repo root (repo-bundled mode)
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | CLI binary name. Lowercase alphanumeric + hyphens (`^[a-z][a-z0-9-]*$`). Must be unique per project. |
| `bin` | string | Yes (repo mode) | Path to executable, relative to repo root. |
| `image` | string | Yes (image mode) | Docker image containing CLI binary. |
| `description` | string | No | Brief description shown in agent instruction block. |

**Distribution modes:**

- **Repo-bundled** (primary): CLI is a pre-built single-file executable in the repo (e.g., esbuild bundle). Platform runs `chmod +x` and adds to PATH after clone. Zero additional latency.
- **Image-based**: CLI is distributed via Docker init container (same pattern as toolchains). Platform pulls the image and copies the binary to a shared volume. Adds 2-5s startup latency.

**Auto-discovery**: The platform automatically scans the manifest for services with `x-eve.cli` or `x-eve.api_spec` and injects them into every agent job. No explicit `with_apis` needed — just declare the CLI here and all agents get it on PATH.

When app APIs are resolved (via auto-discovery or explicit `with_apis`), the agent receives:
- The CLI on `$PATH` (ready to run)
- `EVE_APP_API_URL_{SERVICE}` env var (for CLI internal use)
- `EVE_JOB_TOKEN` for auth (CLI reads this automatically)
- A CLI-first instruction block: "Use `eden --help` to see all commands"

See `references/app-cli.md` for the full implementation guide including bundling, env var contract, and testing patterns.

### Toolchain Declarations

Agents can declare toolchains they need. The platform injects them as init containers at pod creation time, keeping the base worker image small (~800MB) while making language runtimes available on demand.

```yaml
# In eve/agents.yaml
version: 1
agents:
  data-analyst:
    name: Data Analyst
    skill: analyze-data
    harness_profile: claude-sonnet
    toolchains: [python]           # python + uv available at runtime

  doc-processor:
    name: Document Processor
    skill: process-documents
    harness_profile: claude-sonnet
    toolchains: [media]            # ffmpeg + whisper available at runtime

  full-stack:
    name: Full Stack Dev
    skill: full-stack-dev
    harness_profile: claude-opus
    toolchains: [python, rust, java]  # multi-toolchain
```

Available toolchains: `python`, `media`, `rust`, `java`, `kotlin`.

Workflow steps can override agent toolchain defaults:

```yaml
workflows:
  process-document:
    steps:
      - name: process
        agent: doc-processor
        toolchains: [media, python]  # override agent default
```

Toolchain precedence: workflow step `toolchains` > agent `toolchains` > none.

Each toolchain is a small container image (~50-300MB) copied to `/opt/eve/toolchains/{name}/` via init containers. The entrypoint extends `PATH` from `EVE_TOOLCHAIN_PATHS`. Per-toolchain `env.sh` files set additional variables (e.g., `JAVA_HOME`, `RUSTUP_HOME`).

Agents without `toolchains` run on the `base` image (Node.js + harnesses only). The `full` image (~2.6GB, all toolchains baked in) remains available via `EVE_WORKER_VARIANT=full`.

### Cloud FS Mounts

Manifest can reference cloud filesystem mounts (Google Drive) connected at the org level. Cloud FS mounts are managed via the `eve cloud-fs` CLI, not declared in the manifest directly.

```bash
# Mount a Google Drive folder
eve cloud-fs mount \
  --provider google-drive \
  --folder-id <drive-folder-id> \
  --mode read_write \
  --label "Engineering Shared Drive"

# List mounts
eve cloud-fs list

# Browse files in a mount
eve cloud-fs ls / --mount <mount-id>
eve cloud-fs ls /subfolder --mount <mount-id>          # alias: browse

# Search across mounts
eve cloud-fs search <query> [--mount <mount-id>]

# Show mount details
eve cloud-fs show <mount-id>

# Update mount settings
eve cloud-fs update <mount-id> --mode read_only

# Remove a mount
eve cloud-fs unmount <mount-id>                        # aliases: remove, delete
```

Mounts are stored in the `cloud_fs_mounts` table, scoped to org (or optionally project). Each mount links an integration's OAuth credentials to a provider folder with configurable mode (`read_only`, `write_only`, `read_write`) and optional auto-indexing into org docs.

Requires a Google Drive integration connection first (`eve integrations connect google-drive`). See Per-Org OAuth Configs below.

### Per-Org OAuth Configs

Each org brings its own OAuth app credentials for external providers (Google Drive, Slack). No cluster-level OAuth secrets required.

```bash
# View setup instructions (shows redirect URI to register)
eve integrations setup-info google-drive
eve integrations setup-info slack

# Register OAuth app credentials for your org
eve integrations configure google-drive \
  --client-id "xxx.apps.googleusercontent.com" \
  --client-secret "GOCSPX-xxx"

eve integrations configure slack \
  --client-id "12345.67890" \
  --client-secret "abc123" \
  --signing-secret "def456" \
  --app-id "A0123ABC"

# View current config (secrets redacted)
eve integrations config google-drive

# Remove config
eve integrations unconfigure google-drive

# Then connect as before (uses per-org credentials)
eve integrations connect google-drive
```

One OAuth app config per provider per org. Multiple connections (integrations) share the same app config. The platform stores credentials in `oauth_app_configs` and uses them for all OAuth authorize, callback, and token refresh flows. Cluster-level `EVE_GOOGLE_CLIENT_*` / `EVE_SLACK_CLIENT_*` env vars are deprecated.

### Files Mount

Mount source files from the repo into the container:

```yaml
x-eve:
  files:
    - source: ./config/app.conf    # relative path in repo
      target: /etc/app/app.conf    # absolute path in container
```

### Persistent Storage

```yaml
x-eve:
  storage:
    mount_path: /data
    size: 10Gi
    access_mode: ReadWriteOnce     # ReadWriteOnce | ReadWriteMany | ReadOnlyMany
    storage_class: standard        # optional
    name: my-data                  # optional PVC name
```

### Healthcheck

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
  interval: 5s
  timeout: 3s
  retries: 3
  start_period: 10s
```

### Dependency Conditions

```yaml
depends_on:
  db:
    condition: service_healthy     # service_started | service_healthy | started | healthy
```

## Platform Environment Variables

Eve automatically injects these variables into all deployed services:

| Variable | Description |
|----------|-------------|
| `EVE_API_URL` | Internal cluster URL for server-to-server calls (e.g., `http://eve-api:4701`) |
| `EVE_PUBLIC_API_URL` | Public ingress URL for browser-facing apps (e.g., `https://api.eh1.incept5.dev`) |
| `EVE_SSO_URL` | SSO broker URL for user authentication (e.g., `https://sso.eh1.incept5.dev`) |
| `EVE_PROJECT_ID` | The project ID (e.g., `proj_01abc123...`) |
| `EVE_ORG_ID` | The organization ID (e.g., `org_01xyz789...`) |
| `EVE_ENV_NAME` | The environment name (e.g., `staging`, `production`) |

Job runners also receive `EVE_ENV_NAMESPACE`, but service containers do not.
Services can override these values by defining them explicitly in their `environment` section.

**Which API URL to use:**

- Use `EVE_API_URL` for backend/server-side calls from your container to the Eve API (internal cluster networking).
- Use `EVE_PUBLIC_API_URL` for browser/client-side calls or any code running outside the cluster.

```javascript
// Server-side: call Eve API from your backend
const eveApiUrl = process.env.EVE_API_URL;

// Client-side: expose to browser for frontend API calls
const publicApiUrl = process.env.EVE_PUBLIC_API_URL;
```

## Environments

```yaml
environments:
  staging:
    pipeline: deploy
    pipeline_inputs:
      smoke_test: true
    approval: required
    overrides:
      services:
        api:
          environment:
            NODE_ENV: staging
    workers:
      - type: default
        service: worker
        replicas: 2
```

### Environment Fields

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | `persistent` (default) or `temporary` |
| `kind` | string | `standard` (default) or `preview` (PR envs) |
| `pipeline` | string | Pipeline name to trigger on deploy |
| `pipeline_inputs` | object | Inputs passed to pipeline (CLI `--inputs` wins on conflict) |
| `approval` | string | `required` to gate deploys |
| `overrides` | object | Compose-style service overrides |
| `workers` | array | Worker pool configuration |
| `labels` | object | Metadata (PR info for preview envs) |

### Environment Pipeline Behavior

When `pipeline` is configured for an environment, `eve env deploy <env> --ref <sha>` triggers a pipeline run instead of performing a direct deployment. This enables:

- Consistent build/test/deploy workflows across environments
- Promotion patterns where staging/production reuse releases from test
- Environment-specific pipeline inputs and approval gates

To bypass the pipeline and perform a direct deployment, use `--direct`:

```bash
eve env deploy staging --ref 0123456789abcdef0123456789abcdef01234567 --direct
```

### Promotion Example

Define environments that share a pipeline but vary in inputs and approval gates:

```yaml
environments:
  test:
    pipeline: deploy-test
  staging:
    pipeline: deploy
    pipeline_inputs:
      smoke_test: true
  production:
    pipeline: deploy
    approval: required
```

Deploy flow:

```bash
# Build + test + release in test
eve env deploy test --ref 0123456789abcdef0123456789abcdef01234567

# Promote to staging (reuse release, no rebuild)
eve release resolve v1.2.3  # Get release_id from test
eve env deploy staging --ref 0123456789abcdef0123456789abcdef01234567 --inputs '{"release_id":"rel_xxx"}'

# Promote to production (approval required)
eve env deploy production --ref 0123456789abcdef0123456789abcdef01234567 --inputs '{"release_id":"rel_xxx"}'
```

This pattern enables build-once, deploy-many promotion workflows without rebuilding images.

## Pipelines (Steps)

```yaml
pipelines:
  deploy-test:
    steps:
      - name: migrate
        action: { type: job, service: migrate }
      - name: deploy
        depends_on: [migrate]
        action: { type: deploy }
```

Step types: `action`, `script`, `agent`, or shorthand `run`.

See `references/pipelines-workflows.md` for step types, triggers, and the canonical build-release-deploy pattern.

## Workflows

```yaml
workflows:
  nightly-audit:
    db_access: read_only
    hints:
      gates: ["remediate:proj_xxx:staging"]
    steps:
      - agent:
          prompt: "Audit error logs"
```

Workflow invocation creates a job with the workflow hints merged.

### Multi-Step Workflow Syntax

Workflows support multi-step DAGs that expand into child jobs at invocation time:

```yaml
workflows:
  ingestion-pipeline:
    with_apis:
      - service: coordinator
        description: Coordinator API for orchestration
    steps:
      - name: ingest
        agent:
          name: ingestion
      - name: extract
        depends_on: [ingest]
        agent:
          name: extraction
      - name: review
        depends_on: [extract]
        agent:
          name: reviewer
```

| Field | Type | Description |
|-------|------|-------------|
| `steps[].name` | string | Unique step identifier (required when using `depends_on`) |
| `steps[].depends_on` | string[] | Step names this step blocks on |
| `steps[].condition` | string | Conditional execution: `step.status == 'value'` (skip step if false) |
| `steps[].agent.name` | string | Per-step agent override |
| `with_apis` | object[] | API specs attached to the workflow — `{ service, description }` (workflow-level or per-step) |

**Validation** (`eve manifest validate` and `eve project sync` check workflows):
- Duplicate step names → error.
- Cyclic dependencies → error (reports cycle path).
- Invalid `depends_on` references → error.
- Trigger with no recognized type → warning.
- Invalid GitHub event type → warning.
- Unknown system event type → warning.
- Cron trigger with missing schedule → warning.
- Invalid condition format → warning.
- Condition references non-existent step → warning.
- Condition step not in `depends_on` → warning.

**Pack workflow merging**: When packs define workflows, they are merged into the
repo manifest before sync (single POST). Pack workflows overlay repo-manifest
workflows — pack definitions take precedence on name collision.

See `references/pipelines-workflows.md` for expansion behavior, response format, and job tree view.

## Secret Requirements and Validation

Declare required secrets at the top level or per pipeline step:

```yaml
x-eve:
  requires:
    secrets: [GITHUB_TOKEN, REGISTRY_TOKEN]

pipelines:
  ci-cd-main:
    steps:
      - name: integration-tests
        script:
          run: "pnpm test"
        requires:
          secrets: [DATABASE_URL]
```

Validate secrets before syncing:

```bash
eve project sync --validate-secrets     # Warn on missing secrets
eve project sync --strict               # Fail on missing secrets
eve manifest validate                   # Schema + secret validation without syncing
```

Use `eve manifest validate` for pre-flight checks against a local manifest or the latest synced version. Required keys follow standard scope resolution rules.

### Platform-Injected Environment Variables

The deployer automatically injects these env vars into every deployed service.
**Do NOT redeclare them as `${secret.*}` in the manifest** — that overrides the
platform value with an empty string when the secret isn't configured.

| Variable | Value | Notes |
|----------|-------|-------|
| `EVE_API_URL` | Platform API URL (K8s in-cluster) | Auto-resolved |
| `EVE_PROJECT_ID` | Project TypeID | Auto-resolved |
| `EVE_ORG_ID` | Org TypeID | Auto-resolved |
| `EVE_ENV_NAME` | Environment name (e.g., `sandbox`) | Auto-resolved |
| `EVE_SERVICE_TOKEN` | 90-day JWT (type: `service`) | Minted per-deploy, refreshed automatically |
| `EVE_PUBLIC_API_URL` | Public API URL (if configured) | Optional |
| `EVE_SSO_URL` | SSO URL (if configured) | Optional |

The service token carries **read-only default permissions** (`projects:read`,
`jobs:read`, `threads:read`, etc.). Apps that need write access must declare
additional permissions via `x-eve.permissions` — see [Service Token Permissions](#service-token-permissions).

User-defined env vars in the manifest override platform vars, so only declare
`EVE_*` vars if you need a different value than the platform default.

### Secret Interpolation

Interpolate secrets in environment variables:

```yaml
environment:
  DATABASE_URL: postgres://user:${secret.DB_PASSWORD}@db:5432/app
```

Also supported (runtime interpolation): `${ENV_NAME}`, `${PROJECT_ID}`, `${ORG_ID}`, `${ORG_SLUG}`, `${COMPONENT_NAME}`, `${SSO_URL}`, `${secret.KEY}`, `${managed.<service>.<field>}`.

### Internal Service URLs

Apps with multiple services often need to call their own API internally (e.g., to emit events back to themselves). Use `${ENV_NAME}` with K8s service DNS naming:

```yaml
environment:
  MY_API_URL: "http://${ENV_NAME}-api:3000"
```

The pattern is `${ENV_NAME}-{service_key}:{port}`. This resolves to the in-cluster service address — no ingress, no CORS, no public exposure. Essential for apps that trigger workflows via their own API.

## Manifest Defaults (`x-eve.defaults`)

Default job settings applied on creation (job fields override defaults). Default environment should be **staging** unless explicitly overridden:

```yaml
x-eve:
  defaults:
    env: staging
    harness: mclaude
    harness_profile: primary-orchestrator
    harness_options:
      model: opus-4.5
      reasoning_effort: high
    hints:
      permission_policy: auto_edit
      resource_class: job.c1
      max_cost:
        currency: usd
        amount: 5
      max_tokens: 200000
    git:
      ref_policy: auto
      branch: job/${job_id}
      create_branch: if_missing
      commit: manual
      push: never
    workspace:
      mode: job
```

`hints` can include budgeting and accounting fields such as `resource_class`,
`max_cost`, and `max_tokens`. These map to scheduling hints and per-attempt
budget enforcement.

## Project Agent Profiles (`x-eve.agents`)

Define harness profiles used by orchestration skills:

```yaml
x-eve:
  agents:
    version: 1
    availability:
      drop_unavailable: true
    profiles:
      primary-reviewer:
        - harness: mclaude
          model: opus-4.5
          reasoning_effort: high
        - harness: codex
          model: gpt-5.2-codex
          reasoning_effort: x-high
```

For pack-distributed profiles, define them in `eve/x-eve.yaml` and import via `pack.yaml`:

```yaml
# eve/x-eve.yaml
version: 1
agents:
  profiles:
    coordinator:
      - harness: claude
        model: sonnet
        reasoning_effort: medium
    expert:
      - harness: claude
        model: sonnet
        reasoning_effort: high
```

Profiles in `eve/x-eve.yaml` are distributed with the pack. Profiles in the manifest are project-local only.

## AgentPacks (`x-eve.packs` + `x-eve.install_agents`)

AgentPacks import agent/team/chat config and skills from pack repos. Packs are
resolved by `eve agents sync` and locked in `.eve/packs.lock.yaml`.

```yaml
x-eve:
  install_agents: [claude-code, codex, gemini-cli]  # defaults to [claude-code]
  packs:
    - source: ./skillpacks/my-pack
    - source: incept5/eve-skillpacks
      ref: 0123456789abcdef0123456789abcdef01234567
    - source: ./skillpacks/claude-only
      install_agents: [claude-code]
```

Notes:
- Remote pack sources require a 40-char git SHA `ref`.
- Packs can be full AgentPacks (`eve/pack.yaml`) or skills-only packs.
- Local packs use relative paths (resolved from repo root).

### Full AgentPack Descriptor (`eve/pack.yaml`)

A full AgentPack declares its resources via an `imports` map and optional gateway defaults:

```yaml
# eve/pack.yaml
version: 1
id: my-pack
imports:
  agents: eve/agents.yaml
  teams: eve/teams.yaml
  workflows: eve/workflows.yaml
  chat: eve/chat.yaml
  x_eve: eve/x-eve.yaml
gateway:
  default_policy: none
```

| Field | Type | Description |
|-------|------|-------------|
| `version` | number | Schema version (currently `1`) |
| `id` | string | Unique pack identifier |
| `imports` | object | Map of resource type to relative YAML file path |
| `imports.agents` | string | Agent definitions file |
| `imports.teams` | string | Team definitions file |
| `imports.workflows` | string | Workflow definitions (merged with manifest workflows at sync) |
| `imports.chat` | string | Chat route definitions |
| `imports.x_eve` | string | Harness profiles and agent config |
| `gateway` | object | Gateway defaults for the pack |
| `gateway.default_policy` | string | Default gateway policy for pack agents (`none`, `discoverable`, `routable`) |

All `imports` paths are relative to the pack root. Only declare the imports your pack needs — all fields are optional.

### Pack Lock File

`.eve/packs.lock.yaml` tracks resolved state:

```yaml
resolved_at: "2026-02-09T..."
project_slug: myproject
packs:
  - id: pack-id
    source: incept5/eve-skillpacks
    ref: 0123456789abcdef0123456789abcdef01234567
    pack_version: 1
effective:
  agents_count: 5
  teams_count: 2
  routes_count: 3
  profiles_count: 4
```

### Pack Overlay Customization

Local YAML overlays pack defaults using deep merge + `_remove`:

```yaml
# In local agents.yaml
version: 1
agents:
  pack-agent:
    harness_profile: my-override       # override pack default
  unwanted-agent:
    _remove: true                       # remove from pack
```

### Pack CLI

```bash
eve packs status [--repo-dir <path>]           # Show lockfile + drift
eve packs resolve [--dry-run] [--repo-dir <path>]  # Preview resolution
```

## Project Bootstrap

Bootstrap creates a project + environments in a single API call:

```bash
eve project bootstrap --name my-app --repo-url https://github.com/org/repo \
  --environments staging,production
```

API: `POST /projects/bootstrap` with body:
- `org_id`, `name`, `repo_url`, `branch` (required)
- `slug`, `description`, `template`, `packs`, `environments` (optional)

Idempotent — re-calling with the same name returns the existing project.

## Ingress Defaults

If a service exposes ports and the cluster domain is configured, Eve creates ingress by default.
Set `x-eve.ingress.public: false` to disable.

URL pattern: `{service}.{orgSlug}-{projectSlug}-{env}.{domain}`

### Custom Domains

Bring your own domain by adding `domains` to the ingress config:

```yaml
services:
  web:
    x-eve:
      ingress:
        public: true
        alias: myapp              # myapp.eh1.incept5.dev (platform subdomain)
        domains:
          - myapp.com             # custom domain (A record)
          - www.myapp.com         # custom domain (CNAME)
```

**Lifecycle**: `pending_dns` → `dns_verified` → `cert_provisioning` → `active`. Domains are auto-registered during `eve project sync`, bound to environments during deploy. After setting up DNS, run `eve domain verify <hostname>` — it performs real DNS resolution server-side and transitions the status to `dns_verified`. Redeploy to create the Ingress and provision the TLS cert.

**DNS**: Apex domains (`myapp.com`) require an A record pointing to the platform ingress IP. Subdomains (`www.myapp.com`) can use a CNAME to the platform ingress hostname.

**TLS**: Custom domains use `cert-manager.io/cluster-issuer` (HTTP-01 challenge), NOT the platform wildcard cert (`EVE_DEFAULT_TLS_SECRET`). The ClusterIssuer must support HTTP-01 challenges.

## App Undeploy & Delete

Full lifecycle operations for environments, projects, and orgs.

### Environment Undeploy

Take an environment offline without losing config. Tears down K8s resources but preserves the environment record for redeployment.

```bash
eve env undeploy <env> --project <id>
eve env show <project> <env> --json   # Verify deploy_status = 'undeployed'
```

Redeploy later with `eve env deploy <env> --ref <sha>`. The `deploy_status` field tracks state: `unknown`, `deployed`, `undeployed`, `deploying`, `undeploying`, `failed`.

### Project Delete

```bash
eve project delete <project>           # Soft-delete (sets deleted_at)
eve project delete <project> --hard    # Hard-delete: cascades through all resources
eve project delete <project> --hard --force  # Continue on partial failures
```

Hard delete sequence: undeploy all environments, delete environments (triggers managed DB cleanup), cascade-delete jobs/pipeline-runs/releases/builds/agents/teams/threads, delete project record.

### Org Delete

```bash
eve org delete <org>                   # Soft-delete
eve org delete <org> --hard --force    # Full tenancy teardown
```

Cascades through all projects and environments in the org.

### Resource Cleanup

Individual resource delete and prune commands:

```bash
eve build delete <id>                  # Delete a single build
eve build prune --project <id> --keep 10  # Keep last N, delete rest
eve release delete <id>
eve release prune --project <id> --keep 10
eve pipeline delete <name> --project <id>
eve agents delete <name> --project <id>
eve thread delete <id>
```
