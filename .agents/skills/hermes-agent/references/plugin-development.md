# Hermes Agent 插件开发指南

> **版本**: v0.8.0 | **最后更新**: 2026-04-11

## 目录

1. [插件概述](#插件概述)
2. [目录结构](#目录结构)
3. [插件类型](#插件类型)
4. [开发流程](#开发流程)
5. [API 参考](#api-参考)
6. [钩子系统](#钩子系统)
7. [发布与分发](#发布与分发)
8. [示例插件](#示例插件)

---

## 插件概述

Hermes 的插件系统允许用户在不修改核心代码的情况下扩展功能，支持：

| 能力 | 说明 |
|------|------|
| **自定义工具** | 添加新的 LLM 可调用工具 |
| **生命周期钩子** | 在关键事件点执行自定义逻辑 |
| **CLI 命令扩展** | 添加 `hermes <plugin>` 子命令 |
| **技能绑定** | 随插件分发技能文件 |
| **数据文件打包** | 包含配置、模板等资源 |

---

## 目录结构

```
my-plugin/
├── plugin.yaml          # 插件清单（必需）
├── __init__.py          # 注册函数（必需）
├── schemas.py           # 工具模式定义
├── tools.py             # 工具处理器实现
├── data/                # 数据文件（可选）
│   └── config.json
└── skill.md             # 绑定的技能（可选）
```

### plugin.yaml 格式

```yaml
name: my-plugin-name           # 插件标识符（必需）
version: "1.0.0"              # 语义化版本（必需）
description: 简短描述插件的功能 # 用户可见的描述（推荐）
author: Your Name              # 作者信息（可选）
requires_env: []               # 需要的环境变量（可选，安装时提示用户配置）

# 插件类型（自动检测，通常不需要手动指定）
type: general                  # general | memory_provider | context_engine

# 兼容性
hermes_min_version: "0.7.0"   # 最低兼容版本（可选）
license: MIT                   # 许可证（可选）
repository: https://github.com/user/repo  # Git 仓库地址（可选）
```

### __init__.py 注册函数

```python
"""
我的 Hermes 插件 - 实现描述
"""

def register(ctx):
    """
    主注册函数。Hermes 加载插件时调用此函数。
    
    Args:
        ctx (PluginContext): 插件上下文对象，提供以下 API：
            - ctx.register_tool(name, schema, handler): 注册工具
            - ctx.register_hook(event_name, callback): 注册钩子
            - ctx.register_cli_command(name, help, setup_fn, handler_fn): 注册 CLI 命令
            - ctx.inject_message(content, role="user"): 注入消息
    """
    
    # 导入你的工具定义和处理器
    from .schemas import tool_schema
    from .tools import handle_tool_call
    
    # 注册自定义工具
    ctx.register_tool("my_tool_name", tool_schema, handle_tool_call)
    
    # 注册钩子（可选）
    def on_tool_complete(tool_name, params, result):
        print(f"[my-plugin] Tool {tool_name} completed")
        
    ctx.register_hook("post_tool_call", on_tool_complete)
```

---

## 插件类型

### 1. 通用插件 (General Plugin)

最灵活的插件类型，可以添加任意数量的工具和钩子。

```yaml
# plugin.yaml
name: weather-plugin
version: "1.0.0"
description: 天气查询插件
```

```python
# __init__.py
from .schemas import get_weather_schema
from .tools import get_weather_handler

def register(ctx):
    ctx.register_tool("get_weather", get_weather_schema, get_weather_handler)
```

### 2. 内存提供者 (Memory Provider)

替换或增强内置的记忆系统。

```yaml
# plugin.yaml
name: custom-memory
version: "1.0.0"
description: 自定义记忆后端
type: memory_provider
```

```python
# __init__.py
def register(ctx):
    """
    内存提供者需要实现特定接口：
    - search(query) -> List[Note]
    - add(note) -> Note
    - list_notes() -> List[Note]
    - delete(note_id) -> bool
    """
    class CustomMemoryBackend:
        def search(self, query):
            # 你的搜索实现
            pass
            
        def add(self, content, tags=None):
            # 你的添加实现
            pass
    
    ctx.set_memory_backend(CustomMemoryBackend())
```

**可用的内存提供者类型**:

| 后端名 | 特点 |
|--------|------|
| `built-in` | 默认，SQLite + FTS5 |
| `honcho` | AI 原生方言建模 |
| `mem0` | 开源记忆服务 |
| `openviking` | 高级向量检索 |
| `hindsight` | 时间线记忆 |
| `holographic` | 全息记忆系统 |

### 3. 上下文引擎 (Context Engine)

替换内置的上下文压缩器。

```yaml
# plugin.yaml
name: smart-context
version: "1.0.0"
description: 智能上下文压缩
type: context_engine
```

```python
# __init__.py
def register(ctx):
    class SmartContextEngine:
        def compress(self, messages, max_tokens):
            # 自定义的上下文压缩逻辑
            pass
            
        def summarize(self, text, target_length):
            # 自定义摘要逻辑
            pass
    
    ctx.set_context_engine(SmartContextEngine())
```

---

## 开发流程

### 步骤 1：创建插件骨架

```bash
mkdir -p ~/.hermes/plugins/my-plugin
cd ~/.hermes/plugins/my-plugin
touch plugin.yaml __init__.py schemas.py tools.py
```

### 步骤 2：编写 plugin.yaml

```yaml
name: my-awesome-plugin
version: "0.1.0"
description: 我的第一款 Hermes 插件
author: Your Name
```

### 步骤 3：定义工具模式 (schemas.py)

```python
"""
工具模式定义 - LLM 看到的接口说明
"""

tool_schema = {
    "name": "awesome_tool",
    "description": "这个工具做什么的详细描述",
    "parameters": {
        "type": "object",
        "properties": {
            "param1": {
                "type": "string",
                "description": "参数1的说明",
            },
            "param2": {
                "type": "integer",
                "description": "参数2的说明",
                "default": 10,
            },
            "options": {
                "type": "array",
                "items": {"type": "string"},
                "description": "可选选项列表",
            }
        },
        "required": ["param1"],
    }
}
```

### 步骤 4：实现工具处理器 (tools.py)

```python
"""
工具处理器 - 实际执行逻辑
"""

import json

def handle_tool_call(params: dict) -> str:
    """
    处理工具调用。
    
    Args:
        params: 从 LLM 调用中接收到的参数字典
        
    Returns:
        str: 返回给 LLM 的结果字符串（会被添加到对话历史中）
    """
    param1 = params.get("param1", "")
    param2 = params.get("param2", 10)
    options = params.get("options", [])
    
    try:
        # === 在这里实现你的业务逻辑 ===
        
        result = f"处理结果: param1={param1}, param2={param2}"
        
        if options:
            result += f", options={', '.join(options)}"
            
        return result
        
    except Exception as e:
        # 错误处理：返回有意义的错误信息给 LLM
        return f"错误: 执行失败 - {str(e)}"

# 如果有多个工具，可以定义多个 schema/handler 对
another_tool_schema = {
    "name": "another_tool",
    "description": "另一个工具",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "查询内容"}
        },
        "required": ["query"]
    }
}

def another_handler(params: dict) -> str:
    query = params.get("query", "")
    return f"查询 '{query}' 的结果是..."
```

### 步骤 5：在 __init__.py 中注册

```python
"""My Awesome Plugin for Hermes Agent."""

def register(ctx):
    """Register all tools and hooks with Hermes."""
    
    # 导入本地模块
    from .schemas import tool_schema, another_tool_schema
    from .tools import handle_tool_call, another_handler
    
    # 注册工具 1
    ctx.register_tool(
        name="awesome_tool",
        schema=tool_schema,
        handler=handle_tool_call
    )
    
    # 注册工具 2
    ctx.register_tool(
        name="another_tool",
        schema=another_tool_schema,
        handler=another_handler
    )
    
    # 注册钩子（可选）
    def log_tool_usage(tool_name, params, result):
        """记录每次工具调用到日志文件"""
        import json
        from datetime import datetime
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "tool": tool_name,
            "params": params,
            "success": not str(result).startswith("错误")
        }
        
        with open("/tmp/plugin-tool-usage.log", "a") as f:
            f.write(json.dumps(log_entry) + "\n")
            
    ctx.register_hook("post_tool_call", log_tool_usage)
    
    # 注册 CLI 命令（可选）
    def setup_parser(parser):
        """设置 CLI 参数解析器"""
        parser.add_argument("--verbose", action="store_true")
        parser.add_argument("--output-format", choices=["json", "text"], default="text")
        
    def cmd_handler(args):
        """处理 CLI 命令"""
        print(f"My plugin running with verbose={args.verbose}")
        
    ctx.register_cli_command(
        name="my-plugin",
        help="我的插件的自定义命令",
        setup_fn=setup_parser,
        handler_fn=cmd_handler
    )
```

### 步骤 6：安装和测试

```bash
# 安装插件（从本地路径）
hermes plugins install /path/to/my-plugin

# 或从 Git 安装
hermes plugins install https://github.com/you/my-plugin.git

# 启用插件
hermes plugins enable my-plugin

# 测试插件是否加载
hermes plugins list

# 在对话中测试
hermes run "使用 awesome_tool 工具，参数 param1=test" --non-interactive --no-stream
```

---

## API 参考

### PluginContext API

#### `ctx.register_tool(name, schema, handler)`

注册一个可供 LLM 调用的工具。

**参数**:
- `name` (str): 工具名称，全局唯一
- `schema` (dict): JSON Schema 格式的工具定义
- `handler` (callable): 处理函数 `(params: dict) -> str`

**示例**:
```python
ctx.register_tool("my_tool", {...}, lambda p: "result")
```

#### `ctx.register_hook(event_name, callback)`

注册生命周期钩子。

**可用事件**:

| 事件名 | 回调签名 | 触发时机 |
|--------|----------|----------|
| `pre_tool_call` | `(tool_name, params)` | 工具执行前 |
| `post_tool_call` | `(tool_name, params, result)` | 工具执行后 |
| `pre_llm_call` | `(messages, kwargs)` | LLM 调用前，可返回 `{"context": "..."}` 注入上下文 |
| `post_llm_call` | `(response, messages)` | LLM 调用成功后 |
| `on_session_start` | `(session_id)` | 新会话创建时 |
| `on_session_end` | `(session_id)` | 会话结束时 |

#### `ctx.register_cli_command(name, help, setup_fn, handler_fn)`

注册 CLI 子命令。

**参数**:
- `name` (str): 命令名称（如 `my-cmd`，调用方式为 `hermes my-cmd`）
- `help` (str): 帮助文本
- `setup_fn` (callable): 设置参数解析器 `(parser) -> None`
- `handler_fn` (callable): 处理命令 `(args) -> None`

#### `ctx.inject_message(content, role="user")`

向当前会话注入消息。

**示例**:
```python
ctx.inject_message("注意：用户偏好是使用中文回复。", role="system")
```

---

## 钩子系统

### 钩子执行顺序

```
用户输入 → pre_llm_call → [LLM 调用] → post_llm_call 
                                    ↓
                              解析工具调用
                                    ↓
                              pre_tool_call → [工具执行] → post_tool_call
                                    ↓
                              返回响应
```

### 高级钩子用法

#### 1. 上下文注入

在每次 LLM 调用前注入额外的上下文信息：

```python
def inject_user_preferences(messages, kwargs):
    """注入用户偏好的上下文"""
    preferences = load_user_preferences()  # 你自己的函数
    
    context_text = (
        f"当前用户偏好:\n"
        f"- 语言: {preferences['language']}\n"
        f"- 时区: {preferences['timezone']}\n"
        f"- 专业领域: {preferences['domain']}\n"
    )
    
    return {"context": context_text}

ctx.register_hook("pre_llm_call", inject_user_preferences)
```

#### 2. 工具调用审计

记录所有工具调用的完整日志：

```python
def audit_tool_calls(tool_name, params, result):
    """审计所有工具调用"""
    import logging
    
    logger = logging.getLogger("plugin.audit")
    logger.info({
        "tool": tool_name,
        "params": params,
        "result_length": len(str(result)),
        "timestamp": time.time()
    })

ctx.register_hook("post_tool_call", audit_tool_calls)
```

#### 3. 敏感操作确认

对危险操作进行二次确认：

```python
def confirm_destructive_actions(tool_name, params):
    """拦截破坏性操作"""
    destructive_patterns = [
        ("file_delete", ["rm", "delete"]),
        ("execute_command", ["rm -rf", "sudo"]),
    ]
    
    for t_tool, t_keywords in destructive_patterns:
        if tool_name == t_tool:
            for kw in t_keywords:
                params_str = str(params).lower()
                if kw in params_str:
                    raise PermissionError(
                        f"⚠️ 危险操作被拦截: {tool_name} 包含关键词 '{kw}'"
                    )

ctx.register_hook("pre_tool_call", confirm_destructive_actions)
```

---

## 发布与分发

### 本地安装

```bash
# 从本地目录安装
hermes plugins install /path/to/my-plugin

# 或直接复制到插件目录
cp -r my-plugin ~/.hermes/plugins/
hermes plugins enable my-plugin
```

### 通过 Git 分发

```bash
# 从 GitHub 安装
hermes plugins install owner/repo
hermes plugins install https://github.com/owner/repo.git

# 从私有仓库安装（需认证）
hermes plugins install git@github.com:owner/private-repo.git
```

### 通过 Pip 分发

在 `pyproject.toml` 中添加入口点：

```toml
[project.entry-points."hermes_agent.plugins"]
my_plugin = "my_package:register"
```

用户通过 `pip install your-package` 即可安装。

### 更新插件

```bash
# 更新单个插件
hermes plugins update my-plugin

# 更新所有已安装的插件
hermes plugins update --all
```

---

## 示例插件

### 示例 1：天气查询插件

```yaml
# plugin.yaml
name: weather-plugin
version: "1.0.0"
description: 使用 OpenWeatherMap API 查询天气
requires_env: [OPENWEATHERMAP_API_KEY]
author: Example Author
```

```python
# __init__.py
"""Weather Query Plugin for Hermes Agent."""
import os

def register(ctx):
    from .schemas import weather_schema, forecast_schema
    from .tools import get_current_weather, get_forecast
    
    ctx.register_tool("get_current_weather", weather_schema, get_current_weather)
    ctx.register_tool("get_weather_forecast", forecast_schema, get_forecast)
```

```python
# schemas.py
weather_schema = {
    "name": "get_current_weather",
    "description": "获取指定城市的当前天气情况",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "城市名称，如 'Beijing'、'New York'"
            },
            "units": {
                "type": "string",
                "enum": ["metric", "imperial"],
                "default": "metric",
                "description": "温度单位"
            }
        },
        "required": ["city"]
    }
}

forecast_schema = {
    "name": "get_weather_forecast",
    "description": "获取未来几天的天气预报",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "城市名称"
            },
            "days": {
                "type": "integer",
                "description": "预报天数（1-7）",
                "default": 3
            }
        },
        "required": ["city"]
    }
}
```

```python
# tools.py
"""Weather tool implementations."""
import os
import requests

API_KEY = os.environ.get("OPENWEATHERMAP_API_KEY", "")
BASE_URL = "https://api.openweathermap.org/data/2.5"

def get_current_weather(params: dict) -> str:
    city = params["city"]
    units = params.get("units", "metric")
    
    url = f"{BASE_URL}/weather?q={city}&appid={API_KEY}&units={units}"
    
    response = requests.get(url, timeout=10)
    
    if response.status_code != 200:
        return f"无法获取天气信息: {response.json().get('message', '未知错误')}"
    
    data = response.json()
    temp_unit = "°C" if units == "metric" else "°F"
    
    return (
        f"{city} 当前天气:\n"
        f"- 温度: {data['main']['temp']}{temp_unit}\n"
        f"- 体感温度: {data['main']['feels_like']}{temp_unit}\n"
        f"- 湿度: {data['main']['humidity']}%\n"
        f"- 风速: {data['wind'].get('speed', 0)} m/s\n"
        f"- 天气状况: {data['weather'][0]['description']}\n"
        f"- 能见度: {data.get('visibility', 'N/A')} m"
    )

def get_forecast(params: dict) -> string:
    city = params["city"]
    days = min(max(params.get("days", 3), 1), 7)  # 限制在 1-7 天
    
    url = f"{BASE_URL}/forecast?q={city}&appid={API_KEY}&units=metric&cnt={days * 8}"  # 每3小时一个数据点
    
    response = requests.get(url, timeout=10)
    
    if response.status_code != 200:
        return f"无法获取预报: {response.json().get('message', '未知错误')}"
    
    data = response.json()
    
    result = f"{city} 未来{days}天预报:\n\n"
    
    for item in data["list"][:days * 8]:  # 取前 N 天的数据
        dt = item["dt_txt"]
        temp = item["main"]["temp"]
        desc = item["weather"][0]["description"]
        result += f"{dt}: {temp}°C, {desc}\n"
    
    return result
```

### 示例 2：数据库查询插件

```python
# __init__.py
"""Database Query Plugin - 安全地执行 SQL 查询。"""

import sqlite3

def register(ctx):
    db_schema = {
        "name": "query_database",
        "description": "在 SQLite 数据库中执行只读 SQL 查询",
        "parameters": {
            "type": "object",
            "properties": {
                "db_path": {
                    "type": "string",
                    "description": "数据库文件路径"
                },
                "query": {
                    "type": "string",
                    "description": "SQL SELECT 查询语句"
                },
                "limit": {
                    "type": "integer",
                    "description": "最大返回行数（默认100）",
                    "default": 100
                }
            },
            "required": ["db_path", "query"]
        }
    }
    
    def execute_query(params: dict) -> str:
        db_path = params["db_path"]
        query = params["query"].strip()
        limit = params.get("limit", 100)
        
        # 安全检查：只允许 SELECT 语句
        if not query.upper().startswith("SELECT"):
            return "错误: 只允许 SELECT 查询语句"
        
        # 检查危险关键字
        dangerous = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "--", ";"]
        for word in dangerous:
            if word.upper() in query.upper():
                return f"错误: 查询包含不安全的关键字 '{word}'"
        
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            
            # 自动添加 LIMIT
            if "LIMIT" not in query.upper():
                query += f"\nLIMIT {limit}"
            
            cursor = conn.execute(query)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            
            conn.close()
            
            if not rows:
                return "查询返回空结果集"
            
            # 格式化输出为表格
            header = " | ".join(columns)
            separator = "-+-".join(["-" * len(c) for c in columns])
            lines = [header, separator]
            
            for row in rows[:limit]:
                line = " | ".join(str(v) for v in row)
                lines.append(line)
                
            return "\n".join(lines)
            
        except sqlite3.Error as e:
            return f"SQL 错误: {str(e)}"
        except Exception as e:
            return f"执行错误: {str(e)}"
    
    ctx.register_tool("query_database", db_schema, execute_query)
```
