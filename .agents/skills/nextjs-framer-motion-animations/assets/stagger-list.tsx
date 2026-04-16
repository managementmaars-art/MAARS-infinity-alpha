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
