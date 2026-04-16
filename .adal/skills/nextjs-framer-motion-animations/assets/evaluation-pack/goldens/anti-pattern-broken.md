# Golden summary

The audit should flag, at minimum:

- mixed `motion` and `framer-motion` imports
- a client root App Router layout
- server files importing client-only Motion paths
- index keys under `AnimatePresence`
- transform-avoidant `top` / `left` animation
- repeated `layoutId` usage without `LayoutGroup id`
- `motion.create()` inside render
- `motion/react-client` used in a client-driven file
- `Reorder.Item` without `Reorder.Group`
