# DeepSeek-OCR 3B + PaddleOCR | OpenCode 混合 OCR Skill

> 让没有视觉能力的大模型也能"看"图 — 本地 OCR 工具

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenCode](https://img.shields.io/badge/OpenCode-Skill-blue)](https://opencode.ai)

[English](README.md)

## 为什么需要这个 Skill？

很多大模型（比如 GLM-4.7）没有视觉能力，但价格便宜、速度快。这个 Skill 通过本地 OCR 让它们也能"看图"，提取图片中的文字后传给模型分析。

**数据全程不出本机** — 敏感文档放心扫。

## 双模式设计

| 模式 | 引擎 | 适用场景 | 速度 |
|------|------|----------|------|
| **智能模式** (默认) | DeepSeek-OCR 3B | 自定义提问、理解内容 | 10-30秒 |
| **快速模式** (`--fast`) | PaddleOCR PP-OCRv5 | 纯文字提取 | 1-3秒 |

## 特性

- **隐私优先**: 100% 本地运行，数据不上传
- **智能识别**: 可以问图片问题（DeepSeek-OCR 在 OCRBench 得分 834，超越 GPT-4o 的 736）
- **100+ 语言**: 中文、英文、日文、韩文等
- **多种格式**: PNG、JPG、PDF、BMP、GIF、WEBP、TIFF
- **自动压缩**: 大图片自动缩放，避免超时
- **Mac 友好**: 16GB 内存 Mac 即可运行（支持 Apple Silicon）

## 快速开始

### 1. 安装依赖

```bash
# 安装 Ollama
brew install ollama
brew services start ollama

# 下载 DeepSeek-OCR 模型 (约 6.7GB)
ollama pull deepseek-ocr

# Python 依赖
pip install requests pdf2image Pillow
brew install poppler

# (可选) 快速模式
pip install paddleocr paddlepaddle
```

### 2. 安装 Skill

```bash
cd ~/Library/Application\ Support/com.differentai.openwork/workspaces/starter/.opencode/skills
git clone https://github.com/mr-shaper/opencode-skill-hybrid-ocr.git paddle-ocr
```

### 3. 使用

```bash
cd paddle-ocr

# 智能模式 (DeepSeek-OCR)
python3 scripts/ocr.py image.png

# 自定义提问
python3 scripts/ocr.py table.png --prompt "提取为 markdown 表格"

# 快速模式 (PaddleOCR)
python3 scripts/ocr.py image.png --fast

# PDF 识别
python3 scripts/ocr.py document.pdf
```

## 工作原理

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ 图片/PDF    │────▶│ 本地 OCR         │────▶│ 你的大模型       │
│             │     │ (DeepSeek/Paddle)│     │ (GLM-4.7 等)    │
└─────────────┘     └──────────────────┘     └─────────────────┘
```

## 系统要求

- macOS (Apple Silicon 或 Intel)
- 最少 16GB 内存
- Python 3.8+
- 约 7GB 磁盘空间（存放模型）

## 资源占用

| 状态 | 内存占用 |
|------|----------|
| 空闲 | ~30MB (Ollama 服务) |
| 处理中 | ~6-8GB (模型加载后) |

不用时释放内存：
```bash
brew services stop ollama
```

## 常见问题

### Ollama 无法连接？
```bash
brew services start ollama
```

### 模型未找到？
```bash
ollama pull deepseek-ocr
```

### 处理超时？
大图片会自动压缩，如仍超时可用快速模式：
```bash
python3 scripts/ocr.py image.png --fast
```

## 许可证

MIT

---

为 [OpenCode](https://opencode.ai) 社区制作
