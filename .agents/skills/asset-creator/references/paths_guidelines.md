# Complete Path Guidelines

<arc-path>
**Use Case:** Single arc segment

<arc-required-parameters>
Required Parameters:

| Parameter | Description |
|-----------|-------------|
| `start_x` | Starting X coordinate |
| `start_y` | Starting Y coordinate |
| `end_x` | Ending X coordinate |
| `end_y` | Ending Y coordinate |
| `radius` | Radius of the arc |

</arc-required-parameters>

<arc-optional-parameters>
Optional Parameters:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `sweep` | Direction (0 = counter-clockwise, 1 = clockwise) | 1 |
| `large_arc` | Use larger arc (0 = smaller, 1 = larger) | 0 |

</arc-optional-parameters>

<arc-example>
**Example - Door swinging open:**
```bash
python ".claude/skills/asset-creator/scripts/svg-path.py" arc --params '{"start_x": 100, "start_y": 300, "end_x": 400, "end_y": 300, "radius": 200, "sweep": 1, "large_arc": 0}'
```

</arc-example>

</arc-path>

<linear-path>
**Use Case:** Straight line A→B

<linear-required-parameters>
Required Parameters:

| Parameter | Description |
|-----------|-------------|
| `start_x` | Starting X coordinate |
| `start_y` | Starting Y coordinate |
| `end_x` | Ending X coordinate |
| `end_y` | Ending Y coordinate |

</linear-required-parameters>

<linear-example>
**Example - Laser beam:**
```bash
python ".claude/skills/asset-creator/scripts/svg-path.py" linear --params '{"start_x": 100, "start_y": 100, "end_x": 700, "end_y": 400}'
```

</linear-example>

</linear-path>

<circular-path>
**Use Case:** Orbits, spinning

<circular-required-parameters>
Required Parameters:

| Parameter | Description |
|-----------|-------------|
| `center_x` | Center X coordinate |
| `center_y` | Center Y coordinate |
| `radius` | Radius of the circle |

</circular-required-parameters>

<circular-example>
**Example - Planet orbiting sun:**
```bash
python ".claude/skills/asset-creator/scripts/svg-path.py" circular --params '{"center_x": 400, "center_y": 300, "radius": 150}'
```

</circular-example>

</circular-path>

<zigzag-path>
**Use Case:** Sharp angular back-and-forth (lightning, electrical signals)

<zigzag-required-parameters>
Required Parameters:

| Parameter | Description |
|-----------|-------------|
| `start_x` | Starting X coordinate |
| `start_y` | Starting Y coordinate |
| `end_x` | Ending X coordinate |
| `end_y` | Ending Y coordinate |
| `amplitude` | Width of zigzag (perpendicular to direction) |
| `segments` | Number of zigzag segments |

</zigzag-required-parameters>

<zigzag-example>
**Example - Lightning bolt going down:**
```bash
python ".claude/skills/asset-creator/scripts/svg-path.py" zigzag --params '{"start_x": 400, "start_y": 100, "end_x": 400, "end_y": 500, "amplitude": 80, "segments": 8}'
```

</zigzag-example>

</zigzag-path>

<elliptical-path>
**Use Case:** Oval orbits

<elliptical-required-parameters>
Required Parameters:

| Parameter | Description |
|-----------|-------------|
| `center_x` | Center X coordinate |
| `center_y` | Center Y coordinate |
| `radius_x` | Horizontal radius |
| `radius_y` | Vertical radius |

</elliptical-required-parameters>

<elliptical-example>
**Example - Comet orbit:**
```bash
python ".claude/skills/asset-creator/scripts/svg-path.py" elliptical --params '{"center_x": 400, "center_y": 300, "radius_x": 200, "radius_y": 100}'
```

</elliptical-example>

</elliptical-path>

<parabolic-path>
**Use Case:** Projectiles, jumps, throws

<parabolic-required-parameters>
Required Parameters:

| Parameter | Description |
|-----------|-------------|
| `start_x` | Starting X coordinate |
| `start_y` | Starting Y coordinate |
| `end_x` | Ending X coordinate |
| `end_y` | Ending Y coordinate |
| `arc_height` | Height of the arc (positive = up, negative = down) |

</parabolic-required-parameters>

<parabolic-example>
**Example - Ball thrown in arc:**
```bash
python ".claude/skills/asset-creator/scripts/svg-path.py" parabolic --params '{"start_x": 100, "start_y": 400, "end_x": 700, "end_y": 400, "arc_height": 200}'
```

**Output:**
```
M 100 400 Q 400.0 200.0 700 400
```

</parabolic-example>

</parabolic-path>

<bezier-path>
**Use Case:** Custom cubic bezier

<bezier-required-parameters>
Required Parameters:

| Parameter | Description |
|-----------|-------------|
| `start_x` | Starting X coordinate |
| `start_y` | Starting Y coordinate |
| `cp1_x` | First control point X |
| `cp1_y` | First control point Y |
| `cp2_x` | Second control point X |
| `cp2_y` | Second control point Y |
| `end_x` | Ending X coordinate |
| `end_y` | Ending Y coordinate |

