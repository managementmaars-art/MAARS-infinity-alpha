# daisyUI v5 — Special & Interactive Components

Overlays, interactive widgets, media components, mockups, and misc.

---

## dropdown

Opens a menu or any element when a button is clicked.

**Class names**
- component: `dropdown`
- part: `dropdown-content`
- placement: `dropdown-start`, `dropdown-center`, `dropdown-end`, `dropdown-top`, `dropdown-bottom`, `dropdown-left`, `dropdown-right`
- modifier: `dropdown-hover`, `dropdown-open`, `dropdown-close`

**Three implementation patterns — choose based on your framework:**

**1. `<details>`/`<summary>` (no JS, best for SSR/static):**
```html
<details class="dropdown">
  <summary class="btn">Open</summary>
  <ul class="dropdown-content menu bg-base-100 rounded-box z-1 w-52 p-2 shadow">
    <li><a>Item 1</a></li>
    <li><a>Item 2</a></li>
  </ul>
</details>
```

**2. Popover API (modern, native browser popover):**
```html
<button popovertarget="my-popover" style="anchor-name: --my-anchor" class="btn">Open</button>
<ul class="dropdown-content menu bg-base-100 rounded-box z-1 w-52 p-2 shadow"
  popover id="my-popover" style="position-anchor: --my-anchor">
  <li><a>Item 1</a></li>
</ul>
```

**3. CSS focus (fallback, works everywhere):**
```html
<div class="dropdown">
  <div tabindex="0" role="button" class="btn">Open</div>
  <ul tabindex="-1" class="dropdown-content menu bg-base-100 rounded-box z-1 w-52 p-2 shadow">
    <li><a>Item 1</a></li>
  </ul>
</div>
```

**Rules**
- Replace `{id}` and anchor names with unique values per dropdown.
- `dropdown-content` can contain any element, not just `<ul>`.
- Add `z-1` or `z-10` to `dropdown-content` to ensure it appears above other elements.

---

## collapse

Shows/hides content when clicked. Similar to accordion but independent.

**Class names**
- component: `collapse`
- parts: `collapse-title`, `collapse-content`
- modifier: `collapse-arrow`, `collapse-plus`, `collapse-open`, `collapse-close`

**Using `tabindex` (CSS-only, focus-based):**
```html
<div tabindex="0" class="collapse collapse-arrow bg-base-200">
  <div class="collapse-title font-semibold">Click to open</div>
  <div class="collapse-content">
    <p>Hidden content</p>
  </div>
</div>
```

**Using checkbox (toggle behavior):**
```html
<div class="collapse collapse-plus bg-base-200">
  <input type="checkbox" />
  <div class="collapse-title font-semibold">Click to toggle</div>
  <div class="collapse-content">
    <p>Hidden content</p>
  </div>
</div>
```

**Using `<details>`/`<summary>`:**
```html
<details class="collapse bg-base-200">
  <summary class="collapse-title font-semibold">Click to open</summary>
  <div class="collapse-content">
    <p>Hidden content</p>
  </div>
</details>
```

---

## accordion

Like collapse, but only one item can be open at a time (using radio inputs).

**Class names** — same as `collapse`

**Syntax**
```html
<div class="collapse collapse-arrow bg-base-200">
  <input type="radio" name="my-accordion" checked />
  <div class="collapse-title font-semibold">Item 1</div>
  <div class="collapse-content">Content for item 1</div>
</div>
<div class="collapse collapse-arrow bg-base-200">
  <input type="radio" name="my-accordion" />
  <div class="collapse-title font-semibold">Item 2</div>
  <div class="collapse-content">Content for item 2</div>
</div>
```

**Rules**
- All radio inputs with the same `name` form one accordion group.
- Use different `name` values for separate accordion groups on the same page.
- Add `checked` to the radio input you want open by default.

---

## avatar

Displays a user thumbnail image, with optional status indicator or group.

**Class names**
- component: `avatar`, `avatar-group`
- modifier: `avatar-online`, `avatar-offline`, `avatar-placeholder`

**Basic avatar:**
```html
<div class="avatar">
  <div class="w-12 rounded-full">
    <img src="{image-url}" alt="User" />
  </div>
</div>
```

**With online indicator:**
```html
<div class="avatar avatar-online">
  <div class="w-12 rounded-full">
    <img src="{image-url}" alt="User" />
  </div>
</div>
```

**Placeholder (initials):**
```html
<div class="avatar avatar-placeholder">
  <div class="bg-neutral text-neutral-content w-12 rounded-full">
    <span>AB</span>
  </div>
</div>
```

