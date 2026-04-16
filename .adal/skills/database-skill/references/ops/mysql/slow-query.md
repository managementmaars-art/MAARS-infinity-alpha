# 慢查询故障排查

## 概述

慢查询是指执行时间超过 `long_query_time` 阈值的 SQL 语句，可能是由于缺少索引、SQL 写法问题、数据量过大等原因导致。

## 典型症状

- 查询响应时间变长
- 慢查询日志增加
- 监控显示 QueryTime 增大
- 特定页面加载变慢

> 函数参数详见 [api/ops.md](../../api/ops.md)。

## 排查步骤

### 步骤 1: 获取慢查询趋势图

```python
import time
now = int(time.time())

# 获取慢查询时间序列趋势（了解慢查询随时间的变化）
describe_slow_log_time_series_stats(client,
    start_time=now - 3600,
    end_time=now,
    instance_id="mysql-xxx",
    interval=300
)
```

### 步骤 2: 获取慢查询聚合统计

```python
# 获取慢查询聚合统计（按 SQL 模板聚合，找出最耗时的 SQL 类型）
describe_aggregate_slow_logs(client,
    start_time=now - 3600,
    end_time=now,
    instance_id="mysql-xxx",
    order_by="TotalQueryTime",
    sort_by="DESC"
)
```

### 步骤 3: 获取慢查询明细

```python
# 获取慢查询明细（查看具体哪些 SQL 最慢）
describe_slow_logs(client,
    start_time=now - 3600,
    end_time=now,
    order_by="QueryTime",
    sort_by="DESC"
)
```

### 步骤 4: 获取完整 SQL 历史

```python
# 获取完整 SQL 历史详情（包含执行计划等详细信息）
describe_full_sql_detail(client,
    start_time=now - 3600,
    end_time=now,
    instance_id="mysql-xxx",
    page_size=20
)
```

## 常见根因

| 根因 | 说明 |
|-------|-------------|
| 缺少索引 | 缺少索引导致全表扫描 |
| 索引错误 | 使用了错误的索引 |
| 大表扫描 | 数据量大，扫描行数多 |
| 复杂 JOIN | 多表 JOIN 复杂 |
| 统计信息过期 | 表统计信息过期 |

## ⚠️ 应急处置（需确认后执行）

### 终止长时间运行的查询

> **警告**：终止查询会导致当前事务失败，请在确认后执行！

```python
# 终止指定查询（请先确认要终止的 session_id）
# 需要您确认后才能执行
kill_process(client,
    process_ids=["12345"],
    node_id="node-1"
)
```

### 添加索引

> `execute_sql` 仅支持只读操作，DDL 变更须通过工单执行。

```python
# 通过 DDL 工单添加索引（请先确认表名和字段）
create_ddl_sql_change_ticket(client,
    sql_text="ALTER TABLE table_name ADD INDEX idx_column (column);",
    instance_id="mysql-xxx",
    database="db_name",
)
```

## 预防措施

1. 定期审查慢查询日志
2. 根据查询模式添加适当索引
3. 保持表统计信息更新（ANALYZE TABLE）
4. 使用查询分析工具
5. 设置慢查询告警
6. 优化应用 SQL 模式

## 关联场景

- [锁等待](lock-wait.md)
- [CPU 打满](cpu-spike.md)
- [IO 瓶颈](io-bottleneck.md)
