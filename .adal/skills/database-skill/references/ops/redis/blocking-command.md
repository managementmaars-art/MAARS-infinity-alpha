# 阻塞命令故障排查

## 概述

阻塞命令是指 Redis 中某些命令会长时间阻塞主线程，如 `KEYS`、`FLUSHDB`、`FLUSHALL`、`SORT` 等，导致其他命令无法执行。

## 典型症状

- 命令执行超时
- 其他命令响应变慢
- 主线程被阻塞
- 客户端超时

> 函数参数详见 [api/metadata-query.md](../../api/metadata-query.md)。

## 排查步骤

### 步骤 1: 检查阻塞客户端

```python
# 获取阻塞客户端
execute_sql(client,
    sql="CLIENT LIST;", instance_id="redis-xxx", database="0"
)
```

## 常见根因

| 根因 | 说明 |
|-------|-------------|
| KEYS 命令 | keys 命令遍历全量 key |
| FLUSHDB/FLUSHALL | 清空数据库 |
| SORT | 排序操作 |
| HGETALL | 获取大 hash |
| SMEMBERS | 获取大 set |

## ⚠️ 应急处置（需确认后执行）

### 终止阻塞客户端

> **警告**：终止客户端会导致当前任务失败，请在确认后执行！

```python
# 终止指定客户端
execute_sql(client,
    sql="CLIENT KILL ID <id>;", instance_id="redis-xxx", database="0"
)
```

## 预防措施

1. 避免 KEYS 命令，使用 SCAN 代替
2. 使用 pipeline 批量操作
3. 设置适当的客户端超时
4. 避免在高峰期进行阻塞操作
5. 谨慎使用 Lua 脚本
6. 监控慢命令

## 关联场景

- [慢查询](slow-query.md)
- [CPU 打满](cpu-spike.md)
