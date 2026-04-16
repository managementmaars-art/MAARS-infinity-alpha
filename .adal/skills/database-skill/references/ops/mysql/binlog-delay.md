# Binlog 延迟故障排查

## 概述

Binlog 延迟是指主库产生的二进制日志（Binlog）未及时传输到从库或从库未及时应用，导致主从数据不一致、复制延迟。

## 典型症状

- 从库延迟增大
- `SHOW SLAVE STATUS` 显示 `Seconds_Behind_Master` > 0
- Binlog 积压
- 复制链路延迟

> 函数参数详见 [api/ops.md](../../api/ops.md)。

## 排查步骤

### 步骤 0: 获取支持的监控指标（推荐先执行）

> **提示**：在获取具体指标数据之前，建议先调用 `get_metric_items` 查看当前实例支持哪些指标，然后选择合适的指标进行获取。

```python
# 获取当前实例支持的监控指标列表
get_metric_items(client,
)
```

### 步骤 1: 检查复制状态

```python
# 检查从库状态
execute_sql(client,
    sql="SHOW SLAVE STATUS\G",
    instance_id="mysql-xxx",
    database="mysql",
)
```

### 步骤 2: 检查 Binary Log 状态

```python
# 获取 binary log 信息
execute_sql(client,
    sql="SHOW MASTER STATUS;",
    instance_id="mysql-xxx",
    database="mysql",
)
execute_sql(client,
    sql="SHOW BINARY LOGS;",
    instance_id="mysql-xxx",
    database="mysql",
)
```

### 步骤 3: 检查 Binlog 增长速度

```python
import time
now = int(time.time())

# 注意：需通过 get_metric_items 确认该实例是否支持此指标
get_metric_data(client,
    metric_name="BinlogSize",
    period=300,
    start_time=now - 86400,
    end_time=now,
    instance_id="mysql-xxx",
)
```

## 常见根因

| 根因 | 说明 |
|-------|-------------|
| 大事务 | 大事务导致 binlog 传输慢 |
| 网络延迟 | 主从网络延迟 |
| 磁盘 IO 慢 | 从库磁盘 IO 慢 |
| 从库负载 | 从库负载过高 |
| Binlog 格式 | Binlog 格式问题 |

## ⚠️ 应急处置（需确认后执行）

### 清理 Binlog / 跳过事件 / 重启复制

> `execute_sql` 仅支持只读操作，无法执行 `PURGE BINARY LOGS`、`SET GLOBAL`、`STOP/START SLAVE`。
> 需到**火山引擎控制台**操作：
> - 清理 Binlog：控制台 → 日志管理
> - 跳过事件 / 重启复制：控制台 → 复制管理

## 预防措施

1. 使用 ROW 格式进行复制
2. 保持事务简短
3. 确保从库有足够资源
4. 监控 binlog 增长速度
5. 使用半同步复制
6. 设置复制延迟监控告警

## 关联场景

- [磁盘空间不足](disk-full.md)
- [主从延迟](replication-delay.md)
