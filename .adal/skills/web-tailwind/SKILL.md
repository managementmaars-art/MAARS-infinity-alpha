---
name: web-tailwind
cluster: web-dev
description: "Tailwind CSS 4: utility classes, config, JIT, arbitrary values, darkMode, plugins, shadcn/ui"
tags: ["tailwind","css","utility","web"]
dependencies: []
composes: []
similar_to: []
called_by: []
authorization_required: false
scope: general
model_hint: claude-sonnet
embedding_hint: "tailwind css utility classes responsive dark mode shadcn jit"
---

# web-tailwind

## Purpose
This skill enables the AI to assist with Tailwind CSS 4 for building responsive, utility-first web interfaces, focusing on features like utility classes, configuration, JIT compilation, arbitrary values, dark mode, plugins, and shadcn/ui integration.

## When to Use
Use this skill when developing web projects that require rapid styling with reusable classes, such as creating responsive layouts, theming with dark mode, or integrating pre-built components from shadcn/ui. Apply it in scenarios like frontend development for React/Vue apps or static sites where CSS bloat needs minimization.

## Key Capabilities
- Utility classes for direct styling (e.g., 'flex', 'p-4', 'hover:bg-blue-700').
- JIT mode for on-demand CSS generation to reduce bundle size.
- Arbitrary values for custom styling (e.g., 'w-[14rem]' for width).
- Dark mode support via 'dark:' prefix or media queries.
- Plugins for extending functionality, like adding custom utilities.
- shadcn/ui integration for component-based UI kits.
- Responsive design with breakpoints (e.g., 'md:flex' for medium screens and up).

## Usage Patterns
To apply Tailwind classes, add them directly to HTML elements in your markup. For configuration, edit the tailwind.config.js file to customize themes, extend utilities, or enable JIT. Always import Tailwind's base, components, and utilities in your CSS entry point. For shadcn/ui, clone the repository and integrate components via Tailwind classes. To enable dark mode, set it in config and use the 'dark:' variant.

Example 1: Create a responsive button.
```html
<button class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded md:px-6">
  Click me
</button>
```

Example 2: Configure dark mode in tailwind.config.js.
```js
module.exports = {
  darkMode: 'class',  // Use 'media' for OS-level or 'class' for manual toggle
  theme: { extend: {} },
};
```

## Common Commands/API
Use the Tailwind CLI for building and initializing projects. Run `npx tailwindcss init` to generate tailwind.config.js. Build CSS with `npx tailwindcss -i ./input.css -o ./output.css --jit` to enable JIT mode. For purging unused styles, add content paths in config: `content: ['./src/**/*.{html,js}']`. API-wise, Tailwind exposes no direct endpoints, but access config via JavaScript modules. To add plugins, require them in config: `plugins: [require('tailwindcss/plugin')(function({ addUtilities }) { ... })]`.

## Integration Notes
Integrate Tailwind by installing via npm: `npm install -D tailwindcss`. In a React project, import the output CSS in your index.js: `import './output.css';`. For shadcn/ui, run `npx shadcn-ui@latest init` and select Tailwind as the framework, then add components like buttons with Tailwind classes. If using Vite or Webpack, configure PostCSS to process Tailwind. Environment variables aren't required, but for any API-based tools (e.g., if extending with external services), use `$TAILWIND_API_KEY` in scripts.

## Error Handling
If JIT doesn't enable, check for misconfiguration in tailwind.config.js (e.g., ensure `mode: 'jit'` is set). For purging errors, verify content paths include all relevant files; add debug mode with `--watch` flag. Common issues: Missing utilities might indicate uninstalled plugins—install via npm and restart build. If dark mode fails, ensure the 'dark' class is added to the HTML element and check for CSS conflicts. Handle arbitrary values errors by validating CSS units (e.g., use 'px' or 'rem'). Always run `npx tailwindcss build --config tailwind.config.js` to test outputs.

## Graph Relationships
- Related to cluster: web-dev (shares tools for web development).
- Connected to tags: tailwind (core framework), css (styling language), utility (class-based approach), web (domain focus).
- Links to other skills: web-react (for integrating with React components), web-vue (for Vue.js projects).
