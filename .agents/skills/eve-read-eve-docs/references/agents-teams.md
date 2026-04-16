# Agents, Teams + Chat Routing

## Use When
- You need to define or verify agent and team YAML for chat dispatch.
- You need to route inbound Slack/Nostr messages to specific personas or team workflows.
- You need to set or audit gateway discovery policy (`none`, `discoverable`, `routable`).

## Load Next
- `references/gateways.md` to map provider-specific message handling.
- `references/pipelines-workflows.md` for job-based escalation or workflow handoffs.
- `references/skills-system.md` when resolving agent pack prerequisites.

## Ask If Missing
- Confirm the target project/org manifest path and whether agents are repo-synced.
- Confirm whether routing is intended to be command-only or auto-routable in chat.
- Confirm if team dispatch should use fanout, relay, or council semantics (and whether staged preparation is needed).

## Overview

Agents, teams, and chat routes are repo-first YAML configurations synced to Eve via `eve agents sync`. The repo is the source of truth. Agents are personas with skills and policies; teams are dispatch groups that coordinate agents; routes map inbound chat messages to targets.

## agents.yaml

Define agents with capabilities, access, policies, and gateway visibility.

```yaml
version: 1
agents:
  mission-control:
    slug: mission-control           # org-unique, ^[a-z0-9][a-z0-9-]*$
    name: "Mission Control"         # human-readable display name
    alias: mc                       # optional short name for chat addressing
    description: "Primary orchestration agent"
    skill: eve-orchestration        # required
    workflow: nightly-audit          # optional
    harness_profile: primary-orchestrator
    access:
      envs: [staging, production]
      services: [api, web]
      api_specs: [openapi]
      permissions:                    # extra permissions merged with defaults
        - projects:write
        - envdb:write
    policies:
      permission_policy: auto_edit   # auto_edit | never | yolo
      git:
        commit: auto                 # never | manual | auto | required
        push: on_success             # never | on_success | required
    with_apis:
      - service: api
        description: App REST API for reading and writing data
    context:
      memory:
        agent: shared
        categories: [decisions, conventions, context]
        max_items: 20
      threads:
        coordination: true
        max_messages: 30
    gateway:
      policy: routable               # none | discoverable | routable
      clients: [slack]               # omit = all providers
    schedule:
      heartbeat_cron: "*/15 * * * *"
```

### Agent Context

The `context` block gives an agent access to shared memory and coordination thread history across invocations.

```yaml
context:
  memory:
    agent: shared              # memory scope: "shared" (team-wide) or agent slug (private)
    categories: [learnings, decisions, conventions, context, user]  # filter memory categories
    max_items: 20              # max memory items injected into prompt
    max_age: 30d               # optional: only include entries updated within this window
  docs:
    - path: /agents/my-agent/skills/
      recursive: true          # load skill docs for on-demand procedures
  threads:
    coordination: true         # inject recent coordination thread messages
    max_messages: 30           # max thread messages injected
```

- `memory` provides persistent recall across jobs. Use `agent: shared` for team-wide memory or the agent's own slug for private memory.
- **Memory categories**: `learnings` (discoveries), `decisions` (choices with rationale), `conventions` (project patterns), `context` (environment facts), `runbooks` (operational procedures), `user` (user-specific preferences and interaction history).
- `docs` loads org doc paths into `.eve/context/docs/` at session start. Use for skill libraries and shared knowledge.
- `threads.coordination: true` injects recent messages from the team coordination thread, giving the agent awareness of ongoing discussions.

### Agent Slug Rules

- Lowercase alphanumeric + dashes, org-unique, enforced at sync.
- Pack resolver prefixes slugs with the project slug (e.g., `pm` in project `pmbot` becomes `pmbot-pm`).
- Used for Slack routing: `@eve <slug> <command>`.
- Set a default: `eve org update org_xxx --default-agent <slug>`.

### Agent Aliases

Aliases are optional short names that bypass the prefixed slug for chat addressing. Users type `@eve pm hello` instead of `@eve pmbot-pm hello`.

```yaml
agents:
  pm:
    slug: pm
    alias: pm              # short vanity name for chat
    skill: pm-coordinator
    gateway:
      policy: routable
```

Key rules:
- Aliases and slugs share the same org-scoped routing namespace. If a slug `pm` exists, no other agent can claim alias `pm`.
- Matching is case-insensitive and trimmed.
- Reserved words that cannot be used as aliases: `agents`, `help`, `status`, `eve`, `admin`, `system`, `health`.
- Aliases are NOT prefixed by the pack resolver -- that is the entire point.
- Alias uniqueness is validated at sync time. Collisions with existing slugs or aliases are rejected.

Resolution order at chat dispatch:

