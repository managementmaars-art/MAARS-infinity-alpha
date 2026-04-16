#!/usr/bin/env python3
"""
Super PPT Editor - 核心 PPT 编辑模块

支持：
1. 读取和修改现有 PPT 指定页面
2. 应用预设风格系统（如 promotion 风格）
3. 添加动画效果（通过操作底层 XML）
"""

import os
import copy
import zipfile
import tempfile
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any, Union, Literal

try:
    from pptx import Presentation
    from pptx.util import Inches, Pt, Emu
    from pptx.dml.color import RGBColor
    from pptx.enum.shapes import MSO_SHAPE
    from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
except ImportError:
    raise ImportError("请先安装 python-pptx: pip install python-pptx")

# 样式提取器（可选导入）
try:
    from style_extractor import load_style, list_styles, extract_style, USER_STYLES_DIR
    STYLE_EXTRACTOR_AVAILABLE = True
except ImportError:
    STYLE_EXTRACTOR_AVAILABLE = False
    USER_STYLES_DIR = None

# ============================================================================
# 配色主题定义
# ============================================================================

# 内置主题
BUILTIN_THEMES = {
    "promotion": {
        "name": "晋升答辩风格",
        "colors": {
            "primary": "fc5a1f",       # 品牌橙
            "secondary": "3669cd",     # 企业蓝
            "text_dark": "434343",     # 深灰标题
            "text_normal": "707070",   # 正文灰
            "text_light": "a4a4a3",    # 辅助文字
            "background": "ffffff",    # 主背景
            "card_bg": "f8f8f8",       # 卡片背景
            "accent_light": "fca787",  # 浅橙
            "blue_light": "e6edf9",    # 蓝白背景
            "success": "51cf66",       # 成功绿（用于 solution）
            "problem": "fc5a1f",       # 问题色（使用品牌橙）
            "solution": "3669cd",      # 解决色（使用企业蓝）
            "problem_bg": "fff5f0",    # 问题背景（浅橙）
            "solution_bg": "f0f8ff",   # 解决背景（浅蓝）
        },
        "fonts": {
            "title": "Arial",  # 使用 Arial 确保跨平台兼容
            "body": "Arial",
            "title_size": Pt(28),
            "subtitle_size": Pt(18),
            "body_size": Pt(14),
            "caption_size": Pt(10),
        },
        "layout": {
            "margin_left": 0.5,
            "margin_right": 0.5,
            "margin_top": 0.5,  # 减小顶部边距
            "header_height": 0.5,  # 减小标题栏高度（纯数字，单位英寸）
        }
    },
    "tech": {
        "name": "技术分享风格",
        "colors": {
            "primary": "4a00e0",       # 紫色
            "secondary": "8e2de2",     # 浅紫
            "text_dark": "1a1a2e",     # 深色
            "text_normal": "e0e0e0",   # 浅色
            "text_light": "a0a0a0",    # 灰色
            "background": "1a1a2e",    # 深色背景
            "card_bg": "2d2d44",       # 卡片背景
            "accent_light": "00d4ff",  # 青色强调
            "problem": "ff6b6b",       # 问题红
            "solution": "51cf66",      # 解决绿
        },
        "fonts": {
            "title": "Arial",
            "body": "Arial",
            "title_size": Pt(28),
            "subtitle_size": Pt(18),
            "body_size": Pt(14),
            "caption_size": Pt(10),
        },
        "layout": {
            "margin_left": Inches(0.5),
            "margin_right": Inches(0.5),
            "margin_top": Inches(0.8),
            "header_height": Inches(0.8),
        }
    },
}


