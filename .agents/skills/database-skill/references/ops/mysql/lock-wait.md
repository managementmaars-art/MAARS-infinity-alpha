# 锁等待故障排查

## 概述

锁等待是指事务由于无法获取所需的锁而处于等待状态，可能是由于行锁等待、表锁等待或元数据锁等待导致。

**诊断原则：被阻塞的 SQL 是受害者，不是根因。** 排查锁等待时，优先找到持锁事务（blocker），而不是分析被阻塞的 SQL 本身。

## 典型症状

- 查询执行变慢
- 特定操作被阻塞
- 锁等待时间增长
- `SHOW PROCESSLIST` 显示很多 State 为 "Waiting for ..."

> 函数参数详见 [api/ops.md](../../api/ops.md)。

## 排查步骤

### 步骤 1: 定位持锁事务（核心步骤）

```python
# 只查持有锁的事务，快速定位 blocker
describe_trx_and_locks(client,
    instance_id="mysql-xxx",
    search_param={"LockStatus": "LockHold"},
)
```

从结果中重点关注：`trx_id`、`process_id`、`trx_exec_time`（运行时长）、`trx_rows_locked`（锁定行数）、`lock_summary`（锁类型分布）。

### 步骤 2: 分析锁等待链

```python
# 查看完整锁等待关系（阻塞方 b_ 和等待方 r_）
describe_lock_wait(client,
    instance_id="mysql-xxx",
)
```

关注 `b_trx_id`（阻塞方）和 `r_trx_id`（等待方）的对应关系、`b_blocking_wait_secs`（阻塞时长）。

## 常见根因

| 根因 | 说明 |
|-------|-------------|
| 长事务 | 事务过长，持有锁久 |
| 乱序访问 | 不同事务以不同顺序访问 |
| 缺少索引 | 缺少索引导致锁范围大 |
| DDL 操作 | ALTER/CREATE 等 DDL 操作 |
| 批量更新 | 批量更新同一范围数据 |

## ⚠️ 应急处置（需确认后执行）

### 终止阻塞事务

> **警告**：终止事务会导致当前事务失败，请在确认后执行！

```python
# 终止阻塞进程
kill_process(client,
    process_ids=["12345"],
    node_id="node-1",
    instance_id="mysql-xxx",
)
```

### 调整事务隔离级别

> `execute_sql` 仅支持只读操作，无法执行 `SET GLOBAL`。如需将隔离级别改为 `READ-COMMITTED`，需到**火山引擎控制台 → 参数管理**修改 `transaction_isolation`。

## 预防措施

1. 保持事务简短
2. 按一致顺序访问数据
3. 添加适当索引
4. 避免在高峰期进行长时间 DDL
5. 监控锁等待时间
6. 使用适当的隔离级别

## 关联场景

- [死锁](deadlock.md)
- [慢查询](slow-query.md)
- [会话堆积](session-pileup.md)
