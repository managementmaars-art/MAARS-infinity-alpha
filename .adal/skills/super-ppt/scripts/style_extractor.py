#!/usr/bin/env python3
"""
Super PPT Style Extractor - 从 PPT/PDF 提取样式风格

支持：
1. 从 PPT 提取配色、字体、布局信息
2. 从 PDF 提取主题色（通过图像分析）
3. 保存为用户风格配置文件

用户风格目录: ~/.ppt-styles/
"""

import os
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from collections import Counter
from dataclasses import dataclass, asdict
from datetime import datetime

# 用户风格配置目录
USER_STYLES_DIR = Path.home() / ".ppt-styles"


@dataclass
class ExtractedStyle:
    """提取的样式配置"""
    name: str
    description: str
    source_file: str
    extracted_at: str
    
    # 颜色系统
    colors: Dict[str, str]
    
    # 字体设置
    fonts: Dict[str, Any]
    
    # 布局参数
    layout: Dict[str, float]
    
    # 元数据
    metadata: Dict[str, Any]
    
    # 风格提示词（用于 AI 理解和应用风格）
    style_prompt: str = ""


def ensure_styles_dir():
    """确保用户风格目录存在"""
    USER_STYLES_DIR.mkdir(parents=True, exist_ok=True)
    return USER_STYLES_DIR


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """RGB 转 HEX"""
    return f"{r:02x}{g:02x}{b:02x}"


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """HEX 转 RGB"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def color_brightness(r: int, g: int, b: int) -> float:
    """计算颜色亮度 (0-255)"""
    return 0.299 * r + 0.587 * g + 0.114 * b


def is_neutral_color(r: int, g: int, b: int, threshold: int = 15) -> bool:
    """判断是否为中性色（灰色系）"""
    return abs(r - g) < threshold and abs(g - b) < threshold and abs(r - b) < threshold


def categorize_color(r: int, g: int, b: int) -> str:
    """对颜色进行分类"""
    brightness = color_brightness(r, g, b)
    
    # 接近白色
    if brightness > 240:
        return "background"
    
    # 接近黑色
    if brightness < 30:
        return "text_dark"
    
    # 中性灰色
    if is_neutral_color(r, g, b):
        if brightness > 180:
            return "text_light"
        elif brightness > 100:
            return "text_normal"
        else:
            return "text_dark"
    
    # 判断主色调
    max_channel = max(r, g, b)
    if r == max_channel and r > g + 30 and r > b + 30:
        return "primary"  # 偏红/橙
    elif g == max_channel and g > r + 30 and g > b + 30:
        return "success"  # 偏绿
    elif b == max_channel and b > r + 30 and b > g + 30:
        return "secondary"  # 偏蓝
    
    return "accent"


# =============================================================================
# PPT 样式提取
# =============================================================================

def extract_from_pptx(pptx_path: str) -> ExtractedStyle:
    """
    从 PPT 文件提取样式
    
    Args:
        pptx_path: PPT 文件路径
    
    Returns:
        ExtractedStyle 对象
    """
    try:
        from pptx import Presentation
        from pptx.util import Inches
        from pptx.dml.color import RGBColor
    except ImportError:
        raise ImportError("请安装 python-pptx: pip install python-pptx")
    
    prs = Presentation(pptx_path)
    
    # 收集颜色
    colors_found = []
    fonts_found = []
    
    for slide in prs.slides:
        for shape in slide.shapes:
            # 提取形状填充色
            if hasattr(shape, 'fill'):
                fill = shape.fill
                if fill.type is not None:
                    try:
                        if hasattr(fill, 'fore_color') and fill.fore_color.type == 1:  # RGB
                            rgb = fill.fore_color.rgb
                            if rgb:
                                colors_found.append((rgb.red, rgb.green, rgb.blue))
                    except:
                        pass
            
            # 提取文本样式
            if hasattr(shape, 'text_frame'):
                for para in shape.text_frame.paragraphs:
                    for run in para.runs:
                        # 字体
                        if run.font.name:
                            fonts_found.append(run.font.name)
                        # 文字颜色
                        if run.font.color.type == 1:  # RGB
                            rgb = run.font.color.rgb
                            if rgb:
                                colors_found.append((rgb.red, rgb.green, rgb.blue))
    
    # 分析颜色
    color_analysis = analyze_colors(colors_found)
    
    # 分析字体
    font_counter = Counter(fonts_found)
    primary_font = font_counter.most_common(1)[0][0] if font_counter else "Microsoft YaHei"
    
    # 构建样式
    style = ExtractedStyle(
        name=Path(pptx_path).stem.replace(" ", "_").lower(),
        description=f"从 {Path(pptx_path).name} 提取的样式",
        source_file=str(pptx_path),
        extracted_at=datetime.now().isoformat(),
        colors=color_analysis,
        fonts={
            "title": primary_font,
            "body": primary_font,
            "title_size": 28,  # Pt
            "subtitle_size": 18,
            "body_size": 14,
            "caption_size": 10,
        },
        layout={
            "slide_width": float(prs.slide_width.inches),
            "slide_height": float(prs.slide_height.inches),
            "margin_left": 0.5,
            "margin_right": 0.5,
            "margin_top": 0.8,
            "header_height": 0.8,
        },
        metadata={
            "slide_count": len(prs.slides),
            "colors_sampled": len(colors_found),
            "fonts_sampled": len(fonts_found),
        }
    )
    
    return style


# =============================================================================
# PDF 样式提取
# =============================================================================

def extract_from_pdf(pdf_path: str, sample_pages: int = 5) -> ExtractedStyle:
    """
    从 PDF 文件提取样式（通过图像分析）
    
    Args:
        pdf_path: PDF 文件路径
        sample_pages: 采样页数
    
    Returns:
        ExtractedStyle 对象
    """
    try:
        from PIL import Image
    except ImportError:
        raise ImportError("请安装 Pillow: pip install Pillow")
    
    # 创建临时目录存放转换后的图片
    with tempfile.TemporaryDirectory() as tmpdir:
        # 使用 pdftoppm 转换 PDF 为图片
        output_prefix = os.path.join(tmpdir, "page")
        
        try:
            subprocess.run(
                ["pdftoppm", "-png", "-r", "72", "-l", str(sample_pages), pdf_path, output_prefix],
                check=True,
                capture_output=True
            )
        except FileNotFoundError:
            raise RuntimeError("需要安装 poppler-utils: brew install poppler")
        except subprocess.CalledProcessError as e:
            print(f"警告: PDF 转换时出现错误，但继续处理: {e.stderr.decode()[:100]}")
        
        # 收集所有颜色
        all_colors = []
        page_images = sorted(Path(tmpdir).glob("page-*.png"))
        
        for img_path in page_images[:sample_pages]:
            colors = extract_colors_from_image(str(img_path))
            all_colors.extend(colors)
    
    # 分析颜色
    color_analysis = analyze_colors(all_colors)
    
    # 构建样式
    style = ExtractedStyle(
        name=Path(pdf_path).stem.replace(" ", "_").lower(),
        description=f"从 {Path(pdf_path).name} 提取的样式",
        source_file=str(pdf_path),
        extracted_at=datetime.now().isoformat(),
        colors=color_analysis,
        fonts={
            "title": "Microsoft YaHei",
            "body": "Microsoft YaHei",
            "title_size": 28,
            "subtitle_size": 18,
            "body_size": 14,
            "caption_size": 10,
        },
        layout={
            "slide_width": 13.33,  # 默认 16:9
            "slide_height": 7.5,
            "margin_left": 0.5,
            "margin_right": 0.5,
            "margin_top": 0.8,
            "header_height": 0.8,
        },
        metadata={
            "pages_sampled": len(page_images),
            "colors_sampled": len(all_colors),
        }
    )
    
    return style


def extract_colors_from_image(image_path: str, sample_size: int = 100) -> List[Tuple[int, int, int]]:
    """从图片提取颜色样本"""
    try:
        from PIL import Image
    except ImportError:
        return []
    
    img = Image.open(image_path)
    
    # 缩小图片以加速采样
    img_small = img.resize((sample_size, sample_size))
    
    # 转换为 RGB
    if img_small.mode != 'RGB':
        img_small = img_small.convert('RGB')
    
    # 获取像素数据
    pixels = list(img_small.getdata())
    
    # 过滤掉纯白和接近白色的颜色
    filtered = []
    for pixel in pixels:
        r, g, b = pixel[:3]
        # 排除接近白色的颜色
        if not (r > 245 and g > 245 and b > 245):
            filtered.append((r, g, b))
    
    return filtered


def analyze_colors(colors: List[Tuple[int, int, int]]) -> Dict[str, str]:
    """
    分析颜色列表，提取主要颜色类别
    
    Returns:
        颜色配置字典
    """
    if not colors:
        # 返回默认配色
        return {
            "primary": "fc5a1f",
            "secondary": "3669cd",
            "text_dark": "434343",
            "text_normal": "707070",
            "text_light": "a4a4a3",
            "background": "ffffff",
            "card_bg": "f8f8f8",
            "accent_light": "fca787",
            "success": "51cf66",
        }
    
    # 按类别分组
    categories = {
        "primary": [],
        "secondary": [],
        "text_dark": [],
        "text_normal": [],
        "text_light": [],
        "background": [],
        "accent": [],
        "success": [],
    }
    
    for r, g, b in colors:
        cat = categorize_color(r, g, b)
        if cat in categories:
            categories[cat].append((r, g, b))
    
    # 为每个类别选择最常见的颜色
    result = {}
    
    for cat, cat_colors in categories.items():
        if cat_colors:
            # 选择出现最多的颜色
            counter = Counter(cat_colors)
            most_common = counter.most_common(1)[0][0]
            result[cat] = rgb_to_hex(*most_common)
        else:
            # 使用默认值
            defaults = {
                "primary": "fc5a1f",
                "secondary": "3669cd",
                "text_dark": "434343",
                "text_normal": "707070",
                "text_light": "a4a4a3",
                "background": "ffffff",
                "accent": "fca787",
                "success": "51cf66",
            }
            result[cat] = defaults.get(cat, "888888")
    
    # 补充派生颜色
    if "accent_light" not in result and "primary" in result:
        # 从主色派生浅色版本
        r, g, b = hex_to_rgb(result["primary"])
        light_r = min(255, r + 60)
        light_g = min(255, g + 60)
        light_b = min(255, b + 60)
        result["accent_light"] = rgb_to_hex(light_r, light_g, light_b)
    
    if "card_bg" not in result:
        result["card_bg"] = "f8f8f8"
    
    return result


# =============================================================================
# 风格 Prompt 生成
# =============================================================================

def describe_color(hex_color: str) -> str:
    """描述颜色的视觉特征"""
    r, g, b = hex_to_rgb(hex_color)
    
    # 颜色名称映射
    if r > 200 and g < 100 and b < 100:
        return "鲜红色"
    elif r > 200 and g > 100 and g < 180 and b < 100:
        return "橙色"
    elif r > 200 and g > 180 and b < 100:
        return "金黄色"
    elif r < 100 and g > 200 and b < 100:
        return "绿色"
    elif r < 100 and g < 100 and b > 200:
        return "蓝色"
    elif r > 100 and g < 100 and b > 200:
        return "紫色"
    elif r > 200 and g > 200 and b > 200:
        return "白色"
    elif r < 50 and g < 50 and b < 50:
        return "黑色"
    elif abs(r - g) < 20 and abs(g - b) < 20:
        if r > 180:
            return "浅灰色"
        elif r > 100:
            return "灰色"
        else:
            return "深灰色"
    elif r > g and r > b:
        if g > b:
            return "暖橙色"
        else:
            return "品红色"
    elif b > r and b > g:
        if g > r:
            return "青蓝色"
        else:
            return "靛蓝色"
    else:
        return "中性色"


def generate_style_prompt(style: 'ExtractedStyle') -> str:
    """
    根据提取的样式生成描述性 prompt
    
    这个 prompt 可以用于：
    1. 指导 AI 理解和应用该视觉风格
    2. 在创建新 PPT 时作为风格参考
    3. 保持设计的一致性
    """
    colors = style.colors
    fonts = style.fonts
    layout = style.layout
    
    # 分析主色调风格
    primary_desc = describe_color(colors.get("primary", "fc5a1f"))
    secondary_desc = describe_color(colors.get("secondary", "3669cd"))
    
    # 判断整体风格基调
    primary_rgb = hex_to_rgb(colors.get("primary", "fc5a1f"))
    bg_rgb = hex_to_rgb(colors.get("background", "ffffff"))
    
    if color_brightness(*bg_rgb) > 200:
        bg_style = "浅色/白色背景"
        contrast = "深色文字在浅色背景上"
    else:
        bg_style = "深色背景"
        contrast = "浅色文字在深色背景上"
    
    # 判断色彩风格
    if primary_rgb[0] > 200 and primary_rgb[1] < 150:
        color_style = "暖色调、积极活力的"
    elif primary_rgb[2] > 200:
        color_style = "冷色调、专业稳重的"
    else:
        color_style = "中性、平衡的"
    
    # 生成 prompt
    prompt = f"""## 视觉风格指南

