# Jobs Reference

## Use When
- You need to inspect job lifecycle phases, attempts, and dependencies.
- You need to tune scheduling, review, or retry behavior.
- You need to follow, stream, or debug running/failed jobs.

## Load Next
- `references/cli.md` for job list/show/follow/result commands.
- `references/pipelines-workflows.md` when jobs are part of pipeline execution.
- `references/deploy-debug.md` for infrastructure-side runtime symptoms.

## Ask If Missing
- Confirm whether you are working with a root job or child attempt.
- Confirm target job ID, org/project scope, and desired action (`list`/`show`/`follow`).
- Confirm whether you need to review dependency graph or submission state.

## Entity Model

```
Job → JobAttempt → Session → ExecutionProcess
```

- **Job**: Logical unit of work. ID: `{slug}-{hash8}` (e.g., `myproj-a3f2dd12`).
- **JobAttempt**: Isolated execution run. Has UUID `id` + job-scoped `attempt_number` (1, 2, 3...).
- **Session**: Tracks executor within an attempt. May change on reconstruction; attempt_id stays stable.
- **ExecutionProcess**: Single harness invocation within a session.

Child jobs use `{parent}.{n}` format (e.g., `myproj-a3f2dd12.1`). Max depth: 3 levels.

## Lifecycle

**Phases:** `idea` → `backlog` → `ready` → `active` → `review` → `done` | `cancelled`

Jobs default to `ready` (immediately schedulable). Priority: 0-4 (P0 highest, default 2).

**Scheduling order:** Filter phase=ready + all deps done → sort by priority (ascending) → sort by created_at (FIFO).

## API Endpoints

### Project-Scoped

```
POST /projects/{project_id}/jobs              Create job
GET  /projects/{project_id}/jobs              List jobs
GET  /projects/{project_id}/jobs/ready        Ready/schedulable jobs
GET  /projects/{project_id}/jobs/blocked      Blocked jobs
GET  /jobs                                     List jobs (admin, cross-project)
```

### Job-Scoped

```
GET    /jobs/{job_id}                          Get job
PATCH  /jobs/{job_id}                          Update job
GET    /jobs/{job_id}/tree                     Job hierarchy
GET    /jobs/{job_id}/context                  Context + derived status
GET    /jobs/{job_id}/dependencies             List dependencies
POST   /jobs/{job_id}/dependencies             Add dependency
DELETE /jobs/{job_id}/dependencies/{related}   Remove dependency
```

### Claim, Release, Attempts

```
POST /jobs/{job_id}/claim                      Claim (creates attempt, moves to active)
POST /jobs/{job_id}/release                    Release attempt
GET  /jobs/{job_id}/attempts                   List attempts
GET  /jobs/{job_id}/attempts/{n}/logs          Attempt logs
GET  /jobs/{job_id}/attempts/{n}/stream        SSE log stream for attempt
```

### Monitoring

```
GET /jobs/{job_id}/result                      Latest or attempt-specific result
GET /jobs/{job_id}/wait                        Block until completion (SSE, default 300s)
GET /jobs/{job_id}/stream                      SSE log stream for job
```

### Review Workflow

```
POST /jobs/{job_id}/submit                     Submit for review (requires summary)
POST /jobs/{job_id}/approve                    Approve (optional comment)
POST /jobs/{job_id}/reject                     Reject (requires reason)
```

### Thread Endpoints (Coordination)

```
GET  /threads/{id}/messages?since=<iso>&limit=<n>    List messages
POST /threads/{id}/messages                          Post message
```

## Resource Refs

`resource_refs` attach org documents or job attachments to a job. The worker
hydrates them into `.eve/resources/` before harness launch.

```json
[
  {
    "uri": "org_docs:/pm/features/FEAT-123.md@v4",
    "label": "Approved Plan",
    "required": true,
    "mount_path": "pm/approved-plan.md"
  }
]
```

