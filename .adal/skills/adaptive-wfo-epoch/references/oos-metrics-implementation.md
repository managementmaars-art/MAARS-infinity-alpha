**Skill**: [Adaptive WFO Epoch Selection](../SKILL.md)

# OOS Metrics Implementation

## Metric Tiers for Test Evaluation

Following [rangebar-eval-metrics](../../rangebar-eval-metrics/SKILL.md), compute these metrics on TEST data.

**CRITICAL for Range Bars**: Use time-weighted Sharpe (`sharpe_tw`) instead of simple bar Sharpe. See [range-bar-metrics.md](./range-bar-metrics.md) for the canonical implementation. The metrics below assume time-weighted computation for range bar data.

### Tier 1: Primary Metrics (Mandatory)

| Metric                  | Formula                                  | Threshold | Purpose              |
| ----------------------- | ---------------------------------------- | --------- | -------------------- |
| `sharpe_tw`             | Time-weighted (see range-bar-metrics.md) | > 0       | Core performance     |
| `hit_rate`              | `n_correct_sign / n_total`               | > 0.50    | Directional accuracy |
| `cumulative_pnl`        | `sum(pred * actual)`                     | > 0       | Total return         |
| `positive_sharpe_folds` | `n_folds(sharpe_tw > 0) / n_folds`       | > 0.55    | Consistency          |
| `wfe_test`              | `test_sharpe_tw / validation_sharpe_tw`  | > 0.30    | Final transfer       |

### Tier 2: Risk Metrics

| Metric          | Formula                        | Threshold | Purpose        |
| --------------- | ------------------------------ | --------- | -------------- |
| `max_drawdown`  | `max(peak - trough) / peak`    | < 0.30    | Worst loss     |
| `calmar_ratio`  | `annual_return / max_drawdown` | > 0.5     | Risk-adjusted  |
| `profit_factor` | `gross_profit / gross_loss`    | > 1.0     | Win/loss ratio |
| `cvar_10pct`    | `mean(worst 10% returns)`      | > -0.05   | Tail risk      |

### Tier 3: Statistical Validation

| Metric             | Formula                           | Threshold | Purpose                   |
| ------------------ | --------------------------------- | --------- | ------------------------- |
| `psr`              | `P(true_sharpe > 0)`              | > 0.85    | Statistical significance  |
| `dsr`              | `sharpe - E[max_sharpe_null]`     | > 0.50    | Multiple testing adjusted |
| `binomial_pvalue`  | `binom.test(n_positive, n_total)` | < 0.05    | Sign test                 |
| `hac_ttest_pvalue` | HAC-adjusted t-test               | < 0.05    | Autocorrelation robust    |

## Metric Computation Code

```python
import numpy as np
from scipy.stats import norm, binomtest  # norm for PSR, binomtest for sign test

def compute_oos_metrics(
    predictions: np.ndarray,
    actuals: np.ndarray,
    timestamps: np.ndarray,
    duration_us: np.ndarray | None = None,  # Required for range bars
    market_type: str = "crypto_24_7",  # For annualization factor
) -> dict[str, float]:
    """Compute full OOS metrics suite for test data.

    Args:
        predictions: Model predictions (signed magnitude)
        actuals: Actual returns
        timestamps: Bar timestamps for daily aggregation
        duration_us: Bar durations in microseconds (REQUIRED for range bars)

    Returns:
        Dictionary with all tier metrics

    IMPORTANT: For range bars, pass duration_us to compute sharpe_tw.
    Simple bar_sharpe violates i.i.d. assumption - see range-bar-metrics.md.
    """
    pnl = predictions * actuals

    # Tier 1: Primary
    # For range bars: Use time-weighted Sharpe (canonical)
    if duration_us is not None:
        from exp066e_tau_precision import compute_time_weighted_sharpe
        sharpe_tw, weighted_std, total_days = compute_time_weighted_sharpe(
            bar_pnl=pnl,
            duration_us=duration_us,
            annualize=True,
        )
    else:
        # Fallback for time bars (all same duration)
        daily_pnl = group_by_day(pnl, timestamps)
        weekly_factor = get_daily_to_weekly_factor(market_type=market_type)
        sharpe_tw = (
            np.mean(daily_pnl) / np.std(daily_pnl) * weekly_factor
            if np.std(daily_pnl) > 1e-10 else 0.0
        )

    hit_rate = np.mean(np.sign(predictions) == np.sign(actuals))
    cumulative_pnl = np.sum(pnl)

    # Tier 2: Risk
    equity_curve = np.cumsum(pnl)
    running_max = np.maximum.accumulate(equity_curve)
    drawdowns = (running_max - equity_curve) / np.maximum(running_max, 1e-10)
    max_drawdown = np.max(drawdowns)

    gross_profit = np.sum(pnl[pnl > 0])
    gross_loss = abs(np.sum(pnl[pnl < 0]))
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float("inf")

    # CVaR (10%)
    sorted_pnl = np.sort(pnl)
    cvar_cutoff = max(1, int(len(sorted_pnl) * 0.10))
    cvar_10pct = np.mean(sorted_pnl[:cvar_cutoff])

    # Tier 3: Statistical (use sharpe_tw for PSR)
    sharpe_se = 1.0 / np.sqrt(len(pnl)) if len(pnl) > 0 else 1.0
    psr = norm.cdf(sharpe_tw / sharpe_se) if sharpe_se > 0 else 0.5

    n_positive = np.sum(pnl > 0)
    n_total = len(pnl)
    # Use binomtest (binom_test deprecated since scipy 1.10)
    binomial_pvalue = binomtest(n_positive, n_total, 0.5, alternative="greater").pvalue

    return {
        # Tier 1 (use sharpe_tw for range bars)
        "sharpe_tw": sharpe_tw,
        "hit_rate": hit_rate,
        "cumulative_pnl": cumulative_pnl,
        "n_bars": len(pnl),
        # Tier 2
        "max_drawdown": max_drawdown,
        "profit_factor": profit_factor,
        "cvar_10pct": cvar_10pct,
        # Tier 3
        "psr": psr,
        "binomial_pvalue": binomial_pvalue,
    }
```

## Aggregation Across Folds

```python
def aggregate_test_metrics(fold_results: list[dict]) -> dict[str, float]:
    """Aggregate test metrics across all folds.

    NOTE: For range bars, use sharpe_tw (time-weighted).
    See range-bar-metrics.md for why simple bar_sharpe is invalid for range bars.
    """
    metrics = [r["test_metrics"] for r in fold_results]

    # Positive Sharpe Folds (use sharpe_tw for range bars)
    sharpes = [m["sharpe_tw"] for m in metrics]
    positive_sharpe_folds = np.mean([s > 0 for s in sharpes])

    # Median for robustness
    median_sharpe_tw = np.median(sharpes)
    median_hit_rate = np.median([m["hit_rate"] for m in metrics])

    # DSR for multiple testing (use time-weighted Sharpe)
    n_trials = len(metrics)
    dsr = compute_dsr(median_sharpe_tw, n_trials)

    return {
        "n_folds": len(metrics),
        "positive_sharpe_folds": positive_sharpe_folds,
        "median_sharpe_tw": median_sharpe_tw,
        "mean_sharpe_tw": np.mean(sharpes),
        "std_sharpe_tw": np.std(sharpes),
        "median_hit_rate": median_hit_rate,
        "dsr": dsr,
        "total_pnl": sum(m["cumulative_pnl"] for m in metrics),
    }
```

See [oos-metrics.md](./oos-metrics.md) for threshold justifications.
