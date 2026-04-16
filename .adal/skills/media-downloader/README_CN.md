# 🎬 智能媒体下载器

> 根据你的描述自动搜索和下载图片、视频片段，支持视频自动剪辑。

[🇬🇧 English](./README.md)

---

## 🚀 我能帮你做什么？

| 你说... | 我会... |
|---------|---------|
| "下载一些可爱的猫咪图片" | 搜索并下载 5 张猫咪图片 |
| "找一段海浪的视频，15秒左右" | 下载一段 15 秒的海浪视频 |
| "下载一段 30 秒的烹饪视频" | 下载并剪辑烹饪视频 |
| "下载这个 YouTube 视频的 1:30-2:00" | 下载并自动剪辑指定片段 |

---

## ✨ 功能特点

- 🖼️ **图片下载** - 从专业图库搜索高清图片
- 🎬 **视频素材** - 获取免费商用视频片段
- 📺 **YouTube 下载** - 支持下载和剪辑
- ✂️ **智能剪辑** - 自动裁剪到你需要的长度
- 🌍 **中英双语** - 支持中文和英文指令

---

## ⚡ 一句话安装

在 Claude Code 中对 Claude 说：

> **"帮我安装 https://github.com/yizhiyanhua-ai/media-downloader.git 这个 skill 和它的所有依赖，并配置 yt-dlp 使用浏览器 cookies"**

Claude 会自动完成：
- 下载 skill 到正确位置
- 安装 yt-dlp、ffmpeg 等依赖工具
- 配置浏览器 cookies（解决 YouTube「确认你不是机器人」的问题）
- 检查安装状态

你只需要在 Claude 询问时点击「允许」就行了！

---

## 🔑 关于 API Key

> 💡 **按需配置**：安装时不需要配置任何 API Key！
>
> - **下载 YouTube 视频**：不需要 API Key，安装完成即可使用
> - **下载图片**：首次下载时，Claude 会自动引导你配置 Pexels API Key

### 首次下载图片时会发生什么？

当你第一次说「帮我下载一些猫咪图片」时，Claude 会：

1. 检测到你还没有配置图库 API Key
2. 引导你去 **https://www.pexels.com** 注册（支持 Google/Apple 一键注册）
3. 帮你获取 API Key 并自动保存到系统环境变量
4. 然后继续完成图片下载

整个过程只需要几分钟，而且只需要配置一次！

---

## 📋 更多图库（可选）

Pexels 已经能满足大部分需求。如果你想要更多图片来源，可以对 Claude 说：

> **"帮我配置 Pixabay API Key"** 或 **"帮我配置 Unsplash API Key"**

Claude 会引导你完成注册和配置。

---

## 💬 使用示例

> ⚠️ **重要提示**：使用前请先对 Claude 说 **"检查一下 media-downloader 的状态"**，确保所有依赖工具已安装完成！

### 下载图片

```
"帮我下载 5 张星空的图片"
"下载 10 张咖啡店的照片"
"找一些适合做壁纸的风景图"
```

### 下载视频素材

> 💡 **推荐**：如果你需要下载视频，**优先使用 YouTube**！YouTube 视频内容丰富、质量高，而且不需要额外的 API Key。

```
"下载这个视频：https://youtube.com/watch?v=xxx"
"下载这个 YouTube 视频的第 2 分钟到第 3 分钟"
"只下载这个视频的音频"
```

如果你需要从素材库下载短视频片段：

```
"下载一段城市夜景的视频，30秒以内"
"找一段 15 秒的海浪视频"
"找一些适合做背景的自然风光视频"
```

---

## 📁 下载位置

所有文件默认保存在：

```
~/.claude/skills/media-downloader/downloads/
```

### 自定义下载目录

你可以使用 `-o` 或 `--output` 参数指定下载位置：

```bash
# 下载图片到指定文件夹
media_cli.py image "猫咪" -o ~/Pictures/cats

# 下载视频到桌面
media_cli.py video "日落" -o ~/Desktop

# 下载 YouTube 视频到当前目录
media_cli.py youtube "URL" -o .
```

或者直接告诉我你想保存到哪里：

```
"下载 5 张猫咪图片到桌面"
"把视频保存到 ~/Videos/project 文件夹"
```

---

## ❓ 常见问题

### Q: YouTube 提示「需要登录验证」或「确认你不是机器人」？

这是 YouTube 的反爬虫机制。解决方法是让 yt-dlp 使用你浏览器的登录状态：

**方法一：对 Claude 说（推荐）**

> **"帮我配置 yt-dlp 使用浏览器 cookies"**

Claude 会帮你设置好。

**方法二：手动配置**

1. 确保你已经在浏览器（Chrome/Firefox/Edge）中登录了 YouTube
2. 下载视频时添加 `--cookies-from-browser chrome` 参数：

```bash
yt-dlp --cookies-from-browser chrome "YouTube视频链接"
```

> 💡 **提示**：把 `chrome` 换成你使用的浏览器：`firefox`、`edge`、`safari`、`brave` 等

### Q: 为什么搜索图片没有结果？
A: 请确认已配置 API Key。运行 `status` 命令检查配置状态。

### Q: YouTube 视频下载失败？
A: YouTube 下载不需要 API Key，但需要安装 yt-dlp。运行 `pip install yt-dlp` 安装。

### Q: 视频剪辑功能不工作？
A: 需要安装 ffmpeg。macOS 用户运行 `brew install ffmpeg`。

### Q: 这些图片/视频可以商用吗？
A: Pexels、Pixabay、Unsplash 的素材都可以免费商用，无需署名（但署名是一种礼貌）。

---

## 🛠️ CLI 命令参考

供高级用户直接使用命令行：

```bash
# 检查配置状态
media_cli.py status

# 下载图片
media_cli.py image "关键词" -n 数量 -o 输出目录

# 下载视频素材
media_cli.py video "关键词" -d 最大时长 -n 数量

# 下载 YouTube 视频
media_cli.py youtube "URL" --start 开始秒数 --end 结束秒数

# 搜索媒体（不下载）
media_cli.py search "关键词" --type image/video/all

# 剪辑本地视频
media_cli.py trim 输入文件 --start 开始 --end 结束
```

---

## 📦 支持的素材来源

| 来源 | 类型 | 特点 |
|------|------|------|
| Pexels | 图片 + 视频 | 高质量，更新快 |
| Pixabay | 图片 + 视频 | 数量多，种类全 |
| Unsplash | 图片 | 艺术感强，适合壁纸 |
| YouTube | 视频 | 内容丰富，支持剪辑 |

---

## 📄 许可证

MIT License

---

🎬 **开始使用吧！直接告诉我你想要什么图片或视频！**
