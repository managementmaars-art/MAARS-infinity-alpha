---
name: dm-bot
description: Discord 机器人 (dm-bot) 的定时任务管理工具。当用户请求提醒、定时任务、延迟提醒、闹钟、"X分钟后提醒我..."、"每天早上...提醒我"、查看任务列表、删除任务时，必须使用此 skill 执行 CLI 命令。禁止用 bash sleep/notify-send 等方式代替。
---

# dm-bot 定时任务管理

帮助用户管理 dm-bot 的定时任务，支持标准的 cron 表达式。

## 何时使用此 Skill

**当用户说以下类型的话时，必须使用此 Skill：**
- "X分钟后提醒我..."
- "几分钟后叫我..."
- "每天/每周/每月...提醒我..."
- "设个闹钟..."
- "查看我的任务"
- "删除任务X"
- "列出所有定时任务"

**禁止使用 bash sleep/notify-send 等方式实现提醒，必须用下面的 CLI 命令！**

## CLI 命令

所有命令需要在项目根目录执行：

### 创建任务

```bash
npx dm-bot schedule create "<cron表达式>" "<任务内容>" <是否重复>
```

参数：
- cron表达式：如 `0 8 * * *` 表示每天8点
- 任务内容：提醒内容
- 是否重复：`true` 或 `false`

示例：
```bash
npx dm-bot schedule create "0 8 * * *" "提醒喝水" true
npx dm-bot schedule create "0 9 * * 1-5" "上班打卡" true
npx dm-bot schedule create "0 10 1 * *" "月初提醒" false
```

### 列出任务

```bash
npx dm-bot schedule list
```

### 删除任务

```bash
npx dm-bot schedule delete <任务ID>
```

### 开启新会话

```bash
npx dm-bot new
```

### 延迟提醒

当用户说 "5分钟后提醒我喝水" 或 "10分钟后叫我" 等延迟提醒时，使用 delayed 命令：

```bash
npx dm-bot delayed wake <分钟数> [提醒内容]
```

参数：
- 分钟数：延迟的分钟数（可以是小数，如 0.5 表示30秒）
- 提醒内容：可选，自定义提醒文本（默认是"机器人已叫醒！"）

示例：
```bash
npx dm-bot delayed wake 5 "提醒喝水"
npx dm-bot delayed wake 10
npx dm-bot delayed wake 0.5 "休息一下"
```

**重要：延迟任务需要从项目目录执行**，确保数据库路径正确。建议使用绝对路径：
```bash
cd /home/ubuntu/skills/discord-bot && npx dm-bot delayed wake 5 "提醒喝水"
```

## Cron 表达式说明

```
┌───────────── 分钟 (0-59)
│ ┌───────────── 小时 (0-23)
│ │ ┌───────────── 日 (1-31)
│ │ │ ┌───────────── 月 (1-12)
│ │ │ │ ┌───────────── 星期 (0-6, 0=周日)
│ │ │ │ │
* * * * *
```

常用示例：
- `0 8 * * *` - 每天早上8点
- `30 9 * * 1-5` - 工作日早上9:30
- `0 0 * * 0` - 每周日午夜
- `0 8,12,18 * * *` - 每天8点、12点、18点

## 使用流程

当用户说 "每天早上8点提醒我喝水"：

1. 解析时间意图 → cron表达式 `0 8 * * *`
2. 执行命令：
   ```bash
   npx dm-bot schedule create "0 8 * * *" "提醒喝水" true
   ```
3. 返回结果给用户

当用户说 "看看我的任务"：

1. 执行命令：
   ```bash
   npx dm-bot schedule list
   ```
2. 展示任务列表给用户

当用户说 "删除任务3"：

1. 执行命令：
   ```bash
   npx dm-bot schedule delete 3
   ```
2. 确认删除结果

当用户说 "新对话" 或 "开启新会话"：

1. 执行命令：
   ```bash
   npx dm-bot new
   ```
2. 确认开启结果

当用户说 "5分钟后提醒我喝水"、"10分钟后叫我" 等延迟提醒时：

1. 解析延迟分钟数和提醒内容
2. **必须指定项目目录**，使用绝对路径执行：
   ```bash
   cd /home/ubuntu/skills/discord-bot && npx dm-bot delayed wake <分钟数> "<提醒内容>"
   ```
3. 返回成功结果给用户
