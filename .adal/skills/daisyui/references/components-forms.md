# daisyUI v5 — Form Components

All form inputs, labels, validation, and grouping.

---

## fieldset

Groups related form elements with a legend title and optional description.

**Class names**
- component: `fieldset`, `label`
- part: `fieldset-legend`

**Syntax**
```html
<fieldset class="fieldset">
  <legend class="fieldset-legend">Account</legend>
  <label class="label">Username</label>
  <input type="text" class="input" placeholder="johndoe" />
  <p class="label">Must be unique</p>
</fieldset>
```

---

## label / floating-label

Associates a text label with an input. Two patterns: static label and floating label.

**Class names**
- component: `label`, `floating-label`

**Static label (label wraps input):**
```html
<label class="input">
  <span class="label">Email</span>
  <input type="email" placeholder="user@example.com" />
</label>
```

**Floating label (animates above input on focus):**
```html
<label class="floating-label">
  <input type="text" placeholder="Type here" class="input" />
  <span>Your name</span>
</label>
```

**Rules**
- The `input` class goes on the **wrapper** `<label>`, not on the `<input>` element itself.
- `floating-label` requires the `<input>` to come before the `<span>`.

---

## input

Single-line text input field.

**Class names**
- component: `input`
- style: `input-ghost`
- color: `input-neutral`, `input-primary`, `input-secondary`, `input-accent`, `input-info`, `input-success`, `input-warning`, `input-error`
- size: `input-xs`, `input-sm`, `input-md`, `input-lg`, `input-xl`

**Syntax**
```html
<input type="text" placeholder="Type here" class="input {MODIFIER}" />
```

**With label and icon:**
```html
<label class="input">
  <svg class="h-4 w-4 opacity-50">{icon}</svg>
  <input type="text" placeholder="Search" />
</label>
```

**Rules**
- Works with any `type`: `text`, `password`, `email`, `number`, etc.
- When wrapping with a `<label class="input">`, the `input` class goes on the label, not the inner `<input>`.

---

## select

Dropdown selection input.

**Class names**
- component: `select`
- style: `select-ghost`
- color: `select-neutral`, `select-primary`, `select-secondary`, `select-accent`, `select-info`, `select-success`, `select-warning`, `select-error`
- size: `select-xs`, `select-sm`, `select-md`, `select-lg`, `select-xl`

**Syntax**
```html
<select class="select {MODIFIER}">
  <option disabled selected>Pick one</option>
  <option>Option A</option>
  <option>Option B</option>
</select>
```

---

## textarea

Multi-line text input.

**Class names**
- component: `textarea`
- style: `textarea-ghost`
- color: `textarea-neutral`, `textarea-primary`, `textarea-secondary`, `textarea-accent`, `textarea-info`, `textarea-success`, `textarea-warning`, `textarea-error`
- size: `textarea-xs`, `textarea-sm`, `textarea-md`, `textarea-lg`, `textarea-xl`

**Syntax**
```html
<textarea class="textarea {MODIFIER}" placeholder="Bio"></textarea>
```

---

## checkbox

Boolean checkbox input.

**Class names**
- component: `checkbox`
- color: `checkbox-primary`, `checkbox-secondary`, `checkbox-accent`, `checkbox-neutral`, `checkbox-success`, `checkbox-warning`, `checkbox-info`, `checkbox-error`
- size: `checkbox-xs`, `checkbox-sm`, `checkbox-md`, `checkbox-lg`, `checkbox-xl`

**Syntax**
```html
<input type="checkbox" class="checkbox {MODIFIER}" />
```

**With label:**
```html
<label class="flex items-center gap-2">
  <input type="checkbox" class="checkbox checkbox-primary" />
  Accept terms
</label>
```

---

## radio

Radio button — select one from a group.

**Class names**
- component: `radio`
- color: `radio-neutral`, `radio-primary`, `radio-secondary`, `radio-accent`, `radio-success`, `radio-warning`, `radio-info`, `radio-error`
- size: `radio-xs`, `radio-sm`, `radio-md`, `radio-lg`, `radio-xl`

**Syntax**
```html
<input type="radio" name="my-group" class="radio {MODIFIER}" />
```

**Rules**
- All radios in a group share the same `name` attribute.
- Different groups on the same page must have different `name` values.

---

## toggle

Switch-style checkbox.

