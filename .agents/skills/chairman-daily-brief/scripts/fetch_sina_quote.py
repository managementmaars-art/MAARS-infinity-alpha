#!/usr/bin/env python3
"""
备用行情数据源 - 新浪财经
当 QVeris API 不可用时使用
"""

import json
import urllib.request
import ssl
from typing import Dict, Any

def get_stock_quote_sina(symbol: str) -> Dict[str, Any]:
    """
    从新浪财经获取股票行情
    
    支持格式:
    - A股: sh601899 (上证), sz000001 (深证)
    - 港股: hk02899
    - 美股: gb_aapl
    """
    
    # 转换代码格式
    sina_code = convert_to_sina_code(symbol)
    if not sina_code:
        return {}
    
    url = f"https://hq.sinajs.cn/list={sina_code}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://finance.sina.com.cn'
    }
    
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
            data = response.read().decode('gb2312', errors='ignore')
            return parse_sina_data(data, symbol)
    except Exception as e:
        print(f"  新浪财经获取 {symbol} 失败: {e}")
        return {}

def convert_to_sina_code(symbol: str) -> str:
    """转换为新浪代码格式"""
    symbol = symbol.strip().upper()
    
    # 已经是新浪格式
    if symbol.startswith(('SH', 'SZ', 'HK', 'GB_')):
        return symbol.lower()
    
    # A股代码判断
    if symbol.isdigit():
        # 上证: 600/601/603/688 开头
        if symbol.startswith(('600', '601', '603', '688', '689')):
            return f"sh{symbol}"
        # 深证: 000/001/002/003/300 开头
        elif symbol.startswith(('000', '001', '002', '003', '300')):
            return f"sz{symbol}"
    
    # 港股代码 (如 0700.HK, 02899)
    if '.HK' in symbol:
        code = symbol.replace('.HK', '').replace('.hk', '')
        # 港股去掉前导零
        code = code.lstrip('0')
        return f"hk{code}"
    elif symbol.startswith('0') and len(symbol) == 5:
        # 港股 02899 格式
        code = symbol.lstrip('0')
        return f"hk{code}"
    
    # 美股
    return f"gb_{symbol.lower()}"

def parse_sina_data(data: str, original_symbol: str) -> Dict[str, Any]:
    """解析新浪返回的数据"""
    
    try:
        # 数据格式: var hq_str_sh601899="紫金矿业,17.850,..."
        if '="' not in data:
            return {}
        
        content = data.split('="')[1].rstrip('";')
        parts = content.split(',')
        
        if len(parts) < 10:
            return {}
        
        # 根据市场类型解析
        if original_symbol.startswith(('6', '0', '3')) or '.SS' in original_symbol or '.SZ' in original_symbol:
            # A股格式: 名称,今日开盘价,昨日收盘价,当前价,今日最高价,今日最低价,竞买价,竞卖价,成交量,成交额,...
            return {
                "symbol": original_symbol,
                "name": parts[0],
                "open": float(parts[1]) if parts[1] else 0,
                "prev_close": float(parts[2]) if parts[2] else 0,
                "price": float(parts[3]) if parts[3] else 0,
                "high": float(parts[4]) if parts[4] else 0,
                "low": float(parts[5]) if parts[5] else 0,
                "volume": int(float(parts[8]) / 100) if parts[8] else 0,  # 手 -> 股
                "amount": float(parts[9]) / 10000 if parts[9] else 0,  # 万元
            }
        elif 'HK' in original_symbol or original_symbol.startswith('0'):
            # 港股格式类似
            return {
                "symbol": original_symbol,
                "name": parts[0] if len(parts) > 0 else "",
                "price": float(parts[3]) if len(parts) > 3 and parts[3] else 0,
                "change_percent": parts[9] if len(parts) > 9 else "0%",
            }
        
        return {}
    except Exception as e:
        print(f"  解析新浪数据失败: {e}")
        return {}

def calculate_change(quote: Dict[str, Any]) -> Dict[str, Any]:
    """计算涨跌数据"""
    price = quote.get("price", 0)
    prev_close = quote.get("prev_close", 0)
    
    if price and prev_close:
        change = price - prev_close
        change_percent = (change / prev_close) * 100
        quote["change"] = f"{change:+.2f}"
        quote["change_percent"] = f"{change_percent:+.2f}%"
    else:
        quote["change"] = "N/A"
        quote["change_percent"] = "N/A"
    
    return quote

if __name__ == "__main__":
    # 测试
    test_symbols = ["601899", "02899", "000001"]
    for symbol in test_symbols:
        print(f"\n测试 {symbol}:")
        result = get_stock_quote_sina(symbol)
        if result:
            result = calculate_change(result)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print("  获取失败")
