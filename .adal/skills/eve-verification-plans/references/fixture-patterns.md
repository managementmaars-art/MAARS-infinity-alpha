# Fixture Patterns

How to source, manufacture, and document fixtures for Eve verification plans.

## When Fixtures Are Required

Any verification scenario that uploads, imports, or processes files needs fixtures. The fixture set is part of the verification plan — not optional support material.

## Fixture Selection Order

1. **Reuse existing repo fixtures** if they match accepted file types and are deterministic
2. **Manufacture synthetic fixtures** locally with committed scripts or documented commands
3. **Source small public-domain fixtures** only when local manufacture would reduce realism

Always prefer deterministic, repo-local fixtures. External downloads are fragile and non-reproducible.

## Fixture Matrix

For each accepted file class, include:

| Category | Purpose | Example |
|----------|---------|---------|
| **Minimal valid** | Smallest file that exercises the happy path | 1-line CSV, single-paragraph Markdown |
| **Typical real-world** | Representative file matching real usage | 500-word document, 50-row spreadsheet |
| **Boundary / invalid** | Wrong type, malformed, or edge case | Empty file, wrong MIME, oversized |
| **Cross-format** | Each declared accepted type | PDF + Markdown + CSV if all three accepted |

Not every scenario needs all four categories. Use judgment:
- **Happy path only**: Minimal valid + typical real-world
- **Validation matters**: Add boundary/invalid
- **Multiple formats accepted**: Add cross-format coverage

## Fixture Directory Structure

```
<scenario>/
  fixtures/
    README.md              # Provenance and documentation
    sample-document.md     # Happy path Markdown
    sample-report.pdf      # Happy path PDF
    sample-import.csv      # Happy path CSV
    empty-file.md          # Boundary: empty
    wrong-type.txt         # Boundary: wrong MIME
    scripts/
      make-fixtures.sh     # Generator for synthetic fixtures
```

## Provenance Documentation

Every fixture set includes `fixtures/README.md`:

```markdown
# Fixtures for Scenario 04: Input Ingestion

## Files

| File | Type | Size | Source | Notes |
|------|------|------|--------|-------|
| sample-document.md | Markdown | 2 KB | Hand-written | Lorem ipsum style, 500 words |
| sample-report.pdf | PDF | 15 KB | Generated | `scripts/make-fixtures.sh` |
| sample-import.csv | CSV | 1 KB | Hand-written | 50 rows, 5 columns |
| empty-file.md | Markdown | 0 B | Hand-written | Tests empty file handling |
| wrong-type.txt | Plain text | 100 B | Hand-written | Tests MIME rejection |

## Generation

Run `scripts/make-fixtures.sh` to regenerate synthetic fixtures.
Requires: `pandoc` (for PDF generation).

## Content Policy

All fixtures use synthetic or public-domain content.
No production data, customer documents, or copyrighted material.
```

## Fixture Patterns by File Type

### Markdown

```bash
# Minimal valid
echo "# Test Document\n\nThis is a test." > fixtures/minimal.md

# Typical — use heredoc for multi-paragraph
cat > fixtures/sample-document.md << 'EOF'
# Sample Document

## Introduction

This document tests the ingestion pipeline with representative Markdown content.
It includes headings, paragraphs, lists, and code blocks.

## Features

- Bullet list item one
- Bullet list item two
- Bullet list item three

## Code Example

```python
def hello():
    return "world"
```

## Conclusion

This is the final section of the test document.
EOF
```

### PDF

```bash
# Generate from Markdown via pandoc
pandoc fixtures/sample-document.md -o fixtures/sample-report.pdf

# Or create a minimal PDF with Python
python3 -c "
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
c = canvas.Canvas('fixtures/minimal.pdf', pagesize=letter)
c.drawString(72, 720, 'Test PDF Document')
c.drawString(72, 700, 'This is a minimal test fixture.')
c.save()
"
```

### CSV

```bash
cat > fixtures/sample-import.csv << 'EOF'
id,name,email,status,created_at
1,Alice,alice@example.com,active,2026-01-15
2,Bob,bob@example.com,active,2026-01-16
3,Charlie,charlie@example.com,inactive,2026-01-17
4,Diana,diana@example.com,active,2026-01-18
5,Eve,eve@example.com,pending,2026-01-19
EOF
```

### JSON

```bash
cat > fixtures/test-data.json << 'EOF'
{
  "items": [
    {"id": "item-001", "name": "Test Item", "status": "active"},
    {"id": "item-002", "name": "Another Item", "status": "draft"}
  ],
  "metadata": {
    "version": "1.0",
    "generated": "2026-01-15T00:00:00Z"
  }
}
EOF
```

### Images

```bash
# Generate a simple test image with ImageMagick
convert -size 800x600 xc:white \
  -fill black -pointsize 24 -annotate +50+50 "Test Image" \
  fixtures/test-image.png

# Or with Python/Pillow
python3 -c "
from PIL import Image, ImageDraw
img = Image.new('RGB', (800, 600), 'white')
draw = ImageDraw.Draw(img)
draw.text((50, 50), 'Test Image', fill='black')
img.save('fixtures/test-image.png')
"
```

## Boundary Fixtures

### Empty File
```bash
touch fixtures/empty-file.md
```

### Wrong MIME Type
```bash
echo "This is plain text, not a PDF" > fixtures/wrong-type.pdf
```

### Oversized File (when size limits matter)
```bash
# Generate a file just over the limit
dd if=/dev/urandom bs=1M count=11 > fixtures/oversized.bin  # 11MB if limit is 10MB
```

### Malformed Structure
```bash
# Malformed CSV (inconsistent columns)
cat > fixtures/malformed.csv << 'EOF'
id,name,email
1,Alice
2,Bob,bob@example.com,extra-column
3
EOF
```

## Agent-Friendly Rules

- File names must be descriptive: `sample-document.md`, not `test1.md`
- No spaces in file names — use kebab-case
- Include file extension matching actual MIME type
- Keep fixtures small (under 1 MB unless testing size limits)
- All fixtures must be usable without manual preparation
- Generator scripts must be idempotent and dependency-documented
