# Final review checklist

Run this before finishing.

## Scope
- The diff solves the specific request
- No unnecessary global animation architecture was introduced
- The chosen pattern is the narrowest correct one

## Package and imports
- Import path matches the repository choice
- `motion` and `framer-motion` are not mixed casually
- `motion/react-client` is only used in `motion` package codebases
- Any `LazyMotion` setup uses the correct feature pack

## Next.js architecture
- App Router server components stay server-side where possible
- Any Motion hook usage lives in a Client Component
- Client boundaries are intentionally small
- Props passed into client components are serialisable
- Route-transition wrappers stay mounted if exit animations are required

## Pattern correctness
- Reveal uses local `initial` and `animate`
- Scroll reveal uses `whileInView` unless state is required
- Stagger timing lives on the parent
- Exit animation uses `AnimatePresence` with direct-child stable keys
- Layout animation uses `layout` before bespoke size choreography
- Shared elements use `layoutId`, and repeated widgets use `LayoutGroup id` if needed
- Reorder uses `Reorder.Group` and `Reorder.Item`

## Accessibility
- Reduced motion has been handled thoughtfully
- Hover-only cues also have keyboard or focus parity where relevant
- Focus management and click targets still work
- Important information is not hidden behind slow animation

## Performance
- The chosen boundary does not pull a large subtree into the client without reason
- The route is not paying for a global provider unnecessarily
- If a heavy subtree was introduced, bundle impact was considered
- Images still reserve layout space
- Observer or wrapper count has not grown without need

## Verification
- Relevant lint, typecheck, test, or build checks ran if available
- No obvious hydration mismatch risk remains
- Visual behaviour was sanity-checked in the affected UI
- Final answer names changed files, pattern choice, import path, and tuning knobs

## Skill iteration
- If you changed the skill itself, run `node scripts/run-evaluation-pack.mjs`
- Review trigger coverage in `assets/evaluation-pack/trigger-tests.json`
- Recheck anti-pattern guidance with `node scripts/check-motion-antipatterns.mjs --root /path/to/repo`
