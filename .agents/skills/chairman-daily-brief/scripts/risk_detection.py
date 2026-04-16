#!/usr/bin/env python3
"""
风险检测 - 识别新闻中的潜在风险
增强版：添加投资建议
"""

from typing import List, Dict, Any

def detect_risks(news_data: Dict[str, List[Dict[str, Any]]], companies: List[str]) -> Dict[str, Any]:
    """检测风险"""
    result = {
        "risk_level": "low",
        "risk_count": 0,
        "risks": [],
        "risk_by_company": {}
    }
    
    # 风险关键词库
    risk_keywords = {
        "high": {
            "诉讼": ["lawsuit", "诉讼", "控告", "索赔", "赔偿", "被告"],
            "调查": ["investigation", "probe", "调查", "审查", " subpoena", "证监会调查"],
            "财务造假": ["fraud", "accounting irregularities", "财务造假", "假账", "虚增"],
            "破产": ["bankruptcy", "insolvency", "破产", "资不抵债"],
            "监管处罚": ["SEC fine", "regulatory penalty", "处罚", "罚款", "制裁", "退市"]
        },
        "medium": {
            "裁员": ["layoff", "job cut", "裁员", "解雇", "失业", "优化"],
            "业绩下滑": ["missed earnings", "profit decline", "业绩下滑", "亏损", "不及预期", "预警"],
            "高管离职": ["CEO resignation", "executive departure", "高管离职", "董事长辞职"],
            "产品问题": ["product recall", "defect", "召回", "质量问题", "故障", "事故"],
            "竞争压力": ["competition", "market share loss", "竞争", "份额下降", "价格战"]
        },
        "low": {
            "股价波动": ["volatile", "stock drop", "股价下跌", "暴跌", "跌停"],
            "评级下调": ["downgrade", "rating cut", "下调评级", "减持", "卖出评级"],
            "负面报道": ["negative", "批评", "质疑", "争议"]
        }
    }
    
    for company in companies:
        company_news = news_data.get(company, [])
        company_risks = []
        
        for news in company_news:
            title = news.get("title", "").lower()
            summary = news.get("summary", "").lower()
            text = title + " " + summary
            
            # 检测风险
            for level, keywords_dict in risk_keywords.items():
                for risk_type, keywords in keywords_dict.items():
                    if any(kw in text for kw in keywords):
                        company_risks.append({
                            "level": level,
                            "type": risk_type,
                            "title": news.get("title"),
                            "source": news.get("source"),
                            "company": company
                        })
                        break
        
        result["risk_by_company"][company] = company_risks
        result["risks"].extend(company_risks)
    
    # 计算整体风险等级
    high_risks = len([r for r in result["risks"] if r["level"] == "high"])
    medium_risks = len([r for r in result["risks"] if r["level"] == "medium"])
    
    if high_risks > 0:
        result["risk_level"] = "high"
    elif medium_risks > 0:
        result["risk_level"] = "medium"
    
    result["risk_count"] = len(result["risks"])
    
    return result

def get_pr_recommendation(risk_data: Dict[str, Any]) -> str:
    """生成公关建议"""
    level = risk_data.get("risk_level", "low")
    
    recommendations = {
        "high": """🚨 **高风险警告**

**立即行动:**
1. 启动危机公关应急预案，成立专项小组
2. 准备官方声明稿，统一对外口径
3. 安排核心高管接受权威媒体采访
4. 监控舆情发酵，每小时汇报进展
5. 准备法律应对措施""",
        
        "medium": """⚡ **中度关注**

**建议措施:**
1. 密切关注舆情走向，准备应对预案
2. 整理公司正面素材，建立内容弹药库
3. 适时主动发布正面信息引导舆论
4. 加强与核心媒体沟通
5. 评估是否需要官方回应""",
        
        "low": """✅ **风险可控**

**常规监控:**
1. 保持正常舆情监测频率
2. 关注行业动态和竞品动向
3. 积累正面传播素材
4. 维护媒体关系"""
    }
    
    return recommendations.get(level, recommendations["low"])

def get_investment_recommendation(quotes: Dict[str, Any], sentiment_data: Dict[str, Any]) -> str:
    """生成投资建议"""
    
    recommendations = []
    
    # 基于行情的建议
    for symbol, quote in quotes.items():
        change_pct = str(quote.get("change_percent", ""))
        if "+" in change_pct:
            try:
                pct_val = float(change_pct.replace("+", "").replace("%", ""))
                if pct_val > 5:
                    recommendations.append(f"📈 **{symbol}**: 今日大涨 {change_pct}，可考虑逢高减仓，锁定利润")
                elif pct_val > 2:
                    recommendations.append(f"📊 **{symbol}**: 今日上涨 {change_pct}，趋势良好，可持有观望")
            except:
                pass
        elif "-" in change_pct:
            try:
                pct_val = float(change_pct.replace("-", "").replace("%", ""))
                if pct_val > 5:
                    recommendations.append(f"📉 **{symbol}**: 今日大跌 {change_pct}，需关注是否有抄底机会或止损")
                elif pct_val > 2:
                    recommendations.append(f"📊 **{symbol}**: 今日回调 {change_pct}，关注支撑位，暂不建议加仓")
            except:
                pass
    
    # 基于舆情的建议
    for company, sentiment in sentiment_data.get("company_sentiment", {}).items():
        if sentiment.get("sentiment") == "positive" and sentiment.get("positive_count", 0) >= 3:
            recommendations.append(f"✅ **{company}**: 舆情积极，消息面利好，可考虑逢低布局")
        elif sentiment.get("sentiment") == "negative":
            recommendations.append(f"⚠️ **{company}**: 负面舆情较多，建议观望，等待情绪修复")
    
    if not recommendations:
        return "📊 **市场平稳**: 建议维持现有仓位，关注明日重要数据发布"
    
    return "\n".join(recommendations)

if __name__ == "__main__":
    # 测试
    test_data = {
        "AAPL": [{"title": "Apple 发布新款", "source": "TechCrunch", "summary": "Apple 今日发布..."}],
        "TSLA": [{"title": "Tesla 面临 SEC 调查", "source": "Reuters", "summary": "SEC 正在调查..."}]
    }
    
    result = detect_risks(test_data, ["AAPL", "TSLA"])
    import json
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("\n公关建议:")
    print(get_pr_recommendation(result))
