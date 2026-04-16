#!/usr/bin/env python3
"""
测试 Super PPT 编辑功能

使用项目中的实际 PPT 文件进行测试
"""

import sys
import os

# 添加脚本路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ppt_editor import open_ppt, create_ppt, list_themes
from animation_engine import AnimationEngine, list_animations

def test_open_existing_ppt():
    """测试打开现有 PPT"""
    print("\n" + "=" * 60)
    print("测试 1: 打开现有 PPT")
    print("=" * 60)
    
    # 使用项目中的实际 PPT 文件
    ppt_path = "/Users/huyansheng/Documents/write/2026/晋升文档/PPT/胡衍生2026.pptx"
    
    if not os.path.exists(ppt_path):
        print(f"⚠️ 测试文件不存在: {ppt_path}")
        return None
    
    editor = open_ppt(ppt_path, theme="promotion")
    editor.print_slides()
    
    return editor

def test_create_new_ppt():
    """测试创建新 PPT"""
    print("\n" + "=" * 60)
    print("测试 2: 创建新 PPT")
    print("=" * 60)
    
    editor = create_ppt(theme="promotion")
    
    # 添加第一页 - 封面
    n = editor.add_slide()
    editor.set_background(n)
    editor.add_header_bar(n, "Super PPT 测试")
    editor.add_title(n, "Python PPT 编辑器", "支持风格预设和动画", x=0.5, y=2)
    
    # 添加第二页 - 特性展示
    n = editor.add_slide()
    editor.set_background(n)
    editor.add_header_bar(n, "核心功能")
    
    features = [
        {"icon": "📂", "text": "打开现有 PPT"},
        {"icon": "✏️", "text": "修改指定页面"},
        {"icon": "🎨", "text": "风格预设系统"},
        {"icon": "🎬", "text": "动画支持"},
        {"icon": "💾", "text": "保存输出"},
        {"icon": "🔄", "text": "批量处理"},
    ]
    editor.add_feature_grid(n, features, columns=3)
    
    # 添加第三页 - 问题/解决方案
    n = editor.add_slide()
    editor.set_background(n)
    editor.add_header_bar(n, "问题与解决方案")
    
    editor.add_card(n, x=0.5, y=1.2, width=4.5, height=1.5,
                    title="🚫 传统方式", 
                    content="手动调整每一页的样式，耗时且容易不一致",
                    card_type="problem")
    
    editor.add_card(n, x=5.3, y=1.2, width=4.5, height=1.5,
                    title="✅ Super PPT",
                    content="预设风格自动应用，保持全局一致性",
                    card_type="solution")
    
    # 保存
    output_path = "/tmp/super-ppt-test.pptx"
    editor.save(output_path)
    
    return editor, output_path

def test_animation():
    """测试动画功能"""
    print("\n" + "=" * 60)
    print("测试 3: 动画功能")
    print("=" * 60)
    
    # 创建测试 PPT
    editor = create_ppt(theme="promotion")
    n = editor.add_slide()
    editor.set_background(n)
    editor.add_title(n, "动画测试")
    editor.add_text(n, "这段文字将添加淡入动画")
    
    # 添加动画
    engine = AnimationEngine(editor)
    
    # 测试自然语言解析
    print("\n🎬 测试自然语言动画描述:")
    
    descriptions = [
        "标题淡入",
        "内容从左侧飞入",
        "卡片依次弹出",
        "页面使用推进效果切换",
    ]
    
    for desc in descriptions:
        print(f"\n   描述: '{desc}'")
        engine.add_from_description(desc, slide_number=1)
    
    # 添加页面切换
    engine.add_slide_transition(1, "fade")
    
    output_path = "/tmp/super-ppt-animation-test.pptx"
    editor.save(output_path)
    
    return engine

def test_modify_specific_slide():
    """测试修改指定页面"""
    print("\n" + "=" * 60)
    print("测试 4: 修改指定页面")
    print("=" * 60)
    
    # 创建包含多页的 PPT
    editor = create_ppt(theme="promotion")
    
    # 添加 3 页
    for i in range(3):
        n = editor.add_slide()
        editor.add_header_bar(n, f"第 {n} 页")
        editor.add_text(n, f"这是第 {n} 页的内容")
    
    editor.print_slides()
    
    # 修改第 2 页
    print("\n修改第 2 页:")
    editor.clear_slide(2)
    editor.set_background(2, "e6edf9")  # 使用蓝白背景
    editor.add_header_bar(2, "修改后的第 2 页", color="3669cd")  # 使用蓝色
    editor.add_text(2, "这是修改后的内容，使用了不同的配色", y=1.5)
    
    output_path = "/tmp/super-ppt-modify-test.pptx"
    editor.save(output_path)
    
    return editor

def main():
    """运行所有测试"""
    print("🚀 Super PPT 功能测试")
    print("=" * 60)
    
    # 显示可用主题
    print(f"\n📋 可用主题: {', '.join(list_themes())}")
    
    # 显示可用动画
    print(f"\n🎬 可用动画:")
    anims = list_animations()
    for cat, types in anims.items():
        print(f"   {cat}: {', '.join(types[:5])}{'...' if len(types) > 5 else ''}")
    
    # 运行测试
    try:
        test_open_existing_ppt()
    except Exception as e:
        print(f"⚠️ 测试 1 失败: {e}")
    
    try:
        editor, path = test_create_new_ppt()
        print(f"✅ 新建 PPT 测试通过: {path}")
    except Exception as e:
        print(f"⚠️ 测试 2 失败: {e}")
        import traceback
        traceback.print_exc()
    
    try:
        test_animation()
        print("✅ 动画测试通过")
    except Exception as e:
        print(f"⚠️ 测试 3 失败: {e}")
        import traceback
        traceback.print_exc()
    
    try:
        test_modify_specific_slide()
        print("✅ 修改页面测试通过")
    except Exception as e:
        print(f"⚠️ 测试 4 失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("🎉 测试完成!")
    print("=" * 60)

if __name__ == "__main__":
    main()
