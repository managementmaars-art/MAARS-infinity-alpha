---
name: real-estate-ai
description: AI real estate skills — property valuation, listing descriptions, market analysis, investment analysis, lead generation, MLS integration, mortgage calculations for MAARS real estate agents
---

# Real Estate AI — MAARS Reference

## Property Listing Generator
```python
LISTING_PROMPT = """
You are a top real estate copywriter. Write a compelling property listing.

Property details:
Address: {address}
Type: {property_type} (single-family/condo/townhouse/multi-family/commercial)
Bedrooms: {beds} | Bathrooms: {baths}
Sq ft: {sqft} | Lot: {lot_size}
Year built: {year_built}
Price: ${price:,}
Key features: {features}
Neighborhood: {neighborhood}
School district: {school_district}
Recent upgrades: {upgrades}

Write:
1. HEADLINE (8-12 words): Benefit-led, emotional hook
2. OPENING (50 words): Paint the lifestyle, not the house
3. FEATURE HIGHLIGHTS (5-7 bullets): Unique selling points
4. NEIGHBORHOOD SECTION (40 words): Community, walkability, access
5. CALL TO ACTION: Create urgency

Avoid: passive voice, clichés ("move-in ready", "motivated seller"), exact age of items
Tone: {tone} (luxury/family-friendly/investment/modern-urban)
"""
```

## Property Valuation (CMA)
```python
CMA_PROMPT = """
Perform a Comparative Market Analysis for: {subject_property}

Subject property:
{property_details}

Comparables provided:
{comps}

Analyze each comp:
1. SIMILARITY SCORE: How comparable (1-10)
2. ADJUSTMENTS needed:
   - Location ($per mile, school district premium)
   - Size ($/sqft difference)
   - Age/condition (cost approach adjustments)
   - Features (garage, pool, view: market value)
3. ADJUSTED SALE PRICE: After adjustments

Final:
- PRICE RANGE: Low / Mid / High
- RECOMMENDED LIST PRICE: With rationale
- DAYS ON MARKET: Expected based on comps
- STRATEGY: Pricing to sell vs. pricing to negotiate
"""

def calculate_arv(purchase_price: float, rehab_cost: float, 
                   comp_avg_price: float) -> dict:
    """After Repair Value calculation for flippers"""
    arv = comp_avg_price
    max_purchase = (arv * 0.70) - rehab_cost  # 70% rule
    profit_potential = arv - purchase_price - rehab_cost
    roi = profit_potential / (purchase_price + rehab_cost) * 100
    return {
        "arv": arv,
        "max_purchase_70_rule": max_purchase,
        "estimated_profit": profit_potential,
        "roi_percent": roi,
        "deal_quality": "Good" if roi > 20 else "Marginal" if roi > 10 else "Pass",
    }
```

## Investment Analysis
```python
def analyze_rental_property(data: dict) -> dict:
    """Full rental property investment analysis"""
    # Income
    gross_rental_income = data["monthly_rent"] * 12
    vacancy_loss = gross_rental_income * (data.get("vacancy_rate", 0.05))
    effective_gross_income = gross_rental_income - vacancy_loss
    
    # Expenses
    property_tax = data["purchase_price"] * data.get("tax_rate", 0.012)
    insurance = data["purchase_price"] * data.get("insurance_rate", 0.005)
    maintenance = gross_rental_income * 0.10
    management = gross_rental_income * data.get("mgmt_rate", 0.10)
    capex = gross_rental_income * 0.05  # Capital expenditures reserve
    
    total_expenses = property_tax + insurance + maintenance + management + capex
    noi = effective_gross_income - total_expenses
    
    # Mortgage
    loan = data["purchase_price"] * (1 - data.get("down_payment", 0.20))
    monthly_payment = (loan * (data["interest_rate"]/12) * 
                      (1 + data["interest_rate"]/12)**360) / \
                     ((1 + data["interest_rate"]/12)**360 - 1)
    annual_debt_service = monthly_payment * 12
    
    # Returns
    cash_flow = noi - annual_debt_service
    cap_rate = noi / data["purchase_price"] * 100
    cash_on_cash = cash_flow / (data["purchase_price"] * data.get("down_payment", 0.20)) * 100
    dscr = noi / annual_debt_service
    
    return {
        "gross_rental_income": gross_rental_income,
        "effective_gross_income": effective_gross_income,
        "noi": noi,
        "annual_cash_flow": cash_flow,
        "monthly_cash_flow": cash_flow / 12,
        "cap_rate": f"{cap_rate:.2f}%",
        "cash_on_cash_return": f"{cash_on_cash:.2f}%",
        "dscr": f"{dscr:.2f}",
        "verdict": "Good" if cash_on_cash > 8 and dscr > 1.25 else "Marginal" if dscr > 1.0 else "Negative Cash Flow",
    }
```

