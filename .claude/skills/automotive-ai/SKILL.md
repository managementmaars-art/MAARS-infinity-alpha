---
name: automotive-ai
description: AI automotive skills — vehicle diagnostics, EV analysis, dealer inventory, automotive content, fleet management, connected car, autonomous driving for MAARS automotive agents
---

# Automotive AI — MAARS Reference

## Vehicle Diagnostics Assistant
```python
DIAGNOSTIC_PROMPT = """
Analyze vehicle diagnostic information.
Vehicle: {year} {make} {model} ({engine})
Mileage: {mileage}
Symptoms: {symptoms}
OBD-II codes: {dtc_codes}
Freeze frame data: {freeze_frame}
Recent service: {recent_service}

Diagnose:
1. PRIMARY ISSUE: Most likely root cause
2. SUPPORTING EVIDENCE: Why this code/symptom combination
3. RELATED SYSTEMS: Other systems that may be affected
4. RISK LEVEL: Drive safely / Drive to shop soon / Don't drive
5. REPAIR ESTIMATE: Parts + labor (both dealer and independent)
6. DIY DIFFICULTY: For mechanically inclined owners
7. SECONDARY CAUSES: Other possibilities to rule out
8. PREVENTIVE ACTIONS: What to check/change to prevent recurrence

Common DTC context:
P0xxx: Powertrain | B0xxx: Body | C0xxx: Chassis | U0xxx: Network
"""

OBD_SEVERITY = {
    "P0300": "Random/Multiple Cylinder Misfire — HIGH (engine damage risk)",
    "P0420": "Catalyst System Efficiency Below Threshold — MEDIUM (emissions)",
    "P0171": "System Too Lean Bank 1 — MEDIUM (watch for P0174 too)",
    "P0128": "Coolant Temperature Below Thermostat Regulating Temperature — LOW",
    "P0442": "Evaporative Emission System Leak (small) — LOW (usually gas cap)",
    "P0101": "Mass Airflow Sensor Range/Performance — MEDIUM",
    "P0340": "Camshaft Position Sensor — HIGH (no-start risk)",
}
```

## Electric Vehicle Analysis
```python
EV_ANALYSIS_PROMPT = """
Provide comprehensive EV analysis for:
Vehicle: {ev_model}
Driver profile: {driver_profile}
Location: {location}
Current vehicle: {current_vehicle}
Daily mileage: {daily_miles} miles
Annual mileage: {annual_miles} miles

Analyze:
1. RANGE ASSESSMENT:
   - EPA range vs. real-world (typically 15-20% less)
   - Range in {location} climate (cold reduces 20-40%)
   - Range anxiety risk for daily usage
   - Charging frequency needed

2. TOTAL COST OF OWNERSHIP (5 years):
   - Purchase price - federal credit ($7,500 if eligible)
   - State incentives for {location}
   - Fuel savings (kWh cost vs. gasoline)
   - Insurance (EVs typically +15-20%)
   - Maintenance savings (no oil, fewer brakes due to regen)
   - Battery replacement risk/cost

3. HOME CHARGING:
   - Level 1 (120V) — miles per hour charged
   - Level 2 (240V) — installation cost + charging speed
   - Recommended charger for this vehicle

4. PUBLIC CHARGING NETWORK:
   - Available networks in {location} (DCFC coverage)
   - Charging speed at max DC rate
   - Road trip feasibility

5. GRID CARBON IMPACT:
   - CO2 emissions vs. {current_vehicle} in {location}'s grid mix
"""

def ev_cost_comparison(ev_price: float, ice_price: float,
                        annual_miles: int, electricity_rate: float,
                        gas_price: float, ev_mpge: float, ice_mpg: float) -> dict:
    ev_fuel_annual = (annual_miles / ev_mpge) * electricity_rate * 33.7  # kWh
    ice_fuel_annual = (annual_miles / ice_mpg) * gas_price
    annual_savings = ice_fuel_annual - ev_fuel_annual
    ev_maintenance_savings = 800  # Annual avg
    price_premium = ev_price - ice_price
    breakeven_years = price_premium / (annual_savings + ev_maintenance_savings)
    return {
        "ev_annual_fuel_cost": ev_fuel_annual,
        "ice_annual_fuel_cost": ice_fuel_annual,
        "annual_fuel_savings": annual_savings,
        "5yr_total_savings": (annual_savings + ev_maintenance_savings) * 5,
        "breakeven_years": round(breakeven_years, 1),
    }
```

