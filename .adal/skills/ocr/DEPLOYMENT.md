# OCR Skill Deployment Guide

> Give "eyes" to text-only LLMs (like GLM-4.7)

## Background

Some LLMs in OpenWork (like GLM-4.7) cannot process images. Even with existing pdf/pptx skills, these models can't see visual content.

**Solution**: Deploy a local OCR model to extract text from images first, then pass it to the main model for analysis.

---

## Technical Choice

### Why DeepSeek-OCR?

| Feature | Details |
|---------|---------|
| **Engine** | DeepSeek-OCR 3B (VLM) |
| **OCRBench** | 834 (beats GPT-4o's 736) |
| **Compression** | 10x compression with 97% accuracy |
| **Languages** | 100+ languages |
| **Custom Prompt** | ✅ Supported |
| **Platform** | macOS Apple Silicon fully supported |

### Hybrid Mode Design

| Mode | Engine | Use Case | Speed |
|------|--------|----------|-------|
| **Default** | DeepSeek-OCR 3B | Smart extraction, custom prompts | 10-30s/image |
| **Fast** (`--fast`) | PaddleOCR PP-OCRv5 | Pure text extraction | 1-3s/image |

---

## How It Works

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ User Input  │     │ DeepSeek-OCR     │     │ Main Model      │
│ (Image/PDF) │────▶│ (Local Ollama)   │────▶│ (GLM-4.7 etc.)  │
│             │     │ Extract/Analyze  │     │ Process         │
└─────────────┘     └──────────────────┘     └─────────────────┘
```

### Workflow

1. User provides image or PDF path
2. **Auto resize**: Large images (>1536px) automatically scaled
3. `ocr.py` calls DeepSeek-OCR (via Ollama)
4. Smart recognition with optional custom prompt
5. Return extracted text or analysis
6. Pass results to main model for further processing

### Auto Image Compression

Large images are automatically resized to prevent timeout:

```
Original: 6144x3429
Resized: 1536x857
```

- Max size: 1536px (maintains aspect ratio)
- Output quality: JPEG 90%
- Temp files auto-deleted after processing

---

## Full Deployment Steps

### Prerequisites

- macOS (Apple Silicon or Intel)
- Python 3.8+
- Homebrew

### Step 1: Install Ollama

```bash
brew install ollama
brew services start ollama
```

### Step 2: Download DeepSeek-OCR Model

```bash
ollama pull deepseek-ocr
```

> Model size ~6.7GB, download takes a few minutes

### Step 3: Install Python Dependencies

```bash
# Core dependencies
pip install requests Pillow

# PDF support
pip install pdf2image
brew install poppler

# (Optional) Fast mode
pip install paddleocr paddlepaddle
```

### Step 4: Install Skill

```bash
# OpenWork Skills directory
SKILLS_DIR=~/Library/Application\ Support/com.differentai.openwork/workspaces/starter/.opencode/skills

# Clone from GitHub
cd "$SKILLS_DIR"
git clone https://github.com/mr-shaper/opencode-skill-hybrid-ocr.git paddle-ocr
```

### Step 5: Verify Installation

```bash
cd "$SKILLS_DIR/paddle-ocr"
python3 scripts/setup_check.py
```

### Step 6: Test OCR

```bash
# Default mode (DeepSeek-OCR)
python3 scripts/ocr.py test_image.png

# Custom prompt
python3 scripts/ocr.py table.png --prompt "Extract table as markdown"

# Fast mode (PaddleOCR)
python3 scripts/ocr.py test_image.png --fast
```

---

## Directory Structure

### OpenWork Skills Location

```
~/Library/Application Support/com.differentai.openwork/
└── workspaces/
    └── starter/
        └── .opencode/
            └── skills/           ← All Skills here
                ├── paddle-ocr/   ← OCR Skill
                ├── pdf/
                ├── pptx/
                └── ...
```

### Skill Files

```
paddle-ocr/
├── SKILL.md              # Skill definition (for AI)
├── README.md             # English docs
├── README_CN.md          # Chinese docs
├── DEPLOYMENT.md         # This file
├── 部署说明.md            # Chinese deployment guide
├── .gitignore
├── .env.example
└── scripts/
    ├── ocr.py            # Core OCR script (hybrid mode)
    ├── setup_check.py    # Environment check
    └── requirements.txt  # Python dependencies
```

---

## Usage Examples

### Basic Usage

```bash
cd paddle-ocr

# Default mode (DeepSeek-OCR, smart)
python3 scripts/ocr.py image.png

# Fast mode (PaddleOCR, quick)
python3 scripts/ocr.py image.png --fast

# Custom prompt
python3 scripts/ocr.py table.png --prompt "Extract as markdown"
python3 scripts/ocr.py chart.png --prompt "What data is in this chart?"

# PDF OCR
python3 scripts/ocr.py document.pdf

# JSON output
python3 scripts/ocr.py image.png --json > result.json

# Save to file
python3 scripts/ocr.py doc.pdf --output extracted.txt
```

### Code Integration

```python
import subprocess
import json

# Call OCR (with custom prompt)
result = subprocess.run(
    ["python3", "scripts/ocr.py", "chart.png", "--json",
     "--prompt", "Extract all data points from this chart"],
    capture_output=True, text=True,
    cwd="/path/to/paddle-ocr"
)

# Parse result
ocr_data = json.loads(result.stdout)
extracted_text = ocr_data["text"]

# Build enhanced prompt for main model
prompt = f"""
Based on the extracted content:

{extracted_text}

Please analyze and provide insights.
"""
```

---

## Resource Usage

### Model Files

| Component | Size | Location |
|-----------|------|----------|
| DeepSeek-OCR 3B | 6.7 GB | `~/.ollama/models/` |
| PaddleOCR (optional) | ~200 MB | `~/.paddlex/official_models/` |

### Runtime Resources

| State | Ollama | DeepSeek-OCR | Notes |
|-------|--------|--------------|-------|
| **Idle** | ~30MB | Not loaded | Ollama service only |
| **First call** | ~30MB | Loading | Loading model to memory |
| **Processing** | ~30MB | ~6-8GB | While processing images |
| **After processing** | ~30MB | Stays loaded | Faster next call |

### Performance (Apple Silicon Mac)

| Scenario | DeepSeek-OCR | PaddleOCR (--fast) |
|----------|--------------|-------------------|
| First run (loading) | 10-20s | 3-5s |
| Simple text image | 10-15s | 1-3s |
| Complex table | 15-30s | 3-8s |
| Single page PDF | 15-30s | 5-10s |
| 10 page PDF | 3-5 min | 1-2 min |

---

## Ollama Service Management

```bash
# Check service status
brew services list | grep ollama

# Start service
brew services start ollama

# Stop service (free memory)
brew services stop ollama

# Restart service
brew services restart ollama

# Check loaded models
ollama ps

# Unload model (free memory but keep model file)
ollama stop deepseek-ocr

# Delete model (complete removal)
ollama rm deepseek-ocr
```

---

## Troubleshooting

### Cannot connect to Ollama?

```bash
# Ensure Ollama service is running
brew services start ollama

# Check service status
brew services list | grep ollama
```

### DeepSeek-OCR model not found?

```bash
# Download model
ollama pull deepseek-ocr

# Check installed models
ollama list
```

### PDF processing failed?

```bash
# Ensure poppler is installed
brew install poppler

# Ensure pdf2image is installed
pip install pdf2image
```

### Memory usage too high?

```bash
# Stop Ollama service (complete release)
brew services stop ollama

# Or just unload model (keep service running)
ollama stop deepseek-ocr
```

### Fast mode unavailable?

```bash
# Install PaddleOCR
pip install paddleocr paddlepaddle
```

---

## Model Comparison

| Aspect | DeepSeek-OCR 3B | PaddleOCR PP-OCRv5 |
|--------|-----------------|-------------------|
| Type | VLM (Vision Language Model) | Traditional OCR Pipeline |
| Size | 6.7 GB | ~200 MB |
| Architecture | Transformer + Vision | Detection + Recognition |
| Custom prompt | ✅ Supported | ❌ Not supported |
| OCRBench | 834 (beats GPT-4o) | - |
| Speed | 10-30s/image | 1-3s/image |
| Best for | Understanding content | Pure text extraction |

---

## Related Resources

- [DeepSeek-OCR GitHub](https://github.com/deepseek-ai/DeepSeek-OCR)
- [DeepSeek-OCR HuggingFace](https://huggingface.co/deepseek-ai/DeepSeek-OCR)
- [PaddleOCR GitHub](https://github.com/PaddlePaddle/PaddleOCR)
- [Ollama](https://ollama.ai)
- [This Project GitHub](https://github.com/mr-shaper/opencode-skill-hybrid-ocr)

---

*Last updated: 2026-02-03*
