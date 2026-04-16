# Micro-interactions

## What Is a Micro-interaction?

> "Micro-interactions are a form of feedback, but they set things up a notch."

A micro-interaction is a **small, focused animation** triggered by a specific user action that:
1. Confirms the action happened
2. Shows the result of the action
3. Can add delight and personality

The key difference from basic states: **micro-interactions communicate meaning through motion**, not just color/border changes.

---

## The Copy Button Example

This is the canonical example from the video:

### Without Micro-interaction
```
User clicks copy button
→ Button hover state
→ Button active/pressed state
→ ... nothing else
```
The user still doesn't *know* if the copy succeeded.

### With Micro-interaction
```
User clicks copy button
→ Button pressed state
→ "Copied!" chip slides up from below the button (animate in)
→ Chip auto-dismisses after ~1.5s (animate out)
```

> "If we have this chip slide up, that's a micro-interaction that confirms our action."

The chip **slides up** — the motion itself carries meaning (it emerged from the action).

---

## The Spectrum of Micro-interactions

> "These can range from highly practical to much more fun and playful."

### Practical (Functional)
These confirm critical actions and prevent confusion:
- Copy → "Copied!" chip slides up
- Save → "Saved" badge briefly appears on the save button
- Delete → Item slides out and fades (confirms it's gone)
- Submit → Form section fades to success message
- Upload → Progress bar fills and transforms to success state

### Delightful (Expressive)
These add personality without adding confusion:
- Like button → heart "pops" with a scale+bounce animation
- Checkbox → animated checkmark draws itself
- Toggle switch → slides with a satisfying physics-like ease
- Drag item → subtle scale-up and shadow increase while dragging
- Menu open → items stagger-animate in (each delayed by 30-50ms)
- Confetti burst → on completing something major (first project created, etc.)

---

## Anatomy of a Good Micro-interaction

Every micro-interaction has 4 components (Dan Saffer's model):

| Component | Description | Example |
|-----------|-------------|---------|
| **Trigger** | What initiates the interaction | User clicks Copy button |
| **Rules** | What happens as a result | "Copied!" chip appears |
| **Feedback** | The visual/audio response the user sees | Chip slides up, stays 1.5s, fades out |
| **Loops & Modes** | How it behaves on repeat or under conditions | Clicking copy again resets the chip |

---

## Animation Principles for Micro-interactions

### Timing
| Duration | Use |
|---------|-----|
| 100-150ms | Instant feedback (hover state changes) |
| 200-300ms | Simple transitions (fade, small slide) |
| 300-400ms | Moderate complexity (expand/collapse, slide-in panel) |
| 400-600ms | Complex sequences (multi-step animations) |
| 600ms+ | Special effects only (celebration, page transitions) |

### Easing
| Easing | Feel | Use |
|--------|------|-----|
| `ease-out` | Fast start, slow end | Elements entering the screen |
| `ease-in` | Slow start, fast exit | Elements leaving the screen |
| `ease-in-out` | Smooth both ways | Elements moving within the screen |
| `spring` (CSS or JS) | Bouncy, physical | Delightful micro-interactions |

### CSS Example: Chip Slide-Up
```css
@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.copied-chip {
  animation: slideUp 200ms ease-out forwards;
}

.copied-chip.exit {
  animation: slideUp 150ms ease-in reverse forwards;
}
```

---

## Micro-interactions on Scroll & Swipe

> "Even micro animations on scroll or swipe."

- **Scroll-triggered reveals**: Elements fade/slide in as they enter the viewport
- **Parallax**: Background moves at a different speed than foreground
- **Sticky headers**: Shrink or gain shadow as user scrolls down
- **Pull-to-refresh**: Custom animation on mobile pull gesture

---

## When NOT to Use Micro-interactions

- **Never on critical error states** — errors need clear, immediate legibility, not animation
- **Never on frequently repeated actions** — repetitive animation becomes annoying fast
- **Never with long durations on blocking operations** — users want the result, not the show
- **Respect prefers-reduced-motion** — always provide a no-animation fallback

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## Practical Rules

1. **Confirm every action with motion** — especially non-obvious async actions
2. **Keep durations short** — 200-350ms for most micro-interactions
3. **Ease-out for enter, ease-in for exit**
4. **Motion should carry meaning** — slide up = appeared, slide down = dismissed
5. **Delightful animations are optional** — practical confirmations are required
6. **Always implement prefers-reduced-motion** as an accessibility fallback
7. **Don't animate things users interact with constantly** — every tab click doesn't need a spring

---

## Engineering Vocabulary

| Term | Definition |
|------|-----------|
| **Micro-interaction** | A small, contained animation triggered by a single user action |
| **Trigger** | The user action that initiates a micro-interaction |
| **Feedback** | The visual/motion response the user sees as a result |
| **Easing** | The acceleration curve of an animation (ease-in, ease-out, spring) |
| **Keyframe** | A defined state at a specific point in an animation |
| **Transition** | CSS-based change between two states (simpler than keyframe animation) |
| **Spring animation** | Physics-based animation that overshoots and settles (bouncy) |
| **Stagger** | Sequenced delays applied to a list of animating elements |
| **Enter animation** | Motion played when an element appears |
| **Exit animation** | Motion played when an element disappears |
| **prefers-reduced-motion** | CSS media query for users who prefer minimal animation |
| **Optimistic animation** | Playing success animation before server confirms (immediate feedback) |
| **Confetti** | Celebration particle animation for major user milestones |
