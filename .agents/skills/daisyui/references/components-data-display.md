# daisyUI v5 — Data Display Components

Tables, lists, statistics, timelines, and structured data.

---

## table

Displays tabular data with optional styling enhancements.

**Class names**
- component: `table`
- modifier: `table-zebra`, `table-pin-rows`, `table-pin-cols`
- size: `table-xs`, `table-sm`, `table-md`, `table-lg`, `table-xl`

**Syntax**
```html
<div class="overflow-x-auto">
  <table class="table">
    <thead>
      <tr>
        <th></th>
        <th>Name</th>
        <th>Role</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <th>1</th>
        <td>Alice</td>
        <td>Admin</td>
      </tr>
      <tr>
        <th>2</th>
        <td>Bob</td>
        <td>User</td>
      </tr>
    </tbody>
  </table>
</div>
```

**Highlighted row on hover:**
```html
<tr class="hover">...</tr>
```

**Rules**
- Always wrap in `<div class="overflow-x-auto">` to allow horizontal scrolling on small screens.
- `table-zebra` adds alternating row background colors.
- `table-pin-rows` keeps `<thead>` and `<tfoot>` visible when scrolling vertically.
- `table-pin-cols` keeps the first and last columns visible when scrolling horizontally.

---

## list

Vertical layout for displaying rows of structured information (like a settings list or contact list).

**Class names**
- component: `list`, `list-row`
- modifier: `list-col-wrap`, `list-col-grow`

**Syntax**
```html
<ul class="list bg-base-100 rounded-box shadow">
  <li class="list-row">
    <div><img class="size-10 rounded-box" src="{avatar}" /></div>
    <div>
      <p class="font-medium">John Doe</p>
      <p class="text-sm text-base-content/50">Engineer</p>
    </div>
    <button class="btn btn-ghost btn-sm">Follow</button>
  </li>
</ul>
```

**Rules**
- By default, the **second** child of `list-row` fills the remaining space (like a flex-grow item).
- Use `list-col-grow` on a different child to make it fill the space instead.
- Use `list-col-wrap` to force an item to wrap to the next line.

---

## stat

Displays a single metric with title, value, and optional description.

**Class names**
- component: `stats`
- parts: `stat`, `stat-title`, `stat-value`, `stat-desc`, `stat-figure`, `stat-actions`
- direction: `stats-horizontal` (default), `stats-vertical`

**Syntax**
```html
<div class="stats shadow">
  <div class="stat">
    <div class="stat-title">Total Users</div>
    <div class="stat-value">31K</div>
    <div class="stat-desc">↑ 21% more than last month</div>
  </div>
</div>
```

**With icon figure:**
```html
<div class="stats shadow">
  <div class="stat">
    <div class="stat-figure text-primary">
      <svg class="inline-block h-8 w-8 stroke-current">{icon}</svg>
    </div>
    <div class="stat-title">Downloads</div>
    <div class="stat-value text-primary">31K</div>
    <div class="stat-desc">From January 1st to February 1st</div>
  </div>
  <div class="stat">
    <div class="stat-figure text-secondary">
      <svg class="inline-block h-8 w-8 stroke-current">{icon}</svg>
    </div>
    <div class="stat-title">Revenue</div>
    <div class="stat-value text-secondary">$4,200</div>
    <div class="stat-desc">↓ 90 (12%)</div>
  </div>
</div>
```

**Rules**
- `stats` is the container; `stat` is each individual statistic block.
- `stat-figure` floats an icon to the right of the stat.
- `stat-actions` can hold buttons below the stat description.
- Use `stats-vertical` to stack stats vertically instead of side by side.

---

## timeline

Shows a list of events in chronological order.

**Class names**
- component: `timeline`
- parts: `timeline-start`, `timeline-middle`, `timeline-end`
- modifier: `timeline-snap-icon`, `timeline-box`, `timeline-compact`
- direction: `timeline-vertical` (default), `timeline-horizontal`

**Syntax**
```html
<ul class="timeline">
  <li>
    <div class="timeline-start">Jan 2020</div>
    <div class="timeline-middle">
      <svg class="h-5 w-5 text-primary">{checkmark-icon}</svg>
    </div>
    <div class="timeline-end timeline-box">First milestone</div>
    <hr class="bg-primary" />
  </li>
  <li>
    <hr class="bg-primary" />
    <div class="timeline-start">Mar 2021</div>
    <div class="timeline-middle">
      <svg class="h-5 w-5 text-primary">{checkmark-icon}</svg>
    </div>
    <div class="timeline-end timeline-box">Second milestone</div>
    <hr />
  </li>
  <li>
    <hr />
    <div class="timeline-start">Now</div>
    <div class="timeline-middle">{icon}</div>
    <div class="timeline-end timeline-box">Current state</div>
  </li>
</ul>
```

**Rules**
- Default is vertical layout. Add `timeline-horizontal` for a horizontal timeline.
- Use `<hr>` between `<li>` elements to draw the connecting line. Color it with background utilities (e.g. `bg-primary`) to mark completed steps.
- `timeline-box` adds a card-style box around the content.
- `timeline-snap-icon` snaps the icon to the start edge instead of the middle.
- `timeline-compact` forces all content to one side.

---

## kbd

Displays keyboard shortcuts or key names.

**Class names**
- component: `kbd`
- size: `kbd-xs`, `kbd-sm`, `kbd-md`, `kbd-lg`, `kbd-xl`

**Syntax**
```html
<kbd class="kbd">Ctrl</kbd> + <kbd class="kbd">C</kbd>
```

**In a table:**
```html
<table class="table">
  <tr>
    <td><kbd class="kbd kbd-sm">⌘</kbd> + <kbd class="kbd kbd-sm">C</kbd></td>
    <td>Copy</td>
  </tr>
</table>
```

---

## diff

Side-by-side comparison of two items with a draggable resizer.

**Class names**
- component: `diff`
- parts: `diff-item-1`, `diff-item-2`, `diff-resizer`

**Syntax**
```html
<figure class="diff aspect-16/9">
  <div class="diff-item-1">
    <img src="{before-image}" alt="before" />
  </div>
  <div class="diff-item-2">
    <img src="{after-image}" alt="after" />
  </div>
  <div class="diff-resizer"></div>
</figure>
```

**Text comparison:**
```html
<figure class="diff aspect-16/9">
  <div class="diff-item-1">
    <div class="bg-base-200 flex h-full items-center justify-center text-8xl font-black">BEFORE</div>
  </div>
  <div class="diff-item-2">
    <div class="bg-primary flex h-full items-center justify-center text-8xl font-black text-primary-content">AFTER</div>
  </div>
  <div class="diff-resizer"></div>
</figure>
```

**Rules**
- Add an aspect ratio class (e.g. `aspect-16/9`) to maintain proportions.
- The `diff-resizer` handles user-draggable comparison.
- Both items should be the same dimensions for proper alignment.
