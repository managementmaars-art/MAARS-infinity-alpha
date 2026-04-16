---
number: 5236
title: `useFetch` | stream handling
type: other
state: open
created: 2025-12-30
url: "https://github.com/vueuse/vueuse/issues/5236"
reactions: 1
comments: 0
---

# `useFetch` | stream handling

### Clear and concise description of the problem

I am trying to handle a streaming response using `useFetch`.

However, when using `useFetch`, the `data` ref or the response handling seems to wait until the entire request is completed before updating, rather than exposing chunks as they arrive (e.g AI chat response) due to `response.text()` or `response.json()`... is being awaited internally



### Suggested solution

`useFetch` should provide a way to access the `response.body` stream or update a variable incrementally, instead of buffering the whole response internally before returning.

Or at least, `onFetchResponse` should allow us to hijack the reader before `useFetch` attempts to parse the whole body.

### Alternative

_No response_

### Additional context

_No response_

...