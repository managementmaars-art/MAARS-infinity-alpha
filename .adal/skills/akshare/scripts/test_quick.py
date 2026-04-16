#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AkShare Tool 快速测试
只测试基本功能，不进行网络请求
"""

import sys


def test_imports():
    """测试导入"""
    print("测试1: 导入模块...")
    try:
        import akshare as ak
        import pandas as pd
        from akshare_tool import AkShareTool, CacheManager, retry_on_failure
        print("✓ 所有模块导入成功")
        print(f"  - AkShare version: {ak.__version__}")
        print(f"  - Pandas version: {pd.__version__}")
        return True
    except ImportError as e:
        print(f"✗ 导入失败: {e}")
        return False


def test_cache_manager():
    """测试缓存管理器"""
    print("\n测试2: 缓存管理器...")
    try:
        from akshare_tool import CacheManager
        import tempfile
        import os

        # 使用临时目录
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = CacheManager(cache_dir=tmpdir, cache_expiry_hours=24)

            # 测试缓存键生成
            key1 = cache._get_cache_key("test_func", param1="value1", param2="value2")
            key2 = cache._get_cache_key("test_func", param1="value1", param2="value2")
            key3 = cache._get_cache_key("test_func", param1="value1", param2="value3")

            if key1 == key2:
                print("✓ 相同参数生成相同的缓存键")
            else:
                print("✗ 缓存键生成错误")
                return False

            if key1 != key3:
                print("✓ 不同参数生成不同的缓存键")
            else:
                print("✗ 缓存键生成错误")
                return False

            # 测试缓存读写
            import pandas as pd
            test_data = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})

            cache.set("test_func", test_data, param1="value1")
            cached_data = cache.get("test_func", param1="value1")

            if cached_data is not None and not cached_data.empty:
                print("✓ 缓存写入和读取成功")
            else:
                print("✗ 缓存读写失败")
                return False

            # 测试缓存清除
            count = cache.clear()
            print(f"✓ 清除缓存成功，删除了 {count} 个文件")

        return True
    except Exception as e:
        print(f"✗ 缓存管理器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_tool_initialization():
    """测试工具初始化"""
    print("\n测试3: 工具初始化...")
    try:
        from akshare_tool import AkShareTool

        # 测试带缓存初始化
        tool1 = AkShareTool(use_cache=True, cache_expiry_hours=24)
        print("✓ 带缓存初始化成功")

        # 测试不带缓存初始化
        tool2 = AkShareTool(use_cache=False)
        print("✓ 不带缓存初始化成功")

        # 测试清除缓存
        count = tool1.clear_cache()
        print(f"✓ 清除缓存成功")

        return True
    except Exception as e:
        print(f"✗ 工具初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_retry_decorator():
    """测试重试装饰器"""
    print("\n测试4: 重试装饰器...")
    try:
        from akshare_tool import retry_on_failure

        # 测试成功情况
        @retry_on_failure(max_retries=3, delay=0.1)
        def success_func():
            return "success"

        result = success_func()
        if result == "success":
            print("✓ 成功函数执行正常")
        else:
            print("✗ 成功函数返回错误")
            return False

        # 测试失败情况
        @retry_on_failure(max_retries=2, delay=0.1)
        def fail_func():
            raise ValueError("Test error")

        try:
            fail_func()
            print("✗ 失败函数应该抛出异常")
            return False
        except ValueError as e:
            if str(e) == "Test error":
                print("✓ 失败函数正确抛出异常")
            else:
                print("✗ 失败函数抛出错误的异常")
                return False

        return True
    except Exception as e:
        print(f"✗ 重试装饰器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_command_line_help():
    """测试命令行帮助"""
    print("\n测试5: 命令行帮助...")
    try:
        import subprocess
        import os

        script_path = os.path.join(os.path.dirname(__file__), "akshare_tool.py")

        # 测试主帮助
        result = subprocess.run(
            ["python3", script_path, "--help"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0 and "AkShare 金融市场数据获取工具" in result.stdout:
            print("✓ 主帮助信息显示正常")
        else:
            print("✗ 主帮助信息显示失败")
            return False

        # 测试子命令帮助
        result = subprocess.run(
            ["python3", script_path, "stock-realtime", "--help"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0 and ("股票代码" in result.stdout or "symbol" in result.stdout):
            print("✓ 子命令帮助信息显示正常")
        else:
            print("✗ 子命令帮助信息显示失败")
            print(f"  退出码: {result.returncode}")
            print(f"  输出: {result.stdout[:200]}")
            return False

        return True
    except Exception as e:
        print(f"✗ 命令行帮助测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_structure():
    """测试API结构"""
    print("\n测试6: API结构...")
    try:
        from akshare_tool import AkShareTool

        tool = AkShareTool(use_cache=False)

        # 检查所有必需的方法是否存在
        required_methods = [
            'get_stock_realtime',
            'get_stock_history',
            'get_hk_stock_realtime',
            'get_hk_stock_history',
            'get_us_stock_realtime',
            'get_futures_realtime',
            'get_futures_history',
            'get_fund_list',
            'get_fund_history',
            'get_macro_gdp',
            'get_macro_cpi',
            'get_macro_pmi',
            'get_index_realtime',
            'get_index_history',
            'clear_cache',
        ]

        all_exist = True
        for method_name in required_methods:
            if hasattr(tool, method_name):
                print(f"  ✓ {method_name}")
            else:
                print(f"  ✗ {method_name} - 不存在")
                all_exist = False

        if all_exist:
            print("✓ 所有API方法都存在")
        else:
            print("✗ 部分API方法不存在")
            return False

        return True
    except Exception as e:
        print(f"✗ API结构测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """运行所有测试"""
    print("="*80)
    print("AkShare Tool 快速功能测试")
    print("="*80)
    print("注意: 此测试不进行实际网络请求，仅验证代码结构和基本功能\n")

    tests = [
        test_imports,
        test_cache_manager,
        test_tool_initialization,
        test_retry_decorator,
        test_command_line_help,
        test_api_structure,
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
        print("\n提示: 如需测试实际数据获取功能，请运行:")
        print("  python3 test_basic.py")
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