# db diff

分页查看**线上库相对上次分析**的 schema 差异（新增表、删除表、改字段等）。只读。

## 何时用

- 表结构变更后，决定是跑全量分析还是 `analyze-start --tables …` 增量
- 排查「平台数据集与真实库不一致」

## 命令

```bash
rabetbase db diff --id 10157 --format compress
rabetbase db diff --id 10157 --table order --page 1 --pagesize 20 --format compress
```

## 参数

| Flag | 必填 | 说明 |
|------|------|------|
| `--id` | **是** | dblink id |
| `--table` | 否 | 表名模糊过滤 |
| `--page` / `--pagesize` | 否 | 默认 `1` / `20` |

## `diffType` 语义（与 yuntoo-web-app 增量分析抽屉一致）

接口返回 `IDbTableDiffInfo.diffType`，工作台「数据库连接 → 增量分析」里对每行表的展示文案如下，可与 CLI 输出对照：

| `diffType` | 界面文案 | 含义 |
|------------|----------|------|
| `NEW_TABLE` | 表新增 | 物理库中**有**该表，但**尚未纳入**（或尚未完成）上次智能分析；适合勾选后走 `db analyze-start --tables …` 做增量分析。 |
| `DELETED_TABLE` | 表删除 | 相对上次已分析快照，该表在库侧**已不存在**（或已被移除）；界面上勾选增量分析时**不可选**该行。 |
| `MODIFIED_TABLE` | 表修改 | 表仍在，但**结构相对上次分析有变**；同条记录里可能有 `fieldDiff`（`addedColumns` / `deletedColumns` / `modifiedColumns`）。 |
| `ALREADY_ANALYZED` | 无差异 | 当前表结构与上次分析结果**一致**，无需因本表再跑增量（界面用灰色「无差异」标签）。 |

**读你这份 JSON 的示例**：`project_members` 为 `NEW_TABLE` 表示库里有这张新表待分析；其余为 `ALREADY_ANALYZED` 表示与平台已分析状态对齐。若某表为 `MODIFIED_TABLE`，CLI 信封里除 `tableName` 外还可能出现 `fieldDiff` 字段（与界面 Tooltip 中「新增/删除/修改字段」一致）。

## 参考

- [database-connection-workflow.md](../guides/database-connection-workflow.md)
- [SKILL.md](../SKILL.md)
