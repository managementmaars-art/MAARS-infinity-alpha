**Skill**: [Adaptive WFO Epoch Selection](../SKILL.md)

# Troubleshooting

| Issue                       | Cause                       | Solution                                           |
| --------------------------- | --------------------------- | -------------------------------------------------- |
| WFE is None                 | IS_Sharpe below noise floor | Check if IS_Sharpe > 2/sqrt(n_samples)             |
| All epochs rejected         | Severe overfitting          | Reduce model complexity, add regularization        |
| Bayesian posterior unstable | High WFE variance           | Increase observation_variance or use median WFE    |
| Epoch always at boundary    | Search range too narrow     | Expand min_epoch or max_epoch bounds               |
| Look-ahead bias detected    | Using val_optimal for test  | Use prior_bayesian_epoch for test evaluation       |
| DSR too aggressive          | Too many epoch candidates   | Limit to 3-5 epoch configs (meta-overfitting risk) |
| Cauchy mean issues          | Arithmetic mean of WFE      | Use median or pooled WFE for aggregation           |
| Fold metrics inconsistent   | Variable fold sizes         | Use pooled WFE (precision-weighted)                |