## Market Analysis
```python
MARKET_ANALYSIS_PROMPT = """
Real estate market analysis for: {market} ({zip_codes})
Time period: {period}
Property type: {property_type}

Analyze:
1. SUPPLY METRICS:
   - Months of inventory (>6 = buyer's market, <3 = seller's)
   - Days on market trend
   - New listings vs. absorption rate
   - Price reduction frequency

2. DEMAND INDICATORS:
   - Sale-to-list price ratio
   - Multiple offer situations
   - Migration patterns (in vs. out flow)
   - Job market / employer announcements

3. PRICE TRENDS:
   - YoY appreciation
   - Price per sqft by submarket
   - Luxury vs. entry-level divergence

4. FORECAST (6-12 months):
   - Interest rate sensitivity
   - New construction pipeline
   - Economic headwinds/tailwinds

5. OPPORTUNITY ZONES:
   - Neighborhoods with highest upside
   - Asset classes outperforming
"""
```

## Lead Generation & CRM
```python
LEAD_NURTURE_SEQUENCES = {
    "buyer_lead": {
        "day_0": "Welcome email + market report for their search area",
        "day_3": "New listings matching their criteria",
        "day_7": "Buyer's guide + mortgage calculator",
        "day_14": "Neighborhood spotlight video",
        "day_21": "Open house invitations",
        "day_30": "Check-in + 'what's your timeline?'",
        "monthly": "Market update newsletter",
    },
    "seller_lead": {
        "day_0": "Instant CMA + listing presentation request",
        "day_3": "Recent sales in their neighborhood",
        "day_7": "Home staging tips + value-add ideas",
        "day_14": "Case study: similar home sold above ask",
        "day_21": "Market timing analysis",
        "day_30": "Direct ask: 'Ready for a no-obligation conversation?'",
    },
}

AI_LEAD_SCORING = {
    "hot": "Pre-approved, specific area, 0-90 day timeline",
    "warm": "Active search, vague timeline, no pre-approval",
    "cold": "Just browsing, 6+ months, no specific criteria",
    "scoring_signals": [
        "Website pages visited", "Listings favorited",
        "Open rate on emails", "Response to texts",
        "Mortgage calculator usage", "School search activity",
    ],
}
```

## MLS & Zillow API
```python
# Zillow API (RapidAPI)
import requests

def search_zillow(location: str, min_price: int, max_price: int, beds: int):
    return requests.get(
        "https://zillow-com1.p.rapidapi.com/propertyExtendedSearch",
        headers={
            "X-RapidAPI-Key": RAPIDAPI_KEY,
            "X-RapidAPI-Host": "zillow-com1.p.rapidapi.com"
        },
        params={
            "location": location,
            "minPrice": min_price,
            "maxPrice": max_price,
            "bedsMin": beds,
            "status_type": "ForSale",
            "home_type": "Houses,Townhomes,Condos",
        }
    ).json()

def get_zestimate(zpid: str):
    return requests.get(
        f"https://zillow-com1.p.rapidapi.com/property",
        headers={"X-RapidAPI-Key": RAPIDAPI_KEY,
                 "X-RapidAPI-Host": "zillow-com1.p.rapidapi.com"},
        params={"zpid": zpid}
    ).json()
```

## Mortgage Calculations
```python
def mortgage_calculator(home_price: float, down_pct: float, 
                         rate: float, years: int = 30) -> dict:
    loan = home_price * (1 - down_pct)
    monthly_rate = rate / 12
    n = years * 12
    payment = loan * (monthly_rate * (1 + monthly_rate)**n) / ((1 + monthly_rate)**n - 1)
    total_paid = payment * n
    return {
        "loan_amount": loan,
        "monthly_payment": payment,
        "total_interest": total_paid - loan,
        "total_cost": total_paid + (home_price * down_pct),
    }

def affordability_calculator(annual_income: float, monthly_debts: float,
                               rate: float, years: int = 30) -> dict:
    """28/36 rule affordability"""
    max_housing_28 = (annual_income / 12) * 0.28
    max_total_debt_36 = (annual_income / 12) * 0.36
    max_housing_36 = max_total_debt_36 - monthly_debts
    max_monthly_payment = min(max_housing_28, max_housing_36)
    monthly_rate = rate / 12
    n = years * 12
    max_loan = max_monthly_payment * ((1 + monthly_rate)**n - 1) / \
               (monthly_rate * (1 + monthly_rate)**n)
    return {"max_monthly_payment": max_monthly_payment,
            "max_loan": max_loan,
            "max_home_price_20pct_down": max_loan / 0.80}
```

## Models to Use
- **Listing descriptions**: `claude-sonnet-4-6` (best real estate copywriting)
- **CMA / valuation**: `gpt-4o` (structured analysis + calculations)
- **Market reports**: `perplexity/sonar-pro` (real-time data)
- **Investment analysis**: `gpt-4o` with code tools (financial modeling)
- **Lead communication**: `claude-sonnet-4-6` (personalized, empathetic)
