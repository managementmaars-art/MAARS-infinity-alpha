**Skill**: [Adaptive WFO Epoch Selection](../SKILL.md)

# OOS Application Phase

After epoch selection via efficient frontier, apply the selected epochs to held-out test data for final OOS performance metrics. This phase produces "live trading" results that simulate deployment.

## Nested WFO Structure

AWFES uses **Nested WFO** with three data splits per fold:

```
                    AWFES: Nested WFO Data Split (per fold)

#############     +----------+     +---------+     +----------+     #==========#
# Train 60% # --> | Gap 6% A | --> | Val 20% | --> | Gap 6% B | --> H Test 20% H
#############     +----------+     +---------+     +----------+     #==========#
```

<details>
<summary>graph-easy source</summary>

```
graph { label: "AWFES: Nested WFO Data Split (per fold)"; flow: east; }

[ Train 60% ] { border: bold; }
[ Gap 6% A ]
[ Val 20% ]
[ Gap 6% B ]
[ Test 20% ] { border: double; }

[ Train 60% ] -> [ Gap 6% A ]
[ Gap 6% A ] -> [ Val 20% ]
[ Val 20% ] -> [ Gap 6% B ]
[ Gap 6% B ] -> [ Test 20% ]
```

</details>

## Per-Fold Workflow

```
                  AWFES: Per-Fold Workflow

                   -----------------------
                  |      Fold i Data      |
                   -----------------------
                    |
                    v
                  +-----------------------+
                  | Split: Train/Val/Test |
                  +-----------------------+
                    |
                    v
                  +-----------------------+
                  | Epoch Sweep on Train  |
                  +-----------------------+
                    |
                    v
                  +-----------------------+
                  |  Compute WFE on Val   |
                  +-----------------------+
                    |
                    | val optimal
                    v
                  #=======================#
                  H    Bayesian Update    H
                  #=======================#
                    |
                    | smoothed epoch
                    v
                  +-----------------------+
                  |   Train Final Model   |
                  +-----------------------+
                    |
                    v
                  #=======================#
                  H   Evaluate on Test    H
                  #=======================#
                    |
                    v
                   -----------------------
                  |    Fold i Metrics     |
                   -----------------------
```

<details>
<summary>graph-easy source</summary>

```
graph { label: "AWFES: Per-Fold Workflow"; flow: south; }

[ Fold i Data ] { shape: rounded; }
[ Split: Train/Val/Test ]
[ Epoch Sweep on Train ]
[ Compute WFE on Val ]
[ Bayesian Update ] { border: double; }
[ Train Final Model ]
[ Evaluate on Test ] { border: double; }
[ Fold i Metrics ] { shape: rounded; }

[ Fold i Data ] -> [ Split: Train/Val/Test ]
[ Split: Train/Val/Test ] -> [ Epoch Sweep on Train ]
[ Epoch Sweep on Train ] -> [ Compute WFE on Val ]
[ Compute WFE on Val ] -- val optimal --> [ Bayesian Update ]
[ Bayesian Update ] -- smoothed epoch --> [ Train Final Model ]
[ Train Final Model ] -> [ Evaluate on Test ]
[ Evaluate on Test ] -> [ Fold i Metrics ]
```

</details>

## Bayesian Carry-Forward Across Folds

```
                                 AWFES: Bayesian Carry-Forward Across Folds

 -------   init   +--------+  posterior   +--------+  posterior   +--------+     +--------+      -----------
| Prior | ------> | Fold 1 | -----------> | Fold 2 | -----------> | Fold 3 | ..> | Fold N | --> | Aggregate |
 -------          +--------+              +--------+              +--------+     +--------+      -----------
```

<details>
<summary>graph-easy source</summary>

```
graph { label: "AWFES: Bayesian Carry-Forward Across Folds"; flow: east; }

[ Prior ] { shape: rounded; }
[ Fold 1 ]
[ Fold 2 ]
[ Fold 3 ]
[ Fold N ]
[ Aggregate ] { shape: rounded; }

[ Prior ] -- init --> [ Fold 1 ]
[ Fold 1 ] -- posterior --> [ Fold 2 ]
[ Fold 2 ] -- posterior --> [ Fold 3 ]
[ Fold 3 ] ..> [ Fold N ]
[ Fold N ] -> [ Aggregate ]
```

</details>

## Bayesian Epoch Selection for OOS

Instead of using the current fold's optimal epoch (look-ahead bias), use **Bayesian-smoothed epoch** from prior folds:

```python
class BayesianEpochSelector:
    """Bayesian updating of epoch selection across folds.

    Also known as: BayesianEpochSmoother (alias in epoch-smoothing.md)

    Variance parameters are DERIVED from search space, not hard-coded.
    See AWFESConfig._derive_variances() for the principled derivation.
    """

    def __init__(
        self,
        epoch_configs: list[int],
        prior_mean: float | None = None,
        prior_variance: float | None = None,
        observation_variance: float | None = None,
    ):
        self.epoch_configs = sorted(epoch_configs)

        # PRINCIPLED DERIVATION: Variances from search space
        # If not provided, derive from epoch range
        epoch_range = max(epoch_configs) - min(epoch_configs)

        # Prior spans search space with 95% coverage
        # 95% CI = mean +/- 1.96 sigma -> range = 3.92 sigma -> sigma^2 = (range/3.92)^2
        default_prior_var = (epoch_range / 3.92) ** 2

        # Observation variance: 1/4 of prior for balanced learning
        default_obs_var = default_prior_var / 4

        self.posterior_mean = prior_mean or np.mean(epoch_configs)
        self.posterior_variance = prior_variance or default_prior_var
        self.observation_variance = observation_variance or default_obs_var
        self.history: list[dict] = []

    def update(self, observed_optimal_epoch: int, wfe: float) -> int:
        """Update posterior with new fold's optimal epoch.

        Uses precision-weighted Bayesian update:
        posterior_mean = (prior_precision * prior_mean + obs_precision * obs) /
                        (prior_precision + obs_precision)

        Args:
            observed_optimal_epoch: Optimal epoch from current fold's validation
            wfe: Walk-Forward Efficiency (used to weight observation)

        Returns:
            Smoothed epoch selection for TEST evaluation
        """
        # Weight observation by WFE (higher WFE = more reliable signal)
        # Clamp WFE to [0.1, 2.0] to prevent extreme weights:
        #   - Lower bound 0.1: Prevents division issues and ensures minimum weight
        #   - Upper bound 2.0: WFE > 2 is suspicious (OOS > 2x IS suggests:
        #       a) Regime shift favoring OOS (lucky timing, not skill)
        #       b) IS severely overfit (artificially low denominator)
        #       c) Data anomaly or look-ahead bias
        #     Capping at 2.0 treats such observations with skepticism
        wfe_clamped = max(0.1, min(wfe, 2.0))
        effective_variance = self.observation_variance / wfe_clamped

        prior_precision = 1.0 / self.posterior_variance
        obs_precision = 1.0 / effective_variance

        # Bayesian update
        new_precision = prior_precision + obs_precision
        new_mean = (
            prior_precision * self.posterior_mean +
            obs_precision * observed_optimal_epoch
        ) / new_precision

        # Record before updating
        self.history.append({
            "observed_epoch": observed_optimal_epoch,
            "wfe": wfe,
            "prior_mean": self.posterior_mean,
            "posterior_mean": new_mean,
            "selected_epoch": self._snap_to_config(new_mean),
        })

        self.posterior_mean = new_mean
        self.posterior_variance = 1.0 / new_precision

        return self._snap_to_config(new_mean)

    def _snap_to_config(self, continuous_epoch: float) -> int:
        """Snap continuous estimate to nearest valid epoch config."""
        return min(self.epoch_configs, key=lambda e: abs(e - continuous_epoch))

    def get_current_epoch(self) -> int:
        """Get current smoothed epoch without updating."""
        return self._snap_to_config(self.posterior_mean)
```

## Application Workflow

```python
def apply_awfes_to_test(
    folds: list[Fold],
    model_factory: Callable,
    bayesian_selector: BayesianEpochSelector,
) -> list[dict]:
    """Apply AWFES with Bayesian smoothing to test data.

    Workflow per fold:
    1. Split into train/validation/test (60/20/20)
    2. Sweep epochs on train, compute WFE on validation
    3. Update Bayesian posterior with validation-optimal epoch
    4. Train final model at Bayesian-selected epoch on train+validation
    5. Evaluate on TEST (untouched data)
    """
    results = []

    for fold_idx, fold in enumerate(folds):
        # Step 1: Split data
        train, validation, test = fold.split_nested(
            train_pct=0.60,
            validation_pct=0.20,
            test_pct=0.20,
            embargo_pct=0.06,  # 6% gap at each boundary
        )

        # Step 2: Epoch sweep on train -> validate on validation
        epoch_metrics = []
        for epoch in bayesian_selector.epoch_configs:
            model = model_factory()
            model.fit(train.X, train.y, epochs=epoch)

            is_sharpe = compute_sharpe(model.predict(train.X), train.y)
            val_sharpe = compute_sharpe(model.predict(validation.X), validation.y)

            # Use data-driven threshold instead of hardcoded 0.1
            is_threshold = compute_is_sharpe_threshold(len(train.X))
            wfe = val_sharpe / is_sharpe if is_sharpe > is_threshold else None

            epoch_metrics.append({
                "epoch": epoch,
                "is_sharpe": is_sharpe,
                "val_sharpe": val_sharpe,
                "wfe": wfe,
            })

        # Step 3: Find validation-optimal and update Bayesian
        val_optimal = max(
            [m for m in epoch_metrics if m["wfe"] is not None],
            key=lambda m: m["wfe"],
            default={"epoch": bayesian_selector.epoch_configs[0], "wfe": 0.3}
        )
        selected_epoch = bayesian_selector.update(
            val_optimal["epoch"],
            val_optimal["wfe"],
        )

        # Step 4: Train final model on train+validation at selected epoch
        combined_X = np.vstack([train.X, validation.X])
        combined_y = np.hstack([train.y, validation.y])
        final_model = model_factory()
        final_model.fit(combined_X, combined_y, epochs=selected_epoch)

        # Step 5: Evaluate on TEST (untouched)
        test_predictions = final_model.predict(test.X)
        test_metrics = compute_oos_metrics(test_predictions, test.y, test.timestamps)

        results.append({
            "fold_idx": fold_idx,
            "validation_optimal_epoch": val_optimal["epoch"],
            "bayesian_selected_epoch": selected_epoch,
            "test_metrics": test_metrics,
            "epoch_metrics": epoch_metrics,
        })

    return results
```

See [oos-application.md](./oos-application.md) for the complete implementation reference.
