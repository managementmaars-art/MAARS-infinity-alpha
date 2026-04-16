# 复制延迟故障排查

## 概述

复制延迟是指 MongoDB 副本集（Replica Set）中从节点的复制进度落后于主节点，导致读写分离失效、数据不一致等问题。

## 典型症状

- 从节点延迟持续增大
- 读写分离读到的数据过期
- `rs.status()` 显示延迟
- 复制相关报错

> 函数参数详见 [api/metadata-query.md](../../api/metadata-query.md)。

## 排查步骤

### 步骤 1: 检查副本集状态

```python
# 检查副本集状态
execute_sql(client, instance_id="mongo-xxx",
    sql="rs.status();", database="admin"
)
```

### 步骤 2: 检查 Oplog 大小

```python
# 检查 oplog 大小
execute_sql(client, instance_id="mongo-xxx",
    sql="""
    db.getSiblingDB('local').oplog.rs.find().sort({ts: -1}).limit(1);
    """, database="local"
)
```

## 常见根因

| 根因 | 说明 |
|-------|-------------|
| 网络延迟 | 主从网络延迟 |
| 大操作 | 大操作复制时间长 |
| 慢查询 | 从节点执行慢查询 |
| Oplog 太小 | oplog 太小 |

## 预防措施

1. 使用适当的 oplog 大小
2. 保持操作简短
3. 优化从节点慢查询
4. 确保从节点有足够资源
5. 监控复制延迟
6. 使用合适的网络基础设施

## 关联场景

- [慢查询](slow-query.md)
