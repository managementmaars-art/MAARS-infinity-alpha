# Notation & Definitions: Single Source of Truth

**Master reference document** for all symbols, abbreviations, and key terms used throughout the ZigZag research documentation.

All other documents **cross-reference this file** instead of duplicating definitions.

---

## Pivot Notation

| Symbol                     | Definition                           | Units    | Example              |
| -------------------------- | ------------------------------------ | -------- | -------------------- |
| **L₀**                     | Initial low (first confirmed pivot)  | price    | 1.0800               |
| **H₁**                     | Swing high (reversal peak)           | price    | 1.0850               |
| **L₂**                     | Second low (continuation swing)      | price    | 1.0810               |
| **H₃**                     | Second high (final pivot in 3-pivot) | price    | 1.0870               |
| **t_L₀, t_H₁, t_L₂, t_H₃** | Timestamp of pivot                   | datetime | 2025-10-22 10:00 UTC |
| **W**                      | Swing magnitude (H₁ − L₀)            | price    | 0.0050               |

---

## Price Level Relationships

### Pivot Comparisons

| Notation | Definition           | Example           |
| -------- | -------------------- | ----------------- |
| **HL**   | Higher Low: L₂ > L₀  | 1.0810 > 1.0800 ✓ |
| **EL**   | Equal Low: L₂ ≈ L₀   | 1.0800 ± ε        |
| **LL**   | Lower Low: L₂ < L₀   | 1.0795 < 1.0800 ✓ |
| **HH**   | Higher High: H₃ > H₁ | 1.0870 > 1.0850 ✓ |
| **EH**   | Equal High: H₃ ≈ H₁  | 1.0850 ± ε        |
| **LH**   | Lower High: H₃ < H₁  | 1.0840 < 1.0850 ✓ |

---

## Key Formulas

### Normalized Retracement Coordinate

```
z = (L₂ - L₀) / (H₁ - L₀)  ∈ [−∞, +∞]
```

**Interpretation**:

- **z = 1.0**: L₂ equals H₁ (rare)
- **z = 0.5**: L₂ retraces 50% of swing (Fibonacci level)
- **z = 0.0**: L₂ equals L₀ (edge case)
- **z < 0**: L₂ below L₀ (undershoots) — signals LL class

**Usage**:

- Compare patterns across different swing sizes (scale-invariant)
- Input to Freedman–Diaconis binning
- Basis for EL/HL/LL classification

---

### Volatility-Normalized Overshoot

```
o = −z / ATR₁₄ = (L₀ − L₂) / ATR₁₄  ∈ [0, +∞)
```

**Interpretation**:

- **o = 0.1**: Undershoot = 10% of ATR (micro undercut, bounce likely)
- **o = 0.5**: Undershoot = 50% of ATR (moderate panic)
- **o = 1.0**: Undershoot = full ATR (deep reversal)
- **o > 2.0**: Undershoot > 200% ATR (extreme tail event, crash)

**Usage**:

- Quantify "surprise" relative to recent volatility
- Identify tail-risk undercuts
- Input to FD binning for LL sub-classification

---

### Tolerance Band (ε)

See **[epsilon-tolerance.md](epsilon-tolerance.md)** for complete specification.

**Core formula**:

```
ε = min(ε_max, max(ε_min, √[(a·S)² + (b·ATR₁₄)²]))
```

**Components**:

- **S**: Rolling median spread (bid–ask), price units
- **ATR₁₄**: 14-bar Average True Range, price units
- **a**: Spread scaling (default: 2.0)
- **b**: ATR scaling (default: 0.05 for M5–M30, 0.07 for H1–D1)

**Bounds** (EURUSD):

- **ε_min** = max(3 ticks = 0.00003, 1×S)
- **ε_max** = min(5 pips = 0.00050, 0.2×W)

**Relative tolerance**:

```
ε_r = ε / W
```

**Use**: Classify EL if |L₂ − L₀| ≤ ε; else HL or LL

---

### Relative Tolerance (ε_r)

```
ε_r = ε / (H₁ − L₀)  ∈ [0, 1]
```

**Interpretation**:

