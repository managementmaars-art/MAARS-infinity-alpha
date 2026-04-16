"use client"

import * as motion from "motion/react-client"
import { useState } from "react"

export function BadPassive() {
  const [open, setOpen] = useState(false)

  return (
    <motion.div animate={{ opacity: open ? 1 : 0.6 }}>
      <button type="button" onClick={() => setOpen((value) => !value)}>
        Toggle
      </button>
    </motion.div>
  )
}
