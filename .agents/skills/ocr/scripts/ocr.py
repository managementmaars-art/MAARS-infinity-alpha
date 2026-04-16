#!/usr/bin/env python3
"""
OCR Skill - Dual Mode Implementation
- Default: DeepSeek-OCR via Ollama (VLM, supports custom prompts)
- Fast mode: Native PaddleOCR (pure OCR, faster)

Supports: Images (PNG, JPG, JPEG, BMP, GIF, WEBP, TIFF) and PDFs
"""

import argparse
import base64
import json
import os
import sys
import tempfile
from pathlib import Path

# Suppress warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import warnings
warnings.filterwarnings('ignore')

# Supported file extensions
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp", ".tiff", ".tif"}
PDF_EXTENSION = ".pdf"

# Default settings
DEFAULT_MODEL = "deepseek-ocr"
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")


# ============================================
# DeepSeek-OCR via Ollama
# ============================================

def resize_image_if_needed(image_path: str, max_size: int = 1536) -> str:
    """Resize image if too large, returns path to (possibly new) image."""
    try:
        from PIL import Image
    except ImportError:
        return image_path  # Can't resize, use original

    with Image.open(image_path) as img:
        width, height = img.size
        if width <= max_size and height <= max_size:
            return image_path

        # Calculate new size maintaining aspect ratio
        ratio = min(max_size / width, max_size / height)
        new_size = (int(width * ratio), int(height * ratio))

        print(f"Resizing image from {width}x{height} to {new_size[0]}x{new_size[1]}", file=sys.stderr)

        resized = img.resize(new_size, Image.Resampling.LANCZOS)
        temp_file = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
        resized.save(temp_file.name, "JPEG", quality=90)
        return temp_file.name


