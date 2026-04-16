# Arrow Guidelines

<overview>
Arrowheads that attach to path ends to show direction.
There are 3 types of arrow heads that you can use: `fill` (solid), `hollow` (outlined), `line` (V-shape).
</overview>

---

<arrow-path-creation>
To create the arrows path: Read [path-creation.md](./references/path-creation.md)

</arrow-path-creation>

<marker-field-reference>
Marker Field Reference:

| Field | Purpose |
|-------|---------|
| `id` | Unique name to reference this marker |
| `markerWidth` | Arrow width in pixels |
| `markerHeight` | Arrow height in pixels |
| `refX` | Horizontal position where arrow tip aligns with path end |
| `refY` | Vertical center point of the arrow |
| `orient="auto"` | Auto-rotates to match path direction |
| `markerUnits="strokeWidth"` | Scales with path stroke width |

</marker-field-reference>

---

<arrow-sizing-formula>

<formula-calculation>
When `markerUnits="strokeWidth"` is used, **ALWAYS calculate**:
markerWidth = 40 / strokeWidth
markerHeight = markerWidth
refX = markerWidth × 0.9
refY = markerWidth / 2
polygon points = "0,0 {markerWidth},{refY} 0,{markerHeight}"
</formula-calculation>

<formula-explanation>
**Why:** Final arrowhead size = markerWidth × strokeWidth = 40px (optimal)
</formula-explanation>

<formula-example>
**Example for strokeWidth={10}:**
- markerWidth = 40/10 = 4.5
- markerHeight = 4.5
- refX = 4.05
- refY = 2.25
- points = "0,0 4.5,2.25 0,4.5"
</formula-example>

</arrow-sizing-formula>

<creating-markers>
Define once in `<defs>`, reuse on any path.

```xml
<defs>
 <marker
  id="arrowhead-filled"
  markerWidth="10"
  markerHeight="7"
  refX="9"
  refY="3.5"
  orient="auto"
  markerUnits="strokeWidth">
  <polygon points="0 0, 10 3.5, 0 7" fill="#3b82f6"/>
 </marker>
</defs>
```

</creating-markers>

---

<using-markers>

<marker-attachment>
Add `marker-end="url(#marker-id)"` to attach arrow:

```xml
<path
 d="M 50 220 Q 200 100 350 220"
 fill="none"
 stroke="#10b981"
 stroke-width="3"
 marker-end="url(#arrowhead-line)"/>
```
</marker-attachment>

<key-attributes>
**Key attributes:**
- `d` = Path shape
- `fill="none"` = No fill, just stroke
- `stroke` = Line color
- `stroke-width` = Line thickness
- `marker-end` = Attaches the arrow (references marker id)
</key-attributes>

</using-markers>

---
