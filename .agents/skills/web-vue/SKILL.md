---
name: web-vue
cluster: web-dev
description: "Vue 3: Composition API script setup, Pinia, Vue Router 4, SFCs, Vite, Nuxt 3"
tags: ["vue","components","web"]
dependencies: []
composes: []
similar_to: []
called_by: []
authorization_required: false
scope: general
model_hint: claude-sonnet
embedding_hint: "vue composition api pinia router nuxt vite single file"
---

# web-vue

## Purpose
This skill provides tools for building modern Vue 3 applications using the Composition API for reactive logic, Pinia for state management, Vue Router 4 for navigation, Single File Components (SFCs) for modular development, Vite for fast bundling, and Nuxt 3 for server-side rendering and SEO optimization.

## When to Use
Use this skill for creating interactive web apps with reactive UIs, such as dashboards, e-commerce sites, or single-page applications (SPAs). Apply it when you need efficient state handling, routing, or SSR, especially in projects requiring quick development cycles with Vite.

## Key Capabilities
- Composition API: Use `setup()` in SFCs for reactive variables, e.g., `const count = ref(0);` to create a reactive number.
- Pinia: Define stores with `defineStore('main', { state: () => ({ count: 0 }), actions: { increment() { this.count++ } })` for global state.
- Vue Router 4: Set up routes via `createRouter({ history: createWebHistory(), routes: [{ path: '/', component: Home }] })`.
- SFCs: Structure components in .vue files with `<script setup>`, `<template>`, and `<style>` sections.
- Vite: Build projects with `vite build --mode production` for optimized outputs.
- Nuxt 3: Enable SSR with `nuxi generate` for static site generation from Vue apps.

## Usage Patterns
To create a reactive counter component, import `ref` from Vue and use it in `<script setup>`:  
```vue
<script setup>
import { ref } from 'vue';
const count = ref(0);
function increment() { count.value++; }
</script>
<template><button @click="increment">{{ count }}</button></template>
```
For routing, integrate Vue Router by creating a router instance and mounting it:  
```js
import { createRouter, createWebHistory } from 'vue-router';
const router = createRouter({ history: createWebHistory(), routes: [] });
app.use(router);
```
Set up Pinia in main.js: `app.use(createPinia());` and access stores via `useStore()` in components.

## Common Commands/API
- Vite CLI: Run `vite` for dev server, `vite build --base /app/` to specify base path, or `vite preview` for local testing.
- Nuxt 3 CLI: Use `nuxi dev` for development, `nuxi build` for production builds, or `nuxi generate` for static exports.
- Vue API: Call `ref(value)` to create reactive references, `reactive(object)` for proxy objects, or `computed(() => expression)` for derived state.
- Pinia API: Define stores with `defineStore('id', { state, getters, actions })`, access via `const store = useStore('id')`.
- Vue Router API: Use `router.push('/path')` for navigation, or configure guards with `beforeEach((to, from, next) => { next(); })`.
If API keys are needed (e.g., for external services in Nuxt), set them via environment variables like `$NUXT_PUBLIC_API_KEY` in .env files.

## Integration Notes
Integrate Pinia into a Vue app by importing and using it in main.js: `import { createPinia } from 'pinia'; app.use(createPinia());`. For Vue Router, add it after Pinia: `import { createRouter } from 'vue-router'; app.use(router);`. When using Vite, configure in vite.config.js with modules like:  
```js
import { defineConfig } from 'vite';
export default defineConfig({
  plugins: [vue()],
  resolve: { alias: { '@': '/src' } },
});
```
For Nuxt 3, extend the Nuxt config in nuxt.config.ts:  
```ts
export default defineNuxtConfig({
  modules: ['@pinia/nuxt'],
  router: { options: {} },
});
```
Ensure dependencies are installed via `npm install vue@3 pinia vue-router@4 vite nuxt@3`.

## Error Handling
Handle common errors like missing dependencies by checking npm logs and running `npm install`. For reactive issues in Composition API, use `.value` on refs, e.g., if `count` is undefined, ensure it's defined in setup. Vue Router errors (e.g., duplicate routes) show in console; fix by validating routes array. In Vite, if builds fail with "Module not found", verify paths in imports or use `vite build --debug` for details. For Nuxt, catch SSR errors in serverMiddleware or use try-catch in asyncData:  
```js
async asyncData() {
  try { const data = await fetchData(); return { data }; }
  catch (error) { console.error(error); return { error: 'Fetch failed' }; }
}
```

## Concrete Usage Examples
1. Build a simple Vue 3 app with a counter and routing: Create a new Vite project with `npm create vite@latest my-app -- --template vue`, add Pinia via `npm install pinia`, set up a store, and define routes in router/index.js. Then, in App.vue, use the store and router links.
2. Develop a Nuxt 3 app with SSR: Start with `npx nuxi init my-nuxt-app`, install dependencies like `npm install @pinia/nuxt`, create a Pinia store in stores/, and use it in pages/index.vue. Build for production with `nuxi build`, then deploy.

## Graph Relationships
- Related to cluster: web-dev
- Shares tags: vue, components, web
- Connected skills: Other web-dev skills like those for React or general web frameworks.
