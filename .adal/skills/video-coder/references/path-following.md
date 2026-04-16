# Path Following Animation Reference

<overview>
When the design spec includes `"type": "follow-path"`, use the `getPathPoint` utility to animate elements along SVG paths.

**Note:** We cannot use `<animateMotion>` because it runs on its own timeline and cannot be controlled by `currentTime` (no scrubbing, pausing, or sync support).

**For creating paths from design specs**, see **[Path Elements Reference](./path-elements.md)**.
</overview>

---

<critical-props>

## CRITICAL: Path Following Utility is Provided as Props

The `getPathPoint` function is **passed as props** from the VideoPlayer component. It is already defined in the VideoPlayer and shared across all scenes.

The utility automatically aligns ANY element with the path direction.

<scene-props-interface>
**Your SceneProps interface must include:**
```typescript
interface SceneProps {
  currentTime: number;
  getPathPoint: (pathD: string, progress: number, elementOrientation: number) => { x: number; y: number; rotation: number };
}
```

**Element orientation uses numeric degrees:**
- 0° = UP
- 90° = RIGHT
- 180° = DOWN
- 270° = LEFT
- Positive = clockwise, Negative = counter-clockwise
</scene-props-interface>

<scene-destructure>
**And your Scene component must destructure them:**
```typescript
const SceneName = React.memo(function SceneName({ currentTime, getPathPoint }: SceneProps) {
  // Your scene code
});
```
</scene-destructure>

</critical-props>

<requirements>

<requirement-use-props>
1. **Use Props**: Access `getPathPoint` from props. DO NOT embed it inline.
</requirement-use-props>

<requirement-progress-clamping>
2. **Progress Clamping**: The utility handles clamping automatically with `Math.min(progress, 1)` to prevent progress from exceeding 1.0.
</requirement-progress-clamping>

<requirement-state-handling>
3. **State Handling**: When element is visible but not moving, determine if it's waiting at the START (before animation begins) or finished at the END (after animation completes). Check the current time against the animation start time.
</requirement-state-handling>

<requirement-sub-components>
4. **Sub-components**: If you create sub-components that need path-following, pass `getPathPoint` to them as props.
</requirement-sub-components>

<requirement-easing>
5. **Easing Synchronization**: When the design specifies an `easing` field in the `follow-path` action, you MUST apply that easing to the progress calculation using the `applyEasing` function. The `applyEasing` function uses cubic bezier curves matching framer-motion exactly.

</requirement-easing>

<requirement-element-orientation>
6. **Determining Element Orientation**: You MUST determine the correct natural orientation of the element:
   - **For SVG assets**: Use the `orientation` field from the design spec
   - **For SVG shapes you create**: Analyze the shape's points/geometry:
     - Arrow `points="0,-15 15,0 0,15"` → Tip at (15,0) = points RIGHT → Use `90`
     - Arrow `points="-8,0 0,-20 8,0"` → Tip at (0,-20) = points UP → Use `0`
     - Arrow `points="0,-8 20,0 0,8"` → Tip at (20,0) = points RIGHT → Use `90`
   - **Rule**: Find where the "front" or "tip" of the element points in its default position (rotation=0)
   - **Coordinate system**: 0° = UP, positive = clockwise, negative = counter-clockwise
</requirement-element-orientation>

<requirement-flipx-handling>
7. **Handling flipX with Path Following**: When an asset has `flipX: true` in the design spec:

   **Transform Order (CRITICAL):**
   ```tsx
   // CORRECT: rotate BEFORE scaleX in the string (CSS applies right-to-left)
   transform: `translate(-50%, -50%) rotate(${pos.rotation}deg) scaleX(-1)`

   // WRONG: old order causes inverted assets
   transform: `translate(-50%, -50%) scaleX(-1) rotate(${pos.rotation}deg)`
   ```

   **Orientation Value:** Use negative orientation to represent the flipped state:
   ```tsx
   // Design: orientation: 90 (RIGHT), flipX: true
   // After flip, asset points LEFT, so use -90 (equivalent to 270)
   const ELEMENT_ORIENTATION = -90;
   const pos = getPathPoint(PATH_D, progress, ELEMENT_ORIENTATION);
   ```

   **Complete Example:**
   ```tsx
   // Design spec: orientation: 90, flipX: true, follow-path animation
   const ELEMENT_ORIENTATION = -90;  // Effective orientation after flip

   const vehiclePos = useMemo(() => {
     if (!isMoving) {
       return getPathPoint(PATH_D, 0, ELEMENT_ORIENTATION);
     }
     const progress = (relTime - START) / DURATION;
     return getPathPoint(PATH_D, progress, ELEMENT_ORIENTATION);
   }, [relTime, isMoving]);

   // Render with correct transform order
   <div style={{
     left: `${vehiclePos.x}px`,
     top: `${vehiclePos.y}px`,
     transform: `translate(-50%, -50%) rotate(${vehiclePos.rotation}deg) scaleX(-1)`
   }}>
     <AssetComponent />
   </div>
   ```
