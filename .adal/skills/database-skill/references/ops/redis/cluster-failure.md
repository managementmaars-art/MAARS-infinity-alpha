# 集群故障故障排查

## 概述

集群故障是指 Redis 集群（Cluster）中的某个节点出现问题，如主节点宕机、从节点故障、slot 分配不均，导致整个集群或部分数据不可用。

## 典型症状

- 部分 key 无法访问
- 读写操作报错
- 集群状态异常
- 某个主节点不可用
- MOVED 错误增多

> 函数参数详见 [api/metadata-query.md](../../api/metadata-query.md)。

## 排查步骤

### 步骤 1: 检查集群状态

```python
# 获取集群信息
execute_sql(client,
    sql="CLUSTER INFO;", instance_id="redis-xxx", database="0"
)
```

### 步骤 2: 检查集群节点

```python
# 获取集群节点
execute_sql(client,
    sql="CLUSTER NODES;", instance_id="redis-xxx", database="0"
)
```

## 常见根因

| 根因 | 说明 |
|-------|-------------|
| 节点宕机 | 某个节点宕机 |
| 网络分区 | 网络分区 |
| Slot 迁移失败 | slot 迁移失败 |
| 主从切换 | 主从切换 |
| 资源耗尽 | 资源耗尽 |

## 预防措施

1. 监控集群健康状态
2. 使用适当的副本数量（至少 1 个）
3. 合适的网络基础设施
4. 定期备份和恢复测试
5. 监控 slot 分布
6. 设置集群状态告警

## 关联场景

- [复制延迟](replication-delay.md)
