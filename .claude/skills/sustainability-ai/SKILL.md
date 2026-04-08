---
name: sustainability-ai
description: AI sustainability skills — ESG reporting, carbon footprint, lifecycle analysis, green supply chain, renewable energy, circular economy for MAARS sustainability agents
---

# Sustainability AI — MAARS Reference

## ESG Reporting
```python
ESG_REPORT_PROMPT = """
Generate an ESG (Environmental, Social, Governance) report section.
Company: {company_name}
Industry: {industry}
Reporting framework: {framework} (GRI/SASB/TCFD/UN SDGs/CDP)
Reporting period: {period}
Data provided: {esg_data}

Structure per GRI Standards:
ENVIRONMENTAL:
- Energy consumption (MWh) + renewable % 
- GHG emissions (Scope 1/2/3 in tCO2e)
- Water withdrawal and discharge
- Waste generated and diversion rate
- Biodiversity impacts

SOCIAL:
- Total employees + diversity breakdown
- Employee turnover rate
- Lost Time Injury Rate (LTIR)
- Community investment ($)
- Supply chain audits completed

GOVERNANCE:
- Board composition (diversity, independence)
- Executive pay ratio
- Anti-corruption policies
- Data privacy compliance

For each metric:
- Current year figure
- YoY change
- Industry benchmark comparison
- 2030 target progress
"""
```

## Carbon Footprint Calculator
```python
EMISSION_FACTORS = {
    "electricity_grid": {
        "US_avg": 0.386,       # kgCO2e/kWh
        "EU_avg": 0.231,
        "solar": 0.020,
        "wind": 0.011,
        "nuclear": 0.012,
        "coal": 0.820,
        "natural_gas": 0.490,
    },
    "transport": {
        "car_gasoline_per_km": 0.192,
        "car_electric_per_km": 0.053,
        "flight_short_haul_per_pkm": 0.255,
        "flight_long_haul_per_pkm": 0.195,
        "train_per_pkm": 0.041,
        "shipping_sea_per_tonne_km": 0.016,
        "shipping_air_per_tonne_km": 0.602,
        "shipping_truck_per_tonne_km": 0.096,
    },
    "food": {
        "beef_per_kg": 27.0,
        "pork_per_kg": 12.1,
        "chicken_per_kg": 6.9,
        "fish_per_kg": 6.1,
        "dairy_milk_per_liter": 3.2,
        "vegetables_per_kg": 2.0,
        "rice_per_kg": 2.7,
        "legumes_per_kg": 0.9,
    },
    "manufacturing": {
        "steel_per_tonne": 1850,
        "aluminum_per_tonne": 11900,
        "cement_per_tonne": 820,
        "plastic_pet_per_tonne": 3400,
        "cotton_textile_per_kg": 15.0,
    },
}

def calculate_carbon_footprint(activities: dict) -> dict:
    """Calculate tCO2e from activity data"""
    total = 0
    breakdown = {}
    
    if "electricity_kwh" in activities:
        grid = activities.get("grid_type", "US_avg")
        co2 = activities["electricity_kwh"] * EMISSION_FACTORS["electricity_grid"][grid]
        breakdown["electricity"] = co2
        total += co2
    
    if "flights" in activities:
        for flight in activities["flights"]:
            factor = (EMISSION_FACTORS["transport"]["flight_long_haul_per_pkm"] 
                     if flight["distance_km"] > 3000 
                     else EMISSION_FACTORS["transport"]["flight_short_haul_per_pkm"])
            co2 = flight["passengers"] * flight["distance_km"] * factor
            breakdown.setdefault("flights", 0)
            breakdown["flights"] += co2
            total += co2
    
    return {
        "total_kgCO2e": total,
        "total_tCO2e": total / 1000,
        "breakdown": breakdown,
        "offset_cost_usd": (total / 1000) * 15,  # ~$15/tonne
    }
```

## Lifecycle Assessment (LCA)
```python
LCA_PROMPT = """
Perform a simplified Lifecycle Assessment for: {product}
Functional unit: {functional_unit}
System boundary: {boundary} (cradle-to-grave/cradle-to-gate/gate-to-grave)

Analyze each life stage:
1. RAW MATERIAL EXTRACTION:
   - Materials required
   - Extraction impacts (water, land, energy)
   - Depletion of non-renewable resources

2. MANUFACTURING:
   - Energy inputs (type and quantity)
   - Water consumption
   - Waste generated
   - Chemical releases

3. DISTRIBUTION & TRANSPORT:
   - Distance and mode of transport
   - Packaging materials and weight

4. USE PHASE:
   - Energy/water consumed during use
   - Consumables required
   - Maintenance needs
   - Expected product lifespan

5. END OF LIFE:
   - Recyclability %
   - Biodegradability
   - Hazardous material disposal
   - Take-back program availability

IMPACT CATEGORIES:
- Global warming potential (kgCO2e)
- Water consumption (liters)
- Land use (m²·year)
- Particulate matter formation
- Eutrophication potential

HOTSPOTS: Top 3 stages driving environmental impact
IMPROVEMENT OPPORTUNITIES: Ranked by impact reduction potential
"""
```

