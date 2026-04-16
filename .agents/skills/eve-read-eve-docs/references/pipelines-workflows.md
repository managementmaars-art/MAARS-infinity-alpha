# Pipelines + Workflows (Current)

## Use When
- You need to define, run, inspect, or debug pipeline and workflow automation.
- You need trigger wiring for environment deploy and event-based job orchestration.
- You need guidance on build-release-deploy and promotion patterns.

## Load Next
- `references/events.md` if the trigger source is webhook or scheduled.
- `references/builds-releases.md` for image/release semantics and diagnostics.
- `references/cli.md` for pipeline/workflow execution commands.

## Ask If Missing
- Confirm pipeline/workflow name, target env, and repo ref/hash.
- Confirm whether you want standard pipeline execution or direct deploy mode.
- Confirm which inputs/outputs are required before creating or re-running steps.

## Pipelines (Manifest)

Pipelines are ordered steps that expand into a job graph. Define them in `.eve/manifest.yaml`.

```yaml
pipelines:
  deploy-test:
    trigger:
      github:
        event: push
        branch: main
    steps:
      - name: build
        action: { type: build }
      - name: unit-tests
        script: { run: "pnpm test", timeout: 1800 }
      - name: deploy
        depends_on: [build, unit-tests]
        action: { type: deploy }
```

### Canonical Pipeline Pattern

The standard build-release-deploy pipeline:

```yaml
steps:
  - name: build
    action: { type: build }
    # Creates BuildSpec + BuildRun, outputs build_id + image_digests
  - name: release
    depends_on: [build]
    action: { type: release }
    # References build_id, uses digest-based image refs from BuildArtifacts
  - name: deploy
    depends_on: [release]
    action: { type: deploy, env_name: staging }
```

When a project includes persistent DB state, the deploy pipeline must run migrations before deploy:

```yaml
steps:
  - name: build
    action: { type: build }
  - name: release
    depends_on: [build]
    action: { type: release }
  - name: migrate
    depends_on: [release]
    action:
      type: job
      service: migrate
  - name: deploy
    depends_on: [migrate]
    action: { type: deploy, env_name: sandbox }
```

Place a `migrate` service in `services` with `x-eve.role: job`, and make `deploy` depend on it.
That ensures `presence/projects/other-schema` tables are created before pods start serving traffic.

### Step Output Linking

Understand how data flows between pipeline steps:

- The `build` action creates BuildSpec and BuildRun records. On success, it emits `build_id` and `image_digests` as step outputs.
- BuildRuns produce BuildArtifacts containing per-service image digests (`sha256:...`).
- The `release` action automatically receives `build_id` from the upstream build step. It derives `image_digests_json` from BuildArtifacts, ensuring immutable digest-based image references.
- The `deploy` action references images by digest for deterministic, reproducible deployments.

This chain ensures that what was built is exactly what gets released and deployed -- no tag mutation, no ambiguity.

### Step Types

- **action**: built-in actions (`build`, `release`, `deploy`, `run`, `job`, `create-pr`, `notify`, `env-ensure`, `env-delete`)
- **script**: shell command executed by worker (`run` or `command` + `timeout`)
- **agent**: AI agent job (prompt-driven)
- **run**: shorthand for `script.run`

### Pipeline Runs

- A run creates one job per step with dependencies wired from `depends_on`.
- Run IDs: `prun_xxx`.
- Pipeline runs use the job-graph expander by default.
- `eve pipeline run --only <step>` runs a subset of steps.
- A failed job marks the run as failed and cascades cancellation to dependents.
- Cancelled jobs are terminal and unblock downstream jobs.

### CLI

```bash
eve pipeline list [project]
eve pipeline show <project> <name>
eve pipeline run <name> --ref <sha> --env <env> --inputs '{"k":"v"}' --repo-dir ./my-app
eve pipeline runs [project] --status <status>
eve pipeline show-run <pipeline> <run-id>
eve pipeline approve <run-id>
eve pipeline cancel <run-id> [--reason <text>]
eve pipeline logs <pipeline> <run-id> [--step <name>]
```

Notes:
- `--ref` must be a 40-character SHA, or a ref resolved against `--repo-dir`/cwd.

### Auto-Trigger Environment-Linked Pipelines

When an environment references a pipeline (`environments.<env>.pipeline: deploy`) and that pipeline has no explicit `trigger` block, the platform creates an implicit trigger: the pipeline fires automatically on `github.push` to the project's default branch.

Environments can override the branch with `environments.<env>.branch`. Set `auto_deploy: false` to disable implicit triggering for a specific environment.

If the pipeline already has an explicit `trigger` block, the implicit trigger is skipped (user controls triggering).

### Env Deploy as Pipeline Alias

If `environments.<env>.pipeline` is set, `eve env deploy <env> --ref <sha>` triggers the pipeline.
Use `--direct` to bypass. `--ref` must be a 40-character SHA, or a ref resolved
against `--repo-dir`/cwd.

### Promotion Pattern

1. Deploy to test (creates release):
   `eve env deploy test --ref <sha>`
2. Resolve release:
   `eve release resolve vX.Y.Z`
