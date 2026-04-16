#!/usr/bin/env python3
"""
Temu V4.1 Pricing Calculator
Cross-border e-commerce profit calculation for Temu platform

Usage:
    python calculate_pricing.py --temu-price 12.99 --currency USD --ali1688-price 25.00
    python calculate_pricing.py --input products.json --output results.json
"""

import argparse
import json
import sys
from dataclasses import dataclass
from typing import List, Optional, Union


@dataclass
class PricingInput:
    temu_price: float
    currency: str
    ali1688_price: float
    exchange_rate: float = 7.2
    fulfillment_fee: float = 3.5
    platform_rate: float = 0.45
    product_name: Optional[str] = None


@dataclass
class PricingResult:
    input: dict
    calculation: dict
    decision: dict


class TemuPricingCalculator:
    
    DEFAULT_EXCHANGE_RATE = 7.2
    DEFAULT_FULFILLMENT_FEE = 3.5
    DEFAULT_PLATFORM_RATE = 0.45
    PROFIT_THRESHOLD = 5.0
    
    def __init__(
        self,
        exchange_rate: float = DEFAULT_EXCHANGE_RATE,
        fulfillment_fee: float = DEFAULT_FULFILLMENT_FEE,
        platform_rate: float = DEFAULT_PLATFORM_RATE
    ):
        self.exchange_rate = exchange_rate
        self.fulfillment_fee = fulfillment_fee
        self.platform_rate = platform_rate
    
    def calculate(self, data: PricingInput) -> PricingResult:
        if data.currency.upper() == "USD":
            temu_price_cny = data.temu_price * self.exchange_rate
            gross_revenue_usd = data.temu_price * self.platform_rate
            gross_revenue_cny = gross_revenue_usd * self.exchange_rate
        else:
            temu_price_cny = data.temu_price
            gross_revenue_usd = data.temu_price / self.exchange_rate
            gross_revenue_cny = data.temu_price * self.platform_rate
        
        total_cost = data.ali1688_price + self.fulfillment_fee
        net_profit = gross_revenue_cny - total_cost
        
        if net_profit > 10.0:
            status = "STRONG_GO"
            recommendation = "高利润产品，优先上架"
        elif net_profit > 5.0:
            status = "GO"
            recommendation = "利润达标，建议上架"
        elif net_profit > 3.0:
            status = "MARGINAL"
            recommendation = "利润边缘，需优化成本或定价"
        else:
            status = "PASS"
            recommendation = "利润不足，直接淘汰"
        
        margin_pct = (net_profit / temu_price_cny * 100) if temu_price_cny > 0 else 0
        
        return PricingResult(
            input={
                "temu_price": data.temu_price,
                "price_currency": data.currency,
                "ali1688_price": data.ali1688_price,
                "exchange_rate": self.exchange_rate,
                "fulfillment_fee": self.fulfillment_fee,
                "platform_rate": self.platform_rate,
                "product_name": data.product_name
            },
            calculation={
                "temu_price_cny": round(temu_price_cny, 2),
                "gross_revenue_usd": round(gross_revenue_usd, 2),
                "gross_revenue_cny": round(gross_revenue_cny, 2),
                "total_cost": round(total_cost, 2),
                "net_profit": round(net_profit, 2)
            },
            decision={
                "status": status,
                "net_profit_threshold": self.PROFIT_THRESHOLD,
                "margin_percentage": f"{margin_pct:.1f}%",
                "recommendation": recommendation
            }
        )
    
    def calculate_batch(self, products: List[PricingInput]) -> List[PricingResult]:
        results = [self.calculate(p) for p in products]
        results.sort(key=lambda r: r.calculation["net_profit"], reverse=True)
        return results
    
    def calculate_breakeven_price(self, ali1688_price: float, currency: str = "USD") -> dict:
        total_cost = ali1688_price + self.fulfillment_fee
        temu_price_cny = total_cost / self.platform_rate
        
        if currency.upper() == "USD":
            temu_price_usd = temu_price_cny / self.exchange_rate
            return {
                "breakeven_price_cny": round(temu_price_cny, 2),
                "breakeven_price_usd": round(temu_price_usd, 2),
                "currency": "USD"
            }
        else:
            return {
                "breakeven_price_cny": round(temu_price_cny, 2),
                "currency": "CNY"
            }
    
    def calculate_target_price(
        self,
        ali1688_price: float,
        target_profit: float,
        currency: str = "USD"
    ) -> dict:
        total_cost = ali1688_price + self.fulfillment_fee
        required_revenue_cny = total_cost + target_profit
        temu_price_cny = required_revenue_cny / self.platform_rate
        
        if currency.upper() == "USD":
            temu_price_usd = temu_price_cny / self.exchange_rate
            return {
                "target_price_cny": round(temu_price_cny, 2),
                "target_price_usd": round(temu_price_usd, 2),
                "target_profit": target_profit,
                "currency": "USD"
            }
        else:
            return {
                "target_price_cny": round(temu_price_cny, 2),
                "target_profit": target_profit,
                "currency": "CNY"
            }
    
    def sensitivity_analysis(
        self,
        ali1688_price: float,
        price_range_usd: List[float]
    ) -> List[dict]:
        results = []
        for price in price_range_usd:
            data = PricingInput(
                temu_price=price,
                currency="USD",
                ali1688_price=ali1688_price
            )
            result = self.calculate(data)
            results.append({
                "temu_price_usd": price,
                "net_profit_cny": result.calculation["net_profit"],
                "status": result.decision["status"]
            })
        return results