1. Slug match (canonical prefixed slug)
2. Alias match
3. Team name match (see Gateway Team Dispatch below)
4. Org default agent fallback

The `@eve agents list` display shows aliases alongside canonical slugs (e.g., `pmbot-pm (-> pm)`).

### Agent Permissions

Agents receive a default set of job token permissions (`jobs:read/write`, `projects:read`, `threads:read/write`, `envdb:read`, `secrets:read`, `builds:read`, `pipelines:read`). Declare extra permissions in `access.permissions` to grant more:

```yaml
agents:
  map-generator:
    skill: map-gen
    access:
      permissions:
        - projects:write
        - envdb:write
        - envs:write
```

Rules:
- **Additive only** — declared permissions are merged with defaults, never replacing them.
- **Validated at sync** — unknown permission strings are rejected.
- **Per-agent** — different agents in the same project can have different permissions.
- Only applies when minting fresh tokens. Pre-existing/embedded tokens are used as-is.

### Gateway Discovery Policy

Control which agents are visible and directly addressable from external chat gateways. Internal dispatch (teams, pipelines, routes) is always unaffected.

| Policy | `@eve agents list` | `@eve <slug> msg` | Internal dispatch |
|--------|--------------------|--------------------|-------------------|
| `none` | Hidden | Rejected | Works |
| `discoverable` | Visible | Rejected (hint) | Works |
| `routable` | Visible | Works | Works |

Resolution order: pack `gateway.default_policy` (base, defaults to `none`) -> agent `gateway.policy` -> project overlay.

### App API Access (`with_apis` + Auto-Discovery)

**CLI-first is the Eve way.** When an app has an API, wrap it in a CLI and declare it via `x-eve.cli` in the manifest. Agents should use CLI commands (`myapp items list`) instead of raw REST calls (`curl "$EVE_APP_API_URL_API/items"`). CLIs handle auth, URL construction, and error formatting transparently — reducing LLM calls per operation from 3-5 to 1. If you're building an app and an agent needs to interact with it, build a CLI.

**Auto-discovery**: The platform automatically scans the manifest for services with `x-eve.cli` or `x-eve.api_spec` declarations and injects them into every agent job. No explicit `with_apis` is needed — if your manifest declares a CLI, all agents in the project get it on PATH automatically.

**Explicit `with_apis`** still works and takes priority when declared. Use it to restrict which APIs a specific agent or workflow step sees:

```yaml
agents:
  data-agent:
    skill: data-processing
    with_apis:
      - service: api          # explicit: only this service
```

The agent receives:
- `EVE_APP_API_URL_{SERVICE}` env var with the service URL
- `EVE_JOB_TOKEN` for authentication
- If the service has `x-eve.cli`: the CLI binary on PATH (e.g., `eden --help`)
- An instruction block describing available APIs and CLIs

See `references/app-cli.md` for building CLIs that agents use instead of raw REST calls.

## teams.yaml

Define teams with a lead agent, members, and a dispatch mode.

```yaml
version: 1
teams:
  review-council:
    lead: mission-control
    members: [code-reviewer, security-auditor]
    dispatch:
      mode: fanout
      max_parallel: 3
      lead_timeout: 300
      member_timeout: 300
      merge_strategy: majority

  ops:
    lead: ops-lead
    members: [deploy-agent, monitor-agent]
    dispatch:
      mode: relay
```

### Team Dispatch Modes

| Mode | Behavior |
|------|----------|
| `fanout` | Root job + parallel child jobs per member |
| `council` | All agents respond, results merged by strategy |
| `relay` | Sequential delegation from lead through members |

### Staged Team Dispatch

Staged dispatch is an option on council mode where the lead prepares work before members start. Use it when members need processed input (e.g., a transcript, summary, or extracted data) that the lead must produce first.

```yaml
teams:
  expert-panel:
    lead: pm-coordinator
    members: [tech-lead, ux-advocate, biz-analyst, risk-assessor]
    dispatch:
      mode: council
      staged: true              # lead runs first, then members fan out
      lead_timeout: 3600
      member_timeout: 300
```

`staged: true` is only valid with `mode: council`. Schema validation rejects other combinations.

Lifecycle:

1. **Dispatch** -- Lead job is created in `ready` phase. Member jobs are created in `backlog` phase (visible via `eve job list` but not claimable by the orchestrator).
2. **Prepare** -- Lead runs, does pre-processing (transcription, analysis, etc.), posts prepared content to the coordination thread, then returns `eve.status = "prepared"`.
3. **Promote** -- Orchestrator detects `prepared` on a staged job, promotes all `backlog` children to `ready`, and requeues the lead with `wake_on: [children.all_done]`.
4. **Parallel work** -- Members run concurrently, each reading `.eve/coordination-inbox.md` for the lead's prepared content. Each returns `eve.summary` which auto-relays to the coordination thread.
5. **Synthesize** -- Lead wakes when all children complete, reads member summaries from the coordination inbox, produces a final synthesis, returns `eve.status = "success"`.

