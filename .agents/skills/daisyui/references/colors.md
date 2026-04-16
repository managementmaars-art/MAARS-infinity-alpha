# daisyUI v5 — Colors & Themes

## Semantic Color Names

daisyUI adds semantic color names to Tailwind's color system. These resolve to CSS variables that change automatically per theme — so using them ensures your UI works correctly in light, dark, and custom themes.

| Color | Purpose |
|-------|---------|
| `primary` | Main brand color |
| `primary-content` | Foreground color for use on `primary` backgrounds |
| `secondary` | Optional secondary brand color |
| `secondary-content` | Foreground for `secondary` backgrounds |
| `accent` | Optional accent color |
| `accent-content` | Foreground for `accent` backgrounds |
| `neutral` | Unsaturated/dark UI elements |
| `neutral-content` | Foreground for `neutral` backgrounds |
| `base-100` | Page background (lightest) |
| `base-200` | Slightly darker surface (cards, sidebars, navbars) |
| `base-300` | Even darker surface (borders, inputs, dividers) |
| `base-content` | Text/icon color for use on base backgrounds |
| `info` | Informational messages |
| `info-content` | Foreground for `info` backgrounds |
| `success` | Success/safe state |
| `success-content` | Foreground for `success` backgrounds |
| `warning` | Warning/caution state |
| `warning-content` | Foreground for `warning` backgrounds |
| `error` | Error/danger/destructive state |
| `error-content` | Foreground for `error` backgrounds |

Usage in Tailwind utilities:
```html
<div class="bg-primary text-primary-content">...</div>
<div class="bg-base-200 text-base-content">...</div>
<span class="text-error">Something went wrong</span>
```

---

## Color Rules

1. Always prefer daisyUI semantic colors over raw Tailwind colors (e.g. `bg-primary` not `bg-blue-500`) so the UI adapts to themes.
2. No need to use `dark:` prefix with daisyUI colors — they change automatically.
3. A raw Tailwind color (like `text-gray-800`) can be unreadable on dark themes where `bg-base-100` is a dark color.
4. Always pair `*-content` colors with their matching base color for readable contrast.
5. Use `base-*` colors for the majority of the page; use `primary` for the most important interactive elements.

---

## Custom Theme

To create a custom theme, add it to your CSS file alongside the daisyUI plugin:

```css
@import "tailwindcss";
@plugin "daisyui";
@plugin "daisyui/theme" {
  name: "mytheme";
  default: true;
  prefersdark: false;
  color-scheme: light;

  --color-base-100: oklch(98% 0.02 240);
  --color-base-200: oklch(95% 0.03 240);
  --color-base-300: oklch(92% 0.04 240);
  --color-base-content: oklch(20% 0.05 240);
  --color-primary: oklch(55% 0.3 240);
  --color-primary-content: oklch(98% 0.01 240);
  --color-secondary: oklch(70% 0.25 200);
  --color-secondary-content: oklch(98% 0.01 200);
  --color-accent: oklch(65% 0.25 160);
  --color-accent-content: oklch(98% 0.01 160);
  --color-neutral: oklch(50% 0.05 240);
  --color-neutral-content: oklch(98% 0.01 240);
  --color-info: oklch(70% 0.2 220);
  --color-info-content: oklch(98% 0.01 220);
  --color-success: oklch(65% 0.25 140);
  --color-success-content: oklch(98% 0.01 140);
  --color-warning: oklch(80% 0.25 80);
  --color-warning-content: oklch(20% 0.05 80);
  --color-error: oklch(65% 0.3 30);
  --color-error-content: oklch(98% 0.01 30);

  --radius-selector: 1rem;
  --radius-field: 0.25rem;
  --radius-box: 0.5rem;

  --size-selector: 0.25rem;
  --size-field: 0.25rem;

  --border: 1px;

  --depth: 1;
  --noise: 0;
}
```

### Custom theme rules

- All CSS variables listed above are required.
- Colors can be OKLCH, hex, or any valid CSS color format.
- `default: true` makes this theme active without needing `data-theme` on `<html>`.
- `prefersdark: true` makes this theme activate when the OS is in dark mode.
- `color-scheme` hints to the browser which native UI (scrollbars, inputs) to use (`light` or `dark`).
- `--radius-selector`: border radius for selectors (checkbox, toggle, badge). Suggested values: `0rem`, `0.25rem`, `0.5rem`, `1rem`, `2rem`.
- `--radius-field`: border radius for fields (button, input, select, tab).
- `--radius-box`: border radius for boxes (card, modal, alert).
- `--size-selector` / `--size-field`: base sizing unit. Default `0.25rem`. Slightly larger: `0.28125rem` or `0.3125rem`. Slightly smaller: `0.21875rem` or `0.1875rem`.
- `--border`: border width. Default `1px`. Thicker: `1.5px` or `2px`. Thinner: `0.5px`.
- `--depth`: `0` or `1` — adds a shadow and subtle 3D depth effect to components.
- `--noise`: `0` or `1` — adds a subtle noise/grain effect.

### Visual theme builder

Use the official theme generator: https://daisyui.com/theme-generator/