Fields:
- `uri` (required): `org_docs:/path[@vN]` or `job_attachments:/job_id/name`
- `label` (optional): human readable
- `required` (optional, default true): fail provisioning when missing
- `mount_path` (optional): relative path under `.eve/resources/`

## CLI Quick Reference

### Create

```bash
eve job create --description "Fix the login bug"
eve job create --parent myproj-a3f2dd12 --description "Sub-task"
eve job create --description "Review" --harness mclaude --model opus-4.5 --reasoning high
eve job create --description "Fix checkout" \
  --git-ref main --git-branch job/fix-checkout \
  --git-create-branch if_missing --git-commit auto --git-push on_success

# Resource refs (org docs + attachments)
eve job create --project proj_xxx --description "Review brief" \
  --resource-refs='[{"uri":"org_docs:/pm/features/FEAT-123.md@v4","required":true,"mount_path":"pm/brief.md","label":"Approved Plan"}]'
```

Resource refs mount into `.eve/resources/` before harness start. The worker writes
`.eve/resources/index.json` and injects `EVE_RESOURCE_INDEX` for agents.

### App API Awareness

```bash
eve job create --description "Analyze data" --with-apis coordinator,analytics
```

`--with-apis` is now **server-side**: the CLI passes `app_apis` in job hints
instead of generating instructions client-side. The server validates that the
named APIs exist for the project, generates the instruction block (with a
runtime-safe Node `fetch` helper using `EVE_JOB_TOKEN`), and appends it to the
job description. This ensures consistent behavior across CLI, API, workflow, and
SDK job creation paths.

### Attachments

```bash
eve job attach <job-id> --file ./report.pdf --name report.pdf
eve job attach <job-id> --stdin --name output.json --mime application/json
eve job attachments <job-id>           # List attachments
eve job attachment <job-id> <name>     # Fetch attachment content
```

### Batch Operations

```bash
eve job batch --project proj_xxx --file batch.json    # Submit batch job graph
eve job batch-validate --file batch.json              # Validate without submitting
```

### List and View

```bash
eve job list --phase active
eve job list --since 1h --stuck
eve job ready                                  # Schedulable jobs
eve job blocked                                # Waiting on deps
eve job show <job-id>
eve job current                                # From EVE_JOB_ID
eve job tree <job-id>
eve job diagnose <job-id>
```

### Update and Complete

```bash
eve job update <job-id> --phase active --priority 0
eve job close <job-id> --reason "Done"
eve job cancel <job-id> --reason "No longer needed"
```

### Monitor Execution

```bash
eve job follow <job-id>                        # Stream logs (SSE)
eve job wait <job-id> --timeout 120 --json     # Block until done
eve job watch <job-id>                         # Status polling + log streaming
eve job result <job-id> --format text           # Get result
eve job result <job-id> --attempt 2 --format json
eve job runner-logs <job-id>                    # kubectl pod logs
```

`wait` exit codes: 0=success, 1=failed, 124=timeout, 125=cancelled.

### Claim/Release (Agent Use)

```bash
eve job claim <job-id> --agent my-agent --harness mclaude
eve job release <job-id> --reason "Need info"
eve job attempts <job-id>
eve job logs <job-id> --attempt 2
```

### Review

```bash
eve job submit <job-id> --summary "Implemented fix, added tests"
eve job approve <job-id> --comment "LGTM"
eve job reject <job-id> --reason "Missing tests"
```

### Dependencies

```bash
eve job dep add <job-id> <depends-on-id>
eve job dep remove <job-id> <depends-on-id>
eve job dep list <job-id>
```

### Supervision and Thread Coordination

```bash
eve supervise                                  # Long-poll child events (current job)
eve supervise <job-id> --timeout 60
eve thread messages <thread-id> --since 5m
eve thread post <thread-id> --body '{"kind":"directive","body":"focus on auth"}'
eve thread follow <thread-id>
```

