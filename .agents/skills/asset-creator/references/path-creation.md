# Path Creation

<overview>
Generate SVG path `d` attributes using the Python script:

Use the bash tool to call the python script below.

```bash
python ".claude/skills/asset-creator/scripts/svg-path.py" <equation> --params '<json_params>'
```
</overview>

<path-types>
To understand the different path types - Read [paths_guidelines.md](./paths_guidelines.md)

</path-types>

---

<merging-paths>
Use `merge-paths.py` to combine multiple path strings into a single continuous path:

```bash
python ./scripts/merge-paths.py --paths '["M 50 400 L 150 100", "M 150 100 Q 250 400 350 250", "M 350 250 L 500 250"]'
```

<merge-output>
**Output:**
```
M 50 400 L 150 100 Q 250 400 350 250 L 500 250
```
</merge-output>

<merge-tip>
**Tip:** Ensure each segment's start point matches the previous segment's end point.
</merge-tip>

</merging-paths>

<path-styles>

<dashed-path>
**Dashed Path:** Use `stroke-dasharray` with two values: dash length and gap length.
```svg
<path d="M 100 200 L 700 200" fill="none" stroke="#333" stroke-width="3" stroke-dasharray="20 10"/>
```

</dashed-path>

<dotted-path>
**Dotted Path:** Use `stroke-dasharray` with small equal values and `stroke-linecap="round"`.
```svg
<path d="M 100 200 L 700 200" fill="none" stroke="#333" stroke-width="3" stroke-dasharray="1 10" stroke-linecap="round"/>
```

</dotted-path>

</path-styles>

---

<show-hide-path>
Use `opacity` to show or hide a path with animation.

<hide-path>
**Hide Path (visible → invisible)**
```svg
<path d="M 100 300 Q 400 100 700 300" fill="none" stroke="#333" stroke-width="3" opacity="1">
  <animate attributeName="opacity" from="1" to="0" dur="1s" fill="freeze"/>
</path>
```

</hide-path>

<show-path>
**Show Path (invisible → visible)**
```svg
<path d="M 100 300 Q 400 100 700 300" fill="none" stroke="#333" stroke-width="3" opacity="0">
  <animate attributeName="opacity" from="0" to="1" dur="1s" fill="freeze"/>
</path>
```

</show-path>

</show-hide-path>

<coordinate-system>
- Origin (0,0) at top-left of the svg
- X increases right, Y increases down
- Plan parameters within your viewBox dimensions

</coordinate-system>

<viewbox-for-video>
**CRITICAL**: When creating SVG paths for video scenes, the viewBox must match the viewport size:

- **Portrait (9:16)**: `viewBox="0 0 1080 1920"`
- **Landscape (16:9)**: `viewBox="0 0 1920 1080"`

Path coordinates are absolute screen positions, so the viewBox must match the canvas dimensions exactly.

</viewbox-for-video>

<boundary-constraints>
**All path points must stay within valid bounds:**
- No coordinate value should be negative (minimum is 0)
- X coordinates must not exceed the screen's width
- Y coordinates must not exceed the screen's height

</boundary-constraints>

<related-references>
Use the generated path to make an object follow it: See [path-following.md](./animations/path-following.md)
Use the path drawing animations: See [path-drawing.md](./animations/path-drawing.md)

</related-references>
