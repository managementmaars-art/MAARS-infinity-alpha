#!/usr/bin/env python3
"""
格式化输出 - 生成丰富报告
"""

from datetime import datetime
from typing import List, Dict, Any

def format_report(
    report_type: str,
    market_data: Dict[str, Any],
    quotes: Dict[str, Any],
    news_data: Dict[str, Any],
    sentiment_data: Dict[str, Any],
    risk_data: Dict[str, Any],
    macro_news: List[Dict[str, Any]],
    executive_summary: str,
    next_steps: List[str],
    gold_price: Dict[str, Any],
    companies: List[str],
    output_format: str = "markdown"
) -> str:
    """格式化报告"""
    
    if output_format == "feishu":
        return format_feishu_report(report_type, market_data, quotes, news_data, sentiment_data, 
                                   risk_data, macro_news, executive_summary, next_steps, gold_price, companies)
    else:
        return format_markdown_report(report_type, market_data, quotes, news_data, sentiment_data,
                                     risk_data, macro_news, executive_summary, next_steps, gold_price, companies)

def format_markdown_report(
    report_type: str,
    market_data: Dict[str, Any],
    quotes: Dict[str, Any],
    news_data: Dict[str, Any],
    sentiment_data: Dict[str, Any],
    risk_data: Dict[str, Any],
    macro_news: List[Dict[str, Any]],
    executive_summary: str,
    next_steps: List[str],
    gold_price: Dict[str, Any],
    companies: List[str]
) -> str:
    """生成 Markdown 格式报告"""
    
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    report_name = "早报" if report_type == "morning" else "晚报"
    
    lines = []
    
    # 标题
    lines.append(f"# 📊 董事长{report_name} - {now}")
    lines.append("")
    
    # 高管摘要 - 最重要信息放在最前面
    lines.append("## 🎯 今日要点")
    lines.append("")
    lines.append(f"**{executive_summary}**")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # 市场行情
    lines.append("## 📈 市场行情")
    lines.append("")
    
    if market_data.get("note"):
        lines.append(f"*{market_data['note']}*")
        lines.append("")
    
    # 大盘指数
    lines.append("### 大盘指数")
    lines.append("")
    for index in market_data.get("indices", []):
        change_emoji = "🟢" if "+" in str(index.get("change_percent", "")) else "🔴"
        volume = index.get("volume", "")
        volume_str = f" | 成交: {volume}" if volume else ""
        lines.append(f"- {change_emoji} **{index['name']}**: {index['price']} ({index.get('change_percent', 'N/A')}){volume_str}")
    lines.append("")
    
    # 金价
    if gold_price and gold_price.get("price"):
        lines.append(f"### 🥇 黄金价格")
        lines.append(f"- 💰 **国际金价**: {gold_price.get('price')} {gold_price.get('currency', 'USD')}")
        lines.append("")
    
    # 关注公司行情
    if quotes:
        lines.append("### 关注公司行情")
        lines.append("")
        lines.append("| 公司 | 现价 | 涨跌 | 涨跌幅 | 成交量 | 市值 |")
        lines.append("|------|------|------|--------|--------|------|")
        for symbol, quote in quotes.items():
            change_emoji = "🟢" if "+" in str(quote.get("change_percent", "")) else "🔴"
            lines.append(f"| {change_emoji} {symbol} | {quote.get('price', 'N/A')} | {quote.get('change', 'N/A')} | {quote.get('change_percent', 'N/A')} | {quote.get('volume', 'N/A')} | {quote.get('market_cap', 'N/A')} |")
        lines.append("")
    
    # 宏观新闻 / 国内外大事
    if macro_news:
        lines.append("## 🌍 宏观要闻")
        lines.append("")
        for i, news in enumerate(macro_news, 1):
            lines.append(f"**{i}. {news['title']}**")
            lines.append(f"- 💡 影响: {news['impact']}")
            lines.append(f"- 📰 来源: {news['source']}")
            lines.append("")
    
    # 公司新闻
    lines.append("## 🏢 公司动态")
    lines.append("")
    
    for company in companies:
        # 行情
        if company in quotes:
            q = quotes[company]
            change_emoji = "📈" if "+" in str(q.get("change_percent", "")) else "📉"
            lines.append(f"### {change_emoji} {company} - {q.get('price', 'N/A')} ({q.get('change_percent', 'N/A')})")
        else:
            lines.append(f"### {company}")
        
        lines.append("")
        
        # 新闻
        company_news = news_data.get("news", {}).get(company, [])
        if company_news:
            for news in company_news[:3]:
                impact_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(news.get('impact', 'medium'), "⚪")
                sentiment_emoji = {"positive": "✅", "negative": "⚠️", "neutral": "➖"}.get(news.get('sentiment', 'neutral'), "➖")
                lines.append(f"{impact_emoji} **{news['source']}**: {news['title']}")
                lines.append(f"   {sentiment_emoji} {news.get('summary', '')}")
                lines.append("")
        else:
            lines.append("- 暂无重要新闻")
            lines.append("")
        
        # 社媒监控
        social = news_data.get("social_media", {}).get(company, {})
        if social:
            lines.append("**社媒热度:**")
            twitter = social.get("twitter", {})
            weibo = social.get("weibo", {})
            if twitter.get("mentions", 0) > 0:
                lines.append(f"- 🐦 Twitter: {twitter.get('mentions', 0)} 提及 | 情感: {twitter.get('sentiment', 'neutral')}")
            if weibo.get("mentions", 0) > 0:
                lines.append(f"- 📱 微博: {weibo.get('mentions', 0)} 讨论 | 热度: {weibo.get('reading_count', '0')}")
            lines.append("")
    
    # 热点主题
    hot_topics = news_data.get("hot_topics", [])
    if hot_topics:
        lines.append("### 🔥 热点主题")
        lines.append("")
        lines.append(" ".join([f"`{topic}`" for topic in hot_topics]))
        lines.append("")
    
    # 舆情分析
    lines.append("## 📊 舆情分析")
    lines.append("")
    
    sentiment_emoji = {"positive": "🟢 正面", "neutral": "⚪ 中性", "negative": "🔴 负面"}
    overall = sentiment_data.get("overall", "neutral")
    lines.append(f"**整体舆情**: {sentiment_emoji.get(overall, overall)}")
    lines.append("")
    
    # 各公司情感表
    lines.append("| 公司 | 舆情 | 正面 | 负面 | 中性 | 热度 |")
    lines.append("|------|------|------|------|------|------|")
    for company in companies:
        s = sentiment_data.get("company_sentiment", {}).get(company, {})
        sentiment_label = sentiment_emoji.get(s.get("sentiment", "neutral"), "⚪")
        social = news_data.get("social_media", {}).get(company, {})
        mentions = social.get("twitter", {}).get("mentions", 0) + social.get("weibo", {}).get("mentions", 0)
        lines.append(f"| {company} | {sentiment_label} | {s.get('positive_count', 0)} | {s.get('negative_count', 0)} | {s.get('neutral_count', 0)} | {mentions} |")
    lines.append("")
    
    # 风险预警
    lines.append("## ⚠️ 风险预警")
    lines.append("")
    
    risk_level = risk_data.get("risk_level", "low")
    risk_emoji = {"low": "🟢 低风险", "medium": "🟡 中风险", "high": "🔴 高风险"}
    risk_color = {"low": "✅", "medium": "⚡", "high": "🚨"}
    lines.append(f"**整体风险等级**: {risk_emoji.get(risk_level, risk_level)} {risk_color.get(risk_level, '✅')}")
    lines.append("")
    
    if risk_data.get("risks"):
        lines.append("| 等级 | 公司 | 类型 | 描述 |")
        lines.append("|------|------|------|------|")
        for risk in risk_data["risks"][:5]:
            level_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(risk['level'], "⚪")
            lines.append(f"| {level_emoji} {risk['level']} | {risk['company']} | {risk['type']} | {risk['title'][:30]}... |")
    else:
        lines.append("- ✅ 未检测到明显风险")
    
    lines.append("")
    
    # 公关建议
    from risk_detection import get_pr_recommendation
    lines.append("### 💡 公关建议")
    lines.append("")
    lines.append(get_pr_recommendation(risk_data))
    lines.append("")
    
    # 投资建议
    from risk_detection import get_investment_recommendation
    lines.append("### 📈 投资建议")
    lines.append("")
    lines.append(get_investment_recommendation(quotes, sentiment_data))
    lines.append("")
    
    # 下一步行动
    lines.append("## 🎯 下一步行动")
    lines.append("")
    for step in next_steps:
        lines.append(f"- {step}")
    lines.append("")
    
    # 页脚
    lines.append("---")
    lines.append("*本报告由 Chairman Daily Report Skill 自动生成*")
    lines.append("*数据时间: {}*".format(now))
    
    return "\n".join(lines)

def format_feishu_report(*args, **kwargs):
    """飞书格式（复用 Markdown）"""
    return format_markdown_report(*args, **kwargs)

if __name__ == "__main__":
    print("Format output module loaded successfully")
