# CLI: Jobs

## Use When
- You need to create jobs, inspect job state, or attach monitoring/attachments.
- You need to submit results, handle dependencies, or batch-submit job graphs.
- You need retry, review, and attempt-level controls.

## Load Next
- `references/jobs.md` for lifecycle and scheduling model.
- `references/cli-pipelines.md` when jobs are part of pipelines.
- `references/deploy-debug.md` for runtime execution symptoms.

## Ask If Missing
- Confirm root job ID vs child job ID format and whether to perform create, query, or review actions.
- Confirm target project scope and any permission expectations.
- Confirm whether you need attempt-level details (`--attempt`) or scheduler-level snapshots.

## Jobs

See `references/jobs.md` for lifecycle details. Jobs are the fundamental unit of work.

```bash
# Create
eve job create --description "Fix the login bug"
  [--project <id>] [--parent <id>]                     # Root or child job
  [--title "Short title"]                               # Auto-derived from description if omitted
  [--type task] [--priority 2] [--phase ready]
  [--review none|human|agent]
  [--labels "bug,urgent"] [--assignee user_abc]
  [--defer-until 2026-03-01] [--due-at 2026-03-15]
  [--env staging] [--execution-mode persistent|ephemeral]
  [--resource-refs '<json-array>']                      # Resource refs (org docs/attachments)
  [--with-apis <names>]                                 # Comma-separated API names to inject
  [--claim] [--agent <id>]                              # Create and immediately claim

  # Scheduling hints
  [--harness mclaude:fast] [--profile <name>]
  [--variant <v>] [--model <m>] [--reasoning low|medium|high|x-high]
  [--worker-type default] [--permission auto_edit]
  [--timeout 3600] [--resource-class job.c1]
  [--max-tokens 100000] [--max-cost 5.00]

  # Git controls (override project/manifest defaults)
  [--git-ref main] [--git-ref-policy auto|env|project_default|explicit]
  [--git-branch feature/fix] [--git-create-branch never|if_missing|always]
  [--git-commit never|manual|auto|required]
  [--git-commit-message "template"]
  [--git-push never|on_success|required] [--git-remote origin]

  # Workspace
  [--workspace-mode job|session|isolated]
  [--workspace-key <key>]

# List and filter
eve job list [--project <id>] [--phase ready|active|done|blocked]
  [--assignee <id>] [--priority <n>] [--since 1h]
  [--stuck] [--stuck-minutes 30]
  [--limit 50] [--offset 0]
eve job list --all [--org <id>] [--project <id>]        # Admin: cross-project listing
eve job ready [--project <id>] [--limit 10]             # Schedulable jobs shortcut
eve job blocked [--project <id>]                        # Dependency-blocked jobs

# Inspect
eve job show <job-id> [--verbose]                       # Job details (+attempts if verbose)
eve job current [<job-id>]                              # Context view (defaults to $EVE_JOB_ID)
  [--tree]                                              # Show full job tree
eve job tree <job-id>                                   # Job hierarchy tree
eve job diagnose <job-id>                               # Full diagnostic dump

# Lifecycle
eve job update <job-id> [--title] [--priority] [--phase] [--labels] ...
eve job close <job-id> [--reason "completed"]           # Close job
eve job cancel <job-id> [--reason "no longer needed"]   # Cancel job

# Dependencies
eve job dep list <job-id>                               # List dependencies
eve job dep add <job-id> <depends-on-id>                # Add dependency
eve job dep remove <job-id> <depends-on-id>             # Remove dependency

# Execution
eve job claim <job-id> [--agent <id>] [--harness <name>]  # Claim for execution
eve job release <job-id>                                # Release claim
eve job submit <job-id> [--status succeeded|failed]     # Submit result
  [--summary "Done"] [--result-json '{}']
eve job approve <job-id>                                # Approve reviewed job
eve job reject <job-id> [--reason "needs changes"]     # Reject reviewed job

# Monitoring
eve job follow <job-id>                                 # Stream harness logs (SSE)
  # Silence detection: warns at 60s/120s with heartbeat context
  # Heartbeat events silently consumed (tracked, not printed)
eve job wait <job-id> [--timeout 300]                   # Block until job completes
eve job watch <job-id>                                  # Combined status + log stream
eve job runner-logs <job-id>                            # K8s runner pod logs

# Results
eve job result <job-id> [--attempt <n>]                 # Get attempt result
eve job attempts <job-id>                               # List all attempts
eve job logs <job-id> [--attempt <n>] [--after <cursor>]  # Fetch harness logs
eve job receipt <job-id>                                # Cost/token receipt
eve job compare <job-id>                                # Compare attempt results

# Attachments
eve job attach <job-id> --file <path> --name <name> [--mime <type>]
eve job attach <job-id> --stdin --name <name> [--mime <type>]
eve job attachments <job-id>                            # List attachments
eve job attachment <job-id> <name>                      # Get attachment content

# Batch operations
eve job batch --project <id> --file <path>              # Submit batch job graph
eve job batch-validate --file <path>                    # Validate batch without submitting
```

Notes:
- `--claim` on create is the inline-execution pattern: create + claim in one call.
- `--since` accepts relative time (`1h`, `30m`, `2d`) or ISO timestamps.
- `--stuck` filters to jobs active longer than expected (default or `--stuck-minutes`).
- `follow` uses SSE streaming with built-in silence detection (60s/120s warnings). Heartbeat lifecycle events from the harness are silently tracked but not printed as log lines. `watch` combines status polling with log tailing.
- `runner-logs` fetches K8s pod logs, useful for debugging harness startup failures.
- `diagnose` shows heartbeat-aware stuck detection, pod name + live health from agent-runtime, and pre-harness startup timing in the latency waterfall (git clone, credentials, app CLI discovery).
- `--with-apis` is server-side: the CLI passes `app_apis` in job hints; the server validates APIs exist, generates the instruction block, and appends it to the description. Same behavior for CLI, API, workflow, and SDK job creation paths.
