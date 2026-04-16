---
name: ai-tools
description: Manage AI CLI tools (Claude Code, Gemini CLI, Codex CLI). Use when user asks about AI tool versions, updates, installation, or wants to update/install their AI CLI tools. Detects installed tools using two-tier detection (PATH + npm fallback), installs missing tools, checks versions, and retrieves update instructions from authoritative sources using delegation-first pattern.
allowed-tools: Bash, Skill, Task, Read, mcp__perplexity__search, WebSearch
---

# AI Tools Management

Extensible AI CLI tools management with **delegation-first** design. Detects installed tools, installs missing tools, reports versions, and retrieves update instructions from authoritative sources.

## Design Principles

1. **No hardcoded documentation** - Never duplicate docs that exist elsewhere
2. **Delegation-first** - Route to ecosystem skills/agents for authoritative guidance
3. **Graceful fallback** - Skill -> MCP research -> web search
4. **Extensible** - Easy to add new tools via tool-registry.md
5. **Two-tier detection** - PATH check first, npm global fallback second
6. **Install capability** - Offer to install missing tools via delegation

## Workflow

### Step 1: Detect Installed Tools (Two-Tier)

Check which AI CLI tools are installed using two-tier detection:

**Tier 1 - PATH check:**

```bash
# Claude Code
command -v claude &>/dev/null && claude --version 2>/dev/null || echo "NOT_IN_PATH"

# Gemini CLI
command -v gemini &>/dev/null && gemini --version 2>/dev/null || echo "NOT_IN_PATH"

# Codex CLI
command -v codex &>/dev/null && codex --version 2>/dev/null || echo "NOT_IN_PATH"
```

**Tier 2 - npm global fallback** (for tools not found in PATH):

```bash
# Check npm global packages for tools not in PATH
npm list -g @anthropic-ai/claude-code --depth=0 2>/dev/null
npm list -g @google/gemini-cli --depth=0 2>/dev/null
npm list -g @openai/codex --depth=0 2>/dev/null
```

Report which tools are installed with their current versions. Classify each as:

- **Installed** (found in PATH) - version detected
- **Installed (npm only)** - found via npm but not in PATH (may need PATH fix)
- **Not installed** - not found by either method

### Step 2: Install Missing Tools (Delegation Pattern)

For each tool that is **not installed**, offer to install it using the delegation chain from the tool registry's **Install Delegation Chain**.

**Default behavior:** Offer to install missing tools (prompt user for confirmation).

- `--install` mode: Install missing tools without prompting
- `--no-install` mode: Skip installation, only report and update existing tools

#### Claude Code

**Primary**: Invoke `claude-ecosystem:docs-management` skill with query "Claude Code install setup"

**Fallback 1**: Spawn `claude-code-guide` agent to find install docs

**Fallback 2**: `mcp__perplexity__search("Claude Code CLI install npm")`

**Fallback 3**: `WebSearch("Claude Code CLI install")`

#### Gemini CLI

**Primary**: Invoke `google-ecosystem:gemini-cli-docs` skill with query "install setup npm"

**Fallback 1**: `mcp__perplexity__search("Google Gemini CLI npm install setup")`

**Fallback 2**: `WebSearch("Google Gemini CLI npm install")`

#### Codex CLI

**Primary**: Invoke `openai-ecosystem:codex-cli-docs` skill with query "install setup npm"

**Fallback 1**: `mcp__perplexity__search("OpenAI Codex CLI npm install setup")`

**Fallback 2**: `WebSearch("OpenAI Codex CLI npm install")`

After installation, re-run detection to confirm and report installed versions.

### Step 3: Get Update Instructions (Delegation Pattern)

For each installed tool that needs updating, retrieve instructions from authoritative sources using the delegation chain from the tool registry's **Delegation Chain**.

#### Claude Code

**Primary**: Invoke `claude-ecosystem:docs-management` skill with query "Claude Code update install upgrade"

**Fallback 1**: If skill unavailable, spawn `claude-code-guide` agent:

```text
First WebFetch https://code.claude.com/docs/en/claude_code_docs_map.md to find
update/install documentation. Then WebFetch those pages. Return the update commands.
```

**Fallback 2**: If agent unavailable, use MCP:

```text
mcp__perplexity__search("Claude Code CLI update install latest version 2026")
```

**Fallback 3**: WebSearch for "Claude Code CLI update install"

#### Gemini CLI

**Primary**: Invoke `google-ecosystem:gemini-cli-docs` skill with query "update install upgrade npm"

**Fallback 1**: If skill unavailable, use MCP:

```text
mcp__perplexity__search("Google Gemini CLI npm update install latest version 2026")
```

**Fallback 2**: WebSearch for "Google Gemini CLI npm install update"

#### Codex CLI

