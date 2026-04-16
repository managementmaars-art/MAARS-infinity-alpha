# CPU 打满故障排查

## 概述

CPU 打满是指 MySQL 实例的 CPU 使用率持续接近或达到 100%，导致数据库响应变慢或完全无响应。这是生产环境中常见的高优先级故障。

## 典型症状

- CPU 使用率持续 100% 或接近 100%
- 数据库响应变慢，查询超时
- 连接堆积，新请求排队等待
- `top` 或监控显示 MySQL 进程 CPU 占用高

> 函数参数详见 [api/ops.md](../../api/ops.md)。

## 排查步骤

### 步骤 0: 获取支持的监控指标（推荐先执行）

> **提示**：在获取具体指标数据之前，建议先调用 `get_metric_items` 查看当前实例支持哪些指标，然后选择合适的指标进行获取。

```python
# 获取当前实例支持的监控指标列表
get_metric_items(client,
)
```

### 步骤 1: 确认 CPU 使用率

```python
import time
now = int(time.time())

# 获取当前 CPU 使用率
get_metric_data(client,
    metric_name="CpuUtil",
    period=60,
    start_time=now - 300,
    end_time=now,
    instance_id="mysql-xxx",
)
```

### 步骤 2: 检查 QPS/TPS 趋势

```python
# 获取 QPS
get_metric_data(client,
    metric_name="QPS",
    period=60,
    start_time=now - 3600,
    end_time=now,
    instance_id="mysql-xxx",
)

# 获取 TPS
get_metric_data(client,
    metric_name="TPS",
    period=60,
    start_time=now - 3600,
    end_time=now,
    instance_id="mysql-xxx",
)
```

### 步骤 3: 识别活跃会话

```python
# 查询当前活跃会话（按执行时间降序）
list_connections(client,
    instance_id="mysql-xxx",
)
```

### 步骤 4: 分析慢查询

```python
# 获取慢查询（按执行时间排序）
describe_slow_logs(client,
    start_time=now - 1800,
    end_time=now,
    order_by="QueryTime",
    sort_by="DESC"
)
```

### 步骤 5: 检查锁等待

```python
# 只查持有锁的事务，快速定位 blocker
describe_trx_and_locks(client,
    instance_id="mysql-xxx",
    search_param={"LockStatus": "LockHold"},
)

# 锁等待分析（查看阻塞链）
describe_lock_wait(client,
    instance_id="mysql-xxx",
)
```

## 常见根因

| 根因 | 说明 |
|-------|-------------|
| 慢查询 | 缺少索引或 SQL 写法问题导致全表扫描 |
| 高并发 | 突发流量激增 |
| 锁竞争 | 行锁等待导致线程堆积 |
| 全表扫描 | 查询未命中索引 |
| IO 瓶颈 | IO 等待导致 CPU 空转 |

## ⚠️ 应急处置（需确认后执行）

### 终止长时间运行的查询

> **警告**：终止进程会导致当前查询失败，请在确认后执行！

```python
# 按条件终止：终止执行时间超过 60 秒的查询
kill_process(client,
    command_type="Query",
    min_time=60,
    instance_id="mysql-xxx",
)

# 精确终止：终止指定进程（从 list_connections 获取 process_id 和 node_id）
kill_process(client,
    process_ids=["12345"],
    node_id="node-1",
    instance_id="mysql-xxx",
)
```

### 调整参数

> `execute_sql` 仅支持只读操作，无法执行 `SET GLOBAL`。需到**火山引擎控制台 → 参数管理**修改 `max_connections` 等参数。

## 预防措施

1. 优化慢查询，添加合适的索引
2. 正确配置连接池
3. 监控 CPU 使用率并设置告警
4. 定期审查 SQL 执行计划
5. 设置查询超时

## 关联场景

- [慢查询](slow-query.md)
- [锁等待](lock-wait.md)
- [会话堆积](session-pileup.md)
