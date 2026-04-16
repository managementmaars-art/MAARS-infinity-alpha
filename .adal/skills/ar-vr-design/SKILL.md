---
name: ar-vr-design
cluster: ar-vr
description: "Designs interactive AR/VR experiences using 3D modeling, spatial computing, and user interface optimization."
tags: ["ar-vr","design","3d-modeling"]
dependencies: []
composes: []
similar_to: []
called_by: []
authorization_required: false
scope: general
model_hint: claude-sonnet
embedding_hint: "ar vr design 3d modeling spatial computing"
---

# ar-vr-design

## Purpose
This skill designs interactive AR/VR experiences by integrating 3D modeling, spatial computing, and UI optimization, enabling creation of immersive environments for applications like virtual training or augmented overlays.

## When to Use
Use this skill for projects requiring 3D asset manipulation, spatial interactions, or VR-specific UI tweaks, such as developing a virtual museum tour or AR product visualization in e-commerce apps.

## Key Capabilities
- Import and export 3D models in formats like GLTF or OBJ using built-in parsers.
- Perform spatial computing tasks, such as room-scale mapping with algorithms for occlusion and collision detection.
- Optimize UI for AR/VR devices, including rendering adjustments for headsets like Oculus or HoloLens to reduce latency below 20ms.
- Simulate user interactions in a virtual environment to test gesture controls or haptic feedback.

## Usage Patterns
To accomplish tasks, follow these steps: First, initialize a project with required configs; then, build and manipulate 3D assets; next, apply spatial computing for interactions; finally, optimize and simulate. Always set environment variables for authentication, e.g., export SERVICE_API_KEY=your_key before running commands. For integration, wrap skill outputs in a main application loop.

## Common Commands/API
Use the `arvr-cli` tool for core operations. Authenticate via $ARVR_API_KEY environment variable.

- Command: `arvr-cli init --project myvrapp --type vr`
  - Initializes a new VR project; add `--ar` flag for AR mode.
  - Example snippet:
    ```
    export ARVR_API_KEY=abc123
    arvr-cli init --project myvrapp
    ```

- API Endpoint: POST /api/vr/models
  - Uploads a 3D model; requires JSON payload with { "model": "path/to/model.gltf", "scale": 1.5 }.
  - Example snippet:
    ```
    curl -H "Authorization: Bearer $ARVR_API_KEY" -X POST -d '{"model": "asset.gltf"}' https://api.openclaw.com/api/vr/models
    ```

- Command: `arvr-cli optimize --input model.obj --device oculus`
  - Optimizes model for specific devices; outputs optimized file.
  - Example snippet:
    ```
    arvr-cli optimize --input scene.glb --device hololens
    ```

- API Endpoint: GET /api/ar/spatial-map
  - Retrieves spatial data; query with parameters like ?roomSize=10x10.
  - Example snippet:
    ```
    curl -H "Authorization: Bearer $ARVR_API_KEY" https://api.openclaw.com/api/ar/spatial-map?roomSize=5x5
    ```

Config formats: Use JSON for project configs, e.g., { "assets": ["model1.obj"], "spatialSettings": { "gravity": 9.8 } }.

## Integration Notes
Integrate this skill into workflows by importing outputs into engines like Unity or Unreal. For example, after running `arvr-cli init`, copy generated files to a Unity project and reference them in scripts. Use $ARVR_API_KEY for API calls in custom code. To chain with other skills, pipe outputs via stdin/stdout, e.g., output from a 3D modeling skill into this one's input. Ensure compatibility by matching formats: always convert models to GLTF before integration.

## Error Handling
Handle errors by checking exit codes from commands; for API calls, parse HTTP responses. Common issues:
- Authentication failure: If $ARVR_API_KEY is invalid, commands return code 401—fix by verifying and exporting the correct key.
- Invalid model format: Use `arvr-cli validate --file model.obj`; if it fails with code 400, convert the file using a tool like Blender.
- Example snippet for error checking:
  ```
  response=$(curl ...); if [ $? -ne 0 ]; then echo "API error: $response"; fi
  ```
Always wrap API calls in try-catch blocks in scripts, e.g., in Python: try: requests.post(url) except Exception as e: log_error(e).

## Concrete Usage Examples
1. Design a simple AR overlay for a mobile app: First, run `arvr-cli init --project ar-overlay --type ar`. Then, upload a 3D model with `curl -X POST -d '{"model": "overlay.glb"}' https://api.openclaw.com/api/vr/models`. Optimize for mobile: `arvr-cli optimize --input overlay.glb --device android`. Finally, integrate the output into an Android app using Unity's AR Foundation.
   
2. Create a VR simulation for training: Initialize with `arvr-cli init --project vr-training --type vr`. Add spatial mapping: `curl https://api.openclaw.com/api/ar/spatial-map?roomSize=10x10`. Build interactions: Use the API to simulate gestures, then test with `arvr-cli simulate --project vr-training`. Export and import into Unreal Engine for full deployment.

## Graph Relationships
- Related to cluster: ar-vr (e.g., shares tags with skills like ar-vr-development).
- Connected via tags: ["ar-vr"] links to other AR/VR skills; ["design"] connects to ui-design and 3d-modeling skills.
- Dependencies: Requires outputs from 3d-modeling skills as inputs.
