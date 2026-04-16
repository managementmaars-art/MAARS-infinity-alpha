---
name: abtesting-stats
cluster: abtesting
description: "Statistical analysis: t-tests, chi-squared, Mann-Whitney, p-values, CIs, Bonferroni/BH, Bayesian A/B"
tags: ["statistics","t-test","bayesian","p-value"]
dependencies: []
composes: []
similar_to: []
called_by: []
authorization_required: false
scope: general
model_hint: claude-sonnet
embedding_hint: "ab test statistics t-test chi-squared bayesian p-value confidence interval"
---

# abtesting-stats

## Purpose
This skill performs statistical analysis for A/B testing, including t-tests, chi-squared tests, Mann-Whitney U tests, p-value calculations, confidence intervals (CIs), multiple testing corrections like Bonferroni or Benjamini-Hochberg (BH), and Bayesian A/B testing methods.

## When to Use
Use this skill when comparing two groups in experiments, such as website variants, to determine statistical significance. Apply it for hypothesis testing in data science workflows, validating A/B test results, or analyzing user behavior metrics. Avoid if data is non-numeric or sample sizes are too small (<10 per group).

## Key Capabilities
- Conduct t-tests for normally distributed data.
- Perform chi-squared tests for categorical data.
- Run Mann-Whitney U tests for non-parametric comparisons.
- Calculate p-values and 95% CIs for effect sizes.
- Apply corrections like Bonferroni for multiple comparisons or BH for FDR control.
- Execute Bayesian A/B tests using priors like uniform or beta distributions.
- Handle input data from CSV, JSON, or in-memory arrays.

## Usage Patterns
Invoke via CLI for quick runs or integrate via API for scripted workflows. Always provide data sources and specify the test type. Use JSON config files for complex parameters. For example, pipe data directly into CLI or call API endpoints in loops for batch processing. Ensure data is pre-cleaned (e.g., remove NaNs) before use.

## Common Commands/API
Use the OpenClaw CLI with the `abtesting-stats` subcommand. Authentication requires setting `$OPENCLAW_API_KEY` as an environment variable.

- CLI Command for t-test:  
  `openclaw abtesting-stats run --test t-test --data-path data.csv --groups groupA groupB --alpha 0.05`  
  This computes a two-sample t-test and outputs p-value and CI.

- API Endpoint for chi-squared:  
  POST to `/api/abtesting/stats` with JSON body:  
  ```json  
  {  
    "test": "chi-squared",  
    "data": {"category1": [10, 20], "category2": [15, 25]},  
    "alpha": 0.01  
  }  
  ```  
  Response includes p-value and expected frequencies.

- CLI for Mann-Whitney:  
  `openclaw abtesting-stats run --test mann-whitney --file input.json --key metric --significance 0.01`  
  Expects JSON with arrays for each group.

- API for Bayesian A/B:  
  POST to `/api/abtesting/bayesian` with:  
  ```json  
  {  
    "test": "bayesian",  
    "conversions": [50, 60],  
    "trials": [1000, 1000],  
    "prior": "beta"  
  }  
  ```  
  Returns posterior probabilities and credible intervals.

Config format is JSON, e.g., save as `config.json`:  
```json  
{  
  "test": "bonferroni",  
  "p_values": [0.01, 0.02, 0.05]  
}  
```  
Then run: `openclaw abtesting-stats apply-config config.json`.

## Integration Notes
Integrate by setting `$OPENCLAW_API_KEY` for all API calls. For Python scripts, use the OpenClaw SDK:  
```python  
import openclaw  
client = openclaw.Client(api_key=os.environ['OPENCLAW_API_KEY'])  
response = client.post('/api/abtesting/stats', json={'test': 't-test', 'data': [...]})  
```  
Handle asynchronous responses by checking for 'job_id' in the response and polling `/api/jobs/{job_id}`. Combine with data tools like Pandas for preprocessing, e.g., load CSV and format as JSON. Avoid rate limits by batching requests (max 10/sec).

## Error Handling
Check for common errors like invalid data formats (e.g., non-numeric inputs) by validating inputs first. If API returns 401, ensure `$OPENCLAW_API_KEY` is set and valid. For CLI, parse errors from stdout (e.g., "Error: Insufficient samples"). Use try-except in code:  
```python  
try:  
    result = client.post(...)  
except openclaw.AuthError:  
    print("Authentication failed; check $OPENCLAW_API_KEY")  
```  
Log detailed errors with `--verbose` flag in CLI for debugging, e.g., `openclaw abtesting-stats run --verbose ...`. Retry transient errors (e.g., 503) up to 3 times with exponential backoff.

## Concrete Usage Examples
1. **T-test on sales data**: To compare average sales between two ad variants, run:  
   `openclaw abtesting-stats run --test t-test --data-path sales.csv --groups variantA variantB`  
   Assuming sales.csv has columns: group, sales. This outputs: p-value=0.03, CI=[5.2, 10.4], indicating significant difference.

2. **Bayesian A/B for click-through rates**: For testing email campaigns, use API:  
   POST to `/api/abtesting/bayesian` with:  
   ```json  
   {  
     "conversions": [120, 150],  
     "trials": [1000, 1000]  
   }  
   ```  
   This yields a 90% probability that variant B is better, guiding decisions without p-values.

## Graph Relationships
- Related to: abtesting-experiment (provides data setup for this skill)
- Related to: stats-visualization (uses outputs like CIs for plotting)
- Connected via: abtesting cluster (shares common A/B testing utilities)