## Green Supply Chain
```python
SUPPLY_CHAIN_SUSTAINABILITY_PROMPT = """
Analyze and improve supply chain sustainability for: {company}
Industry: {industry}
Tier 1 suppliers: {tier1_count}
Geographic spread: {regions}

Current data:
{supplier_data}

Evaluate:
1. SCOPE 3 EMISSIONS:
   - Purchased goods & services (highest category typically)
   - Transportation & distribution
   - Business travel
   - Waste in operations
   - Use of sold products

2. SUPPLIER RISK MAPPING:
   - Climate physical risk (floods, drought in their regions)
   - Regulatory risk (carbon pricing exposure)
   - Social risk (labor standards, human rights)

3. SUPPLIER SCORECARD (per supplier):
   - Environmental certifications held
   - GHG reduction targets
   - Water stewardship
   - Social compliance audits

4. RECOMMENDATIONS:
   - Supplier development program priorities
   - Near-shoring opportunities (vs. carbon cost of distant sourcing)
   - Material substitution for lower-impact options
   - Circular economy opportunities
"""
```

## Renewable Energy Analysis
```python
ENERGY_TRANSITION_PROMPT = """
Analyze renewable energy transition for: {organization}
Current energy mix: {energy_mix}
Annual consumption: {consumption_mwh} MWh
Location: {location}
Budget: ${budget}

Options to evaluate:
1. ON-SITE SOLAR:
   - Roof/land area available: {area} m²
   - Solar irradiance for {location}: [data]
   - Capacity potential: [calculation]
   - Payback period and IRR

2. WIND POWER:
   - Feasibility for location/context

3. PPAs (Power Purchase Agreements):
   - Virtual PPA vs. physical PPA
   - Available projects in {region}
   - Pricing: $/MWh vs. grid

4. RECs (Renewable Energy Certificates):
   - Market-based accounting
   - Cost per MWh

5. ENERGY STORAGE:
   - Battery backup sizing
   - Grid services revenue potential

6. ENERGY EFFICIENCY (first):
   - Quick wins to reduce consumption first
   - Technology upgrades (LED, HVAC, motors)

RECOMMENDED PATHWAY with timeline and budget
"""

def solar_roi_calculator(roof_area_m2: float, location_sun_hours: float,
                           electricity_rate: float, install_cost_per_kw: float) -> dict:
    panel_efficiency = 0.20
    capacity_kw = roof_area_m2 * panel_efficiency  # ~1kW per 5m²
    annual_production_kwh = capacity_kw * location_sun_hours * 365
    annual_savings = annual_production_kwh * electricity_rate
    total_cost = capacity_kw * install_cost_per_kw
    payback_years = total_cost / annual_savings
    irr_25yr = (annual_savings * 25 - total_cost) / total_cost * 100
    return {
        "capacity_kw": capacity_kw,
        "annual_production_kwh": annual_production_kwh,
        "annual_savings_usd": annual_savings,
        "total_install_cost": total_cost,
        "payback_years": payback_years,
        "co2_avoided_tonnes_year": annual_production_kwh * 0.386 / 1000,
    }
```

## Circular Economy Design
```python
CIRCULAR_DESIGN_PROMPT = """
Redesign this product/service for circular economy principles:
Product: {product}
Current model: {linear_model}
Target market: {market}

Apply circular economy strategies:
1. DESIGN FOR LONGEVITY:
   - Material durability improvements
   - Modular/repairable design
   - Upgrade paths

2. DESIGN FOR DISASSEMBLY:
   - Material separation feasibility
   - Fastener choices (screws not glue)
   - Material labeling for recycling

3. REVERSE LOGISTICS:
   - Take-back program design
   - Incentive structure for returns
   - Refurbishment process

4. NEW BUSINESS MODELS:
   - Product-as-a-service (PaaS)
   - Leasing/subscription
   - Certified refurbished tier

5. MATERIAL RECOVERY:
   - Recyclable materials %
   - Recycled content targets
   - Biological cycle (compostable)

BUSINESS CASE: Revenue from circular model vs. linear
CONSUMER COMMUNICATION: How to position sustainability
"""
```

## Models to Use
- **ESG reporting**: `claude-opus-4-6` (complex framework compliance)
- **Carbon calculations**: `gpt-4o` with code tools (precise math)
- **LCA analysis**: `claude-opus-4-6` (systems thinking)
- **Regulatory research**: `perplexity/sonar-pro` (current regulations)
- **Sustainability strategy**: `claude-opus-4-6` (strategic recommendations)
- **Sustainability communications**: `claude-sonnet-4-6` (clear, authentic)
