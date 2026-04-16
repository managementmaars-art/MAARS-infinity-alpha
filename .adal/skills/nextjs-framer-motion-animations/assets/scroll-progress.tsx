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