- **ε_r = 0.01**: "Equal" means within 1% of swing (tight tolerance)
- **ε_r = 0.10**: "Equal" means within 10% of swing (loose tolerance)

**Use**: Classification threshold

- EL if |z| ≤ ε_r
- HL if z > ε_r
- LL if z < −ε_r

---

### ZigZag Reversal Threshold (τ)

**Purpose**: Minimum price reversal magnitude required to confirm a ZigZag pivot. Adapts dynamically to market conditions (volatility and microstructure).

**Dynamic formula**:

```
τ = min(τ_max, max(τ_min, c_S × S, c_A × ATR₁₄))
```

**Components**:

- **S**: Rolling median spread (bid–ask), price units
- **ATR₁₄**: 14-bar Average True Range, price units
- **c_S**: Spread scaling constant = 3
- **c_A**: ATR scaling constant (timeframe-dependent)

**Constants** (EURUSD):

- **c_S** = 3 (spread scaling – 3× microstructure noise as baseline)
- **c_A** = 0.9 (intraday: M5–M30), 1.1 (H1 and higher: H1–D1)
- **τ_min** = 0.00030 (3 pips, absolute minimum reversal size)
- **τ_max** = min(0.0030, 0.35 × swing)
  - Hard cap: 0.0030 (30 pips maximum)
  - Swing cap: 35% of current swing magnitude (prevents over-aggressive thresholds on small swings)
  - Use whichever is smaller

**Interpretation**:

- **τ = 6 pips**: Pivot confirmed when price reverses ≥6 pips from current extreme
- **τ = 8 pips**: (higher volatility or wider spreads)
- **τ = 3 pips**: (tight market, low volatility)

**Use**: Confirm pivot when price reverses by ≥τ from leg extreme

