# SaaS Metrics & Business Logic Impact

## Core Formulas

### Revenue
```
MRR = Σ(active_subscriptions × monthly_rate)
ARR = MRR × 12
Net New MRR = New + Expansion - Contraction - Churned
```

### Churn
```
Customer Churn = Lost Customers / Starting Customers
Revenue Churn = Lost MRR / Starting MRR
NRR = (Start + Expansion - Contraction - Churn) / Start × 100
```
Benchmarks: Monthly <1% excellent, <3% acceptable, >5% critical

### Unit Economics
```
LTV = (ARPU × Gross Margin) / Monthly Churn
CAC = Sales + Marketing / New Customers
LTV:CAC = 3:1 healthy, <3:1 overspending, >5:1 underinvesting
CAC Payback = CAC / (ARPU × Margin) → Target <12 months
```

## Code → Metric Impact

### Patterns That Kill Conversion
| Pattern | Impact | Detection |
|---------|--------|-----------|
| Forced CC on trial | -20-40% trials | Signup flow |
| Complex onboarding | -50% activation | Step count |
| Email verification blocking | -10-30% signups | Funnel code |

### Patterns That Cause Churn
| Pattern | Impact | Detection |
|---------|--------|-----------|
| No grace period | +0.5-1% churn | Payment handling |
| Immediate lock on fail | Involuntary spike | Dunning logic |
| No win-back flow | Lost reactivation | Cancel triggers |

### Patterns That Hurt Expansion
| Pattern | Impact | Detection |
|---------|--------|-----------|
| Friction in upgrade | Lost expansion | Plan change code |
| No limit prompts | Missed triggers | Limit enforcement |

## Red Flags in Code

```javascript
// Conversion killer
if (!creditCard) return error('Required');

// Churn generator
if (paymentFailed) await lockAccount();

// Expansion blocker
// Complex multi-step upgrade with many failure points
```
