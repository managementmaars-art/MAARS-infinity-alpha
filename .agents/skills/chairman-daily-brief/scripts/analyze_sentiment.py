#!/usr/bin/env python3
"""
舆情分析 - 分析新闻的情感倾向
"""

from typing import List, Dict, Any

def analyze_news_sentiment(news_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    """
    分析新闻舆情
    
    Args:
        news_data: 公司新闻数据
        
    Returns:
        舆情分析结果
    """
    result = {
        "overall": "neutral",  # positive, neutral, negative
        "company_sentiment": {},
        "key_topics": [],
        "positive_news": [],
        "negative_news": []
    }
    
    positive_keywords = ["增长", "上涨", "突破", "创新", "强劲", "超预期", "看好", "买入", "升级", "成功", "positive", "growth", "strong", "beat", "upgrade"]
    negative_keywords = ["下跌", "下滑", "亏损", "裁员", "诉讼", "调查", "下调", "卖出", "降级", "风险", "negative", "decline", "loss", "layoff", "lawsuit", "investigation"]
    
    for company, news_list in news_data.items():
        company_score = 0
        company_analysis = {
            "sentiment": "neutral",
            "score": 0,
            "positive_count": 0,
            "negative_count": 0,
            "neutral_count": 0
        }
        
        for news in news_list:
            title = news.get("title", "").lower()
            summary = news.get("summary", "").lower()
            text = title + " " + summary
            
            # 简单的关键词匹配
            pos_count = sum(1 for kw in positive_keywords if kw in text)
            neg_count = sum(1 for kw in negative_keywords if kw in text)
            
            if pos_count > neg_count:
                company_score += 1
                company_analysis["positive_count"] += 1
                result["positive_news"].append({
                    "company": company,
                    "title": news.get("title"),
                    "source": news.get("source")
                })
            elif neg_count > pos_count:
                company_score -= 1
                company_analysis["negative_count"] += 1
                result["negative_news"].append({
                    "company": company,
                    "title": news.get("title"),
                    "source": news.get("source")
                })
            else:
                company_analysis["neutral_count"] += 1
        
        # 判断公司整体情感
        if company_score > 0:
            company_analysis["sentiment"] = "positive"
        elif company_score < 0:
            company_analysis["sentiment"] = "negative"
        else:
            company_analysis["sentiment"] = "neutral"
        
        company_analysis["score"] = company_score
        result["company_sentiment"][company] = company_analysis
    
    # 计算整体情感
    total_score = sum(a["score"] for a in result["company_sentiment"].values())
    if total_score > 0:
        result["overall"] = "positive"
    elif total_score < 0:
        result["overall"] = "negative"
    
    # 提取关键主题
    result["key_topics"] = extract_key_topics(news_data)
    
    return result

def extract_key_topics(news_data: Dict[str, List[Dict[str, Any]]]) -> List[str]:
    """提取关键主题"""
    topics = set()
    topic_keywords = {
        "财报": ["earnings", "revenue", "profit", "财报", "收入", "利润"],
        "产品发布": ["launch", "release", "new product", "发布", "新品"],
        "股价": ["stock price", "shares", "trading", "股价", "股票"],
        "AI/技术": ["AI", "artificial intelligence", "technology", "技术", "人工智能"],
        "监管": ["regulation", "SEC", "investigation", "监管", "调查"],
        "并购": ["acquisition", "merger", "acquire", "并购", "收购"],
        "人事": ["CEO", "executive", "resign", "人事", "高管"]
    }
    
    for company, news_list in news_data.items():
        for news in news_list:
            text = (news.get("title", "") + " " + news.get("summary", "")).lower()
            for topic, keywords in topic_keywords.items():
                if any(kw in text for kw in keywords):
                    topics.add(topic)
    
    return list(topics)[:5]  # 最多返回 5 个主题

if __name__ == "__main__":
    # 测试
    test_data = {
        "AAPL": [
            {"title": "Apple 发布新款 iPhone，市场反应积极", "source": "TechCrunch", "summary": "Apple 今日发布新一代 iPhone，股价应声上涨 2%..."},
        ],
        "TSLA": [
            {"title": "Tesla 宣布裁员 10%", "source": "Reuters", "summary": "Tesla 计划裁员以降低成本..."},
        ]
    }
    
    result = analyze_news_sentiment(test_data)
    import json
    print(json.dumps(result, indent=2, ensure_ascii=False))
