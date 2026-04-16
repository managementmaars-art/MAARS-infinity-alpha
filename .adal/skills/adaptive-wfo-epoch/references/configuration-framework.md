**Skill**: [Adaptive WFO Epoch Selection](../SKILL.md)

# Principled Configuration Framework

All parameters in AWFES are derived from first principles or data characteristics, not arbitrary magic numbers.

## AWFESConfig: Unified Configuration

```python
from dataclasses import dataclass, field
from typing import Literal
import numpy as np

@dataclass
class AWFESConfig:
    """AWFES configuration with principled parameter derivation.

    No magic numbers - all values derived from search space or data.
    """
    # Search space bounds (user-specified)
    min_epoch: int
    max_epoch: int
    granularity: int  # Number of frontier points

    # Derived automatically
    epoch_configs: list[int] = field(init=False)
    prior_variance: float = field(init=False)
    observation_variance: float = field(init=False)

    # Market context for annualization
    # crypto_session_filtered: Use when data is filtered to London-NY weekday hours
    market_type: Literal["crypto_24_7", "crypto_session_filtered", "equity", "forex"] = "crypto_24_7"
    time_unit: Literal["bar", "daily", "weekly"] = "weekly"

    def __post_init__(self):
        # Generate epoch configs with log spacing (optimal for frontier discovery)
        self.epoch_configs = self._generate_epoch_configs()

        # Derive Bayesian variances from search space
        self.prior_variance, self.observation_variance = self._derive_variances()

    def _generate_epoch_configs(self) -> list[int]:
        """Generate epoch candidates with log spacing.

        Log spacing is optimal for efficient frontier because:
        1. Early epochs: small changes matter more (underfit -> fit transition)
        2. Late epochs: diminishing returns (already near convergence)
        3. Uniform coverage of the WFE vs cost trade-off space

        Formula: epoch_i = min x (max/min)^(i/(n-1))
        """
        if self.granularity < 2:
            return [self.min_epoch]

        log_min = np.log(self.min_epoch)
        log_max = np.log(self.max_epoch)
        log_epochs = np.linspace(log_min, log_max, self.granularity)

        return sorted(set(int(round(np.exp(e))) for e in log_epochs))

    def _derive_variances(self) -> tuple[float, float]:
        """Derive Bayesian variances from search space.

        Principle: Prior should span the search space with ~95% coverage.

        For Normal distribution: 95% CI = mean +/- 1.96 sigma
        If we want 95% of prior mass in [min_epoch, max_epoch]:
            range = max - min = 2 x 1.96 x sigma = 3.92 sigma
            sigma = range / 3.92
            sigma^2 = (range / 3.92)^2

        Observation variance: Set to achieve reasonable learning rate.
        Rule: observation_variance ~ prior_variance / 4
        This means each observation updates the posterior meaningfully
        but doesn't dominate the prior immediately.
        """
        epoch_range = self.max_epoch - self.min_epoch
        prior_std = epoch_range / 3.92  # 95% CI spans search space
        prior_variance = prior_std ** 2

        # Observation variance: 1/4 of prior for balanced learning
        # This gives ~0.2 weight to each new observation initially
        observation_variance = prior_variance / 4

        return prior_variance, observation_variance

    @classmethod
    def from_search_space(
        cls,
        min_epoch: int,
        max_epoch: int,
        granularity: int = 5,
        market_type: str = "crypto_24_7",
    ) -> "AWFESConfig":
        """Create config from search space bounds."""
        return cls(
            min_epoch=min_epoch,
            max_epoch=max_epoch,
            granularity=granularity,
            market_type=market_type,
        )

    def compute_wfe(
        self,
        is_sharpe: float,
        oos_sharpe: float,
        n_samples: int | None = None,
    ) -> float | None:
        """Compute WFE with data-driven IS_Sharpe threshold."""
        min_is = compute_is_sharpe_threshold(n_samples) if n_samples else 0.1
        if abs(is_sharpe) < min_is:
            return None
        return oos_sharpe / is_sharpe

    def get_annualization_factor(self) -> float:
        """Get annualization factor to scale Sharpe from time_unit to ANNUAL.

        IMPORTANT: This returns sqrt(periods_per_year) for scaling to ANNUAL Sharpe.
        For daily-to-weekly scaling, use get_daily_to_weekly_factor() instead.

        Principled derivation:
        - Sharpe scales with sqrt(periods per year)
        - Crypto 24/7: 365 days/year, 52.14 weeks/year
        - Crypto session-filtered: 252 days/year (like equity)
        - Equity: 252 trading days/year, ~52 weeks/year
        - Forex: ~252 days/year (varies by pair)
        """
        PERIODS_PER_YEAR = {
            ("crypto_24_7", "daily"): 365,
            ("crypto_24_7", "weekly"): 52.14,
            ("crypto_24_7", "bar"): None,  # Cannot annualize bars directly
            ("crypto_session_filtered", "daily"): 252,  # London-NY weekdays only
            ("crypto_session_filtered", "weekly"): 52,
            ("equity", "daily"): 252,
            ("equity", "weekly"): 52,
            ("forex", "daily"): 252,
        }

        key = (self.market_type, self.time_unit)
        periods = PERIODS_PER_YEAR.get(key)

        if periods is None:
            raise ValueError(
                f"Cannot annualize {self.time_unit} for {self.market_type}. "
                "Use daily or weekly aggregation first."
            )

        return np.sqrt(periods)

    def get_daily_to_weekly_factor(self) -> float:
        """Get factor to scale DAILY Sharpe to WEEKLY Sharpe.

        This is different from get_annualization_factor()!
        - Daily -> Weekly: sqrt(days_per_week)
        - Daily -> Annual: sqrt(days_per_year)  (use get_annualization_factor)

        Market-specific:
        - Crypto 24/7: sqrt(7) = 2.65 (7 trading days/week)
        - Crypto session-filtered: sqrt(5) = 2.24 (weekdays only)
        - Equity: sqrt(5) = 2.24 (5 trading days/week)
        """
        DAYS_PER_WEEK = {
            "crypto_24_7": 7,
            "crypto_session_filtered": 5,  # London-NY weekdays only
            "equity": 5,
            "forex": 5,
        }

        days = DAYS_PER_WEEK.get(self.market_type)
        if days is None:
            raise ValueError(f"Unknown market type: {self.market_type}")

        return np.sqrt(days)
```