**Grouped avatars:**
```html
<div class="avatar-group -space-x-4">
  <div class="avatar"><div class="w-10"><img src="{url1}" /></div></div>
  <div class="avatar"><div class="w-10"><img src="{url2}" /></div></div>
  <div class="avatar avatar-placeholder"><div class="bg-neutral text-neutral-content w-10"><span>+3</span></div></div>
</div>
```

**Rules**
- Set size using `w-*` on the inner div (not the avatar wrapper).
- Apply `rounded-full`, `rounded-box`, or mask classes to shape the avatar.
- `avatar-placeholder` makes the avatar show text content instead of an image.

---

## carousel

Horizontally or vertically scrollable list of items.

**Class names**
- component: `carousel`
- part: `carousel-item`
- modifier: `carousel-start`, `carousel-center`, `carousel-end`
- direction: `carousel-horizontal` (default), `carousel-vertical`

**Syntax**
```html
<div class="carousel rounded-box">
  <div class="carousel-item">
    <img src="{image1}" alt="1" />
  </div>
  <div class="carousel-item">
    <img src="{image2}" alt="2" />
  </div>
</div>
```

**Full-width carousel with prev/next buttons:**
```html
<div class="carousel w-full">
  <div id="slide1" class="carousel-item relative w-full">
    <img src="{image1}" class="w-full" />
    <div class="absolute left-5 right-5 top-1/2 flex -translate-y-1/2 justify-between">
      <a href="#slide3" class="btn btn-circle">❮</a>
      <a href="#slide2" class="btn btn-circle">❯</a>
    </div>
  </div>
  <div id="slide2" class="carousel-item relative w-full">
    <img src="{image2}" class="w-full" />
    <div class="absolute left-5 right-5 top-1/2 flex -translate-y-1/2 justify-between">
      <a href="#slide1" class="btn btn-circle">❮</a>
      <a href="#slide3" class="btn btn-circle">❯</a>
    </div>
  </div>
</div>
```

**Rules**
- Add `w-full` to each `carousel-item` for a full-width slide carousel.
- The scroll snap modifier (`carousel-start/center/end`) controls which edge items snap to.

---

## indicator

Places a small element (badge, dot) on the corner of another element.

**Class names**
- component: `indicator`
- part: `indicator-item`
- placement: `indicator-start`, `indicator-center`, `indicator-end` (horizontal), `indicator-top`, `indicator-middle`, `indicator-bottom` (vertical)

**Syntax**
```html
<div class="indicator">
  <span class="indicator-item badge badge-primary">99+</span>
  <button class="btn">Inbox</button>
</div>
```

**Rules**
- Place all `indicator-item` elements **before** the main content inside the indicator wrapper.
- Default position is `indicator-end indicator-top` (top-right corner).

---

## swap

Toggles visibility between two elements via a checkbox or CSS class.

**Class names**
- component: `swap`
- parts: `swap-on`, `swap-off`, `swap-indeterminate`
- modifier: `swap-active`
- style: `swap-rotate`, `swap-flip`

**With checkbox (theme toggle example):**
```html
<label class="swap swap-rotate">
  <input type="checkbox" />
  <svg class="swap-on h-8 w-8">{sun-icon}</svg>
  <svg class="swap-off h-8 w-8">{moon-icon}</svg>
</label>
```

**With JS (controlled):**
```html
<div class="swap swap-flip" id="mySwap">
  <div class="swap-on">ON</div>
  <div class="swap-off">OFF</div>
</div>
<script>document.getElementById('mySwap').classList.toggle('swap-active')</script>
```

**Rules**
- Use only a hidden checkbox OR add/remove `swap-active` class via JS.
- `swap-rotate` applies a rotation animation. `swap-flip` applies a 3D flip.
- `swap-indeterminate` shows a third state when the checkbox is indeterminate.

---

## tooltip

Shows a hint message when hovering over an element.

**Class names**
- component: `tooltip`
- part: `tooltip-content`
- modifier: `tooltip-open`
- placement: `tooltip-top` (default), `tooltip-bottom`, `tooltip-left`, `tooltip-right`
- color: `tooltip-primary`, `tooltip-secondary`, `tooltip-accent`, `tooltip-info`, `tooltip-success`, `tooltip-warning`, `tooltip-error`

**Syntax**
```html
<div class="tooltip" data-tip="Tooltip text">
  <button class="btn">Hover me</button>
</div>
```

**Always visible:**
```html
<div class="tooltip tooltip-open tooltip-right" data-tip="Always visible">
  <button class="btn">Button</button>
</div>
```

**Rules**
- `data-tip` sets the tooltip text.
- `tooltip-open` forces the tooltip to always be visible (useful for demos).

---

## mask

Clips an element into a common shape.

