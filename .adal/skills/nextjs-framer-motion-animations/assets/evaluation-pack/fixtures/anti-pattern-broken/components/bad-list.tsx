"use client"

import { AnimatePresence, Reorder, motion } from "framer-motion"

const items = ["alpha", "beta", "gamma"]

export function BadList() {
  return (
    <AnimatePresence mode="popLayout">
      {items.map((item, index) => (
        <Reorder.Item key={index} value={item} as={motion.li}>
          {item}
        </Reorder.Item>
      ))}
    </AnimatePresence>
  )
}