def _convert_user_style_to_theme(style) -> Dict[str, Any]:
    """将用户样式转换为内部主题格式"""
    return {
        "name": style.name,
        "colors": style.colors,
        "fonts": {
            "title": style.fonts.get("title", "Microsoft YaHei"),
            "body": style.fonts.get("body", "Microsoft YaHei"),
            "title_size": Pt(style.fonts.get("title_size", 28)),
            "subtitle_size": Pt(style.fonts.get("subtitle_size", 18)),
            "body_size": Pt(style.fonts.get("body_size", 14)),
            "caption_size": Pt(style.fonts.get("caption_size", 10)),
        },
        "layout": {
            "margin_left": Inches(style.layout.get("margin_left", 0.5)),
            "margin_right": Inches(style.layout.get("margin_right", 0.5)),
            "margin_top": Inches(style.layout.get("margin_top", 0.8)),
            "header_height": Inches(style.layout.get("header_height", 0.8)),
        },
        "style_prompt": getattr(style, 'style_prompt', ''),  # 风格 prompt
    }


def get_theme(theme_name: str) -> Dict[str, Any]:
    """
    获取主题配置
    
    优先级：
    1. 内置主题
    2. 用户自定义主题（~/.ppt-styles/）
    """
    # 检查内置主题
    if theme_name in BUILTIN_THEMES:
        return BUILTIN_THEMES[theme_name]
    
    # 检查用户主题
    if STYLE_EXTRACTOR_AVAILABLE:
        user_style = load_style(theme_name)
        if user_style:
            return _convert_user_style_to_theme(user_style)
    
    # 默认返回 promotion 主题
    print(f"⚠️ 主题 '{theme_name}' 不存在，使用默认 promotion 主题")
    return BUILTIN_THEMES["promotion"]


def get_style_prompt(theme_name: str) -> str:
    """
    获取主题的风格 prompt
    
    返回描述性的风格指南，用于指导 AI 理解和应用该视觉风格
    """
    if STYLE_EXTRACTOR_AVAILABLE:
        user_style = load_style(theme_name)
        if user_style and hasattr(user_style, 'style_prompt'):
            return user_style.style_prompt
    
    # 内置主题的默认 prompt
    if theme_name == "promotion":
        return """## 晋升答辩风格指南

### 整体风格
专业、简洁、重点突出的演示风格，适合晋升答辩、工作汇报等正式场合。

### 配色方案
- **主色调**: #fc5a1f（品牌橙）- 用于标题栏、强调信息
- **辅助色**: #3669cd（企业蓝）- 用于图表、链接
- **文字**: 深灰 #434343 / 中灰 #707070
- **背景**: 纯白 #ffffff，卡片浅灰 #f8f8f8

### 设计原则
1. 信息层次清晰，一页一个重点
2. 数据可视化，用图表代替文字堆砌
3. 适度留白，避免信息过载
4. 统一的标题栏设计，保持页面一致性
"""
    elif theme_name == "tech":
        return """## 技术分享风格指南

### 整体风格
深色背景、科技感强烈的演示风格，适合技术分享、产品发布等场合。

### 配色方案
- **主色调**: #4a00e0（科技紫）
- **强调色**: #00d4ff（青色）
- **背景**: 深色 #1a1a2e
- **文字**: 浅色 #e0e0e0

### 设计原则
1. 代码块使用等宽字体，深色背景
2. 技术架构图使用简洁的线条和图标
3. 动画效果要克制，避免分散注意力
"""
    
    return ""


# 兼容旧代码的 THEMES 变量
THEMES = BUILTIN_THEMES


def hex_to_rgb(hex_color: str) -> RGBColor:
    """将 hex 颜色转换为 RGBColor"""
    hex_color = hex_color.lstrip('#')
    return RGBColor(
        int(hex_color[0:2], 16),
        int(hex_color[2:4], 16),
        int(hex_color[4:6], 16)
    )


# ============================================================================
# PPT 编辑器类
# ============================================================================

