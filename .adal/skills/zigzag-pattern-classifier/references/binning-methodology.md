# Binning Methodology: Freedman–Diaconis for FD-Binned Variants

Complete specification for computing statistically grounded bin edges using the Freedman–Diaconis rule, enabling granular UP–DOWN pattern classification.

## Why Freedman–Diaconis?

| Criterion                  | FD                         | Fixed Quantiles | Manual Thresholds          |
| -------------------------- | -------------------------- | --------------- | -------------------------- |
| **Automatic**              | ✓                          | ✓               | ✗ (requires expert tuning) |
| **Robust to outliers**     | ✓ (IQR-based)              | ✓               | ✗ (sensitive to extremes)  |
| **Stable counts**          | ✓                          | ✓               | ✗ (volatile bin sizes)     |
| **Interpretable**          | ✓                          | ✓               | ✓                          |
| **Theoretically grounded** | ✓ (asymptotic convergence) | ✗               | ✗                          |
| **No external parameters** | ✓                          | ✗ (K fixed)     | ✗ (manual)                 |

**Recommendation**: Use FD as primary; fall back to quantiles if sample < 400.

---

## Freedman–Diaconis Rule

### Bin Width Formula

```
h = 2 × IQR(X) × n^(-1/3)
```

Where:

- **IQR(X)** = Interquartile range (Q₃ − Q₁)
- **n** = Sample size
- **h** = Optimal bin width

### Number of Bins

```
K = ⌈(max(X) - min(X)) / h⌉
```

Clamp to reasonable range:

```
K ∈ [3, 6]  (typically 3–5 for trading data)
```

### Bin Edges

Create uniform edges over observed range:

```
edges = linspace(min(X), max(X), K+1)
bins = [min:edges[1], edges[1]:edges[2], ..., edges[K-1]:max]
```

---

## Application: UP–DOWN Variants

### For HL (Higher Low) Patterns

**Normalized coordinate**:

```
z = (L₂ - L₀) / (H₁ - L₀)  ∈ (0, 1)
```

