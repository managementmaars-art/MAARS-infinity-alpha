# daisyUI v5 — Navigation Components

Menus, tabs, links, breadcrumbs, and navigation bars.

---

## menu

Vertical or horizontal list of navigation links or buttons.

**Class names**
- component: `menu`
- parts: `menu-title`, `menu-dropdown`, `menu-dropdown-toggle`
- modifier: `menu-disabled`, `menu-active`, `menu-focus`, `menu-dropdown-show`
- size: `menu-xs`, `menu-sm`, `menu-md`, `menu-lg`, `menu-xl`
- direction: `menu-vertical` (default), `menu-horizontal`

**Vertical menu:**
```html
<ul class="menu bg-base-200 rounded-box w-56">
  <li><a>Item 1</a></li>
  <li><a>Item 2</a></li>
  <li>
    <details>
      <summary>Parent</summary>
      <ul>
        <li><a>Submenu item</a></li>
      </ul>
    </details>
  </li>
</ul>
```

**Horizontal menu (e.g. in navbar):**
```html
<ul class="menu menu-horizontal">
  <li><a>Home</a></li>
  <li><a>About</a></li>
</ul>
```

**With section titles:**
```html
<ul class="menu">
  <li class="menu-title">Settings</li>
  <li><a>Profile</a></li>
  <li><a>Security</a></li>
</ul>
```

**Rules**
- Use `<details>` + `<summary>` for collapsible submenus (no JS needed).
- Use `menu-dropdown` and `menu-dropdown-toggle` with JS to control submenus programmatically.
- Use `lg:menu-horizontal` for responsive layouts.
- `menu-active` on a `<li>` highlights the active item.
- `menu-disabled` on a `<li>` dims and disables it.

---

## tabs

Tabbed navigation to switch between content panels.

**Class names**
- component: `tabs`
- parts: `tab`, `tab-content`
- style: `tabs-box`, `tabs-border`, `tabs-lift`
- modifier: `tab-active`, `tab-disabled`
- placement: `tabs-top` (default), `tabs-bottom`

**Button tabs (no content panels):**
```html
<div role="tablist" class="tabs tabs-border">
  <button role="tab" class="tab tab-active">Tab 1</button>
  <button role="tab" class="tab">Tab 2</button>
  <button role="tab" class="tab">Tab 3</button>
</div>
```

**Radio tabs with content panels (no JS needed):**
```html
<div role="tablist" class="tabs tabs-lift">
  <input type="radio" name="my_tabs" class="tab" aria-label="Tab 1" checked />
  <div class="tab-content p-4">Content for tab 1</div>

  <input type="radio" name="my_tabs" class="tab" aria-label="Tab 2" />
  <div class="tab-content p-4">Content for tab 2</div>

  <input type="radio" name="my_tabs" class="tab" aria-label="Tab 3" />
  <div class="tab-content p-4">Content for tab 3</div>
</div>
```

**Rules**
- To show tab content panels without JavaScript, use `<input type="radio">` tabs — not `<button>`. Radio inputs must share the same `name`.
- Button tabs are for navigation (each tab links somewhere); radio tabs are for in-page content switching.
- `tabs-box` gives a pill/box background. `tabs-border` shows a bottom border. `tabs-lift` gives a raised card effect.

---

## breadcrumbs

Shows the user's current location in a hierarchy.

**Class names**
- component: `breadcrumbs`

**Syntax**
```html
<div class="breadcrumbs text-sm">
  <ul>
    <li><a>Home</a></li>
    <li><a>Products</a></li>
    <li>Current page</li>
  </ul>
</div>
```

**With icons:**
```html
<div class="breadcrumbs">
  <ul>
    <li>
      <a>
        <svg class="h-4 w-4">{icon}</svg>
        Home
      </a>
    </li>
    <li>About</li>
  </ul>
</div>
```

**Rules**
- The last `<li>` (current page) should not be an `<a>` link.
- If the list overflows its container, it scrolls horizontally.

---

## pagination

A row of page navigation buttons, built using `join`.

**Class names** (uses `join` component)
- component: `join`
- part: `join-item`

**Syntax**
```html
<div class="join">
  <button class="join-item btn">«</button>
  <button class="join-item btn btn-active">1</button>
  <button class="join-item btn">2</button>
  <button class="join-item btn">3</button>
  <button class="join-item btn">»</button>
</div>
```

**Rules**
- Use `btn-active` on the current page button.
- For large page counts, use a text input inside the join: `<input class="join-item btn btn-ghost w-16" type="number" value="4" />`.

---

## link

Adds underline styling to anchor tags.

**Class names**
- component: `link`
- style: `link-hover` (underline only on hover)
- color: `link-neutral`, `link-primary`, `link-secondary`, `link-accent`, `link-success`, `link-info`, `link-warning`, `link-error`

**Syntax**
```html
<a class="link">Default link</a>
<a class="link link-primary">Primary link</a>
<a class="link link-hover">Hover-only underline</a>
```

---

## steps

Displays a multi-step process or wizard progress.

**Class names**
- component: `steps`
- parts: `step`, `step-icon`
- color: `step-neutral`, `step-primary`, `step-secondary`, `step-accent`, `step-info`, `step-success`, `step-warning`, `step-error`
- direction: `steps-vertical`, `steps-horizontal` (default)

**Syntax**
```html
<ul class="steps">
  <li class="step step-primary">Register</li>
  <li class="step step-primary">Choose plan</li>
  <li class="step">Purchase</li>
  <li class="step">Receive product</li>
</ul>
```

**With custom icon and data-content:**
```html
<ul class="steps">
  <li class="step step-primary" data-content="✓">Done</li>
  <li class="step step-primary" data-content="★">Active</li>
  <li class="step">Pending</li>
</ul>
```

**Rules**
- Add a color class (e.g. `step-primary`) to mark steps as completed or active.
- `data-content="{value}"` overrides the step counter with custom text or icons.
- Use `step-icon` class for icon placement inside the step circle.

---

## dock

Bottom navigation bar (also called tab bar or bottom bar). Sticks to the bottom of the screen.

**Class names**
- component: `dock`
- part: `dock-label`
- modifier: `dock-active`
- size: `dock-xs`, `dock-sm`, `dock-md`, `dock-lg`, `dock-xl`

**Syntax**
```html
<div class="dock">
  <button class="dock-active">
    <svg>{icon}</svg>
    <span class="dock-label">Home</span>
  </button>
  <button>
    <svg>{icon}</svg>
    <span class="dock-label">Search</span>
  </button>
  <button>
    <svg>{icon}</svg>
    <span class="dock-label">Profile</span>
  </button>
</div>
```

**Rules**
- Add `dock-active` to the currently active button (not to the dock container).
- Add `<meta name="viewport" content="viewport-fit=cover">` for proper iOS safe-area behavior.
- `dock-label` is optional — dock works icon-only without it.