Edge cases:
- If the lead returns `success` or `failed` without ever returning `prepared`, backlog children are automatically cancelled.
- If staged is true but the team has no members, the lead runs normally (warning logged).

Lead agent skill pattern -- return `prepared` after phase 1, then `success` after synthesis:

```json
{"eve": {"status": "prepared", "summary": "Content prepared for expert review"}}
```

## chat.yaml

Define routing rules with explicit target prefixes.

```yaml
version: 1
default_route: route_default
routes:
  - id: deploy-route
    match: "deploy|release|ship"
    target: agent:deploy-agent
    permissions:
      project_roles: [admin, member]

  - id: review-route
    match: "review|PR|pull request"
    target: team:review-council

  - id: route_default
    match: ".*"
    target: team:ops
    permissions:
      project_roles: [member, admin, owner]
```

### Route Matching

- `match` is a regex tested against message text.
- First match wins; fallback to `default_route` if none match.
- Target prefixes: `agent:<key>`, `team:<key>`, `workflow:<name>`, `pipeline:<name>`.

## Syncing Configuration

```bash
# Sync from committed ref (production)
eve agents sync --project proj_xxx --ref abc123def456...

# Sync local state (development)
eve agents sync --project proj_xxx --local --allow-dirty

# Preview effective config without syncing
eve agents config --repo-dir ./my-app
```

Sync resolves AgentPacks from `x-eve.packs`, deep-merges pack agents/teams/chat with local overrides, validates org-wide slug and alias uniqueness, and pushes to the API.

### Pack Overlay

Local YAML overlays pack defaults via deep merge. Use `_remove: true` to drop a pack agent.

```yaml
agents:
  pack-agent:
    harness_profile: my-custom-profile   # override pack default
  unwanted-agent:
    _remove: true                         # remove from pack
```

## Warm Pods / Agent Runtime

Warm pods are pre-provisioned org-scoped containers that eliminate cold starts for chat-triggered jobs. Routing is org-sticky.

```bash
eve agents runtime-status --org org_xxx
```

Output includes stale detection and summary:
```
Pod                  Status           Capacity  Age   Last Heartbeat
--------------------------------------------------------------------
eve-agent-runtime-0  healthy (stale)  8         145h  2026-03-18T15:19:04.402Z
eve-agent-runtime-1  healthy          8         9s    2026-03-24T16:19:27.286Z

Summary: 1 healthy, 1 stale
```