**Primary**: Invoke `openai-ecosystem:codex-cli-docs` skill with query "update install upgrade npm"

**Fallback 1**: If skill unavailable, use MCP:

```text
mcp__perplexity__search("OpenAI Codex CLI npm update install latest version 2026")
```

**Fallback 2**: WebSearch for "OpenAI Codex CLI npm install update"

### Step 4: Execute Updates

After retrieving authoritative update instructions:

1. Present the update commands to user
2. If `--dry-run` mode, stop here (show what would happen)
3. Otherwise, execute the update commands
4. Report new versions after updates complete

### Step 5: Report Results

Provide a summary table:

| Tool | Before | After | Status |
|------|--------|-------|--------|
| Claude Code | vX.X.X | vY.Y.Y | Updated |
| Gemini CLI | Not installed | vX.X.X | Installed |
| Codex CLI | vX.X.X | vY.Y.Y | Updated |

Possible statuses: **Updated**, **Installed**, **Already latest**, **Skipped**, **Failed**, **Not installed (--no-install)**

## Tool Registry

See [references/tool-registry.md](references/tool-registry.md) for the complete tool registry with:

- Detection commands (two-tier: PATH + npm fallback)
- npm package names and install types
- Delegation sources (skills, agents, MCP queries)
- Install delegation chains
- Fallback search queries

## Adding New Tools

To add a new AI CLI tool:

1. Add entry to `references/tool-registry.md` with:
   - Detection command (how to check if installed)
   - npm package name and install type
   - Version command (how to get current version)
   - Docs source (which skill/agent has authoritative docs)
   - Search query (fallback for MCP/web search)
   - Install delegation chain

2. No code changes needed - the workflow automatically handles tools in the registry

## Supported Modes

- **Default**: Update all installed tools, offer to install missing tools
- **`--tool NAME`**: Update/install specific tool only
- **`--dry-run`**: Show what would happen without executing
- **`--check`**: Only check versions, don't update or install
- **`--install`**: Install missing tools without prompting
- **`--no-install`**: Skip installation of missing tools, only update existing

## Error Handling

- **Tool not installed (default)**: Offer to install via delegation chain
- **Tool not installed (--no-install)**: Skip gracefully, report in summary
- **npm not in PATH**: Detected via npm fallback, suggest PATH fix
- **Skill unavailable**: Fall back to MCP search
- **MCP unavailable**: Fall back to web search
- **Update fails**: Report error, continue with other tools
- **Install fails**: Report error with delegation source that failed, continue with other tools
- **No authoritative source found**: Report inability to update/install, suggest manual check

## Why Delegation?

Update and install commands change over time:

- Package managers evolve (npm -> pnpm, pip -> uv)
- Installation methods change (npm global -> npx)
- Flags and options get added/deprecated

By delegating to ecosystem skills that maintain current documentation, this skill stays accurate without manual updates.

## Test Scenarios

### Scenario 1: Check installed tools

**Given:** User asks "what AI tools do I have installed?"
**Then:** Detect all tools using two-tier detection and report versions

### Scenario 2: Update all tools

**Given:** User asks "update my AI tools"
**Then:** Detect installed tools, retrieve update instructions via delegation, execute updates

### Scenario 3: Update specific tool

**Given:** User asks "update claude code"
**Then:** Retrieve Claude Code update instructions via delegation, execute update

### Scenario 4: Dry run mode

**Given:** User asks "show me how to update my AI tools without running anything"
**Then:** Detect installed tools, retrieve update instructions, display without executing

### Scenario 5: Check only mode

**Given:** User asks "what versions of AI tools do I have?"
**Then:** Detect installed tools and report versions without attempting updates or installs

### Scenario 6: Install missing tools (default)

**Given:** User runs update and some tools are not installed
**Then:** Offer to install missing tools via delegation, install on confirmation, report results

### Scenario 7: Install with --install flag

**Given:** User runs with `--install` flag
**Then:** Install all missing tools without prompting, then update existing tools

### Scenario 8: npm fallback detection

**Given:** Tool is installed via npm but not in PATH
**Then:** Two-tier detection finds it via `npm list -g`, reports as "Installed (npm only)", suggests PATH fix

### Scenario 9: Skip install with --no-install

**Given:** User runs with `--no-install` flag and some tools are not installed
**Then:** Skip missing tools, only update tools that are already installed

## Version History

| Version | Date | Changes |
| --- | --- | --- |
| 1.1.0 | 2026-02-15 | Two-tier detection (PATH + npm fallback), install workflow with --install/--no-install modes, Install Delegation Chain in registry |
| 1.0.0 | 2026-01-17 | Initial release - delegation-first design, support for Claude Code, Gemini CLI, Codex CLI |

---

**Model:** Claude Opus 4.6 (claude-opus-4-6)
**Last Updated:** 2026-02-15
