---
name: plugin-builder
description: 创建和管理私有 Claude Code 插件。当用户想要创建自己的插件、打包 skills/agents/commands/hooks/MCP 配置时使用此 skill。触发场景包括："创建插件"、"打包我的 skills"、"发布我的插件"、"迁移插件"等。
---

# Plugin Builder

帮助你创建和管理私有 Claude Code 插件的 skill。

## 工作流程

### 阶段1：捕获意图

首先了解用户的目标：

1. **创建新仓库** - 从零开始创建一个插件仓库
2. **迁移现有内容** - 将散落的 skills/agents 整理成仓库
3. **更新现有仓库** - 修改已存在的 marketplace 配置

询问用户：
- **托管平台**：GitHub 还是 GitLab（支持自托管 GitLab 实例）
- 仓库名称（如：`my-claude-plugins`）
- 用户名/命名空间（GitHub: username，GitLab: group/namespace）
- 要包含的组件类型（Skills/Agents/Commands/Hooks/MCP）
- 是否有现有内容需要迁移
- **私有仓库**：是否需要配置访问令牌

### 阶段2：规划结构

根据用户需求，规划仓库结构：

```
<repo-name>/
├── .claude-plugin/
│   ├── plugin.json        # 插件清单
│   └── marketplace.json   # 市场配置
├── skills/                # Skills 目录
├── agents/                # Agents 目录
├── commands/              # 斜杠命令目录
├── hooks/                 # 事件钩子
│   └── hooks.json
├── .mcp.json              # MCP 服务器配置
└── README.md              # 说明文档
```

### 阶段3：创建配置文件

#### 3.1 创建 `.claude-plugin/plugin.json`

使用模板生成，包含：
- `name`：插件标识符
- `version`：语义化版本（如 1.0.0）
- `description`：插件描述
- `author`：作者信息
- `skills`/`agents`/`commands`/`hooks`/`mcpServers`：组件路径

参考 `templates/plugin.json.tmpl` 和 `references/plugin-json-schema.md`

#### 3.2 创建 `.claude-plugin/marketplace.json`

定义 marketplace 目录：
- `name`：marketplace 名称
- `owner`：所有者信息
- `plugins`：插件列表

参考 `templates/marketplace.json.tmpl` 和 `references/marketplace-json-schema.md`

### 阶段4：迁移/创建内容

帮助用户：

1. **创建 Skill**
   - 使用 `templates/SKILL.md.tmpl`
   - 参考 `references/skill-structure-guide.md`

2. **创建 Agent**
   - 使用 `templates/agent.md.tmpl`

3. **创建 Command**
   - 创建 Markdown 文件 + YAML frontmatter
   - 放在 `commands/` 目录

4. **配置 Hooks**
   - 在 `hooks/hooks.json` 中定义事件钩子

5. **配置 MCP**
   - 在 `.mcp.json` 中定义 MCP 服务器

### 阶段5：验证

运行验证脚本检查配置：

```bash
python scripts/validate_plugin.py <path-to-plugin>
```

验证项目：
- plugin.json 格式正确
- marketplace.json 格式正确
- 所有引用的文件存在
- SKILL.md 文件格式正确

### 阶段6：发布指导

根据用户选择的平台提供相应的使用说明：

#### GitHub 仓库

```bash
# 添加 marketplace
/plugin marketplace add <username>/<repo-name>

# 安装插件
/plugin install <plugin-name>@<repo-name>

# 更新插件
/plugin update <plugin-name>@<repo-name>
```

#### GitLab 仓库

```bash
# 添加 marketplace（需要指定 gitlab 源类型）
/plugin marketplace add <namespace>/<project-name> --source gitlab

# 或使用完整 URL
/plugin marketplace add https://gitlab.com/<namespace>/<project-name>

# 安装插件
/plugin install <plugin-name>@<marketplace-name>
```

**GitLab 特殊说明**：
- 支持私有仓库（需要配置访问令牌）
- 支持自托管 GitLab 实例
- 需要在 settings.json 中配置 GitLab 访问凭据

详见 `references/gitlab-integration.md`

## 模板和参考

### 参考文档

| 文件 | 说明 |
|------|------|
| `references/plugin-json-schema.md` | plugin.json 字段说明 |
| `references/marketplace-json-schema.md` | marketplace.json 字段说明 |
| `references/skill-structure-guide.md` | Skill 结构指南 |
| `references/gitlab-integration.md` | GitLab 集成指南 |

### 模板文件

| 文件 | 说明 |
|------|------|
| `templates/plugin.json.tmpl` | plugin.json 模板 |
| `templates/marketplace.json.tmpl` | marketplace.json 模板 |
| `templates/SKILL.md.tmpl` | Skill 模板 |
| `templates/agent.md.tmpl` | Agent 模板 |

## 使用模板

创建新组件时，从 `templates/` 目录读取对应模板并填充用户信息：

1. 读取模板文件
2. 替换 `{{变量名}}` 占位符
3. 保存到目标位置

## 最佳实践

1. **保持简洁** - 每个插件职责单一
2. **版本管理** - 使用语义化版本号（Semantic Versioning）
3. **文档完善** - 提供 README 说明用法
4. **测试验证** - 发布前验证配置正确性
5. **许可清晰** - 在 plugin.json 中指定许可证

## 快速开始示例

```bash
# 1. 创建仓库目录
mkdir my-claude-plugins && cd my-claude-plugins

# 2. 初始化 plugin 结构
python ~/.claude/skills/plugin-builder/scripts/init_marketplace.py

# 3. 编辑配置文件
# - .claude-plugin/plugin.json
# - .claude-plugin/marketplace.json

# 4. 验证配置
python ~/.claude/skills/plugin-builder/scripts/validate_plugin.py .

# 5. 提交到 Git 仓库
git init
git add .
git commit -m "Initial plugin setup"
git push origin main
```
