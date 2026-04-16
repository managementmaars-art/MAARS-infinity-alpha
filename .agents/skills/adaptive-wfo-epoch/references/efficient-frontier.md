**Skill**: [Adaptive WFO Epoch Selection](../SKILL.md)

# Efficient Frontier Algorithm

## Pareto-Optimal Epoch Selection

```python
def compute_efficient_frontier(
    epoch_metrics: list[dict],
    wfe_weight: float = 1.0,
    time_weight: float = 0.1,
) -> tuple[list[int], int]:
    """
    Find Pareto-optimal epochs and select best.

    An epoch is on the frontier if no other epoch dominates it
    (better WFE AND lower training time).

    Args:
        epoch_metrics: List of {epoch, wfe, training_time_sec}
        wfe_weight: Weight for WFE in selection (higher = prefer generalization)
        time_weight: Weight for training time (higher = prefer speed)

    Returns:
        (frontier_epochs, selected_epoch)
    """
    import numpy as np

    # Filter valid metrics
    valid = [(m["epoch"], m["wfe"], m.get("training_time_sec", m["epoch"]))
             for m in epoch_metrics
             if m["wfe"] is not None and np.isfinite(m["wfe"])]

    if not valid:
        # Fallback: return epoch with best OOS Sharpe
        best_oos = max(epoch_metrics, key=lambda m: m.get("oos_sharpe", 0))
        return ([best_oos["epoch"]], best_oos["epoch"])

    # Pareto dominance check
    frontier = []
    for i, (epoch_i, wfe_i, time_i) in enumerate(valid):
        dominated = False
        for j, (epoch_j, wfe_j, time_j) in enumerate(valid):
            if i == j:
                continue
            # j dominates i if: better/equal WFE AND lower/equal time (strict in at least one)
            if (wfe_j >= wfe_i and time_j <= time_i and
                (wfe_j > wfe_i or time_j < time_i)):
                dominated = True
                break
        if not dominated:
            frontier.append((epoch_i, wfe_i, time_i))

    frontier_epochs = [e for e, _, _ in frontier]

    if len(frontier) == 1:
        return (frontier_epochs, frontier[0][0])

    # Weighted score selection
    wfes = np.array([w for _, w, _ in frontier])
    times = np.array([t for _, _, t in frontier])

    wfe_norm = (wfes - wfes.min()) / (wfes.max() - wfes.min() + 1e-10)
    time_norm = (times.max() - times) / (times.max() - times.min() + 1e-10)

    scores = wfe_weight * wfe_norm + time_weight * time_norm
    best_idx = np.argmax(scores)

    return (frontier_epochs, frontier[best_idx][0])
```

## Carry-Forward Mechanism

```python
class AdaptiveEpochSelector:
    """Maintains epoch selection state across WFO folds with adaptive stability."""

    def __init__(self, epoch_configs: list[int]):
        self.epoch_configs = epoch_configs
        self.selection_history: list[dict] = []
        self.last_selected: int | None = None
        self.stability = AdaptiveStabilityPenalty()  # Use adaptive, not fixed

    def select_epoch(self, epoch_metrics: list[dict]) -> int:
        """Select epoch with adaptive stability penalty for changes."""
        frontier_epochs, candidate = compute_efficient_frontier(epoch_metrics)

        # Apply adaptive stability penalty if changing epochs
        if self.last_selected is not None and candidate != self.last_selected:
            candidate_wfe = next(
                m["wfe"] for m in epoch_metrics if m["epoch"] == candidate
            )
            last_wfe = next(
                (m["wfe"] for m in epoch_metrics if m["epoch"] == self.last_selected),
                0.0
            )

            # Use adaptive threshold derived from WFE variance
            if not self.stability.should_change_epoch(
                last_wfe, candidate_wfe, self.last_selected, candidate
            ):
                candidate = self.last_selected

        # Record and return
        self.selection_history.append({
            "epoch": candidate,
            "frontier": frontier_epochs,
            "changed": candidate != self.last_selected,
        })
        self.last_selected = candidate
        return candidate
```
