# MARS Command — Captured Website

Source: http://localhost:3000

## How to Create a Video

Invoke the `/website-to-hyperframes` skill. It walks you through the full workflow: read data → create DESIGN.md → plan video → build compositions → lint/validate/preview.

If you don't have the skill installed, run: `npx skills add heygen-com/hyperframes`

## What's in This Capture

| File | Contents |
|------|----------|
| `screenshots/scroll-*.png` | Viewport screenshots covering the full page (1920x1080 each, 30% overlap). **View scroll-000.png FIRST** (hero section), then scan through the rest to understand the full page. |
| `extracted/tokens.json` | Design tokens: 20 colors, 2 fonts, 20 headings, 0 CTAs, 8 sections |
| `extracted/visible-text.txt` | All visible text content in DOM order — use exact strings, never paraphrase |
| `extracted/assets-catalog.json` | Every asset URL (images, fonts, videos, icons) with HTML context |
| `extracted/animations.json` | Animation catalog: 423 web animations, 0 scroll triggers, 1 canvases |
| `assets/svgs/` | Extracted inline SVGs (logos, icons, illustrations) |
| `assets/` | Downloaded images and font files — **Read every image file to see what it contains** |


| `extracted/shaders.json` | Captured WebGL shader source code (GLSL vertex + fragment shaders) |
| `extracted/asset-descriptions.md` | One-line description of every downloaded asset — read this first |

> **DESIGN.md does not exist yet.** It will be created when you run the `/website-to-hyperframes` workflow. Do not write compositions without it.

## Brand Summary

- **Colors**: #FFFFFF, #E2E8F0, #030712, #181C25, #000000, #4FD1C5, #F472B6, #A78BFA, #A1A1AA, #34D399
- **Fonts**: Inter, Outfit
- **Sections**: 8 page sections detected
- **Headings**: 20 headings extracted
- **CTAs**: 0 calls-to-action found

## Source Patterns Detected

- CSS custom properties used extensively — preserve design tokens for colors, spacing, and typography.
- Typography: Inter, Outfit. Match these exact font families and weights.
- 423 active Web Animations detected.
- 1 Canvas/WebGL elements detected.
- Marquee/ticker animation present — preserve continuous scrolling behavior.

## Example Prompts

Try asking:

- "Make me a 15-second social ad from this capture"
- "Create a 30-second product tour video"
- "Turn this into a vertical Instagram reel"
- "Build a feature announcement video highlighting the top 3 features"