3. Deploy to staging/production with:
   `eve env deploy staging --ref <sha> --inputs '{"release_id":"rel_xxx"}'`

This enables build-once, deploy-many promotion workflows without rebuilding images.

## Pipeline Logs and Streaming

### Snapshot Logs

View build and execution logs (not just metadata) with timestamps and step name prefixes:

```bash
eve pipeline logs <pipeline> <run-id>                  # All step logs
eve pipeline logs <pipeline> <run-id> --step <name>    # Single step
```

### Live Streaming

Stream logs in real time via SSE:

```bash
eve pipeline logs <pipeline> <run-id> --follow                   # All steps
eve pipeline logs <pipeline> <run-id> --follow --step <name>     # Single step
```

Output format:

```
[14:23:07] [build] Cloning repository...
[14:23:09] [build] buildkit addr: tcp://buildkitd.eve.svc:1234
[14:23:15] [build] [api] #5 [dependencies 1/4] COPY pnpm-lock.yaml ...
[14:24:01] [deploy] Deployment started; waiting up to 180s
[14:24:12] [deploy] Deployment status: 1/1 ready
```

### Failure Hints

When a build step fails, the CLI automatically shows:
- The error type and classification
- An actionable hint (e.g., `Run 'eve build diagnose bld_xxx'`)
- The build ID for cross-referencing

### Pipeline-to-Build Linkage

Pipeline steps of type `build` create build specs and runs. On failure:
1. The pipeline step error includes the build ID.
2. The CLI prints a hint to run `eve build diagnose <build_id>`.
3. Build diagnosis shows the full buildkit output and the failed Dockerfile stage.

## Workflow Definitions

Workflows are defined in the manifest and invoked as jobs. For pack distribution, also define workflows in `eve/workflows.yaml` and reference it from `eve/pack.yaml` via `imports.workflows`. Pack workflows are merged with manifest workflows at sync time — pack definitions take precedence on name collision.

```yaml
workflows:
  nightly-audit:
    db_access: read_only
    hints:
      gates: ["remediate:proj_xxx:staging"]
    steps:
      - agent:
          prompt: "Audit error logs and summarize anomalies"
```

### Multi-Step Workflow Expansion

Workflows compile to a full job DAG at invocation time. A multi-step workflow creates 1 root container job + N child step jobs with dependency ordering.

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

**How it works:**
- Each step becomes a child job under the root workflow job.
- `depends_on: [step_names]` wires dependency as `blocks` relations -- the scheduler respects them.
- Per-step agent, harness, and toolchain resolution is supported.
- `with_apis` can be set at the workflow level (applies to all steps) or per step.
- When a service declares `x-eve.cli`, agents also get the CLI binary on `$PATH`. See `references/app-cli.md`.

### Resource Propagation Between Steps

All workflow steps receive the parent workflow's `resource_refs`. Resources are hydrated into `.eve/resources/` in each step's workspace automatically. Previously only the first step received resources; now every step gets them.

### Prior Step Result Injection

When a workflow step has `depends_on`, the orchestrator injects the completed dependency's `result_text` into the step's job description at dispatch time. This means downstream agents receive upstream outputs without making API calls.

- Injected as a `## Prior Step Results` section in the job description
- Each prior step's result appears under a `### Step: <name> (<job_id>)` heading
- Capped at 50KB per step to avoid prompt bloat
- If a step has multiple dependencies, all completed results are included

### Per-Step `with_apis` Overrides

Individual workflow steps can override the workflow-level `with_apis` declaration:

```yaml
workflows:
  pipeline:
    with_apis:
      - service: coordinator
        description: Coordinator API for orchestration
    steps:
      - name: ingest
        agent: { name: ingestion }
        # Inherits with_apis from workflow level
      - name: transform
        with_apis:
          - service: coordinator
            description: Coordinator API for orchestration
          - service: analytics
            description: Analytics API for data processing
        agent: { name: transformer }
        # Uses its own with_apis, overriding workflow level
```

Steps without their own `with_apis` inherit from the workflow level.

**Validation rules** (enforced by `eve manifest validate` and `eve project sync`):
- Duplicate step names → error.
- Cyclic dependencies → error (reports the cycle path).
- Invalid `depends_on` references (non-existent step name) → error.
- Trigger with no recognized type key → warning.
- Invalid GitHub event type (not `push` or `pull_request`) → warning.
- Unknown system event type → warning (advisory, custom events allowed).
- Cron trigger with missing schedule → warning.

Trigger validation runs during `eve project sync` (not just `eve manifest validate`), so malformed triggers are surfaced immediately.

### Conditional Steps

Steps can declare a `condition` that's evaluated when dependencies complete. If false, the step is skipped without running an agent.

```yaml
workflows:
  smart-edit:
    steps:
      - name: triage
        agent: { name: fast-triage }
      - name: deep-analysis
        depends_on: [triage]
        condition: "triage.status == 'complex'"
        agent: { name: deep-analyzer }
```

**Condition format:** `step_name.status == 'value'` or `step_name.status != 'value'`.
Evaluates against `result_json.eve.status` of the referenced step.

