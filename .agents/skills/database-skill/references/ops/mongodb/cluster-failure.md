# 集群故障故障排查

## 概述

集群故障是指 MongoDB 分片集群（Sharded Cluster）中的某个组件出现问题，如 mongos、shard、config server 故障，导致整个集群或部分功能不可用。

## 典型症状

- 部分数据无法访问
- 读写操作报错
- 集群状态异常
- 某个分片不可用

> 函数参数详见 [api/metadata-query.md](../../api/metadata-query.md)。

## 排查步骤

### 步骤 1: 检查集群状态

```python
# 检查分片集群状态
execute_sql(client, instance_id="mongo-xxx",
    sql="db.adminCommand({ shardCollection: "database.collection", key: { _id: "hashed" } });", database="admin"
)
```

### 步骤 2: 检查分片状态

```python
# 获取分片状态
execute_sql(client, instance_id="mongo-xxx",
    sql="""
    db.getSiblingDB('admin').runCommand({ listShards: 1 });
    """, database="admin"
)
```

### 步骤 3: 检查 Chunk 分布

```python
# 获取 chunk 分布
execute_sql(client, instance_id="mongo-xxx",
    sql="""
    db.getSiblingDB('database').collection.getShardDistribution();
    """, database="admin"
)
```

## 常见根因

| 根因 | 说明 |
|-------|-------------|
| 分片宕机 | 某个分片宕机 |
| Config Server 问题 | config server 问题 |
| 网络分区 | 网络分区 |
| Chunk 迁移失败 | 分片迁移失败 |
| Mongos 故障 | mongos 路由节点故障 |

## 预防措施

1. 监控集群健康状态
2. 每个分片使用副本集
3. 合适的网络基础设施
4. 定期备份和恢复测试
5. 监控 chunk 分布
6. 设置集群状态告警

## 关联场景

- [复制延迟](replication-delay.md)
