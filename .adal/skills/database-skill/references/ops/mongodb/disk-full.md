# 磁盘空间不足故障排查

## 概述

磁盘空间不足是指 MongoDB 实例的磁盘使用率达到 100% 或接近上限，导致无法写入数据、无法创建索引、WiredTiger 无法 checkpoint。

## 典型症状

- 磁盘使用率 100% 或接近 100%
- 写入数据报错
- 无法创建索引
- WiredTiger checkpoint 失败

> 函数参数详见 [api/metadata-query.md](../../api/metadata-query.md)。

## 排查步骤

### 步骤 1: 检查数据库存储统计

> **注意**：MongoDB 不支持 `get_metric_items/get_metric_data/describe_table_space`，通过 `execute_sql` 使用原生命令获取存储信息。

```python
# 获取整个实例的存储统计
execute_sql(client, instance_id="mongo-xxx",
    sql="db.stats();", database="admin"
)
```

### 步骤 2: 检查各集合大小

```python
# 获取当前数据库所有集合的大小信息
execute_sql(client, instance_id="mongo-xxx",
    sql="""
    db.getCollectionNames().map(function(c) {
        var s = db.getCollection(c).stats();
        return { collection: c, size_mb: Math.round(s.size / 1024 / 1024), storage_mb: Math.round(s.storageSize / 1024 / 1024), index_mb: Math.round(s.totalIndexSize / 1024 / 1024), count: s.count };
    }).sort(function(a, b) { return b.storage_mb - a.storage_mb; });
    """, database="admin"
)
```

### 步骤 3: 检查 Oplog 大小

```python
# 检查 oplog 占用空间
execute_sql(client, instance_id="mongo-xxx",
    sql="db.getReplicationInfo();", database="local"
)
```

## 常见根因

| 根因 | 说明 |
|-------|-------------|
| 数据增长 | 数据快速增长，未及时清理 |
| 索引增长 | 索引过大 |
| WiredTiger Cache | WiredTiger 缓存过大 |
| Oplog 增长 | oplog 过大 |

## ⚠️ 应急处置（需确认后执行）

### 压缩集合

> **警告**：压缩操作会锁定集合，请在确认后执行！

```python
# 压缩集合
execute_sql(client, instance_id="mongo-xxx",
    sql="""
    db.collection.runCommand("compact");
    """, database="admin"
)
```

## 预防措施

1. 设置磁盘使用率监控和告警
2. 实施数据归档和清理策略
3. 监控集合大小
4. 使用 TTL 索引自动清理
5. 定期压缩
6. 评估是否需要扩容存储（在火山引擎控制台调整实例磁盘规格）
7. 设置空间使用预测

## 关联场景

- [慢查询](slow-query.md)
