# Plan Mode 计划模式

在实施代码前创建和维护实施计划的 Skill。专注于需求澄清、技术调研和分阶段规划。

## 功能特性

- 📋 **计划优先**：在编码前先规划，避免返工
- 🔍 **技术调研**：使用 Context7 查询最新技术文档
- 📁 **结构化输出**：计划文档统一存放在 `.plan/` 目录
- 🔄 **子计划支持**：复杂步骤可拆分为独立子计划
- 🎯 **边界清晰**：仅规划不实施，专注方案设计
- 📝 **来源追溯**：所有外部事实均附来源链接

## 依赖要求

⚠️ **使用本 Skill 前必须安装 context7 MCP**

本 Skill 依赖 [context7](https://github.com/upstash/context7-mcp) MCP 服务用于技术文档查询，请根据您使用的工具选择对应的安装方式。

### MCP 依赖安装

#### Claude Code 安装方式

##### **类 Unix (macOS/Linux)**

```bash
claude mcp add --scope user context7 -- npx -y @upstash/context7-mcp@latest
```

##### **Windows (PowerShell)**

```powershell
claude mcp add --scope user context7 -- cmd /c npx -y @upstash/context7-mcp@latest
```

#### Codex 安装方式

##### **类 Unix (macOS/Linux)**

```bash
codex mcp add context7 -- npx -y @upstash/context7-mcp@latest
```

##### **Windows (PowerShell)**

```powershell
codex mcp add context7 -- cmd /c npx -y @upstash/context7-mcp@latest
```

### 验证 MCP 安装

安装完成后，可通过以下方式验证：

#### **Claude Code**：

```bash
claude mcp list
```

或在 Claude Code 会话中使用：

```
/mcp
```

#### **Codex**：

```bash
codex mcp list
```

## 安装 Skill

使用 npx 方式安装：

```bash
npx skills add https://github.com/karthrand/karthrand-ai-public.git --skill plan-mode
```

## 使用方式

在 cli编码工具 中直接调用：

```
/plan-mode 你的需求描述
```

**示例**：

```
/plan-mode 实现用户登录鉴权改造
```

## 输出结构

计划文档将存放在项目根目录的 `.plan/` 文件夹下：

```text
{project-root}/.plan/
├── current/          # 当前进行中的计划
├── archive/          # 已完成或废弃的计划
└── index.json        # 计划索引元数据
```

## 工作流程

1. **分析请求**：判断是新建计划、更新计划还是拆分子计划
2. **项目检查**：在提问前先检查本地项目
3. **需求澄清**：仅在本地检查无法解决时提出一个聚焦问题
4. **技术调研**：使用 Context7 验证技术事实
5. **编写计划**：基于模板生成结构化计划文档
6. **更新索引**：维护 index.json 元数据
7. **输出摘要**：返回简洁总结等待用户审查
