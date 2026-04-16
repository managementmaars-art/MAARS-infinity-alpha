#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AkShare Financial Data Tool
获取中国金融市场数据的命令行工具

功能：
- A股实时行情（支持筛选）
- 股票历史数据（日线/周线/月线）
- 港股/美股数据
- 期货数据
- 基金数据
- 宏观经济数据（GDP/CPI/PMI）
- 指数数据
"""

import argparse
import sys
import json
import time
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List
import hashlib

try:
    import akshare as ak
    import pandas as pd
except ImportError as e:
    print(f"错误: 缺少必要的依赖库")
    print(f"请运行: pip install akshare pandas")
    sys.exit(1)


class CacheManager:
    """数据缓存管理器"""
    
    def __init__(self, cache_dir: str = None, cache_expiry_hours: int = 24):
        """
        初始化缓存管理器
        
        Args:
            cache_dir: 缓存目录路径
            cache_expiry_hours: 缓存过期时间（小时）
        """
        if cache_dir is None:
            cache_dir = os.path.join(os.path.expanduser("~"), ".akshare_cache")
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_expiry_hours = cache_expiry_hours
    
    def _get_cache_key(self, func_name: str, **kwargs) -> str:
        """生成缓存键"""
        # 将参数转换为字符串并排序
        params_str = json.dumps(kwargs, sort_keys=True, ensure_ascii=False)
        # 使用MD5生成唯一键
        key_str = f"{func_name}:{params_str}"
        return hashlib.md5(key_str.encode('utf-8')).hexdigest()
    
    def get(self, func_name: str, **kwargs) -> Optional[pd.DataFrame]:
        """
        从缓存获取数据
        
        Args:
            func_name: 函数名
            **kwargs: 函数参数
            
        Returns:
            缓存的DataFrame，如果不存在或已过期则返回None
        """
        cache_key = self._get_cache_key(func_name, **kwargs)
        cache_file = self.cache_dir / f"{cache_key}.parquet"
        
        if not cache_file.exists():
            return None
        
        # 检查缓存是否过期
        file_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
        expiry_time = datetime.now() - timedelta(hours=self.cache_expiry_hours)
        
        if file_time < expiry_time:
            cache_file.unlink()  # 删除过期缓存
            return None
        
        try:
            df = pd.read_parquet(cache_file)
            return df
        except Exception:
            return None
    
    def set(self, func_name: str, data: pd.DataFrame, **kwargs) -> bool:
        """
        保存数据到缓存
        
        Args:
            func_name: 函数名
            data: 要缓存的数据
            **kwargs: 函数参数
            
        Returns:
            是否成功保存
        """
        cache_key = self._get_cache_key(func_name, **kwargs)
        cache_file = self.cache_dir / f"{cache_key}.parquet"
        
        try:
            data.to_parquet(cache_file)
            return True
        except Exception as e:
            print(f"缓存保存失败: {e}")
            return False
    
    def clear(self) -> int:
        """
        清除所有缓存
        
        Returns:
            删除的缓存文件数量
        """
        count = 0
        for file in self.cache_dir.glob("*.parquet"):
            file.unlink()
            count += 1
        return count


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """
    失败重试装饰器
    
    Args:
        max_retries: 最大重试次数
        delay: 重试延迟（秒）
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_error = None
            current_delay = delay  # 使用局部变量
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        print(f"请求失败，{current_delay}秒后重试... (尝试 {attempt + 1}/{max_retries})")
                        time.sleep(current_delay)
                        current_delay *= 2  # 指数退避
            raise last_error
        return wrapper
    return decorator


