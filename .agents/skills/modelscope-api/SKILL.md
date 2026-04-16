---
name: modelscope-api
description: 使用魔搭平台(ModelScope)API进行图片生成和编辑
---

# ModelScope API 图片生成/编辑

## 环境准备

- Node.js >= 18（使用内置 fetch）
- 设置环境变量：

```bash
set MODELSCOPE_API_KEY=ms-你的API密钥
```

## 功能

### 1. 图片生成 (image-generator.js)

使用 `Tongyi-MAI/Z-Image-Turbo` 模型根据提示词生成图片。

```bash
node image-generator.js -p "一只可爱的猫咪"
node image-generator.js -p "科幻城市夜景" -o city_night.jpg
```

参数：
- `-p, --prompt` - 生成提示词（必需）
- `-o, --output` - 输出文件名（可选）
- `-h, --help` - 显示帮助

### 2. 图片编辑 (image-editor.js)

使用 `Qwen/Qwen-Image-Edit-2511` 模型编辑已有图片。

```bash
node image-editor.js -i ./photo.jpg -p "给图中的人戴上墨镜"
node image-editor.js -i ./dog.png -p "给狗戴上生日帽" -o birthday_dog.jpg
```

参数：
- `-i, --image` - 输入图片路径（必需）
- `-p, --prompt` - 编辑提示词（必需）
- `-o, --output` - 输出文件名（可选）
- `-h, --help` - 显示帮助

## 输出信息

脚本会显示模型调用限制信息：
- 模型剩余调用次数
- 总请求剩余次数

## 目录结构

```
modelscope-api/
├── SKILL.md              # 技能说明文档
├── image-generator.js    # 图片生成脚本
└── image-editor.js       # 图片编辑脚本
```
