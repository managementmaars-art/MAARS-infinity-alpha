# QuickStress Workflow

Rapid analytical stress calculations before committing to full FEA.

## Trigger

"quick stress check", "hand calc", "analytical check"

## Process

### 1. Identify Component Type

Ask user to specify:
- Component type (rod, tube, eye, piston, thread)
- Critical dimensions
- Loading conditions
- Material

### 2. Apply Relevant Formulas

**Rod (Axial):**
```
σ = F / A = F / (π × d²/4)
```

**Rod (Buckling):**
```
Pcr = π² × E × I / (K × L)²
where I = π × d⁴ / 64
```

**Tube (Hoop):**
```
σ_hoop = P × r / t  (thin wall)
σ_hoop = P × (ri² + ro²) / (ro² - ri²)  (thick wall)
```

**Eye (Bearing):**
```
σ_bearing = F / (d × t)
```

**Thread (Shear):**
```
τ = F / (π × d × Le)
```

### 3. Compare to Allowables

| Material | Sy (MPa) | σ_allow (SF=2) |
|----------|----------|----------------|
| 6061-T6 | 276 | 138 |
| 7075-T6 | 503 | 251 |
| 4140 QT | 655-860 | 328-430 |
| 4340 QT | 860-1100 | 430-550 |

### 4. Output Format

```
=== QUICK STRESS CHECK ===
Component: [type]
Material: [material]
Load: [value] N

Stress: [value] MPa
Allowable: [value] MPa
Safety Factor: [value]
Status: PASS/FAIL

Note: Full FEA recommended if SF < 3 or complex geometry
```

## Example Interaction

```
User: "Quick check - will a 16mm 4140 rod handle 4000N?"

Kai:
=== QUICK STRESS CHECK ===
Component: Piston Rod
Material: Steel 4140 (Sy = 700 MPa assumed)
Load: 4000 N

Area = π × 16²/4 = 201 mm²
Axial Stress = 4000 / 201 = 19.9 MPa
Allowable (SF=2) = 350 MPa
Safety Factor = 17.6 ✓

PASS - Very conservative design

For buckling (200mm stroke, K=0.7):
I = π × 16⁴/64 = 3217 mm⁴
Pcr = π² × 205000 × 3217 / (0.7 × 200)² = 332 kN
Buckling SF = 83 ✓

Recommendation: Rod is over-designed for this load.
Could reduce to Ø12mm (SF_stress=5.0, SF_buckle=21)
```
