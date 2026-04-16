# 内存压力故障排查

## 概述

内存压力是指 MySQL 实例的内存使用率持续较高，可能导致 OOM (Out of Memory)、swap 使用、缓存命中率下降等问题。

## 典型症状

- 内存使用率持续 80% 以上
- 系统出现 swap
- InnoDB 缓存命中率下降
- 查询性能下降
- OOM 报错

> 函数参数详见 [api/ops.md](../../api/ops.md)。

## 排查步骤

### 步骤 0: 获取支持的监控指标（推荐先执行）

> **提示**：在获取具体指标数据之前，建议先调用 `get_metric_items` 查看当前实例支持哪些指标，然后选择合适的指标进行获取。

```python
# 获取当前实例支持的监控指标列表
get_metric_items(client,
)
```

### 步骤 1: 检查内存使用率

```python
import time
now = int(time.time())

# 获取内存使用率
get_metric_data(client,
    metric_name="MemUtil",
    period=60,
    start_time=now - 300,
    end_time=now,
    instance_id="mysql-xxx",
)
```

### 步骤 2: 检查 InnoDB Buffer Pool

```python
# 获取 buffer pool 大小
execute_sql(client,
    sql="SHOW VARIABLES LIKE 'innodb_buffer_pool_size';",
    instance_id="mysql-xxx",
    database="performance_schema",
)

# 获取 buffer pool 状态
execute_sql(client,
    sql="""
    SELECT
        POOL_ID,
        POOL_SIZE,
        FREE_BUFFERS,
        DATABASE_PAGES,
        OLD_DATABASE_PAGES,
        TOTAL_MEM_ALLOC
    FROM information_schema.INNODB_BUFFER_POOL_STATS;
    """,
    instance_id="mysql-xxx",
    database="information_schema",
)
```

### 步骤 3: 分析内存使用情况

```python
# 检查各组件内存使用
execute_sql(client,
    sql="""
    SELECT
        EVENT_NAME,
        CURRENT_NUMBER_OF_BYTES_USED,
        HIGH_NUMBER_OF_BYTES_USED
    FROM memory_summary_global_by_event_name
    ORDER BY HIGH_NUMBER_OF_BYTES_USED DESC
    LIMIT 20;
    """,
    instance_id="mysql-xxx",
    database="performance_schema",
)
```

## 常见根因

| 根因 | 说明 |
|-------|-------------|
| Buffer Pool 太小 | innodb_buffer_pool_size 配置过小 |
| 连接数过多 | 连接数过多，内存不足 |
| 大查询 | 大查询消耗过多内存 |
| 内存泄漏 | 内存泄漏 |
| Sort/Join Buffer | 大排序/联接操作占用内存 |

## ⚠️ 应急处置（需确认后执行）

### 终止大查询

> **警告**：终止查询会导致当前事务失败，请在确认后执行！

```python
# 查找并终止大查询
kill_process(client,
    process_ids=["12345"],
    node_id="node-1",
    instance_id="mysql-xxx",
)
```

### 调整 Buffer Pool 大小

> `execute_sql` 仅支持只读操作，无法执行 `SET GLOBAL`。需到**火山引擎控制台 → 参数管理**修改 `innodb_buffer_pool_size`，或通过**实例扩容**增加内存规格。

## 预防措施

1. 正确配置 innodb_buffer_pool_size
2. 设置适当的连接限制
3. 监控内存使用趋势
4. 优化查询以减少内存消耗
5. 设置 OOM 告警
6. 配置 swap 使用告警

## 关联场景

- [慢查询](slow-query.md)
- [临时表溢出](temp-table-overflow.md)