## Dealer Inventory Management
```python
INVENTORY_ANALYSIS_PROMPT = """
Analyze dealer inventory performance:
Dealership: {dealership}
Period: {period}
Inventory data: {inventory_data}

Evaluate:
1. DAYS SUPPLY: By model (target: 45-60 days)
2. AGING ANALYSIS:
   - 0-30 days: Fresh
   - 31-60 days: Monitor
   - 61-90 days: Price action needed
   - 90+ days: Aged units (floor plan cost accumulating)

3. TURN RATE: Annual turns by model (target: 12+)

4. PRICE PERFORMANCE:
   - Market days supply vs. list price
   - Units priced above/at/below market
   - Price adjustment recommendations per VIN

5. MIX OPTIMIZATION:
   - Which models/trims are in demand vs. supply
   - Acquisition recommendations for wholesale/trade

6. FLOOR PLAN COST: Estimated interest cost on aged units

Pricing framework:
- <15 days supply: Can hold + or go above MSRP
- 15-45 days: Market price
- 45-60 days: Incentivize
- 60+ days: Aggressive discount + push to wholesale
"""

def calculate_floor_plan_cost(unit_cost: float, days_on_lot: int, 
                               rate: float = 0.065) -> float:
    """Daily floor plan carrying cost"""
    daily_cost = unit_cost * (rate / 365)
    return daily_cost * days_on_lot
```

## Automotive Content Generation
```python
VEHICLE_REVIEW_PROMPT = """
Write a comprehensive vehicle review.
Vehicle: {year} {make} {model} {trim}
Testing context: {context}
Target reader: {audience} (enthusiast/family buyer/commuter/luxury)

Structure:
1. VERDICT (50 words): Quick take for skimmers
2. DRIVING IMPRESSIONS:
   - Engine/powertrain character
   - Handling and ride quality
   - Steering feel
   - Braking
3. INTERIOR:
   - Quality and materials
   - Technology and infotainment
   - Comfort and space
   - Cargo capacity
4. PRACTICALITY:
   - Fuel economy (real-world)
   - Features vs. competition
   - Ownership costs
5. COMPETITORS: vs. top 3 alternatives
6. WHO SHOULD BUY IT: Ideal buyer profile
7. WHO SHOULDN'T: Honest limitations
8. SCORE: /10 with reasoning

Style: {style} (analytical/enthusiast/consumer-friendly)
"""
```

## Fleet Management AI
```python
FLEET_OPTIMIZATION_PROMPT = """
Optimize fleet management for:
Fleet size: {fleet_size} vehicles
Vehicle types: {vehicle_types}
Operations: {operations_type}
Annual mileage per vehicle: {avg_mileage}
Current issues: {issues}

Analyze and recommend:
1. REPLACEMENT CYCLE:
   - Optimal age/mileage to replace (TCO-based)
   - EV transition candidates
   - Which units to prioritize for replacement

2. MAINTENANCE OPTIMIZATION:
   - Predictive maintenance schedule
   - High-failure items by vehicle type
   - Preferred service intervals

3. FUEL/ENERGY:
   - Current cost per mile/km
   - EV charging infrastructure needs
   - Route optimization for EV range

4. TELEMATICS INSIGHTS:
   - Driver behavior scoring
   - Idling reduction potential
   - Speed compliance

5. INSURANCE OPTIMIZATION:
   - Fleet discount opportunities
   - Risk reduction measures
   - Claims pattern analysis

PROJECTED SAVINGS: Annual cost reduction with recommendations
"""
```

## Connected Car & APIs
```python
# Tesla API (unofficial)
from teslapy import Tesla

def get_tesla_state(email: str):
    tesla = Tesla(email)
    vehicles = tesla.vehicle_list()
    v = vehicles[0]
    v.sync_wake_up()
    return {
        "battery_level": v["charge_state"]["battery_level"],
        "range_miles": v["charge_state"]["battery_range"],
        "charging": v["charge_state"]["charging_state"],
        "climate_on": v["climate_state"]["is_climate_on"],
        "locked": v["vehicle_state"]["locked"],
        "odometer": v["vehicle_state"]["odometer"],
    }

# SmartCar API — multi-brand connected car
import smartcar

client = smartcar.AuthClient(
    client_id=SMARTCAR_CLIENT_ID,
    client_secret=SMARTCAR_CLIENT_SECRET,
    redirect_uri="https://your-app.com/callback"
)

def get_vehicle_data(access_token: str, vehicle_id: str) -> dict:
    vehicle = smartcar.Vehicle(vehicle_id, access_token)
    return {
        "odometer": vehicle.odometer().distance,
        "fuel": vehicle.fuel().percent_remaining if hasattr(vehicle, 'fuel') else None,
        "battery": vehicle.battery().percent_remaining if hasattr(vehicle, 'battery') else None,
        "location": vehicle.location(),
    }
```

## Models to Use
- **Vehicle diagnostics**: `claude-opus-4-6` (technical reasoning + safety)
- **EV analysis**: `gpt-4o` (calculations + data analysis)
- **Inventory analysis**: `gpt-4o` with code tools
- **Vehicle reviews**: `claude-sonnet-4-6` (engaging automotive writing)
- **Fleet optimization**: `claude-opus-4-6` (complex TCO analysis)
- **Automotive news/specs**: `perplexity/sonar-pro` (current model data)
