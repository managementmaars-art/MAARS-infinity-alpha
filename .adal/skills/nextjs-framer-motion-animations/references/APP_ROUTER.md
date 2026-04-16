# App Router guide

## Mental model

In App Router, layouts and pages are Server Components by default. Treat Motion as a local concern unless the user clearly needs a broader transition system.

General rules:
- Keep data fetching and server-only logic in server components.
- Push Motion to the smallest leaf that actually needs it.
- Pass only serialisable props into client components.
- Avoid turning `app/layout.tsx` into a Client Component just to animate one hero, card, or modal.

## Pattern 1: passive Motion component with `motion/react-client`

Use this only when all of the following are true:
- the repo uses the modern `motion` package
- the animation is passive and hook-free
- you do not need `AnimatePresence`, route hooks, scroll state, or local interactivity

Example:

```tsx
import * as motion from "motion/react-client"

export function MotionCard({
  children,
  className,
}: {
  children: React.ReactNode
  className?: string
}) {
  return (
    <motion.article
      className={className}
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
    >
      {children}
    </motion.article>
  )
}
```

## Pattern 2: server parent, animated client leaf

Use when the animated part needs hooks, local state, or other client-only behaviour.

Good fit:
- `useReducedMotion`
- `AnimatePresence`
- `whileInView` with custom logic
- `usePathname`
- `useScroll`
- drag or reorder
- any component already using client hooks

Server component:

```tsx
import { AnimatedHero } from "./animated-hero"

export default async function Page() {
  const data = await getData()

  return <AnimatedHero title={data.title} subtitle={data.subtitle} />
}
```

Client leaf:

```tsx
"use client"

import { motion, useReducedMotion } from "motion/react"

export function AnimatedHero({
  title,
  subtitle,
}: {
  title: string
  subtitle: string
}) {
  const reduceMotion = useReducedMotion()

  return (
    <motion.section
      initial={reduceMotion ? { opacity: 0 } : { opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <h1>{title}</h1>
      <p>{subtitle}</p>
    </motion.section>
  )
}
```

## Pattern 3: client wrapper around server-rendered children

Use when the wrapper needs Motion but the inner content can stay server-rendered.

Good fit:
- modal shell
- drawer shell
- animated panel open/close
- local route-content wrappers
- visibility wrappers around server-rendered content

```tsx
"use client"

import { AnimatePresence, motion } from "motion/react"

export function AnimatedShell({
  open,
  children,
}: {
  open: boolean
  children: React.ReactNode
}) {
  return (
    <AnimatePresence>
      {open ? (
        <motion.div
          key="shell"
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 8 }}
        >
          {children}
        </motion.div>
      ) : null}
    </AnimatePresence>
  )
}
```

## Pattern 4: persistent route shell for enter and exit choreography

Use when the user genuinely wants route-content transitions and the presence boundary must survive route changes.

### Recommended structure
- Keep `app/layout.tsx` as the stable server layout.
- Render a small Client Component shell inside it.
- Put `AnimatePresence` in that shell and key the routed content inside it.

### Example `app/layout.tsx`

```tsx
import type { ReactNode } from "react"
import { RouteTransitionShell } from "@/components/motion/route-transition-shell"

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <RouteTransitionShell>{children}</RouteTransitionShell>
      </body>
    </html>
  )
}
```

## Pattern 5: segment replay with `template.tsx`

Use `template.tsx` when you want remount semantics at a specific segment boundary. It is useful for replaying enter animations, but it is not a complete substitute for a persistent exit-aware shell.

### Example `app/template.tsx`

```tsx
import { FadeInOnMount } from "@/components/motion/fade-in-on-mount"

export default function Template({ children }: { children: React.ReactNode }) {
  return <FadeInOnMount>{children}</FadeInOnMount>
}
```

## Choosing the right pattern
- Choose **Pattern 1** for passive, hook-free motion in modern Motion codebases.
- Choose **Pattern 2** when the animated part needs client hooks or local state.
- Choose **Pattern 3** when a thin wrapper can stay client-side while the inner content remains server-rendered.
- Choose **Pattern 4** when route enter and exit choreography actually matters.
- Choose **Pattern 5** when remount-on-navigation semantics are enough.

## Common mistakes
- Marking the root layout as client for a one-off animation
- Passing functions from a server component into a client animation leaf
- Importing `framer-motion` directly into an App Router server file
- Replacing a server-rendered subtree with a large client rewrite just to animate one element
- Adding `AnimatePresence` everywhere “just in case”
