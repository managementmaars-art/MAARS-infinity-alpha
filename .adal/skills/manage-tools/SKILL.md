---
name: manage-tools
description: >
  Manage the `## External Tools` section in AGENTS.md — the curated list
  of agent skills, MCP servers, and CLIs the project depends on. Auto-
  detects installed tools from config files, presents a checklist to
  the user, and writes a minimal structured section with three fixed
  sub-categories (Agent Skills / MCP Servers / CLIs). Re-runnable for
  drift detection when the project's toolchain evolves.
  "manage tools", "external tools", "add MCP", "add CLI", "register skill",
  "add tool to AGENTS", "list project tools", "update external tools",
  "project toolchain",
  Slash trigger: "/manage-tools".
  Auto trigger: when the user installs a new MCP server (`.mcp.json`
  changes), adds a project-specific CLI to `package.json`/`Brewfile`/
  `mise.toml`, or mentions a shared tool in conversation.
metadata:
  author: dev-goraebap
  version: "0.1.1"
---
<!-- AUTO-GENERATED - DO NOT EDIT DIRECTLY. Edit src/ instead. -->

# manage-tools

Manage the `## External Tools` section in AGENTS.md. This section lists the tools the agent should know about: agent skills that are invoked frequently, MCP servers connected to the project, and CLI tools the project depends on for non-obvious workflows.

**Philosophy.** Tools that are on-demand or obvious do not belong here. The agent already discovers most tools at runtime. This section is for tools that are **shared team conventions** — "when you need issue tracking, use `gh`", "when you need the database, use the `postgres-readonly` MCP" — that a new agent would otherwise miss.

## Scope

**In scope:**
- Add/remove/refresh entries in `## External Tools`
- Auto-detect candidate tools from `.mcp.json`, `package.json`, `Brewfile`, `mise.toml`, `.tool-versions`, and `~/.claude/agents/`
- Present candidates as a checklist (user opts in per item)
- Enforce the 3-category structure: `### Agent Skills`, `### MCP Servers`, `### CLIs`
- Drift detection on re-run: compare current section to detected tools and propose add/remove operations

**Out of scope:**
- Installing or configuring the tools themselves (this skill only documents them)
- Listing every installed dependency (only **shared team conventions** that the agent must know)
- Creating a "Platforms" category (platforms like GitHub/Linear/Notion are referenced through their CLI/MCP/skill, not as a separate category)
- Listing on-demand agent skills (those are auto-invoked — writing them here is redundant)

## Guardrails

| # | Check | On failure |
|---|-------|------------|
| 1 | CWD is a Git repository | "Please run this inside a Git repository." |
| 2 | AGENTS.md exists | "AGENTS.md not found. Run /init-public-rules first." |
| - | Skill update check | **Session dedup**: if you have already fetched `manifest.json` for any agent-collabo skill earlier in this conversation, skip this check entirely and proceed. Otherwise: Let `SELF` be the value of the `name` field in this SKILL.md's frontmatter (e.g., `init-public-rules`). Let `LOCAL` be `metadata.version` from this same frontmatter. Fetch `https://raw.githubusercontent.com/dev-goraebap/agent-collabo/main/manifest.json` (1 HTTP request, fail silently on network error). Then evaluate exactly one case in this order: **Case A — outdated**: if `manifest.skills[SELF]` exists and `LOCAL < manifest.skills[SELF]`, tell the user (in their language) "agent-collabo `{SELF}` has a new version ({LOCAL} → {manifest.skills[SELF]}). Run `/agent-collabo-updater` when convenient. Continuing with the current task." then proceed. **Case B — up to date**: if `manifest.skills[SELF]` exists and `LOCAL === manifest.skills[SELF]`, proceed silently. **Case C — renamed away**: if `SELF` does NOT exist as a key in `manifest.skills` AND `SELF` exists as a key in `manifest.deprecated` (note: check the keys of `deprecated`, not the `renamedTo` values), tell the user "This skill `{SELF}` was renamed to `{manifest.deprecated[SELF].renamedTo}` since v{manifest.deprecated[SELF].since}. Run `/agent-collabo-updater` to migrate." then proceed. **Case D — unknown**: if `SELF` is not in `manifest.skills` and not in `manifest.deprecated`, tell the user "Skill `{SELF}` is no longer maintained. Run `/agent-collabo-updater` to clean up." then proceed with caution. Important: `manifest.deprecated` maps OLD names → NEW names. Never warn about a skill whose name is currently in `manifest.skills` just because that name appears as a `renamedTo` value somewhere in `deprecated`. **CDN cache caveat**: GitHub raw enforces `Cache-Control: max-age=300`, so right after a new release is pushed the manifest may be stale for up to 5 minutes via Fastly PoPs. If the user explicitly mentions they just released a new version (e.g., "I just pushed v0.X.Y") and this check still reports up-to-date or shows an older `manifest.version`, do not insist the local install is current — instead mention the 5-minute CDN window and suggest retrying shortly. For all other users this is invisible because they fetch long after the cache expires. |

