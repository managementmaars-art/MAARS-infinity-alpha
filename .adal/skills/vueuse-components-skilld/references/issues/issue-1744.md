---
number: 1744
title: v9.0 Plan
type: feature
state: closed
created: 2022-07-04
url: "https://github.com/vueuse/vueuse/issues/1744"
reactions: 18
comments: 4
labels: "[enhancement]"
---

# v9.0 Plan

Working branch: https://github.com/vueuse/vueuse/tree/next
Milestone: https://github.com/vueuse/vueuse/milestone/2

## Main Focus

- [x] Refactor all `isSupport` to be ref, for SSR
  - #1800
- [x] #1743
- [x] #1768
- [ ] New @vueuse/math package, and move some functions over
  - #1224 
  - #1794
  - #1810
  - #1223
  - #1812
- [ ] Tests for Vue 2.7

## Breaking Changes

- [ ] #1687 
- [ ] #1605
- [ ] #1506

---

## Top Comments

**@antfu** [maintainer] (+1):

Moved to `@vueuse/math`. Please check the release note.

**@antfu** [maintainer]:

@userquin sure if you could make a PR

**@francoism90**:

```
runtime-core.esm-bundler.js:221 SyntaxError: The requested module '/node_modules/.vite/deps/@vueuse_core.js?v=16ed7cb0' does not provide an export named 'and'
```
Is `and` removed or moved?

Edit: https://vueuse.org/math/logicAnd/