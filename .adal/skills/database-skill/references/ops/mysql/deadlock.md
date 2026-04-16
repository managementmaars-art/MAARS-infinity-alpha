# 死锁故障排查

## 概述

死锁是指两个或多个事务相互持有对方需要的锁，导致所有事务都无法继续执行。MySQL 会自动检测并回滚其中一个事务，但会造成业务报错。

## 典型症状

- 应用报错: `Deadlock found when trying to get lock`
- 事务回滚
- 特定业务操作失败
- 死锁错误日志

> 函数参数详见 [api/ops.md](../../api/ops.md)。

## 排查步骤

### 步骤 1: 分析死锁

```python
# 触发死锁分析，返回死锁详情
describe_deadlock(client,
    instance_id="mysql-xxx",
)
```

### 步骤 2: 分析当前持锁事务

```python
# 查看当前持有锁的事务，确认是否仍有异常事务
describe_trx_and_locks(client,
    instance_id="mysql-xxx",
    search_param={"LockStatus": "LockHold"},
)
```

## 常见根因

| 根因 | 说明 |
|-------|-------------|
| 乱序访问 | 不同事务以不同顺序访问资源 |
| 长事务 | 事务过长，持有锁时间久 |
| 批量更新 | 批量更新相同范围数据 |
| 缺少索引 | 缺少索引导致锁范围扩大 |
| 高并发 | 并发更新同一行数据 |

## ⚠️ 应急处置（需确认后执行）

### 终止阻塞事务

> **警告**：终止事务会导致当前事务失败，请在确认后执行！

```python
# 终止指定事务
kill_process(client,
    process_ids=["12345"],
    node_id="node-1",
    instance_id="mysql-xxx",
)
```

### 调整事务隔离级别

> `execute_sql` 仅支持只读操作，无法执行 `SET GLOBAL`。如需将隔离级别改为 `READ-COMMITTED`，需到**火山引擎控制台 → 参数管理**修改 `transaction_isolation`。

## 预防措施

1. 按一致顺序访问表
2. 保持事务简短
3. 添加适当索引以缩小锁范围
4. 适当情况下使用较低隔离级别
5. 避免在高峰期进行批量更新
6. 监控死锁日志并优化问题查询

## 关联场景

- [锁等待](lock-wait.md)
- [慢查询](slow-query.md)
