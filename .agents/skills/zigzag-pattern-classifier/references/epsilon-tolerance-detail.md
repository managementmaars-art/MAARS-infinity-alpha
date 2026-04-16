# Epsilon Tolerance Band: "Equal" Price Level Definition

Complete specification for computing the tolerance band ε used to classify "equal" pivot levels (EL/EH) in ZigZag pattern analysis.

## Motivation

**Problem**: When are two price levels "equal"?

- Absolute difference (e.g., 1 pip) is scale-dependent and brittle.
- Relative percentage is noisy on small swings.
- **Solution**: Use a **volatility- and microstructure-aware band** that scales to both market conditions and instrument characteristics.

## Core Formula

```
ε = min(ε_max, max(ε_min, √[(a·S)² + (b·ATR₁₄)²]))
```

### Components

| Symbol    | Meaning                         | Units         | Notes                           |
| --------- | ------------------------------- | ------------- | ------------------------------- |
| **S**     | Rolling median spread (bid–ask) | price         | Microstructure noise            |
| **ATR₁₄** | 14-bar Average True Range       | price         | Volatility proxy                |
| **a**     | Spread scaling constant         | dimensionless | Typically 2.0                   |
| **b**     | ATR scaling constant            | dimensionless | Timeframe-dependent; 0.05–0.07  |
| **ε_min** | Floor (minimum tolerance)       | price         | Prevents collapsing below noise |
| **ε_max** | Ceiling (maximum tolerance)     | price         | Prevents absorbing trend moves  |

## Default Parameters for EURUSD

### Constants

- **Tick**: 0.00001 (smallest price unit)
- **Pip**: 0.00010 (10 ticks; standard reporting unit)
- **a**: 2.0 (universal)

### Timeframe-Dependent Coefficients

| Timeframe  | b    | Rationale                        |
| ---------- | ---- | -------------------------------- |
| **M5–M30** | 0.05 | Tighter bands; less volatile     |
| **H1–H4**  | 0.07 | Moderate volatility; wider bands |
| **D1**     | 0.07 | Daily swings; comparable to H4   |

### Bounds

```
ε_min = max(3 ticks, 1 × S)
       = max(0.00003, S)

ε_max = min(0.00050, 0.20 × swing)
       = min(5 pips, 20% of swing magnitude)
```

Where **swing** = |H₁ - L₀| (for high-low classification) or |H₃ - L₂| (for other legs).

## Computation Procedure

### Step 1: Collect Spreads

At each pivot time (t_L₀, t_H₁, t_L₂):

- Extract best-ask − best-bid for that bar.
- Compute rolling median over ±k bars (k=3–5).
- Take median of the three pivot spreads: S = median(S_L₀, S_H₁, S_L₂).

```python
S_L0 = rolling_median(ask - bid, at t_L0, window=3)
S_H1 = rolling_median(ask - bid, at t_H1, window=3)
S_L2 = rolling_median(ask - bid, at t_L2, window=3)
S = median([S_L0, S_H1, S_L2])
```

### Step 2: Compute ATR₁₄

On the same timeframe as ZigZag (e.g., H1), calculate standard 14-bar ATR:

```python
ATR14 = atr(high, low, close, period=14)
```

Use the ATR value at H₁ time (or average of H₁ and L₂ if more recent).

### Step 3: Calculate ε

Apply the formula:

```python
variance = (a * S)**2 + (b * ATR14)**2
epsilon_raw = sqrt(variance)
epsilon = clip(epsilon_raw, ε_min, ε_max)
```

### Step 4: Compute Relative Tolerance

For binning, convert to relative units:

```python
swing = H1 - L0  (or H3 - L2 for other pivots)
epsilon_r = epsilon / swing
```

Use ε_r to classify pivots:

- **EL**: |L₂ - L₀| ≤ ε
- **HL**: (L₂ - L₀) > ε
- **LL**: (L₀ - L₂) > ε

---

## Example Calculation

### Scenario: H1 EURUSD, 2025-10-22 11:00 UTC

**Input Data:**

- L₀ = 1.0800 (high of prior swing)
- H₁ = 1.0850 (peak at 10:00)
- L₂ = 1.0810 (low at 11:00)
- Swing W = 1.0850 - 1.0800 = 0.0050 (50 pips)

**Spreads (bid–ask):**

- S_L0 (at 9:55–10:05) = median(0.0003, 0.0002, 0.0003) = 0.0003
- S_H1 (at 09:55–10:05) = median(0.0002, 0.0002, 0.0002) = 0.0002
- S_L2 (at 10:55–11:05) = median(0.0004, 0.0003, 0.0004) = 0.0004
- **S = median(0.0003, 0.0002, 0.0004) = 0.0003**

**Volatility:**

- **ATR₁₄** (H1, at 11:00) = 0.0065 (65 pips over 14 bars)

**Tolerance Calculation:**

```
ε = √[(2.0 × 0.0003)² + (0.07 × 0.0065)²]
  = √[(0.0006)² + (0.000455)²]
  = √[3.6e-7 + 2.07e-7]
  = √[5.67e-7]
  ≈ 0.000753 pips ≈ 0.75 basis points ≈ 7.53 pips
```