class AkShareTool:
    """AkShare 数据获取工具"""
    
    def __init__(self, use_cache: bool = True, cache_expiry_hours: int = 24):
        """
        初始化工具
        
        Args:
            use_cache: 是否使用缓存
            cache_expiry_hours: 缓存过期时间（小时）
        """
        self.use_cache = use_cache
        self.cache = CacheManager(cache_expiry_hours=cache_expiry_hours) if use_cache else None
    
    def _fetch_with_cache(self, func_name: str, fetch_func, use_cache: bool = None, **kwargs) -> pd.DataFrame:
        """
        带缓存的数据获取
        
        Args:
            func_name: 函数名（用于缓存键）
            fetch_func: 实际获取数据的函数（无参数）
            use_cache: 是否使用缓存（覆盖默认设置）
            **kwargs: 函数参数（仅用于缓存键）
            
        Returns:
            DataFrame数据
        """
        should_cache = use_cache if use_cache is not None else self.use_cache
        
        # 尝试从缓存获取
        if should_cache and self.cache:
            cached_data = self.cache.get(func_name, **kwargs)
            if cached_data is not None:
                print("✓ 使用缓存数据")
                return cached_data
        
        # 从网络获取
        print("正在获取数据...")
        data = fetch_func()
        
        # 保存到缓存
        if should_cache and self.cache and data is not None and not data.empty:
            self.cache.set(func_name, data, **kwargs)
            print("✓ 数据已缓存")
        
        return data
    
    @retry_on_failure(max_retries=3, delay=1.0)
    def get_stock_realtime(self, symbol: str = None, filter_field: str = None, 
                          filter_value: str = None, use_cache: bool = False) -> pd.DataFrame:
        """
        获取A股实时行情
        
        Args:
            symbol: 股票代码（可选，为空则获取全部）
            filter_field: 筛选字段（如 '行业', '市场' 等）
            filter_value: 筛选值
            use_cache: 是否使用缓存
            
        Returns:
            实时行情数据
        """
        def fetch():
            if symbol:
                # 单个股票
                df = ak.stock_zh_a_spot()
                return df[df['代码'] == symbol] if '代码' in df.columns else df
            else:
                # 全部A股
                df = ak.stock_zh_a_spot_em()
                # 筛选
                if filter_field and filter_value and filter_field in df.columns:
                    df = df[df[filter_field].astype(str).str.contains(filter_value, na=False)]
                return df
        
        return self._fetch_with_cache("stock_realtime", fetch, use_cache=use_cache, 
                                     symbol=symbol, filter_field=filter_field, filter_value=filter_value)
    
    @retry_on_failure(max_retries=3, delay=1.0)
    def get_stock_history(self, symbol: str, period: str = "daily", 
                         start_date: str = None, end_date: str = None,
                         adjust: str = "qfq", use_cache: bool = True) -> pd.DataFrame:
        """
        获取股票历史数据
        
        Args:
            symbol: 股票代码（如 "000001"）
            period: 周期（daily/weekly/monthly）
            start_date: 开始日期（格式：YYYYMMDD）
            end_date: 结束日期（格式：YYYYMMDD）
            adjust: 复权类型（qfq-前复权, hfq-后复权, ""-不复权）
            use_cache: 是否使用缓存
            
        Returns:
            历史数据
        """
        # 默认日期范围
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime("%Y%m%d")
        
        def fetch():
            df = ak.stock_zh_a_hist(
                symbol=symbol,
                period=period,
                start_date=start_date,
                end_date=end_date,
                adjust=adjust
            )
            return df
        
        return self._fetch_with_cache("stock_history", fetch, use_cache=use_cache,
                                     symbol=symbol, period=period, start_date=start_date,
                                     end_date=end_date, adjust=adjust)
    
    @retry_on_failure(max_retries=3, delay=1.0)
    def get_hk_stock_realtime(self, use_cache: bool = False) -> pd.DataFrame:
        """获取港股实时行情"""
        def fetch():
            return ak.stock_hk_spot_em()
        
        return self._fetch_with_cache("hk_stock_realtime", fetch, use_cache=use_cache)
    
    @retry_on_failure(max_retries=3, delay=1.0)
    def get_hk_stock_history(self, symbol: str, period: str = "daily",
                            start_date: str = None, end_date: str = None,
                            adjust: str = "qfq", use_cache: bool = True) -> pd.DataFrame:
        """获取港股历史数据"""
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime("%Y%m%d")
        
        def fetch():
            df = ak.stock_hk_hist(
                symbol=symbol,
                period=period,
                start_date=start_date,
                end_date=end_date,
                adjust=adjust
            )
            return df
        
        return self._fetch_with_cache("hk_stock_history", fetch, use_cache=use_cache,
                                     symbol=symbol, period=period, start_date=start_date,
                                     end_date=end_date, adjust=adjust)
    
    @retry_on_failure(max_retries=3, delay=1.0)
    def get_us_stock_realtime(self, use_cache: bool = False) -> pd.DataFrame:
        """获取美股实时行情"""
        def fetch():
            return ak.stock_us_spot_em()
        
        return self._fetch_with_cache("us_stock_realtime", fetch, use_cache=use_cache)
    
    @retry_on_failure(max_retries=3, delay=1.0)
    def get_futures_realtime(self, symbol: str = None, use_cache: bool = False) -> pd.DataFrame:
        """
        获取期货实时行情
        
        Args:
            symbol: 期货代码（可选）
            use_cache: 是否使用缓存
        """
        def fetch():
            df = ak.futures_zh_spot()
            if symbol and '代码' in df.columns:
                df = df[df['代码'].str.contains(symbol, na=False)]
            return df
        
        return self._fetch_with_cache("futures_realtime", fetch, use_cache=use_cache, symbol=symbol)
    
    @retry_on_failure(max_retries=3, delay=1.0)
    def get_futures_history(self, symbol: str, start_date: str = None,
                           end_date: str = None, use_cache: bool = True) -> pd.DataFrame:
        """获取期货历史数据"""
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=90)).strftime("%Y%m%d")
        
        def fetch():
            df = ak.futures_zh_hist_sina(symbol=symbol)
            # 日期筛选
            if 'date' in df.columns:
                df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
            return df
        
        return self._fetch_with_cache("futures_history", fetch, use_cache=use_cache,
                                     symbol=symbol, start_date=start_date, end_date=end_date)
    
    @retry_on_failure(max_retries=3, delay=1.0)
    def get_fund_list(self, fund_type: str = None, use_cache: bool = True) -> pd.DataFrame:
        """
        获取基金列表
        
        Args:
            fund_type: 基金类型（可选）
            use_cache: 是否使用缓存
        """
        def fetch():
            df = ak.fund_open_fund_info_em()
            if fund_type and '基金类型' in df.columns:
                df = df[df['基金类型'].str.contains(fund_type, na=False)]
            return df
        
        return self._fetch_with_cache("fund_list", fetch, use_cache=use_cache, fund_type=fund_type)
    
    @retry_on_failure(max_retries=3, delay=1.0)
    def get_fund_history(self, fund_code: str, indicator: str = "单位净值走势",
                        use_cache: bool = True) -> pd.DataFrame:
        """
        获取基金历史数据
        
        Args:
            fund_code: 基金代码
            indicator: 指标类型（单位净值走势/累计净值走势等）
            use_cache: 是否使用缓存
        """
        def fetch():
            df = ak.fund_open_fund_info_em(fund=fund_code, indicator=indicator)
            return df
        
        return self._fetch_with_cache("fund_history", fetch, use_cache=use_cache,
                                     fund_code=fund_code, indicator=indicator)
    
    @retry_on_failure(max_retries=3, delay=1.0)
    def get_macro_gdp(self, use_cache: bool = True) -> pd.DataFrame:
        """获取GDP数据"""
        def fetch():
            return ak.macro_china_gdp()
        
        return self._fetch_with_cache("macro_gdp", fetch, use_cache=use_cache)
    
    @retry_on_failure(max_retries=3, delay=1.0)
    def get_macro_cpi(self, use_cache: bool = True) -> pd.DataFrame:
        """获取CPI数据"""
        def fetch():
            return ak.macro_china_cpi()
        
        return self._fetch_with_cache("macro_cpi", fetch, use_cache=use_cache)
    
    @retry_on_failure(max_retries=3, delay=1.0)
    def get_macro_pmi(self, use_cache: bool = True) -> pd.DataFrame:
        """获取PMI数据"""
        def fetch():
            return ak.macro_china_pmi()
        
        return self._fetch_with_cache("macro_pmi", fetch, use_cache=use_cache)
    
    @retry_on_failure(max_retries=3, delay=1.0)
    def get_index_realtime(self, index_type: str = "all", use_cache: bool = False) -> pd.DataFrame:
        """
        获取指数实时行情
        
        Args:
            index_type: 指数类型（all/sz/sh）
            use_cache: 是否使用缓存
        """
        def fetch():
            if index_type == "sz":
                df = ak.index_stock_info_sz_name_code()
            elif index_type == "sh":
                df = ak.index_stock_info_sh_name_code()
            else:
                # 获取主要指数实时行情
                df = ak.index_zh_a_spot()
            return df
        
        return self._fetch_with_cache("index_realtime", fetch, use_cache=use_cache, index_type=index_type)
    
    @retry_on_failure(max_retries=3, delay=1.0)
    def get_index_history(self, symbol: str, period: str = "daily",
                         start_date: str = None, end_date: str = None,
                         use_cache: bool = True) -> pd.DataFrame:
        """获取指数历史数据"""
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime("%Y%m%d")
        
        def fetch():
            df = ak.index_zh_a_hist(
                symbol=symbol,
                period=period,
                start_date=start_date,
                end_date=end_date
            )
            return df
        
        return self._fetch_with_cache("index_history", fetch, use_cache=use_cache,
                                     symbol=symbol, period=period, start_date=start_date,
                                     end_date=end_date)
    
    def clear_cache(self) -> int:
        """清除缓存"""
        if self.cache:
            return self.cache.clear()
        return 0


