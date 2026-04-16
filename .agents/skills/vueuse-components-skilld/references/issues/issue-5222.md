---
number: 5222
title: `useIDBKeyval` | SSR-friendly
type: other
state: open
created: 2025-12-17
url: "https://github.com/vueuse/vueuse/issues/5222"
reactions: 1
comments: 0
---

# `useIDBKeyval` | SSR-friendly

### Clear and concise description of the problem

When using the `useIDBKeyval` composable in a Nuxt environment, it throws the following error:
`ERROR: indexedDB is not defined`

### Suggested solution

Implement SSR guards similar to how `useStorage` handles SSR in this code lines

### Alternative

_No response_

### Additional context

_No response_

### Validations

- [x] Follow our Code of Conduct
- [x] Read the Contributing Guidelines.
- [x] Read the docs.
- [x] Check that there isn't already an issue that request the same feature to avoid creating...