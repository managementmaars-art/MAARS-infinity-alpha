---
number: 5279
title: useSortable
category: Q&A
created: 2026-02-04
url: "https://github.com/vueuse/vueuse/discussions/5279"
upvotes: 1
comments: 1
answered: false
---

# useSortable

Does `useSortable` support Swap and MultiDrag plugin from sortable.js ?

---

## Top Comments

**@dosubot**:


No, useSortable does not currently support the Swap or MultiDrag plugins from sortable.js. It does not import the full Sortable package with plugins or expose the Sortable class to allow mounting plugins, so options like { multiDrag: true } have no effect. This limitation is discussed in detail in the community: see discussion.



*To reply, just mention @dosu.*

...