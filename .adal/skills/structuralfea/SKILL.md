---
name: StructuralFEA
description: Open source FEA structural analysis for damper and mechanical components. Generates CalculiX input files, guides mesh setup, provides material databases, interprets results. USE WHEN user says 'FEA', 'structural analysis', 'stress analysis', 'buckling', 'modal analysis', 'finite element', 'CalculiX', 'mesh', or needs to validate damper component designs.
effort: high
---

# StructuralFEA

Open source finite element analysis skill for structural validation of damper components and mechanical parts. Uses CalculiX, FreeCAD FEM, Gmsh, and ParaView.

## Workflow Routing

| Workflow | Trigger | Description |
|----------|---------|-------------|
| **QuickStress** | "quick stress check", "hand calc" | Analytical stress calculations before FEA |
| **ComponentFEA** | "analyze rod", "tube stress", "piston FEA" | Full FEA of specific component |
| **BucklingAnalysis** | "buckling", "column", "stability" | Euler and nonlinear buckling |
| **ModalAnalysis** | "natural frequency", "modal", "vibration" | Eigenvalue extraction |
| **FatigueCheck** | "fatigue", "endurance", "life" | Stress-life fatigue assessment |

## Toolchain Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    OPEN SOURCE FEA STACK                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐          │
│   │  FreeCAD    │────▶│    Gmsh     │────▶│  CalculiX   │          │
│   │  (CAD/GUI)  │     │  (Meshing)  │     │  (Solver)   │          │
│   └─────────────┘     └─────────────┘     └──────┬──────┘          │
│         │                                         │                 │
│         │              ┌─────────────┐           │                 │
│         └─────────────▶│  ParaView   │◀──────────┘                 │
│                        │  (Post-proc)│                              │
│                        └─────────────┘                              │
│                                                                     │
│   Alternative paths:                                                │
│   - FreeCAD FEM Workbench (integrated GUI workflow)                │
│   - Salome-Meca (Code_Aster) for advanced nonlinear               │
│   - OpenFOAM for CFD (valve flow analysis)                         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Installation

### macOS (Homebrew)

```bash
# FreeCAD with FEM workbench
brew install --cask freecad

# Gmsh mesher
brew install gmsh

# CalculiX solver (requires tap)
brew tap costerwi/calculix
brew install calculix-ccx     # Solver
brew install calculix-cgx     # Pre/post (optional, requires XQuartz on macOS)

# ParaView post-processor
brew install --cask paraview

# Optional: OpenFOAM for CFD
brew install openfoam
```

### macOS Alternative (Conda)

```bash
# If you prefer conda
conda install conda-forge::calculix
conda install conda-forge::gmsh
```

### Linux (Ubuntu/Debian)

```bash
# FreeCAD
sudo apt install freecad

# Gmsh
sudo apt install gmsh

# CalculiX
sudo apt install calculix-ccx calculix-cgx

# ParaView
sudo apt install paraview

# Salome-Meca (alternative, more powerful)
# Download from https://www.code-aster.org/
```

### Windows

```powershell
# FreeCAD - via winget or download from freecad.org
winget install FreeCAD.FreeCAD

# Gmsh - via winget or download from gmsh.info
winget install -e --id Gmsh.Gmsh

# CalculiX - multiple options:

# Option 1: bConverged installer (recommended, includes GUI)
# Download from http://www.bconverged.com/calculix.php
# Provides ccx.exe and optional cgx.exe

# Option 2: Chocolatey (if installed)
choco install calculix

# Option 3: WSL (most reliable, identical to Linux)
# Install WSL, then: sudo apt install calculix-ccx calculix-cgx

# ParaView - via winget or download from paraview.org
winget install Kitware.ParaView
```

**Note:** CalculiX is Unix-native software. The bConverged installer is the easiest Windows option. For maximum compatibility, consider running CalculiX in WSL (Windows Subsystem for Linux) which provides identical behaviour to native Linux.

