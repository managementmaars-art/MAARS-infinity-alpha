---
name: wechat-article-fetcher
description: 微信公众号文章抓取工具，自动转换为带Obsidian Front Matter的标准Markdown格式，支持图片本地化存储、全平台兼容、分类标签管理，可直接导入知识库使用。
---

# wechat-article-fetcher 微信公众号文章抓取技能

## 📖 技能概述
专门用于抓取微信公众号公开文章，自动转换为标准Markdown格式，自动下载所有图片到本地并替换为相对路径，同时生成符合Obsidian规范的Front Matter元数据，可直接导入知识库使用。

## 🎯 适用场景
- 📚 个人知识管理素材采集
- 💾 公众号文章本地备份
- 📱 离线阅读素材准备
- 🗃️ Obsidian/Notion等知识库批量导入
- 🏷️ 分类归档公众号文章

## 🔧 依赖安装
### 环境要求
- Node.js >= 14.0.0
- 操作系统：Windows / Linux / macOS 全平台兼容

### 安装步骤
```bash
# 进入技能目录
cd skills/wechat-article-fetcher

# 安装依赖
npm install
```

## 🚀 使用方法
```bash
# 命令格式
node scripts/fetch.js <微信文章URL> [领域分类]
```

### 参数说明
| 参数 | 类型 | 是否必填 | 说明 |
|------|------|----------|------|
| 微信文章URL | string | 是 | 格式为 `https://mp.weixin.qq.com/s/xxx` 的公开文章链接 |
| 领域分类 | string | 否 | 文章分类标签，如：AI、生活、政策、财经、科技等，不传则无分类标签 |
| 自定义摘要 | string | 否 | 大模型生成的文章摘要，100-150字最佳，不传则自动使用文章前150字作为摘要 |

### 使用示例
```bash
# 示例1：无分类，文件名不加前缀，标签只有「摘录」，自动使用文章前150字作为摘要
node scripts/fetch.js https://mp.weixin.qq.com/s/F7nGnSfCLHbBwp2h0QX5tg

# 示例2：指定分类为「生活」，文件名为「生活-xxx.md」，标签增加「生活」
node scripts/fetch.js https://mp.weixin.qq.com/s/F7nGnSfCLHbBwp2h0QX5tg 生活

# 示例3：指定分类为「AI」，文件名为「AI-xxx.md」，标签增加「AI」
node scripts/fetch.js https://mp.weixin.qq.com/s/xxx AI
```

## 📂 输出说明
### 跨平台路径自动适配
- **Windows**：`C:\Users\用户名\AppData\Local\Temp\wechat-article\wechat-article-[时间戳]\`
- **Linux / macOS**：`/tmp/wechat-article/wechat-article-[时间戳]\`

### 目录结构
```
wechat-article-1773845896874/
├── 生活-一组零成本小技巧保护你宝贵的专注力.md  # Markdown文件：[分类]-[文章标题].md
└── attachments/                                  # 图片资源目录
    ├── img-1.jpg
    ├── img-2.png
    └── ...
```

### Markdown文件格式
文件开头自动生成Obsidian标准Front Matter：
```yaml
---
title: 文章标题
source: 原文链接
author:
  - "[[作者名称]]" # 无作者则省略此字段
published: XX公众号 微信公众号
created: 2026-03-18
description: 文章前150字纯文本摘要
tags:
  - 摘录
  - 分类标签 # 仅当传入领域分类参数时显示此行
---
```
正文部分直接保留原文排版：标题、段落、列表、引用、链接、图片等结构完整。

## ✨ 核心特性
✅ **无需登录**：伪装微信客户端UA绕过PC端访问限制，无需扫码登录
✅ **Obsidian原生适配**：自动生成标准Front Matter，可直接导入知识库
✅ **图片本地化**：自动下载所有图片到`attachments`目录，替换为相对路径，离线可完整访问
✅ **全平台兼容**：自动适配Windows/Linux/macOS系统临时目录
✅ **智能元数据提取**：自动提取标题、公众号名称、作者、发布时间、摘要
✅ **文件名安全**：自动替换特殊字符，兼容所有操作系统文件名规则
✅ **分类标签**：支持自定义文章分类，自动添加到标签和文件名
✅ **无浏览器依赖**：轻量HTTP请求，抓取速度快，资源消耗低

## ❓ 常见问题
### Q: 抓取失败提示「未找到文章正文内容」怎么办？
A: 请确认文章链接是公开可访问的，没有设置付费墙或仅粉丝可见；部分公众号反爬策略严格，可多尝试几次。

### Q: 为什么有些图片下载失败？
A: 部分图片可能设置了防盗链或已失效，脚本会自动跳过失败的图片并保留原链接，不影响整体使用。

### Q: 可以自定义输出路径吗？
A: 默认输出到系统临时目录，如需自定义路径可修改脚本中`articleDir`变量配置。

## 📝 更新记录
- **v1.0.1 (2026-03-18)**：修复无分类时标签显示`undefined`问题，无分类时仅保留「摘录」标签，文件名也不加分类前缀
- **v1.0.0 (2026-03-18)**：初始版本，完成核心抓取、Markdown转换、图片下载、Obsidian Front Matter生成功能
