---
number: 4995
title: `useRouteParams` | support for object as first parameter to handle multiple route parameters
type: other
state: open
created: 2025-08-28
url: "https://github.com/vueuse/vueuse/issues/4995"
reactions: 1
comments: 0
---

# `useRouteParams` | support for object as first parameter to handle multiple route parameters

### Clear and concise description of the problem

Currently, the `useRouteParams` function only supports accessing individual route parameters through string identifiers. This becomes cumbersome when developers need to work with multiple route parameters simultaneously, as they have to make multiple function calls and manage multiple reactive references.

### Suggested solution

Extend the `useRouteParams` function to accept an object of default values as the first parameter, enabling handling of multiple route parameters in a single function call. This enhancement would:
1. Allow accessing all route parameters as a single reactive object
2. Provide default values for multiple parameters in a single declaration
3. Maintain backward compatibility with existing string-based usage
4. Support ...