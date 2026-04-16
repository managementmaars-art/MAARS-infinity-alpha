# Color Theory

## Start Simple: One Primary Color

> "Colors are difficult and everyone has their own tastes, but I'm a big fan of starting with one primary color. Generally, this is your brand color."

### Building From One Color

1. **Primary color** — your brand's main color
2. **Lightened version** — good for backgrounds, tints, hover states
3. **Darkened version** — good for text on light backgrounds, pressed states
4. **Full color ramp** — what large companies use for chips, states, charts, all UI

---

## Color Ramps

A color ramp is a spectrum of tints and shades of a single hue, typically numbered:

| Step | Usage |
|------|-------|
| 50 | Lightest tint — backgrounds, subtle fills |
| 100 | Light tint — hover backgrounds |
| 200 | Light — disabled states, borders |
| 300 | Medium-light — secondary elements |
| 400 | Medium |
| 500 | **Base / primary color** |
| 600 | Darker — hover states on primary button |
| 700 | Dark — pressed states |
| 800 | Darker text on light backgrounds |
| 900 | Darkest — heading text in dark contexts |

> "Both good ways to incorporate subtle color and make an otherwise drab design look much more interesting. And with all of that, we're already halfway to a color ramp."

---

## Semantic Colors

> "Make sure you use color for purpose, not just for decoration."

Semantic colors are colors that carry **universal meaning**. They provide signifiers to the user without needing text labels.

| Color | Meaning | When to Use |
|-------|---------|-------------|
| **Blue** | Trust, information, primary action | Links, primary buttons, focus states, info alerts |
| **Red** | Danger, error, urgency | Error messages, destructive actions, delete buttons |
| **Yellow / Amber** | Warning, caution | Warning messages, near-limit states |
| **Green** | Success, confirmation, health | Success toasts, completed states, "new" chips |
| **Orange** | Caution (between yellow and red) | Moderate warnings |
| **Purple** | Premium, creative | Pro tier badges, AI-related features |
| **Gray** | Neutral, disabled, secondary | Labels, placeholders, inactive elements |

### Real-World Semantic Examples

```
Announcement bar    → accent/brand color to grab attention
Input focus state   → blue border highlight
Error input         → red border + red helper text
New item chip       → green background chip
Destructive button  → red text or red background
Warning banner      → yellow background + amber icon
```

---

## The "Let Color Find You" Principle

> "I also think it's important as a beginner to let the color find you."

Don't force color everywhere. Add it where it naturally serves a purpose:
- An announcement bar that needs to grab attention
- A focus state on an input
- A green "New" chip on a link
- A highlighted price or CTA

---

## Color Application Hierarchy

1. **Neutral base** — most of the UI is grayscale or near-neutral
2. **Brand accent** — appears on the single most important action (primary CTA)
3. **Semantic colors** — appear on states (error, success, warning)
4. **Decorative color** — images and illustrations only

> If you're adding color "just because", it's decoration, not design.

---

## Practical Rules

1. **One primary color + its ramp** is all you need to start
2. **Lightened versions** of brand color make great subtle backgrounds
3. **Semantic colors are non-negotiable** — don't use red for success or green for errors
4. **Color draws the eye** — use it sparingly on the things that matter most
5. **More color ≠ better design** — a near-monochrome design with one accent is often stunning
6. **Blue for primary actions** is a global convention — don't fight it without good reason

---

## Engineering Vocabulary

| Term | Definition |
|------|-----------|
| **Primary color** | The main brand/identity color; used on the most important CTAs |
| **Secondary color** | Supporting color used for accents and secondary actions |
| **Color ramp / scale** | A range of tints and shades (50-900) of a single hue |
| **Semantic color** | A color that carries meaning by convention (red=error, green=success) |
| **Tint** | A color mixed with white — lighter variant |
| **Shade** | A color mixed with black — darker variant |
| **Tone** | A color mixed with gray |
| **Saturation** | Intensity/purity of a color; high=vivid, low=muted |
| **Brightness/Value** | How light or dark a color is |
| **Accent color** | A distinct color used sparingly to draw attention |
| **Neutral** | Black, white, and grays — the invisible foundation |
| **HEX / HSL / RGB** | Color encoding formats; HSL is most intuitive for designers |
| **Color contrast ratio** | WCAG accessibility standard for text legibility (min 4.5:1 for body) |