class SuperPPTEditor:
    """
    Super PPT 编辑器
    
    支持：
    - 打开现有 PPT 或创建新 PPT
    - 指定修改某一页
    - 应用风格主题
    - 添加动画效果
    """
    
    def __init__(self, pptx_path: Optional[str] = None, theme: str = "promotion"):
        """
        初始化编辑器
        
        Args:
            pptx_path: PPT 文件路径，None 则创建新 PPT
            theme: 风格主题名称
        """
        self.pptx_path = pptx_path
        self.theme_name = theme
        self.theme = get_theme(theme)
        self.style_prompt = self.theme.get('style_prompt', '') or get_style_prompt(theme)
        
        if pptx_path and os.path.exists(pptx_path):
            self.prs = Presentation(pptx_path)
            print(f"✅ 已加载 PPT: {pptx_path}")
            print(f"   共 {len(self.prs.slides)} 页")
        else:
            self.prs = Presentation()
            # 使用与 PptxGenJS 相同的 16:9 尺寸（10 x 5.625 英寸）
            # 这是 PowerPoint 的标准 16:9 尺寸，与大多数 PPT 工具兼容
            self.prs.slide_width = Inches(10)
            self.prs.slide_height = Inches(5.625)
            print(f"✅ 创建新 PPT (16:9, 10×5.625 英寸)")
        
        print(f"🎨 当前风格: {self.theme['name']}")
        if self.style_prompt:
            print(f"📝 风格 Prompt 已加载 ({len(self.style_prompt)} 字符)")
    
    def get_style_prompt(self) -> str:
        """获取当前主题的风格 prompt"""
        return self.style_prompt
    
    def print_style_prompt(self):
        """打印当前主题的风格 prompt"""
        if self.style_prompt:
            print(f"\n📝 风格 Prompt ({self.theme_name}):")
            print("-" * 50)
            print(self.style_prompt)
            print("-" * 50)
        else:
            print(f"⚠️ 主题 '{self.theme_name}' 没有风格 prompt")
    
    # -------------------------------------------------------------------------
    # 页面访问和信息
    # -------------------------------------------------------------------------
    
    def get_slide(self, slide_number: int):
        """获取指定页面（1-indexed）"""
        if slide_number < 1 or slide_number > len(self.prs.slides):
            raise ValueError(f"页码 {slide_number} 超出范围 (1-{len(self.prs.slides)})")
        return self.prs.slides[slide_number - 1]
    
    def get_slide_count(self) -> int:
        """获取总页数"""
        return len(self.prs.slides)
    
    def list_slides(self) -> List[Dict[str, Any]]:
        """列出所有页面信息"""
        slides_info = []
        for i, slide in enumerate(self.prs.slides, 1):
            # 提取标题
            title = None
            for shape in slide.shapes:
                if shape.has_text_frame:
                    text = shape.text_frame.text.strip()
                    if text:
                        title = text[:50]  # 截取前50字符
                        break
            
            slides_info.append({
                "number": i,
                "title": title or "(无标题)",
                "shape_count": len(slide.shapes)
            })
        return slides_info
    
    def print_slides(self):
        """打印所有页面概览"""
        print(f"\n📑 PPT 概览 ({len(self.prs.slides)} 页):")
        print("-" * 50)
        for info in self.list_slides():
            print(f"  [{info['number']:2d}] {info['title']} ({info['shape_count']} shapes)")
        print("-" * 50)
    
    # -------------------------------------------------------------------------
    # 页面修改
    # -------------------------------------------------------------------------
    
    def add_slide(self, layout_index: int = 6) -> int:
        """
        添加新页面
        
        Args:
            layout_index: 布局索引 (6 = 空白布局)
        
        Returns:
            新页面的页码
        """
        layout = self.prs.slide_layouts[layout_index]
        slide = self.prs.slides.add_slide(layout)
        slide_number = len(self.prs.slides)
        print(f"✅ 添加新页面: 第 {slide_number} 页")
        return slide_number
    
    def clear_slide(self, slide_number: int):
        """清除指定页面的所有内容"""
        slide = self.get_slide(slide_number)
        # 删除所有形状（倒序删除避免索引问题）
        for shape in list(slide.shapes):
            sp = shape._element
            sp.getparent().remove(sp)
        print(f"✅ 已清除第 {slide_number} 页的所有内容")
    
    def set_background(self, slide_number: int, color: Optional[str] = None):
        """设置页面背景色"""
        slide = self.get_slide(slide_number)
        color = color or self.theme["colors"]["background"]
        
        fill = slide.background.fill
        fill.solid()
        fill.fore_color.rgb = hex_to_rgb(color)
        print(f"✅ 设置第 {slide_number} 页背景: #{color}")
    
    # -------------------------------------------------------------------------
    # 添加元素（应用主题风格）
    # -------------------------------------------------------------------------
    
    def add_title(self, slide_number: int, text: str, 
                  subtitle: Optional[str] = None,
                  x: float = 0.5, y: float = 0.3,
                  width: float = 12.33, height: float = 0.8):
        """添加标题（自动应用主题样式）"""
        slide = self.get_slide(slide_number)
        colors = self.theme["colors"]
        fonts = self.theme["fonts"]
        
        # 主标题
        title_box = slide.shapes.add_textbox(
            Inches(x), Inches(y), Inches(width), Inches(height)
        )
        tf = title_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = text
        p.font.size = fonts["title_size"]
        p.font.bold = True
        p.font.color.rgb = hex_to_rgb(colors["primary"])
        p.font.name = fonts["title"]
        
        # 副标题
        if subtitle:
            self.add_text(
                slide_number, subtitle,
                x=x, y=y + height,
                width=width, height=0.5,
                font_size=fonts["subtitle_size"],
                color=colors["text_normal"]
            )
        
        print(f"✅ 添加标题: {text[:30]}...")
    
    def add_text(self, slide_number: int, text: str,
                 x: float = 0.5, y: float = 1.5,
                 width: float = 12.33, height: float = 0.5,
                 font_size: Optional[Pt] = None,
                 color: Optional[str] = None,
                 bold: bool = False,
                 align: str = "left"):
        """添加文本框"""
        slide = self.get_slide(slide_number)
        colors = self.theme["colors"]
        fonts = self.theme["fonts"]
        
        textbox = slide.shapes.add_textbox(
            Inches(x), Inches(y), Inches(width), Inches(height)
        )
        tf = textbox.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        
        # 使用 add_run 来设置文字和样式，这样字体设置会直接应用到 run 上
        run = p.add_run()
        run.text = text
        run.font.size = font_size or fonts["body_size"]
        run.font.bold = bold
        run.font.color.rgb = hex_to_rgb(color or colors["text_normal"])
        run.font.name = fonts["body"]
        
        if align == "center":
            p.alignment = PP_ALIGN.CENTER
        elif align == "right":
            p.alignment = PP_ALIGN.RIGHT
        
        return textbox
    
    def add_card(self, slide_number: int,
                 x: float, y: float, width: float, height: float,
                 title: Optional[str] = None,
                 content: Optional[str] = None,
                 card_type: str = "normal",
                 icon: Optional[str] = None,
                 subtitle: Optional[str] = None,
                 title_size: int = 11,
                 content_size: int = 10):
        """
        添加卡片组件
        
        Args:
            slide_number: 页码
            x, y, width, height: 位置和尺寸（英寸）
            title: 卡片标题
            content: 卡片内容（支持换行符）
            card_type: "normal", "highlight", "problem", "solution"
            icon: 可选图标（如 emoji）
            subtitle: 可选副标题（显示在标题下方，字体较小）
            title_size: 标题字号，默认 11
            content_size: 内容字号，默认 10
        """
        slide = self.get_slide(slide_number)
        colors = self.theme["colors"]
        fonts = self.theme["fonts"]
        
        # 卡片类型配色 - 使用 promotion 风格的配色
        type_colors = {
            "normal": (colors.get("card_bg", "f8f8f8"), colors.get("text_dark", "434343"), None),
            "highlight": (colors.get("card_bg", "f8f8f8"), colors.get("primary", "fc5a1f"), colors.get("primary", "fc5a1f")),
            "problem": (colors.get("problem_bg", "fff5f0"), colors.get("problem", "fc5a1f"), colors.get("problem", "fc5a1f")),
            "solution": (colors.get("solution_bg", "f0f8ff"), colors.get("solution", "3669cd"), colors.get("solution", "3669cd")),
        }
        bg_color, text_accent, border_color = type_colors.get(card_type, type_colors["normal"])
        
        # 卡片背景
        shape = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(x), Inches(y), Inches(width), Inches(height)
        )
        shape.fill.solid()
        shape.fill.fore_color.rgb = hex_to_rgb(bg_color[:6])  # 取前6位
        
        # 边框
        if card_type == "solution" and border_color:
            shape.line.color.rgb = hex_to_rgb(border_color)
            shape.line.width = Pt(2)
        elif card_type == "problem" and border_color:
            shape.line.color.rgb = hex_to_rgb(border_color)
            shape.line.width = Pt(1)
            shape.line.dash_style = 2  # 虚线
        else:
            shape.line.fill.background()  # 无边框
        
        # 左侧强调条
        if card_type in ["highlight", "problem", "solution"] and border_color:
            accent = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE,
                Inches(x), Inches(y), Inches(0.06), Inches(height)
            )
            accent.fill.solid()
            accent.fill.fore_color.rgb = hex_to_rgb(border_color)
            accent.line.fill.background()
        
        # 计算文字起始位置
        text_x = x + 0.15 if card_type != "normal" else x + 0.1
        current_y = y + 0.08
        
        # 标题
        if title:
            title_text = f"{icon} {title}" if icon else title
            title_textbox = slide.shapes.add_textbox(
                Inches(text_x), Inches(current_y), 
                Inches(width - 0.25), Inches(0.28)
            )
            tf = title_textbox.text_frame
            tf.word_wrap = True
            run = tf.paragraphs[0].add_run()
            run.text = title_text
            run.font.size = Pt(title_size)
            run.font.bold = True
            run.font.color.rgb = hex_to_rgb(text_accent if card_type != "normal" else colors.get("text_dark", "434343"))
            run.font.name = fonts.get("body", "Arial")
            current_y += 0.28
        
        # 副标题（可选）
        if subtitle:
            subtitle_textbox = slide.shapes.add_textbox(
                Inches(text_x), Inches(current_y), 
                Inches(width - 0.25), Inches(0.20)
            )
            tf = subtitle_textbox.text_frame
            tf.word_wrap = True
            run = tf.paragraphs[0].add_run()
            run.text = subtitle
            run.font.size = Pt(9)
            run.font.color.rgb = hex_to_rgb(colors.get("text_light", "707070"))
            run.font.name = fonts.get("body", "Arial")
            current_y += 0.20
        
        # 内容
        if content:
            content_textbox = slide.shapes.add_textbox(
                Inches(text_x), Inches(current_y + 0.02),
                Inches(width - 0.25), Inches(height - (current_y - y) - 0.12)
            )
            tf = content_textbox.text_frame
            tf.word_wrap = True
            run = tf.paragraphs[0].add_run()
            run.text = content
            run.font.size = Pt(content_size)
            run.font.color.rgb = hex_to_rgb(colors.get("text_normal", "707070"))
            run.font.name = fonts.get("body", "Arial")
        
        return shape
    
    def add_box(self, slide_number: int,
                x: float, y: float, width: float, height: float,
                fill_color: Optional[str] = None,
                border_color: Optional[str] = None,
                border_width: float = 1,
                border_dash: bool = False,
                rounded: bool = True):
        """
        添加简单矩形框（不含文字），用于精确布局控制
        
        Args:
            slide_number: 页码
            x, y, width, height: 位置和尺寸（英寸）
            fill_color: 填充色（HEX，如 "f8f8f8"）
            border_color: 边框色（HEX）
            border_width: 边框宽度（pt）
            border_dash: 是否使用虚线边框
            rounded: 是否使用圆角
        """
        slide = self.get_slide(slide_number)
        colors = self.theme["colors"]
        
        shape_type = MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE
        shape = slide.shapes.add_shape(
            shape_type,
            Inches(x), Inches(y), Inches(width), Inches(height)
        )
        
        # 填充
        if fill_color:
            shape.fill.solid()
            shape.fill.fore_color.rgb = hex_to_rgb(fill_color)
        else:
            shape.fill.background()  # 透明
        
        # 边框
        if border_color:
            shape.line.color.rgb = hex_to_rgb(border_color)
            shape.line.width = Pt(border_width)
            if border_dash:
                shape.line.dash_style = 2
        else:
            shape.line.fill.background()
        
        return shape
    
    def add_numbered_item(self, slide_number: int,
                          x: float, y: float,
                          number: str,
                          title: str,
                          description: str,
                          number_color: str = "3669cd",
                          title_width: float = 1.5,
                          desc_width: float = 2.2):
        """
        添加带编号的条目（圆形编号 + 标题 + 描述）
        用于展示步骤、改造点等列表
        
        Args:
            number: 编号（如 "1", "2", "3"）
            title: 标题（粗体）
            description: 描述（普通文字）
            number_color: 编号圆圈的颜色
            title_width: 标题宽度
            desc_width: 描述宽度
        """
        slide = self.get_slide(slide_number)
        colors = self.theme["colors"]
        fonts = self.theme["fonts"]
        
        # 圆形编号背景
        circle = slide.shapes.add_shape(
            MSO_SHAPE.OVAL,
            Inches(x), Inches(y), Inches(0.25), Inches(0.25)
        )
        circle.fill.solid()
        circle.fill.fore_color.rgb = hex_to_rgb(number_color)
        circle.line.fill.background()
        
        # 编号文字
        num_textbox = slide.shapes.add_textbox(
            Inches(x), Inches(y), Inches(0.25), Inches(0.25)
        )
        tf = num_textbox.text_frame
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        run = p.add_run()
        run.text = number
        run.font.size = Pt(10)
        run.font.bold = True
        run.font.color.rgb = hex_to_rgb("ffffff")
        run.font.name = fonts.get("body", "Arial")
        
        # 标题
        title_textbox = slide.shapes.add_textbox(
            Inches(x + 0.35), Inches(y), Inches(title_width), Inches(0.25)
        )
        tf = title_textbox.text_frame
        run = tf.paragraphs[0].add_run()
        run.text = title
        run.font.size = Pt(11)
        run.font.bold = True
        run.font.color.rgb = hex_to_rgb(colors.get("text_dark", "434343"))
        run.font.name = fonts.get("body", "Arial")
        
        # 描述
        desc_textbox = slide.shapes.add_textbox(
            Inches(x + 0.35 + title_width + 0.1), Inches(y), Inches(desc_width), Inches(0.25)
        )
        tf = desc_textbox.text_frame
        run = tf.paragraphs[0].add_run()
        run.text = description
        run.font.size = Pt(10)
        run.font.color.rgb = hex_to_rgb(colors.get("text_normal", "707070"))
        run.font.name = fonts.get("body", "Arial")
    
    def add_header_bar(self, slide_number: int, title: str,
                       color: Optional[str] = None):
        """添加页面顶部标题栏"""
        slide = self.get_slide(slide_number)
        colors = self.theme["colors"]
        fonts = self.theme["fonts"]
        layout = self.theme.get("layout", {})
        bar_color = color or colors["primary"]
        
        # 获取标题栏高度（纯数字，单位英寸）
        header_height_val = layout.get("header_height", 0.5)
        # 确保是数字
        if hasattr(header_height_val, 'inches'):
            header_height_val = header_height_val.inches
        elif hasattr(header_height_val, 'pt'):
            header_height_val = header_height_val.pt / 72  # pt to inches
        
        # 标题栏背景
        bar = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(0), Inches(0),
            self.prs.slide_width, Inches(header_height_val)
        )
        bar.fill.solid()
        bar.fill.fore_color.rgb = hex_to_rgb(bar_color)
        bar.line.fill.background()
        
        # 计算文字垂直居中的位置
        text_y = (header_height_val - 0.35) / 2  # 文字框高度约 0.35，居中
        
        # 标题文字（白色）
        self.add_text(
            slide_number, title,
            x=0.5, y=text_y,
            width=12, height=0.35,
            font_size=Pt(22), bold=True,
            color="ffffff"
        )
        
        print(f"✅ 添加标题栏: {title}")
    
    def add_feature_grid(self, slide_number: int,
                         features: List[Dict[str, str]],
                         columns: int = 3,
                         start_x: float = 0.5, start_y: float = 1.5,
                         item_width: float = 3.8, item_height: float = 0.8,
                         gap: float = 0.15):
        """
        添加特性网格
        
        features: [{"icon": "🔧", "text": "Feature 1"}, ...]
        """
        for idx, feat in enumerate(features):
            col = idx % columns
            row = idx // columns
            x = start_x + col * (item_width + gap)
            y = start_y + row * (item_height + gap)
            
            self.add_card(
                slide_number,
                x=x, y=y, width=item_width, height=item_height,
                title=f"{feat.get('icon', '•')} {feat.get('text', '')}",
                card_type="solution" if feat.get("highlight") else "normal"
            )
        
        print(f"✅ 添加 {len(features)} 个特性卡片")
    
    # -------------------------------------------------------------------------
    # 保存
    # -------------------------------------------------------------------------
    
    def save(self, output_path: Optional[str] = None):
        """保存 PPT"""
        output_path = output_path or self.pptx_path or "output.pptx"
        self.prs.save(output_path)
        print(f"\n💾 已保存: {output_path}")
        return output_path


