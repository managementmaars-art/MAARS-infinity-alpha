# PMA-Web Routing And UI

## Routing

- Use TanStack Router file-based routing under `src/app/routes/`.
- Keep `routeTree.gen.ts` generated and excluded from manual lint noise.
- Prefer route-level layouts via `__root.tsx` and nested route folders.
- Keep feature logic in `src/features/`; routes should compose features instead of absorbing all business logic.

## Provider Composition

Provider order:

```text
I18nextProvider (optional)
QueryClientProvider
ThemeProvider
RouterProvider
```

`RouterProvider` is rendered in `main.tsx`, outside the provider factory when that keeps startup clearer.

## Entry Point

Baseline shape:

```typescript
import { createRouter, RouterProvider } from "@tanstack/react-router";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { Providers } from "./app/providers";
import { routeTree } from "./app/routeTree.gen";
import "./index.css";

const router = createRouter({ routeTree });
```

Requirements:

- fail fast when `#root` is missing
- register router types for TanStack Router
- keep global CSS imports at the entry boundary

## shadcn/ui

Use shadcn as owned code, not copy-pasted snippets.

Recommended init choices:

- component library: `base-ui`
- style: `base-nova`
- base color: `neutral`
- CSS variables: `yes`
- aliases aligned to the actual folder layout

Rules:

- generate shared primitives into `src/shared/components/ui/`
- keep business components inside features
- add new primitives through the CLI
- keep `components.json` consistent with repository aliases and Tailwind paths

## Tailwind CSS v4

- Use `@theme` and CSS variables as the design-token layer.
- Prefer oklch values for color tokens.
- Map semantic tokens such as `--color-primary` and `--color-muted` into Tailwind theme variables.
- Keep hardcoded colors out of deep feature components.

Typical imports:

```css
@import "tailwindcss";
@import "tw-animate-css";
@import "shadcn/tailwind.css";
```

## Theming

- ThemeProvider is the single source of truth.
- Support `light`, `dark`, and `system` when the product needs them.
- Persist the selected theme in `localStorage`.
- Do not duplicate theme state in Zustand.
- Prefer a `ModeToggle` that cycles predictably through available modes.

## Fonts And Visual Tokens

- Prefer self-hosted variable fonts when typography matters.
- Keep font and radius tokens in CSS variables.
- Centralize product tokens in `index.css` or a dedicated theme file rather than spreading them across feature components.
