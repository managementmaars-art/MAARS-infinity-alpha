"use client";

import * as React from "react";
import { MotionConfig } from "motion/react";

const defaultTransition = {
  duration: 0.22,
  ease: [0.22, 1, 0.36, 1] as const,
};

export function MotionProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <MotionConfig reducedMotion="user" transition={defaultTransition}>
      {children}
    </MotionConfig>
  );
}
