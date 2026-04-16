# Workflow Phases (Single File Mode)

All phases are MANDATORY. Do NOT skip any phase. AskUserQuestion MUST be used at each decision point.

## Phase 0: Preflight Check

**Purpose**: Verify asciinema is installed and supports convert command.

```bash
/usr/bin/env bash << 'PREFLIGHT_EOF'
if command -v asciinema &>/dev/null; then
  VERSION=$(asciinema --version | head -1)
  echo "asciinema: $VERSION"

  # Check if convert command exists (v2.4+)
  if asciinema convert --help &>/dev/null 2>&1; then
    echo "convert: available"
  else
    echo "convert: MISSING (update asciinema to v2.4+)"
  fi
else
  echo "asciinema: MISSING"
fi
PREFLIGHT_EOF
```

If asciinema is NOT installed or convert is missing, use AskUserQuestion:

```
Question: "asciinema CLI issue detected. How would you like to proceed?"
Header: "Setup"
Options:
  - Label: "Install/upgrade asciinema (Recommended)"
    Description: "Run: brew install asciinema (or upgrade if outdated)"
  - Label: "Show manual instructions"
    Description: "Display installation commands for all platforms"
  - Label: "Cancel"
    Description: "Exit without converting"
```

---

## Phase 1: File Discovery & Selection (MANDATORY)

**Purpose**: Discover .cast files and let user select which to convert.

### Step 1.1: Discover .cast Files

```bash
/usr/bin/env bash << 'DISCOVER_EOF'
# Search for .cast files with metadata
for file in $(fd -e cast . --max-depth 5 2>/dev/null | head -10); do
  SIZE=$(ls -lh "$file" 2>/dev/null | awk '{print $5}')
  LINES=$(wc -l < "$file" 2>/dev/null | tr -d ' ')
  DURATION=$(head -1 "$file" 2>/dev/null | jq -r '.duration // "unknown"' 2>/dev/null)
  BASENAME=$(basename "$file")
  echo "FILE:$file|SIZE:$SIZE|LINES:$LINES|DURATION:$DURATION|NAME:$BASENAME"
done
DISCOVER_EOF
```

### Step 1.2: Present File Selection (MANDATORY AskUserQuestion)

Use discovery results to populate options:

```
Question: "Which recording would you like to convert?"
Header: "Recording"
Options:
  - Label: "{filename} ({size})"
    Description: "{line_count} events, {duration}s duration"
  - Label: "{filename2} ({size2})"
    Description: "{line_count2} events, {duration2}s duration"
  - Label: "Browse for file"
    Description: "Search in a different directory"
  - Label: "Enter path"
    Description: "Provide a custom path to a .cast file"
```

---

## Phase 2: Output Options (MANDATORY)

**Purpose**: Let user configure conversion behavior.

```
Question: "Select conversion options:"
Header: "Options"
multiSelect: true
Options:
  - Label: "Plain text output (Recommended)"
    Description: "Convert to .txt with all ANSI codes stripped"
  - Label: "Create timestamp index"
    Description: "Generate [HH:MM:SS] indexed version for navigation"
  - Label: "Split by idle time"
    Description: "Create separate chunks at 30s+ pauses"
  - Label: "Preserve terminal dimensions"
    Description: "Add header with original terminal size"
```

---

## Phase 3: Output Location (MANDATORY)

**Purpose**: Let user choose where to save the output.

```
Question: "Where should the output be saved?"
Header: "Output"
Options:
  - Label: "Same directory as source (Recommended)"
    Description: "Save {filename}.txt next to {filename}.cast"
  - Label: "Workspace tmp/"
    Description: "Save to ${PWD}/tmp/"
  - Label: "Custom path"
    Description: "Specify a custom output location"
```

---

## Phase 4: Execute Conversion

**Purpose**: Run the conversion and report results.

### Step 4.1: Run asciinema convert

