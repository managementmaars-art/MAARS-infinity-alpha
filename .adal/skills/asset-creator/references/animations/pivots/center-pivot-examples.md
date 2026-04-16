# Center Pivot Examples

<overview>
Objects rotating around their geometric center point.
</overview>

<example-fan>
**1. Fan (Center Pivot)** - Multiple blades rotating continuously from the center hub.

```svg
<svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
  <!-- Fan blades container - rotate from center (100, 100) -->
  <g>
    <!-- Blade 1 -->
    <ellipse cx="135" cy="100" rx="35" ry="12" fill="#3498db" opacity="0.8" />
    <!-- Blade 2 -->
    <ellipse cx="135" cy="100" rx="35" ry="12" fill="#3498db" opacity="0.8" transform="rotate(120 100 100)" />
    <!-- Blade 3 -->
    <ellipse cx="135" cy="100" rx="35" ry="12" fill="#3498db" opacity="0.8" transform="rotate(240 100 100)" />

    <animateTransform
      attributeName="transform"
      type="rotate"
      from="0 100 100"
      to="360 100 100"
      dur="2s"
      repeatCount="indefinite"
    />
  </g>

  <!-- Center hub (drawn after blades to be on top) -->
  <circle cx="100" cy="100" r="15" fill="#2c3e50" />
</svg>
```

<key-point-fan>
**Key point:** Wrap all rotating elements in a `<g>` group and apply animation to the group.
</key-point-fan>

</example-fan>

---

<example-wheel>
**2. Wheel (Center Pivot)** - Simple wheel with spokes rotating continuously.

```svg
<svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
  <!-- Wheel group - rotates from center -->
  <g>
    <!-- Outer rim -->
    <circle cx="100" cy="100" r="70" fill="none" stroke="#34495e" stroke-width="8" />

    <!-- Spokes -->
    <line x1="100" y1="30" x2="100" y2="170" stroke="#7f8c8d" stroke-width="4" />
    <line x1="30" y1="100" x2="170" y2="100" stroke="#7f8c8d" stroke-width="4" />
    <line x1="50" y1="50" x2="150" y2="150" stroke="#7f8c8d" stroke-width="4" />
    <line x1="150" y1="50" x2="50" y2="150" stroke="#7f8c8d" stroke-width="4" />

    <animateTransform
      attributeName="transform"
      type="rotate"
      from="0 100 100"
      to="360 100 100"
      dur="3s"
      repeatCount="indefinite"
    />
  </g>

  <!-- Center hub (stationary) -->
  <circle cx="100" cy="100" r="12" fill="#2c3e50" />
</svg>
```

<key-point-wheel>
**Key point:** The hub can be drawn outside the rotating group to remain stationary.
</key-point-wheel>

</example-wheel>

---

<example-gear>
**3. Gear (Center Pivot)** - Gear with teeth rotating from center.

```svg
<svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
  <!-- Gear group - rotates from center -->
  <g>
    <!-- Gear body -->
    <circle cx="100" cy="100" r="50" fill="#95a5a6" />

    <!-- Teeth (8 teeth around the edge) -->
    <rect x="95" y="40" width="10" height="15" fill="#95a5a6" />
    <rect x="95" y="40" width="10" height="15" fill="#95a5a6" transform="rotate(45 100 100)" />
    <rect x="95" y="40" width="10" height="15" fill="#95a5a6" transform="rotate(90 100 100)" />
    <rect x="95" y="40" width="10" height="15" fill="#95a5a6" transform="rotate(135 100 100)" />
    <rect x="95" y="40" width="10" height="15" fill="#95a5a6" transform="rotate(180 100 100)" />
    <rect x="95" y="40" width="10" height="15" fill="#95a5a6" transform="rotate(225 100 100)" />
    <rect x="95" y="40" width="10" height="15" fill="#95a5a6" transform="rotate(270 100 100)" />
    <rect x="95" y="40" width="10" height="15" fill="#95a5a6" transform="rotate(315 100 100)" />

    <animateTransform
      attributeName="transform"
      type="rotate"
      from="0 100 100"
      to="360 100 100"
      dur="4s"
      repeatCount="indefinite"
    />
  </g>

  <!-- Center hole -->
  <circle cx="100" cy="100" r="10" fill="#2c3e50" />
</svg>
```

<key-point-gear>
**Key point:** All teeth are pre-positioned using static `transform="rotate()"` and the whole group animates together.
</key-point-gear>

</example-gear>
