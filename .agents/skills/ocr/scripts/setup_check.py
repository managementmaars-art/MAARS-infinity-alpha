#!/usr/bin/env python3
"""Check OCR Skill environment setup (DeepSeek-OCR + PaddleOCR)."""

import subprocess
import sys


def check_ollama():
    """Check if Ollama is installed."""
    try:
        result = subprocess.run(
            ["ollama", "--version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            version = result.stdout.strip() or result.stderr.strip()
            print(f"[OK] Ollama installed: {version}")
            return True
    except FileNotFoundError:
        pass
    print("[FAIL] Ollama not found. Install with: brew install ollama")
    return False


def check_ollama_running():
    """Check if Ollama server is running."""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("[OK] Ollama server is running")
            return True
    except Exception:
        pass
    print("[FAIL] Ollama server not running. Start with: brew services start ollama")
    return False


def check_deepseek_model():
    """Check if DeepSeek-OCR model is installed."""
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True
        )
        if "deepseek-ocr" in result.stdout.lower():
            for line in result.stdout.split('\n'):
                if 'deepseek-ocr' in line.lower():
                    print(f"[OK] DeepSeek-OCR model installed: {line.strip()}")
                    return True
    except Exception:
        pass
    print("[WARN] DeepSeek-OCR model not found. Pull with:")
    print("       ollama pull deepseek-ocr")
    return False


def check_paddleocr():
    """Check if PaddleOCR is installed (for fast mode)."""
    try:
        import paddleocr
        version = getattr(paddleocr, '__version__', 'installed')
        print(f"[OK] PaddleOCR installed: {version} (for fast mode)")
        return True
    except ImportError:
        print("[WARN] PaddleOCR not found (fast mode unavailable)")
        print("       Install with: pip install paddleocr paddlepaddle")
        return None  # Warning, not failure


def check_requests():
    """Check if requests is installed."""
    try:
        import requests
        print(f"[OK] requests installed")
        return True
    except ImportError:
        print("[FAIL] requests not found. Install with: pip install requests")
        return False


def check_pdf2image():
    """Check if pdf2image is installed."""
    try:
        import pdf2image
        version = getattr(pdf2image, '__version__', 'installed')
        print(f"[OK] pdf2image installed: {version}")
        return True
    except ImportError:
        print("[WARN] pdf2image not found (PDF support unavailable)")
        print("       Install with: pip install pdf2image")
        return None


def check_poppler():
    """Check if poppler is installed for PDF support."""
    try:
        result = subprocess.run(
            ["pdftoppm", "-v"],
            capture_output=True,
            text=True
        )
        version = result.stderr.strip() if result.stderr else "installed"
        print(f"[OK] Poppler installed: {version}")
        return True
    except FileNotFoundError:
        print("[WARN] Poppler not found (PDF support unavailable)")
        print("       Install with: brew install poppler")
        return None


def test_deepseek_ocr():
    """Quick test of DeepSeek-OCR functionality."""
    print("\n--- Quick DeepSeek-OCR Test ---")
    try:
        import requests
        import base64
        import io
        from PIL import Image, ImageDraw

        # Create a simple test image
        img = Image.new('RGB', (200, 50), color='white')
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), "Hello OCR Test", fill='black')

        # Save to bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_base64 = base64.b64encode(img_bytes.getvalue()).decode('utf-8')

        # Call DeepSeek-OCR
        print("Calling DeepSeek-OCR...", end=" ", flush=True)
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "deepseek-ocr",
                "messages": [{
                    "role": "user",
                    "content": "Extract all text from this image.",
                    "images": [img_base64]
                }],
                "stream": False
            },
            timeout=120
        )

        if response.status_code == 200:
            result = response.json()
            text = result.get("message", {}).get("content", "")
            if text:
                print("done")
                print(f"[OK] DeepSeek-OCR test passed. Output: {text[:80]}...")
                return True
            else:
                print("empty response")
                print("[WARN] DeepSeek-OCR returned empty result")
                return False
        else:
            print(f"HTTP {response.status_code}")
            print(f"[FAIL] DeepSeek-OCR test failed")
            return False

    except ImportError as e:
        print(f"skipped (missing: {e})")
        return None
    except Exception as e:
        print(f"failed")
        print(f"[FAIL] DeepSeek-OCR test failed: {e}")
        return False


def main():
    print("=" * 55)
    print("OCR Skill Environment Check")
    print("(DeepSeek-OCR + PaddleOCR Dual Mode)")
    print("=" * 55)
    print()

    print("--- Core Requirements (DeepSeek-OCR) ---")
    checks_core = [
        ("Ollama Installation", check_ollama),
        ("Ollama Server", check_ollama_running),
        ("DeepSeek-OCR Model", check_deepseek_model),
        ("Python requests", check_requests),
    ]

    results_core = []
    for name, check_fn in checks_core:
        try:
            result = check_fn()
            results_core.append((name, result))
        except Exception as e:
            print(f"[ERROR] {name}: {e}")
            results_core.append((name, False))

    print()
    print("--- Optional: Fast Mode (PaddleOCR) ---")
    checks_optional = [
        ("PaddleOCR", check_paddleocr),
    ]

    results_optional = []
    for name, check_fn in checks_optional:
        try:
            result = check_fn()
            results_optional.append((name, result))
        except Exception as e:
            print(f"[ERROR] {name}: {e}")
            results_optional.append((name, False))

    print()
    print("--- Optional: PDF Support ---")
    checks_pdf = [
        ("pdf2image", check_pdf2image),
        ("Poppler", check_poppler),
    ]

    results_pdf = []
    for name, check_fn in checks_pdf:
        try:
            result = check_fn()
            results_pdf.append((name, result))
        except Exception as e:
            print(f"[ERROR] {name}: {e}")
            results_pdf.append((name, False))

    # Run DeepSeek-OCR test if all core checks passed
    all_results = results_core + results_optional + results_pdf
    core_passed = all(r is True for _, r in results_core)

    if core_passed:
        test_result = test_deepseek_ocr()
        all_results.append(("DeepSeek-OCR Test", test_result))

    # Summary
    print()
    print("=" * 55)
    print("Summary")
    print("=" * 55)

    passed = sum(1 for _, r in all_results if r is True)
    failed = sum(1 for _, r in all_results if r is False)
    warnings = sum(1 for _, r in all_results if r is None)

    for name, result in all_results:
        if result is True:
            status = "PASS"
        elif result is False:
            status = "FAIL"
        else:
            status = "WARN"
        print(f"  {name}: {status}")

    print()
    if failed == 0:
        print("All core checks passed! OCR Skill is ready.")
        print()
        print("Quick start:")
        print("  python scripts/ocr.py image.png           # DeepSeek-OCR (smart)")
        print("  python scripts/ocr.py image.png --fast    # PaddleOCR (fast)")
        print("  python scripts/ocr.py image.png --prompt 'Extract table as markdown'")
        return 0
    else:
        print(f"{failed} check(s) failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
