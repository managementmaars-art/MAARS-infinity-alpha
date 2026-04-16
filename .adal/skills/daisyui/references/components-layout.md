# daisyUI v5 — Layout Components

Components for page structure and spatial arrangement.

---

## card

Groups and displays related content with optional image, body, and actions.

**Class names**
- component: `card`
- parts: `card-body`, `card-title`, `card-actions`
- style: `card-border`, `card-dash`
- modifier: `card-side`, `image-full`
- size: `card-xs`, `card-sm`, `card-md`, `card-lg`, `card-xl`

**Syntax**
```html
<div class="card {MODIFIER}">
  <figure><img src="{image-url}" alt="{alt}" /></figure>
  <div class="card-body">
    <h2 class="card-title">{title}</h2>
    <p>{content}</p>
    <div class="card-actions">{buttons}</div>
  </div>
</div>
```

**Rules**
- `<figure>` and `card-body` are both optional.
- `card-side` lays the image and body horizontally. Use `sm:card-side` for responsive behavior.
- If the image comes after `card-body`, it appears at the bottom.
- `image-full` makes the image fill the entire card and overlays text on top.

---

## navbar

Navigation bar anchored to the top of the page.

**Class names**
- component: `navbar`
- parts: `navbar-start`, `navbar-center`, `navbar-end`

**Syntax**
```html
<div class="navbar bg-base-200">
  <div class="navbar-start">{logo or menu button}</div>
  <div class="navbar-center">{title or links}</div>
  <div class="navbar-end">{actions}</div>
</div>
```

**Rules**
- Use `bg-base-200` for the navbar background.
- Each section (`navbar-start/center/end`) can contain anything: text, buttons, menus, dropdowns.
- When using with `drawer`, the navbar goes inside `drawer-content`.

---

## drawer

Full-page layout with a toggleable sidebar. Controls visibility via a hidden checkbox.

**Class names**
- component: `drawer`
- parts: `drawer-toggle`, `drawer-content`, `drawer-side`, `drawer-overlay`
- placement: `drawer-end` (sidebar on right)
- modifier: `drawer-open` (always visible)
- variants: `is-drawer-open:`, `is-drawer-close:` (for conditional styles inside sidebar)

**Syntax**
```html
<div class="drawer">
  <input id="my-drawer" type="checkbox" class="drawer-toggle" />
  <div class="drawer-content">
    <!-- ALL page content here: navbar, main, footer -->
    <label for="my-drawer" class="btn drawer-button">Open</label>
  </div>
  <div class="drawer-side">
    <label for="my-drawer" aria-label="close sidebar" class="drawer-overlay"></label>
    <ul class="menu bg-base-200 min-h-full w-80 p-4">
      <li><button>Item 1</button></li>
      <li><button>Item 2</button></li>
    </ul>
  </div>
</div>
```

**Always-visible on large screens, toggleable on small:**
```html
<div class="drawer lg:drawer-open">
  <input id="my-drawer" type="checkbox" class="drawer-toggle" />
  <div class="drawer-content flex flex-col">
    <label for="my-drawer" class="btn drawer-button lg:hidden">Open</label>
    <!-- page content -->
  </div>
  <div class="drawer-side">
    <label for="my-drawer" aria-label="close sidebar" class="drawer-overlay"></label>
    <ul class="menu bg-base-200 min-h-full w-80 p-4">
      <li><button>Item</button></li>
    </ul>
  </div>
</div>
```

**Icon-only sidebar that expands on open:**
```html
<div class="drawer lg:drawer-open">
  <input id="my-drawer" type="checkbox" class="drawer-toggle" />
  <div class="drawer-content"><!-- page content --></div>
  <div class="drawer-side is-drawer-close:overflow-visible">
    <label for="my-drawer" aria-label="close sidebar" class="drawer-overlay"></label>
    <div class="is-drawer-close:w-14 is-drawer-open:w-64 bg-base-200 flex flex-col min-h-full">
      <ul class="menu w-full grow">
        <li>
          <button class="is-drawer-close:tooltip is-drawer-close:tooltip-right" data-tip="Home">
            🏠
            <span class="is-drawer-close:hidden">Home</span>
          </button>
        </li>
      </ul>
      <div class="m-2">
        <label for="my-drawer" class="btn btn-ghost btn-circle drawer-button is-drawer-open:rotate-y-180">↔️</label>
      </div>
    </div>
  </div>
</div>
```

