# UP–DOWN Variants: Granular Two-Pivot Classification with FD Binning

Comprehensive analysis of UP–DOWN (L0→H1→L2) patterns with Freedman–Diaconis binning for fine-grained regime discrimination.

## Overview

Two-pivot UP–DOWN patterns provide **immediate binary classification** (simpler than three-pivot):

- **Simple**: Only 3 base classes (EL, HL, LL)
- **Rich**: FD binning adds statistical depth without manual thresholding
- **Practical**: Fewer degrees of freedom = more stable estimates per timeframe

## Base Classification (3 Classes)

All UP–DOWN triplets fall into exactly one of:

| Class  | Definition | Meaning               | Frequency |
| ------ | ---------- | --------------------- | --------- |
| **EL** | L₂ ≈ L₀    | Equal Low (retest)    | ~20–30%   |
| **HL** | L₂ > L₀    | Higher Low (pullback) | ~50–60%   |
| **LL** | L₂ < L₀    | Lower Low (undercut)  | ~10–20%   |

Equality determined by tolerance band ε (see [epsilon-tolerance.md](epsilon-tolerance.md)).

## Granular Classification: 9 FD-Binned Variants

Decompose HL and LL into 4 sub-classes each using normalized retracement depth:

```
z = (L2 - L0) / (H1 - L0)  ∈ [0, 1]  for HL
o = -z / ATR14           ∈ [0, ∞)  for LL
```

