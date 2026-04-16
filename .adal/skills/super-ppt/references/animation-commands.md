# 动画命令参考

Super PPT 支持通过自然语言描述添加动画效果。

## 进入动画

| 中文 | English | 效果 |
|------|---------|------|
| 淡入 | fade in | 透明度渐变显示 |
| 飞入 | fly in | 从边缘飞入 |
| 从左侧飞入 | fly in from left | 从左边飞入 |
| 从右侧飞入 | fly in from right | 从右边飞入 |
| 从顶部飞入 | fly in from top | 从上方飞入 |
| 从底部飞入 | fly in from bottom | 从下方飞入 |
| 缩放 | zoom in | 从小到大放大 |
| 弹跳/弹出 | bounce/pop | 弹性效果 |
| 上浮 | float up | 上浮显示 |
| 擦除 | wipe | 擦除显示 |
| 分裂 | split | 分裂显示 |

## 强调动画

| 中文 | English | 效果 |
|------|---------|------|
| 脉冲 | pulse | 脉冲闪烁 |
| 闪烁 | flash | 快速闪烁 |
| 旋转 | spin | 旋转强调 |
| 放大 | grow | 放大强调 |

## 退出动画

| 中文 | English | 效果 |
|------|---------|------|
| 淡出 | fade out | 渐变消失 |
| 飞出 | fly out | 飞出边缘 |
| 缩小 | zoom out | 缩小消失 |

## 页面切换

| 中文 | English | 效果 |
|------|---------|------|
| 淡入淡出 | fade | 渐变切换 |
| 推进 | push | 推入效果 |
| 擦除 | wipe | 擦除切换 |
| 分裂 | split | 分裂切换 |
| 立方体 | cube | 3D 立方体 |
| 翻转 | flip | 翻页效果 |
| 画廊 | gallery | 画廊效果 |

## 描述语法

### 基本格式
```
[目标] + [动画类型] + [可选: 时间/延迟]
```

### 示例

**单个动画：**
- "标题淡入"
- "标题从左侧飞入"
- "内容弹出"

**带时间参数：**
- "标题淡入，持续 0.5 秒"
- "内容飞入，延迟 0.3 秒"

**序列动画：**
- "所有元素依次淡入"
- "卡片逐个弹出"
- "内容逐行显示"

**同时触发：**
- "所有图片同时缩放"
- "标题和副标题一起淡入"

**页面切换：**
- "页面使用推进效果切换"
- "切换使用淡入淡出"
- "用立方体效果切换到下一页"

## 触发方式

| 关键词 | 触发方式 | 说明 |
|--------|----------|------|
| 依次/逐个/逐行 | afterPrev | 前一个动画结束后触发 |
| 同时/一起 | withPrev | 与前一个动画同时触发 |
| (默认) | onClick | 点击触发 |

## Python API

```python
from animation_engine import AnimationEngine, animate

# 方式 1: 使用引擎
engine = AnimationEngine(ppt_editor)
engine.add_entrance("fade", slide_number=1, shape_index=0)
engine.add_slide_transition(1, "push")

# 方式 2: 自然语言描述
engine.add_from_description("标题从左侧飞入", slide_number=1)

# 方式 3: 便捷函数
animate(ppt_editor, "内容淡入", slide_number=2)
```
