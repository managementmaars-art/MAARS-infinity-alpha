# Hermes Agent CLI 完整命令手册

> **版本**: v0.8.0 | **最后更新**: 2026-04-11

## 目录

1. [基础命令](#基础命令)
2. [执行模式](#执行模式)
3. [工具管理](#工具管理)
4. [记忆系统](#记忆系统)
5. [技能管理](#技能管理)
6. [插件系统](#插件系统)
7. [消息网关](#消息网关)
8. [定时任务](#定时任务)
9. [MCP 集成](#mcp-集成)
10. [诊断与调试](#诊断与调试)

---

## 基础命令

### 启动交互式会话

```bash
hermes
```

启动 TUI（终端用户界面）交互式对话。

**快捷键**:
- `Ctrl+C` - 中断当前生成
- `Ctrl+D` - 退出
- `Tab` - 自动补全
- `↑/↓` - 历史记录

### 查看版本信息

```bash
hermes --version
hermes -v

# 输出示例:
# Hermes Agent v0.8.0 (2026.4.8)
# Project: /path/to/hermes-agent
# Python: 3.11.15
# OpenAI SDK: 2.31.0
```

### 显示帮助信息

```bash
hermes --help
hermes help <command>
```

---

## 执行模式

### 单轮执行 (run)

```bash
hermes run "你的提示词" [选项]
```

**核心选项**:

| 选项 | 简写 | 默认值 | 说明 |
|------|------|--------|------|
| `--non-interactive` | 无 | false | 关闭 TUI，适合脚本调用 |
| `--no-stream` | 无 | false | 禁用流式输出，返回完整结果 |
| `--context-file` | `-c` | null | 注入上下文文件路径 |
| `--toolset` | `-t` | null | 限制使用的工具集名称 |
| `--model` | `-m` | 配置默认值 | 指定模型（覆盖配置） |
| `--provider` | 无 | 配置默认值 | 指定 LLM 提供商 |
| `--timeout` | 无 | 300 | 超时时间（秒） |
| `--max-tokens` | 无 | 配置默认值 | 最大输出 Token 数 |
| `--temperature` | 无 | 配置默认值 | 温度参数 (0.0-2.0) |

**使用示例**:

```bash
# 最简单的单轮调用
hermes run "什么是机器学习？" --non-interactive --no-stream

# 带上下文文件
hermes run "分析这个项目的架构" \
  --context-file ./AGENTS.md \
  --non-interactive --no-stream

# 限制工具集
hermes run "搜索最新的 React 文档" \
  --toolset web_search \
  --non-interactive --no-stream

# 指定模型和超时
hermes run "写一个排序算法" \
  --model gpt-4o \
  --temperature 0.2 \
  --timeout 60 \
  --non-interactive --no-stream
```

---

## 工具管理

### 列出所有可用工具

```bash
hermes tools list
hermes tools list --all    # 包括未启用的
```

### 启用/禁用工具集

```bash
# 列出可用工具集
hermes toolsets

# 启用特定工具集
hermes tools enable web_search browser file_operations

# 禁用特定工具集
hermes tools disable code_execution terminal
```

### 内置工具列表

| 工具集 | 包含工具 | 用途 |
|--------|----------|------|
| `web_search` | search_web, firecrawl_scrape, brave_search, searxng_search | 网页搜索和抓取 |
| `browser` | browser_navigate, browser_click, browser_type, browser_screenshot, browser_extract | 浏览器自动化 |
| `file_operations` | read_file, write_file, edit_file, glob_files, list_directory | 文件读写操作 |
| `terminal` | execute_command, bash, shell | 终端命令执行 |
| `memory` | memory_search, memory_add_note, memory_list_notes | 记忆系统访问 |
| `code_execution` | execute_code | 代码执行沙盒 |
| `delegation` | delegate_task | 子代理委托 |
| `skills` | skills_list, skills_create, skills_edit, skills_remove | 技能管理 |
| `image_generation` | generate_image, upscale_image | AI 图像生成 |
| `voice` | text_to_speech, transcribe_audio | 语音合成与识别 |

---

## 记忆系统

### 搜索记忆

```bash
hermes memory search "关键词"
hermes memory search "用户偏好设置" --limit 10
```

### 笔记管理

```bash
# 列出所有笔记
hermes memory notes list

# 添加新笔记
hermes memory notes add "重要发现：XXX"

# 搜索笔记内容
hermes memory notes search "查询内容"
```

### 导入导出

```bash
# 导出所有记忆数据
hermes memory export ./backup/

# 从备份导入
hermes memory import ./backup/
```

### 记忆后端切换

```bash
# 查看当前记忆后端
hermes memory status

# 切换到 Honcho 后端
hermes memory setup honcho

# 使用内置后端
hermes memory setup built-in
```

**支持的记忆后端**:

| 后端 | 特点 |
|------|------|
| `built-in` | 默认，SQLite + FTS5 全文搜索 |
| `honcho` | AI 原生记忆，方言建模 |
| `mem0` | 开源记忆服务 |
| `openviking` | 高级向量检索 |
| `hindsight` | 时间线记忆 |
| `holographic` | 全息记忆系统 |
| `retaindb` | 企业级记忆存储 |
| `byte-rover` | 轻量级本地记忆 |

---

## 技能管理

### 列出技能

```bash
hermes skills list
hermes skills ls           # 短形式

# 查看技能详情
hermes skills show skill-name
```

### 创建技能

```bash
# 交互式创建
hermes skills create my-skill

# 带描述创建
hermes skills create research-methodology \
  --description "系统性网页研究方法论"

# 从模板创建
hermes skills create code-review --template default
```

### 编辑技能

```bash
hermes skills edit my-skill
# 打开默认编辑器编辑技能 Markdown 文件
```

### 删除技能

```bash
hermes skills remove my-skill
hermes skills rm old-skill   # 短形式
```

### 技能格式规范

每个技能是一个 Markdown 文件，位于 `~/.hermes/skills/<skill-name>/skill.md`：

```markdown
---
name: my-skill
description: 技能描述
triggers:
  - "触发词1"
  - "触发词2"
tags:
  - category1
  - category2
---

# 技能名称

## 步骤
1. 第一步说明
2. 第二步说明

## 最佳实践
- 注意事项
- 推荐做法
```

---

## 插件系统

### 插件管理

```bash
# 列出已安装插件
hermes plugins list
hermes plugins ls

# 安装插件（从 Git）
hermes plugins install owner/repo
hermes plugins install https://github.com/owner/repo.git

# 更新插件
hermes plugins update plugin-name
hermes plugins update --all    # 更新所有

# 卸载插件
hermes plugins remove plugin-name
hermes plugins rm plugin-name

# 启用/禁用插件（保留安装但不加载）
hermes plugins enable plugin-name
hermes plugins disable plugin-name
```

### 插件类型

```bash
# 列出通用插件
hermes plugins list --type general

# 列出内存提供者
hermes plugins list --type memory

# 列出上下文引擎
hermes plugins list --type context_engine
```

### 插件开发

详见 [plugin-development.md](./plugin-development.md)

---

## 消息网关

### 网关管理

```bash
# 设置向导
hermes gateway setup

# 列出已配置的网关
hermes gateway list

# 安装特定平台网关
hermes gateway install telegram
hermes gateway install discord
hermes gateway install slack

# 启动所有网关
hermes gateway start

# 停止所有网关
hermes gateway stop

# 重启特定网关
hermes gateway restart discord
```

### 支持的消息平台

| 平台 | 网关名称 | 功能 |
|------|----------|------|
| Telegram | `telegram` | 完整支持（文字、语音、群组） |
| Discord | `discord` | 完整支持（含语音频道） |
| Slack | `slack` | 支持 |
| WhatsApp | `whatsapp` | 支持 |
| Signal | `signal` | 支持 |
| Matrix | `matrix` | 支持 |
| Mattermost | `mattermost` | 支持 |
| Email | `email` | 支持 |
| SMS | `sms` | 支持 |
| DingTalk (钉钉) | `dingtalk` | 支持 |
| Feishu (飞书) | `feishu` | 支持 |
| WeCom (企业微信) | `wecom` | 支持 |
| Home Assistant | `homeassistant` | 支持 |

---

## 定时任务 (Cron)

### 任务管理

```bash
# 列出所有任务
hermes cron list

# 创建任务
hermes cron add \
  --name "每日新闻摘要" \
  --cron "0 9 * * *" \          # 每天 9:00
  --message "总结今日科技新闻" \
  --skill daily-news             # 可附加技能

# 暂停任务
hermes cron pause TASK_ID 或 任务名

# 恢复任务
hermes cron resume TASK_ID 或 任务名

# 编辑任务
hermes cron edit TASK_ID

# 删除任务
hermes cron remove TASK_ID
hermes cron rm TASK_ID            # 短形式

# 手动触发任务
hermes cron run TASK_ID
```

### Cron 表达式语法

```
┌───────────── 分钟 (0-59)
│ ┌───────────── 小时 (0-23)
│ │ ┌───────────── 月中天 (1-31)
│ │ │ ┌───────────── 月 (1-12)
│ │ │ │ ┌───────────── 周中天 (0-6, 0=周日)
│ │ │ │ │
* * * * *
```

**示例**:

| 表达式 | 含义 |
|--------|------|
| `* * * * *` | 每分钟 |
| `*/15 * * * *` | 每15分钟 |
| `0 * * * *` | 每小时 |
| `0 9 * * *` | 每天 9:00 |
| `0 9 * * 1` | 每周一 9:00 |
| `0 9 1 * *` | 每月1号 9:00 |
| `0 9-17 * * 1-5` | 工作日 9:00-17:00 每小时 |

---

## MCP 集成

### Server 模式（暴露能力给 IDE）

```bash
# 启动 MCP Server
hermes mcp serve --port 8080
hermes mcp serve --stdio        # 标准输入输出模式

# 配置 MCP Server
hermes mcp serve-config         # 生成 IDE 配置片段
```

### Client 模式（连接外部服务）

```bash
# 连接外部 MCP 服务器
hermes mcp connect <server-config-json>

# 列出已连接的 MCP 服务
hermes mcp list

# 断开连接
hermes mcp disconnect <server-id>
```

详见 [mcp-integration.md](./mcp-integration.md)

---

## 诊断与调试

### 状态检查

```bash
# 快速状态概览
hermes status

# 详细诊断
hermes doctor
```

### 日志查看

```bash
# 实时查看日志
hermes logs --follow
hermes logs -f

# 查看最近N行
hermes logs -n 100

# 过滤日志级别
hermes logs --level ERROR
hermes logs --level WARNING

# 查看特定会话的日志
hermes logs --session SESSION_ID
```

### 性能分析

```bash
# 查看最近的性能指标
hermes stats

# 查看Token使用统计
hermes stats tokens

# 查看任务耗时统计
hermes stats timing
```

### 重置与清理

```bash
# 清理缓存
hermes cleanup cache

# 清理旧会话（超过N天的）
hermes cleanup sessions --older-than 30

# 重置为出厂设置（⚠️ 会删除所有数据和配置）
hermes reset --factory
```

---

## 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `HERMES_HOME` | Hermes 数据目录 | `~/.hermes` |
| `HERMES_CONFIG` | 自定义配置文件路径 | `~/.hermes/config.yaml` |
| `HERMES_ENV_FILE` | 自定义环境变量文件 | `~/.hermes/.env` |
| `HERMES_LOG_LEVEL` | 日志级别 | INFO |
| `HERMES_NO_COLOR` | 禁用彩色输出 | false |
| `HERMES_ENABLE_PROJECT_PLUGINS` | 启用项目级插件 | false |
| `HERMES_OPTIONAL_SKILLS` | 自定义可选技能目录 | null |

---

## 退出码

| 退出码 | 含义 |
|--------|------|
| 0 | 成功 |
| 1 | 一般错误 |
| 2 | 参数错误 |
| 3 | 配置错误 |
| 4 | 网络错误 |
| 5 | API 认证失败 |
| 124 | 超时（来自 timeout 命令） |
| 130 | 用户中断 (Ctrl+C) |
