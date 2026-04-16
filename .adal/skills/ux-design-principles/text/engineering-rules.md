# Engineering Quick-Reference: Design Rules

Use this when writing design specs, prompting AI coding assistants, or doing code reviews with a design lens.

---

## The Master Rule

> **Every interaction needs a response. No silent state changes. Ever.**

---

## Button Checklist

```
Every button must have:
[ ] Default state
[ ] Hover state (cursor: pointer, color shift)
[ ] Active / pressed state (darker, optional translateY(1px))
[ ] Disabled state (opacity: 0.5, cursor: not-allowed, pointer-events: none)
[ ] Loading state (if triggers async operation)
```

---

## Input Checklist

```
Every input must have:
[ ] Default border (neutral gray)
[ ] Focus ring (blue border + subtle glow)
[ ] Error state (red border + red helper text below)
[ ] Disabled state (muted background, no hover/focus)
[ ] Warning state (amber/yellow — for optional issues)
```

---

## Spacing Rules

| Rule | Value |
|------|-------|
| All spacing is a multiple of | 4px |
| Default section gap | 32px |
| Related item gap | 8-16px |
| Button horizontal padding | ~2x button height |
| Icon-to-text gap | 4-8px |
| Min clickable target size | 44x44px |

---

## Typography Rules

| Rule | Value |
|------|-------|
| Max different font sizes per page | 6 |
| Recommended typeface | One sans-serif only |
| Hero / large headline letter-spacing | -2% to -3% |
| Hero / large headline line-height | 110-120% |
| Body text line-height | 140-160% |
| Dashboard max font size | 24px |

---

## Color Rules

| Rule |
|------|
| Blue = trust / primary actions |
| Red = danger / error / destructive |
| Yellow/Amber = warning |
| Green = success / positive |
| All spacing = 4pt grid multiples |
| One primary brand color + ramp |
| Color should have purpose, not just decoration |

---

## Icon Rules

| Rule | Value |
|------|-------|
| Icon size | = line-height of adjacent text (not font-size) |
| Body text (16px / 24px LH) | 24px icons |
| Small label (14px / 20px LH) | 20px icons |
| Icon-only buttons | Must have tooltip |

---

## Shadow Rules

| Context | Shadow style |
|---------|-------------|
| Cards (light mode) | Low opacity (8-12%), high blur (8-16px) |
| Dropdowns / popovers | Medium (10-12% opacity, 12-20px blur) |
| Modals | Stronger (12-20% opacity, 24-40px blur) |
| Dark mode | NO shadows — use lighter surfaces instead |
| If shadow is first thing you notice | It's too strong — reduce |

---

## Dark Mode Rules

| Rule |
|------|
| Elevation = lighter surface (not shadows) |
| Border opacity: ~8% white (not full white) |
| Chip backgrounds: muted / dark |
| Chip text: bright / saturated (flip from background) |
| No box-shadow on cards |

---

## Overlay Rules

| Use case | Solution |
|---------|----------|
| Text on image | Linear gradient overlay |
| Premium / editorial | Gradient + progressive blur |
| Full opaque overlay | Avoid — kills the image |
| Modal backdrop | Dark scrim OR blur, not both |

---

## Micro-interaction Rules

| Rule |
|------|
| Every confirmed action needs motion feedback |
| Enter animations: ease-out |
| Exit animations: ease-in |
| Duration: 150-350ms for most interactions |
| Always add prefers-reduced-motion fallback |
| Copy button → "Copied!" chip slide-up |
| Delete → item slide + fade out |

---

## How to Spec UI for AI Assistants

### Pattern: Adding States
```
"Add hover, active/pressed, and disabled states to this button.
Hover: slightly darker bg (#1D4ED8 if primary is #2563EB).
Active: even darker, translateY(1px).
Disabled: opacity-50, cursor-not-allowed, pointer-events-none."
```

### Pattern: Input Validation
```
"Add focus state (blue ring: 0 0 0 3px rgba(37,99,235,0.15)),
error state (red border + red text below input with error message),
warning state (amber border + warning text)."
```

### Pattern: Micro-interaction
```
"On button click, slide up a '...' chip from below the button.
Animate: opacity 0→1, translateY(8px→0), 200ms ease-out.
Auto-dismiss after 1.5s with reverse animation."
```

### Pattern: Dark Mode Card
```
"In dark mode: remove box-shadow, lighten card background by
~6-8% relative to page background, reduce border opacity to ~8%."
```

### Pattern: Gradient Overlay
```
"Add a linear-gradient overlay: transparent at 0%, transparent at 40%,
rgba(0,0,0,0.6) at 70%, rgba(0,0,0,0.85) at 100%. 
Text positioned absolute bottom-left over the overlay."
```
