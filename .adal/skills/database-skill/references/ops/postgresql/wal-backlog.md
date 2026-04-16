# WAL 积压故障排查

## 概述

WAL 积压是指 Write-Ahead Logging (WAL) 写入速度跟不上产生速度，导致 WAL 目录空间增长、复制延迟等问题。

## 典型症状

- WAL 目录空间持续增长
- 复制延迟增大
- Checkpoint 耗时增加
- 写入性能下降

> 函数参数详见 [api/ops.md](../../api/ops.md) 和 [api/metadata-query.md](../../api/metadata-query.md)。

## 排查步骤

### 步骤 1: 检查 WAL 使用情况

```python
# 检查 WAL 使用情况
execute_sql(client,
    instance_id="pg-xxx",
    sql="""
    SELECT
        pg_current_wal_lsn(),
        pg_walfile_name(pg_current_wal_lsn()),
        pg_wal_lsn_diff(pg_current_wal_lsn(), '0/0') AS wal_used_bytes;
    """, database="postgres"
)
```

### 步骤 2: 检查 WAL 统计

```python
# 获取 WAL 统计
execute_sql(client,
    instance_id="pg-xxx",
    sql="""
    SELECT
        buffers_checkpoint * 8192 AS checkpoint_bytes,
        buffers_backend * 8192 AS backend_bytes
    FROM pg_stat_database
    WHERE datname = current_database();
    """, database="postgres"
)
```

## 常见根因

| 根因 | 说明 |
|-------|-------------|
| 高写入负载 | 写入负载过高 |
| Checkpoint 间隔过长 | Checkpoint 间隔过长 |
| 归档失败 | 归档失败 |
| 磁盘 IO 慢 | 磁盘 IO 慢 |
| 复制延迟 | 从库延迟 |

## ⚠️ 应急处置（需确认后执行）

### 强制 Checkpoint

> **警告**：强制 checkpoint 可能影响业务，请在确认后执行！

```python
# 强制 checkpoint
execute_sql(client,
    instance_id="pg-xxx",
    sql="SELECT pg_checkpoint();", database="postgres"
)
```

### 终止长时间运行的事务

> **警告**：终止进程会导致当前事务失败，请在确认后执行！

```python
kill_process(client,
    process_ids=["12345"],
    node_id="node-1",
    instance_id="pg-xxx",
)
```

## 预防措施

1. 调优 checkpoint 参数
2. 使用适当的 wal_level
3. 确保归档正常工作
4. 监控 WAL 增长
5. 谨慎使用复制槽
6. 监控磁盘 IO 性能

## 关联场景

- [磁盘空间不足](disk-full.md)
- [复制延迟](replication-delay.md)
