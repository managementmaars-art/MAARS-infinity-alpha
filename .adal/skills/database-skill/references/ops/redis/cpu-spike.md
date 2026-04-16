# CPU 打满故障排查

## 概述

CPU 打满是指 Redis 实例的 CPU 使用率持续接近或达到 100%，导致响应变慢或完全无响应。Redis 是单线程模型，CPU 打满通常意味着某个命令消耗过多 CPU。

## 典型症状

- CPU 使用率持续 100% 或接近 100%
- 命令响应变慢
- 客户端超时
- 请求堆积

> 函数参数详见 [api/metadata-query.md](../../api/metadata-query.md)。

## 排查步骤

### 步骤 1: 检查 CPU 使用情况

> **注意**：Redis 不支持 `get_metric_items/get_metric_data`，通过 `execute_sql` 使用 Redis 原生命令获取 CPU 信息。

```python
# 获取 CPU 使用信息
execute_sql(client,
    sql="INFO cpu;", instance_id="redis-xxx", database="0"
)
```

### 步骤 2: 获取命令统计

```python
# 获取命令统计
execute_sql(client,
    sql="INFO commandstats;", instance_id="redis-xxx", database="0"
)
```

## 常见根因

| 根因 | 说明 |
|-------|-------------|
| KEYS/SCAN | 遍历全量 key |
| SORT | 排序操作 |
| 大 Set 操作 | 大 set 的交集/并集 |
| Lua Script | 复杂 Lua 脚本 |
| HGETALL | 获取大 hash |

## ⚠️ 应急处置（需确认后执行）

### 终止高 CPU 客户端

> **警告**：终止客户端会导致当前任务失败，请在确认后执行！

```python
# 终止指定客户端
execute_sql(client,
    sql="CLIENT KILL ID <id>;", instance_id="redis-xxx", database="0"
)
```

## 预防措施

1. 避免 KEYS 命令，使用 SCAN 代替
2. 使用适当的数据结构
3. 设置命令超时
4. 监控慢命令
5. 使用 pipeline 批量操作
6. 设置 CPU 使用告警

## 关联场景

- [慢查询](slow-query.md)
- [阻塞命令](blocking-command.md)
