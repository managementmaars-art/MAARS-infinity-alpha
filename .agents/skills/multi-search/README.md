<p align="center">
  <img src="https://raw.githubusercontent.com/Nex-ZMH/Agent-websearch-skill/main/logo.jpg" width="660" alt="Agent WebSearch Skill Logo">
</p>

<h1 align="center">Agent WebSearch Skill 🔍</h1>

<p align="center">
  <b>Intelligent Multi-Engine Search — Works With or Without VPN</b>
</p>

<p align="center">
  <i>Zero config. Zero API keys. Auto-fallback from DuckDuckGo → Tavily → Bing API → Bing Scraper.</i>
</p>

<p align="center">
  <a href="https://opensource.org/licenses/GPL-3.0">
    <img src="https://img.shields.io/badge/License-GPL%203.0-blue.svg?style=flat-square" alt="License: GPL-3.0">
  </a>
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/Python-3.8%2B-green.svg?style=flat-square" alt="Python: 3.8+">
  </a>
  <a href="https://github.com/Nex-ZMH/Agent-websearch-skill">
    <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg?style=flat-square" alt="Platform">
  </a>
  <img src="https://img.shields.io/badge/No%20VPN%20Required-✓-success.svg?style=flat-square" alt="No VPN Required">
</p>

<p align="center">
Built by <a href="https://github.com/Nex-ZMH">Nex-ZMH</a>, an energy industry AI explorer from a remote mountain village of China.
</p>

<p align="center">
  🌐 Languages:
  <a href="#english">English</a> ·
  <a href="#中文">简体中文</a> ·
</p>

<p align="center">
  ⚡️Quick Routes: 
  <a href="#getting-started">Getting Started</a> ·
  <a href="#features">Features</a> ·
  <a href="#installation">Installation</a> ·
</p>

---

## The Problem We Solve

### 🚫 Common Pain Points

| Issue | Description |
|------|------|
| 🔒 **Cannot Get Foreign API Keys** | Brave Search require foreign credit cards or Visa cards, difficult for users in China |
| 🌐 **Unstable Network Environment** | VPN connections are intermittent, search engine availability changes constantly |
| 💰 **Limited API Quota** | Search functionality stops working after free quota is exhausted |
| 🔄 **Tedious Manual Switching** | Need to manually change search engines every time network changes |

> **💡 Why Not Use  Brave Search?**
> 
> OpenClaw's built-in Brave Search requires:
> - ✅ VPN access to reach the service
> - ✅ Visa/MasterCard credit card for account registration
> - ✅ Payment method binding to get API Key
> 
> For most users in China, these barriers are hard to overcome. This project has **zero barriers** — just clone and use!

### ✅ Our Solution

**Agent WebSearch Skill** solves these problems through intelligent engine selection strategy:

- ✨ **Zero Config Ready** — Works with Bing Scraper even without any API Key
- 🔄 **Auto Failover** — Automatically switches to next available engine when one fails
- 📊 **Smart Quota Management** — Prioritizes free engines to save API quota for critical moments
- 🌐 **Network Adaptive** — Auto-detects network environment and selects optimal engine

---

## English

### Getting Started

**Agent WebSearch Skill** — An intelligent multi-engine search solution that works in any network environment. Whether you have VPN access or not, whether you have API keys or not, this tool ensures you can always perform web searches seamlessly.

### Features

- 🔍 **Multi-Engine Architecture** — DuckDuckGo, Tavily, Bing API, Bing Scraper with auto-fallback
- 🔄 **Auto Failover** — Automatically switches to next available engine when one fails
- 🌐 **Network Adaptive** — Detects network environment and selects optimal engine
- 📊 **Smart Quota Management** — Prioritizes free engines to save API quota
- ⚡ **Zero Config** — Works out of the box without any API keys
- 🎯 **Quality Mode** — Optional quality-first mode for important searches

### Installation

```bash
# Clone repository
git clone https://github.com/Nex-ZMH/Agent-websearch-skill.git
cd Agent-websearch-skill

# Install dependencies
pip install requests tavily-python duckduckgo-search beautifulsoup4
```

### Usage

