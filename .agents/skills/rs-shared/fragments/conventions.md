# Conventions

Conventions docs are prescriptive, list-driven implementation guides. They describe HOW the project is built — stack, patterns, tokens, and conventions. They live in `rootspec/CONVENTIONS/` as two files: `technical.md` and `visual.md`.

Conventions are a bridge between the spec and the codebase. `/rs-spec` creates them; `/rs-impl` maintains them.

## Lifecycle

1. **Created** by `/rs-spec` after validation passes (if they don't already exist)
2. **Read** by `/rs-impl` before each story for consistency
3. **Updated** by `/rs-impl` when implementation changes a convention
4. **Never overwritten** — if conventions exist, `/rs-spec` skips creation. Existing conventions mean the implementation is established.

## Creation

If `rootspec/CONVENTIONS/` does not exist, create it with both files.

**Source priority depends on project state:**

- **Greenfield** (HAS_CODE=false): derive from spec (L4 systems, detected FRAMEWORK) + framework ecosystem defaults. For categories without clear guidance, use sensible defaults for the framework and note them.
- **Brownfield** (HAS_CODE=true): extract from existing code. Read source files, `package.json`, config files (tsconfig, eslint, tailwind, vite, etc.), and stylesheets. Document what IS, not what should be.

After writing both files, report: `"Created conventions docs. Review before next run: rootspec/CONVENTIONS/"`

## Format

Structured markdown. Each section is a `##` heading matching a predefined category. Each convention is a `- **Label:** value` list item. No prose, no paragraphs, no interpretation.

```markdown
## Stack
- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript (strict mode)
- **Styling:** Tailwind CSS v3
```

If a category doesn't apply to the project, omit the section entirely. Don't include empty sections or "N/A" entries.

## Maintenance

After implementing each story, check if the implementation introduced or changed any convention. If so, update the specific entry. Only update entries that actually changed — don't rewrite the whole file.

When updating, match the existing format exactly. Add new entries under the appropriate section heading. If a new section is needed, add it at the logical position.

---

## technical.md

Predefined categories and their entries. Include all categories that apply.

### Stack
- **Framework:** framework name and version (e.g., Next.js 14, Vite 5)
- **Language:** language and config (e.g., TypeScript strict mode)
- **Runtime:** runtime if relevant (e.g., Node 20, Bun 1.x)
- **Styling:** CSS approach (e.g., Tailwind CSS v3, CSS Modules)
- **Key libraries:** significant dependencies beyond the framework

### Code Patterns
- **File naming:** convention (e.g., kebab-case, PascalCase for components)
- **Component style:** function vs class, arrow vs declaration
- **Exports:** named vs default
- **Directory structure:** organization pattern (e.g., feature-based, layer-based)

### Imports
- **Order:** import grouping (e.g., external > internal > relative)
- **Barrel files:** yes/no and pattern
- **Path aliases:** configured aliases (e.g., @/ maps to src/)

### Types
- **Object shapes:** interfaces vs type aliases
- **Validation:** library if used (e.g., Zod, io-ts)
- **Generation:** auto-generated types if applicable (e.g., Prisma, GraphQL codegen)

### State Management
- **Global state:** library/approach (e.g., Zustand, Redux Toolkit, Context)
- **Server state:** data fetching approach (e.g., TanStack Query, SWR)
- **Form state:** form library if used (e.g., React Hook Form, Formik)

### Routing
- **Approach:** routing method (e.g., file-based, react-router)
- **Patterns:** route organization (e.g., app router groups, nested layouts)

### API
- **Style:** REST, GraphQL, tRPC, etc.
- **Client:** HTTP client (e.g., fetch, axios, ky)
- **Auth:** authentication strategy (e.g., JWT, session, OAuth)
- **Patterns:** endpoint patterns if applicable

### Data Model
- **ORM/DB:** database access (e.g., Prisma, Drizzle, raw SQL)
- **Schema location:** where schemas are defined
- **Patterns:** data access patterns (e.g., repository pattern, direct queries)

### Error Handling
- **UI errors:** strategy (e.g., error boundaries, toast notifications)
- **Async errors:** strategy (e.g., try-catch, Result types)
- **Logging:** logging approach if relevant

### Testing
- **Unit:** framework (e.g., Vitest, Jest)
- **E2E:** framework (e.g., Cypress, Playwright)
- **Patterns:** testing conventions (e.g., collocated tests, test/ directory)

---

## visual.md

Predefined categories for visual implementation. L1 design pillars provide emotional direction; this doc captures the concrete tokens and patterns that implement that direction.

### Component Library
- **Base:** library if used (e.g., shadcn/ui, Radix, MUI, custom)
- **Customization:** how components are customized (e.g., Tailwind classes, theme tokens)

### Colors
- **Primary:** primary color (e.g., blue-600)
- **Secondary:** secondary color if applicable
- **Neutral:** neutral palette (e.g., slate)
- **Semantic:** success/warning/error colors
- **Background:** page and surface backgrounds

### Spacing
- **Base unit:** spacing base (e.g., 4px, Tailwind default)
- **Scale:** spacing scale approach (e.g., Tailwind spacing utilities)
- **Container:** max-widths for content containers

### Typography
- **Body font:** primary font (e.g., Inter, system-ui)
- **Heading font:** heading font if different
- **Mono font:** monospace font for code
- **Scale:** type scale approach (e.g., Tailwind text utilities)

### Layout
- **Grid:** grid system (e.g., CSS Grid, Tailwind grid)
- **Navigation:** nav pattern (e.g., sidebar, top bar, bottom tabs)
- **Page structure:** common page layout (e.g., sidebar + main, full-width)

### Responsive
- **Approach:** mobile-first or desktop-first
- **Breakpoints:** breakpoint values or system (e.g., Tailwind defaults: sm/md/lg/xl)
- **Patterns:** responsive patterns (e.g., stack on mobile, side-by-side on desktop)

### Motion
- **Transitions:** transition approach (e.g., Tailwind transition utilities, Framer Motion)
- **Duration:** standard durations (e.g., 150ms for micro, 300ms for page)
- **Philosophy:** motion style (e.g., subtle, functional only, expressive)

### Icons
- **Library:** icon set (e.g., Lucide, Heroicons, custom SVGs)
- **Size:** standard sizes (e.g., 16px inline, 24px standalone)
