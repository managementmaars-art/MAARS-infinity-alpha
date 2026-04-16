# 复制延迟故障排查

## 概述

复制延迟是指 Redis 主从复制过程中，从节点的复制进度落后于主节点，导致读写分离失效、数据不一致等问题。

## 典型症状

- 从节点延迟持续增大
- 读写分离读到的数据过期
- `INFO replication` 显示 `master_link_status` 为 down
- 复制相关报错

> 函数参数详见 [api/metadata-query.md](../../api/metadata-query.md)。

## 排查步骤

### 步骤 1: 检查复制状态

```python
# 获取复制信息
execute_sql(client,
    sql="INFO replication;", instance_id="redis-xxx", database="0"
)
```

### 步骤 2: 检查主从连接状态

```python
# 获取主从连接状态
execute_sql(client,
    sql="""
    INFO replication | grep -E "master_link_status|master_repl_offset|second_repl_offset"
    """, instance_id="redis-xxx", database="0"
)
```

## 常见根因

| 根因 | 说明 |
|-------|-------------|
| 网络延迟 | 主从网络延迟 |
| 大操作 | 大 key 复制时间长 |
| 慢命令 | 从节点执行慢命令 |
| 磁盘 IO 瓶颈 | 从节点磁盘 IO 瓶颈 |

## 预防措施

1. 确保主从网络良好
2. 保持 key 大小合理
3. 优化从节点慢命令
4. 确保从节点有足够资源
5. 监控复制延迟
6. 使用适当的副本数量

## 关联场景

- [集群故障](cluster-failure.md)
