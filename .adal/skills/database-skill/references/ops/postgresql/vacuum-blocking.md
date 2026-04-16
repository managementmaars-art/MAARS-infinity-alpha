# VACUUM 阻塞故障排查

## 概述

VACUUM 阻塞是指 VACUUM 或 ANALYZE 操作在执行过程中被阻塞，或者阻塞了其他操作。VACUUM 用于回收死元组占用的空间。

## 典型症状

- VACUUM 操作执行时间长
- 表被锁定，无法进行 DML 操作
- `pg_stat_progress_vacuum` 显示进度
- 磁盘空间未回收

> 函数参数详见 [api/ops.md](../../api/ops.md) 和 [api/metadata-query.md](../../api/metadata-query.md)。

## 排查步骤

### 步骤 1: 检查 VACUUM 进度

```python
# 检查运行中的 VACUUM
execute_sql(client,
    instance_id="pg-xxx",
    sql="""
    SELECT
        pid,
        datname,
        relname,
        phase,
        heap_blks_total,
        heap_blks_scanned
    FROM pg_stat_progress_vacuum;
    """, database="postgres"
)
```

### 步骤 2: 检查表膨胀

```python
# 检查表膨胀
execute_sql(client,
    instance_id="pg-xxx",
    sql="""
    SELECT
        schemaname,
        tablename,
        n_dead_tup,
        last_vacuum,
        last_autovacuum
    FROM pg_stat_user_tables
    WHERE n_dead_tup > 10000
    ORDER BY n_dead_tup DESC;
    """, database="postgres"
)
```

## 常见根因

| 根因 | 说明 |
|-------|-------------|
| 长事务 | 长事务阻止 VACUUM |
| 活跃 DML | 表上有活跃的 DML 操作 |
| 大表 | 表太大，VACUUM 时间长 |
| 资源竞争 | 资源竞争 |

## ⚠️ 应急处置（需确认后执行）

### 取消 VACUUM

> **警告**：取消 VACUUM 可能导致空间无法回收，请在确认后执行！

```python
# 终止 VACUUM 进程
kill_process(client,
    process_ids=["12345"],
    node_id="node-1",
    instance_id="pg-xxx",
)
```

### 手动运行 VACUUM

> **警告**：VACUUM 会锁定表，请在确认后执行！

```python
# 回收空间
execute_sql(client,
    instance_id="pg-xxx",
    sql="VACUUM (VERBOSE, ANALYZE) table_name;", database="postgres"
)
```

## 预防措施

1. 启用并调优 autovacuum
2. 保持事务简短
3. 监控表膨胀
4. 在低峰期安排 VACUUM
5. 谨慎使用 VACUUM FULL
6. 监控 VACUUM 进度

## 关联场景

- [锁等待](lock-wait.md)
- [磁盘空间不足](disk-full.md)
