import { motion } from "motion/react"
import { BadList } from "@/components/bad-list"
import { BadTabs } from "@/components/bad-tabs"
import { BadPassive } from "@/components/bad-passive"
import { BadFactory } from "@/components/bad-factory"

export default function Page() {
  return (
    <main>
      <motion.div
        initial={{ opacity: 0, top: 24, left: 12 }}
        animate={{ opacity: 1, top: 0, left: 0 }}
      >
        Broken dashboard card
      </motion.div>
      <BadList />
      <BadTabs />
      <BadPassive />
      <BadFactory />
    </main>
  )
}
