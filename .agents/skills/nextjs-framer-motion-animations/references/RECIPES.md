# Recipes

Examples below use the current `motion` package. If the repo stays on legacy `framer-motion`, swap imports consistently.

## 1) Subtle button micro-interaction
```tsx
"use client";

import * as React from "react";
import { motion } from "motion/react";

export function MotionButton(
  props: React.ComponentPropsWithoutRef<"button">,
) {
  return (
    <motion.button
      {...props}
      whileHover={{ y: -1 }}
      whileTap={{ scale: 0.98 }}
      transition={{ duration: 0.16, ease: [0.22, 1, 0.36, 1] }}
    />
  );
}
```

Use for:
- CTA buttons
- icon buttons
- menu triggers

Avoid:
- large scale jumps
- removing visible focus styles

## 2) Reveal on scroll
```tsx
"use client";

import * as React from "react";
import { motion } from "motion/react";

export function Reveal({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <motion.div
      className={className}
      initial={{ opacity: 0, y: 16 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.2 }}
      transition={{ duration: 0.28, ease: [0.22, 1, 0.36, 1] }}
    >
      {children}
    </motion.div>
  );
}
```

Use `whileInView` for simple reveal. Switch to `useInView` plus `useAnimate` only when the timeline is custom.

## 3) Staggered list
```tsx
"use client";

import * as React from "react";
import { motion, stagger } from "motion/react";

const container = {
  hidden: {},
  show: {
    transition: {
      delayChildren: stagger(0.06),
    },
  },
};

const item = {
  hidden: { opacity: 0, y: 10 },
  show: { opacity: 1, y: 0 },
};

export function StaggerList({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <motion.ul variants={container} initial="hidden" animate="show">
      {children}
    </motion.ul>
  );
}

export function StaggerItem({
  children,
}: {
  children: React.ReactNode;
}) {
  return <motion.li variants={item}>{children}</motion.li>;
}
```

Use when many siblings share the same entrance idea.

## 4) Modal or drawer shell
Pair Motion with a dialog library for semantics and focus management.

```tsx
"use client";

import * as React from "react";
import { AnimatePresence, motion } from "motion/react";

export function ModalShell({
  open,
  onClose,
  children,
}: {
  open: boolean;
  onClose: () => void;
  children: React.ReactNode;
}) {
  return (
    <AnimatePresence>
      {open ? (
        <>
          <motion.div
            className="fixed inset-0 bg-black/50"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />
          <motion.div
            className="fixed inset-x-0 top-20 mx-auto max-w-lg rounded-2xl bg-white p-6 shadow-xl"
            initial={{ opacity: 0, y: 16, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 8, scale: 0.98 }}
            transition={{ duration: 0.24, ease: [0.22, 1, 0.36, 1] }}
          >
            {children}
          </motion.div>
        </>
      ) : null}
    </AnimatePresence>
  );
}
```

## 5) Shared underline for tabs
```tsx
"use client";

import * as React from "react";
import { LayoutGroup, motion } from "motion/react";

export function Tabs({
  id,
  items,
  value,
  onChange,
}: {
  id: string;
  items: { value: string; label: string }[];
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <LayoutGroup id={id}>
      <div className="flex gap-4">
        {items.map((item) => {
          const selected = item.value === value;

          return (
            <button
              key={item.value}
              className="relative pb-2"
              onClick={() => onChange(item.value)}
            >
              {item.label}
              {selected ? (
                <motion.div
                  layoutId="underline"
                  className="absolute inset-x-0 -bottom-px h-0.5 rounded-full bg-current"
                />
              ) : null}
            </button>
          );
        })}
      </div>
    </LayoutGroup>
  );
}
```

Use `LayoutGroup id` when multiple tab rows may exist on the same page, because `layoutId` is global.

## 6) Accordion layout animation
```tsx
"use client";

import * as React from "react";
import { LayoutGroup, motion } from "motion/react";

export function AccordionItem({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  const [open, setOpen] = React.useState(false);

  return (
    <motion.section layout className="rounded-xl border">
      <button
        className="w-full p-4 text-left"
        onClick={() => setOpen((value) => !value)}
      >
        {title}
      </button>

      {open ? (
        <motion.div
          layout
          className="px-4 pb-4"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          {children}
        </motion.div>
      ) : null}
    </motion.section>
  );
}

export function Accordion({
  children,
}: {
  children: React.ReactNode;
}) {
  return <LayoutGroup>{children}</LayoutGroup>;
}
```

## 7) App Router route shell
Use this when the task explicitly calls for route enter and exit choreography.

```tsx
"use client";

import * as React from "react";
import { AnimatePresence } from "motion/react";
import { motion } from "motion/react";
import { usePathname } from "next/navigation";

export function RouteTransitionShell({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();

  return (
    <AnimatePresence initial={false} mode="wait">
      <motion.main
        key={pathname}
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -8 }}
        transition={{ duration: 0.28, ease: [0.22, 1, 0.36, 1] }}
      >
        {children}
      </motion.main>
    </AnimatePresence>
  );
}
```

Mount this shell from a layout so `AnimatePresence` stays mounted.

## 8) Pages Router `_app.tsx`
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

## 9) Scroll progress bar
```tsx
"use client";

import { motion, useScroll, useSpring } from "motion/react";

export function ScrollProgress() {
  const { scrollYProgress } = useScroll();
  const scaleX = useSpring(scrollYProgress, {
    stiffness: 240,
    damping: 30,
    mass: 0.4,
  });

  return (
    <motion.div
      className="fixed inset-x-0 top-0 h-1 origin-left bg-current"
      style={{ scaleX }}
    />
  );
}
```

## 10) Imperative reveal with `useAnimate`
Use this when the sequence depends on an effect, intersection state, or custom timing that is awkward with props alone.

```tsx
"use client";

import * as React from "react";
import { useAnimate, useInView, stagger } from "motion/react";

export function ImperativeListReveal({
  children,
}: {
  children: React.ReactNode;
}) {
  const [scope, animate] = useAnimate();
  const inView = useInView(scope, { once: true, amount: 0.2 });

  React.useEffect(() => {
    if (!inView) return;

    void animate(
      "li",
      { opacity: [0, 1], y: [12, 0] },
      { delay: stagger(0.06), duration: 0.24, ease: [0.22, 1, 0.36, 1] },
    );
  }, [animate, inView]);

  return (
    <ul ref={scope}>
      {children}
    </ul>
  );
}
```

## 11) Passive App Router card with `motion/react-client`

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
      transition={{ duration: 0.25, ease: "easeOut" }}
    >
      {children}
    </motion.article>
  )
}
```

Use this only when you do not need hooks, `AnimatePresence`, or other client-only logic.

## 12) Reorder list

```tsx
"use client"

import { Reorder } from "motion/react"
import { useState } from "react"

export function ReorderList({ initialItems }: { initialItems: string[] }) {
  const [items, setItems] = useState(initialItems)

  return (
    <Reorder.Group axis="y" values={items} onReorder={setItems}>
      {items.map((item) => (
        <Reorder.Item key={item} value={item}>
          {item}
        </Reorder.Item>
      ))}
    </Reorder.Group>
  )
}
```
