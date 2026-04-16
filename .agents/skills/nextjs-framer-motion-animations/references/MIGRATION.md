# Migration guide

## Current package naming
Motion for React is now published as the `motion` package.

Preferred install:
```bash
npm install motion
```

Preferred imports:
```tsx
import { motion } from "motion/react"
```

## Legacy `framer-motion`
Many repos still use `framer-motion`. That is fine if the task is small and you want the minimum diff.

## Stay vs migrate
Stay on legacy `framer-motion` when:
- The repo already uses it
- The change touches only a few files
- The user wants a minimal patch

Migrate to `motion` when:
- You are installing Motion from scratch
- You are already touching many imports
- You want the current package naming and docs alignment
- You are building a fresh motion layer or shared primitives library

## Minimal migration steps
```bash
npm uninstall framer-motion
npm install motion
```

Then swap imports:
```tsx
// before
import { motion, AnimatePresence } from "framer-motion"

// after
import { motion, AnimatePresence } from "motion/react"
```

## Important migration rules
- Migrate in one focused diff if possible.
- Do not leave a codebase half on `framer-motion` and half on `motion`.
- If the codebase uses `m` plus `LazyMotion`, the modern imports are:
  - `import * as m from "motion/react-m"`
  - `import { LazyMotion, domAnimation, domMax } from "motion/react"`

## App Router note
Motion docs also provide:
```tsx
import * as motion from "motion/react-client"
```

Use that only when you explicitly need Motion components from a Server Component context. Most animation logic should still live in Client Components.

## Older APIs you may see
If you encounter older shared-layout code:
- Replace `AnimateSharedLayout` patterns with `layoutId`
- Use `LayoutGroup` when multiple components affect each other's layout or when repeated shared-layout groups need namespacing

## Suggested migration sequence
1. Run the audit script
2. Decide whether this task is a small local patch or an explicit migration
3. If migrating, update package and imports first
4. Run the build before changing animation behaviour
5. Then refactor patterns, wrappers, and recipes
