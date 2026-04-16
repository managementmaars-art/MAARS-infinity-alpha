# 主从延迟故障排查

## 概述

主从延迟是指 MySQL 主从复制过程中，从库的复制进度落后于主库，导致读写分离失效、数据不一致等问题。

## 典型症状

- 从库延迟持续增大
- 读写分离读到的数据过期
- `SHOW SLAVE STATUS` 显示 `Seconds_Behind_Master` > 0
- 复制相关报错

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

### 步骤 2: 获取复制指标

```python
# 注意：需通过 get_metric_items 确认该实例是否支持此指标
get_metric_data(client,
    metric_name="SlaveLag",
    period=60,
    start_time=now - 3600,
    end_time=now,
    instance_id="mysql-xxx",
)
```

### 步骤 3: 检查主库 Binlog 状态

```python
# 检查 binary log 位置
execute_sql(client,
    sql="SHOW MASTER STATUS;",
    instance_id="mysql-xxx",
    database="mysql",
)
```

### 步骤 4: 分析从库慢查询

```python
# 检查从库慢查询
describe_slow_logs(client,
    start_time=now - 1800,
    end_time=now,
    order_by="QueryTime",
    sort_by="DESC"
)
```

## 常见根因

| 根因 | 说明 |
|-------|-------------|
| 网络延迟 | 主从网络延迟 |
| 大事务 | 大事务复制时间长 |
| 慢查询 | 从库执行慢查询 |
| IO 瓶颈 | 从库磁盘 IO 瓶颈 |
| Binlog 格式 | Binlog 格式问题 |

## ⚠️ 应急处置（需确认后执行）

### 跳过事务 / 重启从库

> `execute_sql` 仅支持只读操作，无法执行 `SET GLOBAL`、`STOP SLAVE`、`START SLAVE`。
> 需到**火山引擎控制台**操作从库复制管理（跳过事务、重启复制等）。

## 预防措施

1. 使用行格式复制 (ROW)
2. 保持事务简短
3. 优化从库慢查询
4. 确保从库有足够资源
5. 监控复制延迟
6. 使用半同步复制

## 关联场景

- [Binlog 延迟](binlog-delay.md)
- [网络抖动](network-jitter.md)
