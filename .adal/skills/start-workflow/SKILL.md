---
name: start-workflow
description: "Spec-driven development pipeline orchestrator. Given a URL or text description, automatically generates specs, implements code, runs codex review, applies security gate, executes tests, syncs docs, and notifies via Telegram. Triggers on: /start-workflow, start workflow, build feature, implement feature, spec-driven, start pipeline."
allowed-tools:
  - Bash(find .claude/skills ~/.claude/skills -maxdepth 1 -name start-workflow -type d*)
  - Bash(python3 .claude/skills/start-workflow/scripts/*)
  - Bash(python3 ~/.claude/skills/start-workflow/scripts/*)
  - Bash(bash .claude/skills/start-workflow/setup.sh*)
  - Bash(bash ~/.claude/skills/start-workflow/setup.sh*)
  - Bash(bash .claude/skills/start-workflow/skills/test-runner/scripts/*)
  - Bash(bash ~/.claude/skills/start-workflow/skills/test-runner/scripts/*)
  - Bash(openspec*)
  - Bash(codex review*)
  - Bash(~/.codex/sessions*)
---

# start-workflow

IRON LAW: Run all phases without stopping. Never ask for confirmation between phases. Only pause at the security gate (TG /approve) if the feature is flagged as security-sensitive.

## Invocation

```
/start-workflow
/start-workflow {url | text description}
/start-workflow --resume
/start-workflow --resume <run_id>
```

## Parameters

| Param | Description |
|-------|-------------|
| (none) | Prompt the user to enter their requirement |
| `{url\|text}` | Feature requirement — URL to a spec/issue, or plain text description |
| `--resume` | Auto-find recent runs and let user pick one to resume |
| `--resume <run_id>` | Resume a specific previous run from its last completed phase |

## Resume Flow

If the user invokes `/start-workflow --resume` (no run_id), auto-discover recent runs:

```bash
ls -dt /tmp/workflow-*/state.json 2>/dev/null | head -10
```

For each state.json found, read and extract: `run_id`, `feature_name`, `phase`, `status`, `started_at`.

Present a numbered list to the user:

> 找到以下未完成的 workflow：
>
> 1. `ab12cd34` — health-check — 中断于 coding（2026-04-12 14:32）
> 2. `ef56gh78` — user-auth — 中断于 code-review（2026-04-11 09:15）
>
> 请回复编号选择要恢复的 run，或回复 n 取消：

- If the user replies with a number, use that run's `run_id`.
- If the user replies "n" or any cancellation, stop.
- If no state files are found, tell the user:

> 没有找到可恢复的 workflow run。请直接用 `/start-workflow {需求}` 开始新的任务。

Only show runs where `status` is not `DONE` — skip completed runs.

## Input Collection

If the user invokes `/start-workflow` with no arguments, ask:

> 请描述你想要实现的功能，或者粘贴一个需求链接（GitHub Issue、文档 URL 等）：

Wait for the user's reply. Use that as `input_raw`.

Then **automatically derive a feature name** from the input:
- From URL: use the last path segment or issue title (e.g. `issues/42` → read title → `user-auth-revamp`)
- From text: extract the core noun phrase (e.g. "给项目加一个 /health 接口" → `health-check`)
- Format: kebab-case, 2–4 words, no spaces, lowercase, ASCII only

Show the derived name to the user:

> 功能名称：`health-check`（如需修改请直接回复新名称，确认则回复 ok）

If the user replies with a new name, use that. If they reply "ok" or any affirmation (好/确认/yes/continue/👍), proceed with the derived name.

## Resolve Skill Directory (run first, every time)

Skills can be installed globally (`~/.claude/skills/`) or per-project (`.claude/skills/`). Always resolve the actual path before running any script:

```bash
SKILL_DIR=$(find \
  .claude/skills ~/.claude/skills \
  .cursor/skills ~/.cursor/skills \
  .windsurf/skills ~/.windsurf/skills \
  .cline/skills ~/.cline/skills \
  .agents/skills ~/.agents/skills \
  -maxdepth 1 -name start-workflow -type d 2>/dev/null | head -1)
SKILLS_BASE="$SKILL_DIR/skills"
```

All script references below use `$SKILL_DIR` (for own scripts) and `$SKILLS_BASE` (for sub-skills).

## Prerequisites Check

```bash
bash "$SKILL_DIR/setup.sh"
```
If any dependency is missing, stop and tell the user what to install.

Read `~/.claude/.env` to get `TG_CHAT_ID` (optional — skip TG steps if absent).

### Git Init Check

Check if the current directory is a git repository:
```bash
git rev-parse --git-dir 2>/dev/null
```

If it is NOT a git repo, tell the user:

> 当前目录不是 git 仓库，openspec 需要 git 环境。是否现在初始化？（会执行 `git init` 和一个空 commit）

If the user agrees, run:
```bash
git init
```

Then create a `.gitignore` with common defaults before the first commit:
```
# Dependencies
node_modules/
.venv/
__pycache__/
*.pyc

# Lock files (tracked but excluded from review diffs)
# package-lock.json and yarn.lock are intentionally committed

# Build output
dist/
build/
.next/
out/

# Environment
.env
.env.local
.env.*.local

# Editor & OS
.DS_Store
.idea/
.vscode/
*.swp
```

```bash
git add .gitignore
git commit -m "chore: init with .gitignore"
```

If the user declines, stop and explain that a git repo is required.

## Execution Flow

### Phase 0 — Bootstrap

```bash
RUN_DIR=$(python3 "$SKILL_DIR/scripts/bootstrap.py" \
  "{feature_name}" "{input_raw}" "{tg_chat_id}")

python3 "$SKILL_DIR/scripts/detect-input.py" "$RUN_DIR/state.json"
```

For `--resume <run_id>` (run_id already known): set `RUN_DIR=/tmp/workflow-<run_id>`, read existing state.json, skip phases with `status: done`.

For `--resume` (no run_id): follow the Resume Flow above to resolve the run_id first, then proceed as above.

### Phase 1 — spec-writer

Load and follow `$SKILLS_BASE/spec-writer/SKILL.md` with:
- `RUN_DIR` = current run directory
- `PROJECT_DIR` = current working directory
- Content = `state.fetched_content` from state.json

After spec-writer completes, update state atomically:
```python
state['phases']['spec-writer']['status'] = 'done'
state['phase'] = 'coding'
```

### Phase 2 — Coding

Before starting, resolve and read project conventions (same pattern as spec-writer):
```bash
CONVENTIONS_DIR=$(find \
  .claude/conventions .cursor/conventions \
  .windsurf/conventions .cline/conventions \
  .agents/conventions \
  -maxdepth 0 -type d 2>/dev/null | head -1)
```
If found, read `frontend.md`, `backend.md`, `database.md` and follow them when writing code.

Read `{specs_dir}/tasks.md`. For **each task**, complete the full cycle before moving to the next:
1. Read the task description
2. Implement **only that task** — do not implement multiple tasks at once
3. `git add -A && git commit -m "feat: {task_name}"` immediately after implementation
4. Update `state.phases.coding.last_task` atomically
5. Only then read and start the next task

Do NOT write all code first and commit later. Each task = one commit, in order.

On completion:
```python
state['phases']['coding']['status'] = 'done'
state['phase'] = 'code-review'
```

### Phase 3 — code-reviewer

Load and follow `$SKILLS_BASE/code-reviewer/SKILL.md` with:
- `RUN_DIR` = current run directory
- `PROJECT_DIR` = current working directory
- Max rounds = 2

After code-reviewer completes, update state and advance phase.

### Phase 4 — Security Gate

Read `{specs_dir}/specs` and `{specs_dir}/design` for keywords:
`auth`, `authentication`, `authorization`, `payment`, `billing`, `PII`, `personal data`, `encryption`, `admin`, `privilege`, `sudo`, `root`

**If NOT sensitive**: set `state.phases.security-gate.status = skipped`, continue.

**If sensitive**:
```bash
MSG_ID=$(python3 "$SKILL_DIR/scripts/tg-send.py" \
  "$TG_CHAT_ID" \
  "⚠️ *需要安全审批*\n\n功能：{feature_name}（{run_id}）\n\n未解决问题：\n{findings_list}\n\n回复 /approve 继续，或 /deny 终止。")

python3 "$SKILL_DIR/scripts/tg-poll-approval.py" \
  "$TG_CHAT_ID" "$MSG_ID" --timeout 3600
APPROVAL_EXIT=$?
# 0=approved, 1=denied, 2=timeout→treat as denied
```

Update state accordingly, stop pipeline if denied.

### Phase 5 — test-runner

Load and follow `$SKILLS_BASE/test-runner/SKILL.md` with `RUN_DIR` and `PROJECT_DIR`.

### Phase 6 — openspec archive

Only if test-runner status = done (tests passed):
```bash
cd "$PROJECT_DIR"
openspec archive "{feature_name}" --yes 2>&1
ARCHIVE_EXIT=$?
```

`openspec archive` moves `.openspec/changes/{feature_name}/` into an archive directory, leaving uncommitted changes in the working tree. After a successful archive, commit these changes:
```bash
git add -A
git commit -m "chore: archive openspec change {feature_name}"
```

Update `state.phases.openspec-archive.status` accordingly. Failure does NOT stop the pipeline — record warning for TG notification.

### Phase 7 — doc-syncer

Load and follow `$SKILLS_BASE/doc-syncer/SKILL.md` with `RUN_DIR` and `PROJECT_DIR`.

### Phase 8 — Done

Update state:
```python
state['status'] = 'DONE'
state['phase']  = 'done'
state['completed_at'] = datetime.now(timezone.utc).isoformat()
```

Send TG notification if `TG_CHAT_ID` is set.

Before sending, compose the message by reading the actual content from artifacts:

- **功能描述**：读取 `{specs_dir}/proposal`，提取"问题陈述"和"成功标准"，用 1-2 句话概括
- **实现内容**：读取 `{specs_dir}/tasks`，列出已完成的任务名称（每条一行，最多 5 条）
- **审查发现与修复**：读取 `$RUN_DIR/review-round-*.txt`，提取实际被修复的 P0/P1 问题描述（非数量，是具体内容）；若全部通过则写"无重大问题"
- **测试结果**：从 `state.phases.test-runner.summary` 读取每个套件的结果：
  - 已运行的套件：显示通过/失败数；若有失败，提取失败测试名称和错误原因（1 句话）
  - 跳过的套件：显示跳过原因 + `next_steps`（安装命令），让用户知道下一步怎么补上

```bash
python3 "$SKILL_DIR/scripts/tg-send.py" \
  "$TG_CHAT_ID" \
  "✅ *工作流完成*\n\n📦 *{feature_name}*（{run_id}）\n⏱ 耗时：{duration}\n\n🎯 *功能概述*\n{proposal_summary}\n\n✅ *已实现*\n{tasks_summary}\n\n🔍 *代码审查*（{review_rounds} 轮）\n{review_findings_summary}\n\n🧪 *测试*\n• Jest：{jest_summary}\n• Playwright：{pw_summary}\n• Smoke：{browser_summary}\n{skipped_hints}\n\n📁 归档：{archive_status} ｜ 📝 文档：{doc_sync_status}"
```

`{skipped_hints}` 由所有有 `next_steps` 的跳过条目组成，例如：
```
⚠️ Playwright 未配置：npm install -D @playwright/test && npx playwright install --with-deps && npx playwright init
```

Print final summary to terminal.

## State Write Pattern (Atomic)

Always use this pattern — never write state directly:
```bash
python3 - "$RUN_DIR/state.json" << 'PYEOF'
import json, os, sys
state_file = sys.argv[1]
state = json.load(open(state_file, encoding='utf-8'))
# modify state...
tmp = state_file + '.tmp.' + str(os.getpid())
with open(tmp, 'w', encoding='utf-8') as f:
    json.dump(state, f, ensure_ascii=False, indent=2)
os.replace(tmp, state_file)
PYEOF
```

## Error Handling

On any phase error:
1. Set `state.status = ERROR`, `state.error = <message>`
2. Send TG notification if TG_CHAT_ID is set
3. Print error and run_id to terminal (user can `--resume` after fixing)
4. Stop immediately
