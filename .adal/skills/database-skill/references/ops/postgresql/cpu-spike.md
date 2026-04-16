# CPU 打满故障排查

## 概述

CPU 打满是指 PostgreSQL 实例的 CPU 使用率持续接近或达到 100%，导致数据库响应变慢或完全无响应。

## 典型症状

- CPU 使用率持续 100% 或接近 100%
- 数据库响应变慢，查询超时
- 连接堆积，新请求排队等待
- 系统负载高

> 函数参数详见 [api/ops.md](../../api/ops.md) 和 [api/metadata-query.md](../../api/metadata-query.md)。

## 排查步骤

### 步骤 1: 确认 CPU 及整体健康状态

```python
import time
now = int(time.time())

# 获取最近一小时健康概览（CPU/内存/连接数/QPS/TPS 等，含环比同比）
describe_health_summary(client,
    end_time=now,
    instance_id="pg-xxx",
)
```

### 步骤 2: 查看活跃会话

```python
# 查询活跃会话（按执行时间降序）
list_connections(client,
    instance_id="pg-xxx",
)
```

关注：长时间运行的查询（time > 300s）、大量活跃连接。

### 步骤 4: 检查锁

```python
# 检查锁
execute_sql(client,
    instance_id="pg-xxx",
    sql="""
    SELECT
        pid,
        relname,
        mode,
        granted,
        duration
    FROM pg_locks l
    JOIN pg_stat_activity a ON l.pid = a.pid
    WHERE NOT granted;
    """, database="postgres"
)
```

## 常见根因

| 根因 | 说明 |
|-------|-------------|
| 复杂查询 | 复杂查询消耗 CPU |
| 缺少索引 | 缺少索引导致全表扫描 |
| 高并发 | 并发请求过多 |
| 大数据处理 | 大数据量处理 |
| 函数执行 | 自定义函数消耗 CPU |

## ⚠️ 应急处置（需确认后执行）

### 终止长时间运行的查询

> **警告**：终止进程会导致当前事务失败，请在确认后执行！

```python
# 按条件终止：终止执行时间超过 60 秒的查询
kill_process(client,
    command_type="Query",
    min_time=60,
    instance_id="pg-xxx",
)

# 精确终止：终止指定进程（从 list_connections 获取 process_id 和 node_id）
kill_process(client,
    process_ids=["12345"],
    node_id="node-1",
    instance_id="pg-xxx",
)
```

## 预防措施

1. 添加适当的索引
2. 优化查询计划
3. 使用连接池（PgBouncer）
4. 监控长时间运行的查询
5. 设置资源限制
6. 定期统计信息收集（ANALYZE）

## 关联场景

- [慢查询](slow-query.md)
- [锁等待](lock-wait.md)
