# PDF Type Detection Guide

Identifying the PDF type is the most important first step. Using the wrong extraction approach wastes hours.

## Detection Checklist

Run these quick checks before choosing any tool:

### Test 1: Copy-Paste Check (30 seconds)

Open the PDF in Preview (macOS) or any PDF viewer. Copy a formula or math expression. Paste into a text editor.

- **You see Unicode math symbols** (∑, π, α, β, γ, →, ≤, ≥, ∈): → **Type A** (Word-generated)
- **You see garbled glyphs or nothing**: → possibly Type B (LaTeX) or Type C (scanned)
- **Copy is impossible (nothing selectable)**: → **Type C** (scanned/image)

### Test 2: Font Inspection (2 minutes)

In macOS Preview: File → Properties → Fonts, or use:

```bash
pdffonts paper.pdf
```

- **Embedded fonts like "TimesNewRoman", "Arial", "Calibri"**: → **Type A** (Word/Office)
- **Computer Modern, Latin Modern, CM-Super**: → **Type B** (LaTeX/TeX)
- **No fonts listed**: → **Type C** (scanned images)

### Test 3: marker-pdf Smoke Test (1 minute)

```bash
uv run --python 3.13 --with marker-pdf marker_single paper.pdf /tmp/marker-out --output_format markdown
cat /tmp/marker-out/*.md | head -50
```

- **Output has LaTeX math** (`$\frac{...}$`, `\sum`, etc.): → probably Type B or C
- **Output has zero math** or replaces formulas with Unicode text: → **Type A** (marker-pdf's Unicode bug)
- **Output is empty / crash with torch error**: → Type A or Type C with incompatible paper size

### Test 4: arxiv Check (10 seconds)

Look for the paper on arxiv.org. If found:

- Download the `.tar.gz` source: `https://arxiv.org/src/{arxiv-id}`
- Extract and check for `.tex` files
- If `.tex` exists: **extract directly from source** — skip PDF entirely

---

## Type A: Word-Generated PDF (Most Common for Recent Academic Papers)

**Examples**: SSRN papers, working papers, journal submissions from MS Word

### Identification

- Microsoft-style fonts (Times New Roman, Calibri, Arial, Georgia)
- Unicode math symbols visible when copy-pasted
- `pdffonts` shows no math-specific fonts
- `marker-pdf` returns empty math sections or Unicode text instead of LaTeX

### What Works

| Tool          | Outcome                                                    |
| ------------- | ---------------------------------------------------------- |
| `pymupdf4llm` | ✅ Best prose extraction with structure (tables, headings) |
| `pdftotext`   | ✅ Plain text, loses table structure                       |
| `markitdown`  | ✅ Alternative prose, slight over-spacing                  |
| `marker-pdf`  | ❌ Returns empty or Unicode-only output                    |

### Math Extraction Approach

**There is no automated solution.** You must:

1. Read the PDF page by page
2. Screenshot each page containing equations (macOS: Cmd+Shift+4)
3. Write LaTeX manually by inspecting the visual formula
4. Cross-reference against any code implementations if available

**Tools that help**:

- Read PDF as screenshots within Claude Code using the Read tool on PNG files
- Use reference implementations (Python code, Julia notebooks) to verify formulas
- Search online for the specific formula + paper title to find existing LaTeX typesettings

### Efficiency Tips for Manual Transcription

- Work top-to-bottom: prose first, then formulas in order
- Number equations as you go — reference numbers make validation easier
- For recurring symbols, decide convention early (e.g., $\hat{S}$ vs $\tilde{S}$)
- Use `aligned` inside `$$` for single-line display (no `\\`), ` ```math ``` ` for multi-line

---

## Type B: LaTeX-Generated PDF

**Examples**: ArXiv preprints, ACM/IEEE proceedings, Springer/Elsevier journals

### Identification

- Computer Modern or Latin Modern fonts
- Precise mathematical spacing (kerning around operators)
- Text is selectable but copy-pasted math may show glyph codes not Unicode
- arxiv.org source download yields `.tex` files

### What Works

| Tool                | Outcome                                                      |
| ------------------- | ------------------------------------------------------------ |
| `pymupdf4llm`       | ✅ Good prose, Unicode math chars (still needs manual LaTeX) |
| `pdftotext -layout` | ✅ Decent structure preservation                             |
| `marker-pdf`        | ⚠️ Partially works — may extract some LaTeX, but unreliable  |

### Math Extraction: Prefer Source

If arxiv source is available, skip PDF:

```bash
# Download source
curl -L "https://arxiv.org/src/2412.12345" -o paper-source.tar.gz
tar -xzf paper-source.tar.gz
ls *.tex

# Convert .tex to markdown (approximate)
pandoc main.tex -o paper.md --mathjax
```

**Warning**: Pandoc `.tex` → markdown conversion is imperfect for complex papers. Use it as a starting point and clean up.

---

## Type C: Scanned/Image PDF

**Examples**: Older papers, scans of physical documents, digitized theses

### Identification

- Zero selectable text
- `pdffonts` returns nothing
- All pages are raster images at constant DPI

### What Works

| Tool          | Outcome                          |
| ------------- | -------------------------------- |
| `marker-pdf`  | ✅ Best neural OCR pipeline      |
| `tesseract`   | ✅ Open-source OCR fallback      |
| `pymupdf4llm` | ❌ Returns empty or headers only |

### marker-pdf Pipeline

```bash
# Install (requires GPU or CPU inference)
pip install marker-pdf

# Convert single file
marker_single paper.pdf /tmp/marker-out --output_format markdown

# If torch error on Apple Silicon:
PYTORCH_ENABLE_MPS_FALLBACK=1 marker_single paper.pdf /tmp/marker-out

# Check output quality
cat /tmp/marker-out/*.md | wc -l   # should be > 100 lines for a real paper
```

**Quality check**: marker-pdf quality varies. Always review the output equations against the original PDF screenshots. Expect 80-90% accuracy on clean scans; less on degraded documents.

---

## Decision Flowchart

```
Can you copy-paste text from the PDF?
├── No → TYPE C (scanned) → use marker-pdf
└── Yes
    ├── Copy-pasted math shows Unicode symbols (∑ π α)?
    │   └── Yes → TYPE A (Word) → pymupdf4llm + manual math transcription
    └── No
        ├── Is paper on arxiv with .tex source?
        │   └── Yes → extract from .tex (bypass PDF entirely)
        └── No → TYPE B (LaTeX) → pymupdf4llm + marker-pdf attempt
```
