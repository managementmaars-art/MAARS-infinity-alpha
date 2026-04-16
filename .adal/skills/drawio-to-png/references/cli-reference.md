# draw.io CLI Reference

Complete reference for the draw.io desktop command-line interface.

## Installation

### macOS
```bash
brew install --cask drawio
```

Or download from: https://github.com/jgraph/drawio-desktop/releases

### Linux (Debian/Ubuntu)
```bash
wget https://github.com/jgraph/drawio-desktop/releases/download/v22.1.16/drawio-amd64-22.1.16.deb
sudo dpkg -i drawio-amd64-22.1.16.deb
```

### Windows
Download installer from: https://github.com/jgraph/drawio-desktop/releases

## CLI Location

- **macOS**: `/Applications/draw.io.app/Contents/MacOS/draw.io`
- **Linux**: `/opt/drawio/drawio` or `drawio` (if in PATH)
- **Windows**: `C:\Program Files\draw.io\draw.io.exe`

## Basic Syntax

```bash
drawio [options] <input-file>
```

## Export Options

### Required Flags

- `-x` or `--export`: Enable export mode
- `-f <format>` or `--format <format>`: Output format
  - `png`: PNG image
  - `jpg` or `jpeg`: JPEG image
  - `svg`: SVG vector image
  - `pdf`: PDF document
  - `vsdx`: Visio format
  - `xml`: Draw.io XML

- `-o <path>` or `--output <path>`: Output file path

### Format-Specific Options

#### PNG/JPG Options

- `-s <scale>` or `--scale <scale>`: Scale factor (default: 1.0)
  - Examples: `1.0` (100%), `2.0` (200%), `3.0` (300%)
  
- `-w <width>` or `--width <width>`: Output width in pixels
  - Overrides scale if specified
  
- `-h <height>` or `--height <height>`: Output height in pixels
  - Overrides scale if specified

- `--transparent`: Transparent background (PNG only)
  - Default: white background
  
- `-b <color>` or `--border <size>`: Border size in pixels
  - Default: 0
  - Example: `--border 10` adds 10px border

- `-q <quality>` or `--quality <quality>`: JPEG quality (1-100)
  - Default: 90
  - Only applies to JPEG format

#### Multi-page Options

- `-p <page>` or `--page <page>`: Page index to export (0-based)
  - Default: all pages
  - Example: `-p 0` exports first page
  
- `--all-pages`: Export all pages as separate files
  - Appends page number to filename
  
- `--page-range <range>`: Page range to export
  - Examples: `0-2`, `1,3,5`

#### SVG Options

- `--embed-svg-images`: Embed images in SVG (base64)
  - Default: external references
  
- `--svg-theme <theme>`: Apply theme
  - Options: `dark`, `kennedy`, `minimal`, `sketch`

#### PDF Options

- `--crop`: Crop PDF to diagram size
  - Default: full page size

## Advanced Options

### Viewport and Rendering

- `--uncompressed`: Disable compression for XML output
  
- `--embed-diagram`: Embed diagram XML in output (PNG, SVG)
  - Allows re-editing from image file

### File Handling

- `--create`: Create output file even if input is empty

## Usage Examples

### Basic Conversion

```bash
# Convert to PNG (default scale)
drawio -x -f png -o output.png input.drawio

# Convert to SVG
drawio -x -f svg -o output.svg input.drawio

# Convert to PDF
drawio -x -f pdf -o output.pdf input.drawio
```

### High Resolution Export

```bash
# 2x resolution (192 DPI)
drawio -x -f png -s 2 -o output-2x.png input.drawio

# 4x resolution (384 DPI) for print
drawio -x -f png -s 4 -o output-4x.png input.drawio

# Custom width
drawio -x -f png -w 3000 -o output-wide.png input.drawio
```

### Transparent Background

```bash
# PNG with transparent background
drawio -x -f png --transparent -o output.png input.drawio

# High-res transparent PNG
drawio -x -f png -s 2 --transparent -o output-2x.png input.drawio
```

### With Border

```bash
# Add 10px border
drawio -x -f png --border 10 -o output.png input.drawio

# High-res with border and transparency
drawio -x -f png -s 2 --border 20 --transparent -o output.png input.drawio
```

### Multi-page Diagrams

```bash
# Export first page only
drawio -x -f png -p 0 -o page-1.png input.drawio

# Export all pages as separate files
drawio -x -f png --all-pages -o output.png input.drawio
# Creates: output-1.png, output-2.png, etc.

# Export specific pages
drawio -x -f png --page-range 0,2,4 -o output.png input.drawio
```

### Batch Processing

```bash
# Convert all .drawio files in directory
for file in *.drawio; do
  drawio -x -f png -s 2 -o "${file%.drawio}.png" "$file"
done

# With error handling
for file in *.drawio; do
  if drawio -x -f png -s 2 -o "${file%.drawio}.png" "$file"; then
    echo "Converted: $file"
  else
    echo "Failed: $file"
  fi
done
```

## Exit Codes

- `0`: Success
- `1`: General error
- `2`: Invalid arguments

## Environment Variables

### Display Settings (Linux)

When running headless (no X server):

```bash
export DISPLAY=:0
xvfb-run drawio -x -f png -o output.png input.drawio
```

### Electron Options

```bash
# Disable GPU acceleration (if rendering issues)
export ELECTRON_DISABLE_GPU=1

# Increase memory limit
export NODE_OPTIONS="--max-old-space-size=4096"
```

## Troubleshooting

### Common Issues

1. **Command not found**
   - Verify draw.io is installed
   - Use full path to executable
   - Add to PATH if needed

2. **Export fails silently**
   - Check input file is valid draw.io format
   - Verify output directory exists and is writable
   - Check disk space

3. **Blank output**
   - Ensure diagram has visible elements
   - Check scale/dimensions aren't too large
   - Verify all referenced resources exist

4. **Memory errors**
   - Reduce scale factor
   - Export fewer pages at once
   - Increase Node.js memory limit

### Debug Mode

```bash
# Enable verbose output
DEBUG=* drawio -x -f png -o output.png input.drawio

# Electron debug logs
ELECTRON_ENABLE_LOGGING=1 drawio -x -f png -o output.png input.drawio
```

## Performance Tips

1. **Use appropriate scale**
   - Don't use higher scale than needed
   - Consider file size vs. quality tradeoff

2. **Batch processing**
   - Process files in parallel (with caution)
   - Limit concurrent processes to avoid memory issues

3. **Optimize diagrams**
   - Simplify complex shapes
   - Reduce embedded images
   - Use references instead of embedding

## API Alternative

For programmatic access without installing desktop app:

```bash
# Using Docker
docker run --rm -v $(pwd):/data rlespinasse/drawio-cli \
  -x -f png -s 2 -o /data/output.png /data/input.drawio
```

## Version Information

```bash
# Check version
drawio --version

# Help
drawio --help
```

## Official Documentation

- GitHub: https://github.com/jgraph/drawio-desktop
- Issues: https://github.com/jgraph/drawio-desktop/issues
- CLI examples: https://github.com/jgraph/drawio-desktop/wiki/Command-Line-Interface