### Verify Installation

```bash
# Check versions
freecad --version
gmsh --version
ccx -v
paraview --version
```

## Material Database

### Aluminium Alloys (for CalculiX .inp files)

```
*MATERIAL, NAME=AL6061T6
*ELASTIC
68900, 0.33
*DENSITY
2700E-12
*EXPANSION
23.6E-6

*MATERIAL, NAME=AL7075T6
*ELASTIC
71700, 0.33
*DENSITY
2810E-12
*EXPANSION
23.4E-6

*MATERIAL, NAME=AL2024T351
*ELASTIC
72400, 0.33
*DENSITY
2780E-12
*EXPANSION
23.2E-6
```

### Steels (for CalculiX .inp files)

```
*MATERIAL, NAME=STEEL4140
*ELASTIC
205000, 0.29
*DENSITY
7850E-12
*EXPANSION
12.3E-6
*PLASTIC
655, 0.0
860, 0.10

*MATERIAL, NAME=STEEL4340
*ELASTIC
205000, 0.29
*DENSITY
7850E-12
*EXPANSION
11.7E-6
*PLASTIC
860, 0.0
1100, 0.08

*MATERIAL, NAME=STEEL174PH
*ELASTIC
196000, 0.27
*DENSITY
7780E-12
*EXPANSION
10.8E-6
*PLASTIC
1170, 0.0
1310, 0.06
```

### Material Properties Summary

| Material | E (MPa) | ν | ρ (kg/m³) | Sy (MPa) | Su (MPa) |
|----------|---------|---|-----------|----------|----------|
| 6061-T6 | 68,900 | 0.33 | 2,700 | 276 | 310 |
| 7075-T6 | 71,700 | 0.33 | 2,810 | 503 | 572 |
| 4140 QT | 205,000 | 0.29 | 7,850 | 655-860 | 810-970 |
| 4340 QT | 205,000 | 0.29 | 7,850 | 860-1100 | 950-1200 |
| 17-4 PH H900 | 196,000 | 0.27 | 7,780 | 1,170 | 1,310 |

## Component Templates

### Piston Rod - Axial + Bending Load

```
** ================================================
** PISTON ROD FEA - COMBINED LOADING
** ================================================
**
*HEADING
Damper Piston Rod - Axial Load with Side Force
**
*NODE, NSET=ALLNODES
** Node data imported from mesh file
*INCLUDE, INPUT=rod_mesh.inp
**
** ------------------------------------------------
** MATERIAL DEFINITION
** ------------------------------------------------
*MATERIAL, NAME=STEEL4140
*ELASTIC
205000, 0.29
*DENSITY
7850E-12
**
*SOLID SECTION, ELSET=EALL, MATERIAL=STEEL4140
**
** ------------------------------------------------
** BOUNDARY CONDITIONS
** ------------------------------------------------
** Fixed end (piston attachment)
*BOUNDARY
FIXED_END, 1, 3, 0.0
**
** ------------------------------------------------
** LOADING
** ------------------------------------------------
** Axial load (compression)
*CLOAD
LOAD_NODE, 3, -5000.0
**
** Side load (bending from misalignment)
*CLOAD
LOAD_NODE, 1, 500.0
**
** ------------------------------------------------
** ANALYSIS
** ------------------------------------------------
*STEP
*STATIC
**
*NODE FILE
U
*EL FILE
S, E
**
*END STEP
```

### Tube - Internal Pressure

```
** ================================================
** DAMPER TUBE - INTERNAL PRESSURE
** ================================================
**
*HEADING
Damper Tube Hoop Stress Analysis
**
*INCLUDE, INPUT=tube_mesh.inp
**
*MATERIAL, NAME=AL6061T6
*ELASTIC
68900, 0.33
**
*SOLID SECTION, ELSET=EALL, MATERIAL=AL6061T6
**
** Fixed end cap
*BOUNDARY
END_FIXED, 1, 3, 0.0
**
** Internal pressure (20 MPa = 200 bar)
*DLOAD
INNER_SURFACE, P, 20.0
**
*STEP
*STATIC
*NODE FILE
U
*EL FILE
S, E
*END STEP
```