**For implementation details and pseudocode**, see [data-pipeline.md § Step [4]](data-pipeline.md#4-determine-zigzag-thresholds).

### Worked Example: Computing τ for H1 EURUSD

**Scenario**: 2025-10-22 11:30 UTC, EURUSD H1, building uptrend

**Input Data:**

- Median spread S = 0.2 pips (1.5 ticks) = 0.00015 price units
- ATR₁₄ = 60 pips (0.00060 price units) over past 14 bars
- Current swing = H-L = 0.0055 (55 pips) – used for τ_max cap
- Timeframe: H1 (intraday H1, so c_A = 1.1)

**Calculation:**

```
Step 1: Compute baseline threshold
τ_base = max(c_S × S, c_A × ATR₁₄)
       = max(3 × 0.00015, 1.1 × 0.00060)
       = max(0.00045, 0.00066)
       = 0.00066 (6.6 pips)

Step 2: Apply bounds
τ_swing_cap = 0.35 × swing = 0.35 × 0.0055 = 0.001925
τ_hard_cap = 0.0030
τ_max = min(0.0030, 0.001925) = 0.001925

τ_min = 0.00030
τ = min(τ_max, max(τ_min, τ_base))
  = min(0.001925, max(0.00030, 0.00066))
  = min(0.001925, 0.00066)
  = 0.00066 (6.6 pips)
```

**Interpretation:**

- **Pivot confirmation threshold**: Price must reverse ≥6.6 pips from current extreme
- **If in uptrend**: Running high H = 1.0900. If price drops to 1.0893 or below, pivot confirmed
- **If in downtrend**: Running low L = 1.0850. If price rises to 1.0856 or above, pivot confirmed

**Comparison with ε (tolerance band)**:

- τ ≈ 6.6 pips (reversal threshold for pivot confirmation)
- ε ≈ 4.5 pips (tolerance for "equal" level classification)
- **Relationship**: τ > ε in this scenario. τ is stricter for pivot detection; ε is looser for classification.

**Sensitivity:**

- If ATR₁₄ doubles to 120 pips: τ_base = max(0.00045, 1.1 × 0.0012) = 0.00132 (13.2 pips)
- If spreads widen to 1 pip: τ_base = max(3 × 0.0001, 1.1 × 0.0006) = 0.00066 (unchanged)
- If swing shrinks to 20 pips: τ_swing_cap = 0.35 × 0.002 = 0.0007 (7 pips), τ = 0.0007

---

## Pattern Classes

### Base Classes (3 mutually exclusive)

| Class  | Condition   | Interpretation                  | Probability |
| ------ | ----------- | ------------------------------- | ----------- |
| **EL** | \|z\| ≤ ε_r | Equal Low — retest of L₀        | ~20–30%     |
| **HL** | z > ε_r     | Higher Low — pullback, no break | ~50–60%     |
| **LL** | z < −ε_r    | Lower Low — undercut below L₀   | ~10–20%     |

---

### FD-Binned Variants (9 total: UP–DOWN)

See **[variants-updown.md](variants-updown.md)** for detailed classification and market regimes.

#### EL Variants

- **EL**: Equal Low (no binning, single class)

#### HL Variants (4 bins, shallow → deep)

- **HL-FD1**: Shallow retrace (0.75 < z < 1.0) — minimal pullback
- **HL-FD2**: Mid-upper retrace (0.50 < z ≤ 0.75) — Fibonacci 38.2% / 50%
- **HL-FD3**: Mid-lower retrace (0.25 < z ≤ 0.50) — Fibonacci 61.8%
- **HL-FD4**: Deep retrace (0 < z ≤ 0.25) — nearly complete retest

#### LL Variants (4 bins, micro → extreme)

- **LL-FD1**: Micro undercut (o ≤ q₂₀) — brief spillover
- **LL-FD2**: Shallow undercut (q₂₀ < o ≤ q₄₀) — moderate panic
- **LL-FD3**: Deep undercut (q₄₀ < o ≤ q₆₀) — structural breakdown
- **LL-FD4**: Extreme undercut (o > q₆₀) — tail-risk crash

---

## Supplementary Flags

Optional flags attach to any variant for richer classification:

| Flag   | Meaning                         | Signal                                |
| ------ | ------------------------------- | ------------------------------------- |
| **+C** | Close below L₀ between H₁→L₂    | Stronger bearish conviction           |
| **+S** | L₂ occurs in single bar (spike) | Sharp reversal; mean reversion likely |
| **+X** | High wicks below L₀, no close   | Liquidity grab; false break setup     |

**Example labels**: `HL-FD2+C`, `LL-FD4+S+C`, `EL+X`

### Flag Combination Examples

**Example 1: HL-FD2+C — Mid-upper Retrace with Close Below Support**

```
Variant: HL-FD2  (L₂ retraces 50–75% of swing; bullish pullback expected)
Flag +C:  Close bar ends BELOW L₀ (between H₁→L₂)
Combined: HL-FD2+C

Interpretation:
- Base regime (HL-FD2): Shallow pullback; likely bounce
- +C modifier: Close below L₀ indicates commitment to bearish; weakens bullish bias
- Signal: Still a pullback pattern but with more downside risk. Caution on longs until bounce confirmed.
- Trade: Enter long near L₂ but tighten stop below recent wick. Consider waiting for close above L₀.
```

**Example 2: LL-FD1+S+C — Micro Undercut with Spike and Close Below**

```
Variant: LL-FD1  (L₂ < L₀ by < 0.5 ATR; brief spillover, micro-crash)
Flag +S:  L₂ occurs in single bar (sharp reversal spike)
Flag +C:  Close bar ends BELOW L₀ (confirming bearish intent)
Combined: LL-FD1+S+C

Interpretation:
- Base regime (LL-FD1): Reversal likely; mean reversion bounce expected
- +S modifier: Sharp single-bar action; price "wicked" quickly; high conviction reversal
- +C modifier: Close below L₀ = confirmed break, not just a wick
- Signal: High-conviction short signal. Price broke support cleanly on single bar. Expect sharp bounce OR continued breakdown.
- Trade: If bounce occurs, enter long after close crosses back above L₀. Probability of bounce = 70%+ given micro nature.
```

**Example 3: EL+X — Equal Low with Liquidity Grab (False Break)**

```
Variant: EL      (L₂ ≈ L₀ within ε; retest of support)
Flag +X:  High wicks below L₀ but close remains above L₀ (no close below)
Combined: EL+X

Interpretation:
- Base regime (EL): Retest of support; equilibrium pattern; slight bullish
- +X modifier: Wicks probe below L₀ but fail to close there (liquidation trap / false break)
- Signal: Liquidity grab. Shorts get stopped out by wick. Close above L₀ shows buyers returning.
- Trade: False break setup. Enter long on close above L₀. Stop loss just below wick low. Probability of upside breakout = 65%+
```

**Example 4: HL-FD4+S — Deep Retrace with Spike (Volatile Consolidation)**

```
Variant: HL-FD4  (L₂ retraces 0–25% of swing; nearly complete retest)
Flag +S:  L₂ occurs in single bar spike
Combined: HL-FD4+S

Interpretation:
- Base regime (HL-FD4): Deep retrace; pullback has burned support; uncertain continuation
- +S modifier: Occurred via sharp spike; rapid reversal execution
- Signal: Deep retest on sharp spike = high conviction selling followed by equally sharp buying. Volatile consolidation zone.
- Trade: Caution. Pullback is deep AND volatile. Wait for second bar confirmation before entry. If close above pivot, long is favored.
```

---

## Market Regimes

See **[variants-updown.md](variants-updown.md#market-regime-mapping)** for trading implications per variant.

| Regime       | Variants     | Characteristics           | Entry Signal                                   |
| ------------ | ------------ | ------------------------- | ---------------------------------------------- |
| **Retest**   | EL           | Lows re-establish support | Long from L₀+ε                                 |
| **Pullback** | HL-FD1/2/3/4 | Retracement without break | Long from L₂ (varies by depth)                 |
| **Undercut** | LL-FD1/2/3/4 | Break below support       | Short trade (micro) or reversal wait (extreme) |

---

## Microstructure Terms

| Term           | Definition                        | Units | Use                                 |
| -------------- | --------------------------------- | ----- | ----------------------------------- |
| **Spread (S)** | best-ask − best-bid               | price | Liquidity quality; noise floor      |
| **ATR₁₄**      | 14-bar Average True Range         | price | Volatility proxy; scales thresholds |
| **Tick**       | Smallest price unit               | price | EURUSD = 0.00001                    |
| **Pip**        | 10 ticks (standard reporting)     | price | EURUSD = 0.00010                    |
| **Repainting** | Pivot changes as new data arrives | flag  | **Excluded** from analysis          |

---

## Abbreviations

| Abbreviation | Full Form                          |
| ------------ | ---------------------------------- |
| **OHLC**     | Open, High, Low, Close             |
| **ATR**      | Average True Range                 |
| **FD**       | Freedman–Diaconis (binning method) |
| **IQR**      | Interquartile Range                |
| **ε**        | Epsilon (tolerance band)           |
| **τ**        | Tau (ZigZag threshold)             |
| **EL**       | Equal Low                          |
| **HL**       | Higher Low                         |
| **LL**       | Lower Low                          |
| **HH**       | Higher High                        |
| **EH**       | Equal High                         |
| **LH**       | Lower High                         |
| **DRY**      | Don't Repeat Yourself (principle)  |
| **UTC**      | Coordinated Universal Time         |

---

## Related Documents

**Implementation & Methodology**:

- **[epsilon-tolerance.md](epsilon-tolerance.md)** — Complete ε formula, EURUSD defaults, examples
- **[binning-methodology.md](binning-methodology.md)** — FD binning algorithm, worked example
- **[data-pipeline.md](data-pipeline.md)** — 11-step pipeline using all above terms

**Pattern Analysis**:

- **[variants-updownup.md](variants-updownup.md)** — 9 three-pivot patterns (L₀→H₁→L₂→H₃)
- **[variants-updown.md](variants-updown.md)** — Granular two-pivot patterns with FD bins

**Development History**:

- **[conversation.md](conversation.md)** — Full 13-part Q&A developing the framework
- **[README.md](README.md)** — Navigation guide and use cases

---

## Document Version

| Date       | Update                                                            |
| ---------- | ----------------------------------------------------------------- |
| 2025-10-22 | Created as single source of truth; replaces scattered definitions |

---

**All notation in this document is normative. Other files reference this document instead of redefining terms.**
