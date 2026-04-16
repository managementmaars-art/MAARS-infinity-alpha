# Batch Mode Workflow (Phases 7-10)

Batch mode converts all .cast files in a directory with organized output. Activated via `--batch` flag.

**Use case**: Convert 1000+ iTerm2 auto-logged recordings efficiently.

## Phase 7: Batch Source Selection

**Purpose**: Select source directory for batch conversion.

**Trigger**: `--batch` flag without `--source` argument.

```
Question: "Select source directory for batch conversion:"
Header: "Source"
Options:
  - Label: "~/asciinemalogs (iTerm2 default)" (Recommended)
    Description: "Auto-logged iTerm2 recordings"
  - Label: "~/Downloads"
    Description: "Recent downloads containing .cast files"
  - Label: "Current directory"
    Description: "Convert .cast files in current working directory"
  - Label: "Custom path"
    Description: "Specify a custom source directory"
```

**Skip condition**: If `--source` argument provided, skip this phase.

---

## Phase 8: Batch Output Organization

**Purpose**: Configure output directory structure.

**Trigger**: `--batch` flag without `--output-dir` argument.

```
Question: "Where should converted files be saved?"
Header: "Output"
Options:
  - Label: "~/Downloads/cast-txt/ (Recommended)"
    Description: "Organized output directory, easy to find"
  - Label: "Same as source"
    Description: "Save .txt files next to .cast files"
  - Label: "Custom directory"
    Description: "Specify a custom output location"
```

**Skip condition**: If `--output-dir` argument provided, skip this phase.

---

## Phase 9: Execute Batch Conversion

**Purpose**: Convert all files with progress reporting.

```bash
/usr/bin/env bash << 'BATCH_EOF'
SOURCE_DIR="${1:?Source directory required}"
OUTPUT_DIR="${2:?Output directory required}"
SKIP_EXISTING="${3:-true}"

mkdir -p "$OUTPUT_DIR"

echo "=== Batch Conversion ==="
echo "Source:        $SOURCE_DIR"
echo "Output:        $OUTPUT_DIR"
echo "Skip existing: $SKIP_EXISTING"
echo ""

total=0
converted=0
skipped=0
failed=0
total_input_size=0
total_output_size=0

# Count files first
total=$(find "$SOURCE_DIR" -maxdepth 1 -name "*.cast" -type f 2>/dev/null | wc -l | tr -d ' ')
echo "Found $total .cast files"
echo ""

for cast_file in "$SOURCE_DIR"/*.cast; do
  [[ -f "$cast_file" ]] || continue

  basename=$(basename "$cast_file" .cast)
  txt_file="$OUTPUT_DIR/${basename}.txt"

  # Skip if already converted (and skip mode enabled)
  if [[ "$SKIP_EXISTING" == "true" && -f "$txt_file" ]]; then
    echo "SKIP: $basename (already exists)"
    ((skipped++))
    continue
  fi

  # Get input size
  input_size=$(stat -f%z "$cast_file" 2>/dev/null || stat -c%s "$cast_file" 2>/dev/null)

  # Convert
  if asciinema convert -f txt "$cast_file" "$txt_file" 2>/dev/null; then
    output_size=$(stat -f%z "$txt_file" 2>/dev/null || stat -c%s "$txt_file" 2>/dev/null)
    if [[ $output_size -gt 0 ]]; then
      ratio=$((input_size / output_size))
    else
      ratio=0
    fi
    echo "OK:   $basename (${ratio}:1 compression)"
    ((converted++))
    total_input_size=$((total_input_size + input_size))
    total_output_size=$((total_output_size + output_size))
  else
    echo "FAIL: $basename"
    ((failed++))
  fi
done

echo ""
echo "=== Batch Complete ==="
echo "Converted: $converted"
echo "Skipped:   $skipped"
echo "Failed:    $failed"

if [[ $total_output_size -gt 0 ]]; then
  overall_ratio=$((total_input_size / total_output_size))
  echo "Overall compression: ${overall_ratio}:1"
fi
echo "Output directory: $OUTPUT_DIR"
BATCH_EOF
```

---

## Phase 10: Batch Next Steps

**Purpose**: Guide user after batch conversion.

```
Question: "Batch conversion complete. What's next?"
Header: "Next"
Options:
  - Label: "Batch analyze with /asciinema-tools:analyze --batch"
    Description: "Run keyword extraction on all converted files"
  - Label: "Open output directory"
    Description: "View converted files in Finder"
  - Label: "Done"
    Description: "Exit - no further action needed"
```
