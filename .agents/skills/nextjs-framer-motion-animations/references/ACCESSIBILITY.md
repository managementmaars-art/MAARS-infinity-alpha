# Accessibility guide

## Reduced motion is mandatory
Default every animated subtree to:

```tsx
<MotionConfig reducedMotion="user">
  {children}
</MotionConfig>
```

This automatically disables transform and layout animations while keeping non-spatial feedback like opacity and colour changes.

## Custom reduced-motion behaviour
Use `useReducedMotion()` when the animation logic itself should change.

Typical adjustments:
- Replace `x` and `y` transitions with opacity changes
- Disable parallax and scroll-linked movement
- Disable autoplaying decorative video or background motion
- Shorten or remove sequential choreography

```tsx
"use client";

import { motion, useReducedMotion } from "motion/react";

export function Drawer({ open }: { open: boolean }) {
  const reduce = useReducedMotion();

  return (
    <motion.aside
      animate={{
        opacity: open ? 1 : 0,
        x: reduce ? 0 : open ? 0 : "100%",
      }}
    />
  );
}
```

## Focus and keyboard use
Animation must not interfere with focus order or visible focus styles.

Rules:
- Keep CSS focus outlines or rings visible on animated buttons and links
- When content mounts or unmounts, do not lose the user's current focus target unexpectedly
- For dialogs, drawers, and popovers, let an accessibility-focused component library manage focus trapping and restoration

Motion should animate the surface, not own accessibility semantics.

## Readability
Avoid:
- large parallax movement on text
- repeated fade-in or shimmer on copy the user is trying to read
- motion that hides where content moved to

Prefer:
- short structural transitions
- small positional cues
- opacity or colour changes instead of large spatial movement in reduced-motion mode

## Accessibility review checklist
- Reduced motion enabled in OS: the UI still works and remains understandable
- Keyboard navigation still reaches every control
- Focus ring remains visible during hover, tap, and press states
- Modals and drawers restore focus on close
- Scroll-linked motion has a meaningful reduced-motion fallback
