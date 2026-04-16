# Rotation Animations

<overview>
Rotation animations cover various ways objects can rotate around different pivot points. This includes rotations from endpoints, center points, edge points, and complex systems with attached child objects.

</overview>

<categories>

<category-end-pivot>
**Category 1: End/Edge Pivot (Rotation from one end)**
Objects rotating from one endpoint.

**Use for:** ANY object that rotates from ONE FIXED END/ANCHOR POINT - clock hands, compass needles, speedometer gauges, pendulums, catapult arms, trebuchet arms, lever arms, door opening from hinges, etc.

**Examples:** Clock hands, Speedometer needle, Pendulum

→ See [end-pivot-examples.md](./pivots/end-pivot-examples.md)

</category-end-pivot>

---

<category-center-pivot>
**Category 2: Center Pivot (Rotation from middle)**
Simple objects rotating around their center point.

**Use for:** ANY object that SPINS AROUND ITS CENTER - fans, propellers, wheels, gears, spinning coins, rotating platforms, etc.

**Examples:** Fan blades

→ See [center-pivot-examples.md](./pivots/center-pivot-examples.md)

</category-center-pivot>

---

<category-edge-pivot>
**Category 3: Edge Point Pivot (Rotation from arbitrary point on edge)**
Objects rotating around any point along their perimeter (not corner, not center).

**Use for:** ANY object rotating around A POINT ON ITS EDGE (not a corner, not the center) - unique rotation patterns for special effects

**Examples:** Polygon edge rotation

→ See [edge-point-pivot-examples.md](./pivots/edge-point-pivot-examples.md)

</category-edge-pivot>

---

<category-attached-objects>
**Category 4: Center Pivot with Attached Objects (Complex systems)**
Parent object rotates, child objects maintain their attachment and correct orientation.

**Use for:** ANY system where A PARENT OBJECT ROTATES and CHILD OBJECTS STAY ATTACHED - seesaws, balance scales, Ferris wheels with seats, rotating platforms with objects, etc.

**Examples:** Seesaw, Balance Scale

→ See [attached-objects-examples.md](./pivots/attached-objects-examples.md)

</category-attached-objects>

</categories>

---

<key-formula>
All rotation animations use the SVG `animateTransform` with `type="rotate"`:

```xml
<animateTransform
  attributeName="transform"
  type="rotate"
  from="startAngle pivotX pivotY"
  to="endAngle pivotX pivotY"
  dur="duration"
  repeatCount="indefinite"
/>
```

<syntax-options>

<continuous-rotation>
**Continuous rotation (from/to):**
```xml
from="0 100 100"
to="360 100 100"
```
</continuous-rotation>

<oscillating-rotation>
**Oscillating/back-and-forth (values):**
```xml
values="-30 100 50; 30 100 50; -30 100 50"
```
</oscillating-rotation>

</syntax-options>

<rotation-parameters>
Parameters:

| Parameter | Description |
|-----------|-------------|
| `angle` | Rotation angle in degrees |
| `pivotX` | X coordinate of pivot point |
| `pivotY` | Y coordinate of pivot point |
| `dur` | Duration (e.g., "2s", "500ms") |
| `repeatCount` | "indefinite" for looping, or a number |

</rotation-parameters>

</key-formula>

<pivot-point-guidelines>
1. **End Pivot**: Set pivot at the fixed/anchor end of the object
2. **Center Pivot**: Set pivot at the geometric center
3. **Edge Pivot**: Set pivot at a point on the perimeter
4. **Attached Objects**: Each child needs its own `animateTransform` with pivot relative to the parent's pivot

</pivot-point-guidelines>

<summary>
1. **End/Edge Pivot** - 3 examples (clock, speedometer, pendulum)
2. **Center Pivot** - 1 example (fan)
3. **Edge Point Pivot** - 1 example (polygon)
4. **Center Pivot with Attached Objects** - 2 examples (seesaw, balance scale)

**Total: 7 unique rotation animations across 4 categories**

</summary>
