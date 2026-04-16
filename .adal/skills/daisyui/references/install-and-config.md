# daisyUI v5 — Installation & Configuration

## Requirements

- daisyUI 5 requires **Tailwind CSS v4**
- `tailwind.config.js` is **deprecated** in Tailwind v4 — do not create or use it

---

## Install (npm)

```bash
npm i -D daisyui@latest
```

Then in your CSS file:

```css
@import "tailwindcss";
@plugin "daisyui";
```

That's the minimal setup. No config file needed.

---

## Install (CDN)

If you can't use a build step:

```html
<link href="https://cdn.jsdelivr.net/npm/daisyui@5" rel="stylesheet" type="text/css" />
<script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
```

---

## Plugin Configuration

Pass options to the plugin directly in the CSS file:

### Minimal (no config)
```css
@plugin "daisyui";
```

### Light theme only
```css
@plugin "daisyui" {
  themes: light --default;
}
```

### Full config with all defaults shown
```css
@plugin "daisyui" {
  themes: light --default, dark --prefersdark;
  root: ":root";
  include: ;
  exclude: ;
  prefix: ;
  logs: true;
}
```

### Config options

| Option | Description |
|--------|-------------|
| `themes` | Comma-separated theme names. `--default` marks the default theme. `--prefersdark` marks the theme used when the OS is in dark mode. |
| `root` | CSS selector where theme variables are applied. Default: `":root"` |
| `include` | Comma-separated list of components to include (empty = all) |
| `exclude` | Comma-separated list of components to exclude |
| `prefix` | Prefix for all daisyUI class names (e.g. `daisy-` makes `daisy-btn`) |
| `logs` | Whether to show daisyUI logs in the console. Default: `true` |

### Example: All themes enabled, bumblebee as default, with prefix and excludes

```css
@plugin "daisyui" {
  themes: light, dark, cupcake, bumblebee --default, emerald, corporate, synthwave --prefersdark, retro, cyberpunk, valentine, halloween, garden, forest, aqua, lofi, pastel, fantasy, wireframe, black, luxury, dracula, cmyk, autumn, business, acid, lemonade, night, coffee, winter, dim, nord, sunset, caramellatte, abyss, silk;
  root: ":root";
  include: ;
  exclude: rootscrollgutter, checkbox;
  prefix: daisy-;
  logs: false;
}
```

---

## Switching Themes

Add `data-theme="THEME_NAME"` to the `<html>` element to activate a theme:

```html
<html data-theme="dark">
```

Available built-in themes: `light`, `dark`, `cupcake`, `bumblebee`, `emerald`, `corporate`, `synthwave`, `retro`, `cyberpunk`, `valentine`, `halloween`, `garden`, `forest`, `aqua`, `lofi`, `pastel`, `fantasy`, `wireframe`, `black`, `luxury`, `dracula`, `cmyk`, `autumn`, `business`, `acid`, `lemonade`, `night`, `coffee`, `winter`, `dim`, `nord`, `sunset`, `caramellatte`, `abyss`, `silk`

For creating a custom theme → see [`colors.md`](colors.md)
