#!/bin/bash

# Example: Convert single draw.io file to PNG
# This example demonstrates basic conversion with commonly used options

# Exit on error
set -e

# Input file
INPUT_FILE="example.drawio"

# Create sample input if it doesn't exist
if [ ! -f "$INPUT_FILE" ]; then
  echo "Creating sample diagram..."
  cat > "$INPUT_FILE" << 'EOF'
<mxfile host="app.diagrams.net" modified="2024-01-01T00:00:00.000Z" agent="Example" version="22.0.0">
  <diagram name="Page-1" id="example-diagram">
    <mxGraphModel dx="1422" dy="794" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="827" pageHeight="1169" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <mxCell id="2" value="Start" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;" vertex="1" parent="1">
          <mxGeometry x="340" y="40" width="120" height="60" as="geometry" />
        </mxCell>
        <mxCell id="3" value="Process" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;" vertex="1" parent="1">
          <mxGeometry x="340" y="140" width="120" height="60" as="geometry" />
        </mxCell>
        <mxCell id="4" value="End" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;" vertex="1" parent="1">
          <mxGeometry x="340" y="240" width="120" height="60" as="geometry" />
        </mxCell>
        <mxCell id="5" value="" style="endArrow=classic;html=1;exitX=0.5;exitY=1;entryX=0.5;entryY=0;" edge="1" parent="1" source="2" target="3">
          <mxGeometry width="50" height="50" relative="1" as="geometry" />
        </mxCell>
        <mxCell id="6" value="" style="endArrow=classic;html=1;exitX=0.5;exitY=1;entryX=0.5;entryY=0;" edge="1" parent="1" source="3" target="4">
          <mxGeometry width="50" height="50" relative="1" as="geometry" />
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
EOF
  echo "✓ Created sample diagram: $INPUT_FILE"
fi

# draw.io CLI path (adjust for your OS)
if [[ "$OSTYPE" == "darwin"* ]]; then
  DRAWIO_CLI="/Applications/draw.io.app/Contents/MacOS/draw.io"
else
  DRAWIO_CLI="drawio"
fi

# Check if draw.io is available
if ! command -v "$DRAWIO_CLI" &> /dev/null && [ ! -f "$DRAWIO_CLI" ]; then
  echo "Error: draw.io CLI not found"
  echo "Please install: https://github.com/jgraph/drawio-desktop/releases"
  exit 1
fi

echo "Converting draw.io file to PNG..."
echo "Input: $INPUT_FILE"
echo ""

# Example 1: Basic conversion (default settings)
echo "Example 1: Basic conversion (scale 1x)"
"$DRAWIO_CLI" -x -f png -o example-basic.png "$INPUT_FILE"
echo "✓ Created: example-basic.png"
echo ""

# Example 2: High resolution (2x scale)
echo "Example 2: High resolution (scale 2x) - Recommended"
"$DRAWIO_CLI" -x -f png -s 2 -o example-2x.png "$INPUT_FILE"
echo "✓ Created: example-2x.png"
echo ""

# Example 3: Transparent background
echo "Example 3: Transparent background"
"$DRAWIO_CLI" -x -f png -s 2 --transparent -o example-transparent.png "$INPUT_FILE"
echo "✓ Created: example-transparent.png"
echo ""

# Example 4: With border
echo "Example 4: With 10px border"
"$DRAWIO_CLI" -x -f png -s 2 --border 10 -o example-border.png "$INPUT_FILE"
echo "✓ Created: example-border.png"
echo ""

# Example 5: Very high resolution (4x for print)
echo "Example 5: Print quality (scale 4x)"
"$DRAWIO_CLI" -x -f png -s 4 -o example-print.png "$INPUT_FILE"
echo "✓ Created: example-print.png"
echo ""

# Example 6: Custom width
echo "Example 6: Fixed width (1200px)"
"$DRAWIO_CLI" -x -f png -w 1200 -o example-1200w.png "$INPUT_FILE"
echo "✓ Created: example-1200w.png"
echo ""

# Example 7: All combined (recommended for documentation)
echo "Example 7: Documentation quality (2x, transparent, 10px border)"
"$DRAWIO_CLI" -x -f png -s 2 --transparent --border 10 -o example-doc.png "$INPUT_FILE"
echo "✓ Created: example-doc.png"
echo ""

# Show file sizes
echo "================================"
echo "File Size Comparison"
echo "================================"
ls -lh example-*.png | awk '{printf "%-30s %10s\n", $9, $5}'
echo ""

echo "All examples completed successfully!"
echo "Check the PNG files to compare different export settings."