**Class names**
- component: `mask`
- shapes: `mask-squircle`, `mask-heart`, `mask-hexagon`, `mask-hexagon-2`, `mask-decagon`, `mask-pentagon`, `mask-diamond`, `mask-square`, `mask-circle`, `mask-star`, `mask-star-2`, `mask-triangle`, `mask-triangle-2`, `mask-triangle-3`, `mask-triangle-4`
- modifier: `mask-half-1`, `mask-half-2`

**Syntax**
```html
<img class="mask mask-squircle w-24 h-24" src="{image-url}" />
<div class="mask mask-heart w-24 h-24 bg-primary"></div>
```

**Half mask (for rating stars):**
```html
<input type="radio" class="mask mask-star mask-half-1" />
<input type="radio" class="mask mask-star mask-half-2" />
```

---

## fab (Floating Action Button)

Persistent button in the bottom corner of the screen that can reveal additional speed-dial buttons.

**Class names**
- component: `fab`
- parts: `fab-close`, `fab-main-action`
- modifier: `fab-flower`

**Single FAB:**
```html
<div class="fab">
  <button class="btn btn-lg btn-circle btn-primary">{icon}</button>
</div>
```

**FAB with speed-dial (vertical):**
```html
<div class="fab">
  <div tabindex="0" role="button" class="btn btn-lg btn-circle btn-primary">{MainIcon}</div>
  <div>{Label1}<button class="btn btn-lg btn-circle">{Icon1}</button></div>
  <div>{Label2}<button class="btn btn-lg btn-circle">{Icon2}</button></div>
</div>
```

**FAB with flower (quarter-circle) layout:**
```html
<div class="fab fab-flower">
  <div tabindex="0" role="button" class="btn btn-lg btn-circle btn-primary">{MainIcon}</div>
  <button class="fab-main-action btn btn-circle btn-lg">{MainActionIcon}</button>
  <div class="tooltip tooltip-left" data-tip="Action 1">
    <button class="btn btn-lg btn-circle">{Icon1}</button>
  </div>
  <div class="tooltip tooltip-left" data-tip="Action 2">
    <button class="btn btn-lg btn-circle">{Icon2}</button>
  </div>
</div>
```

**Rules**
- The first child is the trigger button (always visible). Subsequent children are the speed-dial buttons.
- Use `tabindex="0" role="button"` on the trigger div for accessibility.
- `fab-close` replaces the trigger when the FAB is open.
- `fab-main-action` is a prominent primary action shown when FAB is open.
- `fab-flower` arranges speed-dial buttons in a quarter-circle fan pattern.

---

## hover-3d

Adds an interactive 3D tilt effect based on mouse position.

**Class names**
- component: `hover-3d`

**Syntax**
```html
<div class="hover-3d my-12 mx-2">
  <figure class="max-w-100 rounded-2xl">
    <img src="{image-url}" alt="3D card" />
  </figure>
  <!-- 8 empty divs for hover zones — all required -->
  <div></div>
  <div></div>
  <div></div>
  <div></div>
  <div></div>
  <div></div>
  <div></div>
  <div></div>
</div>
```

**Rules**
- Must have **exactly 9 direct children**: first child is the visible content, the other 8 are empty `<div>`s that define the 3D hover zones.
- Do NOT put interactive elements (buttons, links, inputs) inside `hover-3d` — they won't be reachable.
- If you want the whole card to be clickable, wrap the entire `hover-3d` in an `<a>` tag.
- `hover-3d` can be a `<div>` or an `<a>`.

---

## hover-gallery

Shows one image by default; reveals others as the user hovers horizontally.

**Class names**
- component: `hover-gallery`

**Syntax**
```html
<figure class="hover-gallery max-w-60">
  <img src="{image1}" alt="" />
  <img src="{image2}" alt="" />
  <img src="{image3}" alt="" />
  <img src="{image4}" alt="" />
</figure>
```

**Rules**
- Supports up to 10 images.
- Always set a `max-w-*` class — without it the gallery stretches to fill its container.
- All images must have the same dimensions for proper alignment.
- Can be a `<div>` or `<figure>`.

---

## text-rotate

Rotates through up to 6 lines of text in an infinite loop animation.

**Class names**
- component: `text-rotate`

**Basic syntax:**
```html
<span class="text-rotate">
  <span>
    <span>Option 1</span>
    <span>Option 2</span>
    <span>Option 3</span>
  </span>
</span>
```

**Hero heading style:**
```html
<span class="text-rotate text-7xl font-bold">
  <span class="justify-items-center">
    <span>DESIGN</span>
    <span>DEVELOP</span>
    <span>DEPLOY</span>
  </span>
</span>
```