### Buckling Analysis Template

```
** ================================================
** ROD BUCKLING ANALYSIS
** ================================================
**
*HEADING
Piston Rod Linear Buckling
**
*INCLUDE, INPUT=rod_mesh.inp
**
*MATERIAL, NAME=STEEL4340
*ELASTIC
205000, 0.29
**
*SOLID SECTION, ELSET=EALL, MATERIAL=STEEL4340
**
** Pinned bottom
*BOUNDARY
BOTTOM, 1, 2, 0.0
BOTTOM, 3, 3, 0.0
**
** Guided top (can move axially)
*BOUNDARY
TOP, 1, 2, 0.0
**
** Unit load for eigenvalue extraction
*CLOAD
TOP, 3, -1.0
**
** ------------------------------------------------
** LINEAR BUCKLING (EIGENVALUE)
** ------------------------------------------------
*STEP
*BUCKLE
5
**
*NODE FILE
U
*EL FILE
S
**
*END STEP
```

### Modal Analysis Template

```
** ================================================
** COMPONENT MODAL ANALYSIS
** ================================================
**
*HEADING
Natural Frequency Extraction
**
*INCLUDE, INPUT=component_mesh.inp
**
*MATERIAL, NAME=STEEL4140
*ELASTIC
205000, 0.29
*DENSITY
7850E-12
**
*SOLID SECTION, ELSET=EALL, MATERIAL=STEEL4140
**
*BOUNDARY
FIXED, 1, 3, 0.0
**
*STEP
*FREQUENCY
10
**
*NODE FILE
U
*EL FILE
S
**
*END STEP
```

## Meshing Guidelines

### Element Size Recommendations

| Component | Global Size | Refinement Areas | Element Type |
|-----------|-------------|------------------|--------------|
| Rod (Ø16-25mm) | 2-3mm | Threads: 0.5mm, Fillet: 0.5mm | C3D10 (tet) |
| Tube (Ø40-60mm) | 3-4mm | Thread root: 0.5mm | C3D10 or C3D20R |
| Piston | 2-3mm | Valve ports: 0.3mm | C3D10 |
| Eye/Clevis | 2-3mm | Hole edge: 0.5mm | C3D10 |

### Gmsh Meshing Script

```geo
// ================================================
// GMSH SCRIPT FOR DAMPER ROD
// ================================================

// Load geometry (STEP file from CAD)
Merge "piston_rod.step";

// Define mesh size
Mesh.CharacteristicLengthMax = 2.0;  // mm
Mesh.CharacteristicLengthMin = 0.3;  // mm

// Refine at threads (identify surfaces by number)
Field[1] = Distance;
Field[1].FacesList = {5, 6};  // Thread surfaces
Field[1].NNodesByEdge = 100;

Field[2] = Threshold;
Field[2].IField = 1;
Field[2].LcMin = 0.5;
Field[2].LcMax = 2.0;
Field[2].DistMin = 0.5;
Field[2].DistMax = 5.0;

Background Field = 2;

// Generate 3D mesh
Mesh.Algorithm3D = 1;  // Delaunay
Mesh 3;

// Save for CalculiX
Save "rod_mesh.inp";
```

### FreeCAD FEM Workflow

1. **Create/Import Geometry**
   - Part Design workbench for new geometry
   - Import STEP/IGES for existing CAD

2. **Switch to FEM Workbench**
   - Analysis → New Analysis
   - Model → Solver CalculiX Standard

3. **Assign Material**
   - Model → Material for Solid
   - Select from library or define custom

4. **Apply Constraints**
   - Model → Constraint Fixed (for supports)
   - Model → Constraint Force (for loads)
   - Model → Constraint Pressure (for surfaces)

