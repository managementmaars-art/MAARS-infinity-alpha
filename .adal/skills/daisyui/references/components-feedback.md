# daisyUI v5 — Feedback Components

Alerts, notifications, loading states, progress, and status indicators.

---

## alert

Informs users about important events (info, success, warning, error).

**Class names**
- component: `alert`
- style: `alert-outline`, `alert-dash`, `alert-soft`
- color: `alert-info`, `alert-success`, `alert-warning`, `alert-error`
- direction: `alert-vertical`, `alert-horizontal`

**Syntax**
```html
<div role="alert" class="alert alert-info">
  <svg>{icon}</svg>
  <span>Info message here.</span>
</div>
```

**With title and action:**
```html
<div role="alert" class="alert alert-warning">
  <svg>{icon}</svg>
  <div>
    <h3 class="font-bold">Warning!</h3>
    <div class="text-sm">Something needs your attention.</div>
  </div>
  <button class="btn btn-sm">Review</button>
</div>
```

**Rules**
- Always add `role="alert"` for accessibility.
- Use `sm:alert-horizontal` for responsive stacking.
- `alert-soft` and `alert-outline` are style variants that change the background/border style.

---

## badge

Small inline label for status, count, or category.

**Class names**
- component: `badge`
- style: `badge-outline`, `badge-dash`, `badge-soft`, `badge-ghost`
- color: `badge-neutral`, `badge-primary`, `badge-secondary`, `badge-accent`, `badge-info`, `badge-success`, `badge-warning`, `badge-error`
- size: `badge-xs`, `badge-sm`, `badge-md`, `badge-lg`, `badge-xl`

**Syntax**
```html
<span class="badge badge-primary">New</span>
<span class="badge badge-outline badge-success badge-sm">Active</span>
```

**In a button:**
```html
<button class="btn">
  Inbox
  <span class="badge badge-secondary badge-sm">3</span>
</button>
```

**Empty badge (dot indicator):**
```html
<span class="badge badge-error badge-xs"></span>
```

---

## loading

Animated loading indicator.

**Class names**
- component: `loading`
- style: `loading-spinner`, `loading-dots`, `loading-ring`, `loading-ball`, `loading-bars`, `loading-infinity`
- size: `loading-xs`, `loading-sm`, `loading-md`, `loading-lg`, `loading-xl`

**Syntax**
```html
<span class="loading loading-spinner loading-md"></span>
```

**Inside a button:**
```html
<button class="btn" disabled>
  <span class="loading loading-spinner"></span>
  Loading
</button>
```

---

## modal

Dialog overlay for confirmations, forms, or detailed content.

**Class names**
- component: `modal`
- parts: `modal-box`, `modal-action`, `modal-backdrop`, `modal-toggle`
- modifier: `modal-open`
- placement: `modal-top`, `modal-middle`, `modal-bottom`, `modal-start`, `modal-end`

**Preferred: native `<dialog>` (no JS boilerplate):**
```html
<button onclick="my_modal.showModal()" class="btn">Open</button>

<dialog id="my_modal" class="modal">
  <div class="modal-box">
    <h3 class="text-lg font-bold">Title</h3>
    <p class="py-4">Modal content here.</p>
    <div class="modal-action">
      <form method="dialog">
        <button class="btn">Close</button>
      </form>
    </div>
  </div>
  <form method="dialog" class="modal-backdrop">
    <button>close</button>
  </form>
</dialog>
```

**Legacy: checkbox-controlled (avoid if possible):**
```html
<label for="my-modal" class="btn">Open</label>
<input type="checkbox" id="my-modal" class="modal-toggle" />
<div class="modal">
  <div class="modal-box">
    <p>Content</p>
    <div class="modal-action">
      <label for="my-modal" class="btn">Close</label>
    </div>
  </div>
  <label class="modal-backdrop" for="my-modal">Close</label>
</div>
```

**Rules**
- Use `<dialog>` + `showModal()` — it handles focus trapping, scroll locking, and `Escape` key natively.
- `<form method="dialog">` inside the modal closes it when submitted (without JS).
- The `modal-backdrop` form/label closes the modal when clicking outside the box.
- Use unique IDs for each modal on the page.

---

## toast

Stacks notification messages in a screen corner.

**Class names**
- component: `toast`
- placement: `toast-start`, `toast-center`, `toast-end`, `toast-top`, `toast-middle`, `toast-bottom`

