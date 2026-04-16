**Skill**: [Adaptive WFO Epoch Selection](../SKILL.md)

# Epoch Smoothing Methods

## Why Smooth Epoch Selections?

Raw per-fold epoch selections are noisy due to:

- Limited validation data per fold
- Regime changes between folds
- Stochastic training dynamics

Smoothing reduces variance while preserving signal.

## Method Comparison

| Method                     | Formula                         | Pros                            | Cons                          |
| -------------------------- | ------------------------------- | ------------------------------- | ----------------------------- |
| **Bayesian (Recommended)** | Precision-weighted update       | Principled, handles uncertainty | More complex                  |
| EMA                        | `alpha * new + (1-alpha) * old` | Simple, responsive              | No uncertainty quantification |
| SMA                        | Mean of last N                  | Most stable                     | Slow to adapt                 |
| Median                     | Median of last N                | Robust to outliers              | Loses magnitude info          |

## Bayesian Updating (Primary Method)

```python
def bayesian_epoch_update(
    prior_mean: float,
    prior_variance: float,
    observed_epoch: int,
    observation_variance: float,
    wfe_weight: float = 1.0,
) -> tuple[float, float]:
    """Single Bayesian update step.

    Mathematical formulation:
    - Prior: N(mu_0, sigma_0^2)
    - Observation: N(x, sigma_obs^2/wfe)  # WFE-weighted
    - Posterior: N(mu_1, sigma_1^2)

    Where:
    mu_1 = (mu_0/sigma_0^2 + x*wfe/sigma_obs^2) / (1/sigma_0^2 + wfe/sigma_obs^2)
    sigma_1^2 = 1 / (1/sigma_0^2 + wfe/sigma_obs^2)
    """
    # Effective observation variance (lower WFE = less reliable)
    eff_obs_var = observation_variance / max(wfe_weight, 0.1)

    prior_precision = 1.0 / prior_variance
    obs_precision = 1.0 / eff_obs_var

    posterior_precision = prior_precision + obs_precision
    posterior_mean = (
        prior_precision * prior_mean + obs_precision * observed_epoch
    ) / posterior_precision
    posterior_variance = 1.0 / posterior_precision

    return posterior_mean, posterior_variance
```

## Exponential Moving Average (Alternative)

```python
def ema_epoch_update(
    current_ema: float,
    observed_epoch: int,
    alpha: float = 0.3,
) -> float:
    """EMA update: more weight on recent observations.

    alpha = 0.3 means ~90% of signal from last 7 folds.
    alpha = 0.5 means ~90% of signal from last 4 folds.
    """
    return alpha * observed_epoch + (1 - alpha) * current_ema
```

## Initialization Strategies

| Strategy             | When to Use              | Implementation                       |
| -------------------- | ------------------------ | ------------------------------------ |
| **Midpoint prior**   | No domain knowledge      | `mean(epoch_configs)`                |
| **Literature prior** | Published optimal exists | Known optimal +/- uncertainty        |
| **Burn-in**          | Sufficient data          | Use first N folds for initialization |

```python
# RECOMMENDED: Use AWFESConfig for principled derivation
config = AWFESConfig.from_search_space(
    min_epoch=80,
    max_epoch=400,
    granularity=5,
)
# prior_variance = ((400-80)/3.92)^2 ~ 6,658 (derived automatically)
# observation_variance = prior_variance/4 ~ 1,665 (derived automatically)

# Alternative strategies (if manual configuration needed):

# Strategy 1: Search-space derived (same as AWFESConfig)
epoch_range = max(EPOCH_CONFIGS) - min(EPOCH_CONFIGS)
prior_mean = np.mean(EPOCH_CONFIGS)
prior_variance = (epoch_range / 3.92) ** 2  # 95% CI spans search space

# Strategy 2: Burn-in (use first 5 folds)
burn_in_optima = [run_fold_sweep(fold) for fold in folds[:5]]
prior_mean = np.mean(burn_in_optima)
base_variance = (epoch_range / 3.92) ** 2 / 4  # Reduced after burn-in
prior_variance = max(np.var(burn_in_optima), base_variance)
```

See [epoch-smoothing.md](./epoch-smoothing.md) for extended mathematical analysis.