# ============================================================================
# 便捷函数
# ============================================================================

def open_ppt(path: str, theme: str = "promotion") -> SuperPPTEditor:
    """打开现有 PPT"""
    return SuperPPTEditor(path, theme)


def create_ppt(theme: str = "promotion") -> SuperPPTEditor:
    """创建新 PPT"""
    return SuperPPTEditor(None, theme)


def list_themes() -> List[str]:
    """列出所有可用主题（内置 + 用户自定义）"""
    themes = list(BUILTIN_THEMES.keys())
    
    if STYLE_EXTRACTOR_AVAILABLE:
        user_themes = list_styles()
        themes.extend([f"📁 {t}" for t in user_themes])
    
    return themes


def list_all_themes() -> Dict[str, List[str]]:
    """列出所有主题（分类显示）"""
    result = {
        "builtin": list(BUILTIN_THEMES.keys()),
        "user": []
    }
    
    if STYLE_EXTRACTOR_AVAILABLE:
        result["user"] = list_styles()
    
    return result


# ============================================================================
# CLI 入口
# ============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python ppt_editor.py <pptx_file> [--theme <theme_name>]")
        all_themes = list_all_themes()
        print(f"\n内置主题: {', '.join(all_themes['builtin'])}")
        if all_themes['user']:
            print(f"用户主题: {', '.join(all_themes['user'])}")
        else:
            print(f"用户主题: (无，可通过 style_extractor.py 提取)")
        if USER_STYLES_DIR:
            print(f"\n用户主题目录: {USER_STYLES_DIR}")
        sys.exit(1)
    
    pptx_file = sys.argv[1]
    theme = "promotion"
    
    if "--theme" in sys.argv:
        idx = sys.argv.index("--theme")
        if idx + 1 < len(sys.argv):
            theme = sys.argv[idx + 1]
    
    editor = open_ppt(pptx_file, theme)
    editor.print_slides()
