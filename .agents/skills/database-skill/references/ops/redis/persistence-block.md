# 持久化阻塞故障排查

## 概述

持久化阻塞是指 Redis 在执行 RDB 快照或 AOF 重写时阻塞主线程，导致读写性能下降。这是 Redis 持久化机制的常见问题。

## 典型症状

- 写入操作变慢
- 主线程被阻塞
- `BGSAVE` 或 `BGREWRITEAOF` 执行时间长
- 延迟增加

> 函数参数详见 [api/metadata-query.md](../../api/metadata-query.md)。

## 排查步骤

### 步骤 1: 检查持久化状态

```python
# 检查持久化状态
execute_sql(client,
    sql="INFO persistence;", instance_id="redis-xxx", database="0"
)
```

### 步骤 2: 检查最后保存时间

```python
# 获取最后保存时间
execute_sql(client,
    sql="LASTSAVE;", instance_id="redis-xxx", database="0"
)
```

## 常见根因

| 根因 | 说明 |
|-------|-------------|
| 大数据集 | 数据集过大，RDB 耗时 |
| AOF 重写 | AOF 重写阻塞 |
| Fork 超时 | fork 超时 |
| 磁盘 IO | 磁盘 IO 瓶颈 |

## ⚠️ 应急处置（需确认后执行）

### 使用 AOF Everysec

> **警告**：修改参数可能影响数据安全，请在确认后执行！

```python
# 使用 everysec 代替 always
execute_sql(client,
    sql="CONFIG SET appendfsync everysec;", instance_id="redis-xxx", database="0"
)
```

## 预防措施

1. 使用 AOF 代替 RDB 进行持久化
2. 配置适当的保存点
3. 使用 AOF 重写配合 appendfsync everysec
4. 谨慎使用 copy-on-write (COW)
5. 监控 fork 时间
6. 使用复制减少持久化负载

## 关联场景

- [内存打满](memory-full.md)
- [CPU 打满](cpu-spike.md)
