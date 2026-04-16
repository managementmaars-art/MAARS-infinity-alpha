# Golden summary

- Do **not** mark `app/layout.tsx` as a client component
- Create a small client route-transition shell rendered from `app/layout.tsx`
- Use `AnimatePresence initial={false}` keyed by pathname
- Keep transitions lightweight and route-content scoped
