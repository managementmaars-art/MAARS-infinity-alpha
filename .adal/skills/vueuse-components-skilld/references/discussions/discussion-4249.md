---
number: 4249
title: "Difference between \"useElementVisibility\" & \"useIntersectionObserver\""
category: Q&A
created: 2024-09-24
url: "https://github.com/vueuse/vueuse/discussions/4249"
upvotes: 2
comments: 1
answered: true
---

# Difference between "useElementVisibility" & "useIntersectionObserver"

- useElementVisibility
- useIntersectionObserver

What are the differences? Both seems to mention doing the same thing

---

## Accepted Answer


Hello @tlkiong! I'm a bot here to help you with bug fixes, answering questions, and becoming a contributor. How can I assist you today?


The main difference between `useElementVisibility` and `useIntersectionObserver` is that `useElementVisibility` is a higher-level utility that internally uses `useIntersectionObserver` to determine the visibility of an element.

- **`useElementVisibility`**:
  - It simplifies the process of checking if an element is visible within the viewport.
  - Internally calls `useIntersectionObserver` and handles the logic to set the visibility state based on the intersection entries.
  - Provides a boolean value indicating whether the element is visible or not.

...