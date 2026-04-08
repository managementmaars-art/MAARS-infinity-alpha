---
name: food-beverage-ai
description: AI food & beverage skills — recipe development, menu engineering, nutritional analysis, food safety, supply chain, restaurant operations, CPG product development for MAARS F&B agents
---

# Food & Beverage AI — MAARS Reference

## Recipe Development
```python
RECIPE_DEVELOPMENT_PROMPT = """
Develop a recipe for: {dish_concept}
Cuisine: {cuisine}
Target: {target} (restaurant/home cook/CPG manufacturing/meal kit)
Dietary constraints: {dietary} (vegan/gluten-free/keto/halal/kosher)
Servings: {servings}
Target food cost: {target_cost}% of menu price
Equipment available: {equipment}
Skill level: {skill_level}

Develop:
1. RECIPE NAME: Compelling, on-brand
2. YIELD: {servings} servings, portion size per serving
3. INGREDIENTS (with prep weights and costs):
   - Ingredient | Amount | Prep weight (yield%) | Unit cost | Extended cost
   
4. MISE EN PLACE: Advance prep list
5. METHOD:
   - Step-by-step technique
   - Critical control points (temperature, time, texture cues)
   - Chef's notes for each critical step
   
6. PLATING GUIDE (if restaurant): Component placement, garnish
7. VARIATIONS: 2-3 adaptation ideas
8. SHELF LIFE/STORAGE: Temperature, container, duration
9. NUTRITIONAL ESTIMATE: Per serving (cal/protein/fat/carbs)
10. SCALING NOTES: How recipe behaves at 10x, 100x quantity
"""

def calculate_food_cost(ingredients: list) -> dict:
    """Calculate food cost and suggested menu price"""
    total_cost = sum(i["cost_per_unit"] * i["quantity"] for i in ingredients)
    waste_factor = 1.1  # 10% waste/trim
    total_with_waste = total_cost * waste_factor
    
    return {
        "raw_food_cost": total_cost,
        "food_cost_with_waste": total_with_waste,
        "menu_price_28pct": total_with_waste / 0.28,
        "menu_price_32pct": total_with_waste / 0.32,
        "suggested_price": round(total_with_waste / 0.30, 2),
        "contribution_margin_at_28pct": total_with_waste / 0.28 * 0.72,
    }
```

## Menu Engineering
```python
MENU_ENGINEERING_PROMPT = """
Perform menu engineering analysis.
Restaurant: {restaurant_name}
Period: {period}
Menu data: {menu_items_with_sales_and_costs}

Matrix analysis (contribution margin vs. popularity):
1. STARS: High margin + High popularity → Feature, protect, promote
2. PLOWHORSES: Low margin + High popularity → Reprice or reformulate
3. PUZZLES: High margin + Low popularity → Reposition or bundle
4. DOGS: Low margin + Low popularity → Consider removing

For each category, recommend:
- STARS: Premium placement, menu call-out, photos
- PLOWHORSES: Portion reduction, premium upsell (add-on), recipe cost reduction
- PUZZLES: Photography, rename, bundle with popular item
- DOGS: Remove unless brand essential; replace with better options

Menu psychology recommendations:
- Remove dollar signs from prices
- Anchor with one premium item per section
- Use decoy pricing (middle option wins)
- Descriptive language increases sales 27%

MENU REDESIGN PRIORITIES: Top 5 changes for immediate revenue impact
"""

def calculate_menu_matrix(items: list) -> dict:
    """Classify menu items into engineering matrix"""
    avg_contribution = sum(i["contribution_margin"] for i in items) / len(items)
    avg_popularity = sum(i["count_sold"] for i in items) / len(items)
    
    matrix = {}
    for item in items:
        is_popular = item["count_sold"] >= avg_popularity
        is_profitable = item["contribution_margin"] >= avg_contribution
        
        if is_popular and is_profitable:
            category = "star"
        elif is_popular and not is_profitable:
            category = "plowhorse"
        elif not is_popular and is_profitable:
            category = "puzzle"
        else:
            category = "dog"
        
        matrix[item["name"]] = {
            "category": category,
            "cm": item["contribution_margin"],
            "sales": item["count_sold"],
        }
    return matrix
```

## Nutritional Analysis
```python
NUTRITION_ANALYSIS_PROMPT = """
Analyze nutritional profile for: {product_or_recipe}
Intended consumer: {consumer}
Regulatory market: {market} (US FDA/EU/UK FSA/AU FSANZ)

Provide:
1. NUTRITIONAL FACTS PANEL:
   Per {serving_size}:
   - Calories, Fat (total/saturated/trans), Cholesterol
   - Sodium, Carbohydrates (total/dietary fiber/sugars/added sugars)
   - Protein, Vitamins & Minerals (if significant)
   
2. HEALTH CLAIMS ELIGIBILITY:
   - "Low fat": <3g fat per serving
   - "Low sodium": <140mg per serving
   - "Good source of fiber": ≥10% DV
   - "Excellent source": ≥20% DV
   
3. ALLERGEN DECLARATION:
   - Top 9 allergens present (US) or Top 14 (EU)
   - Cross-contamination warnings
   
4. FRONT-OF-PACK LABELING:
   - Nutri-Score (EU)
   - Traffic light system (UK)
   - Health Star Rating (AU)
   
5. REFORMULATION SUGGESTIONS:
   - Sodium reduction targets
   - Sugar reduction options
   - Fiber fortification opportunities
"""

# USDA FoodData Central API
import requests

def search_food_nutrition(food_name: str) -> list:
    resp = requests.get(
        "https://api.nal.usda.gov/fdc/v1/foods/search",
        params={"query": food_name, "api_key": USDA_FDC_KEY, "pageSize": 5,
                "dataType": ["SR Legacy", "Foundation"]}
    )
    foods = resp.json().get("foods", [])
    return [{
        "name": f["description"],
        "nutrients": {n["nutrientName"]: n["value"] 
                     for n in f.get("foodNutrients", [])[:10]}
    } for f in foods]
```

