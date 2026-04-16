# Hermes Agent MCP 集成详解

> **版本**: v0.8.0 | **最后更新**: 2026-04-11

## 目录

1. [MCP 协议概述](#mcp-协议概述)
2. [双向集成架构](#双向集成架构)
3. [Server 模式（暴露能力）](#server-模式暴露能力)
4. [Client 模式（连接外部服务）](#client-模式连接外部服务)
5. [工具过滤与安全](#工具过滤与安全)
6. [IDE 配置](#ide-配置)
7. [高级用法](#高级用法)
8. [故障排除](#故障排除)

---

## MCP 协议概述

**Model Context Protocol (MCP)** 是一种开放标准，允许 AI 应用与外部数据源和工具进行标准化通信。Hermes Agent 从 v0.6.0 起支持 MCP 的**双向集成**：

```
┌─────────────────────────────────────────────────────┐
│                  MCP 生态                             │
│                                                     │
│   ┌──────────┐     ┌──────────┐     ┌──────────┐   │
│   │   IDE    │ ←→ │  Hermes  │ ←→ │ 外部API  │   │
│   │(Cursor)  │     │   Agent  │     │ (DB/CRM) │   │
│   └──────────┘     └──────────┘     └──────────┘   │
│        ↑               ↑               ↑           │
│   MCP Client       MCP Server      MCP Server       │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### 核心概念

| 概念 | 说明 |
|------|------|
| **MCP Server** | 提供能力和资源的服务端 |
| **MCP Client** | 连接并使用 MCP Server 能力的客户端 |
| **Tool** | 可被 LLM 调用的函数 |
| **Resource** | 可被读取的数据（文件、URI等） |
| **Prompt** | 可被注入的提示模板 |

---

## 双向集成架构

### 架构图

```
                         ┌─────────────────────────┐
                         │    WorkBuddy / IDE       │
                         │         (客户端)          │
                         └───────────┬─────────────┘
                                     │ MCP Protocol
                                     ▼
                    ┌────────────────────────────────┐
                    │        Hermes Agent             │
                    │                                │
                    │  ┌─────────────────────────┐   │
                    │  │   MCP Server Mode        │   │
                    │  │  (暴露 Hermes 能力)      │   │
                    │  │  - 47+ 工具             │   │
                    │  │  - 记忆系统              │   │
                    │  │  - 技能系统              │   │
                    │  └─────────────────────────┘   │
                    │                                │
                    │  ┌─────────────────────────┐   │
                    │  │   MCP Client Mode        │   │
                    │  │  (连接外部服务)          │   │
                    │  │  - 数据库               │   │
                    │  │  - API 服务             │   │
                    │  │  - 文件系统             │   │
                    │  └─────────────────────────┘   │
                    └────────────────────────────────┘
```

### 使用场景

| 场景 | 模式 | 说明 |
|------|------|------|
| IDE 集成 | Server | 在 Cursor/Windsurf 中调用 Hermes |
| 扩展能力 | Client | 让 Hermes 使用外部数据库/API |
| 双向桥接 | 两者兼用 | 同时作为 Server 和 Client |

---

## Server 模式（暴露能力）

### 启动 MCP Server

```bash
# 方式1：标准输入输出模式（推荐用于 IDE 集成）
hermes mcp serve --stdio

# 方式2：HTTP 服务器模式
hermes mcp serve --port 8080

# 方式3：带配置选项启动
hermes mcp serve --stdio \
  --allowed-tools "web_search,memory,delegation" \
  --max-tokens 4096 \
  --model "anthropic/claude-haiku"
```

### Server 配置选项

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `--port` | 8080 | HTTP 模式端口号（仅 HTTP 模式） |
| `--stdio` | false | 使用 stdio 模式（推荐） |
| `--model` | 配置默认值 | 强制使用指定模型 |
| `--max-tokens` | 配置默认值 | 最大输出 Token 数 |
| `--temperature` | 配置默认值 | 温度参数 |
| `--allowed-tools` | 全部 | 允许暴露的工具列表（逗号分隔） |
| `--blocked-tools` | 无 | 禁止暴露的工具列表 |
| `--enable-memory` | true | 是否暴露记忆相关工具 |
| `--enable-delegation` | true | 是否暴露子代理委托工具 |
| `--require-authentication` | false | 是否需要认证令牌 |
| `--auth-token` | 自动生成 | 认证令牌 |

### 暴露的工具列表

当以 Server 模式运行时，以下工具会暴露给 MCP 客户端：

#### 核心工具

| 工具名 | 参数 | 说明 |
|--------|------|------|
| `run_task` | task, context? | 运行完整任务（等同于 `hermes run`） |
| `search_memory` | query, limit? | 搜索历史记忆 |
| `add_note` | content, tags? | 添加新笔记 |
| `list_notes` | tag_filter? | 列出所有笔记 |
| `delegate_task` | task, tools?, timeout? | 创建子代理执行任务 |
| `list_skills` | - | 列出已学技能 |
| `create_skill` | name, description, content? | 创建新技能 |
| `web_search` | query, num_results? | 网页搜索 |
| `read_file` | path, offset?, limit? | 读取文件内容 |
| `write_file` | path, content | 写入文件 |
| `execute_command` | command, timeout? | 执行终端命令 |
| `browser_navigate` | url | 浏览器导航到 URL |
| `browser_click` | selector | 点击页面元素 |
| `browser_extract` | selector, extract_type? | 提取页面数据 |

---

## Client 模式（连接外部服务）

### 连接 MCP Server

```bash
# 方式1：通过命令行添加
hermes mcp connect --name my-database \
  --type sse \
  --url http://localhost:3000/sse

# 方式2：通过 JSON 配置
hermes mcp connect '{
  "name": "postgres-db",
  "type": "sse",
  "url": "http://localhost:3000/mcp",
  "headers": {"Authorization": "Bearer token123"}
}'

# 方式3：从配置文件加载
hermes mcp connect --config ./mcp-servers.json
```

### 配置文件格式 (`~/.hermes/mcp_servers.json`)

```json
{
  "mcpServers": {
    "database": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres", 
               "postgresql://user:pass@localhost:5432/mydb"],
      "env": {}
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", 
               "/path/to/allowed/directory"],
      "env": {}
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_..."
      }
    },
    "slack": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-slack"],
      "env": {
        "SLACK_BOT_TOKEN": "xoxb-...",
        "SLACK_APP_TOKEN": "xapp-..."
      }
    },
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": {
        "BRAVE_API_KEY": "your-key"
      }
    },
    "puppeteer": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-puppeteer"]
    },
    "fetch": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-fetch"]
    }
  }
}
```

### 管理 MCP 连接

```bash
# 列出已连接的 MCP 服务
hermes mcp list

