# 网络抖动故障排查

## 概述

网络抖动是指网络延迟不稳定或丢包，导致数据库连接超时、响应时间波动、数据传输中断等问题。

## 典型症状

- 连接超时错误
- 响应时间波动大
- 连接断开重连
- 网络延迟监控显示抖动

> 函数参数详见 [api/ops.md](../../api/ops.md)。

## 排查步骤

### 步骤 0: 获取支持的监控指标（推荐先执行）

> **提示**：在获取具体指标数据之前，建议先调用 `get_metric_items` 查看当前实例支持哪些指标，然后选择合适的指标进行获取。

```python
# 获取当前实例支持的监控指标列表
get_metric_items(client,
)
```

### 步骤 1: 检查网络指标

```python
import time
now = int(time.time())

# 获取网络流量
get_metric_data(client,
    metric_name="NetworkReceiveThroughput",
    period=60,
    start_time=now - 300,
    end_time=now,
    instance_id="mysql-xxx",
)

get_metric_data(client,
    metric_name="NetworkTransmitThroughput",
    period=60,
    start_time=now - 300,
    end_time=now,
    instance_id="mysql-xxx",
)
```

### 步骤 2: 检查连接错误

```python
# 检查连接错误
execute_sql(client,
    sql="SHOW GLOBAL STATUS LIKE 'Aborted%';",
    instance_id="mysql-xxx",
    database="performance_schema",
)

# 检查连接统计
execute_sql(client,
    sql="SHOW GLOBAL STATUS LIKE 'Connection%';",
    instance_id="mysql-xxx",
    database="performance_schema",
)
```

### 步骤 3: 检查异常状态连接

```python
# 查询活跃会话，从返回结果中筛选异常状态（Timeout/Disconnect 等）
list_connections(client,
    show_sleep=True,
    instance_id="mysql-xxx",
)
```

## 常见根因

| 根因 | 说明 |
|-------|-------------|
| 网络拥塞 | 网络拥塞 |
| 硬件问题 | 网卡/交换机故障 |
| DNS 问题 | DNS 解析问题 |
| 防火墙 | 防火墙规则变化 |
| 高延迟 | 网络延迟高 |

## ⚠️ 应急处置（需确认后执行）

### 调整超时参数

> `execute_sql` 仅支持只读操作，无法执行 `SET GLOBAL`。需到**火山引擎控制台 → 参数管理**修改 `connect_timeout`、`wait_timeout` 等参数。

### 使用 IP 而非主机名

建议应用连接字符串使用 IP 地址而非主机名，避免 DNS 解析延迟。

## 预防措施

1. 使用稳定的网络基础设施
2. 监控网络指标
3. 设置适当的超时值
4. 使用连接池
5. 在应用中实现重试逻辑
6. 设置网络告警

## 关联场景

- [主从延迟](replication-delay.md)
