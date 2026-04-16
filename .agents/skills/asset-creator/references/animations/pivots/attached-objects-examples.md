# Center Pivot with Attached Objects Examples

<overview>
Complex systems where a parent object rotates from its center and child objects stay attached.

**Critical concept:** Each attached object needs its own `animateTransform` with a pivot point calculated relative to the parent's pivot.
</overview>

---

<example-seesaw>
**1. Seesaw (Center Pivot with Attached Objects)** - Plank rotates from center, people on ends stay attached.

```svg
<svg width="300" height="200" xmlns="http://www.w3.org/2000/svg">
  <!-- Support stand -->
  <path d="M 135 150 L 150 120 L 165 150 Z" fill="#34495e" />
  <circle cx="150" cy="120" r="6" fill="#2c3e50" />

  <!-- Seesaw plank - rotates from center (150, 120) -->
  <rect x="50" y="115" width="200" height="10" fill="#8b4513" rx="3">
    <animateTransform
      attributeName="transform"
      type="rotate"
      values="-20 150 120; 20 150 120; -20 150 120"
      dur="3s"
      repeatCount="indefinite"
    />
  </rect>

  <!-- Left person - attached to left end -->
  <!-- Pivot offset: plank center (150,120) minus person position (70,115) = (80, 5) -->
  <g transform="translate(70, 115)">
    <circle cx="0" cy="-15" r="8" fill="#3498db">
      <animateTransform
        attributeName="transform"
        type="rotate"
        values="-20 80 5; 20 80 5; -20 80 5"
        dur="3s"
        repeatCount="indefinite"
      />
    </circle>
    <rect x="-6" y="-7" width="12" height="20" fill="#2980b9" rx="2">
      <animateTransform
        attributeName="transform"
        type="rotate"
        values="-20 80 5; 20 80 5; -20 80 5"
        dur="3s"
        repeatCount="indefinite"
      />
    </rect>
  </g>

  <!-- Right person - attached to right end -->
  <!-- Pivot offset: plank center (150,120) minus person position (230,115) = (-80, 5) -->
  <g transform="translate(230, 115)">
    <circle cx="0" cy="-15" r="8" fill="#e74c3c">
      <animateTransform
        attributeName="transform"
        type="rotate"
        values="-20 -80 5; 20 -80 5; -20 -80 5"
        dur="3s"
        repeatCount="indefinite"
      />
    </circle>
    <rect x="-6" y="-7" width="12" height="20" fill="#c0392b" rx="2">
      <animateTransform
        attributeName="transform"
        type="rotate"
        values="-20 -80 5; 20 -80 5; -20 -80 5"
        dur="3s"
        repeatCount="indefinite"
      />
    </rect>
  </g>
</svg>
```

<pivot-calculation-seesaw>
**Pivot calculation for attached objects:**
```
Child pivot = Parent pivot - Child position
Left person:  (150, 120) - (70, 115)  = (80, 5)
Right person: (150, 120) - (230, 115) = (-80, 5)
```
</pivot-calculation-seesaw>

</example-seesaw>

---

<example-balance-scale>
**2. Balance Scale (Center Pivot with Attached Objects)** - Beam rotates from center, pans on ends stay attached and level.

```svg
<svg width="300" height="200" xmlns="http://www.w3.org/2000/svg">
  <!-- Stand -->
  <rect x="145" y="80" width="10" height="60" fill="#34495e" />
  <circle cx="150" cy="80" r="8" fill="#2c3e50" />

  <!-- Scale beam - rotates from center (150, 80) -->
  <rect x="70" y="77" width="160" height="6" fill="#95a5a6" rx="2">
    <animateTransform
      attributeName="transform"
      type="rotate"
      values="-15 150 80; 15 150 80; -15 150 80"
      dur="4s"
      repeatCount="indefinite"
    />
  </rect>

  <!-- Left pan - attached to left end -->
  <!-- Pivot offset: beam center (150,80) minus pan position (80,80) = (70, 0) -->
  <g transform="translate(80, 80)">
    <line x1="0" y1="0" x2="0" y2="20" stroke="#7f8c8d" stroke-width="2">
      <animateTransform
        attributeName="transform"
        type="rotate"
        values="-15 70 0; 15 70 0; -15 70 0"
        dur="4s"
        repeatCount="indefinite"
      />
    </line>
    <ellipse cx="0" cy="25" rx="25" ry="8" fill="#bdc3c7" stroke="#95a5a6" stroke-width="2">
      <animateTransform
        attributeName="transform"
        type="rotate"
        values="-15 70 0; 15 70 0; -15 70 0"
        dur="4s"
        repeatCount="indefinite"
      />
    </ellipse>
    <!-- Weight on left pan -->
    <circle cx="0" cy="20" r="8" fill="#e74c3c">
      <animateTransform
        attributeName="transform"
        type="rotate"
        values="-15 70 0; 15 70 0; -15 70 0"
        dur="4s"
        repeatCount="indefinite"
      />
    </circle>
  </g>

  <!-- Right pan - attached to right end -->
  <!-- Pivot offset: beam center (150,80) minus pan position (220,80) = (-70, 0) -->
  <g transform="translate(220, 80)">
    <line x1="0" y1="0" x2="0" y2="20" stroke="#7f8c8d" stroke-width="2">
      <animateTransform
        attributeName="transform"
        type="rotate"
        values="-15 -70 0; 15 -70 0; -15 -70 0"
        dur="4s"
        repeatCount="indefinite"
      />
    </line>
    <ellipse cx="0" cy="25" rx="25" ry="8" fill="#bdc3c7" stroke="#95a5a6" stroke-width="2">
      <animateTransform
        attributeName="transform"
        type="rotate"
        values="-15 -70 0; 15 -70 0; -15 -70 0"
        dur="4s"
        repeatCount="indefinite"
      />
    </ellipse>
    <!-- Weight on right pan -->
    <circle cx="0" cy="20" r="6" fill="#3498db">
      <animateTransform
        attributeName="transform"
        type="rotate"
        values="-15 -70 0; 15 -70 0; -15 -70 0"
        dur="4s"
        repeatCount="indefinite"
      />
    </circle>
  </g>
</svg>
```

<pivot-calculation-scale>
**Pivot calculation for attached objects:**
```
Child pivot = Parent pivot - Child position
Left pan:  (150, 80) - (80, 80)  = (70, 0)
Right pan: (150, 80) - (220, 80) = (-70, 0)
```
</pivot-calculation-scale>

</example-balance-scale>

---

<key-formula>
When an object is placed using `transform="translate(x, y)"`, calculate its animation pivot as:

```
animationPivotX = parentPivotX - translateX
animationPivotY = parentPivotY - translateY
```

<attached-requirements>
All attached elements must have:
- Same rotation angles as parent
- Same duration as parent
- Pivot point calculated using the formula above
</attached-requirements>

</key-formula>
