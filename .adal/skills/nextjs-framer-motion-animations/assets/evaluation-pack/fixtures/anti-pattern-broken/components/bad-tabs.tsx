"use client"

import { motion } from "motion/react"
import { useState } from "react"

const items = ["Overview", "Billing", "Usage"]

export function BadTabs() {
  const [active, setActive] = useState(items[0])

  return (
    <div className="flex gap-2">
      {items.map((item) => {
        const selected = item === active
        return (
          <button key={item} type="button" className="relative px-3 py-2" onClick={() => setActive(item)}>
            <span>{item}</span>
            {selected ? <motion.span layoutId="underline" className="absolute inset-x-0 -bottom-px h-0.5 bg-current" /> : null}
          </button>
        )
      })}
    </div>
  )
}