5. **Create Mesh**
   - Mesh → FEM Mesh from Shape
   - Set element size, refinement

6. **Solve**
   - Solve → Solver Job Control
   - Write .inp file, Run CalculiX

7. **View Results**
   - Results → Show Result
   - Filter: Von Mises, displacement, etc.

## Result Interpretation

### Stress Limits (Design Allowables)

| Material | Static σ_allow | Fatigue σ_allow | Note |
|----------|----------------|-----------------|------|
| 6061-T6 | 165 MPa | 60 MPa | 0.6×Sy, Se=97 MPa |
| 7075-T6 | 300 MPa | 100 MPa | 0.6×Sy, Se=159 MPa |
| 4140 QT | 400-520 MPa | 200-260 MPa | Depends on temper |
| 4340 QT | 520-660 MPa | 260-330 MPa | Premium fatigue |
| 17-4 PH | 700 MPa | 350 MPa | H900 condition |

### Safety Factor Guidelines

| Application | Static SF | Fatigue SF | Buckling SF |
|-------------|-----------|------------|-------------|
| Road vehicle | 2.0 | 3.0 | 3.0 |
| Motorsport | 1.5 | 2.0 | 2.5 |
| Industrial | 2.5 | 4.0 | 4.0 |

### Result Checklist

```markdown
## FEA Result Verification

□ Mesh convergence check (refine 2x, stress change <5%)
□ Displacement magnitude reasonable
□ Stress concentrations identified and acceptable
□ von Mises < σ_allowable everywhere
□ No yielding in critical regions
□ Buckling factor > required SF
□ Natural frequencies away from excitation frequencies
□ Reaction forces balance applied loads
□ No mesh distortion warnings
```

## Quick Stress Checks (Before FEA)

### Rod Axial Stress

```
σ = F / A = F / (π × d²/4)

Example:
F = 5000 N, d = 20 mm
σ = 5000 / (π × 20²/4) = 15.9 MPa

For 4140 steel (Sy = 700 MPa):
SF = 700 / 15.9 = 44 ✓ (very conservative)
```

### Rod Buckling

```
Pcr = π² × E × I / (K × L)²

I = π × d⁴ / 64

Example:
d = 20 mm, L = 200 mm, K = 0.7 (guided)
E = 205,000 MPa

I = π × 20⁴ / 64 = 7854 mm⁴
Pcr = π² × 205000 × 7854 / (0.7 × 200)²
Pcr = 809,000 N = 809 kN

For F = 5000 N:
SF = 809,000 / 5000 = 162 ✓
```

### Tube Hoop Stress

```
σ_hoop = P × r / t

Example:
P = 20 MPa, r = 20 mm (inner), t = 3 mm
σ_hoop = 20 × 20 / 3 = 133 MPa

For 6061-T6 (Sy = 276 MPa):
SF = 276 / 133 = 2.1 ✓
```

## Integration with Other Skills

| Skill | Integration |
|-------|-------------|
| **DamperEngineering** | Component loads, material selection |
| **PlantCapability** | Machining feasibility of designs |
| **CuttingParams** | Surface finish requirements |
| **QuoteEstimator** | Material costs, machining time |

## Examples

**Example 1: Quick rod check**
```
User: "Check if 16mm rod can handle 4000N"
→ Run analytical calculation
→ Check axial stress vs allowable
→ Check buckling if stroke > 100mm
→ Report pass/fail with SF
```

**Example 2: Full FEA workflow**
```
User: "Run FEA on piston rod with thread detail"
→ Generate CalculiX template
→ Provide meshing guidance
→ Define boundary conditions
→ Interpret results
→ Recommend design changes if needed
```

**Example 3: Buckling analysis**
```
User: "Will this long rod buckle under max load?"
→ Euler calculation first
→ Set up CalculiX buckling analysis
→ Extract eigenvalue (buckling factor)
→ Report margin
```
