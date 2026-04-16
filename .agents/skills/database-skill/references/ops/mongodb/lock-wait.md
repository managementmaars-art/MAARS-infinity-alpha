# 锁等待故障排查

## 概述

锁等待是指 MongoDB 操作由于无法获取锁而处于等待状态，可能是由于数据库锁、集合锁或元数据锁导致。

## 典型症状

- 查询执行变慢
- 特定操作被阻塞
- 锁等待时间增长
- `db.serverStatus()` 显示锁等待增加

> 函数参数详见 [api/metadata-query.md](../../api/metadata-query.md)。

## 排查步骤

### 步骤 1: 检查锁统计

```python
# 获取锁统计
execute_sql(client, instance_id="mongo-xxx",
    sql="db.serverStatus().locks;", database="admin"
)
```

### 步骤 2: 检查当前操作

```python
# 获取当前操作和锁
execute_sql(client, instance_id="mongo-xxx",
    sql="""
    db.getSiblingDB('admin').aggregate([
        { $currentOp: { allUsers: true, idleConnections: false } },
        { $project: { op: 1, ns: 1, secs_running: 1, locks: 1 } }
    ]);
    """, database="admin"
)
```

## 常见根因

| 根因 | 说明 |
|-------|-------------|
| 长运行操作 | 操作时间过长 |
| 索引构建 | 索引构建 |
| 压缩操作 | 数据压缩操作 |
| 重命名集合 | 集合重命名 |

## ⚠️ 应急处置（需确认后执行）

### 终止阻塞操作

> **警告**：终止操作会导致当前任务失败，请在确认后执行！

```python
# 终止操作
execute_sql(client, instance_id="mongo-xxx",
    sql="""
    db.getSiblingDB('admin').killOp(<opId>);
    """, database="admin"
)
```

## 预防措施

1. 保持操作简短
2. 在低峰期构建索引
3. 使用后台索引创建
4. 监控锁时间
5. 避免长运行操作
6. 使用正确的连接池

## 关联场景

- [慢查询](slow-query.md)
