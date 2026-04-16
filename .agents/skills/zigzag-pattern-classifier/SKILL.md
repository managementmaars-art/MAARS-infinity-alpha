---
name: zigzag-pattern-classifier
description: "ZigZag swing pattern classification framework for algorithmic trading. Covers the complete taxonomy of two-pivot (UP-DOWN, L₀→H₁→L₂) and three-pivot (UP-DOWN-UP, L₀→H₁→L₂→H₃) ZigZag patterns with EL/HL/LL base classes, 9 FD-binned variants, 9 three-pivot variants, 27-way extension, and market regime mapping. Use this skill whenever the user asks about zigzag patterns, swing classification, leg patterns, EL/HL/LL classification, higher-low/lower-low/equal-low patterns, pattern exhaustiveness proofs (why 9 or 27), Freedman-Diaconis binning for swing patterns, epsilon tolerance bands for price equality, normalized retracement z-scores, UP-DOWN or UP-DOWN-UP variant enumeration, market regime labels from swing structure, or any question about how many distinct zigzag configurations exist and what they mean. TRIGGERS - zigzag pattern, swing classification, EL HL LL, higher low lower low, pattern variants, leg classification, zigzag variants, UP-DOWN pattern, three-pivot, two-pivot, FD binning swing, tolerance band epsilon, retracement z-score, pattern exhaustiveness, 9 variants, 27 variants, swing regime, triangle compression, continuation impulse, rally failure."
allowed-tools: Read, Grep, Glob
---

# ZigZag Swing Pattern Classifier

Complete taxonomy for classifying ZigZag swing patterns by structure and market regime. Every confirmed ZigZag sequence maps to exactly one variant — no gaps, no overlaps.

> **Self-Evolving Skill**: This skill improves through use. If instructions are wrong, parameters drifted, or a workaround was needed — fix this file immediately, don't defer. Only update for real, reproducible issues.

## When to Use

- Classifying a confirmed L₀→H₁→L₂ (two-pivot) or L₀→H₁→L₂→H₃ (three-pivot) swing
- Looking up market regime implications of a specific pattern
- Answering "how many distinct patterns exist?" and proving exhaustiveness
- Implementing pattern labeling in code (Rust `qta` crate, Python pipelines)
- Understanding the epsilon tolerance band that defines "equal"
- Applying Freedman-Diaconis binning for sub-classification depth

## Notation (Single Source of Truth)

| Symbol | Definition                                         | Example  |
| ------ | -------------------------------------------------- | -------- |
| **L₀** | Initial low (first confirmed pivot)                | 1.0800   |
| **H₁** | Swing high (reversal peak)                         | 1.0850   |
| **L₂** | Second low (retracement)                           | 1.0810   |
| **H₃** | Second high (three-pivot only)                     | 1.0870   |
| **W**  | Swing magnitude: H₁ − L₀                           | 0.0050   |
| **z**  | Normalized retracement: (L₂ − L₀) / (H₁ − L₀)      | 0.20     |
| **o**  | Volatility-normalized overshoot: (L₀ − L₂) / ATR₁₄ | 0.35     |
| **ε**  | Tolerance band for "equal" classification          | 5 pips   |
| **τ**  | ZigZag reversal threshold                          | 6.6 pips |

### Price Level Comparisons

| Code   | Meaning     | Condition       |
| ------ | ----------- | --------------- |
| **HL** | Higher Low  | L₂ > L₀ + ε     |
| **EL** | Equal Low   | \|L₂ − L₀\| ≤ ε |
| **LL** | Lower Low   | L₂ < L₀ − ε     |
| **HH** | Higher High | H₃ > H₁ + ε     |
| **EH** | Equal High  | \|H₃ − H₁\| ≤ ε |
| **LH** | Lower High  | H₃ < H₁ − ε     |

---

## Part 1: Two-Pivot Patterns (UP-DOWN)

Pattern: **L₀ → H₁ → L₂** (one up-leg, one down-leg)

### Base Classification (3 Classes)

Every UP-DOWN triplet falls into exactly one:

| Class  | Condition       | Meaning               | Frequency |
| ------ | --------------- | --------------------- | --------- |
| **EL** | \|L₂ − L₀\| ≤ ε | Equal Low (retest)    | ~20–30%   |
| **HL** | L₂ > L₀ + ε     | Higher Low (pullback) | ~50–60%   |
| **LL** | L₂ < L₀ − ε     | Lower Low (undercut)  | ~10–20%   |

### Granular Classification: 9 FD-Binned Variants

HL and LL each decompose into 4 sub-classes using Freedman-Diaconis binning on normalized coordinates:

- **HL bins** use z = (L₂ − L₀) / (H₁ − L₀), ranging 0 to 1
- **LL bins** use o = (L₀ − L₂) / ATR₁₄, ranging 0 to ∞

