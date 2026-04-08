---
name: energy-ai
description: AI energy skills — energy trading, grid management, renewable forecasting, demand response, utility analytics, power systems modeling for MAARS energy agents
---

# Energy AI — MAARS Reference

## Energy Demand Forecasting
```python
DEMAND_FORECAST_PROMPT = """
Forecast energy demand for: {utility_or_region}
Period: {forecast_period} (day-ahead/week-ahead/seasonal)
Data available: {data_types}

Historical patterns provided:
{historical_data}

Generate forecast considering:
1. WEATHER IMPACT:
   - Temperature correlation (heating/cooling degree days)
   - Humidity effect (A/C load)
   - Daylight hours (lighting load)

2. TEMPORAL PATTERNS:
   - Hour-of-day profile
   - Day-of-week pattern
   - Seasonal baseline
   - Holidays/events

3. STRUCTURAL CHANGES:
   - EV charging growth (% of fleet electrified × avg load)
   - Heat pump adoption
   - Data center growth in region
   - Industrial load changes

4. ECONOMIC INDICATORS:
   - GDP/industrial activity correlation
   - Population growth

OUTPUT:
- Point forecast (MW) for each hour
- Confidence intervals (P10/P50/P90)
- Peak demand prediction
- Energy (MWh) total for period
- Key risk factors
"""

import numpy as np
from sklearn.ensemble import GradientBoostingRegressor

def train_demand_forecast_model(features: np.ndarray, demand: np.ndarray):
    """Simple ML demand forecast"""
    model = GradientBoostingRegressor(
        n_estimators=500, max_depth=4, learning_rate=0.05,
        subsample=0.8, random_state=42
    )
    model.fit(features, demand)
    return model

def create_forecast_features(datetime_series, temp_series, is_holiday) -> np.ndarray:
    """Feature engineering for demand forecast"""
    features = np.column_stack([
        datetime_series.hour,
        datetime_series.dayofweek,
        datetime_series.month,
        temp_series,
        temp_series ** 2,  # Non-linear temp response
        (temp_series - 18).clip(0),  # Cooling degree hours
        (18 - temp_series).clip(0),  # Heating degree hours
        is_holiday.astype(int),
    ])
    return features
```

## Renewable Energy Forecasting
```python
RENEWABLE_FORECAST_PROMPT = """
Forecast renewable energy production:
Asset type: {asset_type} (solar_pv/wind_onshore/wind_offshore)
Location: {lat}, {lon}
Installed capacity: {capacity_mw} MW
Weather forecast: {weather_data}

For solar PV:
- GHI (Global Horizontal Irradiance) → POA (Plane of Array)
- Panel efficiency + temperature derating
- Inverter losses
- Shading/soiling factor

For wind:
- Wind speed at hub height (from 10m using log law or power law)
- Power curve application
- Turbine cut-in/rated/cut-out speeds
- Wake effect losses for wind farms
- Turbulence intensity correction

Output:
- Hourly P50 production (MWh)
- P10/P90 range (uncertainty)
- Capacity factor for period
- Curtailment risk assessment
"""

def wind_power_output(wind_speed_ms: float, power_curve: dict,
                       capacity_mw: float) -> float:
    """Calculate wind turbine output from power curve"""
    cut_in = power_curve.get("cut_in", 3.0)
    rated = power_curve.get("rated_speed", 12.0)
    cut_out = power_curve.get("cut_out", 25.0)
    rated_power = capacity_mw
    
    if wind_speed_ms < cut_in or wind_speed_ms > cut_out:
        return 0.0
    elif wind_speed_ms >= rated:
        return rated_power
    else:
        # Cubic relationship in the partial load region
        return rated_power * ((wind_speed_ms - cut_in) / (rated - cut_in)) ** 3

def solar_pv_output(ghi: float, temp_c: float, capacity_mwp: float,
                     tilt: float = 30, azimuth: float = 180) -> float:
    """Simplified solar PV output calculation"""
    pr = 0.85  # Performance ratio (typical)
    temp_coeff = -0.004  # %/°C power loss above 25°C
    temp_derating = 1 + temp_coeff * (temp_c - 25)
    irradiance_factor = ghi / 1000  # Normalize to STC (1000 W/m²)
    return capacity_mwp * irradiance_factor * pr * max(0.7, temp_derating)
```

