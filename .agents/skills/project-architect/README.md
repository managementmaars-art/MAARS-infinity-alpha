# Project Architect

An [Agent Skill](https://agentskills.io) for **documentation-first project planning**. Transforms a project idea into implementation-ready blueprints and a single-shot coding agent prompt.

Compatible with **40+ coding agents** including Claude Code, Cursor, Gemini CLI, GitHub Copilot, Codex, Roo Code, and more.

## What It Does

Given a project idea, Project Architect walks you through an interactive discovery process and generates 5 interconnected documents:

```
[Discovery] -> SPECIFICATION.md -> IMPLEMENTATION.md -> TASKS.md -> BRANDING.md
                 (The What)          (The How)          (The Work)   (Identity)
                      |                   |                  |
                      +-------------------+------------------+
                                          |
                                     PROMPT.md
                               (Single-Shot Agent Prompt)
```

| Document | Purpose |
|----------|---------|
| **SPECIFICATION.md** | What the project is, features, data model, API surface |
| **IMPLEMENTATION.md** | Tech stack, design patterns, directory structure, schemas |
| **TASKS.md** | Ordered work items, each completable in a single agent session |
| **BRANDING.md** | Name, colors, typography, voice (optional, for user-facing projects) |
| **PROMPT.md** | Self-contained prompt to build the entire project from scratch |

## Features

- **Interactive tech stack advisor** -- presents options with trade-offs, lets you choose
- **Design pattern recommendations** -- matched to your project's specific needs with code sketches
- **Scales to project size** -- weekend hack gets 15 tasks, enterprise system gets 100+
- **Agent-optimized output** -- every task lists exact files to create/modify with acceptance criteria
- **Pause-and-review flow** -- generates each document, waits for approval before continuing

## Installation

### Universal (any agent) via skills CLI

The easiest way to install, works with all [agentskills.io-compatible agents](https://agentskills.io):

```bash
npx skills add ersinkoc/project-architect
```

This auto-detects your coding agent and installs to the correct location.

**Install for a specific agent:**

```bash
npx skills add ersinkoc/project-architect --agent claude-code
npx skills add ersinkoc/project-architect --agent cursor
npx skills add ersinkoc/project-architect --agent codex
```

**Install globally (all projects):**

```bash
npx skills add ersinkoc/project-architect --global
```

> Repository: [github.com/ersinkoc/project-architect](https://github.com/ersinkoc/project-architect)

### Claude Code (plugin mode)

Add to your project's `.claude/settings.json`:

```json
{
  "plugins": [
    "/absolute/path/to/project-architect"
  ]
}
```

Or add to `~/.claude/settings.json` for global availability.

### Manual installation (any agent)

Clone the repo and copy/symlink the skill directory into your agent's skills folder:

| Agent | Skills Directory |
|-------|-----------------|
| Claude Code | `.claude/skills/` or `~/.claude/skills/` |
| Cursor | `.cursor/skills/` or `~/.cursor/skills/` |
| GitHub Copilot | `.github/skills/` |
| Codex | `.codex/skills/` |
| Gemini CLI | `.gemini/skills/` |
| OpenCode | `.opencode/skills/` |
| Generic | `.agents/skills/` or `~/.agents/skills/` |

```bash
# Example: install for Claude Code globally
git clone https://github.com/ersinkoc/project-architect.git
ln -s $(pwd)/project-architect ~/.claude/skills/project-architect

# Example: install for Cursor in a project
ln -s $(pwd)/project-architect .cursor/skills/project-architect
```

## Usage

Start a conversation with your coding agent and describe what you want to build:

```
> plan my project: a CLI tool for managing dotfiles across machines
```

Or use any of these trigger phrases:

- "plan my project"
- "spec this out"
- "architect a system for..."
- "help me plan"
- "what stack should I use"
- "generate a prompt"
- "break this into tasks"
- "I want to build X"

## Workflow

1. **Discovery** -- Agent asks structured questions about your project (type, scope, stack, features)
2. **SPECIFICATION.md** -- Generated and presented for review
3. **IMPLEMENTATION.md** -- Tech decisions, patterns, directory structure
4. **TASKS.md** -- Ordered work breakdown with file lists and acceptance criteria
5. **BRANDING.md** -- Optional identity guide (colors, typography, voice)
6. **PROMPT.md** -- Everything synthesized into a single executable prompt

You review and approve each document before the next is generated.

## Partial Workflows

You don't have to run the full pipeline:

| What You Say | What Happens |
|-------------|-------------|
| "Just the spec" | Generates SPECIFICATION.md only |
| "Skip to tasks" | Lightweight spec + impl, then detailed tasks |
| "Just give me a prompt" | Condensed discovery, straight to PROMPT.md |
| "Help me choose a stack" | Interactive tech stack selection only |
| "What patterns should I use?" | Design pattern consultation |

## Reference Files

The skill includes detailed guides that inform each generation phase:

| File | Purpose |
|------|---------|
| `references/elicitation-guide.md` | Question framework for project discovery |
| `references/tech-stacks.md` | Interactive tech stack selection with trade-offs |
| `references/design-patterns.md` | Pattern catalog with selection guide |
| `references/specification-guide.md` | Template and rules for SPECIFICATION.md |
| `references/implementation-guide.md` | Template and rules for IMPLEMENTATION.md |
| `references/tasks-guide.md` | Template and rules for TASKS.md |
| `references/branding-guide.md` | Template and rules for BRANDING.md |
| `references/claude-code-prompt.md` | Template and rules for PROMPT.md |

## Project Structure

```
project-architect/
├── SKILL.md                             # Skill definition (agentskills.io format)
├── plugin.json                          # Claude Code plugin manifest
├── LICENSE                              # MIT License
├── README.md                            # This file
└── references/
    ├── elicitation-guide.md             # Discovery question framework
    ├── tech-stacks.md                   # Tech stack advisor
    ├── design-patterns.md               # Pattern catalog
    ├── specification-guide.md           # Spec template
    ├── implementation-guide.md          # Implementation template
    ├── tasks-guide.md                   # Tasks template
    ├── branding-guide.md                # Branding template
    └── claude-code-prompt.md            # Prompt template
```

## Compatibility

This skill follows the [Agent Skills specification](https://agentskills.io/specification) and is compatible with:

- **Claude Code** (plugin + skill)
- **Cursor**
- **GitHub Copilot**
- **OpenAI Codex**
- **Gemini CLI**
- **Roo Code**
- **OpenCode**
- **Kiro**
- **And 30+ more agents** via [agentskills.io](https://agentskills.io)

## License

MIT