```python
from multi_search import search, get_status, fetch_web_content

# Basic search — auto-select best engine
results = search("Python async tutorial", max_results=5)

# Quality-first mode — for important searches
results = search("AI research papers 2024", max_results=5, prefer_quality=True)

# Force network recheck after VPN switch
results = search("latest tech news", force_network_check=True)

# Check system status
status = get_status()

# Fetch detailed content from URL
content = fetch_web_content(results[0]['href'], max_length=3000)
```

### Smart Search Strategy

```
┌─────────────────────────────────────────────────────────────┐
│                  Search Engine Selection Strategy            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Balanced Mode (Default) — Free engines first, save quota   │
│  ┌──────────┐   ┌─────────┐   ┌──────────┐   ┌─────────┐   │
│  │DuckDuckGo│ → │ Tavily  │ → │ Bing API │ → │  Bing   │   │
│  │  (Free)  │   │(API)    │   │  (API)   │   │ Scraper │   │
│  └──────────┘   └─────────┘   └──────────┘   └─────────┘   │
│       ↓              ↓              ↓              ↓        │
│   Needs VPN    VPN+API    VPN+API   Works in China    │
│                                                             │
│  Quality First Mode — Premium APIs first for best results   │
│  ┌─────────┐    ┌──────────┐   ┌──────────┐   ┌─────────┐  │
│  │ Tavily  │ → │DuckDuckGo│ → │ Bing API │ → │  Bing   │  │
│  │(Premium)│    │  (Free)  │   │  (API)   │   │ Scraper │  │
│  └─────────┘    └──────────┘   └──────────┘   └─────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Engine Comparison

| Engine | VPN Required | API Key | Monthly Quota | Quality | Best For |
|--------|:--------------:|:-------:|:-------------:|:-------:|----------|
| **DuckDuckGo** | ✅ Yes | ❌ No | ♾️ Unlimited | ⭐⭐⭐ | Daily searches |
| **Tavily API** | ✅ Yes | ✅ Yes | 1000 | ⭐⭐⭐⭐⭐ | AI Agents, important searches |
| **Bing API** | ✅ Yes | ✅ Yes | 1000 | ⭐⭐⭐⭐ | Official stable search |
| **Bing Scraper** | ❌ No | ❌ No | ♾️ Unlimited | ⭐⭐⭐ | Fallback without VPN |

### Why Choose Us?

**Scenario 1: No VPN, No API Key (China mainland)**
```
Search → DuckDuckGo fails → Skip Tavily → Skip Bing API → Bing Scraper succeeds ✅
Result: Works perfectly without any configuration!
```

**Scenario 2: Has VPN, Has Tavily API Key**
```
Search → DuckDuckGo succeeds ✅
Result: Uses free engine, saves API quota
```

**Scenario 3: Unstable Network**
```
Search → DuckDuckGo fails → Tavily succeeds ✅
Result: Auto-switch, seamless experience
```

### API Configuration (Optional)

> **Note**: This project works **out of the box** without any configuration!

**Method 1: Environment Variables (Recommended)**
```bash
export TAVILY_API_KEY="your-tavily-api-key"
export BING_API_KEY="your-bing-api-key"
```

**Method 2: Configuration File**
```bash
cp api_keys.example.json api_keys.json
# Edit api_keys.json with your keys
```

### Requirements

- Python 3.8+
- `requests` `tavily-python` `duckduckgo-search` `beautifulsoup4`

---

## 中文

### 简介

**Agent WebSearch Skill** — 一款智能多引擎搜索解决方案，在任何网络环境下都能正常工作。无论你是否有科学上网，无论你是否有 API Key，这个工具都能确保你顺畅地进行网络搜索。

### 功能特性

- 🔍 **多引擎架构** — DuckDuckGo、Tavily、Bing API、Bing 爬虫，自动故障转移
- 🔄 **自动切换** — 一个引擎失败，自动切换到下一个可用引擎
- 🌐 **网络自适应** — 自动检测网络环境，选择最优引擎
- 📊 **智能配额管理** — 优先使用免费引擎，节省 API 配额
- ⚡ **零配置** — 无需任何 API Key，开箱即用
- 🎯 **质量模式** — 可选的质量优先模式，适合重要搜索

### 安装方法

```bash
# 克隆仓库
git clone https://github.com/Nex-ZMH/Agent-websearch-skill.git
cd Agent-websearch-skill