## Dependency Model

Relations between jobs: `blocked_by`, `blocks`, `waits_for`, `conditional_blocks`.

- `blocked_by[]`: Job IDs that must complete before this job starts.
- `blocks[]`: Sets the reverse relationship on blocking jobs.
- Scheduler filters out blocked jobs from the ready queue.

```bash
eve job create --description "Deploy to staging" # then:
eve job dep add <deploy-job> <build-job>
```

## Job Context

**Endpoint:** `GET /jobs/{job_id}/context` | **CLI:** `eve job current [--json|--tree]`

Response shape:

```
{ job, parent, children, relations: { dependencies, dependents, blocking },
  latest_attempt, latest_rejection_reason, blocked, waiting, effective_phase }
```

**Derived fields:**
- `blocked`: true when unresolved blocking relations exist.
- `waiting`: true when latest attempt returned `result_json.eve.status == "waiting"`.
- `effective_phase`: priority order `blocked` → `waiting` → `job.phase`.

Use `effective_phase` for display and orchestration decisions, not raw `phase`.

## Control Signals

Harnesses emit a `json-result` block. The worker extracts the **last** one and stores it as `job_attempts.result_json`.

```json-result
{
  "eve": {
    "status": "waiting",
    "summary": "Spawned 3 child jobs, added waits_for relations",
    "reason": "Waiting on child jobs to complete"
  }
}
```

**`eve.status` values:**
- `success`: Normal success path (review or done based on job settings).
- `waiting`: Attempt succeeds, job requeued to `ready`, assignee cleared. No review submission. If no blockers exist, orchestrator applies `defer_until` backoff to prevent tight loops.
- `failed`: Normal failure path.

**`eve.summary`**: Persisted to `job_attempts.result_summary` for quick visibility.

## Git Controls

Job-level git configuration governs ref resolution, branch creation, commit, and push behavior.

### Configuration Object

```json
{
  "git": {
    "ref": "main",
    "ref_policy": "auto",
    "branch": "job/${job_id}",
    "create_branch": "if_missing",
    "commit": "auto",
    "commit_message": "job/${job_id}: ${summary}",
    "push": "on_success",
    "remote": "origin"
  },
  "workspace": {
    "mode": "job",
    "key": "session:${session_id}"
  }
}
```

**Precedence:** explicit job fields → `x-eve.defaults.git` (manifest) → project defaults.

### Ref Resolution (`ref_policy`)

| Policy | Behavior |
|--------|----------|
| `auto` | env release SHA → manifest defaults → project default branch |
| `env` | Requires `env_name` + current release SHA |
| `project_default` | Always uses `project.branch` |
| `explicit` | Requires `git.ref` to be set |

### Repo Auth

- HTTPS: uses `github_token` secret (e.g., `GITHUB_TOKEN`).
- SSH: uses `ssh_key` secret via `GIT_SSH_COMMAND`.
- Missing auth fails fast with remediation hints (`eve secrets set`).

### Branch Creation (`create_branch`)

| Value | Behavior |
|-------|----------|
| `never` | Branch must already exist |
| `if_missing` | Create only when missing (default when `branch` is set) |
| `always` | Reset branch to `ref` |

### Commit Policy (`commit`)

| Value | Behavior |
|-------|----------|
| `never` | No commits |
| `manual` | Agent decides when to commit (default) |
| `auto` | Worker runs `git add -A` + commit after execution, even on failure |
| `required` | On success, fail attempt if working tree is clean |

### Push Policy (`push`)

| Value | Behavior |
|-------|----------|
| `never` | No push (default) |
| `on_success` | Push only when worker created commits in this attempt |
| `required` | Attempt push; no-op if no commits. Fail if push fails. |

Push without git credentials fails fast.

### Attempt Git Metadata (Audit)

Resolved values stored on attempt for debugging:

