"use client";

import * as React from "react";
import { AnimatePresence, LazyMotion, MotionConfig, domAnimation } from "motion/react";
import * as m from "motion/react-m";
import { usePathname } from "next/navigation";

const transition = {
  duration: 0.28,
  ease: [0.22, 1, 0.36, 1] as const,
};

export function RouteTransitionShell({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();

  return (
    <LazyMotion features={domAnimation} strict>
      <MotionConfig reducedMotion="user">
        <AnimatePresence initial={false} mode="wait">
          <m.main
            key={pathname}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={transition}
          >
            {children}
          </m.main>
        </AnimatePresence>
      </MotionConfig>
    </LazyMotion>
  );
}
