---
name: data-analysis
description: AI data analysis skills — pandas, SQL, statistical analysis, visualization, dashboards, predictive modeling, reporting for MAARS data and analytics agents
---

# Data Analysis AI — MAARS Reference

## Python Data Analysis Stack
```python
# Core stack used by MAARS data agents
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import json

# For LLM-assisted analysis
async def analyze_dataset(df: pd.DataFrame, question: str) -> str:
    # Prepare data summary for LLM
    summary = {
        "shape": df.shape,
        "columns": df.dtypes.to_dict(),
        "sample": df.head(5).to_dict(),
        "describe": df.describe().to_dict(),
        "nulls": df.isnull().sum().to_dict(),
    }
    
    prompt = f"""Analyze this dataset to answer: {question}
    
Dataset info: {json.dumps(summary, default=str)}

Provide:
1. Direct answer to the question
2. Key insights from the data
3. Statistical significance (if relevant)
4. Recommended visualizations
5. Python code to generate the analysis"""
    
    return await llm_call("gpt-4o", prompt)
```

## SQL Analysis Patterns
```sql
-- Revenue analysis pattern
WITH monthly_revenue AS (
    SELECT 
        DATE_TRUNC('month', created_at) AS month,
        SUM(amount) AS revenue,
        COUNT(DISTINCT user_id) AS customers,
        SUM(amount) / COUNT(DISTINCT user_id) AS arpu
    FROM transactions
    WHERE status = 'completed'
    GROUP BY 1
),
growth AS (
    SELECT *,
        LAG(revenue) OVER (ORDER BY month) AS prev_revenue,
        (revenue - LAG(revenue) OVER (ORDER BY month)) / 
            NULLIF(LAG(revenue) OVER (ORDER BY month), 0) * 100 AS mom_growth
    FROM monthly_revenue
)
SELECT * FROM growth ORDER BY month;

-- Cohort retention analysis
WITH cohorts AS (
    SELECT user_id, DATE_TRUNC('month', MIN(created_at)) AS cohort_month
    FROM events GROUP BY 1
),
activity AS (
    SELECT e.user_id, c.cohort_month,
           DATE_TRUNC('month', e.created_at) AS activity_month,
           DATEDIFF('month', c.cohort_month, DATE_TRUNC('month', e.created_at)) AS month_number
    FROM events e JOIN cohorts c ON e.user_id = c.user_id
)
SELECT cohort_month, month_number,
       COUNT(DISTINCT user_id) AS users,
       COUNT(DISTINCT user_id) / FIRST_VALUE(COUNT(DISTINCT user_id)) 
           OVER (PARTITION BY cohort_month ORDER BY month_number) AS retention_rate
FROM activity GROUP BY 1, 2 ORDER BY 1, 2;
```

## Statistical Analysis
```python
def comprehensive_analysis(data: pd.Series) -> dict:
    return {
        "descriptive": {
            "mean": data.mean(), "median": data.median(),
            "std": data.std(), "skew": data.skew(),
            "kurtosis": data.kurtosis(),
            "percentiles": data.quantile([0.25, 0.75, 0.9, 0.95, 0.99]).to_dict(),
        },
        "normality_test": {
            "shapiro_pvalue": stats.shapiro(data.dropna()[:5000])[1],
            "is_normal": stats.shapiro(data.dropna()[:5000])[1] > 0.05,
        },
        "outliers": {
            "iqr_method": len(data[(data < data.quantile(0.25) - 1.5 * (data.quantile(0.75) - data.quantile(0.25))) | 
                                   (data > data.quantile(0.75) + 1.5 * (data.quantile(0.75) - data.quantile(0.25)))]),
            "zscore_3std": len(data[np.abs(stats.zscore(data.dropna())) > 3]),
        }
    }
```

## A/B Test Analysis
```python
def analyze_ab_test(control: list, treatment: list, metric: str = "conversion") -> dict:
    from scipy.stats import ttest_ind, chi2_contingency
    
    if metric == "conversion":
        # Proportion test
        control_rate = np.mean(control)
        treatment_rate = np.mean(treatment)
        lift = (treatment_rate - control_rate) / control_rate * 100
        
        # Chi-square test
        contingency = [[sum(control), len(control) - sum(control)],
                       [sum(treatment), len(treatment) - sum(treatment)]]
        chi2, p_value, _, _ = chi2_contingency(contingency)
        
    else:
        # T-test for continuous metrics
        t_stat, p_value = ttest_ind(control, treatment)
        lift = (np.mean(treatment) - np.mean(control)) / np.mean(control) * 100
    
    return {
        "control_rate": np.mean(control),
        "treatment_rate": np.mean(treatment),
        "lift_pct": lift,
        "p_value": p_value,
        "significant": p_value < 0.05,
        "confidence": (1 - p_value) * 100,
        "recommendation": "Ship treatment" if p_value < 0.05 and lift > 0 else "Keep control",
    }
```

## Dashboard/Report Prompt
```python
REPORT_PROMPT = """
You are Ethan Yates, MAARS Data Analyst.

Create an executive report from this data:
{data_summary}

Structure:
1. EXECUTIVE SUMMARY (3 bullet points, key numbers)
2. KEY METRICS vs Previous Period (table with % change, trend arrow)
3. TOP INSIGHTS (3-5 data-backed findings)
4. ANOMALIES & ALERTS (anything >2 std deviations from norm)
5. RECOMMENDED ACTIONS (specific, measurable, time-bound)
6. APPENDIX: Methodology notes

Tone: Clear, concise, executive-level. No jargon. Lead with the "so what".
"""
```

## Models to Use
- **Statistical analysis + code**: `gpt-4o` with code interpreter
- **Report writing**: `claude-sonnet-4-6`
- **SQL generation**: `gpt-4o` or `deepseek-chat` (excellent at SQL)
- **Predictions/ML**: `o3` or `gpt-5.2`
