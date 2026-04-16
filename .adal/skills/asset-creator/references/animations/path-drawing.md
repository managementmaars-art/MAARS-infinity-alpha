# Path Drawing Animation

<prerequisite>
**Prerequisite:** Read [path-creation.md](../path-creation.md) to generate path `d` attributes.
</prerequisite>

<overview>
Animates the drawing of a path itself (line appearing on screen).
</overview>

<technique>
Uses `stroke-dasharray` and `stroke-dashoffset` to progressively reveal a path:
- Set both to the path's total length (hides entire path)
- Animate `stroke-dashoffset` from full length to 0 (reveals path)

</technique>

<basic-pattern>

```svg
<path d="M 100 400 Q 400 200 700 400"
      fill="none"
      stroke="#333"
      stroke-width="3"
      stroke-dasharray="850"
      stroke-dashoffset="850">
  <animate
    attributeName="stroke-dashoffset"
    from="850"
    to="0"
    dur="2s"
    fill="freeze"/>
</path>
```

</basic-pattern>

<with-object-following>

```svg
<svg viewBox="0 0 800 500">
  <defs>
    <path id="trajectory" d="M 100 400 Q 400 200 700 400"/>
  </defs>

  <!-- Drawn path -->
  <use href="#trajectory" fill="none" stroke="#94a3b8" stroke-width="2"
       stroke-dasharray="900" stroke-dashoffset="900">
    <animate attributeName="stroke-dashoffset" from="900" to="0" dur="2s" fill="freeze"/>
  </use>

  <!-- Following object -->
  <circle r="10" fill="#ef4444">
    <animateMotion dur="2s" fill="freeze">
      <mpath href="#trajectory"/>
    </animateMotion>
  </circle>
</svg>
```

</with-object-following>

<key-points>
- Path needs `fill="none"` and visible `stroke`
- Estimate dash length larger than actual path length (works fine)
- Use `stroke-linecap="round"` for smoother ends
- `fill="freeze"` keeps path visible after animation

</key-points>

<related-references>
- [path-creation.md](../path-creation.md) - Generate paths
- [path-following.md](./path-following.md) - Animate objects along paths

</related-references>
