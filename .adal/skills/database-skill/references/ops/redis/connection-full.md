# 连接数打满故障排查

## 概述

连接数打满是指 Redis 实例的当前连接数达到上限，导致新请求无法建立连接，出现连接错误。

## 典型症状

- 应用报错: `max number of clients reached`
- 无法建立新的数据库连接
- 连接数监控显示达到上限
- 旧连接未被释放，堆积

> 函数参数详见 [api/metadata-query.md](../../api/metadata-query.md)。

## 排查步骤

### 步骤 1: 获取连接信息

> **注意**：Redis 不支持 `get_metric_items/get_metric_data`，通过 `execute_sql` 使用 Redis 原生命令获取连接信息。

```python
# 获取 Redis 连接统计
execute_sql(client,
    sql="INFO clients;", instance_id="redis-xxx", database="0"
)
```

### 步骤 2: 查看客户端列表

```python
# 获取所有连接的客户端详情
execute_sql(client,
    sql="CLIENT LIST;", instance_id="redis-xxx", database="0"
)
```

## 常见根因

| 根因 | 说明 |
|-------|-------------|
| 连接泄漏 | 应用未正确关闭 Redis 连接 |
| 连接过多 | 并发请求过多，连接池配置不当 |
| 长运行命令 | 命令执行时间过长 |
| 应用 Bug | 连接未正确释放 |

## ⚠️ 应急处置（需确认后执行）

### 终止空闲连接

> **警告**：终止连接会导致当前任务失败，请在确认后执行！

```python
# 终止指定客户端
execute_sql(client,
    sql="CLIENT KILL ID <id>;", instance_id="redis-xxx", database="0"
)

# 终止所有空闲客户端
execute_sql(client,
    sql="CLIENT KILL TYPE normal;", instance_id="redis-xxx", database="0"
)
```

## 预防措施

1. 使用正确的连接池（Jedis, lettuce 等）
2. 设置适当的连接超时
3. 监控并终止长时间空闲的连接
4. 设置连接数告警
5. 审查应用连接生命周期
6. 配置 client-output-buffer-limit

## 关联场景

- [慢查询](slow-query.md)
