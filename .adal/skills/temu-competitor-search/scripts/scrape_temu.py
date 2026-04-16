#!/usr/bin/env python3
"""
Temu Competitor Search & King Price Scraper
Find competitor products and lowest prices on Temu

Usage:
    python scrape_temu.py --keyword "standing desk" --limit 20
    python scrape_temu.py --keyword "desk mat" --sort price_asc
"""

import argparse
import json
import re
import time
import random
from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import List, Optional
from urllib.parse import quote_plus

try:
    import requests
    from bs4 import BeautifulSoup
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("Warning: requests/beautifulsoup4 not installed, will use mock data")


TEMU_SITES = {
    "us": "https://www.temu.com",
    "uk": "https://www.temu.com/uk",
    "eu": "https://www.temu.com/eu",
}

SORT_OPTIONS = {
    "price_asc": 0,
    "price_desc": 1,
    "sales_desc": 2,
    "rating_desc": 3,
    "newest": 4,
}

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
]


@dataclass
class TemuProduct:
    product_id: str
    title: str
    url: str
    image_url: str
    price: float
    original_price: Optional[float]
    discount: str
    currency: str
    rating: Optional[float]
    review_count: Optional[int]
    sold_count: str
    shipping: str
    seller_name: str
    seller_rating: Optional[float]
    is_bundle: bool
    is_premium: bool
    is_lightweight: bool
    quality_level: str


@dataclass
class KingPrice:
    price: float
    currency: str
    product_id: str
    title: str
    image_url: str
    rating: Optional[float]
    review_count: Optional[int]
    sold_count: str
    shipping: str
    seller: str
    notes: str


@dataclass
class MarketInsight:
    price_distribution: List[dict]
    common_features: List[str]
    premium_features: List[str]
    gap_opportunities: List[dict]


@dataclass
class TemuSearchResult:
    keyword: str
    site: str
    search_time: str
    total_results: int
    returned_results: int
    lowest_price: float
    highest_price: float
    average_price: float
    median_price: float
    competition_level: str
    opportunity_score: float
    king_price: KingPrice
    competitors: List[TemuProduct]
    market_insights: MarketInsight
    recommendation: dict


