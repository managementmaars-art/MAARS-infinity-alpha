---
name: abtesting
cluster: abtesting
description: "Root A/B testing: experiment design, statistical significance, sample size power analysis, launch criteria"
tags: ["ab-testing","experiments","statistics"]
dependencies: []
composes: []
similar_to: []
called_by: []
authorization_required: false
scope: general
model_hint: claude-sonnet
embedding_hint: "ab test experiment statistical significance sample size power analysis"
---

## abtesting

### Purpose
This skill enables A/B testing workflows, including experiment design, statistical significance testing, sample size power analysis, and defining launch criteria. Use it to optimize decisions based on data-driven experiments.

### When to Use
Apply this skill when designing experiments for feature rollouts, website changes, or product variations. Use it for scenarios requiring statistical validation, such as comparing conversion rates or user engagement metrics, to ensure reliable results before full deployment.

### Key Capabilities
- Design A/B experiments with parameters like variants, metrics, and duration.
- Perform power analysis to calculate required sample sizes using formulas like Cohen's d.
- Test statistical significance with t-tests or chi-squared tests on experiment data.
- Define launch criteria based on p-values, confidence intervals, and effect sizes.
- Integrate with data sources for real-time analysis.

### Usage Patterns
Start by initializing an experiment object with required parameters. Use CLI for quick calculations or API for programmatic access. Always set the API key via environment variable `$ABTEST_API_KEY` before operations. For example, chain commands to design, run analysis, and decide on launch. Handle asynchronous API calls by polling for results.

### Common Commands/API
Use the OpenClaw CLI for A/B testing commands. Set up with `export ABTEST_API_KEY=your_key`. Example API endpoint: `POST https://api.openclaw.ai/abtesting/experiments`.

- CLI command for sample size calculation:  
  `abtest calculate-sample-size --effect-size 0.2 --power 0.8 --alpha 0.05`  
  This outputs the minimum sample per group.

- API call for significance test:  
  `curl -H "Authorization: Bearer $ABTEST_API_KEY" -d '{"control': [50, 55], 'treatment': [60, 65], 'metric': 'mean'}" https://api.openclaw.ai/abtesting/significance`  
  Returns JSON with p-value and confidence interval.

- Config format for experiment design (JSON):  
  `{ "name": "email-variant-test", "variants": ["A", "B"], "metric": "click-rate", "duration_days": 7 }`  
  Save as `experiment.json` and run: `abtest design --config experiment.json`.

- Power analysis via code snippet (Python):  
  `import openclaw.abtesting`  
  `result = openclaw.abtesting.power_analysis(effect_size=0.1, alpha=0.05, power=0.8)`  
  Print result for required sample size.

### Integration Notes
Integrate this skill into your codebase by importing the OpenClaw SDK and setting `$ABTEST_API_KEY`. For web apps, use it in CI/CD pipelines to validate experiments before merges. Ensure data sources (e.g., databases) are accessible via the SDK's `connect` method, like `openclaw.abtesting.connect(db_url="postgres://user:pass@host/db")`. If using in a microservice, handle retries for API calls with exponential backoff.

### Error Handling
Check for errors in every command; CLI returns exit codes (e.g., 1 for invalid input). For API, parse HTTP responses: 400 for bad requests, 401 for auth failures. Example:  
`try:  
    response = requests.post(url, headers={"Authorization": f"Bearer {os.environ['ABTEST_API_KEY']}"}))  
    response.raise_for_status()  
except requests.exceptions.HTTPError as e:  
    log_error(e)`  
Handle common issues like insufficient sample size by validating inputs upfront, e.g., use `abtest validate --config experiment.json` to catch errors early.

### Concrete Usage Examples
1. **Design and calculate sample size for a website variant test:**  
   First, create a config: `{ "name": "homepage-test", "variants": ["original", "new"], "metric": "bounce-rate" }`.  
   Run: `abtest calculate-sample-size --effect-size 0.05 --power 0.8 --alpha 0.05`.  
   Use the output (e.g., 500 per group) to set up: `abtest design --config config.json`.  
   This ensures your experiment has enough power.

2. **Analyze significance and decide launch for an email campaign:**  
   Collect data: control clicks = [100, 120], treatment = [140, 150].  
   Run: `curl -H "Authorization: Bearer $ABTEST_API_KEY" -d '{"control": [100,120], "treatment": [140,150], "metric": "mean"}' https://api.openclaw.ai/abtesting/significance`.  
   If p-value < 0.05, proceed with launch criteria: `abtest launch-check --p-value 0.03 --min-effect 0.1`.  
   This automates decision-making based on results.

### Graph Relationships
- Related to cluster: abtesting (direct parent).
- Connected to tags: ab-testing, experiments, statistics.
- Links to other skills: analytics (for data processing), data-science (for advanced stats).