**Syntax**
```html
<div class="toast toast-end toast-bottom">
  <div class="alert alert-success">
    <span>Saved successfully!</span>
  </div>
</div>
```

**Multiple toasts:**
```html
<div class="toast">
  <div class="alert alert-info"><span>New message.</span></div>
  <div class="alert alert-success"><span>Upload complete.</span></div>
</div>
```

**Rules**
- Default position is bottom-end.
- Toast is a positioning wrapper; put `alert` components inside for the actual content.
- Typically managed dynamically with JS (add/remove alert elements).

---

## progress

Linear progress bar.

**Class names**
- component: `progress`
- color: `progress-neutral`, `progress-primary`, `progress-secondary`, `progress-accent`, `progress-info`, `progress-success`, `progress-warning`, `progress-error`

**Syntax**
```html
<progress class="progress progress-primary w-56" value="70" max="100"></progress>
```

**Indeterminate (animated, no known value):**
```html
<progress class="progress w-56"></progress>
```

**Rules**
- Always set `value` and `max` for a determinate bar.
- Omit `value` for an indeterminate/animated bar.

---

## radial-progress

Circular progress ring.

**Class names**
- component: `radial-progress`

**Syntax**
```html
<div
  class="radial-progress"
  style="--value: 70;"
  aria-valuenow="70"
  aria-valuemin="0"
  aria-valuemax="100"
  role="progressbar"
>70%</div>
```

**Custom size and thickness:**
```html
<div class="radial-progress" style="--value: 50; --size: 8rem; --thickness: 4px;">50%</div>
```

**Rules**
- `--value` must be a number between 0 and 100. Update it via JS.
- Use a `<div>`, not `<progress>` — browsers can't render text inside `<progress>`.
- Always include `aria-valuenow`, `aria-valuemin`, `aria-valuemax`, and `role="progressbar"`.
- `--size` sets the diameter (default `5rem`). `--thickness` sets the ring width.

---

## skeleton

Placeholder shown while content is loading.

**Class names**
- component: `skeleton`
- modifier: `skeleton-text`

**Syntax**
```html
<!-- Block skeleton -->
<div class="skeleton h-32 w-32"></div>

<!-- Text skeleton -->
<div class="skeleton skeleton-text w-48"></div>

<!-- Card-shaped skeleton -->
<div class="flex w-52 flex-col gap-4">
  <div class="skeleton h-32 w-full"></div>
  <div class="skeleton h-4 w-28"></div>
  <div class="skeleton h-4 w-full"></div>
</div>
```

**Rules**
- Use `h-*` and `w-*` utilities to match the size of the real content.
- `skeleton-text` is for inline text placeholders.

---

## status

Very small dot indicator for online/offline/error states.

**Class names**
- component: `status`
- color: `status-neutral`, `status-primary`, `status-secondary`, `status-accent`, `status-info`, `status-success`, `status-warning`, `status-error`
- size: `status-xs`, `status-sm`, `status-md`, `status-lg`, `status-xl`

**Syntax**
```html
<span class="status status-success"></span>
<span class="status status-error status-lg"></span>
```

**Combined with text:**
```html
<div class="flex items-center gap-2">
  <span class="status status-success"></span>
  Online
</div>
```

**Rules**
- This component renders only a colored dot — no visible text content.
- Often combined with `avatar` (`avatar-online`, `avatar-offline`) for user presence indicators.

---

## countdown

Animated number counter that transitions smoothly between values (0–999).

**Class names**
- component: `countdown`

**Syntax**
```html
<span class="countdown font-mono text-4xl">
  <span style="--value: 59;" aria-live="polite" aria-label="59">59</span>
</span>
```

**Clock format:**
```html
<span class="countdown font-mono text-4xl">
  <span style="--value: 1;" aria-live="polite" aria-label="1">1</span>h
  <span style="--value: 30;" aria-live="polite" aria-label="30">30</span>m
  <span style="--value: 45;" aria-live="polite" aria-label="45">45</span>s
</span>
```

**Rules**
- The `--value` CSS variable drives the display. Update it via JS to animate.
- The text content inside the span should also match `--value` (for screen readers).
- Always add `aria-live="polite"` and `aria-label="{value}"` for accessibility.
- Value must be 0–999.