**Bounds Check:**

```
ε_min = max(3 ticks, 0.0003) = max(0.00003, 0.0003) = 0.0003
ε_max = min(5 pips, 20% × 50 pips) = min(0.0005, 0.001) = 0.0005

ε_bounded = clip(0.000753, 0.0003, 0.0005) = 0.0005 (exceeds cap)
```

**Final ε = 0.0005 (5 pips)**

**Classification:**

```
|L2 - L0| = |1.0810 - 1.0800| = 0.0010 (10 pips)
Is 0.0010 ≤ 0.0005?  No.
Therefore: HL (Higher Low) — L2 is distinctly higher than L0.
```

**Relative Tolerance:**

```
ε_r = 0.0005 / 0.005 = 0.1 (10% of swing)
```

---

## Sensitivity Analysis

### What If Volatility Spikes?

If ATR₁₄ doubles to 0.013 (during news):

```
ε = √[(2.0 × 0.0003)² + (0.07 × 0.013)²]
  = √[3.6e-7 + 8.28e-7]
  = √[1.188e-6]
  ≈ 0.00109 (11 pips)

Bounded: ε = 0.0005 (capped at ε_max)
```

**Effect**: Tolerance stays at ceiling; prevents wild swings from collapsing to near-zero.

### What If Spreads Widen?

If S triples to 0.0009 (thin liquidity):

```
ε = √[(2.0 × 0.0009)² + (0.07 × 0.0065)²]
  = √[3.24e-6 + 2.07e-7]
  = √[3.447e-6]
  ≈ 0.00186 (18.6 pips)

Bounded: ε = 0.0005 (capped at ε_max)
```

**Effect**: Wider spreads increase noise; tolerance grows but is capped.

### What If Swing is Tiny?

If W = 10 pips instead of 50:

```
ε_max = min(5 pips, 20% × 10 pips) = min(0.0005, 0.002) = 0.0005 ✓
```

**Effect**: Cap still applies; ε_max prevents "equal" from absorbing 50% of micro-moves.

---

## Practical Fallbacks

### If you lack real-time bid/ask (S unavailable):

**Fallback 1: ATR-only (less accurate but workable)**

```
ε = 0.05 × ATR14  (M5–M30)
ε = 0.07 × ATR14  (H1–D1)
```

**Fallback 2: Fixed band (simplest, least ideal)**

```
ε = 3 pips (intraday, M5–M30)
ε = 5 pips (swing, H1–D1)
ε = 10 pips (daily, D1+)
```

These are crude but often sufficient for rough classification.

---

## Validation

To verify your ε formula is reasonable:

1. **Sanity check**: ε should be 3–10 pips for EURUSD on normal market days.
2. **Stability**: ε should not swing wildly between bars (use rolling median of S, not instant).
3. **Regime test**:
   - Calm day (ATR ≈ 50 pips): ε ≈ 3–5 pips.
   - Volatile day (ATR ≈ 100 pips): ε ≈ 5–10 pips.
   - Crisis day (ATR ≈ 200 pips): ε ≈ ε_max (capped).

---

## Implementation Pseudocode

```python
def compute_epsilon(L0, H1, L2, S_L0, S_H1, S_L2, ATR14, b=0.05):
    """
    Compute tolerance band ε for classification.

    Args:
        L0, H1, L2: Pivot prices
        S_L0, S_H1, S_L2: Spreads at pivot times
        ATR14: 14-bar ATR value at H1 time
        b: Timeframe constant (0.05 for M5-M30, 0.07 for H1 and higher)

    Returns:
        epsilon: Tolerance band (price units)
        epsilon_r: Relative tolerance (fraction of swing)
    """

    # Step 1: Aggregate spread
    S = median([S_L0, S_H1, S_L2])

    # Step 2: Compute raw tolerance
    a = 2.0
    variance = (a * S)**2 + (b * ATR14)**2
    epsilon_raw = sqrt(variance)

    # Step 3: Apply bounds
    swing = H1 - L0
    epsilon_min = max(0.00003, S)  # 3 ticks or 1x spread
    epsilon_max = min(0.00050, 0.20 * swing)  # 5 pips or 20% swing

    epsilon = clip(epsilon_raw, epsilon_min, epsilon_max)

    # Step 4: Relative tolerance
    if swing > 0:
        epsilon_r = epsilon / swing
    else:
        epsilon_r = 0.01  # Safe default if swing is near zero

    return epsilon, epsilon_r


def classify_low(L0, L2, epsilon):
    """Classify L2 relative to L0."""
    diff = abs(L2 - L0)
    if diff <= epsilon:
        return 'EL'  # Equal Low
    elif L2 > L0:
        return 'HL'  # Higher Low
    else:
        return 'LL'  # Lower Low
```

---

## References

- **ATR Calculation**: Wilder, J.W. (1978). New Concepts in Technical Trading Systems.
- **Volatility Scaling**: Standard practice in options pricing (similar to volatility cones).
- **Microstructure**: Bid–ask spread models in high-frequency trading literature.

---

**Last Updated**: 2025-10-22
**Context**: EURUSD; no volume data assumed; OHLC high/low used for ZigZag extremes.
