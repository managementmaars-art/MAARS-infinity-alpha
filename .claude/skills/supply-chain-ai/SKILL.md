---
name: supply-chain-ai
description: AI supply chain skills — demand planning, inventory optimization, logistics, procurement, supplier risk, digital twins, warehouse automation for MAARS supply chain agents
---

# Supply Chain AI — MAARS Reference

## Demand Forecasting & Planning
```python
DEMAND_PLANNING_PROMPT = """
Generate demand forecast for: {product_or_sku}
Historical data: {sales_history}
Period: {forecast_horizon} months
Factors to consider:
- Seasonality: {seasonal_patterns}
- Promotions planned: {promotions}
- Market trends: {trends}
- External events: {events}

Provide:
1. POINT FORECAST: Monthly demand (units)
2. CONFIDENCE INTERVAL: P10/P50/P90 scenarios
3. SEASONALITY INDEX: Month-by-month adjustment factors
4. FORECAST ACCURACY TARGET: MAPE < {target_mape}%
5. KEY ASSUMPTIONS: What could make this forecast wrong
6. SAFETY STOCK RECOMMENDATION: Based on forecast error and service level target

Statistical methods applied:
- Moving average baseline
- Exponential smoothing (Holt-Winters for trend + seasonality)
- Machine learning overlay for external factors
"""

def calculate_safety_stock(avg_daily_demand: float, demand_std: float,
                            avg_lead_time: float, lead_time_std: float,
                            service_level: float = 0.95) -> dict:
    """Safety stock calculation with lead time variability"""
    import scipy.stats as stats
    z = stats.norm.ppf(service_level)  # z=1.65 for 95%
    
    # Combined variability formula
    safety_stock = z * ((avg_lead_time * demand_std**2) + 
                        (avg_daily_demand**2 * lead_time_std**2))**0.5
    
    reorder_point = (avg_daily_demand * avg_lead_time) + safety_stock
    
    return {
        "safety_stock_units": round(safety_stock),
        "reorder_point": round(reorder_point),
        "days_of_safety_stock": safety_stock / avg_daily_demand,
        "service_level": f"{service_level:.0%}",
    }
```

## Inventory Optimization
```python
def eoq_analysis(annual_demand: float, order_cost: float, 
                  holding_cost_pct: float, unit_cost: float) -> dict:
    """Economic Order Quantity analysis"""
    import math
    holding_cost = unit_cost * holding_cost_pct
    eoq = math.sqrt((2 * annual_demand * order_cost) / holding_cost)
    
    orders_per_year = annual_demand / eoq
    avg_inventory = eoq / 2
    total_ordering_cost = orders_per_year * order_cost
    total_holding_cost = avg_inventory * holding_cost
    total_cost = total_ordering_cost + total_holding_cost
    
    return {
        "eoq_units": round(eoq),
        "orders_per_year": round(orders_per_year, 1),
        "order_frequency_days": round(365 / orders_per_year),
        "avg_inventory_value": avg_inventory * unit_cost,
        "total_annual_cost": total_cost,
    }

INVENTORY_CLASSIFICATION = {
    "ABC_analysis": {
        "A_items": "Top 20% SKUs = 80% revenue → tight control, frequent review",
        "B_items": "Next 30% SKUs = 15% revenue → moderate control",
        "C_items": "Bottom 50% SKUs = 5% revenue → bulk ordering, less focus",
    },
    "XYZ_analysis": {
        "X_items": "Stable demand (CV < 0.5) → lean inventory",
        "Y_items": "Variable demand (CV 0.5-1.0) → moderate safety stock",
        "Z_items": "Irregular demand (CV > 1.0) → high safety stock or make-to-order",
    },
}
```

## Logistics Optimization
```python
LOGISTICS_PROMPT = """
Optimize logistics network for: {company}
Shipment data: {shipment_data}
Warehouse locations: {warehouses}
Customer locations: {customers}
Service level requirements: {sla} (next day / 2-day / standard)

Analyze and recommend:
1. NETWORK DESIGN:
   - Optimal warehouse locations (consider: cost, coverage, risk)
   - DC vs. cross-dock vs. 3PL mix
   - Last-mile strategy (own fleet / carrier / crowd-sourced)

2. ROUTE OPTIMIZATION:
   - Current vs. optimal routes
   - Load factor improvement opportunities
   - Multi-stop vs. direct shipment trade-offs

3. CARRIER MANAGEMENT:
   - Carrier mix (primary + backup per lane)
   - Rate benchmarking by mode/lane
   - Capacity risk mitigation

4. COST BREAKDOWN:
   - Transportation vs. warehousing vs. inventory carrying
   - Cost per unit/mile/order analysis
   - Savings opportunities ranked by impact

5. SUSTAINABILITY:
   - CO2 per shipment currently
   - Modal shift opportunities (truck → rail → sea)
   - Consolidated shipment opportunities
"""

def vehicle_routing_simple(stops: list, depot: tuple) -> list:
    """Nearest neighbor heuristic for VRP"""
    unvisited = stops.copy()
    route = [depot]
    current = depot
    
    while unvisited:
        nearest = min(unvisited, 
                     key=lambda s: ((s[0]-current[0])**2 + (s[1]-current[1])**2)**0.5)
        route.append(nearest)
        unvisited.remove(nearest)
        current = nearest
    
    route.append(depot)
    return route
```

