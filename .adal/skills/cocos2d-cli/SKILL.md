---
name: cocos2d-cli 
description: 用户提供 UI 截图并要求生成白盒预制体时，使用此技能
---

# cocos2d-cli

Cocos Creator CLI 工具，支持通过 JSON 描述生成预制体/场景，以及截图预览。

## When to use

- 需要将 UI 设计稿还原为 Cocos Creator 白盒预制体时
- 需要快速预览 JSON 描述的 UI 效果而不打开编辑器时
- 需要对现有场景/预制体进行批量查询或修改时

## Instructions

### 1. 核心工作流

JSON 描述 → `screenshot` 预览 → 迭代调整 → `create-prefab` 生成

```bash
# 预览 JSON 效果
npx cocos2d-cli screenshot panel.json

# 生成预制体
npx cocos2d-cli create-prefab panel.json assets/Panel.prefab
```

### 1.1 白盒预制体工作循环

当用户输入一张图，并要求“生成白盒预制体”时，执行下面这个闭环流程，而不是直接一次性输出 prefab。

#### 标准循环

1. **先分析 UI 截图**
   - 识别页面整体尺寸和主要区域划分
   - 识别背景、头部、卡片、按钮、标题、正文、列表、分割线、弹窗、遮罩、角标等结构
   - 识别每个元素的大致位置、宽高、层级关系、对齐方式、留白、颜色块、文字样式
   - 白盒阶段优先还原：**结构、层级、位置、尺寸、间距、对齐、颜色块、文本占位**
   - 白盒阶段不要求真实图片资源，不要求像素级视觉细节

2. **生成第一版 JSON**
   - 先搭建根节点和主要布局骨架，再补充细节节点
   - 使用 `sprite` 表示背景、卡片、按钮、图片占位、分组块
   - 使用 `label` 或 `richText` 表示标题、正文、说明文字
   - 命名保持清晰可读，例如：`Root`、`Header`、`Panel`、`Title`、`Desc`、`BtnConfirm`

3. **使用 CLI 对 JSON 截图**
   - 必须先把 JSON 写入文件
   - 然后执行 `npx cocos2d-cli screenshot <json文件> ...`
   - 截图宽高尽量与原图一致或接近

4. **对比截图与原图**
   - 检查整体结构是否一致
   - 检查主要块级区域的位置、大小、上下关系是否一致
   - 检查文本区、按钮区、卡片区的对齐和留白是否接近
   - 记录差异类型：位置偏移、尺寸错误、层级错误、对齐错误、间距不一致、漏节点、多节点、颜色块不合理

5. **如果有差异，修改 JSON**
   - 优先修正布局骨架问题，再修正局部问题
   - 如果整体偏移，优先检查父节点尺寸、锚点、子节点定位方式
   - 如果文字不对齐，优先检查 `anchorX`、`width`、`horizontalAlign`
   - 如果块级结构不像，优先检查容器宽高、子节点层级和间距

6. **再次截图，继续对比**
   - 重复执行：**修改 JSON → screenshot → 对比原图**
   - 直到判断白盒结果已经没有明显结构性差异

7. **从最终 JSON 生成 prefab**
   - 只有在截图对比通过后，才执行：`npx cocos2d-cli create-prefab <json文件> <输出.prefab>`

#### 强制要求

- **不要**在分析完截图后直接生成 prefab
- **必须**至少经过一轮 `screenshot` 预览
- 如果截图结果和原图仍有明显差异，**必须继续修改 JSON**
- “没有差异”按白盒标准理解：允许缺少真实素材和装饰细节，但**不允许主要结构、主要位置关系、主要尺寸比例明显错误**

#### 推荐执行节奏

1. 先输出 UI 结构分析
2. 再生成 JSON
3. 再执行截图预览
4. 再说明截图与原图的差异
5. 再修改 JSON
6. 循环直到通过
7. 最后生成 prefab

#### 可直接遵循的伪流程

```text
收到 UI 截图 + “生成白盒预制体”
→ 分析 UI 截图
→ 生成 first-pass JSON
→ 保存为 json 文件
→ 执行 screenshot
→ 对比截图与原图
→ 如果仍有明显差异，则修改 JSON 并再次 screenshot
→ 如果已无明显差异，则执行 create-prefab
```

### 2. JSON 节点描述格式

```json
{
  "name": "节点名称",
  "width": 400,
  "height": 300,
  "x": 0,
  "y": 0,
  "anchorX": 0.5,
  "anchorY": 0.5,
  "color": "#336699",
  "opacity": 255,
  "components": [
    "sprite",
    { "type": "label", "string": "文本", "fontSize": 32, "horizontalAlign": "left" },
    { "type": "richText", "string": "普通<color=#ff0000>红色</color>文字", "fontSize": 28 }
  ],
  "children": []
}
```

#### 节点属性说明