def print_dataframe(df: pd.DataFrame, max_rows: int = 20, title: str = "数据结果"):
    """美化打印DataFrame"""
    if df is None or df.empty:
        print("没有数据")
        return
    
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"  共 {len(df)} 条记录")
    print(f"{'='*80}\n")
    
    # 设置显示选项
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', 20)
    
    # 分页显示
    if len(df) > max_rows:
        print(df.head(max_rows))
        print(f"\n... (还有 {len(df) - max_rows} 条记录)")
    else:
        print(df)
    
    print("\n" + "="*80)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="AkShare 金融市场数据获取工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 获取所有A股实时行情
  %(prog)s stock-realtime
  
  # 获取单只股票实时行情
  %(prog)s stock-realtime --symbol 000001
  
  # 筛选特定行业的股票
  %(prog)s stock-realtime --filter-field 行业 --filter-value 银行
  
  # 获取股票历史数据
  %(prog)s stock-history --symbol 000001 --period daily --adjust qfq
  
  # 获取港股实时行情
  %(prog)s hk-realtime
  
  # 获取基金列表
  %(prog)s fund-list
  
  # 获取宏观GDP数据
  %(prog)s macro-gdp
  
  # 清除缓存
  %(prog)s clear-cache
        """
    )
    
    # 全局参数
    parser.add_argument("--no-cache", action="store_true", help="不使用缓存")
    parser.add_argument("--cache-expiry", type=int, default=24, 
                       help="缓存过期时间（小时）")
    parser.add_argument("--output", "-o", type=str, help="输出文件路径（CSV/JSON格式）")
    parser.add_argument("--format", type=str, choices=["table", "json", "csv"], 
                       default="table", help="输出格式")
    
    # 子命令
    subparsers = parser.add_subparsers(dest="command", help="数据类型")
    
    # A股实时行情
    stock_realtime_parser = subparsers.add_parser("stock-realtime", help="A股实时行情")
    stock_realtime_parser.add_argument("--symbol", "-s", type=str, help="股票代码")
    stock_realtime_parser.add_argument("--filter-field", type=str, help="筛选字段")
    stock_realtime_parser.add_argument("--filter-value", type=str, help="筛选值")
    
    # 股票历史数据
    stock_history_parser = subparsers.add_parser("stock-history", help="股票历史数据")
    stock_history_parser.add_argument("--symbol", "-s", type=str, required=True, help="股票代码")
    stock_history_parser.add_argument("--period", "-p", type=str, default="daily",
                                     choices=["daily", "weekly", "monthly"], help="周期")
    stock_history_parser.add_argument("--start-date", type=str, help="开始日期（YYYYMMDD）")
    stock_history_parser.add_argument("--end-date", type=str, help="结束日期（YYYYMMDD）")
    stock_history_parser.add_argument("--adjust", type=str, default="qfq",
                                     choices=["qfq", "hfq", ""], help="复权类型")
    
    # 港股实时行情
    subparsers.add_parser("hk-realtime", help="港股实时行情")
    
    # 港股历史数据
    hk_history_parser = subparsers.add_parser("hk-history", help="港股历史数据")
    hk_history_parser.add_argument("--symbol", "-s", type=str, required=True, help="股票代码")
    hk_history_parser.add_argument("--period", "-p", type=str, default="daily",
                                   choices=["daily", "weekly", "monthly"], help="周期")
    hk_history_parser.add_argument("--start-date", type=str, help="开始日期（YYYYMMDD）")
    hk_history_parser.add_argument("--end-date", type=str, help="结束日期（YYYYMMDD）")
    hk_history_parser.add_argument("--adjust", type=str, default="qfq",
                                   choices=["qfq", "hfq", ""], help="复权类型")
    
    # 美股实时行情
    subparsers.add_parser("us-realtime", help="美股实时行情")
    
    # 期货实时行情
    futures_realtime_parser = subparsers.add_parser("futures-realtime", help="期货实时行情")
    futures_realtime_parser.add_argument("--symbol", "-s", type=str, help="期货代码")
    
    # 期货历史数据
    futures_history_parser = subparsers.add_parser("futures-history", help="期货历史数据")
    futures_history_parser.add_argument("--symbol", "-s", type=str, required=True, help="期货代码")
    futures_history_parser.add_argument("--start-date", type=str, help="开始日期（YYYYMMDD）")
    futures_history_parser.add_argument("--end-date", type=str, help="结束日期（YYYYMMDD）")
    
    # 基金列表
    fund_list_parser = subparsers.add_parser("fund-list", help="基金列表")
    fund_list_parser.add_argument("--type", type=str, help="基金类型")
    
    # 基金历史数据
    fund_history_parser = subparsers.add_parser("fund-history", help="基金历史数据")
    fund_history_parser.add_argument("--code", "-c", type=str, required=True, help="基金代码")
    fund_history_parser.add_argument("--indicator", type=str, default="单位净值走势", help="指标类型")
    
    # 宏观经济数据
    subparsers.add_parser("macro-gdp", help="GDP数据")
    subparsers.add_parser("macro-cpi", help="CPI数据")
    subparsers.add_parser("macro-pmi", help="PMI数据")
    
    # 指数实时行情
    index_realtime_parser = subparsers.add_parser("index-realtime", help="指数实时行情")
    index_realtime_parser.add_argument("--type", type=str, default="all",
                                      choices=["all", "sz", "sh"], help="指数类型")
    
    # 指数历史数据
    index_history_parser = subparsers.add_parser("index-history", help="指数历史数据")
    index_history_parser.add_argument("--symbol", "-s", type=str, required=True, help="指数代码")
    index_history_parser.add_argument("--period", "-p", type=str, default="daily",
                                     choices=["daily", "weekly", "monthly"], help="周期")
    index_history_parser.add_argument("--start-date", type=str, help="开始日期（YYYYMMDD）")
    index_history_parser.add_argument("--end-date", type=str, help="结束日期（YYYYMMDD）")
    
    # 清除缓存
    subparsers.add_parser("clear-cache", help="清除缓存")
    
    args = parser.parse_args()
    
    # 如果没有命令，显示帮助
    if not args.command:
        parser.print_help()
        return
    
    # 初始化工具
    tool = AkShareTool(use_cache=not args.no_cache, cache_expiry_hours=args.cache_expiry)
    
    # 执行命令
    df = None
    title = "数据结果"
    
    try:
        if args.command == "stock-realtime":
            df = tool.get_stock_realtime(
                symbol=args.symbol,
                filter_field=args.filter_field,
                filter_value=args.filter_value,
                use_cache=not args.no_cache
            )
            title = f"A股实时行情 - {args.symbol if args.symbol else '全部'}"
        
        elif args.command == "stock-history":
            df = tool.get_stock_history(
                symbol=args.symbol,
                period=args.period,
                start_date=args.start_date,
                end_date=args.end_date,
                adjust=args.adjust,
                use_cache=not args.no_cache
            )
            title = f"股票历史数据 - {args.symbol} ({args.period})"
        
        elif args.command == "hk-realtime":
            df = tool.get_hk_stock_realtime(use_cache=not args.no_cache)
            title = "港股实时行情"
        
        elif args.command == "hk-history":
            df = tool.get_hk_stock_history(
                symbol=args.symbol,
                period=args.period,
                start_date=args.start_date,
                end_date=args.end_date,
                adjust=args.adjust,
                use_cache=not args.no_cache
            )
            title = f"港股历史数据 - {args.symbol} ({args.period})"
        
        elif args.command == "us-realtime":
            df = tool.get_us_stock_realtime(use_cache=not args.no_cache)
            title = "美股实时行情"
        
        elif args.command == "futures-realtime":
            df = tool.get_futures_realtime(
                symbol=args.symbol,
                use_cache=not args.no_cache
            )
            title = f"期货实时行情 - {args.symbol if args.symbol else '全部'}"
        
        elif args.command == "futures-history":
            df = tool.get_futures_history(
                symbol=args.symbol,
                start_date=args.start_date,
                end_date=args.end_date,
                use_cache=not args.no_cache
            )
            title = f"期货历史数据 - {args.symbol}"
        
        elif args.command == "fund-list":
            df = tool.get_fund_list(
                fund_type=args.type,
                use_cache=not args.no_cache
            )
            title = f"基金列表 - {args.type if args.type else '全部'}"
        
        elif args.command == "fund-history":
            df = tool.get_fund_history(
                fund_code=args.code,
                indicator=args.indicator,
                use_cache=not args.no_cache
            )
            title = f"基金历史数据 - {args.code}"
        
        elif args.command == "macro-gdp":
            df = tool.get_macro_gdp(use_cache=not args.no_cache)
            title = "GDP数据"
        
        elif args.command == "macro-cpi":
            df = tool.get_macro_cpi(use_cache=not args.no_cache)
            title = "CPI数据"
        
        elif args.command == "macro-pmi":
            df = tool.get_macro_pmi(use_cache=not args.no_cache)
            title = "PMI数据"
        
        elif args.command == "index-realtime":
            df = tool.get_index_realtime(
                index_type=args.type,
                use_cache=not args.no_cache
            )
            title = f"指数实时行情 - {args.type}"
        
        elif args.command == "index-history":
            df = tool.get_index_history(
                symbol=args.symbol,
                period=args.period,
                start_date=args.start_date,
                end_date=args.end_date,
                use_cache=not args.no_cache
            )
            title = f"指数历史数据 - {args.symbol} ({args.period})"
        
        elif args.command == "clear-cache":
            count = tool.clear_cache()
            print(f"✓ 已清除 {count} 个缓存文件")
            return
        
        # 输出结果
        if df is not None:
            if args.output:
                # 保存到文件
                if args.output.endswith('.json'):
                    df.to_json(args.output, orient='records', force_ascii=False, indent=2)
                else:
                    df.to_csv(args.output, index=False, encoding='utf-8-sig')
                print(f"✓ 数据已保存到: {args.output}")
            elif args.format == "json":
                print(df.to_json(orient='records', force_ascii=False, indent=2))
            elif args.format == "csv":
                print(df.to_csv(index=False))
            else:
                print_dataframe(df, title=title)
    
    except KeyboardInterrupt:
        print("\n\n操作已取消")
        sys.exit(0)
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()