# Edge Point Pivot Examples

<overview>
Objects rotating around a point on their perimeter (not center, not corner).
</overview>

---

<example-polygon-rolling>
**1. Polygon Rolling on Edge (Edge Point Pivot)** - Hexagon rotates around a point on its edge, creating a rolling effect.

```svg
<svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
  <!-- Pivot point on edge (visible marker) -->
  <circle cx="100" cy="100" r="8" fill="#f39c12" />

  <!-- Hexagon - rotates 360° around edge point (100, 100) -->
  <polygon
    points="100,100 150,100 165,130 150,160 100,160 85,130"
    fill="#9b59b6"
    stroke="#8e44ad"
    stroke-width="3"
  >
    <animateTransform
      attributeName="transform"
      type="rotate"
      from="0 100 100"
      to="360 100 100"
      dur="4s"
      repeatCount="indefinite"
    />
  </polygon>
</svg>
```

<key-point-polygon>
**Key point:** The pivot point (100, 100) is on the edge of the polygon, not at its center.
</key-point-polygon>

</example-polygon-rolling>

---

<example-door-hinge>
**2. Door Hinge (Edge Point Pivot)** - Door rotates from its hinge side.

```svg
<svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
  <!-- Door frame -->
  <rect x="45" y="40" width="110" height="130" fill="none" stroke="#7f8c8d" stroke-width="4" />

  <!-- Hinge markers -->
  <circle cx="50" cy="60" r="4" fill="#f39c12" />
  <circle cx="50" cy="150" r="4" fill="#f39c12" />

  <!-- Door - rotates from left edge (50, 100) -->
  <rect x="50" y="45" width="100" height="120" fill="#8b4513" stroke="#5d3a1a" stroke-width="2">
    <animateTransform
      attributeName="transform"
      type="rotate"
      values="0 50 100; -80 50 100; 0 50 100"
      dur="3s"
      repeatCount="indefinite"
    />
  </rect>

  <!-- Door handle -->
  <circle cx="135" cy="105" r="6" fill="#f39c12">
    <animateTransform
      attributeName="transform"
      type="rotate"
      values="0 50 100; -80 50 100; 0 50 100"
      dur="3s"
      repeatCount="indefinite"
    />
  </circle>
</svg>
```

<key-point-door>
**Key point:** Pivot is on the hinge edge (x=50), not the center. Handle needs same animation to stay attached.
</key-point-door>

</example-door-hinge>

---

<example-lever-arm>
**3. Lever Arm (Edge Point Pivot)** - Lever rotates from its fulcrum point on one end.

```svg
<svg width="200" height="150" xmlns="http://www.w3.org/2000/svg">
  <!-- Fulcrum/base -->
  <path d="M 25 120 L 50 90 L 75 120 Z" fill="#34495e" />

  <!-- Pivot point marker -->
  <circle cx="50" cy="90" r="6" fill="#f39c12" />

  <!-- Lever arm - rotates from left end (50, 90) -->
  <rect x="50" y="85" width="130" height="10" fill="#95a5a6" rx="3">
    <animateTransform
      attributeName="transform"
      type="rotate"
      values="-25 50 90; 25 50 90; -25 50 90"
      dur="2s"
      repeatCount="indefinite"
    />
  </rect>

  <!-- Weight on lever end -->
  <rect x="160" y="70" width="25" height="30" fill="#e74c3c" rx="3">
    <animateTransform
      attributeName="transform"
      type="rotate"
      values="-25 50 90; 25 50 90; -25 50 90"
      dur="2s"
      repeatCount="indefinite"
    />
  </rect>
</svg>
```

<key-point-lever>
**Key point:** The pivot is at the fulcrum point on the left edge of the lever. Objects on the lever share the same animation.
</key-point-lever>

</example-lever-arm>