| Variant    | z or o Range    | Market Regime                        | Probability |
| ---------- | --------------- | ------------------------------------ | ----------- |
| **EL**     | \|z\| ≤ ε_r     | Retest — support re-established      | 20–30%      |
| **HL-FD1** | 0.75 < z < 1.0  | Shallow pullback — buyers in control | 20–25%      |
| **HL-FD2** | 0.50 < z ≤ 0.75 | Moderate pullback — Fib 38–50%       | 15–20%      |
| **HL-FD3** | 0.25 < z ≤ 0.50 | Deep pullback — Fib 61.8%            | 10–15%      |
| **HL-FD4** | 0 < z ≤ 0.25    | Near-complete retrace — barely held  | 5–10%       |
| **LL-FD1** | o ≤ q₂₀         | Micro undercut — brief false break   | 8–12%       |
| **LL-FD2** | q₂₀ < o ≤ q₄₀   | Shallow undercut — moderate panic    | 4–8%        |
| **LL-FD3** | q₄₀ < o ≤ q₆₀   | Deep undercut — structural break     | 2–5%        |
| **LL-FD4** | o > q₆₀         | Extreme undercut — tail event        | <2%         |

### Trading Implications

| Variant    | Entry Signal         | Stop Loss    | Target       |
| ---------- | -------------------- | ------------ | ------------ |
| **EL**     | Long from L₀+ε       | L₀−ε         | H₁ + ΔH      |
| **HL-FD1** | Long from L₂         | L₂−ε         | H₁ + ΔH      |
| **HL-FD2** | Long at confirmation | L₂−ε         | Prior H + ΔH |
| **HL-FD3** | Reduced size; wait   | L₂−ε         | Support + ΔH |
| **HL-FD4** | Extreme risk; avoid  | L₂−ε         | Critical     |
| **LL-FD1** | Short spike trade    | L₂+spike     | L₀           |
| **LL-FD2** | Wait for reversal    | Breakout     | L₀           |
| **LL-FD3** | Short continuation   | Reversal     | New lows     |
| **LL-FD4** | Crisis mode; hedge   | Capitulation | TBD          |

### Optional Sub-Classification Flags

Attach to any variant for richer context:

| Flag   | Meaning                         | Signal                         |
| ------ | ------------------------------- | ------------------------------ |
| **+C** | Any close < L₀ between H₁→L₂    | Stronger bearish commitment    |
| **+S** | L₂ occurs in single bar (spike) | Sharp reversal; mean reversion |
| **+X** | Wicks below L₀ only, no close   | Liquidity grab; false break    |

Example labels: `HL-FD2+C`, `LL-FD4+S+C`, `EL+X`

---

## Part 2: Three-Pivot Patterns (UP-DOWN-UP)

Pattern: **L₀ → H₁ → L₂ → H₃** (up-leg, down-leg, up-leg)

### 9 Exhaustive Variants

Two independent dimensions × 3 values each = **3×3 = 9 mutually exclusive, collectively exhaustive variants**.

**Dimension 1** — L₂ vs L₀: {HL, EL, LL}
**Dimension 2** — H₃ vs H₁: {HH, EH, LH}

| #   | L₂ vs L₀ | H₃ vs H₁ | Name                        | Market Regime           |
| --- | -------- | -------- | --------------------------- | ----------------------- |
| 1   | HL       | HH       | **Continuation impulse**    | Bull trend continuation |
| 2   | HL       | EH       | **Double-top test**         | Range, bullish bias     |
| 3   | HL       | LH       | **Triangle compression**    | Neutral consolidation   |
| 4   | EL       | HH       | **Range break up**          | Bullish transition      |
| 5   | EL       | EH       | **Rectangle**               | Balanced range          |
| 6   | EL       | LH       | **Lower-high at flat base** | Range, bearish bias     |
| 7   | LL       | HH       | **V-reversal / spring**     | Bullish reversal        |
| 8   | LL       | EH       | **Undercut then stall**     | Volatile range          |
| 9   | LL       | LH       | **Rally failure**           | Bear trend continuation |

### Exhaustiveness Proof

All variants satisfy these mandatory constraints:

