# 连接泄漏故障排查

## 概述

连接泄漏是指应用未正确关闭 MongoDB 连接，导致连接堆积、资源耗尽，最终可能导致连接数打满。

## 典型症状

- 连接数持续增长
- 很多连接处于空闲状态
- 连接数接近上限
- 重启应用后连接数下降

> 函数参数详见 [api/metadata-query.md](../../api/metadata-query.md)。

## 排查步骤

### 步骤 1: 检查连接统计

```python
# 获取连接统计
execute_sql(client, instance_id="mongo-xxx",
    sql="db.serverStatus().connections;", database="admin"
)
```

### 步骤 2: 分析连接状态

```python
# 获取按客户端分组的连接
execute_sql(client, instance_id="mongo-xxx",
    sql="""
    db.getSiblingDB('admin').aggregate([
        { $currentOp: { allUsers: true, idleConnections: true } },
        { $group: {
            _id: "$client",
            count: { $sum: 1 },
            avgDuration: { $avg: "$secs_running" }
        }},
        { $sort: { count: -1 } }
    ]);
    """, database="admin"
)
```

## 常见根因

| 根因 | 说明 |
|-------|-------------|
| 应用 Bug | 应用未正确关闭连接 |
| 连接池配置不当 | 连接池配置不当 |
| 异常未处理 | 异常未处理，连接未释放 |
| 网络问题 | 网络问题导致连接未正常关闭 |

## 预防措施

1. 使用正确的连接池
2. 实现正确的连接生命周期管理
3. 正确处理异常
4. 设置适当的超时值
5. 监控连接状态
6. 设置连接数告警

## 关联场景

- [连接数打满](connection-full.md)
