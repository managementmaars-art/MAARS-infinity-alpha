# Data Pipeline: End-to-End ZigZag Classification System

Complete specification of the data pipeline from rolling historical EURUSD quotes to ZigZag-derived regime labels and pattern classifications.

## Pipeline Overview

```
Raw Quotes (bid/ask)
        ↓
[1] Clean & Align
        ↓
[2] Build OHLC & Compute Spreads
        ↓
[3] Compute Volatility (ATR) & Noise Stats
        ↓
[4] Determine ZigZag Thresholds (τ)
        ↓
[5] Detect ZigZag Pivots
        ↓
[6] Form UP–DOWN Triplets
        ↓
[7] Compute Tolerance Band (ε)
        ↓
[8] Classify: EL / HL / LL (base classes)
        ↓
[9] Compute FD Bin Edges (rolling window)
        ↓
[10] Assign FD-Binned Variant Labels
         ↓
[11] Output: Labeled Segments + Features
```

---

## Detailed Pipeline Steps

### [1] Clean & Align Quotes

**Input**: Raw bid/ask time series with timestamps (microsecond precision preferred).

**Operations**:

- Drop records with NaN, Inf, or missing values.
- Remove crossed quotes (ask < bid).
- De-duplicate timestamps; keep first occurrence.
- Forward-fill micro gaps (≤500 ms) if needed.
- Verify no large timestamp jumps (detect session breaks).

**Output**: Clean, aligned quote stream `{t, bid_t, ask_t}`.

```python
def clean_quotes(quotes_df):
    """Remove bad ticks, align timestamps."""
    df = quotes_df.dropna()
    df = df[df['ask'] >= df['bid']]
    df = df.drop_duplicates(subset=['timestamp'], keep='first')
    df['mid'] = (df['bid'] + df['ask']) / 2
    df['spread'] = df['ask'] - df['bid']
    return df.sort_values('timestamp')
```

---

### [2] Build OHLC & Compute Spreads

**Input**: Clean quote stream.

**Operations**:

- Resample quotes to target timeframes (M5, M15, M30, H1, H4, D1).
- For each bar:
  - **High** = max(ask) over bar
  - **Low** = min(bid) over bar
  - **Open/Close** = first/last mid price
  - **Volume** = tick count (if available)
  - **Spread** = median(spread) over bar

**Output**: OHLCV with spread per timeframe.

```python
def build_ohlc(quotes_df, timeframe='H1'):
    """Resample quotes to OHLC bars."""
    quotes_df['time'] = quotes_df['timestamp'].dt.floor(timeframe)
    ohlc = quotes_df.groupby('time').agg({
        'ask': 'max',  # High
        'bid': 'min',  # Low
        'mid': ['first', 'last'],  # Open, Close
        'spread': 'median'
    })
    ohlc.columns = ['high', 'low', 'open', 'close', 'spread']
    return ohlc
```

---

### [3] Compute Volatility & Noise Stats

**Input**: OHLC bars per timeframe.

**Operations**:

- Calculate **ATR₁₄** (14-bar Average True Range).
- Calculate **rolling median spread** over ±k bars (k=3–5).
- Identify **swing filter threshold**: keep only swings Δ ≥ 5×S.

**Output**: ATR, local spread, volatility-adjusted thresholds.

```python
def compute_volatility(ohlc):
    """Calculate ATR and rolling spread."""
    ohlc['tr'] = np.maximum(
        ohlc['high'] - ohlc['low'],
        np.maximum(
            abs(ohlc['high'] - ohlc['close'].shift()),
            abs(ohlc['low'] - ohlc['close'].shift())
        )
    )
    ohlc['atr14'] = ohlc['tr'].rolling(14).mean()
    ohlc['spread_rolling'] = ohlc['spread'].rolling(5, center=True).median()
    return ohlc
```

---

### [4] Determine ZigZag Thresholds

**Input**: ATR, rolling spreads, swing magnitudes.

**Operations**:
Calculate dynamic ZigZag reversal threshold τ:

```
τ = min(τ_max, max(τ_min, c_S × S, c_A × ATR₁₄))
```

**Constants** (EURUSD):

- c_S = 3 (spread scaling)
- c_A = 0.9 (intraday), 1.1 (H1 and higher)
- τ_min = 0.00030 (3 pips)
- τ_max = min(0.0030, 0.35 × swing)

**Output**: Dynamic threshold τ per bar.

```python
def compute_zigzag_threshold(atr14, spread_rolling, c_S=3, c_A=0.9):
    """Compute reversal threshold τ."""
    tau_base = np.maximum(c_S * spread_rolling, c_A * atr14)
    tau_min = 0.00030
    tau_max = 0.0030
    tau = np.clip(tau_base, tau_min, tau_max)
    return tau
```

---

