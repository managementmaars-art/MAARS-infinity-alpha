---
number: 4867
title: `useFileDialog` | Make custom input less eager for late initilised template refs
type: other
state: open
created: 2025-07-09
url: "https://github.com/vueuse/vueuse/issues/4867"
reactions: 2
comments: 1
---

# `useFileDialog` | Make custom input less eager for late initilised template refs

### Clear and concise description of the problem

Currently `useFileDialog` accepts HTMLInputElements for custom input elements.
However this unwraps the ref which when using it as a template ref will be undefined until after mounting.
This means `useFileDialog` is used in the `setup` code then the `input` will always be undefined and a new input created using the `document.createElement` fallback.
```
  let input: HTMLInputElement | undefined
  if (document) {
    input = unrefElement(options.input) || document.createElement('input') // 👈 this will unref the element which will be `undefined`
    input.type = 'file'

    input.onchange = (event: Event) => {
      const result = event.target as HTMLInputElement
      files.value = result.files
      changeTrigger(files.value)
    }

...