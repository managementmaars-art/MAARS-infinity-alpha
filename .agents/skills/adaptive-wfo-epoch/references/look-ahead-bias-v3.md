**Skill**: [Adaptive WFO Epoch Selection](../SKILL.md)

# Look-Ahead Bias Prevention

## The Problem

Using the same data for epoch selection AND final evaluation creates look-ahead bias:

```
WRONG: Use fold's own optimal epoch for fold's OOS evaluation
   - Epoch selection "sees" validation returns
   - Then apply same epoch to OOS from same period
   - Result: Overly optimistic performance
```

## The Solution: Nested WFO + Bayesian Lag

```
CORRECT: Bayesian-smoothed epoch from PRIOR folds for current TEST
   - Epoch selection on train/validation (inner loop)
   - Update Bayesian posterior with validation-optimal
   - Apply Bayesian-selected epoch to TEST (outer loop)
   - TEST data completely untouched during selection
```

## v3 Temporal Ordering (CRITICAL - 2026 Fix)

The v3 implementation fixes a subtle but critical look-ahead bias bug in the original AWFES workflow. The key insight: **TEST must use `prior_bayesian_epoch`, NOT `val_optimal_epoch`**.

### The Bug (v2 and earlier)

```python
# v2 BUG: Bayesian update BEFORE test evaluation
for fold in folds:
    epoch_metrics = sweep_epochs(fold.train, fold.validation)
    val_optimal_epoch = select_optimal(epoch_metrics)

    # WRONG: Update Bayesian with current fold's val_optimal
    bayesian.update(val_optimal_epoch, wfe)
    selected_epoch = bayesian.get_current_epoch()  # CONTAMINATED!

    # This selected_epoch is influenced by val_optimal from SAME fold
    test_metrics = evaluate(selected_epoch, fold.test)  # LOOK-AHEAD BIAS
```

### The Fix (v3)

```python
# v3 CORRECT: Get prior epoch BEFORE any work on current fold
for fold in folds:
    # Step 1: FIRST - Get epoch from ONLY prior folds
    prior_bayesian_epoch = bayesian.get_current_epoch()  # BEFORE any fold work

    # Step 2: Train and sweep to find this fold's optimal
    epoch_metrics = sweep_epochs(fold.train, fold.validation)
    val_optimal_epoch = select_optimal(epoch_metrics)

    # Step 3: TEST uses prior_bayesian_epoch (NOT val_optimal!)
    test_metrics = evaluate(prior_bayesian_epoch, fold.test)  # UNBIASED

    # Step 4: AFTER test - update Bayesian for FUTURE folds only
    bayesian.update(val_optimal_epoch, wfe)  # For fold+1, fold+2, ...
```

### Why This Matters

| Aspect                | v2 (Buggy)              | v3 (Fixed)           |
| --------------------- | ----------------------- | -------------------- |
| When Bayesian updated | Before test eval        | After test eval      |
| Test epoch source     | Current fold influences | Only prior folds     |
| Information flow      | Future -> Present       | Past -> Present only |
| Expected bias         | Optimistic by ~10-20%   | Unbiased             |

### Validation Checkpoint

```python
# MANDATORY: Log these values for audit trail
fold_log.info(
    f"Fold {fold_idx}: "
    f"prior_bayesian_epoch={prior_bayesian_epoch}, "
    f"val_optimal_epoch={val_optimal_epoch}, "
    f"test_uses={prior_bayesian_epoch}"  # MUST equal prior_bayesian_epoch
)
```

See [look-ahead-bias.md](./look-ahead-bias.md) for detailed examples.

## Embargo Requirements

| Boundary            | Embargo           | Rationale                 |
| ------------------- | ----------------- | ------------------------- |
| Train -> Validation | 6% of fold        | Prevent feature leakage   |
| Validation -> Test  | 6% of fold        | Prevent selection leakage |
| Fold -> Fold        | 1 hour (calendar) | Range bar duration        |

```python
def compute_embargo_indices(
    n_total: int,
    train_pct: float = 0.60,
    val_pct: float = 0.20,
    test_pct: float = 0.20,
    embargo_pct: float = 0.06,
) -> dict[str, tuple[int, int]]:
    """Compute indices for nested split with embargoes.

    Returns dict with (start, end) tuples for each segment.
    """
    embargo_size = int(n_total * embargo_pct)

    train_end = int(n_total * train_pct)
    val_start = train_end + embargo_size
    val_end = val_start + int(n_total * val_pct)
    test_start = val_end + embargo_size
    test_end = n_total

    return {
        "train": (0, train_end),
        "embargo_1": (train_end, val_start),
        "validation": (val_start, val_end),
        "embargo_2": (val_end, test_start),
        "test": (test_start, test_end),
    }
```

## Validation Checklist

Before running AWFES with OOS application:

- [ ] **Three-way split**: Train/Validation/Test clearly separated
- [ ] **Embargoes**: 6% gap at each boundary
- [ ] **Bayesian lag**: Current fold uses posterior from prior folds
- [ ] **No peeking**: Test data untouched until final evaluation
- [ ] **Temporal order**: No shuffling, strict time sequence
- [ ] **Feature computation**: Features computed BEFORE split, no recalculation

## Anti-Patterns

| Anti-Pattern                                     | Detection                              | Fix                    |
| ------------------------------------------------ | -------------------------------------- | ---------------------- |
| Using current fold's epoch on current fold's OOS | `selected_epoch == fold_optimal_epoch` | Use Bayesian posterior |
| Validation overlaps test                         | Date ranges overlap                    | Add embargo            |
| Features computed on full dataset                | Scaler fit includes test               | Per-split scaling      |
| Fold shuffling                                   | Folds not time-ordered                 | Enforce temporal order |