# 显示某个服务的可用工具
hermes mcp tools database

# 断开连接
hermes mcp disconnect database

# 断开所有连接
hermes mcp disconnect --all

# 测试连接
hermes mcp test database
```

---

## 工具过滤与安全

### Server 端工具过滤

当 Hermes 作为 MCP Server 运行时，可以限制暴露的工具：

```bash
# 只暴露特定工具
hermes mcp serve --stdio \
  --allowed-tools "run_task,search_memory,web_search"

# 排除危险工具
hermes mcp serve --stdio \
  --blocked-tools "execute_command,write_file,browser_*"

# 组合使用
hermes mcp serve --stdio \
  --allowed-tools "run_task,search_memory,list_notes" \
  --blocked-tools ""
```

### Client 端工具命名空间

来自 MCP Client 的工具会被自动加上命名空间前缀：

```bash
# 假设连接了 postgres 和 github 两个 MCP Server

# 来自 postgres 的工具：
postgres:query
postgres:list_tables
postgres:get_schema

# 来自 github 的工具：
github:search_issues
github:create_issue
github:get_file_contents

# Hermes 内置工具保持原样：
run_task
search_memory
delegate_task
```

### 安全最佳实践

```yaml
# ~/.hermes/config.yaml
security:
  mcp:
    # Server 模式设置
    server:
      require_authentication: true
      auth_token_env: HERMES_MCP_AUTH_TOKEN
      allowed_origins:            # CORS 白名单
        - "vscode-webview://*"
        - "windsurf://*"
      
    # Client 模式设置
    client:
      allow_untrusted_servers: false  # 只允许预配置的服务器
      timeout_per_tool: 60           # 每个 MCP 工具超时时间
      
    # 审计日志
    audit_log:
      enabled: true
      log_mcp_calls: true
      include_params: false          # 不记录敏感参数
```

---

## IDE 配置

### Cursor 配置

在 `.cursor/mcp.json` 中添加：

```json
{
  "mcpServers": {
    "hermes": {
      "command": "hermes",
      "args": ["mcp", "serve", "--stdio", 
               "--allowed-tools", "run_task,search_memory,web_search,read_file,write_file"]
    }
  }
}
```

### VS Code + Claude Code 配置

在 `.vscode/settings.json` 或 Claude Code 配置中：

```json
{
  "mcpServers": {
    "hermes-agent": {
      "command": "/Users/username/.local/bin/hermes",
      "args": [
        "mcp", 
        "serve", 
        "--stdio",
        "--model", "anthropic/claude-haiku",
        "--allowed-tools", "run_task,search_memory,web_search,file_operations,execute_code"
      ]
    }
  }
}
```

### Windsurf 配置

在 `.windsurf/mcp.json` 中：

```json
{
  "servers": {
    "hermes": {
      "command": "hermes",
      "args": ["mcp", "serve", "--stdio"]
    }
  }
}
```

### Zed 编辑器配置

在 `settings.json` 中：

```json
{
  "mcp_servers": {
    "hermes": {
      "command": "hermes",
      "args": ["mcp", "serve", "--stdio"]
    }
  }
}
```

---

## 高级用法

### 1. 多实例部署

同时运行多个 Hermes MCP Server，每个有不同的模型和能力配置：

```bash
# 实例1：轻量级快速任务（Haiku）
HERMES_MCP_PORT=8081 hermes mcp serve --port 8081 \
  --model anthropic/claude-haiku \
  --allowed-tools "run_task,search_memory" &