- **All pods are shown** (stale pods are no longer filtered out — they're marked with `(stale)` instead).
- **Stale** means the pod hasn't sent a heartbeat within the TTL window (`AGENT_RUNTIME_HEARTBEAT_TTL_MS`, default 45s).
- **Active jobs** count is shown when available (e.g., `[2 active]` after the heartbeat timestamp).

`eve system status` also renders agent-runtime health with replica count.

Data model: `agent_runtime_pods` (heartbeat + capacity), `agent_placements` (pod selection), `agent_state` (status + heartbeat).

## Coordination Threads

When teams dispatch work, a coordination thread links the parent job to all child agents.

- Thread key: `coord:job:{parent_job_id}`
- Child agents receive `EVE_PARENT_JOB_ID` environment variable
- Derive the thread key: `coord:job:${EVE_PARENT_JOB_ID}`
- End-of-attempt summaries auto-post to the coordination thread
- Coordination inbox: `.eve/coordination-inbox.md` (regenerated from recent messages at job start)

### Coordination Message Kinds

| Kind | Purpose |
|------|---------|
| `status` | Automatic end-of-attempt summary |
| `directive` | Lead-to-member instruction |
| `question` | Member-to-lead question |
| `update` | Progress update from a member |

### Thread CLI

```bash
eve thread messages <thread-id> --since 5m      # list recent messages
eve thread post <thread-id> --body '{"kind":"update","body":"Phase 1 complete"}'
eve thread follow <thread-id>                    # stream in real-time
```

## Chat Outbound Delivery

Agent results are automatically posted back to the originating Slack thread. When a chat-originated job completes, the orchestrator detects the `chat` label and `hints.thread_id`, extracts the result text (falling back to `eve.summary`), and pushes it through the delivery pipeline:

```
Orchestrator → POST /internal/projects/{id}/chat/deliver → API → Gateway → Slack thread
```

Key behaviors:
- Delivery is fire-and-forget -- failures are logged but never block job completion.
- Threads store provider metadata (`metadata_json`) with `provider`, `account_id`, `channel_id`, and `thread_id` for outbound routing.
- Outbound messages are recorded as `thread_messages` with `direction = 'outbound'` and tracked via `delivery_status` (`pending`, `delivered`, `failed`).
- Duplicate delivery is prevented by a unique index on `job_id` for outbound messages.
- Messages over 3900 characters are truncated with a pointer to `eve job result <id>`.

Inspect delivery status via CLI:

```bash
eve thread messages <thread_id>
# Shows: inbound user message, system ack, outbound agent reply with delivery status
```

## Chat Progress Updates

Agents can send real-time progress updates to the originating Slack thread during execution. The agent emits `eve-message` fenced blocks in its output, and the `EveMessageRelay` on the agent-runtime delivers them to the chat channel.

```
```eve-message
Pulling metrics data from the warehouse...
```                                          # ← posted to Slack thread as progress
```

The relay also accepts structured JSON with a `body` field:

```
```eve-message
{"kind":"progress","body":"Found 847 records, analyzing trends..."}
```
```

Rate limiting:
- Coordination thread (internal): 1 message per 5 seconds, no cap.
- Chat delivery (external): 1 message per 30 seconds, max 10 per job. Progress text is capped at 500 characters.

Progress updates reuse the same delivery pipeline as final results (`POST /internal/.../chat/deliver` with `progress: true`). They are stored as `thread_messages` with `job_id = NULL` (bypassing the outbound idempotency constraint).

Works for both single-agent chat jobs and team dispatch child jobs. Non-chat jobs only relay to the coordination thread.

## Supervision

Monitor a job tree and coordinate team execution.

```bash
eve supervise                       # supervise current job
eve supervise <job-id> --timeout 60 # supervise specific job with timeout
```

Long-polls child job events for the lead agent.

## Slack Integration

### Routing Commands (in Slack)

```
@eve <slug-or-alias> <command>      # direct to specific agent (slug or alias)
@eve <team-name> <command>          # direct to team lead (gateway team dispatch)
@eve agents list                    # list available agent slugs + aliases
@eve agents listen <agent-slug>     # subscribe agent to channel or thread
@eve agents unlisten <agent-slug>   # unsubscribe agent
@eve agents listening               # list active listeners
```

### Gateway Team Dispatch

Teams can be addressed directly from chat using the team name. When a user types `@eve expert-panel review this`, the gateway resolves the name through the standard chain (slug, then alias, then team name lookup). If a team matches:

1. The team lead's `gateway_policy` is checked -- dispatch is rejected if the lead is `none` or the provider is not in the lead's `clients` list.
2. The chat service creates the full team dispatch (fanout/council/relay with staged support) directly, bypassing route matching.
3. Each job receives per-job HOME isolation (`EVE_JOB_USER_HOME`).

This is equivalent to having a `chat.yaml` route with `target: team:expert-panel`, but without needing to define one.

### Thread-Level vs Channel-Level Listeners

- Issue `listen` in a channel: creates a **channel-level** listener (all messages in the channel).
- Issue `listen` inside a thread: creates a **thread-level** listener (only messages in that thread).
- Multiple agents can listen to the same channel or thread.
- Listening uses `message.channels` events; explicit `@eve` commands use `app_mention`.

### Slack CLI Setup

```bash
eve integrations slack connect --org org_xxx --team-id T123 --token xoxb-test
eve integrations list --org org_xxx
eve integrations test <integration_id> --org org_xxx
```

### Default Agent

```bash
eve org update org_xxx --default-agent mission-control
```

When a message does not match any slug, alias, or team name, Eve routes to the org default agent with the full message as the command.

## Chat Simulation

Test the full routing pipeline without a live provider.

```bash
eve chat simulate --project <id> --team-id T123 --channel-id C123 --user-id U123 --text "hello" --json
```

Returns `thread_id` and `job_ids` showing how the message would be dispatched.

## Deleting Agents and Teams

```bash
eve agents delete <slug> --project <id>
eve agents delete-team <team_id> --project <id>
eve thread delete <thread_id>
```

## API Endpoints

```
POST /projects/{id}/agents/sync       # sync agents/teams/chat config
POST /projects/{id}/agents/config     # get effective merged config
GET  /agents                           # list agents (includes alias column)
GET  /teams                            # list teams

GET  /threads/{id}/messages            # list thread messages (includes delivery_status)
POST /threads/{id}/messages            # post to thread
GET  /threads/{id}/follow              # stream thread messages (SSE)

POST /chat/route                       # route inbound message
POST /chat/simulate                    # simulate chat message
POST /chat/listen                      # subscribe agent to channel/thread
POST /chat/unlisten                    # unsubscribe agent
GET  /chat/listeners                   # list active listeners

POST /internal/projects/{id}/chat/deliver  # deliver result/progress to chat thread (internal)
POST /gateway/internal/deliver             # gateway sends to provider (internal)
```