### 整体风格
这是一个{color_style}演示文稿风格，采用{bg_style}设计，{contrast}形成清晰的视觉层次。

### 配色方案
- **主色调**: #{colors.get('primary', 'fc5a1f')}（{primary_desc}）- 用于标题、强调、重要按钮和关键信息
- **辅助色**: #{colors.get('secondary', '3669cd')}（{secondary_desc}）- 用于图标、链接、次要强调
- **标题文字**: #{colors.get('text_dark', '434343')} - 深色，确保可读性
- **正文文字**: #{colors.get('text_normal', '707070')} - 中灰色，舒适阅读
- **辅助文字**: #{colors.get('text_light', 'a4a4a3')} - 浅灰色，用于说明和注释
- **背景色**: #{colors.get('background', 'ffffff')}
- **卡片背景**: #{colors.get('card_bg', 'f8f8f8')}
- **强调高亮**: #{colors.get('accent_light', 'fca787')}

### 字体规范
- **标题字体**: {fonts.get('title', 'Microsoft YaHei')}，{fonts.get('title_size', 28)}pt，加粗
- **正文字体**: {fonts.get('body', 'Microsoft YaHei')}，{fonts.get('body_size', 14)}pt
- **副标题**: {fonts.get('subtitle_size', 18)}pt
- **注释/说明**: {fonts.get('caption_size', 10)}pt