</requirement-flipx-handling>

</requirements>

<quick-example>

```typescript
// Simple usage - element pointing upward (0°) following a curved path
const pos = getPathPoint("M 100 500 Q 500 100 900 500", 0.5, 0);
// Returns: { x: 540, y: 400, rotation: 90 }
```

</quick-example>

<full-usage-example>

```typescript
const PATH_D = "M 100 500 Q 500 100 900 500";
const ANIMATION_START = 1000;
const ANIMATION_DURATION = 3000;
const PATH_EASING = 'easeInOut';  // From design's follow-path action

// Cubic bezier implementation - matches framer-motion/CSS easing curves exactly
const cubicBezier = (p1x: number, p1y: number, p2x: number, p2y: number) => {
  const NEWTON_ITERATIONS = 4;
  const NEWTON_MIN_SLOPE = 0.001;
  const SUBDIVISION_PRECISION = 0.0000001;
  const SUBDIVISION_MAX_ITERATIONS = 10;

  const ax = 3 * p1x - 3 * p2x + 1;
  const bx = 3 * p2x - 6 * p1x;
  const cx = 3 * p1x;
  const ay = 3 * p1y - 3 * p2y + 1;
  const by = 3 * p2y - 6 * p1y;
  const cy = 3 * p1y;

  const sampleCurveX = (t: number) => ((ax * t + bx) * t + cx) * t;
  const sampleCurveY = (t: number) => ((ay * t + by) * t + cy) * t;
  const sampleCurveDerivativeX = (t: number) => (3 * ax * t + 2 * bx) * t + cx;

  const solveCurveX = (x: number) => {
    let t2 = x;
    for (let i = 0; i < NEWTON_ITERATIONS; i++) {
      const x2 = sampleCurveX(t2) - x;
      const d2 = sampleCurveDerivativeX(t2);
      if (Math.abs(x2) < SUBDIVISION_PRECISION) return t2;
      if (Math.abs(d2) < NEWTON_MIN_SLOPE) break;
      t2 -= x2 / d2;
    }
    let t0 = 0, t1 = 1;
    t2 = x;
    for (let i = 0; i < SUBDIVISION_MAX_ITERATIONS; i++) {
      const x2 = sampleCurveX(t2) - x;
      if (Math.abs(x2) < SUBDIVISION_PRECISION) return t2;
      x2 > 0 ? (t1 = t2) : (t0 = t2);
      t2 = (t1 - t0) / 2 + t0;
    }
    return t2;
  };

  return (t: number) => sampleCurveY(solveCurveX(t));
};

// Pre-computed easing functions matching framer-motion/CSS exactly
const easings = {
  easeIn: cubicBezier(0.42, 0, 1, 1),
  easeOut: cubicBezier(0, 0, 0.58, 1),
  easeInOut: cubicBezier(0.42, 0, 0.58, 1),
};

// Easing function at module level - matches framer-motion curves
const applyEasing = (progress: number, easing: string): number => {
  if (progress <= 0) return 0;
  if (progress >= 1) return 1;
  switch (easing) {
    case 'linear':
      return progress;
    case 'easeIn':
      return easings.easeIn(progress);
    case 'easeOut':
      return easings.easeOut(progress);
    case 'easeInOut':
      return easings.easeInOut(progress);
    default:
      return progress;
  }
};

const states = useMemo(() => ({
  showElement: relTime >= 0,
  isElementMoving: relTime >= ANIMATION_START && relTime < (ANIMATION_START + ANIMATION_DURATION)
}), [Math.floor(relTime / 42)]);

const elementPos = useMemo(() => {
  if (!states.showElement) {
    return { x: 100, y: 500, rotation: 0 };
  }

  // Specify element's natural orientation in degrees (0°=UP, 90°=RIGHT, 180°=DOWN, 270°=LEFT)
  // For assets: use orientation from design spec
  // For shapes: determine from geometry
  const ELEMENT_ORIENTATION = 0;  // pointing UP

  if (!states.isElementMoving) {
    if (relTime < ANIMATION_START) {
      // Waiting at START - get rotation from path start
      return getPathPoint(PATH_D, 0, ELEMENT_ORIENTATION);
    } else {
      // Finished at END - get rotation from path end
      return getPathPoint(PATH_D, 1, ELEMENT_ORIENTATION);
    }
  }

  // Animation in progress - calculate current position with EASING
  const rawProgress = Math.min((relTime - ANIMATION_START) / ANIMATION_DURATION, 1);
  const easedProgress = applyEasing(rawProgress, PATH_EASING);  // Apply easing from design!
  return getPathPoint(PATH_D, easedProgress, ELEMENT_ORIENTATION);
}, [relTime, states.isElementMoving, states.showElement]);

// Render - rotation on parent div, animations on motion.div
{states.showElement && (
  <div
    className="absolute z-[10]"
    style={{
      left: `${elementPos.x}px`,
      top: `${elementPos.y}px`,
      transform: `translate(-50%, -50%) rotate(${elementPos.rotation}deg)`  // Rotation HERE
    }}
  >
    <motion.div
      initial={{ opacity: 0, scale: 0.5 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4, type: "spring", bounce: 0.4 }}
    >
      {/* element content */}
    </motion.div>
  </div>
)}
```

