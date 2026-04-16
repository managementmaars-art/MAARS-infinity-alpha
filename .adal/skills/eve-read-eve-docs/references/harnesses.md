# Harness Execution Reference

## Use When
- You need to choose or compare available harnesses and profiles.
- You need workspace, permission, or sandbox guidance for job execution.
- You need to trace how Eve invokes harness binaries during execution.

## Load Next
- `references/jobs.md` for execution lifecycle and attempt scheduling.
- `references/cli.md` for harness-specific profile commands.
- `references/secrets-auth.md` for credentials and secret injection.

## Ask If Missing
- Confirm target harness and repo path for execution.
- Confirm permission policy and sandbox mode requirements (`inline` vs `runner`).
- Confirm available secrets/toolchain constraints for command execution.

Eve executes AI work through **harnesses** -- thin adapters that wrap AI coding CLIs
(Claude Code, Gemini CLI, Codex, etc.) behind a uniform invocation contract. All model
access is BYOK: harnesses and apps bring their own API keys via secrets and call
providers directly. Eve never proxies inference traffic. This reference covers the full
lifecycle: invocation, workspace setup, authentication, per-harness configuration,
policy controls, and introspection.

---

## Invocation Flow

Both the worker and agent-runtime execute jobs through a shared invoke module
(`packages/shared/src/invoke/`). Agent jobs route to the agent-runtime; builds,
deploys, pipelines, and scripts route to the worker. The shared module provides
full feature parity across both runtimes.

Every job attempt follows a two-stage pipeline:

```
HarnessInvocation
  { attemptId, jobId, projectId, text, workspacePath, repoUrl, harness, toolchains }
        |
        v
InvokeService.execute()  (worker or agent-runtime, both using shared invoke module)
  1. prepareWorkspace()          -- mkdir + git clone/copy
  2. writeCarryoverContext()     -- memory, docs, parent attachments
  3. stageAttachments()          -- download chat files to workspace
  4. writeSecurityClaudeMd()     -- security policy to CLAUDE_CONFIG_DIR
  5. resolveWorkerAdapter()      -- look up WorkerHarnessAdapter by name
  6. adapter.buildOptions(ctx)   -- resolve auth, config dirs, env
  7. BudgetEnforcer.start()      -- enforce max_tokens/max_cost via llm.call tracking
  8. executeEveAgentCli()        -- spawn eve-agent-cli, stream JSON to execution_logs
        |
        v
eve-agent-cli
  1. resolveCliAdapter(harness)  -- look up CliHarnessAdapter by name
  2. adapter.buildCommand(ctx)   -- binary + args + env; map permission policy to flags
  3. spawn(binary, args, {cwd: repoPath, env})
     -- run the harness CLI, normalize output to JSON events
```

The worker never calls harness binaries directly. It always goes through `eve-agent-cli`,
which owns argument construction, permission mapping, and output normalization.

### Shared Invoke Module

Agent-execution features live in `packages/shared/src/invoke/` and are imported by
both worker and agent-runtime. Key modules:

| Module                   | Purpose                                              |
|--------------------------|------------------------------------------------------|
| `budget-enforcement.ts`  | BudgetEnforcer: max_tokens/max_cost, llm.call tracking, kill |
| `carryover-context.ts`   | Write memory, docs, parent attachments to workspace  |
| `security-policy.ts`     | Build and write security CLAUDE.md                   |
| `result-extraction.ts`   | Extract result text, JSON, token usage, error messages |
| `attachment-staging.ts`  | Stage chat file attachments into workspace           |
| `coordination.ts`        | Write coordination inbox and thread context           |
| `workspace-hooks.ts`     | Run acquire/release hooks                            |
| `workspace-secrets.ts`   | Resolve, materialize, and clean up secrets           |
| `eve-message-relay.ts`   | EveMessageRelay: deliver to chat + coordination thread |
| `resource-hydration.ts`  | Hydrate resources with lifecycle events              |
| `harness-lifecycle.ts`   | Log harness start/end events                         |
| `codex-auth.ts`          | Write-back refreshed Codex auth tokens               |