- L₀ < H₁ (first uptrend exists)
- L₂ < H₁ (retracement doesn't exceed peak)
- H₃ > L₂ (second uptrend exists)

L₂ has exactly 3 relationships to L₀ (higher, equal, lower). H₃ has exactly 3 relationships to H₁ (higher, equal, lower). These dimensions are independent — no constraint eliminates any combination. Therefore 3 × 3 = 9 variants, all feasible, none missing.

### Natural Groupings

- **Bullish** (4): HL+HH, EL+HH, HL+EH, LL+HH
- **Neutral** (3): HL+LH, EL+EH, LL+EH
- **Bearish** (2): EL+LH, LL+LH

### Regime Assignments

| Regime              | Variants                   |
| ------------------- | -------------------------- |
| Trend Continuation  | HL+HH (bull), LL+LH (bear) |
| Range Consolidation | HL+LH, EL+EH, LL+EH        |
| Bullish Transition  | EL+HH, HL+EH               |
| Bearish Transition  | EL+LH                      |
| Reversal            | LL+HH                      |

---

## Part 3: 27-Way Extension

Adding **H₃ vs L₀** as a third independent dimension:

- **L₂ vs L₀**: {HL, EL, LL}
- **H₃ vs H₁**: {HH, EH, LH}
- **H₃ vs L₀**: {Above, Equal, Below}

This yields 3×3×3 = **27 sub-variants**. Some are mathematically impossible due to constraints (e.g., HL+LH+H₃<L₀ requires H₃ < L₀ < L₂ < H₃, a contradiction).

Analysts often simplify this third dimension to a binary: "reclaims L₀" vs "fails to reclaim L₀".

---

## The Epsilon Tolerance Band

The tolerance band ε determines what "equal" means. It adapts to volatility and microstructure.

### Core Formula

```
ε = min(ε_max, max(ε_min, √[(a·S)² + (b·ATR₁₄)²]))
```

Where:

- **S** = rolling median spread (bid-ask)
- **ATR₁₄** = 14-bar Average True Range
- **a** = 2.0 (spread scaling)
- **b** = 0.05 (M5-M30) or 0.07 (H1-D1)

### Bounds (EURUSD defaults)

```
ε_min = max(3 ticks, 1×S) = max(0.00003, S)
ε_max = min(5 pips, 0.20 × swing) = min(0.00050, 0.20 × W)
```

### Classification Using ε

```
ε_r = ε / W  (relative tolerance)

EL if |z| ≤ ε_r
HL if z > ε_r
LL if z < −ε_r
```

### Practical Fallbacks

If bid-ask spread unavailable:

- **ATR-only**: ε = 0.05 × ATR₁₄ (M5-M30), 0.07 × ATR₁₄ (H1-D1)
- **Fixed band**: ε = 3 pips (intraday), 5 pips (swing), 10 pips (daily)

For complete worked examples with sensitivity analysis, read `references/epsilon-tolerance-detail.md`.

---

## Freedman-Diaconis Binning

The FD rule computes statistically optimal bin edges from data:

```
h = 2 × IQR(X) × n^(-1/3)    (bin width)
K = clip(⌈(max−min) / h⌉, 3, 6)  (number of bins)
edges = linspace(min, max, K+1)
```

### Procedure for HL Patterns

1. Collect 2-3 years of UP-DOWN triplets
2. Filter to HL (z > ε_r)
3. Winsorize z at 0.5%-99.5%
4. Compute FD bin edges on z ∈ (ε_r, 1)
5. Label: HL-FD1 (shallowest) through HL-FDK (deepest)

### Procedure for LL Patterns

1. Filter to LL (z < −ε_r)
2. Compute o = (L₀ − L₂) / ATR₁₄
3. Winsorize o at 0.5%-99.5%
4. Compute FD bin edges on o ∈ (ε_r, ∞)
5. Label: LL-FD1 (micro) through LL-FDK (extreme)

Recompute bin edges monthly or quarterly to track regime drift. Fall back to quantile binning if sample < 400.

---

## Implementation Reference

The `qta` Rust crate (`crates/qta/`) implements the core ZigZag state machine that produces the pivots consumed by this classification framework:

- `ZigZagConfig::new(reversal_depth, epsilon_multiplier, bar_threshold_dbps)`
- `ZigZagState::process_bar(&bar) → ZigZagOutput` with `completed_segment` containing `base_class` (EL/HL/LL) and `z` score
- The crate computes τ and ε dynamically per pivot from `bar_threshold_dbps`

The classification framework in this skill extends the crate's output with FD-binning, three-pivot analysis, and market regime labeling.

---

## Deep Reference Files

For ASCII visualizations, worked examples, and implementation pseudocode, read these reference files as needed:

| File                                        | Contents                                                                          |
| ------------------------------------------- | --------------------------------------------------------------------------------- |
| `references/notation-definitions.md`        | Single source of truth: all symbols, formulas, abbreviations, pattern classes     |
| `references/two-pivot-variants.md`          | All 9 two-pivot ASCII diagrams, trading rules, flag examples                      |
| `references/three-pivot-variants.md`        | All 9 three-pivot ASCII diagrams, 27-way extension, HL+LH granular sub-variants   |
| `references/epsilon-tolerance-detail.md`    | Complete ε formula, worked calculation, sensitivity analysis, pseudocode          |
| `references/binning-methodology.md`         | Freedman-Diaconis algorithm details, FD vs quantile comparison, worked example    |
| `references/data-pipeline.md`               | 11-step end-to-end pipeline: raw quotes → OHLC → ATR → pivots → classify → output |
| `references/eurusd-validation-scenarios.md` | 3 worked market scenarios (Normal, Volatile, Crash) validating ε and τ            |


## Post-Execution Reflection

After this skill completes, check before closing:

1. **Did the command succeed?** — If not, fix the instruction or error table that caused the failure.
2. **Did parameters or output change?** — If the underlying tool's interface drifted, update Usage examples and Parameters table to match.
3. **Was a workaround needed?** — If you had to improvise (different flags, extra steps), update this SKILL.md so the next invocation doesn't need the same workaround.

Only update if the issue is real and reproducible — not speculative.