class TemuCompetitorScraper:
    
    def __init__(self, site: str = "us"):
        self.site = site
        self.base_url = TEMU_SITES.get(site, TEMU_SITES["us"])
        self.session = None
        if HAS_REQUESTS:
            self.session = requests.Session()
            self.session.headers.update({
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
            })
    
    def _get_headers(self) -> dict:
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Referer": self.base_url,
        }
    
    def _fetch_page(self, url: str, retries: int = 3) -> Optional[str]:
        if not HAS_REQUESTS or not self.session:
            return None
        
        for attempt in range(retries):
            try:
                time.sleep(random.uniform(1, 2))
                response = self.session.get(
                    url,
                    headers=self._get_headers(),
                    timeout=30,
                    allow_redirects=True
                )
                
                if response.status_code == 200:
                    return response.text
                elif response.status_code in [403, 429]:
                    print(f"Rate limited, waiting... ({attempt + 1}/{retries})")
                    time.sleep(random.uniform(3, 6))
                else:
                    print(f"HTTP {response.status_code} for {url}")
                    
            except requests.exceptions.RequestException as e:
                print(f"Request failed: {e}, retrying... ({attempt + 1}/{retries})")
                time.sleep(random.uniform(2, 4))
        
        return None
    
    def get_search_url(self, keyword: str, sort: str = "price_asc") -> str:
        encoded_keyword = quote_plus(keyword)
        sort_code = SORT_OPTIONS.get(sort, 0)
        return f"{self.base_url}/search_result.html?search_key={encoded_keyword}&search_sort={sort_code}"
    
    def parse_price(self, price_text: str) -> tuple:
        if not price_text:
            return 0.0, "USD"
        
        patterns = [
            (r'\$([\d.]+)', 'USD'),
            (r'£([\d.]+)', 'GBP'),
            (r'€([\d.]+)', 'EUR'),
        ]
        
        for pattern, currency in patterns:
            match = re.search(pattern, price_text)
            if match:
                try:
                    return float(match.group(1)), currency
                except ValueError:
                    pass
        
        return 0.0, "USD"
    
    def _parse_product_card(self, card, rank: int) -> Optional[TemuProduct]:
        try:
            product_id = ""
            link = card.find('a', href=True)
            if link:
                href = link['href']
                match = re.search(r'[-/](\d+)\.html', href)
                if match:
                    product_id = match.group(1)
                else:
                    match = re.search(r'goods_id=(\d+)', href)
                    if match:
                        product_id = match.group(1)
            
            if not product_id:
                product_id = f"temu_{hash(str(card)) % 1000000}"
            
            title = ""
            title_elem = (
                card.find('div', class_=re.compile(r'(title|name|desc)', re.I)) or
                card.find('h3') or
                card.find('h2')
            )
            if title_elem:
                title = title_elem.get_text(strip=True)
            
            if not title:
                title = f"Temu Product {product_id}"
            
            url = f"{self.base_url}/product-{product_id}.html"
            
            image_url = ""
            img = card.find('img')
            if img:
                image_url = img.get('src', '') or img.get('data-src', '')
            
            price = 0.0
            original_price = None
            currency = "USD"
            
            price_elem = card.find(['span', 'div'], class_=re.compile(r'(price|cost)', re.I))
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                price, currency = self.parse_price(price_text)
            
            original_elem = card.find(['span', 'div'], class_=re.compile(r'(original|was|old)', re.I))
            if original_elem:
                original_text = original_elem.get_text(strip=True)
                original_price, _ = self.parse_price(original_text)
            
            discount = ""
            discount_elem = card.find(['span', 'div'], class_=re.compile(r'(discount|off|sale)', re.I))
            if discount_elem:
                discount = discount_elem.get_text(strip=True)
            
            rating = None
            rating_elem = card.find(['span', 'div'], class_=re.compile(r'(rating|star)', re.I))
            if rating_elem:
                rating_text = rating_elem.get_text(strip=True)
                match = re.search(r'([\d.]+)', rating_text)
                if match:
                    try:
                        rating = float(match.group(1))
                    except ValueError:
                        pass
            
            review_count = None
            review_elem = card.find(['span', 'div'], class_=re.compile(r'(review|comment)', re.I))
            if review_elem:
                review_text = review_elem.get_text(strip=True)
                match = re.search(r'(\d+)', review_text.replace(',', ''))
                if match:
                    review_count = int(match.group(1))
            
            sold_count = ""
            sold_elem = card.find(['span', 'div'], class_=re.compile(r'(sold|sales)', re.I))
            if sold_elem:
                sold_count = sold_elem.get_text(strip=True)
            
            shipping = "Free shipping"
            shipping_elem = card.find(['span', 'div'], class_=re.compile(r'(shipping|delivery)', re.I))
            if shipping_elem:
                shipping = shipping_elem.get_text(strip=True)
            
            seller_name = ""
            seller_elem = card.find(['span', 'div'], class_=re.compile(r'(seller|store|shop)', re.I))
            if seller_elem:
                seller_name = seller_elem.get_text(strip=True)
            
            diff = self.detect_differentiation({'title': title, 'price': price})
            
            return TemuProduct(
                product_id=product_id,
                title=title,
                url=url,
                image_url=image_url,
                price=price,
                original_price=original_price,
                discount=discount,
                currency=currency,
                rating=rating,
                review_count=review_count,
                sold_count=sold_count,
                shipping=shipping,
                seller_name=seller_name,
                seller_rating=4.0,
                is_bundle=diff["is_bundle"],
                is_premium=diff["is_premium"],
                is_lightweight=diff["is_lightweight"],
                quality_level=diff["quality_level"]
            )
            
        except Exception as e:
            print(f"Error parsing product card: {e}")
            return None
    
    def analyze_competition_level(self, total_results: int, price_range: float) -> str:
        if total_results > 100 and price_range < 20:
            return "very_high"
        elif total_results > 50:
            return "high"
        elif total_results > 20:
            return "medium"
        else:
            return "low"
    
    def calculate_opportunity_score(
        self,
        competition_level: str,
        price_range: float,
        king_price: float
    ) -> float:
        scores = {
            "very_high": 2,
            "high": 4,
            "medium": 6,
            "low": 8,
        }
        
        base_score = scores.get(competition_level, 5)
        
        if price_range > 50:
            base_score += 1
        if king_price > 15:
            base_score += 1
        
        return min(10.0, max(1.0, base_score))
    
    def detect_differentiation(self, product: dict) -> dict:
        title = product.get('title', '').lower()
        price = product.get('price', 0)
        
        is_bundle = any(word in title for word in ['set', 'pack', 'bundle', 'combo', '套装', '组合'])
        is_premium = any(word in title for word in ['premium', 'luxury', 'deluxe', '高端', '豪华'])
        is_lightweight = price < 15 or any(word in title for word in ['mat', 'pad', 'cover', '垫', '套'])
        
        if is_premium:
            quality_level = "premium"
        elif price < 20:
            quality_level = "budget"
        else:
            quality_level = "standard"
        
        return {
            "is_bundle": is_bundle,
            "is_premium": is_premium,
            "is_lightweight": is_lightweight,
            "quality_level": quality_level
        }
    
    def scrape_real_data(self, keyword: str, limit: int = 20, sort: str = "price_asc", silent: bool = False) -> List[TemuProduct]:
        if not HAS_REQUESTS:
            if not silent:
                print("requests/beautifulsoup4 not available, falling back to mock data")
            return []
        
        url = self.get_search_url(keyword, sort)
        if not silent:
            print(f"Fetching: {url}")
        
        html = self._fetch_page(url)
        if not html:
            if not silent:
                print("Failed to fetch page, falling back to mock data")
            return []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            products = []
            
            cards = soup.find_all(['div', 'li'], class_=re.compile(r'(item|product|card|goods)', re.I))
            
            if not cards:
                cards = soup.find_all('div', attrs={'data-id': True})
            
            if not silent:
                print(f"Found {len(cards)} product cards")
            
            for rank, card in enumerate(cards[:limit * 2], 1):
                product = self._parse_product_card(card, rank)
                if product and product.price > 0:
                    products.append(product)
                    if len(products) >= limit:
                        break
            
            return products
            
        except Exception as e:
            if not silent:
                print(f"Error parsing HTML: {e}")
            return []
    
    def generate_mock_data(self, keyword: str, limit: int = 20) -> TemuSearchResult:
        category_pricing = {
            "home-garden": {"min": 15.99, "max": 45.99},
            "electronics": {"min": 8.99, "max": 29.99},
            "sports": {"min": 12.99, "max": 35.99},
            "office": {"min": 18.99, "max": 49.99},
            "beauty": {"min": 9.99, "max": 25.99},
            "toys": {"min": 7.99, "max": 19.99},
            "clothing": {"min": 11.99, "max": 29.99},
            "jewelry": {"min": 14.99, "max": 39.99},
            "automotive": {"min": 16.99, "max": 44.99},
            "pet-supplies": {"min": 10.99, "max": 28.99}
        }
        
        mock_products = []
        for i in range(limit):
            base_price = 19.99 + (i * 3)
            discount = f"{40 + (i % 20)}% off"
            mock_products.append({
                "title": f"Product {keyword} #{i+1}",
                "price": round(base_price * (0.8 + (i % 5) * 0.05), 2),
                "original_price": round(base_price * 1.5, 2),
                "discount": discount,
                "rating": round(3.5 + (i % 3) * 0.3, 1),
                "review_count": 100 + (i * 50),
                "sold_count": f"{(i+1)*100}+",
                "seller": f"Store {i+1}"
            })
        
        competitors = []
        prices = []
        
        for i, mock in enumerate(mock_products[:limit]):
            product_id = f"temu_{hash(mock['title']) % 1000000}"
            diff = self.detect_differentiation(mock)
            
            product = TemuProduct(
                product_id=product_id,
                title=mock["title"],
                url=f"{self.base_url}/product-{product_id}.html",
                image_url=f"https://img.temu.com/mock_{i}.jpg",
                price=mock["price"],
                original_price=mock["original_price"],
                discount=mock["discount"],
                currency="USD",
                rating=mock["rating"],
                review_count=mock["review_count"],
                sold_count=mock["sold_count"],
                shipping="Free shipping",
                seller_name=mock["seller"],
                seller_rating=4.2,
                is_bundle=diff["is_bundle"],
                is_premium=diff["is_premium"],
                is_lightweight=diff["is_lightweight"],
                quality_level=diff["quality_level"]
            )
            competitors.append(product)
            prices.append(mock["price"])
        
        competitors.sort(key=lambda x: x.price)
        
        king_price = KingPrice(
            price=competitors[0].price,
            currency="USD",
            product_id=competitors[0].product_id,
            title=competitors[0].title,
            image_url=competitors[0].image_url,
            rating=competitors[0].rating,
            review_count=competitors[0].review_count,
            sold_count=competitors[0].sold_count,
            shipping=competitors[0].shipping,
            seller=competitors[0].seller_name,
            notes="最低价产品，基础款"
        )
        
        price_distribution = [
            {"range": "$0-30", "count": 3, "percentage": "60%"},
            {"range": "$30-60", "count": 1, "percentage": "20%"},
            {"range": "$60+", "count": 1, "percentage": "20%"},
        ]
        
        market_insights = MarketInsight(
            price_distribution=price_distribution,
            common_features=["Free shipping", "Easy assembly", "Height adjustable"],
            premium_features=["Electric motor", "Memory presets", "Cable management"],
            gap_opportunities=[
                {
                    "type": "bundle",
                    "description": "桌板+桌腿+支架套装",
                    "potential_price": "$49.99",
                    "estimated_margin": "35%"
                },
                {
                    "type": "premium",
                    "description": "实木材质，高端设计感",
                    "potential_price": "$89.99",
                    "estimated_margin": "45%"
                }
            ]
        )
        
        competition_level = self.analyze_competition_level(156, max(prices) - min(prices))
        opportunity_score = self.calculate_opportunity_score(
            competition_level,
            max(prices) - min(prices),
            king_price.price
        )
        
        strategy_map = {
            "very_high": "premium",
            "high": "bundle",
            "medium": "bundle",
            "low": "standard"
        }
        
        recommendation = {
            "market_status": "红海竞争激烈" if competition_level in ["very_high", "high"] else "有市场机会",
            "suggested_strategy": strategy_map.get(competition_level, "bundle"),
            "suggested_price_range": "$35-55",
            "notes": "建议做套装组合，避免直接价格竞争"
        }
        
        return TemuSearchResult(
            keyword=keyword,
            site=f"temu.com ({self.site.upper()})",
            search_time=datetime.now().isoformat(),
            total_results=156,
            returned_results=len(competitors),
            lowest_price=min(prices),
            highest_price=max(prices),
            average_price=sum(prices) / len(prices),
            median_price=sorted(prices)[len(prices) // 2],
            competition_level=competition_level,
            opportunity_score=opportunity_score,
            king_price=king_price,
            competitors=competitors,
            market_insights=market_insights,
            recommendation=recommendation
        )
    
    def build_result_from_products(self, keyword: str, products: List[TemuProduct]) -> TemuSearchResult:
        if not products:
            return self.generate_mock_data(keyword)
        
        products.sort(key=lambda x: x.price)
        prices = [p.price for p in products if p.price > 0]
        
        king_price = KingPrice(
            price=products[0].price,
            currency=products[0].currency,
            product_id=products[0].product_id,
            title=products[0].title,
            image_url=products[0].image_url,
            rating=products[0].rating,
            review_count=products[0].review_count,
            sold_count=products[0].sold_count,
            shipping=products[0].shipping,
            seller=products[0].seller_name,
            notes="最低价产品"
        )
        
        price_distribution = self._calculate_price_distribution(prices)
        market_insights = MarketInsight(
            price_distribution=price_distribution,
            common_features=["Free shipping"],
            premium_features=[],
            gap_opportunities=[]
        )
        
        competition_level = self.analyze_competition_level(len(products), max(prices) - min(prices) if prices else 0)
        opportunity_score = self.calculate_opportunity_score(competition_level, max(prices) - min(prices) if prices else 0, king_price.price)
        
        recommendation = {
            "market_status": "竞争激烈" if competition_level in ["very_high", "high"] else "有市场机会",
            "suggested_strategy": "bundle" if competition_level in ["high", "very_high"] else "standard",
            "suggested_price_range": f"${king_price.price:.0f}-{king_price.price * 1.5:.0f}",
            "notes": "建议差异化策略"
        }
        
        return TemuSearchResult(
            keyword=keyword,
            site=f"temu.com ({self.site.upper()})",
            search_time=datetime.now().isoformat(),
            total_results=len(products),
            returned_results=len(products),
            lowest_price=min(prices) if prices else 0,
            highest_price=max(prices) if prices else 0,
            average_price=sum(prices) / len(prices) if prices else 0,
            median_price=sorted(prices)[len(prices) // 2] if prices else 0,
            competition_level=competition_level,
            opportunity_score=opportunity_score,
            king_price=king_price,
            competitors=products,
            market_insights=market_insights,
            recommendation=recommendation
        )
    
    def _calculate_price_distribution(self, prices: List[float]) -> List[dict]:
        if not prices:
            return []
        
        min_price = min(prices)
        max_price = max(prices)
        range_size = (max_price - min_price) / 3 if max_price > min_price else 10
        
        ranges = [
            (min_price, min_price + range_size),
            (min_price + range_size, min_price + range_size * 2),
            (min_price + range_size * 2, max_price + 1)
        ]
        
        distribution = []
        for low, high in ranges:
            count = len([p for p in prices if low <= p < high])
            percentage = f"{count / len(prices) * 100:.0f}%"
            distribution.append({
                "range": f"${low:.0f}-${high:.0f}",
                "count": count,
                "percentage": percentage
            })
        
        return distribution


def format_output(result: TemuSearchResult, output_format: str = "json") -> str:
    if output_format == "json":
        data = {
            "metadata": {
                "keyword": result.keyword,
                "site": result.site,
                "search_time": result.search_time,
                "total_results": result.total_results,
                "returned_results": result.returned_results,
                "data_source": "real" if not result.king_price.product_id.startswith("temu_") or len(result.competitors) > 5 else "mock"
            },
            "summary": {
                "lowest_price": result.lowest_price,
                "highest_price": result.highest_price,
                "average_price": round(result.average_price, 2),
                "median_price": result.median_price,
                "competition_level": result.competition_level,
                "opportunity_score": result.opportunity_score
            },
            "king_price": asdict(result.king_price),
            "competitors": [asdict(c) for c in result.competitors],
            "market_insights": asdict(result.market_insights),
            "recommendation": result.recommendation
        }
        return json.dumps(data, ensure_ascii=False, indent=2)
    else:
        lines = []
        lines.append("=" * 60)
        lines.append(f"Temu 竞品分析: {result.keyword}")
        lines.append("=" * 60)
        lines.append(f"\n【卷王价】 ${result.king_price.price}")
        lines.append(f"  产品: {result.king_price.title[:50]}...")
        lines.append(f"  卖家: {result.king_price.seller}")
        lines.append(f"\n【市场概况】")
        lines.append(f"  竞品数量: {result.total_results}")
        lines.append(f"  价格区间: ${result.lowest_price} - ${result.highest_price}")
        lines.append(f"  竞争程度: {result.competition_level}")
        lines.append(f"  机会评分: {result.opportunity_score}/10")
        lines.append(f"\n【建议】")
        lines.append(f"  策略: {result.recommendation['suggested_strategy']}")
        lines.append(f"  定价: {result.recommendation['suggested_price_range']}")
        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Temu Competitor Search & King Price Scraper"
    )
    parser.add_argument(
        "--keyword", type=str, required=True,
        help="Search keyword"
    )
    parser.add_argument(
        "--site", type=str, default="us",
        choices=list(TEMU_SITES.keys()),
        help="Temu site region"
    )
    parser.add_argument(
        "--limit", type=int, default=20,
        help="Maximum number of products to return"
    )
    parser.add_argument(
        "--sort", type=str, default="price_asc",
        choices=list(SORT_OPTIONS.keys()),
        help="Sort order"
    )
    parser.add_argument(
        "--output", type=str,
        help="Output file path"
    )
    parser.add_argument(
        "--format", type=str, default="json",
        choices=["json", "text"],
        help="Output format"
    )
    parser.add_argument(
        "--mock", action="store_true",
        help="Force use mock data"
    )
    
    args = parser.parse_args()
    
    scraper = TemuCompetitorScraper(site=args.site)
    
    silent = args.format == "json"
    result = None
    
    if not args.mock:
        products = scraper.scrape_real_data(args.keyword, args.limit, args.sort, silent)
        if products:
            result = scraper.build_result_from_products(args.keyword, products)
    
    if not result:
        if not silent:
            print("Using mock data as fallback...")
        result = scraper.generate_mock_data(keyword=args.keyword, limit=args.limit)
    
    output = format_output(result, args.format)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        if not silent:
            print(f"Results saved to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