```bash
/usr/bin/env bash << 'CONVERT_EOF'
INPUT_FILE="${1:?Input file required}"
OUTPUT_FILE="${2:?Output file required}"

echo "Converting: $INPUT_FILE"
echo "Output:     $OUTPUT_FILE"
echo ""

# Run conversion
asciinema convert -f txt "$INPUT_FILE" "$OUTPUT_FILE"

if [[ $? -eq 0 && -f "$OUTPUT_FILE" ]]; then
  echo "Conversion successful"
else
  echo "ERROR: Conversion failed"
  exit 1
fi
CONVERT_EOF
```

### Step 4.2: Report Compression

```bash
/usr/bin/env bash << 'REPORT_EOF'
INPUT_FILE="${1:?}"
OUTPUT_FILE="${2:?}"

# Get file sizes (macOS compatible)
INPUT_SIZE=$(stat -f%z "$INPUT_FILE" 2>/dev/null || stat -c%s "$INPUT_FILE" 2>/dev/null)
OUTPUT_SIZE=$(stat -f%z "$OUTPUT_FILE" 2>/dev/null || stat -c%s "$OUTPUT_FILE" 2>/dev/null)

# Calculate ratio
if [[ $OUTPUT_SIZE -gt 0 ]]; then
  RATIO=$((INPUT_SIZE / OUTPUT_SIZE))
else
  RATIO=0
fi

# Human-readable sizes
INPUT_HR=$(numfmt --to=iec "$INPUT_SIZE" 2>/dev/null || echo "$INPUT_SIZE bytes")
OUTPUT_HR=$(numfmt --to=iec "$OUTPUT_SIZE" 2>/dev/null || echo "$OUTPUT_SIZE bytes")

echo ""
echo "=== Conversion Complete ==="
echo "Input:       $INPUT_HR"
echo "Output:      $OUTPUT_HR"
echo "Compression: ${RATIO}:1"
echo "Output path: $OUTPUT_FILE"
REPORT_EOF
```

---

## Phase 5: Create Timestamp Index (if selected)

**Purpose**: Generate indexed version for navigation.

```bash
/usr/bin/env bash << 'INDEX_EOF'
INPUT_CAST="${1:?}"
OUTPUT_INDEX="${2:?}"

echo "Creating timestamp index..."

# Process .cast file to indexed format
(
  echo "# Recording Index"
  echo "# Format: [HH:MM:SS] content"
  echo "#"

  cumtime=0
  tail -n +2 "$INPUT_CAST" | while IFS= read -r line; do
    # Extract timestamp and content
    ts=$(echo "$line" | jq -r '.[0]' 2>/dev/null)
    type=$(echo "$line" | jq -r '.[1]' 2>/dev/null)
    content=$(echo "$line" | jq -r '.[2]' 2>/dev/null)

    if [[ "$type" == "o" && -n "$content" ]]; then
      # Format timestamp as HH:MM:SS
      hours=$((${ts%.*} / 3600))
      mins=$(((${ts%.*} % 3600) / 60))
      secs=$((${ts%.*} % 60))
      timestamp=$(printf "%02d:%02d:%02d" "$hours" "$mins" "$secs")

      # Clean and output (strip ANSI, limit length)
      clean=$(echo "$content" | sed 's/\x1b\[[0-9;]*[a-zA-Z]//g' | tr -d '\r' | head -c 200)
      [[ -n "$clean" ]] && echo "[$timestamp] $clean"
    fi
  done
) > "$OUTPUT_INDEX"

echo "Index created: $OUTPUT_INDEX"
wc -l "$OUTPUT_INDEX"
INDEX_EOF
```

---

## Phase 6: Next Steps (MANDATORY)

**Purpose**: Guide user to next action.

```
Question: "Conversion complete. What's next?"
Header: "Next"
Options:
  - Label: "Analyze with /asciinema-tools:analyze"
    Description: "Run keyword extraction on the converted file"
  - Label: "Open in editor"
    Description: "View the converted text file"
  - Label: "Done"
    Description: "Exit - no further action needed"
```
