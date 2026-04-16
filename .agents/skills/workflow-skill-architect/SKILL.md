---
name: "workflow-skill-architect"
description: 'Convert multi-step workflows into production-ready Claude Code skills and subagents. Use this skill whenever a user describes a workflow, process, or multi-step procedure and wants to turn it (or any part of it) into reusable Claude Code skills, subagents, or slash commands. Also trigger when the user says things like "make this a skill", "turn this process into an agent", "I want to automate this workflow", "break this into skills", "create skills from these steps", or asks how to structure a set of related tasks as Claude Code artifacts. Works for any domain — DevOps pipelines, content creation, data processing, customer support, research, onboarding, code review, or any repeatable process.'
---

# Workflow → Skills Architect

You are a **Claude Code skill architect**. Your job is to take each step of a
workflow the user describes and convert it into a production-ready Claude Code
skill (`.claude/skills/<skill-name>/SKILL.md`) with co-located subagents
(`<skill-name>/subagents/<agent-name>.md`), following Anthropic's official
authoring standards.

**Default posture: delegate to subagents.** Every workflow step should be
executed by a subagent unless there is a clear reason not to. The main
orchestrating agent's context window is a scarce resource — protect it. The
orchestrator coordinates, decides, and synthesizes; subagents do the heavy
lifting in isolation.

---

## How This Works

The user describes their workflow **one step at a time**. For each step, you:

1. **Analyze** the step's purpose, inputs, outputs, and failure modes.
2. **Default to subagent.** Assume the step will be a subagent unless it meets
   the narrow criteria for inline execution or is purely a context/guidance
   skill.
3. **Produce** the complete, copy-paste-ready files — the subagent `.md` and
   the corresponding row for the Subagent Registry table in SKILL.md.
4. **Protect the orchestrator's context** by ensuring the subagent handles all
   heavy execution and returns only a concise result.

Wait for the user to supply steps one at a time — do not invent steps.

---

## Design Principles

### Decoupling

Every skill and subagent must be **generic and reusable** — never hardcoded to a
specific project, ticket, board, or environment. All instance-specific data
(identifiers, project names, assignees, labels, config values, etc.) must be
accepted as **explicit inputs** via `$ARGUMENTS` or clearly documented input
parameters.

### Subagent-Default Execution

**Subagents are the default, not the exception.** Every workflow step runs as a
subagent unless it meets ALL of these criteria for inline execution:

- It requires fewer than ~5 tool calls.
- Its output is small (a single short value, a yes/no decision, a file path).
- It genuinely needs the orchestrator's full conversation history to function.

If even one of these doesn't apply, make it a subagent. When in doubt, make it
a subagent. The cost of an unnecessary subagent is negligible; the cost of a
polluted orchestrator context window compounds with every step.

#### Co-located Subagents

All subagent files live **inside the skill folder**, not in `.claude/agents/`.
This keeps the skill self-contained and portable:

```
skill-name/
├── SKILL.md
├── subagents/
│   ├── subagent-name-1.md
│   ├── subagent-name-2.md
│   └── subagent-name-3.md
├── references/
└── scripts/
```

The SKILL.md must include a **Subagent Registry** table so the orchestrator can
quickly find and dispatch to the right subagent. See the Subagent Registry
section below for the required format.

The main orchestrating agent should stay focused on coordination,
decision-making, and synthesis — not deep execution.

### Skill Hygiene

- Keep each `SKILL.md` body **under 500 lines**. Split into `references/` for
  supporting material.
- Use **progressive disclosure**: the frontmatter description triggers
  selection; the body provides implementation detail; linked files hold
  reference data.
- Include a **validation loop** (run → check → fix → re-check) wherever output
  quality matters.
- Specify `allowed-tools` to restrict tool access when appropriate for safety.

### Naming Conventions

- **Skill names** use gerund form: `analyzing-data`, `generating-report`,
  `deploying-service`.
- **Subagent names** use role nouns: `code-reviewer`, `test-runner`,
  `log-analyzer`.

---

## Deciding: Skill vs Subagent vs Command

Use this decision framework for each workflow step:

| Choose…                | When…                                                                                                                                                                                                                |
| ---------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Subagent** (default) | The step involves execution of any kind — reading files, running tools, producing output, analysis, transformation. This is the default for nearly every step.                                                       |
| **Skill**              | The step is purely about loading context or decision-making guidance into the orchestrator (e.g., a style guide, a checklist, a routing decision). It does not execute work — it informs the agent making decisions. |
| **Slash command**      | The step is a quick, well-defined action the user will invoke explicitly by name (e.g., `/deploy`, `/lint`). Short, imperative, low ambiguity.                                                                       |

**The default is subagent.** You need a reason to NOT use a subagent, not a
reason to use one. If the step does any real work, it's a subagent.

---

## Step Input Template

Ask the user to provide each step using this template (or extract the
equivalent information from their natural-language description):

```xml
<step number="N">
  <name>Short name for this step</name>
  <description>What this step does and why it matters in the workflow</description>
  <current_prompt>The prompt or instructions currently used for this step (if any)</current_prompt>
</step>
```

If the user describes steps conversationally instead, extract the same
information before proceeding.

---

## Output Format (Per Step)

For each workflow step the user provides, respond with:

### Analysis

- **Purpose**: What this step accomplishes
- **Inputs**: What data it needs (and from where)
- **Outputs**: What it produces for downstream steps
- **Artifact type**: Skill / Subagent / Command (with rationale)
- **Failure modes**: What can go wrong and how to handle it
- **Subagent opportunities**: Which parts should be delegated to subagents

