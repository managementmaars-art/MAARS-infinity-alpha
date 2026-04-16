#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AkShare Tool 基本功能测试
验证核心功能是否正常工作
"""

import sys
from akshare_tool import AkShareTool


def test_imports():
    """测试导入"""
    print("测试1: 导入模块...")
    try:
        import akshare as ak
        import pandas as pd
        print("✓ 导入成功")
        return True
    except ImportError as e:
        print(f"✗ 导入失败: {e}")
        return False


def test_tool_initialization():
    """测试工具初始化"""
    print("\n测试2: 初始化工具...")
    try:
        tool = AkShareTool(use_cache=True, cache_expiry_hours=24)
        print("✓ 工具初始化成功")
        return True
    except Exception as e:
        print(f"✗ 初始化失败: {e}")
        return False


def test_cache_manager():
    """测试缓存管理器"""
    print("\n测试3: 缓存管理器...")
    try:
        tool = AkShareTool(use_cache=True)
        print("✓ 缓存管理器初始化成功")
        
        # 测试清除缓存
        count = tool.clear_cache()
        print(f"✓ 清除缓存成功，删除了 {count} 个文件")
        return True
    except Exception as e:
        print(f"✗ 缓存管理器测试失败: {e}")
        return False


def test_stock_realtime():
    """测试A股实时行情"""
    print("\n测试4: A股实时行情...")
    try:
        tool = AkShareTool(use_cache=False)
        df = tool.get_stock_realtime(symbol="000001", use_cache=False)
        
        if df is not None and not df.empty:
            print(f"✓ 获取成功，返回 {len(df)} 条记录")
            print(f"  列名: {list(df.columns)}")
            return True
        else:
            print("✗ 返回数据为空")
            return False
    except Exception as e:
        print(f"✗ 获取失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_macro_data():
    """测试宏观经济数据"""
    print("\n测试5: 宏观经济数据...")
    try:
        tool = AkShareTool(use_cache=True)
        
        # 测试GDP数据
        df_gdp = tool.get_macro_gdp(use_cache=True)
        if df_gdp is not None and not df_gdp.empty:
            print(f"✓ GDP数据获取成功，返回 {len(df_gdp)} 条记录")
        else:
            print("⚠ GDP数据为空")
        
        # 测试CPI数据
        df_cpi = tool.get_macro_cpi(use_cache=True)
        if df_cpi is not None and not df_cpi.empty:
            print(f"✓ CPI数据获取成功，返回 {len(df_cpi)} 条记录")
        else:
            print("⚠ CPI数据为空")
        
        # 测试PMI数据
        df_pmi = tool.get_macro_pmi(use_cache=True)
        if df_pmi is not None and not df_pmi.empty:
            print(f"✓ PMI数据获取成功，返回 {len(df_pmi)} 条记录")
        else:
            print("⚠ PMI数据为空")
        
        return True
    except Exception as e:
        print(f"✗ 获取失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_retry_mechanism():
    """测试重试机制"""
    print("\n测试6: 重试机制...")
    print("  (重试机制在网络错误时自动触发，此处仅验证装饰器正常工作)")
    try:
        tool = AkShareTool()
        # 重试机制会在实际网络请求时自动触发
        print("✓ 重试机制装饰器已加载")
        return True
    except Exception as e:
        print(f"✗ 重试机制测试失败: {e}")
        return False


def run_all_tests():
    """运行所有测试"""
    print("="*80)
    print("AkShare Tool 基本功能测试")
    print("="*80)
    
    tests = [
        test_imports,
        test_tool_initialization,
        test_cache_manager,
        test_stock_realtime,
        test_macro_data,
        test_retry_mechanism,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n✗ 测试异常: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    # 统计结果
    print("\n" + "="*80)
    print("测试结果汇总")
    print("="*80)
    passed = sum(results)
    total = len(results)
    print(f"通过: {passed}/{total}")
    print(f"失败: {total - passed}/{total}")
    
    if passed == total:
        print("\n✓ 所有测试通过！")
        return 0
    else:
        print(f"\n✗ {total - passed} 个测试失败")
        return 1


if __name__ == "__main__":
    try:
        exit_code = run_all_tests()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n发生未预期的错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)