---
name: claude-changelog
description: 获取 Claude Code 最新 changelog。触发词：claude changelog、CC更新了什么、claude code更新、最新版本、what's new in claude code
allowed-tools: Bash, WebFetch, WebSearch
---

# Claude Code Changelog — 版本更新追踪

获取 Claude Code 昨天到当前的所有版本更新，输出结构化的 changelog 摘要报告。

## When to Use

当用户请求以下操作时触发：
- "claude changelog" / "CC 更新了什么" / "claude code 最新更新"
- "what's new in claude code" / "最新版本"
- "今天 claude code 发了什么版本"

## Phase 1: 数据采集

### 1.1 获取最新 releases

运行以下命令获取最近的 GitHub Releases（拉取足够多以覆盖昨天到今天的所有版本）：

```bash
gh api repos/anthropics/claude-code/releases --jq '.[0:30] | .[] | {tag_name, published_at, body}' 2>/dev/null
```

如果 `gh` 命令不可用，fallback 到 curl：

```bash
curl -s "https://api.github.com/repos/anthropics/claude-code/releases?per_page=30"
```

### 1.2 确定时间范围

**默认范围**：昨天 CST 00:00 到当前时间。

用户可覆盖默认范围：

| 用户输入 | 筛选规则 |
|---------|---------|
| 默认（无指定）| 昨天 CST 00:00 ~ 当前时间 |
| 今天 / today | 今天 CST 00:00 ~ 当前时间 |
| 最近N天 | N天前 CST 00:00 ~ 当前时间 |
| 最新 / latest | 仅最新 1 个版本 |
| 全部 / all | 最近 30 个版本 |

先用 `date` 命令计算昨天 CST 00:00 对应的 UTC 时间戳，然后按 `published_at` 过滤 releases。

```bash
# 计算昨天 CST 00:00 的 UTC 时间（即昨天 UTC 16:00）
SINCE=$(TZ=Asia/Shanghai date -v-1d +"%Y-%m-%dT00:00:00+08:00" 2>/dev/null || TZ=Asia/Shanghai date -d "yesterday" +"%Y-%m-%dT00:00:00+08:00")
echo "筛选起点: $SINCE"
```

GitHub API 返回 UTC 时间，展示时转为 CST (UTC+8)。

## Phase 2: 分析与分类

对筛选后的版本进行分析。

### 2.1 变更分类

将每个 release body 中的条目分为以下类别：

| 类别 | 标记 | 说明 |
|------|------|------|
| NEW | 新功能 | 新增的用户可感知功能 |
| IMPROVE | 改进 | 对已有功能的增强 |
| FIX | 修复 | Bug 修复 |
| SECURITY | 安全 | 安全相关修复 |
| PERF | 性能 | 性能优化、内存优化 |
| PLATFORM | 平台 | 特定平台修复（Windows/macOS/Linux/VS Code）|

### 2.2 重要性标注

对每个变更评估重要性：
- **HIGH**：新功能、breaking changes、安全修复
- **MEDIUM**：功能改进、常见 bug 修复
- **LOW**：平台特定修复、小优化

## Phase 3: 输出报告

输出 markdown 格式的 changelog 摘要：

```markdown
# Claude Code Changelog Report

> 时间范围：{start_date} ~ {end_date} CST
> 版本数：{count} 个（{earliest_version} → {latest_version}）

## 速览

> **值得关注的更新：**
> - {HIGH importance item 1}
> - {HIGH importance item 2}
> - ...

## 版本详情

### v{version} — {YYYY-MM-DD HH:MM} CST

**新功能**
- {item}

**改进**
- {item}

**修复**
- {item}

---

### v{version} — {YYYY-MM-DD HH:MM} CST
...

## 统计

| 类别 | 数量 |
|------|------|
| 新功能 | {n} |
| 改进 | {n} |
| 修复 | {n} |
| 性能 | {n} |
| 平台 | {n} |
```

**输出规则：**
- 时间统一用 CST (UTC+8) 展示
- 每个版本的变更条目保留原文，分类标签加在行首
- 版本按时间**从新到旧**排列
- 如果时间范围内无新版本，说明该时段无更新
- 将报告保存为 `claude-changelog-{date}.md` 到当前工作目录

## Edge Cases

- **GitHub API 不可用**：fallback 到 `curl` 直接拉 CHANGELOG.md raw 文件：`curl -s "https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md" | head -200`
- **无网络**：提示用户检查网络连接
- **gh 未安装**：自动 fallback 到 curl
- **时间范围内无版本**：输出"该时段无新版本发布"并附最近一个版本的信息
