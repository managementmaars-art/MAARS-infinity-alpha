# 锁等待故障排查

## 概述

锁等待是指事务由于无法获取所需的锁而处于等待状态，可能是由于行锁等待、表锁等待或元数据锁等待导致。

## 典型症状

- 查询执行变慢
- 特定操作被阻塞
- 锁等待时间增长
- `pg_stat_activity` 显示很多进程在等待

> 函数参数详见 [api/ops.md](../../api/ops.md)。

## 排查步骤

### 步骤 1: 定位持锁事务（核心步骤）

```python
# 只查持有锁的事务，快速定位 blocker
describe_trx_and_locks(client,
    instance_id="pg-xxx",
    search_param={"LockStatus": "LockHold"},
)
```

关注 `trx_exec_time`（运行时长）、`trx_rows_locked`（锁定行数）、`lock_summary`（锁类型分布）。

### 步骤 2: 分析锁等待链

```python
# 查看完整锁等待关系（阻塞方 b_ 和等待方 r_）
describe_lock_wait(client,
    instance_id="pg-xxx",
)
```

## 常见根因

| 根因 | 说明 |
|-------|-------------|
| 长事务 | 事务过长，持有锁久 |
| 乱序访问 | 不同事务以不同顺序访问 |
| 缺少索引 | 缺少索引导致锁范围大 |
| DDL 操作 | ALTER/CREATE 等 DDL 操作 |

## ⚠️ 应急处置（需确认后执行）

### 终止阻塞事务

> **警告**：终止进程会导致当前事务失败，请在确认后执行！

```python
# 终止阻塞进程（从排查步骤获取 blocking_pid）
kill_process(client,
    process_ids=["12345"],
    node_id="node-1",
    instance_id="pg-xxx",
)
```

## 预防措施

1. 保持事务简短
2. 按一致顺序访问数据
3. 添加适当索引
4. 避免在高峰期进行长时间 DDL
5. 监控锁等待时间
6. 使用适当的锁模式

## 关联场景

- [慢查询](slow-query.md)
- [VACUUM 阻塞](vacuum-blocking.md)
