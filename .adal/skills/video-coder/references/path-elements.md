# Path Elements Implementation Reference

<overview>
This guide covers how to implement path elements from design specifications.
</overview>

---

<generating-paths>

When design includes `path_params` or `merge_path_params`, generate the SVG path using the Python script. **Do NOT manually write path approximations.**

<why-use-script>
- Ensures paths match exactly what the designer specified
- Prevents misalignment between paths and elements positioned along them
- Supports complex path types (splines, parabolic, etc.) with correct mathematics
</why-use-script>

<how-to-generate-paths>

<steps>
**Step 1: Identify the path type from design**

```json
"path_params": {
  "type": "spline",
  "points": [[680, 920], [750, 750], [820, 520]],
  "tension": 0.4
}
```

**Step 2: Call the Python script**

```bash
python ".claude/skills/asset-creator/scripts/svg-path.py" spline --params '{"points": [[680, 920], [750, 750], [820, 520]], "tension": 0.4}'
```
**Step 3: Use the output in your code**

```typescript
// Copy the EXACT output from the Python script
const PATH_D = "M 680 920 C 708.0 852.0 694.0 910.0 750 750 C 792.0 632.0 776.0 664.0 820 520";

// Use for rendering
<path d={PATH_D} stroke="#FF0000" strokeWidth={4} fill="none" />
```
</steps>

<path-usage-critical>
**CRITICAL:** The same path string must be used for:
- Rendering the path visually
- Positioning elements along it (with `getPathPoint`) - see **[Path Following Reference](./path-following.md)**
- Any path-following animations
</path-usage-critical>
</how-to-generate-paths>

<supported-path-types>

The Python script supports all path types from the design schema:
- `linear` - Straight line
- `arc` - Curved arc segment
- `bezier` - Cubic bezier curve
- `parabolic` - Parabolic arc
- `spline` - Smooth curve through points
- `circular` - Complete circle
- `elliptical` - Elliptical path
- `spiral` - Spiral curve
- `sine_wave` - Sine wave
- `zigzag` - Angular zigzag
- `bounce` - Bouncing trajectory
- `s_curve` - S-shaped curve
</supported-path-types>

</generating-paths>

<composite-paths>

When design uses `merge_path_params`, generate each segment separately and concatenate:

<composite-design-example>
```json
"merge_path_params": [
  {"type": "linear", "start_x": 100, "start_y": 200, "end_x": 300, "end_y": 200},
  {"type": "arc", "start_x": 300, "start_y": 200, "end_x": 300, "end_y": 400, "radius": 100}
]
```
</composite-design-example>

<generate-segments>
Generate each path segment:
```bash
python ".claude/skills/asset-creator/scripts/svg-path.py" linear --params '{"start_x": 100, "start_y": 200, "end_x": 300, "end_y": 200}'
# Output: M 100 200 L 300 200

python ".claude/skills/asset-creator/scripts/svg-path.py" arc --params '{"start_x": 300, "start_y": 200, "end_x": 300, "end_y": 400, "radius": 100, "sweep": 1, "large_arc": 0}'
# Output: M 300 200 A 100 100 0 0 1 300 400
```
</generate-segments>

<combine-segments>
**CRITICAL:** Remove the `M` command from subsequent segments to create a continuous path:
```typescript
const SEGMENT_1 = "M 100 200 L 300 200";
const SEGMENT_2 = "M 300 200 A 100 100 0 0 1 300 400";

// Strip "M x y" from segment 2 and concatenate
const PATH_D = SEGMENT_1 + " " + SEGMENT_2.replace(/^M\s*[\d.-]+\s*[\d.-]+\s*/, "");
// Result: "M 100 200 L 300 200 A 100 100 0 0 1 300 400"
```
</combine-segments>

</composite-paths>

---

<path-rendering>

## Path Rendering

<basic-path>
### Basic Path

```typescript
<svg viewBox="0 0 1080 1920">
  <path
    d={PATH_D}
    stroke="#FF0000"
    strokeWidth={4}
    fill="none"
    opacity={1}
  />
</svg>
```
</basic-path>

<path-with-animation>

Use path-draw animation for progressive drawing:

```typescript
<motion.path
  d={PATH_D}
  stroke="#FF0000"
  strokeWidth={4}
  fill="none"
  initial={{ pathLength: 0, opacity: 0 }}
  animate={{ pathLength: 1, opacity: 1 }}
  transition={{ duration: 2, ease: "easeInOut" }}
/>
```

**IMPORTANT - When synchronized with follow-path:**
- If the design specifies `easing` in BOTH path-draw AND follow-path, you MUST apply easing to BOTH
- Use the same `applyEasing` function for the path's progress calculation (not just the vehicle)
- See **[Path Following Reference](./path-following.md)** for the `applyEasing` function

**Example with easing:**
```typescript
const pathProgress = useMemo(() => {
  if (relTime < PATH_START) return 0;
  const elapsed = relTime - PATH_START;
  const rawProgress = Math.min(elapsed / PATH_DURATION, 1);
  return applyEasing(rawProgress, 'easeInOut');  // Apply easing here too!
}, [Math.floor(relTime / 42)]);

<motion.path
  d={PATH_D}
  animate={{ pathLength: pathProgress }}
  transition={{ duration: 0.1 }}  // Snap to eased value
/>
```

</path-with-animation>

<path-with-arrow-marker>

When design includes `"arrow_marker": "fill"`:

```typescript
<svg viewBox="0 0 1080 1920">
  <defs>
    <marker
      id="arrowhead"
      markerWidth="10"
      markerHeight="10"
      refX="10"
      refY="5"
      orient="auto"
    >
      <polygon points="0,0 10,5 0,10" fill="#FF0000" />
    </marker>
  </defs>
  <path
    d={PATH_D}
    stroke="#FF0000"
    strokeWidth={4}
    fill="none"
    markerEnd="url(#arrowhead)"
  />
</svg>
```
</path-with-arrow-marker>

</path-rendering>

---

<common-pitfalls>

<pitfall-manual-approximation>
❌ **Don't manually approximate paths:**
```typescript
// WRONG - Manual approximation
const PATH_D = "M 680 920 Q 750 750 820 520";
```

✅ **Always use the Python script:**
```typescript
// CORRECT - From Python script output
const PATH_D = "M 680 920 C 708.0 852.0 694.0 910.0 750 750 C 792.0 632.0 776.0 664.0 820 520";
```
</pitfall-manual-approximation>

<pitfall-different-paths>
❌ **Don't use different paths for rendering vs positioning:**
```typescript
// WRONG - Different paths
<path d="M 100 500 Q 500 100 900 500" />
const pos = getPathPoint("M 100 500 C 300 200 700 200 900 500", progress, orientation);
```

✅ **Use the exact same path string:**
```typescript
// CORRECT - Same path
const PATH_D = "M 100 500 C 300 200 700 200 900 500";
<path d={PATH_D} />
const pos = getPathPoint(PATH_D, progress, orientation);
```
</pitfall-different-paths>

</common-pitfalls>
