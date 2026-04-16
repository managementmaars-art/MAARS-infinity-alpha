"use client"

import * as React from "react"
import { motion } from "motion/react"

export function BadFactory() {
  const MotionButton = motion.create("button")

  return <MotionButton whileHover={{ scale: 1.05 }}>Broken factory</MotionButton>
}
