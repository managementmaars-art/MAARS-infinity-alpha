---
number: 4625
title: The problem of using useElementBounding and useDraggable together
category: Q&A
created: 2025-02-25
url: "https://github.com/vueuse/vueuse/discussions/4625"
upvotes: 1
comments: 1
answered: true
---

# The problem of using useElementBounding and useDraggable together

When I use useElementBounding and useDraggable together, the element position cannot be updated responsively after dragging the element. Can useElementBounding only be updated after the scrollbar and window changes? If I want to drag and drop to get element data, where do I need to change (add configuration) or there are other ready-made methods?

---

## Accepted Answer


Hey @hzlzsm!  I'm here to help you with any bugs, questions, or contributions you might have. Let's work together to solve the issue you're facing.


There are two similar closed issues related to your question, but neither provided a solution in the comments:

1. The absolute/relative positioning makes the useDraggable element change its coordinates as moving starts <sup>[[1]](https://github.com/vueuse/vueuse/issues/3199)</sup>.
2. useElementBounding 的目标元素被flex包裹时，位置信息不会响应式更新 <sup>[[2]](https://github.com/vueuse/vueuse/issues/2978)</sup>.

...