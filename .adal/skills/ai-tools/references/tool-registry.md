# AI Tools Registry

Detection metadata for AI CLI tools. Contains ONLY detection commands and delegation sources - never hardcoded update or install instructions.

## Registry Format

Each tool entry contains:

- **id**: Unique identifier for the tool
- **name**: Display name
- **npm-package**: npm package name for global install
- **install-type**: Installation method (npm-global, binary, etc.)
- **detection**: Commands to check if installed (cross-platform)
- **version**: Command to get current version
- **docs-source**: Primary skill/agent for authoritative documentation
- **docs-fallback**: Fallback agent if primary unavailable
- **search-query**: Query for MCP/web search fallback

---

## Claude Code

| Field | Value |
|-------|-------|
| **id** | `claude-code` |
| **name** | Claude Code |
| **npm-package** | `@anthropic-ai/claude-code` |
| **install-type** | `npm-global` |
| **detection** | `which claude` (Unix) / `where claude` (Windows) |
| **version** | `claude --version` |
| **docs-source** | `claude-ecosystem:docs-management` skill |
| **docs-fallback** | `claude-code-guide` agent |
| **search-query** | "Claude Code CLI update install latest version" |

### Detection Script

```bash
# Two-tier detection: PATH check + npm fallback
if command -v claude &>/dev/null; then
  CLAUDE_INSTALLED=true
  CLAUDE_VERSION=$(claude --version 2>/dev/null | head -1)
elif npm list -g @anthropic-ai/claude-code --depth=0 2>/dev/null | grep -q '@anthropic-ai/claude-code'; then
  CLAUDE_INSTALLED=true
  CLAUDE_VERSION=$(npm list -g @anthropic-ai/claude-code --depth=0 2>/dev/null | grep '@anthropic-ai/claude-code' | sed 's/.*@//')
else
  CLAUDE_INSTALLED=false
fi
```

### Delegation Chain

1. `Skill("claude-ecosystem:docs-management")` - query "Claude Code update install upgrade"
2. `Task(claude-code-guide)` - WebFetch docs_map.md, find update docs
3. `mcp__perplexity__search("Claude Code CLI update install")`
4. `WebSearch("Claude Code CLI update install")`

### Install Delegation Chain

1. `Skill("claude-ecosystem:docs-management")` - query "Claude Code install setup"
2. `Task(claude-code-guide)` - WebFetch docs_map.md, find install docs
3. `mcp__perplexity__search("Claude Code CLI install npm")`
4. `WebSearch("Claude Code CLI install")`

---

## Gemini CLI

| Field | Value |
|-------|-------|
| **id** | `gemini-cli` |
| **name** | Google Gemini CLI |
| **npm-package** | `@google/gemini-cli` |
| **install-type** | `npm-global` |
| **detection** | `which gemini` (Unix) / `where gemini` (Windows) |
| **version** | `gemini --version` |
| **docs-source** | `google-ecosystem:gemini-cli-docs` skill |
| **docs-fallback** | None (use MCP directly) |
| **search-query** | "Google Gemini CLI npm update install latest version" |

### Detection Script

```bash
# Two-tier detection: PATH check + npm fallback
if command -v gemini &>/dev/null; then
  GEMINI_INSTALLED=true
  GEMINI_VERSION=$(gemini --version 2>/dev/null | head -1)
elif npm list -g @google/gemini-cli --depth=0 2>/dev/null | grep -q '@google/gemini-cli'; then
  GEMINI_INSTALLED=true
  GEMINI_VERSION=$(npm list -g @google/gemini-cli --depth=0 2>/dev/null | grep '@google/gemini-cli' | sed 's/.*@//')
else
  GEMINI_INSTALLED=false
fi
```

### Delegation Chain

1. `Skill("google-ecosystem:gemini-cli-docs")` - query "update install upgrade npm"
2. `mcp__perplexity__search("Google Gemini CLI npm update install")`
3. `WebSearch("Google Gemini CLI npm install update")`

### Install Delegation Chain

1. `Skill("google-ecosystem:gemini-cli-docs")` - query "install setup npm"
2. `mcp__perplexity__search("Google Gemini CLI npm install setup")`
3. `WebSearch("Google Gemini CLI npm install")`

---

## Codex CLI

| Field | Value |
|-------|-------|
| **id** | `codex-cli` |
| **name** | OpenAI Codex CLI |
| **npm-package** | `@openai/codex` |
| **install-type** | `npm-global` |
| **detection** | `which codex` (Unix) / `where codex` (Windows) |
| **version** | `codex --version` |
| **docs-source** | `openai-ecosystem:codex-cli-docs` skill |
| **docs-fallback** | None (use MCP directly) |
| **search-query** | "OpenAI Codex CLI npm update install latest version" |

### Detection Script

```bash
# Two-tier detection: PATH check + npm fallback
if command -v codex &>/dev/null; then
  CODEX_INSTALLED=true
  CODEX_VERSION=$(codex --version 2>/dev/null | head -1)
elif npm list -g @openai/codex --depth=0 2>/dev/null | grep -q '@openai/codex'; then
  CODEX_INSTALLED=true
  CODEX_VERSION=$(npm list -g @openai/codex --depth=0 2>/dev/null | grep '@openai/codex' | sed 's/.*@//')
else
  CODEX_INSTALLED=false
fi
```

### Delegation Chain

1. `Skill("openai-ecosystem:codex-cli-docs")` - query "update install upgrade npm"
2. `mcp__perplexity__search("OpenAI Codex CLI npm update install")`
3. `WebSearch("OpenAI Codex CLI npm install update")`

### Install Delegation Chain

1. `Skill("openai-ecosystem:codex-cli-docs")` - query "install setup npm"
2. `mcp__perplexity__search("OpenAI Codex CLI npm install setup")`
3. `WebSearch("OpenAI Codex CLI npm install")`

---

## Adding New Tools

To add a new AI CLI tool, create an entry following this template:

```markdown
## Tool Name

| Field | Value |
|-------|-------|
| **id** | `tool-id` |
| **name** | Display Name |
| **npm-package** | `@scope/package-name` |
| **install-type** | `npm-global` |
| **detection** | `which tool` (Unix) / `where tool` (Windows) |
| **version** | `tool --version` |
| **docs-source** | `plugin:skill-name` skill |
| **docs-fallback** | `agent-name` agent (or None) |
| **search-query** | "Tool Name update install latest version" |

### Detection Script
[bash script with two-tier detection: PATH check + npm fallback]

### Delegation Chain
[ordered list of delegation sources for updates]

### Install Delegation Chain
[ordered list of delegation sources for fresh installation]
```

## Future Tools (Placeholders)

These tools may be added when ecosystem plugins are created:

- **Aider** - AI pair programming CLI
- **Continue** - Open-source AI code assistant
- **Cody** - Sourcegraph's AI coding assistant
- **Tabby** - Self-hosted AI coding assistant

---

**Last Updated:** 2026-02-15
