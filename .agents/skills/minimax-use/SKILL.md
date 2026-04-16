---
name: minimax-use
description: 使用 MiniMax 进行网络搜索。触发条件：用户要求进行网络搜索、在线搜索、查找最新资讯。其他功能（图像理解、图片生成、语音合成）需要用户明确指定使用 MiniMax 才会触发。
---

# minimax-use

使用 MiniMax 进行网络搜索、图像理解、图片生成和语音合成。

## 功能一：网络搜索

### 调用 web_search

使用脚本调用 MCP 服务：

```bash
python3 {curDir}/scripts/web_search.py "<搜索查询>"
```

**示例：**

```bash
# 搜索今日新闻
python3 {curDir}/scripts/web_search.py "今天的热点新闻"
```

### API 参数说明

| 参数 | 说明 | 类型 |
|------|------|------|
| query | 搜索查询字符串 | string (必填) |

## 功能二：图像理解

### 准备图片

将图片放到可访问路径，例如：
- `~/.openclaw/workspace/images/图片名.jpg`
- 或者使用 URL

### 调用 understand_image

使用脚本调用 MCP 服务：

```bash
python3 {curDir}/scripts/understand_image.py <图片路径或URL> "<对图片的提问>"
```

**示例：**

```bash
# 描述图片内容
python3 {curDir}/scripts/understand_image.py ~/image.jpg "详细描述这张图片的内容"

# 使用 URL
python3 {curDir}/scripts/understand_image.py "https://example.com/image.jpg" "这张图片展示了什么？"
```

### API 参数说明

| 参数 | 说明 | 类型 |
|------|------|------|
| image | 图片路径或 URL | string (必填) |
| prompt | 对图片的提问 | string (必填) |

## 功能三：图片生成

**注意：图片生成消耗较多 token，执行前必须先询问用户是否同意生成。**

### 调用 image

使用脚本调用 MiniMax 图片生成 API：

```bash
python3 {curDir}/scripts/image.py "<描述>" [选项]
```

**示例：**

```bash
# 文生图（T2I）
python3 {curDir}/scripts/image.py "一只可爱的猫咪在阳光下玩耍"

# 指定宽高比和数量
python3 {curDir}/scripts/image.py "一只可爱的猫咪在阳光下玩耍" --aspect-ratio 16:9 --n 2

# 指定宽高
python3 {curDir}/scripts/image.py "一只可爱的猫咪在阳光下玩耍" --width 1024 --height 768 --output cat.png

# 图生图（I2I）
python3 {curDir}/scripts/image.py --subject /path/to/image.jpg "猫咪玩耍"
```

### 选项说明

| 选项 | 说明 | 默认值 |
|------|------|--------|
| --model | 模型版本 | image-01 |
| --aspect-ratio | 图片宽高比 | 1:1 |
| --width | 图片宽度（512-2048，8的倍数） | 无 |
| --height | 图片高度（512-2048，8的倍数） | 无 |
| --n | 生成图片数量（1-9） | 1 |
| --seed | 随机种子 | 无 |
| --output | 保存图片到文件（png/jpg 格式） | 无 |
| --subject | 主体参考图片（图生图 I2I） | 无 |

### 可用模型

**文生图（T2I）：**
- image-01
- image-01-live

**图生图（I2I）：**
- image-01
- image-01-live

### 宽高比选项

- 1:1 (1024x1024)
- 16:9 (1280x720)
- 4:3 (1152x864)
- 3:2 (1248x832)
- 2:3 (832x1248)
- 3:4 (864x1152)
- 9:16 (720x1280)
- 21:9 (1344x576) (仅适用于 image-01)

## 功能四：语音合成 (Text-to-Speech)

### 调用 text_to_speech

使用脚本调用 MiniMax 语音合成 API：

```bash
python3 {curDir}/scripts/text_to_speech.py "<文本>" [选项]
```

**示例：**

```bash
# 基础语音合成
python3 {curDir}/scripts/text_to_speech.py "你好世界" --output audio.mp3

# 指定音色和情感
python3 {curDir}/scripts/text_to_speech.py "今天真开心" --voice female-shaonv --emotion happy --output happy.mp3

# 列出所有可用音色
python3 {curDir}/scripts/text_to_speech.py --list-voices
```

### 选项说明

| 选项 | 说明 | 默认值 |
|------|------|--------|
| --model | 模型版本 | speech-2.8-hd |
| --output | 保存音频到文件（mp3 格式） | 无 (直接输出包含十六进制数据的 JSON) |
| --voice | 音色 ID | female-shaonv |
| --emotion | 情感 (happy, sad, angry, fearful, disgusted, surprised, calm, fluent, whisper) | 无 |
| --list-voices | 列出所有可用的音色列表 | 无 |
