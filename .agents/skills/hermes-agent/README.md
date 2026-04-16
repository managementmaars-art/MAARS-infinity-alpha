# Hermes Agent Skill 🏥

> 通用可移植的 Hermes Agent 集成 Skill，适用于 WorkBuddy / Claude Code / Cursor 等 AI Agent 平台。

[![Version](https://img.shields.io/badge/version-2.0.0-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()
[![Hermes](https://img.shields.io/badge/Hermes-v0.8.0-purple)]()

## ✨ 功能特性

- 🚀 **自改进技能系统** — 从任务中自动创建可复用技能
- 🧠 **持久化记忆** — FTS5 全文搜索 + LLM 摘要
- 🤖 **子代理委托** — 任务隔离和并行处理
- 🔌 **MCP 双向集成** — Model Context Protocol 支持
- 🌐 **浏览器自动化** — Web 页面交互
- 💻 **代码执行** — 沙盒内安全执行
- 🔍 **网页研究** — 信息检索与分析

## 📦 安装

### 方式一：一键安装（推荐）

```bash
npx skills add chunhaixu/hermes-agent-skill@hermes-agent -g -y
```

### 方式二：手动安装

```bash
# 1. 克隆仓库
git clone https://github.com/chunhaixu/hermes-agent-skill.git

# 2. 复制到 Skill 目录
cp -r hermes-agent-skill ~/.workbuddy/skills/hermes-agent

# 3. 运行安装脚本
bash ~/.workbuddy/skills/hermes-agent/scripts/install_hermes.sh

# 4. 配置 API Key
nano ~/.hermes/.env
```

## ⚙️ 配置

### API Key 配置

编辑 `~/.hermes/.env`，添加你的 LLM 提供商密钥：

```bash
# 智谱 AI（推荐）
GLM_API_KEY=your_key_here

# 或 OpenRouter
OPENROUTER_API_KEY=your_key_here

# 或 Anthropic
ANTHROPIC_API_KEY=your_key_here
```

### 模型配置

编辑 `~/.hermes/config.yaml`：

```yaml
model:
  default: "glm-5"          # 默认模型
  provider: "zai"           # 提供商: zai / openrouter / anthropic / ...
  base_url: "https://api.z.ai/api/paas/v4"
```

## 🔧 使用

安装后，在 AI Agent 中使用以下触发词：

| 触发词 | 说明 |
|--------|------|
| `使用 hermes` | 激活 Hermes Agent |
| `hermes run "任务"` | 执行单轮任务 |
| `hermes memory search "关键词"` | 搜索记忆 |
| `hermes delegate "复杂任务"` | 子代理委托 |
| `hermes skills list` | 查看已学技能 |

## 🏗️ 项目结构

```
hermes-agent-skill/
├── SKILL.md              # Skill 描述文件（Agent 自动加载）
├── _meta.json            # 元数据（版本、依赖、触发词等）
├── scripts/
│   ├── install_hermes.sh    # 一键安装脚本
│   ├── hermes_wrapper.sh    # CLI 统一封装
│   └── hermes_delegate.sh   # 子代理委托脚本
└── references/
    ├── cli-commands.md           # CLI 命令参考
    ├── config-guide.md           # 配置指南
    ├── mcp-integration.md        # MCP 集成
    ├── plugin-development.md     # 插件开发
    └── self-improving-integration.md  # 自改进系统
```

## 🔗 相关链接

- [Hermes Agent 官方仓库](https://github.com/NousResearch/hermes-agent)
- [Skills.sh - Agent Skill 生态](https://skills.sh/)
- [智谱 AI 开放平台](https://open.bigmodel.cn)

## 📄 License

MIT License
