---
name: formatting
description: "Generate branded Word (.docx) and PDF documents with 3 brand templates: Etna Labs (English memos), 拾象科技 (Chinese research), 海外独角兽 (Chinese public content). Use when asked to format, typeset, or brand a document, create a memo, or turn content into a professional doc. Also trigger for '帮我排版' '用拾象/海外独角兽格式' 'branded document' 'format as doc' 'generate PDF'."
---

# 品牌文档排版器

将内容排版成带有品牌视觉的专业 Word (.docx) + PDF 文档。支持三套品牌模板。

## Step 1: 选择品牌

先问用户要用哪套品牌（如果上下文明确就直接选）：

| 品牌 | 语言 | 主色 | Logo | 适用场景 |
|------|------|------|------|---------|
| **Etna Labs** | English | `#C45A48` 赤陶红 | `assets/etna/logo_header.png` | 内部 memo、LP letter、英文报告 |
| **拾象科技** | 中文 | `#A11F2A` 深红 | `assets/shixiang/logo_header.png` | 对外投研报告 |
| **海外独角兽** | 中文 | `#736de9` 紫色 | `assets/haiwai/logo_header.jpeg` | 公众号长文、对外分享 |

## Step 2: 文档结构

三套品牌共享同一套版式逻辑，仅颜色/字体/logo 不同：

### 页面设置
- **Etna**: US Letter, margins 1800/1440/1440/1440 DXA
- **拾象/海外独角兽**: A4, margins 1440/1440/1829/1829 DXA

### 页眉
- 右侧放品牌 Logo（Tab 推至最右）
- Etna：左侧加 slogan "Deep Conviction. Long View." + etnalabs.co，下方品牌色分隔线
- 拾象/海外独角兽：页眉无下划线

### 字体层级

**Etna Labs（English）：**

| 层级 | 字体 | 大小 | 颜色 |
|------|------|------|------|
| H1 主标题 | Anonymous Pro | 22pt | 品牌色 Bold |
| H2 章节 | Anonymous Pro | 16pt | 品牌色 Bold，带罗马数字 I. II. III. |
| H3 子标题 | Times New Roman | 13pt | 品牌色 Bold |
| 正文 | Times New Roman | 12pt | 黑色 |

**拾象/海外独角兽（中文）：**

| 层级 | 字体 | 大小 | 颜色 |
|------|------|------|------|
| 大标题 | 楷体 | 18pt | 黑色 Bold |
| H1 | 楷体 | 16pt | 品牌色 Bold，带罗马数字 |
| H2 | 楷体 | 14pt | 品牌色 Bold |
| H3 | 楷体 | 13pt | 品牌色 Bold |
| 正文 | 楷体（中文）+ Times New Roman（英文） | 12pt | 黑色 |

### 元信息块
- **Etna**: `From: Etna Labs`，下方品牌色分隔线 + 页脚含日期和 "Confidential"
- **拾象/海外独角兽**: `To: Investment Team` + `Date: YYYY-Mon.`，Date 行底部黑色横线

### 表格样式
- 表头行：品牌色背景 + 白色粗体文字
- 数据行：交替白色 / 品牌浅色底
- 边框：品牌中间色，1pt

### 文末（拾象/海外独角兽专属）
- 二维码居中，下方灰色小字"扫码关注'海外独角兽'，解锁更多深度报告"
- 二维码已内置于 `assets/shixiang/qrcode.jpg` 和 `assets/haiwai/qrcode.jpg`

## Step 3: 生成流程

1. 读取 docx skill（如有 `/mnt/skills/public/docx/SKILL.md`）
2. 用 docx-js 构建文档（参考 `references/` 中的完整代码模板）
3. 验证 .docx
4. 转换为 PDF
5. 输出两个文件

## 关键规则

- **中文文档**：凡中文用楷体，凡英文用 Times New Roman，通过 mixedRuns() 实现
- **Etna 文档**：全英文，Times New Roman + Anonymous Pro
- **不要手动加 PageBreak** — 让内容自然分页
- **二维码已内置** — 不要向用户索取
- **项目符号**：符号用品牌色，文字保持黑色
- **必须同时输出 .docx 和 .pdf**

## Assets 目录结构

```
formatting/
├── SKILL.md
├── assets/
│   ├── etna/
│   │   ├── logo_header.png
│   │   └── logo_horizontal_trimmed.png
│   ├── shixiang/
│   │   ├── logo_header.png
│   │   ├── qrcode.jpg
│   │   └── SimKai.ttf
│   └── haiwai/
│       ├── logo_header.jpeg
│       ├── qrcode.jpg
│       └── SimKai.ttf
└── references/
    ├── etna-template.js
    ├── shixiang-template.js
    └── haiwai-template.js
```
