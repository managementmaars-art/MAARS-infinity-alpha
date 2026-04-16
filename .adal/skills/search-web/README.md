# Search-Web

集成多源搜索的技术查询技能，整合 Context7 文档查询、Exa 网络搜索、DeepWiki 仓库文档和 github-fetcher 仓库文件读取。

## 前置条件

### 必需的 MCP 服务器

| MCP 工具 | 用途 | 类型 |
|----------|------|------|
| **context7** | 技术文档和代码示例查询 | stdio (npx) |
| **exa** | 网络搜索 | 远程 HTTP |
| **mcp-deepwiki** | GitHub 仓库文档查询 | stdio (npx) |
| **github-fetcher** | GitHub 仓库文件与目录读取 | stdio (npx) |

### 支持的 Code Agent

- Claude Code
- Codex
- OpenCode
- QwenCode

### 验证安装

- 直接询问 code agent 有哪些 skills
- 或运行 `bash scripts/detect.sh` 确认宿主识别正常

## 整体流程

```mermaid
flowchart TD
    Start([用户查询]) --> CheckState{运行 detect.sh 检查初始化状态}
    CheckState -->|缺失/不一致| CheckCreds{检查 credentials}
    CheckState -->|正常| ConfigCheck{配置项类问题?}

    CheckCreds -->|context7 hasApiKey=false| AskC7[询问是否配置 Context7 API Key]
    CheckCreds -->|exa hasApiKey=false| AskExa[询问是否配置 Exa API Key]
    CheckCreds -->|Key 齐全或已跳过| Setup[进入 setup 流程]
    AskC7 -->|用户提供| SaveC7Key[写入 credentials/context7]
    AskC7 -->|用户跳过| AskExa
    AskExa -->|用户提供| SaveExaKey[写入 credentials/exa]
    AskExa -->|用户跳过| Setup
    SaveC7Key --> CheckCreds
    SaveExaKey --> CheckCreds

    Setup --> Detect[1. detect.sh（无参数）]
    Detect --> CheckMCP[2. 逐项检测 4 个 MCP]
    CheckMCP -->|缺失| InstallMCP[3. setup-mcp.sh 安装<br/>自动从 credentials 读取 Key]
    CheckMCP -->|全部可用| WriteState[4. 创建 init_flag 标志文件]
    InstallMCP --> WriteState
    WriteState --> ConfigCheck

    ConfigCheck -->|是| ConfigStrategy[config-index-shortcut]
    ConfigCheck -->|否| C7Check{技术文档?}
    ConfigStrategy --> C7Check

    C7Check -->|是| C7[Context7: resolve --> query]
    C7Check -->|否| Exa[Exa 网络搜索]
    C7 --> Exa
    Exa --> ResultType{命中类型}
    ResultType -->|网页| WebRead[正文读取]
    ResultType -->|GitHub 文档| DeepWiki[mcp-deepwiki]
    ResultType -->|GitHub 文件| GHFetcher[github-fetcher]
    ResultType -->|普通| Collect[整理结果]

    WebRead --> Format[output-format 格式化]
    DeepWiki --> Format
    GHFetcher --> Format
    Collect --> Format
    Format --> Output([输出回答])

    style Start fill:#e1f5fe
    style Output fill:#e8f5e9
    style Setup fill:#fff3e0
    style InstallMCP fill:#ffebee
    style AskC7 fill:#fce4ec
    style AskExa fill:#fce4ec
```

## 手动初始化

首次使用前，需确保 4 个必需 MCP 已安装：

```bash
# 1. 检测环境（agent、os、state_dir、initialized 四项一次输出）
bash scripts/detect.sh

# 2. 使用脚本安装 MCP（推荐）
bash scripts/setup-mcp.sh --mcp context7
bash scripts/setup-mcp.sh --mcp exa
bash scripts/setup-mcp.sh --mcp mcp-deepwiki
bash scripts/setup-mcp.sh --mcp github-fetcher

# 或手动按宿主类型配置（见 references/setup.md）
```

完整初始化指南见 `references/setup.md`。

## MCP 使用边界

| 搜索目标 | 使用的 MCP | 说明 |
|---------|-----------|------|
| 技术文档 | Context7 | 固定顺序：先 resolve-library-id 再 query-docs |
| 网络搜索 | Exa | 不得使用其他搜索型 MCP 替代 |
| GitHub 仓库文档 | mcp-deepwiki | 仓库级别的文档概览和深读 |
| GitHub 仓库文件/目录 | github-fetcher | 读取具体文件内容或目录结构 |
| 网页正文 | 宿主提供的读取工具 | 仅在已知 URL 后使用，不能替代 Exa |

## 目录结构

```
search-web/
├── SKILL.md                              # 技能主文件
├── README.md                             # 本文件
├── scripts/
│   ├── detect.sh                         # 统一环境检测脚本（agent/os/state-dir）
│   └── setup-mcp.sh                      # MCP 安装脚本
├── references/
│   ├── setup.md                          # 初始化配置指南
│   ├── rules/
│   │   └── output-format.md              # 输出格式规范
│   └── strategies/
│       └── config-index-shortcut.md      # 配置索引直达策略
└── examples/
    └── usage.md                          # 使用示例
```
