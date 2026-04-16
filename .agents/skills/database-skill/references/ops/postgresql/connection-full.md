# 连接数打满故障排查

## 概述

连接数打满是指 PostgreSQL 实例的当前连接数达到 `max_connections` 上限，导致新请求无法建立连接，出现 `sorry, too many clients already` 错误。

## 典型症状

- 应用报错: `sorry, too many clients already`
- 无法建立新的数据库连接
- 连接数监控显示达到上限
- 旧连接未被释放，堆积

> 函数参数详见 [api/ops.md](../../api/ops.md)。

## 排查步骤

> **重要约束**：连接数打满时，`execute_sql` 也需要建立新连接，会直接报 `sorry, too many clients already` 失败。以下步骤优先使用管理 API（`list_connections` 等），它们不占用数据库连接，连接打满时仍可正常调用。

### 步骤 1: 检查当前连接数及健康状态

```python
import time
now = int(time.time())

# 获取最近一小时健康概览（含活跃会话数、当前打开连接数等指标）
describe_health_summary(client,
    end_time=now,
    instance_id="pg-xxx",
)
```

> `max_connections` 的精确值需到**火山引擎控制台 → 参数管理**查看，连接打满时无法通过 `execute_sql` 查询。

### 步骤 3: 分析连接状态

```python
# ⚠️ 不要直接输出全部 sessions！拿到数据后做分组统计再输出
# 完整参数（筛选、分页）见 api/ops.md 中 list_connections 说明
from collections import Counter, defaultdict

# 1) 分页拉取全量会话
all_sessions = []
page = 1
while True:
    result = list_connections(client, show_sleep=True, page_number=page, instance_id="pg-xxx")
    all_sessions.extend(result["data"]["sessions"])
    total = result["data"]["total"]
    if len(all_sessions) >= total:
        break
    page += 1

print(f"总连接数: {total}")

# 2) 单维度统计
# 诊断提示：avg 短（< 10s）= 正常短查询；avg 长（> 60s）+ Sleep/idle 多 = 疑似连接泄漏
print("=== 按用户 ===")
user_time = defaultdict(lambda: {"count": 0, "total_time": 0})
for s in all_sessions:
    user_time[s["user"]]["count"] += 1
    user_time[s["user"]]["total_time"] += int(s["time"])
for user, st in sorted(user_time.items(), key=lambda x: -x[1]["count"]):
    avg = st["total_time"] // st["count"]
    print(f"  {user}: {st['count']}个 ({st['count']*100//total}%), avg={avg}s")

print("=== 按状态 ===")
for cmd, cnt in Counter(s["command"] for s in all_sessions).most_common():
    print(f"  {cmd}: {cnt}")

print("=== 按数据库 ===")
for db, cnt in Counter(s.get("db") or "(none)" for s in all_sessions).most_common():
    print(f"  {db}: {cnt}")

print("=== 按来源 IP（Top 10）===")
for ip, cnt in Counter(s["host"].split(":")[0] for s in all_sessions).most_common(10):
    print(f"  {ip}: {cnt}")

print("=== 按执行时间分布 ===")
buckets = {"0-10s": 0, "10-60s": 0, "1-5min": 0, "5-60min": 0, ">1h": 0}
for s in all_sessions:
    t = int(s["time"])
    if t <= 10: buckets["0-10s"] += 1
    elif t <= 60: buckets["10-60s"] += 1
    elif t <= 300: buckets["1-5min"] += 1
    elif t <= 3600: buckets["5-60min"] += 1
    else: buckets[">1h"] += 1
for b, cnt in buckets.items():
    print(f"  {b}: {cnt}")

# 3) 联合维度统计
print("=== 用户×数据库 ===")
for (user, db), cnt in Counter((s["user"], s.get("db") or "(none)") for s in all_sessions).most_common():
    print(f"  {user} → {db}: {cnt}")

print("=== 用户×状态（含时间汇总）===")
user_cmd_stats = defaultdict(lambda: {"count": 0, "total_time": 0, "max_time": 0})
for s in all_sessions:
    key = (s["user"], s["command"])
    t = int(s["time"])
    user_cmd_stats[key]["count"] += 1
    user_cmd_stats[key]["total_time"] += t
    user_cmd_stats[key]["max_time"] = max(user_cmd_stats[key]["max_time"], t)
for (user, cmd), st in sorted(user_cmd_stats.items(), key=lambda x: -x[1]["count"]):
    avg = st["total_time"] // st["count"]
    print(f"  {user}/{cmd}: {st['count']}个, avg={avg}s, max={st['max_time']}s")
```

若 `len(sessions) < total`，翻页继续拉取后合并统计。

### 步骤 4: 对比历史连接分布（可选）

```python
# 查询问题出现前的连接快照（需实例已开启会话快照采集）
list_history_connections(client,
    start_time=now - 7200,
    end_time=now - 3600,
    show_sleep=True,
    instance_id="pg-xxx",
)
```

对比 `summary.by_user` / `summary.by_db` 与当前分布，判断连接增长来源。

## 常见根因

| 根因 | 说明 |
|-------|-------------|
| 连接泄漏 | 应用未正确关闭数据库连接 |
| 连接过多 | 并发请求过多，连接池配置不当 |
| 长查询 | 查询耗时过长 |
| 空闲连接 | 长时间空闲的连接未释放 |

## ⚠️ 应急处置（需确认后执行）

### 终止空闲连接

> **警告**：终止进程会导致当前事务失败，请在确认后执行！

```python
# 按条件终止：终止所有空闲超过 300 秒的连接
kill_process(client,
    command_type="Sleep",
    min_time=300,
    instance_id="pg-xxx",
)

# 精确终止：终止指定进程
kill_process(client,
    process_ids=["12345", "12346"],
    node_id="node-1",
    instance_id="pg-xxx",
)
```

## 预防措施

1. 使用正确的连接池（PgBouncer, Pgpool-II）
2. 设置适当的连接超时
3. 监控并终止长时间空闲的连接
4. 设置连接数告警
5. 审查应用连接生命周期
6. 配置 `idle_in_transaction_session_timeout`

## 关联场景

- [慢查询](slow-query.md)
