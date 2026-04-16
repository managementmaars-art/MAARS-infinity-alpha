**Skill**: [Adaptive WFO Epoch Selection](../SKILL.md)

# WFE Aggregation Methods

**WARNING: Cauchy Distribution Under Null**

Under the null hypothesis (no predictive skill), WFE follows a **Cauchy distribution**, which has:

- No defined mean (undefined expectation)
- No defined variance (infinite)
- Heavy tails (extreme values common)

This makes **arithmetic mean unreliable**. A single extreme WFE can dominate the average. **Always prefer median or pooled methods** for robust WFE aggregation. See [mathematical-formulation.md](./mathematical-formulation.md) for the proof: `WFE | H0 ~ Cauchy(0, sqrt(T_IS/T_OOS))`.

## Method 1: Pooled WFE (Recommended for precision-weighted)

```python
def pooled_wfe(fold_results: list[dict]) -> float:
    """Weights each fold by its sample size (precision).

    Formula: sum(T_OOS * SR_OOS) / sum(T_IS * SR_IS)

    Advantage: More stable than arithmetic mean, handles varying fold sizes.
    Use when: Fold sizes vary significantly.
    """
    numerator = sum(r["n_oos"] * r["oos_sharpe"] for r in fold_results)
    denominator = sum(r["n_is"] * r["is_sharpe"] for r in fold_results)

    if denominator < 1e-10:
        return float("nan")
    return numerator / denominator
```

## Method 2: Median WFE (Recommended for robustness)

```python
def median_wfe(fold_results: list[dict]) -> float:
    """Robust to outliers, standard in robust statistics.

    Advantage: Single extreme fold doesn't dominate.
    Use when: Suspected outlier folds (regime changes, data issues).
    """
    wfes = [r["wfe"] for r in fold_results if r["wfe"] is not None]
    return float(np.median(wfes)) if wfes else float("nan")
```

## Method 3: Weighted Arithmetic Mean

```python
def weighted_mean_wfe(fold_results: list[dict]) -> float:
    """Weights by inverse variance (efficiency weighting).

    Formula: sum(w_i * WFE_i) / sum(w_i)
    where w_i = 1 / Var(WFE_i) ~ n_oos * n_is / (n_oos + n_is)

    Advantage: Optimal when combining estimates of different precision.
    Use when: All folds have similar characteristics.
    """
    weighted_sum = 0.0
    weight_total = 0.0

    for r in fold_results:
        if r["wfe"] is None:
            continue
        weight = r["n_oos"] * r["n_is"] / (r["n_oos"] + r["n_is"] + 1e-10)
        weighted_sum += weight * r["wfe"]
        weight_total += weight

    return weighted_sum / weight_total if weight_total > 0 else float("nan")
```

## Aggregation Selection Guide

| Scenario            | Recommended Method | Rationale               |
| ------------------- | ------------------ | ----------------------- |
| Variable fold sizes | Pooled WFE         | Weights by precision    |
| Suspected outliers  | Median WFE         | Robust to extremes      |
| Homogeneous folds   | Weighted mean      | Optimal efficiency      |
| Reporting           | **All three**      | Cross-check consistency |
