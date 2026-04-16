# 内存压力故障排查

## 概述

内存压力是指 PostgreSQL 实例的内存使用率持续较高，可能导致 OOM、swap 使用、缓存命中率下降、查询性能下降等问题。

## 典型症状

- 内存使用率持续 80% 以上
- 系统出现 swap
- 缓存命中率下降
- 查询性能下降
- OOM 报错

> 函数参数详见 [api/ops.md](../../api/ops.md) 和 [api/metadata-query.md](../../api/metadata-query.md)。

## 排查步骤

### 步骤 1: 检查内存使用率

```python
import time
now = int(time.time())

# 获取最近一小时健康概览（含内存使用率、连接数使用率等）
describe_health_summary(client,
    end_time=now,
    instance_id="pg-xxx",
)
```

### 步骤 2: 检查内存配置

```python
# 获取 shared buffers
execute_sql(client,
    instance_id="pg-xxx",
    sql="SHOW shared_buffers;", database="postgres"
)

# 获取 work mem
execute_sql(client,
    instance_id="pg-xxx",
    sql="SHOW work_mem;", database="postgres"
)
```

## 常见根因

| 根因 | 说明 |
|-------|-------------|
| Shared Buffers 太小 | shared_buffers 配置过小 |
| 连接数过多 | 连接数过多 |
| 大查询 | 大查询消耗过多内存 |
| 复杂排序 | 复杂排序占用内存 |

## ⚠️ 应急处置（需确认后执行）

### 终止大查询

> **警告**：终止进程会导致当前事务失败，请在确认后执行！

```python
kill_process(client,
    process_ids=["12345"],
    node_id="node-1",
    instance_id="pg-xxx",
)
```

## 预防措施

1. 正确配置 shared_buffers
2. 设置适当的 work_mem
3. 使用连接池（PgBouncer）
4. 监控内存使用趋势
5. 优化查询以减少内存消耗
6. 设置内存使用告警

## 关联场景

- [慢查询](slow-query.md)
