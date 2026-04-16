# Path References

## Choosing the Right Path Type

### Decision Guide

**Simple single-curve paths:**
- ✅ Use **Linear** - Straight lines
- ✅ Use **Arc** - Single curved segment between two points
- ✅ Use **Parabolic** - Throw/projectile arcs

**Complex multi-curve paths:**
- ✅ Use **Spline** - Smooth path through multiple points
- ✅ Use **Bezier** - Custom curves with precise control points
- ✅ Use **Elliptical** - Complete oval/circular motion

**Closed loop paths:**
- ✅ Use **Circular** - Perfect circles
- ✅ Use **Elliptical** - Ovals
- ✅ Use **Spline** with first and last points matching

---

## Arc Path

Single curved arc segment.

### Use Cases
- Door swings
- Partial circles
- Simple curves

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `start_x` | number | Yes | Starting X coordinate (absolute screen position) |
| `start_y` | number | Yes | Starting Y coordinate (absolute screen position) |
| `end_x` | number | Yes | Ending X coordinate (absolute screen position) |
| `end_y` | number | Yes | Ending Y coordinate (absolute screen position) |
| `radius` | number | Yes | Arc radius in pixels |
| `sweep` | number | No | Direction arc curves toward. Default 0 (UP) |
| `large_arc` | number | No | 0 = short arc, 1 = long arc (>180°). Default 0 |

### Sweep Reference

| Value | Direction |
|-------|-----------|
| 0 | UP ↑ |
| 1 | DOWN ↓ |
| 2 | LEFT ← |
| 3 | RIGHT → |

### path_params

```json
"path_params": {
  "type": "arc",
  "start_x": 100,
  "start_y": 300,
  "end_x": 400,
  "end_y": 300,
  "radius": 200,
  "sweep": 0,
  "large_arc": 0
}
```

## Bezier Path

Custom cubic bezier curve with two control points.

### Use Cases
- Custom curved arrows
- Flowing connections
- Smooth custom paths

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `start_x` | number | Yes | Starting X coordinate (absolute screen position) |
| `start_y` | number | Yes | Starting Y coordinate (absolute screen position) |
| `cp1_x` | number | Yes | First control point X (absolute, influences curve near start) |
| `cp1_y` | number | Yes | First control point Y (absolute) |
| `cp2_x` | number | Yes | Second control point X (absolute, influences curve near end) |
| `cp2_y` | number | Yes | Second control point Y (absolute) |
| `end_x` | number | Yes | Ending X coordinate (absolute screen position) |
| `end_y` | number | Yes | Ending Y coordinate (absolute screen position) |

### path_params

```json
"path_params": {
  "type": "bezier",
  "start_x": 100,
  "start_y": 400,
  "cp1_x": 200,
  "cp1_y": 100,
  "cp2_x": 600,
  "cp2_y": 100,
  "end_x": 700,
  "end_y": 400
}
```

## Bounce Path

Bouncing trajectory with decreasing height.

### Use Cases
- Ball bouncing
- Hopping motion
- Rebounding objects

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `start_x` | number | Yes | Starting X coordinate (absolute screen position) |
| `start_y` | number | Yes | Starting Y coordinate (absolute screen position) |
| `end_x` | number | Yes | Ending X coordinate (absolute screen position) |
| `ground_y` | number | Yes | Y-coordinate of ground/floor (absolute screen position) |
| `initial_height` | number | Yes | Height of first bounce ABOVE ground_y |
| `bounces` | number | Yes | Number of bounces |
| `decay` | number | No | Height reduction factor per bounce (default 0.6) |

### path_params

```json
"path_params": {
  "type": "bounce",
  "start_x": 100,
  "start_y": 100,
  "end_x": 700,
  "ground_y": 400,
  "initial_height": 250,
  "bounces": 4,
  "decay": 0.6
}
```

## Circular Path

Complete circle path around a center point.

### Use Cases
- Orbits
- Spinning paths
- Rotation indicators

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `center_x` | number | Yes | Center X coordinate (absolute screen position) |
| `center_y` | number | Yes | Center Y coordinate (absolute screen position) |
| `radius` | number | Yes | Circle radius in pixels |

### path_params

```json
"path_params": {
  "type": "circular",
  "center_x": 400,
  "center_y": 300,
  "radius": 150
}
```

## Elliptical Path

Oval-shaped closed path.

### Use Cases
- Stretched orbits
- Oval rotations
- Elliptical motion paths

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `center_x` | number | Yes | Center X coordinate (absolute screen position) |
| `center_y` | number | Yes | Center Y coordinate (absolute screen position) |
| `radius_x` | number | Yes | Horizontal radius |
| `radius_y` | number | Yes | Vertical radius |

### path_params

```json
"path_params": {
  "type": "elliptical",
  "center_x": 400,
  "center_y": 300,
  "radius_x": 200,
  "radius_y": 100
}
```

## Linear Path

Straight line from point A to point B.

### Use Cases
- Laser beams
- Direct arrows
- Straight connections

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `start_x` | number | Yes | Starting X coordinate (absolute screen position) |
| `start_y` | number | Yes | Starting Y coordinate (absolute screen position) |
| `end_x` | number | Yes | Ending X coordinate (absolute screen position) |
| `end_y` | number | Yes | Ending Y coordinate (absolute screen position) |

### path_params

```json
"path_params": {
  "type": "linear",
  "start_x": 100,
  "start_y": 100,
  "end_x": 700,
  "end_y": 400
}
```

## Parabolic Path

