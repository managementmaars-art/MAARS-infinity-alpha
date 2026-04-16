---
name: sdd-init
description: >
  Initialize Spec-Driven Development context in any project. Detects stack, conventions, and bootstraps engram persistence.
  Trigger: When user wants to initialize SDD in a project, or says "sdd init", "iniciar sdd".
license: MIT
metadata:
  version: "3.0"
---

## Purpose

You are a sub-agent responsible for initializing the Spec-Driven Development (SDD) context in a project. You detect the project stack and conventions, then bootstrap engram persistence.

You are an EXECUTOR for this phase, not the orchestrator. Do the initialization work yourself. Do NOT launch sub-agents, do NOT call `delegate` or `task`, and do NOT hand execution back unless you hit a real blocker that must be reported upstream.

## Execution and Persistence Contract

- If Engram is available (default):
  **Save project context**:
  ```
  mem_save(
    title: "sdd-init/{project-name}",
    topic_key: "sdd-init/{project-name}",
    type: "architecture",
    project: "{project-name}",
    content: "{detected project context markdown}"
  )
  ```
  `topic_key` enables upserts — re-running init updates the existing context, not duplicates.

  (See `skills/_shared/engram-convention.md` for full naming conventions.)
- If Engram is not available (`none` mode): Return detected context without writing project files.

## What to Do

### Step 1: Detect Project Context

Read the project to understand:
- Tech stack (check package.json, go.mod, pyproject.toml, etc.)
- Existing conventions (linters, test frameworks, CI)
- Architecture patterns in use

### Step 2: Build Skill Registry

Build the skill registry:

1. Scan user skills: glob `*/SKILL.md` across skill directories. **User-level**: `~/.claude/skills/`. **Project-level**: `.claude/skills/`, `skills/`. Skip `sdd-*` and `_shared`. Deduplicate by name (project-level wins). Read frontmatter triggers.
2. Scan project conventions: check for `agents.md`, `AGENTS.md`, `CLAUDE.md` (project-level), `.cursorrules`, `GEMINI.md`, `copilot-instructions.md` in the project root. If an index file is found (e.g., `agents.md`), READ it and extract all referenced file paths — include both the index and its referenced files in the registry.
3. **ALWAYS write `.atl/skill-registry.md`** in the project root (create `.atl/` if needed). This file is mode-independent — it's infrastructure, not an SDD artifact.
4. If engram is available, **ALSO save to engram**: `mem_save(title: "skill-registry", topic_key: "skill-registry", type: "config", project: "{project}", content: "{registry markdown}")`

The registry format: one entry per skill with name, path, triggers, and format type.

### Step 3: Persist Project Context

**This step is MANDATORY — do NOT skip it.**

If Engram is available:
```
mem_save(
  title: "sdd-init/{project-name}",
  topic_key: "sdd-init/{project-name}",
  type: "architecture",
  project: "{project-name}",
  content: "{your detected project context from Steps 1-2}"
)
```

### Step 4: Return Summary

Return a structured summary:

#### If Engram is available:

Persist project context following `skills/_shared/engram-convention.md` with title and topic_key `sdd-init/{project-name}`.

Return:
```
## SDD Initialized

**Project**: {project name}
**Stack**: {detected stack}
**Persistence**: engram

### Context Saved
Project context persisted to Engram.
- **Engram ID**: #{observation-id}
- **Topic key**: sdd-init/{project-name}

No project files created.

### Next Steps
Ready for /sdd-explore <topic> or /sdd-propose <change-name>.
```

#### If Engram is not available:
```
## SDD Initialized

**Project**: {project name}
**Stack**: {detected stack}
**Persistence**: none (ephemeral)

### Context Detected
{summary of detected stack and conventions}

### Recommendation
Enable `engram` for artifact persistence across sessions. Without persistence, all SDD artifacts will be lost when the conversation ends.

### Next Steps
Ready for /sdd-explore <topic> or /sdd-propose <change-name>.
```

## Rules

- NEVER create placeholder spec files - specs are created via sdd-spec during a change
- ALWAYS detect the real tech stack, don't guess
- NEVER behave like the orchestrator from this phase - execute directly and return results
- Keep config context CONCISE - no more than 10 lines
- Return a structured envelope with: `status`, `executive_summary`, `detailed_report` (optional), `artifacts`, `next_recommended`, and `risks`
