#!/usr/bin/env python3
"""查询股票价格脚本

用法:
    python check.py                    # 查询默认股票列表
    python check.py sh600036           # 查询单只股票
    python check.py sh600036 sz002352  # 查询多只股票

股票代码格式:
    - 上证股票: sh + 6位数字 (如 sh600036)
    - 深证股票: sz + 6位数字 (如 sz002352)
    - 指数基金: 同股票格式 (如 sh000300 沪深300)
"""

import sys
import requests

# 默认股票列表
DEFAULT_STOCKS = [
    "sh000985",   # 中证全指
    "sh000300",   # 沪深300
    "sh000905",   # 中证500
    "sh000852",   # 中证1000
    "sz399006",   # 创业板指
]


def fetch_stock_price(stock_codes):
    """查询股票价格"""
    url = f"http://qt.gtimg.cn/q={','.join(stock_codes)}"
    
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
    except requests.RequestException as e:
        print(f"请求失败: {e}")
        return []
    
    text = r.content.decode("gbk")
    lines = text.strip().split(";")
    
    results = []
    for line in lines:
        if not line.strip():
            continue
        
        try:
            # 提取引号内的数据
            data = line.split('"')[1].split("~")
            name = data[1]
            price = data[3]
            code = data[2]
            results.append((code, name, price))
        except (IndexError, ValueError):
            continue
    
    return results


def main():
    # 获取命令行参数，如果没有则使用默认股票列表
    if len(sys.argv) > 1:
        stocks = sys.argv[1:]
    else:
        stocks = DEFAULT_STOCKS
    
    # 查询并输出结果
    results = fetch_stock_price(stocks)
    
    if not results:
        print("未获取到股票数据")
        return
    
    for code, name, price in results:
        print(f"{code} {name} {price}")


if __name__ == "__main__":
    main()
