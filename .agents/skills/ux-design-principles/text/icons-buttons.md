# Icons & Buttons

## Icons

### The Most Common Icon Mistake: Too Large

> "Most icons are generally too large."

Icons used alongside text are almost always oversized by default. The fix is simple and precise.

### Icon Sizing Rule

> "Get the line height of your font — in this case 24 pixels — and make the icons the same size."

```
Font size: 16px
Line height: 24px (1.5x)
Icon size: 24px  ← match to line-height, NOT font-size
```

This aligns the icon optically with the text baseline and cap height.

**Common sizes:**

| Context | Font Size | Line Height | Icon Size |
|---------|-----------|-------------|-----------|
| Body text | 16px | 24px | 24px |
| Small label | 14px | 20px | 20px |
| Caption | 12px | 16px | 16px |
| Large heading | 24px | 32px | 24-28px |

Then also tighten the gap between icon and text:
```css
/* Icon + text pair */
display: flex;
align-items: center;
gap: 6px;  /* tight gap, icons are already visually close to text */
```

---

## Buttons

### The Ghost Button

> "Sidebar links are actually just buttons without a background until you hover — often called ghost buttons."

A **ghost button** is a button with:
- Transparent background (default state)
- Visible border (or no border, relying only on text/icon)
- Background fill on hover

**When to use ghost buttons:**
- Secondary CTA alongside a primary filled button
- Navigation/sidebar items (look like links, act like buttons)
- Destructive actions that shouldn't look alarming at first glance

### Button Anatomy

```
[  Icon  Label  ]
    ↑ icon = line-height size
         ↑ padding: 2x height for width (horizontal), ~8-12px vertical
```

> "A good guideline for padding on these is to double the height for the width."

Example: If a button is 36px tall (8px top + 20px line-height + 8px bottom), horizontal padding should be ~36px on each side — making it approximately 2:1 width-to-height ratio.

### Button Variants

| Variant | Appearance | Use Case |
|---------|-----------|----------|
| **Primary** | Filled, brand color | Main CTA — one per page/section |
| **Secondary** | Outlined or filled neutral | Supporting actions |
| **Ghost** | No background, may have border | Tertiary actions, nav items |
| **Destructive** | Red fill or red text | Delete, remove, irreversible actions |
| **Link** | Underlined text only | Inline text actions |

### Buttons With and Without Icons

> "These can be done with or without icons, too."

- **Icon + label**: Common for actions (e.g., "⬆ Upload", "✓ Save")
- **Label only**: Clean, text-forward; works for most CTAs
- **Icon only**: Use only when icon meaning is universally understood; always add a tooltip

---

## Button States (see also Feedback & States)

Every button needs **at minimum 4 states**:

1. **Default** — resting appearance
2. **Hover** — cursor enters the element
3. **Active / Pressed** — during click/tap
4. **Disabled** — non-interactive, reduced opacity

Optional:
5. **Loading** — async action in progress (spinner replaces or appends to label)
6. **Success** — brief confirmation state (rare, for very important actions)

---

## Practical Rules

1. **Icon size = font line-height** (not font-size)
2. **Tighten icon-to-text gap** — 4-8px is usually right
3. **Button padding: horizontal ≈ 2x vertical**
4. **Ghost buttons are sidebar/nav defaults** — fill only on hover
5. **One primary button per section** — never two bright CTAs competing
6. **All icon-only buttons need tooltips**
7. **Destructive buttons** should be red — this is semantic, not decorative

---

## Engineering Vocabulary

| Term | Definition |
|------|-----------|
| **Ghost button** | Button with transparent background; border or text only until hover |
| **Primary CTA** | The main call-to-action; filled, high-contrast button |
| **Secondary CTA** | Supporting action; often outlined or ghost style |
| **Destructive action** | An irreversible action (delete, remove, leave); styled red |
| **Button state** | One of: default, hover, active/pressed, disabled, loading |
| **Icon-only button** | A button with only an icon; must have tooltip for accessibility |
| **Padding** | Internal space between button content and its edges |
| **Pill button** | Button with fully-rounded corners (border-radius: 9999px) |
| **Rounded button** | Button with moderate corner rounding (border-radius: 6-8px typical) |
| **Loading state** | Button showing a spinner while async operation is in progress |
| **Disabled state** | Non-interactive button; typically 40-50% opacity, no pointer events |
