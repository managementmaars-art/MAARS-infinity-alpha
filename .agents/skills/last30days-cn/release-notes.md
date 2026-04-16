# 发行说明

> Author: Jesse (https://github.com/Jesseovo)

## v2.0.0

**last30days-cn** 重大升级：集成 MediaCrawler 爬虫引擎，大幅减少 API Key 依赖。

### 亮点

- **集成 MediaCrawler 爬虫引擎**：基于 Playwright 浏览器自动化，灵感来源于 [NanmiCoder/MediaCrawler](https://github.com/NanmiCoder/MediaCrawler)，无需逆向加密算法，降低使用门槛。
- **7/8 平台零 API Key 可用**：安装 Playwright 后，微博、小红书、抖音、B站、知乎、百度、今日头条均可无需 API Key 使用（仅微信公众号仍需 API）。
- **三级自动降级策略**：API 优先 → 爬虫模式 → 公开接口，确保最大数据可用性。
- **登录态 Cookie 缓存**：爬虫模式支持持久化 Cookie，减少重复登录操作。

### Bug 修复

- **修复 Issue #1**：修复 `marketplace.json` 缺少 `owner` 字段导致 Claude Code Marketplace 安装报错的问题（"Invalid input: expected object, received undefined"）。

### 变更

- 新增 `scripts/lib/crawler_bridge.py` — MediaCrawler 爬虫桥接模块
- 更新 `weibo.py`、`xiaohongshu.py`、`douyin.py`、`bilibili.py`、`zhihu.py` — 增加爬虫模式自动降级
- 更新 `env.py` — 诊断函数考虑 Playwright 可用性
- 更新 `last30days.py` — 诊断输出增加爬虫引擎状态
- 更新 `requirements.txt` — 新增 `playwright` 可选依赖
- 更新 `README.md` — 增加免责声明、法律合规说明、v2.0 升级文档
- 更新 `SKILL.md` — 版本号升级，配置说明更新
- 更新 `.claude-plugin/marketplace.json` — 添加 `owner` 字段，修复安装问题
- 更新 `.claude-plugin/plugin.json` — 版本号升级至 2.0.0

### 说明

配置与 CLI 详见 `README.md` 与 `SPEC.md`。许可证：**MIT**。

---

## v1.0.0

**last30days-cn** 首个正式发布：面向中文互联网的近 30 天多源研究技能。

### 亮点

- **8 大中文平台**：微博、小红书、B 站、知乎、抖音、微信公众号、百度搜索、今日头条并行检索与统一简报。  
- **中文 NLP**：集成 **jieba** 分词，用于查询扩展与相关性计算，更贴合中文检索与排序。  
- **多 Agent 支持**：可作为 Cursor Skill、Claude Code 技能、OpenClaw（ClawHub / `~/.agents`）、Gemini CLI Extension 或任意具备 Bash / 读写的 Agent 工具链使用。

### 说明

配置与 CLI 详见 `README.md` 与 `SPEC.md`。许可证：**MIT**。
