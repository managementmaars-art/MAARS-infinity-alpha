---
number: 4367
title: Bundle size in v12
category: Q&A
created: 2024-11-27
url: "https://github.com/vueuse/vueuse/discussions/4367"
upvotes: 2
comments: 1
answered: false
---

# Bundle size in v12

https://bundlephobia.com/package/@vueuse/core@12.0.0

Is it expected that the bundle size went up in size since v12?

---

## Top Comments

**@antfu** [maintainer]:

The bundle size is the same. It's just that Vue has been moved from the optional PeerDependency of `vue-demi` to dependencies, which causes this measure to be different.