### [5] Detect ZigZag Pivots

**Input**: OHLC highs/lows, threshold τ.

**Operations**:

- Initialize from first bar; track current leg (up/down).
- For each new bar:
  - If in **uptrend**: update running max H; if price reverses by ≥τ from H, confirm pivot.
  - If in **downtrend**: update running min L; if price reverses by ≥τ from L, confirm pivot.
- Confirm pivot only when **reversal is confirmed** (no repainting).

**Output**: Sequence of pivots `{t_i, p_i, type_i ∈ {L, H}}`.

```python
def detect_zigzag_pivots(ohlc, tau_col='tau'):
    """Identify ZigZag pivots (no repainting)."""
    pivots = []
    leg_type = 'UP'  # Start with UP
    leg_extreme = ohlc['high'].iloc[0]
    leg_extreme_idx = 0

    for i in range(1, len(ohlc)):
        if leg_type == 'UP':
            # Uptrend: track high
            if ohlc['high'].iloc[i] > leg_extreme:
                leg_extreme = ohlc['high'].iloc[i]
                leg_extreme_idx = i
            # Check for reversal
            elif leg_extreme - ohlc['low'].iloc[i] >= ohlc[tau_col].iloc[i]:
                pivots.append({'time': ohlc.index[leg_extreme_idx],
                              'price': leg_extreme, 'type': 'H'})
                leg_type = 'DOWN'
                leg_extreme = ohlc['low'].iloc[i]
                leg_extreme_idx = i
        else:
            # Downtrend: track low
            if ohlc['low'].iloc[i] < leg_extreme:
                leg_extreme = ohlc['low'].iloc[i]
                leg_extreme_idx = i
            # Check for reversal
            elif ohlc['high'].iloc[i] - leg_extreme >= ohlc[tau_col].iloc[i]:
                pivots.append({'time': ohlc.index[leg_extreme_idx],
                              'price': leg_extreme, 'type': 'L'})
                leg_type = 'UP'
                leg_extreme = ohlc['high'].iloc[i]
                leg_extreme_idx = i

    return pd.DataFrame(pivots)
```

---

### [6] Form UP–DOWN Triplets

**Input**: Pivot sequence from step [5].

**Operations**:

- Slide a 3-element window over pivots with pattern L-H-L.
- Extract features:
  - Prices: L₀, H₁, L₂
  - Times: t_L₀, t_H₁, t_L₂
  - Swing: W = H₁ − L₀
  - Spreads at pivots: S_L₀, S_H₁, S_L₂
  - ATR₁₄ at H₁ and L₂
  - Durations: t_up = t_H₁ − t_L₀, t_down = t_L₂ − t_H₁
  - Flags: C (close<L₀?), S (spike?)

**Output**: Triplet records with features.

```python
def form_triplets(pivots, ohlc_indexed):
    """Form L0-H1-L2 triplets."""
    triplets = []
    for i in range(len(pivots) - 2):
        if pivots['type'].iloc[i] == 'L' and \
           pivots['type'].iloc[i+1] == 'H' and \
           pivots['type'].iloc[i+2] == 'L':

            L0 = pivots['price'].iloc[i]
            H1 = pivots['price'].iloc[i+1]
            L2 = pivots['price'].iloc[i+2]
            t_L0 = pivots['time'].iloc[i]
            t_H1 = pivots['time'].iloc[i+1]
            t_L2 = pivots['time'].iloc[i+2]

            # Features
            W = H1 - L0
            t_up = (t_H1 - t_L0).total_seconds()
            t_down = (t_L2 - t_H1).total_seconds()

            # Spreads and ATR
            S_L0 = ohlc_indexed.loc[t_L0, 'spread_rolling']
            S_H1 = ohlc_indexed.loc[t_H1, 'spread_rolling']
            S_L2 = ohlc_indexed.loc[t_L2, 'spread_rolling']
            atr_H1 = ohlc_indexed.loc[t_H1, 'atr14']
            atr_L2 = ohlc_indexed.loc[t_L2, 'atr14']

            triplets.append({
                'segment_id': f"{t_L0.date()}-{i}",
                't_L0': t_L0, 't_H1': t_H1, 't_L2': t_L2,
                'L0': L0, 'H1': H1, 'L2': L2,
                'W': W, 't_up': t_up, 't_down': t_down,
                'S_L0': S_L0, 'S_H1': S_H1, 'S_L2': S_L2,
                'atr_H1': atr_H1, 'atr_L2': atr_L2
            })

    return pd.DataFrame(triplets)
```

---

### [7] Compute Tolerance Band (ε)

**Input**: Triplet features (spreads, ATR, swing).

**Operations**:
Apply ε formula per triplet.

**See [epsilon-tolerance.md](epsilon-tolerance.md) for complete formula specification, EURUSD defaults, and examples.**