| 属性 | 类型 | 说明 |
|------|------|------|
| name | string | 节点名称，显示在编辑器层级中 |
| x, y | number | 相对于父节点中心的偏移（见坐标系说明） |
| width, height | number | 节点宽高 |
| anchorX, anchorY | number (0-1) | 锚点，默认 0.5 表示中心 |
| color | string (#RRGGBB) | 节点颜色，影响 Sprite 填充/Label 文字色 |
| opacity | number (0-255) | 透明度 |
| rotation | number | 旋转角度（度） |
| scaleX, scaleY | number | 缩放 |
| active | boolean | 是否激活 |
| components | array | 组件列表（见组件说明） |
| children | array | 子节点列表（递归） |

### 3. 坐标系说明（Cocos 中心锚点）

**Cocos 默认锚点在节点中心**（anchorX=0.5, anchorY=0.5），x/y 是相对父节点中心的偏移。

**计算示例**：父节点宽 660，子节点宽 150，要靠左留 30px 边距
```
x = -(660/2) + 30 + (150/2) = -225
```

**靠左/靠右布局推荐写法**（使用 anchorX + horizontalAlign）：

```json
// 靠左对齐文字：节点锚点设为左边，文字对齐设为 left
{
  "anchorX": 0,
  "x": -330,
  "width": 300,
  "components": [
    { "type": "label", "string": "打款人", "horizontalAlign": "left" }
  ]
}

// 靠右对齐文字：节点锚点设为右边，文字对齐设为 right
{
  "anchorX": 1,
  "x": 330,
  "width": 300,
  "components": [
    { "type": "label", "string": "¥40.00", "horizontalAlign": "right" }
  ]
}
```

这样做的好处：锚点控制节点定位基准，horizontalAlign 控制文字在节点内的排列，语义清晰，不需要心算偏移量。

### 4. 组件类型说明

#### sprite
精灵，显示为纯色方块（颜色由节点 color 控制）
```json
"sprite"
// 或
{ "type": "sprite", "sizeMode": 0 }
```

#### label
文本组件
```json
{
  "type": "label",
  "string": "文本内容",
  "fontSize": 28,
  "lineHeight": 40,
  "horizontalAlign": "left",    // left / center / right，默认 center
  "verticalAlign": "center",      // top / center / bottom，默认 center
  "color": "#ffffff"              // 兼容写法，效果等同于节点 color
}
```

**注意**：label 的文字颜色实际由节点 color 控制，组件内的 color 是兼容写法。

**重要补充**：
- `label` 默认按内容自适应显示，不要把 `width` / `height` 当成稳定的文本排版手段
- `anchorX` / `anchorY` 锚定的是节点，不是文字笔画本身的视觉中心
- `horizontalAlign` / `verticalAlign` 主要控制文字在节点内的排列，不等于能自动解决跨多个文本节点的组合排版
- 遇到关键文本时，必须以 `screenshot` 的实际渲染结果为准，不要只凭 JSON 参数脑补最终效果

#### richText
富文本，支持 BBCode 局部样式
```json
{
  "type": "richText",
  "string": "发起<color=#3cb034>准备40元打款</color>的申请<br/>请及时审批！",
  "fontSize": 28,
  "lineHeight": 40,
  "maxWidth": 600,
  "horizontalAlign": "left"       // left / center / right
}
```

**支持的 BBCode 标签**：
- `<color=#RRGGBB>文字</color>` — 局部变色
- `<size=30>文字</size>` — 局部字体大小
- `<b>文字</b>` — 加粗
- `<i>文字</i>` — 斜体
- `<u>文字</u>` — 下划线
- `<br/>` — 换行

**重要**：richText 的节点 color 和 BBCode color 不要混用，运行时以 BBCode 为准。

#### widget
对齐组件
```json
{
  "type": "widget",
  "isAlignLeft": true,
  "isAlignRight": true,
  "isAlignTop": true,
  "isAlignBottom": true,
  "left": 0,
  "right": 0,
  "top": 0,
  "bottom": 0
}
```

#### button
按钮组件（通常配合 sprite 使用）
```json
"button"
```

### 5. CLI 命令参考

```bash
# 预览 JSON 效果（截图）
npx cocos2d-cli screenshot <json文件> [选项]
  -o, --output <目录>     输出目录，默认当前目录
  --width <数值>          视口宽度，默认 750
  --height <数值>         视口高度，默认 1334
  --debug-bounds          叠加节点边界框和名称

# 生成预制体
npx cocos2d-cli create-prefab [JSON文件] <输出.prefab>

# 生成场景
npx cocos2d-cli create-scene [JSON文件] <输出.fire>

# 查看节点树
npx cocos2d-cli tree <场景或预制体文件>

# 获取节点属性
npx cocos2d-cli get <文件> <节点路径> [属性名|组件类型]

# 设置节点属性
npx cocos2d-cli set <文件> <节点路径> <属性名> <值>

# 添加组件
npx cocos2d-cli add-component <文件> <节点路径> <类型>
```

### 6. 注意事项

1. **JSON 参数必须是文件路径**，不支持直接传递 JSON 字符串
2. **颜色说明**：节点 color 控制 Sprite 填充色和 Label 文字色；Label 组件内的 color 是兼容写法，实际同步到节点
3. **richText 颜色**：使用 BBCode `<color=#xxx>` 设置局部颜色，不要依赖节点 color
4. **坐标计算**：默认锚点在中心，复杂布局建议使用 `anchorX=0`（靠左）或 `anchorX=1`（靠右）配合 `horizontalAlign`
5. **文本组合规则**：当多个文本共同组成一个视觉整体时，不要把它们当作互相独立的普通 `label` 分散硬摆；应先建立父节点，把这组文本作为一个组合块来组织布局，再分别放置子 `label`
6. **截图校正规则**：大数字 + 小文字、金额 + 单位、标题 + 状态词这类组合文本，必须通过 `screenshot` 回看实际效果并微调，不能假设一次参数设置就能直接得到正确视觉结果
