# Hermes Agent 配置指南

> **版本**: v0.8.0 | **最后更新**: 2026-04-11

## 目录

1. [API Key 配置](#api-key-配置)
2. [模型配置](#模型配置)
3. [提供商设置](#提供商设置)
4. [工具集配置](#工具集配置)
5. [记忆系统配置](#记忆系统配置)
6. [网关配置](#网关配置)
7. [安全配置](#安全配置)
8. [完整配置示例](#完整配置示例)

---

## API Key 配置

### 环境变量文件 (`~/.hermes/.env`)

这是存储所有敏感凭证的主要位置。**不要将此文件提交到版本控制系统！**

```bash
# ========================================
# 必需：至少配置一个 LLM 提供商
# ========================================

# OpenRouter（推荐，支持 200+ 模型）
OPENROUTER_API_KEY=sk-or-v1-your-key-here

# 或使用其他提供商：
# Anthropic (Claude)
ANTHROPIC_API_KEY=sk-ant-your-key-here

# OpenAI (GPT-4o, etc.)
OPENAI_API_KEY=sk-openai-your-key-here

# Google (Gemini)
GOOGLE_API_KEY=your-google-api-key

# ========================================
# 可选：增强功能
# ========================================

# Firecrawl - 高级网页抓取（比内置搜索更强大）
FIRECRAWL_API_KEY=fc-your-firecrawl-key

# FAL.ai - 图像生成（FLUX 模型）
FAL_KEY=your-fal-api-key

# ElevenLabs - 高级语音合成（替代免费的 Edge TTS）
ELEVENLABS_API_KEY=your-elevenlabs-key

# Brave Search - 网页搜索
BRAVE_API_KEY=your-brave-search-key

# OpenWeatherMap - 天气查询
OPENWEATHERMAP_API_KEY=your-weather-key

# GitHub Token - 用于 GitHub 集成
GITHUB_TOKEN=ghp_your-github-token

# ========================================
# 可选：消息平台
# ========================================

# Telegram Bot
TELEGRAM_BOT_TOKEN=your-telegram-bot-token

# Discord Bot
DISCORD_BOT_TOKEN=your-discord-bot-token

# Slack Bot
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
SLACK_APP_TOKEN=xapp-your-slack-app-token

# WhatsApp Bridge (需要单独配置)
# 参考文档: https://hermes-agent.nousresearch.com/docs/gateways/whatsapp/
```

### 获取 API Key 的途径

| 服务 | 获取地址 | 免费额度 |
|------|----------|----------|
| **OpenRouter** | https://openrouter.ai/keys | 注册即送少量额度 |
| **Anthropic** | https://console.anthropic.com/ | 新用户 $5 免费 |
| **OpenAI** | https://platform.openai.com/api-keys | 新用户 $5 免费 |
| **Google AI** | https://aistudio.google.com/apikey | 免费层可用 |
| **Firecrawl** | https://www.firecrawl.dev/account | 500 次免费抓取 |
| **FAL.ai** | https://fal.ai/dashboard/keys | 每日免费额度 |
| **ElevenLabs** | https://elevenlabs.io/app/settings/api-keys | 每月 10k 字符免费 |
| **Brave Search** | https://brave.com/search/api/ | 每月 2k 次免费 |

---

## 模型配置

### 通过 CLI 选择模型

```bash
# 启动交互式模型选择向导
hermes model
```

### 通过配置文件指定模型

编辑 `~/.hermes/config.yaml`:

```yaml
model:
  # LLM 提供商
  provider: openrouter
  
  # 模型名称
  # OpenRouter 格式: <provider>/<model-name>
  model: anthropic/claude-sonnet-4-20250514
  
  # 或直接使用提供商原生名称:
  # model: claude-3-5-sonnet-20241022    # Anthropic 直接调用
  # model: gpt-4o                        # OpenAI 直接调用
  
  # 温度参数 (0.0 = 确定性, 2.0 = 最大随机性)
  temperature: 0.7
  
  # 最大输出 token 数
  max_tokens: 4096
  
  # Top P 采样参数
  top_p: 1.0
  
  # 是否启用流式输出
  streaming: true
```

### 推荐模型选择

#### 性价比优先

| 模型 | 成本 ($/1M tokens) | 特点 |
|------|---------------------|------|
| `openrouter/google/gemini-flash-1.5` | ~$0.07 | 最便宜，速度快 |
| `openrouter/meta-llama/llama-3.1-8b-instruct:free` | 免费 | 开源，适合简单任务 |
| `anthropic/claude-haiku-4-5-20251001` | ~$0.80 | 快速，质量好 |

#### 质量优先

| 模型 | 成本 ($/1M tokens) | 特点 |
|------|---------------------|------|
| `anthropic/claude-sonnet-4-20250514` | ~$3.00 | 平衡质量和成本 |
| `openai/gpt-4o` | ~$2.50 | 多模态能力强 |
| `google/gemini-2.5-pro` | ~$6.25 | 推理能力强，长上下文 |

#### 专业用途

| 用途 | 推荐模型 | 原因 |
|------|----------|------|
| 代码生成 | `anthropic/claude-sonnet-4-20250514` | 代码能力优秀 |
| 网页研究 | `google/gemini-2.5-pro` | 大上下文窗口 |
| 创意写作 | `openai/gpt-4o` | 文学风格多样 |
| 快速问答 | `anthropic/claude-haiku-4-5-20251001` | 响应快，成本低 |
| 数据分析 | `openai/o4-mini` | 推理能力强 |

---

## 提供商设置

### OpenRouter（推荐）

```yaml
providers:
  openrouter:
    base_url: "https://openrouter.ai/api/v1"
    api_key_env: OPENROUTER_API_KEY  # 从 .env 读取
    models:
      default: "anthropic/claude-sonnet-4-20250514"
    
    # 高级选项
    timeout: 120                    # 请求超时（秒）
    max_retries: 3                  # 重试次数
    
    # HTTP Headers（可选）
    extra_headers:
      X-Title: "Hermes Agent"
      HTTP-Referer: "http://localhost:8080"
```

### Anthropic 直接连接

```yaml
providers:
  anthropic:
    api_key_env: ANTHROPIC_API_KEY
    models:
      default: "claude-sonnet-4-20250514"
    base_url: "https://api.anthropic.com"
```

### OpenAI 直接连接

```yaml
providers:
  openai:
    api_key_env: OPENAI_API_KEY
    models:
      default: "gpt-4o"
    base_url: "https://api.openai.com/v1"
```

### Ollama（本地模型，零成本）

```yaml
providers:
  ollama:
    base_url: "http://localhost:11434/v1"
    models:
      default: "llama3.1:8b"        # 需先运行 ollama pull llama3.1:8b
    api_key: "ollama"               # Ollama 不需要真实 API Key
    # 无需 API Key，完全离线运行
```

---

## 工具集配置

### 启用/禁用工具集

```yaml
tools:
  # 全局默认启用状态
  enabled_by_default: true
  
  # 工具集定义
  toolsets:
    web_search:
      enabled: true
      tools:
        - search_web
        - firecrawl_scrape
        
    browser:
      enabled: true
      backend: local_chrome       # browserbase_cloud | browser_use_cloud | local_chrome | local_chromium
      
    file_operations:
      allowed_paths:
        - /Users/chunhaixu/Projects
        - /tmp
        - ~/Documents
      denied_paths:
        - ~/.ssh
        - ~/.gnupg
        - /etc
        
    terminal:
      allowed_commands:
        - git
        - npm
        - python
        - cat
        - ls
        - grep
        - find
      denied_commands:
        - rm -rf /
        - sudo
        - chmod 777
        
    memory:
      enabled: true
      backend: built-in           # built-in | honcho | mem0 | ...
      
    code_execution:
      enabled: true
      sandbox: docker             # docker | subprocess
      
    delegation:
      enabled: true
      max_concurrent: 3          # 最大并发子代理数
      default_timeout: 300        # 默认超时（秒）
      
    image_generation:
      enabled: false              # 需要 FAL_KEY
      provider: fal               # fal | ...
      model: flux-2-pro          
      upscale: true               # 自动 2x 放大
      
    voice:
      enabled: true
      tts_provider: edge_tts      # edge_tts | elevenlabs | openai_tts | minimax | neutts
      stt_provider: whisper       # whisper | groq_whisper
```

---

## 记忆系统配置

```yaml
memory:
  # 后端选择
  provider: built-in             # built-in | honcho | mem0 | openviking | hindsight | holographic | retaindb | byte-rover
  
  # 内置后端特定配置
  built_in:
    storage_path: ~/.hermes/memory
    fts_enabled: true            # 启用全文搜索
    max_notes: 10000             # 最大笔记数
    auto_summarize: true         # 自动摘要旧会话
    summary_model: haiku         # 用于摘要的模型
    
  # Honcho 后端（如果使用）
  honcho:
    project_id: your-project-id
    dialect_name: user-profile   # 用户方言文件名
    
  # 记忆保留策略
  retention:
    hot_memory_days: 7           # 热记忆保留天数
    session_history_days: 30     # 会话历史保留天数
    cold_storage_after: 90       # 天数后归档
    auto_prune: true             # 自动清理过期记忆
```

---

## 网关配置

### Telegram 示例

```yaml
gateway:
  telegram:
    enabled: true
    bot_token_env: TELEGRAM_BOT_TOKEN
    allowed_users:                # 限制可用的用户 ID（可选）
      - 123456789
    allowed_groups:               # 限制群组（可选）
      - -1001234567890
    commands:
      start: "欢迎使用 Hermes Agent！输入你的问题开始对话。"
      help: "可用命令：\n/ask <问题>\n/memory search <关键词>\n/status"
    features:
      voice: true                 # 支持语音消息
      image_analysis: true        # 分析图片
      inline_queries: true        # 内联模式
```

### Discord 示例

```yaml
gateway:
  discord:
    enabled: true
    bot_token_env: DISCORD_BOT_TOKEN
    command_prefix: "!"           # 命令前缀
    allowed_guilds:              # 限制服务器
      - "123456789012345678"
    voice_channels:              # 支持语音频道
      enabled: true
    features:
      slash_commands: true       # 斜杠命令
      context_menus: true        # 右键菜单
      message_content: true      # 内容意图（需在 Discord 开发者门户开启）
```

---

## 安全配置

```yaml
security:
  # 提示注入防护
  prompt_injection_protection:
    enabled: true                 # v0.7.0+ 默认开启
    strictness: medium            # low | medium | high
    
  # 凭证过滤
  credential_filtering:
    enabled: true
    patterns:                    # 要过滤的模式
      - "(?i)(api[_-]?key|token|secret|password)[=:]\s*\S+"
      - "sk-[a-zA-Z0-9]{20,}"
      - "ghp_[a-zA-Z0-9]{36}"
      
  # 工具权限控制
  tool_permissions:
    terminal:
      require_confirmation:
        - "rm "
        - "sudo"
        - "chmod 777"
        - "curl.*\\| bash"
        
  # 日志审计
  audit_logging:
    enabled: true
    log_tool_calls: true
    log_file_access: true
    log_network_requests: true
    
  # 网络访问控制
  network:
    allowed_domains:             # 白名单（留空则允许所有）
      - "*.openai.com"
      - "*.anthropic.com"
      - "*.openrouter.ai"
    blocked_domains:              # 黑名单
      - "*.malicious-site.com"
```

---

## 完整配置示例

这是一个生产就绪的完整配置示例：

```yaml
# ============================================
# Hermes Agent 完整配置示例
# 文件位置: ~/.hermes/config.yaml
# ============================================

# --- 核心模型设置 ---
model:
  provider: openrouter
  model: anthropic/claude-sonnet-4-20250514
  temperature: 0.7
  max_tokens: 8192
  top_p: 1.0
  streaming: true

# --- 提供商 ---
providers:
  openrouter:
    base_url: "https://openrouter.ai/api/v1"
    api_key_env: OPENROUTER_API_KEY
    timeout: 120
    max_retries: 3
    extra_headers:
      X-Title: "My Hermes Instance"

# --- 工具集 ---
tools:
  enabled_by_default: true
  toolsets:
    web_search:
      enabled: true
    browser:
      enabled: true
      backend: local_chrome
    file_operations:
      allowed_paths:
        - ~/Projects
        - /tmp
        - ~/Documents
      denied_paths:
        - ~/.ssh
        - ~/.gnupg
    terminal:
      enabled: true
      allowed_commands:
        - git
        - npm
        - python
        - node
        - make
        - cat
        - ls
        - grep
        - find
        - head
        - tail
        - wc
        - sed
        - awk
    memory:
      enabled: true
      provider: built-in
    code_execution:
      enabled: true
    delegation:
      enabled: true
      max_concurrent: 3
      default_timeout: 300
    image_generation:
      enabled: false
    voice:
      enabled: true
      tts_provider: edge_tts

# --- 记忆系统 ---
memory:
  provider: built-in
  retention:
    hot_memory_days: 7
    session_history_days: 30
    cold_storage_after: 90
    auto_prune: true

# --- 安全 ---
security:
  prompt_injection_protection:
    enabled: true
    strictness: medium
  credential_filtering:
    enabled: true
  tool_permissions:
    terminal:
      require_confirmation:
        - "rm -rf"
        - "sudo"
        - "curl.*\\| bash"
        - "wget.*\\| sh"
  audit_logging:
    enabled: true

# --- 网关（按需启用）---
gateway:
  telegram:
    enabled: false
  discord:
    enabled: false

# --- UI 设置 ---
ui:
  theme: dark                   # dark | light
  color_output: true
  show_thinking: false         # 显示推理过程
  timestamp_format: "%Y-%m-%d %H:%M:%S"
```

---

## 常见配置问题

### Q: 如何切换模型？

```bash
# 方法1：交互式
hermes model

# 方法2：命令行临时覆盖
hermes run "prompt" --model gpt-4o --non-interactive

# 方法3：编辑配置文件
nano ~/.hermes/config.yaml  # 修改 model.model 字段
```

### Q: 如何降低成本？

1. 使用更便宜的模型（如 Haiku、Flash）
2. 减少最大 token 数
3. 限制启用的工具集（减少不必要的函数调用）
4. 使用缓存友好的提示词
5. 考虑 Ollama 本地模型（零 API 成本）

### Q: 如何解决 "API key invalid" 错误？

1. 检查 `~/.hermes/.env` 中密钥是否正确
2. 确认密钥没有过期或达到配额限制
3. 运行 `hermes doctor` 进行诊断
4. 尝试切换到备用提供商

### Q: 如何让多个项目共享同一个 Hermes？

创建项目级 `.hermes/config.yaml`：

```bash
cd my-project
mkdir -p .hermes
cat > .hermes/config.yaml << EOF
model:
  provider: openrouter
  model: anthropic/claude-sonnet-4-20250514
EOF

HERMES_ENABLE_PROJECT_AGENTS=true hermes
```
