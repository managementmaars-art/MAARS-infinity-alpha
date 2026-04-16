---
number: 4981
title: `useAxios` | Support for Path Variables
type: other
state: open
created: 2025-08-23
url: "https://github.com/vueuse/vueuse/issues/4981"
reactions: 2
comments: 0
---

# `useAxios` | Support for Path Variables

### Clear and concise description of the problem

Currently, useAxios does not support dynamic path variables in the request URL, such as :id. It would be very useful if useAxios could accept placeholders in the path and allow us to pass their values later when executing the request.

For example:

```ts
const { execute } = useAxios('users/:id/posts')

// later, when we have the `id` (e.g. after a form submit):
execute({ pathParams: { id: 123 } })

```

This feature would be especially helpful in cases where we don’t yet know the value of a path parameter at the time of defining the request, but want to provide it dynamically later (e.g. during form submission, user interaction, etc.).

...