# 实例2：深度研究任务（Sonnet）
HERMES_MCP_PORT=8082 hermes mcp serve --port 8082 \
  --model anthropic/claude-sonnet \
  --allowed-tools "run_task,web_search,browser,delegation" &

# 实例3：代码任务（GPT-4o）
HERMES_MCP_PORT=8083 hermes mcp serve --port 8083 \
  --model openai/gpt-4o \
  --allowed-tools "run_task,file_operations,code_execution,terminal" &
```

IDE 配置中选择不同的端口连接不同能力的实例。

### 2. 链式 MCP 调用

Hermes 作为中间层，串联多个 MCP 服务：

```
IDE → Hermes MCP Server → [Hermes 内部处理]
                           ↓
                    Hermes MCP Client A → PostgreSQL
                    Hermes MCP Client B → GitHub API
                    Hermes MCP Client C → Slack
```

Hermes 可以智能地根据任务需求选择调用哪个外部 MCP 工具。

### 3. 自定义工具包装

将外部 MCP 工具包装为 Hermes 的原生技能：

```python
# 包装脚本示例
def wrap_mcp_tool(ctx, tool_name, params):
    """
    将 MCP 工具调用包装为 Hermes 技能
    """
    result = call_mcp_client("my-server", tool_name, params)
    
    # 后处理结果
    if tool_name.startswith("db:"):
        return format_as_markdown_table(result)
    elif tool_name.startswith("gh:"):
        return format_github_result(result)
    
    return result

ctx.register_tool(
    name="query_database_via_mcp",
    schema=db_schema,
    handler=lambda p: wrap_mcp_tool(ctx, f"db:query", p)
)
```

### 4. 性能优化

```yaml
# config.yaml
mcp:
  server:
    # 缓存常用查询结果
    cache_enabled: true
    cache_ttl: 300          # 缓存有效期（秒）
    
    # 并发控制
    max_concurrent_requests: 5
    
    # 流式响应
    streaming_enabled: true
    
  client:
    # 连接池
    connection_pool_size: 10
    
    # 重试策略
    retry_attempts: 3
    retry_backoff: 1s
    
    # 请求超时
    request_timeout: 30s
```

---

## 故障排除

### 常见问题

#### Q: MCP Server 启动失败

```bash
# 检查依赖
hermes doctor

# 查看 MCP 相关日志
hermes logs --level ERROR | grep -i mcp

# 手动测试 stdio 模式
echo '{"jsonrpc":"2.0","method":"initialize","params":{"capabilities":{}},"id":1}' | hermes mcp serve --stdio
```

#### Q: IDE 无法连接到 MCP Server

1. **检查路径**: 确保 `hermes` 命令在 PATH 中
2. **检查权限**: 确保 IDE 有权限执行 shell 命令
3. **检查参数**: 确保 `args` 数组格式正确
4. **测试连接**: 在终端手动运行相同命令验证

```bash
# Cursor/VSCODE 的调试方法
hermes mcp serve --stdio &
# 输入 JSON-RPC 测试消息
echo '{"jsonrpc":"2.0","method":"tools/list","id":1}'
```

#### Q: MCP Client 连接超时

```bash
# 测试外部 MCP Server 是否可达
curl -v http://localhost:3000/sse

# 检查网络配置
hermes mcp test <server-name>

# 增加超时时间
hermes mcp connect ... --timeout 120
```

#### Q: 工具名称冲突

当 Hermes 内置工具和 MCP Client 工具同名时，MCP 工具会自动加前缀。如果需要自定义前缀：

```yaml
mcp:
  client:
    namespace_prefix: true           # 启用命名空间前缀（默认开启）
    namespace_separator: ":"         # 分隔符
    conflict_resolution: "prefix"    # prefix | rename | error
```

### 调试模式

```bash
# 启用详细调试日志
HERMES_LOG_LEVEL=DEBUG hermes mcp serve --stdio

# 查看所有 MCP 通信
hermes logs --follow | grep -i mcp
```

---

## 参考资源

- **MCP 规范**: https://modelcontextprotocol.io/
- **官方 SDK**: https://github.com/modelcontextprotocol/python-sdk
- **社区服务器**: https://mcp.so/
- **Hermes MCP 源码**: `mcp_serve.py`
