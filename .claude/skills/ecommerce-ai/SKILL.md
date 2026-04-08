---
name: ecommerce-ai
description: AI ecommerce skills — product descriptions, Shopify, pricing strategy, conversion optimization, abandoned cart, customer journey, reviews management for MAARS ecommerce agents
---

# Ecommerce AI — MAARS Reference

## Product Description Generator
```python
PRODUCT_DESC_PROMPT = """
Write a compelling product description for:
Product: {product_name}
Category: {category}
Key features: {features}
Target customer: {customer}
Tone: {tone} (professional/casual/luxury/technical)
Length: {length} (short: 50 words / standard: 150 words / detailed: 300 words)

Structure:
- HEADLINE: Benefit-led, not feature-led
- HOOK: First 2 lines must hook the reader
- BENEFITS: 3-5 bullet points (benefit → feature, not feature → benefit)
- SOCIAL PROOF: Add placeholder [NUMBER] customers / [RATING] stars
- CTA: Create urgency or ease
- SEO KEYWORDS: Naturally include {keywords}
"""
```

## Conversion Rate Optimization
```python
CRO_CHECKLIST = {
    "product_page": [
        "High-quality images (6+ angles + zoom)",
        "Video demonstration",
        "Price clearly visible above fold",
        "Trust badges (secure checkout, returns policy)",
        "Social proof (reviews count, rating, recent purchases)",
        "Stock urgency ('Only 3 left' if true)",
        "Clear size/variant selector",
        "Sticky 'Add to Cart' button on mobile",
        "Related products / frequently bought together",
    ],
    "checkout": [
        "Guest checkout option",
        "Progress indicator (3 steps max)",
        "Multiple payment options (card, PayPal, BNPL, Apple Pay)",
        "Order summary visible",
        "Security indicators",
        "Abandoned cart email trigger",
        "Exit intent popup with discount",
    ],
    "homepage": [
        "Value proposition in hero (above fold)",
        "Category navigation clear",
        "Featured/bestseller products",
        "Trust signals (reviews, media logos, certifications)",
        "Promotional banner (sale, free shipping threshold)",
    ],
}
```

## Email Sequences for Ecommerce
```python
EMAIL_SEQUENCES = {
    "welcome": {
        "timing": ["Immediate", "Day 2", "Day 5"],
        "content": ["Welcome + 10% off", "Brand story + bestsellers", "Customer favorites + social"],
    },
    "abandoned_cart": {
        "timing": ["1 hour", "24 hours", "72 hours"],
        "content": ["Reminder + product image", "Soft urgency + reviews", "Last chance + small discount"],
    },
    "post_purchase": {
        "timing": ["Immediate (confirmation)", "Day 2 (shipping)", "Day 7 (check-in)", "Day 30 (review request)"],
    },
    "winback": {
        "timing": ["60 days inactive", "90 days", "120 days"],
        "content": ["We miss you", "What's new + 15% off", "Last chance offer"],
    },
}
```

## Pricing Strategy Framework
```python
PRICING_STRATEGIES = {
    "value_based": "Price based on customer's perceived value, not cost",
    "competitive": "Price relative to competitors (+/- premium/discount)",
    "penetration": "Low price to gain market share, raise later",
    "skimming": "High initial price, lower over time",
    "dynamic": "Real-time pricing based on demand/inventory",
    "bundle": "Group products at discount to increase AOV",
    "freemium": "Free tier → paid conversion",
    "subscription": "Recurring revenue, higher LTV",
}

PRICE_PSYCHOLOGY = {
    "charm_pricing": "9.99 vs 10.00 (left-digit effect)",
    "anchor_pricing": "Show original price crossed out",
    "tier_of_3": "Good/Better/Best — middle option gets chosen most",
    "round_numbers": "Premium products use round numbers ($300 vs $299)",
    "free_shipping_threshold": "Set just above current AOV to increase it",
}
```

## Shopify Integration
```python
import shopify

shopify.ShopifyResource.set_site(f"https://{API_KEY}:{PASSWORD}@{SHOP}.myshopify.com/admin/api/2024-01")

# Create product
product = shopify.Product()
product.title = "Product Name"
product.body_html = "<p>Description</p>"
product.variants = [{"price": "29.99", "sku": "SKU-001", "inventory_quantity": 100}]
product.save()

# Get orders
orders = shopify.Order.find(status="open", limit=50)

# Update inventory
variant = shopify.Variant.find(variant_id)
variant.inventory_quantity = 50
variant.save()
```

## Models to Use
- **Product descriptions**: `claude-sonnet-4-6` (best writing)
- **Bulk descriptions**: `gpt-4o-mini` (fast + cheap at scale)
- **Pricing analysis**: `gpt-4o` with code tools
- **Customer support responses**: `gpt-4o` or `claude-sonnet-4-6`
- **Review analysis**: `gpt-4o` (sentiment + extraction)
