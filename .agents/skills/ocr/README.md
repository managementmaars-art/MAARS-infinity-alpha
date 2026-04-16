# DeepSeek-OCR 3B + PaddleOCR | OpenCode Hybrid OCR Skill

> Give "eyes" to text-only LLMs — Local OCR for OpenCode/OpenWork

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenCode](https://img.shields.io/badge/OpenCode-Skill-blue)](https://opencode.ai)

[中文文档](README_CN.md)

## Why This Skill?

Many LLMs (like GLM-4.7) don't have vision capabilities but are affordable and fast. This skill gives them "eyes" by running OCR locally, extracting text from images so any model can understand visual content.

**All data stays on your machine** — perfect for sensitive documents.

## Hybrid Mode

| Mode | Engine | Best For | Speed |
|------|--------|----------|-------|
| **Smart** (default) | DeepSeek-OCR 3B | Custom prompts, understanding content | 10-30s |
| **Fast** (`--fast`) | PaddleOCR PP-OCRv5 | Pure text extraction | 1-3s |

## Features

- **Privacy First**: 100% local, no data leaves your machine
- **Smart OCR**: Ask questions about images (DeepSeek-OCR scores 834 on OCRBench, beating GPT-4o's 736)
- **100+ Languages**: Chinese, English, Japanese, Korean, and more
- **Multiple Formats**: PNG, JPG, PDF, BMP, GIF, WEBP, TIFF
- **Auto Resize**: Large images automatically scaled to prevent timeout
- **Mac Friendly**: Runs on 16GB Mac (Apple Silicon supported)

## Quick Start

### 1. Install Dependencies

```bash
# Install Ollama
brew install ollama
brew services start ollama

# Download DeepSeek-OCR model (~6.7GB)
ollama pull deepseek-ocr

# Python dependencies
pip install requests pdf2image Pillow
brew install poppler

# (Optional) Fast mode
pip install paddleocr paddlepaddle
```

### 2. Install Skill

```bash
cd ~/Library/Application\ Support/com.differentai.openwork/workspaces/starter/.opencode/skills
git clone https://github.com/mr-shaper/opencode-skill-hybrid-ocr.git paddle-ocr
```

### 3. Use

```bash
cd paddle-ocr

# Smart mode (DeepSeek-OCR)
python3 scripts/ocr.py image.png

# Custom prompt
python3 scripts/ocr.py table.png --prompt "Extract as markdown table"

# Fast mode (PaddleOCR)
python3 scripts/ocr.py image.png --fast

# PDF
python3 scripts/ocr.py document.pdf
```

## How It Works

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ Image/PDF   │────▶│ Local OCR        │────▶│ Your LLM        │
│             │     │ (DeepSeek/Paddle)│     │ (GLM-4.7, etc.) │
└─────────────┘     └──────────────────┘     └─────────────────┘
```

## Requirements

- macOS (Apple Silicon or Intel)
- 16GB RAM minimum
- Python 3.8+
- ~7GB disk space for models

## Resource Usage

| State | Memory |
|-------|--------|
| Idle | ~30MB (Ollama service) |
| Processing | ~6-8GB (model loaded) |

Free memory when not needed:
```bash
brew services stop ollama
```

## License

MIT

---

Made for [OpenCode](https://opencode.ai) community