</bezier-required-parameters>

<bezier-example>
**Example - Custom curve with control points:**
```bash
python ".claude/skills/asset-creator/scripts/svg-path.py" bezier --params '{"start_x": 100, "start_y": 400, "cp1_x": 200, "cp1_y": 100, "cp2_x": 600, "cp2_y": 100, "end_x": 700, "end_y": 400}'
```

</bezier-example>

</bezier-path>

<bounce-path>
**Use Case:** Bouncing ball trajectory

<bounce-required-parameters>
Required Parameters:

| Parameter | Description |
|-----------|-------------|
| `start_x` | Starting X coordinate |
| `start_y` | Starting Y coordinate |
| `end_x` | Ending X coordinate |
| `ground_y` | Y coordinate of the ground |
| `initial_height` | Height of first bounce |
| `bounces` | Number of bounces |

</bounce-required-parameters>

<bounce-optional-parameters>
Optional Parameters:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `decay` | Height reduction per bounce (0-1) | 0.6 |

</bounce-optional-parameters>

<bounce-example>
**Example - Ball bouncing across screen:**
```bash
python ".claude/skills/asset-creator/scripts/svg-path.py" bounce --params '{"start_x": 100, "start_y": 100, "end_x": 700, "ground_y": 400, "initial_height": 250, "bounces": 4, "decay": 0.6}'
```

</bounce-example>

</bounce-path>

<s-curve-path>
**Use Case:** Smooth transitions

<s-curve-required-parameters>
Required Parameters:

| Parameter | Description |
|-----------|-------------|
| `start_x` | Starting X coordinate |
| `start_y` | Starting Y coordinate |
| `end_x` | Ending X coordinate |
| `end_y` | Ending Y coordinate |

</s-curve-required-parameters>

<s-curve-optional-parameters>
Optional Parameters:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `curvature` | Amount of curve (0-1) | 0.5 |

</s-curve-optional-parameters>

<s-curve-example>
**Example - Road winding through hills:**
```bash
python ".claude/skills/asset-creator/scripts/svg-path.py" s_curve --params '{"start_x": 100, "start_y": 200, "end_x": 700, "end_y": 500, "curvature": 0.4}'
```

</s-curve-example>

</s-curve-path>

<sine-wave-path>
**Use Case:** Waves, snake movement, heat radiation, signals

<sine-wave-required-parameters>
Required Parameters:

| Parameter | Description |
|-----------|-------------|
| `start_x` | Starting X coordinate |
| `start_y` | Starting Y coordinate |
| `end_x` | Ending X coordinate |
| `end_y` | Ending Y coordinate |
| `amplitude` | Height of the wave (perpendicular to direction) |
| `cycles` | Number of wave cycles |

</sine-wave-required-parameters>

<sine-wave-example>
**Example - Snake slithering right:**
```bash
python ".claude/skills/asset-creator/scripts/svg-path.py" sine_wave --params '{"start_x": 50, "start_y": 300, "end_x": 650, "end_y": 300, "amplitude": 60, "cycles": 6}'
```

**Example - Wave going down (vertical):**
```bash
python ".claude/skills/asset-creator/scripts/svg-path.py" sine_wave --params '{"start_x": 300, "start_y": 50, "end_x": 300, "end_y": 550, "amplitude": 40, "cycles": 5}'
```

</sine-wave-example>

</sine-wave-path>

<spiral-path>
**Use Case:** Tornado, galaxy, swirls

<spiral-required-parameters>
Required Parameters:

| Parameter | Description |
|-----------|-------------|
| `center_x` | Center X coordinate |
| `center_y` | Center Y coordinate |
| `max_radius` | Maximum radius of the spiral |
| `revolutions` | Number of spiral turns |

</spiral-required-parameters>

<spiral-optional-parameters>
Optional Parameters:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `points` | Number of points for smoothness | auto |

</spiral-optional-parameters>

<spiral-example>
**Example - Water draining:**
```bash
python ".claude/skills/asset-creator/scripts/svg-path.py" spiral --params '{"center_x": 400, "center_y": 300, "max_radius": 150, "revolutions": 3}'
```

</spiral-example>

</spiral-path>

<spline-path>
**Use Case:** Smooth curve through N points

<spline-required-parameters>
Required Parameters:

| Parameter | Description |
|-----------|-------------|
| `points` | Array of [x,y] coordinates |

</spline-required-parameters>

<spline-optional-parameters>
Optional Parameters:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `tension` | Curve smoothness (0-1) | 0.3 |

</spline-optional-parameters>

<spline-example>
**Example - River flowing through landscape:**
```bash
python ".claude/skills/asset-creator/scripts/svg-path.py" spline --params '{"points": [[100,300], [200,100], [300,350], [400,150], [500,300], [600,100], [700,250]], "tension": 0.3}'
```

</spline-example>

</spline-path>
