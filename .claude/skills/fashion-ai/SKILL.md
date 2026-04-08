---
name: fashion-ai
description: AI fashion skills — trend forecasting, outfit styling, product descriptions, virtual try-on, size recommendations, sustainability analysis, brand voice for MAARS fashion agents
---

# Fashion AI — MAARS Reference

## Trend Forecasting
```python
TREND_FORECAST_PROMPT = """
You are a fashion trend analyst with expertise in forecasting.

Season: {season} {year}
Market segment: {segment} (luxury/contemporary/fast-fashion/streetwear/activewear)
Target demographic: {demographic}
Geographic focus: {markets}

Analyze:
1. MACRO TRENDS: Cultural, social, economic forces shaping fashion
2. COLOR STORY: 
   - Hero colors (3-5) with Pantone references
   - Color combinations and palettes
   - Color trend lifecycle (emerging/peak/declining)
3. SILHOUETTE TRENDS: Shape direction for tops, bottoms, outerwear
4. KEY MATERIALS: Fabrics, textures, finishes gaining momentum
5. PRINT & PATTERN: Directions in graphics, florals, geometrics
6. DETAIL MOMENTS: Hardware, embellishments, closures
7. STYLING TRENDS: How pieces are being worn/combined
8. RUNWAY → RETAIL TIMELINE: When to bring trends to market

Sources to reference: Runway collections, street style, social media signals,
search trend data, cultural moments.
"""
```

## AI Styling Assistant
```python
STYLING_PROMPT = """
You are a personal stylist with excellent taste and body-positive philosophy.

Client profile:
Body type: {body_type}
Coloring: {coloring} (skin tone, hair, eyes)
Lifestyle: {lifestyle} (career type, activities, social life)
Budget: {budget_range}
Style personality: {style} (classic/minimalist/bohemian/edgy/preppy/eclectic)
Occasion: {occasion}
Existing wardrobe highlights: {existing_pieces}
Avoids: {dislikes}
Fit preferences: {fit_prefs}

Create:
1. OUTFIT RECOMMENDATIONS (3 complete looks):
   - Each piece with specific product suggestions
   - Why this works for their body/coloring/lifestyle
   - Styling notes (how to wear it)
   - Price estimate

2. CAPSULE WARDROBE GAPS: 5 key pieces they're missing

3. SHOPPING GUIDE: Where to find these items (budget-appropriate)

4. OUTFIT FORMULAS: Repeatable combinations from their closet
"""
```

## Product Description for Fashion
```python
FASHION_PRODUCT_PROMPT = """
Write compelling product copy for fashion.

Item: {item_name}
Category: {category}
Brand voice: {brand_voice} (luxury/playful/sustainable/minimalist)
Target customer: {customer}
Key features: {features}
Materials: {materials}
Sizing: {sizing_info}
Price point: ${price}

Write:
1. PRODUCT NAME: Aspirational, memorable
2. HERO DESCRIPTION (50 words): Feeling-led, sensory language
3. FEATURE BULLETS (4-5):
   - Lead with benefit, support with feature
   - Include material composition
   - Mention sustainability credentials if applicable
4. SIZE & FIT GUIDE: Honest, helpful
5. STYLING SUGGESTIONS: 2-3 ways to wear
6. CARE INSTRUCTIONS: Clear, friendly

SEO keywords to include naturally: {keywords}
Avoid: Generic terms, excessive superlatives, greenwashing claims
"""
```

## Virtual Try-On Integration
```python
# Replicate — Virtual try-on with IDM-VTON
import replicate

def virtual_try_on(person_image_url: str, garment_image_url: str) -> str:
    output = replicate.run(
        "cuuupid/idm-vton:c871bb9b046607b680449ecbae55fd8c6d945e0a1948644bf2361b3d021d3ff4",
        input={
            "human_img": person_image_url,
            "garm_img": garment_image_url,
            "garment_des": "upper body clothing",
            "is_checked": True,
            "is_checked_crop": False,
            "denoise_steps": 30,
            "seed": 42,
        }
    )
    return output[0]  # URL to try-on result

# Fashn.ai — Commercial virtual try-on API
def fashn_try_on(model_image: str, garment_image: str, category: str):
    import requests
    resp = requests.post(
        "https://api.fashn.ai/v1/run",
        headers={"Authorization": f"Bearer {FASHN_API_KEY}"},
        json={
            "model_image": model_image,
            "garment_image": garment_image,
            "category": category,  # "tops", "bottoms", "one-pieces"
        }
    )
    prediction_id = resp.json()["id"]
    # Poll for result
    while True:
        import time
        status = requests.get(f"https://api.fashn.ai/v1/status/{prediction_id}",
                             headers={"Authorization": f"Bearer {FASHN_API_KEY}"}).json()
        if status["status"] == "completed":
            return status["output"][0]
        time.sleep(3)
```

