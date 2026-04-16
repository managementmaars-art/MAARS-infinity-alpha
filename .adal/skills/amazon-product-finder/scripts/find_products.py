#!/usr/bin/env python3
"""
Amazon Product Finder
Search Amazon and return top products with affiliate links
"""

import sys
import os
import json
from urllib.parse import quote

# Get affiliate ID from environment or use placeholder
AFFILIATE_ID = os.getenv("AMAZON_AFFILIATE_ID", "YOUR-AFFILIATE-ID-21")

def search_amazon(keyword):
    """
    Search Amazon for products
    Note: This is a simplified version using hardcoded database
    For production, use Amazon PA API or web scraping
    """
    
    # Demo product database
    DATABASE = {
        "dünger": [
            {"name": "COMPO Bio Grünpflanzen-Dünger", "asin": "B00X9XZ5", "price": "€8,99", "rating": 4.5, "reviews": 2341},
            {"name": "Substral Naturen Bio Dünger", "asin": "B07YG2N", "price": "€12,49", "rating": 4.3, "reviews": 892},
        ],
        "erde": [
            {"name": "Bio Blumenerde 20L", "asin": "B07XYZD", "price": "€8,99", "rating": 4.5, "reviews": 1567},
        ],
        "licht": [
            {"name": "LED Pflanzenlampe Vollspektrum", "asin": "B08XYZC", "price": "€29,99", "rating": 4.3, "reviews": 3421},
        ],
        "default": [
            {"name": "Gießkanne mit Brause 2L", "asin": "B07QABC", "price": "€15,99", "rating": 4.6, "reviews": 2103},
            {"name": "Pflanzensprüher 1L", "asin": "B06XYZA", "price": "€9,99", "rating": 4.3, "reviews": 876},
        ]
    }
    
    # Find matching products
    keyword_lower = keyword.lower()
    products = []
    
    for key, items in DATABASE.items():
        if key in keyword_lower or keyword_lower in key:
            products.extend(items)
    
    # Return default if no match
    if not products:
        products = DATABASE["default"]
    
    return products[:3]  # Top 3

def format_output(products, keyword):
    """Format products for display"""
    print(f"🛒 Gefundene Produkte für \"{keyword}\":\n")
    
    for i, p in enumerate(products, 1):
        affiliate_link = f"https://www.amazon.de/dp/{p['asin']}?tag={AFFILIATE_ID}"
        
        print(f"{i}. {p['name']}")
        print(f"   ASIN: {p['asin']}")
        print(f"   Preis: {p['price']}")
        print(f"   Bewertung: ⭐{p['rating']} ({p['reviews']:,} Reviews)")
        print(f"   Link: {affiliate_link}")
        print()
    
    print("💡 Tipp: Füge diese ASINs in deine Website ein!")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 find_products.py \"<search keyword>\"")
        print("Example: python3 find_products.py \"Bio Dünger\"")
        sys.exit(1)
    
    keyword = sys.argv[1]
    products = search_amazon(keyword)
    format_output(products, keyword)

if __name__ == "__main__":
    main()