```json
{
  "resolved_ref": "refs/heads/main",
  "resolved_sha": "abc123",
  "resolved_branch": "job/myproj-a3f2dd12",
  "ref_source": "env_release|manifest|project_default|explicit",
  "pushed": true,
  "commits": ["def456"]
}
```

Also promoted to `JobResponse.resolved_git` from the latest successful attempt.

## Harness Selection

Target a harness directly or via a project profile (`x-eve.agents`):

| Flag | Purpose |
|------|---------|
| `--harness` | Harness name (mclaude, codex, gemini, zai) |
| `--profile` | Profile from `x-eve.agents` |
| `--variant` | Config overlay preset |
| `--model` | Model override |
| `--reasoning` | Effort: low, medium, high, x-high |

## Scheduling Hints

Preferences (not requirements) that influence scheduling:

| Hint | Description |
|------|-------------|
| `worker_type` | e.g., `default`, `gpu` |
| `permission_policy` | `yolo` (default), `auto_edit`, `never` |
| `timeout_seconds` | Execution timeout |

## Coordination Threads

Team dispatches create coordination threads with key `coord:job:{parent_job_id}`. Thread ID stored in `hints.coordination.thread_id`.

Child agents receive `EVE_PARENT_JOB_ID` to derive the coordination key. On attempt completion, the orchestrator auto-posts a status summary to the thread.

**Inbox file:** `.eve/coordination-inbox.md` is regenerated from recent thread messages at job start.

**Message kinds:** `status` (auto summary), `directive` (lead→member), `question` (member→lead), `update` (progress).

## Agent Environment Variables

Injected by the worker during execution:

- `EVE_PROJECT_ID` — current project
- `EVE_JOB_ID` — current job
- `EVE_ATTEMPT_ID` — current attempt UUID
- `EVE_AGENT_ID` — agent identifier
- `EVE_PARENT_JOB_ID` — parent job (for coordination)

## Agent-Native Job Monitoring

### Event→Job Linkage

When the orchestrator processes an event and creates a workflow job, it writes the `job_id` back to the event record. Use `eve event show <event-id>` to see which job an event triggered. This enables tracing from event source through to job execution.

### Workflow-Aware List Filtering

```bash
eve job list --label workflow:ingestion-pipeline --root   # Root workflow jobs only
eve job list --type agent --since 1h                      # Filter by job type
eve job list --dead-letters                                # Failed (not cancelled) jobs
eve job list --disposition failed                          # Explicit disposition filter
```

Flags: `--label`, `--type`, `--root` (root jobs only, excludes children), `--dead-letters` (shorthand for `--phase cancelled --disposition failed`), `--disposition` (`failed` | `cancelled` | `upstream_failed`).

### Summary Follow Mode

```bash
eve job follow <job-id> --summary
eve job logs <job-id> --summary
```

`--summary` emits only actionable lines: phase transitions, permission rejections, periodic LLM cost/token aggregates, tool names (no I/O), eve-message blocks, errors, and a final summary footer with totals (LLM calls, tokens in/out, cost, tool uses). Cuts hundreds of raw JSONL lines to ~20 lines.

### Active-Job Observability

For active jobs, the CLI now exposes the same signals operators previously had to cross-check in kubectl:

- `eve job diagnose <job-id>` includes the latest attempt pod name from `runtime_meta`, best-effort live pod health from agent-runtime status, and the most recent harness heartbeat age.
- `eve job follow <job-id>` warns after 60s and 120s of silence. If heartbeat lifecycle events are still arriving, it reports the harness as alive but quiet; otherwise it warns that the run may have stalled.
- `eve agents runtime-status --org <org-id>` now shows stale pods and active-job counts in the tabular output.
- `eve system status` now renders agent-runtime health alongside API, orchestrator, worker, and queue state when the backend returns it.

## Production Hardening

### Content-Hash Deduplication (Ingest)

