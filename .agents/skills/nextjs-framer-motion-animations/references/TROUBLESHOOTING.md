# Troubleshooting

## Nothing animates
- Check that the component actually renders a Motion element such as `motion.div`.
- Confirm the repo import path is consistent with the installed package.
- Make sure the triggering prop or key is changing when you expect an animation.
- In App Router, verify that client-only Motion imports are not sitting in a server file.

## App Router says a component needs `use client`
You are probably importing `motion/react` or `framer-motion` into a server file.

Fixes:
- Move the animated piece into a small Client Component leaf.
- Or, for passive hook-free Motion in a modern Motion codebase, use `motion/react-client`.
- Do not make `app/layout.tsx` client-side unless the request truly needs a global client boundary.

## Exit animations do not fire
- The exiting element must be a direct child of `AnimatePresence`.
- The child must have a stable `key`.
- The presence boundary must stay mounted long enough for the exit to happen.
- In App Router, template remounts alone will not give you a persistent exit-aware shell.

## Enter animations run when they should not
- Use `initial={false}` when the first paint should match the final state.
- Check whether the component is remounting because of a changing `key`.
- Verify that `template.tsx` remount semantics are actually wanted.

## Dynamic Pages Router routes do not transition
- In `_app.tsx`, key by `router.asPath` when dynamic param changes matter.
- Do not key by a value that stays constant across the transitions you care about.

## Layout animation is not happening or looks stretched
- Start with `layout` before manual size choreography.
- If only position should animate, try `layout="position"`.
- If children distort, add `layout` to affected descendants as well.
- Confirm the layout is actually changing between renders.

## Shared-element underline animates in the wrong group
- `layoutId` is global within the current layout tree.
- In repeated widgets, wrap each instance in `LayoutGroup id`.
- Ensure only one active shared element with a given `layoutId` exists per group.

## `mode="popLayout"` looks broken
- The parent needs a non-static position.
- Check for clipping or stacking-context side effects.
- Use it only when you truly need the exiting item popped out of layout.

## Scroll reveal fires against the wrong container
- If the scroll container is not the window, configure `viewport.root`.
- If you need more control, switch to `useInView` with the correct root.
- Avoid stacking multiple observers when one container-level approach would do.

## Motion feels too heavy or distracting
- Reduce distance before reducing duration.
- Prefer opacity plus a small `y` change.
- Remove bounce from content surfaces unless the design system calls for it.
- Re-check whether Motion is even necessary for the requested effect.

## Hydration mismatch or flashing
- Keep the server-rendered structure stable.
- Avoid using route hooks or browser-only APIs in server files.
- Use `initial={false}` when first paint should not animate in.
- Be careful when wrappers change DOM structure around server-rendered content.

## Reduced motion is not handled
- Add `MotionConfig reducedMotion="user"` at an appropriate subtree boundary.
- Use `useReducedMotion()` when behaviour, not just timing, should change.
- Replace large movement with opacity-only changes when reasonable.

## Styling or refs break after wrapping with Motion
- Prefer converting the existing root element to a Motion element rather than adding an extra wrapper.
- If you must wrap a design-system component, use `motion.create()` outside render.
- Make sure the wrapped component forwards its ref.

## `LazyMotion` complains or bundle size jumped
- `domAnimation` is the default feature pack.
- `domMax` is only for layout, drag, or features that truly need it.
- Keep `LazyMotion` local to the subtree that benefits from it.
- Check whether a simple local `motion` import would actually be cheaper operationally for the task.

## CSP blocks Motion styles
- Some Motion features rely on runtime style injection.
- Check the project CSP and nonce setup before blaming the component code.
- If CSP is strict, prefer patterns that fit the project’s existing allowances or adjust CSP deliberately.

## Template-based transition did not retrigger
- `template.tsx` remounts on segment changes, not every possible state change.
- Search-param-only changes may not behave the way you expect.
- If you need a guaranteed content transition on pathname change, use a client wrapper keyed by pathname.
