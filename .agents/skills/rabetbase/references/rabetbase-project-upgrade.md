# project upgrade

从 lovrabet-cli 迁移到 rabetbase-cli。

> **风险等级：high-risk-write** — 删除文件、修改配置、卸载/安装包。

## 命令

```bash
# 交互模式（先分析 → 展示报告 → 确认 → 执行）
rabetbase project upgrade

# 自动模式（跳过确认）
rabetbase project upgrade --yes
```

## 参数

| Flag | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| `--yes` | boolean | 否 | `false` | 跳过确认提示，直接执行 |

## 执行流程

两阶段模式：先分析 → 展示报告 → 确认 → 执行 6 步：

| 步骤 | 操作 | 说明 |
|------|------|------|
| 1 | 配置文件迁移 | 旧配置（`.lovrabet.json` 等）→ `.rabetbase.json`，旧文件备份为 `.bak` |
| 2 | 删除 `.lovrabet/` | 移除旧的工作目录 |
| 3 | 删除旧 IDE skill 文件 | 移除 `.cursor/rules/lovrabet_rules.mdc`、`.claude/skills/lovrabet` 等 |
| 4 | 清理 MCP 配置 | 从 `.cursor/mcp.json` 移除引用 `@lovrabet/dataset-mcp-server` 的条目 |
| 5 | 移除旧 skill | `npx skills remove lovrabet/lovrabet-skill` |
| 6 | 安装新 skill | `npx skills add lovrabet/rabetbase --global` |

## 分析报告

执行前会扫描并展示：
- 旧配置文件路径和待迁移字段
- 旧文件/目录列表
- MCP 配置中待清理的条目
- 是否需要 skill 替换

## 输出

- 每步显示 OK / FAIL 和详情
- 最终汇总表：所有步骤的执行结果
- 全部成功：`Upgrade completed successfully!`
- 部分失败：提示检查 summary

## 触发方式

- 手动执行：`rabetbase project upgrade`
- 自动触发：`rabetbase init` 检测到旧配置时自动路由

## 参考

- [SKILL.md](../SKILL.md)
- [rabetbase init](rabetbase-init.md)