**See [notation-definitions.md#tolerance-band-ε](notation-definitions.md#tolerance-band-ε) for quick reference.**

**Output**: ε and ε_r per triplet.

```python
def compute_epsilon(triplets, b=0.05):
    """Compute tolerance band."""
    S = triplets[['S_L0', 'S_H1', 'S_L2']].median(axis=1)
    atr = triplets['atr_H1']

    eps_raw = np.sqrt((2 * S)**2 + (b * atr)**2)

    eps_min = np.maximum(0.00003, S)
    eps_max = np.minimum(0.00050, 0.20 * triplets['W'])

    triplets['eps'] = np.clip(eps_raw, eps_min, eps_max)
    triplets['eps_r'] = triplets['eps'] / triplets['W']

    return triplets
```

---

### [8] Classify Base Classes (EL / HL / LL)

**Input**: Triplets with ε, ε_r.

**Operations**:
For each triplet, compute normalized coordinate:

```
z = (L₂ - L₀) / (H₁ - L₀)
```

See [`notation-definitions.md#normalized-retracement-coordinate`](notation-definitions.md#normalized-retracement-coordinate) for canonical definition.

Classify:

- **EL** if |z| ≤ ε_r
- **HL** if z > ε_r
- **LL** if z < −ε_r

**Output**: Base class label per triplet.

```python
def classify_base(triplets):
    """Classify EL / HL / LL."""
    z = (triplets['L2'] - triplets['L0']) / triplets['W']
    triplets['z'] = z

    triplets['base_class'] = 'UNDEFINED'
    triplets.loc[np.abs(z) <= triplets['eps_r'], 'base_class'] = 'EL'
    triplets.loc[z > triplets['eps_r'], 'base_class'] = 'HL'
    triplets.loc[z < -triplets['eps_r'], 'base_class'] = 'LL'

    return triplets
```

---

### [9] Compute FD Bin Edges (Rolling)

**Input**: Historical triplets with z values and base_class labels.

**Operations**:
Per timeframe, on rolling 2–3 year window:

1. Separate HL and LL populations:
   - Z_HL = {z_i : base_class_i = 'HL'}
   - Z_LL = {z_i : base_class_i = 'LL'}

2. For each population:
   - Winsorize at 0.5%–99.5%
   - Compute FD bin width h
   - Determine K ∈ [3, 6]
   - Create uniform edges

3. Store edges for scoring new triplets.

**Output**: Bin edge arrays `edges_hl`, `edges_ll` per timeframe.

**Implementation**: See [binning-methodology.md § Implementation Pseudocode](binning-methodology.md#implementation-pseudocode) for the complete `compute_fd_bins()` function with detailed documentation.

---

### [10] Assign FD-Binned Labels

**Input**: Triplets with z values; FD edges from step [9].

**Operations**:
For each triplet:

- If base_class = 'EL': label = 'EL'
- If base_class = 'HL': find bin index of z in edges_hl → label = f'HL-FD{k}'
- If base_class = 'LL':
  - Compute o = -z / ATR₁₄
  - Find bin index of o in edges_ll → label = f'LL-FD{j}'

Add optional flags:

- **+C** if any close < L₀ between H₁ → L₂
- **+S** if L₂ occurs in single bar (spike)

**Output**: FD-binned variant label per triplet.

```python
def assign_fd_labels(triplets, edges_hl, edges_ll):
    """Assign FD-binned variant labels."""
    labels = []

    for idx, row in triplets.iterrows():
        if row['base_class'] == 'EL':
            label = 'EL'
        elif row['base_class'] == 'HL':
            for k, (lo, hi) in enumerate(zip(edges_hl[:-1], edges_hl[1:])):
                if lo <= row['z'] <= hi:
                    label = f'HL-FD{k+1}'
                    break
        elif row['base_class'] == 'LL':
            o = -row['z']
            for j, (lo, hi) in enumerate(zip(edges_ll[:-1], edges_ll[1:])):
                if lo <= o <= hi:
                    label = f'LL-FD{j+1}'
                    break

        # Add flags
        if row.get('close_below_L0', False):
            label += '+C'
        if row.get('spike', False):
            label += '+S'

        labels.append(label)

    triplets['variant'] = labels
    return triplets
```

---

### [11] Output: Labeled Segments

**Input**: Triplets with all features, classes, variants.

**Operations**:

- Deduplicate segment_id
- Sort by time
- Add derived fields:
  - `regime` = regime label (Retest, Pullback, Undercut, ...)
  - `retrace_pct` = 1 − z (% of swing retraced)
  - `overshot_pct` = o × ATR₁₄ / W (% overshooting L₀)

**Output**: Segments table ready for analysis/backtest.

```python
def finalize_segments(triplets):
    """Finalize output table."""
    segments = triplets[[
        'segment_id', 't_L0', 't_H1', 't_L2',
        'L0', 'H1', 'L2', 'W',
        'S_L0', 'S_H1', 'S_L2', 'eps', 'eps_r',
        'z', 'atr_H1', 'atr_L2',
        't_up', 't_down',
        'base_class', 'variant'
    ]].copy()

    segments['retrace_pct'] = 1 - segments['z']
    segments['regime'] = segments['variant'].apply(infer_regime)

    return segments.sort_values('t_L0')


def infer_regime(variant_label):
    """Map variant to regime."""
    if 'EL' in variant_label:
        return 'Retest'
    elif 'HL' in variant_label:
        return 'Pullback'
    elif 'LL' in variant_label:
        return 'Undercut'
    else:
        return 'Unknown'
```

---

## Complete Pipeline Pseudocode

```python
def full_pipeline(quotes_df, timeframes=['M5', 'H1', 'D1'], lookback_years=3):
    """End-to-end ZigZag classification pipeline."""

    # Step 1: Clean
    quotes_clean = clean_quotes(quotes_df)

    results = []

    for tf in timeframes:
        # Step 2: Build OHLC
        ohlc = build_ohlc(quotes_clean, tf)

        # Step 3: Volatility
        ohlc = compute_volatility(ohlc)

        # Step 4: ZigZag threshold
        ohlc['tau'] = compute_zigzag_threshold(ohlc['atr14'], ohlc['spread_rolling'])

        # Step 5: Detect pivots
        pivots = detect_zigzag_pivots(ohlc)

        # Step 6: Form triplets
        triplets = form_triplets(pivots, ohlc)

        # Step 7: Tolerance band
        triplets = compute_epsilon(triplets)

        # Step 8: Base classification
        triplets = classify_base(triplets)

        # Step 9: FD bins (rolling window)
        # Note: compute_fd_bins() implementation in binning-methodology.md § Implementation Pseudocode
        z_hl = triplets[triplets['base_class'] == 'HL']['z'].values
        z_ll = -triplets[triplets['base_class'] == 'LL']['z'].values
        edges_hl, K_hl = compute_fd_bins(z_hl)
        edges_ll, K_ll = compute_fd_bins(z_ll)

        # Step 10: FD labels
        triplets = assign_fd_labels(triplets, edges_hl, edges_ll)

        # Step 11: Finalize
        segments = finalize_segments(triplets)
        segments['timeframe'] = tf

        results.append(segments)

    # Combine all timeframes
    all_segments = pd.concat(results, ignore_index=True)
    all_segments = all_segments.sort_values('t_L0')

    return all_segments
```

---

## Data Quality Checks

Before running pipeline, verify:

- [ ] Quotes cover at least 2–3 years
- [ ] No large gaps (>1 hour) in quote stream
- [ ] Bid ≤ Ask (no crossed quotes)
- [ ] Spread > 0 (no phantom liquidity)
- [ ] ATR₁₄ > 0 (adequate volatility data)
- [ ] Pivot count > 100 per triplet class (sufficient sample)

---

## Output Storage

Recommended database schema:

```sql
CREATE TABLE segments (
    segment_id VARCHAR(50) PRIMARY KEY,
    timeframe VARCHAR(5),
    t_L0 TIMESTAMP,
    t_H1 TIMESTAMP,
    t_L2 TIMESTAMP,
    L0 FLOAT,
    H1 FLOAT,
    L2 FLOAT,
    W FLOAT,
    z FLOAT,
    eps FLOAT,
    eps_r FLOAT,
    base_class VARCHAR(10),
    variant VARCHAR(20),
    regime VARCHAR(20),
    atr_H1 FLOAT,
    atr_L2 FLOAT,
    t_up INT,
    t_down INT,
    retrace_pct FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Performance Monitoring

Track pipeline health:

| Metric               | Target                 | Alert        |
| -------------------- | ---------------------- | ------------ |
| Pivot detection rate | 0.5–1.0 per day per TF | <0.3 or >1.5 |
| EL fraction          | 20–30%                 | <15% or >40% |
| HL fraction          | 50–65%                 | <40% or >75% |
| LL fraction          | 10–20%                 | <5% or >25%  |
| Avg episode duration | 1–10 bars              | <0.5 or >20  |
| FD bin stability     | K±1 month-to-month     | Change >1    |

---

## References

- See [epsilon-tolerance.md](epsilon-tolerance.md) for ε formula details
- See [binning-methodology.md](binning-methodology.md) for FD edge computation
- See [variants-updown.md](variants-updown.md) for variant interpretation

---

**Last Updated**: 2025-10-22
**Context**: EURUSD forex; multiple timeframes; 2–3 year rolling history; no volume data required.