## Language Policy

Conduct all user-facing communication in the user's language: interview questions, follow-up prompts, status messages, diagnostic reports, and summaries. Detect the language from (in order):

1. The language of the user's most recent messages in the current session
2. Declarations in their local rules file (e.g., `CLAUDE.local.md`, `.cursor/rules/local.mdc`) — look for instructions like "respond in Korean"
3. OS locale (`$LANG`, `$LC_ALL`)
4. English as fallback

Generated file content follows the file's audience: team-shared files (`AGENTS.md`, `CHANGELOG.md`) stay in English regardless of the user's language; personal files (`CLAUDE.local.md`, `GEMINI.local.md`, etc.) use the user's language unless they specify otherwise.

## The three fixed categories

```markdown
## External Tools

### Agent Skills
- **/work-unit-ritual** — Orchestrates a full work-unit cycle
  (plan → implement → close issue). Prefer this over ad-hoc git+issue
  workflows for non-trivial tasks.
- **/manage-refs** — Keeps `## References` in sync when spec docs
  are added or moved.

### MCP Servers
- **playwright** — Browser automation for E2E verification. Use for
  any UI change that needs visual confirmation.
- **postgres-readonly** — Read-only DB queries against the dev database.
  Use for debugging data flow, never for writes.

### CLIs
- **gh** — GitHub interaction. Prefer `gh pr create` over `git push`
  when opening PRs. Prefer `gh issue` over web UI.
- **just** — Task runner. `just <target>` wraps common workflows;
  see `justfile` for targets.
```

**Rules for entries:**

1. One-line description following the em-dash is required.
2. Description must answer **"when should the agent use this?"** — not "what is this tool?".
3. Tools that exist but have no usage convention beyond "it's installed" are omitted.
4. Empty categories are not rendered (skip the `###` header).

## Category filters

### `### Agent Skills`

**Include:**
- Slash-command skills the agent should invoke proactively during specific situations (e.g., `/work-unit-ritual` before starting a task).
- Skills that override default behavior for a frequent task.

