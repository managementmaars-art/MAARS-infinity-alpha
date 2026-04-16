# End/Edge Pivot Examples

<overview>
Objects rotating from one fixed endpoint or anchor point.
</overview>

---

<example-clock>
**1. Clock (End Pivot)** - Multiple hands rotating from the center point. Each hand has its own rotation speed.

```svg
<svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
  <!-- Clock face -->
  <circle cx="100" cy="100" r="80" fill="#2d3436" stroke="#dfe6e9" stroke-width="4" />

  <!-- Hour markers -->
  <line x1="100" y1="25" x2="100" y2="35" stroke="#dfe6e9" stroke-width="2" />
  <line x1="175" y1="100" x2="165" y2="100" stroke="#dfe6e9" stroke-width="2" />
  <line x1="100" y1="175" x2="100" y2="165" stroke="#dfe6e9" stroke-width="2" />
  <line x1="25" y1="100" x2="35" y2="100" stroke="#dfe6e9" stroke-width="2" />

  <!-- Hour hand - rotates from center (100, 100) -->
  <rect x="96" y="60" width="8" height="40" fill="#e74c3c" rx="4">
    <animateTransform
      attributeName="transform"
      type="rotate"
      from="0 100 100"
      to="360 100 100"
      dur="12s"
      repeatCount="indefinite"
    />
  </rect>

  <!-- Minute hand -->
  <rect x="97" y="40" width="6" height="60" fill="#3498db" rx="3">
    <animateTransform
      attributeName="transform"
      type="rotate"
      from="0 100 100"
      to="360 100 100"
      dur="4s"
      repeatCount="indefinite"
    />
  </rect>

  <!-- Second hand -->
  <line x1="100" y1="100" x2="100" y2="30" stroke="#f39c12" stroke-width="2">
    <animateTransform
      attributeName="transform"
      type="rotate"
      from="0 100 100"
      to="360 100 100"
      dur="2s"
      repeatCount="indefinite"
    />
  </line>

  <!-- Center dot -->
  <circle cx="100" cy="100" r="5" fill="#ecf0f1" />
</svg>
```

<key-point-clock>
**Key point:** All hands share the same pivot point (100, 100) but have different durations.
</key-point-clock>

</example-clock>

---

<example-speedometer>
**2. Speedometer (End Pivot)** - Needle oscillates between min and max values using the `values` attribute.

```svg
<svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
  <!-- Dial background -->
  <path
    d="M 20 100 A 80 80 0 0 1 180 100"
    fill="#2d3436"
    stroke="#dfe6e9"
    stroke-width="4"
  />

  <!-- Dial markers -->
  <line x1="40" y1="60" x2="50" y2="70" stroke="#dfe6e9" stroke-width="2" />
  <line x1="100" y1="30" x2="100" y2="45" stroke="#dfe6e9" stroke-width="2" />
  <line x1="160" y1="60" x2="150" y2="70" stroke="#dfe6e9" stroke-width="2" />

  <!-- Speed labels -->
  <text x="45" y="85" fill="#dfe6e9" font-size="12">0</text>
  <text x="95" y="55" fill="#dfe6e9" font-size="12">100</text>
  <text x="145" y="85" fill="#dfe6e9" font-size="12">200</text>

  <!-- Needle - rotates from base (100, 100) -->
  <path d="M 97 100 L 100 35 L 103 100 Z" fill="#e74c3c">
    <animateTransform
      attributeName="transform"
      type="rotate"
      values="-60 100 100; 60 100 100; -60 100 100"
      dur="3s"
      repeatCount="indefinite"
    />
  </path>

  <!-- Pivot point -->
  <circle cx="100" cy="100" r="6" fill="#ecf0f1" />
</svg>
```

<key-point-speedometer>
**Key point:** Uses `values` for oscillating motion between -60° and 60°.
</key-point-speedometer>

</example-speedometer>

---

<example-pendulum>
**3. Pendulum (End Pivot)** - Swings from top anchor point. Both rod and bob need the same animation.

```svg
<svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
  <!-- Anchor point -->
  <rect x="80" y="40" width="40" height="10" fill="#34495e" rx="2" />
  <circle cx="100" cy="50" r="5" fill="#2c3e50" />

  <!-- Pendulum rod - rotates from top (100, 50) -->
  <line x1="100" y1="50" x2="100" y2="150" stroke="#95a5a6" stroke-width="3">
    <animateTransform
      attributeName="transform"
      type="rotate"
      values="-30 100 50; 30 100 50; -30 100 50"
      dur="2s"
      repeatCount="indefinite"
    />
  </line>

  <!-- Pendulum bob - same animation, same pivot -->
  <circle cx="100" cy="150" r="15" fill="#e74c3c">
    <animateTransform
      attributeName="transform"
      type="rotate"
      values="-30 100 50; 30 100 50; -30 100 50"
      dur="2s"
      repeatCount="indefinite"
    />
  </circle>
</svg>
```

<key-point-pendulum>
**Key point:** Pivot is at the TOP (100, 50) where the pendulum hangs from. Both rod and bob share identical animation.
</key-point-pendulum>

</example-pendulum>
