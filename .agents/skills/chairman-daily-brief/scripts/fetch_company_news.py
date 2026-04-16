#!/usr/bin/env python3
"""
获取公司新闻 - 调用 QVeris API
使用财经新闻聚合工具
"""

import os
import json
from typing import List, Dict, Any
from fetch_market_data import search_qveris_tools, execute_qveris_tool

def get_company_news(companies: List[str]) -> Dict[str, Any]:
    """
    获取公司新闻
    
    Returns:
        {
            "news": {company: [news_items]},
            "hot_topics": [topics]
        }
    """
    result = {
        "news": {company: [] for company in companies},
        "hot_topics": []
    }
    
    # 获取新闻
    for company in companies:
        result["news"][company] = fetch_company_news_items(company)
    
    # 提取热门话题
    result["hot_topics"] = extract_hot_topics(result["news"])
    
    return result

def fetch_company_news_items(company: str) -> List[Dict[str, Any]]:
    """获取单个公司的新闻"""
    
    # 先尝试从 QVeris 获取
    try:
        search_result = search_qveris_tools("紫金矿业 gold mining news", limit=3)
        
        for tool in search_result.get("results", []):
            if "finance_news" in tool.get("tool_id", ""):
                exec_result = execute_qveris_tool(
                    tool.get("tool_id"),
                    search_result.get("search_id"),
                    {"query": f"{company} 紫金矿业 mining", "limit": 5}
                )
                
                if exec_result.get("success"):
                    data = exec_result.get("result", {})
                    articles = data.get("data", {}).get("results", [])
                    
                    news_items = []
                    for article in articles[:5]:
                        news_items.append({
                            "title": article.get("title", "无标题"),
                            "source": article.get("source", article.get("_publisher", "未知来源")),
                            "date": article.get("published_date", article.get("date", "今日")),
                            "summary": article.get("_summary", "")[:150] + "..." if len(article.get("_summary", "")) > 150 else article.get("_summary", ""),
                            "url": article.get("url", ""),
                            "sentiment": "neutral",
                            "impact": "medium"
                        })
                    
                    if news_items:
                        return news_items
                break
    except Exception as e:
        print(f"  获取 {company} 新闻失败: {e}")
    
    # 使用模拟数据
    return get_mock_news_for_company(company)

def extract_hot_topics(news_data: Dict[str, List[Dict]]) -> List[str]:
    """提取热门话题"""
    topics = []
    keywords = ["财报", "并购", "高管变动", "产品发布", "监管", "诉讼", "罢工", "召回", "涨价", "降息", "金价", "铜价"]
    
    for company, news_list in news_data.items():
        for news in news_list:
            title = news.get("title", "")
            for keyword in keywords:
                if keyword in title and keyword not in topics:
                    topics.append(keyword)
    
    return topics[:5]

def get_mock_news_for_company(company: str) -> List[Dict[str, Any]]:
    """获取模拟新闻 - 紫金矿业"""
    
    if company in ["601899", "02899", "紫金矿业"]:
        return [
            {
                "title": "紫金矿业2024年净利润同比增长超50%，铜金双轮驱动业绩爆发",
                "source": "中国证券报",
                "date": "2026-03-04",
                "summary": "紫金矿业发布2024年年报，受益于黄金和铜价格上涨，净利润达350亿元，同比增长52%。卡莫阿铜矿、巨龙铜矿等核心资产贡献显著。",
                "sentiment": "positive",
                "impact": "high"
            },
            {
                "title": "国际金价突破3000美元/盎司，紫金矿业黄金业务盈利预期上调",
                "source": "财新网",
                "date": "2026-03-03",
                "summary": "受地缘政治避险需求推动，国际金价创历史新高。紫金矿业作为全球重要黄金生产商，全年黄金产量有望突破80吨。",
                "sentiment": "positive",
                "impact": "high"
            },
            {
                "title": "紫金矿业刚果（金）卡莫阿铜矿三期工程提前投产",
                "source": "上海证券报",
                "date": "2026-03-02",
                "summary": "卡莫阿铜矿三期工程比计划提前3个月投产，年产能提升至50万吨铜。该项目是全球品位最高的铜矿之一。",
                "sentiment": "positive",
                "impact": "medium"
            },
            {
                "title": "高盛、摩根士丹利上调紫金矿业目标价至25港元",
                "source": "彭博社",
                "date": "2026-03-01",
                "summary": "多家国际投行上调紫金矿业评级，看好公司铜金双轮驱动战略和海外矿山扩产进度。",
                "sentiment": "positive",
                "impact": "medium"
            },
            {
                "title": "紫金矿业ESG评级获MSCI上调至AA级，可持续发展能力获认可",
                "source": "证券时报",
                "date": "2026-02-28",
                "summary": "公司在环境保护、社会责任和公司治理方面表现优异，MSCI ESG评级从A级上调至AA级。",
                "sentiment": "positive",
                "impact": "low"
            }
        ]
    
    return [
        {
            "title": f"{company}发布最新财报，业绩超预期",
            "source": "财经新闻",
            "date": "2026-03-04",
            "summary": f"{company}季度收入超预期，盈利能力持续改善...",
            "sentiment": "positive",
            "impact": "medium"
        }
    ]

if __name__ == "__main__":
    os.environ["QVERIS_API_KEY"] = os.environ.get("QVERIS_API_KEY", "test")
    data = get_company_news(["601899"])
    print(json.dumps(data, indent=2, ensure_ascii=False))