`eve ingest confirm` checks the S3 ETag as a content fingerprint. If an identical file was already confirmed in the same project, it returns the existing record (`deduplicated: true`) instead of firing a new processing event. Use `--force` to skip the dedup check.

### Failure Disposition (Dead Letters)

Jobs have a `failure_disposition` field distinguishing intentional cancellation from exhausted-retry failure:

| Value | Meaning |
|-------|---------|
| `cancelled` | Explicitly cancelled by user/API |
| `failed` | Failed after exhausting retries |
| `upstream_failed` | Cascaded failure from upstream dependency |

Query dead letters: `GET /projects/{id}/jobs?phase=cancelled&failure_disposition=failed`

### Auto-Retry with Backoff

Configure retry policy via hints or CLI:

```bash
eve job create --description "Process data" --retry-max 3 --retry-backoff 30
```

Policy fields (in `hints.retry`):
- `max_attempts` — max attempts before permanent failure (default: 1 = no retry)
- `backoff_seconds` — base delay (default: 60)
- `backoff_multiplier` — exponential multiplier (default: 2)
- `retryable_errors` — error codes eligible for retry (default: `['attempt_timeout', 'attempt_stale']`)

On failure, the orchestrator checks the retry policy. If retries remain and the error is retryable, it creates a new attempt with `trigger_type = 'auto_retry'` and sets `defer_until` for backoff. When retries are exhausted, the job gets `failure_disposition = 'failed'`.

Workflow steps support retry in the manifest:

```yaml
steps:
  - name: ingest
    agent: doc-processor
    retry:
      max_attempts: 3
      backoff_seconds: 30
      retryable_errors: [attempt_timeout, attempt_stale]
```

### Cost Tracking

```bash
eve analytics cost-by-agent --window 7d
```

Groups cost by agent across all projects in the org. Shows attempts, total cost, and token counts per agent.

### Per-Phase Latency in Diagnostics

`eve job diagnose` now shows a latency waterfall from existing lifecycle execution logs:

```
Latency Breakdown:
  provision/clone     12,340ms  ████████░░░░░░░░  14%
  provision/setup      2,100ms  █░░░░░░░░░░░░░░░   2%
  invoke/harness      71,200ms  ████████████████  82%
  cleanup/workspace    1,400ms  █░░░░░░░░░░░░░░░   2%
  ────────────────────────────
  Total               87,040ms
```

The same diagnostic view now adds:
- pod health correlation for active jobs when the latest attempt includes `runtime_meta.pod_name`
- heartbeat-aware stuck detection (`Harness alive` vs `No harness heartbeat`)
- pre-harness startup timing visibility, including clone/setup work that previously required pod logs

### Routing Decision Logging

A structured `routing` execution log is written at claim time, capturing harness selection, target (agent-runtime vs worker), budget config, and selection source. Visible in `eve job diagnose` and `eve job logs`.

### Auto-Expiry for Stale Documents

Org documents with `expires_at` are automatically transitioned to `expired` status by a background loop (every 15 minutes). After a grace period (default 7 days, configurable via `EVE_DOC_EXPIRY_GRACE_DAYS`), expired documents are archived (content cleared, metadata preserved).

## Per-Job HOME Isolation

Each job attempt gets an isolated HOME directory at `/tmp/eve/agent-homes/<attemptId>/home/`. The worker overrides `HOME` and sets `EVE_JOB_USER_HOME` in the harness environment. Pre-created directories:

- `.config/eve/` — Eve CLI credentials
- `.config/gh/` — GitHub CLI auth
- `.claude/` — Claude config
- `.eve/harnesses/` — Harness config

All directories are mode 0700. Cleaned up after the attempt completes. This prevents agents from reading credentials written for other jobs or the host system.

## Not Yet Implemented

- Workspace reuse (`workspace.mode=job|session|isolated`). Today every attempt gets a fresh workspace.
- Disk LRU/TTL cleanup policies.
- Review semantics that compute diffs for branch-based jobs.
