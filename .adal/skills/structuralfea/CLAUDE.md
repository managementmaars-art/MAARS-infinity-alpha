# StructuralFEA - Extended Technical Content

Deep technical guidance for open source FEA workflows, scripting, automation, and advanced analysis techniques.

---

## Table of Contents

1. [Complete FreeCAD FEM Tutorial](#complete-freecad-fem-tutorial)
2. [CalculiX Input File Reference](#calculix-input-file-reference)
3. [Gmsh Scripting Guide](#gmsh-scripting-guide)
4. [Python Automation Scripts](#python-automation-scripts)
5. [Damper Component Analysis Library](#damper-component-analysis-library)
6. [Advanced Analysis Types](#advanced-analysis-types)
7. [Troubleshooting Guide](#troubleshooting-guide)

---

## Complete FreeCAD FEM Tutorial

### Step-by-Step: Piston Rod Analysis

**1. Create Geometry (Part Design Workbench)**

```python
# FreeCAD Python console script for rod geometry
import FreeCAD
import Part
import PartDesign

doc = FreeCAD.newDocument("PistonRod")

# Create body
body = doc.addObject("PartDesign::Body", "RodBody")

# Sketch for rod profile
sketch = body.newObject("Sketcher::SketchObject", "RodProfile")
sketch.Support = (doc.getObject("XY_Plane"), [""])
sketch.addGeometry(Part.Circle(FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 0, 1), 10))  # Ø20mm

# Pad to length
pad = body.newObject("PartDesign::Pad", "RodPad")
pad.Profile = sketch
pad.Length = 200  # 200mm length

doc.recompute()
```

**2. Switch to FEM Workbench**

```python
# Set up FEM analysis
import FemGui
import ObjectsFem

FreeCAD.setActiveDocument("PistonRod")

# Create analysis container
analysis = ObjectsFem.makeAnalysis(doc, "RodAnalysis")

# Add CalculiX solver
solver = ObjectsFem.makeSolverCalculixCcxTools(doc, "SolverCcx")
analysis.addObject(solver)
```

**3. Define Material**

```python
# Add material
material = ObjectsFem.makeMaterialSolid(doc, "Steel4140")
material.Material = {
    'Name': 'Steel 4140',
    'YoungsModulus': '205000 MPa',
    'PoissonRatio': '0.29',
    'Density': '7850 kg/m^3',
}
analysis.addObject(material)
```

**4. Apply Constraints**

```python
# Fixed constraint at one end
fixed = ObjectsFem.makeConstraintFixed(doc, "FixedEnd")
fixed.References = [(doc.RodBody, "Face1")]  # Bottom face
analysis.addObject(fixed)

# Force at other end
force = ObjectsFem.makeConstraintForce(doc, "AxialLoad")
force.References = [(doc.RodBody, "Face2")]  # Top face
force.Force = 5000  # Newtons
force.Direction = (doc.RodBody, ["Face2"])
force.Reversed = True  # Compression
analysis.addObject(force)
```

**5. Create Mesh**

```python
# FEM mesh from shape
mesh = ObjectsFem.makeMeshGmsh(doc, "RodMesh")
mesh.Part = doc.RodBody
mesh.CharacteristicLengthMax = 2.0  # mm
mesh.CharacteristicLengthMin = 0.5  # mm
mesh.ElementOrder = "2nd"  # Quadratic elements
analysis.addObject(mesh)

# Generate mesh
from femmesh import gmshtools
gmsh_mesh = gmshtools.GmshTools(mesh)
gmsh_mesh.create_mesh()
```

**6. Run Analysis**

```python
# Write input file and solve
from femtools import ccxtools

fea = ccxtools.FemToolsCcx(analysis, solver)
fea.purge_results()
fea.reset_all()
fea.run()
```

**7. View Results**

```python
# Results are automatically added to analysis
# In FreeCAD GUI: double-click result object
# Use Pipeline to filter (von Mises, displacement, etc.)
```

---

## CalculiX Input File Reference

### Complete Input File Structure

```
** ================================================
** CALCULIX INPUT FILE - COMPLETE TEMPLATE
** ================================================
** File: analysis.inp
** Date: [DATE]
** Description: [COMPONENT DESCRIPTION]
** ================================================

**----------------------------------------------
** HEADING
**----------------------------------------------
*HEADING
[Analysis description - appears in output]

**----------------------------------------------
** NODES
**----------------------------------------------
*NODE, NSET=ALLNODES
[node_id], [x], [y], [z]
** Or include from mesh file:
*INCLUDE, INPUT=mesh_nodes.inp

**----------------------------------------------
** ELEMENTS
**----------------------------------------------
*ELEMENT, TYPE=C3D10, ELSET=EALL
[elem_id], [n1], [n2], [n3], [n4], [n5], [n6], [n7], [n8], [n9], [n10]
** Or include from mesh file:
*INCLUDE, INPUT=mesh_elements.inp

**----------------------------------------------
** NODE SETS (for BCs)
**----------------------------------------------
*NSET, NSET=FIXED_NODES
[node_id_1], [node_id_2], ...
*NSET, NSET=LOAD_NODES
[node_id_1], [node_id_2], ...

**----------------------------------------------
** ELEMENT SETS
**----------------------------------------------
*ELSET, ELSET=BODY_ELEMENTS
[elem_id_1], [elem_id_2], ...

**----------------------------------------------
** SURFACE DEFINITIONS
**----------------------------------------------
*SURFACE, NAME=PRESSURE_SURFACE, TYPE=ELEMENT
[elem_id], S[face_number]
** Face numbers: S1-S4 for tets, S1-S6 for hex

**----------------------------------------------
** MATERIAL
**----------------------------------------------
*MATERIAL, NAME=STEEL4140
*ELASTIC
205000, 0.29
*DENSITY
7850E-12
*PLASTIC
** yield_stress, plastic_strain
655, 0.0
700, 0.02
750, 0.05
800, 0.10

**----------------------------------------------
** SECTION ASSIGNMENT
**----------------------------------------------
*SOLID SECTION, ELSET=EALL, MATERIAL=STEEL4140

**----------------------------------------------
** INITIAL CONDITIONS (optional)
**----------------------------------------------
*INITIAL CONDITIONS, TYPE=TEMPERATURE
ALLNODES, 20.0

**----------------------------------------------
** BOUNDARY CONDITIONS
**----------------------------------------------
** Format: node/nset, DOF_start, DOF_end, value
*BOUNDARY
FIXED_NODES, 1, 3, 0.0
** 1=X, 2=Y, 3=Z, 4=rotX, 5=rotY, 6=rotZ

**----------------------------------------------
** STEP DEFINITION
**----------------------------------------------
*STEP, NLGEOM=NO
** NLGEOM=YES for large displacement
*STATIC
** [initial_increment], [total_time], [min_inc], [max_inc]
0.1, 1.0, 0.01, 0.5

**----------------------------------------------
** LOADS
**----------------------------------------------
** Concentrated load
*CLOAD
LOAD_NODES, 3, -5000.0
** node/nset, DOF, magnitude

** Distributed load (pressure)
*DLOAD
PRESSURE_SURFACE, P, 20.0
** surface, load_type, magnitude

** Gravity
*DLOAD
EALL, GRAV, 9810, 0, 0, -1
** elset, GRAV, magnitude, direction_x, direction_y, direction_z

**----------------------------------------------
** OUTPUT REQUESTS
**----------------------------------------------
** Results to .frd file (for ParaView/CGX)
*NODE FILE
U, RF
** U=displacement, RF=reaction force

*EL FILE
S, E, PEEQ
** S=stress, E=strain, PEEQ=plastic strain

** Node print (to .dat file)
*NODE PRINT, NSET=LOAD_NODES
U, RF

** Element print
*EL PRINT, ELSET=EALL
S

*END STEP
```

### Element Types

| Element | Nodes | Description | Use Case |
|---------|-------|-------------|----------|
| C3D4 | 4 | Linear tetrahedron | Quick meshes, not recommended |
| C3D10 | 10 | Quadratic tetrahedron | General 3D, default choice |
| C3D8 | 8 | Linear hexahedron | Structured meshes |
| C3D20 | 20 | Quadratic hexahedron | High accuracy |
| C3D20R | 20 | Reduced integration hex | Best for bending |

### Load Types

```
** POINT LOADS
*CLOAD
node, 1, Fx    ** X-direction force
node, 2, Fy    ** Y-direction force
node, 3, Fz    ** Z-direction force

** PRESSURE (normal to surface)
*DLOAD
surface, P, pressure_value

** DISTRIBUTED LOAD (on edge/line)
*DLOAD
surface, P1, value_at_end_1
surface, P2, value_at_end_2

** CENTRIFUGAL LOAD
*DLOAD
elset, CENTRIF, omega^2, x0, y0, z0, ax, ay, az
** rotation about axis through (x0,y0,z0) in direction (ax,ay,az)

** THERMAL LOAD
*TEMPERATURE
nset, temperature_value
```

### Analysis Types

```
** STATIC (linear or nonlinear)
*STEP
*STATIC
[time_params]
*END STEP

** BUCKLING (eigenvalue)
*STEP
*BUCKLE
[num_eigenvalues], [accuracy]
*END STEP

** MODAL (frequency)
*STEP
*FREQUENCY
[num_modes], [lower_freq], [upper_freq]
*END STEP

** DYNAMIC (time integration)
*STEP
*DYNAMIC
[time_increment], [total_time]
*END STEP

** HEAT TRANSFER
*STEP
*HEAT TRANSFER, STEADY STATE
*END STEP
```

---

## Gmsh Scripting Guide

### Complete Meshing Script for Damper Rod

```geo
// ================================================
// GMSH SCRIPT: PISTON ROD MESHING
// ================================================
// Run: gmsh rod_mesh.geo -3 -o rod_mesh.inp
// ================================================

SetFactory("OpenCASCADE");

// ------------------------------------------------
// PARAMETERS
// ------------------------------------------------
rod_diameter = 20;    // mm
rod_length = 200;     // mm
thread_length = 15;   // mm
thread_pitch = 2.5;   // mm (M20x2.5)

// Mesh sizes
mesh_body = 2.0;      // mm - general body
mesh_thread = 0.5;    // mm - thread refinement
mesh_fillet = 0.3;    // mm - stress concentration

// ------------------------------------------------
// GEOMETRY
// ------------------------------------------------
// Main rod body
Cylinder(1) = {0, 0, 0, 0, 0, rod_length, rod_diameter/2, 2*Pi};

// Thread relief groove (simplified)
Cylinder(2) = {0, 0, rod_length - thread_length - 2,
               0, 0, 2, rod_diameter/2 - 0.5, 2*Pi};
BooleanDifference{ Volume{1}; Delete; }{ Volume{2}; Delete; }

// ------------------------------------------------
// PHYSICAL GROUPS (for boundary conditions)
// ------------------------------------------------
// Bottom face (fixed)
Physical Surface("FIXED_END") = {1};  // Identify by inspection

// Top face (load application)
Physical Surface("LOAD_END") = {2};

// Cylindrical surface
Physical Surface("ROD_SURFACE") = {3};

// All elements
Physical Volume("ROD_BODY") = {1};

// ------------------------------------------------
// MESH SIZE FIELDS
// ------------------------------------------------
// Field 1: Distance from thread area
Field[1] = Distance;
Field[1].FacesList = {2};  // Top face with threads
Field[1].Sampling = 100;

// Field 2: Threshold for mesh gradation
Field[2] = Threshold;
Field[2].InField = 1;
Field[2].SizeMin = mesh_thread;
Field[2].SizeMax = mesh_body;
Field[2].DistMin = 1;
Field[2].DistMax = 20;

// Field 3: Distance from groove (stress concentration)
Field[3] = Distance;
Field[3].FacesList = {4};  // Groove faces
Field[3].Sampling = 100;

// Field 4: Refinement at groove
Field[4] = Threshold;
Field[4].InField = 3;
Field[4].SizeMin = mesh_fillet;
Field[4].SizeMax = mesh_body;
Field[4].DistMin = 0.5;
Field[4].DistMax = 5;

// Field 5: Combine fields (take minimum)
Field[5] = Min;
Field[5].FieldsList = {2, 4};

Background Field = 5;

// ------------------------------------------------
// MESH OPTIONS
// ------------------------------------------------
Mesh.Algorithm = 6;           // Frontal-Delaunay
Mesh.Algorithm3D = 1;         // Delaunay
Mesh.ElementOrder = 2;        // Quadratic elements (C3D10)
Mesh.SecondOrderLinear = 0;   // True quadratic
Mesh.Optimize = 1;
Mesh.OptimizeNetgen = 1;
Mesh.HighOrderOptimize = 2;

// ------------------------------------------------
// GENERATE AND EXPORT
// ------------------------------------------------
Mesh 3;

// Save in CalculiX format
Save "rod_mesh.inp";

// Also save native format for review
Save "rod_mesh.msh";
```

### Mesh Quality Checking

```geo
// Add to end of script for quality metrics
Plugin(AnalyseMeshQuality).JacobianDeterminant = 1;
Plugin(AnalyseMeshQuality).Run;

// View mesh statistics
Print Sprintf("Mesh statistics:");
Print Sprintf("  Nodes: %g", Mesh.NbNodes);
Print Sprintf("  Elements: %g", Mesh.NbTetrahedra);
```

---

## Python Automation Scripts

### Complete FEA Automation Script

```python
#!/usr/bin/env python3
"""
structural_fea.py - Automated FEA workflow for damper components

Usage:
    python structural_fea.py --geometry rod.step --material steel4140 --load 5000

Requires:
    - FreeCAD (freecad module)
    - Gmsh (gmsh module)
    - CalculiX (ccx in PATH)
"""

import argparse
import subprocess
import json
from pathlib import Path

# Material database
MATERIALS = {
    'steel4140': {
        'E': 205000,      # MPa
        'nu': 0.29,
        'rho': 7.85e-9,   # tonne/mm³ (for mm units)
        'Sy': 655,        # MPa
    },
    'steel4340': {
        'E': 205000,
        'nu': 0.29,
        'rho': 7.85e-9,
        'Sy': 860,
    },
    'al6061t6': {
        'E': 68900,
        'nu': 0.33,
        'rho': 2.70e-9,
        'Sy': 276,
    },
    'al7075t6': {
        'E': 71700,
        'nu': 0.33,
        'rho': 2.81e-9,
        'Sy': 503,
    },
}


def generate_mesh(step_file: Path, output: Path, mesh_size: float = 2.0):
    """Generate mesh using Gmsh"""

    geo_script = f"""
SetFactory("OpenCASCADE");
Merge "{step_file}";

Mesh.CharacteristicLengthMax = {mesh_size};
Mesh.CharacteristicLengthMin = {mesh_size / 4};
Mesh.ElementOrder = 2;
Mesh.Algorithm3D = 1;

Mesh 3;
Save "{output}";
"""

    geo_file = output.with_suffix('.geo')
    geo_file.write_text(geo_script)

    subprocess.run(['gmsh', str(geo_file), '-3', '-format', 'inp',
                    '-o', str(output)], check=True)

    return output


def generate_calculix_input(mesh_file: Path, material: str,
                            load: float, fixed_face: int, load_face: int) -> Path:
    """Generate CalculiX input file"""

    mat = MATERIALS[material]

    inp_content = f"""** Auto-generated CalculiX input file
*HEADING
Structural analysis - {mesh_file.stem}

*INCLUDE, INPUT={mesh_file.name}

*MATERIAL, NAME={material.upper()}
*ELASTIC
{mat['E']}, {mat['nu']}
*DENSITY
{mat['rho']}

*SOLID SECTION, ELSET=EALL, MATERIAL={material.upper()}

*BOUNDARY
FIXED_END, 1, 3, 0.0

*STEP
*STATIC
0.1, 1.0

*CLOAD
LOAD_END, 3, {-load}

*NODE FILE
U, RF
*EL FILE
S, E

*END STEP
"""

    inp_file = mesh_file.with_suffix('.inp').with_stem(mesh_file.stem + '_analysis')
    inp_file.write_text(inp_content)

    return inp_file


def run_calculix(inp_file: Path) -> dict:
    """Run CalculiX solver"""

    job_name = inp_file.stem

    result = subprocess.run(
        ['ccx', '-i', job_name],
        cwd=inp_file.parent,
        capture_output=True,
        text=True
    )

    # Check for errors
    if 'ERROR' in result.stdout or result.returncode != 0:
        raise RuntimeError(f"CalculiX failed: {result.stdout}")

    # Parse results from .dat file
    dat_file = inp_file.with_suffix('.dat')
    results = parse_results(dat_file)

    return results


def parse_results(dat_file: Path) -> dict:
    """Parse CalculiX .dat output file"""

    results = {
        'max_displacement': 0.0,
        'max_stress': 0.0,
        'max_reaction': 0.0,
    }

    if dat_file.exists():
        content = dat_file.read_text()
        # Basic parsing - expand as needed
        # Look for displacement and stress values

    return results


def check_design(results: dict, material: str, safety_factor: float = 2.0) -> dict:
    """Check results against design allowables"""

    mat = MATERIALS[material]
    allowable = mat['Sy'] / safety_factor

    assessment = {
        'max_stress': results['max_stress'],
        'allowable': allowable,
        'safety_factor': allowable / results['max_stress'] if results['max_stress'] > 0 else float('inf'),
        'pass': results['max_stress'] < allowable,
    }

    return assessment


def main():
    parser = argparse.ArgumentParser(description='Run FEA on damper component')
    parser.add_argument('--geometry', type=Path, required=True, help='STEP file')
    parser.add_argument('--material', choices=MATERIALS.keys(), required=True)
    parser.add_argument('--load', type=float, required=True, help='Load in N')
    parser.add_argument('--mesh-size', type=float, default=2.0, help='Mesh size in mm')
    parser.add_argument('--sf', type=float, default=2.0, help='Required safety factor')

    args = parser.parse_args()

    print(f"=== Structural FEA Analysis ===")
    print(f"Geometry: {args.geometry}")
    print(f"Material: {args.material}")
    print(f"Load: {args.load} N")

    # Generate mesh
    print("\n[1/3] Generating mesh...")
    mesh_file = generate_mesh(args.geometry, args.geometry.with_suffix('.inp'), args.mesh_size)

    # Generate input
    print("[2/3] Setting up analysis...")
    inp_file = generate_calculix_input(mesh_file, args.material, args.load, 1, 2)

    # Run solver
    print("[3/3] Running CalculiX...")
    results = run_calculix(inp_file)

    # Check design
    assessment = check_design(results, args.material, args.sf)

    print("\n=== Results ===")
    print(f"Max stress: {assessment['max_stress']:.1f} MPa")
    print(f"Allowable:  {assessment['allowable']:.1f} MPa")
    print(f"Safety factor: {assessment['safety_factor']:.2f}")
    print(f"Status: {'PASS ✓' if assessment['pass'] else 'FAIL ✗'}")

    return 0 if assessment['pass'] else 1


if __name__ == '__main__':
    exit(main())
```

### Batch Analysis Script

```python
#!/usr/bin/env python3
"""
batch_fea.py - Run FEA on multiple load cases

Usage:
    python batch_fea.py config.json
"""

import json
from pathlib import Path
from structural_fea import generate_mesh, generate_calculix_input, run_calculix, check_design

def run_batch(config_file: Path):
    """Run batch analysis from config file"""

    config = json.loads(config_file.read_text())

    results = []

    for case in config['load_cases']:
        print(f"\n--- Running: {case['name']} ---")

        # Modify load
        inp_file = generate_calculix_input(
            Path(config['mesh_file']),
            config['material'],
            case['load'],
            config['fixed_face'],
            config['load_face']
        )

        # Solve
        result = run_calculix(inp_file)

        # Assess
        assessment = check_design(result, config['material'])
        assessment['case'] = case['name']

        results.append(assessment)

    # Summary table
    print("\n=== BATCH RESULTS ===")
    print(f"{'Case':<20} {'Stress':>10} {'SF':>8} {'Status':>8}")
    print("-" * 50)
    for r in results:
        status = 'PASS' if r['pass'] else 'FAIL'
        print(f"{r['case']:<20} {r['max_stress']:>10.1f} {r['safety_factor']:>8.2f} {status:>8}")

    return results

# Example config.json:
"""
{
    "mesh_file": "rod_mesh.inp",
    "material": "steel4140",
    "fixed_face": 1,
    "load_face": 2,
    "load_cases": [
        {"name": "Normal operation", "load": 3000},
        {"name": "Peak load", "load": 5000},
        {"name": "Overload (1.5x)", "load": 7500}
    ]
}
"""
```

---

## Damper Component Analysis Library

### Rod Analysis

```python
def analyze_piston_rod(diameter_mm: float, length_mm: float,
                       load_n: float, material: str = 'steel4140') -> dict:
    """
    Quick analytical check for piston rod

    Returns:
        dict with stress, buckling, and safety factors
    """
    import math

    mat = MATERIALS[material]

    # Cross-section
    area = math.pi * (diameter_mm/2)**2  # mm²
    I = math.pi * diameter_mm**4 / 64     # mm⁴

    # Axial stress
    sigma = load_n / area  # MPa

    # Buckling (Euler, K=0.7 for guided ends)
    K = 0.7
    P_critical = math.pi**2 * mat['E'] * I / (K * length_mm)**2  # N

    results = {
        'diameter': diameter_mm,
        'length': length_mm,
        'load': load_n,
        'material': material,
        'axial_stress': sigma,
        'buckling_load': P_critical,
        'sf_stress': mat['Sy'] / sigma,
        'sf_buckling': P_critical / load_n,
        'critical_mode': 'stress' if mat['Sy']/sigma < P_critical/load_n else 'buckling'
    }

    return results
```

### Tube Analysis

```python
def analyze_tube(od_mm: float, wall_mm: float, pressure_mpa: float,
                 material: str = 'al6061t6') -> dict:
    """
    Tube hoop stress analysis
    """
    mat = MATERIALS[material]

    id_mm = od_mm - 2*wall_mm
    r_inner = id_mm / 2

    # Thin wall approximation (valid if t < 0.1*r)
    sigma_hoop = pressure_mpa * r_inner / wall_mm

    # Thick wall (more accurate)
    r_outer = od_mm / 2
    sigma_hoop_thick = pressure_mpa * (r_inner**2 + r_outer**2) / (r_outer**2 - r_inner**2)

    results = {
        'od': od_mm,
        'id': id_mm,
        'wall': wall_mm,
        'pressure': pressure_mpa,
        'material': material,
        'hoop_stress_thin': sigma_hoop,
        'hoop_stress_thick': sigma_hoop_thick,
        'sf': mat['Sy'] / sigma_hoop_thick,
    }

    return results
```

### Eye/Clevis Analysis

```python
def analyze_eye(hole_dia_mm: float, eye_od_mm: float,
                thickness_mm: float, load_n: float,
                material: str = 'steel4140') -> dict:
    """
    Eye bearing and tearout analysis
    """
    mat = MATERIALS[material]

    # Bearing stress
    bearing_area = hole_dia_mm * thickness_mm
    sigma_bearing = load_n / bearing_area

    # Tearout (net section)
    edge_dist = (eye_od_mm - hole_dia_mm) / 2
    tearout_area = 2 * edge_dist * thickness_mm
    sigma_tearout = load_n / tearout_area

    # Allowables
    bearing_allow = 1.5 * mat['Sy']  # Bearing typically higher
    tearout_allow = mat['Sy']

    results = {
        'hole_dia': hole_dia_mm,
        'eye_od': eye_od_mm,
        'thickness': thickness_mm,
        'load': load_n,
        'bearing_stress': sigma_bearing,
        'tearout_stress': sigma_tearout,
        'sf_bearing': bearing_allow / sigma_bearing,
        'sf_tearout': tearout_allow / sigma_tearout,
        'critical_mode': 'bearing' if bearing_allow/sigma_bearing < tearout_allow/sigma_tearout else 'tearout'
    }

    return results
```

---

## Advanced Analysis Types

### Nonlinear Material (Plasticity)

```
** Add to material definition for nonlinear analysis
*MATERIAL, NAME=STEEL4140_PLASTIC
*ELASTIC
205000, 0.29
*PLASTIC
** yield_stress, plastic_strain
655, 0.000
700, 0.020
750, 0.050
800, 0.100
850, 0.200

** Enable geometric nonlinearity
*STEP, NLGEOM=YES
*STATIC
0.01, 1.0, 1e-6, 0.1
```

### Contact Analysis

```
** Define contact surfaces
*SURFACE, NAME=MASTER_SURF, TYPE=ELEMENT
[elements], S3

*SURFACE, NAME=SLAVE_SURF, TYPE=ELEMENT
[elements], S1

** Define contact pair
*CONTACT PAIR, INTERACTION=INT1, TYPE=SURFACE TO SURFACE
SLAVE_SURF, MASTER_SURF

*SURFACE INTERACTION, NAME=INT1
*FRICTION
0.15
```

### Thermal-Structural

```
** Combined thermal-structural analysis
*STEP
*COUPLED TEMPERATURE-DISPLACEMENT, STEADY STATE

** Thermal BCs
*BOUNDARY
HOT_SURFACE, 11, 11, 100.0   ** DOF 11 = temperature
COLD_SURFACE, 11, 11, 20.0

** Mechanical BCs
*BOUNDARY
FIXED, 1, 3, 0.0

*NODE FILE
U, NT
*EL FILE
S, HFL

*END STEP
```

---

## Troubleshooting Guide

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| "singular matrix" | Unconstrained body | Add sufficient BCs (6 DOF minimum) |
| "zero pivot" | Bad mesh or material | Check mesh quality, E > 0 |
| "negative jacobian" | Inverted elements | Remesh with better quality |
| "no convergence" | Nonlinear divergence | Reduce load increment, check BCs |
| "insufficient memory" | Mesh too large | Reduce mesh density |

### Mesh Quality Checklist

```markdown
## Before Running Analysis

□ Element quality > 0.2 (Jacobian)
□ No inverted elements
□ Aspect ratio < 10 (ideally < 5)
□ At least 3 elements through thickness
□ Refinement at stress concentrations
□ Smooth transition between sizes (< 2x change)
□ Physical groups defined for BCs
```

### Result Validation

```markdown
## Sanity Checks

□ Reaction forces sum to applied loads
□ Displacement magnitude reasonable
□ Stress distribution makes physical sense
□ Max stress at expected locations
□ Mesh convergence verified
□ Compare to hand calculations
```

### Performance Tips

1. **Start coarse, refine later** - Verify setup with coarse mesh first
2. **Use symmetry** - Half/quarter models where applicable
3. **Submodeling** - Global model → refined local model
4. **Hex vs Tet** - Hex elements more accurate, but harder to mesh
5. **Reduce output** - Only request needed results

---

## Integration Commands

### CLI Tool Concept

```bash
# Future CLI tool structure
fea-tool analyze rod.step --material steel4140 --load 5000
fea-tool mesh geometry.step --size 2.0 --output mesh.inp
fea-tool check results.frd --allowable 400
fea-tool report analysis.inp --format pdf
```

### FreeCAD Macro for Quick Analysis

```python
# Add to FreeCAD macro menu
def quick_stress_check():
    """Quick stress check on selected solid"""

    sel = FreeCADGui.Selection.getSelection()
    if not sel:
        print("Select a solid body first")
        return

    # Prompt for inputs
    from PySide import QtGui

    load, ok = QtGui.QInputDialog.getDouble(
        None, "Load", "Applied load (N):", 5000, 0, 1e9, 0
    )
    if not ok:
        return

    material, ok = QtGui.QInputDialog.getItem(
        None, "Material", "Select material:",
        list(MATERIALS.keys()), 0, False
    )
    if not ok:
        return

    # Run analysis...
    print(f"Running analysis with {load}N load, {material} material")
```
