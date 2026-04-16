# dataset links

获取应用数据集的链接关系图（数据集之间的 JOIN 关联关系）。

## 命令

```bash
rabetbase dataset links --format json
rabetbase dataset links --db ecommerce_db --format json
rabetbase dataset links --db 10157 --format json
```

## 参数

| Flag | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| `--db <name|id>` | string | 否 | 自动枚举所有数据库 | 按数据库筛选，支持名称或数字 ID |
| `--verbose` | boolean | 否 | `false` | 返回 API 原始完整响应 |
| `--format <fmt>` | string | 否 | `pretty` | 输出格式 |

## 输出

返回每个数据库下所有数据集的字段结构（含 PK/FK 标记）和数据集之间的 JOIN 关联关系（含 joinType）。

```json
{
  "db": "ecommerce_db",
  "dbId": 10157,
  "datasetCount": 15,
  "datasets": [{
    "name": "订单主表",
    "code": "...",
    "table": "order",
    "fields": [
      { "name": "user_id", "displayName": "用户ID", "type": "BIGINT UNSIGNED", "pk": false, "fk": true }
    ],
    "relations": [
      { "from": "user_id", "toDataset": "用户", "toCode": "...", "toField": "id", "joinType": "ONE_TO_MANY" }
    ]
  }]
}
```

## 提示

- AI 在编写跨数据集 SQL 或 BFF 前，用一次调用获取完整数据模型
- 无需多次调用 `dataset detail` 来了解表间关系

## 参考

- [SKILL.md](../SKILL.md)
