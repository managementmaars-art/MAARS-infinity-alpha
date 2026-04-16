---
number: 4268
title: Difference(s) between `useElementSize` and `useResizeObserver`
category: Q&A
created: 2024-10-05
url: "https://github.com/vueuse/vueuse/discussions/4268"
upvotes: 1
comments: 1
answered: false
---

# Difference(s) between `useElementSize` and `useResizeObserver`

Are there any difference between those two? Both implementations use the ResizeObserver API, and are basically doing the same thing. Is there a reason, why those two functions exist separately?

---

## Top Comments

**@dosubot** (+1):


Hey @FeBe95! I'm here to help you with any questions or issues you have. Let's tackle this together!


`useElementSize` and `useResizeObserver` serve different purposes despite both using the ResizeObserver API.

1. **`useResizeObserver`:** This function provides a lower-level abstraction, allowing you to observe size changes of an element and execute a callback when a resize event occurs. It offers flexibility for various custom behaviors beyond just tracking size.

...