### 布局规范
- **幻灯片尺寸**: {layout.get('slide_width', 13.33)}" × {layout.get('slide_height', 7.5)}"（16:9 比例）
- **页边距**: 左右 {layout.get('margin_left', 0.5)}"，顶部 {layout.get('margin_top', 0.8)}"
- **标题栏高度**: {layout.get('header_height', 0.8)}"

### 设计原则
1. **简洁留白**: 保持充足的空白区域，避免内容拥挤
2. **层次分明**: 通过字号、颜色深浅区分信息层级
3. **一致性**: 同类元素使用相同的样式处理
4. **重点突出**: 使用主色调（{primary_desc}）标注关键信息
5. **专业感**: 配色克制，避免过多颜色混用

### 卡片/模块设计
- 使用圆角矩形作为内容容器
- 卡片背景使用浅灰色 #{colors.get('card_bg', 'f8f8f8')}
- 重要卡片可使用主色调边框或左侧强调条
- 问题/痛点使用红色标记，解决方案使用绿色标记

### 适用场景
此风格适合：工作汇报、晋升答辩、技术分享、产品演示等需要专业、清晰表达的场合。
"""
    
    return prompt.strip()


# =============================================================================
# 样式保存和加载
# =============================================================================

def save_style(style: ExtractedStyle, name: Optional[str] = None) -> Path:
    """
    保存样式到用户配置目录
    
    Args:
        style: 提取的样式
        name: 自定义名称（可选）
    
    Returns:
        保存的文件路径
    """
    styles_dir = ensure_styles_dir()
    
    style_name = name or style.name
    style_name = style_name.replace(" ", "_").lower()
    
    # 保存为 JSON
    style_path = styles_dir / f"{style_name}.json"
    
    with open(style_path, 'w', encoding='utf-8') as f:
        json.dump(asdict(style), f, ensure_ascii=False, indent=2)
    
    print(f"✅ 样式已保存: {style_path}")
    return style_path


def load_style(name: str) -> Optional[ExtractedStyle]:
    """
    从用户配置目录加载样式
    
    Args:
        name: 样式名称
    
    Returns:
        ExtractedStyle 对象，不存在则返回 None
    """
    styles_dir = ensure_styles_dir()
    style_path = styles_dir / f"{name}.json"
    
    if not style_path.exists():
        return None
    
    with open(style_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return ExtractedStyle(**data)


def list_styles() -> List[str]:
    """列出所有已保存的样式"""
    styles_dir = ensure_styles_dir()
    return [p.stem for p in styles_dir.glob("*.json")]


def delete_style(name: str) -> bool:
    """删除指定样式"""
    styles_dir = ensure_styles_dir()
    style_path = styles_dir / f"{name}.json"
    
    if style_path.exists():
        style_path.unlink()
        print(f"✅ 样式已删除: {name}")
        return True
    return False


# =============================================================================
# 主函数
# =============================================================================

def extract_style(file_path: str, name: Optional[str] = None, save: bool = True) -> ExtractedStyle:
    """
    从文件提取样式（自动识别 PPT/PDF）
    
    Args:
        file_path: 文件路径（.pptx 或 .pdf）
        name: 自定义样式名称
        save: 是否保存到用户目录
    
    Returns:
        ExtractedStyle 对象
    """
    file_path = os.path.expanduser(file_path)
    ext = Path(file_path).suffix.lower()
    
    print(f"📂 正在分析: {file_path}")
    
    if ext == '.pptx':
        style = extract_from_pptx(file_path)
    elif ext == '.pdf':
        style = extract_from_pdf(file_path)
    else:
        raise ValueError(f"不支持的文件格式: {ext}（支持 .pptx, .pdf）")
    
    if name:
        style.name = name
    
    # 生成风格 prompt
    style.style_prompt = generate_style_prompt(style)
    
    # 打印提取结果
    print(f"\n🎨 提取的样式: {style.name}")
    print(f"   来源: {style.source_file}")
    print(f"   颜色配置:")
    for key, value in style.colors.items():
        print(f"     {key}: #{value}")
    
    print(f"\n📝 生成的风格 Prompt:")
    print("-" * 50)
    # 只打印前几行
    prompt_lines = style.style_prompt.split('\n')[:15]
    for line in prompt_lines:
        print(f"   {line}")
    print(f"   ... (共 {len(style.style_prompt.split(chr(10)))} 行)")
    print("-" * 50)
    
    if save:
        save_style(style)
    
    return style


# =============================================================================
# CLI 入口
# =============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  提取样式:  python style_extractor.py <pptx_or_pdf_file> [--name <style_name>]")
        print("  列出样式:  python style_extractor.py --list")
        print("  删除样式:  python style_extractor.py --delete <style_name>")
        print(f"\n样式目录: {USER_STYLES_DIR}")
        sys.exit(1)
    
    if sys.argv[1] == "--list":
        styles = list_styles()
        if styles:
            print("📋 已保存的样式:")
            for s in styles:
                print(f"   - {s}")
        else:
            print("暂无保存的样式")
    
    elif sys.argv[1] == "--delete":
        if len(sys.argv) < 3:
            print("请指定要删除的样式名称")
            sys.exit(1)
        delete_style(sys.argv[2])
    
    else:
        file_path = sys.argv[1]
        name = None
        
        if "--name" in sys.argv:
            idx = sys.argv.index("--name")
            if idx + 1 < len(sys.argv):
                name = sys.argv[idx + 1]
        
        extract_style(file_path, name)