See [`notation-definitions.md#normalized-retracement-coordinate`](notation-definitions.md#normalized-retracement-coordinate) and [`notation-definitions.md#volatility-normalized-overshoot`](notation-definitions.md#volatility-normalized-overshoot) for the single-source definitions.

Run Freedman–Diaconis separately on each; typical result: 4 bins per side + 1 EL bin = **9 variants**.

## Complete Variant Set

### Class: EL (Equal Low)

```
Levels    │ L0 │ H1 │ L2 │
≈H1       │    │ •  │    │
HL bands  │    │    │    │
= L0±ε    │ •  │    │ •  │
Below L0  │    │    │    │
```

**Interpretation**: L₂ equals L₀ within tolerance band ε.
**Market Regime**: **Retest** – Market re-establishes support; neutral to slight upside.
**Probability**: Lower (20–30% of observations).
**Next Move**: Likely bounce from L₀; watch for breakout above H₁.

---

### Class: HL-FD1 — Shallow Retrace (0.75 < z < 1.0)

```
Levels          │ L0 │ H1 │ L2 │
≈H1             │    │ •  │    │
HL-FD1 band     │    │    │ •  │
HL-FD2 band     │    │    │    │
HL-FD3 band     │    │    │    │
HL-FD4 band     │    │    │    │
= L0            │ •  │    │    │
Below L0        │    │    │    │
```

**Interpretation**: L₂ retraces only 0–25% of swing (H₁ - L₀).
**Market Regime**: **Shallow Pullback** – Minor consolidation; bullish continuation likely.
**Probability**: Most common HL sub-class (35–40% of HL).
**Next Move**: Quick recovery; minimal hesitation; buyers in control.

---

### Class: HL-FD2 — Mid-Upper Retrace (0.50 < z ≤ 0.75)

```
Levels          │ L0 │ H1 │ L2 │
≈H1             │    │ •  │    │
HL-FD1 band     │    │    │    │
HL-FD2 band     │    │    │ •  │
HL-FD3 band     │    │    │    │
HL-FD4 band     │    │    │    │
= L0            │ •  │    │    │
Below L0        │    │    │    │
```

**Interpretation**: L₂ retraces 25–50% of swing (Fibonacci 38.2%, 50%).
**Market Regime**: **Moderate Pullback** – Standard retracement; consolidation before continuation.
**Probability**: Second-most common HL sub-class (25–30% of HL).
**Next Move**: May establish support; decision point; watch above H₁ for breakout signal.

---

### Class: HL-FD3 — Mid-Lower Retrace (0.25 < z ≤ 0.50)

```
Levels          │ L0 │ H1 │ L2 │
≈H1             │    │ •  │    │
HL-FD1 band     │    │    │    │
HL-FD2 band     │    │    │    │
HL-FD3 band     │    │    │ •  │
HL-FD4 band     │    │    │    │
= L0            │ •  │    │    │
Below L0        │    │    │    │
```

**Interpretation**: L₂ retraces 50–75% of swing (Fibonacci 61.8%).
**Market Regime**: **Deep Pullback** – Significant retracement; sellers testing conviction.
**Probability**: Less common HL sub-class (20–25% of HL).
**Next Move**: Risk/reward tight; reversal risk growing; tight stops required.

---

### Class: HL-FD4 — Deep Retrace (0 < z ≤ 0.25)

```
Levels          │ L0 │ H1 │ L2 │
≈H1             │    │ •  │    │
HL-FD1 band     │    │    │    │
HL-FD2 band     │    │    │    │
HL-FD3 band     │    │    │    │
HL-FD4 band     │    │    │ •  │
= L0            │ •  │    │    │
Below L0        │    │    │    │
```

**Interpretation**: L₂ retraces 75–100% of swing (approaches L₀ but doesn't break below).
**Market Regime**: **Nearly Complete Retrace** – Significant selling pressure; buyers barely hold.
**Probability**: Least common HL sub-class (10–15% of HL).
**Next Move**: Highest reversal risk; trendline break possible; wait for confirmation close above L₂.

---

### Class: LL-FD1 — Micro Undercut (o ≤ q₂₀)

```
Levels          │ L0 │ H1 │ L2 │
≈H1             │    │ •  │    │
HL-FD bands     │    │    │    │
= L0            │ •  │    │    │
LL-FD1 band     │    │    │ •  │
LL-FD2 band     │    │    │    │
LL-FD3 band     │    │    │    │
LL-FD4 band     │    │    │    │
```

**Interpretation**: L₂ breaks below L₀ by ≤20th percentile of overshoot depth (minimal).
**Market Regime**: **Micro Undercut** – Brief failure break; contained spillover; short seller test.
**Probability**: Most common LL sub-class (40–50% of LL).
**Next Move**: Quick reversal likely; spike play; watch for high-vol bounce.

**Flags**:

- **+S** (Spike): If undercut occurs in single bar, expect rapid reversal.
- **+C** (Close below L₀): Check if close is below L₀; stronger commitment if yes.

---

### Class: LL-FD2 — Shallow Undercut (q₂₀ < o ≤ q₄₀)

```
Levels          │ L0 │ H1 │ L2 │
≈H1             │    │ •  │    │
HL-FD bands     │    │    │    │
= L0            │ •  │    │    │
LL-FD1 band     │    │    │    │
LL-FD2 band     │    │    │ •  │
LL-FD3 band     │    │    │    │
LL-FD4 band     │    │    │    │
```

**Interpretation**: L₂ breaks below L₀ by 20–40th percentile (small overshoot).
**Market Regime**: **Shallow Undercut** – Moderate panic; test of sellers; probable reversal.
**Probability**: Second-most common LL sub-class (25–30% of LL).
**Next Move**: Reversal not guaranteed; may establish lower support; watch for continuation down.

---

### Class: LL-FD3 — Deep Undercut (q₄₀ < o ≤ q₆₀)

```
Levels          │ L0 │ H1 │ L2 │
≈H1             │    │ •  │    │
HL-FD bands     │    │    │    │
= L0            │ •  │    │    │
LL-FD1 band     │    │    │    │
LL-FD2 band     │    │    │    │
LL-FD3 band     │    │    │ •  │
LL-FD4 band     │    │    │    │
```

**Interpretation**: L₂ breaks below L₀ by 40–60th percentile (significant overshoot).
**Market Regime**: **Deep Undercut** – Major breakdown; strong selling; structural support broken.
**Probability**: Less common LL sub-class (15–20% of LL).
**Next Move**: Extended downtrend likely; new support needed; risk management critical.

---

### Class: LL-FD4 — Extreme Undercut (o > q₆₀)

```
Levels          │ L0 │ H1 │ L2 │
≈H1             │    │ •  │    │
HL-FD bands     │    │    │    │
= L0            │ •  │    │    │
LL-FD1 band     │    │    │    │
LL-FD2 band     │    │    │    │
LL-FD3 band     │    │    │    │
LL-FD4 band     │    │    │ •  │
```

**Interpretation**: L₂ breaks below L₀ by >60th percentile (extreme overshoot, rare event).
**Market Regime**: **Extreme Undercut** – Panic, shock, tail event; severe breakdown.
**Probability**: Rare; <10% of LL.
**Next Move**: Crisis mode; VaR breach possible; free-fall likely; watch for capitulation reversal.

**Flags**:

- **+S** (Spike): Extreme undercuts often spike; mean reversion likely if single-bar.
- **+C** (Close below L₀): Critical signal; shows commitment; downside extension very likely.

---

## Optional Sub-Classification Flags

Attach to any variant for richer context:

| Flag   | Meaning                            | Market Signal                                                    |
| ------ | ---------------------------------- | ---------------------------------------------------------------- |
| **+C** | Any close < L₀ between H₁→L₂       | Stronger bearish commitment; downtrend escalates                 |
| **+S** | L₂ occurs in single bar (spike)    | Likely sharp reversal; mean reversion setup; reduced persistence |
| **+X** | No close below L₀, high wicks only | False break; liquidity grab; setup for trap                      |

Example labels: `HL-FD2+C`, `LL-FD4+S+C`, `EL+X`.

---

## Binning Edge Computation

See [binning-methodology.md](binning-methodology.md) for complete FD procedure.

**Quick summary**:

1. Collect 2–3 years of UP–DOWN segments per timeframe.
2. Compute z for HL cases, o for LL cases.
3. Run Freedman–Diaconis: h = 2·IQR(x)·n^(-1/3)
4. Determine K = clip(⌈(max - min) / h⌉, 3, 6)
5. Create uniform bin edges; assign variant labels.
6. Recompute monthly or quarterly to track regime drift.

---

## Market Regime Mapping

| Variant Class | Typical Market Regime | Entry Signal         | Stop Loss    | Target       |
| ------------- | --------------------- | -------------------- | ------------ | ------------ |
| **EL**        | Retest                | Long from L₀+ε       | L₀-ε         | H₁ + ΔH      |
| **HL-FD1**    | Shallow Pullback      | Long from L₂         | L₂-ε         | H₁ + ΔH      |
| **HL-FD2**    | Moderate Pullback     | Long at confirmation | L₂-ε         | Prior H + ΔH |
| **HL-FD3**    | Deep Pullback         | Reduced size; wait   | L₂-ε         | Support + ΔH |
| **HL-FD4**    | Nearly Complete       | Extreme risk; avoid  | L₂-ε         | Critical     |
| **LL-FD1**    | Micro Undercut        | Short spike trade    | L₂+spike     | L₀           |
| **LL-FD2**    | Shallow Undercut      | Wait for reversal    | Breakout     | L₀           |
| **LL-FD3**    | Deep Undercut         | Short continuation   | Reversal     | New lows     |
| **LL-FD4**    | Extreme Undercut      | Crisis mode; hedge   | Capitulation | TBD          |

---

## Implementation Checklist

- [ ] Compute ε (tolerance band) per [epsilon-tolerance.md](epsilon-tolerance.md)
- [ ] Build UP–DOWN triplet list from ZigZag pivots
- [ ] Calculate z = (L₂ - L₀) / (H₁ - L₀) for each triplet
- [ ] Classify EL if |z| ≤ εᵣ; otherwise HL if z > 0 else LL
- [ ] For HL: run FD binning on {z ∈ (εᵣ, 1)}
- [ ] For LL: compute o = -z, run FD binning on {o > εᵣ}
- [ ] Assign labels HL-FD1..k and LL-FD1..j
- [ ] Add optional flags (+C, +S, +X)
- [ ] Store in time-series database with segment_id, timeframe, regime labels
- [ ] Backtest regime-conditional trading rules

---

## Typical Distribution

On EURUSD 2–3 year history (all timeframes combined):

- **EL**: 20–30% (retests common but not dominant)
- **HL-FD1**: 20–25% (shallow pullbacks most common)
- **HL-FD2**: 15–20% (moderate retraces)
- **HL-FD3**: 10–15% (deeper pullbacks less frequent)
- **HL-FD4**: 5–10% (near-complete retraces rare)
- **LL-FD1**: 8–12% (micro undercuts most common LL)
- **LL-FD2**: 4–8% (shallow undershoots less frequent)
- **LL-FD3**: 2–5% (deep undershoots infrequent)
- **LL-FD4**: <2% (extreme undershoots extremely rare)

**Note**: Exact percentages vary by timeframe, symbol, and market regime (trending vs ranging).

---

## Next Steps

1. Implement FD binning on your EURUSD data
2. Backtest returns per variant across M5, M15, M30, H1, H4, D1
3. Compare to other classification schemes (Fibonacci, quantile-based, etc.)
4. Combine variants with volume, spreads, volatility for multi-factor models
5. Extend to 3-pivot UP–DOWN–UP for richer feature set

---

**Reference**: Methodologically complete; 9 variants cover all UP–DOWN configurations.
**Basis**: Freedman–Diaconis binning on volatility-normalized coordinate.