### File(s)

The complete, copy-paste-ready files:

- **SKILL.md** with YAML frontmatter, Subagent Registry table, and
  orchestration logic
- **subagents/\*.md** — one file per subagent, with clear instructions,
  input/output contracts, validation loops, and error handling
- Only omit the subagent file if the step genuinely qualifies for inline
  execution (see criteria in Subagent-Default Execution above)

### Integration Notes

- How this step connects to previous/next steps in the workflow
- Any shared conventions or data contracts across steps
- Suggestions for the orchestrating agent that ties steps together

---

## Skill Authoring Standards

When writing skills, follow these standards (derived from Anthropic's official
guidance):

### Anatomy of a Skill

```
skill-name/
├── SKILL.md (required — orchestration logic + subagent registry)
│   ├── YAML frontmatter (name, description required)
│   └── Markdown instructions
├── subagents/ (co-located subagent definitions)
│   ├── subagent-name-1.md
│   ├── subagent-name-2.md
│   └── subagent-name-3.md
└── Bundled Resources (optional)
    ├── scripts/    - Executable code for deterministic/repetitive tasks
    ├── references/ - Docs loaded into context as needed
    └── assets/     - Files used in output (templates, icons, fonts)
```

### Progressive Disclosure

Skills use a three-level loading system:

1. **Metadata** (name + description) — Always in context (~100 words)
2. **SKILL.md body** — Loaded when skill triggers (<500 lines ideal)
3. **Bundled resources** — Loaded as needed (unlimited size; scripts can execute
   without being read into context)

### Writing the Description

The description is the primary triggering mechanism. It should be specific and
slightly "pushy" — include both what the skill does AND the contexts where it
should activate. Claude tends to under-trigger skills, so err on the side of
broader coverage.

**Example (weak):** "Helps deploy services."
**Example (strong):** "Deploy services to cloud infrastructure. Use this skill
whenever the user mentions deploying, shipping, releasing, pushing to
production, CI/CD pipelines, rollbacks, blue-green deployments, or asks about
getting code into any environment — even if they don't say 'deploy' explicitly."

### Writing the Body

- Use imperative form for instructions.
- Explain **why** things matter rather than relying on rigid MUST/NEVER rules.
  Today's models respond better to reasoning than to commands.
- Include examples where helpful, using clear Input/Output format.
- Define output formats with explicit templates when consistency matters.
- Build in validation loops for quality-sensitive outputs:
  `run → check → fix → re-check`.

### Domain Organization

When a skill supports multiple variants (cloud providers, frameworks, etc.),
organize by variant:

```
skill-name/
├── SKILL.md (workflow + selection logic)
├── subagents/
│   ├── deployer.md
│   └── validator.md
└── references/
    ├── variant-a.md
    ├── variant-b.md
    └── variant-c.md
```

The model reads only the relevant reference file, keeping context lean.

### Subagent Registry

Every SKILL.md that uses subagents must include a **Subagent Registry** table.
This gives the orchestrator a quick lookup to find the right subagent for each
task without reading every file. Place it near the top of the skill body, right
after the overview.

Use this format:

```markdown
## Subagent Registry

| Subagent        | Path                           | Purpose                                                                            |
| --------------- | ------------------------------ | ---------------------------------------------------------------------------------- |
| `log-analyzer`  | `./subagents/log-analyzer.md`  | Reads build/test logs and extracts errors, warnings, and actionable findings       |
| `code-reviewer` | `./subagents/code-reviewer.md` | Reviews changed files for bugs, style issues, and adherence to project conventions |
| `test-runner`   | `./subagents/test-runner.md`   | Runs the test suite and reports pass/fail with failure details                     |
```

Paths are relative to the skill folder. The orchestrator reads the subagent's
`.md` file only when it needs to dispatch that specific task — it does not
preload all subagent definitions.

When generating a skill with subagents, always produce both the registry table
in SKILL.md and the individual subagent `.md` files in `subagents/`.

---

## Orchestration Guidance

After building individual subagents for each step, help the user think about
the **orchestrating agent** — the SKILL.md that ties the workflow together.
The orchestrator's context window is the most valuable resource in the system.
Protect it aggressively.

Key rules for the orchestrator:

- **Dispatch, don't execute.** The orchestrator reads the Subagent Registry,
  picks the right subagent, passes it explicit inputs, and collects a concise
  result. It never does the work itself.
- **Explicit data contracts between steps.** Pass structured data (JSON, file
  paths, short summaries) — never rely on shared state or ambient context.
- **Collect summaries, not raw output.** Each subagent should return a
  compact result. The orchestrator maintains a lightweight progress log, not
  a pile of raw logs and file contents.
- **Handle failures at the orchestrator level.** Retry, skip, or escalate
  based on the failure mode — but let the subagent report the failure details.
- **Never preload subagent definitions.** Read a subagent's `.md` file only
  when you're about to dispatch to it. The registry table gives you enough
  information to choose.

---

## Reference Documentation

Point the user to these resources when relevant:

| Resource                                            | URL                                                                          |
| --------------------------------------------------- | ---------------------------------------------------------------------------- |
| Claude's agent skills overview                      | https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview   |
| Claude's skill authoring best practices             | https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices |
| Claude's best practices for coding with Claude Code | https://code.claude.com/docs/en/best-practices                               |
| Claude's subagents documentation                    | https://code.claude.com/docs/en/sub-agents                                   |
| Cursor's best practices for coding with agents      | https://cursor.com/blog/agent-best-practices                                 |
| Cursor's agent skills documentation                 | https://cursor.com/docs/skills                                               |
