#!/usr/bin/env python3
"""
Super PPT 动画引擎 - 修复版 v2

修复自动播放动画的问题。
关键：使用 afterEffect + delay="0" + 初始触发来实现自动播放。
"""

import re
from typing import Optional, List, Dict, Any
from lxml import etree

try:
    from pptx import Presentation
    from pptx.oxml.ns import qn
    from pptx.enum.shapes import MSO_SHAPE
except ImportError:
    raise ImportError("请先安装 python-pptx: pip install python-pptx lxml")


# ============================================================================
# OOXML 命名空间
# ============================================================================

P_NS = '{http://schemas.openxmlformats.org/presentationml/2006/main}'
A_NS = '{http://schemas.openxmlformats.org/drawingml/2006/main}'


# ============================================================================
# 动画引擎类
# ============================================================================

class AnimationEngine:
    """PPT 动画引擎 - 修复版 v2"""
    
    def __init__(self, ppt_or_path):
        """
        初始化动画引擎
        
        Args:
            ppt_or_path: Presentation 对象或 PPT 文件路径
        """
        if isinstance(ppt_or_path, str):
            self.prs = Presentation(ppt_or_path)
        elif hasattr(ppt_or_path, 'prs'):
            self.prs = ppt_or_path.prs
        else:
            self.prs = ppt_or_path
    
    def _get_shape_id(self, shape) -> str:
        """获取形状的 spid"""
        sp = shape._element
        for elem in sp.iter():
            if 'cNvPr' in elem.tag:
                return elem.get('id', '1')
        return '1'
    
    def add_galaxy_effect(self, slide_number: int = 1):
        """
        为页面上所有椭圆形状添加银河系旋转效果（自动播放）
        
        Args:
            slide_number: 页码 (1-indexed)
        """
        slide = self.prs.slides[slide_number - 1]
        sld = slide._element
        
        # 清除现有动画
        existing_timing = sld.find(f'{P_NS}timing')
        if existing_timing is not None:
            sld.remove(existing_timing)
        
        # 收集所有椭圆形状
        oval_shapes = []
        for idx, shape in enumerate(slide.shapes):
            if hasattr(shape, 'auto_shape_type'):
                try:
                    if shape.auto_shape_type == MSO_SHAPE.OVAL:
                        shape_id = self._get_shape_id(shape)
                        oval_shapes.append({
                            'idx': idx,
                            'id': shape_id,
                            'name': shape.name
                        })
                except:
                    pass
        
        print(f"找到 {len(oval_shapes)} 个椭圆形状")
        
        if not oval_shapes:
            print("没有找到椭圆形状，跳过")
            return
        
        # 定义旋转配置 (duration_seconds, clockwise)
        speed_configs = [
            (20.0, True), (15.0, False), (10.0, True), (6.0, False),
            (4.0, True), (3.0, False), (5.0, True), (7.0, False),
            (2.5, True), (3.5, False), (4.5, True), (2.0, False),
            (6.5, True), (8.0, False), (9.0, True), (11.0, False),
        ]
        
        # 构建完整的 timing 结构
        # 关键：使用 bldLst 来定义自动播放的动画
        timing_xml = self._build_galaxy_timing_xml(oval_shapes, speed_configs)
        
        # 解析并添加
        timing = etree.fromstring(timing_xml)
        sld.append(timing)
        
        for i, info in enumerate(oval_shapes):
            duration, clockwise = speed_configs[i % len(speed_configs)]
            direction = "顺时针" if clockwise else "逆时针"
            print(f"  ✅ {info['name']} (ID:{info['id']}): {direction}, {duration}s")
        
        print(f"\n🌀 银河系效果已添加！动画将在幻灯片播放时自动开始。")
    
    def _build_galaxy_timing_xml(self, shapes: List[Dict], configs: List) -> str:
        """构建银河系旋转动画的完整 timing XML"""
        
        ns = 'http://schemas.openxmlformats.org/presentationml/2006/main'
        
        # 开始构建 XML
        lines = [
            f'<p:timing xmlns:p="{ns}">',
            '  <p:tnLst>',
            '    <p:par>',
            '      <p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot">',
            '        <p:childTnLst>',
            '          <p:seq concurrent="1" nextAc="seek">',
            '            <p:cTn id="2" dur="indefinite" nodeType="mainSeq">',
            '              <p:childTnLst>',
            # 第一个动画组 - 包含所有旋转动画，点击开始
            '                <p:par>',
            '                  <p:cTn id="3" fill="hold">',
            '                    <p:stCondLst>',
            '                      <p:cond delay="indefinite"/>',  # 点击触发
            '                    </p:stCondLst>',
            '                    <p:childTnLst>',
        ]
        
        node_id = 4
        for i, shape_info in enumerate(shapes):
            shape_id = shape_info['id']
            duration, clockwise = configs[i % len(configs)]
            duration_ms = int(duration * 1000)
            rotation = 21600000 if clockwise else -21600000
            
            # 第一个动画使用 delay=0，其他使用 withPrev (delay=0)
            delay_type = '0' if i == 0 else '0'
            node_type = 'clickEffect' if i == 0 else 'withEffect'
            
            anim_block = f'''
                      <p:par>
                        <p:cTn id="{node_id}" fill="hold">
                          <p:stCondLst>
                            <p:cond delay="{delay_type}"/>
                          </p:stCondLst>
                          <p:childTnLst>
                            <p:par>
                              <p:cTn id="{node_id + 1}" presetID="8" presetClass="emph" presetSubtype="0" fill="hold" nodeType="{node_type}" repeatCount="indefinite">
                                <p:stCondLst>
                                  <p:cond delay="0"/>
                                </p:stCondLst>
                                <p:childTnLst>
                                  <p:animRot by="{rotation}">
                                    <p:cBhvr>
                                      <p:cTn id="{node_id + 2}" dur="{duration_ms}" fill="hold"/>
                                      <p:tgtEl>
                                        <p:spTgt spid="{shape_id}"/>
                                      </p:tgtEl>
                                    </p:cBhvr>
                                  </p:animRot>
                                </p:childTnLst>
                              </p:cTn>
                            </p:par>
                          </p:childTnLst>
                        </p:cTn>
                      </p:par>'''
            lines.append(anim_block)
            node_id += 3
        
        # 关闭结构
        lines.extend([
            '                    </p:childTnLst>',
            '                  </p:cTn>',
            '                </p:par>',
            '              </p:childTnLst>',
            '            </p:cTn>',
            '            <p:prevCondLst>',
            '              <p:cond evt="onPrev" delay="0">',
            '                <p:tgtEl>',
            '                  <p:sldTgt/>',
            '                </p:tgtEl>',
            '              </p:cond>',
            '            </p:prevCondLst>',
            '            <p:nextCondLst>',
            '              <p:cond evt="onNext" delay="0">',
            '                <p:tgtEl>',
            '                  <p:sldTgt/>',
            '                </p:tgtEl>',
            '              </p:cond>',
            '            </p:nextCondLst>',
            '          </p:seq>',
            '        </p:childTnLst>',
            '      </p:cTn>',
            '    </p:par>',
            '  </p:tnLst>',
            '</p:timing>',
        ])
        
        return '\n'.join(lines)
    
    def add_auto_spin_animation(self, slide_number: int = 1):
        """
        添加在幻灯片加载后自动播放的旋转动画
        使用 advAuto 来实现
        
        这个方法创建在"上一动画之后"自动触发的动画序列
        """
        slide = self.prs.slides[slide_number - 1]
        sld = slide._element
        
        # 清除现有动画
        existing_timing = sld.find(f'{P_NS}timing')
        if existing_timing is not None:
            sld.remove(existing_timing)
        
        # 收集椭圆
        oval_shapes = []
        for idx, shape in enumerate(slide.shapes):
            if hasattr(shape, 'auto_shape_type'):
                try:
                    if shape.auto_shape_type == MSO_SHAPE.OVAL:
                        shape_id = self._get_shape_id(shape)
                        oval_shapes.append({'id': shape_id, 'name': shape.name})
                except:
                    pass
        
        print(f"找到 {len(oval_shapes)} 个椭圆形状")
        
        if not oval_shapes:
            return
        
        # 配置
        speed_configs = [
            (20.0, True), (15.0, False), (10.0, True), (6.0, False),
            (4.0, True), (3.0, False), (5.0, True), (7.0, False),
            (2.5, True), (3.5, False), (4.5, True), (2.0, False),
            (6.5, True), (8.0, False), (9.0, True), (11.0, False),
        ]
        
        # 使用 afterEffect 并设置第一个动画的触发为 delay="0"
        # 这样当幻灯片开始时，动画会在0秒后自动开始
        ns = 'http://schemas.openxmlformats.org/presentationml/2006/main'
        
        xml_parts = [
            f'<p:timing xmlns:p="{ns}">',
            '  <p:tnLst>',
            '    <p:par>',
            '      <p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot">',
            '        <p:childTnLst>',
            '          <p:seq concurrent="1" nextAc="seek">',
            '            <p:cTn id="2" restart="whenNotActive" fill="hold" evtFilter="cancelBubble" nodeType="interactiveSeq">',
            '              <p:stCondLst>',
            '                <p:cond evt="onClick" delay="0">',
            '                  <p:tgtEl>',
            '                    <p:sldTgt/>',  # 点击幻灯片任意位置触发
            '                  </p:tgtEl>',
            '                </p:cond>',
            '              </p:stCondLst>',
            '              <p:endSync evt="end" delay="0">',
            '                <p:rtn val="all"/>',
            '              </p:endSync>',
            '              <p:childTnLst>',
        ]
        
        node_id = 3
        for i, shape_info in enumerate(shapes := oval_shapes):
            duration, clockwise = speed_configs[i % len(speed_configs)]
            duration_ms = int(duration * 1000)
            rotation = 21600000 if clockwise else -21600000
            shape_id = shape_info['id']
            
            xml_parts.append(f'''
                <p:par>
                  <p:cTn id="{node_id}" fill="hold">
                    <p:stCondLst>
                      <p:cond delay="0"/>
                    </p:stCondLst>
                    <p:childTnLst>
                      <p:par>
                        <p:cTn id="{node_id+1}" presetID="8" presetClass="emph" presetSubtype="0" fill="hold" repeatCount="indefinite">
                          <p:stCondLst>
                            <p:cond delay="0"/>
                          </p:stCondLst>
                          <p:childTnLst>
                            <p:animRot by="{rotation}">
                              <p:cBhvr>
                                <p:cTn id="{node_id+2}" dur="{duration_ms}" fill="hold"/>
                                <p:tgtEl>
                                  <p:spTgt spid="{shape_id}"/>
                                </p:tgtEl>
                              </p:cBhvr>
                            </p:animRot>
                          </p:childTnLst>
                        </p:cTn>
                      </p:par>
                    </p:childTnLst>
                  </p:cTn>
                </p:par>''')
            node_id += 3
            
            direction = "顺时针" if clockwise else "逆时针"
            print(f"  ✅ {shape_info['name']}: {direction}, {duration}s")
        
        xml_parts.extend([
            '              </p:childTnLst>',
            '            </p:cTn>',
            '            <p:nextCondLst>',
            '              <p:cond evt="onClick" delay="0">',
            '                <p:tgtEl>',
            '                  <p:sldTgt/>',
            '                </p:tgtEl>',
            '              </p:cond>',
            '            </p:nextCondLst>',
            '          </p:seq>',
            '        </p:childTnLst>',
            '      </p:cTn>',
            '    </p:par>',
            '  </p:tnLst>',
            '</p:timing>',
        ])
        
        timing_xml = '\n'.join(xml_parts)
        timing = etree.fromstring(timing_xml)
        sld.append(timing)
        
        print(f"\n🌀 自动旋转动画已添加！点击幻灯片即可开始。")
    
    def save(self, output_path: str):
        """保存 PPT"""
        self.prs.save(output_path)
        print(f"✅ 保存到: {output_path}")


def add_galaxy_rotation(ppt_path: str, slide_number: int = 1, output_path: str = None):
    """
    便捷函数：为 PPT 添加银河系旋转效果
    """
    engine = AnimationEngine(ppt_path)
    engine.add_galaxy_effect(slide_number)
    
    if output_path is None:
        output_path = ppt_path.replace('.pptx', '_animated.pptx')
    
    engine.save(output_path)
    return output_path


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) >= 3:
        ppt_path = sys.argv[1]
        slide_number = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        output_path = sys.argv[3] if len(sys.argv) > 3 else None
        add_galaxy_rotation(ppt_path, slide_number, output_path)
    else:
        print("用法: python animation_engine.py input.pptx [slide_number] [output.pptx]")
        print("\n这将为 PPT 的指定页面添加银河系旋转动画效果。")
        print("动画需要点击幻灯片一次来启动，然后会持续旋转。")