**Rules:**
- Referenced step must exist in the workflow and be in `depends_on`
- Skipped steps are marked `done` with `close_reason: 'condition_not_met'`
- Downstream steps that depend on a skipped step still become eligible
- Condition validation runs at sync time (format, reference, dependency checks)

**Use case — triage escalation:** A fast agent (low reasoning) classifies task complexity. An expert agent (high reasoning) only runs for complex tasks. Simple tasks are handled entirely by the triage step.

**Response format** includes `step_jobs`:

```json
{
  "job_id": "proj-abc12345",
  "status": "active",
  "step_jobs": [
    {"job_id": "proj-abc12345.1", "step_name": "ingest"},
    {"job_id": "proj-abc12345.2", "step_name": "extract", "depends_on": ["ingest"]},
    {"job_id": "proj-abc12345.3", "step_name": "review", "depends_on": ["extract"]}
  ]
}
```

**Job tree view** (`eve job tree`):

```
[*] proj-abc12345 [Workflow] ingestion-pipeline
|- [-] proj-abc12345.1 [ingestion-pipeline] ingest
|- [-] proj-abc12345.2 [ingestion-pipeline] extract
|- [-] proj-abc12345.3 [ingestion-pipeline] review
```

### Workflow Hints

Workflow definitions may include a `hints` block. These hints are merged into the job at invocation time (API, CLI, or event triggers). Use hints for:

- **Remediation gates**: control which environments a workflow can remediate. Pattern: one gate per environment.
  ```yaml
  hints:
    gates: ["remediate:proj_abc123:staging"]
  ```
- **Timeouts**: set execution time limits for the workflow job.
- **Harness preferences**: specify model/harness settings that override project defaults for this workflow.

### Invocation

- Invoking a workflow creates a **job** with workflow metadata in `hints`.
- `wait=true` returns `result_json` with a 60s timeout.

### Workflow CLI

```bash
eve workflow list [project]
eve workflow show <project> <name>
eve workflow run <project> <name> --input '{"k":"v"}'
eve workflow invoke <project> <name> --input '{"k":"v"}'
eve workflow logs <job-id>
```

## Triggers

Both pipelines and workflows can include a `trigger` block. The orchestrator matches incoming events and creates pipeline runs or workflow jobs.

### Generic Event Triggers

Workflows and pipelines can trigger on any event source and type:

```yaml
trigger:
  event:
    source: app
    type: document.uploaded
```

- `source` (required): matches `event.source` (e.g., `app`, `runner`, `chat`, `github`)
- `type` (optional): matches `event.type` exactly; omit to match all events from that source

When a workflow is triggered by an event, the event payload is forwarded as workflow input. The input JSON is included in child job descriptions so step agents can see what triggered them.

### App Trigger (Shorthand)

For app-sourced events, use the `app` trigger as a shorthand:

```yaml
trigger:
  app:
    event: question.answered
```

This is equivalent to `event: { source: app, type: question.answered }`. Both formats work; use whichever reads better in context.

### GitHub Push Triggers

```yaml
trigger:
  github:
    event: push
    branch: main
```

Branch patterns support wildcards (e.g., `release/*`, `*-prod`).

### GitHub Pull Request Triggers

```yaml
trigger:
  github:
    event: pull_request
    action: [opened, synchronize]
    base_branch: main
```

Supported PR actions: `opened`, `synchronize`, `reopened`, `closed`.
Base branch filtering supports wildcard patterns.

### PR Preview Deployment Example

Deploy a preview environment on PR open/update, clean up on close:

```yaml
pipelines:
  pr-preview:
    trigger:
      github:
        event: pull_request
        action: [opened, synchronize]
        base_branch: main
    steps:
      - name: create-preview-env
        action:
          type: env-ensure
          with:
            env_name: ${{ env.pr_${{ github.pull_request.number }} }}
            kind: preview
      - name: deploy
        depends_on: [create-preview-env]
        action:
          type: deploy
          with:
            env_name: ${{ env.pr_${{ github.pull_request.number }} }}

  pr-cleanup:
    trigger:
      github:
        event: pull_request
        action: closed
        base_branch: main
    steps:
      - name: cleanup-env
        action:
          type: env-delete
          with:
            env_name: ${{ env.pr_${{ github.pull_request.number }} }}
```

## API Endpoints

```
GET  /projects/{project_id}/pipelines
GET  /projects/{project_id}/pipelines/{name}

# Pipeline runs
POST /projects/{project_id}/pipelines/{name}/run
GET  /projects/{project_id}/pipelines/{name}/runs
GET  /projects/{project_id}/pipelines/{name}/runs/{run_id}
POST /pipeline-runs/{run_id}/approve
POST /pipeline-runs/{run_id}/cancel
GET  /pipeline-runs/{run_id}/stream
GET  /pipeline-runs/{run_id}/steps/{name}/stream

# Workflows
GET  /projects/{project_id}/workflows
GET  /projects/{project_id}/workflows/{name}
POST /projects/{project_id}/workflows/{name}/invoke?wait=true|false
```
