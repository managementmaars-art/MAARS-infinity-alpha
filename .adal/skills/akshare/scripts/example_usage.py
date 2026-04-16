#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AkShare Tool 使用示例
演示如何使用 akshare_tool.py 中的功能
"""

from akshare_tool import AkShareTool
import pandas as pd


def example_stock_realtime():
    """示例1: 获取A股实时行情"""
    print("\n" + "="*80)
    print("示例1: 获取A股实时行情")
    print("="*80)
    
    tool = AkShareTool()
    
    # 获取单只股票实时行情
    df = tool.get_stock_realtime(symbol="000001", use_cache=False)
    print(f"\n平安银行(000001)实时行情:")
    print(df)
    
    # 获取银行业股票
    df_banks = tool.get_stock_realtime(filter_field="行业", filter_value="银行", use_cache=False)
    print(f"\n银行板块股票数量: {len(df_banks)}")
    print(df_banks.head(10))


def example_stock_history():
    """示例2: 获取股票历史数据"""
    print("\n" + "="*80)
    print("示例2: 获取股票历史数据")
    print("="*80)
    
    tool = AkShareTool()
    
    # 获取平安银行日线数据
    df = tool.get_stock_history(
        symbol="000001",
        period="daily",
        start_date="20240101",
        end_date="20241231",
        adjust="qfq",
        use_cache=True
    )
    
    print(f"\n平安银行历史数据 (最近10天):")
    print(df.tail(10))
    
    # 计算技术指标
    df['MA5'] = df['收盘'].rolling(window=5).mean()
    df['MA20'] = df['收盘'].rolling(window=20).mean()
    
    print(f"\n包含移动平均线的数据 (最近5天):")
    print(df[['日期', '收盘', 'MA5', 'MA20']].tail(5))


def example_hk_stock():
    """示例3: 获取港股数据"""
    print("\n" + "="*80)
    print("示例3: 获取港股数据")
    print("="*80)
    
    tool = AkShareTool()
    
    # 获取腾讯控股实时行情
    df = tool.get_hk_stock_realtime(use_cache=False)
    print(f"\n港股实时行情数量: {len(df)}")
    print(df.head(10))
    
    # 获取腾讯控股历史数据
    df_history = tool.get_hk_stock_history(
        symbol="00700",
        period="daily",
        start_date="20240101",
        end_date="20241231",
        use_cache=True
    )
    print(f"\n腾讯控股历史数据 (最近5天):")
    print(df_history.tail(5))


def example_futures():
    """示例4: 获取期货数据"""
    print("\n" + "="*80)
    print("示例4: 获取期货数据")
    print("="*80)
    
    tool = AkShareTool()
    
    # 获取期货实时行情
    df = tool.get_futures_realtime(use_cache=False)
    print(f"\n期货实时行情数量: {len(df)}")
    print(df.head(10))
    
    # 获取沪深300期货历史数据
    df_history = tool.get_futures_history(
        symbol="IF0",
        start_date="20240101",
        end_date="202401231",
        use_cache=True
    )
    if not df_history.empty:
        print(f"\n沪深300期货历史数据 (最近5天):")
        print(df_history.tail(5))


def example_fund():
    """示例5: 获取基金数据"""
    print("\n" + "="*80)
    print("示例5: 获取基金数据")
    print("="*80)
    
    tool = AkShareTool()
    
    # 获取基金列表
    df = tool.get_fund_list(use_cache=True)
    print(f"\n基金总数: {len(df)}")
    print(df.head(10))
    
    # 获取特定基金的历史净值
    df_history = tool.get_fund_history(
        fund_code="000001",
        indicator="单位净值走势",
        use_cache=True
    )
    if not df_history.empty:
        print(f"\n华夏成长基金历史净值 (最近10天):")
        print(df_history.tail(10))


def example_macro():
    """示例6: 获取宏观经济数据"""
    print("\n" + "="*80)
    print("示例6: 获取宏观经济数据")
    print("="*80)
    
    tool = AkShareTool()
    
    # 获取GDP数据
    df_gdp = tool.get_macro_gdp(use_cache=True)
    print(f"\nGDP数据:")
    print(df_gdp)
    
    # 获取CPI数据
    df_cpi = tool.get_macro_cpi(use_cache=True)
    print(f"\nCPI数据 (最近10期):")
    print(df_cpi.tail(10))
    
    # 获取PMI数据
    df_pmi = tool.get_macro_pmi(use_cache=True)
    print(f"\nPMI数据 (最近10期):")
    print(df_pmi.tail(10))


def example_index():
    """示例7: 获取指数数据"""
    print("\n" + "="*80)
    print("示例7: 获取指数数据")
    print("="*80)
    
    tool = AkShareTool()
    
    # 获取指数实时行情
    df = tool.get_index_realtime(index_type="all", use_cache=False)
    print(f"\n指数实时行情:")
    print(df)
    
    # 获取上证指数历史数据
    df_history = tool.get_index_history(
        symbol="000001",
        period="daily",
        start_date="20240101",
        end_date="20241231",
        use_cache=True
    )
    print(f"\n上证指数历史数据 (最近10天):")
    print(df_history.tail(10))


def example_cache():
    """示例8: 缓存管理"""
    print("\n" + "="*80)
    print("示例8: 缓存管理")
    print("="*80)
    
    tool = AkShareTool(use_cache=True, cache_expiry_hours=24)
    
    # 第一次请求（从网络获取）
    print("\n第一次请求（从网络获取）:")
    df1 = tool.get_stock_realtime(symbol="000001", use_cache=True)
    
    # 第二次请求（从缓存获取）
    print("\n第二次请求（从缓存获取）:")
    df2 = tool.get_stock_realtime(symbol="000001", use_cache=True)
    
    # 清除缓存
    print("\n清除缓存:")
    count = tool.clear_cache()
    print(f"已清除 {count} 个缓存文件")
    
    # 再次请求（从网络获取）
    print("\n清除后再次请求:")
    df3 = tool.get_stock_realtime(symbol="000001", use_cache=True)


def example_error_handling():
    """示例9: 错误处理"""
    print("\n" + "="*80)
    print("示例9: 错误处理")
    print("="*80)
    
    tool = AkShareTool()
    
    try:
        # 尝试获取不存在的股票
        df = tool.get_stock_realtime(symbol="999999")
        if df.empty:
            print("股票代码不存在，返回空数据")
    except Exception as e:
        print(f"发生错误: {e}")


def example_data_analysis():
    """示例10: 数据分析"""
    print("\n" + "="*80)
    print("示例10: 数据分析")
    print("="*80)
    
    tool = AkShareTool()
    
    # 获取股票历史数据
    df = tool.get_stock_history(
        symbol="000001",
        period="daily",
        start_date="20240101",
        end_date="20241231",
        adjust="qfq"
    )
    
    if df.empty:
        print("没有数据")
        return
    
    # 计算收益率
    df['涨跌幅'] = df['收盘'].pct_change() * 100
    
    # 计算移动平均线
    df['MA5'] = df['收盘'].rolling(window=5).mean()
    df['MA10'] = df['收盘'].rolling(window=10).mean()
    df['MA20'] = df['收盘'].rolling(window=20).mean()
    
    # 计算波动率
    df['波动率'] = df['涨跌幅'].rolling(window=20).std()
    
    # 统计信息
    print("\n统计信息:")
    print(f"交易天数: {len(df)}")
    print(f"平均涨跌幅: {df['涨跌幅'].mean():.2f}%")
    print(f"最大涨幅: {df['涨跌幅'].max():.2f}%")
    print(f"最大跌幅: {df['涨跌幅'].min():.2f}%")
    print(f"平均波动率: {df['波动率'].mean():.2f}%")
    
    print("\n最近10天数据:")
    print(df[['日期', '收盘', '涨跌幅', 'MA5', 'MA10', 'MA20', '波动率']].tail(10))


def main():
    """运行所有示例"""
    print("\n" + "="*80)
    print("AkShare Tool 使用示例")
    print("="*80)
    
    examples = [
        ("A股实时行情", example_stock_realtime),
        ("股票历史数据", example_stock_history),
        ("港股数据", example_hk_stock),
        ("期货数据", example_futures),
        ("基金数据", example_fund),
        ("宏观经济数据", example_macro),
        ("指数数据", example_index),
        ("缓存管理", example_cache),
        ("错误处理", example_error_handling),
        ("数据分析", example_data_analysis),
    ]
    
    print("\n可用示例:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    
    print("\n运行所有示例可能需要较长时间，请耐心等待...")
    input("\n按Enter键开始运行所有示例，或Ctrl+C取消...")
    
    try:
        for name, func in examples:
            try:
                func()
            except Exception as e:
                print(f"\n示例 '{name}' 运行出错: {e}")
                import traceback
                traceback.print_exc()
        
        print("\n" + "="*80)
        print("所有示例运行完成！")
        print("="*80)
    
    except KeyboardInterrupt:
        print("\n\n用户中断执行")
    except Exception as e:
        print(f"\n发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()