# Decision tree

Use this to choose the narrowest correct pattern before editing.

## Boundary choice shortcut

### Use `motion/react-client` when
- the repo uses the modern `motion` package
- the file can stay server-friendly
- the animation is passive and hook-free
- you do not need `AnimatePresence`, route hooks, `useScroll`, `useAnimate`, or local interactive state

### Use a small Client Component leaf when
- you need `useReducedMotion`, `useInView`, `useScroll`, `useAnimate`, or route hooks
- you need `AnimatePresence`
- the component is already interactive or stateful
- the animation is local to one widget and should not drag a larger subtree into the client

### Use a client wrapper around server-rendered children when
- the wrapper controls visibility or transition
- the wrapped content can stay server-rendered
- the boundary is smaller than converting the whole parent to a Client Component

### Use a layout-mounted shell or `pages/_app.tsx` wrapper when
- you genuinely need route-content enter and exit choreography
- the transition should survive route changes because the presence boundary stays mounted

## Choosing between closely related APIs

### `whileInView` vs `useInView`
- Start with `whileInView` for straightforward reveal-on-scroll.
- Use `useInView` when entering the viewport must drive React state, imperative code, or cross-element coordination.
- If the scroll container is not the window, make sure the correct root is configured.

### `layout` vs manual height animation
- Start with `layout` for accordions, chips, tab underlines, and small reflows.
- Reach for manual height or `useAnimate` only when `layout` cannot model the transition cleanly.
- If content stretches during layout animation, try `layout="position"` or add `layout` to the affected children.

### Variants vs `useAnimate`
- Use variants for ordinary parent-child orchestration, stagger, and reusable patterns.
- Use `useAnimate` for small imperative sequences or when declarative variants become awkward.
- Do not escalate to a timeline mindset for simple UI state changes.

### `motion` vs `m` plus `LazyMotion`
- Use plain `motion` for local edits and small numbers of animated elements.
- Use `m` plus `LazyMotion` when Motion becomes broad in scope or bundle size is a real concern.
- Prefer `domAnimation` unless you truly need layout or drag features that require `domMax`.

## If the request says “make it smoother”
- Reduce travel distance before increasing duration.
- Prefer opacity plus a small `y` change over bigger movement.
- Remove unnecessary bounce from content surfaces.
- Try `layout` before manual size choreography.
- Avoid stacking reveal, scale, rotate, and parallax on the same region.

## If the request says “this breaks in App Router”
Check, in order:
1. Is a server file importing `motion/react` or `framer-motion` directly?
2. Does the file actually need hooks or can it stay passive with `motion/react-client`?
3. Can the animation move into a smaller client leaf instead of making the parent or layout client-side?
4. Are only serialisable props being passed into the client component?
5. Is the presence boundary staying mounted if exit animations are expected?

## If bundle size suddenly matters
- Prefer CSS for tiny hover or focus effects when Motion is not a requirement.
- Keep Client Component boundaries small.
- Consider `LazyMotion` for large motion-heavy subtrees.
- Lazy-load animation-heavy islands such as rarely opened drawers or modals.
- Inspect actual import paths before assuming the problem is Motion itself.
