# Feedback & States

## The Governing Principle

> "A good rule of design is: when a user does anything, there should be a response."

> "Every interaction needs a response."

This is the single most important UX principle in the video. It is absolute: **no silent interactions**.

---

## Button States (Minimum 4)

> "Every button needs at least four states: default, hovered, active or pressed, and disabled."

| State | When | Visual Treatment |
|-------|------|-----------------|
| **Default** | Resting | Base appearance — the button as designed |
| **Hover** | Cursor enters | Slightly darker/lighter background, cursor changes to pointer |
| **Active / Pressed** | During click/tap | Noticeably darker, may shift slightly (translateY 1px) |
| **Disabled** | Not actionable | Reduced opacity (40-50%), cursor: not-allowed, no hover effect |
| **Loading** *(optional)* | Async action pending | Spinner icon; label may change to "Saving...", non-interactive |

### CSS Example: Primary Button States
```css
.btn {
  background: #2563EB;         /* Default */
  cursor: pointer;
}
.btn:hover {
  background: #1D4ED8;         /* Hover — darker */
}
.btn:active {
  background: #1E40AF;         /* Pressed — even darker */
  transform: translateY(1px);  /* Subtle press-down feel */
}
.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  pointer-events: none;
}
```

---

## Input States (Even More Critical)

> "Inputs are even more critical."

Inputs communicate a lot of state: active, valid, invalid, warning. Missing any of these breaks the user's mental model.

| State | When | Visual Treatment |
|-------|------|-----------------|
| **Default** | Resting | Neutral border (gray) |
| **Focus** | User clicked in / tabbed to | **Blue ring/border** — field is active and receiving input |
| **Filled** | Has value | May show a clear button or character count |
| **Error** | Validation failed | **Red border** + red helper text below explaining what's wrong |
| **Warning** | Optional issue | **Yellow/amber border** + warning message |
| **Disabled** | Not editable | Muted background, no focus state |
| **Read-only** | Display only | Similar to filled but clearly non-interactive |
| **Success** | Validation passed | **Green border** (optional, used sparingly) |

> "You'll need a focus state when the user clicks in, error states with red borders and messages when something's wrong, and sometimes even warning states for optional issues."

### CSS Example: Input States
```css
.input {
  border: 1px solid #D1D5DB;   /* Default */
  outline: none;
}
.input:focus {
  border-color: #2563EB;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15);  /* Focus ring */
}
.input.error {
  border-color: #EF4444;
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}
.input.warning {
  border-color: #F59E0B;
}
```

---

## Global State Feedback

> "This applies everywhere."

Beyond buttons and inputs, *every* interactive and data-bearing element needs states:

| Element | States Needed |
|---------|--------------|
| **Navigation item** | Default, hover, active (current page) |
| **Checkbox** | Unchecked, checked, indeterminate, disabled |
| **Toggle/Switch** | Off, on, disabled |
| **Tab** | Inactive, active, hover |
| **Card** | Default, hover (if clickable), selected |
| **Data list** | Loading, empty state, error state, populated |
| **Form section** | Default, loading, success, error |
| **Dropdown** | Closed, open, option hovered, option selected |

---

## Loading States

> "Loading spinners when data is fetching."

| Pattern | Use Case |
|---------|----------|
| **Spinner** | Single element or button loading |
| **Skeleton screen** | Page/section loading — show layout with gray shimmer placeholders |
| **Progress bar** | File upload, multi-step process with known completion |
| **Pulse animation** | Background polling (subtle, non-intrusive) |

**Rule:** Show a loading state immediately on action — never let the UI appear frozen.

---

## Success States

> "Success messages when an action completes."

| Pattern | Use Case |
|---------|----------|
| **Toast notification** | Global success (saved, sent, deleted) |
| **Inline success message** | Form submission |
| **Check icon swap** | Button temporarily shows checkmark after action |
| **State text change** | "Save" → "Saved!" → back to "Save" after 2s |

---

## Empty States

Not mentioned explicitly in the video, but critical:

| Situation | What to Show |
|-----------|-------------|
| No search results | Friendly message + suggestion to change query |
| No data yet | Illustration + CTA to create first item |
| Error loading | Error message + retry button |
| No notifications | "You're all caught up!" message |

---

## Practical Rules

1. **Every button needs 4 states** — no exceptions
2. **Inputs need focus state** — it's critical for accessibility and usability
3. **Error state = red border + text message** (not just border alone)
4. **Loading spinners appear immediately** — never let UI appear frozen
5. **Success states are often temporary** — auto-dismiss after 2-3s
6. **Disabled ≠ hidden** — disabled elements should be visible but clearly non-interactive
7. **Never remove a button during loading** — replace label with spinner instead

---

## Engineering Vocabulary

| Term | Definition |
|------|-----------|
| **State** | One of multiple visual/behavioral modes an element can be in |
| **Hover state** | Visual change when cursor enters element bounds |
| **Focus state** | Visual indicator (typically blue ring) when element has keyboard focus |
| **Active state** | Visual feedback during the moment a click/tap is happening |
| **Disabled state** | Non-interactive; visually muted to communicate unavailability |
| **Loading state** | Indicates async operation in progress |
| **Error state** | Communicates invalid input or failed operation (red) |
| **Empty state** | The UI shown when a list/view has no content |
| **Skeleton screen** | Placeholder layout shown while real content loads |
| **Toast** | Temporary popup notification that auto-dismisses |
| **Focus ring** | The visible outline around a focused element |
| **Optimistic UI** | Immediately showing the success state before server confirms |
