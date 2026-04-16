# Grids, Layouts & Spacing

## The Misconception

> "Some people have this misconception that all of your content needs to align to a 12-column grid and be exactly 8 pixels apart — but these are just guidelines."

Grids are tools, not laws. Many great designs don't follow a 12-column grid at all — especially custom landing pages.

---

## When Grids Actually Help

| Use Case | Grid Benefit |
|----------|-------------|
| Galleries, blogs, repeating content | Alignment + consistency |
| Responsive layouts | Guidelines for breakpoints: 12 col desktop, 8 col tablet, 4 col mobile |
| Data-heavy dashboards | Visual order in dense information |
| Marketing pages | Usually not needed — custom layout is fine |

**Rule:** Use grids for highly structured content with repeating patterns. Don't force them on unique, expressive layouts.

---

## The 4-Point Grid System

> "Everything is a multiple — not because it inherently looks better, but because you can always split things in half, which creates consistency throughout a design."

All spacing values are multiples of 4:

| Value | Use |
|-------|-----|
| 4px | Minimum gap (icon to label) |
| 8px | Tight spacing within a component |
| 12px | Inner padding (compact components) |
| 16px | Default inner padding |
| 24px | Related group spacing |
| 32px | Section spacing (between distinct groups) |
| 48px | Large section breaks |
| 64px+ | Hero/banner separation |

**Why multiples of 4?** Because 4 divides evenly into 8, 16, 32, 64 — you can always halve or double for responsive scaling.

---

## Whitespace Is the Most Important Spacing Concept

> "Much more important than using excessive grids and layouts is whitespace — letting things breathe."

### Landing Page Section Anatomy

```
[Announcement bar]         ← optional, top
                           ← 32px gap
[Hero headline]            ← large font, ~48-72px, tight line-height (110-120%)
[Subheadline]              ← 32px gap
[CTA button(s)]            ← 32px gap
                           ← 32px between every distinct item
```

**Grouping rule:** Related elements (headline + subheadline) get less gap between them (8-16px). Unrelated elements (button group → next section) get 32px+. This *grouping via proximity* is itself a form of visual hierarchy.

---

## Line Height

Line height affects readability and the "feel" of typography:

| Text Type | Recommended Line Height |
|-----------|------------------------|
| Large display/hero text | 110–120% (tight — looks "pro") |
| Body text | 140–160% |
| Dense UI labels | 100–130% |

> "If you tighten up the letter spacing by about -2 to -3% and drop the line height to about 110 to 120%, it instantly makes any larger text look super pro."

---

## Practical Layout Rules

1. **32px between every top-level section** is a reliable default
2. **Group related elements** with smaller internal spacing (8-16px)
3. **All spacing values must be multiples of 4** for consistency
4. **Don't over-engineer with 12-column grids** unless content is repeating
5. **For repeating content** (galleries, cards, lists) — grids prevent visual chaos
6. **Line height of large text** should be tight (110-120%), not the default 150%

---

## Engineering Vocabulary

| Term | Definition |
|------|-----------|
| **4-point grid** | Design system where all spacing is a multiple of 4px |
| **8-point grid** | Stricter variant — all spacing multiples of 8px |
| **Whitespace (negative space)** | Empty space around and between elements; essential for breathing room |
| **Gutter** | The space between columns in a grid |
| **Column grid** | Vertical divisions used to align content horizontally |
| **Responsive breakpoints** | Pixel widths where layout adapts (desktop/tablet/mobile) |
| **Proximity** | Grouping elements visually by placing them close together |
| **Line height (leading)** | Vertical space between lines of text |
| **Letter spacing (tracking)** | Horizontal spacing between characters |
| **Content width (max-width)** | The maximum width of content before it stops growing |