New agent-execution features go in the shared module, never in a single runtime.

---

## Harness Naming and Aliases

| Harness    | Binary    | Aliases  | Notes                                               |
|------------|-----------|----------|-----------------------------------------------------|
| `mclaude`  | `mclaude` | --       | cc-mirror Claude variant                             |
| `claude`   | `claude`  | --       | Official @anthropic-ai/claude-code                   |
| `zai`      | `zai`     | --       | cc-mirror Z.ai variant                               |
| `gemini`   | `gemini`  | --       | @google/gemini-cli                                   |
| `code`     | `code`    | `coder`  | @just-every/code. Use `coder` on host to avoid VS Code clash |
| `codex`    | `codex`   | --       | @openai/codex                                        |

Do not parse `harness:variant` syntax. Use `harness_options.variant` instead.

---

## Workspace Directory Structure

```
$WORKSPACE_ROOT/                       # e.g. /opt/eve/workspaces
  {attemptId}/                         # unique per attempt
    repo/                              # cloned/copied repository
      AGENTS.md                        # project memory for agents
      CLAUDE.md                        # Claude-specific instructions
      .agents/skills/                   # installed skills (gitignored)
      .agents/harnesses/<harness>/      # per-harness config (optional)
      .claude/skills/                  # symlink or overrides (gitignored)
```

| Variable        | Value                              | Description                        |
|-----------------|------------------------------------|------------------------------------|
| `workspacePath` | `$WORKSPACE_ROOT/{attemptId}`      | Root workspace for this attempt    |
| `repoPath`      | `$workspacePath/repo`              | Cloned repository                  |
| `cwd` (harness) | `$repoPath`                        | Working directory for execution    |

The harness runs with `cwd = repoPath` so it sees AGENTS.md, CLAUDE.md, and project files.

### Environment Contract

- `EVE_WORKSPACE_ROOT` -- root for all workspaces (e.g. `/opt/eve/workspaces`)
- `EVE_CACHE_ROOT` -- shared cache for package managers and build artifacts
- Processes run as UID 1000 (non-root); workspace dirs are writable
- Cache directories are shared across attempts for efficiency
- Credentials and config injected via secrets/config maps

---

## Repository Preparation

The worker requires `repoUrl` for every job. Preparation depends on URL type:

**Remote URL** (https://, git://):
- If `job.git` is set, use **GitWorkspace**: shallow clone of the resolved ref,
  fetch-based checkout, branch creation if requested.
- Otherwise, legacy shallow clone: `git clone --depth 1 --branch <branch> <url>`.

**Local URL** (file://):
- Copy directory with `fs.cp`. Branch is ignored. Dev/test only.
- Not supported in k8s runtime or push-required workflows.

### Git Controls

When a job has `git` configuration, the worker:

1. Resolve the ref per `git.ref_policy` (env release -> manifest defaults -> project branch).
2. Create or check out a branch per `git.branch` and `git.create_branch`.
3. Apply commit and push policies **after** execution:
   - `commit=auto` -- `git add -A` and commit any changes, even on failed attempts.
   - `commit=required` -- fail on success if the working tree is clean.
   - `push=on_success` or `push=required` -- push only when the worker created commits.
4. Store resolved metadata on the attempt (`job_attempts.git_json`).

---

## Worker Image and Toolchains

The default worker image is `base` (~800MB), which includes Node.js, git, gh, kubectl,
kaniko, buildctl, and all harness binaries (claude-code, codex, gemini-cli, cc-mirror,
code, bd, skills). Most agent jobs need nothing beyond this.

### Toolchain-on-Demand

Toolchains (Python, Rust, Java, Kotlin, ffmpeg/whisper) are delivered as init containers
rather than baked into the worker image. This replaces the previous `full` image (2.6GB)
approach.

Available toolchains:

| Toolchain | Contents                                     | Approx Size |
|-----------|----------------------------------------------|-------------|
| `python`  | Python 3, pip, venv, uv                      | ~100MB      |
| `media`   | ffmpeg, whisper-cli, ggml-small.en model     | ~300MB      |
| `rust`    | rustup, stable toolchain, rustfmt, clippy    | ~400MB      |
| `java`    | Temurin JDK 21                               | ~300MB      |
| `kotlin`  | kotlinc 2.0.21 + bundled JDK 21             | ~350MB      |

Init containers copy toolchain payloads from small single-purpose images into
`/opt/eve/toolchains/{name}/`. The entrypoint extends `PATH` from `EVE_TOOLCHAIN_PATHS`
and sources per-toolchain `env.sh` files for variables like `JAVA_HOME` and `CARGO_HOME`.

### Declaring Toolchains

Agents declare required toolchains in their config:

```yaml
# eve/agents.yaml
agents:
  data-analyst:
    name: Data Analyst
    skill: analyze-data
    harness_profile: claude-sonnet
    toolchains: [python]

  doc-processor:
    name: Document Processor
    skill: process-documents
    harness_profile: claude-sonnet
    toolchains: [media]
```

Workflows can override the agent default:

```yaml
# eve/workflows.yaml
workflows:
  process-document:
    trigger:
      system.event: doc.ingest
    steps:
      - name: process
        agent: doc-processor
        toolchains: [media, python]    # override agent default
```

Toolchain precedence: workflow step `toolchains` overrides agent `toolchains` overrides
empty (base-only). The `full` image remains available via `EVE_WORKER_VARIANT=full` for
backwards compatibility.

### Runner Pod Injection

For K8s runner pods, the orchestrator generates init containers from the `toolchains`
array. Each init container copies its payload into a shared `emptyDir` volume mounted
at `/opt/eve/toolchains/`. On nodes with a persistent toolchain cache (node-local PVC),
init containers skip the copy if the cached version matches.

---

## Disk Management

Operator knobs (env vars):

| Variable                    | Purpose                                    |
|-----------------------------|--------------------------------------------|
| `EVE_WORKSPACE_MAX_GB`      | Total workspace budget per instance        |
| `EVE_WORKSPACE_MIN_FREE_GB` | Hard floor; refuse new claims if below     |
| `EVE_WORKSPACE_TTL_HOURS`   | Idle TTL for job worktrees                 |
| `EVE_SESSION_TTL_HOURS`     | Idle TTL for session workspaces            |
| `EVE_MIRROR_MAX_GB`         | Cap for bare mirrors                       |

Policies: LRU eviction when over budget. TTL cleanup for idle worktrees. Mirror
maintenance via `git fetch --prune` and periodic `git gc --prune=now`. Fail-fast on
low disk (emit system event; do not start new attempts).

K8s: per-attempt PVCs are deleted after completion. Session-scoped PVCs use TTL cleanup.

---

## Authentication

### Claude-Based Harnesses (mclaude, claude, zai)

**Priority:** `ANTHROPIC_API_KEY` (highest, skips OAuth) -> OAuth tokens
(`CLAUDE_CODE_OAUTH_TOKEN` + `CLAUDE_OAUTH_REFRESH_TOKEN`).

**OAuth refresh:** Automatic with 5-minute buffer before expiry. Cached in-memory for
the worker process lifetime. Refresh endpoint:
```
POST https://console.anthropic.com/v1/oauth/token
{ "grant_type": "refresh_token", "refresh_token": "<token>",
  "client_id": "9d1c250a-e61b-44d9-88ed-5944d1962f5e" }
```

**Credentials file search order:**
1. `~/.claude/.credentials.json`
2. `~/.claude/credentials.json` (legacy)
3. `$XDG_CONFIG_HOME/claude/.credentials.json`
4. `$XDG_CONFIG_HOME/claude/credentials.json` (legacy)
5. `$CLAUDE_CONFIG_DIR/.credentials.json` (cc-mirror)

**File format:** `{ "claudeAiOauth": { "accessToken": "...", "refreshToken": "...", "expiresAt": <ms> } }`

The Docker entrypoint writes credentials to `~/.claude/.credentials.json` and the
cc-mirror config dir at container startup.

### Zai Harness

Requires `Z_AI_API_KEY`. The worker maps this to `ANTHROPIC_API_KEY` at spawn time.
The Docker image strips `ANTHROPIC_API_KEY` from zai's settings.json so the runtime
value takes precedence.

`ANTHROPIC_BASE_URL` precedence for zai adapter:
1. `ANTHROPIC_BASE_URL`
2. `Z_AI_BASE_URL` (fallback)

### Gemini Harness

Uses `GEMINI_API_KEY` or `GOOGLE_API_KEY`. No special credential setup.

### Code / Codex Harnesses

Docker entrypoint writes OpenAI OAuth to `~/.code/auth.json` and `~/.codex/auth.json`.
Format: `{ "tokens": { "access_token": "...", "refresh_token": "...", "id_token": "...", "account_id": "..." } }`

Eve automatically writes back refreshed Code/Codex tokens after each invocation. If the
`auth.json` changed during the session, the new value is patched to the originating secret
scope (user/org/project). Write-back failures are non-fatal (logged as warning).

To initially register tokens, re-auth with `codex auth` / `code auth`, then run `eve auth sync`.

---

## Token Lifecycle Management

### Claude OAuth Tokens

Claude OAuth tokens (`sk-ant-oat01-*`) are short-lived (~15h) and cannot be refreshed by the
worker -- the Claude harness handles refresh internally during a session. For jobs that may
exceed the token's remaining lifetime, prefer `ANTHROPIC_API_KEY` (a long-lived setup-token).

Token types detected by `eve auth creds` and `eve auth sync`:

| Token prefix | Type | Lifetime |
|---|---|---|
| `sk-ant-oat01-` | `setup-token` | Long-lived (preferred) |
| Other `sk-ant-*` | `oauth` | ~15h (short-lived) |

`eve auth sync` warns when syncing a short-lived OAuth token (any Claude token not starting
with `sk-ant-oat01-`), recommending a setup-token for long-running jobs.

### Codex/Code OAuth Tokens

Codex and Code CLI store OAuth tokens in `auth.json` under `~/.codex/` or `~/.code/`. The
CLI may refresh these tokens automatically during a session.

**Write-back flow:**

1. Before invocation: worker captures the base64-encoded `auth.json` and its originating secret scope.
2. After invocation: worker reads `auth.json` from disk (picks freshest across `~/.code` and `~/.codex`).
3. If the base64 differs (token was refreshed), the new value is written back to the originating secret via `PATCH /internal/secrets/:scope_type/:scope_id/CODEX_AUTH_JSON_B64`.
4. Write-back failures are non-fatal (logged as `warn`).

This keeps tokens fresh across jobs without manual re-sync.

---

## Harness Config Root

Per-harness configuration lives in a single root with subfolders:

```
.agents/harnesses/
  <harness>/
    config.toml|json|yaml
    variants/
      <variant>/
        config.toml|json|yaml
```

Resolution: `EVE_HARNESS_CONFIG_ROOT` (if set) -> `<repo>/.agents/harnesses/<harness>`.
If a `variants/<variant>` directory exists, it overlays the base config.

---

## Adding a New BYOK Model

1. **Rate card** — `packages/shared/src/pricing/default-rate-card.ts`:
   add entry under `llm.byok.<provider>.<model-id>`, update effective date.
2. **Model examples** — `packages/shared/src/harnesses/capabilities.ts`:
   update `model_examples` for the relevant harness (recommended default first).
3. **Env example** — `.env.example`: update the suggested model if it's the new default.
4. **Model normalization** — `packages/shared/src/pricing/model-normalization.ts`:
   add rules if provider uses non-standard suffixes.

---

## Per-Harness CLI Arguments

### mclaude / claude

```
mclaude --print --verbose --output-format stream-json \
  --model sonnet --permission-mode default "<prompt>"
```

- Config dir: `<config root>/mclaude` or `$CLAUDE_CONFIG_DIR`
- Model: `$CLAUDE_MODEL` or `sonnet` (default fallback changed from `opus` to `sonnet`)
- Skills: mclaude installs from `skills.txt` into `.agents/skills/` at runtime

### zai

```
zai --print --verbose --output-format stream-json \
  --model <model> --permission-mode default "<prompt>"
```

- Config dir: `<config root>/zai` or `$CLAUDE_CONFIG_DIR`
- Model: `$ZAI_MODEL` or `$CLAUDE_MODEL`

### gemini

```
gemini --output-format stream-json \
  --model <model> --approval-mode default "<prompt>"
```

Uses `--approval-mode` instead of `--permission-mode`.

### code / coder / codex

```
code --ask-for-approval on-request --model <model> \
  --profile <variant> exec --json --skip-git-repo-check "<prompt>"
```

- Config dir: `<config root>/code` (or `/codex`) or `$CODEX_HOME`
- Auth: `auth.json` in config dir (from `CODEX_AUTH_JSON_B64` or `CODEX_OAUTH_*` vars)

---

## Permission Policies

| Policy      | mclaude/claude/zai                    | gemini                     | code/codex                      |
|-------------|---------------------------------------|----------------------------|---------------------------------|
| `default`   | `--permission-mode default`           | `--approval-mode default`  | `--ask-for-approval on-request` |
| `auto_edit` | `--permission-mode acceptEdits`       | `--approval-mode auto_edit`| `--ask-for-approval on-failure` |
| `never`     | `--permission-mode dontAsk`           | (fallback to default)      | `--ask-for-approval never`      |
| `yolo`      | `--dangerously-skip-permissions`      | `--yolo`                   | `--ask-for-approval never`      |

Sandbox flags applied automatically by `eve-agent-cli`:
- Claude/mclaude/zai: `--add-dir <workspace>`
- Code/Codex: `--sandbox workspace-write -C <workspace>`
- Gemini: `--sandbox`

---

## Reasoning Effort

Jobs pass `harness_options.reasoning_effort` (`low`, `medium`, `high`, `x-high`).

| Harness family     | Mechanism         | Notes                                  |
|--------------------|-------------------|----------------------------------------|
| mclaude/claude/zai | thinking tokens   | Maps effort level to token budget      |
| code/codex         | `--reasoning`     | Passes effort level as CLI flag        |
| gemini             | passthrough       | Effort level passed directly           |

---

## Project Harness Profiles

Define named profiles in the manifest under `x-eve.agents`:

```yaml
x-eve:
  agents:
    version: 1
    availability:
      drop_unavailable: true       # drop entries for unavailable harnesses
    profiles:
      primary-coder:
        - harness: codex
          model: gpt-5.2-codex
          reasoning_effort: high
      primary-reviewer:
        - harness: mclaude
          model: opus-4.5
          reasoning_effort: high
        - harness: codex
          model: gpt-5.2-codex
          reasoning_effort: x-high
      planning-council:
        - profile: primary-planner  # reference another profile
```

Reference profiles in jobs via `harness_profile` to avoid hardcoding harness choices.
Skills should always reference profiles, not specific harnesses.

### Profile Resolution for Chat-Routed Jobs

Harness profiles resolve correctly for chat-routed jobs. The ChatService resolves
`harness_profile` names to concrete harness + harness_options using the project's
`x_eve_yaml` (from agent config, synced via `eve agents sync`). This applies to all
chat job creation paths: direct agent routing, team lead/coordinator jobs, team relay
and fanout member jobs, and direct slug routing.

### Profile Resolution Source

Profiles are read from `agent_config.x_eve_yaml` (set during agents sync), not from
`manifest.manifest_yaml`. The manifest contains `x-eve.packs` but not profiles. For
backwards compatibility, resolution falls back to the manifest if agent config is absent.

---

## Harness Auth Status (Introspection)

**API:**
- `GET /harnesses` -- list all harnesses with auth status
- `GET /harnesses/{name}` -- single harness details

**Response shape:**
```json
{ "name": "mclaude", "aliases": [], "description": "...",
  "variants": [{ "name": "default", "description": "...", "source": "config" }],
  "auth": { "available": true, "reason": "...", "instructions": [] },
  "capabilities": {
    "supports_model": true, "model_examples": ["opus-4.5"],
    "reasoning": { "supported": true, "levels": ["low","medium","high","x-high"],
                   "mode": "thinking_tokens" }
  }
}
```

**CLI:**
- `eve harness list` -- auth availability
- `eve harness list --capabilities` -- auth + model + reasoning support
- `eve agents config --json` -- project policy + profile resolution

---

## eve-agent-cli Arguments

```
eve-agent-cli \
  --harness <harness>           # mclaude, claude, zai, gemini, code, codex
  --permission <policy>         # default, auto_edit, never, yolo
  --output-format stream-json
  --workspace <workspacePath>
  --prompt "<text>"
  [--variant <variant>]         # optional harness variant
  [--model <model>]             # optional model override
```

---

## Execution Logging

All harness output is logged to the `execution_logs` table:

| Type           | Description                                           |
|----------------|-------------------------------------------------------|
| `event`        | Normalized harness event (assistant, tool_use, tool_result, etc.) |
| `system`       | System events (init, completed)                       |
| `system_error` | Stderr output                                         |
| `parse_error`  | Failed to parse JSON line from harness                |
| `spawn_error`  | Failed to spawn harness process                       |

---

## Environment Variables Reference

### Auth Variables

| Variable                       | Description                                    |
|--------------------------------|------------------------------------------------|
| `ANTHROPIC_API_KEY`            | API key for Claude harnesses (overrides OAuth) |
| `CLAUDE_CODE_OAUTH_TOKEN`      | OAuth access token for Claude harnesses        |
| `CLAUDE_OAUTH_REFRESH_TOKEN`   | OAuth refresh token                            |
| `CLAUDE_OAUTH_EXPIRES_AT`      | Token expiry (ms since epoch)                  |
| `Z_AI_API_KEY`                 | API key for zai harness                        |
| `GEMINI_API_KEY` / `GOOGLE_API_KEY` | API key for Gemini                        |
| `CODEX_AUTH_JSON_B64`          | Base64-encoded auth.json for Code/Codex        |
| `CODEX_OAUTH_ACCESS_TOKEN`     | OAuth access token for Code/Codex              |
| `CODEX_OAUTH_REFRESH_TOKEN`    | OAuth refresh token for Code/Codex             |
| `CODEX_OAUTH_ID_TOKEN`         | OAuth ID token for Code/Codex                  |
| `CODEX_OAUTH_ACCOUNT_ID`       | Account ID for Code/Codex                      |

### Config + Worker Variables

| Variable                       | Description                                    |
|--------------------------------|------------------------------------------------|
| `EVE_HARNESS_CONFIG_ROOT`      | Override repo `.agent/harnesses` root          |
| `CLAUDE_CONFIG_DIR`            | Config directory for Claude-based harnesses    |
| `CLAUDE_MODEL`                 | Default model for Claude harnesses             |
| `ZAI_MODEL`                    | Model override for zai                         |
| `CODEX_HOME`                   | Config directory for Code/Codex                |
| `CLAUDE_CODE_TEAM_NAME`        | Set to attemptId for tracking                  |
| `WORKSPACE_ROOT` / `EVE_WORKSPACE_ROOT` | Root directory for workspaces        |
| `EVE_CACHE_ROOT`               | Shared cache directory                         |
| `EVE_AGENT_CLI_PATH`           | Override path to eve-agent-cli binary          |
| `EVE_TOOLCHAIN_PATHS`          | Colon-separated paths to mounted toolchain bins |
| `EVE_TOOLCHAIN_IMAGE_PREFIX`   | Image prefix for toolchain init containers     |
| `EVE_TOOLCHAIN_IMAGE_TAG`      | Image tag for toolchain init containers        |
