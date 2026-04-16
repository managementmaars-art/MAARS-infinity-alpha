# 🎨 AI Image Prompt Optimizer

A Claude Code skill for generating and optimizing AI image generation prompts with **primary support for Google Gemini (Nano Banana)**, plus Midjourney, Stable Diffusion, DALL-E, Leonardo.ai, and other text-to-image tools.

## ✨ Features

- **Google Gemini Optimized**: Primary focus on conversational, natural language prompts for Google Gemini (Nano Banana)
- **Multi-Platform Support**: Secondary support for Midjourney, Stable Diffusion, DALL-E, Leonardo.ai
- **Bilingual Output**: English and Chinese prompt variations
- **Educational**: Explains prompt components and optimization strategies
- **Comprehensive Templates**: Pre-built templates for portraits, landscapes, products, and more
- **Reference Library**: Extensive keyword and platform-specific reference materials

## 📦 Installation

### Using npx (Recommended)

```bash
npx skills add manzxiao/text-to-image-prompt-optimizer
```

### Manual Installation

1. Clone this repository to your Claude Code skills directory:
```bash
cd ~/.claude/skills
git clone https://github.com/manzxiao/text-to-image-prompt-optimizer.git
```

2. Restart Claude Code or reload skills

## 🚀 Usage

The skill activates automatically when you:

1. Request prompt generation: "Generate a prompt for..."
2. Optimize existing prompts: "Optimize this prompt: ..."
3. Ask for variations: "Create variations of this image idea"
4. Mention keywords: Gemini, Nano Banana, Midjourney, AI绘图, text-to-image
5. Use command patterns: "/imagine", "提示词"

### Example Requests

```
Generate a prompt for a sunset over mountains

优化这个提示词: a cat sitting on a table

Create variations for a cyberpunk street scene

帮我生成一个适合 Nano Banana 的人物肖像提示词
```

## 📚 What You Get

Each prompt generation includes:

- ⭐ **Google Gemini version** (Primary, conversational style)
- 🎯 **Alternative platform versions** (Midjourney, SD, etc.)
- 📝 **Prompt breakdown** explaining each component
- ⚙️ **Platform-specific guidance** and parameters
- 💡 **Optimization tips** for refinement
- 🎯 **Next steps** for implementation

## 🎓 Reference Materials

The skill includes comprehensive reference documentation:

- **prompt-library.md** - Template library organized by category (portraits, landscapes, products, etc.)
- **keywords-reference.md** - Quick keyword lookup by type
- **platform-specific.md** - Platform-specific parameters and advanced techniques

## 🌟 Platform Priority

**Primary (Default):**
- Google Gemini (Nano Banana) - Conversational, natural language prompts

**Secondary (On Request):**
- Midjourney
- Stable Diffusion
- DALL-E
- Leonardo.ai

## 📖 Example Output

When you ask for a prompt, you'll receive:

```
## 🎨 Generated Prompts

### ⭐ Variation 1: Google Gemini (Nano Banana) - RECOMMENDED
English (Conversational):
Create a professional portrait of a young woman in her late 20s with warm,
natural lighting. She should have confident, friendly expression...

中文版本:
生成一张专业人像照片，主角是一位20多岁的年轻女性，采用温暖自然的光线...

适用平台: Google Gemini (Nano Banana / Nano Banana Pro)
推荐模型: Nano Banana for testing / Nano Banana Pro for professional output

---

### Variation 2: Midjourney Style
professional portrait, young woman, late 20s, warm lighting,
confident expression, natural beauty...

[Plus detailed breakdowns, tips, and next steps]
```

## 🛠️ Technical Details

- **Skill Type**: Claude Code Agent Skill
- **Format**: SKILL.md with YAML frontmatter
- **Compatibility**: Claude Code CLI, skills.sh
- **Language**: English & Chinese

## 🤝 Contributing

Contributions are welcome! Feel free to:

- Report issues
- Suggest improvements
- Add new templates or keywords
- Expand platform support

## 📄 License

MIT License - Feel free to use and modify for your projects.

## 🔗 Links

- [Skills.sh Directory](https://skills.sh/)
- [Claude Code Documentation](https://code.claude.com/docs)
- [Google Gemini](https://gemini.google.com/)

## 📮 Author

**manzxiao**

If you find this skill useful, please ⭐ star the repository!

---

**Installation:**
```bash
npx skills add manzxiao/text-to-image-prompt-optimizer
```
