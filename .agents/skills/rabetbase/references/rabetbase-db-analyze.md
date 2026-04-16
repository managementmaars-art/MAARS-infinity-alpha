# db analyze-start / analyze-cancel / analyze-status

管理 **schema 分析任务**：启动全量/增量分析、取消、查询状态。`analyze-start` 与 `analyze-cancel` 为 **write**；`analyze-status` 为 **read**（仅按 plan 查询，不需要配置 appcode）。

## 何时用

- **analyze-start**：接入新库或表结构大变后，同步到 Lovrabet（生成/更新数据集元数据的前置）
- **analyze-cancel**：任务卡住或误触，需要停掉当前分析
- **analyze-status**：轮询任务是否 `SUCCESS` / `FAILED`

## trace / plan id 从哪来

见 [database-connection-workflow.md](../guides/database-connection-workflow.md) 第二节。摘要：

1. **`db list` / `db detail`** 中的 **`latestAnalysisTraceId`**
2. **`db analyze-start`** 返回的 **`data.planId`**

## 命令

```bash
# 全量或默认分析
rabetbase db analyze-start --id 10157 --format compress

# 仅分析指定表（逗号分隔）
rabetbase db analyze-start --id 10157 --tables orders,order_item --format compress

# 取消（可省略 --plan，CLI 会取该连接 latestAnalysisTraceId）
rabetbase db analyze-cancel --id 10157 --format compress

# 查状态（必须 --plan）
rabetbase db analyze-status --id 10157 --plan <traceId> --format compress
```

## 参数

| 子命令 | 主要 flags |
|--------|------------|
| **analyze-start** | `--id`（必填）、`--tables`（可选，增量表名列表） |
| **analyze-cancel** | `--id`（必填）、`--plan`（可选，缺省用 latestAnalysisTraceId） |
| **analyze-status** | `--id`（必填）、`--plan`（必填） |

## 参考

- [database-connection-workflow.md](../guides/database-connection-workflow.md)
- [SKILL.md](../SKILL.md)
