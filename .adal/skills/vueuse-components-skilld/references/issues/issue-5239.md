---
number: 5239
title: `toRef` type mismatch with Vue
type: other
state: open
created: 2026-01-04
url: "https://github.com/vueuse/vueuse/issues/5239"
reactions: 1
comments: 1
---

# `toRef` type mismatch with Vue

I’m using Nuxt(v4.2.2) with `@vueuse/nuxt`(v14.1.0).

Nuxt auto-imports Vue’s `toRef`. VueUse also provides `toRef`, but it is not auto-imported

When using VueUse composables, the inferred toRef type (from Vue) does not match what VueUse expects

This leads to confusing TypeScript errors even though runtime behavior is correct.

...