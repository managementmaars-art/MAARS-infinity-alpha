## Path Creation Guidelines

To design a path you need to use the following schemas so that a path is precisely created.

To use path an element should set "type" of the element as "path".

### **Path Types**

Read the Path Types [path-references.md](./path-references.md)

### **Coordinate System**

- Origin (0,0) at top-left corner of the viewport
- X increases right, Y increases down
- **All path coordinates use ABSOLUTE screen positions**
- No position/size fields needed for path elements

**Example - Line from center to top:**
- Viewport: 1080×1920 (portrait)
- Center: (540, 960)
- Top center: (540, 0)

```json
{
  "path_params": {
    "type": "linear",
    "start_x": 540,
    "start_y": 960,
    "end_x": 540,
    "end_y": 0
  }
}
```

---

## Arrow Marker

  Arrow markers place an arrowhead at the end of a path. Three visual styles are available: `hollow` (outlined arrowhead), `fill` (filled arrowhead), and `line` (simple line arrow).

### Arrow Marker Schema Example

```json
{
 "path_params":
    {
      "type": "linear",
      "start_x": 100,
      "start_y": 500,
      "end_x": 300,
      "end_y": 500
    },
 "arrow_marker": "hollow|fill|line", //(optional field)
}
```

## Path Animation Types

### Entrance Animations

| Animation | Description |
|-----------|-------------|
| `path-draw` | Progressively draws the path from start to end over the specified duration


### Exit Animations
| Animation | Description |
|-----------|-------------|
| `path-erase` | Progressively erases the path from start to end |

### Path-Draw Animation

The `path-draw` animation is specifically designed for path elements. It draws the path progressively over the specified duration, creating a "drawing" effect.

This will draw the path over 1000ms (1 second), starting from the path's origin and following its defined trajectory.

### Object Path Following (`follow-path` Action)

When an object should travel along a visible path, use the `follow-path` action type. Do NOT use separate x/y property animations - they create straight-line movement.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `type` | Yes | `"follow-path"` |
| `pathId` | Yes | ID of the path element to follow |
| `autoRotate` | No | Rotate to face direction of travel (default: true) |
| `easing` | No | Animation easing (default: "linear") |

**Important:**
- Object's initial `x`, `y` should match path's start coordinates
- Set `follow-path` duration equal to `path-draw` duration to sync movement with path drawing
- Set `path-draw` easing to match `follow-path` easing (e.g., both use `"easeInOut"` or both use `"linear"`)

**Example: Object following a simple path**
```json
// Path element
{
  "id": "example_path",
  "type": "path",
  "enterOn": 1000,
  "exitOn": 5000,
  "stroke": "#FFFFFF",
  "strokeWidth": 3,
  "fill": "none",
  "path_params": {
    "type": "parabolic",
    "start_x": 200,
    "start_y": 400,
    "end_x": 800,
    "end_y": 400,
    "arc_height": 300
  },
  "animation": {
    "entrance": {
      "type": "path-draw",
      "duration": 2000,
      "easing": "easeInOut"
    }
  }
}

// Object following the path (easing must match path-draw)
{
  "id": "moving_object",
  "type": "asset",
  "x": 200,
  "y": 400,
  "width": 50,
  "height": 50,
  "enterOn": 1000,
  "exitOn": 5000,
  "animation": {
    "actions": [
      {
        "type": "follow-path",
        "pathId": "example_path",
        "autoRotate": true,
        "on": 1000,
        "duration": 2000,
        "easing": "easeInOut"
      }
    ]
  }
}
```

### Using `follow-path` with Composite Paths

When a path uses `merge_path_params` to combine multiple segments, objects can follow the entire composite path using `follow-path`. The object will traverse all segments in sequence.

**Example: Object following a multi-segment path**
```json
// Composite path with multiple segments
{
  "id": "composite_path",
  "type": "path",
  "enterOn": 0,
  "exitOn": 5000,
  "stroke": "#00FF00",
  "strokeWidth": 4,
  "fill": "none",
  "merge_path_params": [
    { "type": "linear", "start_x": 100, "start_y": 200, "end_x": 100, "end_y": 400 },
    { "type": "arc", "start_x": 100, "start_y": 400, "end_x": 300, "end_y": 400, "radius": 100, "sweep": 1, "large_arc": 0 },
    { "type": "linear", "start_x": 300, "start_y": 400, "end_x": 500, "end_y": 200 }
  ],
  "animation": {
    "entrance": {
      "type": "path-draw",
      "duration": 3000,
      "easing": "linear"
    }
  }
}

// Object follows the entire composite path (easing must match path-draw)
{
  "id": "moving_object",
  "type": "asset",
  "x": 100,
  "y": 200,
  "width": 60,
  "height": 60,
  "enterOn": 0,
  "exitOn": 5000,
  "animation": {
    "actions": [
      {
        "type": "follow-path",
        "pathId": "composite_path",
        "autoRotate": true,
        "on": 1000,
        "duration": 3000,
        "easing": "linear"
      }
    ]
  }
}
```

**Important:** The object will follow ALL segments of a composite path. If only part of the trajectory should use `follow-path`, split into separate paths or adjust timing.

## Composite Paths (Multiple Path Segments)

To create a single path element that comprises multiple connected path segments, use `merge_path_params` instead of `path_params`. The `merge_path_params` is an **array** of path configurations where each segment defines its own path type and parameters. They are drawn sequentially to form one continuous composite path. The start of the second path will be from teh end of the previous path.

