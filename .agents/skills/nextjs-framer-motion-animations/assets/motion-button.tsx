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