Arc that rises then falls (or vice versa).

### Use Cases
- Projectiles
- Thrown objects
- Jumping arcs

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `start_x` | number | Yes | Starting X coordinate (absolute screen position) |
| `start_y` | number | Yes | Starting Y coordinate (absolute screen position) |
| `end_x` | number | Yes | Ending X coordinate (absolute screen position) |
| `end_y` | number | Yes | Ending Y coordinate (absolute screen position) |
| `arc_height` | number | Yes | Height above the line between start and end (negative for downward arc) |

### path_params

```json
"path_params": {
  "type": "parabolic",
  "start_x": 100,
  "start_y": 400,
  "end_x": 700,
  "end_y": 400,
  "arc_height": 200
}
```

## S-Curve Path

Smooth S-shaped transition between two points.

### Use Cases
- Winding roads
- Smooth directional changes
- Flowing transitions

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `start_x` | number | Yes | Starting X coordinate (absolute screen position) |
| `start_y` | number | Yes | Starting Y coordinate (absolute screen position) |
| `end_x` | number | Yes | Ending X coordinate (absolute screen position) |
| `end_y` | number | Yes | Ending Y coordinate (absolute screen position) |
| `curvature` | number | No | Bend intensity, range 0-1 (default 0.5) |

### path_params

```json
"path_params": {
  "type": "s_curve",
  "start_x": 100,
  "start_y": 200,
  "end_x": 700,
  "end_y": 500,
  "curvature": 0.4
}
```

## Sine Wave Path

Smooth oscillating wave pattern from start to end point.

### Use Cases
- Snake movement
- Water waves
- Oscillations
- Heat/energy radiation
- Signal waves

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `start_x` | number | Yes | Starting X coordinate (absolute screen position) |
| `start_y` | number | Yes | Starting Y coordinate (absolute screen position) |
| `end_x` | number | Yes | Ending X coordinate (absolute screen position) |
| `end_y` | number | Yes | Ending Y coordinate (absolute screen position) |
| `amplitude` | number | Yes | Height of wave peaks perpendicular to direction |
| `cycles` | number | Yes | Number of complete wave cycles |

### path_params

```json
"path_params": {
  "type": "sine_wave",
  "start_x": 280,
  "start_y": 840,
  "end_x": 880,
  "end_y": 840,
  "amplitude": 12,
  "cycles": 6
}
```

### Direction Examples

Wave going **right** (horizontal):
```json
{ "start_x": 100, "start_y": 500, "end_x": 500, "end_y": 500, "amplitude": 20, "cycles": 4 }
```

Wave going **down** (vertical):
```json
{ "start_x": 500, "start_y": 100, "end_x": 500, "end_y": 500, "amplitude": 20, "cycles": 4 }
```

Wave going **diagonal**:
```json
{ "start_x": 100, "start_y": 100, "end_x": 500, "end_y": 500, "amplitude": 20, "cycles": 4 }
```

## Spiral Path

Spiral pattern that can expand outward or collapse inward.

### Use Cases
- Tornado
- Galaxy
- Swirls
- Draining effect (inward)
- Expanding energy (outward)

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `center_x` | number | Yes | Center X coordinate (absolute screen position) |
| `center_y` | number | Yes | Center Y coordinate (absolute screen position) |
| `max_radius` | number | Yes | Maximum radius at outermost point |
| `revolutions` | number | Yes | Number of complete rotations |
| `points` | number | No | Number of points for smoothness (default 100) |
| `inward` | boolean | No | false (default) = center to edge, true = edge to center |

### path_params

```json
"path_params": {
  "type": "spiral",
  "center_x": 400,
  "center_y": 300,
  "max_radius": 150,
  "revolutions": 3,
  "points": 100
}
```

## Spline Path

Smooth curve that passes through multiple control points.

### Use Cases
- River flowing through landscape
- Organic curves
- Multi-point smooth paths
- Natural flowing motion

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `points` | array | Yes | Array of [x, y] coordinate pairs (absolute screen positions) to pass through |
| `tension` | number | No | Controls curve tightness, 0-1 (default 0.3) |

### path_params

```json
"path_params": {
  "type": "spline",
  "points": [[100,300], [200,100], [300,350], [400,150], [500,300], [600,100], [700,250]],
  "tension": 0.3
}
```

## Zigzag Path

Sharp angular back-and-forth pattern from start to end point.

### Use Cases
- Lightning
- Sharp turns
- Jagged paths
- Electrical signals

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `start_x` | number | Yes | Starting X coordinate (absolute screen position) |
| `start_y` | number | Yes | Starting Y coordinate (absolute screen position) |
| `end_x` | number | Yes | Ending X coordinate (absolute screen position) |
| `end_y` | number | Yes | Ending Y coordinate (absolute screen position) |
| `amplitude` | number | Yes | Width of zigzag perpendicular to direction |
| `segments` | number | Yes | Number of zigzag segments |

### path_params

```json
"path_params": {
  "type": "zigzag",
  "start_x": 100,
  "start_y": 300,
  "end_x": 500,
  "end_y": 300,
  "amplitude": 80,
  "segments": 8
}
```

### Direction Examples

Zigzag going **right** (horizontal):
```json
{ "start_x": 100, "start_y": 500, "end_x": 500, "end_y": 500, "amplitude": 40, "segments": 6 }
```

Zigzag going **down** (vertical lightning bolt):
```json
{ "start_x": 500, "start_y": 100, "end_x": 500, "end_y": 600, "amplitude": 50, "segments": 8 }
```
