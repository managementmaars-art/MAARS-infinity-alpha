# 3D Shapes (Cubes, Boxes, etc.)

When designing isometric or orthographic 3D shapes like cubes:

**ALWAYS define as a SINGLE element** - never create separate elements for each face.

## CORRECT - Single unified element:
```json
{
  "id": "cube",
  "type": "shape",
  "content": "A cube shown in orthographic projection with three visible faces: front, top, and right side. The cube is rendered as THREE ADJOINING PARALLELOGRAMS forming a cube illusion. Front face is [COLOR] filling a square area. Top face is [LIGHTER COLOR] forming a parallelogram above. Right side face is [DARKER COLOR] forming a parallelogram on the right edge. Each face has a thin dark outline separating the faces."
}
```

## WRONG - Separate face elements (causes gaps/misalignment):
```json
{ "id": "cube_front_face", ... },
{ "id": "cube_top_face", ... },
{ "id": "cube_right_face", ... }
```

## Why this matters:
- Single element = code generator creates ONE SVG with shared coordinate system
- Separate elements = code generator creates multiple positioned divs that may not align properly, causing visible gaps between faces

## Key description phrases to include:
- "three adjoining parallelograms forming a cube illusion"
- "Front face... Top face... Right side face..." (all in ONE element description)
- Specify colors for each face within the single description