## IS_Sharpe Threshold: Signal-to-Noise Derivation

```python
def compute_is_sharpe_threshold(n_samples: int | None = None) -> float:
    """Compute minimum IS_Sharpe threshold from signal-to-noise ratio.

    Principle: IS_Sharpe must be statistically distinguishable from zero.

    Under null hypothesis (no skill), Sharpe ~ N(0, 1/sqrt(n)).
    To reject null at alpha=0.05 (one-sided), need Sharpe > 1.645/sqrt(n).

    For practical use, we use 2 sigma threshold (~97.7% confidence):
        threshold = 2.0 / sqrt(n)

    This adapts to sample size:
    - n=100: threshold ~ 0.20
    - n=400: threshold ~ 0.10
    - n=1600: threshold ~ 0.05

    Fallback for unknown n: 0.1 (assumes n~400, typical fold size)

    Rationale for 0.1 fallback:
    - 2/sqrt(400) = 0.1, so 0.1 assumes ~400 samples per fold
    - This is conservative: 400 samples is typical for weekly folds
    - If actual n is smaller, threshold is looser (accepts more noise)
    - If actual n is larger, threshold is tighter (fine, we're conservative)
    - The 0.1 value also corresponds to "not statistically distinguishable
      from zero at reasonable sample sizes" - a natural floor for Sharpe SE
    """
    if n_samples is None or n_samples < 10:
        # Conservative fallback: 0.1 assumes ~400 samples (typical fold size)
        # Derivation: 2/sqrt(400) = 0.1; see rationale above
        return 0.1

    return 2.0 / np.sqrt(n_samples)
```
