---
name: daisyui
description: >
  Build UI with daisyUI v5 and Tailwind CSS v4 — components, themes, colors, layout.
  Use this skill whenever working on HTML/JSX/TSX UI, adding or styling components,
  building pages or forms, customizing themes, or handling dark mode.
  Triggers on: "add a button", "make a modal", "style this form", "dark mode",
  "responsive layout", "daisyUI component", "card/navbar/table/badge/alert/etc.",
  building a page or UI from scratch. If someone is writing frontend HTML and has
  daisyUI installed, always use this skill.
---

# daisyUI v5

daisyUI 5 is a CSS component library for Tailwind CSS v4. It provides semantic class names for common UI patterns on top of Tailwind utilities.

- [Docs](https://daisyui.com) · [Components](https://daisyui.com/components/) · [Themes](https://daisyui.com/docs/themes/) · [v5 release notes](https://daisyui.com/docs/v5/)

## Quick Start

```css
/* In your CSS file */
@import "tailwindcss";
@plugin "daisyui";
```

```bash
npm i -D daisyui@latest
```

For setup details, CDN usage, or plugin config options → read [`references/install-and-config.md`](references/install-and-config.md)

---

## Core Rules

1. Apply styles by combining a **component class** with optional **part**, **modifier**, **color**, and **size** classes.
2. Extend with Tailwind utilities when daisyUI classes don't cover it (e.g. `btn px-10`).
3. If CSS specificity blocks a Tailwind override, append `!` (e.g. `btn bg-red-500!`). Use sparingly.
4. If no daisyUI component fits, build it purely with Tailwind utilities.
5. Layout with `flex`/`grid` should be responsive using Tailwind breakpoint prefixes.
6. Only use existing daisyUI class names or Tailwind utility classes — no arbitrary custom CSS unless unavoidable.
7. Prefer daisyUI **semantic colors** (e.g. `bg-primary`) over raw Tailwind colors (e.g. `bg-blue-500`) so themes work.
8. Raw Tailwind colors like `text-gray-800` can be unreadable on dark themes — always prefer `*-content` colors.
9. Do not add `bg-base-100 text-base-content` to `<body>` unless it's actually needed.
10. For placeholder images use `https://picsum.photos/{width}/{height}`.
11. Follow [Refactoring UI](https://www.refactoringui.com/) principles for design decisions.

---

## Color System

daisyUI adds semantic color names that automatically change per theme. Use these instead of raw Tailwind colors.

| Color | Purpose |
|-------|---------|
| `primary` | Main brand color |
| `secondary` | Optional secondary brand color |
| `accent` | Optional accent color |
| `neutral` | Unsaturated/dark UI elements |
| `base-100` | Page background (lightest) |
| `base-200` | Slightly darker surface (cards, sidebars) |
| `base-300` | Even darker surface (borders, inputs) |
| `base-content` | Text on base colors |
| `info` | Informational messages |
| `success` | Success/safe messages |
| `warning` | Warning/caution messages |
| `error` | Error/danger messages |

Each semantic color has a `-content` pair (e.g. `primary-content`) for text/icons placed on top of it.

Usage: `bg-primary text-primary-content`, `bg-base-200`, `text-error`, etc.

For custom themes and full color reference → read [`references/colors.md`](references/colors.md)

---

## Component Quick Reference

The most commonly used components. For full syntax, modifiers, and edge cases read the relevant reference file.

| Component | Element | Base class | Key modifiers |
|-----------|---------|------------|---------------|
| Button | `<button>` or `<a>` | `btn` | `btn-primary`, `btn-ghost`, `btn-outline`, `btn-sm/lg`, `btn-circle` |
| Input | `<input>` | `input` | `input-primary`, `input-error`, `input-sm/lg` |
| Select | `<select>` | `select` | `select-primary`, `select-sm/lg` |
| Textarea | `<textarea>` | `textarea` | `textarea-primary`, `textarea-sm/lg` |
| Checkbox | `<input type="checkbox">` | `checkbox` | `checkbox-primary`, `checkbox-sm/lg` |
| Toggle | `<input type="checkbox">` | `toggle` | `toggle-primary`, `toggle-sm/lg` |
| Card | `<div>` | `card` | `card-body`, `card-title`, `card-actions`, `card-side`, `card-sm/lg` |
| Navbar | `<div>` | `navbar` | `navbar-start`, `navbar-center`, `navbar-end` |
| Modal | `<dialog>` | `modal` | `modal-box`, `modal-backdrop`, `modal-top/bottom` |
| Alert | `<div role="alert">` | `alert` | `alert-info/success/warning/error`, `alert-soft`, `alert-outline` |
| Badge | `<span>` | `badge` | `badge-primary`, `badge-outline`, `badge-xs/lg` |
| Table | `<table>` | `table` | `table-zebra`, `table-pin-rows`, `table-sm/lg` |
| Tabs | `<div role="tablist">` | `tabs` | `tabs-box`, `tabs-lift`, `tab-active` |
| Menu | `<ul>` | `menu` | `menu-horizontal`, `menu-sm/lg` |
| Loading | `<span>` | `loading` | `loading-spinner/dots/ring`, `loading-sm/lg` |
| Tooltip | `<div>` | `tooltip` | `tooltip-top/bottom/left/right`, `tooltip-primary` |
| Avatar | `<div>` | `avatar` | `avatar-online/offline/placeholder`, `avatar-group` |
| Drawer | `<div>` | `drawer` | `drawer-toggle`, `drawer-content`, `drawer-side`, `lg:drawer-open` |

---

## Special Cases Worth Knowing

These are non-obvious behaviors that cause bugs if missed:

**`drawer`** — Every piece of page content (navbar, footer, main) must live inside `drawer-content`. Nothing goes outside the `drawer` wrapper. Use `lg:drawer-open` to auto-show the sidebar on large screens. Use `is-drawer-open:` / `is-drawer-close:` variant classes for conditional styling inside the sidebar.

**`modal`** — Prefer the native `<dialog>` element with `showModal()` JavaScript. The checkbox and anchor-link patterns are legacy. Use `<form method="dialog">` inside the modal to close it on submit.

**`tabs` with panel content** — Tab content panels only work when using `<input type="radio">` elements as tabs (not `<button>`). Radio inputs must share the same `name` attribute.

**`accordion`** — Uses radio inputs; all inputs with the same `name` form a group where only one can be open. Use a different `name` per accordion group on the same page.

**`dropdown`** — Three implementation patterns exist: `<details>`/`<summary>` (simplest, no JS), Popover API (requires unique `id` + `anchor-name`), or CSS focus (requires `tabindex="0"`). Choose based on your framework and browser targets.

**`hover-3d`** — Must have **exactly 9 direct children**: the first child is your content, the remaining 8 are empty `<div>`s that act as hover zones. Do not put interactive elements (buttons, links, inputs) inside it.

**`filter`** — Use a `<form>` tag as the wrapper when possible so the reset input (`type="reset"`) works natively. Fall back to `<div>` + `filter-reset` class only if a form element isn't viable. Each filter group needs a unique `name` on the radio inputs.

**`countdown`** and **`radial-progress`** — Both require a CSS variable (`--value`) to be set inline and kept in sync via JS. Always include `aria-*` attributes for accessibility.

**`theme-controller`** — A checked `<input class="theme-controller" value="dark">` anywhere on the page will switch the entire page to that theme. Useful for theme toggles.

---

## Reference Files

Read the appropriate file when you need full component syntax, all class names, or advanced examples:

| Need | Read |
|------|------|
| Installation, CDN, plugin config options | [`references/install-and-config.md`](references/install-and-config.md) |
| Custom themes, color vars, theme generator | [`references/colors.md`](references/colors.md) |
| Drawer, navbar, footer, hero, card, stack, divider, join | [`references/components-layout.md`](references/components-layout.md) |
| Input, select, textarea, checkbox, radio, toggle, range, file-input, rating, filter, fieldset, validator, label | [`references/components-forms.md`](references/components-forms.md) |
| Menu, tabs, breadcrumbs, pagination, link, steps, dock | [`references/components-navigation.md`](references/components-navigation.md) |
| Alert, badge, loading, modal, toast, progress, skeleton, status, countdown | [`references/components-feedback.md`](references/components-feedback.md) |
| Table, list, stat, timeline, kbd, diff | [`references/components-data-display.md`](references/components-data-display.md) |
| FAB, dropdown, collapse, accordion, avatar, carousel, indicator, swap, tooltip, mask, hover-3d, hover-gallery, text-rotate, mockups, calendar, chat, theme-controller | [`references/components-special.md`](references/components-special.md) |
