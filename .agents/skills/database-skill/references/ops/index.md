---
name: "database-skill-ops"
description: "数据库运维 SOP：基于标准化流程（SOP）进行数据库故障排查，涵盖资源基线确认、负载分析、会话分析、慢查询定位、空间分析及变更追溯。"
---

# 数据库故障排查 SOP

> 🔴 **本文件是路由中枢。** 根据 db_type + 症状匹配场景后，**必须同时阅读两个文件**：
> 1. 对应的 **SOP 文件**（排查步骤和调用顺序）
> 2. **[api/ops.md](../api/ops.md)**（函数完整参数、返回格式、约束条件）
>
> SOP 中的函数调用是简化示例，不含全部参数（如分页、排序、过滤、时间范围限制等）。**不读 API 参考直接调用函数会导致参数缺失或用法错误。** 排查中途需要换方向时，回到本文件重新匹配。

## 通用场景

- [巡检](health-inspection.md) - 健康检查，产出概览报告（适用所有 db_type，不支持的项自动跳过）

## 运维函数支持范围

> SQL Server、Redis、External 实例**不支持任何运维诊断函数**，仅支持元数据探查、数据查询和工单。
> 不支持的函数调用时会被代码自动拦截，无需 Agent 判断。

| 能力 | MySQL | VeDB-MySQL | Postgres | MongoDB |
|:---|:---:|:---:|:---:|:---:|
| 慢查询（明细/聚合/趋势） | ✓ | ✓ | ✓ | ✓ |
| 全量 SQL | ✓ | ✓ | ✓ | ✗ |
| 死锁 | ✓ | ✓ | ✗ | ✗ |
| 事务和锁 | ✓ | ✓ | ✓ | ✗ |
| 锁等待分析 | ✓ | ✓ | ✓ | ✗ |
| 错误日志 | ✓ | ✓ | ✓ | ✗ |
| 表空间 | ✓ | ✓ | ✓ | ✗ |
| 健康概览 | ✓ | ✓ | ✓ | ✗ |
| 监控指标（metric_items/data） | ✓ | ✗ | ✗ | ✗ |
| 表级监控（table_metric） | ✓ | ✓ | ✓ | ✗ |
| 活跃会话列表 | ✓ | ✓ | ✓ | ✓ |
| 历史连接快照 | ✓ | ✓ | ✓ | ✓ |

---

## MySQL（包括 VeDBMySQL、ByteRDS 等 MySQL 兼容引擎）

MySQL 及 MySQL 兼容数据库引擎的故障排查指南。

**常见场景：**
- [CPU 打满](mysql/cpu-spike.md) - CPU 使用率过高
- [连接数打满](mysql/connection-full.md) - 连接数达到上限
- [磁盘空间不足](mysql/disk-full.md) - 磁盘空间耗尽
- [内存压力](mysql/memory-pressure.md) - 内存使用率过高
- [死锁](mysql/deadlock.md) - 事务死锁
- [主从延迟](mysql/replication-delay.md) - 主从复制延迟
- [慢查询](mysql/slow-query.md) - 查询性能问题
- [IO 瓶颈](mysql/io-bottleneck.md) - 磁盘 IO 瓶颈
- [锁等待](mysql/lock-wait.md) - 锁竞争
- [会话堆积](mysql/session-pileup.md) - 活跃会话堆积
- [临时表溢出](mysql/temp-table-overflow.md) - 磁盘临时表溢出
- [Binlog 延迟](mysql/binlog-delay.md) - Binlog 延迟
- [网络抖动](mysql/network-jitter.md) - 网络延迟问题


---

## Postgres（包括所有 Postgres 兼容引擎）

Postgres 及所有 Postgres 兼容数据库引擎的故障排查指南。

**常见场景：**
- [CPU 打满](postgresql/cpu-spike.md) - CPU 使用率过高
- [连接数打满](postgresql/connection-full.md) - 连接数达到上限
- [磁盘空间不足](postgresql/disk-full.md) - 磁盘空间耗尽
- [慢查询](postgresql/slow-query.md) - 查询性能问题
- [锁等待](postgresql/lock-wait.md) - 锁竞争
- [内存压力](postgresql/memory-pressure.md) - 内存使用率过高
- [VACUUM 阻塞](postgresql/vacuum-blocking.md) - VACUUM 操作阻塞
- [WAL 积压](postgresql/wal-backlog.md) - WAL 累积
- [复制延迟](postgresql/replication-delay.md) - 流复制延迟


---

## MongoDB

MongoDB 数据库故障排查指南。可用运维函数：慢查询（明细/聚合/趋势）、实例节点列表。不支持：全量 SQL、死锁、事务/锁、错误日志、表空间、健康概览、监控指标。

**常见场景：**
- [连接数打满](mongodb/connection-full.md) - 连接数达到上限
- [磁盘空间不足](mongodb/disk-full.md) - 磁盘空间耗尽
- [慢查询](mongodb/slow-query.md) - 查询性能问题
- [内存压力](mongodb/memory-pressure.md) - WiredTiger 缓存压力
- [复制延迟](mongodb/replication-delay.md) - 副本集延迟
- [锁等待](mongodb/lock-wait.md) - 数据库/集合锁
- [连接泄漏](mongodb/connection-leak.md) - 连接泄漏
- [集群故障](mongodb/cluster-failure.md) - 分片集群问题


---

## Redis

Redis 内存数据库故障排查指南。**Redis 不支持任何运维诊断 API**，以下 SOP 主要通过 `execute_sql`（Redis 命令）进行排查。

**常见场景：**
- [内存打满](redis/memory-full.md) - 内存耗尽 (OOM)
- [连接数打满](redis/connection-full.md) - 连接数达到上限
- [持久化阻塞](redis/persistence-block.md) - AOF/RDB 阻塞
- [集群故障](redis/cluster-failure.md) - 集群节点故障
- [阻塞命令](redis/blocking-command.md) - 阻塞命令
- [复制延迟](redis/replication-delay.md) - 主从延迟
- [CPU 打满](redis/cpu-spike.md) - CPU 使用率过高