## Food Safety & HACCP
```python
HACCP_PLAN_PROMPT = """
Develop a HACCP plan for: {food_product}
Production type: {production_type}
Facility: {facility_type}
Output: {daily_output}

7 HACCP Principles:
1. HAZARD ANALYSIS:
   - Biological hazards (pathogens, spoilage organisms)
   - Chemical hazards (allergens, pesticides, cleaning chemicals)
   - Physical hazards (metal, glass, bone, foreign material)
   
2. CRITICAL CONTROL POINTS (CCPs):
   For each CCP:
   - Process step
   - Hazard controlled
   - Critical limit (e.g., 165°F/74°C for 15 seconds)
   - Monitoring procedure (who, how, frequency)
   - Corrective action if limit breached
   - Verification method
   - Records required

3. CRITICAL LIMITS: Science-based (FDA, USDA, Codex)

4. MONITORING PROCEDURES: Real-time measurement

5. CORRECTIVE ACTIONS: What to do when deviation occurs

6. VERIFICATION: How we confirm HACCP is working

7. RECORD-KEEPING: Log templates for each CCP

PREREQUISITE PROGRAMS: GMP, sanitation, pest control, supplier approval
"""

FOOD_SAFETY_TEMPS = {
    "danger_zone": "40°F-140°F (4°C-60°C) — bacteria double every 20 min",
    "cooking_temperatures": {
        "poultry": "165°F (74°C)",
        "ground_meat": "160°F (71°C)",
        "steaks_chops": "145°F + 3 min rest (63°C)",
        "fish": "145°F (63°C)",
        "eggs_hot_hold": "145°F (63°C)",
        "reheating": "165°F (74°C)",
    },
    "cold_storage": {
        "refrigerator": "≤40°F (4°C)",
        "freezer": "0°F (-18°C)",
    },
}
```

## Beverage Development
```python
BEVERAGE_FORMULATION_PROMPT = """
Develop beverage formula for: {beverage_concept}
Category: {category} (RTD/concentrate/alcoholic/functional)
Target market: {market}
Key attributes: {attributes}
Regulatory constraints: {constraints}
Target pH: {target_ph}
Target Brix: {target_brix}

Develop:
1. BASE FORMULA (per 100g/100ml):
   - Water, juice, base spirit etc.
   - Sweeteners (sucrose equivalent)
   - Acid blend (for pH)
   - Flavoring system (natural vs. artificial)
   - Color (natural vs. synthetic)
   - Preservatives (if applicable)
   - Functional ingredients (vitamins, adaptogens, nootropics)

2. PROCESSING PARAMETERS:
   - Mixing order (critical for emulsions)
   - Temperature requirements
   - Homogenization needs
   - Pasteurization spec (HTST/UHT/tunnel)

3. SHELF LIFE TARGET:
   - pH, water activity, preservative system
   - Accelerated shelf life testing protocol
   - Packaging compatibility

4. SENSORY PROFILE:
   - Flavor arc (initial → mid → finish)
   - Color specification (visual)
   - Mouthfeel targets

5. COST PER UNIT: Ingredient cost + processing estimate

6. REGULATORY: Label requirements, claims substantiation
"""
```

## Restaurant Operations AI
```python
OPERATIONS_PROMPT = """
Optimize restaurant operations for: {restaurant_name}
Type: {type} (QSR/fast-casual/casual/fine dining)
Covers per day: {daily_covers}
Current issues: {pain_points}

Analyze and recommend:
1. LABOR OPTIMIZATION:
   - Labor % target: {labor_target}% of revenue
   - Scheduling optimization (sales forecast vs. labor)
   - Cross-training opportunities
   - Productivity benchmarks (revenue per labor hour)

2. WASTE REDUCTION:
   - Current waste %: {waste_pct}%
   - FIFO implementation
   - Par level optimization
   - Prep batch sizing

3. TABLE TURNS (if applicable):
   - Current turn time: {turn_time} min
   - Industry benchmark: {benchmark} min
   - Friction points analysis
   - POS and payment flow optimization

4. UPSELLING SYSTEM:
   - Server training on suggestive selling
   - POS prompts
   - Average check target: ${target_check}

5. TECHNOLOGY STACK:
   - POS recommendation for size
   - Online ordering integration
   - Inventory management system
   - Labor scheduling tool
"""
```

## Models to Use
- **Recipe development**: `claude-opus-4-6` (creative + technical food science)
- **Menu engineering**: `gpt-4o` with code tools (matrix analysis)
- **Nutritional analysis**: `gpt-4o` + USDA API
- **Food safety/HACCP**: `claude-opus-4-6` (safety-critical, regulatory)
- **Beverage formulation**: `claude-opus-4-6` (food science + chemistry)
- **Operations optimization**: `claude-sonnet-4-6` (practical recommendations)
- **Food trend research**: `perplexity/sonar-pro` (current trends)
