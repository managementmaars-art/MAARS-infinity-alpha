# 🎬 Media Downloader

> Smart media downloader - Automatically search and download images/video clips based on your description, with auto-trimming support.

[🇨🇳 中文文档](./README_CN.md)

---

## 🚀 What Can I Do?

| You say... | I will... |
|------------|-----------|
| "Download some cute cat pictures" | Search and download 5 cat images |
| "Find a 15-second ocean wave video" | Download a 15s ocean wave clip |
| "Get me a 30-second cooking video" | Download a trimmed cooking clip |
| "Download this YouTube video from 1:30 to 2:00" | Download and auto-trim the specified segment |

---

## ✨ Features

- 🖼️ **Image Download** - Search HD images from professional stock libraries
- 🎬 **Video Clips** - Get free commercial-use video footage
- 📺 **YouTube Download** - Download and trim support
- ✂️ **Smart Trimming** - Auto-crop to your desired length
- 🌍 **Bilingual** - Supports both Chinese and English commands

---

## ⚡ One-Line Install

In Claude Code, just say:

> **"Help me install https://github.com/yizhiyanhua-ai/media-downloader.git and all its dependencies, and configure yt-dlp to use browser cookies"**

Claude will automatically:
- Download the skill to the correct location
- Install yt-dlp, ffmpeg and other dependencies
- Configure browser cookies (fixes YouTube "confirm you're not a bot" issue)
- Check installation status

Just click "Allow" when Claude asks for permission!

---

## 🔑 About API Keys

> 💡 **On-Demand Configuration**: No API Key needed during installation!
>
> - **YouTube Videos**: No API Key required, works right after installation
> - **Image Downloads**: Claude will guide you to configure Pexels API Key on first use

### What Happens When You First Download Images?

When you first say "Download some cat pictures", Claude will:

1. Detect that you haven't configured a stock photo API Key yet
2. Guide you to register at **https://www.pexels.com** (Google/Apple quick signup supported)
3. Help you get the API Key and automatically save it to system environment variables
4. Then continue with the image download

The whole process takes just a few minutes, and you only need to do it once!

---

## 📋 More Image Sources (Optional)

Pexels covers most needs. If you want more image sources, just tell Claude:

> **"Help me configure Pixabay API Key"** or **"Help me configure Unsplash API Key"**

Claude will guide you through registration and configuration.

---

## 💬 Usage Examples

> ⚠️ **Important**: Before using, tell Claude **"Check the status of media-downloader"** to make sure all dependencies are installed!

### Download Images

```
"Download 5 starry sky images"
"Download 10 coffee shop photos"
"Find some landscape images suitable for wallpapers"
```

### Download Videos

> 💡 **Recommended**: If you need to download videos, **use YouTube first**! YouTube has rich content, high quality, and doesn't require an extra API Key.

```
"Download this video: https://youtube.com/watch?v=xxx"
"Download minute 2 to minute 3 of this YouTube video"
"Only download the audio from this video"
```

If you need short video clips from stock libraries:

```
"Download a city night video, under 30 seconds"
"Find me a 15-second ocean wave video"
"Find some natural scenery videos suitable for backgrounds"
```

---

## 📁 Download Location

By default, all files are saved to:

```
~/.claude/skills/media-downloader/downloads/
```

### Custom Download Directory

You can specify a custom download location using the `-o` or `--output` option:

```bash
# Download images to a specific folder
media_cli.py image "cats" -o ~/Pictures/cats

# Download videos to Desktop
media_cli.py video "sunset" -o ~/Desktop

# Download YouTube video to current directory
media_cli.py youtube "URL" -o .
```

Or simply tell me where you want the files:

```
"Download 5 cat images to my Desktop"
"Save the video to ~/Videos/project"
```

---

## ❓ FAQ

### Q: YouTube says "Sign in to confirm you're not a bot"?

This is YouTube's anti-bot mechanism. The solution is to let yt-dlp use your browser's login session:

**Method 1: Tell Claude (Recommended)**

> **"Help me configure yt-dlp to use browser cookies"**

Claude will set it up for you.

**Method 2: Manual Configuration**

1. Make sure you're logged into YouTube in your browser (Chrome/Firefox/Edge)
2. Add `--cookies-from-browser chrome` when downloading:

```bash
yt-dlp --cookies-from-browser chrome "YouTube_URL"
```

> 💡 **Tip**: Replace `chrome` with your browser: `firefox`, `edge`, `safari`, `brave`, etc.

### Q: Why are there no image search results?
A: Please confirm API Key is configured. Run `status` command to check configuration status.

### Q: YouTube video download failed?
A: YouTube download doesn't need an API Key, but requires yt-dlp. Run `pip install yt-dlp` to install.

### Q: Video trimming doesn't work?
A: ffmpeg is required. macOS users run `brew install ffmpeg`.

### Q: Can these images/videos be used commercially?
A: Assets from Pexels, Pixabay, and Unsplash can all be used commercially for free, no attribution required (though attribution is appreciated).

---

## 🛠️ CLI Reference

For advanced users using command line directly:

```bash
# Check configuration status
media_cli.py status

# Download images
media_cli.py image "keywords" -n count -o output_dir

# Download stock videos
media_cli.py video "keywords" -d max_duration -n count

# Download YouTube video
media_cli.py youtube "URL" --start start_seconds --end end_seconds

# Search media (no download)
media_cli.py search "keywords" --type image/video/all

# Trim local video
media_cli.py trim input_file --start start --end end
```

---

## 📦 Supported Sources

| Source | Type | Features |
|--------|------|----------|
| Pexels | Images + Videos | High quality, frequently updated |
| Pixabay | Images + Videos | Large quantity, diverse categories |
| Unsplash | Images | Artistic, great for wallpapers |
| YouTube | Videos | Rich content, trimming support |

---

## 📄 License

MIT License

---

🎬 **Start using! Just tell me what images or videos you want!**
