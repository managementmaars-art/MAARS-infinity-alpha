# plugin.json 字段参考

## 自动发现机制

**重要**：Claude Code 使用自动发现机制来识别插件组件。

如果你的插件使用默认目录位置（`commands/`、`skills/`、`agents/` 等），`plugin.json` 是**可选的**，且**不需要**在配置文件中声明这些路径。

官方文档明确说明：
> "If your Plugin uses default directory locations (`commands/`, `skills/`, `agents/` etc.) and doesn't need custom configuration, `plugin.json` is **optional**."

### 默认目录结构

Claude Code 会自动发现以下目录中的组件：

| 组件类型 | 默认目录 | 说明 |
|---------|---------|------|
| Commands | `commands/` | 斜杠命令（`.md` 文件） |
| Agents | `agents/` | AI 代理（`.md` 文件） |
| Skills | `skills/` | 技能（含 `SKILL.md` 的子目录） |
| Hooks | `hooks/hooks.json` | 事件钩子配置 |
| MCP Servers | `.mcp.json` | MCP 服务器配置 |
| Settings | `.claude/plugin-name.local.md` | 插件设置 |

### 何时需要显式配置路径

仅当你使用**非默认目录名**时，才需要在 `plugin.json` 中声明路径。例如：

```json
{
  "name": "my-plugin",
  "commands": ["./my-commands/", "./contrib/commands/"],
  "skills": ["./custom-skills/"]
}
```

---

## 顶层字段

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `name` | string | 是 | 插件唯一标识符，kebab-case 格式 |
| `version` | string | 是 | 语义化版本号（如 1.0.0） |
| `description` | string | 是 | 插件描述 |
| `author` | object | 是 | 作者信息 |
| `homepage` | string | 否 | 主页 URL |
| `repository` | string | 否 | 仓库 URL |
| `license` | string | 否 | 许可证标识（如 MIT、Apache-2.0） |
| `keywords` | array | 否 | 关键词列表 |
| `skills` | array | 否 | **自定义** Skills 目录路径（非默认时使用） |
| `agents` | array | 否 | **自定义** Agents 目录路径（非默认时使用） |
| `commands` | array | 否 | **自定义** Commands 目录路径（非默认时使用） |
| `hooks` | string | 否 | **自定义** Hooks 配置文件路径（非默认时使用） |
| `mcpServers` | string | 否 | **自定义** MCP 服务器配置文件路径（非默认时使用） |

## author 对象

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `name` | string | 是 | 作者名称 |
| `email` | string | 否 | 作者邮箱 |
| `url` | string | 否 | 作者主页 |

## 组件路径数组

`skills`、`agents`、`commands` 字段为字符串数组，每个字符串表示相对于插件根目录的路径：

```json
{
  "skills": ["./skills/", "./contrib/skills/"],
  "agents": ["./agents/"],
  "commands": ["./commands/"]
}
```

## hooks 配置

`hooks` 字段指向一个 JSON 文件，格式如下：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "name": "log-tool-usage",
        "description": "记录工具调用"
      }
    ],
    "PostToolUse": [
      {
        "name": "analyze-results",
        "description": "分析工具结果"
      }
    ]
  }
}
```

## MCP 服务器配置

`mcpServers` 字段指向一个 JSON 文件，格式如下：

```json
{
  "mcpServers": {
    "server-name": {
      "command": "node",
      "args": ["path/to/server.js"],
      "env": {
        "API_KEY": "your-key"
      }
    }
  }
}
```

## 完整示例

### 标准配置（使用自动发现）

大多数插件只需要基础元数据，组件会被自动发现：

```json
{
  "name": "my-awesome-plugins",
  "version": "1.0.0",
  "description": "我的 Claude Code 插件集合",
  "author": {
    "name": "Your Name",
    "email": "your.email@example.com",
    "url": "https://example.com"
  },
  "homepage": "https://github.com/username/my-claude-plugins",
  "repository": "https://github.com/username/my-claude-plugins.git",
  "license": "MIT",
  "keywords": ["claude-code", "plugins", "productivity"]
}
```

### 自定义路径配置

仅当使用非默认目录时才需要声明路径：

```json
{
  "name": "my-custom-plugins",
  "version": "1.0.0",
  "description": "使用自定义目录的插件",
  "author": {
    "name": "Your Name"
  },
  "skills": ["./custom-skills/", "./contrib/skills/"],
  "agents": ["./my-agents/"],
  "commands": ["./user-commands/"]
}
```

## 语义化版本规范

版本号格式：`MAJOR.MINOR.PATCH`

- **MAJOR**：不兼容的 API 变更
- **MINOR**：向后兼容的功能新增
- **PATCH**：向后兼容的问题修复

示例：
- `1.0.0` - 初始版本
- `1.1.0` - 新增功能
- `1.1.1` - 问题修复
- `2.0.0` - 重大变更