## Size Recommendation System
```python
SIZE_RECOMMENDATION_PROMPT = """
Generate size recommendations for:
Customer measurements:
- Height: {height}
- Bust/Chest: {bust}
- Waist: {waist}
- Hips: {hips}
- Weight: {weight} (optional)
- Fit preference: {fit_pref} (slim/regular/relaxed/oversized)

Brand: {brand}
Item type: {item_type}
Brand's size guide: {size_guide}

Recommend:
1. PRIMARY SIZE: Best fit with confidence %
2. SECONDARY SIZE: If between sizes
3. FIT NOTES: Where it may run tight/loose
4. ALTERATION SUGGESTIONS: If needed
5. STYLE CONSIDERATION: Does this cut work for their measurements?
"""

def calculate_size_from_measurements(measurements: dict, brand_guide: dict) -> dict:
    """Rule-based size calculator"""
    bust = measurements.get("bust", 0)
    waist = measurements.get("waist", 0)
    hips = measurements.get("hips", 0)
    
    # Find closest match in brand guide
    best_size = None
    min_variance = float("inf")
    
    for size, ranges in brand_guide.items():
        variance = (abs(bust - ranges["bust_mid"]) + 
                   abs(waist - ranges["waist_mid"]) + 
                   abs(hips - ranges["hips_mid"]))
        if variance < min_variance:
            min_variance = variance
            best_size = size
    
    return {"recommended_size": best_size, "confidence": max(0, 1 - min_variance/20)}
```

## Sustainability Analysis
```python
SUSTAINABILITY_AUDIT_PROMPT = """
Analyze the sustainability credentials of: {brand_or_product}

Evaluate across:
1. MATERIALS SOURCING:
   - Organic/recycled content %
   - Certifications: GOTS, OEKO-TEX, Bluesign, Fair Trade
   - Supply chain transparency

2. PRODUCTION:
   - Factory certifications (SA8000, WRAP, B Corp)
   - Worker wages vs. living wage benchmark
   - Country of manufacture + labor standards

3. ENVIRONMENTAL IMPACT:
   - Water usage (conventional cotton: 2,700L per shirt)
   - Carbon footprint vs. industry average
   - Chemical use and discharge

4. END OF LIFE:
   - Take-back programs
   - Recyclability
   - Biodegradability

5. GREENWASHING CHECK:
   - Are claims specific and verifiable?
   - Third-party verified vs. self-certified?

OVERALL RATING: A-F with explanation
"""
```

## Fashion E-commerce Optimization
```python
FASHION_CRO = {
    "product_imagery": [
        "Model shots: front/back/detail/lifestyle (min 6)",
        "Show on multiple body types when possible",
        "Flat lay for pattern/texture detail",
        "Video: movement and drape",
        "User-generated content social proof",
    ],
    "size_confidence": [
        "Model height and size displayed",
        "Measurements of item at each size",
        "True-to-size customer review aggregation",
        "Size chart with measurement instructions",
        "Easy size exchange policy prominent",
    ],
    "conversion_lifts": {
        "size_recommendation_tool": "+20-30% conversion",
        "virtual_try_on": "+40% for applicable categories",
        "free_returns": "+30% for new customers",
        "user_reviews_with_photos": "+25% conversion",
    },
}
```

## Models to Use
- **Trend forecasting**: `claude-opus-4-6` (cultural + creative synthesis)
- **Styling advice**: `claude-sonnet-4-6` (warm, personalized)
- **Product descriptions**: `claude-sonnet-4-6` (sensory, brand-appropriate)
- **Virtual try-on**: IDM-VTON (replicate) or Fashn.ai API
- **Image generation for fashion**: `stability/sd3-ultra` or DALL-E 3
- **Sustainability research**: `perplexity/sonar-pro` (current certifications)
- **Size recommendations**: Rule-based + `gpt-4o` for edge cases
