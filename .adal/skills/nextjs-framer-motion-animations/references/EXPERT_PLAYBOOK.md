# Expert playbook

## Package strategy
Use one package strategy per diff:
- **Current default:** `motion`
- **Legacy compatibility:** `framer-motion`
- **Do not mix both** in the same patch unless the task is an explicit migration.

Use the current package when:
- Installing animation support from scratch
- Touching many imports anyway
- Building a new shared motion layer

Stay on legacy `framer-motion` when:
- The repo already uses it heavily
- The task is small and package churn would dominate the diff
- The user asked for the smallest possible change

## API selection matrix

| Problem | Best first choice | Escalate to |
| --- | --- | --- |
| Hover, tap, focus, simple entrance | `motion.*` | variants if repeated across children |
| Reusable coordinated list or card grid | variants plus `stagger` | `useAnimate` for imperative sequencing |
| Modal, drawer, toast, conditional panel | `AnimatePresence` | `useAnimate` plus `usePresence` for custom exits |
| Accordion, expanding card, layout reflow | `layout` | `LayoutGroup` if siblings affect each other |
| Shared underline, card-to-detail, selected pill | `layoutId` | `LayoutGroup id` when multiple instances exist |
| Reveal on scroll | `whileInView` | `useInView` plus `useAnimate` if custom timeline is needed |
| Scroll-linked progress or parallax | `useScroll` plus `useTransform` | `useSpring` to smooth linked values |
| Design-system button, link, card | `motion.create()` | explicit wrappers per component family |

## Motion tokens
Start here before tuning.

### Easing
Use one default easing curve across the feature:
```ts
const easeOut = [0.22, 1, 0.36, 1] as const
```

### Micro-interactions
```ts
const microTransition = { duration: 0.16, ease: easeOut }
```

### Reveal / entrance
```ts
const revealTransition = { duration: 0.28, ease: easeOut }
```

### Springs
Use springs when the UI is reacting to stateful layout changes rather than decorative fades.
```ts
const gentleSpring = { type: "spring", stiffness: 260, damping: 24, mass: 0.9 } as const
const snappySpring = { type: "spring", stiffness: 420, damping: 32, mass: 0.7 } as const
```

Guideline:
- Use **tween** for simple opacity and transform reveals.
- Use **spring** for toggles, expanding panels, and layout-driven movement.
- Use `visualDuration` only when you need a spring to visually line up with time-based transitions.

## Strong opinions
- Default to **subtle** motion. Most UIs improve with less movement, not more.
- Use **one primary animation idea per surface**. Do not layer hover scale, shadow bloom, blur, and parallax onto the same component unless the user explicitly wants it.
- Choose **layout animation** instead of manual height or position hacks when the movement is caused by a React re-render.
- Choose **shared layout** instead of manually syncing coordinates for tabs, pills, and selected cards.
- Choose **imperative sequencing** only when declarative props become harder to reason about.

## Route transition rules
- If you need **exit animations**, `AnimatePresence` must stay mounted while the child changes.
- In App Router, prefer a **persistent client shell under a layout** for exit choreography.
- Use `template.tsx` when you want **segment remount semantics** and replayed enter animations, not as the only tool for all route exits.
- In Pages Router, keep presence in `_app.tsx`.
- For dynamic routes in Pages Router, `router.route` will not change across param changes. Use `router.asPath` when those changes should animate.

## Layout animation rules
- If content looks stretched, add `layout` to the affected children too.
- If an image or text block changes aspect ratio, prefer `layout="position"` so only position animates.
- If you reuse the same `layoutId` in multiple repeated groups, namespace them with `LayoutGroup id`.
- When mixing exiting children and layout animation, be ready to wrap related elements in `LayoutGroup`.

## Scroll rules
- **Reveal** and **scroll-linked** animation are different tasks. Use `whileInView` for reveal, `useScroll` for scroll-linked values.
- Avoid parallax on long text blocks.
- For progress bars, map `scrollYProgress` through `useSpring` so the bar feels smooth rather than noisy.

## Accessibility rules
- Every animated subtree should either inherit `MotionConfig reducedMotion="user"` or explicitly honour `useReducedMotion()`.
- Reduced motion does not mean zero feedback. Prefer opacity or colour changes over large transforms.
- For modals and drawers, let a dialog library own focus management. Motion should own visuals.

## Anti-patterns
- Mixing `motion` and `framer-motion` imports
- Mounting and unmounting `AnimatePresence` itself
- Keying exit-sensitive nodes by array index
- Using `top` and `left` when `x` and `y` would do
- Animating huge shadows or blurs on large surfaces
- Calling `motion.create()` inside render
- Reusing global `layoutId` values across multiple independent tab sets
- Treating `template.tsx` as if it remounts on search-param-only changes
