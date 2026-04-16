# 连接数打满故障排查

## 概述

连接数打满是指 MySQL 实例的当前连接数达到 `max_connections` 上限，导致新请求无法建立连接，出现 `Too many connections` 错误。

**诊断原则：连接数打满是结果，不是原因。** 排查时必须按用户、来源 IP、状态等维度分组统计，定位哪个服务/客户端贡献了异常连接数，而不是只看总数。

## 典型症状

- 应用报错: `Too many connections`
- 无法建立新的数据库连接
- 连接数监控显示达到上限
- 旧连接未被释放，堆积

> 函数参数详见 [api/ops.md](../../api/ops.md)。

## 排查步骤

> **重要约束**：连接数打满时，`execute_sql` 也需要建立新连接，会直接报 `Too many connections` 失败。以下步骤优先使用管理 API（`get_metric_data`、`list_connections` 等），它们不占用数据库连接，连接打满时仍可正常调用。

### 步骤 0: 获取支持的监控指标（推荐先执行）

> **提示**：在获取具体指标数据之前，建议先调用 `get_metric_items` 查看当前实例支持哪些指标，然后选择合适的指标进行获取。

```python
# 获取当前实例支持的监控指标列表
get_metric_items(client)
```

### 步骤 1: 检查当前连接数

```python
import time
now = int(time.time())

# 获取连接数时序数据
get_metric_data(client,
    metric_name="ThreadsConnected",
    period=60,
    start_time=now - 300,
    end_time=now,
    instance_id="mysql-xxx",
)
```

> `max_connections` 的精确值需到**火山引擎控制台 → 参数管理**查看，连接打满时无法通过 `execute_sql` 查询。

### 步骤 3: 分析连接状态

```python
# 查询会话（含 Sleep 连接）
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

# 2) 单维度统计 — 快速定位异常维度
# 按用户：哪个账号连接数最多，平均时间多长
# 诊断提示：avg 短（< 10s）= 正常短查询；avg 长（> 60s）+ Sleep 多 = 疑似连接泄漏
print("=== 按用户 ===")
user_time = defaultdict(lambda: {"count": 0, "total_time": 0})
for s in all_sessions:
    user_time[s["user"]]["count"] += 1
    user_time[s["user"]]["total_time"] += int(s["time"])
for user, st in sorted(user_time.items(), key=lambda x: -x[1]["count"]):
    avg = st["total_time"] // st["count"]
    print(f"  {user}: {st['count']}个 ({st['count']*100//total}%), avg={avg}s")

# 按状态：Sleep 占比高说明空闲连接堆积
print("=== 按状态 ===")
for cmd, cnt in Counter(s["command"] for s in all_sessions).most_common():
    print(f"  {cmd}: {cnt}")

# 按数据库：哪个库的连接最多
print("=== 按数据库 ===")
for db, cnt in Counter(s.get("db") or "(none)" for s in all_sessions).most_common():
    print(f"  {db}: {cnt}")

# 按来源 IP：均匀分布=多副本连接池问题，集中在少数 IP=单点泄漏
print("=== 按来源 IP（Top 10）===")
for ip, cnt in Counter(s["host"].split(":")[0] for s in all_sessions).most_common(10):
    print(f"  {ip}: {cnt}")

# 按执行时间分布：大量长时间 Sleep 说明连接池未回收空闲连接
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

# 3) 联合维度统计 — 定位具体根因
# 用户×数据库：哪个账号连了哪个库
print("=== 用户×数据库 ===")
for (user, db), cnt in Counter((s["user"], s.get("db") or "(none)") for s in all_sessions).most_common():
    print(f"  {user} → {db}: {cnt}")

# 用户×状态×平均时间：哪个账号的哪种状态占了多久
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

### 步骤 4: 对比历史连接分布（可选）

如需确认连接数何时开始上涨、是否为持续性泄漏：

```python
# 查询问题出现前的连接快照（需实例已开启会话快照采集）
list_history_connections(client,
    start_time=now - 7200,
    end_time=now - 3600,
    show_sleep=True,
    instance_id="mysql-xxx",
)
```

对比 `summary.by_user` 与当前分布，定位连接增长最快的来源。

## 常见根因

| 根因     | 说明                 |
| ------ | ------------------ |
| 连接泄漏   | 应用未正确关闭数据库连接       |
| 连接过多   | 并发请求过多，连接池配置不当     |
| 长查询    | 查询耗时过长，占用连接        |
| 空闲连接   | 长时间空闲的 Sleep 连接未释放 |
| 应用 Bug | 连接未正确释放            |

## 修复建议（排查后必须给出）

排查完成后，**必须**向用户提供具体可操作的修复方案，从以下常见方案中选择：

1. **终止空闲连接** — 通过 `kill_process` 批量终止 Sleep 状态超过阈值的连接
2. **调整 max\_connections** — 临时或永久提升最大连接数上限
3. **优化连接池配置** — 建议调整应用侧连接池参数（最大连接数、空闲超时、最小连接数）
4. **实例扩容** — 在火山引擎控制台升级实例规格以支持更多连接
5. **配置 wait\_timeout** — 设置合理的空闲连接自动断开时间

## ⚠️ 应急处置（需确认后执行）

### 终止空闲连接

> **警告**：终止连接会导致当前事务失败，请在确认后执行！

```python
# 按条件终止：终止所有 Sleep 超过 300 秒的空闲连接
kill_process(client,
    command_type="Sleep",
    min_time=300,
    instance_id="mysql-xxx",
)

# 按条件终止：终止指定用户的全部连接
kill_process(client,
    users="leak_user",
    instance_id="mysql-xxx",
)

# 精确终止：终止指定进程
kill_process(client,
    process_ids=["12345", "12346"],
    node_id="node-1",
    instance_id="mysql-xxx",
)
```

### 增加 max\_connections

> `execute_sql` 仅支持只读操作，无法执行 `SET GLOBAL` 或 `FLUSH`。需到**火山引擎控制台 → 参数管理**修改 `max_connections` 等参数。

## 预防措施

1. 使用正确的连接池（HikariCP, Druid 等）
2. 设置适当的连接超时
3. 监控并终止长时间空闲的连接
4. 设置连接数告警
5. 审查应用连接生命周期
6. 配置 `wait_timeout` 和 `interactive_timeout`

## 关联场景

- [会话堆积](session-pileup.md)
- [慢查询](slow-query.md)

