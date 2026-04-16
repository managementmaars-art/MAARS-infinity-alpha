# 磁盘空间不足故障排查

## 概述

磁盘空间不足是指 MySQL 实例的磁盘使用率达到 100% 或接近上限，导致无法写入数据、无法创建索引、无法执行 DDL 操作。

## 典型症状

- 磁盘使用率 100% 或接近 100%
- 写入数据报错: `Disk full`
- DDL 操作失败: `Table 'xxx' is full`
- Binlog 无法写入
- InnoDB 无法 checkpoint

> 函数参数详见 [api/ops.md](../../api/ops.md)。

## 排查步骤

### 步骤 0: 获取支持的监控指标（推荐先执行）

> **提示**：在获取具体指标数据之前，建议先调用 `get_metric_items` 查看当前实例支持哪些指标，然后选择合适的指标进行获取。

```python
# 获取当前实例支持的监控指标列表
get_metric_items(client,
)
```

### 步骤 1: 检查磁盘使用率

```python
import time
now = int(time.time())

# 获取磁盘使用率
get_metric_data(client,
    metric_name="DiskUtil",
    period=60,
    start_time=now - 300,
    end_time=now,
    instance_id="mysql-xxx"
)
```

### 步骤 2: 查找大表

```python
# 获取表空间详情（含各表数据量、索引大小）
describe_table_space(client, instance_id="mysql-xxx")
```

### 步骤 3: 分析表空间

```python
# 获取详细表空间信息
describe_table_space(client,
    database="db_name",
    table_name="table_name",
    instance_id="mysql-xxx"
)
```

### 步骤 4: 检查 Binlog 使用情况

```python
# 检查 binlog 使用情况
execute_sql(client,
    sql="SHOW BINARY LOGS;",
    instance_id="mysql-xxx",
    database="mysql",
)

# 检查 binlog 大小
execute_sql(client,
    sql="""
    SELECT
        log_name,
        file_size,
        (SELECT SUM(file_size) FROM mysql.bbinlog_files) AS total_size
    FROM mysql.bbinlog_files
    ORDER BY log_name;
    """,
    instance_id="mysql-xxx",
    database="mysql",
)
```

### 步骤 5: 检查 InnoDB 表空间

```python
# 检查 InnoDB 文件大小
execute_sql(client,
    sql="""
    SELECT
        FILE_NAME,
        TABLESPACE_NAME,
        INITIAL_SIZE,
        TOTAL_EXTENTS * EXTENT_SIZE AS TOTAL_SIZE
    FROM information_schema.FILES
    WHERE FILE_TYPE = 'TABLESPACE';
    """,
    instance_id="mysql-xxx",
    database="information_schema",
)
```

## 常见根因

| 根因 | 说明 |
|-------|-------------|
| 数据增长 | 数据快速增长，未及时清理 |
| Binlog 累积 | Binlog 未清理，磁盘占满 |
| 临时表 | 临时表/排序文件占用空间 |
| Undo/Redo | Undo/Redo 日志过大 |
| 慢查询 | 大排序操作产生临时文件 |

## 修复建议（排查后必须给出）

排查完成后，**必须**向用户提供至少 2 条可操作的修复建议，从以下常见方案中选择：

1. **清理/归档旧数据** — 对占空间最大的表，归档或删除历史数据（通过 DML 工单）
2. **OPTIMIZE TABLE** — 对碎片率高的表执行 `OPTIMIZE TABLE` 回收空间（通过 DDL 工单）
3. **扩容存储** — 在火山引擎控制台调整实例磁盘规格（适用于数据持续增长的场景）
4. **清理 Binlog** — 清理过期的 Binlog 日志
5. **删除未使用的索引** — 减少不必要的索引占用

## ⚠️ 应急处置（需确认后执行）

### 清理 Binlog

> `execute_sql` 仅支持只读操作，无法执行 `PURGE BINARY LOGS`。需到**火山引擎控制台 → 日志管理**清理 Binlog。

### 删除旧数据

> 数据变更须通过 DML 工单执行。

```python
# 通过 DML 工单归档或删除旧数据
create_dml_sql_change_ticket(client,
    sql_text="DELETE FROM logs WHERE created_at < '2023-01-01';",
    instance_id="mysql-xxx",
    database="db_name",
)
```

### 删除未使用的索引

先查找未使用的索引，再通过 DDL 工单删除：

```python
# 查找未使用的索引（只读查询）
execute_sql(client,
    sql="""
    SELECT
        OBJECT_SCHEMA,
        OBJECT_NAME,
        INDEX_NAME
    FROM performance_schema.table_io_waits_summary_by_index_usage
    WHERE INDEX_NAME IS NOT NULL
    AND COUNT_STAR = 0
    AND OBJECT_SCHEMA != 'mysql';
    """,
    instance_id="mysql-xxx",
    database="performance_schema",
)

# 确认后通过 DDL 工单删除
create_ddl_sql_change_ticket(client,
    sql_text="DROP INDEX idx_name ON table_name;",
    instance_id="mysql-xxx",
    database="db_name",
)
```

## 预防措施

1. 设置磁盘使用率监控和告警
2. 实施数据归档和清理策略
3. 配置 binlog 过期（binlog_expire_logs_seconds）
4. 定期表优化（OPTIMIZE TABLE 回收碎片空间）
5. 监控临时表使用情况
6. 评估是否需要扩容存储（在火山引擎控制台调整实例磁盘规格）
7. 设置空间使用预测

## 关联场景

- [临时表溢出](temp-table-overflow.md)
- [Binlog 延迟](binlog-delay.md)
