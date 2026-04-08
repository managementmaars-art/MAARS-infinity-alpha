---
name: finance-ai
description: AI-powered finance skills — financial modeling, forecasting, valuation, budget analysis, investment research, pitch decks, P&L analysis for MAARS finance agents
---

# Finance AI — MAARS Reference

## Core Financial Analysis Capabilities

### Financial Modeling Prompt Framework
```python
FINANCIAL_MODEL_PROMPT = """
You are Benjamin Cole, MAARS Financial Analyst.

Build a {model_type} financial model for {company}:
- Revenue drivers: {drivers}
- Time horizon: {years} years
- Scenarios: Base, Bull (+{bull_pct}%), Bear (-{bear_pct}%)

Output:
1. Revenue projection table (monthly/annual)
2. Cost structure breakdown
3. Unit economics (CAC, LTV, payback period)
4. Cash flow statement
5. Key assumptions and sensitivities
6. Break-even analysis
"""
```

### P&L Analysis Template
```
REVENUE ANALYSIS:
- MRR/ARR trend (12 months)
- Revenue by segment/product
- Churn rate and expansion revenue
- Net Revenue Retention

COST STRUCTURE:
- COGS → Gross Margin
- S&M as % of revenue
- R&D as % of revenue  
- G&A as % of revenue
- EBITDA margin

UNIT ECONOMICS:
- CAC by channel
- LTV (3-year)
- LTV:CAC ratio (target >3x)
- Payback period (target <18 months)
```

### Valuation Methods
```python
VALUATION_METHODS = {
    "DCF": {
        "inputs": ["revenue_forecast", "ebitda_margin", "wacc", "terminal_growth"],
        "best_for": "mature businesses with predictable cash flows",
    },
    "SaaS_multiple": {
        "inputs": ["ARR", "growth_rate", "NRR", "margin"],
        "formula": "ARR × (growth_rate / 0.1) × margin_multiplier",
        "benchmark_multiples": {"top_quartile": 12, "median": 6, "bottom": 3},
    },
    "Comparable_transactions": {
        "inputs": ["revenue", "ebitda", "industry_comps"],
        "best_for": "M&A scenarios",
    },
    "VC_method": {
        "inputs": ["exit_valuation", "dilution", "required_return"],
        "best_for": "early-stage startups",
    },
}
```

### Investment Memo Structure
```
EXECUTIVE SUMMARY (2 paragraphs)
MARKET OPPORTUNITY: TAM/SAM/SOM
BUSINESS MODEL: Revenue mechanics, unit economics
COMPETITIVE ANALYSIS: Moat, differentiation
TEAM: Relevant experience, domain expertise
TRACTION: Key metrics, growth rate, retention
FINANCIALS: Historical (if any), 3-year projections
USE OF FUNDS: Allocation, milestones unlocked
RISKS & MITIGATIONS: Top 3 risks
ASK: Amount, valuation, structure
```

### Budget vs Actual Analysis
```python
VARIANCE_ANALYSIS_PROMPT = """
Analyze this budget vs actual data:
{data}

For each line item:
1. Calculate variance ($ and %)
2. Flag items >10% off budget
3. Identify root causes
4. Recommend corrective actions
5. Update full-year forecast

Format as executive summary + detailed table.
"""
```

### Financial Ratios Reference
```python
KEY_RATIOS = {
    "liquidity": ["current_ratio", "quick_ratio", "cash_ratio"],
    "profitability": ["gross_margin", "ebitda_margin", "net_margin", "roe", "roa"],
    "efficiency": ["asset_turnover", "inventory_days", "receivables_days"],
    "leverage": ["debt_to_equity", "interest_coverage", "net_debt_to_ebitda"],
    "saas": ["arr", "mrr_growth", "churn_rate", "nrr", "magic_number", "rule_of_40"],
}
```

## Models to Use
- **Complex modeling**: `o3` or `gpt-5.2` (best at math/reasoning)
- **Report writing**: `claude-opus-4-6`
- **Data analysis**: `gpt-4o` with code interpreter
- **Quick calculations**: `deepseek-reasoner` (excellent math, cheap)
