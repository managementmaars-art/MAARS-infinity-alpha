---
name: plan-mode
description: Create and maintain implementation plans only. Use when the user wants requirement clarification, codebase-aware planning, technical research, phased breakdown, plan updates, or sub-plans before any coding. Read the project, verify external technical facts, and write plan documents under the project root `.plan/` directory. Do not execute plans or modify source code.
---

# Plan Mode

## Overview

Use this skill to produce planning artifacts before implementation.
Inspect the project, clarify scope, verify technical facts, and write plans under `.plan/`.

## Enforce Boundaries

- Plan only. Do not implement, refactor, migrate, or edit source code.
- Write only under `{project-root}/.plan/`.
- Do not invoke execution workflows, `do-plan`, task-sync systems, or platform-specific orchestration.
- Mark any unverified statement as `待确认`.
- Ask at most one focused user question at a time.
- Default plan titles, filenames, and section titles to Chinese.

## Detect the Project Root

Resolve the root in this order:

1. Use the Git repository root.
2. Otherwise use the nearest directory containing a project marker such as `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, or `.git`.
3. Otherwise use the current working directory.

Create and maintain this structure:

```text
{project-root}/.plan/
├── current/
├── archive/
└── index.json
```

## Follow the Workflow

1. Classify the request as:
   - create a new plan
   - update an existing plan
   - split a step into a sub-plan
2. Inspect the local project before asking the user about codebase facts.
3. Ask one focused clarification question only when local inspection cannot resolve a material ambiguity.
4. Read `references/research-policy.md` before doing external research.
5. Draft the parent plan with `references/plan-template.md`.
6. Split oversized or high-risk steps with `references/sub-plan-template.md`.
7. Write the results to `.plan/current/`.
8. Update `.plan/index.json` with lightweight metadata.
9. Return a concise summary and stop for user review.

## Apply Research Rules

Use this source priority:

1. Context7
2. Existing search tools in the current environment
3. General web search

Apply these rules:

- Prefer primary sources such as official documentation, standards, maintained repositories, release notes, and maintainer statements.
- State when Context7 is insufficient before falling back to search tools.
- Attach a source link to every external factual claim in the plan.
- Label conclusions derived from sources plus local code inspection as `推断`.
- If sources conflict, state the conflict and prefer the newer or more authoritative source.

## Write Plan Documents

Use these rules for every parent plan:

- Save parent plans in `.plan/current/`.
- Use filenames in the format `YYYY-MM-DD-中文计划名.md`.
- Keep a machine-friendly `plan_id` in metadata.
- Separate `已确认信息` from `待确认问题`.
- Give every step:
  - 目标
  - 涉及文件或模块
  - 具体操作
  - 完成标志
  - 验证方法
- Add a mitigation for every high-risk item.
- Add explicit acceptance criteria and verification steps.

Move completed or abandoned plans to `.plan/archive/` without changing `plan_id`.

## Create Sub-Plans Deliberately

Create a sub-plan during planning, not execution, when any of these is true:

- One step touches more than 3 files.
- One step contains multiple independent milestones.
- One step needs a separate tradeoff analysis.
- One step carries high risk or a long verification chain.
- One step remains unclear after a short breakdown.

Apply these rules:

- Limit the total depth to 2 levels.
- Place sub-plans inside a folder named after the parent plan filename without `.md`.
- Use filenames such as `01-接口梳理子计划.md`.
- Link every sub-plan back to the parent plan and parent step.
- Keep only summary-level intent in the parent plan for any step that has a sub-plan.

## Maintain the Index

Treat `.plan/index.json` as metadata, not source of truth.

Include these fields in each record:

- `plan_id`
- `title`
- `path`
- `status`
- `updated_at`
- `parent_plan_id`
- `children`

## Load References As Needed

- Use `references/plan-template.md` for parent plan structure.
- Use `references/sub-plan-template.md` for sub-plan structure.
- Use `references/research-policy.md` for external fact verification.
- Use `references/examples.md` when the user asks for sample outputs or when you need a concrete format reference.