**Class names**
- component: `toggle`
- color: `toggle-primary`, `toggle-secondary`, `toggle-accent`, `toggle-neutral`, `toggle-success`, `toggle-warning`, `toggle-info`, `toggle-error`
- size: `toggle-xs`, `toggle-sm`, `toggle-md`, `toggle-lg`, `toggle-xl`

**Syntax**
```html
<input type="checkbox" class="toggle {MODIFIER}" />
```

---

## range

Slider for selecting a numeric value.

**Class names**
- component: `range`
- color: `range-neutral`, `range-primary`, `range-secondary`, `range-accent`, `range-success`, `range-warning`, `range-info`, `range-error`
- size: `range-xs`, `range-sm`, `range-md`, `range-lg`, `range-xl`

**Syntax**
```html
<input type="range" min="0" max="100" value="40" class="range {MODIFIER}" />
```

**Rules**
- Always set `min` and `max` attributes.

---

## file-input

File upload input.

**Class names**
- component: `file-input`
- style: `file-input-ghost`
- color: `file-input-neutral`, `file-input-primary`, `file-input-secondary`, `file-input-accent`, `file-input-info`, `file-input-success`, `file-input-warning`, `file-input-error`
- size: `file-input-xs`, `file-input-sm`, `file-input-md`, `file-input-lg`, `file-input-xl`

**Syntax**
```html
<input type="file" class="file-input {MODIFIER}" />
```

---

## rating

Star rating using radio inputs.

**Class names**
- component: `rating`
- modifier: `rating-half`, `rating-hidden`
- size: `rating-xs`, `rating-sm`, `rating-md`, `rating-lg`, `rating-xl`

**Syntax**
```html
<div class="rating">
  <input type="radio" name="rating-1" class="rating-hidden" />
  <input type="radio" name="rating-1" class="mask mask-star" />
  <input type="radio" name="rating-1" class="mask mask-star" />
  <input type="radio" name="rating-1" class="mask mask-star" />
  <input type="radio" name="rating-1" class="mask mask-star" />
  <input type="radio" name="rating-1" class="mask mask-star" />
</div>
```

**Rules**
- The first `rating-hidden` radio acts as a "clear" option so the user can deselect.
- Each rating group needs a unique `name`.
- Use `rating-half` to allow half-star ratings (requires two mask inputs per star).
- Use `mask-star-2` for a filled-star shape variant.

---

## filter

A group of radio buttons that filters content. Selecting one hides the rest; a reset button appears.

**Class names**
- component: `filter`
- part: `filter-reset`

**Using `<form>` (preferred — native reset works):**
```html
<form class="filter">
  <input class="btn btn-square" type="reset" value="×" />
  <input class="btn" type="radio" name="framework" aria-label="React" />
  <input class="btn" type="radio" name="framework" aria-label="Vue" />
  <input class="btn" type="radio" name="framework" aria-label="Svelte" />
</form>
```

**Using `<div>` (fallback when form element isn't viable):**
```html
<div class="filter">
  <input class="btn filter-reset" type="radio" name="framework" aria-label="×" />
  <input class="btn" type="radio" name="framework" aria-label="React" />
  <input class="btn" type="radio" name="framework" aria-label="Vue" />
</div>
```

**Rules**
- Each filter group needs a unique `name` on its radio inputs to avoid conflicts with other filters on the page.
- Use `<form>` when possible so the native `type="reset"` works without JS.
- In the `<div>` variant, add `filter-reset` to the reset radio to make it functional.

---

## validator

Applies error/success styles to form inputs based on HTML5 validation state.

**Class names**
- component: `validator`
- part: `validator-hint`

**Syntax**
```html
<input type="email" class="input validator" required />
<p class="validator-hint">Please enter a valid email address.</p>
```

**With pattern validation:**
```html
<input
  type="text"
  class="input validator"
  pattern="[A-Za-z]{3,}"
  required
  placeholder="Username"
/>
<p class="validator-hint">At least 3 letters, no numbers or symbols.</p>
```

**Rules**
- Use with `input`, `select`, or `textarea`.
- The `validator-hint` paragraph appears below the input and changes color based on validity.
- Validation state is driven by native HTML5 constraint validation (`:valid`, `:invalid` pseudo-classes).
- Works with attributes: `required`, `pattern`, `minlength`, `maxlength`, `min`, `max`, `type`.
