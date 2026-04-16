# WeChat Daily Report Generator (微信群聊日报生成工具)

这是一个用于分析微信群聊天记录，结合 AI 生成内容，并最终输出为精美手机端长图（PNG）的工具。

## ✨ 功能特点

- **数据统计**: 自动分析群聊记录，生成话唠榜、熬夜冠军、词云统计等数据。
- **AI 智能摘要**: 利用 AI 识别讨论热点、提取有价值的资源/教程、捕捉有趣对话和问答。
- **可视化报告**: 基于 HTML/CSS 模板渲染，自动生成适配手机屏幕（iPhone 14 Pro Max 分辨率）的日报图片。
- **风格化**: 支持幽默、玩梗的报告风格，提升阅读乐趣。
- **本地原始库直连**: 直接读取解密后的微信数据库分析指定群聊，不再需要 ChatLab JSON 中间文件。

## 🛠️ 依赖环境

- Python 3.8+
- Node.js (可选，仅用于开发调试模板)

### Python 库安装

```bash
pip install jieba jinja2 playwright
playwright install chromium
```

### 可选：本地微信数据库解密依赖

如果你要直接从本机微信数据库导出群聊，而不是手头已有 ChatLab JSON：

```bash
python scripts/setup_check.py --ensure-decryptor
```

这一步会自动把 `wechat-decrypt` 安装到当前项目下的 `vendor/`，并安装其运行依赖。

## 🚀 使用流程

### 第一步：安装 Skill

**自动安装 (推荐)**:
```bash
npx skills add https://github.com/ADVISORYDZ/wechat-daily-report-skill
```

**手动安装**:
克隆本仓库到您的 Claude Skills 目录（如果目录不存在请先创建）：

```bash
cd ~/.claude/skills/
git clone https://github.com/ADVISORYDZ/wechat-daily-report-skill.git
```

### 第二步：基本使用

在 Claude Code 中直接对 Claude 下达指令：

> **“生成 [群名称] 今日日报”**

Claude 将自动调用本项目中的脚本，从解密后的原始数据库读取指定群聊并渲染日报长图。

---

## 🛠️ 详细步骤 (内部逻辑)

## 📂 数据来源

输入来源是当前项目下 `vendor/wechat-decrypt/decrypted/` 的原始 SQLite 数据库：

- `contact/contact.db`
- `message/message_*.db`
- `session/session.db`

`scripts/analyze_chat.py` 会直接从这些库里读取指定群聊，不再经过 JSON 转换；并且默认会在每次分析前先刷新一次解密快照。

## 📁 项目结构

- `scripts/`: 核心 Python 脚本
    - `setup_check.py`: 检查微信解密环境并准备 `wechat-decrypt`
    - `decrypt_wechat.py`: 解密本机微信数据库
    - `list_wechat_groups.py`: 列出解密库中的群聊和消息量
    - `wechat_decrypted_reader.py`: 读取解密后的微信群聊原始数据
    - `analyze_chat.py`: 直接分析解密后的群聊数据库并生成统计
    - `generate_report.py`: 模板渲染与图片生成
- `assets/`: 资源文件
    - `report_template.html`: Jinja2 报告模板
- `references/`: 参考文档
    - `ai_prompt.md`: AI 提示词模板
- `SKILL.md`: 技能详细说明

## 📝 License

MIT
