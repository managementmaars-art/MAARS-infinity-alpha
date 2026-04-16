# Pages Router guide

## Core pattern
In Pages Router, the most reliable route-transition setup is a stable `AnimatePresence` in `pages/_app.tsx` and an animated page wrapper inside each page or shared layout.

## `_app.tsx` wiring
Keep the presence wrapper mounted at the app root.

```tsx
import type { AppProps } from "next/app";
import { AnimatePresence, MotionConfig } from "motion/react";

export default function App({ Component, pageProps, router }: AppProps) {
  return (
    <MotionConfig reducedMotion="user">
      <AnimatePresence initial={false} mode="wait">
        <Component {...pageProps} key={router.asPath} />
      </AnimatePresence>
    </MotionConfig>
  );
}
```

See `assets/pages-app.tsx`.

## Which key to use
Choose the key based on what should count as a new page:

- `router.asPath`
  - Best when dynamic param changes should animate
  - Includes query string and hash, so query-only changes can also retrigger transitions

- `router.route`
  - Stable route pattern like `/posts/[slug]`
  - Good when you only want transitions between different route templates
  - Not enough when `/posts/a` and `/posts/b` should animate differently

Rule of thumb:
- Start with `router.asPath`
- If query-string transitions become noisy, switch to a path-only key derived from `router.asPath.split("?")[0]`

## Page wrapper
A page still needs its own animated surface.

```tsx
import { motion } from "motion/react";

export default function Page() {
  return (
    <motion.main
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
      transition={{ duration: 0.28, ease: [0.22, 1, 0.36, 1] }}
    >
      ...
    </motion.main>
  );
}
```

## Navigation notes
Prefer Next.js `<Link>` for navigation. Use `useRouter()` only when you need programmatic navigation from a Client Component.

## Common mistakes
- Using `router.route` and expecting dynamic-param transitions to fire
- Mounting `AnimatePresence` inside each page instead of `_app.tsx`
- Forgetting an `exit` state on the animated page wrapper
- Letting two competing wrappers animate the same page surface
