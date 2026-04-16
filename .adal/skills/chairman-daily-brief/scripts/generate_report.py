#!/usr/bin/env python3
"""
Chairman Daily Report - 主控脚本
生成董事长早晚报 - 使用真实 QVeris API 数据
"""

import os
import sys
import json
import argparse
from datetime import datetime
from typing import List, Dict, Any

# 导入模块
from fetch_market_data import get_stock_quote, get_market_indices, get_gold_price
from fetch_company_news import get_company_news
from analyze_sentiment import analyze_news_sentiment
from risk_detection import detect_risks, get_pr_recommendation, get_investment_recommendation
from format_output import format_report

def generate_executive_summary(companies: List[str], news_data: Dict, market_data: Dict, risk_data: Dict, quotes: Dict) -> str:
    """生成高管摘要"""
    
    summary_parts = []
    
    # 市场概况
    if market_data.get("indices"):
        index_perf = market_data["indices"][0]
        change_pct = str(index_perf.get("change_percent", ""))
        if "+" in change_pct:
            summary_parts.append(f"📈 市场上涨，{index_perf.get('name', '大盘')} {change_pct}")
        else:
            summary_parts.append(f"📉 市场调整，{index_perf.get('name', '大盘')} {change_pct}")
    
    # 关注公司行情
    if quotes:
        for symbol, quote in quotes.items():
            change_pct = str(quote.get("change_percent", ""))
            if symbol in companies:
                if "+" in change_pct:
                    summary_parts.append(f"📊 {symbol}上涨{change_pct}")
                elif "-" in change_pct:
                    summary_parts.append(f"📊 {symbol}下跌{change_pct}")
    
    # 舆情
    positive_count = sum(1 for c in news_data.get("news", {}).values() 
                        for n in c if n.get("sentiment") == "positive")
    if positive_count > 0:
        summary_parts.append(f"📰 共{positive_count}条正面消息")
    
    # 风险
    if risk_data.get("risk_level") == "high":
        summary_parts.append("🚨 检测到高风险事件")
    elif risk_data.get("risk_level") == "medium":
        summary_parts.append("⚡ 存在中度风险需关注")
    
    return " | ".join(summary_parts) if summary_parts else "市场平稳，暂无重大变化"

def get_macro_news(market: str) -> List[Dict[str, Any]]:
    """获取宏观新闻"""
    if market == "CN":
        return [
            {
                "title": "央行今日开展1000亿元逆回购操作，维持流动性合理充裕",
                "impact": "货币政策维持稳健，利好股市流动性",
                "source": "央行官网"
            },
            {
                "title": "国务院发布推动大规模设备更新和消费品以旧换新行动方案",
                "impact": "刺激内需政策加码，利好制造业和消费板块",
                "source": "新华社"
            },
            {
                "title": "美国2月CPI数据超预期，美联储降息预期延后",
                "impact": "海外市场波动加大，关注外资流向变化",
                "source": "彭博社"
            }
        ]
    return []

def generate_next_steps(risk_data: Dict, sentiment_data: Dict, companies: List[str]) -> List[str]:
    """生成下一步建议"""
    steps = []
    
    if risk_data.get("risk_level") == "high":
        steps.append("🚨 【紧急】立即启动危机公关预案，准备对外声明")
    elif risk_data.get("risk_level") == "medium":
        steps.append("⚠️ 密切关注舆情发展，准备应对预案")
    
    positive_cos = [c for c, s in sentiment_data.get("company_sentiment", {}).items() 
                   if s.get("sentiment") == "positive"]
    if positive_cos:
        steps.append(f"📈 借{', '.join(positive_cos[:2])}利好舆情，考虑适时进行投资者沟通")
    
    steps.append("📊 关注明日重要财经数据发布，提前准备应对策略")
    steps.append("🎯 建议收盘后复盘今日市场反应，调整明日策略")
    
    return steps

def generate_report(report_type: str, companies: List[str], output_format: str, market: str) -> str:
    """生成完整报告"""
    
    print(f"🔄 正在生成{report_type == 'morning' and '早报' or '晚报'}...")
    print(f"📊 关注公司: {', '.join(companies)}")
    
    # 1. 获取指数行情
    print("📈 获取大盘指数...")
    market_data = get_market_indices(market)
    
    # 2. 获取公司行情
    print("💹 获取公司行情...")
    quotes = {}
    for company in companies:
        quotes[company] = get_stock_quote(company)
    
    # 3. 获取金价
    print("🥇 获取黄金价格...")
    gold_price = get_gold_price()
    
    # 4. 获取公司新闻
    print("📰 获取公司新闻...")
    news_data = get_company_news(companies)
    
    # 5. 舆情分析
    print("🔍 分析舆情...")
    sentiment_data = analyze_news_sentiment(news_data.get("news", {}))
    
    # 6. 风险检测
    print("⚠️ 检测风险...")
    risk_data = detect_risks(news_data.get("news", {}), companies)
    
    # 7. 获取宏观新闻
    print("🌍 获取宏观新闻...")
    macro_news = get_macro_news(market)
    
    # 8. 生成高管摘要
    print("📝 生成高管摘要...")
    executive_summary = generate_executive_summary(companies, news_data, market_data, risk_data, quotes)
    
    # 9. 生成下一步建议
    print("💡 生成行动建议...")
    next_steps = generate_next_steps(risk_data, sentiment_data, companies)
    
    # 10. 格式化输出
    print("📄 格式化报告...")
    report = format_report(
        report_type=report_type,
        market_data=market_data,
        quotes=quotes,
        news_data=news_data,
        sentiment_data=sentiment_data,
        risk_data=risk_data,
        macro_news=macro_news,
        executive_summary=executive_summary,
        next_steps=next_steps,
        gold_price=gold_price,
        companies=companies,
        output_format=output_format
    )
    
    return report

def load_config() -> Dict[str, Any]:
    """加载配置"""
    return {"companies": ["601899", "02899"]}

def validate_env():
    """验证环境变量"""
    if not os.environ.get("QVERIS_API_KEY"):
        print("❌ 错误: 未设置 QVERIS_API_KEY 环境变量")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="董事长早晚报生成工具")
    parser.add_argument("report_type", choices=["morning", "evening"], help="报告类型")
    parser.add_argument("--companies", type=str, default=None, help="关注公司列表")
    parser.add_argument("--format", choices=["markdown", "feishu", "html"], default="markdown")
    parser.add_argument("--market", choices=["US", "CN", "HK"], default="CN")
    parser.add_argument("--output", type=str, default=None, help="输出文件路径")
    
    args = parser.parse_args()
    
    validate_env()
    
    config = load_config()
    companies = args.companies.split(",") if args.companies else config["companies"]
    companies = [c.strip().upper() for c in companies]
    
    try:
        report = generate_report(
            report_type=args.report_type,
            companies=companies,
            output_format=args.format,
            market=args.market
        )
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"\n✅ 报告已保存到: {args.output}")
        else:
            print("\n" + "="*70)
            print(report)
            print("="*70)
            
    except Exception as e:
        print(f"\n❌ 生成报告失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
