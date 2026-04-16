# Dark Mode

## The Core Challenge

Dark mode is not "invert light mode." It requires a completely different approach to depth, elevation, and contrast.

> "Designing in dark mode presents some pretty interesting challenges for us."

---

## Key Problem: Shadows Don't Work in Dark Mode

In light mode, shadows create depth by simulating light hitting a raised surface.
In dark mode, shadows disappear against a dark background — they're invisible.

**Solution:** Use **surface lightness** for elevation instead of shadows.

---

## Dark Mode Elevation System

| Layer | Background | Usage |
|-------|-----------|-------|
| App background | Darkest (e.g., #0A0A0A) | Page background |
| Card surface | Slightly lighter (e.g., #1A1A1A) | Cards, panels |
| Elevated panel | Lighter still (e.g., #242424) | Modals, dropdowns, popovers |
| Input / interactive | Slightly lighter (e.g., #2A2A2A) | Form fields |
| Tooltip / highest | Near-white or contrast surface | Tooltips |

> "To create depth, we need to have a lighter card than the background."

**Rule: Higher elevation = lighter surface.** This is the opposite of shadows (which add darkness below).

---

## Border Contrast in Dark Mode

> "This card is using a light border, which creates a bit too much contrast, so we'll lower that down."

In light mode, borders can be 1px solid #E5E5E5. In dark mode, the same approach creates harsh contrast.

**Fix:** Lower border opacity significantly:
```css
/* Light mode */
border: 1px solid rgba(0, 0, 0, 0.1);

/* Dark mode */
border: 1px solid rgba(255, 255, 255, 0.08);
```

---

## Chip / Badge Saturation in Dark Mode

> "This chip is also far too bright, so we can dim down the saturation and brightness and flip that for the text to create some hierarchy."

Vivid chips from light mode look garish in dark mode.

**Fix:** Reduce saturation and brightness of chip background, then *increase* text brightness/saturation to compensate.

```css
/* Light mode chip */
background: #22C55E;  /* vivid green */
color: #ffffff;

/* Dark mode chip */
background: #166534;  /* dark, muted green */
color: #86EFAC;       /* bright, saturated green text */
```

---

## Color Palette in Dark Mode

> "There's also a ton of flexibility for deep purples, reds, or greens — not just navy blue or gray."

Dark mode doesn't have to be gray. It opens up richness:
- Deep forest greens
- Rich navy blues
- Dark burgundy
- Deep indigo
- Charcoal with warm undertones

Avoid: flat, lifeless grays with no temperature or personality.

---

## Dark Mode Checklist

- [ ] Cards are visibly lighter than the page background
- [ ] Border opacity is low (not harsh white lines)
- [ ] No box-shadow on cards (use surface elevation instead)
- [ ] Chips/badges have reduced saturation on background, higher on text
- [ ] Text contrast ratios still pass WCAG (check with a contrast checker)
- [ ] Focus states are still visible (may need to adjust ring color)
- [ ] Primary button has sufficient contrast against dark card backgrounds
- [ ] Images don't need modification (they're already correct)

---

## Practical Rules

1. **Elevation = lighter surface** — not shadows
2. **Lower border opacity** — thin, subtle separators
3. **Chip backgrounds: muted** — flip text to be the vivid element
4. **Don't copy light mode colors** — darken, mute, adjust
5. **Explore rich dark palettes** — beyond gray
6. **Test contrast ratios** — WCAG AA minimum 4.5:1 for body text

---

## Engineering Vocabulary

| Term | Definition |
|------|-----------|
| **Dark mode** | UI variant designed for low-light environments with dark background surfaces |
| **Surface elevation** | In dark mode, using lighter background to indicate higher z-level |
| **Elevation** | The perceived depth/height of an element in the visual stack |
| **Color scheme** | CSS media feature: prefers-color-scheme (light/dark) |
| **Saturation** | Color intensity; high = vivid, low = washed out |
| **WCAG contrast ratio** | Accessibility standard for text-background contrast |
| **Foreground / background** | Text color vs surface color — must have sufficient contrast |
| **Muted color** | A color with reduced saturation — softer, less loud |
| **Dark surface** | A dark-colored background layer in dark mode |