# 安装依赖
pip install requests tavily-python duckduckgo-search beautifulsoup4
```

### 使用方法

```python
from multi_search import search, get_status, fetch_web_content

# 基本搜索 — 自动选择最优引擎
results = search("Python 异步编程教程", max_results=5)

# 质量优先模式 — 适合重要搜索
results = search("AI 论文 2024", max_results=5, prefer_quality=True)

# 切换网络后强制重新检测
results = search("最新科技新闻", force_network_check=True)

# 查看当前系统状态
status = get_status()

# 抓取网页详细内容
content = fetch_web_content(results[0]['href'], max_length=3000)
```

### 智能搜索策略

```
┌─────────────────────────────────────────────────────────────┐
│                    搜索引擎选择策略                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  平衡模式（默认）— 优先免费引擎，节省 API 配额               │
│  ┌─────────┐    ┌─────────┐    ┌──────────┐    ┌─────────┐ │
│  │DuckDuckGo│ → │ Tavily  │ → │ Bing API │ → │  Bing   │ │
│  │ (免费)   │    │(需API)  │    │ (需API)  │    │ 爬虫    │ │
│  └─────────┘    └─────────┘    └──────────┘    └─────────┘ │
│       ↓              ↓              ↓              ↓       │
│    需科学上网    需科学上网+API  需科学上网+API  国内直连    │
│                                                             │
│  质量优先模式 — 优先高质量 API，适合重要搜索                 │
│  ┌─────────┐    ┌─────────┐    ┌──────────┐    ┌─────────┐ │
│  │ Tavily  │ → │DuckDuckGo│ → │ Bing API │ → │  Bing   │ │
│  │(高质量) │    │ (免费)   │    │ (需API)  │    │ 爬虫    │ │
│  └─────────┘    └─────────┘    └──────────┘    └─────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 各引擎特点对比

| 引擎 | 需要科学上网 | 需要 API Key | 月配额 | 搜索质量 | 适用场景 |
|------|:------------:|:------------:|:------:|:--------:|----------|
| **DuckDuckGo** | ✅ 需要 | ❌ 不需要 | ♾️ 无限 | ⭐⭐⭐ | 日常搜索首选 |
| **Tavily API** | ✅ 需要 | ✅ 需要 | 1000次 | ⭐⭐⭐⭐⭐ | AI Agent、重要搜索 |
| **Bing API** | ✅ 需要 | ✅ 需要 | 1000次 | ⭐⭐⭐⭐ | 官方稳定搜索 |
| **Bing 爬虫** | ❌ 不需要 | ❌ 不需要 | ♾️ 无限 | ⭐⭐⭐ | 国内无科学上网时的保底方案 |

### 为什么选择我们？

**场景 1：国内用户，没有科学上网，没有 API Key**
```
用户搜索 → DuckDuckGo 失败 → Tavily 跳过 → Bing API 跳过 → Bing 爬虫成功 ✅
结果：正常返回搜索结果，完全可用！
```

**场景 2：有科学上网，有 Tavily API Key**
```
用户搜索 → DuckDuckGo 成功 ✅
结果：使用免费引擎，节省 API 配额
```

**场景 3：网络不稳定，时断时续**
```
用户搜索 → DuckDuckGo 失败 → Tavily 成功 ✅
结果：自动切换，用户无感知
```

### API 配置（可选）

> **重要**：本项目**无需任何配置即可使用**！以下配置仅用于解锁高级功能。

**方法 1：环境变量（推荐）**
```bash
export TAVILY_API_KEY="your-tavily-api-key"
export BING_API_KEY="your-bing-api-key"
```

**方法 2：配置文件**
```bash
cp api_keys.example.json api_keys.json
# 编辑 api_keys.json 填入你的密钥
```

### 系统要求

- Python 3.8+
- `requests` `tavily-python` `duckduckgo-search` `beautifulsoup4`

---

## Roadmap

- [ ] Add Google Search API support
- [ ] Implement async/await for parallel searches
- [ ] Add rate limiting configuration
- [ ] Support custom search engine priority
- [ ] Add Searxng integration for privacy-focused users

---

## Author

[Nex-ZMH](https://github.com/Nex-ZMH)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.