</full-usage-example>

<static-path-aligned>

When design includes `pathPositions`, use `getPathPoint` to position static elements along a path.

<static-example>
**Example:**
```typescript
const PATH_D = "M 680 920 C ...";  // From Python script
const PROGRESS = [0.1, 0.3, 0.5, 0.7, 0.9];  // From design

const positions = useMemo(() =>
  PROGRESS.map(p => getPathPoint(PATH_D, p, 90))  // 90° = pointing RIGHT
, [getPathPoint]);

return (
  <svg>
    <path d={PATH_D} stroke="#FF0000" strokeWidth={4} fill="none" />
    {positions.map((pos, i) => (
      <polygon
        key={i}
        points="0,-8 20,0 0,8"
        fill="#FF0000"
        transform={`translate(${pos.x},${pos.y}) rotate(${pos.rotation})`}
      />
    ))}
  </svg>
);

</static-example>

</static-path-aligned>

<common-mistakes>

<mistake-wrong-orientation>
### ❌ Wrong Element Orientation

**Problem:** Element rotates incorrectly along the path (appears sideways, backwards, or at wrong angles)

**Example:**
```typescript
// Arrow shape points RIGHT (tip at x=20)
<polygon points="0,-8 20,0 0,8" />

// WRONG - Telling system arrow points UP (0°)
const pos = getPathPoint(PATH_D, progress, 0);
// Result: Arrow rotates 90° off from path direction
```

**Solution:** Use the correct degree value matching the shape's actual orientation
```typescript
// CORRECT - Arrow tip is at x=20 (positive X = RIGHT = 90°)
const pos = getPathPoint(PATH_D, progress, 90);
```

<how-to-determine-orientation>
1. Look at your shape's points/vertices
2. Find the "tip" or "front" coordinate
3. Determine which direction it points (0° = UP, positive = clockwise):
   - Tip at negative Y (e.g., 0,-20) = UP → Use `0`
   - Tip at positive X (e.g., 20,0) = RIGHT → Use `90`
   - Tip at positive Y (e.g., 0,20) = DOWN → Use `180`
   - Tip at negative X (e.g., -20,0) = LEFT → Use `270`
</how-to-determine-orientation>
</mistake-wrong-orientation>

<mistake-autorotate>
### ❌ Using autoRotate Incorrectly

**Problem:** Design specifies `"autoRotate": false` with fixed `"rotation"`, but coder uses `getPathPoint` rotation

<when-fixed-rotation>
```typescript
// Design: "autoRotate": false, "rotation": -90
<div style={{
  left: `${pos.x}px`,
  top: `${pos.y}px`,
  transform: `translate(-50%, -50%) rotate(-90deg)`  // Use design's fixed value
}} />
```
</when-fixed-rotation>

<when-path-rotation>
```typescript
// Design: "autoRotate": true (or not specified)
<div style={{
  left: `${pos.x}px`,
  top: `${pos.y}px`,
  transform: `translate(-50%, -50%) rotate(${pos.rotation}deg)`  // Use calculated rotation
}} />
```
</when-path-rotation>
</mistake-autorotate>

</common-mistakes>