def ocr_with_deepseek(image_path: str, prompt: str = "Extract all text from this image.") -> str:
    """Perform OCR using DeepSeek-OCR via Ollama."""
    try:
        import requests
    except ImportError:
        print("Error: requests not found. Install with: pip install requests", file=sys.stderr)
        sys.exit(1)

    # Resize large images to prevent timeout
    processed_path = resize_image_if_needed(image_path)

    # Read and encode image
    with open(processed_path, "rb") as f:
        image_base64 = base64.b64encode(f.read()).decode("utf-8")

    # Call Ollama API
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json={
                "model": DEFAULT_MODEL,
                "messages": [{
                    "role": "user",
                    "content": prompt,
                    "images": [image_base64]
                }],
                "stream": False
            },
            timeout=300
        )
        response.raise_for_status()
        result = response.json()

        # Cleanup temp file if we resized
        if processed_path != image_path:
            try:
                os.unlink(processed_path)
            except Exception:
                pass

        return result.get("message", {}).get("content", "")
    except requests.exceptions.ConnectionError:
        print("Error: Cannot connect to Ollama. Start with: brew services start ollama", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("Error: Ollama request timed out.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error calling Ollama: {e}", file=sys.stderr)
        sys.exit(1)


# ============================================
# Native PaddleOCR (Fast Mode)
# ============================================

_paddle_ocr_instance = None

def get_paddle_ocr_instance(lang='ch'):
    """Get or create PaddleOCR instance."""
    global _paddle_ocr_instance
    if _paddle_ocr_instance is None:
        try:
            from paddleocr import PaddleOCR
        except ImportError:
            print("Error: paddleocr not found. Install with: pip install paddleocr paddlepaddle", file=sys.stderr)
            sys.exit(1)
        print("Initializing PaddleOCR (first run may download models)...", file=sys.stderr)
        os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'
        _paddle_ocr_instance = PaddleOCR(lang=lang)
    return _paddle_ocr_instance


def ocr_with_paddle(image_path: str, lang: str = 'ch') -> str:
    """Perform OCR using native PaddleOCR."""
    ocr = get_paddle_ocr_instance(lang)
    result = ocr.ocr(image_path)

    if result is None or len(result) == 0:
        return ""

    # Extract text from results (PaddleOCR 3.x format)
    lines = []
    for page_result in result:
        if page_result is None:
            continue
        # New format: page_result is a dict with 'rec_texts' key
        if isinstance(page_result, dict):
            rec_texts = page_result.get('rec_texts', [])
            lines.extend(rec_texts)
        # Old format: page_result is a list of [box, (text, confidence)]
        elif isinstance(page_result, list):
            for line in page_result:
                if line and len(line) >= 2:
                    text = line[1][0] if isinstance(line[1], tuple) else line[1]
                    lines.append(text)

    return '\n'.join(lines)


# ============================================
# PDF Processing
# ============================================

def pdf_to_images(pdf_path: str) -> list:
    """Convert PDF pages to temporary image files."""
    try:
        from pdf2image import convert_from_path
    except ImportError:
        print("Error: pdf2image not found. Install with: pip install pdf2image", file=sys.stderr)
        print("Also ensure poppler is installed: brew install poppler", file=sys.stderr)
        sys.exit(1)

    try:
        images = convert_from_path(pdf_path, dpi=200)
    except Exception as e:
        print(f"Error converting PDF: {e}", file=sys.stderr)
        print("Ensure poppler is installed: brew install poppler", file=sys.stderr)
        sys.exit(1)

    temp_paths = []
    for i, image in enumerate(images):
        temp_file = tempfile.NamedTemporaryFile(
            suffix=".png", delete=False, prefix=f"page_{i+1}_"
        )
        image.save(temp_file.name, "PNG")
        temp_paths.append(temp_file.name)
        print(f"Converted page {i+1}/{len(images)}", file=sys.stderr)

    return temp_paths


# ============================================
# Main Processing Functions
# ============================================

def process_image(image_path: str, prompt: str = None, fast_mode: bool = False, lang: str = 'ch') -> dict:
    """Process a single image and return OCR result."""
    print(f"Processing: {image_path}", file=sys.stderr)

    if fast_mode:
        print("Mode: PaddleOCR (fast)", file=sys.stderr)
        text = ocr_with_paddle(image_path, lang)
    else:
        print("Mode: DeepSeek-OCR (smart)", file=sys.stderr)
        text = ocr_with_deepseek(image_path, prompt or "Extract all text from this image.")

    return {
        "source": str(image_path),
        "type": "image",
        "mode": "paddle" if fast_mode else "deepseek",
        "text": text
    }


def process_pdf(pdf_path: str, prompt: str = None, fast_mode: bool = False, lang: str = 'ch') -> dict:
    """Process a PDF file by converting to images and OCR each page."""
    print(f"Processing PDF: {pdf_path}", file=sys.stderr)
    temp_images = pdf_to_images(pdf_path)

    pages = []
    try:
        for i, image_path in enumerate(temp_images):
            print(f"OCR page {i+1}/{len(temp_images)}...", file=sys.stderr)
            if fast_mode:
                text = ocr_with_paddle(image_path, lang)
            else:
                text = ocr_with_deepseek(image_path, prompt or "Extract all text from this image.")
            pages.append({
                "page": i + 1,
                "text": text
            })
    finally:
        # Cleanup temporary files
        for temp_path in temp_images:
            try:
                os.unlink(temp_path)
            except Exception:
                pass

    return {
        "source": str(pdf_path),
        "type": "pdf",
        "mode": "paddle" if fast_mode else "deepseek",
        "total_pages": len(pages),
        "pages": pages
    }


def format_output(result: dict, as_json: bool = False) -> str:
    """Format the OCR result for output."""
    if as_json:
        return json.dumps(result, indent=2, ensure_ascii=False)

    if result.get("type") == "pdf":
        parts = []
        for page in result.get("pages", []):
            parts.append(f"=== Page {page['page']} ===\n{page['text']}")
        return "\n\n".join(parts)
    else:
        return result.get("text", "")


def main():
    parser = argparse.ArgumentParser(
        description="OCR Skill - DeepSeek-OCR (default) or PaddleOCR (fast mode)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ocr.py image.png                     # DeepSeek-OCR (smart mode)
  python ocr.py image.png --fast              # PaddleOCR (fast mode)
  python ocr.py image.png --prompt "提取表格为markdown"
  python ocr.py document.pdf                  # OCR all pages of a PDF
  python ocr.py image.png --json              # Output as JSON
  python ocr.py doc.pdf -o result.txt         # Save to file

Modes:
  Default (DeepSeek-OCR): VLM-based, supports custom prompts, smarter
  --fast (PaddleOCR): Traditional OCR, faster, pure text extraction

Supported formats:
  Images: PNG, JPG, JPEG, BMP, GIF, WEBP, TIFF
  Documents: PDF
        """
    )
    parser.add_argument("input_file", help="Image or PDF file to process")
    parser.add_argument("--fast", "-f", action="store_true",
                        help="Use PaddleOCR for faster pure text extraction")
    parser.add_argument("--prompt", "-p",
                        help="Custom prompt for DeepSeek-OCR (ignored in fast mode)")
    parser.add_argument("--lang", "-l", default="ch",
                        help="Language for PaddleOCR (default: ch for Chinese+English)")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    parser.add_argument("--output", "-o", help="Output file path (default: stdout)")

    args = parser.parse_args()

    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: File not found: {args.input_file}", file=sys.stderr)
        sys.exit(1)

    suffix = input_path.suffix.lower()

    if suffix == PDF_EXTENSION:
        result = process_pdf(str(input_path), args.prompt, args.fast, args.lang)
    elif suffix in IMAGE_EXTENSIONS:
        result = process_image(str(input_path), args.prompt, args.fast, args.lang)
    else:
        print(f"Error: Unsupported file type: {suffix}", file=sys.stderr)
        print(f"Supported: PDF, {', '.join(sorted(IMAGE_EXTENSIONS))}", file=sys.stderr)
        sys.exit(1)

    output_text = format_output(result, args.json)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_text)
        print(f"Output saved to: {args.output}", file=sys.stderr)
    else:
        print(output_text)


if __name__ == "__main__":
    main()