def format_result_output(result: PricingResult) -> str:
    lines = []
    lines.append("=" * 50)
    if result.input.get("product_name"):
        lines.append(f"产品: {result.input['product_name']}")
    lines.append("")
    lines.append("【输入参数】")
    lines.append(f"  Temu 卷王价: {result.input['temu_price']} {result.input['price_currency']}")
    lines.append(f"  1688 拿货价: ¥{result.input['ali1688_price']}")
    lines.append(f"  汇率: {result.input['exchange_rate']}")
    lines.append("")
    lines.append("【计算过程】")
    lines.append(f"  Temu 价格(人民币): ¥{result.calculation['temu_price_cny']}")
    lines.append(f"  回款预估(美元): ${result.calculation['gross_revenue_usd']}")
    lines.append(f"  回款预估(人民币): ¥{result.calculation['gross_revenue_cny']}")
    lines.append(f"  总成本: ¥{result.calculation['total_cost']}")
    lines.append(f"  净利润: ¥{result.calculation['net_profit']}")
    lines.append("")
    lines.append("【决策结果】")
    status_icon = {
        "STRONG_GO": "✅✅",
        "GO": "✅",
        "MARGINAL": "⚠️",
        "PASS": "❌"
    }.get(result.decision["status"], "?")
    lines.append(f"  状态: {status_icon} {result.decision['status']}")
    lines.append(f"  利润率: {result.decision['margin_percentage']}")
    lines.append(f"  建议: {result.decision['recommendation']}")
    lines.append("=" * 50)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Temu V4.1 Pricing Calculator"
    )
    parser.add_argument(
        "--temu-price", type=float,
        help="Temu front-end price (lowest competitor price)"
    )
    parser.add_argument(
        "--currency", type=str, default="USD",
        choices=["USD", "CNY", "usd", "cny"],
        help="Price currency (default: USD)"
    )
    parser.add_argument(
        "--ali1688-price", type=float,
        help="1688 wholesale price in CNY"
    )
    parser.add_argument(
        "--exchange-rate", type=float, default=7.2,
        help="USD to CNY exchange rate (default: 7.2)"
    )
    parser.add_argument(
        "--fulfillment-fee", type=float, default=3.5,
        help="Domestic fulfillment fee in CNY (default: 3.5)"
    )
    parser.add_argument(
        "--input", type=str,
        help="Input JSON file for batch processing"
    )
    parser.add_argument(
        "--output", type=str,
        help="Output JSON file"
    )
    parser.add_argument(
        "--breakeven", action="store_true",
        help="Calculate breakeven price"
    )
    parser.add_argument(
        "--target-profit", type=float,
        help="Calculate required price for target profit"
    )
    parser.add_argument(
        "--profit-threshold", type=float, default=5.0,
        help="Net profit threshold for GO decision (default: 5.0)"
    )
    parser.add_argument(
        "--format", type=str, default="text",
        choices=["text", "json"],
        help="Output format (default: text)"
    )
    
    args = parser.parse_args()
    
    calculator = TemuPricingCalculator(
        exchange_rate=args.exchange_rate,
        fulfillment_fee=args.fulfillment_fee
    )
    calculator.PROFIT_THRESHOLD = args.profit_threshold
    
    if args.input:
        with open(args.input, 'r', encoding='utf-8') as f:
            input_data = json.load(f)
        
        if "products" in input_data:
            products = [
                PricingInput(
                    temu_price=p["temu_price"],
                    currency=p.get("currency", "USD"),
                    ali1688_price=p["ali1688_price"],
                    product_name=p.get("name")
                )
                for p in input_data["products"]
            ]
            results = calculator.calculate_batch(products)
            output = {
                "results": [
                    {
                        "input": r.input,
                        "calculation": r.calculation,
                        "decision": r.decision
                    }
                    for r in results
                ]
            }
        else:
            data = PricingInput(
                temu_price=input_data["temu_price"],
                currency=input_data.get("currency", "USD"),
                ali1688_price=input_data["ali1688_price"]
            )
            result = calculator.calculate(data)
            output = {
                "input": result.input,
                "calculation": result.calculation,
                "decision": result.decision
            }
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(output, f, ensure_ascii=False, indent=2)
            print(f"Results saved to {args.output}")
        else:
            print(json.dumps(output, ensure_ascii=False, indent=2))
        
        return
    
    if args.breakeven and args.ali1688_price:
        result = calculator.calculate_breakeven_price(
            args.ali1688_price,
            args.currency
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    
    if args.target_profit and args.ali1688_price:
        result = calculator.calculate_target_price(
            args.ali1688_price,
            args.target_profit,
            args.currency
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    
    if args.temu_price and args.ali1688_price:
        data = PricingInput(
            temu_price=args.temu_price,
            currency=args.currency,
            ali1688_price=args.ali1688_price
        )
        result = calculator.calculate(data)
        
        if args.format == "json":
            output = {
                "input": result.input,
                "calculation": result.calculation,
                "decision": result.decision
            }
            print(json.dumps(output, ensure_ascii=False, indent=2))
        else:
            print(format_result_output(result))
        return
    
    parser.print_help()


if __name__ == "__main__":
    main()
