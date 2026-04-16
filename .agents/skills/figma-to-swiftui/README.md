# Figma to SwiftUI Skill

Translate Figma designs into production-ready SwiftUI code with pixel-perfect accuracy using the [Figma MCP Server](https://developers.figma.com/docs/figma-mcp-server/). Built for the [Agent Skills open format](https://agentskills.io/home).

This skill provides a structured 8-step workflow that guides AI agents through fetching design context, downloading assets, and implementing native SwiftUI views — without blindly porting React + Tailwind output.

## Who this is for

* iOS developers who receive designs in Figma and want to speed up implementation
* Teams using Figma Dev Mode who want consistent design-to-code translation
* Anyone who wants their AI coding tool to produce native SwiftUI instead of web-style layouts

## What this Skill Does

### Structured Workflow

Guides the agent through 8 steps: parse Figma URL → fetch design context → capture screenshot → fetch tokens → download assets → implement in SwiftUI → validate (on user request) → register Code Connect mappings.

### Native SwiftUI Translation

Complete mapping tables for:
* **Layout** — Figma Auto Layout → VStack/HStack/ZStack, padding, spacing, sizing modes
* **Typography** — font family, weight, size, line height, letter spacing
* **Colors** — hex, gradients, opacity, dark mode, design tokens
* **Components** — buttons, inputs, lists, navigation, sheets, cards
* **Effects** — shadows, blur, corner radius, borders, masks, Liquid Glass (iOS 26+)
* **Animations** — prototype transitions → SwiftUI animations, matched geometry, Lottie integration

### Smart Asset Handling

* Prefers SF Symbols over custom icons (with per-asset confirmation for cross-platform projects)
* Downloads from MCP localhost URLs directly — no placeholders
* Raster images to Asset Catalog with @1x/@2x/@3x variants
* Vector assets as SVG with Preserve Vector Data

### Project-Aware

* Checks project dependencies before implementing — uses Kingfisher, Lottie, SnapKit, or whatever the project already has instead of introducing native alternatives
* Maps Figma design tokens to the project's existing color/typography/spacing system
* Skips system-provided elements (keyboard, status bar, home indicator, system alerts, etc.)
* Respects platform conventions: safe areas, Dynamic Type, accessibility

### Not Opinionated About Architecture

This skill handles visual translation only. It does not enforce MV, MVVM, or any other pattern — that's the job of your architecture skill.

## How to Use This Skill

### Quick Install

```bash
npx skills add https://github.com/daetojemax/figma-to-swiftui-skill --skill figma-to-swiftui
```

### Manual Install

1. **Clone** this repository
2. **Install or symlink** the `figma-to-swiftui/` folder following your tool's skills installation docs
3. **Ensure Figma MCP server is connected** — see `references/figma-mcp-setup.md` for troubleshooting

Then use in your AI agent:

> Use the figma-to-swiftui skill and implement this design: https://www.figma.com/design/abc123/MyApp?node-id=10-5&m=dev

#### Where to Save Skills

* **Codex:** [Where to save skills](https://developers.openai.com/codex/skills/#where-to-save-skills)
* **Claude Code:** [Using Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview#using-skills)
* **Cursor:** [Enabling Skills](https://cursor.com/docs/context/skills#enabling-skills)

## Prerequisites

* **Figma MCP server** connected and authenticated (see `references/figma-mcp-setup.md`)
* **Figma URL** with a node ID — supports `/design/` and legacy `/file/` formats, with or without `www.`, `&m=dev`, etc.
* **Xcode project** with an established SwiftUI codebase (recommended)

## Skill Structure

```
figma-to-swiftui/
  SKILL.md                                — Main workflow (8 steps)
  references/
    layout-translation.md                 — Auto Layout → Stacks, sizing, scroll, common patterns
    responsive-layout.md                  — Size classes, adaptive layouts, multi-device designs
    design-token-mapping.md               — Figma variables → Color/Font/Spacing tokens
    component-variants.md                 — Figma variants → SwiftUI styles and enums
    asset-handling.md                      — SF Symbols, xcassets, SVG, remote images
    figma-mcp-setup.md                    — MCP connection, troubleshooting
```

## Key Design Decisions

**MCP output is a spec, not code.** Figma MCP returns React + Tailwind by default. This skill treats it as a design specification and builds native SwiftUI from the extracted properties — it never ports web code.

**Ask, don't assume.** The skill prompts the user for decisions it cannot safely make: validation method, SF Symbols for cross-platform projects, image loading library when none is found, whether an element is system-provided or custom.

**System elements are not implemented.** Keyboards, status bars, navigation back buttons, and other iOS-provided UI that designers include for mockup context are skipped automatically.

**Project dependencies take priority.** Before writing any code, the agent checks what libraries the project already uses and follows established patterns.

## Contributing

Contributions are welcome! If you have improvements to the translation tables, additional component mappings, or better reference material — please open a PR.

When contributing:
* Keep SKILL.md focused on the workflow — detailed mappings go in `references/`
* Test changes against real Figma designs with the MCP server connected
* Follow the [Agent Skills open format](https://agentskills.io/home) structure