## Procurement & Supplier Management
```python
SOURCING_ANALYSIS_PROMPT = """
Analyze sourcing strategy for: {category}
Current spend: ${spend}
Suppliers: {supplier_list}
Market data: {market_benchmarks}

Evaluate:
1. MARKET STRUCTURE:
   - Supplier concentration (HHI index)
   - Switching costs
   - Make vs. buy analysis

2. SUPPLIER SCORECARD:
   For each supplier:
   - Quality (defect rate, DPPM)
   - Delivery (OTIF %)
   - Responsiveness (lead time, communication)
   - Price competitiveness vs. market
   - Financial stability (risk rating)
   - Innovation capability

3. NEGOTIATION STRATEGY:
   - Price targets based on should-cost analysis
   - Volume consolidation opportunities
   - Long-term contract vs. spot purchase
   - Dual-source requirements (risk)

4. SHOULD-COST MODEL:
   - Material content
   - Labor cost (by manufacturing country)
   - Overhead + profit assumptions
   - Benchmark vs. current prices
"""

def supplier_risk_score(supplier: dict) -> dict:
    """Score supplier risk across dimensions"""
    scores = {
        "financial_risk": 10 - min(10, supplier.get("altman_z", 3) * 2),
        "geographic_risk": {"low": 2, "medium": 5, "high": 8}.get(
            supplier.get("geo_risk", "medium"), 5),
        "concentration_risk": min(10, supplier.get("revenue_pct_from_us", 0) / 10),
        "quality_risk": min(10, supplier.get("dppm", 1000) / 100),
        "delivery_risk": max(0, 10 - supplier.get("otif_pct", 95) / 10),
    }
    total = sum(scores.values()) / len(scores)
    return {
        "total_risk_score": round(total, 1),
        "risk_level": "Low" if total < 3 else "Medium" if total < 6 else "High",
        "breakdown": scores,
    }
```

## Supply Chain Digital Twin
```python
DIGITAL_TWIN_PROMPT = """
Design a supply chain digital twin for: {company}
Scope: {scope} (end-to-end / regional / product family)

Components to model:
1. DEMAND SIGNAL:
   - POS data integration
   - Weather/events external signals
   - Promotional calendars

2. SUPPLY NETWORK GRAPH:
   - Tier 1, 2, 3 suppliers
   - Manufacturing sites
   - Distribution centers
   - Last mile nodes

3. INVENTORY VISIBILITY:
   - Stock levels by location in real-time
   - In-transit inventory (EDI/IoT)
   - Aging and expiry tracking

4. DISRUPTION SCENARIOS:
   - Supplier failure impact propagation
   - Port congestion effects
   - Demand spike response
   - Natural disaster routing alternatives

5. OPTIMIZATION LEVERS:
   - Inventory repositioning
   - Supplier switching
   - Transportation mode change
   - Customer allocation during shortage

SIMULATION CAPABILITIES:
- What-if analysis for each disruption type
- Monte Carlo simulation for demand uncertainty
- Network optimization under constraints
"""
```

## Warehouse Management
```python
WAREHOUSE_AI = {
    "slotting_optimization": {
        "principle": "Place fast movers near output, group by order affinity",
        "metrics": ["picks/hour", "travel distance", "replenishment frequency"],
        "result": "20-30% pick productivity improvement",
    },
    "receiving_automation": {
        "tools": ["Computer vision for PO matching", "RFID", "AI dimension scanning"],
        "reduces": ["Receiving dwell time", "Putaway errors"],
    },
    "pick_optimization": {
        "methods": ["Batch picking", "Zone picking", "Wave planning"],
        "ai_enhancement": "ML-predicted wave sizing based on order patterns",
    },
    "robotics_roi": {
        "amr_typical_payback": "18-24 months",
        "goods_to_person_payback": "24-36 months",
        "throughput_improvement": "3-5x vs. manual",
        "when_to_automate": "High volume + repetitive + labor cost > $50K/head/year",
    },
}

WAREHOUSE_KPIs = {
    "receiving": ["Lines per hour", "Receiving accuracy %", "Dock-to-stock time"],
    "inventory": ["Inventory accuracy %", "Cycle count frequency", "Shrink %"],
    "picking": ["Order lines picked per hour", "Pick accuracy %", "Cost per pick"],
    "shipping": ["OTIF %", "Order cycle time", "Damage rate"],
}
```

## Models to Use
- **Demand forecasting**: `gpt-4o` with code tools (statistical models + ML)
- **Network optimization**: `claude-opus-4-6` (complex multi-variable optimization)
- **Supplier analysis**: `claude-opus-4-6` (strategic assessment)
- **Disruption response**: `claude-opus-4-6` (scenario reasoning)
- **Procurement negotiations**: `claude-sonnet-4-6` (communication strategy)
- **Real-time pricing/rates**: `perplexity/sonar-pro` (current freight rates)