**Rotating word in a sentence with colors:**
```html
<span>
  Built for
  <span class="text-rotate">
    <span>
      <span class="bg-primary text-primary-content px-2">Everyone</span>
      <span class="bg-secondary text-secondary-content px-2">Teams</span>
      <span class="bg-accent text-accent-content px-2">Makers</span>
    </span>
  </span>
</span>
```

**Rules**
- `text-rotate` must contain **one** wrapper span/div, which contains **2 to 6** child spans/divs.
- Default loop duration is 10000ms. Override with `duration-{ms}` (e.g. `duration-8000`).
- Animation pauses on hover.

---

## chat

Chat bubble layout for conversations.

**Class names**
- component: `chat`
- parts: `chat-image`, `chat-header`, `chat-footer`, `chat-bubble`
- placement: `chat-start`, `chat-end`
- color: `chat-bubble-neutral`, `chat-bubble-primary`, `chat-bubble-secondary`, `chat-bubble-accent`, `chat-bubble-info`, `chat-bubble-success`, `chat-bubble-warning`, `chat-bubble-error`

**Syntax**
```html
<div class="chat chat-start">
  <div class="chat-image avatar">
    <div class="w-10 rounded-full">
      <img src="{avatar}" />
    </div>
  </div>
  <div class="chat-header">Alice <time class="text-xs opacity-50">12:45</time></div>
  <div class="chat-bubble">Hello!</div>
  <div class="chat-footer opacity-50">Delivered</div>
</div>

<div class="chat chat-end">
  <div class="chat-bubble chat-bubble-primary">Hey, how are you?</div>
</div>
```

**Rules**
- `chat-start` and `chat-end` are required — they control which side the bubble appears on.
- `chat-image`, `chat-header`, and `chat-footer` are all optional.
- Use the `avatar` component inside `chat-image` for user thumbnails.

---

## theme-controller

Switches the page theme when an input is checked.

**Class names**
- component: `theme-controller`

**Checkbox (toggle between two themes):**
```html
<input type="checkbox" value="dark" class="theme-controller toggle" />
```

**Select dropdown (pick any theme):**
```html
<select class="select theme-controller">
  <option value="light">Light</option>
  <option value="dark">Dark</option>
  <option value="cupcake">Cupcake</option>
</select>
```

**Swap toggle (icon-based):**
```html
<label class="swap swap-rotate">
  <input type="checkbox" class="theme-controller" value="dark" />
  <svg class="swap-off h-6 w-6">{sun-icon}</svg>
  <svg class="swap-on h-6 w-6">{moon-icon}</svg>
</label>
```

**Rules**
- The `value` attribute must be a valid daisyUI theme name.
- When checked, the theme is applied to the entire page automatically.
- Works with checkbox, radio, or select inputs.

---

## mockup-browser

A box styled to look like a browser window.

**Class names**
- component: `mockup-browser`
- part: `mockup-browser-toolbar`

**Syntax**
```html
<div class="mockup-browser border-base-300 border">
  <div class="mockup-browser-toolbar">
    <div class="input">https://example.com</div>
  </div>
  <div class="flex justify-center px-4 py-16 border-t border-base-300">
    Page content here
  </div>
</div>
```

---

## mockup-code

A box styled to look like a terminal or code editor.

**Class names**
- component: `mockup-code`

**Syntax**
```html
<div class="mockup-code">
  <pre data-prefix="$"><code>npm install daisyui</code></pre>
  <pre data-prefix=">" class="text-success"><code>Done!</code></pre>
</div>
```

**Rules**
- `data-prefix="{char}"` sets the character shown before each line (e.g. `$`, `>`, line numbers).
- Highlight a line by adding a background color class to the `<pre>`.

---

## mockup-phone

A box styled to look like an iPhone.

**Class names**
- component: `mockup-phone`
- parts: `mockup-phone-camera`, `mockup-phone-display`

**Syntax**
```html
<div class="mockup-phone">
  <div class="mockup-phone-camera"></div>
  <div class="mockup-phone-display">
    <div class="artboard artboard-demo phone-1">
      App content here
    </div>
  </div>
</div>
```

---

## mockup-window

A box styled to look like an OS window.

**Class names**
- component: `mockup-window`

**Syntax**
```html
<div class="mockup-window border-base-300 border">
  <div class="flex justify-center border-t border-base-300 px-4 py-16">
    Window content here
  </div>
</div>
```

---

## calendar

Styles for third-party calendar libraries.

**Supported libraries and their class names:**
- **Cally** web component: `cally`
- **Pikaday**: `pika-single`
- **React Day Picker**: `react-day-picker`

**Cally:**
```html
<calendar-date class="cally">{CONTENT}</calendar-date>
```

**Pikaday:**
```html
<input type="text" class="input pika-single" />
```

**React Day Picker:**
```jsx
<DayPicker className="react-day-picker" />
```
