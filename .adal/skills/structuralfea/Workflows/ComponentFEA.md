# ComponentFEA Workflow

Full FEA analysis of a damper component using the open source toolchain.

## Trigger

"FEA analysis", "run FEA", "structural analysis"

## Prerequisites

- FreeCAD with FEM workbench installed
- Gmsh mesher installed
- CalculiX (ccx) solver installed
- ParaView for post-processing

## Process

### 1. Geometry Preparation

**Option A: Import STEP**
```
User provides: .step file from CAD

Check:
□ Watertight solid (no gaps)
□ No small features < mesh size
□ Units confirmed (mm)
```

**Option B: Create in FreeCAD**
```
Guide user through Part Design workbench
- Sketch base profile
- Revolve/Pad to solid
- Add features (grooves, holes, threads)
```

### 2. Define Analysis Setup

Gather from user:
- Material selection (from database)
- Fixed boundary (which face?)
- Load application (force, pressure, or displacement)
- Load magnitude and direction
- Analysis type (static, buckling, modal)

### 3. Generate Mesh

Provide Gmsh script or FreeCAD instructions:

```geo
// Template for component
SetFactory("OpenCASCADE");
Merge "[GEOMETRY_FILE]";

Mesh.CharacteristicLengthMax = [MESH_SIZE];
Mesh.CharacteristicLengthMin = [MESH_SIZE]/4;
Mesh.ElementOrder = 2;

// Refinement at stress concentrations
Field[1] = Distance;
Field[1].FacesList = {[CRITICAL_FACES]};
Field[1].Sampling = 100;

Field[2] = Threshold;
Field[2].InField = 1;
Field[2].SizeMin = [FINE_SIZE];
Field[2].SizeMax = [MESH_SIZE];
Field[2].DistMin = 1;
Field[2].DistMax = 10;

Background Field = 2;

Mesh 3;
Save "[OUTPUT].inp";
```

Mesh size recommendations:
| Component | Global (mm) | Refined (mm) |
|-----------|-------------|--------------|
| Rod Ø16-20 | 2.0 | 0.5 |
| Rod Ø20-30 | 3.0 | 0.8 |
| Tube Ø40-50 | 3.0 | 0.5 |
| Tube Ø50-70 | 4.0 | 0.8 |

### 4. Generate CalculiX Input

Provide complete .inp file:

```
*HEADING
[Component description]

*INCLUDE, INPUT=[mesh_file].inp

*MATERIAL, NAME=[MATERIAL]
*ELASTIC
[E], [nu]
*DENSITY
[rho]

*SOLID SECTION, ELSET=EALL, MATERIAL=[MATERIAL]

*BOUNDARY
[FIXED_NSET], 1, 3, 0.0

*STEP
*STATIC

*CLOAD
[LOAD_NSET], [DOF], [MAGNITUDE]

*NODE FILE
U, RF
*EL FILE
S, E

*END STEP
```

### 5. Run Solver

```bash
ccx -i [job_name]
```

Expected output files:
- `.dat` - Text results
- `.frd` - Binary results for visualization

### 6. Post-Process Results

**ParaView workflow:**
1. Open `.frd` file with CalculiX FRD reader
2. Apply "Warp by Vector" (displacement)
3. Color by von Mises stress
4. Add contour legend
5. Check max values

**Key checks:**
- Max von Mises vs allowable
- Displacement magnitude reasonable
- Stress concentration locations
- Reaction force balance

### 7. Report Results

```markdown
## FEA Analysis Report

### Component
- Name: [name]
- Material: [material]
- Mesh: [nodes] nodes, [elements] elements

### Loading
- Boundary: [fixed face description]
- Load: [magnitude] N applied to [face]

### Results
- Max Displacement: [value] mm at [location]
- Max von Mises Stress: [value] MPa at [location]
- Allowable Stress: [value] MPa (Sy/SF)
- Safety Factor: [calculated]

### Assessment
[PASS/FAIL] - [comments]

### Recommendations
- [any design changes suggested]
```

## Example Output

```
=== FEA COMPLETE ===

Component: Piston Rod M20×200
Mesh: 45,231 nodes, 28,456 C3D10 elements

Results:
  Max displacement: 0.024 mm (at loaded end)
  Max stress: 48.2 MPa (at thread root)
  Reaction force: 5000 N (matches applied load ✓)

Assessment:
  Material: 4140 Steel (Sy = 700 MPa)
  Allowable (SF=2): 350 MPa
  Actual SF: 14.5

  ✓ PASS - Design is adequate with large margin

  Stress concentration at thread root is expected.
  Consider thread relief groove if fatigue is concern.

Files generated:
  - rod_analysis.inp
  - rod_analysis.dat
  - rod_analysis.frd (open in ParaView)
```
