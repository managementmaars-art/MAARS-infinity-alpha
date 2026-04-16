# 连接数打满故障排查

## 概述

连接数打满是指 MongoDB 实例的当前连接数达到上限，导致新请求无法建立连接，出现连接错误。

## 典型症状

- 应用报错: `too many connections`
- 无法建立新的数据库连接
- 连接数监控显示达到上限
- 旧连接未被释放，堆积

> 函数参数详见 [api/metadata-query.md](../../api/metadata-query.md)。

## 排查步骤

### 步骤 1: 获取连接统计

> **注意**：MongoDB 不支持 `get_metric_items/get_metric_data`，通过 `execute_sql` 使用原生命令获取连接信息。

```python
# 获取连接统计
execute_sql(client, instance_id="mongo-xxx",
    sql="db.serverStatus().connections;", database="admin"
)
```

### 步骤 2: 检查当前活跃操作

```python
# 查看当前所有连接的操作状态
execute_sql(client, instance_id="mongo-xxx",
    sql="""
    db.getSiblingDB('admin').aggregate([
        { $currentOp: { allUsers: true, idleConnections: true } },
        { $group: { _id: "$appName", count: { $sum: 1 }, active: { $sum: { $cond: ["$active", 1, 0] } } } },
        { $sort: { count: -1 } }
    ]);
    """, database="admin"
)
```

## 常见根因

| 根因 | 说明 |
|-------|-------------|
| 连接泄漏 | 应用未正确关闭数据库连接 |
| 连接过多 | 并发请求过多，连接池配置不当 |
| 长运行操作 | 操作耗时过长，占用连接 |
| 应用 Bug | 连接未正确释放 |

## ⚠️ 应急处置（需确认后执行）

### 终止长时间运行的操作

> **警告**：终止操作会导致当前任务失败，请在确认后执行！

```python
# 终止指定操作
execute_sql(client, instance_id="mongo-xxx",
    sql="""
    db.getSiblingDB('admin').killOp(<opId>);
    """, database="admin"
)
```

## 预防措施

1. 使用正确的连接池（MongoClient 设置）
2. 设置适当的连接超时
3. 监控并终止长时间空闲的连接
4. 设置连接数告警
5. 审查应用连接生命周期
6. 适当配置 `maxIncomingConnections`

## 关联场景

- [连接泄漏](connection-leak.md)
- [慢查询](slow-query.md)
