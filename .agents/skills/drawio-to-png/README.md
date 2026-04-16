# Draw.io to PNG Converter Skill

✅ **Skill 已成功创建！**

## 📁 Skill 位置

```
/Users/huyansheng/.codeflicker/skills/drawio-to-png/
```

## 📋 Skill 信息

- **名称**: drawio-to-png
- **版本**: 1.0.0
- **类型**: 个人级 Skill (Personal)
- **描述**: 将 draw.io 格式文件转换为高清 PNG 图片

## 🎯 触发方式

当你说以下任何一句话时，这个 Skill 会被激活：

- "convert drawio to png"
- "export drawio diagram"
- "generate png from drawio"
- "drawio导出png"
- "转换drawio图片"
- "drawio转图片"
- "生成高清drawio图片"
- "批量导出drawio"

## ✨ 主要功能

1. **单文件转换**：将单个 .drawio 文件转为高清 PNG
2. **批量转换**：批量处理多个 draw.io 文件
3. **质量控制**：支持自定义分辨率（1x-5x）
4. **透明背景**：可选透明背景导出
5. **边框设置**：可添加边框增强可见性
6. **多页支持**：支持导出多页图表的特定页面

## 📦 Skill 结构

```
drawio-to-png/
├── SKILL.md                          # 主要技能文档
├── references/
│   ├── cli-reference.md             # draw.io CLI 完整参考
│   └── quality-guide.md             # 质量和分辨率指南
├── scripts/
│   ├── convert.sh                   # 单文件转换脚本
│   └── batch-convert.sh             # 批量转换脚本
└── examples/
    └── single-file.sh               # 示例脚本
```

## 🚀 快速使用

### 方法 1: 通过 AI 助手

直接对 AI 说：
```
"帮我把这个 drawio 文件转成高清 PNG"
```

### 方法 2: 使用脚本

```bash
# 转换单个文件
~/.codeflicker/skills/drawio-to-png/scripts/convert.sh diagram.drawio

# 批量转换当前目录的所有 drawio 文件
~/.codeflicker/skills/drawio-to-png/scripts/batch-convert.sh

# 自定义设置
SCALE=3 TRANSPARENT=true ~/.codeflicker/skills/drawio-to-png/scripts/convert.sh diagram.drawio
```

### 方法 3: 直接使用 draw.io CLI

```bash
# macOS
/Applications/draw.io.app/Contents/MacOS/draw.io -x -f png -s 2 -o output.png input.drawio

# 高清透明背景
/Applications/draw.io.app/Contents/MacOS/draw.io -x -f png -s 2 --transparent -o output.png input.drawio
```

## 📖 使用示例

### 示例 1: 文档配图（推荐设置）

```bash
# 2倍分辨率，透明背景，10px边框
drawio -x -f png -s 2 --transparent --border 10 -o diagram.png input.drawio
```

### 示例 2: 演示文稿（1080p）

```bash
# 2倍分辨率，适合 Full HD 显示
drawio -x -f png -s 2 -o slide-diagram.png input.drawio
```

### 示例 3: 打印材料

```bash
# 4倍分辨率，打印级质量
drawio -x -f png -s 4 -o print-diagram.png input.drawio
```

### 示例 4: 多页图表

```bash
# 导出第一页
drawio -x -f png -s 2 -p 0 -o page-1.png multi-page.drawio

# 导出所有页面
drawio -x -f png -s 2 --all-pages -o output.png multi-page.drawio
```

## 🔧 前置要求

需要安装 draw.io 桌面应用：

### macOS
```bash
brew install --cask drawio
```

### Linux (Debian/Ubuntu)
```bash
wget https://github.com/jgraph/drawio-desktop/releases/download/v22.1.16/drawio-amd64-22.1.16.deb
sudo dpkg -i drawio-amd64-22.1.16.deb
```

### Windows
从 [GitHub Releases](https://github.com/jgraph/drawio-desktop/releases) 下载安装

## 📚 更多信息

查看详细文档：

- **CLI 参考**: `references/cli-reference.md`
- **质量指南**: `references/quality-guide.md`
- **使用示例**: `examples/single-file.sh`

## ⚠️ 重要提示

**Skill 生效时间**：
- Skill 需要间隔 **30秒** 才能被系统扫描并生效
- 或者 **重启 VS Code** 立即生效

建议：等待 30 秒后再测试这个 Skill，或者现在重启 VS Code。

## 🎉 下一步

1. **等待生效**：等待 30 秒或重启 VS Code
2. **测试 Skill**：尝试说 "帮我转换这个 drawio 文件"
3. **查看文档**：阅读 references/ 目录了解更多细节
4. **运行示例**：执行 `examples/single-file.sh` 查看效果

## 🔄 Git 版本管理（可选）

如果你想对这个 Skill 进行版本管理：

```bash
cd ~/.codeflicker/skills/drawio-to-png
git init
git add .
git commit -m "Initial commit: drawio-to-png skill"
```

---

**祝你使用愉快！如果有任何问题或需要改进，随时告诉我。** 🚀
