# 会话堆积故障排查

## 概述

活跃会话堆积是指大量连接处于活跃状态（Sleep/Waiting），导致连接数资源耗尽，响应变慢。

## 典型症状

- 活跃连接数持续较高
- 很多连接处于 Sleep 状态
- 连接数接近上限
- 响应时间变长

> 函数参数详见 [api/ops.md](../../api/ops.md)。

## 排查步骤

### 步骤 0: 获取支持的监控指标（推荐先执行）

> **提示**：在获取具体指标数据之前，建议先调用 `get_metric_items` 查看当前实例支持哪些指标，然后选择合适的指标进行获取。

```python
# 获取当前实例支持的监控指标列表
get_metric_items(client,
)
```

### 步骤 1: 检查活跃会话

```python
import time
now = int(time.time())

# 获取活跃会话数
get_metric_data(client,
    metric_name="ThreadsConnected",
    period=60,
    start_time=now - 300,
    end_time=now,
    instance_id="mysql-xxx",
)
```

### 步骤 2: 分析会话状态

```python
# ⚠️ 不要直接输出全部 sessions！拿到数据后做分组统计再输出
# 完整参数（筛选、分页）见 api/ops.md 中 list_connections 说明
from collections import Counter, defaultdict

# 1) 分页拉取全量会话
all_sessions = []
page = 1
while True:
    result = list_connections(client, show_sleep=True, page_number=page, instance_id="mysql-xxx")
    all_sessions.extend(result["data"]["sessions"])
    total = result["data"]["total"]
    if len(all_sessions) >= total:
        break
    page += 1

print(f"总连接数: {total}")

# 2) 单维度统计
print("=== 按状态 ===")
for cmd, cnt in Counter(s["command"] for s in all_sessions).most_common():
    print(f"  {cmd}: {cnt}")

print("=== 按 state ===")
for state, cnt in Counter(s["state"] for s in all_sessions).most_common():
    print(f"  {state}: {cnt}")

# 诊断提示：avg 短（< 10s）= 正常短查询；avg 长（> 60s）+ Sleep 多 = 疑似连接泄漏
print("=== 按用户 ===")
user_time = defaultdict(lambda: {"count": 0, "total_time": 0})
for s in all_sessions:
    user_time[s["user"]]["count"] += 1
    user_time[s["user"]]["total_time"] += int(s["time"])
for user, st in sorted(user_time.items(), key=lambda x: -x[1]["count"]):
    avg = st["total_time"] // st["count"]
    print(f"  {user}: {st['count']}个 ({st['count']*100//total}%), avg={avg}s")

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

long_running = [s for s in all_sessions if int(s["time"]) > 60]
print(f"\n运行 > 60s 的会话: {len(long_running)} 个")
```

若 `len(sessions) < total`，翻页继续拉取后合并统计。

### 步骤 3: 对比历史会话快照（可选）

如需判断会话是突增还是持续泄漏，可对比历史快照：

```python
# 查询 1 小时前的连接快照（需实例已开启会话快照采集）
list_history_connections(client,
    start_time=now - 7200,
    end_time=now - 3600,
    show_sleep=True,
    instance_id="mysql-xxx",
)
```

对比 `summary.by_user` / `summary.by_db` 与当前 `list_connections` 的分布，判断是某用户/应用持续泄漏还是突发流量。

## 常见根因

| 根因 | 说明 |
|-------|-------------|
| 连接泄漏 | 应用未正确关闭连接 |
| 长查询 | 查询执行时间过长 |
| 网络问题 | 网络问题导致连接断开慢 |
| 应用 Bug | 应用逻辑问题 |
| 连接池配置不当 | 连接池配置不当 |

## ⚠️ 应急处置（需确认后执行）

### 终止长时间运行的查询

> **警告**：终止会话会导致当前事务失败，请在确认后执行！

```python
# 按条件终止：终止执行时间超过 60 秒的会话
kill_process(client,
    min_time=60,
    instance_id="mysql-xxx",
)

# 按条件终止：终止指定用户的全部 Sleep 会话
kill_process(client,
    users="app_user",
    command_type="Sleep",
    instance_id="mysql-xxx",
)

# 精确终止：终止指定进程（从 list_connections 获取 process_id 和 node_id）
kill_process(client,
    process_ids=["12345", "12346"],
    node_id="node-1",
    instance_id="mysql-xxx",
)
```

### 调整超时设置

> `execute_sql` 仅支持只读操作，无法执行 `SET GLOBAL`。需到**火山引擎控制台 → 参数管理**修改 `wait_timeout` 等参数。

## 预防措施

1. 使用正确的连接池
2. 设置适当的超时值
3. 监控连接状态
4. 实现连接生命周期管理
5. 设置连接数告警
6. 审查应用连接代码

## 关联场景

- [慢查询](slow-query.md)
- [锁等待](lock-wait.md)
- [连接数打满](connection-full.md)