**Rules**
- **All page content must be inside `drawer-content`** — navbar, main content, footer, everything.
- `drawer-toggle` is a hidden checkbox. Use `<label for="{id}">` to toggle it.
- Use `drawer-end` to put the sidebar on the right.
- `lg:drawer-open` keeps the sidebar open on large screens without JS.
- `is-drawer-open:` and `is-drawer-close:` are variant classes for styling elements conditionally based on drawer state.

---

## hero

Large display section with centered content, often used for landing pages.

**Class names**
- component: `hero`
- parts: `hero-content`, `hero-overlay`

**Syntax**
```html
<div class="hero min-h-screen bg-base-200">
  <div class="hero-content text-center">
    <div class="max-w-md">
      <h1 class="text-5xl font-bold">Hello</h1>
      <p class="py-6">Description text</p>
      <button class="btn btn-primary">Get Started</button>
    </div>
  </div>
</div>
```

**With background image and overlay:**
```html
<div class="hero min-h-screen" style="background-image: url('{image-url}');">
  <div class="hero-overlay"></div>
  <div class="hero-content text-center text-neutral-content">
    <h1 class="text-5xl font-bold">Title</h1>
  </div>
</div>
```

**Rules**
- `hero-content` centers its children.
- `hero-overlay` overlays a semi-transparent color over the background image.
- Can contain a `<figure>` alongside the text content for side-by-side layout.

---

## footer

Page footer with logo, copyright, and grouped links.

**Class names**
- component: `footer`
- parts: `footer-title`
- placement: `footer-center`
- direction: `footer-horizontal`, `footer-vertical`

**Syntax**
```html
<footer class="footer bg-base-200 p-10">
  <nav>
    <h6 class="footer-title">Services</h6>
    <a class="link link-hover">Branding</a>
    <a class="link link-hover">Design</a>
  </nav>
  <nav>
    <h6 class="footer-title">Company</h6>
    <a class="link link-hover">About us</a>
    <a class="link link-hover">Contact</a>
  </nav>
</footer>
```

**Rules**
- Use `sm:footer-horizontal` to make footer responsive.
- `footer-center` centers all content.
- Suggested background: `bg-base-200` or `bg-neutral text-neutral-content`.

---

## divider

Separates content horizontally or vertically, with optional label text.

**Class names**
- component: `divider`
- color: `divider-neutral`, `divider-primary`, `divider-secondary`, `divider-accent`, `divider-success`, `divider-warning`, `divider-info`, `divider-error`
- direction: `divider-vertical`, `divider-horizontal`
- placement: `divider-start`, `divider-end`

**Syntax**
```html
<div class="divider">OR</div>
<div class="divider divider-primary">Label</div>
<div class="divider divider-vertical"></div>
```

**Rules**
- Omit text content for a plain line.
- `divider-start` / `divider-end` shifts the label to the left or right.

---

## stack

Visually layers elements on top of each other (like a deck of cards).

**Class names**
- component: `stack`
- modifier: `stack-top`, `stack-bottom`, `stack-start`, `stack-end`

**Syntax**
```html
<div class="stack">
  <div class="card bg-base-200">Bottom card</div>
  <div class="card bg-base-300">Middle card</div>
  <div class="card bg-primary text-primary-content">Top card</div>
</div>
```

**Rules**
- Apply `w-*` and `h-*` to the stack container to size all children consistently.
- The last child in the DOM appears on top visually.
- Modifier classes adjust alignment of the stacked items.

---

## join

Groups multiple elements (buttons, inputs, etc.) into a connected row or column, applying border radius only to the outer edges.

**Class names**
- component: `join`
- part: `join-item`
- direction: `join-vertical`, `join-horizontal`

**Syntax**
```html
<div class="join">
  <button class="btn join-item">A</button>
  <button class="btn join-item">B</button>
  <button class="btn join-item">C</button>
</div>
```

**With input:**
```html
<div class="join">
  <input class="input join-item" placeholder="Search" />
  <button class="btn join-item">Go</button>
</div>
```

**Rules**
- Any direct child automatically gets joined. Add `join-item` explicitly if the element isn't a direct child.
- Use `join-vertical` for a vertical stack.
- Use `lg:join-horizontal` for responsive layouts.