### Composite/Merged Path Schema

```json
{
  "id": "unique_id",
  "type": "path",
  "content": "Description of what this composite path represents",
  "enterOn": number,
  "exitOn": number,
  "x": number,
  "y": number,
  "width": number,
  "height": number,
  "stroke": "#HEXCOLOR",
  "strokeWidth": number,
  "fill": "none|#HEXCOLOR",
  "opacity": number,
  "zIndex": number,

  // IMPORTANT: All timing values (enterOn, exitOn, action.on) must use absolute video timestamps
  // matching scene.startTime, not relative scene time. If syncing to audio at relative time T,
  // use: scene.startTime + T

  "merge_path_params": [
    {
      "type": "linear",
      "start_x": number,
      "start_y": number,
      "end_x": number,
      "end_y": number
    },
    {
      "type": "arc",
      "start_x": number,
      "start_y": number,
      "end_x": number,
      "end_y": number,
      "radius": number,
      "sweep": number,
      "large_arc": number
    },
    {
      "type": "linear",
      "start_x": number,
      "start_y": number,
      "end_x": number,
      "end_y": number
    }
  ],

  "animation": {
    "entrance": {
      "type": "path-draw|fade-in|pop-in|etc",
      "duration": number
    }
  }
}
```

### Key Points for Composite Paths

1. **Use `merge_path_params`**: Use this instead of `path_params` when you need to combine multiple path segments
2. **Array Format**: `merge_path_params` is always an array where each element defines a separate path segment
3. **Sequential Connection**: Segments are drawn in order; ensure the `end` of one segment matches the `start` of the next for smooth connections
4. **Mixed Types**: You can combine any path types (linear, arc, bezier, parabolic, etc.) within a single composite path
5. **Single Animation**: The entire composite path shares one animation configuration - `path-draw` will draw all segments sequentially
6. **Unified Styling**: All segments inherit the same stroke, fill, and style properties from the parent element

---

## Path Element Schema

When creating a path element, use `type: "path"` and include `path_params` to define the path geometry.

```json
{
  "id": "unique_path_id",
  "type": "path",
  "content": "Description of the path - e.g., 'a parabolic path to show a trajectory of a missile'",
  "enterOn": number,
  "exitOn": number,
  "x": number,
  "y": number,
  "width": number,
  "height": number,
  "stroke": "#HEXCOLOR",
  "strokeWidth": number,
  "fill": "none|#HEXCOLOR",
  "opacity": number,
  "zIndex": number,

  // IMPORTANT: All timing values (enterOn, exitOn, action.on) must use absolute video timestamps
  // matching scene.startTime, not relative scene time. If syncing to audio at relative time T,
  // use: scene.startTime + T

  "path_params": {
    "type": "linear|arc|bezier|bounce|circular|elliptical|parabolic|s_curve|sine_wave|spiral|spline|zigzag",
    // ... type-specific parameters (see individual path reference files)
    // All coordinates are ABSOLUTE screen positions
  },

  "animation": {
    "entrance": {
      "type": "path-draw|fade-in|pop-in|etc",
      "duration": number
    },
    "exit": {
      "type": "path-erase|fade-out|pop-out|etc",
      "duration": number
    },
    "actions": []
  }
}
```

## Path Instances

Paths support the `instances` pattern for creating multiple similar paths with variations.

### Example: Multiple paths with variations

```json
{
  "id": "arrow_path",
  "type": "path",
  "enterOn": 1000,
  "exitOn": 5000,
  "x": 0,
  "y": 0,
  "stroke": "#FFFFFF",
  "strokeWidth": 3,
  "path_params": {
    "type": "linear",
    "start_x": 100,
    "start_y": 200,
    "end_x": 300,
    "end_y": 200,
    "instances": [
      { "useDefaults": true },
      { "start_y": 400, "end_y": 400 },
      { "start_y": 600, "end_y": 600 }
    ]
  },
  "arrow_marker": "fill"
}
```

Creates 3 horizontal arrows at different y positions (200, 400, 600). First instance uses base values, others override y coordinates.

---

## Static Path-Aligned Elements

For elements positioned along a path but not moving (like directional arrows), use `pathPositions` instead of manual x/y/rotation coordinates.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `pathId` | Yes | ID of the path element to align to |
| `progress` | Yes | Array of progress values 0-1 along path (0=start, 1=end) |
| `orientation` | Yes | Element's natural direction in degrees (0=up, 90=right, 180=down, 270=left) |

**Important:**
- Use progress values instead of hardcoded coordinates to ensure alignment
- Coder will use `getPathPoint` to calculate actual positions from the path

**Example: Arrows along a trajectory path**
```json
// Path element
{
  "id": "trajectory_path",
  "type": "path",
  "stroke": "#FF0000",
  "strokeWidth": 4,
  "fill": "none",
  "merge_path_params": [{
    "type": "spline",
    "points": [[680, 920], [750, 750], [820, 520]],
    "tension": 0.4
  }]
}

// Arrows positioned along the path
{
  "id": "trajectory_arrows",
  "type": "shape",
  "fill": "#FF0000",
  "pathPositions": {
    "pathId": "trajectory_path",
    "progress": [0.1, 0.3, 0.5, 0.7, 0.9],
    "orientation": 90
  }
}
```
