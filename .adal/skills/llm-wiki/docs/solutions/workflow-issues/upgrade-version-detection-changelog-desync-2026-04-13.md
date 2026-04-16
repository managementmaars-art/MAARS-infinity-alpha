---
title: "升级脚本版本检测失败：git tag 与 CHANGELOG.md 不同步"
date: 2026-04-13
category: docs/solutions/workflow-issues
module: llm-wiki-skill
problem_type: workflow_issue
component: tooling
severity: medium
root_cause: missing_workflow_step
resolution_type: workflow_improvement
applies_when:
  - 发布新版本并推送 git tag 后
  - 运行 /llm-wiki-upgrade 验证版本检测时
  - 任何使用 CHANGELOG.md 作为版本源的升级流程
tags: [changelog, version, git-tag, release-workflow, upgrade]
---

# 升级脚本版本检测失败：git tag 与 CHANGELOG.md 不同步

## Context

合并 Phase A+B 功能 PR 后，创建了 git tag `v2.1.0` 并推送到远程。运行 `/llm-wiki-upgrade` 时，脚本报告版本仍为 `v2.0.0`，提示"已是最新版本"。

升级脚本从 CHANGELOG.md 读取版本号：

```bash
# llm-wiki-upgrade SKILL.md 第 22 行
OLD_VERSION=$(grep -m1 "^## v" "$SKILL_DIR/CHANGELOG.md" 2>/dev/null \
  | grep -oE 'v[0-9]+\.[0-9]+\.[0-9]+' | head -1 || echo "unknown")
```

CHANGELOG.md 第一个 `## v` 标题仍然是 `## v2.0.0 (2026-04-11)`。git tag 存在但 changelog 未更新，脚本比较 `v2.0.0 == v2.0.0`，判定无需升级。

## Guidance

### 规则：每个 git tag 必须伴随 CHANGELOG.md 更新，且 tag 必须打在包含 changelog 的 commit 上

正确发布顺序：

```bash
# 1. 先更新 CHANGELOG.md（在文件顶部添加新版本条目）
# 2. 提交 changelog
git add CHANGELOG.md
git commit -m "docs: update CHANGELOG for vX.Y.Z"

# 3. 在包含 changelog 的 commit 上打 tag
git tag vX.Y.Z

# 4. 推送
git push && git push origin vX.Y.Z
```

### 本次修复操作

```bash
# 1. 更新 CHANGELOG.md 添加 v2.1.0 条目
# 2. 提交
git add CHANGELOG.md
git commit -m "docs: update CHANGELOG for v2.1.0"

# 3. 删除旧 tag 并重新打
git tag -d v2.1.0
git tag v2.1.0

# 4. 推送 commit 和 force-push tag
git push origin main
git push origin v2.1.0 --force
```

## Why This Matters

1. **升级检测依赖 CHANGELOG.md**：`/llm-wiki-upgrade` 用 CHANGELOG.md 的第一个 `## v` 标题判断版本。changelog 未更新，即使 tag 存在，升级不会触发。

2. **tag 和 changelog 必须指向同一个 commit**：tag 指向的 commit 必须包含对应的 changelog 条目。否则用户 clone 后看到的 changelog 版本与 tag 不匹配。

3. **跳过此步骤的后果**：本次 bug 中，用户完成开发、合并 PR、打 tag 后，运行升级得到"已是最新"。其他环境中的用户同样无法感知新版本。

## When to Apply

- 每次创建语义化版本 tag（`vX.Y.Z`）时
- 合并 feature PR 或 release PR 后准备发布时
- 执行 `/llm-wiki-upgrade` 前检查版本一致性时

## Examples

### 错误做法（本次 bug）

```bash
# 合并 PR
gh pr merge 6 --merge

# 直接打 tag，跳过 CHANGELOG
git tag v2.1.0
git push origin v2.1.0

# 结果：upgrade skill 读到 v2.0.0，判定"已是最新"
```

### 正确做法

```bash
# 合并 PR
gh pr merge 6 --merge

# 先更新 CHANGELOG.md
# ...添加 ## v2.1.0 (2026-04-13) 条目...

# 提交 changelog
git add CHANGELOG.md
git commit -m "docs: update CHANGELOG for v2.1.0"

# 在包含 changelog 的 commit 上打 tag
git tag v2.1.0

# 推送
git push && git push origin v2.1.0
```

### 发布检查清单

发布新版本前确认：

- [ ] CHANGELOG.md 顶部有新版本条目
- [ ] CHANGELOG.md 条目的版本号与即将创建的 tag 一致
- [ ] tag 打在包含 changelog 更新的 commit 上
- [ ] 本地运行 `/llm-wiki-upgrade` 验证版本检测正确

## Related

- `~/.claude/skills/llm-wiki-upgrade/SKILL.md` — 升级脚本，版本检测逻辑所在
- `docs/plans/2026-04-11-wiki-core-upgrades-design.md` — Phase 5 提到 CHANGELOG 更新但未定义发布门禁
