# Performance guide

## Keep Client Components small
Push Motion to the smallest leaf that actually needs it. A local reveal should not turn an entire page, layout, or data-fetching branch into client code.

## Use `motion/react-client` for passive App Router cases
If the repo already uses the modern `motion` package and the animation is passive and hook-free, `motion/react-client` can keep the file server-friendly.

Do not use it for:
- `AnimatePresence`
- route hooks
- `useScroll`
- `useAnimate`
- local interactive state

## Plain `motion` vs `m` plus `LazyMotion`
- Use plain `motion` for local edits and small scopes.
- Use `m` plus `LazyMotion` when Motion becomes broad in scope or bundle size is a real concern.

### Feature packs
- `domAnimation` for standard animations, hover, tap, focus, variants, and exit.
- `domMax` only when you need layout or drag features that require the fuller bundle.

## Use `MotionConfig` for subtree defaults
If multiple components in the same subtree share reduced-motion handling or default transitions, use `MotionConfig` locally instead of repeating config everywhere.

## Lazy-load heavy animation islands
Rarely opened drawers, modals, or dashboards with lots of motion can often be split or loaded lazily. Prefer local dynamic boundaries over global motion infrastructure.

## Prefer transform and opacity
These are usually the safest properties to animate. Avoid animating `top`, `left`, large filters, or expensive paint-heavy effects on large surfaces.

## Layout animation details
- Start with `layout` before manual height animation.
- If only position should animate, try `layout="position"`.
- If layout animation causes distortion, give affected children their own `layout` handling.

## Scroll performance
- Prefer `whileInView` for ordinary reveal-on-scroll.
- Reserve `useScroll` for effects that genuinely need continuous scroll linkage.
- Keep observer and wrapper count under control; one well-placed wrapper often beats many tiny ones.

## Protect image layout
When animating `next/image` or its wrapper:
- preserve the layout box
- keep reserved space intact
- animate transform or opacity rather than intrinsic size

## Inspect before optimising blindly
Do not assume Motion is the only source of bundle growth or jank. Check:
- actual import paths
- whether the client boundary widened
- whether a new global provider was added
- whether the route now mounts more animated DOM than before

## When not to animate
Skip or reduce Motion when:
- the effect can be handled cleanly in CSS and Motion was not required
- the route is highly performance-sensitive and the effect is purely decorative
- reduced-motion users would receive little value from the movement