**Exclude:**
- On-demand skills that auto-trigger from natural language (the skill's own `description` field handles discovery — listing them here is redundant).
- Personal skills installed only for the current user.
- Skills that are invoked so rarely that listing them adds noise.

**Detection source:**
- `~/.claude/agents/` for user-scope skills
- `.claude/agents/` for project-scope skills
- Filter by checking if the skill's description indicates slash-command usage or proactive invocation.

### `### MCP Servers`

**Include:**
- MCP servers configured in `.mcp.json` (project scope) or `~/.claude/mcp.json` (user scope).
- Servers that provide a capability the agent should know about (browser, database, issue tracker, search).

**Exclude:**
- Servers the user uses personally but the team does not share.
- Servers the agent will naturally discover by tool listing (if you have to explain "we have a Postgres MCP", it belongs here; if the agent already calls it instinctively, the entry is optional).

**Detection source:**
- `.mcp.json` at the project root
- Fall back to asking the user if no `.mcp.json` exists

### `### CLIs`

**Include:**
- Non-obvious CLIs the agent should prefer over defaults (e.g., `gh` over raw `curl`, `just` over `npm run`, `supabase` over raw SQL).
- CLIs that require specific flags or env variables to work correctly in this project.

**Exclude:**
- Standard tools available everywhere (`git`, `ls`, `cat`, `node`, `python`) — the agent has these.
- CLIs used only once during setup.
- Package manager CLIs (`npm`, `pnpm`, `yarn`, `cargo`) unless the project specifically forbids one (then note it in Boundaries, not here).

**Detection sources (in order):**
- `package.json` bin dependencies and scripts that shell out to non-standard CLIs
- `mise.toml` / `.tool-versions` runtime version files
- `Brewfile` (macOS) or `justfile` `just` targets
- `.github/workflows/*.yml` for CI tools worth surfacing

## Workflow

### Step 1: Detect intent and mode

| Entry signal | Mode |
|---|---|
| User explicitly invoked `/manage-tools` on a project that has never run it | **First setup** → full interview |
| User explicitly invoked `/manage-tools` and `## External Tools` already exists | **Drift refresh** → compare detected vs current |
| User added `.mcp.json` entry, modified `package.json` deps, or mentioned a new tool | **Auto add** → single-tool add, skip full scan |

### Step 2: First setup — scan and classify

Run the detection sources above. Build three candidate lists.

Present the candidates as a checklist:

```
Detected tools in this project. Select which ones the agent should know about:

Agent Skills (3 detected):
  a) /work-unit-ritual
  b) /manage-refs
  c) /refine-boundaries

MCP Servers (2 detected):
  d) playwright (from .mcp.json)       [recommended]
  e) postgres-readonly (from .mcp.json) [recommended]

CLIs (5 detected):
  f) gh (GitHub CLI — from package.json scripts)  [recommended]
  g) docker compose (from compose.yml)
  h) supabase (from package.json bin)
  i) just (from justfile)
  j) mise (from mise.toml)                        [recommended]

[recommended] = clear usage evidence found in project configs.
Enter the letters of the items you want (e.g., "d, e, f, j"):
```

Default checked state: tools that have clear evidence of usage in the project (scripts, configs, justfiles). Unchecked by default: tools whose relevance is ambiguous.

### Step 3: One-line description interview (selected only)

For each **selected** item, ask for a one-line "when to use" description:

```
gh (GitHub CLI)
  When should the agent use this? (one line)
  Examples: "Prefer over `git push` for PRs", "Use for issue comments"
```

If the user leaves the description blank, skip the entry — a tool without a usage convention does not belong in this section.

### Step 4: Generate section

Write `## External Tools` with only the non-empty categories. Order inside each category: alphabetical by tool name.

If `## External Tools` does not exist, create it. Placement order in AGENTS.md:

```
# Project Overview
## Project Structure (if present)
## External Tools           ← here
## Git Workflow (if present)
## Code Style (if present)
## Testing (if present)
## Boundaries (if present)
## References (if present)
```

### Step 5: Auto add mode

When triggered by `.mcp.json` change, `package.json` update, or a user mention of a new tool:

1. Detect the **single** new tool.
2. If it already exists in `## External Tools`, exit silently.
3. Ask a single question:
   ```
   Detected new MCP server `playwright` in .mcp.json. Add it to
   AGENTS.md ## External Tools?

   1. Yes — add with a one-line description (I'll ask)
   2. No — skip this time
   ```
4. On "Yes", ask for the description and append.
5. Never re-scan the full project from auto mode.

### Step 6: Drift refresh mode

When re-invoked on a project that has an `## External Tools` section:

1. Parse the current section entries.
2. Run detection sources and build the candidate set.
3. Classify differences:
   - **Unchanged** — detected and present
   - **Orphan** — present but no longer detected (MCP removed from `.mcp.json`, CLI removed from `package.json`)
   - **New candidate** — detected but not present
4. Report:
   ```
   External Tools drift check:

   ✅ Unchanged (3):
      - /work-unit-ritual
      - playwright
      - gh

   ⚠️  Orphan (1) — present in AGENTS.md but no longer detected:
      - supabase (CLI)
      → Remove from AGENTS.md? The project may still use it even if it
        was removed from package.json.

   ➕ New candidates (2) — detected but not in AGENTS.md:
      - /manage-refs (Agent Skill)
      - postgres-readonly (MCP Server)
      → Add to AGENTS.md?
   ```
5. Ask the user to confirm each addition or removal individually.

### Step 7: Summary

```
✅ Done. ## External Tools updated.

Summary:
  - Added: /work-unit-ritual, playwright, gh
  - Kept:  /manage-refs
  - Removed: (none)

Run /audit-rules to verify the full AGENTS.md is still under budget.
```

## Interaction with other skills

- **`/init-public-rules`** does not create `## External Tools` — it's created lazily by this skill on first run.
- **`/manage-refs`** is typically listed in `### Agent Skills` if the project uses design/spec docs.
- **`/work-unit-ritual`** is listed in `### Agent Skills` when active. At runtime it reads `## External Tools` to discover which issue tracker CLI (`gh` / `glab` / `linear-cli`) to use.
- **`/audit-rules`** does not have a dedicated check for External Tools content, but T2 (section balance) may flag it if it grows too large.

## Prohibited actions

- Never create a fourth category (no "Platforms", "Services", "APIs", etc.). The 3 categories are fixed.
- Never list a tool without a one-line "when to use" description.
- Never list every installed package — only shared team conventions.
- Never auto-load or read the content of tool configurations (`.mcp.json`, `mise.toml`) beyond extracting tool names.
- Never batch-add detected tools without user confirmation.
