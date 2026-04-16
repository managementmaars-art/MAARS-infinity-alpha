---
name: imagegen-gpt
description: Use when the user asks to generate a new image (banner, post, mockup, illustration) or to turn a textual brief into a production-ready image prompt and render it via OpenAI gpt-image-1. Do not use for video. Do not use for simple text-only brainstorming.
---

## Goal
Generate a single high-quality image using OpenAI `gpt-image-1` and save it into `./assets/generated/`.

## Inputs to collect (ask only if missing)
- Purpose: (e.g., Instagram feed 1:1, story 9:16, banner 16:9, icon 1:1)
- Style: (photorealistic, flat illustration, 3D, minimal, etc.)
- Text on image? If yes: exact text and language (warn about small text legibility)
- Brand constraints (colors, logos, layout rules)
- Output filename (default: `image.png`)

## Output
- Generate the image file in `./assets/generated/<filename>.png`
- Print the saved path and a short summary of the prompt used.

## Execution steps
1. Draft a final image prompt (concise, unambiguous).
2. Run `python3 .agents/skills/imagegen-gpt/scripts/generate_image.py --prompt "<PROMPT>" --out "./assets/generated/<filename>.png"`.
3. If the command fails due to missing API key, instruct the user to set `OPENAI_API_KEY` and re-run.
4. If the user requests multiple variants, run multiple times with different `--seed` values and distinct filenames.
