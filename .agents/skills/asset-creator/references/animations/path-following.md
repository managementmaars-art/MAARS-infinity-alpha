# Path Following Animations

<overview>
**USE THIS FOR:** ANY object following a curved path using `<animateMotion>` + `<mpath>`
</overview>

<getting-the-path>
Generate a path using the script. See [path-creation.md](../path-creation.md) for all path types and parameters.

```bash
python ".claude/skills/asset-creator/scripts/svg-path.py" s_curve --params '{"start_x": 10, "start_y": 50, "end_x": 190, "end_y": 50, "curvature": 0.4}'
```

# Output: M 10 50 Q 50 10 100 50 T 190 50

</getting-the-path>

<using-path-with-animatemotion>

```svg
<svg viewBox="0 0 200 100" xmlns="http://www.w3.org/2000/svg">
  <!-- Visible path for reference -->
  <path id="track"
        d="M10,50 Q50,10 100,50 T190,50"
        fill="none"
        stroke="#ddd"
        stroke-width="2"/>

  <!-- Moving element -->
  <polygon points="0,-5 10,0 0,5" fill="tomato">
    <animateMotion
      dur="3s"
      repeatCount="indefinite"
      rotate="auto">
      <mpath href="#track"/>
    </animateMotion>
  </polygon>
</svg>
```

</using-path-with-animatemotion>

<animatemotion-attributes>
animateMotion Attributes:

| Attribute   | Description        | Values                             |
|-------------|--------------------|------------------------------------|
| dur         | Duration           | "3s", "500ms"                      |
| repeatCount | Repetitions        | "indefinite", number               |
| rotate      | Orient along path  | "auto", "auto-reverse", angle      |
| begin       | Delay before start | "2s", "0s"                         |
| fill        | End behavior       | "freeze" (stay), "remove" (return) |

</animatemotion-attributes>

<related-references>
- [path-creation.md](../path-creation.md) - Generate paths
- [path-drawing.md](./path-drawing.md) - Animate objects along paths

</related-references>