Reference: [`notation-definitions.md#normalized-retracement-coordinate`](notation-definitions.md#normalized-retracement-coordinate).

**Procedure**:

1. Collect all UP–DOWN triplets from rolling history (2–3 years).
2. Classify as HL if z > ε_r.
3. Extract subset Z = {z_i : z_i > ε_r}.
4. Winsorize Z at 0.5%–99.5% to remove extreme outliers.
5. Compute IQR(Z_winsor).
6. Calculate h = 2 × IQR(Z) × |Z|^(-1/3).
7. Determine K = clip(⌈(max Z − min Z) / h⌉, 3, 6).
8. Create uniform edges on [min Z, max Z] with K bins.
9. Label bins HL-FD1 (shallowest), HL-FD2, ..., HL-FDK (deepest).

### For LL (Lower Low) Patterns

**Normalized coordinate** (overshoot depth):

```
o = -z = (L₀ - L₂) / ATR₁₄  ∈ (0, ∞)
```

Reference: [`notation-definitions.md#volatility-normalized-overshoot`](notation-definitions.md#volatility-normalized-overshoot).

**Procedure**:

1. Collect all UP–DOWN triplets.
2. Classify as LL if z < −ε_r (equivalently, o > ε_r).
3. Extract subset O = {o_i : o_i > ε_r}.
4. Winsorize O at 0.5%–99.5%.
5. Compute IQR(O_winsor).
6. Calculate h = 2 × IQR(O) × |O|^(-1/3).
7. Determine K = clip(⌈(max O − min O) / h⌉, 3, 6).
8. Create uniform edges on [min O, max O] with K bins.
9. Label bins LL-FD1 (micro undercut), LL-FD2, ..., LL-FDK (extreme undercut).

### For EL (Equal Low) Patterns

**No binning**: Single class if |z| ≤ ε_r.

---

## Example Calculation

### Scenario: H1 EURUSD, Rolling 3-Year Window

**Input Data**:

- 1,500 UP–DOWN triplets collected over 3 years of H1 data
- ε_r computed for each triplet (see [epsilon-tolerance.md](epsilon-tolerance.md))
- Roughly 60% are HL, 20% are EL, 20% are LL

### HL Binning

**Step 1: Extract HL subset**

```
Z_raw = {z_i for all triplets where z_i > ε_r_i}
|Z_raw| = 900 triplets
```

**Step 2: Winsorize**

```
Z_0.5% ≈ 0.05  (5% retrace)
Z_99.5% ≈ 0.95  (95% retrace)
Z_winsor = clip(Z_raw, 0.05, 0.95)
|Z_winsor| = 880 triplets (20 removed as outliers)
```

**Step 3: Calculate IQR**

```
Q1 = 0.20  (25th percentile: 20% retrace)
Q3 = 0.60  (75th percentile: 60% retrace)
IQR(Z) = 0.60 − 0.20 = 0.40
```

**Step 4: Compute bin width**

```
h = 2 × 0.40 × 880^(-1/3)
  = 0.80 × 0.0968
  ≈ 0.0774
```

**Step 5: Determine K**

```
Range = max(Z) − min(Z) ≈ 0.95 − 0.05 = 0.90
K_raw = ⌈0.90 / 0.0774⌉ = ⌈11.6⌉ = 12
K = clip(12, 3, 6) = 6  (cap at 6 for readability)
```

**Step 6: Create edges**

```
edges = linspace(0.05, 0.95, K+1)
      = [0.05, 0.20, 0.35, 0.50, 0.65, 0.80, 0.95]
```

**Step 7: Bin labels**

```
HL-FD1: z ∈ [0.80, 0.95]   (shallow; 20–25% of HL)
HL-FD2: z ∈ [0.65, 0.80]   (mid-upper; 18–22% of HL)
HL-FD3: z ∈ [0.50, 0.65]   (mid-lower; 17–21% of HL)
HL-FD4: z ∈ [0.35, 0.50]   (deep; 15–20% of HL)
HL-FD5: z ∈ [0.20, 0.35]   (deep; 12–17% of HL)
HL-FD6: z ∈ [0.05, 0.20]   (nearly complete; 8–12% of HL)
```

### LL Binning

**Step 1: Extract LL subset**

```
O_raw = {−z_i for all triplets where z_i < −ε_r_i}
|O_raw| = 300 triplets
```

**Step 2: Winsorize**

```
O_0.5% ≈ 0.05  (depth of 5% normalized by ATR)
O_99.5% ≈ 2.50  (depth of 250% normalized by ATR, extreme)
O_winsor = clip(O_raw, 0.05, 2.50)
|O_winsor| = 290 triplets (10 removed as outliers)
```

**Step 3: Calculate IQR**

```
Q1 = 0.15  (25th percentile)
Q3 = 0.60  (75th percentile)
IQR(O) = 0.60 − 0.15 = 0.45
```

**Step 4: Compute bin width**

```
h = 2 × 0.45 × 290^(-1/3)
  = 0.90 × 0.0675
  ≈ 0.0608
```

**Step 5: Determine K**

```
Range = max(O) − min(O) ≈ 2.50 − 0.05 = 2.45
K_raw = ⌈2.45 / 0.0608⌉ = ⌈40.3⌉ = 40
K = clip(40, 3, 6) = 6  (cap at 6)
```

**Step 6: Create edges**

```
edges = linspace(0.05, 2.50, K+1)
      = [0.05, 0.45, 0.85, 1.25, 1.65, 2.05, 2.50]
```

**Step 7: Bin labels**

```
LL-FD1: o ∈ [0.05, 0.45]   (micro; 40–50% of LL)
LL-FD2: o ∈ [0.45, 0.85]   (shallow; 20–25% of LL)
LL-FD3: o ∈ [0.85, 1.25]   (deep; 10–15% of LL)
LL-FD4: o ∈ [1.25, 1.65]   (deeper; 5–10% of LL)
LL-FD5: o ∈ [1.65, 2.05]   (extreme; 2–5% of LL)
LL-FD6: o ∈ [2.05, 2.50]   (catastrophic; <2% of LL)
```

---

## Practical Considerations

### Sample Size Requirements

| Minimum N | Confidence | Recommendation                 |
| --------- | ---------- | ------------------------------ |
| < 100     | Low        | Use quantiles or fixed bins    |
| 100–400   | Moderate   | FD works but use K ∈ [3,4]     |
| 400–2000  | Good       | FD recommended                 |
| > 2000    | Excellent  | FD reliable; can use K ∈ [5,6] |

**For EURUSD**: 2–3 years of daily to hourly data typically yields > 1000 triplets per timeframe → FD is appropriate.

### Winsorization Strategy

Clip extreme outliers at 0.5%–99.5% to:

- Reduce FD sensitivity to tail events
- Maintain reasonable bin widths
- Preserve representativeness of typical market conditions

### Refitting Schedule

Recompute bin edges periodically to track regime drift:

| Timeframe  | Refit Frequency         | Reason                                |
| ---------- | ----------------------- | ------------------------------------- |
| **M5–M15** | Monthly                 | Higher turnover; faster regime change |
| **M30–H4** | Quarterly               | Moderate drift                        |
| **D1**     | Quarterly–Semi-annually | Slower regime change                  |

### Stability Test

If refit produces significantly different K or edges, investigate:

1. Market regime shift (trending → ranging or vice versa)
2. Volatility regime change
3. Seasonality effects
4. Data quality issues

---

## Fallback: Quantile-Based Binning

If FD results are unstable or sample is small, use fixed quantiles:

```
HL quantiles:  20%, 40%, 60%, 80%  → 4 bins (HL-Q1, HL-Q2, HL-Q3, HL-Q4)
LL quantiles:  20%, 40%, 60%, 80%  → 4 bins (LL-Q1, LL-Q2, LL-Q3, LL-Q4)
```

Each quantile bin contains ~25% of observations; simpler but less optimal than FD.

---

## Implementation Pseudocode

```python
def compute_fd_bins(X, min_K=3, max_K=6):
    """
    Compute Freedman–Diaconis bin edges.

    Args:
        X: Array of normalized values (e.g., z for HL or o for LL)
        min_K, max_K: Bounds on bin count

    Returns:
        edges: Array of bin edges [min, edge1, edge2, ..., max]
        K: Number of bins
    """

    X_array = np.array(X)
    n = len(X_array)

    # Winsorize at 0.5% and 99.5%
    X_winsor = np.clip(X_array, np.percentile(X_array, 0.5),
                                np.percentile(X_array, 99.5))

    # Compute IQR and bin width
    Q1, Q3 = np.percentile(X_winsor, [25, 75])
    IQR = Q3 - Q1

    if IQR == 0:
        # All values are equal; use quantile bins
        edges = np.percentile(X_array, [0, 20, 40, 60, 80, 100])
        return edges, min(5, max_K)

    h = 2 * IQR * (n ** (-1/3))
    K_raw = int(np.ceil((np.max(X_winsor) - np.min(X_winsor)) / h))
    K = np.clip(K_raw, min_K, max_K)

    # Create uniform edges
    edges = np.linspace(np.min(X_array), np.max(X_array), K + 1)

    return edges, K


def classify_triplet(L0, H1, L2, epsilon_r, fd_edges_hl, fd_edges_ll):
    """
    Classify an UP–DOWN triplet into FD-binned variant.

    Args:
        L0, H1, L2: Pivot prices
        epsilon_r: Relative tolerance band
        fd_edges_hl: FD bin edges for HL
        fd_edges_ll: FD bin edges for LL

    Returns:
        variant: String label (e.g., 'HL-FD2', 'LL-FD3', 'EL')
    """

    z = (L2 - L0) / (H1 - L0) if H1 > L0 else 0.0

    if abs(z) <= epsilon_r:
        return 'EL'
    elif z > epsilon_r:
        # HL: find which bin
        for i, (low, high) in enumerate(zip(fd_edges_hl[:-1], fd_edges_hl[1:])):
            if low <= z < high or (i == len(fd_edges_hl) - 2 and z == high):
                return f'HL-FD{i+1}'
        return 'HL-FD1'  # Fallback
    else:
        # LL: compute overshoot and find bin
        o = -z
        for i, (low, high) in enumerate(zip(fd_edges_ll[:-1], fd_edges_ll[1:])):
            if low <= o < high or (i == len(fd_edges_ll) - 2 and o == high):
                return f'LL-FD{i+1}'
        return 'LL-FD1'  # Fallback
```

---

## Validation Checklist

- [ ] Sample size N ≥ 400 for each (HL, LL)
- [ ] IQR > 0 (avoid degenerate case of zero variance)
- [ ] Winsorization removes <5% of data (outliers only)
- [ ] K ∈ [3, 6] (readable bin count)
- [ ] Bin edges monotonically increasing
- [ ] Each bin contains ≥5 observations
- [ ] Refit monthly; compare edges to prior month (should be stable)
- [ ] Backtest: returns per bin should show monotonic trend

---

## References

- **Freedman, D. & Diaconis, P.** (1981). "On the histogram as a density estimator." _Zeitschrift für Wahrscheinlichkeitstheorie und Verwandte Gebiete_.
- **Sturges' Rule** (alternative): K ≈ ⌈log₂(n)⌉; coarser bins, simpler formula.
- **Scott's Rule** (alternative): h = 3.49 × σ × n^(-1/3); sensitive to σ estimate.

---

**Last Updated**: 2025-10-22
**Context**: UP–DOWN pattern binning; 2–3 year rolling history; EURUSD typical.
