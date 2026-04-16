#!/usr/bin/env bash
# Extract PDF to Markdown with multiple fallback methods.
# Usage: extract_pdf.sh <pdf_path>
set -euo pipefail

PDF_PATH="${1:?Usage: extract_pdf.sh <pdf_path>}"

if [ ! -f "$PDF_PATH" ]; then
  echo "ERROR: File not found: $PDF_PATH" >&2
  exit 1
fi

# Method 1: marker-pdf (best quality for papers, tables, complex layouts)
if command -v marker_single &>/dev/null; then
  OUTPUT_DIR="${2:-$HOME/Downloads}"
  marker_single "$PDF_PATH" --output_dir "$OUTPUT_DIR"
  exit 0
fi

# Method 2: pdftotext (fast, good for text-heavy PDFs)
if command -v pdftotext &>/dev/null; then
  pdftotext -layout "$PDF_PATH" - | sed 's/\f/\n---\n/g'
  exit 0
fi

# Method 3: pypdf (no-dependency fallback)
python3 -c "
import sys
try:
    import pypdf
except ImportError:
    print('ERROR: pypdf not installed. Run: pip install pypdf', file=sys.stderr)
    sys.exit(1)

reader = pypdf.PdfReader(sys.argv[1])
print('\n\n'.join(page.extract_text() for page in reader.pages))
" "$PDF_PATH"
