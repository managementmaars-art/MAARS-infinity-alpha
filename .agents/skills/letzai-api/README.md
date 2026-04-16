# LetzAI API Skill for Claude

A Claude skill that enables AI-powered image and video generation using the [LetzAI API](https://www.letz.ai).

## What is This?

This repository contains a Claude skill that teaches Claude how to effectively use the LetzAI API. When this skill is active, Claude can help you:

- **Generate AI images** using multiple base models (Nano Banana Pro, Flux2 Max, SeeDream)
- **Create AI videos** from images using VEO, Kling, and Wan models
- **Edit images** with context-aware AI editing
- **Upscale images** to higher resolutions
- **Use custom trained models** with the `@modelname` syntax

## Repository Structure

```
letzai-skill/
├── SKILL.md              # Main skill file (required by Claude)
├── api_reference.md      # Detailed API documentation
├── examples/
│   ├── image_generation.js   # JavaScript examples
│   ├── video_generation.py   # Python examples
│   └── polling_pattern.md    # Async polling guide
├── LICENSE.txt           # MIT License
└── README.md             # This file
```

## Quick Start

### Prerequisites

1. Get your API key at [letz.ai/subscription](https://letz.ai/subscription)
2. Set up authentication with Bearer token

### Installation

#### Skills CLI (Recommended)
Install with a single command using [skills.sh](https://skills.sh):

```bash
npx skills add Letz-AI/letzai-skill
```

#### Claude Code
Place this skill in your project's `.claude/skills/letzai-api/` directory.

#### Claude.ai
Go to **Settings → Features → Add custom skill** (requires Pro/Max/Team/Enterprise).

#### Claude API
Upload via the Skills API. See [Anthropic's Skills documentation](https://docs.anthropic.com) for details.

## Usage Examples

Once the skill is installed, you can ask Claude things like:

- *"Generate an image of a sunset over the ocean using LetzAI"*
- *"Create a video from this image with the camera slowly panning"*
- *"Edit this photo to change the background to a beach"*
- *"List my trained models and generate an image with @john_doe"*
- *"Upscale this image to 4K"*

## API Overview

| Endpoint | Purpose |
|----------|---------|
| `POST /images` | Generate images |
| `POST /videos` | Generate videos from images |
| `POST /image-edits` | Edit existing images |
| `POST /upscales` | Upscale images |
| `GET /models` | List custom trained models |

All generation is asynchronous - poll the `GET` endpoints until status is `"ready"`.

## Available Base Models

### Image Generation
| Model | API Value | Resolutions |
|-------|-----------|-------------|
| Nano Banana Pro | `gemini-3-pro-image-preview` | default, 2k, 4k |
| Flux2 Max | `flux2-max` | 1k, hd |
| SeeDream 4.5 | `seedream-4-5-251128` | 2k, 4k |

### Video Generation
| Model | API Value | Duration |
|-------|-----------|----------|
| Default | `default` | 2-6 sec |
| VEO 3.1 | `veo31` | 8 sec |
| Kling 2.6 | `kling26` | 5-10 sec |
| Wan 2.5 | `wan25` | 5-10 sec |

## Custom Trained Models

LetzAI supports custom trained models for persons, objects, and styles. Use them in prompts with the `@modelname` syntax:

```
@john_doe on the beach at sunset
A product photo featuring @my_product
Portrait in @vintage_style aesthetic
```

Train models via the [LetzAI web interface](https://letz.ai).

## Resources

- **LetzAI Website:** [www.letz.ai](https://www.letz.ai)
- **API Documentation:** [api.letz.ai/doc](https://api.letz.ai/doc)
- **Developer Docs:** [letz.ai/docs/api](https://letz.ai/docs/api)
- **Get API Key:** [letz.ai/subscription](https://letz.ai/subscription)

## License

This skill is released under the MIT License. See [LICENSE.txt](LICENSE.txt) for details.

## Disclaimer

This skill is provided to help integrate with the LetzAI API. Always test thoroughly in your own environment. API behavior and pricing may change - refer to the official LetzAI documentation for the most current information.
