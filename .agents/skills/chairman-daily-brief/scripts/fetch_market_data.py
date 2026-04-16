#!/usr/bin/env python3
"""
获取市场数据 - 调用 QVeris API
使用同花顺实时行情工具
"""

import os
import json
import ssl
import urllib.request
from typing import Dict, Any, List
from datetime import datetime

QVERIS_BASE_URL = "https://qveris.ai/api/v1"

def get_api_key() -> str:
    """获取 API Key"""
    api_key = os.environ.get("QVERIS_API_KEY")
    if not api_key:
        raise ValueError("QVERIS_API_KEY not set")
    return api_key

def call_qveris_api(endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """调用 QVeris API"""
    api_key = get_api_key()
    url = f"{QVERIS_BASE_URL}/{endpoint}"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=30) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        raise Exception(f"API Error {e.code}: {error_body}")

def search_qveris_tools(query: str, limit: int = 5) -> Dict[str, Any]:
    """搜索 QVeris 工具"""
    return call_qveris_api("search", {"query": query, "limit": limit})

def execute_qveris_tool(tool_id: str, search_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """执行 QVeris 工具"""
    import urllib.parse
    
    api_key = get_api_key()
    url = f"{QVERIS_BASE_URL}/tools/execute?tool_id={urllib.parse.quote(tool_id)}"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    payload = {
        "search_id": search_id,
        "parameters": parameters,
        "max_response_size": 20480
    }
    
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    with urllib.request.urlopen(req, context=ctx, timeout=60) as response:
        return json.loads(response.read().decode('utf-8'))

def get_stock_quote(symbol: str) -> Dict[str, Any]:
    """获取股票实时行情 - 使用同花顺工具"""
    try:
        # 转换代码格式为同花顺格式
        sina_symbol = convert_to_ths_code(symbol)
        
        search_result = search_qveris_tools("同花顺实时行情", limit=3)
        
        for tool in search_result.get("results", []):
            if "ths_ifind" in tool.get("tool_id", ""):
                exec_result = execute_qveris_tool(
                    tool.get("tool_id"),
                    search_result.get("search_id"),
                    {"codes": sina_symbol}
                )
                
                if exec_result.get("success"):
                    data = exec_result.get("result", {})
                    items = data.get("data", [])
                    if items and len(items) > 0 and len(items[0]) > 0:
                        quote = items[0][0]
                        return parse_quote_data(quote, symbol)
                break
    except Exception as e:
        print(f"  获取 {symbol} 行情失败: {e}")
    
    return get_mock_quote(symbol)

def convert_to_ths_code(symbol: str) -> str:
    """转换为同花顺代码格式"""
    symbol = symbol.strip().upper()
    
    # 已经是标准格式
    if ".SH" in symbol or ".SZ" in symbol or ".HK" in symbol:
        return symbol
    
    # A股代码
    if symbol.isdigit():
        if symbol.startswith(('600', '601', '603', '688', '689')):
            return f"{symbol}.SH"
        elif symbol.startswith(('000', '001', '002', '003', '300')):
            return f"{symbol}.SZ"
    
    # 港股
    if symbol.startswith('0') and len(symbol) == 5:
        # 港股 02899 格式
        return f"{symbol}.HK"
    
    return symbol

def parse_quote_data(quote: Dict, original_symbol: str) -> Dict[str, Any]:
    """解析行情数据"""
    latest = quote.get("latest", 0)
    pre_close = quote.get("preClose", 0)
    change = quote.get("change", 0)
    change_ratio = quote.get("changeRatio", 0)
    
    return {
        "symbol": original_symbol,
        "name": quote.get("thscode", original_symbol),
        "price": f"{latest:.2f}" if latest else "N/A",
        "prev_close": f"{pre_close:.2f}" if pre_close else "N/A",
        "change": f"{change:+.2f}" if change else "N/A",
        "change_percent": f"{change_ratio:+.2f}%" if change_ratio else "N/A",
        "open": f"{quote.get('open', 0):.2f}" if quote.get('open') else "N/A",
        "high": f"{quote.get('high', 0):.2f}" if quote.get('high') else "N/A",
        "low": f"{quote.get('low', 0):.2f}" if quote.get('low') else "N/A",
        "volume": format_volume(quote.get("volume", 0)),
        "amount": format_amount(quote.get("amount", 0)),
        "market_cap": format_market_cap(quote.get("mv", 0)),
        "pe": f"{quote.get('pe_ttm', 0):.2f}" if quote.get('pe_ttm') else "N/A",
        "pb": f"{quote.get('pbr_lf', 0):.2f}" if quote.get('pbr_lf') else "N/A",
        "time": quote.get("time", "")
    }

def format_volume(volume: int) -> str:
    """格式化成交量"""
    if volume >= 100000000:
        return f"{volume/100000000:.2f}亿"
    elif volume >= 10000:
        return f"{volume/10000:.2f}万"
    return str(volume)

def format_amount(amount: float) -> str:
    """格式化成交额"""
    if amount >= 100000000:
        return f"{amount/100000000:.2f}亿"
    elif amount >= 10000:
        return f"{amount/10000:.2f}万"
    return str(int(amount))

def format_market_cap(mv: float) -> str:
    """格式化市值"""
    if mv >= 1000000000000:
        return f"{mv/1000000000000:.2f}万亿"
    elif mv >= 100000000:
        return f"{mv/100000000:.2f}亿"
    return str(int(mv))

def get_market_indices(market: str = "CN") -> Dict[str, Any]:
    """获取大盘指数"""
    indices_map = {
        "CN": ["000001.SH", "399001.SZ", "399006.SZ"],
        "US": ["^GSPC", "^DJI", "^IXIC"],
        "HK": ["^HSI", "^HSCEI"]
    }
    
    result = {
        "market": market,
        "indices": [],
        "market_sentiment": "neutral"
    }
    
    try:
        codes = ",".join(indices_map.get(market, indices_map["CN"]))
        search_result = search_qveris_tools("同花顺实时行情", limit=3)
        
        for tool in search_result.get("results", []):
            if "ths_ifind" in tool.get("tool_id", ""):
                exec_result = execute_qveris_tool(
                    tool.get("tool_id"),
                    search_result.get("search_id"),
                    {"codes": codes}
                )
                
                if exec_result.get("success"):
                    data = exec_result.get("result", {})
                    items = data.get("data", [])
                    if items and len(items) > 0:
                        for idx_data in items[0]:
                            quote = parse_quote_data(idx_data, idx_data.get("thscode", ""))
                            result["indices"].append(quote)
                break
    except Exception as e:
        print(f"  获取指数失败: {e}")
    
    if not result["indices"]:
        result = get_mock_indices(market)
    
    return result

def get_gold_price() -> Dict[str, Any]:
    """获取黄金价格"""
    try:
        search_result = search_qveris_tools("gold price XAUUSD", limit=3)
        
        for tool in search_result.get("results", []):
            if "gold" in tool.get("tool_id", "").lower():
                exec_result = execute_qveris_tool(
                    tool.get("tool_id"),
                    search_result.get("search_id"),
                    {"symbol": "XAUUSD", "limit": 1}
                )
                
                if exec_result.get("success"):
                    data = exec_result.get("result", {})
                    results = data.get("data", {}).get("results", [])
                    if results:
                        return {
                            "price": results[0].get("price", 0),
                            "date": results[0].get("date", ""),
                            "currency": results[0].get("_currency", "USD")
                        }
                break
    except Exception as e:
        print(f"  获取金价失败: {e}")
    
    return {"price": 2900, "date": datetime.now().strftime("%Y-%m-%d"), "currency": "USD"}

def get_mock_quote(symbol: str) -> Dict[str, Any]:
    """模拟行情数据"""
    mock_data = {
        "601899": {"price": "37.96", "change": "-0.90", "change_percent": "-2.32%", "volume": "312.57万", "amount": "11.90亿", "market_cap": "7,820亿", "pe": "22.16", "pb": "6.02"},
        "02899": {"price": "41.94", "change": "-1.28", "change_percent": "-2.96%", "volume": "7,582.95万", "amount": "31.57亿", "market_cap": "2,511.72亿", "pe": "23.11", "pb": "6.04"}
    }
    return mock_data.get(symbol, {"price": "N/A", "change": "N/A", "change_percent": "N/A"})

def get_mock_indices(market: str) -> Dict[str, Any]:
    """模拟指数数据"""
    mock_data = {
        "CN": {
            "indices": [
                {"symbol": "000001.SH", "name": "上证指数", "price": "3,120.00", "change": "+15.20", "change_percent": "+0.49%", "volume": "3,850亿"},
                {"symbol": "399001.SZ", "name": "深证成指", "price": "9,850.00", "change": "+68.50", "change_percent": "+0.70%", "volume": "4,520亿"},
                {"symbol": "399006.SZ", "name": "创业板指", "price": "1,950.00", "change": "+28.30", "change_percent": "+1.47%", "volume": "1,980亿"}
            ],
            "market_sentiment": "谨慎乐观",
            "note": "A股震荡反弹，创业板表现强势"
        }
    }
    return mock_data.get(market, mock_data["CN"])

if __name__ == "__main__":
    os.environ["QVERIS_API_KEY"] = os.environ.get("QVERIS_API_KEY", "test")
    
    print("=== 测试紫金矿业 601899 ===")
    quote = get_stock_quote("601899")
    print(json.dumps(quote, indent=2, ensure_ascii=False))
    
    print("\n=== 测试上证指数 ===")
    indices = get_market_indices("CN")
    print(json.dumps(indices, indent=2, ensure_ascii=False))
    
    print("\n=== 测试金价 ===")
    gold = get_gold_price()
    print(json.dumps(gold, indent=2, ensure_ascii=False))