## Energy Trading & Market Analysis
```python
ENERGY_TRADING_PROMPT = """
Analyze energy market opportunity:
Market: {market} (ERCOT/PJM/CAISO/MISO/NYISO/UK_EPEX)
Product: {product} (day-ahead/real-time/ancillary/capacity)
Position: {position} (long/short, MW quantity)
Time period: {period}

Market analysis:
1. PRICE FORECAST:
   - Forward curve vs. model forecast
   - Weather-related price risk
   - Congestion points

2. SUPPLY/DEMAND BALANCE:
   - Generation outages (planned + forced)
   - Demand forecast vs. normal
   - Import/export flows

3. RENEWABLE IMPACT:
   - Solar/wind forecast and price depression risk
   - Duck curve timing (CAISO afternoon ramp)
   - Negative price risk

4. ANCILLARY SERVICES:
   - Frequency regulation opportunity
   - Spinning reserves requirements
   - Voltage support needs

5. TRADE RECOMMENDATION:
   - Entry point and rationale
   - Risk limits (stop loss)
   - Expected P&L scenario analysis
"""

# EIA API — US energy data
import requests

def get_eia_data(series_id: str, start: str, end: str):
    """Fetch US energy statistics from EIA"""
    return requests.get(
        "https://api.eia.gov/v2/electricity/rto/region-data/data/",
        params={
            "api_key": EIA_API_KEY,
            "frequency": "hourly",
            "data[0]": "value",
            "facets[respondent][]": series_id,
            "start": start, "end": end,
            "sort[0][column]": "period",
            "sort[0][direction]": "desc",
        }
    ).json()
```

## Demand Response Optimization
```python
DEMAND_RESPONSE_PROMPT = """
Design a demand response program:
Utility: {utility}
Peak demand: {peak_demand_mw} MW
DR target: {dr_target_mw} MW reduction
Customer segments: {segments}
Event trigger: {trigger} (price/reliability/emergency)

Program design:
1. CUSTOMER SEGMENTATION:
   - Large industrial (>1MW) — direct control
   - Commercial (100kW-1MW) — automated + manual
   - Small commercial/residential — behavioral + smart devices

2. LOAD REDUCTION STRATEGIES BY SEGMENT:
   - HVAC setback (2-4°F for 30-60 min)
   - Lighting reduction (10-20%)
   - Industrial process shifting
   - EV charging curtailment
   - Battery storage dispatch

3. INCENTIVE STRUCTURE:
   - Capacity payment ($/kW-month)
   - Performance payment ($/MWh curtailed)
   - Enrollment bonus
   - Penalty for non-performance

4. AUTOMATION:
   - Smart thermostat integration (Ecobee/Nest API)
   - Industrial SCADA integration
   - EV charger API (OCPP protocol)
   - Smart meter AMI commands

5. VERIFICATION:
   - Baseline calculation methodology
   - Measurement & verification (M&V) protocol
   - Settlement process
"""

def calculate_demand_response_baseline(hourly_load: list, 
                                        event_day: str, 
                                        method: str = "CAISO_10_in_10") -> float:
    """Calculate baseline load for DR settlement"""
    if method == "CAISO_10_in_10":
        # Average of highest 10 of last 10 non-event days
        sorted_days = sorted(hourly_load, reverse=True)
        return sum(sorted_days[:10]) / 10
    elif method == "unadjusted_matching":
        # Same hours on matching days (same weekday)
        return sum(hourly_load) / len(hourly_load)
```

## Grid Stability & Power Quality
```python
GRID_ANALYSIS_PROMPT = """
Analyze power system stability for: {network}
Scenario: {scenario}

Grid data:
{grid_parameters}

Assess:
1. FREQUENCY STABILITY:
   - Inertia level (H constant)
   - Rate of Change of Frequency (RoCoF) risk
   - Frequency nadir estimate
   - Required fast frequency response

2. VOLTAGE STABILITY:
   - P-V curves for critical buses
   - Reactive power margins
   - Undervoltage load shedding requirements

3. THERMAL LIMITS:
   - Overloaded lines/transformers
   - N-1 contingency analysis
   - Cable ampacity margins

4. SHORT CIRCUIT LEVELS:
   - Available fault current vs. equipment ratings
   - Protection coordination issues

5. RENEWABLE INTEGRATION:
   - System strength at connection point
   - Harmonic distortion concerns
   - Protection setting requirements

RECOMMENDATIONS: Grid reinforcement priorities
"""
```

## Models to Use
- **Demand forecasting**: `gpt-4o` with code tools (time series + regression)
- **Energy market analysis**: `claude-opus-4-6` (complex market dynamics)
- **Grid operations**: `claude-opus-4-6` (power systems engineering)
- **Regulatory analysis**: `perplexity/sonar-pro` (current energy policy)
- **Renewable forecasting**: `gpt-4o` + physics models
- **Energy trading strategy**: `claude-opus-4-6` (risk + market reasoning)
