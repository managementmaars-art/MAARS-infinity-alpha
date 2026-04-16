# 磁盘空间不足故障排查

## 概述

磁盘空间不足是指 PostgreSQL 实例的磁盘使用率达到 100% 或接近上限，导致无法写入数据、无法创建索引、WAL 无法写入。

## 典型症状

- 磁盘使用率 100% 或接近 100%
- 写入数据报错
- DDL 操作失败
- WAL 无法写入

> 函数参数详见 [api/ops.md](../../api/ops.md) 和 [api/metadata-query.md](../../api/metadata-query.md)。

## 排查步骤

### 步骤 1: 检查磁盘使用率及健康状态

```python
import time
now = int(time.time())

# 获取最近一小时健康概览（含内存使用率、连接数使用率等，可间接了解整体负载）
describe_health_summary(client,
    end_time=now,
    instance_id="pg-xxx",
)
```

### 步骤 2: 查找大表

```python
# 获取表空间详情（含各表数据量、索引大小）
describe_table_space(client, instance_id="pg-xxx")
```

### 步骤 3: 检查 WAL 使用情况

```python
# 检查 WAL 目录大小
execute_sql(client,
    instance_id="pg-xxx",
    sql="""
    SELECT
        pg_current_wal_lsn(),
        pg_walfile_name(pg_current_wal_lsn()),
        pg_wal_lsn_diff(pg_current_wal_lsn(), '0/0') AS wal_used;
    """, database="postgres"
)
```

## 常见根因

| 根因 | 说明 |
|-------|-------------|
| 数据增长 | 数据快速增长，未及时清理 |
| WAL 累积 | WAL 日志积压 |
| 索引膨胀 | 索引膨胀 |
| 临时表 | 临时表占用空间 |
| VACUUM 未完成 | VACUUM 未完成 |

## ⚠️ 应急处置（需确认后执行）

### 回收空间

> `execute_sql` 仅支持只读操作，`VACUUM` 须通过 DDL 工单执行。

```python
# 通过 DDL 工单执行 VACUUM
create_ddl_sql_change_ticket(client,
    sql_text="VACUUM (VERBOSE, ANALYZE) table_name;",
    instance_id="pg-xxx",
    database="db_name",
)
```

### 删除旧数据

> 数据变更须通过 DML 工单执行。

```python
# 通过 DML 工单归档或删除旧数据
create_dml_sql_change_ticket(client,
    sql_text="DELETE FROM logs WHERE created_at < '2023-01-01';",
    instance_id="pg-xxx",
    database="db_name",
)
```

## 预防措施

1. 设置磁盘使用率监控和告警
2. 实施数据归档和清理策略
3. 定期 VACUUM（启用 AUTOVACUUM）
4. 监控 WAL 增长
5. 使用表分区
6. 评估是否需要扩容存储（在火山引擎控制台调整实例磁盘规格）
7. 设置空间使用预测

## 关联场景

- [WAL 积压](wal-backlog.md)
- [VACUUM 阻塞](vacuum-blocking.md)
