---
name: ux-design-principles
description: Comprehensive UI/UX design principles covering affordances, visual hierarchy, grids, typography, color theory, dark mode, shadows, icons, buttons, feedback states, micro-interactions, and overlays. Use when designing UI components, reviewing design quality, building new screens, giving design feedback, writing design specs for AI coding assistants, or teaching product/engineering teams correct design vocabulary.
---

# UX Design Principles

> Source: "Every UI/UX Concept Explained in Under 10 Minutes" — Kole Jain (March 2026, 138K views)
> Figma files: https://www.kolejain.com/resources?scrollTo=every-ui-concept

## The One Rule That Governs Everything

> **"When a user does anything, there should be a response."**

Every interaction — click, hover, focus, error, load, success — must have a visible, purposeful response. This is the single most important principle in UI/UX design.

---

## Chapter Map

| Chapter | Core Concept | Quick Rule |
|---------|-------------|------------|
| [Affordances & Signifiers](text/affordances-signifiers.md) | UI communicates how it works through appearance | Good UI teaches itself |
| [Visual Hierarchy](text/visual-hierarchy.md) | Size, position, color control what users see first | Most important = largest + boldest + top |
| [Grids, Layouts & Spacing](text/grids-layouts-spacing.md) | Structure and breathing room | Whitespace > rigid grids |
| [Typography](text/typography.md) | Font choices, sizing, letter spacing | One sans-serif font, max 6 sizes |
| [Color Theory](text/color-theory.md) | Brand color + semantic colors + ramps | Color with purpose, not decoration |
| [Dark Mode](text/dark-mode.md) | Depth via lightness, not shadows | Lighter cards on dark backgrounds |
| [Shadows](text/shadows.md) | Elevation and depth on light mode | Low opacity, high blur |
| [Icons & Buttons](text/icons-buttons.md) | Sizing, padding, ghost buttons | Match icon size to line-height |
| [Feedback & States](text/feedback-states.md) | Every element needs multiple states | 4 states minimum per button |
| [Micro-interactions](text/micro-interactions.md) | Motion that confirms and delights | Confirm actions with animation |
| [Overlays](text/overlays.md) | Gradients and blur over images | Linear gradient then progressive blur |

---

## For Engineers: How to Talk to AI Assistants

Use precise vocabulary when describing UI to an AI coding assistant:

```
BAD:  "Make the button look better"
GOOD: "Add hover, active/pressed, and disabled states. Use ghost button style
       (transparent background, border only) as secondary CTA next to primary."

BAD:  "Fix the dark mode"
GOOD: "In dark mode: elevate card by lightening surface relative to background,
       remove box-shadow, lower border opacity, reduce chip saturation/brightness."

BAD:  "Add some animation"
GOOD: "Add micro-interaction on copy button: slide up a 'Copied!' chip on click
       that auto-dismisses after 1.5s. This confirms the action."

BAD:  "Fix the spacing"
GOOD: "Apply 4-point grid: all spacing values must be multiples of 4.
       32px between top-level sections, group related items with 8-16px."
```

See [text/engineering-rules.md](text/engineering-rules.md) for the full quick-reference.

---

## The 10 Design Laws

1. **Every interaction needs a response** — no silent state changes ever
2. **Contrast creates hierarchy** — big vs small, colorful vs gray, bold vs regular
3. **Whitespace is design** — let elements breathe; 32px between sections default
4. **Color carries meaning** — blue=trust, red=danger, yellow=warning, green=success
5. **One font is enough** — pick one sans-serif, vary by weight and size
6. **Match icon size to line-height** — body line-height 24px = icons 24px
7. **If the shadow is the first thing you notice, it's too strong**
8. **Images always improve hierarchy** — add color, aid scanning, draw the eye
9. **Dark mode = lighter surfaces for elevation**, not shadows
10. **Linear gradient beats solid overlay** — preserves image, readable text

---

## Deep Dives

- [Affordances & Signifiers](text/affordances-signifiers.md)
- [Visual Hierarchy](text/visual-hierarchy.md)
- [Grids, Layouts & Spacing](text/grids-layouts-spacing.md)
- [Typography](text/typography.md)
- [Color Theory](text/color-theory.md)
- [Dark Mode](text/dark-mode.md)
- [Shadows](text/shadows.md)
- [Icons & Buttons](text/icons-buttons.md)
- [Feedback & States](text/feedback-states.md)
- [Micro-interactions](text/micro-interactions.md)
- [Overlays](text/overlays.md)
- [Engineering Quick-Reference](text/engineering-rules.md)
- [Full Glossary](text/glossary.md)
