# IO 瓶颈故障排查

## 概述

IO 瓶颈是指磁盘 IOPS 或吞吐量达到上限，导致数据库请求等待 IO 完成，表现为 IO 使用率高、IO 等待时间长的现象。

## 典型症状

- IOPS 达到上限
- IO 使用率 100%
- 磁盘响应时间变长
- 查询执行时间变长
- `iostat` 显示 high await

> 函数参数详见 [api/ops.md](../../api/ops.md)。

## 排查步骤

### 步骤 0: 获取支持的监控指标（推荐先执行）

> **提示**：在获取具体指标数据之前，建议先调用 `get_metric_items` 查看当前实例支持哪些指标，然后选择合适的指标进行获取。

```python
# 获取当前实例支持的监控指标列表
get_metric_items(client,
)
```

### 步骤 1: 检查 IOPS 使用情况

```python
import time
now = int(time.time())

# 获取 InnoDB 读 IO 次数（注意：无直接 IOPS 指标，此指标覆盖 InnoDB 读 IO 计数）
get_metric_data(client,
    metric_name="InnodbDataReadCounts",
    period=60,
    start_time=now - 300,
    end_time=now,
    instance_id="mysql-xxx",
)

# 获取 InnoDB 读数据字节数（注意：无直接 DiskThroughput 指标，此指标覆盖 InnoDB 读数据吞吐）
get_metric_data(client,
    metric_name="InnodbDataReadBytes",
    period=60,
    start_time=now - 300,
    end_time=now,
    instance_id="mysql-xxx",
)
```

### 步骤 2: 检查磁盘使用率

```python
# 获取磁盘使用率
get_metric_data(client,
    metric_name="DiskUtil",
    period=60,
    start_time=now - 300,
    end_time=now,
    instance_id="mysql-xxx",
)
```

### 步骤 3: 检查 InnoDB IO 统计

```python
# 获取 InnoDB IO 统计
execute_sql(client,
    sql="SHOW ENGINE INNODB STATUS;",
    instance_id="mysql-xxx",
    database="performance_schema",
)
```

## 常见根因

| 根因 | 说明 |
|-------|-------------|
| 高并发 | 并发请求过多，IO 密集 |
| 大表扫描 | 大表扫描频繁 |
| 存储性能不足 | 磁盘性能不足 |
| 随机写入 | 随机写入过多 |
| Binlog 写入 | Binlog 写入频繁 |

## ⚠️ 应急处置（需确认后执行）

### 调整 IO 相关参数

> `execute_sql` 仅支持只读操作，无法执行 `SET GLOBAL`。如需调整以下参数，需到**火山引擎控制台 → 参数管理**修改：
> - `innodb_flush_log_at_trx_commit`（改为 2 可提升性能但降低持久性）
> - `sync_binlog`（改为 0 可减少 IO 但降低数据安全性）

## 预防措施

1. 使用 SSD 或高性能存储
2. 优化查询以减少 IO
3. 正确索引以减少随机 IO
4. 分离数据和日志文件
5. 监控 IO 指标并设置告警
6. 使用读写分离

## 关联场景

- [慢查询](slow-query.md)
- [磁盘空间不足](disk-full.md)
